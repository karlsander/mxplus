ENTRY(mx1_uac2_initialize)
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
    ASSERT(. <= 0x01010000, "Main private SRAM extension overlaps initialized data")
}
