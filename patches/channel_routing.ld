ENTRY(mx1_route_ui_event)
SECTIONS {
    . = 0x0100f6a4;
    .text : {
        KEEP(*(.text.hook))
        *(.text*)
        *(.rodata*)
        . = ALIGN(4);
        KEEP(*(.patch_data))
        *(.data*)
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
    }
    /DISCARD/ : { *(.comment*) *(.ARM.exidx*) *(.ARM.extab*) *(.eh_frame*) }
    ASSERT(. <= 0x01010000, "Routing extension overlaps original initialized SRAM")
}
