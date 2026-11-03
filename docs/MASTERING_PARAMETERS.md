# Mastering parameters in the original MX-1 firmware

All 65 names below are present in the supplied original main application. `N`
is the one-based hidden-editor number. Stored values are integer indices; the
display column describes the original format strings, not measured DSP units.
Gain/level and threshold names suggest dB, frequency tables suggest Hz, and
release tables suggest milliseconds. Those unit interpretations are not a DSP
calibration. In particular, Q **0–32**, enhancer frequency **0–64**, attack
**0–100** and splitter delay **0–10** must not be treated as proven physical units.

The exact extraction, including full enumeration strings, descriptor defaults
and per-name addresses, is in [mastering-verification.json](../build/mainline/mastering-verification.json).
Names start at main decoded `0x748c0`, runtime `0x600748c0`, with 28-byte records;
each preceding two-byte header contains its parameter ID. The executed original
lookup at decoded `0x1f866`, runtime `0x6001f866`, maps index `N-1` to
`0x476 + N-1`. Range descriptors begin at decoded `0x686d8`, runtime
`0x600686d8`, with 16 bytes per ID; display pointers begin at decoded `0x70c04`,
runtime `0x60070c04`, with 8 bytes per ID. Some descriptor defaults are outside
the advertised range, so they are not presented as verified preset defaults.

## Signal flow

