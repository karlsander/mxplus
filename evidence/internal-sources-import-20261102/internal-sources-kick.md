# Internal noise and bass-drum numerical engines

The source is [internal_sources_dsp.c](../patches/internal_sources_dsp.c), with
its caller contract in [internal_sources_dsp.h](../patches/internal_sources_dsp.h).
This note covers the numerical generator only. Firmware integration, exchange
slots, routing, clocks, UI and their byte guards have separate evidence.
Numerical success does not establish audible output or a real-time margin on
the physical MX-1.

## Batboy reference and provenance

The requested reference was inspected at Batboy commit
`1b1ba51fad4fc6a6a07808d4207df8fd55b0a5e9` on 2 November 2026:

- [Current compact kick](https://github.com/karlsander/batboy/blob/1b1ba51fad4fc6a6a07808d4207df8fd55b0a5e9/src/pad_oscillator_drum5.inc),
  `drum5_init` / `render_drum5`.
- [Earlier percussion engines and their notice](https://github.com/karlsander/batboy/blob/1b1ba51fad4fc6a6a07808d4207df8fd55b0a5e9/src/osc_percussion.c),
  `bat_drum_init` / `bat_drum_render`.
- [Recorded measurement context](https://github.com/karlsander/batboy/blob/1b1ba51fad4fc6a6a07808d4207df8fd55b0a5e9/research/synth-roadmap5.md),
  “Isolated measurements.” These are Cortex-M7 instruction observations with
  floating-point arithmetic, not MX-1 measurements.

Batboy uses a phase accumulator and sine lookup, a falling pitch envelope,
an amplitude envelope, cubic drive, a short noise click and a final tone
filter. The older file identifies its Plaits/stmlib ancestry and contains
Emilie Gillet's 2016 copyright and MIT notice. The repository is private;
these links identify the research source for its owner.

The mxplus integer implementation is new project code. No Batboy source,
waveform table, compiler output or firmware bytes were copied into it. It
uses the generic swept-sine synthesis structure and omits the drive, click
and tone-filter stages. Its sine and tuning constants are generated from
their mathematical definitions. Project licensing remains as described in
[PROVENANCE.md](../PROVENANCE.md); this note does not grant a license to
Roland firmware or change the private reference repository's visibility.

## Bass drum

Each independent voice has a 32-byte state. There is no allocation, floating
point, libm call or mutable shared oscillator state. Supported sample rates
are 44,100, 48,000 and 96,000 Hz. An unsupported rate returns failure before
changing any voice byte. Callers zero-initialize or reset a voice before use.

The parameters are intended to be captured from the triggering step:

| Parameter | Range | Meaning |
| --- | --- | --- |
| Pitch | −24 to +24 semitones | Final oscillator frequency relative to 55 Hz; 13.75–220 Hz |
| Decay | 0–100 | Exponential body time to approximately −60 dB |

`MXKICK_DEFAULT_DECAY` is 53, approximately 249 ms. The default pitch is zero,
55 Hz. The cubic control curve gives useful resolution for short kicks:

| Decay value | Body time to approximately −60 dB |
| --- | --- |
| 0 | 30 ms |
| 25 | 53 ms |
| 50 | 214 ms |
| 53 | 249 ms |
| 75 | 650 ms |
| 100 | 1,500 ms |

The duration formula is `30 + round(1470 × (decay / 100)³)` milliseconds.
Both parameters clamp to their supported range. Each trigger captures
coefficients; an edit to a stored step does not need to alter an already
ringing voice.

The unsigned 32-bit phase accumulator advances by the tuned increment plus
a short decaying increment. Initial frequency is four times the final
frequency, falling with a 10 ms time constant. Even the highest allowed
initial pitch is 880 Hz. The sine uses a 65-entry signed 16-bit quarter-wave
table, reflection and linear interpolation. Frequency lookup contains one
octave for each supported rate; octave shifts extend it to the full pitch
range. The amplitude and pitch envelopes use bounded integer products.

Every trigger restarts phase and uses a 32-sample convex crossfade from the
last output. The first new sample equals the last old sample, removing an
instantaneous sample jump. Retriggering during an existing crossfade remains
bounded because the blend never sums two full-gain signals. At the three
rates the transition lasts about 0.73, 0.67 and 0.33 ms. This is a numerical
continuity property, not a guarantee of an inaudible change on the hardware.

Output is signed Q15 PCM with a peak no greater than 16,384 (approximately
−6 dBFS). The finite body reaches exact digital silence after its envelope
falls below the cutoff. The original source strip's gain, effects and fader
remain responsible for subsequent processing. There is no separate global
pitch or decay parameter in the engine.

## Constant white noise

`mxnoise_next` advances one xorshift32 state per sample. State zero recovers
to a fixed nonzero seed, avoiding the absorbing all-zero state. The top bits
map to the uniform integer range −8,192 through 8,191, approximately −12 dBFS
peak and −16.8 dBFS RMS. There is no envelope, sample-and-hold clock reduction
or filter. It is deterministic pseudorandom white noise, not a source of
cryptographic randomness. A caller may generate it once per frame and send
the same sample to multiple assigned strips.

## Verification and cost

Run the pinned environment's standalone verifier:

```bash
.venv/bin/python tools/internal_sources_dsp_verify.py --output build/generator-probe/dsp-verification.json
```

An optional `--preview-wav /tmp/mxplus-bd-preview.wav` produces five numerical
examples. That WAV is synthesized by the checked host build; it is not a
recording from a mixer.

The verifier checks all 147 supported rate/pitch combinations, 75 combinations
of rate/pitch/decay through their tails, 256 rapid retriggers, rejected-rate
immutability, control clamps, reset and one million noise samples. Nine
4,096-sample kick vectors and four 4,096-sample noise vectors execute the
actual compiled Cortex-M3 Thumb code. Their PCM and final state must match
the host C implementation byte for byte. No numerical engine call or PRNG
is stubbed. The host build enables undefined-behavior checks.

At the checked compiler settings, a voice occupies 32 bytes and the engine's
functions plus constant tables occupy about 0.75 KiB. Exact current sizes
and source hashes are recorded by the verifier. Measured instruction paths
include function entry and return:

| One call | Executed Cortex-M3 instructions |
| --- | --- |
| Silent bass drum | 10 |
| Bass drum onset with crossfade | 58 |
| Active body with pitch sweep | 51 |
| Active body after pitch settles | 46 |
| Voice reset | 6 |
| Noise | 12 |
| Noise recovering an all-zero state | 14 |

These are representative executed paths, not a worst-case bound over all
phase/control values. They are **not CPU cycles**. At 96 kHz, eleven active
voices alone would execute roughly 49–61 million instructions per second
at these observed paths, before the caller, sample conversion, exchange
writes, interrupt work or any retained firmware work. No processor clock
or available real-time headroom is inferred from those numbers. The physical
deadline and multi-voice limit require measurement.
