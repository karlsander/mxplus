# USB-host MIDI experiment

Mainline adds USB-MIDI 1.0 input and output on the four host ports. Sync output
is the priority. The user confirmed MIDI output to an FM-1 after the
[alternate-zero setup fix](../evidence/host-midi-alt-zero-20261104/README.md),
using candidate `253645edb92a09c7b0d100da01f57d5127834c109b2ad499332645487a7a1d14`.
Exact messages, duration and timing were not recorded; the result does not
establish all MIDI directions or routing combinations. Earlier descriptor and
startup failures remain in their historical evidence records.

The current candidate includes the measured [FM-1 audio profile](USB_HOST_AUDIO.md),
but pauses audio startup on the observed EHCI connection.
That changed image still requires physical MIDI/audio acceptance. Other generic
audio profiles remain disabled. The FM-1 experiment also emits a bounded
[host diagnostic SysEx report](USB_HOST_AUDIO.md#host-diagnostic-report).

Candidate SHA-256: `f9d900f6a17159b89bd59bdf690942fbaa3b6f97d07e66177d4422153de2ad1b`.

## Behavior and scope

- One MIDIStreaming interface, alternate zero, protocol zero, with one embedded
  cable per direction. Input-only, output-only and bidirectional devices are
  accepted. MIDI-only devices do not need an audio interface. The MIDI parser
  ignores composite audio interfaces; a separate helper selects only the
  measured FM-1 input alternate.
- MIDI header length accepts the header/jack sum or the exact full MIDI span,
  including endpoint descriptors, as used by the FM-1. Every descriptor is still
  individually validated; unrelated audio interfaces are not counted.
- Successful setup on an already-active alternate zero explicitly invokes the
  stock MIDI-open dispatcher. It no longer depends on an alternate-change
  rebind. Absent audio interface IDs retain their `0xff` sentinels so a
  MIDI-only interface zero is classified correctly.
- Standard bulk endpoints at full speed (8/16/32/64-byte maximum packets) or
  high speed (512 bytes). Low speed, MIDI 2.0, multiple streaming interfaces,
  multiple cables per endpoint and nonzero MIDI alternates are excluded.
- Clock, Start, Continue, Stop and Song Position output use a separate priority
  queue. Channel messages and SysEx retain their order within the data queue.
  Already-submitted transfers cannot be preempted. No jitter bound is claimed.
- Incoming host Clock, Start, Continue, Stop, Song Position and MTC quarter-frame
  messages are discarded before the main processor. This applies to **Roland
  devices too**, so host inputs cannot become AUTO clock sources. USB-B and DIN
  input behavior is unchanged. The original SYNC menu still displays USB1–4;
  those choices cannot receive clock in this build. Use INT, MIDI or PC.
- Roland vendor devices retain their original parser, selection and high-speed
  transfer implementation, with the same incoming-sync filter. Standard-class
  devices with Roland's VID are not newly admitted by this initial profile.

The transport passes notes, controllers and SysEx into the existing routing
system. It does not introduce a routing matrix or remap the control surface.
Do not infer that every source can already control every destination. Playing
attached synths, recording their MIDI, editing patches and remotely controlling
the mixer are useful applications, but each depends on the existing route and
the receiving device's MIDI implementation. End-to-end USB-B/DIN/host routing
in all mixer modes still needs validation.

The existing system menu is entered by holding **GAIN while powering on**.
MIDI channel and Control Surface mode remain there. Its existing MIDI Through
setting controls DIN IN → DIN OUT; it is not a new host-port router. Any future
routing configuration belongs in this menu, not a second settings gesture.
See Roland's [Owner's Manual, System Settings](https://static.roland.com/assets/media/pdf/MX-1_e01_W.pdf).

## Queue and disconnect behavior

The original cross-core ring supplies events to the host transmitter. Each
new generic port has a 32-event sync queue and a 32-event background queue.
Each submission carries at most 16 events. Up to one IN and one OUT request
per port can be outstanding through the stock asynchronous USB stack.

A background-queue overflow disables background output on that port until
reconnection, discards its queued data and increments a counter; sync output
continues. A sync-queue overflow, failed submission, failed completion or short
write disables that direction until reconnection. This avoids silently replaying
old clock pulses. These limits matter for dense notes and large SysEx bursts:
**this build does not establish lossless bulk patch transfer**. It is not a MIDI
firmware-update transport with verified delivery.

Input waits without a timeout, since a quiet MIDI device is normal. B3 requests
the stock short-packet option (`2000` hex), so valid variable-length MIDI and
zero-length packets complete successfully. Non-word lengths and controller errors
still fault the direction. [Original EHCI evidence](../evidence/fm1-midi-bridge-b3-20261106/README.md). Other generic output uses
the stock API's timeout value 100; its wall-clock duration has not been measured.
B4 uses −1 (no per-transfer alarm) only for the matched FM-1 debug session to
isolate the captured TX error −20. A noncompleting write keeps its one buffer
until completion or stock disconnect cancellation; there is no new watchdog
or retry. This is a diagnostic experiment, not established fault recovery.
[Original alarm/core evidence](../evidence/fm1-midi-timeout-b4-20261106/README.md).
A blocked or failed generic port does not make the new dispatcher wait for that
port. The existing Roland/cross-core paths retain their original behavior.

Completion callbacks publish status/length and wake the MIDI task. They do not
run the potentially blocking main-processor delivery routine. Disconnect cancels
through the stock stack, invalidates the generation and clears queued output.
The DMA buffer remains owned until completion even if cancellation fails.
Reconnect cannot overwrite that buffer; stale input from the old generation is
discarded. Switching to a Roland device while old generic DMA is outstanding is
rejected until that completion has been consumed and the device is reconnected.

## Integration and memory

Only `tools/build_firmware.py` builds the candidate. It uses `patches/mainline.ld`
for two separate processor ELFs, then rebuilds the existing main and USB
application components in one container. There is no separate host firmware.
Boot programs, updater, panel payload, update range and container boundaries
remain unchanged. The host-MIDI addition in PR #14 changed **app_usb** while retaining PR #13
main-application bytes. Later mastering changes are documented in
[mainline integration](MAINLINE.md). The FM-1 audio follow-up adds USB manager/OHCI/EHCI hooks and SDRAM placement;
the main application remains identical
to the mastering held-key fix in PR #18.

USB startup originally copies decoded `0x2b1f4..0x36dd8` to
`0x01000300..0x0100bee4`. The new USB code is inserted at decoded `0x36dd8`,
runtime `0x0100bee4`, below the existing USB allocator at `0x0100d000`.
The extension occupies 3,056 bytes (`0x0100bee4..0x0100cad4`), leaving
1,324 bytes before that allocator. State occupies 1,472 bytes
(`0x01017868..0x01017e28`), leaving 472 bytes before the writable-region limit.
The five following initialized-data source literals move; their destinations
do not. New zero-initialized state starts at the original USB BSS end,
`0x01017868`, and must end before `0x01018000`.

The original USB MPU setup at decoded `0x3760`, resident `0x60003760`, makes
the code read-only and the state region writable. Original RTOS pools are
`0x010142c4..0x010152c4` and `0x01020000..0x01028000`. The separate USB allocator
table at decoded `0x2820c` also reserves `0x0100d000`, `0x0100e000` and
`0x0100f000` as 4-KiB regions. Exact table bytes are guarded.

The separate [audio extension](USB_HOST_AUDIO.md#usb-processor-placement-and-binary-changes) reserves 64 KiB from the original USB SDRAM heap; its code and state are initialized by formerly empty startup entries.

These are USB-processor addresses, not additional space in the main processor.
Mastering reclaimed 2,548 bytes of resident main code footprint and consumed
140 bytes of writable main SRAM; it did not free main SRAM. The main executable
extension still has only 20 bytes unused.

| app_usb decoded offset | Runtime | Purpose |
| --- | --- | --- |
| `0xa1e2` | `0x6000a1e2` | Bounded generic configuration parser; exact Roland trampoline |
| `0x7848` | `0x60007848` | Selection callback; generic MIDI only, original Roland policy |
| `0x28288` | `0x60028288` | Setup callback table entry; finish generic MIDI alt0 setup using the original open dispatcher, then select measured FM-1 audio |
| `0x7844` | `0x60007844` | Receive callback; reject incoming host sync before cross-core delivery |
| `0x90fa`, `0x9160` | `0x600090fa`, `0x60009160` | Generic IN/OUT open; retain original Roland endpoint setup |
| `0x33f60`, `0x340b0` | `0x0100906c`, `0x010091bc` | IN/OUT disconnect wrappers |
| `0x342ae` | `0x010093ba` | Original TX dispatcher to per-port queues |
| `0x33ff8`, `0x34188` | `0x01009104`, `0x01009294` | Original MIDI-task calls redirected to poll wrappers |
| `0xe8`, `0x100`, `0x108`, `0x114`, `0x128`, `0x13c`, `0x150` | `0x60000000 + offset` | Startup copy/zero accounting |

`build/mainline/build-report.json` records every old/new byte, export, branch
address, section extent, source hash, component checksum and container hash.
`app_usb.mainline.bin` is the decoded component; `usb-host.load.bin` is its
inserted code, not a separately flashable image.

The new full-speed path uses the stock request builder at USB decoded `0x9464`,
resident `0x60009464`, instead of altering the high-speed queue-head format.
Completion dispatch at `0x6000f60a` passes interface, endpoint, a two-word
status/length result and user context. Standard transfers still depend on the
stock controller driver, scheduling and physical topology.

## Verification and remaining work

`tools/host_midi_verify.py` runs in the mainline ARM stage. It executes original
startup and pool initialization, MPU programming, configuration ABI construction,
Roland descriptor parsing/selection, cross-core TX ring dispatch, asynchronous
request packing and completion dispatch. New code executes as ARM instructions,
including all four ports, both speeds, the FM-1 built descriptor, malformed
descriptors, both MIDI length conventions, sync filtering,
priority, short writes, overload isolation and reconnect with old DMA pending.
Transport and setup calls preserve r4–r11 and SP; code pages are protected against writes.
`tools/host_midi_setup_verify.py` additionally executes original record construction,
interface binding, setup, alternate completion, MIDI request packing, task open
handlers and manager disconnect/reconnect. The old setup path stays at state
`0001`; the new one reaches `0005` and submits sync in the model. Roland
alternate-change requests/binds are compared unchanged. Control success, list
lookup, endpoint lookup and RTOS message delivery are modeled. State `0005`
means the stock open queues accepted requests; it alone does not prove transfers.

The original main MIDI sender at main decoded `0xd171e`, runtime `0x01000e92`,
is separately executed with all four host destinations enabled (`0x2a800`).
It sends Clock/Start/Continue/Stop to the expected four host cable numbers.
That test models mailbox acceptance; it does not establish the complete
panel/settings-to-clock path or hardware timing.

USB submission/cancellation and RTOS delivery are modeled for streaming tests.
Controller/DMA/PHY transactions, real disconnect races, stack headroom under
preemption, timing under audio load and long SysEx delivery remain unverified.
The original decoder/updater and boot checks cover both changed applications;
physical recovery is not established by those offline checks.

For an authorized bench experiment, follow [hardware validation](HARDWARE_VALIDATION.md).
Capture the actual device descriptors and speed first. With the exact candidate
recorded, test INT clock and Start/Stop into one device; then all four ports,
external clock through DIN/USB-B, notes/controllers/SysEx, and simultaneous audio.
Inject clock from every host port and verify it never changes the MX-1's clock
or transport. Record jitter, losses, reconnect behavior and duration. Generic
audio remains a later experiment, even when the attached device offers it.
