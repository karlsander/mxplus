# Experimental MX-1 USB-B UAC2 candidate

## Status

`build/device-probe/MX1_UAC2_DEVICE_PROBE_UNTESTED.bin` is a rebuilt research
candidate for the MX-1 computer Type-B port. It contains compiled new code,
new audio descriptors, and a narrowly targeted capture-startup change.
The original initializer, control-dispatch, descriptor-programming, and
startup-copy code have been executed with the extension in a CPU emulator.
The candidate has **not been flashed to an MX-1 or tested with an iPhone,
iPad, Mac, or other physical USB host**.

This is a concrete implementation experiment, not a completed compatible
firmware release. It should remain clearly separated from the original
firmware and from the independent USB1–4 host-port experiment.

| Item | Identity |
| --- | --- |
| Original updater SHA256 | `26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e` |
| Candidate updater SHA256 | `b17f9005dd2b32b9fd89ccdd07c3a2ef0dda0854fb67ad5732a76390cc005d57` |
| Candidate decoded main-app SHA256 | `59bf5d2e7d206315cbc6ae59e8072bff410ea3c2ff850062da5f405148642a9e` |
| New compiled extension | 900 bytes, Cortex-M3 Thumb, code and writable data |
| Extension placement | `0x0100f6a4` through `0x0100fa27` |
| New configuration descriptor | 355 bytes |

The build report is the authoritative source for a regenerated candidate's
hashes and symbol addresses. An image produced by a different build must be
checked against its own report.

## What the candidate changes

The normal USB initializer at `0x6000d980` redirects to
`mx1_uac2_initialize(sample_rate)`. The wrapper retains the actual rate
selected on the mixer, configures the new descriptor, runs the original
descriptor/class initialization, registers the new class-control handler,
then starts the original USB stack.

The high-speed configuration advertises a UAC2 AudioControl graph with a
shared fixed clock, plus the existing two audio streaming interfaces:

| Interface / alternate | Direction from computer | Channels | Endpoint |
| --- | --- | ---: | --- |
| 1 / 0 | Inactive playback | 0 | None |
| 1 / 1 | OUT, computer to mixer | 18 | `0x0d` |
| 1 / 2 | OUT, computer to mixer | 2 | `0x0d` |
| 2 / 0 | Inactive capture | 0 | None |
| 2 / 1 | IN, mixer to computer | 18 | `0x8e` |
| 2 / 2 | IN, mixer to computer | 2 | `0x8e` |

The original four-byte sample containers, 24-bit resolution, endpoint
addresses, alternate numbers, and high-speed service interval remain. The
original vendor MIDI interface 3 is retained byte for byte. This candidate
does not make MIDI class compliant.

The new read-only clock entity reports 44,100, 48,000, or 96,000 Hz according
to the existing mixer setting. It handles CUR, RANGE, the two-byte RANGE
header probe, and clock-validity CUR. It rejects unsupported writes and
malformed requests with an EP0 stall. The validity response reflects a valid
configured rate; it is not a measured hardware PLL-lock indication.

The original capture pump required playback availability before advancing
two capture startup states. At runtime `0x01009a06`, the candidate changes
`mov.w r12,#0` to `mov.w r12,#1`. The pump still writes playback silence when
OUT data is absent, and retains its IN-readiness, priming, phase, and commit
checks. This change addresses the identified software startup dependency.
It does not prove that the physical USB peripheral will produce all needed
clock and FIFO conditions before playback starts.

## What the offline checks establish

### Compiled ARM integration

`tools/device_probe_verify.py` executes the candidate through the original
normal initializer entry point. Eight groups pass:

1. The original ARM startup copies the extension and preserves all original
   initialized data outside the extended hot-code section.
2. The new initializer registers the real handler after the original callback
   array is cleared, preserves the current sample rate, and writes correct
   packet maxima at all three rates.
3. Eighty-four positive class-control cases pass through the original
   dispatcher and callback wrapper into the actual compiled handler.
4. Ten negative request cases execute the original EP0 stall register
   routine, reset the control state, and clear the setup packet.
5. The original descriptor dispatcher returns the new device/configuration
   data and correctly follows high-speed/full-speed and other-speed pointers.
6. The original descriptor walker produces **identical endpoint hardware
   table writes** for the stock configuration and new UAC2 configuration at
   three rates and both bus-speed selections. This includes the retained MIDI
   endpoints and alternate settings.
7. The compiled initializer reports failure for invalid rates and injected
   failures in each stock initialization stage.
8. The original backup initializer produces the same descriptor and callback
   tables with the original and candidate applications.

Only RTOS task creation, low-level hardware start, and EP0 reply delivery into
the real FIFO are stubbed for these checks. The adapter's supplied reply
pointer, length, flags, and bytes are inspected. The original register-level
stall routine actually executes in mapped memory. These checks establish
code integration and control flow, not physical enumeration.

Detailed results: `build/device-probe/arm-verification.json`.

