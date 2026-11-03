ENTRY(mx1_route_ui_event)
mx1_original_mix_invalid = 0x6001e650;
SECTIONS {
    .usb_playback_patch 0x01009860 : { KEEP(*(.usb_playback_patch)) }
    ASSERT(SIZEOF(.usb_playback_patch) == 438, "USB playback patch overflow")
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
    ASSERT(SIZEOF(.route_state) == 24, "Unexpected routing state size")
    ASSERT(ADDR(.text) + SIZEOF(.text) <= 0x01010000, "Routing code overflow")
    ASSERT(ADDR(.route_state) + SIZEOF(.route_state) <= 0x01018000, "Routing state overflow")
    .usb_data 0x0101727c : { KEEP(*(.usb_data)) . = ALIGN(4); }
    .usb_state 0x01017430 (NOLOAD) : { KEEP(*(.usb_state)) KEEP(*(.usb_stream_state)) . = ALIGN(4); }
    ASSERT(SIZEOF(.usb_data) == 436, "Unexpected USB descriptor storage")
    ASSERT(SIZEOF(.usb_state) == 20, "Unexpected USB control state")
    ASSERT(ADDR(.usb_state) + SIZEOF(.usb_state) <= 0x01018000, "Writable state overflow")
    .master_lookup 0x6001dbd6 : { KEEP(*(.master_lookup)) }
    .master_head 0x6001dbf4 : { *(.master_head) *(.master_rodata) . = ALIGN(4); }
    .master_text 0x6001de0c : { *(.master_text) *(.master_labels) . = ALIGN(4); }
    ASSERT(SIZEOF(.master_lookup) <= 30, "Mixer lookup replacement overflow")
    ASSERT(SIZEOF(.master_head) <= 532, "Mastering head overlaps shared literal")
    ASSERT(SIZEOF(.master_text) <= 2016, "Mastering code overlaps shared return")
    .master_state 0x01017444 (NOLOAD) : {
        *(.master_state) . = ALIGN(4);
    }
    ASSERT(ADDR(.master_state) + SIZEOF(.master_state) <= 0x01018000, "Mastering state overflow")
    /DISCARD/ : { *(.comment*) *(.ARM.exidx*) *(.ARM.extab*) *(.eh_frame*) }
}
