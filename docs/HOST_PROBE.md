# Retired USB-host unlock research

**Documentation only, retired 2 November 2026.** Mainline leaves the USB-host
application unchanged. The following records the earlier narrow UAC1 experiment;
its code, builder and binaries have been removed from the current tree because
suitable hardware validation is unavailable. No generic USB-host compatibility
is claimed. Paths and hashes below refer to the historical implementation.

## Result and status

The project contains a compiled firmware experiment that allows a narrow,
standard USB Audio Class 1 streaming profile to reach the MX-1's existing host
selection logic. It changes the USB application used by the four AIRA host
ports. The original ARM startup, descriptor parser, selection ABI, boot
decompressor, and updater checks have been executed against the rebuilt image
in Unicorn. **No physical mixer or USB audio device has run this image. Audio
streaming interoperability remains unproven.**

The rebuild preserves Roland's existing binaries and adds 1,132 bytes of newly
compiled C and assembly at three hooks. Ghidra pseudocode supports the analysis;
the project does not contain a recovered, complete Roland source tree. This
prototype does not implement the separate USB-B/iOS device-mode feature; see
`docs/DEVICE_PROBE.md` for that experiment.

The reviewed artifact is
`build/host-probe/MX1_UAC1_HOST_PROBE_UNTESTED.bin`. Its explicit experimental
filename differs from the updater's normal filename.

| Artifact | SHA-256 |
|---|---|
| Supplied original, 4,194,320 bytes | `26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e` |
| Rebuilt host candidate, 4,194,320 bytes | `516fc0a3baeaf179e018d7eff2eba376ba21eaed8b9e43a9b9860dce6f45dd58` |
| Decoded patched USB application, 226,000 bytes | `c3f01a8f51b8c5746fcf9a0f8b06a18de5a158ba300375e1c91dd676787d824c` |
| Compiled extension, 1,132 bytes | `dcf163c5f3edfa6f0ddde642b0aeb959e9c0e96a3b07982c9a819d251f06a937` |

The embedded application version remains `1.051132`. The build script requires
the exact original hash and checks every overwritten instruction byte before
applying a patch. These hashes and the patch manifest are recorded in
`build/host-probe/build-report.json`.

## Experimental device profile

These are the constraints implemented by `patches/uac1_host_probe.c` for newly
admitted, non-Roland devices. They describe the enumeration experiment, not a
claim that a real device matching them already works.

| Property | Implemented requirement |
|---|---|
| Bus speed | High speed, as reported by the original USB stack. Full-speed devices are rejected by the selection policy. |
| Streaming interface class | Audio class `0x01`, AudioStreaming subclass `0x02`, protocol `0x00` (UAC1). |
| Intended topology | Separate IN and OUT streaming interfaces. Each selected direction requires a validated inactive alternate 0 and active alternate 1. Other generic alternate settings are not selected. |
| Format | Type I PCM, two channels, four bytes per channel sample, 24 significant bits. |
| Sample rate | Exactly one discrete advertised rate: 44,100, 48,000, or 96,000 Hz. IN and OUT must advertise the same rate. |
| Data endpoint | Exactly one isochronous data endpoint per active alternate. Endpoint number must be nonzero, with no reserved address bits. |
| Synchronization attributes | OUT uses `bmAttributes=0x05`; IN uses `0x05` or `0x25`. These are asynchronous data profiles, with the latter IN form advertising implicit feedback. |
| Service interval | `bInterval=1`, corresponding to one high-speed microframe. |
| Packet capacity | No high-bandwidth transaction encoding; packet capacity is at most 1,023 bytes and at least 56 bytes for 44.1/48 kHz or 104 bytes for 96 kHz. The minimum includes room for one extra stereo sample. |
| Feedback | No separate feedback endpoint. `bSynchAddress` must be zero when present. Existing Roland transport behavior is retained; an independent feedback implementation has not been added. |
| Selection | Alternate 1 in both directions, starting with the first stereo pair. Generic MIDI is not enabled. |
| Configuration bounds | Descriptor chains must fit the declared total length, between 9 and 4,096 bytes. Interface numbers are limited to 0–7 by the wrapper. |

The classifier checks streaming descriptors. It does not implement a complete
AudioControl topology validator, every USB descriptor consistency rule, feature
unit controls, or device-specific initialization. Endpoint descriptors of at
least seven bytes are accepted; the optional synchronization-address check is
applied when a ninth byte is present. A device passing these checks still needs
hardware validation.

