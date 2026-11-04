# USB-host MIDI alternate-zero startup, 4 November 2026

## Observation and scope

On diagnostic d001, candidate SHA-256
`72050c85919774c40cad920a97b6a31bf03571380a71e0885f7052f4f5f7a695`,
the user reported FM-1 on MX-1 USB3: `U3=0001`, `C3=0001`, monitor RX=0.
Demora on USB1 showed `U1=0007`, `C1=0101`; `C2=0001` was also reported.
The display reads main-processor state, not live USB-processor SRAM. The
FM-1 was connected to a USB-A host port, not USB-B. These observations imply
connection reported without MIDI readiness; they do not locate a wire error.
Exact board revision, cable, duration and live USB traffic were not captured.

This candidate targets that setup stall, retains the mastering held-key fix
without a debug menu, and leaves generic host audio disabled. There is no
physical result for the new candidate.

## Original instruction evidence

All addresses in this section belong to **app_usb**. Resident runtime addresses
are `0x60000000 + decoded offset`. USB startup copies original decoded
`0x2b1f4..0x36dd8` to `0x01000300..0x0100bee4`; hot-code decoded offsets below
use that map. These addresses are unrelated to main-processor SRAM.

- Record construction, decoded `0x7e72`, runtime `0x60007e72`, classifies
  interfaces by comparing audio IDs at record `+0x71/+0x72` before MIDI ID
  `+0x73`. The generic parser had overwritten absent audio IDs with zero,
  incorrectly classifying a MIDI-only interface 0 as audio. Restore the
  original `0xff` absence sentinels in the parsed structure at `+0x0d/+0x0e`.
- Initial interface event, decoded `0x8426`, runtime `0x60008426`, queues
  manager event 4 when all interfaces are present with zero status/error.
  Its alternative MIDI-open event 8 requires the selected MIDI alternate
  to match. The initial selection is `0xff`, so initial binding cannot open it.
- Setup, decoded `0x865c`, runtime `0x6000865c`, selects MIDI alt0 with the
  exact FM-1 built-image fixture, sets connection bit 1 and submits
  `SET_INTERFACE` (`bmRequestType=1`, request=11, value=0, index=2, length=0).
- Successful control completion, decoded `0xef38`, runtime `0x6000ef38`,
  compares the old/current and requested interface-node pointers. Equal
  pointers bypass detach/bind and return success. An already-active alt0
  therefore produces no follow-up bind to queue MIDI-open.
- Original MIDI-open dispatcher, decoded `0x33cbe`, runtime `0x01008dca`,
  builds RX/TX open requests and publishes status bit 4 only after their queues
  accept them. Queue acceptance is not endpoint or wire success.

`tools/host_midi_setup_verify.py` executes these actual instructions. The
before/after regression uses the same compiled parser and fixture, invoking
original setup directly for the before case and the patched table entry for
the after case. Before stays at `0001` without opens; after reaches `0005`,
opens both endpoints through original task handlers, then submits Start,
Clock and Stop. No main availability or clock gate is forced by the fix.

## Patch and bounds

The guarded four-byte callback entry at decoded `0x28288`, runtime
`0x60028288`, changes from `5d860060` (Thumb `0x6000865d`) to `1bc30001`
(Thumb `mx1_host_setup`, `0x0100c31b`). The table still dispatches event 4.
The wrapper calls original setup, then requires a non-Roland device, no error,
connected but not MIDI-ready status, selected MIDI alt0, a nonempty cable
selection and an active class-3 alt0 interface in the bounded eight-slot record.
It invokes the original MIDI-open dispatcher directly in the same manager task.
It does not enqueue a duplicate manager event or publish readiness itself.
Roland setup and alternate changes retain their original path.

ABI: the wrapper receives the stock event pointer in r0; setup and MIDI-open
consume the device pointer at event `+4`. Calls preserve r4-r11 and SP. No
pointer escapes beyond the original copied open requests. The unchanged stock
control call is synchronous at this boundary; tests model wire success and run
its original alternate-completion routine before returning to setup. A separate
actual-instruction check runs control request packing at `0x60009558` and the
wait/result path at `0x600093b0`, with RTOS allocation, enqueue, wait and release
stubbed. Both success and failure return the completion result after the wait.

USB extension grows 132 bytes, from 2,640 to 2,772 bytes, at
`0x0100bee4..0x0100c9b8`, leaving 1,608 bytes before the existing allocator at
`0x0100d000`. Writable USB state stays 1,472 bytes at
`0x01017868..0x01017e28`, with 472 bytes remaining. No new main SRAM or SDRAM
is reserved. The existing five initialized-data source relocations move by the
new extension length; destinations stay unchanged. Every displaced instruction,
callback target and component checksum is recorded in the build report.

## Candidate identities

- Container: `253645edb92a09c7b0d100da01f57d5127834c109b2ad499332645487a7a1d14`
- USB app: `7086bed11d109cd1ca72a54784d3246086a3997ff31b89a107433b5e8ebd360f`
- USB extension: `3aa2115c2123febe54e6a86ee34584832e8a5a1e18540f8afad1738147a1f1bc`
- Main app, unchanged from PR #18: `15ff306f7bc970266402ce54bf4c713c7fbd14d85eae4e796bc377dc211c0d2a`
- Main extension, unchanged: `fc4ed00c31546c74a84dbaece0ac9fda8fad28a3c21f19038e123617b945bbeb`

Boot programs, updater, panel payload, USB-B descriptors and main application
are unchanged from the mastering fix. Only the sole mainline image is built.
The previous diagnostic SDRAM reservation remains absent.

## Verification and limits

The host verification report includes all four physical-port mappings, exact
FM-1 fixture, genuine MIDI-only interface 0, input-only/output-only/bidirectional
profiles, repeated setup and late binds, control failure, rejected open queues,
inactive interface, endpoint lookup failure, manager disconnect/reconnect with
old RX DMA pending, stale input rejection and unchanged Roland alternate-switch
requests/callbacks. RX notes pass while host clock/transport remain blocked.
Existing transport regressions cover SysEx, overload, failed/short transfers,
priority and reconnect isolation. The full reproduction and committed-evidence
gates also cover container, startup and unchanged main behavior.

Modeled boundaries: descriptor/configuration/list/endpoint lookup, successful
control I/O, RTOS delivery, USB submission/cancel/completion and PHY/DMA hardware.
Original record construction, callbacks, setup, alternate completion, open/close
request packing, state notification, MIDI task handlers and compiled extension
instructions execute. This is not a whole-device scheduler or timing simulation.
The Roland comparison runs original alternate completion but models driver
bind/detach delivery; it is not an audio-stream test. Hardware boot, host MIDI,
clock jitter, simultaneous audio and long SysEx remain unverified.

For the next authorized test, use this exact candidate, FM-1 on a USB-A host
port, MX-1 clock source INT, and the monitor's RX counter plus LIVE USB/ALL
REALTIME view. Check clock and Start/Stop, then reconnect, notes/controllers and
input-sync rejection. A successful test must be recorded separately from these
offline results; follow [hardware validation](../../docs/HARDWARE_VALIDATION.md).
