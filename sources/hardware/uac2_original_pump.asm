01009840  2de9f84f   push.w   {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}
01009844  b54f       ldr      r7, [pc, #0x2d4] ; [01009b1c]=0x01010044
01009846  4ff0010c   mov.w    ip, #1
0100984a  b868       ldr      r0, [r7, #8]
0100984c  4fea5000   lsr.w    r0, r0, #1
01009850  b860       str      r0, [r7, #8]
01009852  b348       ldr      r0, [pc, #0x2cc] ; [01009b20]=0x40003228
01009854  0068       ldr      r0, [r0]
01009856  b968       ldr      r1, [r7, #8]
01009858  00f00200   and      r0, r0, #2
0100985c  0843       orrs     r0, r1
0100985e  b860       str      r0, [r7, #8]
01009860  3878       ldrb     r0, [r7]
01009862  b04c       ldr      r4, [pc, #0x2c0] ; [01009b24]=0x40010000
01009864  0025       movs     r5, #0
01009866  48b1       cbz      r0, #0x100987c
01009868  d4f86c01   ldr.w    r0, [r4, #0x16c]
0100986c  0007       lsls     r0, r0, #0x1c
0100986e  05d5       bpl      #0x100987c
01009870  d4f8d800   ldr.w    r0, [r4, #0xd8]
01009874  c0f30a00   ubfx     r0, r0, #0, #0xb
01009878  f860       str      r0, [r7, #0xc]
0100987a  3d70       strb     r5, [r7]
0100987c  dff8a892   ldr.w    sb, [pc, #0x2a8] ; [01009b28]=0x2000041c
01009880  dff8b082   ldr.w    r8, [pc, #0x2b0] ; [01009b34]=0x4004056c
01009884  a949       ldr      r1, [pc, #0x2a4] ; [01009b2c]=0xbf800000
01009886  d9f80400   ldr.w    r0, [sb, #4]
0100988a  a94e       ldr      r6, [pc, #0x2a4] ; [01009b30]=0x40101000
0100988c  dff8a4a2   ldr.w    sl, [pc, #0x2a4] ; [01009b34]=0x4004056c
01009890  4ff00042   mov.w    r2, #-0x80000000
01009894  08f10808   add.w    r8, r8, #8
01009898  0228       cmp      r0, #2
0100989a  05d0       beq      #0x10098a8
0100989c  4b46       mov      r3, sb
0100989e  0128       cmp      r0, #1
010098a0  07d0       beq      #0x10098b2
010098a2  0328       cmp      r0, #3
010098a4  67d0       beq      #0x1009976
010098a6  0be0       b        #0x10098c0
010098a8  d4f86c01   ldr.w    r0, [r4, #0x16c]
010098ac  0007       lsls     r0, r0, #0x1c
010098ae  14d4       bmi      #0x10098da
010098b0  06e0       b        #0x10098c0
010098b2  d4f86c01   ldr.w    r0, [r4, #0x16c]
010098b6  0007       lsls     r0, r0, #0x1c
010098b8  02d5       bpl      #0x10098c0
010098ba  b868       ldr      r0, [r7, #8]
010098bc  0128       cmp      r0, #1
010098be  0cd0       beq      #0x10098da
010098c0  d4f86c01   ldr.w    r0, [r4, #0x16c]
010098c4  0007       lsls     r0, r0, #0x1c
010098c6  77d5       bpl      #0x10099b8
010098c8  b868       ldr      r0, [r7, #8]
010098ca  0128       cmp      r0, #1
010098cc  02d0       beq      #0x10098d4
010098ce  0120       movs     r0, #1
010098d0  c9f80400   str.w    r0, [sb, #4]
010098d4  0120       movs     r0, #1
010098d6  3870       strb     r0, [r7]
010098d8  97e0       b        #0x1009a0a
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
01009956  7849       ldr      r1, [pc, #0x1e0] ; [01009b38]=0x20000a10
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
01009976  d4f87c01   ldr.w    r0, [r4, #0x17c]
0100997a  c0f30340   ubfx     r0, r0, #0x10, #4
0100997e  0228       cmp      r0, #2
01009980  4ff00000   mov.w    r0, #0
01009984  0ad0       beq      #0x100999c
01009986  9346       mov      fp, r2
01009988  8946       mov      sb, r1
0100998a  1968       ldr      r1, [r3]
0100998c  04c9       ldm      r1!, {r2}
0100998e  0092       str      r2, [sp]
01009990  1960       str      r1, [r3]
01009992  5a45       cmp      r2, fp
01009994  21d1       bne      #0x10099da
01009996  46f82090   str.w    sb, [r6, r0, lsl #2]
0100999a  24e0       b        #0x10099e6
0100999c  9646       mov      lr, r2
0100999e  8b46       mov      fp, r1
010099a0  d146       mov      sb, sl
010099a2  03e0       b        #0x10099ac
010099a4  1028       cmp      r0, #0x10
010099a6  08d0       beq      #0x10099ba
010099a8  1128       cmp      r0, #0x11
010099aa  06d0       beq      #0x10099ba
010099ac  46f82050   str.w    r5, [r6, r0, lsl #2]
010099b0  401c       adds     r0, r0, #1
010099b2  1228       cmp      r0, #0x12
010099b4  f6db       blt      #0x10099a4
010099b6  19e0       b        #0x10099ec
010099b8  22e0       b        #0x1009a00
010099ba  1968       ldr      r1, [r3]
010099bc  04c9       ldm      r1!, {r2}
010099be  0092       str      r2, [sp]
010099c0  1960       str      r1, [r3]
010099c2  7245       cmp      r2, lr
010099c4  02d1       bne      #0x10099cc
010099c6  46f820b0   str.w    fp, [r6, r0, lsl #2]
010099ca  f1e7       b        #0x10099b0
010099cc  c9f80020   str.w    r2, [sb]
010099d0  d8f80010   ldr.w    r1, [r8]
010099d4  46f82010   str.w    r1, [r6, r0, lsl #2]
010099d8  eae7       b        #0x10099b0
010099da  caf80020   str.w    r2, [sl]
010099de  d8f80010   ldr.w    r1, [r8]
010099e2  46f82010   str.w    r1, [r6, r0, lsl #2]
010099e6  401c       adds     r0, r0, #1
010099e8  1228       cmp      r0, #0x12
010099ea  cedb       blt      #0x100998a
010099ec  5248       ldr      r0, [pc, #0x148] ; [01009b38]=0x20000a10
010099ee  1a68       ldr      r2, [r3]
010099f0  9030       adds     r0, #0x90
010099f2  8242       cmp      r2, r0
010099f4  0fd3       blo      #0x1009a16
010099f6  0120       movs     r0, #1
010099f8  3870       strb     r0, [r7]
010099fa  0220       movs     r0, #2
010099fc  5860       str      r0, [r3, #4]
010099fe  0ae0       b        #0x1009a16
01009a00  c9f80450   str.w    r5, [sb, #4]
01009a04  3d70       strb     r5, [r7]
01009a06  4ff0000c   mov.w    ip, #0
01009a0a  0020       movs     r0, #0
01009a0c  46f82050   str.w    r5, [r6, r0, lsl #2]
01009a10  401c       adds     r0, r0, #1
01009a12  1228       cmp      r0, #0x12
01009a14  fadb       blt      #0x1009a0c
01009a16  7868       ldr      r0, [r7, #4]
01009a18  88b1       cbz      r0, #0x1009a3e
01009a1a  4849       ldr      r1, [pc, #0x120] ; [01009b3c]=0x00fb6004
01009a1c  0228       cmp      r0, #2
01009a1e  19d0       beq      #0x1009a54
01009a20  0328       cmp      r0, #3
01009a22  41d0       beq      #0x1009aa8
01009a24  0428       cmp      r0, #4
01009a26  44d0       beq      #0x1009ab2
01009a28  b868       ldr      r0, [r7, #8]
01009a2a  0228       cmp      r0, #2
01009a2c  38d1       bne      #0x1009aa0
01009a2e  bcf1000f   cmp.w    ip, #0
01009a32  35d0       beq      #0x1009aa0
01009a34  c81e       subs     r0, r1, #3
01009a36  c4f87001   str.w    r0, [r4, #0x170]
01009a3a  0220       movs     r0, #2
01009a3c  2fe0       b        #0x1009a9e
01009a3e  d4f87401   ldr.w    r0, [r4, #0x174]
01009a42  c003       lsls     r0, r0, #0xf
01009a44  2cd5       bpl      #0x1009aa0
01009a46  d4f87401   ldr.w    r0, [r4, #0x174]
01009a4a  10f0706f   tst.w    r0, #0xf000000
01009a4e  27d0       beq      #0x1009aa0
01009a50  0120       movs     r0, #1
01009a52  24e0       b        #0x1009a9e
01009a54  d4f87401   ldr.w    r0, [r4, #0x174]
01009a58  10f0706f   tst.w    r0, #0xf000000
01009a5c  22d0       beq      #0x1009aa4
01009a5e  d4f87401   ldr.w    r0, [r4, #0x174]
01009a62  4007       lsls     r0, r0, #0x1d
01009a64  1ed5       bpl      #0x1009aa4
01009a66  d4f87c01   ldr.w    r0, [r4, #0x17c]
01009a6a  c0f30330   ubfx     r0, r0, #0xc, #4
01009a6e  0228       cmp      r0, #2
01009a70  4ff00000   mov.w    r0, #0
01009a74  05d1       bne      #0x1009a82
01009a76  c4f8b851   str.w    r5, [r4, #0x1b8]
01009a7a  401c       adds     r0, r0, #1
01009a7c  0228       cmp      r0, #2
01009a7e  fadb       blt      #0x1009a76
01009a80  04e0       b        #0x1009a8c
01009a82  c4f8b851   str.w    r5, [r4, #0x1b8]
01009a86  401c       adds     r0, r0, #1
01009a88  1228       cmp      r0, #0x12
01009a8a  fadb       blt      #0x1009a82
01009a8c  b868       ldr      r0, [r7, #8]
01009a8e  0228       cmp      r0, #2
01009a90  06d1       bne      #0x1009aa0
01009a92  d4f87401   ldr.w    r0, [r4, #0x174]
01009a96  0843       orrs     r0, r1
01009a98  c4f87401   str.w    r0, [r4, #0x174]
01009a9c  0320       movs     r0, #3
01009a9e  7860       str      r0, [r7, #4]
01009aa0  bde8f88f   pop.w    {r3, r4, r5, r6, r7, r8, sb, sl, fp, pc}
01009aa4  7d60       str      r5, [r7, #4]
01009aa6  fbe7       b        #0x1009aa0
01009aa8  bcf1000f   cmp.w    ip, #0
01009aac  f8d0       beq      #0x1009aa0
01009aae  0420       movs     r0, #4
01009ab0  7860       str      r0, [r7, #4]
01009ab2  d4f87401   ldr.w    r0, [r4, #0x174]
01009ab6  10f0706f   tst.w    r0, #0xf000000
01009aba  f3d0       beq      #0x1009aa4
01009abc  d4f87401   ldr.w    r0, [r4, #0x174]
01009ac0  4007       lsls     r0, r0, #0x1d
01009ac2  efd5       bpl      #0x1009aa4
01009ac4  d4f87c01   ldr.w    r0, [r4, #0x17c]
01009ac8  c0f30330   ubfx     r0, r0, #0xc, #4
01009acc  0228       cmp      r0, #2
01009ace  15d0       beq      #0x1009afc
01009ad0  0020       movs     r0, #0
01009ad2  5246       mov      r2, sl
01009ad4  06eb8003   add.w    r3, r6, r0, lsl #2
01009ad8  9b6c       ldr      r3, [r3, #0x48]
01009ada  c8f80030   str.w    r3, [r8]
01009ade  1368       ldr      r3, [r2]
01009ae0  c4f8b831   str.w    r3, [r4, #0x1b8]
01009ae4  401c       adds     r0, r0, #1
01009ae6  1228       cmp      r0, #0x12
01009ae8  f4db       blt      #0x1009ad4
01009aea  b868       ldr      r0, [r7, #8]
01009aec  0228       cmp      r0, #2
01009aee  d7d1       bne      #0x1009aa0
01009af0  d4f87401   ldr.w    r0, [r4, #0x174]
01009af4  0843       orrs     r0, r1
01009af6  c4f87401   str.w    r0, [r4, #0x174]
01009afa  d1e7       b        #0x1009aa0
01009afc  56f8880f   ldr      r0, [r6, #0x88]!
01009b00  c8f80000   str.w    r0, [r8]
01009b04  daf80020   ldr.w    r2, [sl]
01009b08  c4f8b821   str.w    r2, [r4, #0x1b8]
01009b0c  7268       ldr      r2, [r6, #4]
01009b0e  c8f80020   str.w    r2, [r8]
01009b12  daf80000   ldr.w    r0, [sl]
01009b16  c4f8b801   str.w    r0, [r4, #0x1b8]
01009b1a  e6e7       b        #0x1009aea
01009b1c  4400       lsls     r4, r0, #1
01009b1e  0101       lsls     r1, r0, #4
01009b20  2832       adds     r2, #0x28
01009b22  0040       ands     r0, r0
01009b24  0000       movs     r0, r0
01009b26  0140       ands     r1, r0
01009b28  1c04       lsls     r4, r3, #0x10
01009b2a  0020       movs     r0, #0
01009b2c  0000       movs     r0, r0
01009b2e  80bf       hint     #8
01009b30  0010       asrs     r0, r0, #0x20
01009b32  1040       ands     r0, r2
01009b34  6c05       lsls     r4, r5, #0x15
01009b36  0440       ands     r4, r0
01009b38  100a       lsrs     r0, r2, #8
01009b3a  0020       movs     r0, #0
01009b3c  0460       str      r4, [r0]
01009b3e  fb00       lsls     r3, r7, #3
01009b40  2de9f041   push.w   {r4, r5, r6, r7, r8, lr}
01009b44  374f       ldr      r7, [pc, #0xdc] ; [01009c24]=0x0100f458
01009b46  384e       ldr      r6, [pc, #0xe0] ; [01009c28]=0x20000428
01009b48  0546       mov      r5, r0
01009b4a  19b3       cbz      r1, #0x1009b94
01009b4c  0ab1       cbz      r2, #0x1009b52
01009b4e  0121       movs     r1, #1
01009b50  00e0       b        #0x1009b54
01009b52  0021       movs     r1, #0
01009b54  03eb4300   add.w    r0, r3, r3, lsl #1
01009b58  4ff00004   mov.w    r4, #0
