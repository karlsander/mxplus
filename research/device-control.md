> Historical investigation: standalone build paths refer to Git history. The only active firmware is [mainline](../docs/MAINLINE.md). Historical evidence has not been rewritten as combined-image evidence.

# MX-1 computer-port USB control and audio startup

## Result and scope

The main application contains enough reusable USB infrastructure for a concrete
UAC2 experiment. The original control engine can send short class-control
responses, its descriptor loader is largely class agnostic, and its normal USB
initializer can be replaced without changing the backup/mass-storage
initializer. A newly written fixed-clock request adapter is provided and has
passed native request tests.

The firmware also contains a specific playback-before-capture dependency. It
is not merely inferred from Linux's Roland quirk: the original audio pump
checks OUT availability before advancing two IN startup states. One
four-byte Thumb instruction controls that dependency. Executing the original
732-byte pump in Unicorn with explicitly mocked MMIO demonstrates that the
instruction change permits IN priming without OUT data under the modeled
conditions. Physical USB timing and successful iOS enumeration remain
unverified.

This report describes the **computer Type-B USB function** in the main
application. It does not describe the separate application that hosts the four
AIRA ports. The proposed code is newly written; it is not original Roland C
source recovered by the decompiler.

### Binary identity and address convention

- Source updater: `inputs/MX1_UPD.original.bin` (unchanged upload originally
  named `MX1_UPD.BIN`), SHA256
  `26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`.
- Decoded main application: `analysis/container_app_main.bin`, 918,600 bytes,
  SHA256 `256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b`.
- Resident image base: `0x60000000`.
- Hot-code copy: image source `0x600d0b8c` to runtime `0x01000300`, length
  `0xf3a4` / 62,372 bytes.
- For an address in that hot-code range, decoded-file offset is
  `0xd0b8c + (runtime_address - 0x01000300)`.
- Odd addresses in tables identify Thumb function pointers. Function names
  below use the even instruction address.

Evidence comes from Ghidra pseudocode and references, followed by Capstone
checks of consequential instructions. Ghidra sometimes merges shared tails
or misses functions reached only through tables. Its inferred C types and
parameter counts are not authoritative; the specific ABIs below were checked
in assembly.

## 1. Normal initialization and live descriptors

`FUN_6000ebce` reads the sample-rate setting, caches it at `0x60512820`, stops
the old USB instance when necessary, and calls normal initialization with:

| Setting | Value passed in r0 |
| --- | ---: |
| 0 | 44,100 |
| 1 | 48,000 |
| 2 | 96,000 |

The normal initializer at `0x6000d980` has this effective contract:

```c
int normal_usb_initialize(uint32_t sample_rate)
{
    patch_original_audio_descriptor(sample_rate);       // 6000d9c4
    if (descriptor_init((void *)0x600b4af8)) return -1;   // 6003b764
    if (register_class((void *)0x600b4960)) return -1;    // 6003b7cc
    if (usb_start()) return -1;                         // 6003b786
    return 0;
}
```

The pointer table at `0x600b4af8` contains the device, high-speed
configuration, full-speed configuration, qualifier, and four string pointers.
The original audio device descriptor is at `0x600b4980`; the high-speed
configuration is at `0x600b499c`. The main configuration pointer itself is the
word at `0x600b4afc`.

`FUN_6003c19c` resolves this table into eight pointer slots at `0x606293dc`.
It permits one configuration pair, four strings, and a qualifier, and checks
that all eight slots are present. It retains pointers; it does not make an
independent immutable copy of the configuration. Consequently a replacement
descriptor in writable SRAM can be referenced through the existing pointer
table.

The descriptor getters mutate configuration byte 1 between type 2 and type 7
for CONFIGURATION and OTHER_SPEED_CONFIGURATION responses. The replacement
descriptor therefore must remain writable. The full-speed and qualifier
objects must also be reviewed for truthful behavior; changing only the
high-speed class bytes is incomplete.

### The original rate writer must be replaced

`FUN_6000d9c4` writes directly into the live high-speed configuration using
hardcoded offsets. It does not find descriptors by walking their lengths.

| Field | Original offsets relative to `0x600b499c` |
| --- | --- |
| Four three-byte frequencies | `0x39`, `0x62`, `0x94`, `0xbd` |
| 18-channel OUT / IN packet sizes | `0x40`, `0x9b` |
| Two-channel OUT / IN packet sizes | `0x69`, `0xc4` |

The packet formulas are:

