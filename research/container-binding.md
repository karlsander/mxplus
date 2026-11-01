# Audit of the early USB host driver binding filter

## Finding

The MX-1's original USB mixer driver registers a **wildcard driver**, with all
vendor, product, device-class, and interface-class matching disabled at this
early stage. The candidate does not need another patch to an earlier
vendor-class registration gate.

This does not imply that the original firmware accepts generic audio devices.
The later configuration parser and policy callback impose additional restrictions.
This audit addresses whether an earlier library filter would prevent ordinary
class-1 audio interfaces from reaching those later stages.

Evidence comes from the supplied original firmware, direct Capstone disassembly,
the Ghidra binding routines, and an independent execution of the original binder
and probe callback in Unicorn. No external-source assumptions are needed.

## Registration record and call path

An indefinitely running task starts at USB application runtime `0x60008958`.
Its startup calls the library initializer `0x600092e4` and then registers the
mixer driver through `0x600093f8` at instruction `0x60008976`.

The instruction at `0x60008974` loads `r0` from literal `0x60008b80`. That literal
contains `0x6002b0ac`, the address of this 16-byte registration record:

```
00 00 00 00 00 00 00 00 7d 83 00 60 91 83 00 60
```

The record's fields are:

| Record offset | Size | Value | Meaning |
|---|---:|---:|---|
| `+0x00` | 2 | `0` | Vendor ID filter value |
| `+0x02` | 2 | `0` | Product ID filter value |
| `+0x04` | 1 | `0` | Device-class filter value |
| `+0x05` | 1 | `0` | Interface-class filter value |
| `+0x06` | 1 | `0` | Match flags; all four filters disabled |
| `+0x07` | 1 | `0` | Reserved/unused here |
| `+0x08` | 4 | `0x6000837d` | Probe callback, Thumb bit included |
| `+0x0c` | 4 | `0x60008391` | Removal callback, Thumb bit included |

The public registration wrapper `0x600093f8` queues message `0x02000004`.
The host task dispatches that message to `0x6000ec8a`, which allocates a driver
node and copies the 16-byte registration record to node offset `+8`.

The binder functions use the following mask bits, now at node offset `+0x0e`:

| Bit | Required comparison when enabled |
|---:|---|
| `0x01` | Device VID equals node VID |
| `0x02` | Device PID equals node PID |
| `0x04` | Device class equals node device class |
| `0x08` | Interface class equals node interface class |

`0x6000eb76` applies the registration to existing interfaces.
`0x6000ee16` applies it to a newly selected interface. Both contain these same
conditional predicates. Because the mixer record's mask is zero, neither
routine rejects an interface on these fields for this registration.

The probe callback at `0x6000837c` queues mixer event 0 and returns success. It
does not add a vendor/class predicate. The later event handler at `0x60008426`
creates the per-device state through `0x60007e72`, which obtains/parses the
configuration with `0x6000a466`. That is the later parser/policy path being
extended by the experimental host candidate.

## Distinguishing the hub driver

There is another driver registration at `0x6002b164`, registered during hub
initialization through the call at `0x6000d7c4`. It has device class `0x09`,
interface class `0x09`, and mask `0x0c`. This is the USB hub driver. Confusing
its record with the mixer registration would give the wrong conclusion about
the audio device filter.

The hub initializer runs before the mixer registration. This audit does not
change either record or their order.

## Why the automatic decompilation missed the registration task

The headless import seeded many indirect targets by looking for a conventional
`PUSH` that saves `LR`. The task at `0x60008958` begins with `sub sp, #0x40` and
never returns. Consequently, the original automatic function export omitted it,
even though its address is present in the task setup's literal pool.

Direct disassembly from the task entry recovered the registration call:

```
60008958: 90b0       sub sp, #0x40
...
6000896a: 00f0bbfc   bl #0x600092e4
...
60008974: 8248       ldr r0, [pc, #0x208]
60008976: 00f03ffd   bl #0x600093f8
```

This is a concrete reason to treat automatically discovered function counts as
coverage statistics, not proof of a complete decompilation. For a future Ghidra
project pass, explicitly disassemble/create a function at `0x60008958`.

## Original-instruction verification

Reproduce with:

```sh
python3 tools/container_binding_verify.py /path/to/MX1_UPD.BIN \
  --output binding-verification.json
```

The harness loads the original USB application and its recovered runtime memory
map. It constructs a single-node driver list using the exact original mixer
registration record, then calls the original `0x6000ee16` binder. The original
list helpers and original `0x6000837c` probe execute. RTOS critical-section
entry/exit and delivery of the queued probe event are stubbed.

With VID `0x1234`, PID `0x5678`, these cases all attach the driver and generate
one probe event:

| Device class | Interface class | Result |
|---:|---:|---|
| `0x00` | `0x01` | Success |
| `0x01` | `0x01` | Success |
| `0xef` | `0x01` | Success |
| `0xff` | `0xff` | Success |
| `0x00` | `0x08` | Success at this early stage |

The last case intentionally demonstrates that this is an early wildcard
binding step; it is not evidence that storage devices can stream audio.

As a negative control, the harness changes only its **in-memory test record**
to require interface class `0xff` using mask `0x08`. An interface with class
`0x01` is then rejected, with no driver attached and no probe event. Thus the
test exercises the actual filter rather than bypassing it.

Results are saved in `analysis/container_binding_verification.json`. The report
includes the exact record bytes, registration disassembly, fixture outcomes,
and test limitations. No firmware change is made by this audit.
