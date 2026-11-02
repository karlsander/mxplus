#ifndef MXPLUS_INTERNAL_SOURCES_DSP_H
#define MXPLUS_INTERNAL_SOURCES_DSP_H
#include <stdint.h>

/* Bounded numerical engine; hardware integration is separate.
 * A 32-bit phase oscillator and two decaying envelopes are the generic
 * synthesis structure also used by Batboy's compact bass drum. This integer
 * implementation is written for mxplus research; no Batboy source is copied.
 * Caller owns each state. No globals, allocation, float or libm dependency. */
typedef struct {
    uint32_t phase, step, bend, bend_drop, envelope, envelope_drop;
    int16_t last, previous;
    uint32_t crossfade;
} mxkick_voice;

enum { MXKICK_DEFAULT_DECAY = 53 };
void mxkick_reset(mxkick_voice *voice);

/* Accepts 44100, 48000 or 96000 Hz. Pitch is semitones relative to 55 Hz;
 * range -24..24. Decay 0..100 gives 30..1500 ms to -60 dB, cubic mapping.
 * Unsupported rates reject without modifying voice. Reset/zero before first use.
 * Trigger resets phase with a 32-sample crossfade from the previous output.
 * The pitch sweep is fixed; there is no independent noise click. */
int mxkick_trigger(mxkick_voice *voice, uint32_t sample_rate,
                   int32_t semitones, uint32_t decay);
int16_t mxkick_next(mxkick_voice *voice);
int16_t mxnoise_next(uint32_t *state);
#endif