### Original audio pump execution

`sources/hardware/uac2_pump_harness.py` executes the original 732-byte Thumb
audio pump with an explicit model of the relevant readiness/phase inputs.
Under that model:

- The original capture-only path writes no IN data and remains in startup
  state 1.
- The candidate instruction permits silence priming and normal capture state
  4 without a single OUT FIFO read.
- Original and candidate traces are identical when playback already starts
  first. Both keep capturing when playback subsequently stops.
- Capture can stop and restart when modeled IN readiness disappears and
  returns.
- Stereo capture uses two words per active tick.
- Mixed 18-channel OUT/two-channel IN and two-channel OUT/18-channel IN
  exercise independent alternate-selection branches with unchanged original
  versus candidate duplex traces.

The model supplies USB readiness and phase inputs, and uses an identity
sample-conversion stub. It does not emulate FIFO capacity, real packets,
timing, converter scaling, or endpoint-reset side effects. Mixed-alternate
tests therefore establish independent code branches, not validated physical
packet-boundary handling.

Detailed results: `sources/hardware/uac2_pump_harness_results.json`.

### New control logic

The native C harness independently passed 4,881 request cases, including all
response lengths from 0 through 512, three rates, malformed requests, and
registration/start error handling. This larger boundary test complements the
compiled ARM integration test.

## Rebuild and reproduce

The scripts require the original supplied firmware. The build is restricted
by its exact SHA256 and checks the expected bytes at every patch point.

From the project directory, using its local virtual environment and the
unchanged packaged input:

```bash
.venv/bin/python tools/build_device_probe.py inputs/MX1_UPD.original.bin \
  --output build/device-probe

.venv/bin/python tools/device_probe_verify.py inputs/MX1_UPD.original.bin \
  --build build/device-probe \
  --output build/device-probe/arm-verification.json

.venv/bin/python sources/hardware/uac2_pump_harness.py
```

The native logic test uses the system C compiler:

```bash
gcc -std=c11 -Wall -Wextra -Werror -O2 -DMX1_UAC2_NATIVE_TEST \
  sources/hardware/uac2_adapter.c \
  sources/hardware/uac2_adapter_native_test.c \
  -o sources/hardware/uac2_adapter_native_test
sources/hardware/uac2_adapter_native_test
```

The compiler used for this candidate is `ziglang` 0.13.0 targeting Cortex-M3
Thumb with ReleaseSmall optimization and no LTO. The linker bounds the
extension below the original initialized SRAM at `0x01010000`. The builder
extends the existing startup copy and adjusts subsequent initialized-data
source addresses. It repackages only the main application; the host-port
application, boot blocks, updater, and sub-CPU component remain original.

The first build uses a simple lossless literal-only encoder, so compressed
main-application storage grows even though the compiled extension is only
900 bytes. The resulting component still fits its original container slot.
Container-format checks and execution of the old loader/updater are separate
from the USB checks documented here.

`research/device-reproducibility.md` lists every Python dependency, the
original-image extraction/map prerequisites for the pump test, and the
observed result of a fresh build in a separate compiler-cache directory.

## What remains to be established on hardware

The first unanswered question is whether IN tokens and the ESC2 phase
generator yield the modeled readiness conditions without preceding OUT
traffic. A real capture-first bus trace is decisive. A successful UAC2
descriptor response alone would not establish that audio starts.

Further validation must cover all three sample rates, all four independent
capture/playback alternate combinations, sample bit alignment and level,
packet lengths and jitter, long-running duplex audio, stop/restart, USB
reset/disconnect/reconnect, MIDI, and backup mode. Full-speed operation
retains the stock 45-byte vendor configuration with no audio endpoints; this
candidate only attempts high-speed audio.

The experiment also retains Roland's VID/PID. A Mac with the Roland driver
installed may bind differently from a class-only host, and driver caches may
affect comparisons. No inference about physical Apple driver behavior should
be drawn from the CPU tests.

The current evidence makes the candidate reviewable and explains exactly
which missing behavior it attempts to add. Successful flashing, recovery
after a failed flash, class compliance, and useful iOS audio are not yet
demonstrated.

## Source map

| File | Purpose |
| --- | --- |
| `patches/uac2_device_probe.c` | New normal-mode initializer and live packet-size setup |
| `patches/uac2_device.ld` | Bounded SRAM placement |
| `sources/hardware/uac2_adapter.c` | Fixed-clock class-control implementation and stock-call bindings |
| `tools/uac2_design.py` | UAC2 descriptor graph generation |
| `tools/build_device_probe.py` | Version-guarded compilation, patching, relocation, and container rebuild |
| `tools/device_probe_verify.py` | Actual ARM integration and descriptor-table comparison |
| `research/device-control.md` | Original functions, ABIs, registers, and instruction-level evidence |
| `research/usb-compatibility.md` | USB standards, Apple behavior, and Linux/Roland context |
