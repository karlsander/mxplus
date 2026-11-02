# NSE/BD source picker and BD step editor

This note records the main-application panel and clock evidence used by the
internal-source experiment. The normal source picker gains `NSE` and `BD`.
A selected BD strip has an independent sixteen-step note pattern. Holding one
step redirects VALUE to that step's pitch and TEMPO to that step's decay.

**Status: compiled and exercised offline. Physical panel wiring, LED appearance,
audio, installation, recovery, and real-time margin have not been established.**
The final candidate and its exact identities are recorded in
[`build/generator-probe/build-report.json`](../build/generator-probe/build-report.json).
This is a new combined routing/internal-source experiment; the earlier routing
candidate remains independently reproducible.

## Panel behavior and the recovered mode

Hold a destination's SELECT and turn TEMPO to reach `NSE` or `BD`, using the
same picker implemented by the routing experiment. They are mono sources on all
eleven strips. Release SELECT, select the BD channel, and leave CHANNEL SETTING
BFX editing to access the note pattern. GAIN, PAN, TONE, AUX and FADER focus all
permit BD notes. CHANNEL SETTING BFX focus retains the original BFX step editor.
The BD pattern remains sixteen steps regardless of a BFX pattern's last step.

| Gesture | Result |
| --- | --- |
| Tap one step | Toggle that note on release. |
| Hold one step and turn VALUE, the left encoder | Change only that step's pitch, one semitone per nonzero encoder event, from −24 to +24. |
| Hold one step and turn TEMPO, the right encoder | Change only that step's decay, one unit per nonzero encoder event, from 0 to 100. |
| Release a step after moving either encoder | Retain its note enable state; editing does not also toggle it. |
| Hold a disabled step and turn an encoder | Edit its stored parameters without enabling the note. |
| Hold two or more steps | Cancel their tap toggles and consume ambiguous encoder movement. |
| Hold another button before pressing a step | Retain the original button combination. |
| Select CHANNEL SETTING BFX | Return the steps to the stock BFX pattern editor. |

The default pitch is zero and default decay is 53. Both parameters exist in
each step record, including disabled steps. There is no global kick-pitch or
global kick-decay setting. A power cycle restores empty patterns and defaults;
the extension adds no scene storage or flash writes.

The VALUE display shows a signed pitch using a blank positive sign (` 00`,
` 12`) and a minus for negative values (`-12`). This is deliberate: the stock
seven-segment font maps both ASCII `+` and `-` to the same segment mask, `0x40`.
Using a literal plus would make positive pitch appear negative on the panel.
The four-character TEMPO display shows decay as `d000` through `d100` while a
step is held. Releasing the step restores both original displays.

### Why focus is separate from BFX enable

The request described the unedited step view as a color gradient while a
channel was selected and no Beat FX was selected. The exact supported binary
has a narrower gradient condition: the original renderer at `0x600140c2`
branches to its gradient path at `0x60014212` when current-channel parameter
`0xfb` is `-1`. With a current channel, it renders that channel's BFX step mask
even if the channel's BFX processing is bypassed. The offline verifier executes
both original paths and records their different palette calls.

