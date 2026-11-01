ENTRY(mx1_uac1_classify)
SECTIONS {
    . = 0x0100bee4;
    .text : {
        KEEP(*(.text.hook))
        KEEP(*(.text.policy))
        KEEP(*(.text.trampoline))
        *(.text*)
        *(.rodata*)
        . = ALIGN(4);
    }
    /DISCARD/ : { *(.comment*) *(.ARM.exidx*) *(.ARM.extab*) *(.eh_frame*) }
    ASSERT(. <= 0x0100d000, "USB private SRAM extension overlaps USB heap regions")
}
