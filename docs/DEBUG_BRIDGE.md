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
forwarding with the Mac modeling MX-1 replies. The first real HOST3 run exposed
EHCI controller 1, no audio packet progress and timed-out MX-1 commands.
[Live evidence and original-instruction findings](../evidence/fm1-ehci-debug-20261106/README.md).

## MX-1 hooks

The sole mainline image adds the following through the existing FM-1 MIDI path:

- Full host-audio counters and startup result, without the A1 report's 7-bit saturation.
- Cached OHCI registers, ED/head ITD, all 17 ITD statuses and 32 HCCA schedule entries.
- A request for a fresh snapshot, dispatched through the original HCD worker queue.
- Three converter modes: normal USB audio, muted input, and a local triangle tone.
- Cached device/parent-hub topology and MIDI RX/TX software state.
- Individually queued rate, alternate and endpoint-lookup probes on EHCI.
- Unsolicited TX telemetry to diagnose a failed MIDI IN command direction.

Build B2 pauses automatic audio startup on EHCI before any audio controls,
lookup, DSP initialization or ISO submission. The existing ISO transport is
OHCI-only; it cannot serve the observed HOST3 connection. B2 isolates MIDI and
lets the Mac exercise setup steps independently. FM-1 stays on bridge B1.

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
| 2 | Page 0–4 | Pages 0–2: page, snapshot sequence, raw fields; pages 3–4: page, fields |
| 3 | Mode 0–2 | Selected mode |
| 4 | none | Fresh snapshot sequence after worker completion |
| 5 | Step 1–4 | Accepted step; completion is reported by status |

Result 0 succeeds; 1 is unsupported command/arguments; 2 is unavailable or a
concurrent snapshot. Refresh failures return the original absolute queue/worker
error. Probe queue failure is result 3. Invalid framing/checksum is silent and
increments errors. B1 is 177; the current MX-1 B2 is 178.

Status after result: build, port, stage, result_code, controller, phase, control,
flags, cc, frame, packets, malformed, overflow, underrun, missed, dsp_errors,
wanted, claimed, generation, write_count, read_count, next_frame, close_frame,
cost, tail_slot, mode, command_errors, command_dropped, probe_pending, probe_done,
probe_result. The final three fields are added in B2. probe_result retains the
signed return code in uint32 representation. Port 2 is physical HOST3.
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
Page 3: 12 cached topology words: controller index, device address, raw speed,
configuration; parent-hub pointer, parent-device pointer; parent controller,
address, speed, VID, PID; one-based downstream port. Raw speed 0 is full-speed,
400 hex is high-speed. Zero parent fields mean no parent device was recorded.
No hardware register is read for this page.

Page 4: 24 MIDI software words. First ten for RX, next ten for TX: endpoint,
busy, ready, last completion result, completed bytes, requested bytes, managed,
fault, generation, in-flight generation. Final four: ordinary queue count,
urgent queue count, dropped count, errors. Tasks can advance between fields;
this is not an atomic snapshot. A submission failure sets fault/errors but the
last completion result may still describe an earlier transfer.

Operation 5 accepts only the current EHCI FM-1 with no claimed audio stream.
Step 1 sends endpoint SET_CUR 44100; 2 selects IF1 alt1; 3 looks up and validates
EP84 without submitting a transfer; 4 selects IF1 alt0. RX queues a private event
5 (third word 3242444d hex), and the manager performs the synchronous API call.
The response means accepted, not completed. Poll status before sending the next
step. Stages 31–34 hex mean executing a step; 39–3C mean returned. A subsequent
interface bind can restore stage 48; probe_done/result still retain the outcome.
One pending step per device. Rebinding setup resets the diagnostic session.

Unsolicited op 7E hex, sequence 0, contains seven words: result 0, build 178,
startup stage, RX flags, TX flags, last RX result, last TX result. Flags are busy
in bit 0, ready in bit 1, fault in bits 8 onward. This fits in one 60-byte USB
MIDI transfer and is emitted every 512 eligible TX polls, behind user SysEx.
The interval is not a measured clock. It cannot report through a failed TX path.
FM-1 B1 forwards it to BLE; the Mac client records it as a reply in the raw log.

These readouts accept no arbitrary addresses. The probe operations do not
submit ISO, write controller registers, reset USB or change flash.

## Integration and evidence

All changes belong to **app_usb**, independently of the main processor. Existing
resident addresses map as runtime = 60000000 + decoded offset; hot relocation is
original decoded 2b1f4 → runtime 01000300, length bbe4. The builder records every
changed original byte, callback target, inserted source, startup copy/zero and hash.

- Hot extension: 0100bee4..0100ca54, 2,928 bytes; writable hot state remains 1,472 bytes.
- Audio/debug code: 607f0000..607f206c, 8,300 bytes, within the existing 16-KiB code slot.
- Audio/DMA state remains 607f4000..607f9880; the A1 diagnostics remain 607f9880..607f9930.
- Bridge state follows at 607f9930..607fa564 (3,124 bytes). The whole 25,956-byte
  state stays in the already reserved 64-KiB SDRAM region; allocator bounds are unchanged.

The original main application, boot programs, updater and panel payload are
unchanged by this revision. The input hash and exact patch guards remain in force.
No new builder or alternate MX-1 candidate is introduced.

`tools/host_audio_verify.py` executes the actual compiled ARM parser, RX/TX hooks,
queue callback, snapshots, mode selection and watchdog. It checks malformed
requests, bounded multi-transfer replies, normal/user-SysEx continuity, replacement
device isolation, queue pressure, worker-only reads and 441 synthetic frames per
40 converter calls. USB delivery, RTOS queue delivery and DSP hardware are modeled.
The original queue/tree and converter regression checks also run. B2 adds actual
original controller binding, deferred bind-event delivery, EHCI startup rejection,
stepwise manager probes/failure results, topology/MIDI pages and one-transfer
unsolicited telemetry. Endpoint lookup and on-wire control remain modeled.

Install the verified mainline file as `MX1_UPD.BIN`, wait
for the updater's completion, restart normally, then connect FM-1 directly to
HOST3. Keep USB3 at Auto/USB3. Read status and pages 3/4 first; if those work,
run `mx-probe 1`, `mx-probe 2`, then `mx-probe 3`, checking status and FM-1 trace
between steps. `mx-probe 4` returns to alt0. OHCI MMIO pages and converter modes
remain unavailable on EHCI; no audio packet progress is expected from B2.
