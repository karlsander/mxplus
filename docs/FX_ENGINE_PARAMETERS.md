# Internal performance FX engines and parameters

[Effects and DSP findings](DSP_FINDINGS.md) · [All 48 factory macro mappings](FX_MACRO_MAPPINGS.md)

The supported original main application enumerates **20 algorithm IDs: bypass
plus 19 effect engines**. The panel variations are presets of these engines;
Room, Hall and Reverb Mod, for example, use the same reverb algorithm.
This inventory concerns performance MASTER FX, not the separate channel BEAT FX
or mastering processor.

Reverb has **seven active engine parameters**: type, time, pre-delay, HPF, LPF,
density and effect level. Its eighth named entry is unused and has no registered
callback. The [new internal send](FX_SENDS.md) currently exposes density and time;
its variation chooses the factory type/settings and its other engine settings
come from that factory preset.

| Algorithm ID | Original engine name | Engine-specific parameters | Active entries |
| --- | --- | --- | --- |
| 0 | Bypass | None | 0 |
| 1 | Delay | Type; time; sync on/off; sync note; feedback; LF damping; HF damping; effect level | 8 |
| 2 | Tape Echo | Mode; repeat rate; sync on/off; sync note; feedback; bass; treble; short/middle/long head pan; tape distortion; wow/flutter rate; wow/flutter depth; effect level | 14 |
| 3 | Spiral | Voice; feedback; pitch 1; pre-delay 1; level 1; pitch 2; pre-delay 2; level 2 | 8 |
| 4 | Reverb | Type; time; pre-delay; HPF; LPF; density; effect level | 7 |
| 5 | Filter Drive | Filter type; cutoff; resonance; drive | 4 |
| 6 | Isolator | Low; mid; high | 3 |
| 7 | Equalizer | Low cut; low gain; low-mid frequency/resonance/gain; high-mid frequency/resonance/gain; high cut; high gain; level | 11 |
| 8 | Flanger | Rate; sync on/off; sync note; depth; manual; resonance; separation; HPF; effect level | 9 |
| 9 | Phaser | Type; rate; sync on/off; tempo sync; depth; manual; resonance; step rate; step sync; effect level | 10 |
| 10 | Chorus | Mode; rate; depth; pre-delay; HPF; LPF; level | 7 |
| 11 | Ring Modulator | Frequency; polarity; sense; level | 4 |
| 12 | Bit Crush | Filter type; filter; sample rate; bit rate; level | 5 |
| 13 | Distortion | Mode; drive; tone; amp switch; type; level | 6 |
| 14 | Re-trigger | Rate; triplet switch; cutoff; resonance; level | 5 |
| 15 | Reverser | Rate; cutoff; resonance; level | 4 |
| 16 | Tape Stop | Rate; depth; filter modulation; resonance; amp modulation; hold switch | 6 |
| 17 | Stretcher | Rate; pitch switch; BPM sync; cutoff; resonance | 5 |
| 18 | Scatter | Type; depth 1; control 4; control 5; control 6 | 5 |
| 19 | Oscillator | OSC; pitch; filter type; cutoff; resonance; delay sync note; delay feedback; delay effect level; noise level | 9 |

“Active entries” means named parameters with nontrivial registered callbacks,
not physical listening validation or complete DSP source recovery. Display
spellings are expanded for readability. In particular, `SC CONTROL4..6` remain
unnamed controls: their musical meanings have not been established here. `OSC`
is the original parameter name; its complete value enumeration is not claimed.
The decoded mode/type enumerations are listed below. Other physical units,
ranges and scaling curves require parameter-specific decoding; a raw 0–127 value is not necessarily a linear
physical quantity.

There are also shared controls outside these counts: algorithm selection
(`TYPE`), enable (`SW`), and the unnamed parameter `0` whose original callback
controls the instance's dry contribution for the send algorithms. The send sets
that dry contribution to zero and keeps its independent instance enabled.

## Evidence anchors

All CPU addresses below are **app_main**, in its resident region: runtime equals
`0x60000000 + decoded offset`. The original input SHA-256 remains
`26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`.

- Engine enumeration string: decoded `0xb08af`, runtime `0x600b08af`.
  It lists BYPASS, DELAY, TAPE ECHO, SPIRAL, REVERB, FILTER DRIVE, ISOLATOR,
  EQUALIZER, FLANGER, PHASER, CHORUS, RING MODULATER, BIT CRUSH, DISTORTION,
  RE-TRIGGER, REVERSER, TAPE STOP, STRETCHER, SCATTER, OSCILLATOR.
- ID-indexed parameter-name pointers: decoded `0x6f278`, runtime `0x6006f278`;
  each pointer is at `table + 4 * parameter_ID`.
