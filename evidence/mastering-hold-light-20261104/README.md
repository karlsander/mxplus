# Mastering hold and selected preset light, 4 November 2026

The user reported “master mode is working great now” after testing the held-key
fix in PR #18, candidate
`9f6da91f9aaaedfb406ed1fa2d6af1a51900b44ecc950d4294cc6a513d5d8d38`.
They requested returning to a held MASTERING button without TAP and lighting
the currently selected preset in the step row. This is scoped user feedback,
not comprehensive mastering/audio/storage acceptance.

## Result

A 1,200-tick MASTERING hold enters the editor. Short presses retain the stock
operation; MASTERING + TEMPO remains available. TAP is no longer an entry
modifier. Buttons/encoders cancel pending entry while ADC/background events
do not. Held repeats and the release after entry are consumed; a fresh press
exits. The corrected physical-key range and all supported mixer pages remain.
Physical hold duration still needs confirmation.

The selected preset pad uses steady mode 1, brightness 9 and nonzero palette
index 4. All other pads, including 11–16, are explicitly off. Selection still
saves the outgoing slot, mutes temporarily and loads the new slot through stock
transactions. There is no change to parameter assignments or storage behavior.

## Original-instruction evidence

These addresses belong to **app_main**. Resident addresses are decoded offset
plus `0x60000000`. The relocated hot section originally starts at decoded
`0xd0b8c`, copied to runtime `0x01000300`; use that map for the hot addresses.

- Original clock API `0x010037e8` copies the counter at `0x01015304` into two
  words. Tick advancement at `0x0100858c` increments the second word and carries
  into the first. The new hold uses the second word and unsigned subtraction.
  Tests execute the clock API unchanged with modeled counter advancement.
- Logical LED mapping at `0x01002ad2` maps step IDs `0x19..0x28` to physical
  LED IDs `0xa2..0xb1`. These are distinct from physical key IDs 1–16.
- Mono helper `0x60014a78` unconditionally supplies palette index zero.
  Original RGB encoder `0x01009b40` sends three zero channel bytes for palette
  zero even with ON mode and brightness 9. Thus earlier tests that only captured
  the logical ON argument did not prove a visible pad.
- RGB-capable helper `0x60014a8e` preserves its fourth color argument. The stock
  selected-control renderer at `0x60019538` uses nonzero palette index 4. New
  redraw calls `0x60014a8e` with that palette. Original LED record writer
  `0x60001ff0` stores mode at `+4`, brightness at `+0x1c` and color at `+0x24`.
  Original RGB encoding gives channel bytes `[1,0,0]` for the selected pad and
  `[0,0,0]` for the other fifteen. No physical color calibration is claimed.

## Placement and identity

Candidate: `54d59222e51b44c3583e60c52400f06fc8e3d66e44ecb47e861f2333000250e1`.
Main application: `cfab5a905d27497f74e40f8147346307a3aaae56497eac520324f6d0c0ab1281`.
USB application remains `7086bed11d109cd1ca72a54784d3246086a3997ff31b89a107433b5e8ebd360f`,
including the [alternate-zero host MIDI fix](../host-midi-alt-zero-20261104/README.md).

This uses the same reclaimed resident main slots: lookup 26/30 bytes at
`0x6001dbd6`, head 504/532 bytes at `0x6001dbf4`, text 1,996/2,016 bytes at
`0x6001de0c`. Shared literal `0x6001de08` and return `0x6001e5ec` remain intact.
The existing 140-byte state at `0x01017444` reuses its first word for hold start;
no added SRAM, SDRAM, heap or MPU reservation. Main load extension, USB app,
boot programs, updater and panel payload stay unchanged from the MIDI fix.
The registered event callback now targets Thumb `0x6001e00f` from decoded
`0xf5d8`; the periodic callback targets `0x6001de0d` from `0xf5dc`, and redraw
remains at `0x6001dbf5`. AAPCS register/stack preservation is checked.
The guarded builder report records all overwritten bytes, new callback targets,
section bounds, startup relocation and component checksums.

## Verification and limitations

`tools/mastering_verify.py` covers all eight combinations of non-panel bits
85–87, all 85 real held-key blockers, exact hold threshold, low-word rollover,
short taps, held repeats, background ADC/notifications, cancellation by controls
and modal/page/lock changes. It executes original clock reads, parameter and
storage transactions, logical RGB LED mapping and record writes, then original
RGB encoding for each of ten slots across all sixteen pads. The regression also
reproduces zero RGB output from the old mono helper's palette-zero setting.
Existing control assignments, pickup, save/load, mute and ABI checks remain.

RTOS scheduling and advancing time, LED locks, final panel submission, storage
submission, notification boundaries and the stock periodic callback body are
modeled or stubbed. RGB encoding runs from steady on/off states; the complete
blink scheduler and physical panel are not simulated. Offline success does not
establish real hold duration, physical LED visibility, audio behavior or durable
save/restart. The prior chord-build observation does not validate these changed
routines. This candidate retains its UNTESTED name and has not been installed.

The next authorized bench check should verify long MASTERING entry, short
MASTERING action, MASTERING + TEMPO, all ten selected preset lights, entry/exit
under audio, and the FM-1 MIDI checks. Follow the existing
[hardware validation procedure](../../docs/HARDWARE_VALIDATION.md).