```c
max_packet_18 = (sample_rate / 8000 + 2) * 72;
max_packet_2  = (sample_rate / 8000 + 2) * 8;
```

| Rate | 18-channel maximum | Two-channel maximum |
| --- | ---: | ---: |
| 44.1 kHz | 504 bytes | 56 bytes |
| 48 kHz | 576 bytes | 64 bytes |
| 96 kHz | 1,008 bytes | 112 bytes |

These maxima include headroom. They are not assertions that every packet
contains that many bytes. Leaving this writer active after installing UAC2
would overwrite unrelated fields of the new terminal/clock graph.

For the 355-byte preserving design produced by
`tools/uac2_design.py`, the new 16-bit packet fields are at:

| Stream | Endpoint descriptor offset | Packet field offset |
| --- | --- | --- |
| IF1 alt1, 18-channel OUT | `0x8d` | `0x91` |
| IF1 alt2, stereo OUT | `0xbb` | `0xbf` |
| IF2 alt1, 18-channel IN | `0xf2` | `0xf6` |
| IF2 alt2, stereo IN | `0x120` | `0x124` |

Only these four sizes need runtime rate patching in that fixed-clock design.
The UAC2 clock entity supplies the rate through control requests.

## 2. Descriptor-driven hardware setup and alternate settings

The low-level descriptor walker at `0x6003d026` parses standard descriptor
types 2, 4, and 5 into registers under `0x40010000`. It skips other types
using each descriptor's length. It does not require the original vendor
interface class or the original UAC1-style format layout.

For interfaces it passes the interface number and alternate setting to
`0x6003cfaa`. For endpoints it encodes the endpoint number, direction,
transfer type, selected interface/alternate, and 11-bit maximum packet size
into descriptor registers around `0x40010200`. This is a useful basis for
UAC2: an AudioControl graph, IAD, and UAC2 class-specific streaming blocks
can be present without this walker interpreting their layouts.

The observed register assignments support hardware-assisted standard USB
configuration and alternate selection. `0x010054a8` synthesizes a
SET_CONFIGURATION setup packet from hardware state and invokes callback 10.
The generic library has SET_INTERFACE notification machinery at `0x6003b10a`
and callback 12, but no active low-level invocation of callback 12 was found
in the inspected normal dispatch. The normal application does not rely on
an audio start/stop class object: its two class-object functions at
`0x6000d978` and `0x6000d97c` simply return zero.

Instead, the audio pump observes the hardware's selected alternate state
directly. Assembly at `0x010098da`, `0x01009976`, `0x01009a66`, and
`0x01009ac4` shows:

| Field at `0x4001017c` | Observed use |
| --- | --- |
| Bits 19:16 | OUT stream alternate; value 2 selects stereo |
| Bits 15:12 | IN stream alternate; value 2 selects stereo |

The 18-channel branches read/write 18 four-byte words per audio tick. Stereo
OUT is placed into internal channels 16/17; stereo IN uses internal capture
channels 16/17. Retaining interface numbers 1 and 2, endpoint addresses
`0x0d` and `0x8e`, and alternate numbers 1 and 2 avoids altering these
assumptions.

### Preserve the vendor MIDI interface for this experiment

The current 355-byte design retains the original 52-byte interface 3 block
unchanged at new offset `0x12f`. It remains vendor-specific MIDI, not a newly
class-compliant MIDI implementation. The IAD covers interfaces 0 through 2
only, while the configuration counts four interfaces.

This is preferable to removing interface 3 during the first audio experiment.
The main application's direct MIDI sender at `0x01000566` can check global
USB configuration and then poll the ready state of endpoint 4 or 5. Without
the original interface/endpoint configuration, an otherwise unrelated MIDI
event could reach a wait whose completion is no longer assured. This is a
static risk, not a reproduced hang, but retaining the original descriptors
avoids introducing it.

## 3. Exact class-control callback contract

The main USB stack has two callback layers:

| Object | Address / offset |
| --- | --- |
| Current eight-byte setup packet | `0x606293fc` |
| EP0 state byte | `0x600d09c0` |
| Low-level callback table | `0x606293fc + 0x72c` |
| Low-level class request callback, index 1 | `0x60629b2c` |
| Application callback table for instance 0 | `0x605251b8` |
| Application class request callback, index 1 | `0x605251bc` |

`FUN_01004834` dispatches request types. Class requests enter
`FUN_01004646`, which leaves r0 pointing to the setup packet and tail-calls
low-level callback 1. For an IN request with a data stage, it first writes
EP0 state 3. OUT data uses state 4; a no-data request uses state 5.

