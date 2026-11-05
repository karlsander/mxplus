.syntax unified
.thumb
.cpu cortex-m3
.global mx1_host_image
.set mx1_host_image,1
.section .host_text,"ax",%progbits
.macro trampoline name
.global \name
.type \name,%function
.thumb_func
\name:
.endm
.macro resume address
 ldr r12,=\address
 bx r12
 .ltorg
.endm
trampoline host_config_original
 push.w {r4-r11,lr}
 sub sp,#28
 mov r4,r0
 mov r5,r1
 resume 0x6000a1ed
trampoline host_tx_open_original
 push.w {r4-r10,lr}
 mov r4,r0
 ldrb r2,[r0,#15]
 resume 0x60009169
trampoline host_rx_open_original
 push.w {r4-r10,lr}
 ldr r5,=0x4000bc00
 mov r4,r0
 ldrb r2,[r0,#15]
 resume 0x60009105
trampoline host_tx_close_original
 push {r4-r6,lr}
 ldrb r0,[r0,#4]
 ldr r1,=0x4000bf20
 add.w r0,r0,r0,lsl #2
 resume 0x010091c7
trampoline host_rx_close_original
 push {r4-r6,lr}
 ldrb r0,[r0,#4]
 ldr r1,=0x4000bf20
 add.w r0,r0,r0,lsl #2
 resume 0x01009077
trampoline host_enqueue_original
 ldr r2,=0x4000bf20
 push {r4-r6,lr}
 mov r3,r1
 add.w r1,r0,r0,lsl #2
 resume 0x010093c5
trampoline host_tx_poll_original
 resume 0x01009377
trampoline host_rx_poll_original
 resume 0x010092ef
trampoline host_ohci_bind_original
 ldr r2,=0x6002b0f0
 add.w r0,r0,r0,lsl #1
 ldrh.w r0,[r2,r0,lsl #2]
 resume 0x60013c7f
trampoline host_ohci_done_original
 push.w {r3-r11,lr}
 mov r5,r0
 /* Displaced 60013f78 is the identity mapping (bx lr). */
 resume 0x6001380f
trampoline host_audio_close_original
 push {r4-r6,lr}
 ldrsh.w r4,[r0,#0x12]
 ldrsh.w r5,[r0,#2]
 resume 0x6000834b
trampoline host_audio_tick_original
 push.w {r2-r12,lr}
 ldr r11,=0x4000b400
 resume 0x01008c69