The implemented interpretation therefore uses **editing focus**: a selected BD
channel in an ordinary channel-setting view edits notes; explicit BFX focus
edits BFX. It does not treat BFX bypass as absence of a selected effect. This
allows a BD channel to use its normal BFX processing while its notes are edited.
The distinction between CHANNEL SETTING BFX and enabling BFX on a channel also
appears in the [official MX-1 owner's manual](https://cdn.roland.com/assets/media/pdf/MX-1_e01_W.pdf),
under channel settings and Beat FX. Numeric mode values below come from the
firmware, not from the manual.

## Original instructions and state

All resident code addresses below belong to the original main application.
Its decoded file offset is the runtime address minus `0x60000000`.
The supported original container SHA-256 is
`26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`.
SRAM code and tables are relocated by startup; see
[`analysis/map-main.json`](../analysis/map-main.json).

| Finding | Runtime address or parameter | Evidence and use |
| --- | --- | --- |
| Panel callback registration | Decoded `0xf5d8`, original pointer `0x60010b49` | The new event wrapper chains the previous source-picker wrapper. |
| Physical decoder | `0x60010a94` | Type 2 press, type 1 release, type 4 signed 16-bit encoder delta. |
| Original queue and held bits | `0x60010636`; bits at `0x605129a4` | Steps are key IDs `0x01..0x10`; SELECT keys are `0x29..0x33`. The original decoder and queue update these bits before the high-level actions. |
| High-level press and release entries | `0x60010516`, `0x60010538` | Intercepting these entries retains the original queue and physical held state. |
| Stock page-action dispatch | `0x6001099c`, `0x600109a6` | These are the explicitly modeled action-body boundaries in the UI verifier. |
| UI parameter getter | `0x6001a1cf`, context `0x60514504` | ID 0 is channel-setting focus: 0 GAIN, 1 PAN, 2 TONE, 3 AUX, 4 BFX, 5 FADER. |
| Mixer parameter getter | `0x6001e65f`, context `0x600b53ac` | ID `0xfb` is the current selected strip, or −1. |
| Per-channel BFX values | IDs `0x42+strip`, `0x73+strip`, `0x7e+strip`, `0x89+strip` | Respectively enable, effect type, step mask and last step. They are separate from editing focus and from BD state. |
| Main page | Halfword `0x600b4b5e` | BD editing requires zero. |
| Boot mode | Word `0x600b4b94` | BD editing requires normal mode zero. |
| Modal display | Query `0x60018259`, state `0x600b53a4` | Busy modal displays retain the original UI. |
| System mode | Getter `0x6001a897`, context `0x600b5390`, ID `0x19` | External Mixer value 2 retains the original step handling and routing behavior. |
| DSP diagnostic mode | Word `0x6051deb8` | Values greater than 3 disable the BD editor. |
| Deferred redraw flags | Halfword `0x605141cc` | Bit `0x10` steps, `0x200` VALUE, `0x400` TEMPO; input sets these flags instead of performing display I/O synchronously. |
| VALUE renderer | `0x60013740` | Original display index 0 has three characters. |
| TEMPO renderer | `0x60013356` | Original display index 1 has four characters; the new fallback chains the existing source-picker overlay. |
| Text API | `0x60054f85` to SRAM `0x01002a00` | Fixed-length character loop, with font lookup at `0x0100280a`. |
| Font table | SRAM `0x0100ecd4`, decoded `0xdf560` | Width bytes are 3 and 4; character segment bytes begin at +2. The lookup's literal is at `0x01002a9c`. |

The UI uses only the current strip returned by `0xfb`. Other selected-state
flags and linked-channel behavior remain owned by the original SELECT action.
The source-picker wrapper still passes every SELECT press and release to that
action. Source routes remain independent of which strip is current.

### Capturing a step without breaking release behavior

Six initialized extension bytes hold the captured pad bitmask, the edited or
cancelled bitmask, and the original strip index. They are part of the extension
startup copy, not an extra allocation. The original firmware retains ownership
of the physical held-key bits.

A BD press captures the pad and defers its toggle. An eligible nonzero encoder
event edits the captured step and marks it edited. Release consumes the captured
action even if the selected channel, route, menu or modal state changed during
the hold. A toggle requires the original strip and target view, no other keys,
and no edit or overlapping pad. Thus releasing an old hold cannot toggle a
newly selected channel or fall through as an unmatched stock BFX release.

All physical buttons `0..0x54` are checked. Any non-step hold excludes the BD
view, preserving shortcuts, effect-type holds, last-step operations and
SELECT+TEMPO source assignment. If another key arrives during a captured hold,
the old tap is cancelled and the new key follows its normal action. Signed
encoder deltas are normalized to one detent, matching the established picker.
A zero-delta event is consumed while held but does not mark the step edited.

## Step LEDs

The stock raw-color API is `0x60014a8f(id, mode, intensity, color)`. It reaches
SRAM dispatcher `0x01002ad2` and the final driver boundary at `0x60002010`.
Step LED IDs are `0x19..0x28`. The extension performs exactly sixteen calls.

The original three-byte color table starts at SRAM `0x0100f458`, decoded offset
`0xdfce4`. The chosen violet entries are valid original table entries and do
not occur in the four stock step-palette tables examined for this change.
They avoid adding a panel protocol or inventing an unrecognized color code.

| State | Original color index | Table triple | API mode / intensity |
| --- | --- | --- | --- |
| Enabled BD note | 18 | `(1, 0, 3)` | `1 / 9` |
| Current BD playhead | 22 | `(1, 0, 2)` | `1 / 9` |
| Held BD note | 7 | `(3, 3, 3)` | `1 / 9` |
| Disabled note outside playhead | 18 | Off | `0 / 0` |

A held marker takes precedence over the playhead. The playhead appears on
disabled steps too, so the full sixteen-step cycle is visible. These values
establish the programmed color choices; their perceived hue, brightness and
playhead contrast still require a physical panel check.

## Clock evidence and sixteen-step independence

The native sequencer calls `0x6000a894(context, native_step)` from the normal
step path at `0x6000ab32` and the shuffled path at `0x6000aab6`. The internal
source wrapper retains the complete original callback first, then publishes
one BD step. It uses the same timing decisions, including shuffle, without
creating a new timer or task.

The native step number is **not** a safe fixed-sixteen counter. Native reset
`0x6000a7a0` sets step zero and obtains a last-step value through
`0x6005b3c6(context=0x604df820)`, choosing values at context offsets `0x14` or
`0x18`. Advancement at `0x6000ab44` wraps at that native limit. Reusing its
argument directly could truncate the BD pattern. The extension therefore
increments a separate counter modulo 16 for each callback and resets it on
transport start/stop.

| Finding | Runtime address | Meaning |
| --- | --- | --- |
| Native transport start | `0x6000a7dc` | Wrapper resets BD phase before a real stopped-to-running start, then executes original instructions. |
| Native transport stop | `0x6000a810` | Wrapper retains original stop, then clears BD phase and invalidates voices. |
| Native step callback | `0x6000a894` | Original context in r0 and native step in r1; both preserved for stock processing. |
| Running / started flags | Bytes `0x600b4834`, `0x600b4835` | The playhead API returns −1 while stopped. |
| Native step and last step | Words `0x600b483c`, `0x600b4840` | Distinct from the extension's counter. |
| Tick counter and ticks per step | Words `0x600b4844`, `0x600b4854` | Original scheduling remains responsible for cadence. |
| Native step-rate setter | `0x6000b7fc` | Mode 0 → 8 ticks, 1 → 4, default 2 → 6, 3 → 3; the extension inherits this clock grid. |
| Original update callback | Pointer `0x600b4838`, original `0x6000a359` | Retained native scheduling/UI notification; the original path wakes HMI at `0x6000f3c4`. |

The core's published clock value carries a validity bit, a serial and the
independent step index. The UI reads it through `mx1_bd_current_step()`. Clock
hook control flow and sample generation have separate verifiers; the panel
test's explicit running-byte changes are not evidence of hardware timing.

## Hook bytes and ABI

[`tools/internal_sources_ui_patch.py`](../tools/internal_sources_ui_patch.py)
guards the exact original bytes below before writing each veneer. Thumb
addresses supplied as C calls include bit zero. The build report records every
replacement and final target address; no existing routing candidate is patched
in place.

| Decoded offset | Exact original bytes | Hook |
| --- | --- | --- |
| `0x0f5d8` | `49 0b 01 60` | Physical callback → BD encoder wrapper → existing source picker. |
| `0x10516` | `11 49 10 b5 08 31 48 80 6f f0 63 00` | High-level press. |
| `0x10538` | `08 49 10 b5 14 31 48 80` | High-level release. |
| `0x140c2` | `2d e9 f0 41 00 22 11 46 e5 48` | Sixteen-step display. |
| `0x13740` | `2d e9 fc 41 80 46 00 22` | VALUE overlay. |
| `0x13356` | `fe b5 04 46 c5 48 04 f0 7c ff` | TEMPO overlay and existing source label. |

The press guard is twelve bytes because its final `mvn` is a complete
four-byte instruction. A ten-byte overwrite would split that instruction.
Unaligned entries receive a NOP followed by a word-aligned literal jump;
remaining complete halfwords receive NOPs. The assembly trampolines in
[`patches/internal_sources_ui.S`](../patches/internal_sources_ui.S) reproduce
each displaced instruction and substitute resolved constants for PC-relative
loads. Resume addresses are `0x60010523`, `0x60010541`, `0x600140cd` and
`0x60013749`. The TEMPO fallback reuses the existing original-instruction
trampoline from the routing implementation.

The core API in [`patches/internal_sources.h`](../patches/internal_sources.h)
keeps UI work separate from sample rendering:

```c
uint32_t mx1_bd_step_get(uint32_t strip, uint32_t step);
void mx1_bd_step_toggle(uint32_t strip, uint32_t step);
void mx1_bd_step_adjust(uint32_t strip, uint32_t step,
                        uint32_t parameter, int32_t delta);
int mx1_bd_current_step(void);
```

Each aligned step word stores enable in bit 0, signed semitone pitch in bits
8..15 and decay in bits 16..23. Parameter 0 selects pitch; parameter 1 selects
decay. The UI writes no voice state, floating-point hardware, sample port or
DSP programming port. Audio consumes the core publication separately.

## Reproducing the panel evidence

Build the combined candidate using its builder, then test its actual decoded
main application and symbol map:

```bash
.venv/bin/python tools/build_generator_probe.py inputs/MX1_UPD.original.bin \
  --output build/generator-probe
.venv/bin/python tools/internal_sources_ui_verify.py inputs/MX1_UPD.original.bin \
  --build build/generator-probe --output build/generator-probe/ui-verification.json
```

The aggregator imports `verify(original, patched, build)` directly. That call
uses exactly the supplied application bytes and symbols. The separate
`--ui-only` option links the production UI with inert API fixtures at the
reviewed extension address and explicitly loads them in the emulator. It
produces no update container and is not a flashable candidate.

The tests cover all 176 strip/step addresses, every permitted channel focus,
held-note parameter and display binding across bitset byte boundaries, signed
encoder extremes and zero, release after view/source/channel changes,
overlapping pad holds, all 69 other physical buttons, the existing source
picker, sixteen LED calls and original renderer fallback. The font lookup runs
unchanged through the final segment-driver boundary. It catches unsupported or
ambiguous glyph choices rather than checking only requested text.

Final-candidate integration groups also execute the real route and BD APIs on
all eleven strips: physical SELECT+TEMPO wraps Auto→BD→NSE, the compiled step
array initializes all 176 records, the held encoders edit only the addressed
record, and the actual clock publication feeds the LED playhead across step
15→0. Every exercised entry checks r4–r11, restored SP and normal return.

Parameter storage returns explicit supplied values. Stock page-action bodies
and final display/LED delivery are observed boundaries. Broad gesture groups
model the core API to isolate panel behavior; final-candidate integration
groups run the compiled core state unchanged. RTOS posting is recorded without
scheduling a task. These tests establish the stated byte, control-flow and
state-update behavior under those boundaries. They do not establish physical
scan timing, switch wiring, perceived colors, audible output, clock jitter or
deadline margin.
