#ifndef MX1_INTERNAL_SOURCES_UI_H
#define MX1_INTERNAL_SOURCES_UI_H

#include <stdint.h>

/* Final physical event entry chains the existing SELECT + TEMPO picker. */
void mx1_sources_ui_event(const uint8_t *event);
int mx1_sources_ui_press(uint32_t key);
int mx1_sources_ui_release(uint32_t key);
void mx1_sources_ui_select_leds(void *context);
void mx1_sources_ui_steps(void *context);
void mx1_sources_ui_value(void *context);
void mx1_sources_ui_tempo(void *context);

/* -1 outside the eligible source edit view; route target also excludes held keys. */
int mx1_sources_ui_edit_target(void);
int mx1_sources_ui_route_target(void);
int mx1_sources_ui_target(void);

#endif
