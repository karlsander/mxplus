/* BD pad editor for the exact MX-1 1.05 image. Independently written 2026-11-02.
 * The original event decoder/queue owns the physical held-key bits. Only the
 * high-level step action is intercepted, so route-picker and modifier guards
 * see the same key state as the stock UI. See docs/INTERNAL_SOURCES.md.
 */
#include "internal_sources_ui.h"
#include "internal_sources.h"
#include "channel_routing.h"

extern void mx1_route_ui_event(const uint8_t *event);
extern void mx1_route_ui_display(void *context);
extern int mx1_sources_ui_press_original(uint32_t key);
extern int mx1_sources_ui_release_original(uint32_t key);
extern void mx1_sources_ui_steps_original(void *context);
extern void mx1_sources_ui_value_original(void *context);
extern void mx1_sources_ui_select_leds_original(void *context);

/* All capture bytes belong to the initialized extension copy. A captured release
 * stays ours even if the selected channel/page changes while a pad is held. */
static struct {
    uint16_t owned;
    uint16_t edited;
    uint8_t strip;
    uint8_t edit;
    uint8_t armed;
    uint8_t previous;
    uint16_t selected;
} capture __attribute__((section(".patch_data"))) = {0};

static uint32_t ui_parameter(uint32_t id)
{
    return ((uint32_t (*)(uint32_t, uint32_t, uint32_t))0x6001a1cfu)
        (0x60514504u, id, 0);
}

static uint32_t mixer_parameter(uint32_t id)
{
    return ((uint32_t (*)(uint32_t, uint32_t, uint32_t))0x6001e65fu)
        (0x600b53acu, id, 0);
}

static void dirty(void)
{
    *(volatile uint16_t *)0x605141ccu |= 0x612u;
}

/* Return the physical pad mask, or -1 when any other key is held. This leaves
 * BFX/MFX type holds, last-step editing, shortcuts and SELECT routing intact. */
static int pad_keys(void)
{
    const volatile uint8_t *keys = (const volatile uint8_t *)0x605129a4u;
    uint32_t pads = 0;
    for (uint32_t key = 0; key < 0x55; ++key) {
        if (!(keys[key >> 3] & (1u << (key & 7)))) continue;
        if (key < 1 || key > 16) return -1;
        pads |= 1u << (key - 1);
    }
    return (int)pads;
}

/* Edit state is deliberately transient; snapshots keep the source assignment,
 * not a physical button gesture. Stock no-selection remains valid at startup. */
static int ordinary_view(void)
{
    uint32_t page = *(const volatile uint16_t *)0x600b4b5eu;
    return !*(const volatile uint32_t *)0x600b4b94u &&
        (page == 5 || page == 15) && ui_parameter(0) <= 5 &&
        *(const volatile uint32_t *)0x6051deb8u <= 3 &&
        !((int (*)(const void *))0x60018259u)((const void *)0x605144ccu) &&
        ((uint32_t (*)(uint32_t, uint32_t, uint32_t))0x6001a897u)
            (0x600b5390u, 0x19, 0) != 2;
}

static int only_key(uint32_t wanted)
{
    const volatile uint8_t *keys = (const volatile uint8_t *)0x605129a4u;
    for (uint32_t key = 0; key < 0x55; ++key)
        if ((keys[key >> 3] & (1u << (key & 7))) && key != wanted) return 0;
    return 1;
}

int mx1_sources_ui_edit_target(void)
{
    if (!capture.edit || !ordinary_view()) return -1;
    uint32_t strip = mixer_parameter(0xfb);
    return strip == capture.previous && strip < MX1_STRIP_COUNT ? (int)strip : -1;
}

int mx1_sources_ui_route_target(void)
{
    return only_key(0xff) ? mx1_sources_ui_edit_target() : -1;
}

void mx1_sources_ui_select_leds(void *context)
{
    mx1_sources_ui_select_leds_original(context);
    int strip = mx1_sources_ui_edit_target();
    if (strip >= 0)
        ((void (*)(uint32_t, uint32_t, uint32_t))0x60014a79u)
            ((uint32_t)strip + 0x34u, 3, 9);
}

