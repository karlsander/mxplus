ENTRY(mx1_route_ui_event)
SECTIONS {
    . = 0x0100f6a4;
    .text : {
        KEEP(*(.text.hook))
        *(.text*)
        *(.rodata*)
        . = ALIGN(4);
    }
    .route_state 0x01017264 (NOLOAD) : {
        KEEP(*(.route_state))
        . = ALIGN(4);
    }
    ASSERT(SIZEOF(.route_state) == 24, "Unexpected routing state size")
    ASSERT(ADDR(.text) + SIZEOF(.text) <= 0x01010000, "Routing code overflow")
    ASSERT(ADDR(.route_state) + SIZEOF(.route_state) <= 0x01018000, "Routing state overflow")
    .usb_data 0x0101727c : { KEEP(*(.usb_data)) . = ALIGN(4); }
    .usb_state 0x010173e0 (NOLOAD) : { KEEP(*(.usb_state)) . = ALIGN(4); }
    ASSERT(SIZEOF(.usb_data) == 356, "Unexpected USB descriptor storage")
    ASSERT(SIZEOF(.usb_state) == 20, "Unexpected USB control state")
    ASSERT(ADDR(.usb_state) + SIZEOF(.usb_state) <= 0x01018000, "Writable state overflow")
    /DISCARD/ : { *(.comment*) *(.ARM.exidx*) *(.ARM.extab*) *(.eh_frame*) }
}
