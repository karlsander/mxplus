# FM-1 Bluetooth development bridge

For the current candidate, hardware state and next bench steps, start with the
[FM-1 audio handoff](FM1_AUDIO_HANDOFF.md). The protocol/history below spans
multiple experimental builds.

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
B7 waits for two received packets before the first normal/muted converter
submission, retains controller and first-MIDI-failure snapshots across rebind,
and lets debug replies use a healthy endpoint after clock-queue overflow.
Actual USB transfer errors still stop the affected direction until reconnect.
[B7 candidate](../evidence/fm1-startup-b7-20261106/README.md).

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
| 2 | Page 0–19 | Pages 0–2 and 5–8: page, snapshot sequence, raw fields; pages 3–4: page, fields; pages 9–19 below |
| 3 | Mode 0–3 | Selected mode |
| 4 | none | Fresh snapshot sequence after worker completion |
| 5 | Step 1–10 | Accepted step; completion is reported by status |

B6 step 7 initializes the original converter context but starts with converter
submission bypassed. Mode 3 drains PCM without submitting it to the converter
and expires by stopping. Modes 0/1/2 require explicit selection to leave that bypass.

B8 step 8 uses the same converter-bypass mode but expires after 8,000 audio
task calls (nominally two seconds). It does not enable a tone.

B9 step 9 uses the same short bypass/retirement sequence with ISO IOC clear.
It services completions through the existing controller-status worker queue
at most every 16 audio ticks (nominally four ms), with only one request pending.
Other probes retain IOC and their 32-tick fallback. No controller interrupt
register, original MIDI request or split mask changes. This compares service
policies, not only a single IRQ bit: the polling cadence also differs.
The default `tools/fm1_audio_bench.py` uses probe 9; `--short-probe 8` selects
the prior policy and `--compare-ioc` runs both, with stop/alt0/setup between them.
It records reply latency and live status, reads snapshots before another start,
and reads final FM status after alt0. First-failure pages remain first-since-boot,
whereas async snapshots reset on each start. `--extended` selects the separate
longer tone/converter experiment. [B9 evidence](../evidence/fm1-poll-b9-20261115/README.md).

B14 step 10 uses the same poll-only policy as step 9, with the existing
240,000-tick (nominal 60-second) bypass expiry. `--long-silent` observes it
without tone or converter submission; it cannot combine with `--extended`
or `--compare-ioc`. The explicit `--extended` converter sequence now starts
through step 10 as well. Default operation remains the short silent step 9.

Result 0 succeeds; 1 is unsupported command/arguments; 2 is unavailable or a
concurrent snapshot. Refresh failures return the original absolute queue/worker
error. Probe queue failure is result 3. Invalid framing/checksum is silent and
increments errors. B1 is 177, B2 is 178, B3 is 179, B4 is 180, B5 is 181,
B6 is 182, B7 is 183, B8 is 184, B9 is 185, B10 is 186, B11 is 187, B12 is 188, B13 is 189 and current MX-1 candidate B14 is 190.

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
B7 fault bits are 1 for a terminal USB transfer/length error, 2 for ordinary
queue overflow and 4 for urgent clock/transport queue overflow. Bit 4 stops
all musical output while permitting separate debug replies; bit 1 still stops
all submissions in that direction. Rebind clears the live fault flags.

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
worker's own stage. Step 8 uses 38/40. One pending step per device. Rebinding setup resets the
protocol session. B7 retains cached controller words, whose generation and
captured state may describe the preceding attachment; it does not follow their
stored pointers. The next controller snapshot replaces those words.

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
converter call (including failure) and every 32 ticks in mode 3 or while B7
waits for its first two input packets. Explicit local-tone mode can start
without USB samples. This page
does not execute MMIO reads in the MIDI task. Its context/flags are diagnostic
observations, not independently verified DSP-ready or sample-rate indicators.

Pages 9 (RX) and 10 (TX) retain the first MIDI failure since boot. Replies are
result, page, sequence (2 when complete), source, audio tick, audio phase,
signed result in uint32, then the same 24 words as page 4. Source 1 is completion
status/length failure, 2 is synchronous submission failure, 3 is urgent queue
overflow and 4 is ordinary queue overflow. No record or an unfinished record
returns result 2. Atomic first-writer ownership prevents overwriting the first
cause; its 24 software fields can still advance during capture. These pages
survive reconnect and are cleared only by normal firmware startup. Use the
bench script or raw operation 2; the existing FM-1 client CLI predates them.

B8 pages 11/12 contain the first RX/TX asynchronous snapshot after 4,000
stream audio ticks; pages 13/14 contain the last sampled running state. Each
reply has 40 words: result, page, then sequence, tick, phase, event-call count,
fallback-poll count, accumulated event bits, validation errors, active request
count, USBCMD, USBSTS, USBINTR, FRINDEX, followed by 26 direction-specific words:

- Wrapper address, endpoint object, QH address, first qTD address, requested
  bytes, software completed bytes.
- Twelve QH words: horizontal link, endpoint characteristics, endpoint
  capabilities, current qTD, next qTD, alternate next qTD, token, five buffers.
- Three first-qTD words: next, alternate next, token.
- qTD count, wrapper words at offsets 8 and 12, last qTD address and token.

