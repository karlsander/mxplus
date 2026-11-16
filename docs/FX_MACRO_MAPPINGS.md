# All factory MASTER FX knob mappings

This is a transcription of all 48 original preset records, not a proposed new
mapping. See [the engine inventory](FX_ENGINE_PARAMETERS.md) for type enums and
[the DSP findings index](DSP_FINDINGS.md) for ownership and evidence limits.
The firmware's initial parameter block is separate from these macros.

Each side applies up to four target/min/max triples, in recorded order. Values
below are **raw integers**, not inferred Hz, milliseconds or dB. Arrows run from
near center toward that side's endpoint; “fixed” means equal endpoints. Zero
target slots are omitted. TIME names its separate target; its range is not one
of the knob triples. Center remains the stock OFF position.

The six banks and public variation names are catalogued in the
[panel mapping](FX_ENGINE_PARAMETERS.md#six-panel-banks-and-their-eight-variations).
“Stereo Delay & Pan Delay” uses one engine, with different type values on each
side. COMBI sequences selections rather than applying every listed engine.
The new internal send uses direct controls and does not apply these macros.

## Source and interpretation

Component: **app_main**. Original decoded-image SHA-256:
`256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b`.
Records start at decoded `0x60ab0` / runtime `0x60060ab0`, stride 652 bytes,
48 records, 163 little-endian words each. Row offsets below are decoded offsets;
add `0x60000000` for resident runtime addresses. Word zero is global TYPE
(`0x3d3`). Right-side triples occupy IDs `0x45d..0x468`, left-side triples
`0x469..0x474`, and TIME is `0x475`. Add `0x3d4` to each nonzero local target.
Names come from the ID-indexed pointer table at decoded `0x6f278`.

Original instructions `0x6002a5e2..0x6002a702` select sides, interpolate and clamp
the four mappings; live updates use `0x6002a768`. For knob values 0–127, distance
from center is `(64-knob)/64` on the left or `(knob-64)/63` on the right, with
integer arithmetic. Clamping can further limit the raw values. These tables
describe stored endpoints, not listening results or a complete proof that every
stored field is effective. In particular Oscillator DUMMY and Scatter Controls
1–3 have the inactive behavior documented in the inventory.

## DELAY

| Variation / decoded record | Engine ID / name | Left side | Right side | TIME target |
| --- | --- | --- | --- | --- |
| 1. Stereo Delay (`0x60ab0`) | 1 / DELAY | DD FEEDBACK (`0x3da`): 0 → 127; DD EFX LEVEL (`0x3dd`): 15 → 108; DD LF DAMP (`0x3db`): 2 fixed; DD HF DAMP (`0x3dc`): 7 fixed | DD FEEDBACK (`0x3da`): 0 → 127; DD EFX LEVEL (`0x3dd`): 15 → 108; DD LF DAMP (`0x3db`): 10 fixed; DD HF DAMP (`0x3dc`): 1 fixed | DD TIME (`0x3d7`) |
| 2. Pan Delay (`0x60d3c`) | 1 / DELAY | DD FEEDBACK (`0x3da`): 0 → 127; DD EFX LEVEL (`0x3dd`): 15 → 108; DD LF DAMP (`0x3db`): 3 fixed; DD HF DAMP (`0x3dc`): 7 fixed | DD FEEDBACK (`0x3da`): 0 → 127; DD EFX LEVEL (`0x3dd`): 15 → 108; DD LF DAMP (`0x3db`): 10 fixed; DD HF DAMP (`0x3dc`): 1 fixed | DD TIME (`0x3d7`) |
| 3. Cross Delay (`0x60fc8`) | 1 / DELAY | DD FEEDBACK (`0x3da`): 0 → 127; DD EFX LEVEL (`0x3dd`): 15 → 108; DD LF DAMP (`0x3db`): 2 fixed; DD HF DAMP (`0x3dc`): 7 fixed | DD FEEDBACK (`0x3da`): 0 → 127; DD EFX LEVEL (`0x3dd`): 15 → 108; DD LF DAMP (`0x3db`): 10 fixed; DD HF DAMP (`0x3dc`): 1 fixed | DD TIME (`0x3d7`) |
| 4. Stereo Delay & Pan Delay (`0x61254`) | 1 / DELAY | DD FEEDBACK (`0x3da`): 0 → 127; DD EFX LEVEL (`0x3dd`): 15 → 108; DD TYPE (`0x3d6`): 2 fixed | DD FEEDBACK (`0x3da`): 0 → 127; DD EFX LEVEL (`0x3dd`): 15 → 108; DD TYPE (`0x3d6`): 1 fixed | DD TIME (`0x3d7`) |
| 5. Spiral (`0x614e0`) | 3 / SPIRAL | 0 (`0x3d5`): 0 fixed; PS PITCH1 (`0x3ee`): 24 → 17; PS PITCH2 (`0x3f1`): 24 → 17; PS FEEDBACK (`0x3ed`): 0 → 127 | 0 (`0x3d5`): 0 fixed; PS PITCH1 (`0x3ee`): 24 → 31; PS PITCH2 (`0x3f1`): 24 → 31; PS FEEDBACK (`0x3ed`): 0 → 127 | None |
| 6. Room (`0x6176c`) | 4 / REVERB | RV TIME (`0x3f5`): 40 → 64; RV EFFECT LEVEL (`0x3fa`): 0 → 90 | RV TIME (`0x3f5`): 40 → 125; RV EFFECT LEVEL (`0x3fa`): 0 → 40 | None |
| 7. Hall (`0x619f8`) | 4 / REVERB | RV TIME (`0x3f5`): 40 → 64; RV EFFECT LEVEL (`0x3fa`): 0 → 90 | RV TIME (`0x3f5`): 40 → 127; RV EFFECT LEVEL (`0x3fa`): 0 → 70 | None |
| 8. Reverb Mod (`0x61c84`) | 4 / REVERB | RV TIME (`0x3f5`): 40 → 127; RV HPF (`0x3f7`): 4 fixed; RV EFFECT LEVEL (`0x3fa`): 0 → 120; RV LPF (`0x3f8`): 12 fixed | RV TIME (`0x3f5`): 40 → 127; RV HPF (`0x3f7`): 12 fixed; RV EFFECT LEVEL (`0x3fa`): 0 → 80; RV LPF (`0x3f8`): 4 fixed | None |

## FILTER

| Variation / decoded record | Engine ID / name | Left side | Right side | TIME target |
| --- | --- | --- | --- | --- |
| 1. Filter 6dB (`0x61f10`) | 5 / FILTER DRIVE | FILTER CUTOFF (`0x3fd`): 0 → 127; FILTER TYPE (`0x3fc`): 0 fixed | FILTER CUTOFF (`0x3fd`): 0 → 127; FILTER TYPE (`0x3fc`): 1 fixed | FILTER RESONANCE (`0x3fe`) |
| 2. Filter 12dB (`0x6219c`) | 5 / FILTER DRIVE | FILTER CUTOFF (`0x3fd`): 0 → 127; FILTER TYPE (`0x3fc`): 2 fixed | FILTER CUTOFF (`0x3fd`): 0 → 127; FILTER TYPE (`0x3fc`): 3 fixed | FILTER RESONANCE (`0x3fe`) |
| 3. Filter 24dB (`0x62428`) | 5 / FILTER DRIVE | FILTER CUTOFF (`0x3fd`): 0 → 127; FILTER TYPE (`0x3fc`): 4 fixed | FILTER CUTOFF (`0x3fd`): 0 → 127; FILTER TYPE (`0x3fc`): 5 fixed | FILTER RESONANCE (`0x3fe`) |
| 4. Iso Hi-Low (`0x626b4`) | 6 / ISOLATOR | ISO HIGH (`0x402`): 105 → 0; ISO LOW (`0x400`): 105 fixed; ISO MID (`0x401`): 105 fixed | ISO HIGH (`0x402`): 105 fixed; ISO LOW (`0x400`): 105 → 0; ISO MID (`0x401`): 105 fixed | None |
| 5. Iso Low (`0x62940`) | 6 / ISOLATOR | ISO HIGH (`0x402`): 105 fixed; ISO LOW (`0x400`): 105 → 0; ISO MID (`0x401`): 105 fixed | ISO HIGH (`0x402`): 105 fixed; ISO LOW (`0x400`): 105 → 125; ISO MID (`0x401`): 105 fixed | None |
| 6. Iso Hi-Mid (`0x62bcc`) | 6 / ISOLATOR | ISO HIGH (`0x402`): 105 → 0; ISO LOW (`0x400`): 105 fixed; ISO MID (`0x401`): 105 fixed | ISO HIGH (`0x402`): 105 → 0; ISO LOW (`0x400`): 105 → 0; ISO MID (`0x401`): 105 → 115 | None |
| 7. Oscillator (`0x62e58`) | 19 / OSCILLATOR | OSC (`0x453`): 0 fixed; OSC PITCH (`0x454`): 127 → 20; DD EFX LEVEL (`0x45b`): 0 → 10; NOISE LEVEL (`0x45c`): 64 → 112 | OSC (`0x453`): 1 fixed; OSC PITCH (`0x454`): 0 → 127; DD EFX LEVEL (`0x45b`): 0 → 10; NOISE LEVEL (`0x45c`): 20 → 100 | FILTER RESONANCE (`0x457`) |
| 8. Noise (`0x630e4`) | 19 / OSCILLATOR | FILTER TYPE (`0x455`): 0 fixed; FILTER CUTOFF (`0x456`): 127 → 10; DD EFX LEVEL (`0x45b`): 0 → 69; NOISE LEVEL (`0x45c`): 0 → 127 | FILTER TYPE (`0x455`): 2 fixed; FILTER CUTOFF (`0x456`): 0 → 100; DD EFX LEVEL (`0x45b`): 0 → 69; NOISE LEVEL (`0x45c`): 0 → 110 | FILTER RESONANCE (`0x457`) |

## SCATTER

| Variation / decoded record | Engine ID / name | Left side | Right side | TIME target |
| --- | --- | --- | --- | --- |
| 1. Scatter 1 (`0x63370`) | 18 / SCATTER | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 0 fixed; SC TYPE (`0x44b`): 0 fixed; SC CONTROL6 (`0x452`): 125 → 85 | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 2 fixed; SC TYPE (`0x44b`): 1 fixed; SC CONTROL6 (`0x452`): 125 → 100 | SC CONTROL5 (`0x451`) |
| 2. Scatter 2 (`0x635fc`) | 18 / SCATTER | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 0 fixed; SC TYPE (`0x44b`): 2 fixed; SC CONTROL6 (`0x452`): 120 → 110 | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 0 fixed; SC TYPE (`0x44b`): 3 fixed; SC CONTROL6 (`0x452`): 120 → 105 | SC CONTROL5 (`0x451`) |
| 3. Scatter 3 (`0x63888`) | 18 / SCATTER | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 0 fixed; SC TYPE (`0x44b`): 4 fixed; SC CONTROL6 (`0x452`): 120 → 105 | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 2 fixed; SC TYPE (`0x44b`): 5 fixed; SC CONTROL6 (`0x452`): 123 → 105 | SC CONTROL5 (`0x451`) |
| 4. Scatter 4 (`0x63b14`) | 18 / SCATTER | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 0 fixed; SC TYPE (`0x44b`): 6 fixed; SC CONTROL6 (`0x452`): 95 → 100 | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 2 fixed; SC TYPE (`0x44b`): 7 fixed; SC CONTROL6 (`0x452`): 100 → 90 | SC CONTROL5 (`0x451`) |
| 5. Scatter 5 (`0x63da0`) | 18 / SCATTER | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 0 fixed; SC TYPE (`0x44b`): 10 fixed; SC CONTROL6 (`0x452`): 117 → 72 | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 2 fixed; SC TYPE (`0x44b`): 11 fixed; SC CONTROL6 (`0x452`): 120 → 86 | SC CONTROL5 (`0x451`) |
| 6. Scatter 6 (`0x6402c`) | 18 / SCATTER | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 0 fixed; SC TYPE (`0x44b`): 12 fixed; SC CONTROL6 (`0x452`): 120 → 70 | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 2 fixed; SC TYPE (`0x44b`): 13 fixed; SC CONTROL6 (`0x452`): 120 → 80 | SC CONTROL5 (`0x451`) |
| 7. Scatter 7 (`0x642b8`) | 18 / SCATTER | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 0 fixed; SC TYPE (`0x44b`): 14 fixed; SC CONTROL6 (`0x452`): 123 → 105 | SC DEPTH1 (`0x44c`): 0 → 9; SC CONTROL4 (`0x450`): 2 fixed; SC TYPE (`0x44b`): 15 fixed; SC CONTROL6 (`0x452`): 127 → 108 | SC CONTROL5 (`0x451`) |
| 8. Scatter 8 (`0x64544`) | 18 / SCATTER | SC DEPTH1 (`0x44c`): 0 → 6; SC CONTROL4 (`0x450`): 0 fixed; SC TYPE (`0x44b`): 16 fixed; SC CONTROL6 (`0x452`): 120 → 110 | SC DEPTH1 (`0x44c`): 0 → 6; SC CONTROL4 (`0x450`): 2 fixed; SC TYPE (`0x44b`): 17 fixed; SC CONTROL6 (`0x452`): 120 → 113 | SC CONTROL5 (`0x451`) |

## FLANGER

| Variation / decoded record | Engine ID / name | Left side | Right side | TIME target |
| --- | --- | --- | --- | --- |
| 1. Flanger 1 (`0x647d0`) | 8 / FLANGER | FL DEPTH (`0x411`): 0 → 127; FL RESONANCE (`0x413`): 0 → 36; 0 (`0x3d5`): 127 → 0; FL EFFECT LEVEL (`0x416`): 0 → 100 | FL DEPTH (`0x411`): 64 → 127; FL RESONANCE (`0x413`): 0 → 70; 0 (`0x3d5`): 127 → 0; FL EFFECT LEVEL (`0x416`): 0 → 96 | FL RATE (`0x40e`) |
| 2. Flanger 2 (`0x64a5c`) | 8 / FLANGER | FL HPF (`0x415`): 3 → 0; FL RESONANCE (`0x413`): 0 → 70; 0 (`0x3d5`): 127 → 0; FL EFFECT LEVEL (`0x416`): 0 → 55 | FL HPF (`0x415`): 4 → 8; FL RESONANCE (`0x413`): 0 → 105; 0 (`0x3d5`): 127 → 0; FL EFFECT LEVEL (`0x416`): 10 → 40 | FL RATE (`0x40e`) |
| 3. Flanger Manual (`0x64ce8`) | 8 / FLANGER | FL MANUAL (`0x412`): 0 fixed; FL SYNC NOTE (`0x410`): 25 → 0; FL DEPTH (`0x411`): 64 → 120; FL RESONANCE (`0x413`): 0 → 60 | FL MANUAL (`0x412`): 0 → 127; FL SYNC NOTE (`0x410`): 0 fixed; FL DEPTH (`0x411`): 0 fixed; FL RESONANCE (`0x413`): 0 → 60 | None |
| 4. Phaser 1 (`0x64f74`) | 9 / PHASER | 0 (`0x3d5`): 127 → 0; PH EFFECT LEVEL (`0x420`): 0 → 108; PH TYPE (`0x417`): 1 fixed; PH RESONANCE (`0x41d`): 40 → 10 | 0 (`0x3d5`): 127 → 0; PH EFFECT LEVEL (`0x420`): 0 → 60; PH TYPE (`0x417`): 0 fixed; PH RESONANCE (`0x41d`): 0 → 90 | PH RATE (`0x418`) |
| 5. Phaser 2 (`0x65200`) | 9 / PHASER | 0 (`0x3d5`): 127 → 0; PH EFFECT LEVEL (`0x420`): 0 → 50; PH TYPE (`0x417`): 3 fixed; PH RESONANCE (`0x41d`): 20 → 50 | 0 (`0x3d5`): 127 → 0; PH EFFECT LEVEL (`0x420`): 0 → 90; PH TYPE (`0x417`): 2 fixed; PH RESONANCE (`0x41d`): 48 → 70 | PH RATE (`0x418`) |
| 6. Phaser Manual (`0x6548c`) | 9 / PHASER | PH RESONANCE (`0x41d`): 30 → 100; PH TEMPO SYNC (`0x41a`): 25 → 0; PH DEPTH (`0x41b`): 100 → 127; PH MANUAL (`0x41c`): 0 fixed | PH RESONANCE (`0x41d`): 50 → 100; PH TEMPO SYNC (`0x41a`): 0 fixed; PH DEPTH (`0x41b`): 0 fixed; PH MANUAL (`0x41c`): 0 → 127 | None |
| 7. Ring Mod 1 (`0x65718`) | 11 / RING MODULATER | 0 (`0x3d5`): 127 → 0; RM FREQUENCY (`0x428`): 64 → 16; RM LEVEL (`0x42b`): 40 → 100 | 0 (`0x3d5`): 127 → 0; RM FREQUENCY (`0x428`): 0 → 110; RM LEVEL (`0x42b`): 80 → 50 | None |
| 8. Ring Mod 2 (`0x659a4`) | 11 / RING MODULATER | 0 (`0x3d5`): 127 → 0; RM FREQUENCY (`0x428`): 64 → 5; RM LEVEL (`0x42b`): 90 → 93 | 0 (`0x3d5`): 0 fixed; RM FREQUENCY (`0x428`): 64 → 110; RM LEVEL (`0x42b`): 80 → 65 | None |

## BIT CRUSH

| Variation / decoded record | Engine ID / name | Left side | Right side | TIME target |
| --- | --- | --- | --- | --- |
| 1. Bit Crush 1 (`0x65c30`) | 12 / BIT CRUSH | BC SAMPLE RATE (`0x42e`): 0 → 64; BC FILTER (`0x42d`): 127 → 110; 0 (`0x3d5`): 127 → 64; BC LEVEL (`0x430`): 0 → 127 | BC SAMPLE RATE (`0x42e`): 0 → 88; BC FILTER (`0x42d`): 127 fixed; 0 (`0x3d5`): 127 → 0; BC LEVEL (`0x430`): 0 → 115 | BC BIT RATE (`0x42f`) |
| 2. Bit Crush 2 (`0x65ebc`) | 12 / BIT CRUSH | BC SAMPLE RATE (`0x42e`): 20 → 105; BC FILTER (`0x42d`): 0 → 50; 0 (`0x3d5`): 127 → 0; BC LEVEL (`0x430`): 0 → 127 | BC SAMPLE RATE (`0x42e`): 50 → 105; BC FILTER (`0x42d`): 0 fixed; 0 (`0x3d5`): 127 → 0; BC LEVEL (`0x430`): 0 → 85 | BC BIT RATE (`0x42f`) |
| 3. Distortion 1 (`0x66148`) | 13 / DISTORTION | 0 (`0x3d5`): 127 → 0; DS LEVEL (`0x436`): 0 → 16; DS DRIVE (`0x432`): 0 → 38; DS TONE (`0x433`): 39 → 0 | 0 (`0x3d5`): 127 → 0; DS LEVEL (`0x436`): 0 → 18; DS DRIVE (`0x432`): 0 → 38; DS TONE (`0x433`): 30 → 90 | DS TYPE (`0x435`) |
| 4. Distortion 2 (`0x663d4`) | 13 / DISTORTION | 0 (`0x3d5`): 127 → 0; DS LEVEL (`0x436`): 0 → 16; DS DRIVE (`0x432`): 0 → 80; DS TONE (`0x433`): 58 → 0 | 0 (`0x3d5`): 127 → 0; DS LEVEL (`0x436`): 0 → 18; DS DRIVE (`0x432`): 0 → 80; DS TONE (`0x433`): 48 → 110 | DS TYPE (`0x435`) |
| 5. Stretcher 1 (`0x66660`) | 17 / STRETCHER | STR BPM SYNC (`0x448`): 0 → 127; STR CUTOFF (`0x449`): 0 → 127 | STR BPM SYNC (`0x448`): 0 → 127 | None |
| 6. Stretcher 2 (`0x668ec`) | 17 / STRETCHER | STR BPM SYNC (`0x448`): 0 → 127; STR CUTOFF (`0x449`): 0 → 127 | STR BPM SYNC (`0x448`): 0 → 127 | None |
| 7. Pitch Shift 1 (`0x66b78`) | 3 / SPIRAL | PS PITCH1 (`0x3ee`): 24 → 0; PS PITCH2 (`0x3f1`): 24 → 0; PS LEVEL1 (`0x3f0`): 15 → 127; 0 (`0x3d5`): 127 → 0 | PS PITCH1 (`0x3ee`): 24 → 48; PS PITCH2 (`0x3f1`): 24 → 48; PS LEVEL1 (`0x3f0`): 15 → 110; 0 (`0x3d5`): 127 → 0 | None |
| 8. Pitch Shift 2 (`0x66e04`) | 3 / SPIRAL | PS PITCH1 (`0x3ee`): 24 → 12; PS PITCH2 (`0x3f1`): 24 → 12; PS LEVEL1 (`0x3f0`): 0 → 127; 0 (`0x3d5`): 127 → 0 | PS PITCH1 (`0x3ee`): 24 → 36; PS PITCH2 (`0x3f1`): 24 → 36; PS LEVEL1 (`0x3f0`): 0 → 85; 0 (`0x3d5`): 127 → 0 | None |

## ROLL

| Variation / decoded record | Engine ID / name | Left side | Right side | TIME target |
| --- | --- | --- | --- | --- |
| 1. Roll (`0x67090`) | 14 / RE-TRIGGER | RTG RESONANCE (`0x43a`): 0 → 80; RTG CUTOFF (`0x439`): 0 → 110; RTG RATE (`0x437`): 7 → 0 | RTG RESONANCE (`0x43a`): 0 fixed; RTG CUTOFF (`0x439`): 0 fixed; RTG RATE (`0x437`): 7 → 0 | None |
| 2. Roll Tri (`0x6731c`) | 14 / RE-TRIGGER | RTG RESONANCE (`0x43a`): 0 → 80; RTG CUTOFF (`0x439`): 0 → 110; RTG RATE (`0x437`): 7 → 0 | RTG RESONANCE (`0x43a`): 0 fixed; RTG CUTOFF (`0x439`): 0 fixed; RTG RATE (`0x437`): 7 → 0 | None |
| 3. Roll (Time) (`0x675a8`) | 14 / RE-TRIGGER | RTG RESONANCE (`0x43a`): 32 → 80; RTG CUTOFF (`0x439`): 0 → 112 | RTG RESONANCE (`0x43a`): 0 fixed; RTG CUTOFF (`0x439`): 0 → 64 | RTG RATE (`0x437`) |
| 4. Roll (Time) w/Dry (`0x67834`) | 14 / RE-TRIGGER | RTG RESONANCE (`0x43a`): 32 → 80; RTG CUTOFF (`0x439`): 0 → 112; 0 (`0x3d5`): 127 → 0; RTG LEVEL (`0x43b`): 0 → 127 | RTG RESONANCE (`0x43a`): 0 fixed; RTG CUTOFF (`0x439`): 0 fixed; 0 (`0x3d5`): 127 → 0; RTG LEVEL (`0x43b`): 0 → 127 | RTG RATE (`0x437`) |
| 5. Tape Stop Roll (`0x67ac0`) | 16 / TAPE STOP | TPS FILTER MOD (`0x442`): 64 → 127; TPS RESONANCE (`0x443`): 16 → 64; TPS AMP MOD (`0x444`): 0 fixed; TPS RATE (`0x440`): 8 → 1 | TPS AMP MOD (`0x444`): 0 → 64; TPS RESONANCE (`0x443`): 0 fixed; TPS FILTER MOD (`0x442`): 0 → 64; TPS RATE (`0x440`): 8 → 1 | None |
| 6. Tape Stop 1/4 (`0x67d4c`) | 16 / TAPE STOP | TPS FILTER MOD (`0x442`): 0 → 127; TPS RESONANCE (`0x443`): 16 → 69; TPS AMP MOD (`0x444`): 0 fixed | TPS AMP MOD (`0x444`): 0 → 64; TPS RESONANCE (`0x443`): 0 fixed; TPS FILTER MOD (`0x442`): 0 → 127 | None |
| 7. Tape Stop (Time) (`0x67fd8`) | 16 / TAPE STOP | TPS FILTER MOD (`0x442`): 0 → 127; TPS RESONANCE (`0x443`): 16 → 69; TPS AMP MOD (`0x444`): 0 fixed | TPS AMP MOD (`0x444`): 0 → 64; TPS RESONANCE (`0x443`): 0 fixed; TPS FILTER MOD (`0x442`): 0 → 127 | TPS RATE (`0x440`) |
| 8. Tape Stop Long (`0x68264`) | 16 / TAPE STOP | TPS FILTER MOD (`0x442`): 0 → 127; TPS RESONANCE (`0x443`): 16 → 69; TPS AMP MOD (`0x444`): 0 fixed | TPS AMP MOD (`0x444`): 0 → 64; TPS RESONANCE (`0x443`): 0 fixed; TPS FILTER MOD (`0x442`): 0 → 127 | None |

## Reproduce a row

From the repository root, run the following read-only snippet with
`.venv/bin/python`. It prints DELAY variation 4. Change `bank` (0–5) and
`variation` (1–8) to inspect another record. It checks the supported decoded-image
identity and reads original data, not a decompiler's inferred structure.

```python
import hashlib
from pathlib import Path
import struct
import sys
sys.path.insert(0, "tools")
from routing_hardware_audit import MAIN_SHA256

blob = Path("analysis/container_app_main.bin").read_bytes()
assert hashlib.sha256(blob).hexdigest() == MAIN_SHA256
bank, variation = 0, 4
assert 0 <= bank < 6 and 1 <= variation <= 8
start = 0x60ab0 + (bank * 8 + variation - 1) * 652
record = struct.unpack_from("<163I", blob, start)
print("engine", record[0], "decoded record", hex(start))
for side, first in (("left", 0x469), ("right", 0x45d)):
    for parameter in range(first, first + 12, 3):
        target, low, high = record[parameter - 0x3d3:parameter - 0x3d3 + 3]
        if target:
            low = low if low < 0x80000000 else low - 0x100000000
            high = high if high < 0x80000000 else high - 0x100000000
            print(side, hex(target + 0x3d4), low, high)
time = record[0x475 - 0x3d3]
print("TIME", hex(time + 0x3d4) if time else "unused")
```