- Registered `{ID, callback, secondary}` records: decoded
  `0xb5594..0xb7130`, runtime `0x600b5594..0x600b7130`.
  [The stock audit](../tools/fx_sends_audit.py) parses this registry.
- Parameter families: Delay `0x3d6..0x3dd`, Tape Echo `0x3de..0x3eb`,
  Spiral `0x3ec..0x3f3`, Reverb `0x3f4..0x3fa`, Filter Drive `0x3fc..0x3ff`,
  Isolator `0x400..0x402`, Equalizer `0x403..0x40d`, Flanger `0x40e..0x416`,
  Phaser `0x417..0x420`, Chorus `0x421..0x427`, Ring Modulator `0x428..0x42b`,
  Bit Crush `0x42c..0x430`, Distortion `0x431..0x436`, Re-trigger
  `0x437..0x43b`, Reverser `0x43c..0x43f`, Tape Stop `0x440..0x445`,
  Stretcher `0x446..0x44a`, Scatter `0x44b..0x452`, Oscillator `0x453..0x45c` (excluding dummy `0x45a`).
- Reverb's seven callbacks are runtime `0x6002b648`, `0x6002b66a`,
  `0x6002b68c`, `0x6002b6ae`, `0x6002b6d0`, `0x6002b6f2`, `0x6002b714`.
  ID `0x3fb`, named `RV (not use)`, has no callback record.
- Scatter control 1/2/3 (IDs `0x44d..0x44f`) have registered callbacks at
  runtime `0x6002c366/368/36a`, but their branch chains lead through
  `0x6002bb8c` to `BX LR` at `0x6002b3c4`. They do no work. Control 4/5/6
  have real engine writers; interpreting them as particular musical controls
  from their names alone would be speculative.
- Oscillator entry `0x45a` (DUMMY) has a null callback. It is a hole, not
  the end of the table: `0x45b` (DD EFX LEVEL) at decoded `0xb7118`
  registers runtime `0x6002c01c`, and `0x45c` (NOISE LEVEL) at decoded
  `0xb7124` registers runtime `0x6002c058`. Their original instructions check
  algorithm 19 and call writers `0x6003b032` and `0x6003b064`. The earlier
  seven-control inventory stopped before this hole; the correct count is nine.

The original [partial DSP listings](DSP_DISASSEMBLY.md) contain all twenty
algorithms in both relocated slots. [Send implementation evidence](FX_SENDS.md)
separately records the three algorithms currently used by the internal send
and the original callbacks executed by its tests.


## Six panel banks and their eight variations

Each of the 48 records at main decoded `0x60ab0`, runtime `0x60060ab0`,
has 163 little-endian words (652 bytes). Its first word is one algorithm ID;
the rest contains initial parameters and macro assignments. In bank order:

| Button | Variations 1–8 | Engine IDs in that order |
| --- | --- | --- |
| DELAY | Stereo Delay; Pan Delay; Cross Delay; Stereo Delay & Pan Delay; Spiral; Room; Hall; Reverb Mod | 1, 1, 1, 1, 3, 4, 4, 4 |
| FILTER | Filter 6dB; Filter 12dB; Filter 24dB; Iso Hi-Low; Iso Low; Iso Hi-Mid; Oscillator; Noise | 5, 5, 5, 6, 6, 6, 19, 19 |
| SCATTER | Scatter 1 through Scatter 8 | 18 for all eight |
| FLANGER | Flanger 1; Flanger 2; Flanger Manual; Phaser 1; Phaser 2; Phaser Manual; Ring Mod 1; Ring Mod 2 | 8, 8, 8, 9, 9, 9, 11, 11 |
| BIT CRUSH | Bit Crush 1; Bit Crush 2; Distortion 1; Distortion 2; Stretcher 1; Stretcher 2; Pitch Shift 1; Pitch Shift 2 | 12, 12, 13, 13, 17, 17, 3, 3 |
| ROLL | Roll; Roll Tri; Roll (Time); Roll (Time) w/Dry; Tape Stop Roll; Tape Stop 1/4; Tape Stop (Time); Tape Stop Long | 14, 14, 14, 14, 16, 16, 16, 16 |

