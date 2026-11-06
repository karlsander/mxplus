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
- Explicit EHCI start/stop, siTD status, packet counts and stereo sample peaks.

Build B5 retained the pause of automatic audio startup on EHCI. It added an
explicit start/stop experiment for the observed HOST3 connection, with EHCI
pages and sample-peak counters. The working B4 MIDI path remains. FM-1 stays
on bridge B1. [Transport, admission and ownership](../research/fm1-ehci.md).
B5's clean bench advanced the FM-1 packet counter by five, then stopped on one
MX converter error before any MX accepted PCM. B6 adds transport-only probe 7,
mode 3 and cached converter page 8 to isolate that failure. It also publishes
running phase only after all sixteen siTDs are built. [B6 evidence](../evidence/fm1-converter-b6-20261106/README.md).

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
| 2 | Page 0–8 | Pages 0–2 and 5–8: page, snapshot sequence, raw fields; pages 3–4: page, fields |
| 3 | Mode 0–3 | Selected mode |
| 4 | none | Fresh snapshot sequence after worker completion |
| 5 | Step 1–7 | Accepted step; completion is reported by status |

B6 step 7 initializes the original converter context but starts with converter
submission bypassed. Mode 3 drains PCM without submitting it to the converter
and expires by stopping. Modes 0/1/2 require explicit selection to leave that bypass.

Result 0 succeeds; 1 is unsupported command/arguments; 2 is unavailable or a
concurrent snapshot. Refresh failures return the original absolute queue/worker
error. Probe queue failure is result 3. Invalid framing/checksum is silent and
increments errors. B1 is 177, B2 is 178, B3 is 179, B4 is 180, B5 is 181 and current MX-1 B6 is 182.

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

Operation 5 accepts only the current EHCI FM-1. Steps 1–5 and 7 require no claimed
audio stream; step 6 is also available while running or retiring.
Step 1 sends endpoint SET_CUR 44100; 2 selects IF1 alt1; 3 looks up and validates
EP84 without submitting a transfer; 4 selects IF1 alt0. RX queues a private event
5 (third word 3242444d hex), and the manager performs the synchronous API call.
The response means accepted, not completed. Poll status before sending the next
step. Stages 31–34 hex mean executing a step; 39–3C mean returned. A subsequent
interface bind can restore stage 48; probe_done/result still retain the outcome.
Step 5 queues input start to the HCD worker after probes 1/2/3. Its probe result
only confirms queue acceptance; wait for phase 2/stage 56 to establish a running
transport. Step 6 publishes
stop, clears audio readiness and stops the converter in the manager. The HCD
retains DMA ownership until retirement. Wait for phase/claimed zero before
step 4 (alt0) or another start. Steps 5/6/7 use stages 35/36/37 and 3D/3E/3F before the
worker's own stage. One pending step per device. Rebinding setup resets the session.

Pages 5–7 are the EHCI counterparts of OHCI pages 0–2. They are available after
a guarded start attempt; controller mismatches and concurrent writes return 2.
Page 5 contains 36 words: context, operational registers, active table,
HCCPARAMS, USBCMD, USBSTS, USBINTR, FRINDEX, CTRLDSSEGMENT, PERIODICLISTBASE,
ASYNCLISTADDR, CONFIGFLAG, phase, port, linked-slot mask, deadline tick,
last-service tick, poll pending, service count, stop reason, rejected link,
maximum chain length, next frame, oldest slot, accepted packets, malformed,
missed, peak L, peak R, nonzero packets, last byte count, last siTD status,
endpoint word, split mask, generation, stock-audio mask (4000bbb0; reserved zero in B5).
Page 6 contains 16 pairs of scheduled frame/current siTD status, then two zeros.
Page 7 contains 16 pairs of saved original frame-list head/last completion status.
Fields can change with hardware between reads; the sequence protects only
against concurrent software snapshot publication.

Page 8 is an audio-task snapshot with sequence and 35 data words: call count,
success count, signed last return in uint32, entry gate value (ffffffff if its
pointer cannot be read within the fixed DSP data range), submitted frame count;
then tick, port, mode, phase, controller, context address, context offsets
00/04/08/0c/10/14/18/20/24/28/2c/30/34, global words 6002b094/98/9c,
smoothing offsets 00/10/30/40/50/60 relative to 010157f8+port*4,
DSP result word 40101000 and stock mask 4000bbb0. The audio task captures every
converter call (including failure) and every 32 ticks in mode 3. This page
does not execute MMIO reads in the MIDI task. Its context/flags are diagnostic
observations, not independently verified DSP-ready or sample-rate indicators.