The prototype intentionally excludes packed 24-bit samples in three-byte
subframes, 16-bit samples, 32 significant bits, mono or multichannel formats,
continuous or multiple advertised sample rates, UAC2, explicit feedback
endpoints, adaptive/synchronous endpoint profiles, and full-speed operation.
The absence of a sample-rate `SET_CUR` implementation also matters: this
experiment is aimed at a single fixed-rate streaming profile, and matching the
device's actual clock to the MX-1's operating rate must be confirmed on hardware.

## How the patch works

The early driver registration is already a wildcard. Its registration record
at USB runtime address `0x6002b0ac` has all VID, PID, device-class, and
interface-class match flags clear. Running the original binder confirms that
generic audio interfaces can reach the mixer driver. No earlier registration
filter needs to be removed. The evidence and reproduction tool are described
in `research/container-binding.md`.

The restrictions addressed here occur later:

1. **Descriptor classification at `0x6000a11e`.** The stock classifier accepts
   Roland-style vendor-specific interface descriptors. The new hook delegates
   class `0xff` to an exact-prologue trampoline and adds the narrow standard
   UAC1 profile above. Standard alternate 0 has no endpoint direction, so the
   hook validates its matching alternate 1 before creating the inactive record.
2. **Configuration parsing at `0x6000a1e2`.** A wrapper checks descriptor-chain
   lengths, calls the original configuration parser through a second exact
   trampoline, and records the origin of accepted standard interfaces in
   otherwise reserved stream-record bytes. The marker follows descriptor order,
   including later records that overwrite a slot with the same alternate
   number. Both alternate 0 and alternate 1 must carry the standard-profile
   marker before a new device is selected.
3. **Selection callback pointer at `0x60007848`.** The replacement policy calls
   the original routine at `0x60007bf8` for VID `0x0582`. For other VIDs it
   requires the speed, counts, matching format/rate, and all four origin markers
   before enabling IN and OUT. This prevents an unrelated vendor-specific
   interface from bypassing the stricter UAC1 classifier through the stock
   parser's summarized format fields.

The alternate-origin markers are necessary. During independent review, a
vendor-specific 32-bit, interval-4 fixture was initially admitted by an earlier
version because its summarized fields resembled the supported format. A second
fixture exposed later descriptor overwrites, and duplicate alternate-1 records
could imitate a count of two without an alternate 0. The final build rejects
all of these regression fixtures. The review also tightened the executable
SRAM bound to avoid an existing USB buffer allocator.

The existing USB controller, isochronous scheduler, clock behavior, sample
conversion, MIDI handling, mixer routing, and user interface remain the original
firmware implementations. Successful selection therefore establishes a useful
entry point for hardware research; it does not establish correct audio transfer.

## Injection and memory checks

The original USB startup copies `0xbbe4` bytes from load address `0x6002b1f4`
to private SRAM starting at `0x01000300`. The extension is inserted immediately
after that load-image block, at decoded-image offset `0x36dd8`, and runs at
`0x0100bee4..0x0100c350` (end exclusive).

The builder increases that first copy length and moves the five later
initialized-data source literals at offsets `0x100`, `0x114`, `0x128`, `0x13c`,
and `0x150`. Runtime addresses of existing code and data are preserved. Tests
execute the original startup instructions for both images and compare the
existing initialized sections after relocation.

The usable reviewed USB gap ends at `0x0100d000`. An original table at decoded
USB offset `0x2820c`, consumed by `0x60007faa` and allocator setup `0x6000a548`,
reserves three 4-KiB regions beginning at `0x0100d000`, `0x0100e000`, and
`0x0100f000`. Both the linker and builder now reject extensions reaching those
regions. The current extension leaves 3,248 bytes below the first allocator
region.

The separate main-core device experiment uses a different address space. A
bounded static review of its candidate gap `0x0100f6a4..0x01010000` found no
equivalent allocator table or decoded direct reference into that interval. The
only gap-valued literal read as data was the zero-length startup section at its
lower bound; the next initialized section begins at `0x01010000`. This supports
that placement but does not prove the absence of every computed pointer or
hardware use. The USB-core allocator reservation must not be transferred
between cores merely because the numeric SRAM addresses overlap.

