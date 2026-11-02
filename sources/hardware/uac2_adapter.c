/*
 * MX-1 UAC2 fixed-clock control adapter prototype.
 *
 * This is newly written experimental code, not recovered Roland source.
 * Bindings apply only to main app SHA256
 * 256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b.
 * No hardware validation. The caller must supply truthful UAC2 descriptors,
 * preserve the live sample rate, and arrange input-first streaming separately.
 */
#include <stdint.h>
#include <stddef.h>

/* Shared writable mainline reservation. Native tests use ordinary host BSS. */
#ifdef MX1_UAC2_NATIVE_TEST
#define USB_STATE
#else
#define USB_STATE __attribute__((section(".usb_state")))
#endif
static uint32_t mx1_uac2_rate USB_STATE;
static uint8_t mx1_uac2_reply[14] USB_STATE;

#ifdef MX1_UAC2_NATIVE_TEST
extern void mx1_uac2_transport_reply(const void *, uint32_t, uint32_t);
extern void mx1_uac2_transport_stall(void);
extern int mx1_uac2_transport_register(int, uint32_t, uintptr_t);
extern int mx1_uac2_transport_start(void);
#else
static void mx1_uac2_transport_reply(const void *data, uint32_t length,
                                     uint32_t flags)
{
    ((void (*)(const void *, uint32_t, uint32_t))(uintptr_t)0x010046bbu)
        (data, length, flags);
}

static void mx1_uac2_transport_stall(void)
{
    volatile uint8_t *state = (volatile uint8_t *)(uintptr_t)0x600d09c0u;
    volatile uint8_t *setup = (volatile uint8_t *)(uintptr_t)0x606293fcu;
    *state = 1;
    for (uint32_t i = 0; i != 8; ++i)
        setup[i] = 0;
    ((void (*)(uint32_t))(uintptr_t)0x01003e1bu)(0);
}

static int mx1_uac2_transport_register(int instance, uint32_t event,
                                      uintptr_t callback)
{
    return ((int (*)(int, uint32_t, uintptr_t))(uintptr_t)0x6003b7f5u)
        (instance, event, callback);
}

static int mx1_uac2_transport_start(void)
{
    return ((int (*)(void))(uintptr_t)0x6003b787u)();
}
#endif

static uint16_t get16(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static void put32(uint8_t *p, uint32_t value)
{
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8);
    p[2] = (uint8_t)(value >> 16);
    p[3] = (uint8_t)(value >> 24);
}

/* Call with r0 preserved from stock FUN_6000d9c4(rate). */
void mx1_uac2_set_rate(uint32_t rate)
{
    mx1_uac2_rate = rate;
}

/* Hardware clock lock has not been reverse engineered. This validity test
 * reflects the accepted configured rate; it does not prove PLL lock. */
static int rate_configured(void)
{
    return mx1_uac2_rate == 44100u || mx1_uac2_rate == 48000u ||
           mx1_uac2_rate == 96000u;
}

/* r0 points to the eight setup bytes; callback return value is ignored. */
void mx1_uac2_class_request(const uint8_t *setup)
{
    uint16_t value = get16(setup + 2);
    uint16_t length = get16(setup + 6);
    uint32_t response_length;

    /* AudioControl interface 0, clock source entity 0x10, channel zero.
     * bmRequestType 0xa1 = device-to-host, class, interface recipient. */
    if (setup[0] != 0xa1u || get16(setup + 4) != 0x1000u || !length)
        goto stall;

    if (setup[1] == 1u && value == 0x0200u) {
        mx1_uac2_reply[0] = (uint8_t)rate_configured();
        response_length = 1;
    } else if (!rate_configured()) {
        goto stall;
    } else if (setup[1] == 1u && value == 0x0100u) {
        put32(mx1_uac2_reply, mx1_uac2_rate);
        response_length = 4;
    } else if (setup[1] == 2u && value == 0x0100u) {
        mx1_uac2_reply[0] = 1; /* wNumSubRanges, little endian. */
        mx1_uac2_reply[1] = 0;
        put32(mx1_uac2_reply + 2, mx1_uac2_rate); /* MIN */
        put32(mx1_uac2_reply + 6, mx1_uac2_rate); /* MAX */
        put32(mx1_uac2_reply + 10, 0);           /* RES */
        response_length = 14;
    } else {
        goto stall;
    }

    if (response_length > length)
        response_length = length;
    /* These replies are shorter than EP0's 64-byte max packet. No ZLP flag. */
    mx1_uac2_transport_reply(mx1_uac2_reply, response_length, 0);
    return;

stall:
    mx1_uac2_transport_stall();
}

/* Redirect the normal-mode BL at 0x6000d99a here. Do not call this from the
 * earlier descriptor-rate hook: stock 0x6003b764 would erase the callback.
 * The original backup/mass-storage initializer does not use this callsite. */
int mx1_uac2_start(void)
{
    int result = mx1_uac2_transport_register(0, 1,
                    (uintptr_t)&mx1_uac2_class_request);
    if (result)
        return result;
    return mx1_uac2_transport_start();
}
