# Mastering EQ mode

Hold **MASTERING** alone until it blinks, then release it. Press MASTERING
once to return to the mixer. A short tap retains the stock mastering bypass
operation. MASTERING + TEMPO still selects the stock preset when the encoder
is turned before the hold completes. Entry is limited to the stock operational pages (IDs 5 and 15), outside
boot, lock and modal states.

The mode takes over panel buttons, encoders, faders and scanned knobs. Unassigned
controls do nothing. Pad **1** enables/disables EQ and lights when EQ is on.
The current mastering preset and overall mastering bypass are retained: turn
mastering on before entering if it is bypassed. This first version edits EQ only.

| Strip | Fader | TONE/FILTER knob |
| --- | --- | --- |
| 1 | EQ output level | EQ input level |
| 2 | Unassigned | Unassigned |
| 3 | Low gain | Low frequency |
| 4 | Low Q | Low shelf/peak type |
| 5/6 | Low-mid gain | Low-mid frequency |
| DIGITAL | Low-mid Q | Unassigned |
| USB 1 | High-mid gain | High-mid frequency |
| USB 2 | High-mid Q | Unassigned |
| USB 3 | High gain | High frequency |
| USB 4 | High Q | High shelf/peak type |
| PC | Unassigned | Unassigned |

This covers all 16 adjustable EQ parameters, plus its switch. The left display
shows an abbreviated parameter name; the right display uses Roland's value
formatter. Controls pick up their existing EQ value before changing it. Assigned
fader lights blink until pickup. Filter-type knobs select shelf in their lower
half and peak in their upper half, also with pickup.

Leaving restores the mixer display and holds each displaced control's mixer
value until its physical position crosses that value. Faders use the original
snapshot/pickup blink renderer. The extra pickup gate applies even when the
system fader setting is Jump; the stock setting itself is unchanged. Knobs also
pick up, without a new knob indicator. Linked follower strips retain their stock
behavior. Buttons held while leaving cannot trigger stock release actions.

Edits use the original parameter setter and notification path. This does not
establish physical DSP response or save/restart persistence. See the separate
[full effect parameter tables](MASTERING_PARAMETERS.md).

## Placement and original-instruction evidence

This is a control-task change, with no new sample callback. It reclaims part of
the existing mixer parameter-ID lookup, rather than placing executable code in
a new memory region. Neither the unsuccessful `0x01018000` experiment nor the
unvalidated reserved-SDRAM generator design is used. The history and unresolved
freeze cause remain in [the generator research](GENERATOR_RESEARCH.md).

All addresses below belong to **app_main**. Resident runtime addresses are
`0x60000000 + decoded-image offset`; the existing relocated SRAM slot and its
startup map are documented in [MAINLINE.md](MAINLINE.md).

| Main decoded offset | Runtime | Change or evidence |
| --- | --- | --- |
| `0x1dbd6..0x1dbf4` | `0x6001dbd6..0x6001dbf4` | Compress stock mixer ID lookup into 26 bytes; 30-byte slot |
| `0x1dbf4..0x1de08` | `0x6001dbf4..0x6001de08` | 532-byte slot for mastering redraw, constants and trampoline |
| `0x1de08` | `0x6001de08` | Preserve original `0x600b53ac` literal used at `0x6001dbca` |
| `0x1de0c..0x1e5ec` | `0x6001de0c..0x6001e5ec` | 2,016-byte slot for mastering control code |
| `0x1e5ec..0x1e65e` | `0x6001e5ec..0x6001e65e` | Preserve shared return and invalid-ID diagnostic path; callers at `0x6001e80a` and `0x6001e97c` |
| `0xf5d8` | `0x6000f5d8` | Registered event callback wraps the existing routing callback |
| `0xf5dc` | `0x6000f5dc` | Registered periodic callback wraps original `0x60010b76` |
| `0x1484a` | `0x6001484a` | Full-redraw entry veneer; trampoline reproduces displaced prologue and both conditional destinations |
| `0x108` | `0x60000108` | Extend startup BSS clear for 140 bytes of state at `0x010173f4..0x01017480` |

Original mixer lookup inputs `0..0x106` yield `n + 0x10f` below `0x73`, then
`n + 0x114`. The verifier executes the original and replacement for all 263
valid inputs, plus unsigned/signed boundary-invalid values and diagnostic calls.
It checks the external Ghidra references against the preserved literal/shared
return and scans literal words for additional pointers into the reclaimed body.
These checks support this exact revision, not a generic lookup replacement.

Original mastering lookup `0x6001f866` (decoded `0x1f866`) maps zero-based
indices `0..64` to parameter IDs `0x476..0x4b6`. The getter at `0x6001fa48`,
formatter at `0x6001fadc` and generic transaction setter at `0x600161f6` are
called with the original mastering object at `0x600b53b8`. The setter owns
clamping and notification. There is no direct DSP register write in the new UI.

Callbacks retain the Cortex-M3 Thumb AAPCS convention. Function pointers set
Thumb bit 0; calls preserve r4–r11 and stack balance in the instruction tests.
The clock call at relocated SRAM `0x010037e8` returns a two-word value; the
hold uses its low word with unsigned wrap-safe subtraction and a 1,200-tick
threshold. Physical hold duration and panel scheduling remain to be measured.
Stock fader and tone handlers are `0x600174f2` / `0x600175d4`; stock fader
blink rendering is `0x60014488` (decoded offsets subtract `0x60000000`).

[The build report](../build/mainline/build-report.json) records exact old/new
bytes, veneers, exported targets, section usage, relocation literals and all
component checksums. [The guarded sites](../patches/mastering_sites.json) contain
the exact original lookup bytes. The existing SRAM code/load block is unchanged;
total writable reservation grows from 400 to 540 bytes inside stock MPU region 2.
No heap, MPU, USB application, boot program, updater or panel payload changes.

## Verification and limits

[mastering-verification.json](../build/mainline/mastering-verification.json)
executes the compiled registered callbacks, original parameter storage/getters/
clamping transactions and value formatter. It covers short/long gestures, timer
wrap, page/modal/lock guards, all EQ assignments and ranges, isolated controls,
held releases, return pickup in Jump and Pass modes, externally changed targets,
original tone/fader handling, blink encoding and the displaced redraw branches.

Object constructors are represented by original vtables and initialized values.
Clock time, the periodic callback body, mutex operations, parameter notification
boundaries, MIDI output and final panel I/O are stubbed. Physical LED timing,
DSP sound, task timing and mastering save/recall/restart are not established.
The full reproduction also checks the existing routing, startup, allocator,
USB and container boundaries. The artifact remains **UNTESTED**.

For an independently authorized bench run, add entry/exit while audio runs,
every EQ control, bypass and preset shortcuts, held buttons, both pickup modes,
linked channels, scene recall/restart and USB/routing regression to the existing
[hardware validation procedure](HARDWARE_VALIDATION.md). No hardware was accessed
for this implementation.
