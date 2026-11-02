#include "internal_sources_dsp.h"

/* Round(sin(i*pi/128) * 32767), i=0..64; interpolation adds eight bits.
 * Generated from the mathematical definition, not imported from a library. */
static const int16_t sine_quarter[65] = {
    0,804,1608,2410,3212,4011,4808,5602,
    6393,7179,7962,8739,9512,10278,11039,11793,
    12539,13279,14010,14732,15446,16151,16846,17530,
    18204,18868,19519,20159,20787,21403,22005,22594,
    23170,23731,24279,24811,25329,25832,26319,26790,
    27245,27683,28105,28510,28898,29268,29621,29956,
    30273,30571,30852,31113,31356,31580,31785,31971,
    32137,32285,32412,32521,32609,32678,32728,32757,32767
};

/* Round(13.75*2^(semitone/12)*2^32/sample_rate). Octaves are shifts. */
static const uint32_t increments[3][12] = {
    {1339134,1418763,1503127,1592507,1687203,1787529,
     1893821,2006434,2125742,2252146,2386065,2527948},
    {1230329,1303488,1380998,1463116,1550118,1642292,
     1739948,1843411,1953026,2069159,2192197,2322552},
    {615165,651744,690499,731558,775059,821146,
     869974,921705,976513,1034579,1096099,1161276}
};

void mxkick_reset(mxkick_voice *v)
{
    v->phase = v->step = v->bend = v->bend_drop = 0;
    v->envelope = v->envelope_drop = v->crossfade = 0;
    v->last = v->previous = 0;
}

int mxkick_trigger(mxkick_voice *v, uint32_t sr, int32_t semitone, uint32_t decay)
{
    uint32_t rate;
    if (sr == 44100) rate = 0;
    else if (sr == 48000) rate = 1;
    else if (sr == 96000) rate = 2;
    else return 0;
    if (semitone < -24) semitone = -24;
    if (semitone > 24) semitone = 24;
    if (decay > 100) decay = 100;
    uint32_t note = (uint32_t)(semitone + 24);
    uint32_t duration_ms = 30u + (decay * decay * decay * 1470u + 500000u) / 1000000u;
    static const uint32_t amplitude_numerators[3] = {
        336378492u,309047740u,154523870u
    };
    static const uint32_t sweep_drops[3] = {
        4864061u,4469267u,2235797u
    };
    v->phase = 0;
    v->previous = v->last;
    v->crossfade = 32;
    v->step = increments[rate][note % 12] << (note / 12);
    v->bend = 3u * v->step; /* Starts at four times the final frequency. */
    v->bend_drop = sweep_drops[rate]; /* 10 ms time constant. */
    v->envelope = 0x7fffffffu;
    v->envelope_drop = amplitude_numerators[rate] / duration_ms;
    return 1;
}

int16_t mxkick_next(mxkick_voice *v)
{
    if (v->envelope < 32768u) {
        v->envelope = 0;
        v->last = 0;
        return 0;
    }
    uint32_t phase = v->phase;
    uint32_t offset = phase & 0x3fffffffu;
    if (phase & 0x40000000u) offset = 0x40000000u - offset;
    uint32_t index = offset >> 24;
    int32_t sine = sine_quarter[index];
    if (index < 64) {
        uint32_t fraction = (offset >> 16) & 255u;
        sine += ((sine_quarter[index + 1] - sine) * (int32_t)fraction) >> 8;
    }
    if (phase & 0x80000000u) sine = -sine;
    int16_t sample = (int16_t)((sine * (int32_t)(v->envelope >> 16)) >> 16);
    if (v->crossfade) {
        /* Convex blend remains bounded even after closely spaced retriggers.
         * Its first sample equals the prior output, so retrigger adds no jump. */
        sample = (int16_t)(((int32_t)sample * (int32_t)(32u - v->crossfade)
                  + (int32_t)v->previous * (int32_t)v->crossfade) >> 5);
        --v->crossfade;
    }
    v->last = sample;
    v->phase += v->step + v->bend;
    v->envelope -= (uint32_t)(((uint64_t)v->envelope * v->envelope_drop) >> 31);
    if (v->bend > 1024u)
        v->bend -= (uint32_t)(((uint64_t)v->bend * v->bend_drop) >> 31);
    else v->bend = 0;
    return sample;
}

int16_t mxnoise_next(uint32_t *state)
{
    uint32_t x = *state ? *state : 0x6d2b79f5u;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    *state = x;
    return (int16_t)((int32_t)(x >> 18) - 8192);
}
