/* B10: independent lifetime counters, never reset while requests can run.
 * Each stage has one task writer. Cross-stage reads are observational, not
 * an atomic transaction or a task-timing measurement. Values are stage-specific:
 * API entry length, core entry request pointer, HCD entry endpoint, or result.
 */
#ifndef MX1_HOST_TRACE_H
#define MX1_HOST_TRACE_H
#include <stdint.h>
enum { TRACE_API_IN, TRACE_API_OUT, TRACE_CORE_IN, TRACE_CORE_OUT,
       TRACE_HCD_IN, TRACE_HCD_OUT, TRACE_DONE, TRACE_STAGES };
typedef struct { uint32_t stage[TRACE_STAGES][3]; } MidiPipeline;
extern volatile MidiPipeline mx1_midi_pipeline[4][2];
extern volatile uint32_t debug_ticks;
void mx1_host_trace_hcd(void *, unsigned, int);
#endif
