#ifndef MX1_CHANNEL_ROUTING_H
#define MX1_CHANNEL_ROUTING_H

#include <stdint.h>

/* Existing physical strips, in panel SELECT-key order. */
enum mx1_route_strip {
    MX1_STRIP_1, MX1_STRIP_2, MX1_STRIP_3, MX1_STRIP_4,
    MX1_STRIP_56, MX1_STRIP_DIGITAL, MX1_STRIP_USB1, MX1_STRIP_USB2,
    MX1_STRIP_USB3, MX1_STRIP_USB4, MX1_STRIP_COMPUTER, MX1_STRIP_COUNT
};

enum { MX1_ROUTE_AUTO = 0, MX1_ROUTE_NSE = 53, MX1_ROUTE_BD = 54, MX1_ROUTE_SOURCE_COUNT = 55 };

/* AUTO restores the current Roland source/connection policy. Routes save with scenes and stock system autosave.
 * Mono strips skip stereo-pair choices. Labels always
 * contain four initialized display characters; they need not end in NUL. */
uint32_t mx1_route_get(uint32_t strip);
void mx1_route_adjust(uint32_t strip, int32_t delta);
const char *mx1_route_label(uint32_t strip);

/* Called only by the DSP task, after its original parameter-queue drain. */
void mx1_route_dispatch(void);
void mx1_route_flush(void);

#endif
