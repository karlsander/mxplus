ENTRY(mx1_sources_ui_event)
SECTIONS {
    .route_state 0x01017264 (NOLOAD) : {
        KEEP(*(.route_state)) KEEP(*(.route_ready)) . = ALIGN(4);
    }
    .usb_data 0x0101727c : { KEEP(*(.usb_data)) . = ALIGN(4); }
    .usb_state 0x010173e0 (NOLOAD) : { KEEP(*(.usb_state)) . = ALIGN(4); }
    .generator_data 0x010173f4 : {
        KEEP(*(.patch_data)) *(.data*) *(.bss*) *(COMMON) . = ALIGN(4);
    }
    .text 0x01018000 : {
        KEEP(*(.text.hook)) *(.text*) *(.rodata*) . = ALIGN(4);
    }
    ASSERT(SIZEOF(.route_state) == 24, "Unexpected routing state size")
    ASSERT(SIZEOF(.usb_data) == 356, "Unexpected USB descriptor storage")
    ASSERT(SIZEOF(.usb_state) == 20, "Unexpected USB control state")
    ASSERT(ADDR(.generator_data) + SIZEOF(.generator_data) <= 0x01018000, "Writable state overflow")
    ASSERT(ADDR(.text) + SIZEOF(.text) <= 0x0101c000, "Mainline code overflow")
    /DISCARD/ : { *(.comment*) *(.ARM.exidx*) *(.ARM.extab*) *(.eh_frame*) }
}
