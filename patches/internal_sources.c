/* Internal source state and sample renderer, written for mxplus 2026-11-02.
 * Control and DSP tasks never touch voice state. Each sample callback consumes
 * aligned word publications; it performs no allocation, parameter lookup,
 * DSP command-port operation, floating-point calculation or storage write.
 */
#include "internal_sources.h"
#include "internal_sources_dsp.h"

#define DATA __attribute__((section(".patch_data")))
#define DEFAULT_STEP ((uint32_t)MXKICK_DEFAULT_DECAY << 16)
#define ROW {DEFAULT_STEP, DEFAULT_STEP, DEFAULT_STEP, DEFAULT_STEP, \
             DEFAULT_STEP, DEFAULT_STEP, DEFAULT_STEP, DEFAULT_STEP, \
             DEFAULT_STEP, DEFAULT_STEP, DEFAULT_STEP, DEFAULT_STEP, \
             DEFAULT_STEP, DEFAULT_STEP, DEFAULT_STEP, DEFAULT_STEP}
volatile uint32_t mx1_bd_steps[11][MX1_BD_STEPS] DATA = {
    ROW, ROW, ROW, ROW, ROW, ROW, ROW, ROW, ROW, ROW, ROW
};
volatile uint32_t mx1_bd_clock DATA = 0;
volatile uint32_t mx1_internal_active_mask DATA = 0;
static uint32_t next_step DATA = 0;
static uint32_t last_clock DATA = 0;
/* No exchange ports belong to us until a generator is selected. In particular
 * a cold all-Auto boot must not probe the inferred generator bank at all. */
static uint32_t previous_mask DATA = 0;
static uint32_t previous_rate DATA = 0;
static uint32_t previous_running DATA = 0;
static volatile uint32_t transport_generation DATA = 0;
static uint32_t last_transport_generation DATA = 0;
static uint32_t noise_state DATA = 0x6d2b79f5u;
static mxkick_voice voices[11] DATA = {{0}};

static uint32_t running(void)
{
    return *(const volatile uint8_t *)0x600b4834u != 0;
}

uint32_t mx1_bd_step_get(uint32_t strip, uint32_t step)
{
    return strip < 11 && step < MX1_BD_STEPS ? mx1_bd_steps[strip][step] : 0;
}

void mx1_bd_step_toggle(uint32_t strip, uint32_t step)
{
    if (strip < 11 && step < MX1_BD_STEPS) mx1_bd_steps[strip][step] ^= 1u;
}

void mx1_bd_step_adjust(uint32_t strip, uint32_t step, uint32_t parameter,
                        int32_t delta)
{
    if (strip >= 11 || step >= MX1_BD_STEPS || parameter > 1 || !delta) return;
    uint32_t value = mx1_bd_steps[strip][step];
    int32_t change = delta > 0 ? 1 : -1;
    if (!parameter) {
        int32_t pitch = (int8_t)(value >> 8);
        pitch += change;
        if (pitch < -24) pitch = -24;
        if (pitch > 24) pitch = 24;
        value = (value & ~0xff00u) | ((uint32_t)(uint8_t)pitch << 8);
    } else {
        int32_t decay = (int32_t)((value >> 16) & 255u) + change;
        if (decay < 0) decay = 0;
        if (decay > 100) decay = 100;
        value = (value & ~0xff0000u) | ((uint32_t)decay << 16);
    }
    mx1_bd_steps[strip][step] = value;
}

int mx1_bd_current_step(void)
{
    uint32_t clock = mx1_bd_clock;
    return running() && (clock & 0x80000000u) ? (int)(clock & 15u) : -1;
}

void mx1_internal_routes(uint32_t mask)
{
    mx1_internal_active_mask = mask & (MX1_INTERNAL_BD_BITS | MX1_INTERNAL_NOISE_BIT);
}

void mx1_internal_transport_reset(void)
{
    next_step = 0;
    ++transport_generation;
    /* Advance the serial even on reset, so stop/start between audio callbacks
     * cannot make a new first step look identical to the old one. */
    mx1_bd_clock = (mx1_bd_clock + 16u) & 0x7ffffff0u;
}