int mx1_sources_ui_target(void)
{
    if (*(const volatile uint32_t *)0x600b4b94u ||
        (*(const volatile uint16_t *)0x600b4b5eu != 5 &&
         *(const volatile uint16_t *)0x600b4b5eu != 15) ||
        *(const volatile uint32_t *)0x6051deb8u > 3 ||
        ((int (*)(const void *))0x60018259u)((const void *)0x605144ccu)) return -1;
    uint32_t mode = ui_parameter(0);
    /* CHANNEL SETTING BFX is mode 4. Its audio enable is deliberately NOT a
     * condition: a BD channel can retain its own BFX processing while editing
     * notes with GAIN/PAN/TONE/AUX/FADER focus (0,1,2,3,5). */
    if (mode > 5 || mode == 4 || pad_keys() < 0 ||
        mx1_sources_ui_edit_target() < 0) return -1;
    if (((uint32_t (*)(uint32_t, uint32_t, uint32_t))0x6001a897u)
            (0x600b5390u, 0x19, 0) == 2) return -1;
    uint32_t strip = mixer_parameter(0xfb);
    return strip < MX1_STRIP_COUNT && mx1_route_get(strip) == MX1_ROUTE_BD ? (int)strip : -1;
}

static int held_step(void)
{
    uint32_t mask = capture.owned;
    if (!mask || (mask & (mask - 1)) || pad_keys() != (int)mask ||
        mx1_sources_ui_target() != capture.strip) return -1;
    unsigned step = 0;
    while (!(mask & (1u << step))) ++step;
    return (int)step;
}

int mx1_sources_ui_press(uint32_t key)
{
    capture.armed = 0;
    if (key >= 0x29 && key <= 0x33) {
        uint32_t previous = ordinary_view() && only_key(key) ?
            mixer_parameter(0xfb) : 0xffffffffu;
        if (previous == key - 0x29) {
            capture.armed = 1;
            capture.previous = (uint8_t)previous;
            capture.selected = 0;
            for (uint32_t i = 0; i < MX1_STRIP_COUNT; ++i)
                if (mixer_parameter(i)) capture.selected |= (uint16_t)(1u << i);
        } else {
            capture.edit = 0;
        }
        dirty();
    }
    if (key >= 1 && key <= 16) {
        int strip = mx1_sources_ui_target();
        if (strip >= 0) {
            uint16_t bit = (uint16_t)(1u << (key - 1));
            if (!capture.owned) {
                capture.strip = (uint8_t)strip;
                capture.edited = 0;
            }
            /* A second pad or a channel change cancels tap toggles. It does
             * not edit or accidentally toggle the previously held note. */
            if (capture.owned && !(capture.owned & bit))
                capture.edited = capture.owned | bit;
            if (capture.strip != strip) capture.edited |= bit;
            capture.owned |= bit;
            dirty();
            return 1;
        }
    }
    if (capture.owned) capture.edited |= capture.owned;
    return mx1_sources_ui_press_original(key);
}

int mx1_sources_ui_release(uint32_t key)
{
    if (key >= 1 && key <= 16) {
        uint16_t bit = (uint16_t)(1u << (key - 1));
        if (capture.owned & bit) {
            if (capture.owned == bit && !(capture.edited & bit) &&
                mx1_sources_ui_target() == capture.strip && pad_keys() == 0)
                mx1_bd_step_toggle(capture.strip, key - 1);
            capture.owned &= (uint16_t)~bit;
            capture.edited &= (uint16_t)~bit;
            dirty();
            return 1;
        }
    }
    /* The stock callback owns link/multi-selection semantics. Only replace its
     * ordinary, same-channel deselection after it has completed synchronously.
     * A second key cancels arming; no programmatic SELECT action is changed. */
    int toggle = capture.armed && key == capture.previous + 0x29u &&
                 ordinary_view() && only_key(0xff);
    capture.armed = 0;
    int result = mx1_sources_ui_release_original(key);
    if (toggle && mixer_parameter(0xfb) == 0xffffffffu) {
        void (*set)(uint32_t, uint32_t, uint32_t) =
            (void (*)(uint32_t, uint32_t, uint32_t))0x6001e695u;
        for (uint32_t i = 0; i < MX1_STRIP_COUNT; ++i)
            set(0x600b53acu, i, (capture.selected >> i) & 1u);
        set(0x600b53acu, 0xfb, capture.previous);
        capture.edit ^= 1u;
        dirty();
    }
    return result;
}

