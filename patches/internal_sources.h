#ifndef MX1_INTERNAL_SOURCES_H
#define MX1_INTERNAL_SOURCES_H
#include <stdint.h>

enum {
    MX1_BD_STEPS = 16,
    MX1_INTERNAL_NOISE_BIT = 1u << 16,
    MX1_INTERNAL_BD_BITS = (1u << 11) - 1,
    MX1_INTERNAL_PORT_COUNT = 12,
    MX1_INTERNAL_NOISE_OPERAND = 0xa040,
    MX1_INTERNAL_BD_OPERAND = 0xa041
};

/* One aligned word per step is the UI-to-audio publication boundary:
 * bit 0 = enabled; bits 8..15 = signed semitones; bits 16..23 = decay 0..100.
 * No channel-global pitch/decay or persistent storage is introduced. */
uint32_t mx1_bd_step_get(uint32_t strip, uint32_t step);
void mx1_bd_step_toggle(uint32_t strip, uint32_t step);
void mx1_bd_step_adjust(uint32_t strip, uint32_t step, uint32_t parameter,
                        int32_t delta);
int mx1_bd_current_step(void);

/* DSP task publishes source availability; the sample IRQ owns all voices. */
void mx1_internal_routes(uint32_t mask);
void mx1_internal_render(uint32_t sample_rate, volatile uint32_t *ports);
void mx1_internal_audio_frame(void);
/* Audio callback only: forget normal-program bank state without writing MMIO. */
void mx1_internal_invalidate(void);

/* A separate 16-step counter follows the original shuffled step callbacks.
 * Original BFX LAST STEP values never shorten this counter. */
void mx1_internal_step(void);
void mx1_internal_transport_reset(void);
void mx1_internal_clock_start(void);
void mx1_internal_clock_stop(void);
void mx1_internal_clock_step(void *context, uint32_t native_step);

extern volatile uint32_t mx1_bd_steps[11][MX1_BD_STEPS];
extern volatile uint32_t mx1_bd_clock;
extern volatile uint32_t mx1_internal_active_mask;
#endif
