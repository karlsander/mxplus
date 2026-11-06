# FM-1 Bluetooth development bridge

The user authorized a dedicated FM-1 development firmware and MX-1 MIDI control
hooks on 2026-11-06. The intended connection is Mac ↔ Bluetooth MIDI ↔ FM-1 ↔
USB ↔ MX-1 HOST3. Both the Mac and MX-1 HOST ports are USB hosts; a direct cable
between them does not provide this device-side diagnostic connection.

The FM-1 bridge lives in [fm1-instrument/debug-bridge](https://github.com/karlsander/fm1-instrument/tree/codex/host-debug-bridge/debug-bridge).
Its instrument app is absent, but saved instrument objects and panel calibration
retain their IDs/addresses. It advertises the already measured FM-1 UAC1 profile.
Its Mac bench passed BLE control and simultaneous 44.1-kHz stereo USB input,
including separate left/right tones, muted boot/disconnect, and USB↔BLE command
forwarding with the Mac modeling MX-1 replies. This does not establish MX-1 audio.

## MX-1 hooks

The sole mainline image adds the following through the existing FM-1 MIDI path:

- Full host-audio counters and startup result, without the A1 report's 7-bit saturation.
- Cached OHCI registers, ED/head ITD, all 17 ITD statuses and 32 HCCA schedule entries.
- A request for a fresh snapshot, dispatched through the original HCD worker queue.
- Three converter modes: normal USB audio, muted input, and a local triangle tone.

Only the current matching FM-1 device on the receiving physical port can use
these hooks. No arbitrary addresses, writes, USB resets or flash operations are
exposed. Other devices retain their existing MIDI path. Incoming host clock and
transport remain blocked. A multi-transfer response temporarily holds queued
musical messages, so no channel message splits its SysEx. Existing user SysEx
finishes before a debug response starts. This is a bench control interface;
checksums are not authentication.

Mode 2 sends a quiet 220-Hz triangle (PCM16 peak 2048, about −24 dBFS) through
the original 44.1-to-96-kHz converter without depending on incoming USB samples.
It requires a claimed, running FM-1 audio endpoint. The ordinary packet consumer
continues draining. Mode 1 feeds silence through that converter. Modes expire
after 240,000 audio-task calls, nominally 60 seconds at the established 250-us
cadence. This watchdog is not a measured hardware timebase. Rebinding resets
the mode. Default mode 0 leaves the normal sample path intact.

The controller worker alone reads OHCI MMIO and HCCA; the MIDI task reads cached
RAM. A sequence counter catches concurrent software snapshot writes, but the
hardware may change between individual reads. The snapshot is not atomic with DMA.
Refresh uses the original request queue at app_usb runtime 6000c276 (decoded
0c276) and worker 6000bdc8 (decoded 0bdc8). The existing custom OHCI callback
recognizes the private callback/token and validates endpoint generation. It does
not send an additional USB transaction or alter the periodic schedule.

## Protocol v1

`F0 7D 44 42 01 01 seq op payload checksum F7`. Sum from 7D through checksum
is zero modulo 128. Payload uint32 values occupy five least-significant-first
7-bit bytes; fifth byte ≤15. Replies set op bit 6 and retain sequence.
Requests contain zero or one word (10 or 15 bytes); responses are ≤240 bytes.
One pending response/refresh per port. A second command is counted and dropped;
retry reads with a fresh sequence after timeout. New F0 resynchronizes incomplete
requests. Overlong private frames are consumed through F7, not forwarded as music.

| Op | Request | Reply words after result |
| --- | --- | --- |
| 1 | none | Status below |
| 2 | Page 0–2 | Page, snapshot sequence, raw fields below |
| 3 | Mode 0–2 | Selected mode |
| 4 | none | Fresh snapshot sequence after worker completion |

Result 0 succeeds; 1 is unsupported command/arguments; 2 is unavailable or a
concurrent snapshot. Refresh failures return the original absolute queue/worker
error. Invalid framing/checksum is silent and increments errors. Build B1 is 177.

Status after result: build, port, stage, result_code, controller, phase, control,
flags, cc, frame, packets, malformed, overflow, underrun, missed, dsp_errors,
wanted, claimed, generation, write_count, read_count, next_frame, close_frame,
cost, tail_slot, mode, command_errors, command_dropped. Port 2 is physical HOST3.
Stage/control/flags retain the meanings in [the audio report](USB_HOST_AUDIO.md).

Page 0, 36 raw words:

1. Controller context, custom ED address, custom ITD array address.
2. OHCI offsets 00, 04, 08, 0c, 10, 18, 1c, 30, 34, 38, 3c, 40, 44:
   revision, control, command status, interrupt status/enable, HCCA pointer,
   periodic current ED, done head, frame interval/remaining/number, periodic start,
   low-speed threshold.
3. HCCA words at 80 and 84 (frame/pad, done head).
4. ED control, tail, head, next.
5. Eight words of the owned head ITD (control, page, next, end, four PSW words),
   or zeros if head is outside the custom array.
6. Original controller context words 28, 2c, 30, 34, halfword 38 and word 53c:
   periodic-list bookkeeping and bandwidth evidence.

Page 1: 17 pairs of ITD control and PSW0. Page 2: all 32 HCCA periodic entries.
These are read-only diagnostics; numerical pointers are not accepted in requests.

## Integration and evidence

All changes belong to **app_usb**, independently of the main processor. Existing
resident addresses map as runtime = 60000000 + decoded offset; hot relocation is
original decoded 2b1f4 → runtime 01000300, length bbe4. The builder records every
changed original byte, callback target, inserted source, startup copy/zero and hash.

- Hot extension: 0100bee4..0100ca54, 2,928 bytes; writable hot state remains 1,472 bytes.
- Audio/debug code: 607f0000..607f1b8c, 7,052 bytes, within the existing 16-KiB code slot.
- Audio/DMA state remains 607f4000..607f9880; the A1 diagnostics remain 607f9880..607f9930.
- Bridge state follows at 607f9930..607fa464 (2,868 bytes). The whole 25,700-byte
  state stays in the already reserved 64-KiB SDRAM region; allocator bounds are unchanged.

The original main application, boot programs, updater and panel payload are
unchanged by this revision. The input hash and exact patch guards remain in force.
No new builder or alternate MX-1 candidate is introduced.

`tools/host_audio_verify.py` executes the actual compiled ARM parser, RX/TX hooks,
queue callback, snapshots, mode selection and watchdog. It checks malformed
requests, bounded multi-transfer replies, normal/user-SysEx continuity, replacement
device isolation, queue pressure, worker-only reads and 441 synthetic frames per
40 converter calls. USB delivery, RTOS queue delivery and DSP hardware are modeled.
The original queue/tree and converter regression checks also run.

When the user returns: install the verified mainline file as `MX1_UPD.BIN`, wait
for the updater's completion, restart normally, then connect FM-1 directly to
HOST3. Keep USB3 at Auto/USB3. The Mac can then read `mx-status`, `mx-refresh`
and `mx-page` over Bluetooth, with no manual hexadecimal transcription.
