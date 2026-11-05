# FM-1 USB-host audio experiment

The mainline candidate adds **FM-1 stereo audio input alongside host MIDI**.
Both tested candidates retained MIDI but produced no USB3 meter activity on
the MX-1. The current revision corrects an endpoint-address rejection found
after the first attempt, but a further failure remains; see
[the bench record](../evidence/fm1-host-audio-20261105/README.md#corrected-mx-1-audio-attempt).
It has instruction-level checks and a live FM-1 computer baseline, but no
successful physical MX-1 audio result yet.

The accepted profile is VID `1209`, PID `0001`, full-speed USB, UAC1 interface 1
alternate 1: stereo signed 16-bit PCM at 44,100 Hz, asynchronous IN endpoint
`84`, maximum 184 bytes per millisecond. MIDI remains on interface 2 alternate 0.
The installed FM-1 advertises no USB audio playback interface. Other generic
audio profiles remain disabled; the existing Roland path remains available.

The FM-1 does not need to run at 96 kHz. Its received samples are converted to
the original MX-1 host converter's four-byte format and fed to the existing
internal 96-kHz conversion path. The USB-B system-rate setting is separate.
Actual behavior at all three system rates still needs bench testing.

## Computer baseline

The [live capture](../evidence/fm1-host-audio-20261105/README.md) matches the
earlier descriptor fixture byte for byte. macOS opened stereo 16-bit/44.1-kHz
input; MIDI notes sent to the `Felucca` destination produced nonzero audio.
The endpoint accepted sampling-frequency `GET_CUR` and `SET_CUR` at 44,100 Hz.
Its short-run clock estimate was slightly above nominal, supporting the need
to preserve actual packet sample counts and clock-drift correction.

The user had already confirmed MX-1 MIDI output to this FM-1 with candidate
`253645edb92a09c7b0d100da01f57d5127834c109b2ad499332645487a7a1d14`.
That result does not validate audio or the changed candidate.

## Transport and ownership

The stock full-speed OHCI driver has incomplete isochronous submission and
completion paths. The extension supplies a bounded input transport; it does
not send audio through the MIDI bulk API or reinterpret EHCI descriptors.

The manager selects the endpoint rate and streaming alternate. The original
HCD queue starts the transport in the OHCI worker. That worker owns periodic
list insertion, bandwidth accounting, completion and unlinking. Each port has
17 aligned ISO descriptors: 16 scheduled transfers and one queue tail. Each
descriptor receives one full-speed frame. Original general/MIDI completions
are separated from custom ISO entries and passed to the original handler.

Valid short packets, including 44/45-frame packets, retain their actual sample
counts. This first profile accepts 40–46 stereo frames per packet. Corrupt,
oversized, fractional-frame and very short packets are discarded. The bounded
eight-packet queue drops new packets on overflow; counters record overflow,
starvation, missed schedules, malformed packets and DSP failures.

The original audio task consumes one quarter of each packet per 250-us call.
Signed16 samples become left-aligned signed32 before the original converter.
The original 44.1-kHz smoothing and adaptive conversion remain in place. Two
packets are buffered before consuming; starvation supplies silence and waits
for that buffer again. This is not a measured end-to-end latency specification.

Disconnect publishes a stop request without retrying through freed USB
objects. The next completion unlinks the endpoint in the HCD worker. Descriptor
storage remains owned until two frame boundaries have passed, neither hardware
nor HCCA has pending done entries, and the controller no longer visits the ED.
Original controller teardown removes custom endpoints before freeing lists.
An unresolved controller fault can retain the reservation until reset; automatic
recovery from every hardware/controller error is not established.

## USB-processor placement and binary changes

All addresses in this section belong to **app_usb**. Main-processor code remains
byte-identical to the preceding candidate. Boot programs, updater and panel
payload remain unchanged. Only `tools/build_firmware.py` produces firmware.

| Runtime interval, end exclusive | Use |
| --- | --- |
| `0100bee4..0100ca1c` | 2,872-byte MIDI extension and original-function trampolines |
| `01017868..01017e28` | Existing 1,472-byte MIDI state |
| `607f0000..607f0d80` | 3,456-byte audio extension |
| `607f4000..607f9880` | 22,656-byte audio state, descriptors and packet buffers |

The USB processor's original general heap spans `604b1178..60800000`.
The builder reduces its upper bound to `607f0000`, reserving 64 KiB in existing
SDRAM. It guards the old end at decoded offset `3750` and unchanged base at
`3754`. Original heap-creation instructions execute in the verifier. The
original MPU already permits this memory's access and execution; no MPU rule
is relaxed. The main processor's retired generator reservation is unrelated.

The formerly empty startup zero at literals `f0/f4` initializes audio state.
The formerly empty copy at `10c/110/114` loads audio code. Existing stack
initialization and nonempty copy destinations remain unchanged. The code is
appended after relocated USB initialized data; its exact source is recorded in
`build/mainline/build-report.json` under `host_midi.audio_source`.

| USB decoded offset | Runtime | Change |
| --- | --- | --- |
| `28278`, `2827c` | `60028278`, `6002827c` | Bind/remove callbacks retain original manager handling and add audio ownership |
| `28288` | `60028288` | Existing MIDI setup wrapper also selects FM-1 audio |
| `2828c` | `6002828c` | Audio-ready event; original handler retained for other devices |
| `13c74` | `60013c74` | Original OHCI binding plus request/cancel/event/reset wrappers |
| `13804` | `60013804` | Split ISO/general completion lists; original general handler retained |
| `8340` | `60008340` | Close custom audio without touching unused EHCI descriptors |
| `33b54` | `01008c60` | Original audio task followed by FM-1 packet consumption |

Original hot code relocates from decoded `2b1f4` to runtime `01000300`.
The build report records exact overwritten/new bytes, branch targets, sources,
section bounds and component/container checksums. `usb-host-audio.load.bin` is
an extension artifact, not an independently flashable image.

## Verification and bench procedure

`tools/host_audio_verify.py` executes ARM code for descriptor rejection,
combined MIDI/audio setup, original alternate switching and binding, heap
creation, OHCI scheduler admission, aligned/page-crossing descriptors, frame
wraparound, short packets, signed stereo conversion, mixed completion lists,
unlink/retirement/reopen, multiple periodic endpoints, controller teardown,
and packet pacing with source-clock variation. Original converter initialization,
audio-task dispatch and input conversion also execute with explicit DSP/MMIO
models; checks cover sample order and buffer boundaries, not interpolation.
The original startup loops and MPU setup also execute in the MIDI verifier.
USB DMA, RTOS delivery and DSP hardware are explicit modeled boundaries.
The full reproduction gate checks this evidence against the actual USB image
and both inserted USB code artifacts. No hardware probe runs in reproduction.

For the authorized first MX-1 test:

1. Retain the last working image and settings backup. Copy the candidate as
   **`MX1_UPD.BIN`**, without a hyphen, to the updater volume. The original
   updater's filename literal is at decoded `59c4`, runtime `600059c4`.
2. Safely eject and disconnect USB, press TAP, wait for `Fin`, then restart with
   monitoring down. Check normal analog mixing first.
3. Connect the FM-1 directly to HOST 3, which supplies bus power. Record the
   exact wiring, power arrangement, system rate and candidate hash.
4. Trigger notes as in the successful MIDI test. Raise the USB3 channel and
   monitoring gradually. Check both channels, note tails, clipping and clicks.
5. Stop/start notes, unplug/reconnect the FM-1, and restart with it connected.
   Confirm MIDI still operates during audio. Record any failure and its trigger.
6. After a short successful run, test sustained audio, other supported system
   rates, stereo separation, and coexistence with a Roland device and USB-B.

Retain `UNTESTED` until these observations exist. A passing build or computer
baseline does not establish MX-1 timing, sound quality, broad interoperability
or failed-application recovery.