The installed generic callback at `0x6003b664` forwards the same pointer to
application callback 1 if that pointer is nonzero. Neither layer interprets
the callback's return value. The effective callback type is:

```c
void class_request(const uint8_t setup[8]);
```

The normal initializer currently registers no application class handler.
Therefore advertising standard UAC2 controls without adding one would leave
requests without the required response.

### Registering a handler

The checked registration ABI is:

```c
int register_application_callback(int instance, uint32_t index,
                                  uintptr_t thumb_function);
// Firmware address with Thumb bit: 0x6003b7f5
// For this task: instance=0, index=1.
// Return: 0 on success, -1 on invalid arguments.
```

Registration must occur after `0x6003b764`, which calls the upper-stack
initializer `0x6003b38c` and zeros the callback array. Installing the callback
from only the old rate-writer hook would be too early: it would be erased.
Registration before the stock USB start at `0x6003b786` avoids enumeration
starting with a missing handler.

### Sending a short EP0 IN reply

Assembly verifies the reusable helper:

```c
void ep0_reply(const void *data, uint32_t length, uint32_t flags);
// Firmware address with Thumb bit: 0x010046bb
```

It creates a 16-byte transfer record, writes length and data pointer, stores
the flags in the halfword at offset 10, submits it as logical endpoint 1 via
`0x6003c438`, and immediately invokes the EP0 FIFO sender at `0x01003bbc`.
The transfer record is copied into stack-owned storage. The response buffer
must remain valid; the prototype uses persistent writable memory.

For the one-, four-, and fourteen-byte clock replies, flags zero is sufficient.
The stock descriptor path uses flag 8 when a shorter-than-requested response
is an exact multiple of 64 bytes and needs a terminating zero-length packet.
The proposed clock replies do not meet that condition.

### Stalling an unsupported request

Returning a failure integer from the callback has no effect. The stock
failure pattern is to set the EP0 state byte to 1, clear the eight setup
bytes, then invoke `0x01003e1a(0)` (Thumb pointer `0x01003e1b`). For endpoint
zero, that routine clears two control bits and asserts the stall bit in
`0x40010100`.

The adapter follows that pattern for invalid requests and unsupported writes.
It does not silently acknowledge a host attempt to change a read-only clock.

## 4. Newly written fixed-clock adapter

Files:

- `sources/hardware/uac2_adapter.c`: freestanding-friendly request adapter and
  verified firmware-call bindings.
- `sources/hardware/uac2_adapter_native_test.c`: native transport mocks and
  request tests.

Exports:

```c
void mx1_uac2_set_rate(uint32_t rate);
void mx1_uac2_class_request(const uint8_t *setup);
int  mx1_uac2_start(void);
```

The start helper registers the handler and then calls the original USB start.
It propagates registration/start failures. A replacement normal initializer
can call the setter, prepare the replacement descriptor, call the original
descriptor and class-object initialization functions, and then call this
start helper. The backup/mass-storage initializer uses a different callsite.

For clock entity `0x10` on AudioControl interface 0 the adapter implements:

| Operation | Accepted request fields | Reply |
| --- | --- | --- |
| Frequency CUR | `a1`, request 1, `wValue=0100`, `wIndex=1000` | Configured rate, 32-bit LE |
| Frequency RANGE | `a1`, request 2, same value/index | One subrange: MIN=MAX=rate, RES=0 |
| Clock validity CUR | `a1`, request 1, `wValue=0200`, `wIndex=1000` | One byte |

Every response is clamped to the host's `wLength`. A two-byte RANGE probe
receives only the range-count header. Zero-length reads and unsupported
selectors, entities, channels, recipients, directions, requests, and writes
stall.

Validity currently means that the captured configured rate is one of 44.1,
48, or 96 kHz. Hardware PLL-lock reporting was not located. That limitation
must not be misreported as a verified physical clock-validity sensor.

Native verification command:

```bash
gcc -std=c11 -Wall -Wextra -Werror -O2 -DMX1_UAC2_NATIVE_TEST \
  sources/hardware/uac2_adapter.c \
  sources/hardware/uac2_adapter_native_test.c \
  -o sources/hardware/uac2_adapter_native_test
sources/hardware/uac2_adapter_native_test
```

