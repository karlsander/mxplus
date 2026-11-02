.syntax unified
.thumb
.cpu cortex-m3

/* Main application offsets equal runtime minus 0x60000000. Each trampoline
 * recreates complete displaced instructions, resolving PC-relative literals. */
.section .text.mx1_sources_ui_press_original,"ax",%progbits
.global mx1_sources_ui_press_original
.type mx1_sources_ui_press_original,%function
.thumb_func
mx1_sources_ui_press_original:
    ldr r1, =0x600b4b5c
    push {r4,lr}
    adds r1, #8
    strh r0, [r1,#2]
    mvn r0, #0x63
    ldr pc, =0x60010523
.size mx1_sources_ui_press_original, .-mx1_sources_ui_press_original
.ltorg

.section .text.mx1_sources_ui_release_original,"ax",%progbits
.global mx1_sources_ui_release_original
.type mx1_sources_ui_release_original,%function
.thumb_func
mx1_sources_ui_release_original:
    ldr r1, =0x600b4b5c
    push {r4,lr}
    adds r1, #0x14
    strh r0, [r1,#2]
    ldr pc, =0x60010541
.size mx1_sources_ui_release_original, .-mx1_sources_ui_release_original
.ltorg

.section .text.mx1_sources_ui_steps_original,"ax",%progbits
.global mx1_sources_ui_steps_original
.type mx1_sources_ui_steps_original,%function
.thumb_func
mx1_sources_ui_steps_original:
    push {r4-r8,lr}
    movs r2, #0
    mov r1, r2
    ldr r0, =0x60514504
    ldr pc, =0x600140cd
.size mx1_sources_ui_steps_original, .-mx1_sources_ui_steps_original
.ltorg

.section .text.mx1_sources_ui_value_original,"ax",%progbits
.global mx1_sources_ui_value_original
.type mx1_sources_ui_value_original,%function
.thumb_func
mx1_sources_ui_value_original:
    push {r2-r8,lr}
    mov r8, r0
    movs r2, #0
    ldr pc, =0x60013749
.size mx1_sources_ui_value_original, .-mx1_sources_ui_value_original
.ltorg

.section .text.mx1_sources_ui_select_leds_original,"ax",%progbits
.global mx1_sources_ui_select_leds_original
.type mx1_sources_ui_select_leds_original,%function
.thumb_func
mx1_sources_ui_select_leds_original:
    push {r4-r8,lr}
    ldr r0, =0x605144cc
    ldr r12, =0x60018259
    blx r12
    ldr pc, =0x6001469d
.size mx1_sources_ui_select_leds_original, .-mx1_sources_ui_select_leds_original
.ltorg
