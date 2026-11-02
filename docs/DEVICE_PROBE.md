# Experimental MX-1 USB-B UAC2 candidate

## Status

USB-B UAC2 is part of the sole [mainline build](MAINLINE.md), not a separate
candidate. The preceding mainline (`88457445…`) passed a user-reported
iPhone/AUM audio round trip over a direct USB-B–to–USB-C cable: analog input,
AUM effect, then return to another mixer channel. See the
[hardware record](../evidence/iphone-aum-20261102/README.md) for scope and unknowns.
Generators and their SELECT editor have been removed from the active build.
Their failures are documented in [the DSP handoff](GENERATOR_RESEARCH.md). The retired
standalone candidate's mutable SRAM placement was invalid under the stock MPU;
mainline uses separate writable descriptor/rate/reply storage. Historical build
identities are in `evidence/retired-probes-20261102/`.

The [adversarial review](ADVERSARIAL_REVIEW.md) reproduced a stereo playback
accounting defect in that image. The current `dacb12ae…` candidate contains
the [packet fix](USB_PACKET_FIX.md), with finite-packet and alternate-transition
instruction tests. This changed image has not been tested on hardware.

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
two capture startup states. The corrected playback block preserves `r12=1`
from the original prologue, retaining capture-first priming while supplying
playback silence when OUT data is absent. Capture's original IN-readiness,
phase and commit checks remain unchanged. Physical capture-first clock/FIFO
conditions still require a bus trace.

Playback accounting now follows the selected frame size, and buffered tails
are discarded when OUT changes alternate. The patch remains inside the
original callback's playback window; it adds no executable memory reservation.
See [placement, ABI and packet evidence](USB_PACKET_FIX.md).

## What the offline checks establish

### Compiled ARM integration

`tools/usb_audio_verify.py` executes the candidate through the original
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

Detailed results: `build/mainline/usb-verification.json`.

### Historical capture-first control-flow experiment

`sources/hardware/uac2_pump_harness.py` executes the original 732-byte Thumb
audio pump with an explicit model of the relevant readiness/phase inputs.
It tests the original and one-instruction capture-first fixture, not the current
complete playback fix. Under that model:

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

### Current candidate packet execution

`tools/usb_packet_verify.py` executes the current callback with finite packets,
sample-order assertions and packet-boundary failures. Seven groups cover
stereo/18-channel and mixed alternates at all three rates, short/malformed
packets, conversion edge cases, capture-first, restart and changes during
buffered playback. The 18-channel traces match the predecessor. This verifier
runs within mainline reproduction; its report is
`build/mainline/packet-verification.json`. Peripheral readiness, conversion and
alternate-change flushing remain explicit model boundaries.

### New control logic

The native C harness independently passed 4,881 request cases, including all
response lengths from 0 through 512, three rates, malformed requests, and
registration/start error handling. This larger boundary test complements the
compiled ARM integration test.

## Rebuild and reproduce

Run `tools/reproduce.py` followed by `tools/check_reproduction.py --check-committed`
with the pinned project Python environment. The only builder is
`tools/build_firmware.py`; USB instruction evidence is
`build/mainline/usb-verification.json`. The compiled initializer and controls
run with code SRAM write protection enforced. See [mainline integration](MAINLINE.md).

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

The iPhone/AUM observation establishes one useful duplex path. It does not
establish every advertised alternate or universal class compliance. TAP
rollback has worked after the observed application failures; other recovery
classes remain unverified. The packet fix still needs physical acceptance.

## Source map

- `patches/usb_audio.c`: initializer and mutable descriptor packet-size setup.
- `patches/mainline.ld`: shared code and writable-data reservations.
- `sources/hardware/uac2_adapter.c`: clock controls and original-call bindings.
- `tools/uac2_design.py`: descriptor generation.
- `tools/build_firmware.py`: sole firmware builder.
- `tools/usb_audio_verify.py`: USB instruction tests within mainline verification.
- `patches/usb_playback.S`: bounded playback replacement; capture stays original.
- `tools/usb_packet_verify.py`: finite-packet and transition instruction tests.