Result: **4,881 control-request cases passed**, including three rates,
lengths 0 through 512, the RANGE header probe, malformed requests, invalid
configured clocks, and callback-registration ordering/error propagation.
These tests validate the new control logic. They do not emulate the original
EP0 hardware or prove successful host enumeration.

## 5. Original audio pump and the playback dependency

`FUN_01009840` is the full-duplex computer-port audio pump. It is installed
by `0x60001670` into the audio callback structure using `0x0100c8f0`.

| Location | Observed purpose |
| --- | --- |
| `0x4001016c` | Endpoint 13 OUT status; bit 3 is tested for usable OUT data |
| `0x400101f4` | Endpoint 13 OUT FIFO read port |
| `0x400100d8` low 11 bits | OUT byte count sampled by this function |
| `0x40010170` | Endpoint 14 IN control |
| `0x40010174` | Endpoint 14 IN status/commit |
| `0x400101b8` | Endpoint 14 IN FIFO write port |
| `0x20000420` | OUT receive state |
| `0x01010048` | IN transmit state |
| `0x0101004c` | Two-sample history of bit 1 at `0x40003228` |
| `0x40101000` | 18 internal playback words |
| `0x40101048` | 18 internal capture words |

Register names above describe observed use, not an unpublished ESC2 register
manual. The function uses fixed/float conversion ports at `0x4004056c` and
`0x40040574`. It explicitly maps the integer `0x80000000` to float `-1.0`.
That is useful evidence about the sample path, but the converter scaling and
all valid-bit alignment remain to be physically checked.

At entry, the function sets r12 to 1. If the OUT endpoint has no usable data
and no buffered tail remains, it resets OUT state, fills the playback words
with silence, and sets r12 to 0 at `0x01009a06`.

The IN state machine then behaves as follows:

| State | Observed action / next state |
| --- | --- |
| 0 | Wait for IN status bit 16 and a nonzero status field at bits 27:24; then state 1 |
| 1 | Wait for a rising phase edge **and r12 != 0**; write IN control and enter state 2 |
| 2 | While IN status permits writes, fill the FIFO with zero audio words; commit on a phase edge, then state 3 |
| 3 | Wait for **r12 != 0**; then state 4 |
| 4 | Copy mixer capture words through the converter into the IN FIFO and commit on phase edges |

If required IN readiness disappears in the active path, the state returns
to zero. Once state 4 is reached, capture does not continuously depend on
OUT availability. This explains why the proposed change is a startup
experiment rather than a replacement of the whole transport.

### Exact candidate instruction

| Item | Value |
| --- | --- |
| Runtime address | `0x01009a06` |
| Decoded main-file offset | `0x000da292` |
| Original instruction | `mov.w r12, #0` |
| Original bytes | `4f f0 00 0c` |
| Experimental instruction | `mov.w r12, #1` |
| Experimental bytes | `4f f0 01 0c` |

This leaves the OUT-silence writes and OUT-state reset intact, while allowing
the two IN startup checks to proceed without OUT data. Other IN readiness,
clock-edge, priming, and packet-commit conditions remain active. The binary
must be version/hash guarded; this address must not be used against another
firmware without reanalysis.

## 6. Executing the original pump with mocked MMIO

`sources/hardware/uac2_pump_harness.py` executes the actual original Thumb
instructions in Unicorn. It loads the relevant original scatter-copy data
and compares the original function against the one-instruction variant.
It does not replace the pump with a C reimplementation.

The model explicitly supplies host-IN-ready status bits, an OUT-ready bit,
and a periodic clock/phase input. It uses identity conversion registers so
that control-flow behavior can be distinguished from audio numeric behavior.
It does not model real FIFO capacity, USB tokens, NAK behavior, microframe
timing, peripheral reset side effects, or physical clock generation.

The 90-tick runs produced:

| Scenario | Original result | Variant result |
| --- | --- | --- |
| Capture only, no OUT data | 0 IN words, stuck in state 1 | 1,494 IN words, state 4, zero OUT reads |
| Duplex startup | 1,494 IN words | Identical FIFO, commit, state, and OUT-read trace |
| Stop/restart capture without OUT | 0 IN words | 1,044 IN words; no writes while IN readiness absent |
| Start duplex, then stop playback | Capture continues | Identical trace; both continue capture |
| Stereo capture only | Not a comparison case | 166 IN words, exactly two words per active tick |
| Mixed OUT18/IN2 | 166 IN words | Identical duplex trace; independent IN stereo selection |
| Mixed OUT2/IN18 | 1,494 IN words | Identical duplex trace; independent OUT stereo selection |

