# B6 converter isolation, 6 November 2026

The [B5 bench](../fm1-ehci-split-b5-20261106/README.md#observed-on-b5) established
normal boot, working MIDI commands and small FM-1 audio-packet counter deltas,
then one MX converter error before any accepted PCM packet. A clean boot with
only FM-1 reproduced it. No tone window completed and no audible result exists.

B6 retains the explicitly started EHCI input path and adds manager probe 7:
start in transport-only mode 3. It consumes accepted PCM and measures peaks
without calling the converter. Modes 0/1/2 still select normal/muted/local-tone
converter input while running; switching from 3 is explicit. Mode 3 expires
by stopping, never by enabling the converter. Probe 6 still stops, and probe 4
returns the FM-1 to alt0 after DMA retirement. FM-1 bridge B1 is unchanged.

The converter error policy remains stop-on-error. Page 8 records its call and
success counts, signed return value, entry gate, fixed original context,
smoothing state and DSP result. The audio task owns this snapshot. MIDI reads
only the cached page and checks its sequence; it cannot access arbitrary
addresses. The gate pointer is read only when aligned inside 40100000..40110000,
otherwise the page records ffffffff. Page 5's former final reserved word now
reports the stock-audio mask at 4000bbb0, to distinguish B5's first rejection.

An independent publication defect was found while reviewing B5: phase 2 was
visible before all sixteen siTDs had been constructed. The audio task could
preempt that construction and publish a converter failure. B6 publishes phase 2
after the ring is complete. This is not claimed as the cause of the observed
converter return; a targeted instruction check establishes the corrected order.

## Original instruction findings

All addresses are **app_usb**. Resident runtime is decoded offset +60000000;
hot code maps decoded 2b1f4 to runtime 01000300, length bbe4. See the retained
[original instructions](original-disassembly.txt).

- Runtime 010088dc (decoded 337d0) rejects a nonzero word through converter
  context +14 at 010088f8 before calling the converter body. Context is
  20005ee0 + port*a4. Original 60007884 (decoded 07884) constructs that pointer
  from DSP data base 40101000 and initialized per-port parameters.
- Runtime 010087d6 (decoded 336ca) calls 01008a90 for DSP completion, then
  returns −1 at 0100881e when the result has no float exponent bits. The
  completion helper returns zero on its wait/error outcome. Other failures
  also exist in drift estimation. B5's single counter cannot distinguish them.
- Original initializer 600079ee(port,1,44100) remains unchanged. B6 does not
  force the entry gate, invent a successful DSP result, or retry a failed DSP
  transaction. Its new mode isolates USB transfer evidence before exercising
  the original converter again.

## Placement and verification

The sole mainline builder still changes app_usb only. Hot code is 3,056 bytes,
hot state 1,472 bytes, audio/debug code 12,692 bytes (607f0000..607f3194).
The existing audio, MIDI diagnostic and EHCI layouts are unchanged. Four
144-byte converter snapshots append at 607fa66c..607fa8ac, for 26,796 bytes of
audio/debug state. Everything remains in the existing 64-KiB reservation.
Original main, boot, updater, panel and container boundaries are unchanged.
The build report retains exact patch bytes, targets, startup relocations,
bounds and component hashes. Candidate identity and validation completion are
recorded in [candidate.json](candidate.json). The compiled audio-task wrapper
uses a 184-byte frame including saved registers, 64 more than B5. Original
task creation at app_usb decoded 08ac0/runtime 60008ac0 reserves 1,024 bytes
at 4000b620. No task/stack allocation changes; these frame sizes are not a
whole-call-chain or hardware high-water measurement.

Targeted checks execute the original entry-gate failure and verify its capture,
RAM-only page reads with DSP memory unmapped, sequence contention, explicit
manager probe 7, transport-only packet draining and stop-on-expiry, and phase
publication after all sixteen DMA heads. Existing scheduling, retirement,
source-rate, original converter and MIDI tests remain. DMA, DSP results, MMIO
and task/interrupt delivery remain modeled; they do not establish timing or
working audio. B6 has not been installed at candidate preparation.

The optional hardware script first measures silence and stereo tone packets
with the converter bypassed, then explicitly enables the converter and records
its result. It captures pages even after a failed window, then mutes, stops and
returns to alt0. Other USB-host audio devices must remain disconnected for this
narrow admission experiment. No additional flashing path or firmware variant
is introduced.

All 17 offline reproduction stages, current and committed-artifact gates, and
six browser patcher tests passed for the code/artifact commit recorded in
[candidate.json](candidate.json). Hosted offline workflow [42241871889](https://github.com/karlsander/mxplus/actions/runs/42241871889)
passed for commit `be505dda7082d8e8ea5802bbb5b918255cfe5ccc`.

At 17:25 UTC, B6 was copied as `MX1_UPD.BIN` to the Roland updater, readback
hash-verified, and ejected. [Copy receipt](copy.json). Update completion and
normal boot were not yet observed at that point.

## Observed on B6

The user completed the update and restarted with only FM-1 on HOST3. Wire
build 182 confirmed B6; FM bridge B1 remained build 177. The sanitized
[bench summary](bench-summary.json) retains the counters, diagnostic words,
environment and cleanup. Raw Bluetooth logs stay private.

Probe 7 began the transport-only run, but its reply and subsequent MX commands
timed out. FM Bluetooth stayed responsive and its packet counter advanced by
52,640, representing 2,338,752 ring-fed frames, before plateauing around the
nominal 60-second expiry. Tone remained zero throughout. FM underruns increased
by 279 and overruns by 1,314. This is transfer progress with substantial gaps,
not a clean audio stream or an audible result.

Unplugging/reconnecting FM-1 without rebooting MX-1 restored MIDI. The retained
MX counters showed 52,631 accepted packets, zero malformed packets/queue
overflows, 3,619 queue underruns, 5,884 schedule corrections and zero converter
errors. Page 8 retained zero converter calls in mode 3, as intended. The mixer
was inactive/unclaimed after reconnect; FM was alt0 and muted. Page 4 reported
one drop and one error, but no immediate pre-start page-4 baseline or first
failure record exists. The early reconnect heartbeat's RX −7 may be unplug
cancellation; it does not identify the streaming failure. Rebind cleared the
EHCI page-5 cache, so the original stop reason is unavailable.

A subsequent muted normal-converter test ran setup probes 1/2/3 before probe 5.
Two converter calls succeeded; the third returned −1 with entry gate
`38800000` at `401010c0` (context `20006028`, port 2). Original app_usb
decoded `337d0`/runtime `010088dc` reads that gate through context +14 and
rejects nonzero at `010088f8`. This identifies the failing branch, not the
reason the gate remains nonzero. No new MX PCM packet was accepted before
stop; FM advanced by one packet/44 frames. MIDI continued working and explicit
mute, stop, retirement and alt0 cleanup succeeded. An earlier probe-5 attempt
without setup returned −5 without opening a stream; it is retained separately.

The bench helper now records exception types and collects FM status/trace
independently when MX commands time out. An offline injected probe-7 timeout
verified mute, FM counters/trace and six page-specific timeout records survive;
the stubbed bridge did not access hardware. Firmware bytes are unchanged.
