.syntax unified
.thumb
.cpu cortex-m3

/* main 0x60013356..0x6001335f is overwritten by the aligned absolute veneer.
 * Reproduce its prologue and the displaced PC-relative load/call explicitly.
 * The old literal at 0x60013670 contains 0x605144cc. */
.section .text.mx1_route_ui_display_original,"ax",%progbits
.global mx1_route_ui_display_original
.type mx1_route_ui_display_original,%function
.thumb_func
mx1_route_ui_display_original:
    push {r1,r2,r3,r4,r5,r6,r7,lr}
    mov r4,r0
    ldr r0,=0x605144cc
    ldr r12,=0x60018259
    blx r12
    ldr r12,=0x60013361
    bx r12
.size mx1_route_ui_display_original, .-mx1_route_ui_display_original
.ltorg