The variant first writes silence, then nonzero fixture capture data. This
demonstrates removal of the identified software startup dependency under the
modeled conditions. It does **not** establish that an actual host and ESC2
peripheral will supply those readiness/phase conditions without playback.
That last boundary requires a bus trace or device test.

The mixed-alternate cases also confirm there is no code-level requirement
that the two selected alternate numbers match. The OUT tail accounting still
uses a fixed 72-byte decrement even in the stereo branch. The limited FIFO
model does not validate the hardware's packet-count semantics; real mixed
alternatives and packet boundaries remain a physical test requirement.

Reproduce from the project directory:

```bash
.venv/bin/python sources/hardware/uac2_pump_harness.py
```

Machine-readable results are in
`sources/hardware/uac2_pump_harness_results.json`.

## 7. Integration and remaining concrete validation

A coherent experimental normal-mode replacement should do all of the
following together:

1. Preserve the selected sample rate passed to normal USB initialization.
2. Install a truthful UAC2 descriptor/qualifier set and replace the original
   fixed-offset UAC1 rate writer.
3. Preserve the original interface/endpoint/alternate mappings, including
   vendor MIDI, unless a separate change deliberately replaces them.
4. Register the class handler after stack initialization and before USB start.
5. Supply the actual fixed current frequency and single supported range for
   that session; do not advertise writable frequency control.
6. Apply and test the narrowly identified input-startup change.
7. Verify the resulting binary's load placement, Thumb branches, persistent
   buffers, checksums, and boot/update behavior independently.

The next physical tests should establish that original and candidate images
enumerate at the three rates; that both GET_DESCRIPTOR and OTHER_SPEED paths
return consistent data; that clock CUR/RANGE probes complete; that IN starts
before any OUT packet; that 18-channel and stereo alternatives transfer the
expected number and alignment of samples; and that stop/restart, reset,
disconnect/reconnect, MIDI, and backup modes remain usable.

The analysis supports producing a reviewable experimental image and a narrow
validation plan. It does not support labeling an untested image a working
iOS-compatible or generally class-compliant firmware release.

## 8. Compiled candidate integration verification

The main investigation subsequently compiled and integrated this adapter into
a 900-byte extension and produced
`build/device-probe/MX1_UAC2_DEVICE_PROBE_UNTESTED.bin`. The candidate SHA256 is
`b17f9005dd2b32b9fd89ccdd07c3a2ef0dda0854fb67ad5732a76390cc005d57`.
`docs/DEVICE_PROBE.md` describes the complete candidate, rebuild commands,
and remaining limitations.

`tools/device_probe_verify.py` executed the original ARM startup, actual
initializer veneer, original descriptor/class initialization, real
`0x01004834 -> 0x01004646 -> 0x6003b664` request route, and compiled adapter.
Eighty-four positive class-control cases and ten negative cases passed.
The negative cases executed the original EP0 stall register writes. Stock
GET_DESCRIPTOR and OTHER_SPEED_DESCRIPTOR paths also returned the correct
live pointers and lengths.

For all three rates at high-speed and full-speed selections, running the
original `0x6003d026` descriptor walker produced byte-identical endpoint
hardware register-write sequences for the original configuration and new
UAC2 configuration. This directly checks the new descriptor graph against
the existing endpoint loader. The original backup initializer's resolved
descriptor and callback tables were also identical.

The only normal stubs in that integration test are RTOS task creation,
low-level hardware start, and EP0 reply delivery to a real FIFO. The reply
pointer, bytes, length, and flags are recorded instead. See
`build/device-probe/arm-verification.json` for the eight test groups,
instruction counts, and explicit scope. These CPU-level results strengthen
the implementation evidence without resolving the physical USB questions.

## Supporting analysis files

- `sources/hardware/show_main_functions.py`: select original decompiled
  functions and resolve their literal-pool words through scatter mappings.
- `sources/hardware/disasm_main.py`: targeted ARM M-class Thumb disassembly
  with literal annotations.
- `sources/hardware/uac2_original_functions.txt`: selected original functions
  used for this report, including initialization, callbacks, descriptor
  programming, and the audio pump.
- `sources/hardware/uac2_original_pump.asm`: exact pump disassembly and
  surrounding literal pool.

External USB standards, Apple startup guidance, and Linux Roland-specific
behavior are documented and sourced in `research/usb-compatibility.md`.
The new claims in this report are independently reproducible observations of
the supplied binary and the explicitly described local experiments.