The two wrapper words contain controller/address and speed/endpoint/direction/
type, respectively. RX means FM-to-MX; TX means MX-to-FM. Missing directions
are zero. Validation flags: 1 excessive list count, 2 invalid wrapper, 4 invalid
private structure, 8 invalid QH, 16 invalid qTD table/count, 32 invalid qTD,
64 duplicate direction. The worker bounds the walk to 16 original requests,
checks pointer ranges and reads only EP1 bulk wrappers for the current FM.

Snapshots are taken at most once per 128 audio ticks, plus a final observation
when worker service sees stop intent. Both snapshots reset on a new transport
start attempt, remain after stop/rebind, and are read without dereferencing
saved pointers. A page for a different physical port or an incomplete snapshot
returns 2. DMA can advance during capture; a sequence check protects the copied
record against software writers, not against hardware changes. Descriptor
Active bits separate controller-pending work from delayed software completion.
They do not alone identify the cause of either condition.

EHCI stages: 50 topology rejection, 51 controller/table configuration,
52 periodic admission, 56 running, 57 stop, 58 run expired, 59 controller fault
or teardown, 5A worker gap/other periodic activity, 5B insertion admission,
5C changed link/table. Phase 4 quarantines DMA ownership until reboot when
destroy did not establish a halted controller. On EHCI, status control is raw
USBCMD, flags is the linked-slot mask and cc is the last siTD status byte.

Unsolicited op 7E hex, sequence 0, contains seven words: result 0, build 190,
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

- Hot extension: 0100bee4..0100cf9c, 4,280 bytes; writable hot state remains 1,472 bytes.
- Audio/debug code: 607f0000..607f3820, 14,368 bytes, within the existing 16-KiB code slot.
- Audio/DMA state remains 607f4000..607f9880; the A1 diagnostics remain 607f9880..607f9930.
- Bridge state follows at 607f9930..607fa564 (3,124 bytes); EHCI state adds 264
  bytes at 607fa564..607fa66c. B6 adds 576 bytes of converter snapshots at
  607fa66c..607fa8ac. Failure/async records and B10 pipeline counters follow
  through 607fb254; B11 appends its four-byte deadline through 607fb258; B12 adds 48 bytes of service timing through 607fb288. B14 appends its 6,016-byte EHCI packet queue through 607fca08. The whole 35,336-byte
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
devices disconnected for this experiment. B6 accepted 52,631 packets in its
transport-only test, but MIDI replies stopped until reconnect. A separate
muted converter test returned an entry-gate error on its third call.
[B6 results and limitations](../evidence/fm1-converter-b6-20261106/README.md#observed-on-b6).


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

## B10 pipeline pages

Pages 15/16 are first RX/TX and 17/18 are last RX/TX, aligned with the snapshots
on pages 11..14. Reply words are result, page, sequence, tick, phase, then seven
triples of count/latest-tick/value. Stage order: API entry, API return, core
entry, core return, HCD entry, HCD return, application completion. Entry values
are requested byte length, core request address and endpoint address respectively;
return/completion values are the original signed result represented as uint32.
Counters are lifetime totals and survive USB rebind; snapshot caches reset per
start. Compare stages and first/last values, accounting for multiple outstanding
requests and preemption. Triples/cross-stage values are not an atomic task trace.
No saved address is followed by MIDI. Wrong owner or an incomplete snapshot
returns result 2. [B10 evidence](../evidence/fm1-pipeline-b10-20261115/README.md).

## B11 poll admission

The poll latch now covers service as well as queue wait. The next poll becomes
eligible 16 ticks (probe 9) or 32 ticks (IOC mode) after callback completion,
including a fresh interval after an enqueue error. Nominal 4/8-ms values do not
include service duration. Existing commands and cached pipeline pages are
unchanged. [B11 evidence](../evidence/fm1-poll-fairness-b11-20261115/README.md).

## B12 worker timing

Page 19 returns result, page, sequence, calls, total/max/last FRINDEX delta,
last/max audio-tick delta, last/total accepted packets, entry/exit FRINDEX,
and ambiguity count. FRINDEX deltas are modulo 16,384 microframes (125 us each),
including preemption. Observed tick deltas >=8,192 flag long samples and exclude
them from total/max microframes; this does not establish CPU time or detect all
possible counter halts/wraps. The frame counter must be running. Cache resets
per start. Wrong-owner/incomplete reads return 2 and never access live MMIO.
[Definition, primary source and tests](../evidence/fm1-sram-b12-20261115/README.md).

## B13 service placement

The worker's unchanged service body now runs in the reserved executable SRAM,
including its inlined packet copy and asynchronous snapshots. The five
enumeration/open/close bodies move to the existing SDRAM code reservation;
steady MIDI polling, enqueue and completion code remain in SRAM. No command,
timer, queue policy or state address changes. Page 19 remains the comparison
metric, including preemption. [B13 evidence](../evidence/fm1-service-sram-b13-20261115/README.md).

## B14 queue buffering

The single EHCI stream uses a 32-packet queue appended after page 19's cache.
Only its owner may consume it. Sixteen published packets prime/re-prime the
consumer, increasing buffering delay to absorb worker batches. This is not
measured end-to-end latency or a guarantee of continuous audio. OHCI keeps its
eight-entry queue and two-packet priming; all existing state and DMA addresses
remain fixed. [B14 evidence](../evidence/fm1-queue-b14-20261115/README.md).