EHCI stages: 50 topology rejection, 51 controller/table configuration,
52 periodic admission, 56 running, 57 stop, 58 run expired, 59 controller fault
or teardown, 5A worker gap/other periodic activity, 5B insertion admission,
5C changed link/table. Phase 4 quarantines DMA ownership until reboot when
destroy did not establish a halted controller. On EHCI, status control is raw
USBCMD, flags is the linked-slot mask and cc is the last siTD status byte.

Unsolicited op 7E hex, sequence 0, contains seven words: result 0, build 182,
startup stage, RX flags, TX flags, last RX result, last TX result. Flags are busy
in bit 0, ready in bit 1, fault in bits 8 onward. This fits in one 60-byte USB
MIDI transfer. B3 wakes the TX task every 4,096 audio-task calls, even with no
claimed audio stream. A report is eligible 4,096 calls after the previous report
or completed reply (nominally about one second). User SysEx and queued replies
take precedence. Missed intervals coalesce; there is no catch-up burst. The
interval is not a measured clock. It cannot report through a failed TX path.
Publishing a command reply also wakes TX, without needing musical traffic.
FM-1 B1 forwards it to BLE; the Mac client records it as a reply in the raw log.

These readouts accept no arbitrary addresses. Probe 5 submits the bounded
split-ISO experiment; no command writes controller registers, resets USB or
changes flash.

## Integration and evidence

All changes belong to **app_usb**, independently of the main processor. Existing
resident addresses map as runtime = 60000000 + decoded offset; hot relocation is
original decoded 2b1f4 → runtime 01000300, length bbe4. The builder records every
changed original byte, callback target, inserted source, startup copy/zero and hash.

- Hot extension: 0100bee4..0100cad4, 3,056 bytes; writable hot state remains 1,472 bytes.
- Audio/debug code: 607f0000..607f3194, 12,692 bytes, within the existing 16-KiB code slot.
- Audio/DMA state remains 607f4000..607f9880; the A1 diagnostics remain 607f9880..607f9930.
- Bridge state follows at 607f9930..607fa564 (3,124 bytes); EHCI state adds 264
  bytes at 607fa564..607fa66c. B6 adds 576 bytes of converter snapshots at
  607fa66c..607fa8ac. The whole 26,796-byte
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
between steps. `mx-probe 7` starts B6 in transport-only mode; pages 5–8 then show
EHCI and converter state. Select mode 0 explicitly to test the converter, or
mode 2 for its local tone. `mx-probe 5` starts normal conversion directly.
Modes become available when phase is 2. `mx-probe 6` stops it;
wait for retirement before `mx-probe 4` returns to alt0. Leave other host-audio
devices disconnected for this experiment. B5 stopped before accepted PCM or
sound; B6 has not yet been installed.


B2's physical run retained alt0 but commands still timed out. B3 fixes two
independently established defects: the MIDI IN request omitted the original
short-packet flag, and debug replies did not signal the TX task. It also replaces
the idle TX-poll heartbeat with the audio-task wake cadence described above.
[Before/after evidence and test boundaries](../evidence/fm1-midi-bridge-b3-20261106/README.md).
B3 was installed and its startup heartbeat captured build 179, previous RX −7
and previous TX −20. Commands still timed out; last results survive reconnect.
B4 removes the stock per-transfer alarm only for MIDI OUT belonging to the
matched FM-1 debug session. The original five-alarm pool can produce −20 before
HCD submission; actual live exhaustion has not been established. Untimed writes
retain their buffer until completion or stock disconnect cancellation, with no
new watchdog or retry. Other generic MIDI OUT keeps timeout 100.
[B4 experiment and actual-instruction tests](../evidence/fm1-midi-timeout-b4-20261106/README.md).
The FM-1 firmware and base Mac client are unchanged. B4 passed the first physical
round trip: status, topology, MIDI state and all four manager setup probes.
Continuous telemetry was captured for approximately 31 seconds, with zero
MX-1 MIDI faults/errors. Audio stayed at zero packets; the test returned AS
to alt0. [B4 bench results](../evidence/fm1-midi-timeout-b4-20261106/README.md#observed-on-b4).
