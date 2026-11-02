.syntax unified
.thumb
.cpu cortex-m3

/* Each trampoline replaces only the exact displaced original instructions.
 * Original stack frames/epilogues remain paired, including 8-byte alignment. */
.section .text.mx1_internal_start_original,"ax",%progbits
.global mx1_internal_start_original
.type mx1_internal_start_original,%function
.thumb_func
mx1_internal_start_original:
    push {lr}
    ldr r0,=0x600b4834
    sub sp,#0x134
    ldrb r1,[r0]
    ldr pc,=0x6000a7e5
.size mx1_internal_start_original, .-mx1_internal_start_original
.ltorg

.section .text.mx1_internal_stop_original,"ax",%progbits
.global mx1_internal_stop_original
.type mx1_internal_stop_original,%function
.thumb_func
mx1_internal_stop_original:
    push {r4,lr}
    ldr r4,=0x600b4834
    sub sp,#0x130
    ldrb r1,[r4]
    ldr pc,=0x6000a819
.size mx1_internal_stop_original, .-mx1_internal_stop_original
.ltorg

.section .text.mx1_internal_step_original,"ax",%progbits
.global mx1_internal_step_original
.type mx1_internal_step_original,%function
.thumb_func
mx1_internal_step_original:
    push {r4,r5,r6,r7,lr}
    ldr r4,=0x604df820
    sub sp,#0x264
    ldr pc,=0x6000a89d
.size mx1_internal_step_original, .-mx1_internal_step_original
.ltorg
