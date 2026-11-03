# Display diagnostics d001

This is the sole mainline candidate, with temporary control-task diagnostics.
It observes the unresolved MASTERING entry and FM-1 host-MIDI failures. It does
not claim to fix either. Candidate SHA-256:
`72050c85919774c40cad920a97b6a31bf03571380a71e0885f7052f4f5f7a695`.

## Controls and first test

Hold **channel 1 SELECT**, press **TAP**, then release both. The displays should
read **bLd d001**. Turn **TEMPO** one detent to move one page; reverse to go back.
The same SELECT + TAP combination exits. Entry works independently of the
mastering page/lock/modal guard, but is excluded during boot/setup and while
already in the mastering editor. This is a diagnostic overlay, not a routing
settings menu. It is off after every restart and writes no settings itself.

The label is on the three-character display and the value on the four-character
display. **All values are hexadecimal**, with `b` and `d` drawn lowercase.
Ordinary buttons still act normally except the diagnostic combination; TEMPO
browses pages while the overlay is open. Other knobs/faders keep their normal
behavior, including the mastering editor if entry succeeds.

1. Open diagnostics and confirm **bLd d001**.
2. Turn TEMPO once to **btn**. Press MASTERING: expect **0217**. Release it;
   the last-press value stays visible. Hold MASTERING and press TAP: expect
   **0200**. Release both before browsing the other pages.
3. Record **Mgd, MPg, MKy, MHi, MSt, tgd, tKy, tPr, tPo, CAn**. If the editor
   entered, press MASTERING once to exit/save before touching other controls.
   This further MASTERING press overwrites the MASTERING snapshot, so read it
   first if entry succeeded. Snapshots start at zero and are meaningful only
   after pressing the corresponding button.
4. Connect the powered FM-1 monitor to **MX-1 USB-A host 1**, with clock source
   INT and transport running. Read **U1** and **C1**, both before and after
   plugging it in. For another host port use its matching U/C pages.
   USB-B to the Mac is separate and is not the FM-1 host path.

## Readout legend

| Page | Value |
| --- | --- |
| bLd | `d001`, diagnostic build identifier |
| btn | Last button-down event: high byte event type, low byte raw ID; expected MASTERING `0217`, TAP `0200` |
| Cnt | Button-down count modulo 65536; excludes the consumed diagnostic TAP |
| Mgd | Entry-blocking mask immediately before the last MASTERING-down event |
| MPg | Panel page at that event; normal allowed pages `0005`–`000A` and `000F` |
| MKy | First set bit among all 88 bits checked by the mastering held-key guard; `FFFF` means none |
| MHi | Raw last byte of that key bitmap; includes bits 85–87 that routing does not check |
| MSt | Editor state immediately after MASTERING-down: bit 0 active, bit 1 pending |
| tgd | Entry-blocking mask immediately before the last ordinary TAP-down event |
| tKy | First held-key bit at that TAP event; `FFFF` means none |
| tPr / tPo | Editor state immediately before / after that TAP event |
| CAn | Last observed pending cancellation since boot: event type/ID, or `FFFE` for periodic cancellation; zero initially. Ordinary MASTERING release is excluded |
| StA | Live editor state: `0000` inactive, `0002` MASTERING modifier pending, `0001` editor active |
| U1–U4 | Raw main-processor host notification/status byte for each port |
| C1–C4 | High byte: clock destination availability gate; low byte: per-port clock-output enable gate. `0101` means both enabled |

**Mgd/tgd masks:** `0001` boot mode, `0002` UI lock, `0004` disallowed page,
`0008` modal display busy, `0010` held-key bitmap nonempty. Bits combine;
`0000` means these sampled guards did not block entry. Successful chord capture
normally gives MSt `0002`, tPr `0002`, tPo `0001`.

**U status bits:** `01` connection reported, `02` audio-ready reported, `04`
MIDI-ready reported. Either error bit `08` or `10` makes the original MIDI-ready
reader return error. With this MIDI-only FM-1 selection, `0005` would mean
connected + MIDI-ready. `0001` without `04` distinguishes connection from MIDI
setup. `0000` means no such notification has reached the main processor; it
cannot distinguish no physical attachment from an earlier enumeration failure.
Other bits are left raw rather than assigned an unproven hardware meaning.