Roland's [audio signal-flow diagram](https://static.roland.com/assets/media/pdf/MX-1_Signalflow.pdf)
places mastering after the Master FX/output sum and before MASTER LEVEL.
Its [mastering guide, Tip 10](https://rolandcorp.com.au/blog/the-ultimate-guide-to-the-aira-mx-1)
links the [ten preset chains](https://www.rolandcorp.com.au/blog/wp-content/uploads/2017/03/Mastering-Chain-Table-1024x423.jpg).
That is the source for preset order; the firmware parameter list alone does
not establish the order or active stages of each preset.

| Preset(s) | Published processing order |
| --- | --- |
| 1, 3, 7, 9 | EQ → low-cut → enhancer → three-band compressor → stereo imager → limiter |
| 2 | Low-cut → enhancer → three-band compressor → stereo imager → limiter |
| 4 | EQ → low-cut → three-band compressor → stereo imager → limiter |
| 5, 6 | EQ → enhancer → three-band compressor → stereo imager → limiter |
| 8 | Low-cut → three-band compressor → stereo imager → limiter |
| 10 | Low-cut → limiter |

Matching block lists do not imply identical parameter settings. This chart
does not establish whether a missing block is bypassed or absent from a DSP
program, or whether its switch can enable it in every preset.

The parameter families reveal EQ, low-cut, enhancer, a three-band splitter,
per-band expansion/compression and recombination, mid/side levels, limiter,
output level, clipping and dither. Interpreting SPL as a crossover feeding the
three dynamics bands, MIX as their recombination, and STR as mid/side processing
is supported by the names; exact DSP connections and bypass behavior require
further tracing or measurement. The extra stages should not be omitted merely
because the public preset chart simplifies its labels.

## Equalizer

| N | Firmware name | Meaning | Stored range | Display range / choices |
| --- | --- | --- | --- | --- |
| 1 | `EQ_SW` | EQ enable | 0–1 | OFF / ON |
| 2 | `EQ_IN_LEV` | EQ input level | 0–36 | -24–+12 |
| 3 | `EQ_L_TYPE` | Low filter type | 0–1 | SHLV / PEAK |
| 4 | `EQ_L_GAIN` | Low gain | 0–24 | -12–+12 |
| 5 | `EQ_L_FREQ` | Low frequency | 0–63 | 16–22k (64 choices) |
| 6 | `EQ_L_Q` | Low Q | 0–31 | 0–32 |
| 7 | `EQ_LM_GAIN` | Low-mid gain | 0–24 | -12–+12 |
| 8 | `EQ_LM_FREQ` | Low-mid frequency | 0–63 | 16–22k (64 choices) |
| 9 | `EQ_LM_Q` | Low-mid Q | 0–31 | 0–32 |
| 10 | `EQ_HM_GAIN` | High-mid gain | 0–24 | -12–+12 |
| 11 | `EQ_HM_FREQ` | High-mid frequency | 0–63 | 16–22k (64 choices) |
| 12 | `EQ_HM_Q` | High-mid Q | 0–31 | 0–32 |
| 13 | `EQ_H_TYPE` | High filter type | 0–1 | SHLV / PEAK |
| 14 | `EQ_H_GAIN` | High gain | 0–24 | -12–+12 |
| 15 | `EQ_H_FREQ` | High frequency | 0–63 | 16–22k (64 choices) |
| 16 | `EQ_H_Q` | High Q | 0–31 | 0–32 |
| 17 | `EQ_OUT_LEV` | EQ output level | 0–36 | -24–+12 |

## Low-cut filter

| N | Firmware name | Meaning | Stored range | Display range / choices |
| --- | --- | --- | --- | --- |
| 18 | `LCUT_SW` | Low-cut enable | 0–1 | OFF / ON |
| 19 | `LCUT_FREQ` | Low-cut frequency | 0–63 | 16–22k (64 choices) |

## Enhancer

| N | Firmware name | Meaning | Stored range | Display range / choices |
| --- | --- | --- | --- | --- |
| 20 | `EH_SW` | Enhancer enable | 0–1 | OFF / ON |
| 21 | `EH_SENS` | Enhancer sensitivity | 0–100 | 0–100 |
| 22 | `EH_FREQ` | Enhancer frequency control | 0–63 | 0–64 |
| 23 | `EH_LEV` | Enhancer level | 0–36 | -24–+12 |

## Three-band splitter

| N | Firmware name | Meaning | Stored range | Display range / choices |
| --- | --- | --- | --- | --- |
| 24 | `SPL_IN_LEV` | Splitter input level | 0–36 | -24–+12 |
| 25 | `SPL_DLY` | Splitter delay | 0–10 | 0–10 |
| 26 | `SPL_FREQ_L` | Low crossover frequency | 0–63 | 16–22k (64 choices) |
| 27 | `SPL_FREQ_H` | High crossover frequency | 0–63 | 16–22k (64 choices) |

## Three-band expander

| N | Firmware name | Meaning | Stored range | Display range / choices |
| --- | --- | --- | --- | --- |
| 28 | `EXP_SW` | Expander enable | 0–1 | OFF / ON |
| 29 | `EXP_L_THRE` | Low threshold | 0–80 | -80–0 |
| 30 | `EXP_L_RATIO` | Low ratio | 0–13 | 1.00–INF (14 choices; see below) |
| 31 | `EXP_L_ATK` | Low attack | 0–100 | 0–100 |
| 32 | `EXP_L_REL` | Low release | 0–100 | 50–5000 (101 choices) |
| 33 | `EXP_M_THRE` | Mid threshold | 0–80 | -80–0 |
| 34 | `EXP_M_RATIO` | Mid ratio | 0–13 | 1.00–INF (14 choices; see below) |
| 35 | `EXP_M_ATK` | Mid attack | 0–100 | 0–100 |
| 36 | `EXP_M_REL` | Mid release | 0–100 | 50–5000 (101 choices) |
| 37 | `EXP_H_THRE` | High threshold | 0–80 | -80–0 |
| 38 | `EXP_H_RATIO` | High ratio | 0–13 | 1.00–INF (14 choices; see below) |
| 39 | `EXP_H_ATK` | High attack | 0–100 | 0–100 |
| 40 | `EXP_H_REL` | High release | 0–100 | 50–5000 (101 choices) |

## Three-band compressor

| N | Firmware name | Meaning | Stored range | Display range / choices |
| --- | --- | --- | --- | --- |
| 41 | `CMP_SW` | Compressor enable | 0–1 | OFF / ON |
| 42 | `CMP_L_THRE` | Low threshold | 0–24 | -24–0 |
| 43 | `CMP_L_RATIO` | Low ratio | 0–13 | 1.00–INF (14 choices; see below) |
| 44 | `CMP_L_ATK` | Low attack | 0–100 | 0–100 |
| 45 | `CMP_L_REL` | Low release | 0–100 | 50–5000 (101 choices) |
| 46 | `CMP_M_THRE` | Mid threshold | 0–24 | -24–0 |
| 47 | `CMP_M_RATIO` | Mid ratio | 0–13 | 1.00–INF (14 choices; see below) |
| 48 | `CMP_M_ATK` | Mid attack | 0–100 | 0–100 |
| 49 | `CMP_M_REL` | Mid release | 0–100 | 50–5000 (101 choices) |
| 50 | `CMP_H_THRE` | High threshold | 0–24 | -24–0 |
| 51 | `CMP_H_RATIO` | High ratio | 0–13 | 1.00–INF (14 choices; see below) |
| 52 | `CMP_H_ATK` | High attack | 0–100 | 0–100 |
| 53 | `CMP_H_REL` | High release | 0–100 | 50–5000 (101 choices) |

## Band mixer

| N | Firmware name | Meaning | Stored range | Display range / choices |
| --- | --- | --- | --- | --- |
| 54 | `MIX_L_LEV` | Low-band level | 0–86 | -80–+6 |
| 55 | `MIX_M_LEV` | Mid-band level | 0–86 | -80–+6 |
| 56 | `MIX_H_LEV` | High-band level | 0–86 | -80–+6 |

## Stereo mid/side levels

| N | Firmware name | Meaning | Stored range | Display range / choices |
| --- | --- | --- | --- | --- |
| 57 | `STR_M_LEV` | Mid level | 0–36 | -24–+12 |
| 58 | `STR_S_LEV` | Side level | 0–36 | -24–+12 |

## Limiter

| N | Firmware name | Meaning | Stored range | Display range / choices |
| --- | --- | --- | --- | --- |
| 59 | `LMT_SW` | Limiter enable | 0–1 | OFF / ON |
| 60 | `LMT_THRE` | Limiter threshold | 0–24 | -24–0 |
| 61 | `LMT_ATK` | Limiter attack | 0–100 | 0–100 |
| 62 | `LMT_REL` | Limiter release | 0–100 | 50–5000 (101 choices) |

## Final output

| N | Firmware name | Meaning | Stored range | Display range / choices |
| --- | --- | --- | --- | --- |
| 63 | `OUT_LEV` | Final output level | 0–86 | -80–+6 |
| 64 | `CLIP_SW` | Clip enable | 0–1 | OFF / ON |
| 65 | `DITHER` | Dither setting | 0–17 | OFF; 24 down to 8 |

Ratio choices, in order: **1.00, 1.12, 1.25, 1.40, 1.60, 1.80, 2.00,
2.50, 3.20, 4.00, 5.60, 8.00, 16.0, INF**. A ratio-to-one interpretation is
consistent with the parameter names. Dither's numeric settings likely denote
bit depth; neither its algorithm nor noise shaping has been established here.

The new [mastering mode](MASTERING.md) exposes N1–N17. It does not change the
stock parameter definitions or synthesize additional EQ processing.
