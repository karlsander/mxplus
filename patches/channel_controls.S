.syntax unified
.thumb
.cpu cortex-m3
.section .channel_lookup,"ax",%progbits
.global mx1_system_parameter_id
.type mx1_system_parameter_id,%function
.thumb_func
mx1_system_parameter_id:
    cmp r1,#0x8d
    bhs 1f
    mov r0,r1
    bx lr
1:  push {r4,lr}
    b.w mx1_original_system_invalid
.size mx1_system_parameter_id,.-mx1_system_parameter_id
