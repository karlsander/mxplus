/* Bounded replacement for main-app USB playback, 0x01009860..0x01009a16.
 * The original callback prologue, phase tracking, capture path and epilogue
 * stay in place. No calls, extra stack, allocation or sample arithmetic.
 * Original conversion registers and INT_MIN -> float(-1) handling remain.
 * r7 points to the original packet flag/capture state/phase/byte counter.
 * r12=1 from the original prologue is preserved for capture-first startup.
 */
.syntax unified
.thumb
.section .usb_playback_patch,"ax",%progbits
.global mx1_usb_playback_patch
.type mx1_usb_playback_patch,%function
.thumb_func
mx1_usb_playback_patch:
    ldr r4, =0x40010000              /* USB peripheral */
    ldr r6, =0x40101000              /* playback exchange lanes */
    ldr r8, =0x40040574              /* converted float */
    ldr r10, =0x4004056c             /* integer conversion input */
    ldr r9, =0x2000041c              /* tail pointer, playback state */
    movs r5, #0

    /* Snapshot the OUT alternate once; never interpret an old buffered tail
     * with a new channel count. The byte occupies existing owned padding. */
    ldr r0, [r4, #0x17c]
    ubfx r0, r0, #16, #4
    ldr r1, =mx1_usb_playback_alt
    ldrb r2, [r1]
    cmp r0, r2
    beq .Lsame_alternate
    strb r0, [r1]
    str r5, [r9, #4]
    strb r5, [r7]
.Lsame_alternate:
    movs r2, #72
    cmp r0, #1
    beq .Lvalid_alternate
    cmp r0, #2
    bne .Lreset
    movs r2, #8
.Lvalid_alternate:
    mov r11, r2                     /* bytes per complete sample frame */
    ldr r3, [r4, #0x16c]
    ands r3, r3, #8                 /* OUT FIFO readiness */
    ldrb r0, [r7]
    cbz r0, .Ldispatch
    cbz r3, .Ldispatch
    ldr r0, [r4, #0xd8]
    ubfx r0, r0, #0, #11
    /* Reject partial frames before any FIFO access. Zero-length packets
     * likewise take the silent reset path instead of wrapping the count. */
    udiv r1, r0, r11
    mls r1, r1, r11, r0
    cmp r1, #0
    bne .Lreset
    str r0, [r7, #12]
    strb r5, [r7]
.Ldispatch:
    ldr r0, [r9, #4]
    cmp r0, #3
    beq .Lbuffered
    cmp r3, #0
    beq .Lreset
    cmp r0, #2
    beq .Ldirect
    cmp r0, #1
    bne .Lprime
    ldr r0, [r7, #8]
    cmp r0, #1
    beq .Ldirect
.Lprime:
    /* Preserve the original falling-phase startup handshake. */
    ldr r0, [r7, #8]
    cmp r0, #1
    beq .Larm_packet
    movs r0, #1
    str r0, [r9, #4]
.Larm_packet:
    movs r0, #1
    strb r0, [r7]
    b .Lsilence

.Ldirect:
    ldr r0, [r7, #12]
    cmp r0, r11
    blo .Lreset
    add.w r1, r4, #0x1f4            /* fixed FIFO address */
    mov.w lr, #0                   /* source increment */
    b .Lframe
.Lbuffered:
    ldr r1, [r9]
    ldr r0, =0x20000a10
    cmp r1, r0
    blo .Lreset
    adds r0, #144
    cmp r1, r0
    bhs .Lreset
    subs r0, r0, r1
    cmp r0, r11
    blo .Lreset
    mov.w lr, #4                   /* advancing SRAM source */
.Lframe:
    movs r0, #0
    cmp r11, #8
    bne .Lsample
.Lclear_stereo_prefix:
    str r5, [r6, r0, lsl #2]
    adds r0, #1
    cmp r0, #16
    blo .Lclear_stereo_prefix
.Lsample:
    ldr r2, [r1]
    add r1, lr
    cmp r2, #0x80000000
    beq .Lminimum
    str r2, [r10]
    ldr r2, [r8]
    b .Lstore_sample
.Lminimum:
    ldr r2, =0xbf800000
.Lstore_sample:
    str r2, [r6, r0, lsl #2]
    adds r0, #1
    cmp r0, #18
    blo .Lsample
    cmp lr, #0
    beq .Laccount_packet

    str r1, [r9]
    ldr r0, =0x20000aa0
    cmp r1, r0
    blo .Lcapture
.Lnext_packet:
    movs r0, #1
    strb r0, [r7]
    movs r0, #2
    str r0, [r9, #4]
    b .Lcapture

.Laccount_packet:
    ldr r0, [r7, #12]
    sub r0, r0, r11
    str r0, [r7, #12]
    cmp r0, #0
    beq .Lnext_packet
    cmp r0, r11, lsl #1
    bls .Lprefetch
    movs r0, #2
    str r0, [r9, #4]
    b .Lcapture
.Lprefetch:
    /* Place one/two remaining frames at the end of the original 144-byte
     * buffer. Stereo uses 8/16 bytes; 18-channel uses 72/144. */
    ldr r1, =0x20000aa0
    subs r1, r1, r0
    str r1, [r9]
    lsrs r0, r0, #2
.Lprefetch_word:
    ldr r2, [r4, #0x1f4]
    stm r1!, {r2}
    subs r0, #1
    bne .Lprefetch_word
    strb r5, [r7]
    movs r0, #3
    str r0, [r9, #4]
    b .Lcapture

.Lreset:
    str r5, [r9, #4]
    strb r5, [r7]
    str r5, [r7, #12]
.Lsilence:
    movs r0, #0
.Lclear_lane:
    str r5, [r6, r0, lsl #2]
    adds r0, #1
    cmp r0, #18
    blo .Lclear_lane
.Lcapture:
    b .Lcapture_resume
    .ltorg
.size mx1_usb_playback_patch, .-mx1_usb_playback_patch
    /* Exact original overwrite bound. Assembly fails rather than expanding. */
    .org 0x1b6, 0
.Lcapture_resume:

.section .usb_stream_state,"aw",%nobits
.global mx1_usb_playback_alt
.type mx1_usb_playback_alt,%object
mx1_usb_playback_alt:
    .space 1
.size mx1_usb_playback_alt, 1
