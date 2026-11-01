.syntax unified
.thumb
.cpu cortex-m3
.section .text.trampoline,"ax",%progbits
.global mx1_original_classify
.type mx1_original_classify,%function
.thumb_func
mx1_original_classify:
    /* These are the exact three instructions overwritten at 0x6000a11e. */
    push.w {r4,r5,r6,r7,r8,lr}
    ldrb.w r12,[r1,#5]
    movs r6,#0
    ldr.w pc,.Lresume
    .balign 4
.Lresume:
    .word 0x6000a129
.size mx1_original_classify,.-mx1_original_classify

.global mx1_original_configuration
.type mx1_original_configuration,%function
.thumb_func
mx1_original_configuration:
    /* Exact first ten bytes replaced at stock configuration parser 6000a1e2. */
    push.w {r4,r5,r6,r7,r8,r9,r10,r11,lr}
    sub sp,#0x1c
    mov r4,r0
    mov r5,r1
    ldr.w pc,.Lconfig_resume
    .balign 4
.Lconfig_resume:
    .word 0x6000a1ed
.size mx1_original_configuration,.-mx1_original_configuration