void mx1_internal_step(void)
{
    if (!running()) return;
    uint32_t serial = (mx1_bd_clock + 16u) & 0x7ffffff0u;
    mx1_bd_clock = 0x80000000u | serial | next_step;
    next_step = (next_step + 1u) & 15u;
}

/* Signed Q15 samples have at most 16 significant bits, so this conversion is
 * exact in IEEE binary32. It never touches Roland's shared conversion unit. */
static uint32_t sample_word(int32_t sample)
{
    if (!sample) return 0;
    uint32_t magnitude = sample < 0 ? (uint32_t)-sample : (uint32_t)sample;
    uint32_t leading = (uint32_t)__builtin_clz(magnitude);
    uint32_t exponent = 143u - leading; /* 127 + (31 - leading) - 15. */
    uint32_t fraction = (magnitude << (leading - 8u)) & 0x7fffffu;
    return (sample < 0 ? 0x80000000u : 0u) | (exponent << 23) | fraction;
}

void mx1_internal_invalidate(void)
{
    /* Diagnostics own the exchange bank. Force active voices to reset on
     * return, retaining the actual ownership mask so never-selected ports
     * remain untouched. Removed owned ports still receive their final zero. */
    previous_rate = 0;
    last_clock = mx1_bd_clock;
}

void mx1_internal_render(uint32_t sample_rate, volatile uint32_t *ports)
{
    uint32_t mask = mx1_internal_active_mask;
    uint32_t clock = mx1_bd_clock;
    uint32_t transport = running();
    uint32_t generation = transport_generation;
    if (sample_rate != 44100 && sample_rate != 48000 && sample_rate != 96000)
        mask = 0; /* Invalid rate is silence, never out-of-bounds table access. */
    if (!mask && !previous_mask) {
        last_clock = clock;
        previous_running = transport;
        last_transport_generation = generation;
        return;
    }
    uint32_t reset_all = sample_rate != previous_rate ||
                         generation != last_transport_generation ||
                         transport != previous_running;
    uint32_t trigger = transport && (clock & 0x80000000u) && clock != last_clock;
    if (mask & MX1_INTERNAL_NOISE_BIT) ports[0] = sample_word(mxnoise_next(&noise_state));
    else if (previous_mask & MX1_INTERNAL_NOISE_BIT) ports[0] = 0;
    uint32_t removed = previous_mask & ~mask & MX1_INTERNAL_BD_BITS;
    while (removed) {
        uint32_t strip = (uint32_t)__builtin_ctz(removed);
        removed &= removed - 1u;
        mxkick_reset(&voices[strip]);
        ports[strip + 1] = 0;
    }
    uint32_t active = mask & MX1_INTERNAL_BD_BITS;
    while (active) {
        uint32_t strip = (uint32_t)__builtin_ctz(active);
        active &= active - 1u;
        uint32_t bit = 1u << strip;
        if (reset_all || !(previous_mask & bit)) mxkick_reset(&voices[strip]);
        if (!transport || !(clock & 0x80000000u)) {
            if (reset_all || !(previous_mask & bit)) ports[strip + 1] = 0;
            continue;
        }
        if (trigger) {
            uint32_t step = mx1_bd_steps[strip][clock & 15u];
            if (step & 1u)
                mxkick_trigger(&voices[strip], sample_rate, (int8_t)(step >> 8),
                               (step >> 16) & 255u);
        }
        ports[strip + 1] = sample_word(mxkick_next(&voices[strip]));
    }
    previous_mask = mask;
    previous_rate = sample_rate;
    previous_running = transport;
    last_transport_generation = generation;
    last_clock = clock;
}

extern void mx1_internal_start_original(void);
extern void mx1_internal_stop_original(void);
extern void mx1_internal_step_original(void *context, uint32_t native_step);

void mx1_internal_clock_start(void)
{
    if (!running()) mx1_internal_transport_reset();
    mx1_internal_start_original();
}

void mx1_internal_clock_stop(void)
{
    mx1_internal_stop_original();
    mx1_internal_transport_reset();
}

void mx1_internal_clock_step(void *context, uint32_t native_step)
{
    mx1_internal_step_original(context, native_step);
    mx1_internal_step();
}
