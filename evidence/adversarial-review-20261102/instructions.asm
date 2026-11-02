; main app decoded +0xd4686, runtime 0x01003dfa
01003dfa  1e4a       ldr      r2, [pc, #0x78]
01003dfc  0028       cmp      r0, #0
01003dfe  07d0       beq      #0x1003e10
01003e00  02ebc000   add.w    r0, r2, r0, lsl #3
01003e04  b0f87000   ldrh.w   r0, [r0, #0x70]
01003e08  c0f30a00   ubfx     r0, r0, #0, #0xb
01003e0c  0880       strh     r0, [r1]
01003e0e  7047       bx       lr
01003e10  106f       ldr      r0, [r2, #0x70]
01003e12  00f07f00   and      r0, r0, #0x7f
01003e16  0880       strh     r0, [r1]
01003e18  7047       bx       lr
; main app decoded +0xd5234, runtime 0x010049a8
010049a8  4a4e       ldr      r6, [pc, #0x128]
010049aa  d6f80401   ldr.w    r0, [r6, #0x104]
010049ae  01a9       add      r1, sp, #4
010049b0  0020       movs     r0, #0
010049b2  fff722fa   bl       #0x1003dfa
010049b6  0099       ldr      r1, [sp]
010049b8  bdf80440   ldrh.w   r4, [sp, #4]
010049bc  0868       ldr      r0, [r1]
010049be  a042       cmp      r0, r4
010049c0  00d8       bhi      #0x10049c4
010049c2  0446       mov      r4, r0
010049c4  4968       ldr      r1, [r1, #4]
010049c6  2246       mov      r2, r4
010049c8  0020       movs     r0, #0
010049ca  fff70bfa   bl       #0x1003de4
010049ce  0099       ldr      r1, [sp]
; main app decoded +0xda0ec, runtime 0x01009860
01009860  3878       ldrb     r0, [r7]
01009862  b04c       ldr      r4, [pc, #0x2c0]
01009864  0025       movs     r5, #0
01009866  48b1       cbz      r0, #0x100987c
01009868  d4f86c01   ldr.w    r0, [r4, #0x16c]
0100986c  0007       lsls     r0, r0, #0x1c
0100986e  05d5       bpl      #0x100987c
01009870  d4f8d800   ldr.w    r0, [r4, #0xd8]
01009874  c0f30a00   ubfx     r0, r0, #0, #0xb
01009878  f860       str      r0, [r7, #0xc]
0100987a  3d70       strb     r5, [r7]
; main app decoded +0xda166, runtime 0x010098da
010098da  d4f87c01   ldr.w    r0, [r4, #0x17c]
010098de  9346       mov      fp, r2
010098e0  c0f30340   ubfx     r0, r0, #0x10, #4
010098e4  0228       cmp      r0, #2
010098e6  4ff00000   mov.w    r0, #0
010098ea  1bd0       beq      #0x1009924
010098ec  0b46       mov      r3, r1
010098ee  d4f8f411   ldr.w    r1, [r4, #0x1f4]
010098f2  0091       str      r1, [sp]
010098f4  5945       cmp      r1, fp
010098f6  1bd1       bne      #0x1009930
010098f8  46f82030   str.w    r3, [r6, r0, lsl #2]
010098fc  1ee0       b        #0x100993c
010098fe  1028       cmp      r0, #0x10
01009900  01d0       beq      #0x1009906
01009902  1128       cmp      r0, #0x11
01009904  0ed1       bne      #0x1009924
01009906  d4f8f421   ldr.w    r2, [r4, #0x1f4]
0100990a  0092       str      r2, [sp]
0100990c  5a45       cmp      r2, fp
0100990e  02d1       bne      #0x1009916
01009910  46f82010   str.w    r1, [r6, r0, lsl #2]
01009914  08e0       b        #0x1009928
01009916  caf80020   str.w    r2, [sl]
0100991a  d8f80020   ldr.w    r2, [r8]
0100991e  46f82020   str.w    r2, [r6, r0, lsl #2]
01009922  01e0       b        #0x1009928
01009924  46f82050   str.w    r5, [r6, r0, lsl #2]
01009928  401c       adds     r0, r0, #1
0100992a  1228       cmp      r0, #0x12
0100992c  e7db       blt      #0x10098fe
0100992e  08e0       b        #0x1009942
01009930  caf80010   str.w    r1, [sl]
01009934  d8f80010   ldr.w    r1, [r8]
01009938  46f82010   str.w    r1, [r6, r0, lsl #2]
0100993c  401c       adds     r0, r0, #1
0100993e  1228       cmp      r0, #0x12
01009940  d5db       blt      #0x10098ee
01009942  f868       ldr      r0, [r7, #0xc]
01009944  4838       subs     r0, #0x48
01009946  f860       str      r0, [r7, #0xc]
01009948  f868       ldr      r0, [r7, #0xc]
0100994a  9028       cmp      r0, #0x90
0100994c  03d0       beq      #0x1009956
0100994e  0220       movs     r0, #2
01009950  c9f80400   str.w    r0, [sb, #4]
01009954  5fe0       b        #0x1009a16
01009956  7849       ldr      r1, [pc, #0x1e0]
01009958  0020       movs     r0, #0
0100995a  d4f8f421   ldr.w    r2, [r4, #0x1f4]
0100995e  41f82020   str.w    r2, [r1, r0, lsl #2]
01009962  401c       adds     r0, r0, #1
01009964  2428       cmp      r0, #0x24
01009966  f8db       blt      #0x100995a
01009968  3d70       strb     r5, [r7]
0100996a  c9f80010   str.w    r1, [sb]
0100996e  0321       movs     r1, #3
01009970  c9f80410   str.w    r1, [sb, #4]
01009974  4fe0       b        #0x1009a16
; main app decoded +0xda278, runtime 0x010099ec
010099ec  5248       ldr      r0, [pc, #0x148]
010099ee  1a68       ldr      r2, [r3]
010099f0  9030       adds     r0, #0x90
010099f2  8242       cmp      r2, r0
010099f4  0fd3       blo      #0x1009a16
010099f6  0120       movs     r0, #1
010099f8  3870       strb     r0, [r7]
010099fa  0220       movs     r0, #2
010099fc  5860       str      r0, [r3, #4]
010099fe  0ae0       b        #0x1009a16
