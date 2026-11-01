/* MX-1 source selection gesture, independently written 2026-11-01.
 * Uses original panel key state; no new polling task or writable UI state.
 * The original SELECT press/release callbacks are always preserved.
 * See research/channel-routing-ui.md for original-instruction evidence.
 */
#include "channel_routing.h"

typedef unsigned char ui_u8;
typedef unsigned short ui_u16;
typedef unsigned int ui_u32;

extern void mx1_route_ui_display_original(void *context);

/* Normal panel boot, normal main page, no transient modal display, exactly one
 * SELECT and no other physical button held. This leaves stereo-link and all
 * existing modified gestures to Roland's original code. */
static int target(void) {
    const volatile ui_u8 *keys = (const volatile ui_u8 *)0x605129a4u;
    if (*(const volatile ui_u32 *)0x600b4b94u != 0 ||
        *(const volatile ui_u16 *)0x600b4b5eu != 0 ||
        ((int (*)(const void *))0x60018259u)((const void *)0x605144ccu) != 0) return -1;
    int selected = -1;
    for (unsigned key = 0; key < 0x55; ++key) {
        if (!(keys[key >> 3] & (1u << (key & 7)))) continue;
        if (key < 0x29 || key > 0x33 || selected >= 0) return -1;
        selected = (int)key - 0x29;
    }
    return selected;
}

/* Original tempo renderer replacement. Text API draws exactly four bytes,
 * so mx1_route_label must return a space-padded four-character label. */
void mx1_route_ui_display(void *context) {
    int strip = target();
    if (strip < 0) {
        mx1_route_ui_display_original(context);
        return;
    }
    ((void (*)(void *, unsigned, const char *, unsigned))0x60054f85u)
        ((void *)0x60512984u, 1, mx1_route_label((unsigned)strip), 0);
}

/* Registration at main decoded offset 0xf5d8 originally points to 0x60010b49.
 * Its ABI is a four-byte physical event packet pointer in r0. */
void mx1_route_ui_event(const ui_u8 *event) {
    int select_key = (event[0] == 1 || event[0] == 2) &&
                     event[1] >= 0x29 && event[1] <= 0x33;
    int before = select_key ? target() : -1;
    if (event[0] == 4 && event[1] == 1) {
        int strip = target();
        if (strip >= 0) {
            int delta = (short)((unsigned)event[2] | ((unsigned)event[3] << 8));
            if (delta) mx1_route_adjust((unsigned)strip, delta > 0 ? 1 : -1);
            mx1_route_ui_display((void *)0x605141ccu);
            return; /* Do not enqueue the stock tempo adjustment. */
        }
    }
    ((void (*)(const ui_u8 *))0x60010b49u)(event);
    if (select_key && (before >= 0 || target() >= 0) &&
        *(const volatile ui_u32 *)0x600b4b94u == 0 &&
        *(const volatile ui_u16 *)0x600b4b5eu == 0)
        mx1_route_ui_display((void *)0x605141ccu);
}