Public variation names are confirmed by [Roland's variation list](https://support.roland.com/hc/ja/articles/4404526414363-MX-1-MFX%E3%81%AE%E3%83%90%E3%83%AA%E3%82%A8%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%AB%E3%81%AF%E4%BD%95%E3%81%8C%E3%81%82%E3%82%8A%E3%81%BE%E3%81%99%E3%81%8B);
engine IDs come from the original records. Tape Echo, Equalizer, Chorus and
Reverser exist in the firmware but none of these 48 stock presets selects them.
That finding does not imply they have been physically tested as hidden effects.

These banks do not describe six simultaneously instantiated engines. COMBI
switches the chosen effect over sequencer steps, as stated in the [owner's
manual, MASTER FX section](https://cdn.roland.com/assets/media/pdf/MX-1_e01_W.pdf)
and seen in original main routine `0x6002ac4a`. The original two slots provide
type-change transitions. Some individual algorithms themselves combine stages:
Oscillator includes filter and delay controls; Spiral has two pitch/delay voices.

## The large knob is a macro

Each record's parameters `0x45d..0x474` contain **four target/min/max triples
for the right side and four for the left side**. `0x475` selects the TIME target.
Targets are local parameter indices; add `0x3d4` to obtain the global ID.
Zero means an unused macro slot. A min/max pair can be equal, selecting a
fixed mode as soon as that side is active. The stock center is the OFF position.

Original main instructions at `0x6002a5e2..0x6002a690` choose sides, interpolate
values, resolve callbacks and clamp to the parameter bounds. The loop ends after
four mappings at `0x6002a6fc..0x6002a702`. Live knob updates at `0x6002a768`
use the same four-map structure. The right-side distance is `(knob-64)/63`;
the left is `(64-knob)/64`, with original integer arithmetic.

Examples from the records:

- DELAY variation 4: both sides sweep feedback 0–127 and effect level 15–108;
  left fixes delay type 2 (Pan), right fixes type 1 (Stereo). It is one engine
  with different parameter states on the two sides, not two parallel delays.
- FILTER variations 1–3: left selects LPF/LPF2/LPF3, right HPF/HPF2/HPF3,
  with a cutoff sweep. TIME selects resonance. Their public slope names are
  6/12/24 dB respectively.
- SCATTER variations assign depth, type, Control 4 and Control 6 together;
  TIME selects Control 5. Left/right type pairs are 0/1, 2/3, 4/5, 6/7,
  10/11, 12/13, 14/15 and 16/17. Thus the eight variations are eight macro
  configurations, not simply eight consecutive values of SC TYPE.

The new internal send currently takes the variation's initial settings and
exposes two direct controls. It does not reproduce these performance knob macros.
In particular its fourth delay choice takes variation 4's Stereo initial state;
it does not sweep between Pan and Stereo with the two direct send controls.

## Mode/type values

The original parameter display metadata is an eight-byte record per global ID
at decoded `0x70c08`, runtime `0x60070c08`. Its first word points to a list
(separated by byte `0x01`) or a numeric range (byte `0x02`). These records supply
the following enumerations, corroborated by factory values and macro mappings.
Raw values below are zero-based, not panel variation numbers.

| Parameter | Raw values |
| --- | --- |
| DD TYPE (`0x3d6`) | 0 Single; 1 Stereo; 2 Pan; 3 Cross |
| RE MODE (`0x3de`) | 0 Short; 1 Middle; 2 Long; 3 S+M; 4 S+L; 5 M+L; 6 S+M+L |
| PS VOICE (`0x3ec`) | 0 1MONO; 1 2MONO; 2 STEREO |
| RV TYPE (`0x3f4`) | Numeric 0–6. Factory Room uses 0, Hall 3, Reverb Mod 5. No names recovered for 1, 2, 4 or 6. |
| FILTER TYPE (`0x3fc`) | 0 LPF; 1 HPF; 2 LPF2; 3 HPF2; 4 LPF3; 5 HPF3 |
| PH TYPE (`0x417`) | 0 4-stage; 1 8-stage; 2 12-stage; 3 Bi-phase |
| CH MODE (`0x421`) | 0 Mono; 1 Stereo1; 2 Stereo2 |
| RM POLARITY (`0x429`) | 0 Up; 1 Down |
| BC FILTER TYPE (`0x42c`) | 0 LPF; 1 HPF |
| DS MODE (`0x431`) | 0 Overdrive; 1 Distortion |
| DS TYPE (`0x435`) | 0 Small; 1 Built-in; 2 2-stack; 3 3-stack; interpreted as amp/cabinet choice alongside DS AMP SW |
| OSC (`0x453`) | 0 Noise; 1 Saw; 2 Pulse |
| Oscillator FILTER TYPE (`0x455`) | 0 LPF; 1 HPF; 2 LPF2; 3 HPF2 |

SC TYPE metadata advertises 0–127 without labels; only the factory-used values
listed above are established here as panel mappings. That range alone is not
proof of 128 implemented Scatter patterns. Likewise numeric RV TYPE values
cannot safely be assigned names from another Roland product.

Display metadata is not authoritative for all processing semantics. For example,
DD SYNC's text lists ON/OFF, but original writer `0x60033d6a` and time calculation
`0x60033d04` show that raw 1 enables tempo-derived time and raw 0 uses free time.
The internal send's free-time setting remains correct.
