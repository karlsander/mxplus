/* MX-1 frozen 1.05-generation input-operand experiment; no hardware validation.
 *
 * Source reads are changed in DSP0's original input gain block, before the
 * per-strip effects/faders. No samples are copied by the ARM processor.
 * The UI only stores a byte and posts the existing DSP parameter event. All
 * programming-command writes occur after that task has drained its queue.
 * See research/channel-routing-audio.md for binary evidence and limits.
 */
#include "channel_routing.h"

struct source { uint16_t left, right; char label[4]; };
#define MONO(op, label) {op, op, label}
#define PAIR(op, label) {op, (op) + 1, label}
#define USB(n, op) PAIR(op, "US" #n " "), MONO(op, "U" #n " L"), MONO((op)+1, "U" #n " R")
#define PC(n, op) PAIR(op, "PC" #n " "), MONO(op, "P" #n " L"), MONO((op)+1, "P" #n " R")
static const struct source sources[MX1_ROUTE_SOURCE_COUNT] = {
    MONO(0, "Auto"),
    MONO(0x6000, "An1 "), MONO(0x6001, "An2 "),
    MONO(0x6002, "An3 "), MONO(0x6003, "An4 "),
    PAIR(0x6004, "A56 "), MONO(0x6004, "An5 "), MONO(0x6005, "An6 "),
    PAIR(0x6008, "dIG "), MONO(0x6008, "dI L"), MONO(0x6009, "dI R"),
    USB(1, 0x600a), USB(2, 0x600c), USB(3, 0x600e), USB(4, 0x6010),
    PAIR(0x6006, "rtn "), MONO(0x6006, "rt L"), MONO(0x6007, "rt R"),
    PC(1, 0xa000), PC(2, 0xa002), PC(3, 0xa004), PC(4, 0xa006),
    PC(5, 0xa008), PC(6, 0xa00a), PC(7, 0xa00c), PC(8, 0xa00e), PC(9, 0xa010)
};

/* DSP logical byte offsets, NOT CPU-addressed little-endian halfwords. */
static const uint16_t input_sites[18] = {
    0x0328, 0x033a, 0x034c, 0x0360, 0x0376, 0x038a,
    0x03ac, 0x03c2, 0x03e2, 0x03f8, 0x0418, 0x042e,
    0x044e, 0x0464, 0x0484, 0x049a, 0x04ac, 0x04bc
};
static const uint16_t stock_operands[18] = {
    0x6000, 0x6001, 0x6002, 0x6003, 0x6004, 0x6005,
    0x6008, 0x6009, 0x600a, 0x600b, 0x600c, 0x600d,
    0x600e, 0x600f, 0x6010, 0x6011, 0x2010, 0x2011
};

/* Writable state follows original SRAM BSS; the builder extends its startup
 * clear. The code SRAM at 0x0100f6a4 is read-only after MPU setup. */
volatile uint8_t mx1_route_state[MX1_STRIP_COUNT] __attribute__((section(".route_state"))) = {0};
static uint8_t applied[MX1_STRIP_COUNT] __attribute__((section(".route_state"))) = {0};

static uint32_t parameter(uint32_t id)
{
    return ((uint32_t (*)(uint32_t, uint32_t, uint32_t))0x6001a897)(0x600b5390, id, 0);
}

static int blocked(void)
{
    /* Diagnostic programs have a different DSP layout. External Mixer uses
     * a separate, downstream computer/native switch and stays stock. */
    return *(volatile uint32_t *)0x6051deb8 > 3 || parameter(0x19) == 2;
}

uint32_t mx1_route_get(uint32_t strip)
{
    return strip < MX1_STRIP_COUNT ? mx1_route_state[strip] : 0;
}

const char *mx1_route_label(uint32_t strip)
{
    if (strip >= MX1_STRIP_COUNT) return "----";
    if (blocked()) return "modE";
    return sources[mx1_route_state[strip]].label;
}

void mx1_route_adjust(uint32_t strip, int32_t delta)
{
    if (strip >= MX1_STRIP_COUNT || !delta || blocked()) return;
    uint32_t value = mx1_route_state[strip];
    do {
        if (delta > 0) value = value + 1 == MX1_ROUTE_SOURCE_COUNT ? 0 : value + 1;
        else value = value ? value - 1 : MX1_ROUTE_SOURCE_COUNT - 1;
    } while (strip < 4 && sources[value].left != sources[value].right);
    /* A byte store is atomic. The higher-priority DSP task may process it
     * before or after this post; either order leaves the newest route queued. */
    mx1_route_state[strip] = (uint8_t)value;
    ((void (*)(uint32_t, uint32_t))0x0100e267)(0x6051dea8, 8);
}

static void operand(uint32_t offset, uint32_t value)
{
    ((void (*)(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t))0x0100ab05)
        (0x20000b24, 0, offset, 0, value);
}

static void selector(uint32_t offset, uint32_t enabled)
{
    ((void (*)(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t))0x0100baef)
        (0x20000b24, 0, offset, 0, enabled ? 0x3f800000 : 0);
}

void mx1_route_flush(void)
{
    /* Never write normal-program operands into a diagnostic DSP program. */
    if (*(volatile uint32_t *)0x6051deb8 > 3) return;
    uint32_t external = parameter(0x19) == 2;
    for (uint32_t strip = 0; strip < MX1_STRIP_COUNT; ++strip) {
        uint32_t value = external ? 0 : mx1_route_state[strip];
        uint32_t previous = applied[strip];
        /* Rate changes reload the complete program, then enqueue the stock
         * parameter groups through this same event. Reassert active operands
         * on each drain rather than trusting a stale applied-program cache. */
        if (value || previous) {
            uint32_t lane = strip < 4 ? strip : 2 * strip - 4;
            uint32_t count = strip < 4 ? 1 : 2;
            for (uint32_t side = 0; side < count; ++side) {
                uint32_t read = value ? (side ? sources[value].right : sources[value].left)
                                      : stock_operands[lane + side];
                operand(input_sites[lane + side], read);
            }
            applied[strip] = (uint8_t)value;
        }
        if (strip >= MX1_STRIP_DIGITAL && strip <= MX1_STRIP_USB4 && (value || previous)) {
            uint32_t enable = 0;
            if (!value) {
                enable = external || (strip == MX1_STRIP_DIGITAL && parameter(0x0c) == 1)
                         || !parameter(0x92 + strip - MX1_STRIP_DIGITAL);
            }
            /* Stock digital/AIRA paths can ADD their own computer return.
             * Explicit assignment suppresses that destination's summand.
             * PC sources above read the raw a000..a011 exchange ports, so
             * suppressing a destination never changes another source. */
            uint32_t offset = 0x1de + (strip - MX1_STRIP_DIGITAL) * 0x34;
            selector(offset, enable);
            selector(offset + 0x1a, enable);
        }
    }
}

/* Recreates exactly the original 10-byte entry displaced by the far hook.
 * The original handler still drains all queued parameter changes and restores
 * its own frame. The wrapper then applies policy in that same DSP task. */
__attribute__((naked)) static void original_dispatch(void)
{
    __asm__ volatile(
        "push.w {r4-r9, lr}\n"
        "sub sp, #28\n"
        "ldr r3, =0x6000f1bd\n"
        "blx r3\n"
        "ldr pc, =0x60024bb9\n"
    );
}

void mx1_route_dispatch(void)
{
    original_dispatch();
    mx1_route_flush();
}
