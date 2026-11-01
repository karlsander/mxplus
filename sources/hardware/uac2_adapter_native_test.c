/* Native unit harness for the newly written control-request adapter. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

void mx1_uac2_set_rate(uint32_t);
void mx1_uac2_class_request(const uint8_t *);
int mx1_uac2_start(void);

static uint8_t actual[32];
static uint32_t actual_length, replies, stalls, registrations, starts;
static int registration_result, start_result;
static uintptr_t registered_callback;
static unsigned checks;

void mx1_uac2_transport_reply(const void *data, uint32_t n, uint32_t flags)
{
    assert(n <= sizeof(actual));
    assert(flags == 0);
    memcpy(actual, data, n);
    actual_length = n;
    ++replies;
}

void mx1_uac2_transport_stall(void) { ++stalls; }

int mx1_uac2_transport_register(int instance, uint32_t event, uintptr_t fn)
{
    assert(instance == 0 && event == 1);
    assert(starts == 0);
    registered_callback = fn;
    ++registrations;
    return registration_result;
}

int mx1_uac2_transport_start(void)
{
    assert(registrations == 1);
    ++starts;
    return start_result;
}

static void request(uint8_t type, uint8_t code, uint16_t value,
                    uint16_t index, uint16_t length)
{
    const uint8_t setup[8] = {type, code, (uint8_t)value, (uint8_t)(value >> 8),
                             (uint8_t)index, (uint8_t)(index >> 8),
                             (uint8_t)length, (uint8_t)(length >> 8)};
    actual_length = replies = stalls = 0;
    memset(actual, 0xa5, sizeof(actual));
    mx1_uac2_class_request(setup);
    ++checks;
}

static void expect_reply(const uint8_t *expected, uint32_t n)
{
    assert(replies == 1 && stalls == 0);
    assert(actual_length == n);
    assert(memcmp(actual, expected, n) == 0);
    for (uint32_t i = n; i < sizeof(actual); ++i)
        assert(actual[i] == 0xa5);
}

static void expect_stall(void) { assert(stalls == 1 && replies == 0); }

int main(void)
{
    const uint32_t rates[] = {44100, 48000, 96000};
    for (unsigned r = 0; r < sizeof(rates) / sizeof(rates[0]); ++r) {
        uint32_t rate = rates[r];
        uint8_t frequency[4] = {(uint8_t)rate, (uint8_t)(rate >> 8),
                                (uint8_t)(rate >> 16), 0};
        uint8_t range[14] = {1, 0};
        const uint8_t validity[1] = {1};
        memcpy(range + 2, frequency, 4);
        memcpy(range + 6, frequency, 4);
        mx1_uac2_set_rate(rate);
        /* Includes the two-byte range-header probe, short reads, and long
         * requested lengths. The adapter must never copy beyond its reply. */
        for (unsigned length = 0; length <= 512; ++length) {
            request(0xa1, 1, 0x0100, 0x1000, (uint16_t)length);
            if (length) expect_reply(frequency, length < 4 ? length : 4);
            else expect_stall();
            request(0xa1, 2, 0x0100, 0x1000, (uint16_t)length);
            if (length) expect_reply(range, length < 14 ? length : 14);
            else expect_stall();
            request(0xa1, 1, 0x0200, 0x1000, (uint16_t)length);
            if (length) expect_reply(validity, 1);
            else expect_stall();
        }
    }
    /* Every request type other than the exact read/class/interface type. */
    for (unsigned type = 0; type < 256; ++type) {
        if (type == 0xa1) continue;
        request((uint8_t)type, 1, 0x0100, 0x1000, 4);
        expect_stall();
    }
    request(0xa1, 1, 0x0101, 0x1000, 4); expect_stall();
    request(0xa1, 1, 0x0100, 0x1001, 4); expect_stall();
    request(0xa1, 1, 0x0100, 0x1100, 4); expect_stall();
    request(0xa1, 2, 0x0200, 0x1000, 1); expect_stall();
    request(0xa1, 3, 0x0100, 0x1000, 4); expect_stall();
    request(0x21, 1, 0x0100, 0x1000, 4); expect_stall();
    mx1_uac2_set_rate(12345);
    request(0xa1, 1, 0x0100, 0x1000, 4); expect_stall();
    request(0xa1, 2, 0x0100, 0x1000, 14); expect_stall();
    request(0xa1, 1, 0x0200, 0x1000, 1);
    { const uint8_t invalid = 0; expect_reply(&invalid, 1); }

    registrations = starts = 0; registration_result = 0; start_result = -23;
    assert(mx1_uac2_start() == -23);
    assert(registrations == 1 && starts == 1);
    assert(registered_callback == (uintptr_t)&mx1_uac2_class_request);
    registrations = starts = 0; registration_result = -17;
    assert(mx1_uac2_start() == -17);
    assert(registrations == 1 && starts == 0);
    printf("PASS: %u EP0 request cases; start ordering and error propagation\n", checks);
    return 0;
}
