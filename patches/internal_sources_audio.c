/* Internal-source sample hook for the frozen MX-1 main application.
 *
 * The original DSP0 slot-zero callback transfers exactly one computer frame.
 * Registration does not depend on a connected USB host. Retain that callback
 * first, then publish the independent generator samples into unused exchange
 * indices 0x40..0x4b. See docs/INTERNAL_SOURCES.md for the original
 * registration/IRQ evidence and the limits of the exchange-bank inference.
 */
#include "internal_sources.h"

void mx1_internal_audio_frame(void)
{
    ((void (*)(void))0x01009841u)();
    /* Diagnostic programs use different shared-port layouts. */
    if (*(const volatile uint32_t *)0x6051deb8u <= 3u)
        mx1_internal_render(*(const volatile uint32_t *)0x20000b24u,
                            (volatile uint32_t *)0x40101100u);
    else
        mx1_internal_invalidate();
}
