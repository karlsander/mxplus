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

These findings explain concrete failure paths, but no live MX-1 error code
was received. They do not prove that these are the only hardware blockers.
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
Physical B3 installation and the real command round trip remain pending.
