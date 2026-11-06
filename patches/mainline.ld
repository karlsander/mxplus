ENTRY(mx1_route_ui_event)
mx1_original_mix_invalid = 0x6001e650;
SECTIONS {
    /* Separate USB-processor ELF, built only by the same mainline builder.
       Numeric addresses overlap the main processor's independent SRAM. */
    .host_text 0x0100bee4 : { *(.host_text) *(.host_rodata) . = ALIGN(4); }
    .host_state 0x01017868 (NOLOAD) : { *(.host_state) . = ALIGN(4); }
    ASSERT(ADDR(.host_text) + SIZEOF(.host_text) <= 0x0100d000, "Host code overlaps stock USB allocators")
    ASSERT(ADDR(.host_state) + SIZEOF(.host_state) <= 0x01018000, "Host writable SRAM overflow")
    ASSERT(DEFINED(mx1_host_image) || (SIZEOF(.host_text) + SIZEOF(.host_state) == 0), "Host sections in main ELF")
    ASSERT(!DEFINED(mx1_host_image) || SIZEOF(.text) == 0, "Unexpected host code section")

    .usb_playback_patch 0x01009860 : { KEEP(*(.usb_playback_patch)) }
    ASSERT(SIZEOF(.usb_playback_patch) == (DEFINED(mx1_host_image) ? 0 : 438), "USB playback patch overflow")
    . = 0x0100f6a4;
    .text : {
        KEEP(*(.text.hook))
        *(.text*)
        *(.rodata*)
        . = ALIGN(4);
    }
    .route_state 0x01017264 (NOLOAD) : {
        KEEP(*(.route_state))
        KEEP(*(.route_ready))
        . = ALIGN(4);
    }
    ASSERT(SIZEOF(.route_state) == (DEFINED(mx1_host_image) ? 0 : 24), "Unexpected routing state size")
    ASSERT(ADDR(.text) + SIZEOF(.text) <= 0x01010000, "Routing code overflow")
    ASSERT(ADDR(.route_state) + SIZEOF(.route_state) <= 0x01018000, "Routing state overflow")
    .usb_data 0x0101727c : { KEEP(*(.usb_data)) . = ALIGN(4); }
    .usb_state 0x01017430 (NOLOAD) : { KEEP(*(.usb_state)) KEEP(*(.usb_stream_state)) . = ALIGN(4); }
    ASSERT(SIZEOF(.usb_data) == (DEFINED(mx1_host_image) ? 0 : 436), "Unexpected USB descriptor storage")
    ASSERT(SIZEOF(.usb_state) == (DEFINED(mx1_host_image) ? 0 : 20), "Unexpected USB control state")
    ASSERT(ADDR(.usb_state) + SIZEOF(.usb_state) <= 0x01018000, "Writable state overflow")
    .master_lookup 0x6001dbd6 : { KEEP(*(.master_lookup)) }
    /* Keep empty main-only sections beside host BSS in the USB ELF, so lld
       does not emit a sparse multi-gigabyte segment spanning both address spaces. */
    .master_head (DEFINED(mx1_host_image) ? ADDR(.host_state) + SIZEOF(.host_state) : 0x6001dbf4) : { *(.master_head) *(.master_rodata) . = ALIGN(4); }
    .master_text (DEFINED(mx1_host_image) ? ADDR(.host_state) + SIZEOF(.host_state) : 0x6001de0c) : { *(.master_text) *(.master_labels) . = ALIGN(4); }
    ASSERT(SIZEOF(.master_lookup) <= 30, "Mixer lookup replacement overflow")
    ASSERT(SIZEOF(.master_head) <= 532, "Mastering head overlaps shared literal")
    ASSERT(SIZEOF(.master_text) <= 2016, "Mastering code overlaps shared return")
    .master_state (DEFINED(mx1_host_image) ? ADDR(.host_state) + SIZEOF(.host_state) : 0x01017444) (NOLOAD) : {
        *(.master_state) . = ALIGN(4);
    }
    ASSERT(ADDR(.master_state) + SIZEOF(.master_state) <= 0x01018000, "Mastering state overflow")
    /* app_usb: reserve the last 64 KiB of its ORIGINAL SDRAM heap. Its heap
       end and unused startup copy/zero operations are guarded by the builder. */
    .host_audio (DEFINED(mx1_host_image) ? 0x607f0000 : ADDR(.master_state) + SIZEOF(.master_state)) : { *(.host_audio) *(.host_audio_rodata) . = ALIGN(4); }
    .host_audio_state (DEFINED(mx1_host_image) ? 0x607f4000 : ADDR(.host_audio) + SIZEOF(.host_audio)) (NOLOAD) : { *(.host_audio_state) *(.host_audio_diagnostics) *(.host_debug_state) }
    ASSERT(ADDR(.host_audio) + SIZEOF(.host_audio) <= 0x607f4000, "Host audio code reservation overflow")
    ASSERT(ADDR(.host_audio_state) + SIZEOF(.host_audio_state) <= 0x60800000, "Host audio state reservation overflow")
    ASSERT(DEFINED(mx1_host_image) || (SIZEOF(.host_audio) + SIZEOF(.host_audio_state) == 0), "Host audio in main ELF")
    /DISCARD/ : { *(.comment*) *(.ARM.exidx*) *(.ARM.extab*) *(.eh_frame*) }
}
