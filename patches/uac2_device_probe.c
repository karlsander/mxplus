/* MX-1 normal USB-B UAC2 enumeration/control/stream-start experiment.
 * Newly written source. Not hardware validated; see docs/DEVICE_PROBE.md.
 */
#include <stdint.h>
#include "uac2_configuration.h"

extern void mx1_uac2_set_rate(uint32_t rate);
extern int mx1_uac2_start(void);

/* Generated from a checked UAC2 descriptor graph. Stored in the SRAM extension
 * and writable so endpoint packet sizes can follow the existing boot setting. */
__attribute__((section(".patch_data")))
uint8_t mx1_uac2_configuration[] = MX1_UAC2_CONFIGURATION_BYTES;

__attribute__((section(".text.hook")))
int mx1_uac2_initialize(uint32_t rate)
{
    if (rate!=44100 && rate!=48000 && rate!=96000) return -1;
    mx1_uac2_set_rate(rate);
    uint32_t channels=18;
    for (uint32_t p=0;p<sizeof(mx1_uac2_configuration);p+=mx1_uac2_configuration[p]) {
        uint8_t *d=mx1_uac2_configuration+p;
        if (d[1]==4 && (d[2]==1 || d[2]==2)) channels=d[3]==2?2:18;
        if (d[1]==5 && (d[2]==0x0d || d[2]==0x8e)) {
            /* Exact positive-rate formula used by stock FUN_6000d9c4. */
            uint32_t maximum=(rate/8000+2)*channels*4;
            d[4]=(uint8_t)maximum;d[5]=(uint8_t)(maximum>>8);
        }
    }
    if (((int (*)(const void *))(uintptr_t)0x6003b765u)((const void *)0x600b4af8u)) return -1;
    if (((int (*)(const void *))(uintptr_t)0x6003b7cdu)((const void *)0x600b4960u)) return -1;
    if (mx1_uac2_start()) return -1;
    return 0;
}
