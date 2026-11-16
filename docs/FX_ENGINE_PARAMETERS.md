# Internal performance FX engines and parameters

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
| 19 | Oscillator | OSC; pitch; filter type; cutoff; resonance; delay sync note; delay feedback | 7 |

“Active entries” means named parameters with nontrivial registered callbacks,
not physical listening validation or complete DSP source recovery. Display
spellings are expanded for readability. In particular, `SC CONTROL4..6` remain
unnamed controls: their musical meanings have not been established here. `OSC`
is the original parameter name; its complete value enumeration is not claimed.
Physical units, ranges, scaling curves and all type enumerations require
parameter-specific decoding; a raw 0–127 value is not necessarily a linear
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
  `0xb5594..0xb710c`, runtime `0x600b5594..0x600b710c`.
  [The stock audit](../tools/fx_sends_audit.py) parses this registry.
- Parameter families: Delay `0x3d6..0x3dd`, Tape Echo `0x3de..0x3eb`,
  Spiral `0x3ec..0x3f3`, Reverb `0x3f4..0x3fa`, Filter Drive `0x3fc..0x3ff`,
  Isolator `0x400..0x402`, Equalizer `0x403..0x40d`, Flanger `0x40e..0x416`,
  Phaser `0x417..0x420`, Chorus `0x421..0x427`, Ring Modulator `0x428..0x42b`,
  Bit Crush `0x42c..0x430`, Distortion `0x431..0x436`, Re-trigger
  `0x437..0x43b`, Reverser `0x43c..0x43f`, Tape Stop `0x440..0x445`,
  Stretcher `0x446..0x44a`, Scatter `0x44b..0x452`, Oscillator `0x453..0x459`.
- Reverb's seven callbacks are runtime `0x6002b648`, `0x6002b66a`,
  `0x6002b68c`, `0x6002b6ae`, `0x6002b6d0`, `0x6002b6f2`, `0x6002b714`.
  ID `0x3fb`, named `RV (not use)`, has no callback record.
- Scatter control 1/2/3 (IDs `0x44d..0x44f`) have registered callbacks at
  runtime `0x6002c366/368/36a`, but their branch chains lead through
  `0x6002bb8c` to `BX LR` at `0x6002b3c4`. They do no work. Control 4/5/6
  have real engine writers; interpreting them as particular musical controls
  from their names alone would be speculative.
- Oscillator entries `0x45a` (DUMMY), `0x45b` (DD EFX LEVEL) and `0x45c`
  (NOISE LEVEL) are named but have no registered callback in this table.
  They are excluded from the active count; their names alone do not establish
  independently editable controls.

The original [partial DSP listings](DSP_DISASSEMBLY.md) contain all twenty
algorithms in both relocated slots. [Send implementation evidence](FX_SENDS.md)
separately records the three algorithms currently used by the internal send
and the original callbacks executed by its tests.