## Retired implementation

There is no current host-unlock builder, extension source or candidate binary.
The historical implementation and reproduction commands can be inspected at
[commit 6322349](https://github.com/karlsander/mxplus/tree/6322349).
The reports are preserved under `evidence/retired-probes-20261102/`. They describe
the old experiment, not mainline behavior or a maintained research build.

## What the tests establish

The exact candidate above passes all ten groups in
`analysis/host_probe_verification.json`:

| Evidence | Result |
|---|---|
| Original ARM startup | Extension copied into SRAM; existing initialized-data contents preserved. |
| Original Roland classifier fixture | All nine interfaces/alternates in the firmware's own descriptor tree produce identical classifier records through the trampoline. |
| Generic standard-profile fixtures | 44.1, 48, and 96 kHz reach the original parser, ABI builder, and replacement selection policy; the stock image leaves them unselected. |
| Unsupported profiles | Twenty format, speed, endpoint, and alternate-setting cases remain unselected. |
| Unequal IN/OUT rates | Rejected. |
| Unrelated vendor-class audio | Cannot inherit the new generic admission policy. |
| Origin/pairing regressions | Later vendor overwrite, duplicate alternate 1 without alternate 0, and reverse vendor/standard ordering are rejected. |
| Original Roland full parsing and selection | Matches the original result for the embedded MX-1 descriptor fixture. |
| Malformed new-classifier input | Five truncated or zero-length descriptor-chain fixtures are rejected. |
| Calling convention | Seven representative hook/trampoline paths preserve AAPCS registers r4–r11, stack pointer, and return address. |

The generic descriptors are synthetic fixtures, not descriptor captures from a
physical interface, and the AudioControl tree is deliberately minimal. Their
purpose is to exercise the actual firmware parser path. Equivalence on the
embedded Roland fixture does not establish regression coverage for every AIRA
product.

`analysis/container_host_candidate_verification.json` independently shows that
the original ARM LZSS decoder produces the complete modified application, the
original trailer parser and component-tag gate accept the rebuilt envelope,
the original write/readback loop processes exactly 704 blocks, and all four
original post-write checksums pass. The standard update range is
`[0x40000, 0x300000)`; bytes outside it, including both boot images and the
updater, are preserved. File/flash I/O and UI notifications are explicitly
stubbed during these tests. See `research/container.md` for addresses,
container fields, and the distinction between instruction execution and real
hardware acceptance.

Neither test set models USB-controller registers, interrupts, audio DMA,
clock drift, actual flash programming, power-loss recovery, or the complete
boot sequence. Instruction counts are not cycle counts or real-time performance
measurements. Preserving the boot/updater region does not by itself prove that
a failed application can be recovered through an accessible physical procedure.

## Hardware evidence that would move this forward

The most useful next step is to identify a real device and compare its complete
descriptors with the profile table before trying an update. Capture its device,
configuration, AudioControl, streaming, endpoint, and class-specific endpoint
descriptors, plus the negotiated bus speed. On a Linux inspection machine,
`lsusb -v -d VVVV:PPPP` and `lsusb -t` provide a useful first report. A raw
descriptor dump is preferable for a reproducible fixture.

Then obtain a known-good AIRA trace on the unmodified MX-1: enumeration, every
control request before streaming, selected alternates, endpoint intervals,
packet sizes, and start/stop behavior. This can reveal vendor initialization,
sample alignment, or clock assumptions absent from the static parser analysis.
An arbitrary class-compliant interface may advertise UAC2, packed samples,
multiple rates, or explicit feedback and therefore require additional driver
work rather than this particular probe.

Before a hardware update experiment, establish a recovery procedure on the
actual board and retain a verified complete original flash image. Board
identification, boot-entry access, and any debug/programming connection should
be documented from the physical unit. The recovery-related strings in the
firmware are leads, not a demonstrated recovery method.

For the first controlled streaming trial, verify setup and packet contents
before connecting audible outputs. Confirm that the device and mixer use the
same rate, inspect 24-bit sample alignment inside each four-byte subframe, and
measure packet-length variation and buffer occupancy over time. A short burst
of correct audio is insufficient to validate asynchronous clock behavior.
Longer operation, disconnect/reconnect, start/stop, all four ports, and normal
AIRA operation provide the evidence needed to extend this experiment into a
usable firmware feature.