void mx1_sources_ui_event(const uint8_t *event)
{
    if (event[0] == 4 && event[1] <= 1) {
        int step = held_step();
        if (step >= 0) {
            int32_t delta = (int16_t)((uint32_t)event[2] | ((uint32_t)event[3] << 8));
            if (delta) {
                capture.edited |= capture.owned;
                mx1_bd_step_adjust(capture.strip, (uint32_t)step, event[1],
                                   delta > 0 ? 1 : -1);
            }
            dirty();
            return;
        }
        if (capture.owned && pad_keys() >= 0 &&
            mx1_sources_ui_target() == capture.strip) {
            /* An ambiguous multi-pad hold must not leak into PAN or TEMPO. */
            capture.edited |= capture.owned;
            dirty();
            return;
        }
    }
    if (event[0] == 2 && capture.owned && (event[1] < 1 || event[1] > 16))
        capture.edited |= capture.owned;
    mx1_route_ui_event(event);
    /* A source/view change can expose or remove the pad editor. Reusing the
     * existing deferred dirty bits avoids synchronous font/LED I/O in input. */
    if (event[0] == 1 || event[0] == 2 || event[0] == 4) dirty();
}

void mx1_sources_ui_steps(void *context)
{
    int strip = mx1_sources_ui_target();
    if (strip < 0) {
        mx1_sources_ui_steps_original(context);
        return;
    }
    int playhead = mx1_bd_current_step();
    for (uint32_t step = 0; step < 16; ++step) {
        uint32_t on = mx1_bd_step_get((uint32_t)strip, step) & 1u;
        uint32_t color = 18; /* Valid stock RGB table entry (1,0,3), violet. */
        if (capture.strip == strip && (capture.owned & (1u << step))) {
            on = 1;
            color = 7; /* White held-note marker. */
        } else if (playhead == (int)step) {
            on = 1;
            color = 22; /* (1,0,2), distinct playhead violet. */
        }
        ((void (*)(uint32_t, uint32_t, uint32_t, uint32_t))0x60014a8fu)
            (step + 0x19, on, on ? 9 : 0, color);
    }
}

static void text(uint32_t display, const char *value)
{
    ((void (*)(uint32_t, uint32_t, const char *, uint32_t))0x60054f85u)
        (0x60512984u, display, value, 0);
}

void mx1_sources_ui_value(void *context)
{
    int step = held_step();
    if (step < 0) {
        mx1_sources_ui_value_original(context);
        return;
    }
    int pitch = (int8_t)(mx1_bd_step_get(capture.strip, (uint32_t)step) >> 8);
    /* The stock seven-segment font maps '+' to the same glyph as '-'. A blank
     * positive sign is unambiguous on the real display; negative uses '-'. */
    char value[3] = {pitch < 0 ? '-' : ' ', '0', '0'};
    if (pitch < 0) pitch = -pitch;
    value[1] += (char)(pitch / 10);
    value[2] += (char)(pitch % 10);
    text(0, value);
}

void mx1_sources_ui_tempo(void *context)
{
    int step = held_step();
    if (step < 0) {
        mx1_route_ui_display(context);
        return;
    }
    uint32_t decay = (mx1_bd_step_get(capture.strip, (uint32_t)step) >> 16) & 255u;
    char value[4] = {'d', (char)('0' + decay / 100),
                    (char)('0' + (decay / 10) % 10), (char)('0' + decay % 10)};
    text(1, value);
}
