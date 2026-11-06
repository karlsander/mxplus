# B3: short MIDI input and transmit wakeups

The installed [B2 candidate](../fm1-ehci-debug-20261106/README.md#observed-on-b2)
kept FM-1 audio at alternate zero but its MIDI commands still timed out. The
FM-1 Bluetooth link stayed responsive. A clock test produced no additional
received USB MIDI traffic; the mixer clock destinations were not read.

Two software defects were then established independently of the live timeout:

- Generic MIDI IN submitted the stock asynchronous request with flags zero.
  The original EHCI completion rejects a successful short packet as −15 with
  that setting. The extension treats completion errors as terminal until
  reconnect, so a normal command can disable its receive direction.
- The debug reply publisher did not signal the flag on which the original
  MIDI TX task waits. A reply could remain queued without outgoing music.
  B2's heartbeat counted TX polls but did not itself wake the task.

These findings explain concrete failure paths. At B3 build time no live MX-1
error code had been received; the later reconnect capture below establishes
further errors. These were not the only hardware blockers.
EHCI audio remains unimplemented and deliberately disabled at automatic setup.

## Original instructions

All findings concern **app_usb**, not the main processor. See the
[original instruction excerpts](original-disassembly.txt).

| Decoded offset | Runtime | Finding |
| --- | --- | --- |
| `09464` | `60009464` | Asynchronous API packs flags at request +28 |
| `0f908` | `6000f908` | Core submission passes that halfword to lower HCD request |
| `112ae` | `600112ae` | EHCI request copies flag bit 13 to wrapper +16 |
| `11af2` | `60011af2` | Successful short completion returns −15 unless wrapper +16 is nonzero |
| `34110` | `0100921c` | MIDI TX waits on the flag handle at `4000bc0a` |
| `34188` | `01009294` | Flag bit 1 leads to the patched TX-poll call |

Resident runtime is decoded + `60000000`. Hot relocation copies decoded
`2b1f4..36dd8` to runtime `01000300..0100bee4`.

## Change

B3 supplies `2000` hex for MIDI IN requests; OUT still uses zero and requires
full completion. RX still rejects non-four-byte lengths, oversize data and
controller errors. The flag is a stock driver option; no original HCD routine
or completion status is patched or ignored.

Publishing a reply now signals TX flag 1. Every 4,096 audio-task calls also
signals TX once if a debug device is present, even when no audio endpoint is
claimed. TX builds and submits a single 60-byte heartbeat only when 4,096 calls
have elapsed since the last heartbeat or completed reply. Existing user SysEx
and pending replies take precedence. Missed intervals coalesce. The nominal
period is about one second, not a measured timing guarantee. No USB call is
made by this new audio-task wakeup.

Build ID is B3 (179). Protocol fields and FM-1 bridge B1 are unchanged. No new
FM-1 flash or client change is needed. Automatic EHCI audio remains at alt0;
manager probes are retained for the next live round trip.

## Binary identity and bounds

Candidate: `44314acc16a88248b74e0a4dd315f976f6b03f0c6d37e130d27b986ca8573c6c`.
Only app_usb changes relative to B2. Hot code is 2,984 bytes at
`0100bee4..0100ca8c`, leaving 1,396 bytes before the original allocator.
Audio/debug code is 8,460 bytes at `607f0000..607f210c`, within its 16-KiB slot.
Both state layouts are unchanged: 1,472-byte hot state and 25,956-byte SDRAM
state. The 64-KiB SDRAM reservation is unchanged. The main application, boot
programs, updater and panel payload retain their previous bytes.

[Candidate record](candidate.json) contains hashes and verification. The sole
[build report](../../build/mainline/build-report.json) records exact overwritten
bytes, replacements, branch/callback addresses, source hashes, startup changes
and checksums. Source changes are in the existing extension; the builder and
its whole-input and per-site guards remain unchanged.

## Verification boundary

`tools/host_midi_ehci_verify.py` executes original EHCI wrapper, QH and qTD
construction, asynchronous schedule linking, toggle bookkeeping and completion.
It models heap allocation, critical sections, controller status and DMA writeback.
For both full-speed and high-speed fixtures, 0/4/16/60-byte completions fail with
old flags and succeed with the corrected flag; 64-byte completions succeed in
both. The returned status then drives the compiled MIDI callback/poll to prove
continued reception. Stalls and malformed lengths still stop that direction.
USB electrical behavior, DMA timing and actual delivery are not established.

The bridge ARM checks assert that a reply signals TX, an idle audio tick signals
TX without claimed audio, no heartbeat floods a single interval, and user SysEx
defers a due heartbeat. RTOS scheduling and wire delivery remain modeled.
The full reproduction also retains startup, memory bounds, Roland MIDI,
USB-B audio/MIDI, mainline routing/mastering, updater and container checks.
The user confirmed B3 installation; the failed first live read is recorded below.


## Verified updater copy

At 13:03 UTC on 6 November, all 4,194,320 bytes were copied to the identified
Roland MX-1 updater volume as `MX1_UPD.BIN`. Readback matched candidate SHA-256
`44314acc16a88248b74e0a4dd315f976f6b03f0c6d37e130d27b986ca8573c6c`;
the volume was ejected successfully. [Receipt](copy.json). The user subsequently
confirmed updater completion, restart and HOST3 reconnection. All 17 local offline
stages, the committed-artifact gate and six browser-patcher checks passed on
code commit `7dc8203`; hosted run 42222314766 was still running at copy time.


## First B3 live read

The user confirmed installing B3 and reconnecting FM-1 to HOST3. The
[readout](live-b3.json) still timed out on MX-1 status. FM-1 remained configured
at alt0 with zero new audio packets. USB RX was 153 (one more than B2); MIDI
words were 1,171 (15 more). That is consistent with one startup heartbeat,
but it arrived before Bluetooth capture, so its contents/version were not
retained. The legacy-report count stayed at 2 and its old B2 latch is not new
B3 evidence. During the status attempt USB TX advanced from 204 to 205; RX
stayed 153. No later heartbeat arrived during the following three-minute watch.
BLE still worked and USB SOFs advanced. Parser errors remained zero.

The corrected short-input and wakeup paths therefore do not establish a
working bridge on this hardware. No audio probe or test tone was enabled. The subsequent receipt commit
superseded/cancelled the first hosted run. Hosted run 42222563693 passed on
receipt commit `122402689d79e6f1bb0bf9604d7ac8fc47f664df`, including the
committed-artifact gate and browser tests.

## Reconnect captured over Bluetooth

The user reconnected FM-1 USB to HOST3 while the powered FM-1 remained connected
over BLE. The [capture](reconnect-b3.json) contains one structured frame:

```text
target=1 seq=0 op=7E
words=[0,179,72,1,0,4294967289,4294967276]
```

This confirms MX-1 **B3 (179)** on the wire. Stage is `48` hex (automatic EHCI
audio stopped). RX flags show busy=1, ready=0, fault=0; TX flags are all zero
at heartbeat construction, before its submission. Last RX result is −7 and
last TX result is −20. `open_port` resets faults but retains last results, so
these are preceding-transfer results, not evidence that the newly opened RX
request has already failed.

FM-1 USB resets advanced 7→9, received packets 153→154 and MIDI words
1,171→1,186: exactly one 60-byte heartbeat. The following status command timed
out; queued FM-1 TX advanced 205→206 but RX stayed 154 for the remaining
approximately 27 seconds. No further heartbeat arrived. Audio stayed alt0;
18,216 cumulative packets remain the old Mac bench count, not MX-1 audio.
The BLE link and SOFs continued. The cause of −20 and the receive failure
requires further isolation; this does not establish a working command bridge.

A later [read-only FM-1 trace](reconnect-trace.json), at FM-1 uptime
7,370,692 ms, still had RX 154 / TX 206 / MIDI 1,186. Retained setup
requests end with `0009010000000000` (SET_CONFIGURATION 1) and
`010b000002000000` (SET_INTERFACE 0 on MIDI interface 2). This is device-side
request instrumentation, not an on-wire capture of successful status stages.
