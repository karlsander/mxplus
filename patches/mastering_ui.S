.syntax unified
.thumb
.cpu cortex-m3
.section .master_head,"ax",%progbits
.global mx1_master_redraw_original
.type mx1_master_redraw_original,%function
.thumb_func
mx1_master_redraw_original:
    /* Displaced 0x6001484a..0x60014853, including the conditional branch. */
    push {r4,lr}
    mov r4,r0
    ldrh r0,[r0]
    cmp r0,#0
    bne 1f
    ldr r12,=0x60014951
    bx r12
1:  ldr r12,=0x60014855
    bx r12
.size mx1_master_redraw_original,.-mx1_master_redraw_original
.ltorg

.section .master_lookup,"ax",%progbits
.global mx1_mixer_parameter_id
.type mx1_mixer_parameter_id,%function
.thumb_func
mx1_mixer_parameter_id:
    cmp.w r1,#0x106
    bhi 2f
    movw r0,#0x10f
    cmp r1,#0x73
    it hs
    addhs r0,#5
    add r0,r1
    bx lr
2:  push {r4,lr}
    /* Same diagnostic and shared pop as the original invalid-input path. */
    b.w mx1_original_mix_invalid
.size mx1_mixer_parameter_id,.-mx1_mixer_parameter_id