C=`0101` does not prove clocks reach USB or the FM-1: the original sender also
needs a clock event and destination mask, followed by successful cross-core and
USB transport. No parser-attempt, endpoint-open or transfer-completion counters
are exposed by this build. U/C are main-side observations, not reads of the
independent USB processor's SRAM. Incoming host sync remains blocked.

## Implementation and memory

All new hooks and addresses here belong to **app_main**:

| Decoded offset | Runtime | Role |
| --- | --- | --- |
| `0xf5d8` | `0x6000f5d8` | Event pointer → diagnostic wrapper → existing mastering/routing event path |
| `0xf5dc` | `0x6000f5dc` | Periodic pointer → diagnostic wrapper → existing mastering/stock callback |
| `0x1484a` | `0x6001484a` | Existing redraw veneer → diagnostic wrapper → existing mastering/original redraw |
| `0x375c` | `0x6000375c` | Original literal identifies host status bytes at `0x600b1b3a` |
| `0x35c8` | `0x600035c8` | Unchanged host notification decoder; events 0/4 set connection/MIDI bits |
| `0x34e8` | `0x600034e8` | Unchanged MIDI-ready reader tests bits `05` and errors `18` |
| `0xd171e` | `0x01000e92` after startup relocation | Unchanged MIDI sender reads the displayed gates at `0x200003fc + port` and `+5+port` |
| `0x134/0x138/0x13c` | `0x60000134/138/13c` | Formerly empty startup copy 8 loads diagnostic code to `0x60664000` |
| `0xd76c` | `0x6000d76c` | Heap start literal moves `0x606634d0` → `0x60665000` |
| `0x108` | `0x60000108` | BSS clear extends by 36 bytes for diagnostics |

The diagnostic section is 1,076 bytes in a reserved 4-KiB SDRAM page
`0x60664000..0x60665000`. Its load bytes follow the SRAM code and USB descriptor
inside the one existing insertion; the report records the exact load offset.
The final stock SDRAM clear ends at `0x606634d0` and does not erase it. Reserving
alignment plus that page reduces the stock heap by **6,960 bytes**, leaving
26,849,280 bytes. The original heap creator and allocator remain unchanged.
This follows the separately documented [historical placement evidence](SDRAM_CODE.md),
but does not transfer that candidate's physical result to this build.

Diagnostic state occupies `0x010174d0..0x010174f4` (36 bytes), bringing the main
writable extension reservation to 656 bytes. Hexadecimal display constants bring the internal
code slot to 2,392 bytes, leaving 4 bytes. Mastering slots/state and both original
RTOS pools retain their bounds. No code uses `0x01018000`, no new task/ISR is
registered, and no audio sample callback is changed. The USB application is
byte-identical to PR #16. Boot programs, updater and panel payload are unchanged.

Text output uses the existing `0x60054f84` API in control-task callbacks. Idle
ADC samples do not force repeated display writes. Original callbacks run first
unless consuming diagnostic TAP/navigation. AAPCS registers and stack balance
are checked. SDRAM remains writable/executable under the unchanged MPU; harness
write protection of the diagnostic page is stronger than hardware protection.

## Evidence boundary

[Diagnostic instruction tests](../build/mainline/diagnostics-verification.json)
exercise entry/exit, both display widths, page wrap, guards including key 87,
button snapshots, successful mastering entry, event/tick cancellation, live
host flags and clock gates. Original notification decoding and MIDI-ready
reading run unchanged with only transaction delivery/logging modeled. The
original sender independently rejects each port when either displayed gate is
zero; mailbox acceptance is modeled. Original heap creation/allocation through
exhaustion checks that all writes exclude the diagnostic reservation.

Full reproduction also checks dirty startup, original data copies, patch-byte
accounting, component bounds, MPU and RTOS pools, mastering/routing regressions,
USB descriptors and MIDI filtering/transport models, original decoding/updater
acceptance and boot selection. Parameter notification, final panel I/O, the
stock periodic body and physical USB/DMA are not established by these tests.
Physical display visibility, scheduler/stack headroom, peak heap usage, audio
stability and the two reported failures still require the user's bench run.
