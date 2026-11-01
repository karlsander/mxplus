01000280: f704       lsls     r7, r6, #0x13
01000282: 0001       lsls     r0, r0, #4
01000284: f704       lsls     r7, r6, #0x13
01000286: 0001       lsls     r0, r0, #4
01000288: f704       lsls     r7, r6, #0x13
0100028a: 0001       lsls     r0, r0, #4
0100028c: f704       lsls     r7, r6, #0x13
0100028e: 0001       lsls     r0, r0, #4
01000290: f704       lsls     r7, r6, #0x13
01000292: 0001       lsls     r0, r0, #4
01000294: f704       lsls     r7, r6, #0x13
01000296: 0001       lsls     r0, r0, #4
01000298: f704       lsls     r7, r6, #0x13
0100029a: 0001       lsls     r0, r0, #4
0100029c: f704       lsls     r7, r6, #0x13
0100029e: 0001       lsls     r0, r0, #4
010002a0: f704       lsls     r7, r6, #0x13
010002a2: 0001       lsls     r0, r0, #4
010002a4: f704       lsls     r7, r6, #0x13
010002a6: 0001       lsls     r0, r0, #4
010002a8: f704       lsls     r7, r6, #0x13
010002aa: 0001       lsls     r0, r0, #4
010002ac: f704       lsls     r7, r6, #0x13
010002ae: 0001       lsls     r0, r0, #4
010002b0: f704       lsls     r7, r6, #0x13
010002b2: 0001       lsls     r0, r0, #4
010002b4: f704       lsls     r7, r6, #0x13
010002b6: 0001       lsls     r0, r0, #4
010002b8: f704       lsls     r7, r6, #0x13
010002ba: 0001       lsls     r0, r0, #4
010002bc: f704       lsls     r7, r6, #0x13
010002be: 0001       lsls     r0, r0, #4
010002c0: dff80cd0   ldr.w    sp, [pc, #0xc]
010002c4: 02f06cf8   bl       #0x10023a0
010002c8: 0048       ldr      r0, [pc, #0]
010002ca: 0047       bx       r0
010002cc: 8704       lsls     r7, r0, #0x12
010002ce: 0001       lsls     r0, r0, #4
010002d0: 0080       strh     r0, [r0]
010002d2: 0201       lsls     r2, r0, #4
010002d4: 40f00100   orr      r0, r0, #1
010002d8: 0047       bx       r0
010002da: 0000       movs     r0, r0
010002dc: 10b5       push     {r4, lr}
010002de: 0749       ldr      r1, [pc, #0x1c]
010002e0: 0020       movs     r0, #0
010002e2: 4ff08444   mov.w    r4, #0x42000000
010002e6: 04eb4113   add.w    r3, r4, r1, lsl #5
010002ea: 03eb8002   add.w    r2, r3, r0, lsl #2
010002ee: 1368       ldr      r3, [r2]
010002f0: 13b1       cbz      r3, #0x10002f8
010002f2: 4ff04270   mov.w    r0, #0x3080000
010002f6: 10bd       pop      {r4, pc}
010002f8: 0148       ldr      r0, [pc, #4]
010002fa: fce7       b        #0x10002f6
010002fc: 04d0       beq      #0x1000308
010002fe: 0240       ands     r2, r0
01000300: 0000       movs     r0, r0
01000302: 0103       lsls     r1, r0, #0xc
01000304: 2548       ldr      r0, [pc, #0x94]
01000306: 0068       ldr      r0, [r0]
01000308: 401c       adds     r0, r0, #1
0100030a: 2449       ldr      r1, [pc, #0x90]
0100030c: 0860       str      r0, [r1]
0100030e: 7047       bx       lr
01000310: 2248       ldr      r0, [pc, #0x88]
01000312: 0068       ldr      r0, [r0]
01000314: 7047       bx       lr
01000316: 2248       ldr      r0, [pc, #0x88]
01000318: 0068       ldr      r0, [r0]
0100031a: 20f0c040   bic      r0, r0, #0x60000000
0100031e: 00f1c040   add.w    r0, r0, #0x60000000
01000322: 1f49       ldr      r1, [pc, #0x7c]
01000324: 0860       str      r0, [r1]
01000326: 0846       mov      r0, r1
01000328: 1e49       ldr      r1, [pc, #0x78]
0100032a: 0968       ldr      r1, [r1]
0100032c: 0160       str      r1, [r0]
0100032e: 7047       bx       lr
01000330: 08b5       push     {r3, lr}
01000332: 1d48       ldr      r0, [pc, #0x74]
01000334: 0068       ldr      r0, [r0]
01000336: 0090       str      r0, [sp]
01000338: 1c49       ldr      r1, [pc, #0x70]
0100033a: 0098       ldr      r0, [sp]
0100033c: 0860       str      r0, [r1]
0100033e: 1a48       ldr      r0, [pc, #0x68]
01000340: 00f10400   add.w    r0, r0, #4
01000344: 0068       ldr      r0, [r0]
01000346: 0090       str      r0, [sp]
01000348: 4ff08041   mov.w    r1, #0x40000000
0100034c: 0098       ldr      r0, [sp]
0100034e: c1f80401   str.w    r0, [r1, #0x104]
01000352: 4ff00000   mov.w    r0, #0
01000356: 0090       str      r0, [sp]
01000358: 0098       ldr      r0, [sp]
0100035a: c1f80801   str.w    r0, [r1, #0x108]
0100035e: 1248       ldr      r0, [pc, #0x48]
01000360: 00f10800   add.w    r0, r0, #8
01000364: 0068       ldr      r0, [r0]
01000366: 0090       str      r0, [sp]
01000368: 0098       ldr      r0, [sp]
0100036a: c1f80c01   str.w    r0, [r1, #0x10c]
0100036e: 4ff00000   mov.w    r0, #0
01000372: 0090       str      r0, [sp]
01000374: 0e49       ldr      r1, [pc, #0x38]
01000376: 0098       ldr      r0, [sp]
01000378: 0860       str      r0, [r1]
0100037a: 08bd       pop      {r3, pc}
0100037c: 7047       bx       lr
0100037e: 10b5       push     {r4, lr}
01000380: fff7d6ff   bl       #0x1000330
01000384: fff7c7ff   bl       #0x1000316
01000388: 0a48       ldr      r0, [pc, #0x28]
0100038a: 4169       ldr      r1, [r0, #0x14]
0100038c: 0a48       ldr      r0, [pc, #0x28]
0100038e: 8847       blx      r1
01000390: fff7f4ff   bl       #0x100037c
01000394: 0a20       movs     r0, #0xa
01000396: 00f0f7f9   bl       #0x1000788
0100039a: 10bd       pop      {r4, pc}
0100039c: 0000       movs     r0, r0
0100039e: 0101       lsls     r1, r0, #4
010003a0: 0050       str      r0, [r0, r0]
010003a2: 0040       ands     r0, r0
010003a4: a428       cmp      r0, #0xa4
010003a6: 0001       lsls     r0, r0, #4
010003a8: a828       cmp      r0, #0xa8
010003aa: 0001       lsls     r0, r0, #4
010003ac: 0001       lsls     r0, r0, #4
010003ae: 0040       ands     r0, r0
010003b0: 0002       lsls     r0, r0, #8
010003b2: 0040       ands     r0, r0
010003b4: 0030       adds     r0, #0
010003b6: 0002       lsls     r0, r0, #8
010003b8: c0cd       ldm      r5!, {r6, r7}
010003ba: 1700       movs     r7, r2
010003bc: 0eb5       push     {r1, r2, r3, lr}
010003be: 1f4a       ldr      r2, [pc, #0x7c]
010003c0: 07ca       ldm      r2, {r0, r1, r2}
010003c2: 8de80700   stm.w    sp, {r0, r1, r2}
010003c6: 6846       mov      r0, sp
010003c8: 00f08df9   bl       #0x10006e6
010003cc: 0ebd       pop      {r1, r2, r3, pc}
010003ce: 7047       bx       lr
010003d0: 00b5       push     {lr}
010003d2: 95b0       sub      sp, #0x54
010003d4: 5022       movs     r2, #0x50
010003d6: 1949       ldr      r1, [pc, #0x64]
010003d8: 0c31       adds     r1, #0xc
010003da: 01a8       add      r0, sp, #4
010003dc: 01f09cff   bl       #0x1002318
010003e0: 01a8       add      r0, sp, #4
010003e2: 00f080f9   bl       #0x10006e6
010003e6: 15b0       add      sp, #0x54
010003e8: 00bd       pop      {pc}
010003ea: 00b5       push     {lr}
010003ec: 8bb0       sub      sp, #0x2c
010003ee: 2822       movs     r2, #0x28
010003f0: 1249       ldr      r1, [pc, #0x48]
010003f2: 5c31       adds     r1, #0x5c
010003f4: 01a8       add      r0, sp, #4
010003f6: 01f08fff   bl       #0x1002318
010003fa: 4ff48020   mov.w    r0, #0x40000
010003fe: 1049       ldr      r1, [pc, #0x40]
01000400: 0860       str      r0, [r1]
01000402: 4011       asrs     r0, r0, #5
01000404: 0861       str      r0, [r1, #0x10]
01000406: 0120       movs     r0, #1
01000408: 8861       str      r0, [r1, #0x18]
0100040a: 0020       movs     r0, #0
0100040c: 0862       str      r0, [r1, #0x20]
0100040e: 8862       str      r0, [r1, #0x28]
01000410: 1c20       movs     r0, #0x1c
01000412: 0863       str      r0, [r1, #0x30]
01000414: 01a8       add      r0, sp, #4
01000416: 00f066f9   bl       #0x10006e6
0100041a: 0bb0       add      sp, #0x2c
0100041c: 00bd       pop      {pc}
0100041e: 10b5       push     {r4, lr}
01000420: fff7d6ff   bl       #0x10003d0
01000424: 0749       ldr      r1, [pc, #0x1c]
01000426: c868       ldr      r0, [r1, #0xc]
01000428: 8047       blx      r0
0100042a: 0228       cmp      r0, #2
0100042c: 01d0       beq      #0x1000432
0100042e: fff7c5ff   bl       #0x10003bc
01000432: fff7ccff   bl       #0x10003ce
01000436: fff7d8ff   bl       #0x10003ea
0100043a: 10bd       pop      {r4, pc}
0100043c: b428       cmp      r0, #0xb4
0100043e: 0001       lsls     r0, r0, #4
01000440: 00d0       beq      #0x1000444
01000442: 0240       ands     r2, r0
01000444: 0030       adds     r0, #0
01000446: 0002       lsls     r0, r0, #8
01000448: 2de9f041   push.w   {r4, r5, r6, r7, r8, lr}
0100044c: 0446       mov      r4, r0
0100044e: e06b       ldr      r0, [r4, #0x3c]
01000450: 50b1       cbz      r0, #0x1000468
01000452: e06a       ldr      r0, [r4, #0x2c]
01000454: 0619       adds     r6, r0, r4
01000456: a76b       ldr      r7, [r4, #0x38]
01000458: d4f83c80   ldr.w    r8, [r4, #0x3c]
0100045c: 4246       mov      r2, r8
0100045e: 3946       mov      r1, r7
01000460: 3046       mov      r0, r6
01000462: 00f08cf8   bl       #0x100057e
01000466: 0ce0       b        #0x1000482
01000468: e36a       ldr      r3, [r4, #0x2c]
0100046a: 1819       adds     r0, r3, r4
0100046c: a16b       ldr      r1, [r4, #0x38]
0100046e: 226b       ldr      r2, [r4, #0x30]
01000470: 0025       movs     r5, #0
01000472: 02e0       b        #0x100047a
01000474: 08c8       ldm      r0!, {r3}
01000476: 08c1       stm      r1!, {r3}
01000478: 6d1c       adds     r5, r5, #1
0100047a: b5eb920f   cmp.w    r5, r2, lsr #2
0100047e: f9d3       blo      #0x1000474
01000480: 00bf       nop      
01000482: bde8f081   pop.w    {r4, r5, r6, r7, r8, pc}
01000486: 70b5       push     {r4, r5, r6, lr}
01000488: 00f05af8   bl       #0x1000540
0100048c: fff777ff   bl       #0x100037e
01000490: fff724ff   bl       #0x10002dc
01000494: 0446       mov      r4, r0
01000496: b4f1427f   cmp.w    r4, #0x3080000
0100049a: 01d1       bne      #0x10004a0
0100049c: 01f00efb   bl       #0x1001abc
010004a0: 0d4d       ldr      r5, [pc, #0x34]
010004a2: 2846       mov      r0, r5
010004a4: 01f0b4f9   bl       #0x1001810
010004a8: b4f1427f   cmp.w    r4, #0x3080000
010004ac: 08d1       bne      #0x10004c0
010004ae: 4ff04875   mov.w    r5, #0x3200000
010004b2: 2846       mov      r0, r5
010004b4: fff7c8ff   bl       #0x1000448
010004b8: 2846       mov      r0, r5
010004ba: 01f016fb   bl       #0x1001aea
010004be: 00bf       nop      
010004c0: 2046       mov      r0, r4
010004c2: fff7c1ff   bl       #0x1000448
010004c6: 0549       ldr      r1, [pc, #0x14]
010004c8: 8869       ldr      r0, [r1, #0x18]
010004ca: 8047       blx      r0
010004cc: a06a       ldr      r0, [r4, #0x28]
010004ce: fff701ff   bl       #0x10002d4
010004d2: 0120       movs     r0, #1
010004d4: 70bd       pop      {r4, r5, r6, pc}
010004d6: 0000       movs     r0, r0
010004d8: 0080       strh     r0, [r0]
010004da: 0003       lsls     r0, r0, #0xc
010004dc: 0030       adds     r0, #0
010004de: 0002       lsls     r0, r0, #8
010004e0: 0548       ldr      r0, [pc, #0x14]
010004e2: 0047       bx       r0
010004e4: fee7       b        #0x10004e4
010004e6: fee7       b        #0x10004e6
010004e8: fee7       b        #0x10004e8
010004ea: fee7       b        #0x10004ea
010004ec: fee7       b        #0x10004ec
010004ee: fee7       b        #0x10004ee
010004f0: fee7       b        #0x10004f0
010004f2: fee7       b        #0x10004f2
010004f4: fee7       b        #0x10004f4
010004f6: fee7       b        #0x10004f6
010004f8: c102       lsls     r1, r0, #0xb
010004fa: 0001       lsls     r0, r0, #4
010004fc: 10b5       push     {r4, lr}
010004fe: 0320       movs     r0, #3
01000500: 0246       mov      r2, r0
01000502: 144b       ldr      r3, [pc, #0x50]
01000504: 1968       ldr      r1, [r3]
01000506: 4ff6ff03   movw     r3, #0xf8ff
0100050a: 1940       ands     r1, r3
0100050c: 124b       ldr      r3, [pc, #0x48]
0100050e: 0b43       orrs     r3, r1
01000510: 43ea0221   orr.w    r1, r3, r2, lsl #8
01000514: 0f4b       ldr      r3, [pc, #0x3c]
01000516: 1960       str      r1, [r3]
01000518: 00bf       nop      
0100051a: 001f       subs     r0, r0, #4
0100051c: 1f21       movs     r1, #0x1f
0100051e: 0028       cmp      r0, #0
01000520: 08da       bge      #0x1000534
01000522: ca06       lsls     r2, r1, #0x1b
01000524: 140e       lsrs     r4, r2, #0x18
01000526: 0b4a       ldr      r2, [pc, #0x2c]
01000528: 0c32       adds     r2, #0xc
0100052a: 00f00f03   and      r3, r0, #0xf
0100052e: 1b1f       subs     r3, r3, #4
01000530: d454       strb     r4, [r2, r3]
01000532: 03e0       b        #0x100053c
01000534: ca06       lsls     r2, r1, #0x1b
01000536: 130e       lsrs     r3, r2, #0x18
01000538: 084a       ldr      r2, [pc, #0x20]
0100053a: 1354       strb     r3, [r2, r0]
0100053c: 00bf       nop      
0100053e: 10bd       pop      {r4, pc}
01000540: 10b5       push     {r4, lr}
01000542: 0749       ldr      r1, [pc, #0x1c]
01000544: 886d       ldr      r0, [r1, #0x58]
01000546: 8047       blx      r0
01000548: fff769ff   bl       #0x100041e
0100054c: fff7d6ff   bl       #0x10004fc
01000550: 10bd       pop      {r4, pc}
01000552: 0000       movs     r0, r0
01000554: 0ced00e0   stc      p0, c14, [ip, #-0]
01000558: 0000       movs     r0, r0
0100055a: fa05       lsls     r2, r7, #0x17
0100055c: 00e4       b        #0xfffd60
0100055e: 00e0       b        #0x1000562
01000560: 0030       adds     r0, #0
01000562: 0002       lsls     r0, r0, #8
01000564: 0146       mov      r1, r0
01000566: 01f00302   and      r2, r1, #3
0100056a: 12b9       cbnz     r2, #0x1000572
0100056c: 3a4b       ldr      r3, [pc, #0xe8]
0100056e: 0868       ldr      r0, [r1]
01000570: 1860       str      r0, [r3]
01000572: d300       lsls     r3, r2, #3
01000574: 3848       ldr      r0, [pc, #0xe0]
01000576: 0068       ldr      r0, [r0]
01000578: d840       lsrs     r0, r3
0100057a: c0b2       uxtb     r0, r0
0100057c: 7047       bx       lr
0100057e: 2de9fc5f   push.w   {r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, ip, lr}
01000582: 0546       mov      r5, r0
01000584: 0c46       mov      r4, r1
01000586: 9146       mov      sb, r2
01000588: 04eb0900   add.w    r0, r4, sb
0100058c: 0090       str      r0, [sp]
0100058e: 0026       movs     r6, #0
01000590: 03e0       b        #0x100059a
01000592: 0020       movs     r0, #0
01000594: 3149       ldr      r1, [pc, #0xc4]
01000596: 8855       strb     r0, [r1, r6]
01000598: 761c       adds     r6, r6, #1
0100059a: 40f6ee70   movw     r0, #0xfee
0100059e: 8642       cmp      r6, r0
010005a0: f7db       blt      #0x1000592
010005a2: 0746       mov      r7, r0
010005a4: 4ff0000b   mov.w    fp, #0
010005a8: 00bf       nop      
010005aa: 4fea6b00   asr.w    r0, fp, #1
010005ae: 8346       mov      fp, r0
010005b0: 10f4807f   tst.w    r0, #0x100
010005b4: 06d1       bne      #0x10005c4
010005b6: 2846       mov      r0, r5
010005b8: 6d1c       adds     r5, r5, #1
010005ba: fff7d3ff   bl       #0x1000564
010005be: 8046       mov      r8, r0
010005c0: 48f47f4b   orr      fp, r8, #0xff00
010005c4: 1bf0010f   tst.w    fp, #1
010005c8: 12d0       beq      #0x10005f0
010005ca: 2846       mov      r0, r5
010005cc: 6d1c       adds     r5, r5, #1
010005ce: fff7c9ff   bl       #0x1000564
010005d2: 8046       mov      r8, r0
010005d4: 0098       ldr      r0, [sp]
010005d6: 8442       cmp      r4, r0
010005d8: 00d3       blo      #0x10005dc
010005da: 39e0       b        #0x1000650
010005dc: 04f8018b   strb     r8, [r4], #1
010005e0: 3846       mov      r0, r7
010005e2: 7f1c       adds     r7, r7, #1
010005e4: 1d49       ldr      r1, [pc, #0x74]
010005e6: 01f80080   strb.w   r8, [r1, r0]
010005ea: c7f30b07   ubfx     r7, r7, #0, #0xc
010005ee: dce7       b        #0x10005aa
010005f0: 2846       mov      r0, r5
010005f2: 6d1c       adds     r5, r5, #1
010005f4: fff7b6ff   bl       #0x1000564
010005f8: 0646       mov      r6, r0
010005fa: 2846       mov      r0, r5
010005fc: 6d1c       adds     r5, r5, #1
010005fe: fff7b1ff   bl       #0x1000564
01000602: 8246       mov      sl, r0
01000604: 0af0f000   and      r0, sl, #0xf0
01000608: 46ea0016   orr.w    r6, r6, r0, lsl #4
0100060c: 0af00f00   and      r0, sl, #0xf
01000610: 00f1020a   add.w    sl, r0, #2
01000614: 0020       movs     r0, #0
01000616: 0190       str      r0, [sp, #4]
01000618: 16e0       b        #0x1000648
0100061a: 0198       ldr      r0, [sp, #4]
0100061c: 3044       add      r0, r6
0100061e: c0f30b00   ubfx     r0, r0, #0, #0xc
01000622: 0e49       ldr      r1, [pc, #0x38]
01000624: 11f80080   ldrb.w   r8, [r1, r0]
01000628: 0098       ldr      r0, [sp]
0100062a: 8442       cmp      r4, r0
0100062c: 00d3       blo      #0x1000630
0100062e: 0ee0       b        #0x100064e
01000630: 04f8018b   strb     r8, [r4], #1
01000634: 3846       mov      r0, r7
01000636: 7f1c       adds     r7, r7, #1
01000638: 0849       ldr      r1, [pc, #0x20]
0100063a: 01f80080   strb.w   r8, [r1, r0]
0100063e: c7f30b07   ubfx     r7, r7, #0, #0xc
01000642: 0198       ldr      r0, [sp, #4]
01000644: 401c       adds     r0, r0, #1
01000646: 0190       str      r0, [sp, #4]
01000648: 0198       ldr      r0, [sp, #4]
0100064a: 5045       cmp      r0, sl
0100064c: e5dd       ble      #0x100061a
0100064e: ace7       b        #0x10005aa
01000650: 00bf       nop      
01000652: 4846       mov      r0, sb
01000654: bde8fc9f   pop.w    {r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, ip, pc}
01000658: 0400       movs     r4, r0
0100065a: 0101       lsls     r1, r0, #4
0100065c: 6c00       lsls     r4, r5, #1
0100065e: 0101       lsls     r1, r0, #4
01000660: 01b5       push     {r0, lr}
01000662: bdf80020   ldrh.w   r2, [sp]
01000666: c2f30311   ubfx     r1, r2, #4, #4
0100066a: ca17       asrs     r2, r1, #0x1f
0100066c: 01eb9272   add.w    r2, r1, r2, lsr #30
01000670: 9210       asrs     r2, r2, #2
01000672: bdf80030   ldrh.w   r3, [sp]
01000676: 03f00f03   and      r3, r3, #0xf
0100067a: 02eb8302   add.w    r2, r2, r3, lsl #2
0100067e: 234b       ldr      r3, [pc, #0x8c]
01000680: 03eb8200   add.w    r0, r3, r2, lsl #2
01000684: bdf80020   ldrh.w   r2, [sp]
01000688: c2f30311   ubfx     r1, r2, #4, #4
0100068c: ca17       asrs     r2, r1, #0x1f
0100068e: 01eb9272   add.w    r2, r1, r2, lsr #30
01000692: 9210       asrs     r2, r2, #2
01000694: b1eb8202   subs.w   r2, r1, r2, lsl #2
01000698: 06d0       beq      #0x10006a8
0100069a: 012a       cmp      r2, #1
0100069c: 0bd0       beq      #0x10006b6
0100069e: 022a       cmp      r2, #2
010006a0: 10d0       beq      #0x10006c4
010006a2: 032a       cmp      r2, #3
010006a4: 1cd1       bne      #0x10006e0
010006a6: 14e0       b        #0x10006d2
010006a8: 9df80120   ldrb.w   r2, [sp, #1]
010006ac: 0168       ldr      r1, [r0]
010006ae: 62f30701   bfi      r1, r2, #0, #8
010006b2: 0160       str      r1, [r0]
010006b4: 15e0       b        #0x10006e2
010006b6: 9df80120   ldrb.w   r2, [sp, #1]
010006ba: 0168       ldr      r1, [r0]
010006bc: 62f30f21   bfi      r1, r2, #8, #8
010006c0: 0160       str      r1, [r0]
010006c2: 0ee0       b        #0x10006e2
010006c4: 9df80120   ldrb.w   r2, [sp, #1]
010006c8: 0168       ldr      r1, [r0]
010006ca: 62f31741   bfi      r1, r2, #0x10, #8
010006ce: 0160       str      r1, [r0]
010006d0: 07e0       b        #0x10006e2
010006d2: 9df80120   ldrb.w   r2, [sp, #1]
010006d6: 0168       ldr      r1, [r0]
010006d8: 62f31f61   bfi      r1, r2, #0x18, #8
010006dc: 0160       str      r1, [r0]
010006de: 00e0       b        #0x10006e2
010006e0: 00bf       nop      
010006e2: 00bf       nop      
010006e4: 08bd       pop      {r3, pc}
010006e6: 18b5       push     {r3, r4, lr}
010006e8: 0446       mov      r4, r0
010006ea: 2088       ldrh     r0, [r4]
010006ec: 0090       str      r0, [sp]
010006ee: 05e0       b        #0x10006fc
010006f0: 0098       ldr      r0, [sp]
010006f2: fff7b5ff   bl       #0x1000660
010006f6: a41c       adds     r4, r4, #2
010006f8: 2088       ldrh     r0, [r4]
010006fa: 0090       str      r0, [sp]
010006fc: bdf80000   ldrh.w   r0, [sp]
01000700: 00f00f00   and      r0, r0, #0xf
01000704: 0f28       cmp      r0, #0xf
01000706: f3d1       bne      #0x10006f0
01000708: 18bd       pop      {r3, r4, pc}
0100070a: 0000       movs     r0, r0
0100070c: 00d4       bmi      #0x1000710
0100070e: 0240       ands     r2, r0
01000710: 70b5       push     {r4, r5, r6, lr}
01000712: 0446       mov      r4, r0
01000714: 0d46       mov      r5, r1
01000716: 2046       mov      r0, r4
01000718: 00f013f8   bl       #0x1000742
0100071c: 70bd       pop      {r4, r5, r6, pc}
0100071e: 10b5       push     {r4, lr}
01000720: 0446       mov      r4, r0
01000722: 00f02af8   bl       #0x100077a
01000726: 10bd       pop      {r4, pc}
01000728: 0146       mov      r1, r0
0100072a: 4ff0ff30   mov.w    r0, #-1
0100072e: 7047       bx       lr
01000730: 10b5       push     {r4, lr}
01000732: 0446       mov      r4, r0
01000734: 2046       mov      r0, r4
01000736: 00f004f8   bl       #0x1000742
0100073a: 10bd       pop      {r4, pc}
0100073c: 00bf       nop      
0100073e: fee7       b        #0x100073e
01000740: 7047       bx       lr
01000742: 0146       mov      r1, r0
01000744: 0e4a       ldr      r2, [pc, #0x38]
01000746: 1268       ldr      r2, [r2]
01000748: 12f0807f   tst.w    r2, #0x1000000
0100074c: 13d0       beq      #0x1000776
0100074e: 0d4a       ldr      r2, [pc, #0x34]
01000750: 1268       ldr      r2, [r2]
01000752: 12f0010f   tst.w    r2, #1
01000756: 0ed0       beq      #0x1000776
01000758: 0a4a       ldr      r2, [pc, #0x28]
0100075a: 803a       subs     r2, #0x80
0100075c: 1268       ldr      r2, [r2]
0100075e: 12f0010f   tst.w    r2, #1
01000762: 08d0       beq      #0x1000776
01000764: 00bf       nop      
01000766: 4ff06042   mov.w    r2, #-0x20000000
0100076a: 1268       ldr      r2, [r2]
0100076c: 002a       cmp      r2, #0
0100076e: fad0       beq      #0x1000766
01000770: 4ff06043   mov.w    r3, #-0x20000000
01000774: 1970       strb     r1, [r3]
01000776: 00bf       nop      
01000778: 7047       bx       lr
0100077a: 0020       movs     r0, #0
0100077c: 7047       bx       lr
0100077e: 0000       movs     r0, r0
01000780: fced00e0   ldcl     p0, c14, [ip, #0]!
01000784: 800e       lsrs     r0, r0, #0x1a
01000786: 00e0       b        #0x100078a
01000788: 70b5       push     {r4, r5, r6, lr}
0100078a: 0446       mov      r4, r0
0100078c: fff7c0fd   bl       #0x1000310
01000790: 00eb8000   add.w    r0, r0, r0, lsl #2
01000794: 4500       lsls     r5, r0, #1
01000796: 08e0       b        #0x10007aa
01000798: fff7bafd   bl       #0x1000310
0100079c: 00eb8000   add.w    r0, r0, r0, lsl #2
010007a0: 2919       adds     r1, r5, r4
010007a2: b1eb400f   cmp.w    r1, r0, lsl #1
010007a6: 00d2       bhs      #0x10007aa
010007a8: 00e0       b        #0x10007ac
010007aa: f5e7       b        #0x1000798
010007ac: 00bf       nop      
010007ae: 70bd       pop      {r4, r5, r6, pc}
010007b0: 10b5       push     {r4, lr}
010007b2: 0028       cmp      r0, #0
010007b4: 07da       bge      #0x10007c6
010007b6: ca06       lsls     r2, r1, #0x1b
010007b8: 140e       lsrs     r4, r2, #0x18
010007ba: fe4a       ldr      r2, [pc, #0x3f8]
010007bc: 00f00f03   and      r3, r0, #0xf
010007c0: 1b1f       subs     r3, r3, #4
010007c2: d454       strb     r4, [r2, r3]
010007c4: 03e0       b        #0x10007ce
010007c6: ca06       lsls     r2, r1, #0x1b
010007c8: 130e       lsrs     r3, r2, #0x18
010007ca: fb4a       ldr      r2, [pc, #0x3ec]
010007cc: 1354       strb     r3, [r2, r0]
010007ce: 10bd       pop      {r4, pc}
010007d0: 18b1       cbz      r0, #0x10007da
010007d2: 5921       movs     r1, #0x59
010007d4: f94a       ldr      r2, [pc, #0x3e4]
010007d6: 1160       str      r1, [r2]
010007d8: 02e0       b        #0x10007e0
010007da: 5d21       movs     r1, #0x5d
010007dc: f74a       ldr      r2, [pc, #0x3dc]
010007de: 1160       str      r1, [r2]
010007e0: 7047       bx       lr
010007e2: 0021       movs     r1, #0
010007e4: f64a       ldr      r2, [pc, #0x3d8]
010007e6: 1154       strb     r1, [r2, r0]
010007e8: f64a       ldr      r2, [pc, #0x3d8]
010007ea: 1154       strb     r1, [r2, r0]
010007ec: f64a       ldr      r2, [pc, #0x3d8]
010007ee: 1154       strb     r1, [r2, r0]
010007f0: 7047       bx       lr
010007f2: f34a       ldr      r2, [pc, #0x3cc]
010007f4: 115c       ldrb     r1, [r2, r0]
010007f6: c0f10702   rsb.w    r2, r0, #7
010007fa: f44b       ldr      r3, [pc, #0x3d0]
010007fc: 03eb8222   add.w    r2, r3, r2, lsl #10
01000800: 9268       ldr      r2, [r2, #8]
01000802: f34b       ldr      r3, [pc, #0x3cc]
01000804: 03eb8013   add.w    r3, r3, r0, lsl #6
01000808: 5a54       strb     r2, [r3, r1]
0100080a: 4a1c       adds     r2, r1, #1
0100080c: d1b2       uxtb     r1, r2
0100080e: 4029       cmp      r1, #0x40
01000810: 01db       blt      #0x1000816
01000812: 0022       movs     r2, #0
01000814: 00e0       b        #0x1000818
01000816: 0a46       mov      r2, r1
01000818: e94b       ldr      r3, [pc, #0x3a4]
0100081a: 1a54       strb     r2, [r3, r0]
0100081c: 7047       bx       lr
0100081e: 10b5       push     {r4, lr}
01000820: 0246       mov      r2, r0
01000822: 0b46       mov      r3, r1
01000824: 0024       movs     r4, #0
01000826: e748       ldr      r0, [pc, #0x39c]
01000828: 815c       ldrb     r1, [r0, r2]
0100082a: e548       ldr      r0, [pc, #0x394]
0100082c: 805c       ldrb     r0, [r0, r2]
0100082e: 8842       cmp      r0, r1
01000830: 01d1       bne      #0x1000836
01000832: 0020       movs     r0, #0
01000834: 10bd       pop      {r4, pc}
01000836: 0ee0       b        #0x1000856
01000838: e548       ldr      r0, [pc, #0x394]
0100083a: 00eb8210   add.w    r0, r0, r2, lsl #6
0100083e: 405c       ldrb     r0, [r0, r1]
01000840: 03f8010b   strb     r0, [r3], #1
01000844: 481c       adds     r0, r1, #1
01000846: c1b2       uxtb     r1, r0
01000848: 641c       adds     r4, r4, #1
0100084a: 4029       cmp      r1, #0x40
0100084c: 01db       blt      #0x1000852
0100084e: 0020       movs     r0, #0
01000850: 00e0       b        #0x1000854
01000852: 0846       mov      r0, r1
01000854: 0146       mov      r1, r0
01000856: da48       ldr      r0, [pc, #0x368]
01000858: 805c       ldrb     r0, [r0, r2]
0100085a: 8842       cmp      r0, r1
0100085c: ecd1       bne      #0x1000838
0100085e: d948       ldr      r0, [pc, #0x364]
01000860: 8154       strb     r1, [r0, r2]
01000862: 2046       mov      r0, r4
01000864: e6e7       b        #0x1000834
01000866: 0021       movs     r1, #0
01000868: da4a       ldr      r2, [pc, #0x368]
0100086a: 1154       strb     r1, [r2, r0]
0100086c: da4a       ldr      r2, [pc, #0x368]
0100086e: 1154       strb     r1, [r2, r0]
01000870: 7047       bx       lr
01000872: d94a       ldr      r2, [pc, #0x364]
01000874: 115c       ldrb     r1, [r2, r0]
01000876: 4a1c       adds     r2, r1, #1
01000878: d1b2       uxtb     r1, r2
0100087a: 2029       cmp      r1, #0x20
0100087c: 01db       blt      #0x1000882
0100087e: 0022       movs     r2, #0
01000880: 00e0       b        #0x1000884
01000882: 0a46       mov      r2, r1
01000884: 1146       mov      r1, r2
01000886: d44a       ldr      r2, [pc, #0x350]
01000888: 1154       strb     r1, [r2, r0]
0100088a: 7047       bx       lr
0100088c: 0146       mov      r1, r0
0100088e: d248       ldr      r0, [pc, #0x348]
01000890: 405c       ldrb     r0, [r0, r1]
01000892: d04b       ldr      r3, [pc, #0x340]
01000894: 5b5c       ldrb     r3, [r3, r1]
01000896: 9842       cmp      r0, r3
01000898: 01d1       bne      #0x100089e
0100089a: 0020       movs     r0, #0
0100089c: 7047       bx       lr
0100089e: cf48       ldr      r0, [pc, #0x33c]
010008a0: 00ebc110   add.w    r0, r0, r1, lsl #7
010008a4: cc4b       ldr      r3, [pc, #0x330]
010008a6: 5b5c       ldrb     r3, [r3, r1]
010008a8: 50f82320   ldr.w    r2, [r0, r3, lsl #2]
010008ac: 1046       mov      r0, r2
010008ae: f5e7       b        #0x100089c
010008b0: 10b5       push     {r4, lr}
010008b2: 0246       mov      r2, r0
010008b4: 0b46       mov      r3, r1
010008b6: c748       ldr      r0, [pc, #0x31c]
010008b8: 815c       ldrb     r1, [r0, r2]
010008ba: 481c       adds     r0, r1, #1
010008bc: c1b2       uxtb     r1, r0
010008be: 2029       cmp      r1, #0x20
010008c0: 01db       blt      #0x10008c6
010008c2: 0020       movs     r0, #0
010008c4: 00e0       b        #0x10008c8
010008c6: 0846       mov      r0, r1
010008c8: 0146       mov      r1, r0
010008ca: c348       ldr      r0, [pc, #0x30c]
010008cc: 805c       ldrb     r0, [r0, r2]
010008ce: 8842       cmp      r0, r1
010008d0: 01d1       bne      #0x10008d6
010008d2: 0020       movs     r0, #0
010008d4: 10bd       pop      {r4, pc}
010008d6: c148       ldr      r0, [pc, #0x304]
010008d8: 00ebc210   add.w    r0, r0, r2, lsl #7
010008dc: bd4c       ldr      r4, [pc, #0x2f4]
010008de: a45c       ldrb     r4, [r4, r2]
010008e0: 40f82430   str.w    r3, [r0, r4, lsl #2]
010008e4: bb48       ldr      r0, [pc, #0x2ec]
010008e6: 8154       strb     r1, [r0, r2]
010008e8: 0120       movs     r0, #1
010008ea: f3e7       b        #0x10008d4
010008ec: 70b5       push     {r4, r5, r6, lr}
010008ee: 0446       mov      r4, r0
010008f0: 0d46       mov      r5, r1
010008f2: 15f00e0f   tst.w    r5, #0xe
010008f6: 18d0       beq      #0x100092a
010008f8: b948       ldr      r0, [pc, #0x2e4]
010008fa: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
010008fe: 007c       ldrb     r0, [r0, #0x10]
01000900: 80b1       cbz      r0, #0x1000924
01000902: b748       ldr      r0, [pc, #0x2dc]
01000904: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000908: 007c       ldrb     r0, [r0, #0x10]
0100090a: 401e       subs     r0, r0, #1
0100090c: b449       ldr      r1, [pc, #0x2d0]
0100090e: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01000912: 0874       strb     r0, [r1, #0x10]
01000914: 0020       movs     r0, #0
01000916: b249       ldr      r1, [pc, #0x2c8]
01000918: 41f82400   str.w    r0, [r1, r4, lsl #2]
0100091c: 2046       mov      r0, r4
0100091e: fff757ff   bl       #0x10007d0
01000922: 70bd       pop      {r4, r5, r6, pc}
01000924: 2046       mov      r0, r4
01000926: fff7a4ff   bl       #0x1000872
0100092a: 012d       cmp      r5, #1
0100092c: 02d1       bne      #0x1000934
0100092e: 2046       mov      r0, r4
01000930: fff79fff   bl       #0x1000872
01000934: aa48       ldr      r0, [pc, #0x2a8]
01000936: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
0100093a: 8069       ldr      r0, [r0, #0x18]
0100093c: 28b1       cbz      r0, #0x100094a
0100093e: a848       ldr      r0, [pc, #0x2a0]
01000940: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000944: 8669       ldr      r6, [r0, #0x18]
01000946: b047       blx      r6
01000948: 00bf       nop      
0100094a: 0020       movs     r0, #0
0100094c: a449       ldr      r1, [pc, #0x290]
0100094e: 41f82400   str.w    r0, [r1, r4, lsl #2]
01000952: 2046       mov      r0, r4
01000954: fff73cff   bl       #0x10007d0
01000958: 00bf       nop      
0100095a: e2e7       b        #0x1000922
0100095c: 7047       bx       lr
0100095e: 0146       mov      r1, r0
01000960: 9f48       ldr      r0, [pc, #0x27c]
01000962: 50f82100   ldr.w    r0, [r0, r1, lsl #2]
01000966: 08b9       cbnz     r0, #0x100096c
01000968: 0020       movs     r0, #0
0100096a: 7047       bx       lr
0100096c: 0120       movs     r0, #1
0100096e: fce7       b        #0x100096a
01000970: 30b5       push     {r4, r5, lr}
01000972: 0446       mov      r4, r0
01000974: 0d46       mov      r5, r1
01000976: 2946       mov      r1, r5
01000978: 2046       mov      r0, r4
0100097a: fff799ff   bl       #0x10008b0
0100097e: 08b9       cbnz     r0, #0x1000984
01000980: 0020       movs     r0, #0
01000982: 30bd       pop      {r4, r5, pc}
01000984: 2046       mov      r0, r4
01000986: fff723ff   bl       #0x10007d0
0100098a: 0120       movs     r0, #1
0100098c: f9e7       b        #0x1000982
0100098e: 70b5       push     {r4, r5, r6, lr}
01000990: 0446       mov      r4, r0
01000992: 9348       ldr      r0, [pc, #0x24c]
01000994: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000998: 0028       cmp      r0, #0
0100099a: 6cd1       bne      #0x1000a76
0100099c: 0026       movs     r6, #0
0100099e: 0025       movs     r5, #0
010009a0: 2046       mov      r0, r4
010009a2: fff773ff   bl       #0x100088c
010009a6: 0546       mov      r5, r0
010009a8: 05b9       cbnz     r5, #0x10009ac
010009aa: 70bd       pop      {r4, r5, r6, pc}
010009ac: 687c       ldrb     r0, [r5, #0x11]
010009ae: a874       strb     r0, [r5, #0x12]
010009b0: e868       ldr      r0, [r5, #0xc]
010009b2: 6860       str      r0, [r5, #4]
010009b4: 0020       movs     r0, #0
010009b6: a860       str      r0, [r5, #8]
010009b8: 8948       ldr      r0, [pc, #0x224]
010009ba: 40f82450   str.w    r5, [r0, r4, lsl #2]
010009be: 0020       movs     r0, #0
010009c0: 8849       ldr      r1, [pc, #0x220]
010009c2: 0855       strb     r0, [r1, r4]
010009c4: 8648       ldr      r0, [pc, #0x218]
010009c6: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
010009ca: 0078       ldrb     r0, [r0]
010009cc: 00f0fe00   and      r0, r0, #0xfe
010009d0: c4f10701   rsb.w    r1, r4, #7
010009d4: 7d4a       ldr      r2, [pc, #0x1f4]
010009d6: 02eb8121   add.w    r1, r2, r1, lsl #10
010009da: 8860       str      r0, [r1, #8]
010009dc: 8048       ldr      r0, [pc, #0x200]
010009de: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
010009e2: 4078       ldrb     r0, [r0, #1]
010009e4: c0f38000   ubfx     r0, r0, #2, #1
010009e8: 30b9       cbnz     r0, #0x10009f8
010009ea: 7d48       ldr      r0, [pc, #0x1f4]
010009ec: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
010009f0: 4078       ldrb     r0, [r0, #1]
010009f2: 10f0010f   tst.w    r0, #1
010009f6: 1fd0       beq      #0x1000a38
010009f8: 17e0       b        #0x1000a2a
010009fa: 7948       ldr      r0, [pc, #0x1e4]
010009fc: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000a00: 807c       ldrb     r0, [r0, #0x12]
01000a02: 401e       subs     r0, r0, #1
01000a04: 7649       ldr      r1, [pc, #0x1d8]
01000a06: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01000a0a: 8874       strb     r0, [r1, #0x12]
01000a0c: 7448       ldr      r0, [pc, #0x1d0]
01000a0e: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000a12: 1c30       adds     r0, #0x1c
01000a14: 7249       ldr      r1, [pc, #0x1c8]
01000a16: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01000a1a: 897c       ldrb     r1, [r1, #0x12]
01000a1c: 405c       ldrb     r0, [r0, r1]
01000a1e: c4f10701   rsb.w    r1, r4, #7
01000a22: 6a4a       ldr      r2, [pc, #0x1a8]
01000a24: 02eb8121   add.w    r1, r2, r1, lsl #10
01000a28: 8860       str      r0, [r1, #8]
01000a2a: 6d48       ldr      r0, [pc, #0x1b4]
01000a2c: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000a30: 807c       ldrb     r0, [r0, #0x12]
01000a32: 0028       cmp      r0, #0
01000a34: e1d1       bne      #0x10009fa
01000a36: 18e0       b        #0x1000a6a
01000a38: 0026       movs     r6, #0
01000a3a: 0be0       b        #0x1000a54
01000a3c: 6848       ldr      r0, [pc, #0x1a0]
01000a3e: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000a42: 4069       ldr      r0, [r0, #0x14]
01000a44: 805d       ldrb     r0, [r0, r6]
01000a46: c4f10701   rsb.w    r1, r4, #7
01000a4a: 604a       ldr      r2, [pc, #0x180]
01000a4c: 02eb8121   add.w    r1, r2, r1, lsl #10
01000a50: 8860       str      r0, [r1, #8]
01000a52: 761c       adds     r6, r6, #1
01000a54: 6248       ldr      r0, [pc, #0x188]
01000a56: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000a5a: 4068       ldr      r0, [r0, #4]
01000a5c: b042       cmp      r0, r6
01000a5e: edd8       bhi      #0x1000a3c
01000a60: 0020       movs     r0, #0
01000a62: 5f49       ldr      r1, [pc, #0x17c]
01000a64: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01000a68: 4860       str      r0, [r1, #4]
01000a6a: 0120       movs     r0, #1
01000a6c: 5e49       ldr      r1, [pc, #0x178]
01000a6e: a1ebc431   sub.w    r1, r1, r4, lsl #15
01000a72: 0860       str      r0, [r1]
01000a74: 00bf       nop      
01000a76: 00bf       nop      
01000a78: 97e7       b        #0x10009aa
01000a7a: 10b9       cbnz     r0, #0x1000a82
01000a7c: 8421       movs     r1, #0x84
01000a7e: 4f4a       ldr      r2, [pc, #0x13c]
01000a80: 1160       str      r1, [r2]
01000a82: 7047       bx       lr
01000a84: 10b5       push     {r4, lr}
01000a86: 0446       mov      r4, r0
01000a88: 34e0       b        #0x1000af4
01000a8a: 5548       ldr      r0, [pc, #0x154]
01000a8c: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000a90: 0078       ldrb     r0, [r0]
01000a92: 10f0010f   tst.w    r0, #1
01000a96: 18d0       beq      #0x1000aca
01000a98: c4f10700   rsb.w    r0, r4, #7
01000a9c: 4b49       ldr      r1, [pc, #0x12c]
01000a9e: 01eb8020   add.w    r0, r1, r0, lsl #10
01000aa2: 8068       ldr      r0, [r0, #8]
01000aa4: 4e49       ldr      r1, [pc, #0x138]
01000aa6: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01000aaa: 4969       ldr      r1, [r1, #0x14]
01000aac: 4c4a       ldr      r2, [pc, #0x130]
01000aae: 52f82420   ldr.w    r2, [r2, r4, lsl #2]
01000ab2: 9268       ldr      r2, [r2, #8]
01000ab4: 8854       strb     r0, [r1, r2]
01000ab6: 4a48       ldr      r0, [pc, #0x128]
01000ab8: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000abc: 8068       ldr      r0, [r0, #8]
01000abe: 401c       adds     r0, r0, #1
01000ac0: 4749       ldr      r1, [pc, #0x11c]
01000ac2: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01000ac6: 8860       str      r0, [r1, #8]
01000ac8: 14e0       b        #0x1000af4
01000aca: 4848       ldr      r0, [pc, #0x120]
01000acc: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000ad0: 68b1       cbz      r0, #0x1000aee
01000ad2: c4f10700   rsb.w    r0, r4, #7
01000ad6: 3d4b       ldr      r3, [pc, #0xf4]
01000ad8: 03eb8020   add.w    r0, r3, r0, lsl #10
01000adc: 8068       ldr      r0, [r0, #8]
01000ade: c2b2       uxtb     r2, r0
01000ae0: 4248       ldr      r0, [pc, #0x108]
01000ae2: 10f82410   ldrb.w   r1, [r0, r4, lsl #2]
01000ae6: 2046       mov      r0, r4
01000ae8: 00f0e3fd   bl       #0x10016b2
01000aec: 02e0       b        #0x1000af4
01000aee: 2046       mov      r0, r4
01000af0: fff77ffe   bl       #0x10007f2
01000af4: c4f10700   rsb.w    r0, r4, #7
01000af8: 3449       ldr      r1, [pc, #0xd0]
01000afa: 01eb8020   add.w    r0, r1, r0, lsl #10
01000afe: 8069       ldr      r0, [r0, #0x18]
01000b00: c0f30720   ubfx     r0, r0, #8, #8
01000b04: 0028       cmp      r0, #0
01000b06: c0d1       bne      #0x1000a8a
01000b08: 3749       ldr      r1, [pc, #0xdc]
01000b0a: 1c39       subs     r1, #0x1c
01000b0c: a1ebc431   sub.w    r1, r1, r4, lsl #15
01000b10: 0860       str      r0, [r1]
01000b12: 10bd       pop      {r4, pc}
01000b14: 3648       ldr      r0, [pc, #0xd8]
01000b16: 0069       ldr      r0, [r0, #0x10]
01000b18: 20f40041   bic      r1, r0, #0x8000
01000b1c: 3448       ldr      r0, [pc, #0xd0]
01000b1e: 0161       str      r1, [r0, #0x10]
01000b20: 7047       bx       lr
01000b22: 38b5       push     {r3, r4, r5, lr}
01000b24: 0446       mov      r4, r0
01000b26: c4f10700   rsb.w    r0, r4, #7
01000b2a: 2849       ldr      r1, [pc, #0xa0]
01000b2c: 01eb8020   add.w    r0, r1, r0, lsl #10
01000b30: 0068       ldr      r0, [r0]
01000b32: 10f4007f   tst.w    r0, #0x200
01000b36: 08d0       beq      #0x1000b4a
01000b38: 2a48       ldr      r0, [pc, #0xa8]
01000b3a: 005d       ldrb     r0, [r0, r4]
01000b3c: 20f00200   bic      r0, r0, #2
01000b40: 801c       adds     r0, r0, #2
01000b42: 2849       ldr      r1, [pc, #0xa0]
01000b44: 0855       strb     r0, [r1, r4]
01000b46: fff7e5ff   bl       #0x1000b14
01000b4a: c4f10700   rsb.w    r0, r4, #7
01000b4e: 1f49       ldr      r1, [pc, #0x7c]
01000b50: 01eb8020   add.w    r0, r1, r0, lsl #10
01000b54: 4068       ldr      r0, [r0, #4]
01000b56: 10f0080f   tst.w    r0, #8
01000b5a: 73d0       beq      #0x1000c44
01000b5c: 2148       ldr      r0, [pc, #0x84]
01000b5e: 005d       ldrb     r0, [r0, r4]
01000b60: 20f00800   bic      r0, r0, #8
01000b64: 0830       adds     r0, #8
01000b66: 1f49       ldr      r1, [pc, #0x7c]
01000b68: 0855       strb     r0, [r1, r4]
01000b6a: c4f10700   rsb.w    r0, r4, #7
01000b6e: 1749       ldr      r1, [pc, #0x5c]
01000b70: 01eb8020   add.w    r0, r1, r0, lsl #10
01000b74: 4069       ldr      r0, [r0, #0x14]
01000b76: 20f00100   bic      r0, r0, #1
01000b7a: c4f10701   rsb.w    r1, r4, #7
01000b7e: 134a       ldr      r2, [pc, #0x4c]
01000b80: 02eb8121   add.w    r1, r2, r1, lsl #10
01000b84: 4861       str      r0, [r1, #0x14]
01000b86: c4f10700   rsb.w    r0, r4, #7
01000b8a: 1146       mov      r1, r2
01000b8c: 01eb8020   add.w    r0, r1, r0, lsl #10
01000b90: 4069       ldr      r0, [r0, #0x14]
01000b92: 40f00400   orr      r0, r0, #4
01000b96: c4f10701   rsb.w    r1, r4, #7
01000b9a: 02eb8121   add.w    r1, r2, r1, lsl #10
01000b9e: 4861       str      r0, [r1, #0x14]
01000ba0: c4f10700   rsb.w    r0, r4, #7
01000ba4: 1146       mov      r1, r2
01000ba6: 01eb8020   add.w    r0, r1, r0, lsl #10
01000baa: 4069       ldr      r0, [r0, #0x14]
01000bac: 20f00400   bic      r0, r0, #4
01000bb0: 20e0       b        #0x1000bf4
01000bb2: 0000       movs     r0, r0
01000bb4: 18ed00e0   ldc      p0, c14, [r8, #-0]
01000bb8: 00e4       b        #0x10003bc
01000bba: 00e0       b        #0x1000bbe
01000bbc: 00ef00e0   vhadd.s8 d14, d0, d0
01000bc0: 2800       movs     r0, r5
01000bc2: 0101       lsls     r1, r0, #4
01000bc4: 2a00       movs     r2, r5
01000bc6: 0101       lsls     r1, r0, #4
01000bc8: 2c00       movs     r4, r5
01000bca: 0101       lsls     r1, r0, #4
01000bcc: 0080       strh     r0, [r0]
01000bce: 0240       ands     r2, r0
01000bd0: 8011       asrs     r0, r0, #6
01000bd2: 0101       lsls     r1, r0, #4
01000bd4: 2400       movs     r4, r4
01000bd6: 0101       lsls     r1, r0, #4
01000bd8: 2600       movs     r6, r4
01000bda: 0101       lsls     r1, r0, #4
01000bdc: 8010       asrs     r0, r0, #2
01000bde: 0101       lsls     r1, r0, #4
01000be0: 1000       movs     r0, r2
01000be2: 0101       lsls     r1, r0, #4
01000be4: 1800       movs     r0, r3
01000be6: 0101       lsls     r1, r0, #4
01000be8: 3c80       strh     r4, [r7]
01000bea: 5342       rsbs     r3, r2, #0
01000bec: 1c00       movs     r4, r3
01000bee: 0101       lsls     r1, r0, #4
01000bf0: 009c       ldr      r4, [sp]
01000bf2: 0240       ands     r2, r0
01000bf4: c4f10701   rsb.w    r1, r4, #7
01000bf8: 02eb8121   add.w    r1, r2, r1, lsl #10
01000bfc: 4861       str      r0, [r1, #0x14]
01000bfe: c4f10700   rsb.w    r0, r4, #7
01000c02: 1146       mov      r1, r2
01000c04: 01eb8020   add.w    r0, r1, r0, lsl #10
01000c08: 4069       ldr      r0, [r0, #0x14]
01000c0a: 40f00100   orr      r0, r0, #1
01000c0e: c4f10701   rsb.w    r1, r4, #7
01000c12: 02eb8121   add.w    r1, r2, r1, lsl #10
01000c16: 4861       str      r0, [r1, #0x14]
01000c18: c4f10700   rsb.w    r0, r4, #7
01000c1c: 1146       mov      r1, r2
01000c1e: 01eb8020   add.w    r0, r1, r0, lsl #10
01000c22: 4068       ldr      r0, [r0, #4]
01000c24: 20f48040   bic      r0, r0, #0x4000
01000c28: 00f58040   add.w    r0, r0, #0x4000
01000c2c: c4f10701   rsb.w    r1, r4, #7
01000c30: 02eb8121   add.w    r1, r2, r1, lsl #10
01000c34: 4860       str      r0, [r1, #4]
01000c36: 0020       movs     r0, #0
01000c38: fe49       ldr      r1, [pc, #0x3f8]
01000c3a: a1ebc431   sub.w    r1, r1, r4, lsl #15
01000c3e: 0860       str      r0, [r1]
01000c40: 38bd       pop      {r3, r4, r5, pc}
01000c42: ffe7       b        #0x1000c44
01000c44: c4f10700   rsb.w    r0, r4, #7
01000c48: fb49       ldr      r1, [pc, #0x3ec]
01000c4a: 01eb8020   add.w    r0, r1, r0, lsl #10
01000c4e: 4068       ldr      r0, [r0, #4]
01000c50: 10f0040f   tst.w    r0, #4
01000c54: 45d0       beq      #0x1000ce2
01000c56: 0025       movs     r5, #0
01000c58: c4f10700   rsb.w    r0, r4, #7
01000c5c: 01eb8020   add.w    r0, r1, r0, lsl #10
01000c60: 0068       ldr      r0, [r0]
01000c62: 10f4004f   tst.w    r0, #0x8000
01000c66: 0dd0       beq      #0x1000c84
01000c68: c4f10700   rsb.w    r0, r4, #7
01000c6c: 01eb8020   add.w    r0, r1, r0, lsl #10
01000c70: 4068       ldr      r0, [r0, #4]
01000c72: 20f00400   bic      r0, r0, #4
01000c76: c4f10701   rsb.w    r1, r4, #7
01000c7a: ef4a       ldr      r2, [pc, #0x3bc]
01000c7c: 02eb8121   add.w    r1, r2, r1, lsl #10
01000c80: 4860       str      r0, [r1, #4]
01000c82: dde7       b        #0x1000c40
01000c84: 09e0       b        #0x1000c9a
01000c86: c4f10700   rsb.w    r0, r4, #7
01000c8a: eb49       ldr      r1, [pc, #0x3ac]
01000c8c: 01eb8020   add.w    r0, r1, r0, lsl #10
01000c90: 8068       ldr      r0, [r0, #8]
01000c92: c0b2       uxtb     r0, r0
01000c94: 0df80500   strb.w   r0, [sp, r5]
01000c98: 6d1c       adds     r5, r5, #1
01000c9a: c4f10700   rsb.w    r0, r4, #7
01000c9e: e649       ldr      r1, [pc, #0x398]
01000ca0: 01eb8020   add.w    r0, r1, r0, lsl #10
01000ca4: 8069       ldr      r0, [r0, #0x18]
01000ca6: c0f30720   ubfx     r0, r0, #8, #8
01000caa: 0028       cmp      r0, #0
01000cac: ebd1       bne      #0x1000c86
01000cae: 0098       ldr      r0, [sp]
01000cb0: 00ba       rev      r0, r0
01000cb2: e249       ldr      r1, [pc, #0x388]
01000cb4: 41f82400   str.w    r0, [r1, r4, lsl #2]
01000cb8: 0846       mov      r0, r1
01000cba: 50f82410   ldr.w    r1, [r0, r4, lsl #2]
01000cbe: 2046       mov      r0, r4
01000cc0: 00f0b2fc   bl       #0x1001628
01000cc4: c4f10700   rsb.w    r0, r4, #7
01000cc8: db49       ldr      r1, [pc, #0x36c]
01000cca: 01eb8020   add.w    r0, r1, r0, lsl #10
01000cce: 4068       ldr      r0, [r0, #4]
01000cd0: 20f00400   bic      r0, r0, #4
01000cd4: c4f10701   rsb.w    r1, r4, #7
01000cd8: d74a       ldr      r2, [pc, #0x35c]
01000cda: 02eb8121   add.w    r1, r2, r1, lsl #10
01000cde: 4860       str      r0, [r1, #4]
01000ce0: aee7       b        #0x1000c40
01000ce2: c4f10700   rsb.w    r0, r4, #7
01000ce6: d449       ldr      r1, [pc, #0x350]
01000ce8: 01eb8020   add.w    r0, r1, r0, lsl #10
01000cec: 4068       ldr      r0, [r0, #4]
01000cee: 10f0020f   tst.w    r0, #2
01000cf2: 7dd0       beq      #0x1000df0
01000cf4: c4f10700   rsb.w    r0, r4, #7
01000cf8: 01eb8020   add.w    r0, r1, r0, lsl #10
01000cfc: 4068       ldr      r0, [r0, #4]
01000cfe: 20f00200   bic      r0, r0, #2
01000d02: c4f10701   rsb.w    r1, r4, #7
01000d06: cc4a       ldr      r2, [pc, #0x330]
01000d08: 02eb8121   add.w    r1, r2, r1, lsl #10
01000d0c: 4860       str      r0, [r1, #4]
01000d0e: cc48       ldr      r0, [pc, #0x330]
01000d10: 005d       ldrb     r0, [r0, r4]
01000d12: 0028       cmp      r0, #0
01000d14: 4bd0       beq      #0x1000dae
01000d16: 34e0       b        #0x1000d82
01000d18: ca48       ldr      r0, [pc, #0x328]
01000d1a: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000d1e: 0078       ldrb     r0, [r0]
01000d20: 10f0010f   tst.w    r0, #1
01000d24: 18d0       beq      #0x1000d58
01000d26: c4f10700   rsb.w    r0, r4, #7
01000d2a: c349       ldr      r1, [pc, #0x30c]
01000d2c: 01eb8020   add.w    r0, r1, r0, lsl #10
01000d30: 8068       ldr      r0, [r0, #8]
01000d32: c449       ldr      r1, [pc, #0x310]
01000d34: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01000d38: 4969       ldr      r1, [r1, #0x14]
01000d3a: c24a       ldr      r2, [pc, #0x308]
01000d3c: 52f82420   ldr.w    r2, [r2, r4, lsl #2]
01000d40: 9268       ldr      r2, [r2, #8]
01000d42: 8854       strb     r0, [r1, r2]
01000d44: bf48       ldr      r0, [pc, #0x2fc]
01000d46: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000d4a: 8068       ldr      r0, [r0, #8]
01000d4c: 401c       adds     r0, r0, #1
01000d4e: bd49       ldr      r1, [pc, #0x2f4]
01000d50: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01000d54: 8860       str      r0, [r1, #8]
01000d56: 14e0       b        #0x1000d82
01000d58: b848       ldr      r0, [pc, #0x2e0]
01000d5a: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000d5e: 68b1       cbz      r0, #0x1000d7c
01000d60: c4f10700   rsb.w    r0, r4, #7
01000d64: b44b       ldr      r3, [pc, #0x2d0]
01000d66: 03eb8020   add.w    r0, r3, r0, lsl #10
01000d6a: 8068       ldr      r0, [r0, #8]
01000d6c: c2b2       uxtb     r2, r0
01000d6e: b348       ldr      r0, [pc, #0x2cc]
01000d70: 10f82410   ldrb.w   r1, [r0, r4, lsl #2]
01000d74: 2046       mov      r0, r4
01000d76: 00f09cfc   bl       #0x10016b2
01000d7a: 02e0       b        #0x1000d82
01000d7c: 2046       mov      r0, r4
01000d7e: fff738fd   bl       #0x10007f2
01000d82: c4f10700   rsb.w    r0, r4, #7
01000d86: ac49       ldr      r1, [pc, #0x2b0]
01000d88: 01eb8020   add.w    r0, r1, r0, lsl #10
01000d8c: 8069       ldr      r0, [r0, #0x18]
01000d8e: c0f30720   ubfx     r0, r0, #8, #8
01000d92: 0028       cmp      r0, #0
01000d94: c0d1       bne      #0x1000d18
01000d96: 2046       mov      r0, r4
01000d98: 00f0cafc   bl       #0x1001730
01000d9c: a848       ldr      r0, [pc, #0x2a0]
01000d9e: 015d       ldrb     r1, [r0, r4]
01000da0: 2046       mov      r0, r4
01000da2: fff7a3fd   bl       #0x10008ec
01000da6: 0020       movs     r0, #0
01000da8: a549       ldr      r1, [pc, #0x294]
01000daa: 0855       strb     r0, [r1, r4]
01000dac: 3fe0       b        #0x1000e2e
01000dae: c4f10700   rsb.w    r0, r4, #7
01000db2: a149       ldr      r1, [pc, #0x284]
01000db4: 01eb8020   add.w    r0, r1, r0, lsl #10
01000db8: 8069       ldr      r0, [r0, #0x18]
01000dba: 00f47f40   and      r0, r0, #0xff00
01000dbe: b0f5a06f   cmp.w    r0, #0x500
01000dc2: 02d0       beq      #0x1000dca
01000dc4: 0098       ldr      r0, [sp]
01000dc6: 401c       adds     r0, r0, #1
01000dc8: 0090       str      r0, [sp]
01000dca: 15e0       b        #0x1000df8
01000dcc: 9b48       ldr      r0, [pc, #0x26c]
01000dce: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000dd2: 70b1       cbz      r0, #0x1000df2
01000dd4: c4f10700   rsb.w    r0, r4, #7
01000dd8: 974b       ldr      r3, [pc, #0x25c]
01000dda: 03eb8020   add.w    r0, r3, r0, lsl #10
01000dde: 8068       ldr      r0, [r0, #8]
01000de0: c2b2       uxtb     r2, r0
01000de2: 9648       ldr      r0, [pc, #0x258]
01000de4: 10f82410   ldrb.w   r1, [r0, r4, lsl #2]
01000de8: 2046       mov      r0, r4
01000dea: 00f062fc   bl       #0x10016b2
01000dee: 03e0       b        #0x1000df8
01000df0: 22e0       b        #0x1000e38
01000df2: 2046       mov      r0, r4
01000df4: fff7fdfc   bl       #0x10007f2
01000df8: c4f10700   rsb.w    r0, r4, #7
01000dfc: 8e49       ldr      r1, [pc, #0x238]
01000dfe: 01eb8020   add.w    r0, r1, r0, lsl #10
01000e02: 8069       ldr      r0, [r0, #0x18]
01000e04: c0f30720   ubfx     r0, r0, #8, #8
01000e08: 0028       cmp      r0, #0
01000e0a: dfd1       bne      #0x1000dcc
01000e0c: 8b48       ldr      r0, [pc, #0x22c]
01000e0e: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000e12: 10b9       cbnz     r0, #0x1000e1a
01000e14: 2046       mov      r0, r4
01000e16: fff730fe   bl       #0x1000a7a
01000e1a: 2046       mov      r0, r4
01000e1c: 00f088fc   bl       #0x1001730
01000e20: 2046       mov      r0, r4
01000e22: fff79bfd   bl       #0x100095c
01000e26: 2046       mov      r0, r4
01000e28: fff7d2fc   bl       #0x10007d0
01000e2c: 00bf       nop      
01000e2e: 0020       movs     r0, #0
01000e30: 8249       ldr      r1, [pc, #0x208]
01000e32: 41f82400   str.w    r0, [r1, r4, lsl #2]
01000e36: 03e7       b        #0x1000c40
01000e38: c4f10700   rsb.w    r0, r4, #7
01000e3c: 7e49       ldr      r1, [pc, #0x1f8]
01000e3e: 01eb8020   add.w    r0, r1, r0, lsl #10
01000e42: 0068       ldr      r0, [r0]
01000e44: 10f4004f   tst.w    r0, #0x8000
01000e48: 7ed0       beq      #0x1000f48
01000e4a: c4f10700   rsb.w    r0, r4, #7
01000e4e: 01eb8020   add.w    r0, r1, r0, lsl #10
01000e52: 4068       ldr      r0, [r0, #4]
01000e54: 10f0800f   tst.w    r0, #0x80
01000e58: 56d0       beq      #0x1000f08
01000e5a: c4f10700   rsb.w    r0, r4, #7
01000e5e: 01eb8020   add.w    r0, r1, r0, lsl #10
01000e62: 4068       ldr      r0, [r0, #4]
01000e64: 10f0400f   tst.w    r0, #0x40
01000e68: 1fd0       beq      #0x1000eaa
01000e6a: 7548       ldr      r0, [pc, #0x1d4]
01000e6c: 005d       ldrb     r0, [r0, r4]
01000e6e: 20f00400   bic      r0, r0, #4
01000e72: 001d       adds     r0, r0, #4
01000e74: 7249       ldr      r1, [pc, #0x1c8]
01000e76: 0855       strb     r0, [r1, r4]
01000e78: c4f10700   rsb.w    r0, r4, #7
01000e7c: 6e49       ldr      r1, [pc, #0x1b8]
01000e7e: 01eb8020   add.w    r0, r1, r0, lsl #10
01000e82: 4069       ldr      r0, [r0, #0x14]
01000e84: 40f00400   orr      r0, r0, #4
01000e88: c4f10701   rsb.w    r1, r4, #7
01000e8c: 6a4a       ldr      r2, [pc, #0x1a8]
01000e8e: 02eb8121   add.w    r1, r2, r1, lsl #10
01000e92: 4861       str      r0, [r1, #0x14]
01000e94: 0020       movs     r0, #0
01000e96: 6749       ldr      r1, [pc, #0x19c]
01000e98: 1c31       adds     r1, #0x1c
01000e9a: a1ebc431   sub.w    r1, r1, r4, lsl #15
01000e9e: 0860       str      r0, [r1]
01000ea0: 6449       ldr      r1, [pc, #0x190]
01000ea2: a1ebc431   sub.w    r1, r1, r4, lsl #15
01000ea6: 0860       str      r0, [r1]
01000ea8: c1e1       b        #0x100122e
01000eaa: c4f10700   rsb.w    r0, r4, #7
01000eae: 6249       ldr      r1, [pc, #0x188]
01000eb0: 01eb8020   add.w    r0, r1, r0, lsl #10
01000eb4: 4068       ldr      r0, [r0, #4]
01000eb6: 10f0100f   tst.w    r0, #0x10
01000eba: f5d0       beq      #0x1000ea8
01000ebc: c4f10700   rsb.w    r0, r4, #7
01000ec0: 01eb8020   add.w    r0, r1, r0, lsl #10
01000ec4: 4068       ldr      r0, [r0, #4]
01000ec6: 10f4007f   tst.w    r0, #0x200
01000eca: edd0       beq      #0x1000ea8
01000ecc: 5d48       ldr      r0, [pc, #0x174]
01000ece: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000ed2: 8168       ldr      r1, [r0, #8]
01000ed4: 5b48       ldr      r0, [pc, #0x16c]
01000ed6: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000eda: 8068       ldr      r0, [r0, #8]
01000edc: 401c       adds     r0, r0, #1
01000ede: 594a       ldr      r2, [pc, #0x164]
01000ee0: 52f82420   ldr.w    r2, [r2, r4, lsl #2]
01000ee4: 9060       str      r0, [r2, #8]
01000ee6: 5748       ldr      r0, [pc, #0x15c]
01000ee8: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000eec: 4069       ldr      r0, [r0, #0x14]
01000eee: 405c       ldrb     r0, [r0, r1]
01000ef0: c4f10701   rsb.w    r1, r4, #7
01000ef4: 504a       ldr      r2, [pc, #0x140]
01000ef6: 02eb8121   add.w    r1, r2, r1, lsl #10
01000efa: 8860       str      r0, [r1, #8]
01000efc: 0020       movs     r0, #0
01000efe: 4d49       ldr      r1, [pc, #0x134]
01000f00: a1ebc431   sub.w    r1, r1, r4, lsl #15
01000f04: 0860       str      r0, [r1]
01000f06: 92e1       b        #0x100122e
01000f08: c4f10700   rsb.w    r0, r4, #7
01000f0c: 4a49       ldr      r1, [pc, #0x128]
01000f0e: 01eb8020   add.w    r0, r1, r0, lsl #10
01000f12: 4068       ldr      r0, [r0, #4]
01000f14: 10f4007f   tst.w    r0, #0x200
01000f18: 7ed0       beq      #0x1001018
01000f1a: 4a48       ldr      r0, [pc, #0x128]
01000f1c: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000f20: 4068       ldr      r0, [r0, #4]
01000f22: 0028       cmp      r0, #0
01000f24: 79d0       beq      #0x100101a
01000f26: 4748       ldr      r0, [pc, #0x11c]
01000f28: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000f2c: 4078       ldrb     r0, [r0, #1]
01000f2e: c0f38000   ubfx     r0, r0, #2, #1
01000f32: 0028       cmp      r0, #0
01000f34: 72d0       beq      #0x100101c
01000f36: 4348       ldr      r0, [pc, #0x10c]
01000f38: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000f3c: 4078       ldrb     r0, [r0, #1]
01000f3e: 10f0010f   tst.w    r0, #1
01000f42: 0cd0       beq      #0x1000f5e
01000f44: 3f48       ldr      r0, [pc, #0xfc]
01000f46: 00e0       b        #0x1000f4a
01000f48: 52e1       b        #0x10011f0
01000f4a: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000f4e: 0078       ldrb     r0, [r0]
01000f50: c4f10701   rsb.w    r1, r4, #7
01000f54: 384a       ldr      r2, [pc, #0xe0]
01000f56: 02eb8121   add.w    r1, r2, r1, lsl #10
01000f5a: 8860       str      r0, [r1, #8]
01000f5c: 0be0       b        #0x1000f76
01000f5e: 3948       ldr      r0, [pc, #0xe4]
01000f60: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000f64: 0078       ldrb     r0, [r0]
01000f66: 00f0fe00   and      r0, r0, #0xfe
01000f6a: c4f10701   rsb.w    r1, r4, #7
01000f6e: 324a       ldr      r2, [pc, #0xc8]
01000f70: 02eb8121   add.w    r1, r2, r1, lsl #10
01000f74: 8860       str      r0, [r1, #8]
01000f76: 3348       ldr      r0, [pc, #0xcc]
01000f78: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000f7c: 4068       ldr      r0, [r0, #4]
01000f7e: 4028       cmp      r0, #0x40
01000f80: 2cd2       bhs      #0x1000fdc
01000f82: 20e0       b        #0x1000fc6
01000f84: 2f48       ldr      r0, [pc, #0xbc]
01000f86: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000f8a: 8168       ldr      r1, [r0, #8]
01000f8c: 2d48       ldr      r0, [pc, #0xb4]
01000f8e: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000f92: 8068       ldr      r0, [r0, #8]
01000f94: 401c       adds     r0, r0, #1
01000f96: 2b4a       ldr      r2, [pc, #0xac]
01000f98: 52f82420   ldr.w    r2, [r2, r4, lsl #2]
01000f9c: 9060       str      r0, [r2, #8]
01000f9e: 2948       ldr      r0, [pc, #0xa4]
01000fa0: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000fa4: 4069       ldr      r0, [r0, #0x14]
01000fa6: 405c       ldrb     r0, [r0, r1]
01000fa8: c4f10701   rsb.w    r1, r4, #7
01000fac: 224a       ldr      r2, [pc, #0x88]
01000fae: 02eb8121   add.w    r1, r2, r1, lsl #10
01000fb2: 8860       str      r0, [r1, #8]
01000fb4: 2348       ldr      r0, [pc, #0x8c]
01000fb6: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000fba: 4068       ldr      r0, [r0, #4]
01000fbc: 401e       subs     r0, r0, #1
01000fbe: 2149       ldr      r1, [pc, #0x84]
01000fc0: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01000fc4: 4860       str      r0, [r1, #4]
01000fc6: 1f48       ldr      r0, [pc, #0x7c]
01000fc8: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01000fcc: 4068       ldr      r0, [r0, #4]
01000fce: 0028       cmp      r0, #0
01000fd0: d8d1       bne      #0x1000f84
01000fd2: 1c49       ldr      r1, [pc, #0x70]
01000fd4: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01000fd8: 8860       str      r0, [r1, #8]
01000fda: 2ae0       b        #0x1001032
01000fdc: 0020       movs     r0, #0
01000fde: 25e0       b        #0x100102c
01000fe0: 1849       ldr      r1, [pc, #0x60]
01000fe2: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01000fe6: 8a68       ldr      r2, [r1, #8]
01000fe8: 1649       ldr      r1, [pc, #0x58]
01000fea: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01000fee: 8968       ldr      r1, [r1, #8]
01000ff0: 491c       adds     r1, r1, #1
01000ff2: 144b       ldr      r3, [pc, #0x50]
01000ff4: 53f82430   ldr.w    r3, [r3, r4, lsl #2]
01000ff8: 9960       str      r1, [r3, #8]
01000ffa: 1249       ldr      r1, [pc, #0x48]
01000ffc: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01001000: 4969       ldr      r1, [r1, #0x14]
01001002: 895c       ldrb     r1, [r1, r2]
01001004: c4f10702   rsb.w    r2, r4, #7
01001008: 0b4b       ldr      r3, [pc, #0x2c]
0100100a: 03eb8222   add.w    r2, r3, r2, lsl #10
0100100e: 9160       str      r1, [r2, #8]
01001010: 0c49       ldr      r1, [pc, #0x30]
01001012: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01001016: 02e0       b        #0x100101e
01001018: dae0       b        #0x10011d0
0100101a: 96e0       b        #0x100114a
0100101c: 2ae0       b        #0x1001074
0100101e: 4968       ldr      r1, [r1, #4]
01001020: 491e       subs     r1, r1, #1
01001022: 084a       ldr      r2, [pc, #0x20]
01001024: 52f82420   ldr.w    r2, [r2, r4, lsl #2]
01001028: 5160       str      r1, [r2, #4]
0100102a: 401c       adds     r0, r0, #1
0100102c: 4028       cmp      r0, #0x40
0100102e: d7db       blt      #0x1000fe0
01001030: 00bf       nop      
01001032: 09e0       b        #0x1001048
01001034: 2080       strh     r0, [r4]
01001036: 5342       rsbs     r3, r2, #0
01001038: 0080       strh     r0, [r0]
0100103a: 0240       ands     r2, r0
0100103c: 1c00       movs     r4, r3
0100103e: 0101       lsls     r1, r0, #4
01001040: 1800       movs     r0, r3
01001042: 0101       lsls     r1, r0, #4
01001044: 1000       movs     r0, r2
01001046: 0101       lsls     r1, r0, #4
01001048: fe48       ldr      r0, [pc, #0x3f8]
0100104a: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
0100104e: 4078       ldrb     r0, [r0, #1]
01001050: 20f00400   bic      r0, r0, #4
01001054: fb49       ldr      r1, [pc, #0x3ec]
01001056: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
0100105a: 4870       strb     r0, [r1, #1]
0100105c: 0120       movs     r0, #1
0100105e: fa49       ldr      r1, [pc, #0x3e8]
01001060: a1ebc431   sub.w    r1, r1, r4, lsl #15
01001064: 0860       str      r0, [r1]
01001066: 0020       movs     r0, #0
01001068: f749       ldr      r1, [pc, #0x3dc]
0100106a: 1839       subs     r1, #0x18
0100106c: a1ebc431   sub.w    r1, r1, r4, lsl #15
01001070: 0860       str      r0, [r1]
01001072: dce0       b        #0x100122e
01001074: f348       ldr      r0, [pc, #0x3cc]
01001076: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
0100107a: 4068       ldr      r0, [r0, #4]
0100107c: 4028       cmp      r0, #0x40
0100107e: 2cd2       bhs      #0x10010da
01001080: 20e0       b        #0x10010c4
01001082: f048       ldr      r0, [pc, #0x3c0]
01001084: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01001088: 8168       ldr      r1, [r0, #8]
0100108a: ee48       ldr      r0, [pc, #0x3b8]
0100108c: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01001090: 8068       ldr      r0, [r0, #8]
01001092: 401c       adds     r0, r0, #1
01001094: eb4a       ldr      r2, [pc, #0x3ac]
01001096: 52f82420   ldr.w    r2, [r2, r4, lsl #2]
0100109a: 9060       str      r0, [r2, #8]
0100109c: e948       ldr      r0, [pc, #0x3a4]
0100109e: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
010010a2: 4069       ldr      r0, [r0, #0x14]
010010a4: 405c       ldrb     r0, [r0, r1]
010010a6: c4f10701   rsb.w    r1, r4, #7
010010aa: e84a       ldr      r2, [pc, #0x3a0]
010010ac: 02eb8121   add.w    r1, r2, r1, lsl #10
010010b0: 8860       str      r0, [r1, #8]
010010b2: e448       ldr      r0, [pc, #0x390]
010010b4: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
010010b8: 4068       ldr      r0, [r0, #4]
010010ba: 401e       subs     r0, r0, #1
010010bc: e149       ldr      r1, [pc, #0x384]
010010be: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
010010c2: 4860       str      r0, [r1, #4]
010010c4: df48       ldr      r0, [pc, #0x37c]
010010c6: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
010010ca: 4068       ldr      r0, [r0, #4]
010010cc: 0028       cmp      r0, #0
010010ce: d8d1       bne      #0x1001082
010010d0: dc49       ldr      r1, [pc, #0x370]
010010d2: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
010010d6: 8860       str      r0, [r1, #8]
010010d8: 26e0       b        #0x1001128
010010da: 0020       movs     r0, #0
010010dc: 21e0       b        #0x1001122
010010de: d949       ldr      r1, [pc, #0x364]
010010e0: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
010010e4: 8a68       ldr      r2, [r1, #8]
010010e6: d749       ldr      r1, [pc, #0x35c]
010010e8: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
010010ec: 8968       ldr      r1, [r1, #8]
010010ee: 491c       adds     r1, r1, #1
010010f0: d44b       ldr      r3, [pc, #0x350]
010010f2: 53f82430   ldr.w    r3, [r3, r4, lsl #2]
010010f6: 9960       str      r1, [r3, #8]
010010f8: d249       ldr      r1, [pc, #0x348]
010010fa: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
010010fe: 4969       ldr      r1, [r1, #0x14]
01001100: 895c       ldrb     r1, [r1, r2]
01001102: c4f10702   rsb.w    r2, r4, #7
01001106: d14b       ldr      r3, [pc, #0x344]
01001108: 03eb8222   add.w    r2, r3, r2, lsl #10
0100110c: 9160       str      r1, [r2, #8]
0100110e: cd49       ldr      r1, [pc, #0x334]
01001110: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
01001114: 4968       ldr      r1, [r1, #4]
01001116: 491e       subs     r1, r1, #1
01001118: ca4a       ldr      r2, [pc, #0x328]
0100111a: 52f82420   ldr.w    r2, [r2, r4, lsl #2]
0100111e: 5160       str      r1, [r2, #4]
01001120: 401c       adds     r0, r0, #1
01001122: 4028       cmp      r0, #0x40
01001124: dbdb       blt      #0x10010de
01001126: 00bf       nop      
01001128: c648       ldr      r0, [pc, #0x318]
0100112a: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
0100112e: 4078       ldrb     r0, [r0, #1]
01001130: 20f00400   bic      r0, r0, #4
01001134: c349       ldr      r1, [pc, #0x30c]
01001136: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
0100113a: 4870       strb     r0, [r1, #1]
0100113c: 0020       movs     r0, #0
0100113e: c249       ldr      r1, [pc, #0x308]
01001140: 1839       subs     r1, #0x18
01001142: a1ebc431   sub.w    r1, r1, r4, lsl #15
01001146: 0860       str      r0, [r1]
01001148: 71e0       b        #0x100122e
0100114a: be48       ldr      r0, [pc, #0x2f8]
0100114c: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
01001150: 4078       ldrb     r0, [r0, #1]
01001152: c0f38000   ubfx     r0, r0, #2, #1
01001156: 18b3       cbz      r0, #0x10011a0
01001158: ba48       ldr      r0, [pc, #0x2e8]
0100115a: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
0100115e: 4078       ldrb     r0, [r0, #1]
01001160: 20f00400   bic      r0, r0, #4
01001164: b749       ldr      r1, [pc, #0x2dc]
01001166: 51f82410   ldr.w    r1, [r1, r4, lsl #2]
0100116a: 4870       strb     r0, [r1, #1]
0100116c: 0120       movs     r0, #1
0100116e: b649       ldr      r1, [pc, #0x2d8]
01001170: a1ebc431   sub.w    r1, r1, r4, lsl #15
01001174: 0860       str      r0, [r1]
01001176: c4f10700   rsb.w    r0, r4, #7
0100117a: b449       ldr      r1, [pc, #0x2d0]
0100117c: 01eb8020   add.w    r0, r1, r0, lsl #10
01001180: 4068       ldr      r0, [r0, #4]
01001182: 20f00400   bic      r0, r0, #4
01001186: c4f10701   rsb.w    r1, r4, #7
0100118a: b04a       ldr      r2, [pc, #0x2c0]
0100118c: 02eb8121   add.w    r1, r2, r1, lsl #10
01001190: 4860       str      r0, [r1, #4]
01001192: 0020       movs     r0, #0
01001194: ac49       ldr      r1, [pc, #0x2b0]
01001196: 1839       subs     r1, #0x18
01001198: a1ebc431   sub.w    r1, r1, r4, lsl #15
0100119c: 0860       str      r0, [r1]
0100119e: 46e0       b        #0x100122e
010011a0: a848       ldr      r0, [pc, #0x2a0]
010011a2: 50f82400   ldr.w    r0, [r0, r4, lsl #2]
010011a6: 4068       ldr      r0, [r0, #4]
010011a8: 30b9       cbnz     r0, #0x10011b8
010011aa: a948       ldr      r0, [pc, #0x2a4]
010011ac: 005d       ldrb     r0, [r0, r4]
010011ae: 20f00100   bic      r0, r0, #1
010011b2: 401c       adds     r0, r0, #1
010011b4: a649       ldr      r1, [pc, #0x298]
010011b6: 0855       strb     r0, [r1, r4]
010011b8: 0020       movs     r0, #0
010011ba: a349       ldr      r1, [pc, #0x28c]
010011bc: 091d       adds     r1, r1, #4
010011be: a1ebc431   sub.w    r1, r1, r4, lsl #15
010011c2: 0860       str      r0, [r1]
010011c4: a049       ldr      r1, [pc, #0x280]
010011c6: 1839       subs     r1, #0x18
010011c8: a1ebc431   sub.w    r1, r1, r4, lsl #15
010011cc: 0860       str      r0, [r1]
010011ce: 2ee0       b        #0x100122e
010011d0: c4f10700   rsb.w    r0, r4, #7
010011d4: 9d49       ldr      r1, [pc, #0x274]
010011d6: 01eb8020   add.w    r0, r1, r0, lsl #10
010011da: 4068       ldr      r0, [r0, #4]
010011dc: 10f0100f   tst.w    r0, #0x10
010011e0: 25d0       beq      #0x100122e
010011e2: 0020       movs     r0, #0
010011e4: 9849       ldr      r1, [pc, #0x260]
010011e6: 1839       subs     r1, #0x18
010011e8: a1ebc431   sub.w    r1, r1, r4, lsl #15
010011ec: 0860       str      r0, [r1]
010011ee: 1ee0       b        #0x100122e
010011f0: c4f10700   rsb.w    r0, r4, #7
010011f4: 9549       ldr      r1, [pc, #0x254]
010011f6: 01eb8020   add.w    r0, r1, r0, lsl #10
010011fa: 4068       ldr      r0, [r0, #4]
010011fc: 10f0100f   tst.w    r0, #0x10
01001200: 0fd0       beq      #0x1001222
01001202: 2046       mov      r0, r4
01001204: 00f0bdfa   bl       #0x1001782
01001208: 0120       movs     r0, #1
0100120a: 8f49       ldr      r1, [pc, #0x23c]
0100120c: 091f       subs     r1, r1, #4
0100120e: a1ebc431   sub.w    r1, r1, r4, lsl #15
01001212: 0860       str      r0, [r1]
01001214: 0020       movs     r0, #0
01001216: 8c49       ldr      r1, [pc, #0x230]
01001218: 1839       subs     r1, #0x18
0100121a: a1ebc431   sub.w    r1, r1, r4, lsl #15
0100121e: 0860       str      r0, [r1]
01001220: 05e0       b        #0x100122e
01001222: 0020       movs     r0, #0
01001224: 8849       ldr      r1, [pc, #0x220]
01001226: 1839       subs     r1, #0x18
01001228: a1ebc431   sub.w    r1, r1, r4, lsl #15
0100122c: 0860       str      r0, [r1]
0100122e: 00bf       nop      
01001230: 06e5       b        #0x1000c40
01001232: 10b5       push     {r4, lr}
01001234: 0020       movs     r0, #0
01001236: fff774fc   bl       #0x1000b22
0100123a: 10bd       pop      {r4, pc}
0100123c: 00b5       push     {lr}
0100123e: 0020       movs     r0, #0
01001240: fff7a5fb   bl       #0x100098e
01001244: 00bd       pop      {pc}
01001246: 10b5       push     {r4, lr}
01001248: 0020       movs     r0, #0
0100124a: fff71bfc   bl       #0x1000a84
0100124e: 10bd       pop      {r4, pc}
01001250: 10b5       push     {r4, lr}
01001252: 8048       ldr      r0, [pc, #0x200]
01001254: 0069       ldr      r0, [r0, #0x10]
01001256: 20f40041   bic      r1, r0, #0x8000
0100125a: 7e48       ldr      r0, [pc, #0x1f8]
0100125c: 0161       str      r1, [r0, #0x10]
0100125e: 0121       movs     r1, #1
01001260: 0165       str      r1, [r0, #0x50]
01001262: 4069       ldr      r0, [r0, #0x14]
01001264: 20f00101   bic      r1, r0, #1
01001268: 7a48       ldr      r0, [pc, #0x1e8]
0100126a: 4161       str      r1, [r0, #0x14]
0100126c: 4069       ldr      r0, [r0, #0x14]
0100126e: 40f00401   orr      r1, r0, #4
01001272: 7848       ldr      r0, [pc, #0x1e0]
01001274: 4161       str      r1, [r0, #0x14]
01001276: 4069       ldr      r0, [r0, #0x14]
01001278: 20f00401   bic      r1, r0, #4
0100127c: 7548       ldr      r0, [pc, #0x1d4]
0100127e: 4161       str      r1, [r0, #0x14]
01001280: 4069       ldr      r0, [r0, #0x14]
01001282: 40f00101   orr      r1, r0, #1
01001286: 7348       ldr      r0, [pc, #0x1cc]
01001288: 4161       str      r1, [r0, #0x14]
0100128a: 4068       ldr      r0, [r0, #4]
0100128c: 20f48040   bic      r0, r0, #0x4000
01001290: 00f58040   add.w    r0, r0, #0x4000
01001294: 6f49       ldr      r1, [pc, #0x1bc]
01001296: 4860       str      r0, [r1, #4]
01001298: 0846       mov      r0, r1
0100129a: 0069       ldr      r0, [r0, #0x10]
0100129c: 20f40040   bic      r0, r0, #0x8000
010012a0: 00f50040   add.w    r0, r0, #0x8000
010012a4: 0861       str      r0, [r1, #0x10]
010012a6: 0221       movs     r1, #2
010012a8: 0020       movs     r0, #0
010012aa: fff71ffb   bl       #0x10008ec
010012ae: 10bd       pop      {r4, pc}
010012b0: 00b5       push     {lr}
010012b2: 6949       ldr      r1, [pc, #0x1a4]
010012b4: 0020       movs     r0, #0
010012b6: fff7b2fa   bl       #0x100081e
010012ba: 00bd       pop      {pc}
010012bc: 00b5       push     {lr}
010012be: 6649       ldr      r1, [pc, #0x198]
010012c0: 0120       movs     r0, #1
010012c2: fff7acfa   bl       #0x100081e
010012c6: 00bd       pop      {pc}
010012c8: 10b5       push     {r4, lr}
010012ca: 0120       movs     r0, #1
010012cc: fff729fc   bl       #0x1000b22
010012d0: 10bd       pop      {r4, pc}
010012d2: 00b5       push     {lr}
010012d4: 0120       movs     r0, #1
010012d6: fff75afb   bl       #0x100098e
010012da: 00bd       pop      {pc}
010012dc: 10b5       push     {r4, lr}
010012de: 0120       movs     r0, #1
010012e0: fff7d0fb   bl       #0x1000a84
010012e4: 10bd       pop      {r4, pc}
010012e6: 10b5       push     {r4, lr}
010012e8: 5c48       ldr      r0, [pc, #0x170]
010012ea: 0069       ldr      r0, [r0, #0x10]
010012ec: 20f40041   bic      r1, r0, #0x8000
010012f0: 5a48       ldr      r0, [pc, #0x168]
010012f2: 0161       str      r1, [r0, #0x10]
010012f4: 0121       movs     r1, #1
010012f6: 0165       str      r1, [r0, #0x50]
010012f8: 4069       ldr      r0, [r0, #0x14]
010012fa: 20f00101   bic      r1, r0, #1
010012fe: 5748       ldr      r0, [pc, #0x15c]
01001300: 4161       str      r1, [r0, #0x14]
01001302: 4069       ldr      r0, [r0, #0x14]
01001304: 40f00401   orr      r1, r0, #4
01001308: 5448       ldr      r0, [pc, #0x150]
0100130a: 4161       str      r1, [r0, #0x14]
0100130c: 4069       ldr      r0, [r0, #0x14]
0100130e: 20f00401   bic      r1, r0, #4
01001312: 5248       ldr      r0, [pc, #0x148]
01001314: 4161       str      r1, [r0, #0x14]
01001316: 4069       ldr      r0, [r0, #0x14]
01001318: 40f00101   orr      r1, r0, #1
0100131c: 4f48       ldr      r0, [pc, #0x13c]
0100131e: 4161       str      r1, [r0, #0x14]
01001320: 4068       ldr      r0, [r0, #4]
01001322: 20f48040   bic      r0, r0, #0x4000
01001326: 00f58040   add.w    r0, r0, #0x4000
0100132a: 4c49       ldr      r1, [pc, #0x130]
0100132c: 4860       str      r0, [r1, #4]
0100132e: 0846       mov      r0, r1
01001330: 0069       ldr      r0, [r0, #0x10]
01001332: 20f40040   bic      r0, r0, #0x8000
01001336: 00f50040   add.w    r0, r0, #0x8000
0100133a: 0861       str      r0, [r1, #0x10]
0100133c: 0221       movs     r1, #2
0100133e: 0120       movs     r0, #1
01001340: fff7d4fa   bl       #0x10008ec
01001344: 10bd       pop      {r4, pc}
01001346: 70b5       push     {r4, r5, r6, lr}
01001348: 0446       mov      r4, r0
0100134a: 0d46       mov      r5, r1
0100134c: c4f10700   rsb.w    r0, r4, #7
01001350: 3e49       ldr      r1, [pc, #0xf8]
01001352: 01eb8020   add.w    r0, r1, r0, lsl #10
01001356: 4249       ldr      r1, [pc, #0x108]
01001358: 0968       ldr      r1, [r1]
0100135a: 0160       str      r1, [r0]
0100135c: c4f10700   rsb.w    r0, r4, #7
01001360: 3a49       ldr      r1, [pc, #0xe8]
01001362: 01eb8020   add.w    r0, r1, r0, lsl #10
01001366: 3f49       ldr      r1, [pc, #0xfc]
01001368: 0968       ldr      r1, [r1]
0100136a: c160       str      r1, [r0, #0xc]
0100136c: 4ff68070   movw     r0, #0xff80
01001370: 40ea5500   orr.w    r0, r0, r5, lsr #1
01001374: c4f10701   rsb.w    r1, r4, #7
01001378: 344a       ldr      r2, [pc, #0xd0]
0100137a: 02eb8121   add.w    r1, r2, r1, lsl #10
0100137e: 0861       str      r0, [r1, #0x10]
01001380: c4f10700   rsb.w    r0, r4, #7
01001384: 1146       mov      r1, r2
01001386: 01eb8020   add.w    r0, r1, r0, lsl #10
0100138a: 3749       ldr      r1, [pc, #0xdc]
0100138c: 0968       ldr      r1, [r1]
0100138e: 4161       str      r1, [r0, #0x14]
01001390: 4ff48040   mov.w    r0, #0x4000
01001394: c4f10701   rsb.w    r1, r4, #7
01001398: 02eb8121   add.w    r1, r2, r1, lsl #10
0100139c: 8861       str      r0, [r1, #0x18]
0100139e: 2046       mov      r0, r4
010013a0: fff761fa   bl       #0x1000866
010013a4: 2046       mov      r0, r4
010013a6: fff71cfa   bl       #0x10007e2
010013aa: c4f10700   rsb.w    r0, r4, #7
010013ae: 2749       ldr      r1, [pc, #0x9c]
010013b0: 01eb8020   add.w    r0, r1, r0, lsl #10
010013b4: 006b       ldr      r0, [r0, #0x30]
010013b6: 20f0f000   bic      r0, r0, #0xf0
010013ba: 3030       adds     r0, #0x30
010013bc: c4f10701   rsb.w    r1, r4, #7
010013c0: 224a       ldr      r2, [pc, #0x88]
010013c2: 02eb8121   add.w    r1, r2, r1, lsl #10
010013c6: 0863       str      r0, [r1, #0x30]
010013c8: c4f10700   rsb.w    r0, r4, #7
010013cc: 1146       mov      r1, r2
010013ce: 01eb8020   add.w    r0, r1, r0, lsl #10
010013d2: 006b       ldr      r0, [r0, #0x30]
010013d4: 20f00f00   bic      r0, r0, #0xf
010013d8: c4f10701   rsb.w    r1, r4, #7
010013dc: 02eb8121   add.w    r1, r2, r1, lsl #10
010013e0: 0863       str      r0, [r1, #0x30]
010013e2: 2249       ldr      r1, [pc, #0x88]
010013e4: c4f10700   rsb.w    r0, r4, #7
010013e8: 02eb8020   add.w    r0, r2, r0, lsl #10
010013ec: 4164       str      r1, [r0, #0x44]
010013ee: c4f10700   rsb.w    r0, r4, #7
010013f2: 1146       mov      r1, r2
010013f4: 01eb8020   add.w    r0, r1, r0, lsl #10
010013f8: 006c       ldr      r0, [r0, #0x40]
010013fa: 20f00100   bic      r0, r0, #1
010013fe: 401c       adds     r0, r0, #1
01001400: c4f10701   rsb.w    r1, r4, #7
01001404: 02eb8121   add.w    r1, r2, r1, lsl #10
01001408: 0864       str      r0, [r1, #0x40]
0100140a: c4f10700   rsb.w    r0, r4, #7
0100140e: 1146       mov      r1, r2
01001410: 01eb8020   add.w    r0, r1, r0, lsl #10
01001414: 006c       ldr      r0, [r0, #0x40]
01001416: 20f01000   bic      r0, r0, #0x10
0100141a: 1030       adds     r0, #0x10
0100141c: c4f10701   rsb.w    r1, r4, #7
01001420: 02eb8121   add.w    r1, r2, r1, lsl #10
01001424: 0864       str      r0, [r1, #0x40]
01001426: 0020       movs     r0, #0
01001428: c4f10701   rsb.w    r1, r4, #7
0100142c: 02eb8121   add.w    r1, r2, r1, lsl #10
01001430: c1f8a000   str.w    r0, [r1, #0xa0]
01001434: 49f69601   movw     r1, #0x9896
01001438: c4f10700   rsb.w    r0, r4, #7
0100143c: 02eb8020   add.w    r0, r2, r0, lsl #10
01001440: 16e0       b        #0x1001470
01001442: 0000       movs     r0, r0
01001444: 1000       movs     r0, r2
01001446: 0101       lsls     r1, r0, #4
01001448: 3880       strh     r0, [r7]
0100144a: 5342       rsbs     r3, r2, #0
0100144c: 0080       strh     r0, [r0]
0100144e: 0240       ands     r2, r0
01001450: 1800       movs     r0, r3
01001452: 0101       lsls     r1, r0, #4
01001454: 009c       ldr      r4, [sp]
01001456: 0240       ands     r2, r0
01001458: 0012       asrs     r0, r0, #8
0100145a: 0101       lsls     r1, r0, #4
0100145c: 0098       ldr      r0, [sp]
0100145e: 0240       ands     r2, r0
01001460: 3829       cmp      r1, #0x38
01001462: 0001       lsls     r0, r0, #4
01001464: 3c29       cmp      r1, #0x3c
01001466: 0001       lsls     r0, r0, #4
01001468: 4029       cmp      r1, #0x40
0100146a: 0001       lsls     r0, r0, #4
0100146c: 2d31       adds     r1, #0x2d
0100146e: 0100       movs     r1, r0
01001470: c0f8a410   str.w    r1, [r0, #0xa4]
01001474: 0020       movs     r0, #0
01001476: c4f10701   rsb.w    r1, r4, #7
0100147a: 02eb8121   add.w    r1, r2, r1, lsl #10
0100147e: c1f8b000   str.w    r0, [r1, #0xb0]
01001482: 49f69601   movw     r1, #0x9896
01001486: c4f10700   rsb.w    r0, r4, #7
0100148a: 02eb8020   add.w    r0, r2, r0, lsl #10
0100148e: c0f8b410   str.w    r1, [r0, #0xb4]
01001492: e4b1       cbz      r4, #0x10014ce
01001494: 0321       movs     r1, #3
01001496: 5a20       movs     r0, #0x5a
01001498: fff78af9   bl       #0x10007b0
0100149c: 0321       movs     r1, #3
0100149e: 5920       movs     r0, #0x59
010014a0: fff786f9   bl       #0x10007b0
010014a4: 0321       movs     r1, #3
010014a6: 5820       movs     r0, #0x58
010014a8: fff782f9   bl       #0x10007b0
010014ac: 0321       movs     r1, #3
010014ae: 5b20       movs     r0, #0x5b
010014b0: fff77ef9   bl       #0x10007b0
010014b4: 5a20       movs     r0, #0x5a
010014b6: 00f035f8   bl       #0x1001524
010014ba: 5920       movs     r0, #0x59
010014bc: 00f032f8   bl       #0x1001524
010014c0: 5820       movs     r0, #0x58
010014c2: 00f02ff8   bl       #0x1001524
010014c6: 5b20       movs     r0, #0x5b
010014c8: 00f02cf8   bl       #0x1001524
010014cc: 22e0       b        #0x1001514
010014ce: 0321       movs     r1, #3
010014d0: 5e20       movs     r0, #0x5e
010014d2: fff76df9   bl       #0x10007b0
010014d6: 0321       movs     r1, #3
010014d8: 5d20       movs     r0, #0x5d
010014da: fff769f9   bl       #0x10007b0
010014de: 0321       movs     r1, #3
010014e0: 5c20       movs     r0, #0x5c
010014e2: fff765f9   bl       #0x10007b0
010014e6: 0321       movs     r1, #3
010014e8: 5f20       movs     r0, #0x5f
010014ea: fff761f9   bl       #0x10007b0
010014ee: 0421       movs     r1, #4
010014f0: 8420       movs     r0, #0x84
010014f2: fff75df9   bl       #0x10007b0
010014f6: 5e20       movs     r0, #0x5e
010014f8: 00f014f8   bl       #0x1001524
010014fc: 5d20       movs     r0, #0x5d
010014fe: 00f011f8   bl       #0x1001524
01001502: 5c20       movs     r0, #0x5c
01001504: 00f00ef8   bl       #0x1001524
01001508: 5f20       movs     r0, #0x5f
0100150a: 00f00bf8   bl       #0x1001524
0100150e: 8420       movs     r0, #0x84
01001510: 00f008f8   bl       #0x1001524
01001514: 0020       movs     r0, #0
01001516: 0949       ldr      r1, [pc, #0x24]
01001518: 41f82400   str.w    r0, [r1, r4, lsl #2]
0100151c: 0849       ldr      r1, [pc, #0x20]
0100151e: 41f82400   str.w    r0, [r1, r4, lsl #2]
01001522: 70bd       pop      {r4, r5, r6, pc}
01001524: 00f01f02   and      r2, r0, #0x1f
01001528: 0121       movs     r1, #1
0100152a: 9140       lsls     r1, r2
0100152c: 4209       lsrs     r2, r0, #5
0100152e: 4ff0e023   mov.w    r3, #-0x1fff2000
01001532: 03eb8202   add.w    r2, r3, r2, lsl #2
01001536: c2f80011   str.w    r1, [r2, #0x100]
0100153a: 7047       bx       lr
0100153c: 1c00       movs     r4, r3
0100153e: 0101       lsls     r1, r0, #4
01001540: 1000       movs     r0, r2
01001542: 0101       lsls     r1, r0, #4
01001544: 38b5       push     {r3, r4, r5, lr}
01001546: 0446       mov      r4, r0
01001548: 2078       ldrb     r0, [r4]
0100154a: 0b28       cmp      r0, #0xb
0100154c: 62d2       bhs      #0x1001614
0100154e: dfe800f0   tbb      [pc, r0]
01001552: 0607       lsls     r6, r0, #0x1c
01001554: 1c1d       adds     r4, r3, #4
01001556: 2361       str      r3, [r4, #0x10]
01001558: 6161       str      r1, [r4, #0x14]
0100155a: 6161       str      r1, [r4, #0x14]
0100155c: 4900       lsls     r1, r1, #1
0100155e: 5ae0       b        #0x1001616
01001560: 6178       ldrb     r1, [r4, #1]
01001562: bdf80000   ldrh.w   r0, [sp]
01001566: 61f30300   bfi      r0, r1, #0, #4
0100156a: 0090       str      r0, [sp]
0100156c: a178       ldrb     r1, [r4, #2]
0100156e: bdf80000   ldrh.w   r0, [sp]
01001572: 61f30710   bfi      r0, r1, #4, #4
01001576: 0090       str      r0, [sp]
01001578: e078       ldrb     r0, [r4, #3]
0100157a: 40f08000   orr      r0, r0, #0x80
0100157e: 8df80100   strb.w   r0, [sp, #1]
01001582: 0098       ldr      r0, [sp]
01001584: fff76cf8   bl       #0x1000660
01001588: 45e0       b        #0x1001616
0100158a: 44e0       b        #0x1001616
0100158c: a078       ldrb     r0, [r4, #2]
0100158e: 6178       ldrb     r1, [r4, #1]
01001590: 904a       ldr      r2, [pc, #0x240]
01001592: 42f82100   str.w    r0, [r2, r1, lsl #2]
01001596: 3ee0       b        #0x1001616
01001598: a078       ldrb     r0, [r4, #2]
0100159a: 88b1       cbz      r0, #0x10015c0
0100159c: 8e48       ldr      r0, [pc, #0x238]
0100159e: 0068       ldr      r0, [r0]
010015a0: 6278       ldrb     r2, [r4, #1]
010015a2: 0121       movs     r1, #1
010015a4: 9140       lsls     r1, r2
010015a6: 0843       orrs     r0, r1
010015a8: 8b49       ldr      r1, [pc, #0x22c]
010015aa: 0860       str      r0, [r1]
010015ac: 081f       subs     r0, r1, #4
010015ae: 0068       ldr      r0, [r0]
010015b0: 6278       ldrb     r2, [r4, #1]
010015b2: 0121       movs     r1, #1
010015b4: 9140       lsls     r1, r2
010015b6: 0843       orrs     r0, r1
010015b8: 8749       ldr      r1, [pc, #0x21c]
010015ba: 091f       subs     r1, r1, #4
010015bc: 0860       str      r0, [r1]
010015be: 10e0       b        #0x10015e2
010015c0: 8548       ldr      r0, [pc, #0x214]
010015c2: 0068       ldr      r0, [r0]
010015c4: 6278       ldrb     r2, [r4, #1]
010015c6: 0121       movs     r1, #1
010015c8: 9140       lsls     r1, r2
010015ca: 8843       bics     r0, r1
010015cc: 8249       ldr      r1, [pc, #0x208]
010015ce: 0860       str      r0, [r1]
010015d0: 081f       subs     r0, r1, #4
010015d2: 0068       ldr      r0, [r0]
010015d4: 6278       ldrb     r2, [r4, #1]
010015d6: 0121       movs     r1, #1
010015d8: 9140       lsls     r1, r2
010015da: 8843       bics     r0, r1
010015dc: 7e49       ldr      r1, [pc, #0x1f8]
010015de: 091f       subs     r1, r1, #4
010015e0: 0860       str      r0, [r1]
010015e2: 18e0       b        #0x1001616
010015e4: a078       ldrb     r0, [r4, #2]
010015e6: 50b1       cbz      r0, #0x10015fe
010015e8: 7b48       ldr      r0, [pc, #0x1ec]
010015ea: 001f       subs     r0, r0, #4
010015ec: 0068       ldr      r0, [r0]
010015ee: 6278       ldrb     r2, [r4, #1]
010015f0: 0121       movs     r1, #1
010015f2: 9140       lsls     r1, r2
010015f4: 0843       orrs     r0, r1
010015f6: 7849       ldr      r1, [pc, #0x1e0]
010015f8: 091f       subs     r1, r1, #4
010015fa: 0860       str      r0, [r1]
010015fc: 09e0       b        #0x1001612
010015fe: 7648       ldr      r0, [pc, #0x1d8]
01001600: 001f       subs     r0, r0, #4
01001602: 0068       ldr      r0, [r0]
01001604: 6278       ldrb     r2, [r4, #1]
01001606: 0121       movs     r1, #1
01001608: 9140       lsls     r1, r2
0100160a: 8843       bics     r0, r1
0100160c: 7249       ldr      r1, [pc, #0x1c8]
0100160e: 091f       subs     r1, r1, #4
01001610: 0860       str      r0, [r1]
01001612: 00e0       b        #0x1001616
01001614: 00bf       nop      
01001616: 00bf       nop      
01001618: 38bd       pop      {r3, r4, r5, pc}
0100161a: 0168       ldr      r1, [r0]
0100161c: 09ba       rev      r1, r1
0100161e: 21f07f41   bic      r1, r1, #0xff000000
01001622: 6e4a       ldr      r2, [pc, #0x1b8]
01001624: 1160       str      r1, [r2]
01001626: 7047       bx       lr
01001628: 10b5       push     {r4, lr}
0100162a: 00ebc002   add.w    r2, r0, r0, lsl #3
0100162e: 6c4b       ldr      r3, [pc, #0x1b0]
01001630: 03eb8202   add.w    r2, r3, r2, lsl #2
01001634: 5160       str      r1, [r2, #4]
01001636: 6b4b       ldr      r3, [pc, #0x1ac]
01001638: ca1a       subs     r2, r1, r3
0100163a: 9942       cmp      r1, r3
0100163c: 14d0       beq      #0x1001668
0100163e: 06dc       bgt      #0x100164e
01001640: 6ff00062   mvn      r2, #0x8000000
01001644: 8a18       adds     r2, r1, r2
01001646: 09d0       beq      #0x100165c
01001648: 012a       cmp      r2, #1
0100164a: 12d1       bne      #0x1001672
0100164c: 07e0       b        #0x100165e
0100164e: fd2a       cmp      r2, #0xfd
01001650: 06d0       beq      #0x1001660
01001652: a2f54072   sub.w    r2, r2, #0x300
01001656: fd3a       subs     r2, #0xfd
01001658: 0bd1       bne      #0x1001672
0100165a: 06e0       b        #0x100166a
0100165c: 00bf       nop      
0100165e: 00bf       nop      
01001660: 0022       movs     r2, #0
01001662: 614b       ldr      r3, [pc, #0x184]
01001664: 1a70       strb     r2, [r3]
01001666: 22e0       b        #0x10016ae
01001668: 21e0       b        #0x10016ae
0100166a: 0022       movs     r2, #0
0100166c: 5f4b       ldr      r3, [pc, #0x17c]
0100166e: 1a70       strb     r2, [r3]
01001670: 1de0       b        #0x10016ae
01001672: 00ebc002   add.w    r2, r0, r0, lsl #3
01001676: 5a4b       ldr      r3, [pc, #0x168]
01001678: 03eb8202   add.w    r2, r3, r2, lsl #2
0100167c: 5268       ldr      r2, [r2, #4]
0100167e: 00ebc003   add.w    r3, r0, r0, lsl #3
01001682: 574c       ldr      r4, [pc, #0x15c]
01001684: 04eb8303   add.w    r3, r4, r3, lsl #2
01001688: da61       str      r2, [r3, #0x1c]
0100168a: 00ebc002   add.w    r2, r0, r0, lsl #3
0100168e: 2346       mov      r3, r4
01001690: 03eb8202   add.w    r2, r3, r2, lsl #2
01001694: d269       ldr      r2, [r2, #0x1c]
01001696: 564b       ldr      r3, [pc, #0x158]
01001698: 1a60       str      r2, [r3]
0100169a: 1a46       mov      r2, r3
0100169c: 1268       ldr      r2, [r2]
0100169e: 1268       ldr      r2, [r2]
010016a0: 12ba       rev      r2, r2
010016a2: 544b       ldr      r3, [pc, #0x150]
010016a4: 1a60       str      r2, [r3]
010016a6: 1a46       mov      r2, r3
010016a8: 534b       ldr      r3, [pc, #0x14c]
010016aa: 1a60       str      r2, [r3]
010016ac: 00bf       nop      
010016ae: 00bf       nop      
010016b0: 10bd       pop      {r4, pc}
010016b2: 70b5       push     {r4, r5, r6, lr}
010016b4: 0b46       mov      r3, r1
010016b6: 00ebc001   add.w    r1, r0, r0, lsl #3
010016ba: 494c       ldr      r4, [pc, #0x124]
010016bc: 04eb8101   add.w    r1, r4, r1, lsl #2
010016c0: 4c68       ldr      r4, [r1, #4]
010016c2: 484d       ldr      r5, [pc, #0x120]
010016c4: 611b       subs     r1, r4, r5
010016c6: ac42       cmp      r4, r5
010016c8: 10d0       beq      #0x10016ec
010016ca: 06dc       bgt      #0x10016da
010016cc: 6ff00061   mvn      r1, #0x8000000
010016d0: 6118       adds     r1, r4, r1
010016d2: 09d0       beq      #0x10016e8
010016d4: 0129       cmp      r1, #1
010016d6: 1ad1       bne      #0x100170e
010016d8: 07e0       b        #0x10016ea
010016da: fd29       cmp      r1, #0xfd
010016dc: 07d0       beq      #0x10016ee
010016de: a1f54071   sub.w    r1, r1, #0x300
010016e2: fd39       subs     r1, #0xfd
010016e4: 13d1       bne      #0x100170e
010016e6: 0ae0       b        #0x10016fe
010016e8: 00bf       nop      
010016ea: 00bf       nop      
010016ec: 1ee0       b        #0x100172c
010016ee: 3e4c       ldr      r4, [pc, #0xf8]
010016f0: 2178       ldrb     r1, [r4]
010016f2: 4c1c       adds     r4, r1, #1
010016f4: 3c4d       ldr      r5, [pc, #0xf0]
010016f6: 2c70       strb     r4, [r5]
010016f8: 404c       ldr      r4, [pc, #0x100]
010016fa: 6254       strb     r2, [r4, r1]
010016fc: 16e0       b        #0x100172c
010016fe: 3b4c       ldr      r4, [pc, #0xec]
01001700: 2178       ldrb     r1, [r4]
01001702: 4c1c       adds     r4, r1, #1
01001704: 394d       ldr      r5, [pc, #0xe4]
01001706: 2c70       strb     r4, [r5]
01001708: 3d4c       ldr      r4, [pc, #0xf4]
0100170a: 6254       strb     r2, [r4, r1]
0100170c: 0ee0       b        #0x100172c
0100170e: 00ebc004   add.w    r4, r0, r0, lsl #3
01001712: 334d       ldr      r5, [pc, #0xcc]
01001714: 05eb8404   add.w    r4, r5, r4, lsl #2
01001718: e169       ldr      r1, [r4, #0x1c]
0100171a: 4c1c       adds     r4, r1, #1
0100171c: 00ebc005   add.w    r5, r0, r0, lsl #3
01001720: 2f4e       ldr      r6, [pc, #0xbc]
01001722: 06eb8505   add.w    r5, r6, r5, lsl #2
01001726: ec61       str      r4, [r5, #0x1c]
01001728: 0a70       strb     r2, [r1]
0100172a: 00bf       nop      
0100172c: 00bf       nop      
0100172e: 70bd       pop      {r4, r5, r6, pc}
01001730: 10b5       push     {r4, lr}
01001732: 0446       mov      r4, r0
01001734: 04ebc400   add.w    r0, r4, r4, lsl #3
01001738: 2949       ldr      r1, [pc, #0xa4]
0100173a: 01eb8000   add.w    r0, r1, r0, lsl #2
0100173e: 4168       ldr      r1, [r0, #4]
01001740: 284a       ldr      r2, [pc, #0xa0]
01001742: 881a       subs     r0, r1, r2
01001744: 9142       cmp      r1, r2
01001746: 10d0       beq      #0x100176a
01001748: 06dc       bgt      #0x1001758
0100174a: 6ff00060   mvn      r0, #0x8000000
0100174e: 0818       adds     r0, r1, r0
01001750: 09d0       beq      #0x1001766
01001752: 0128       cmp      r0, #1
01001754: 12d1       bne      #0x100177c
01001756: 07e0       b        #0x1001768
01001758: fd28       cmp      r0, #0xfd
0100175a: 07d0       beq      #0x100176c
0100175c: a0f54070   sub.w    r0, r0, #0x300
01001760: fd38       subs     r0, #0xfd
01001762: 0bd1       bne      #0x100177c
01001764: 06e0       b        #0x1001774
01001766: 00bf       nop      
01001768: 00bf       nop      
0100176a: 08e0       b        #0x100177e
0100176c: 2348       ldr      r0, [pc, #0x8c]
0100176e: fff7e9fe   bl       #0x1001544
01001772: 04e0       b        #0x100177e
01001774: 2248       ldr      r0, [pc, #0x88]
01001776: fff750ff   bl       #0x100161a
0100177a: 00e0       b        #0x100177e
0100177c: 00bf       nop      
0100177e: 00bf       nop      
01001780: 10bd       pop      {r4, pc}
01001782: 00ebc001   add.w    r1, r0, r0, lsl #3
01001786: 164a       ldr      r2, [pc, #0x58]
01001788: 02eb8101   add.w    r1, r2, r1, lsl #2
0100178c: 4968       ldr      r1, [r1, #4]
0100178e: 6ff00062   mvn      r2, #0x8000000
01001792: 8918       adds     r1, r1, r2
01001794: 08d0       beq      #0x10017a8
01001796: 0129       cmp      r1, #1
01001798: 07d0       beq      #0x10017aa
0100179a: 0229       cmp      r1, #2
0100179c: 06d0       beq      #0x10017ac
0100179e: a1f54071   sub.w    r1, r1, #0x300
010017a2: ff39       subs     r1, #0xff
010017a4: 04d1       bne      #0x10017b0
010017a6: 02e0       b        #0x10017ae
010017a8: 00bf       nop      
010017aa: 00bf       nop      
010017ac: 0fe0       b        #0x10017ce
010017ae: 0ee0       b        #0x10017ce
010017b0: 1149       ldr      r1, [pc, #0x44]
010017b2: 0968       ldr      r1, [r1]
010017b4: 0978       ldrb     r1, [r1]
010017b6: c0f10702   rsb.w    r2, r0, #7
010017ba: 124b       ldr      r3, [pc, #0x48]
010017bc: 03eb8222   add.w    r2, r3, r2, lsl #10
010017c0: 9160       str      r1, [r2, #8]
010017c2: 0d49       ldr      r1, [pc, #0x34]
010017c4: 0968       ldr      r1, [r1]
010017c6: 491c       adds     r1, r1, #1
010017c8: 0b4a       ldr      r2, [pc, #0x2c]
010017ca: 1160       str      r1, [r2]
010017cc: 00bf       nop      
010017ce: 00bf       nop      
010017d0: 7047       bx       lr
010017d2: 0000       movs     r0, r0
010017d4: 000c       lsrs     r0, r0, #0x10
010017d6: 0340       ands     r3, r0
010017d8: fcdf       svc      #0xfc
010017da: 0240       ands     r2, r0
010017dc: 0010       asrs     r0, r0, #0x20
010017de: 0240       ands     r2, r0
010017e0: 4012       asrs     r0, r0, #9
010017e2: 0101       lsls     r1, r0, #4
010017e4: 0300       movs     r3, r0
010017e6: 0008       lsrs     r0, r0, #0x20
010017e8: 3000       movs     r0, r6
010017ea: 0101       lsls     r1, r0, #4
010017ec: 3100       movs     r1, r6
010017ee: 0101       lsls     r1, r0, #4
010017f0: 3800       movs     r0, r7
010017f2: 0101       lsls     r1, r0, #4
010017f4: 3400       movs     r4, r6
010017f6: 0101       lsls     r1, r0, #4
010017f8: 3c00       movs     r4, r7
010017fa: 0101       lsls     r1, r0, #4
010017fc: 8812       asrs     r0, r1, #0xa
010017fe: 0101       lsls     r1, r0, #4
01001800: 9812       asrs     r0, r3, #0xa
01001802: 0101       lsls     r1, r0, #4
01001804: 0080       strh     r0, [r0]
01001806: 0240       ands     r2, r0
01001808: 0020       movs     r0, #0
0100180a: 3e49       ldr      r1, [pc, #0xf8]
0100180c: 0860       str      r0, [r1]
0100180e: 7047       bx       lr
01001810: 10b5       push     {r4, lr}
01001812: 88b0       sub      sp, #0x20
01001814: 0446       mov      r4, r0
01001816: d021       movs     r1, #0xd0
01001818: 0020       movs     r0, #0
0100181a: fff794fd   bl       #0x1001346
0100181e: 00bf       nop      
01001820: 0020       movs     r0, #0
01001822: fff79cf8   bl       #0x100095e
01001826: 0028       cmp      r0, #0
01001828: fad1       bne      #0x1001820
0100182a: 00bf       nop      
0100182c: 3548       ldr      r0, [pc, #0xd4]
0100182e: 0068       ldr      r0, [r0]
01001830: 0028       cmp      r0, #0
01001832: fbd1       bne      #0x100182c
01001834: 0120       movs     r0, #1
01001836: 3349       ldr      r1, [pc, #0xcc]
01001838: 0860       str      r0, [r1]
0100183a: d020       movs     r0, #0xd0
0100183c: 8df80000   strb.w   r0, [sp]
01001840: 4ff08070   mov.w    r0, #0x1000000
01001844: 0790       str      r0, [sp, #0x1c]
01001846: 3049       ldr      r1, [pc, #0xc0]
01001848: a068       ldr      r0, [r4, #8]
0100184a: 0844       add      r0, r1
0100184c: 0590       str      r0, [sp, #0x14]
0100184e: e068       ldr      r0, [r4, #0xc]
01001850: 0390       str      r0, [sp, #0xc]
01001852: 0420       movs     r0, #4
01001854: 8df81100   strb.w   r0, [sp, #0x11]
01001858: 9df80100   ldrb.w   r0, [sp, #1]
0100185c: 20f00100   bic      r0, r0, #1
01001860: 401c       adds     r0, r0, #1
01001862: 8df80100   strb.w   r0, [sp, #1]
01001866: 9df80100   ldrb.w   r0, [sp, #1]
0100186a: 20f00400   bic      r0, r0, #4
0100186e: 001d       adds     r0, r0, #4
01001870: 8df80100   strb.w   r0, [sp, #1]
01001874: 0320       movs     r0, #3
01001876: 8df81000   strb.w   r0, [sp, #0x10]
0100187a: 2448       ldr      r0, [pc, #0x90]
0100187c: 0690       str      r0, [sp, #0x18]
0100187e: 6946       mov      r1, sp
01001880: 0020       movs     r0, #0
01001882: fff775f8   bl       #0x1000970
01001886: 00bf       nop      
01001888: 0020       movs     r0, #0
0100188a: fff768f8   bl       #0x100095e
0100188e: 0028       cmp      r0, #0
01001890: fad1       bne      #0x1001888
01001892: 00bf       nop      
01001894: 1b48       ldr      r0, [pc, #0x6c]
01001896: 0068       ldr      r0, [r0]
01001898: 0028       cmp      r0, #0
0100189a: fbd1       bne      #0x1001894
0100189c: 0120       movs     r0, #1
0100189e: 1949       ldr      r1, [pc, #0x64]
010018a0: 0860       str      r0, [r1]
010018a2: d020       movs     r0, #0xd0
010018a4: 8df80000   strb.w   r0, [sp]
010018a8: 4ff00060   mov.w    r0, #0x8000000
010018ac: 0790       str      r0, [sp, #0x1c]
010018ae: 1848       ldr      r0, [pc, #0x60]
010018b0: 0590       str      r0, [sp, #0x14]
010018b2: 0420       movs     r0, #4
010018b4: 0390       str      r0, [sp, #0xc]
010018b6: 8df81100   strb.w   r0, [sp, #0x11]
010018ba: 9df80100   ldrb.w   r0, [sp, #1]
010018be: 20f00100   bic      r0, r0, #1
010018c2: 401c       adds     r0, r0, #1
010018c4: 8df80100   strb.w   r0, [sp, #1]
010018c8: 9df80100   ldrb.w   r0, [sp, #1]
010018cc: 20f00400   bic      r0, r0, #4
010018d0: 001d       adds     r0, r0, #4
010018d2: 8df80100   strb.w   r0, [sp, #1]
010018d6: 0320       movs     r0, #3
010018d8: 8df81000   strb.w   r0, [sp, #0x10]
010018dc: 0b48       ldr      r0, [pc, #0x2c]
010018de: 0690       str      r0, [sp, #0x18]
010018e0: 6946       mov      r1, sp
010018e2: 0020       movs     r0, #0
010018e4: fff744f8   bl       #0x1000970
010018e8: 00bf       nop      
010018ea: 0020       movs     r0, #0
010018ec: fff737f8   bl       #0x100095e
010018f0: 0028       cmp      r0, #0
010018f2: fad1       bne      #0x10018ea
010018f4: 00bf       nop      
010018f6: 0348       ldr      r0, [pc, #0xc]
010018f8: 0068       ldr      r0, [r0]
010018fa: 0028       cmp      r0, #0
010018fc: fbd1       bne      #0x10018f6
010018fe: 08b0       add      sp, #0x20
01001900: 10bd       pop      {r4, pc}
01001902: 0000       movs     r0, r0
01001904: 4000       lsls     r0, r0, #1
01001906: 0101       lsls     r1, r0, #4
01001908: 0080       strh     r0, [r0]
0100190a: 0003       lsls     r0, r0, #0xc
0100190c: 0918       adds     r1, r1, r0
0100190e: 0001       lsls     r0, r0, #4
01001910: 4429       cmp      r1, #0x44
01001912: 0001       lsls     r0, r0, #4
01001914: 10b5       push     {r4, lr}
01001916: 0028       cmp      r0, #0
01001918: 07da       bge      #0x100192a
0100191a: ca06       lsls     r2, r1, #0x1b
0100191c: 140e       lsrs     r4, r2, #0x18
0100191e: 984a       ldr      r2, [pc, #0x260]
01001920: 00f00f03   and      r3, r0, #0xf
01001924: 1b1f       subs     r3, r3, #4
01001926: d454       strb     r4, [r2, r3]
01001928: 03e0       b        #0x1001932
0100192a: ca06       lsls     r2, r1, #0x1b
0100192c: 130e       lsrs     r3, r2, #0x18
0100192e: 954a       ldr      r2, [pc, #0x254]
01001930: 1354       strb     r3, [r2, r0]
01001932: 10bd       pop      {r4, pc}
01001934: 9448       ldr      r0, [pc, #0x250]
01001936: 0068       ldr      r0, [r0]
01001938: 20f00400   bic      r0, r0, #4
0100193c: 9349       ldr      r1, [pc, #0x24c]
0100193e: c1f88002   str.w    r0, [r1, #0x280]
01001942: 9348       ldr      r0, [pc, #0x24c]
01001944: 0068       ldr      r0, [r0]
01001946: 20f00401   bic      r1, r0, #4
0100194a: 9148       ldr      r0, [pc, #0x244]
0100194c: 0160       str      r1, [r0]
0100194e: 4ff00100   mov.w    r0, #1
01001952: 9049       ldr      r1, [pc, #0x240]
01001954: 0860       str      r0, [r1]
01001956: 7047       bx       lr
01001958: 0020       movs     r0, #0
0100195a: 8f49       ldr      r1, [pc, #0x23c]
0100195c: 0860       str      r0, [r1]
0100195e: 8f48       ldr      r0, [pc, #0x23c]
01001960: 0068       ldr      r0, [r0]
01001962: 48b1       cbz      r0, #0x1001978
01001964: 8a48       ldr      r0, [pc, #0x228]
01001966: 0068       ldr      r0, [r0]
01001968: 40f00801   orr      r1, r0, #8
0100196c: 8848       ldr      r0, [pc, #0x220]
0100196e: 0160       str      r1, [r0]
01001970: 4ff00000   mov.w    r0, #0
01001974: 8949       ldr      r1, [pc, #0x224]
01001976: 0860       str      r0, [r1]
01001978: 7047       bx       lr
0100197a: 00bf       nop      
0100197c: 864a       ldr      r2, [pc, #0x218]
0100197e: 1268       ldr      r2, [r2]
01001980: 012a       cmp      r2, #1
01001982: fbd0       beq      #0x100197c
01001984: 824a       ldr      r2, [pc, #0x208]
01001986: 1268       ldr      r2, [r2]
01001988: 42f00403   orr      r3, r2, #4
0100198c: 804a       ldr      r2, [pc, #0x200]
0100198e: 1360       str      r3, [r2]
01001990: 00bf       nop      
01001992: 804a       ldr      r2, [pc, #0x200]
01001994: 1268       ldr      r2, [r2]
01001996: 002a       cmp      r2, #0
01001998: fbd0       beq      #0x1001992
0100199a: 4ff00002   mov.w    r2, #0
0100199e: 7d4b       ldr      r3, [pc, #0x1f4]
010019a0: 1a60       str      r2, [r3]
010019a2: 7f4a       ldr      r2, [pc, #0x1fc]
010019a4: 1160       str      r1, [r2]
010019a6: 7f4a       ldr      r2, [pc, #0x1fc]
010019a8: 1060       str      r0, [r2]
010019aa: 7f4a       ldr      r2, [pc, #0x1fc]
010019ac: 1368       ldr      r3, [r2]
010019ae: 7f4a       ldr      r2, [pc, #0x1fc]
010019b0: 1360       str      r3, [r2]
010019b2: 00bf       nop      
010019b4: 7e4a       ldr      r2, [pc, #0x1f8]
010019b6: 1268       ldr      r2, [r2]
010019b8: 012a       cmp      r2, #1
010019ba: fbd0       beq      #0x10019b4
010019bc: 0122       movs     r2, #1
010019be: 764b       ldr      r3, [pc, #0x1d8]
010019c0: 1a60       str      r2, [r3]
010019c2: 7a4a       ldr      r2, [pc, #0x1e8]
010019c4: 1268       ldr      r2, [r2]
010019c6: 42f04043   orr      r3, r2, #0xc0000000
010019ca: 784a       ldr      r2, [pc, #0x1e0]
010019cc: 1360       str      r3, [r2]
010019ce: 7047       bx       lr
010019d0: 6f48       ldr      r0, [pc, #0x1bc]
010019d2: 0068       ldr      r0, [r0]
010019d4: 20f00801   bic      r1, r0, #8
010019d8: 6d48       ldr      r0, [pc, #0x1b4]
010019da: 0160       str      r1, [r0]
010019dc: 00bf       nop      
010019de: 7448       ldr      r0, [pc, #0x1d0]
010019e0: 0068       ldr      r0, [r0]
010019e2: 0028       cmp      r0, #0
010019e4: fbd1       bne      #0x10019de
010019e6: 6c48       ldr      r0, [pc, #0x1b0]
010019e8: 0068       ldr      r0, [r0]
010019ea: 18b1       cbz      r0, #0x10019f4
010019ec: 0120       movs     r0, #1
010019ee: 6b49       ldr      r1, [pc, #0x1ac]
010019f0: 0860       str      r0, [r1]
010019f2: 7047       bx       lr
010019f4: 6448       ldr      r0, [pc, #0x190]
010019f6: 0068       ldr      r0, [r0]
010019f8: 20f00800   bic      r0, r0, #8
010019fc: 6349       ldr      r1, [pc, #0x18c]
010019fe: c1f88002   str.w    r0, [r1, #0x280]
01001a02: 4ff00100   mov.w    r0, #1
01001a06: 6a49       ldr      r1, [pc, #0x1a8]
01001a08: 0860       str      r0, [r1]
01001a0a: 6048       ldr      r0, [pc, #0x180]
01001a0c: 006a       ldr      r0, [r0, #0x20]
01001a0e: 40f04040   orr      r0, r0, #0xc0000000
01001a12: 5e49       ldr      r1, [pc, #0x178]
01001a14: 0862       str      r0, [r1, #0x20]
01001a16: 00bf       nop      
01001a18: ebe7       b        #0x10019f2
01001a1a: 0020       movs     r0, #0
01001a1c: 6449       ldr      r1, [pc, #0x190]
01001a1e: 0860       str      r0, [r1]
01001a20: 5a48       ldr      r0, [pc, #0x168]
01001a22: 4069       ldr      r0, [r0, #0x14]
01001a24: 6349       ldr      r1, [pc, #0x18c]
01001a26: 0968       ldr      r1, [r1]
01001a28: 0844       add      r0, r1
01001a2a: 6249       ldr      r1, [pc, #0x188]
01001a2c: 0860       str      r0, [r1]
01001a2e: 5748       ldr      r0, [pc, #0x15c]
01001a30: c069       ldr      r0, [r0, #0x1c]
01001a32: 6149       ldr      r1, [pc, #0x184]
01001a34: 0968       ldr      r1, [r1]
01001a36: 0844       add      r0, r1
01001a38: 5449       ldr      r1, [pc, #0x150]
01001a3a: c861       str      r0, [r1, #0x1c]
01001a3c: 0846       mov      r0, r1
01001a3e: 406a       ldr      r0, [r0, #0x24]
01001a40: 496a       ldr      r1, [r1, #0x24]
01001a42: 0843       orrs     r0, r1
01001a44: 5149       ldr      r1, [pc, #0x144]
01001a46: 4862       str      r0, [r1, #0x24]
01001a48: 5148       ldr      r0, [pc, #0x144]
01001a4a: 0068       ldr      r0, [r0]
01001a4c: 40f00801   orr      r1, r0, #8
01001a50: 4f48       ldr      r0, [pc, #0x13c]
01001a52: 0160       str      r1, [r0]
01001a54: 7047       bx       lr
01001a56: 584a       ldr      r2, [pc, #0x160]
01001a58: 1160       str      r1, [r2]
01001a5a: 0022       movs     r2, #0
01001a5c: 554b       ldr      r3, [pc, #0x154]
01001a5e: 1a60       str      r2, [r3]
01001a60: 4ff40072   mov.w    r2, #0x200
01001a64: 494b       ldr      r3, [pc, #0x124]
01001a66: 5a61       str      r2, [r3, #0x14]
01001a68: 1a46       mov      r2, r3
01001a6a: d061       str      r0, [r2, #0x1c]
01001a6c: 534a       ldr      r2, [pc, #0x14c]
01001a6e: 1268       ldr      r2, [r2]
01001a70: 1a62       str      r2, [r3, #0x20]
01001a72: 474a       ldr      r2, [pc, #0x11c]
01001a74: 1268       ldr      r2, [r2]
01001a76: 42f00803   orr      r3, r2, #8
01001a7a: 454a       ldr      r2, [pc, #0x114]
01001a7c: 1360       str      r3, [r2]
01001a7e: 7047       bx       lr
01001a80: 10b5       push     {r4, lr}
01001a82: 0421       movs     r1, #4
01001a84: 2620       movs     r0, #0x26
01001a86: fff745ff   bl       #0x1001914
01001a8a: 2620       movs     r0, #0x26
01001a8c: 00f06bf8   bl       #0x1001b66
01001a90: 0421       movs     r1, #4
01001a92: 8d20       movs     r0, #0x8d
01001a94: fff73eff   bl       #0x1001914
01001a98: 8d20       movs     r0, #0x8d
01001a9a: 00f064f8   bl       #0x1001b66
01001a9e: 0821       movs     r1, #8
01001aa0: 2720       movs     r0, #0x27
01001aa2: fff737ff   bl       #0x1001914
01001aa6: 2720       movs     r0, #0x27
01001aa8: 00f05df8   bl       #0x1001b66
01001aac: 0421       movs     r1, #4
01001aae: 8c20       movs     r0, #0x8c
01001ab0: fff730ff   bl       #0x1001914
01001ab4: 8c20       movs     r0, #0x8c
01001ab6: 00f056f8   bl       #0x1001b66
01001aba: 10bd       pop      {r4, pc}
01001abc: 10b5       push     {r4, lr}
01001abe: 0020       movs     r0, #0
01001ac0: 03e0       b        #0x1001aca
01001ac2: 0021       movs     r1, #0
01001ac4: 3e4a       ldr      r2, [pc, #0xf8]
01001ac6: 1154       strb     r1, [r2, r0]
01001ac8: 401c       adds     r0, r0, #1
01001aca: b0f5007f   cmp.w    r0, #0x200
01001ace: f8db       blt      #0x1001ac2
01001ad0: 00f0e0fb   bl       #0x1002294
01001ad4: 00f0c3f9   bl       #0x1001e5e
01001ad8: 00f0d4fb   bl       #0x1002284
01001adc: fff7d0ff   bl       #0x1001a80
01001ae0: 0021       movs     r1, #0
01001ae2: 3748       ldr      r0, [pc, #0xdc]
01001ae4: fff7b7ff   bl       #0x1001a56
01001ae8: 10bd       pop      {r4, pc}
01001aea: 70b5       push     {r4, r5, r6, lr}
01001aec: 0546       mov      r5, r0
01001aee: 4022       movs     r2, #0x40
01001af0: 2946       mov      r1, r5
01001af2: 3448       ldr      r0, [pc, #0xd0]
01001af4: 00f010fc   bl       #0x1002318
01001af8: 0a20       movs     r0, #0xa
01001afa: fef745fe   bl       #0x1000788
01001afe: 00f01df9   bl       #0x1001d3c
01001b02: 0a20       movs     r0, #0xa
01001b04: fef740fe   bl       #0x1000788
01001b08: 4021       movs     r1, #0x40
01001b0a: 2e48       ldr      r0, [pc, #0xb8]
01001b0c: fff735ff   bl       #0x100197a
01001b10: 00bf       nop      
01001b12: 2b48       ldr      r0, [pc, #0xac]
01001b14: 0078       ldrb     r0, [r0]
01001b16: 0028       cmp      r0, #0
01001b18: fbd0       beq      #0x1001b12
01001b1a: 2948       ldr      r0, [pc, #0xa4]
01001b1c: 0078       ldrb     r0, [r0]
01001b1e: 1028       cmp      r0, #0x10
01001b20: 01d0       beq      #0x1001b26
01001b22: 00bf       nop      
01001b24: fee7       b        #0x1001b24
01001b26: 0020       movs     r0, #0
01001b28: 2549       ldr      r1, [pc, #0x94]
01001b2a: 0870       strb     r0, [r1]
01001b2c: 0024       movs     r4, #0
01001b2e: 08e0       b        #0x1001b42
01001b30: 2449       ldr      r1, [pc, #0x90]
01001b32: 896b       ldr      r1, [r1, #0x38]
01001b34: 0819       adds     r0, r1, r4
01001b36: 4ff40071   mov.w    r1, #0x200
01001b3a: fff71eff   bl       #0x100197a
01001b3e: 04f50074   add.w    r4, r4, #0x200
01001b42: 2048       ldr      r0, [pc, #0x80]
01001b44: c06b       ldr      r0, [r0, #0x3c]
01001b46: a042       cmp      r0, r4
01001b48: f2d8       bhi      #0x1001b30
01001b4a: 00bf       nop      
01001b4c: 1c48       ldr      r0, [pc, #0x70]
01001b4e: 0078       ldrb     r0, [r0]
01001b50: 0028       cmp      r0, #0
01001b52: fbd0       beq      #0x1001b4c
01001b54: 1a48       ldr      r0, [pc, #0x68]
01001b56: 0078       ldrb     r0, [r0]
01001b58: 2028       cmp      r0, #0x20
01001b5a: 01d0       beq      #0x1001b60
01001b5c: 00bf       nop      
01001b5e: fee7       b        #0x1001b5e
01001b60: 00f098fb   bl       #0x1002294
01001b64: 70bd       pop      {r4, r5, r6, pc}
01001b66: 00f01f02   and      r2, r0, #0x1f
01001b6a: 0121       movs     r1, #1
01001b6c: 9140       lsls     r1, r2
01001b6e: 4209       lsrs     r2, r0, #5
01001b70: 4ff0e023   mov.w    r3, #-0x1fff2000
01001b74: 03eb8202   add.w    r2, r3, r2, lsl #2
01001b78: c2f80011   str.w    r1, [r2, #0x100]
01001b7c: 7047       bx       lr
01001b7e: 0000       movs     r0, r0
01001b80: 18ed00e0   ldc      p0, c14, [r8, #-0]
01001b84: 00e4       b        #0x1001388
01001b86: 00e0       b        #0x1001b8a
01001b88: 8032       adds     r2, #0x80
01001b8a: 0040       ands     r0, r0
01001b8c: 0030       adds     r0, #0
01001b8e: 0040       ands     r0, r0
01001b90: 8432       adds     r2, #0x84
01001b92: 0040       ands     r0, r0
01001b94: 4c00       lsls     r4, r1, #1
01001b96: 0101       lsls     r1, r0, #4
01001b98: 5000       lsls     r0, r2, #1
01001b9a: 0101       lsls     r1, r0, #4
01001b9c: 5800       lsls     r0, r3, #1
01001b9e: 0101       lsls     r1, r0, #4
01001ba0: 9430       adds     r0, #0x94
01001ba2: 0040       ands     r0, r0
01001ba4: 9c30       adds     r0, #0x9c
01001ba6: 0040       ands     r0, r0
01001ba8: 4829       cmp      r1, #0x48
01001baa: 0001       lsls     r0, r0, #4
01001bac: a030       adds     r0, #0xa0
01001bae: 0040       ands     r0, r0
01001bb0: 5400       lsls     r4, r2, #1
01001bb2: 0101       lsls     r1, r0, #4
01001bb4: 4800       lsls     r0, r1, #1
01001bb6: 0101       lsls     r1, r0, #4
01001bb8: 4400       lsls     r4, r0, #1
01001bba: 0101       lsls     r1, r0, #4
01001bbc: 4c29       cmp      r1, #0x4c
01001bbe: 0001       lsls     r0, r0, #4
01001bc0: 4000       lsls     r0, r0, #1
01001bc2: 0020       movs     r0, #0
01001bc4: 0000       movs     r0, r0
01001bc6: 0020       movs     r0, #0
01001bc8: b448       ldr      r0, [pc, #0x2d0]
01001bca: 0078       ldrb     r0, [r0]
01001bcc: 7047       bx       lr
01001bce: 10b5       push     {r4, lr}
01001bd0: 0446       mov      r4, r0
01001bd2: b348       ldr      r0, [pc, #0x2cc]
01001bd4: 00ea0440   and.w    r0, r0, r4, lsl #16
01001bd8: 40f4a060   orr      r0, r0, #0x500
01001bdc: b149       ldr      r1, [pc, #0x2c4]
01001bde: 0860       str      r0, [r1]
01001be0: b148       ldr      r0, [pc, #0x2c4]
01001be2: ae49       ldr      r1, [pc, #0x2b8]
01001be4: 0860       str      r0, [r1]
01001be6: 8020       movs     r0, #0x80
01001be8: b049       ldr      r1, [pc, #0x2c0]
01001bea: 0870       strb     r0, [r1]
01001bec: 0020       movs     r0, #0
01001bee: b049       ldr      r1, [pc, #0x2c0]
01001bf0: 0860       str      r0, [r1]
01001bf2: 17e0       b        #0x1001c24
01001bf4: a948       ldr      r0, [pc, #0x2a4]
01001bf6: 0078       ldrb     r0, [r0]
01001bf8: ac49       ldr      r1, [pc, #0x2b0]
01001bfa: 0870       strb     r0, [r1]
01001bfc: a748       ldr      r0, [pc, #0x29c]
01001bfe: 0168       ldr      r1, [r0]
01001c00: aca0       adr      r0, #0x2b0
01001c02: 00f0fffb   bl       #0x1002404
01001c06: aa48       ldr      r0, [pc, #0x2a8]
01001c08: 0068       ldr      r0, [r0]
01001c0a: 401c       adds     r0, r0, #1
01001c0c: a849       ldr      r1, [pc, #0x2a0]
01001c0e: 0860       str      r0, [r1]
01001c10: 6428       cmp      r0, #0x64
01001c12: 07db       blt      #0x1001c24
01001c14: a9a3       adr      r3, #0x2a4
01001c16: 3122       movs     r2, #0x31
01001c18: b0a1       adr      r1, #0x2c0
01001c1a: b7a0       adr      r0, #0x2dc
01001c1c: 00f0f2fb   bl       #0x1002404
01001c20: 00bf       nop      
01001c22: fee7       b        #0x1001c22
01001c24: fff7d0ff   bl       #0x1001bc8
01001c28: 0028       cmp      r0, #0
01001c2a: e3d1       bne      #0x1001bf4
01001c2c: 9d49       ldr      r1, [pc, #0x274]
01001c2e: 0860       str      r0, [r1]
01001c30: b648       ldr      r0, [pc, #0x2d8]
01001c32: 9a49       ldr      r1, [pc, #0x268]
01001c34: 0860       str      r0, [r1]
01001c36: 8020       movs     r0, #0x80
01001c38: 9c49       ldr      r1, [pc, #0x270]
01001c3a: 0870       strb     r0, [r1]
01001c3c: 0020       movs     r0, #0
01001c3e: 9c49       ldr      r1, [pc, #0x270]
01001c40: 0860       str      r0, [r1]
01001c42: 17e0       b        #0x1001c74
01001c44: 9548       ldr      r0, [pc, #0x254]
01001c46: 0078       ldrb     r0, [r0]
01001c48: 9849       ldr      r1, [pc, #0x260]
01001c4a: 0870       strb     r0, [r1]
01001c4c: 9348       ldr      r0, [pc, #0x24c]
01001c4e: 0168       ldr      r1, [r0]
01001c50: afa0       adr      r0, #0x2bc
01001c52: 00f0d7fb   bl       #0x1002404
01001c56: 9648       ldr      r0, [pc, #0x258]
01001c58: 0068       ldr      r0, [r0]
01001c5a: 401c       adds     r0, r0, #1
01001c5c: 9449       ldr      r1, [pc, #0x250]
01001c5e: 0860       str      r0, [r1]
01001c60: 6428       cmp      r0, #0x64
01001c62: 07db       blt      #0x1001c74
01001c64: 95a3       adr      r3, #0x254
01001c66: 3a22       movs     r2, #0x3a
01001c68: 9ca1       adr      r1, #0x270
01001c6a: a3a0       adr      r0, #0x28c
01001c6c: 00f0cafb   bl       #0x1002404
01001c70: 00bf       nop      
01001c72: fee7       b        #0x1001c72
01001c74: fff7a8ff   bl       #0x1001bc8
01001c78: 0028       cmp      r0, #0
01001c7a: e3d1       bne      #0x1001c44
01001c7c: 10bd       pop      {r4, pc}
01001c7e: 10b5       push     {r4, lr}
01001c80: 0446       mov      r4, r0
01001c82: a548       ldr      r0, [pc, #0x294]
01001c84: a549       ldr      r1, [pc, #0x294]
01001c86: 0860       str      r0, [r1]
01001c88: 8548       ldr      r0, [pc, #0x214]
01001c8a: 00ea0440   and.w    r0, r0, r4, lsl #16
01001c8e: 40f41060   orr      r0, r0, #0x900
01001c92: 8449       ldr      r1, [pc, #0x210]
01001c94: 0860       str      r0, [r1]
01001c96: 8448       ldr      r0, [pc, #0x210]
01001c98: 8049       ldr      r1, [pc, #0x200]
01001c9a: 0860       str      r0, [r1]
01001c9c: 4ff08000   mov.w    r0, #0x80
01001ca0: 8249       ldr      r1, [pc, #0x208]
01001ca2: 0870       strb     r0, [r1]
01001ca4: 4ff00000   mov.w    r0, #0
01001ca8: 8149       ldr      r1, [pc, #0x204]
01001caa: 0860       str      r0, [r1]
01001cac: 17e0       b        #0x1001cde
01001cae: 7b48       ldr      r0, [pc, #0x1ec]
01001cb0: 0078       ldrb     r0, [r0]
01001cb2: 7e49       ldr      r1, [pc, #0x1f8]
01001cb4: 0870       strb     r0, [r1]
01001cb6: 7948       ldr      r0, [pc, #0x1e4]
01001cb8: 0168       ldr      r1, [r0]
01001cba: 99a0       adr      r0, #0x264
01001cbc: 00f0a2fb   bl       #0x1002404
01001cc0: 7b48       ldr      r0, [pc, #0x1ec]
01001cc2: 0068       ldr      r0, [r0]
01001cc4: 401c       adds     r0, r0, #1
01001cc6: 7a49       ldr      r1, [pc, #0x1e8]
01001cc8: 0860       str      r0, [r1]
01001cca: 6428       cmp      r0, #0x64
01001ccc: 07db       blt      #0x1001cde
01001cce: 7ba3       adr      r3, #0x1ec
01001cd0: 5022       movs     r2, #0x50
01001cd2: 82a1       adr      r1, #0x208
01001cd4: 88a0       adr      r0, #0x220
01001cd6: 00f095fb   bl       #0x1002404
01001cda: 00bf       nop      
01001cdc: fee7       b        #0x1001cdc
01001cde: fff773ff   bl       #0x1001bc8
01001ce2: 0028       cmp      r0, #0
01001ce4: e3d1       bne      #0x1001cae
01001ce6: 6f49       ldr      r1, [pc, #0x1bc]
01001ce8: 0860       str      r0, [r1]
01001cea: 091d       adds     r1, r1, #4
01001cec: 0860       str      r0, [r1]
01001cee: 8748       ldr      r0, [pc, #0x21c]
01001cf0: 6a49       ldr      r1, [pc, #0x1a8]
01001cf2: 0860       str      r0, [r1]
01001cf4: 8020       movs     r0, #0x80
01001cf6: 6d49       ldr      r1, [pc, #0x1b4]
01001cf8: 0870       strb     r0, [r1]
01001cfa: 0020       movs     r0, #0
01001cfc: 6c49       ldr      r1, [pc, #0x1b0]
01001cfe: 0860       str      r0, [r1]
01001d00: 17e0       b        #0x1001d32
01001d02: 6648       ldr      r0, [pc, #0x198]
01001d04: 0078       ldrb     r0, [r0]
01001d06: 6949       ldr      r1, [pc, #0x1a4]
01001d08: 0870       strb     r0, [r1]
01001d0a: 6448       ldr      r0, [pc, #0x190]
01001d0c: 0168       ldr      r1, [r0]
01001d0e: 86a0       adr      r0, #0x218
01001d10: 00f078fb   bl       #0x1002404
01001d14: 6648       ldr      r0, [pc, #0x198]
01001d16: 0068       ldr      r0, [r0]
01001d18: 401c       adds     r0, r0, #1
01001d1a: 6549       ldr      r1, [pc, #0x194]
01001d1c: 0860       str      r0, [r1]
01001d1e: 6428       cmp      r0, #0x64
01001d20: 07db       blt      #0x1001d32
01001d22: 66a3       adr      r3, #0x198
01001d24: 5a22       movs     r2, #0x5a
01001d26: 6da1       adr      r1, #0x1b4
01001d28: 73a0       adr      r0, #0x1cc
01001d2a: 00f06bfb   bl       #0x1002404
01001d2e: 00bf       nop      
01001d30: fee7       b        #0x1001d30
01001d32: fff749ff   bl       #0x1001bc8
01001d36: 0028       cmp      r0, #0
01001d38: e3d1       bne      #0x1001d02
01001d3a: 10bd       pop      {r4, pc}
01001d3c: 10b5       push     {r4, lr}
01001d3e: 0120       movs     r0, #1
01001d40: fff745ff   bl       #0x1001bce
01001d44: 0120       movs     r0, #1
01001d46: fff79aff   bl       #0x1001c7e
01001d4a: 0420       movs     r0, #4
01001d4c: 7849       ldr      r1, [pc, #0x1e0]
01001d4e: 0860       str      r0, [r1]
01001d50: 7849       ldr      r1, [pc, #0x1e0]
01001d52: c1f84c01   str.w    r0, [r1, #0x14c]
01001d56: 10bd       pop      {r4, pc}
01001d58: 7048       ldr      r0, [pc, #0x1c0]
01001d5a: 001f       subs     r0, r0, #4
01001d5c: 7649       ldr      r1, [pc, #0x1d8]
01001d5e: 8862       str      r0, [r1, #0x28]
01001d60: 0846       mov      r0, r1
01001d62: 0069       ldr      r0, [r0, #0x10]
01001d64: 40f02000   orr      r0, r0, #0x20
01001d68: 0861       str      r0, [r1, #0x10]
01001d6a: 7047       bx       lr
01001d6c: 7348       ldr      r0, [pc, #0x1cc]
01001d6e: 7449       ldr      r1, [pc, #0x1d0]
01001d70: 0860       str      r0, [r1]
01001d72: 7448       ldr      r0, [pc, #0x1d0]
01001d74: 7449       ldr      r1, [pc, #0x1d0]
01001d76: c1f80402   str.w    r0, [r1, #0x204]
01001d7a: 4ff08040   mov.w    r0, #0x40000000
01001d7e: 7349       ldr      r1, [pc, #0x1cc]
01001d80: 0860       str      r0, [r1]
01001d82: 4ff00000   mov.w    r0, #0
01001d86: 01f10401   add.w    r1, r1, #4
01001d8a: 0860       str      r0, [r1]
01001d8c: 7048       ldr      r0, [pc, #0x1c0]
01001d8e: 01f10401   add.w    r1, r1, #4
01001d92: 0860       str      r0, [r1]
01001d94: 4ff00000   mov.w    r0, #0
01001d98: 01f10401   add.w    r1, r1, #4
01001d9c: 0860       str      r0, [r1]
01001d9e: 01f10401   add.w    r1, r1, #4
01001da2: 0860       str      r0, [r1]
01001da4: 01f10401   add.w    r1, r1, #4
01001da8: 0860       str      r0, [r1]
01001daa: 01f10401   add.w    r1, r1, #4
01001dae: 0860       str      r0, [r1]
01001db0: 01f10401   add.w    r1, r1, #4
01001db4: 0860       str      r0, [r1]
01001db6: 6748       ldr      r0, [pc, #0x19c]
01001db8: 6749       ldr      r1, [pc, #0x19c]
01001dba: 0860       str      r0, [r1]
01001dbc: 6748       ldr      r0, [pc, #0x19c]
01001dbe: 01f10401   add.w    r1, r1, #4
01001dc2: 0860       str      r0, [r1]
01001dc4: 4ff08040   mov.w    r0, #0x40000000
01001dc8: 01f10401   add.w    r1, r1, #4
01001dcc: 0860       str      r0, [r1]
01001dce: 6448       ldr      r0, [pc, #0x190]
01001dd0: 6449       ldr      r1, [pc, #0x190]
01001dd2: 0860       str      r0, [r1]
01001dd4: 6448       ldr      r0, [pc, #0x190]
01001dd6: 01f10401   add.w    r1, r1, #4
01001dda: 0860       str      r0, [r1]
01001ddc: 4ff08040   mov.w    r0, #0x40000000
01001de0: 01f10401   add.w    r1, r1, #4
01001de4: 0860       str      r0, [r1]
01001de6: 6148       ldr      r0, [pc, #0x184]
01001de8: 6149       ldr      r1, [pc, #0x184]
01001dea: 0860       str      r0, [r1]
01001dec: 6148       ldr      r0, [pc, #0x184]
01001dee: 01f10401   add.w    r1, r1, #4
01001df2: 0860       str      r0, [r1]
01001df4: 4ff08040   mov.w    r0, #0x40000000
01001df8: 01f10401   add.w    r1, r1, #4
01001dfc: 0860       str      r0, [r1]
01001dfe: 5e48       ldr      r0, [pc, #0x178]
01001e00: 5e49       ldr      r1, [pc, #0x178]
01001e02: 0860       str      r0, [r1]
01001e04: 5e48       ldr      r0, [pc, #0x178]
01001e06: 01f10401   add.w    r1, r1, #4
01001e0a: 0860       str      r0, [r1]
01001e0c: 4ff08040   mov.w    r0, #0x40000000
01001e10: 01f10401   add.w    r1, r1, #4
01001e14: 0860       str      r0, [r1]
01001e16: 4e48       ldr      r0, [pc, #0x138]
01001e18: 0060       str      r0, [r0]
01001e1a: 00f10401   add.w    r1, r0, #4
01001e1e: 0860       str      r0, [r1]
01001e20: 5848       ldr      r0, [pc, #0x160]
01001e22: 1e49       ldr      r1, [pc, #0x78]
01001e24: 0860       str      r0, [r1]
01001e26: 1f48       ldr      r0, [pc, #0x7c]
01001e28: 01f10401   add.w    r1, r1, #4
01001e2c: 0860       str      r0, [r1]
01001e2e: 5648       ldr      r0, [pc, #0x158]
01001e30: 1c49       ldr      r1, [pc, #0x70]
01001e32: 0860       str      r0, [r1]
01001e34: 4ff00000   mov.w    r0, #0
01001e38: 01f10401   add.w    r1, r1, #4
01001e3c: 0860       str      r0, [r1]
01001e3e: 01f10401   add.w    r1, r1, #4
01001e42: 0860       str      r0, [r1]
01001e44: 7047       bx       lr
01001e46: 3b4a       ldr      r2, [pc, #0xec]
01001e48: 1169       ldr      r1, [r2, #0x10]
01001e4a: d268       ldr      r2, [r2, #0xc]
01001e4c: d043       mvns     r0, r2
01001e4e: 0140       ands     r1, r0
01001e50: 7047       bx       lr
01001e52: 384a       ldr      r2, [pc, #0xe0]
01001e54: 1169       ldr      r1, [r2, #0x10]
01001e56: d268       ldr      r2, [r2, #0xc]
01001e58: d043       mvns     r0, r2
01001e5a: 0140       ands     r1, r0
01001e5c: 7047       bx       lr
01001e5e: 00b5       push     {lr}
01001e60: 0820       movs     r0, #8
01001e62: 3449       ldr      r1, [pc, #0xd0]
01001e64: 0860       str      r0, [r1]
01001e66: 0120       movs     r0, #1
01001e68: 4849       ldr      r1, [pc, #0x120]
01001e6a: 0860       str      r0, [r1]
01001e6c: 3149       ldr      r1, [pc, #0xc4]
01001e6e: c1f82001   str.w    r0, [r1, #0x120]
01001e72: 4749       ldr      r1, [pc, #0x11c]
01001e74: 0860       str      r0, [r1]
01001e76: 2f49       ldr      r1, [pc, #0xbc]
01001e78: c1f84801   str.w    r0, [r1, #0x148]
01001e7c: fff776ff   bl       #0x1001d6c
01001e80: 2c48       ldr      r0, [pc, #0xb0]
01001e82: 4069       ldr      r0, [r0, #0x14]
01001e84: 40f2fe71   movw     r1, #0x7fe
01001e88: 8843       bics     r0, r1
01001e8a: 2a49       ldr      r1, [pc, #0xa8]
01001e8c: 4861       str      r0, [r1, #0x14]
01001e8e: 0420       movs     r0, #4
01001e90: 4049       ldr      r1, [pc, #0x100]
01001e92: 0860       str      r0, [r1]
01001e94: 2749       ldr      r1, [pc, #0x9c]
01001e96: c1f84401   str.w    r0, [r1, #0x144]
01001e9a: 00bd       pop      {pc}
01001e9c: 0886       strh     r0, [r1, #0x30]
01001e9e: 0040       ands     r0, r0
01001ea0: 0000       movs     r0, r0
01001ea2: ffff008c   vdup.8   d24, d0[7]
01001ea6: 0040       ands     r0, r0
01001ea8: 808e       ldrh     r0, [r0, #0x34]
01001eaa: 0800       movs     r0, r1
01001eac: 6400       lsls     r4, r4, #1
01001eae: 0101       lsls     r1, r0, #4
01001eb0: 6000       lsls     r0, r4, #1
01001eb2: 0101       lsls     r1, r0, #4
01001eb4: 6125       movs     r5, #0x61
01001eb6: 3038       subs     r0, #0x30
01001eb8: 780a       lsrs     r0, r7, #9
01001eba: 0000       movs     r0, r0
01001ebc: 2b2b       cmp      r3, #0x2b
01001ebe: 7469       ldr      r4, [r6, #0x14]
01001ec0: 6d65       str      r5, [r5, #0x54]
01001ec2: 4f75       strb     r7, [r1, #0x15]
01001ec4: 7443       muls     r4, r6, r4
01001ec6: 6e74       strb     r6, [r5, #0x11]
01001ec8: 203c       subs     r4, #0x20
01001eca: 2054       strb     r0, [r4, r0]
01001ecc: 494d       ldr      r5, [pc, #0x124]
01001ece: 454f       ldr      r7, [pc, #0x114]
01001ed0: 5554       strb     r5, [r2, r1]
01001ed2: 5f4c       ldr      r4, [pc, #0x17c]
01001ed4: 494d       ldr      r5, [pc, #0x124]
01001ed6: 4954       strb     r1, [r1, r1]
01001ed8: 0000       movs     r0, r0
01001eda: 0000       movs     r0, r0
01001edc: 7372       strb     r3, [r6, #9]
01001ede: 635f       ldrsh    r3, [r4, r5]
01001ee0: 7573       strb     r5, [r6, #0xd]
01001ee2: 625c       ldrb     r2, [r4, r1]
01001ee4: 7573       strb     r5, [r6, #0xd]
01001ee6: 6268       ldr      r2, [r4, #4]
01001ee8: 5f64       str      r7, [r3, #0x44]
01001eea: 6d61       str      r5, [r5, #0x14]
01001eec: 5f64       str      r7, [r3, #0x44]
01001eee: 7276       strb     r2, [r6, #0x19]
01001ef0: 2e63       str      r6, [r5, #0x30]
01001ef2: 7070       strb     r0, [r6, #1]
01001ef4: 0000       movs     r0, r0
01001ef6: 0000       movs     r0, r0
01001ef8: 2573       strb     r5, [r4, #0xc]
01001efa: 2825       movs     r5, #0x28
01001efc: 6429       cmp      r1, #0x64
01001efe: 205f       ldrsh    r0, [r4, r4]
01001f00: 4153       strh     r1, [r0, r5]
01001f02: 5345       cmp      r3, sl
01001f04: 5254       strb     r2, [r2, r1]
01001f06: 3a20       movs     r0, #0x3a
01001f08: 2573       strb     r5, [r4, #0xc]
01001f0a: 0a00       movs     r2, r1
01001f0c: 808d       ldrh     r0, [r0, #0x2c]
01001f0e: 0080       strh     r0, [r0]
01001f10: 6225       movs     r5, #0x62
01001f12: 3038       subs     r0, #0x30
01001f14: 780a       lsrs     r0, r7, #9
01001f16: 0000       movs     r0, r0
01001f18: 01e0       b        #0x1001f1e
01001f1a: 0002       lsls     r0, r0, #8
01001f1c: 0482       strh     r4, [r0, #0x10]
01001f1e: 0040       ands     r0, r0
01001f20: 6325       movs     r5, #0x63
01001f22: 3038       subs     r0, #0x30
01001f24: 780a       lsrs     r0, r7, #9
01001f26: 0000       movs     r0, r0
01001f28: 6425       movs     r5, #0x64
01001f2a: 3038       subs     r0, #0x30
01001f2c: 780a       lsrs     r0, r7, #9
01001f2e: 0000       movs     r0, r0
01001f30: 2441       asrs     r4, r4
01001f32: 0440       ands     r4, r0
01001f34: 0040       ands     r0, r0
01001f36: 0440       ands     r4, r0
01001f38: 0070       strb     r0, [r0]
01001f3a: 0040       ands     r0, r0
01001f3c: 0246       mov      r2, r0
01001f3e: 0440       ands     r4, r0
01001f40: 0082       strh     r0, [r0, #0x10]
01001f42: 0040       ands     r0, r0
01001f44: 00e0       b        #0x1001f48
01001f46: 0002       lsls     r0, r0, #8
01001f48: 0080       strh     r0, [r0]
01001f4a: 0040       ands     r0, r0
01001f4c: 0882       strh     r0, [r1, #0x10]
01001f4e: 0040       ands     r0, r0
01001f50: 0086       strh     r0, [r0, #0x30]
01001f52: 0040       ands     r0, r0
01001f54: 8246       mov      sl, r0
01001f56: 0440       ands     r4, r0
01001f58: 0046       mov      r0, r0
01001f5a: 0440       ands     r4, r0
01001f5c: 0123       movs     r3, #1
01001f5e: 0002       lsls     r0, r0, #8
01001f60: 8248       ldr      r0, [pc, #0x208]
01001f62: 0440       ands     r4, r0
01001f64: 8046       mov      r8, r0
01001f66: 0440       ands     r4, r0
01001f68: 0124       movs     r4, #1
01001f6a: 0002       lsls     r0, r0, #8
01001f6c: 0249       ldr      r1, [pc, #8]
01001f6e: 0440       ands     r4, r0
01001f70: 8048       ldr      r0, [pc, #0x200]
01001f72: 0440       ands     r4, r0
01001f74: 0128       cmp      r0, #1
01001f76: 0002       lsls     r0, r0, #8
01001f78: 0282       strh     r2, [r0, #0x10]
01001f7a: 0040       ands     r0, r0
01001f7c: 0049       ldr      r1, [pc, #0]
01001f7e: 0440       ands     r4, r0
01001f80: 0129       cmp      r1, #1
01001f82: 0002       lsls     r0, r0, #8
01001f84: 008d       ldrh     r0, [r0, #0x28]
01001f86: 0080       strh     r0, [r0]
01001f88: 0005       lsls     r0, r0, #0x14
01001f8a: 0100       movs     r1, r0
01001f8c: 1841       asrs     r0, r3
01001f8e: 0440       ands     r4, r0
01001f90: 4041       adcs     r0, r0
01001f92: 0440       ands     r4, r0
01001f94: 1c41       asrs     r4, r3
01001f96: 0440       ands     r4, r0
01001f98: 10b5       push     {r4, lr}
01001f9a: 0028       cmp      r0, #0
01001f9c: 07da       bge      #0x1001fae
01001f9e: ca06       lsls     r2, r1, #0x1b
01001fa0: 140e       lsrs     r4, r2, #0x18
01001fa2: d04a       ldr      r2, [pc, #0x340]
01001fa4: 00f00f03   and      r3, r0, #0xf
01001fa8: 1b1f       subs     r3, r3, #4
01001faa: d454       strb     r4, [r2, r3]
01001fac: 03e0       b        #0x1001fb6
01001fae: ca06       lsls     r2, r1, #0x1b
01001fb0: 130e       lsrs     r3, r2, #0x18
01001fb2: cd4a       ldr      r2, [pc, #0x334]
01001fb4: 1354       strb     r3, [r2, r0]
01001fb6: 10bd       pop      {r4, pc}
01001fb8: 0cb5       push     {r2, r3, lr}
01001fba: 0021       movs     r1, #0
01001fbc: 0191       str      r1, [sp, #4]
01001fbe: 0091       str      r1, [sp]
01001fc0: 0191       str      r1, [sp, #4]
01001fc2: 07e0       b        #0x1001fd4
01001fc4: 9df80010   ldrb.w   r1, [sp]
01001fc8: 491c       adds     r1, r1, #1
01001fca: c9b2       uxtb     r1, r1
01001fcc: 0091       str      r1, [sp]
01001fce: 0199       ldr      r1, [sp, #4]
01001fd0: 491c       adds     r1, r1, #1
01001fd2: 0191       str      r1, [sp, #4]
01001fd4: 0199       ldr      r1, [sp, #4]
01001fd6: 8142       cmp      r1, r0
01001fd8: f4d3       blo      #0x1001fc4
01001fda: 0cbd       pop      {r2, r3, pc}
01001fdc: 10b5       push     {r4, lr}
01001fde: 0446       mov      r4, r0
01001fe0: c248       ldr      r0, [pc, #0x308]
01001fe2: 406d       ldr      r0, [r0, #0x54]
01001fe4: 00f44060   and      r0, r0, #0xc00
01001fe8: b0f5006f   cmp.w    r0, #0x800
01001fec: 24d1       bne      #0x1002038
01001fee: bf48       ldr      r0, [pc, #0x2fc]
01001ff0: 406d       ldr      r0, [r0, #0x54]
01001ff2: 40f48070   orr      r0, r0, #0x100
01001ff6: bd49       ldr      r1, [pc, #0x2f4]
01001ff8: 4865       str      r0, [r1, #0x54]
01001ffa: bd48       ldr      r0, [pc, #0x2f4]
01001ffc: fff7dcff   bl       #0x1001fb8
01002000: ba48       ldr      r0, [pc, #0x2e8]
01002002: 406d       ldr      r0, [r0, #0x54]
01002004: 20f48070   bic      r0, r0, #0x100
01002008: b849       ldr      r1, [pc, #0x2e0]
0100200a: 4865       str      r0, [r1, #0x54]
0100200c: 00bf       nop      
0100200e: b748       ldr      r0, [pc, #0x2dc]
01002010: 406d       ldr      r0, [r0, #0x54]
01002012: 10f4807f   tst.w    r0, #0x100
01002016: fad1       bne      #0x100200e
01002018: b448       ldr      r0, [pc, #0x2d0]
0100201a: 406d       ldr      r0, [r0, #0x54]
0100201c: 10f0040f   tst.w    r0, #4
01002020: 0ad0       beq      #0x1002038
01002022: b248       ldr      r0, [pc, #0x2c8]
01002024: 406d       ldr      r0, [r0, #0x54]
01002026: 40f00800   orr      r0, r0, #8
0100202a: b049       ldr      r1, [pc, #0x2c0]
0100202c: 4865       str      r0, [r1, #0x54]
0100202e: 0846       mov      r0, r1
01002030: 4069       ldr      r0, [r0, #0x14]
01002032: 00f00400   and      r0, r0, #4
01002036: 4861       str      r0, [r1, #0x14]
01002038: 10bd       pop      {r4, pc}
0100203a: 70b5       push     {r4, r5, r6, lr}
0100203c: ab48       ldr      r0, [pc, #0x2ac]
0100203e: 4469       ldr      r4, [r0, #0x14]
01002040: 8669       ldr      r6, [r0, #0x18]
01002042: 3440       ands     r4, r6
01002044: 14f0010f   tst.w    r4, #1
01002048: 05d0       beq      #0x1002056
0100204a: 4069       ldr      r0, [r0, #0x14]
0100204c: 00f00100   and      r0, r0, #1
01002050: a649       ldr      r1, [pc, #0x298]
01002052: 4861       str      r0, [r1, #0x14]
01002054: 4fe0       b        #0x10020f6
01002056: 14f0020f   tst.w    r4, #2
0100205a: 06d0       beq      #0x100206a
0100205c: a348       ldr      r0, [pc, #0x28c]
0100205e: 4069       ldr      r0, [r0, #0x14]
01002060: 00f00200   and      r0, r0, #2
01002064: a149       ldr      r1, [pc, #0x284]
01002066: 4861       str      r0, [r1, #0x14]
01002068: 45e0       b        #0x10020f6
0100206a: 14f0100f   tst.w    r4, #0x10
0100206e: 03d0       beq      #0x1002078
01002070: 1020       movs     r0, #0x10
01002072: 9e49       ldr      r1, [pc, #0x278]
01002074: 4861       str      r0, [r1, #0x14]
01002076: 3ee0       b        #0x10020f6
01002078: 14f0040f   tst.w    r4, #4
0100207c: 2ed0       beq      #0x10020dc
0100207e: 9b48       ldr      r0, [pc, #0x26c]
01002080: 4069       ldr      r0, [r0, #0x14]
01002082: 00f00400   and      r0, r0, #4
01002086: 9949       ldr      r1, [pc, #0x264]
01002088: 4861       str      r0, [r1, #0x14]
0100208a: 0846       mov      r0, r1
0100208c: 456d       ldr      r5, [r0, #0x54]
0100208e: 15f0100f   tst.w    r5, #0x10
01002092: 30d1       bne      #0x10020f6
01002094: 15f0040f   tst.w    r5, #4
01002098: 07d0       beq      #0x10020aa
0100209a: 0820       movs     r0, #8
0100209c: 4865       str      r0, [r1, #0x54]
0100209e: 0846       mov      r0, r1
010020a0: 4069       ldr      r0, [r0, #0x14]
010020a2: 40f00400   orr      r0, r0, #4
010020a6: 4861       str      r0, [r1, #0x14]
010020a8: 25e0       b        #0x10020f6
010020aa: 15f0020f   tst.w    r5, #2
010020ae: 22d0       beq      #0x10020f6
010020b0: 8e48       ldr      r0, [pc, #0x238]
010020b2: 406d       ldr      r0, [r0, #0x54]
010020b4: 40f00200   orr      r0, r0, #2
010020b8: 8c49       ldr      r1, [pc, #0x230]
010020ba: 4865       str      r0, [r1, #0x54]
010020bc: 15f0010f   tst.w    r5, #1
010020c0: 08d0       beq      #0x10020d4
010020c2: fff749fe   bl       #0x1001d58
010020c6: 2846       mov      r0, r5
010020c8: fff788ff   bl       #0x1001fdc
010020cc: 0120       movs     r0, #1
010020ce: 8949       ldr      r1, [pc, #0x224]
010020d0: 0860       str      r0, [r1]
010020d2: 10e0       b        #0x10020f6
010020d4: 0020       movs     r0, #0
010020d6: 8749       ldr      r1, [pc, #0x21c]
010020d8: 0860       str      r0, [r1]
010020da: 0ce0       b        #0x10020f6
010020dc: 14f0080f   tst.w    r4, #8
010020e0: 03d0       beq      #0x10020ea
010020e2: 0820       movs     r0, #8
010020e4: 8149       ldr      r1, [pc, #0x204]
010020e6: 4861       str      r0, [r1, #0x14]
010020e8: 05e0       b        #0x10020f6
010020ea: 14f0200f   tst.w    r4, #0x20
010020ee: 02d0       beq      #0x10020f6
010020f0: 2020       movs     r0, #0x20
010020f2: 7e49       ldr      r1, [pc, #0x1f8]
010020f4: 4861       str      r0, [r1, #0x14]
010020f6: 70bd       pop      {r4, r5, r6, pc}
010020f8: 4ff00410   mov.w    r0, #0x40004
010020fc: 7e49       ldr      r1, [pc, #0x1f8]
010020fe: 0860       str      r0, [r1]
01002100: 4ff01700   mov.w    r0, #0x17
01002104: 7949       ldr      r1, [pc, #0x1e4]
01002106: 8861       str      r0, [r1, #0x18]
01002108: 7c48       ldr      r0, [pc, #0x1f0]
0100210a: 4862       str      r0, [r1, #0x24]
0100210c: 7c48       ldr      r0, [pc, #0x1f0]
0100210e: 8862       str      r0, [r1, #0x28]
01002110: 0846       mov      r0, r1
01002112: 0069       ldr      r0, [r0, #0x10]
01002114: 20f47f00   bic      r0, r0, #0xff0000
01002118: 0861       str      r0, [r1, #0x10]
0100211a: 0846       mov      r0, r1
0100211c: 0069       ldr      r0, [r0, #0x10]
0100211e: 40f48030   orr      r0, r0, #0x10000
01002122: 0861       str      r0, [r1, #0x10]
01002124: 0846       mov      r0, r1
01002126: 0069       ldr      r0, [r0, #0x10]
01002128: 40f00100   orr      r0, r0, #1
0100212c: 0861       str      r0, [r1, #0x10]
0100212e: 0846       mov      r0, r1
01002130: 006d       ldr      r0, [r0, #0x50]
01002132: 40f00100   orr      r0, r0, #1
01002136: 0865       str      r0, [r1, #0x50]
01002138: 0846       mov      r0, r1
0100213a: 406d       ldr      r0, [r0, #0x54]
0100213c: 40f48050   orr      r0, r0, #0x1000
01002140: 4865       str      r0, [r1, #0x54]
01002142: 7047       bx       lr
01002144: 6f4a       ldr      r2, [pc, #0x1bc]
01002146: 1068       ldr      r0, [r2]
01002148: 121d       adds     r2, r2, #4
0100214a: 1168       ldr      r1, [r2]
0100214c: 0840       ands     r0, r1
0100214e: 10f0020f   tst.w    r0, #2
01002152: 5cd1       bne      #0x100220e
01002154: 10f0100f   tst.w    r0, #0x10
01002158: 59d1       bne      #0x100220e
0100215a: 10f0080f   tst.w    r0, #8
0100215e: 56d1       bne      #0x100220e
01002160: 10f0400f   tst.w    r0, #0x40
01002164: 53d0       beq      #0x100220e
01002166: 674a       ldr      r2, [pc, #0x19c]
01002168: 4832       adds     r2, #0x48
0100216a: 1268       ldr      r2, [r2]
0100216c: 12f4803f   tst.w    r2, #0x10000
01002170: 07d0       beq      #0x1002182
01002172: 4ff48032   mov.w    r2, #0x10000
01002176: 634b       ldr      r3, [pc, #0x18c]
01002178: 4833       adds     r3, #0x48
0100217a: 1a60       str      r2, [r3]
0100217c: 4022       movs     r2, #0x40
0100217e: 614b       ldr      r3, [pc, #0x184]
01002180: 1a60       str      r2, [r3]
01002182: 604a       ldr      r2, [pc, #0x180]
01002184: 4832       adds     r2, #0x48
01002186: 1268       ldr      r2, [r2]
01002188: 12f0020f   tst.w    r2, #2
0100218c: 07d0       beq      #0x100219e
0100218e: 4ff40032   mov.w    r2, #0x20000
01002192: 5c4b       ldr      r3, [pc, #0x170]
01002194: 4833       adds     r3, #0x48
01002196: 1a60       str      r2, [r3]
01002198: 4022       movs     r2, #0x40
0100219a: 5a4b       ldr      r3, [pc, #0x168]
0100219c: 1a60       str      r2, [r3]
0100219e: 594a       ldr      r2, [pc, #0x164]
010021a0: 4832       adds     r2, #0x48
010021a2: 1268       ldr      r2, [r2]
010021a4: 12f0040f   tst.w    r2, #4
010021a8: 07d0       beq      #0x10021ba
010021aa: 4ff48022   mov.w    r2, #0x40000
010021ae: 554b       ldr      r3, [pc, #0x154]
010021b0: 4833       adds     r3, #0x48
010021b2: 1a60       str      r2, [r3]
010021b4: 4022       movs     r2, #0x40
010021b6: 534b       ldr      r3, [pc, #0x14c]
010021b8: 1a60       str      r2, [r3]
010021ba: 524a       ldr      r2, [pc, #0x148]
010021bc: 4832       adds     r2, #0x48
010021be: 1268       ldr      r2, [r2]
010021c0: 12f0080f   tst.w    r2, #8
010021c4: 09d0       beq      #0x10021da
010021c6: 4ff40022   mov.w    r2, #0x80000
010021ca: 4e4b       ldr      r3, [pc, #0x138]
010021cc: 4833       adds     r3, #0x48
010021ce: 1a60       str      r2, [r3]
010021d0: 4022       movs     r2, #0x40
010021d2: 4c4b       ldr      r3, [pc, #0x130]
010021d4: 1a60       str      r2, [r3]
010021d6: 00bf       nop      
010021d8: fee7       b        #0x10021d8
010021da: 4a4a       ldr      r2, [pc, #0x128]
010021dc: 4832       adds     r2, #0x48
010021de: 1268       ldr      r2, [r2]
010021e0: 12f4801f   tst.w    r2, #0x100000
010021e4: 07d0       beq      #0x10021f6
010021e6: 4ff48012   mov.w    r2, #0x100000
010021ea: 464b       ldr      r3, [pc, #0x118]
010021ec: 4833       adds     r3, #0x48
010021ee: 1a60       str      r2, [r3]
010021f0: 4022       movs     r2, #0x40
010021f2: 444b       ldr      r3, [pc, #0x110]
010021f4: 1a60       str      r2, [r3]
010021f6: 434a       ldr      r2, [pc, #0x10c]
010021f8: 4832       adds     r2, #0x48
010021fa: 1268       ldr      r2, [r2]
010021fc: 12f4807f   tst.w    r2, #0x100
01002200: 05d0       beq      #0x100220e
01002202: 404a       ldr      r2, [pc, #0x100]
01002204: 1268       ldr      r2, [r2]
01002206: 42f04002   orr      r2, r2, #0x40
0100220a: 3e4b       ldr      r3, [pc, #0xf8]
0100220c: 1a60       str      r2, [r3]
0100220e: 7047       bx       lr
01002210: 3d48       ldr      r0, [pc, #0xf4]
01002212: 3c49       ldr      r1, [pc, #0xf0]
01002214: 0c31       adds     r1, #0xc
01002216: 0860       str      r0, [r1]
01002218: 3c48       ldr      r0, [pc, #0xf0]
0100221a: 3a49       ldr      r1, [pc, #0xe8]
0100221c: 091d       adds     r1, r1, #4
0100221e: 0860       str      r0, [r1]
01002220: 3b48       ldr      r0, [pc, #0xec]
01002222: 3849       ldr      r1, [pc, #0xe0]
01002224: 2831       adds     r1, #0x28
01002226: 0860       str      r0, [r1]
01002228: 40f24650   movw     r0, #0x546
0100222c: 3549       ldr      r1, [pc, #0xd4]
0100222e: 3431       adds     r1, #0x34
01002230: 0860       str      r0, [r1]
01002232: 3448       ldr      r0, [pc, #0xd0]
01002234: 0838       subs     r0, #8
01002236: 0068       ldr      r0, [r0]
01002238: 40f08000   orr      r0, r0, #0x80
0100223c: 3149       ldr      r1, [pc, #0xc4]
0100223e: 0839       subs     r1, #8
01002240: 0860       str      r0, [r1]
01002242: 3048       ldr      r0, [pc, #0xc0]
01002244: 4830       adds     r0, #0x48
01002246: 0068       ldr      r0, [r0]
01002248: 40f48070   orr      r0, r0, #0x100
0100224c: 2d49       ldr      r1, [pc, #0xb4]
0100224e: 4831       adds     r1, #0x48
01002250: 0860       str      r0, [r1]
01002252: 2c48       ldr      r0, [pc, #0xb0]
01002254: 0838       subs     r0, #8
01002256: 0068       ldr      r0, [r0]
01002258: 40f0c000   orr      r0, r0, #0xc0
0100225c: 2949       ldr      r1, [pc, #0xa4]
0100225e: 0839       subs     r1, #8
01002260: 0860       str      r0, [r1]
01002262: 7047       bx       lr
01002264: 10b5       push     {r4, lr}
01002266: 2020       movs     r0, #0x20
01002268: 00f027f8   bl       #0x10022ba
0100226c: 0421       movs     r1, #4
0100226e: 2020       movs     r0, #0x20
01002270: fff792fe   bl       #0x1001f98
01002274: 2120       movs     r0, #0x21
01002276: 00f020f8   bl       #0x10022ba
0100227a: 0421       movs     r1, #4
0100227c: 2120       movs     r0, #0x21
0100227e: fff78bfe   bl       #0x1001f98
01002282: 10bd       pop      {r4, pc}
01002284: 10b5       push     {r4, lr}
01002286: fff7edff   bl       #0x1002264
0100228a: fff735ff   bl       #0x10020f8
0100228e: fff7bfff   bl       #0x1002210
01002292: 10bd       pop      {r4, pc}
01002294: 10b5       push     {r4, lr}
01002296: 1548       ldr      r0, [pc, #0x54]
01002298: 0069       ldr      r0, [r0, #0x10]
0100229a: 20f00100   bic      r0, r0, #1
0100229e: 1349       ldr      r1, [pc, #0x4c]
010022a0: 0861       str      r0, [r1, #0x10]
010022a2: 0846       mov      r0, r1
010022a4: 406d       ldr      r0, [r0, #0x54]
010022a6: 20f48050   bic      r0, r0, #0x1000
010022aa: 4865       str      r0, [r1, #0x54]
010022ac: 2020       movs     r0, #0x20
010022ae: 00f010f8   bl       #0x10022d2
010022b2: 2120       movs     r0, #0x21
010022b4: 00f00df8   bl       #0x10022d2
010022b8: 10bd       pop      {r4, pc}
010022ba: 00f01f02   and      r2, r0, #0x1f
010022be: 0121       movs     r1, #1
010022c0: 9140       lsls     r1, r2
010022c2: 4209       lsrs     r2, r0, #5
010022c4: 4ff0e023   mov.w    r3, #-0x1fff2000
010022c8: 03eb8202   add.w    r2, r3, r2, lsl #2
010022cc: c2f80011   str.w    r1, [r2, #0x100]
010022d0: 7047       bx       lr
010022d2: 00f01f02   and      r2, r0, #0x1f
010022d6: 0121       movs     r1, #1
010022d8: 9140       lsls     r1, r2
010022da: 0e4a       ldr      r2, [pc, #0x38]
010022dc: 4309       lsrs     r3, r0, #5
010022de: 42f82310   str.w    r1, [r2, r3, lsl #2]
010022e2: 7047       bx       lr
010022e4: 18ed00e0   ldc      p0, c14, [r8, #-0]
010022e8: 00e4       b        #0x1001aec
010022ea: 00e0       b        #0x10022ee
010022ec: 0070       strb     r0, [r0]
010022ee: 0040       ands     r0, r0
010022f0: c05c       ldrb     r0, [r0, r3]
010022f2: 1500       movs     r5, r2
010022f4: 6800       lsls     r0, r5, #1
010022f6: 0101       lsls     r1, r0, #4
010022f8: 9470       strb     r4, [r2, #2]
010022fa: 0040       ands     r0, r0
010022fc: 0043       orrs     r0, r0
010022fe: 0440       ands     r4, r0
01002300: 0046       mov      r0, r0
01002302: 0440       ands     r4, r0
01002304: 0c74       strb     r4, [r1, #0x10]
01002306: 0040       ands     r0, r0
01002308: 004d       ldr      r5, [pc, #0]
0100230a: 0440       ands     r4, r0
0100230c: 5a00       lsls     r2, r3, #1
0100230e: 0080       strh     r0, [r0]
01002310: fe05       lsls     r6, r7, #0x17
01002312: 6e04       lsls     r6, r5, #0x11
01002314: 80e1       b        #0x1002618
01002316: 00e0       b        #0x100231a
01002318: 40ea0103   orr.w    r3, r0, r1
0100231c: 9b07       lsls     r3, r3, #0x1e
0100231e: 03d0       beq      #0x1002328
01002320: 09e0       b        #0x1002336
01002322: 08c9       ldm      r1!, {r3}
01002324: 121f       subs     r2, r2, #4
01002326: 08c0       stm      r0!, {r3}
01002328: 042a       cmp      r2, #4
0100232a: fad2       bhs      #0x1002322
0100232c: 03e0       b        #0x1002336
0100232e: 11f8013b   ldrb     r3, [r1], #1
01002332: 00f8013b   strb     r3, [r0], #1
01002336: 521e       subs     r2, r2, #1
01002338: f9d2       bhs      #0x100232e
0100233a: 7047       bx       lr
0100233c: 2de9f05f   push.w   {r4, r5, r6, r7, r8, sb, sl, fp, ip, lr}
01002340: 0546       mov      r5, r0
01002342: 0020       movs     r0, #0
01002344: 9246       mov      sl, r2
01002346: 9b46       mov      fp, r3
01002348: 8846       mov      r8, r1
0100234a: 0646       mov      r6, r0
0100234c: 8146       mov      sb, r0
0100234e: 4024       movs     r4, #0x40
01002350: 1be0       b        #0x100238a
01002352: 2846       mov      r0, r5
01002354: 4146       mov      r1, r8
01002356: 4746       mov      r7, r8
01002358: 2246       mov      r2, r4
0100235a: 00f042f8   bl       #0x10023e2
0100235e: 5346       mov      r3, sl
01002360: 5a46       mov      r2, fp
01002362: c01a       subs     r0, r0, r3
01002364: 9141       sbcs     r1, r2
01002366: 10d3       blo      #0x100238a
01002368: 1146       mov      r1, r2
0100236a: 1846       mov      r0, r3
0100236c: 2246       mov      r2, r4
0100236e: 00f029f8   bl       #0x10023c4
01002372: 2d1a       subs     r5, r5, r0
01002374: 67eb0108   sbc.w    r8, r7, r1
01002378: 4f46       mov      r7, sb
0100237a: 2246       mov      r2, r4
0100237c: 0120       movs     r0, #1
0100237e: 0021       movs     r1, #0
01002380: 00f020f8   bl       #0x10023c4
01002384: 17eb0009   adds.w   sb, r7, r0
01002388: 4e41       adcs     r6, r1
0100238a: 201e       subs     r0, r4, #0
0100238c: a4f10104   sub.w    r4, r4, #1
01002390: dfdc       bgt      #0x1002352
01002392: 4846       mov      r0, sb
01002394: 3146       mov      r1, r6
01002396: 2a46       mov      r2, r5
01002398: 4346       mov      r3, r8
0100239a: bde8f09f   pop.w    {r4, r5, r6, r7, r8, sb, sl, fp, ip, pc}
0100239e: 0000       movs     r0, r0
010023a0: 064c       ldr      r4, [pc, #0x18]
010023a2: 074d       ldr      r5, [pc, #0x1c]
010023a4: 06e0       b        #0x10023b4
010023a6: e068       ldr      r0, [r4, #0xc]
010023a8: 40f00103   orr      r3, r0, #1
010023ac: 94e80700   ldm.w    r4, {r0, r1, r2}
010023b0: 9847       blx      r3
010023b2: 1034       adds     r4, #0x10
010023b4: ac42       cmp      r4, r5
010023b6: f6d3       blo      #0x10023a6
010023b8: fdf786ff   bl       #0x10002c8
010023bc: 5029       cmp      r1, #0x50
010023be: 0001       lsls     r0, r0, #4
010023c0: 8029       cmp      r1, #0x80
010023c2: 0001       lsls     r0, r0, #4
010023c4: 202a       cmp      r2, #0x20
010023c6: 04db       blt      #0x10023d2
010023c8: 203a       subs     r2, #0x20
010023ca: 00fa02f1   lsl.w    r1, r0, r2
010023ce: 0020       movs     r0, #0
010023d0: 7047       bx       lr
010023d2: 9140       lsls     r1, r2
010023d4: c2f12003   rsb.w    r3, r2, #0x20
010023d8: 20fa03f3   lsr.w    r3, r0, r3
010023dc: 1943       orrs     r1, r3
010023de: 9040       lsls     r0, r2
010023e0: 7047       bx       lr
010023e2: 202a       cmp      r2, #0x20
010023e4: 04db       blt      #0x10023f0
010023e6: 203a       subs     r2, #0x20
010023e8: 21fa02f0   lsr.w    r0, r1, r2
010023ec: 0021       movs     r1, #0
010023ee: 7047       bx       lr
010023f0: 21fa02f3   lsr.w    r3, r1, r2
010023f4: d040       lsrs     r0, r2
010023f6: c2f12002   rsb.w    r2, r2, #0x20
010023fa: 9140       lsls     r1, r2
010023fc: 0843       orrs     r0, r1
010023fe: 1946       mov      r1, r3
01002400: 7047       bx       lr
01002402: 0000       movs     r0, r0
01002404: 0fb4       push     {r0, r1, r2, r3}
01002406: 054b       ldr      r3, [pc, #0x14]
01002408: 10b5       push     {r4, lr}
0100240a: 03a9       add      r1, sp, #0xc
0100240c: 044a       ldr      r2, [pc, #0x10]
0100240e: 0298       ldr      r0, [sp, #8]
01002410: 00f018f8   bl       #0x1002444
01002414: 10bc       pop      {r4}
01002416: 5df814fb   ldr      pc, [sp], #0x14
0100241a: 0000       movs     r0, r0
0100241c: 1107       lsls     r1, r2, #0x1c
0100241e: 0001       lsls     r0, r0, #4
01002420: 0800       movs     r0, r1
01002422: 0101       lsls     r1, r0, #4
01002424: 02e0       b        #0x100242c
01002426: 08c8       ldm      r0!, {r3}
01002428: 121f       subs     r2, r2, #4
0100242a: 08c1       stm      r1!, {r3}
0100242c: 002a       cmp      r2, #0
0100242e: fad1       bne      #0x1002426
01002430: 7047       bx       lr
01002432: 7047       bx       lr
01002434: 0020       movs     r0, #0
01002436: 01e0       b        #0x100243c
01002438: 01c1       stm      r1!, {r0}
0100243a: 121f       subs     r2, r2, #4
0100243c: 002a       cmp      r2, #0
0100243e: fbd1       bne      #0x1002438
01002440: 7047       bx       lr
01002442: 0000       movs     r0, r0
01002444: 2de9ff4f   push.w   {r0, r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}
01002448: 8db0       sub      sp, #0x34
0100244a: 0f46       mov      r7, r1
0100244c: 0546       mov      r5, r0
0100244e: 0026       movs     r6, #0
01002450: dee1       b        #0x1002810
01002452: 2528       cmp      r0, #0x25
01002454: 74d1       bne      #0x1002540
01002456: 0024       movs     r4, #0
01002458: 6d1c       adds     r5, r5, #1
0100245a: f149       ldr      r1, [pc, #0x3c4]
0100245c: a246       mov      sl, r4
0100245e: a146       mov      sb, r4
01002460: 0122       movs     r2, #1
01002462: 2b78       ldrb     r3, [r5]
01002464: 203b       subs     r3, #0x20
01002466: 02fa03f0   lsl.w    r0, r2, r3
0100246a: 0842       tst      r0, r1
0100246c: 02d0       beq      #0x1002474
0100246e: 0443       orrs     r4, r0
01002470: 6d1c       adds     r5, r5, #1
01002472: f6e7       b        #0x1002462
01002474: 2878       ldrb     r0, [r5]
01002476: 2a28       cmp      r0, #0x2a
01002478: 10d0       beq      #0x100249c
0100247a: 6ff02f02   mvn      r2, #0x2f
0100247e: 2878       ldrb     r0, [r5]
01002480: a0f13001   sub.w    r1, r0, #0x30
01002484: 0929       cmp      r1, #9
01002486: 15d8       bhi      #0x10024b4
01002488: 0aeb8a01   add.w    r1, sl, sl, lsl #2
0100248c: 02eb4101   add.w    r1, r2, r1, lsl #1
01002490: 44f00204   orr      r4, r4, #2
01002494: 00eb010a   add.w    sl, r0, r1
01002498: 6d1c       adds     r5, r5, #1
0100249a: f0e7       b        #0x100247e
0100249c: 57f804ab   ldr      sl, [r7], #4
010024a0: baf1000f   cmp.w    sl, #0
010024a4: 03da       bge      #0x10024ae
010024a6: 44f40054   orr      r4, r4, #0x2000
010024aa: caf1000a   rsb.w    sl, sl, #0
010024ae: 44f00204   orr      r4, r4, #2
010024b2: 6d1c       adds     r5, r5, #1
010024b4: 2878       ldrb     r0, [r5]
010024b6: 2e28       cmp      r0, #0x2e
010024b8: 17d1       bne      #0x10024ea
010024ba: 15f8010f   ldrb     r0, [r5, #1]!
010024be: 44f00404   orr      r4, r4, #4
010024c2: 2a28       cmp      r0, #0x2a
010024c4: 0ed0       beq      #0x10024e4
010024c6: 6ff02f02   mvn      r2, #0x2f
010024ca: 2878       ldrb     r0, [r5]
010024cc: a0f13001   sub.w    r1, r0, #0x30
010024d0: 0929       cmp      r1, #9
010024d2: 0ad8       bhi      #0x10024ea
010024d4: 09eb8901   add.w    r1, sb, sb, lsl #2
010024d8: 02eb4101   add.w    r1, r2, r1, lsl #1
010024dc: 00eb0109   add.w    sb, r0, r1
010024e0: 6d1c       adds     r5, r5, #1
010024e2: f2e7       b        #0x10024ca
010024e4: 57f8049b   ldr      sb, [r7], #4
010024e8: 6d1c       adds     r5, r5, #1
010024ea: 2878       ldrb     r0, [r5]
010024ec: 6c28       cmp      r0, #0x6c
010024ee: 0fd0       beq      #0x1002510
010024f0: 06dc       bgt      #0x1002500
010024f2: 4c28       cmp      r0, #0x4c
010024f4: 17d0       beq      #0x1002526
010024f6: 6828       cmp      r0, #0x68
010024f8: 0dd0       beq      #0x1002516
010024fa: 6a28       cmp      r0, #0x6a
010024fc: 14d1       bne      #0x1002528
010024fe: 04e0       b        #0x100250a
01002500: 7428       cmp      r0, #0x74
01002502: 10d0       beq      #0x1002526
01002504: 7a28       cmp      r0, #0x7a
01002506: 0fd1       bne      #0x1002528
01002508: 0de0       b        #0x1002526
0100250a: 44f40014   orr      r4, r4, #0x200000
0100250e: 0ae0       b        #0x1002526
01002510: 44f48014   orr      r4, r4, #0x100000
01002514: 01e0       b        #0x100251a
01002516: 44f44014   orr      r4, r4, #0x300000
0100251a: 6978       ldrb     r1, [r5, #1]
0100251c: 8142       cmp      r1, r0
0100251e: 02d1       bne      #0x1002526
01002520: 6d1c       adds     r5, r5, #1
01002522: 04f58014   add.w    r4, r4, #0x100000
01002526: 6d1c       adds     r5, r5, #1
01002528: 2a78       ldrb     r2, [r5]
0100252a: 6e2a       cmp      r2, #0x6e
0100252c: 20d0       beq      #0x1002570
0100252e: 0ddc       bgt      #0x100254c
01002530: 632a       cmp      r2, #0x63
01002532: 33d0       beq      #0x100259c
01002534: 05dc       bgt      #0x1002542
01002536: 002a       cmp      r2, #0
01002538: 6fd0       beq      #0x100261a
0100253a: 582a       cmp      r2, #0x58
0100253c: 12d1       bne      #0x1002564
0100253e: a2e0       b        #0x1002686
01002540: 11e0       b        #0x1002566
01002542: 642a       cmp      r2, #0x64
01002544: 6ad0       beq      #0x100261c
01002546: 692a       cmp      r2, #0x69
01002548: 0cd1       bne      #0x1002564
0100254a: 67e0       b        #0x100261c
0100254c: 732a       cmp      r2, #0x73
0100254e: 2fd0       beq      #0x10025b0
01002550: 04dc       bgt      #0x100255c
01002552: 6f2a       cmp      r2, #0x6f
01002554: 6fd0       beq      #0x1002636
01002556: 702a       cmp      r2, #0x70
01002558: 04d1       bne      #0x1002564
0100255a: 99e0       b        #0x1002690
0100255c: 752a       cmp      r2, #0x75
0100255e: 6bd0       beq      #0x1002638
01002560: 782a       cmp      r2, #0x78
01002562: 6ad0       beq      #0x100263a
01002564: 1046       mov      r0, r2
01002566: dde90f12   ldrd     r1, r2, [sp, #0x3c]
0100256a: 9047       blx      r2
0100256c: 761c       adds     r6, r6, #1
0100256e: 4ee1       b        #0x100280e
01002570: c4f30250   ubfx     r0, r4, #0x14, #3
01002574: 0228       cmp      r0, #2
01002576: 06d0       beq      #0x1002586
01002578: 0328       cmp      r0, #3
0100257a: 0ad0       beq      #0x1002592
0100257c: 0428       cmp      r0, #4
0100257e: 01cf       ldm      r7!, {r0}
01002580: 0ad0       beq      #0x1002598
01002582: 0660       str      r6, [r0]
01002584: 43e1       b        #0x100280e
01002586: 01cf       ldm      r7!, {r0}
01002588: 4feae671   asr.w    r1, r6, #0x1f
0100258c: c0e90061   strd     r6, r1, [r0]
01002590: 3de1       b        #0x100280e
01002592: 01cf       ldm      r7!, {r0}
01002594: 0680       strh     r6, [r0]
01002596: 3ae1       b        #0x100280e
01002598: 0670       strb     r6, [r0]
0100259a: 38e1       b        #0x100280e
0100259c: 17f8040b   ldrb     r0, [r7], #4
010025a0: 8df80000   strb.w   r0, [sp]
010025a4: 0020       movs     r0, #0
010025a6: 8df80100   strb.w   r0, [sp, #1]
010025aa: eb46       mov      fp, sp
010025ac: 0120       movs     r0, #1
010025ae: 03e0       b        #0x10025b8
010025b0: 57f804bb   ldr      fp, [r7], #4
010025b4: 4ff0ff30   mov.w    r0, #-1
010025b8: 6107       lsls     r1, r4, #0x1d
010025ba: 4ff00001   mov.w    r1, #0
010025be: 02d4       bmi      #0x10025c6
010025c0: 0de0       b        #0x10025de
010025c2: 08f10101   add.w    r1, r8, #1
010025c6: 8846       mov      r8, r1
010025c8: 4945       cmp      r1, sb
010025ca: 0fda       bge      #0x10025ec
010025cc: 8045       cmp      r8, r0
010025ce: f8db       blt      #0x10025c2
010025d0: 1bf80810   ldrb.w   r1, [fp, r8]
010025d4: 0029       cmp      r1, #0
010025d6: f4d1       bne      #0x10025c2
010025d8: 08e0       b        #0x10025ec
010025da: 08f10101   add.w    r1, r8, #1
010025de: 8846       mov      r8, r1
010025e0: 8142       cmp      r1, r0
010025e2: fadb       blt      #0x10025da
010025e4: 1bf80810   ldrb.w   r1, [fp, r8]
010025e8: 0029       cmp      r1, #0
010025ea: f6d1       bne      #0x10025da
010025ec: dde90f23   ldrd     r2, r3, [sp, #0x3c]
010025f0: aaeb0800   sub.w    r0, sl, r8
010025f4: 8146       mov      sb, r0
010025f6: 2146       mov      r1, r4
010025f8: 00f03bf9   bl       #0x1002872
010025fc: 3044       add      r0, r6
010025fe: 00eb0806   add.w    r6, r0, r8
01002602: 04e0       b        #0x100260e
01002604: dde90f12   ldrd     r1, r2, [sp, #0x3c]
01002608: 1bf8010b   ldrb     r0, [fp], #1
0100260c: 9047       blx      r2
0100260e: b8f10108   subs.w   r8, r8, #1
01002612: f7d2       bhs      #0x1002604
01002614: 2146       mov      r1, r4
01002616: 4846       mov      r0, sb
01002618: f4e0       b        #0x1002804
0100261a: fde0       b        #0x1002818
0100261c: 0a21       movs     r1, #0xa
0100261e: c4f30253   ubfx     r3, r4, #0x14, #3
01002622: 4ff0000b   mov.w    fp, #0
01002626: 0891       str      r1, [sp, #0x20]
01002628: 022b       cmp      r3, #2
0100262a: 07d0       beq      #0x100263c
0100262c: 01cf       ldm      r7!, {r0}
0100262e: c117       asrs     r1, r0, #0x1f
01002630: 032b       cmp      r3, #3
01002632: 09d0       beq      #0x1002648
01002634: 0ae0       b        #0x100264c
01002636: 34e0       b        #0x10026a2
01002638: 23e0       b        #0x1002682
0100263a: 24e0       b        #0x1002686
0100263c: ff1d       adds     r7, r7, #7
0100263e: 27f00707   bic      r7, r7, #7
01002642: f7e80201   ldrd     r0, r1, [r7], #8
01002646: 05e0       b        #0x1002654
01002648: 00b2       sxth     r0, r0
0100264a: c117       asrs     r1, r0, #0x1f
0100264c: 042b       cmp      r3, #4
0100264e: 01d1       bne      #0x1002654
01002650: 40b2       sxtb     r0, r0
01002652: c117       asrs     r1, r0, #0x1f
01002654: 0029       cmp      r1, #0
01002656: 07da       bge      #0x1002668
01002658: 4ff0000c   mov.w    ip, #0
0100265c: d0eb0c00   rsbs     r0, r0, ip
01002660: 6ceb0101   sbc.w    r1, ip, r1
01002664: 2d23       movs     r3, #0x2d
01002666: 02e0       b        #0x100266e
01002668: 2305       lsls     r3, r4, #0x14
0100266a: 04d5       bpl      #0x1002676
0100266c: 2b23       movs     r3, #0x2b
0100266e: 8df82430   strb.w   r3, [sp, #0x24]
01002672: 0123       movs     r3, #1
01002674: 03e0       b        #0x100267e
01002676: e307       lsls     r3, r4, #0x1f
01002678: 01d0       beq      #0x100267e
0100267a: 2023       movs     r3, #0x20
0100267c: f7e7       b        #0x100266e
0100267e: 9846       mov      r8, r3
01002680: 50e0       b        #0x1002724
01002682: 0a21       movs     r1, #0xa
01002684: 0ee0       b        #0x10026a4
01002686: 1020       movs     r0, #0x10
01002688: 4ff0000b   mov.w    fp, #0
0100268c: 0890       str      r0, [sp, #0x20]
0100268e: 0ce0       b        #0x10026aa
01002690: 1021       movs     r1, #0x10
01002692: 4ff0000b   mov.w    fp, #0
01002696: 44f00404   orr      r4, r4, #4
0100269a: 4ff00809   mov.w    sb, #8
0100269e: 0891       str      r1, [sp, #0x20]
010026a0: 03e0       b        #0x10026aa
010026a2: 0821       movs     r1, #8
010026a4: 4ff0000b   mov.w    fp, #0
010026a8: 0891       str      r1, [sp, #0x20]
010026aa: c4f30253   ubfx     r3, r4, #0x14, #3
010026ae: 022b       cmp      r3, #2
010026b0: 04d0       beq      #0x10026bc
010026b2: 01cf       ldm      r7!, {r0}
010026b4: 0021       movs     r1, #0
010026b6: 032b       cmp      r3, #3
010026b8: 06d0       beq      #0x10026c8
010026ba: 06e0       b        #0x10026ca
010026bc: ff1d       adds     r7, r7, #7
010026be: 27f00707   bic      r7, r7, #7
010026c2: f7e80201   ldrd     r0, r1, [r7], #8
010026c6: 03e0       b        #0x10026d0
010026c8: 80b2       uxth     r0, r0
010026ca: 042b       cmp      r3, #4
010026cc: 00d1       bne      #0x10026d0
010026ce: c0b2       uxtb     r0, r0
010026d0: 4ff00008   mov.w    r8, #0
010026d4: 2307       lsls     r3, r4, #0x1c
010026d6: 25d5       bpl      #0x1002724
010026d8: 702a       cmp      r2, #0x70
010026da: 2ad0       beq      #0x1002732
010026dc: ddf820c0   ldr.w    ip, [sp, #0x20]
010026e0: 8cf0100c   eor      ip, ip, #0x10
010026e4: 5cea0b0c   orrs.w   ip, ip, fp
010026e8: 09d1       bne      #0x10026fe
010026ea: 50ea0103   orrs.w   r3, r0, r1
010026ee: 06d0       beq      #0x10026fe
010026f0: 3023       movs     r3, #0x30
010026f2: 8df82430   strb.w   r3, [sp, #0x24]
010026f6: 8df82520   strb.w   r2, [sp, #0x25]
010026fa: 0223       movs     r3, #2
010026fc: 9846       mov      r8, r3
010026fe: ddf820c0   ldr.w    ip, [sp, #0x20]
01002702: 8cf0080c   eor      ip, ip, #8
01002706: 5cea0b0c   orrs.w   ip, ip, fp
0100270a: 0bd1       bne      #0x1002724
0100270c: 50ea0103   orrs.w   r3, r0, r1
01002710: 01d1       bne      #0x1002716
01002712: 6307       lsls     r3, r4, #0x1d
01002714: 06d5       bpl      #0x1002724
01002716: 3023       movs     r3, #0x30
01002718: 8df82430   strb.w   r3, [sp, #0x24]
0100271c: 4ff00108   mov.w    r8, #1
01002720: a9f10109   sub.w    sb, sb, #1
01002724: 582a       cmp      r2, #0x58
01002726: 09d0       beq      #0x100273c
01002728: 3ea2       adr      r2, #0xf8
0100272a: 0b92       str      r2, [sp, #0x2c]
0100272c: 08aa       add      r2, sp, #0x20
0100272e: 0a92       str      r2, [sp, #0x28]
01002730: 11e0       b        #0x1002756
01002732: 4023       movs     r3, #0x40
01002734: 8df82430   strb.w   r3, [sp, #0x24]
01002738: 0123       movs     r3, #1
0100273a: dfe7       b        #0x10026fc
0100273c: 3ea2       adr      r2, #0xf8
0100273e: f4e7       b        #0x100272a
01002740: 5b46       mov      r3, fp
01002742: 089a       ldr      r2, [sp, #0x20]
01002744: fff7fafd   bl       #0x100233c
01002748: 0b9b       ldr      r3, [sp, #0x2c]
0100274a: 9b5c       ldrb     r3, [r3, r2]
0100274c: 0a9a       ldr      r2, [sp, #0x28]
0100274e: a2f10102   sub.w    r2, r2, #1
01002752: 0a92       str      r2, [sp, #0x28]
01002754: 1370       strb     r3, [r2]
01002756: 50ea0102   orrs.w   r2, r0, r1
0100275a: f1d1       bne      #0x1002740
0100275c: 0a98       ldr      r0, [sp, #0x28]
0100275e: adeb0000   sub.w    r0, sp, r0
01002762: 00f1200b   add.w    fp, r0, #0x20
01002766: 6007       lsls     r0, r4, #0x1d
01002768: 02d5       bpl      #0x1002770
0100276a: 24f48034   bic      r4, r4, #0x10000
0100276e: 01e0       b        #0x1002774
01002770: 4ff00109   mov.w    sb, #1
01002774: d945       cmp      sb, fp
01002776: 02dd       ble      #0x100277e
01002778: a9eb0b00   sub.w    r0, sb, fp
0100277c: 00e0       b        #0x1002780
0100277e: 0020       movs     r0, #0
01002780: 00eb0b01   add.w    r1, r0, fp
01002784: 4144       add      r1, r8
01002786: 0890       str      r0, [sp, #0x20]
01002788: aaeb010a   sub.w    sl, sl, r1
0100278c: e003       lsls     r0, r4, #0xf
0100278e: 06d4       bmi      #0x100279e
01002790: dde90f23   ldrd     r2, r3, [sp, #0x3c]
01002794: 2146       mov      r1, r4
01002796: 5046       mov      r0, sl
01002798: 00f06bf8   bl       #0x1002872
0100279c: 0644       add      r6, r0
0100279e: 0020       movs     r0, #0
010027a0: 08e0       b        #0x10027b4
010027a2: 09a9       add      r1, sp, #0x24
010027a4: 11f80900   ldrb.w   r0, [r1, sb]
010027a8: dde90f12   ldrd     r1, r2, [sp, #0x3c]
010027ac: 9047       blx      r2
010027ae: 761c       adds     r6, r6, #1
010027b0: 09f10100   add.w    r0, sb, #1
010027b4: 8146       mov      sb, r0
010027b6: 4045       cmp      r0, r8
010027b8: f3db       blt      #0x10027a2
010027ba: e003       lsls     r0, r4, #0xf
010027bc: 0cd5       bpl      #0x10027d8
010027be: dde90f23   ldrd     r2, r3, [sp, #0x3c]
010027c2: 2146       mov      r1, r4
010027c4: 5046       mov      r0, sl
010027c6: 00f054f8   bl       #0x1002872
010027ca: 0644       add      r6, r0
010027cc: 04e0       b        #0x10027d8
010027ce: dde90f12   ldrd     r1, r2, [sp, #0x3c]
010027d2: 3020       movs     r0, #0x30
010027d4: 9047       blx      r2
010027d6: 761c       adds     r6, r6, #1
010027d8: 0899       ldr      r1, [sp, #0x20]
010027da: 481e       subs     r0, r1, #1
010027dc: 0890       str      r0, [sp, #0x20]
010027de: 0029       cmp      r1, #0
010027e0: f5dc       bgt      #0x10027ce
010027e2: 08e0       b        #0x10027f6
010027e4: 0a98       ldr      r0, [sp, #0x28]
010027e6: 0a99       ldr      r1, [sp, #0x28]
010027e8: 0078       ldrb     r0, [r0]
010027ea: 491c       adds     r1, r1, #1
010027ec: 0a91       str      r1, [sp, #0x28]
010027ee: dde90f12   ldrd     r1, r2, [sp, #0x3c]
010027f2: 9047       blx      r2
010027f4: 761c       adds     r6, r6, #1
010027f6: bbf10001   subs.w   r1, fp, #0
010027fa: abf1010b   sub.w    fp, fp, #1
010027fe: f1dc       bgt      #0x10027e4
01002800: 2146       mov      r1, r4
01002802: 5046       mov      r0, sl
01002804: dde90f23   ldrd     r2, r3, [sp, #0x3c]
01002808: 00f020f8   bl       #0x100284c
0100280c: 0644       add      r6, r0
0100280e: 6d1c       adds     r5, r5, #1
01002810: 2878       ldrb     r0, [r5]
01002812: 0028       cmp      r0, #0
01002814: 7ff41dae   bne.w    #0x1002452
01002818: 11b0       add      sp, #0x44
0100281a: 3046       mov      r0, r6
0100281c: bde8f08f   pop.w    {r4, r5, r6, r7, r8, sb, sl, fp, pc}
01002820: 0928       cmp      r0, #9
01002822: 0100       movs     r1, r0
01002824: 3031       adds     r1, #0x30
01002826: 3233       adds     r3, #0x32
01002828: 3435       adds     r5, #0x34
0100282a: 3637       adds     r7, #0x36
0100282c: 3839       subs     r1, #0x38
0100282e: 6162       str      r1, [r4, #0x24]
01002830: 6364       str      r3, [r4, #0x44]
01002832: 6566       str      r5, [r4, #0x64]
01002834: 0000       movs     r0, r0
01002836: 0000       movs     r0, r0
01002838: 3031       adds     r1, #0x30
0100283a: 3233       adds     r3, #0x32
0100283c: 3435       adds     r5, #0x34
0100283e: 3637       adds     r7, #0x36
01002840: 3839       subs     r1, #0x38
01002842: 4142       rsbs     r1, r0, #0
01002844: 4344       add      r3, r8
01002846: 4546       mov      r5, r8
01002848: 0000       movs     r0, r0
0100284a: 0000       movs     r0, r0
0100284c: 2de9f041   push.w   {r4, r5, r6, r7, r8, lr}
01002850: 0446       mov      r4, r0
01002852: 0025       movs     r5, #0
01002854: 1e46       mov      r6, r3
01002856: 1746       mov      r7, r2
01002858: 8804       lsls     r0, r1, #0x12
0100285a: 05d4       bmi      #0x1002868
0100285c: 06e0       b        #0x100286c
0100285e: 3946       mov      r1, r7
01002860: 2020       movs     r0, #0x20
01002862: b047       blx      r6
01002864: 05f10105   add.w    r5, r5, #1
01002868: 641e       subs     r4, r4, #1
0100286a: f8d5       bpl      #0x100285e
0100286c: 2846       mov      r0, r5
0100286e: bde8f081   pop.w    {r4, r5, r6, r7, r8, pc}
01002872: 2de9f041   push.w   {r4, r5, r6, r7, r8, lr}
01002876: 0446       mov      r4, r0
01002878: 0025       movs     r5, #0
0100287a: 1e46       mov      r6, r3
0100287c: 9046       mov      r8, r2
0100287e: c803       lsls     r0, r1, #0xf
01002880: 01d5       bpl      #0x1002886
01002882: 3027       movs     r7, #0x30
01002884: 00e0       b        #0x1002888
01002886: 2027       movs     r7, #0x20
01002888: 8804       lsls     r0, r1, #0x12
0100288a: 05d5       bpl      #0x1002898
0100288c: 06e0       b        #0x100289c
0100288e: 4146       mov      r1, r8
01002890: 3846       mov      r0, r7
01002892: b047       blx      r6
01002894: 05f10105   add.w    r5, r5, #1
01002898: 641e       subs     r4, r4, #1
0100289a: f8d5       bpl      #0x100288e
0100289c: 2846       mov      r0, r5
0100289e: bde8f081   pop.w    {r4, r5, r6, r7, r8, pc}
010028a2: 0000       movs     r0, r0
010028a4: 0000       movs     r0, r0
010028a6: 00e0       b        #0x10028aa
010028a8: 0144       add      r1, r0
010028aa: 0000       movs     r0, r0
010028ac: 5802       lsls     r0, r3, #9
010028ae: 0001       lsls     r0, r0, #4
010028b0: 4111       asrs     r1, r0, #5
010028b2: 4300       lsls     r3, r0, #1
010028b4: d182       strh     r1, [r2, #0x16]
010028b6: c182       strh     r1, [r0, #0x16]
010028b8: b100       lsls     r1, r6, #2
010028ba: a182       strh     r1, [r4, #0x14]
010028bc: 9182       strh     r1, [r2, #0x14]
010028be: 0f00       movs     r7, r1
010028c0: f281       strh     r2, [r6, #0xe]
010028c2: e281       strh     r2, [r4, #0xe]
010028c4: c281       strh     r2, [r0, #0xe]
010028c6: b281       strh     r2, [r6, #0xc]
010028c8: a281       strh     r2, [r4, #0xc]
010028ca: 9281       strh     r2, [r2, #0xc]
010028cc: 8281       strh     r2, [r0, #0xc]
010028ce: 7281       strh     r2, [r6, #0xa]
010028d0: 6281       strh     r2, [r4, #0xa]
010028d2: 5281       strh     r2, [r2, #0xa]
010028d4: 4281       strh     r2, [r0, #0xa]
010028d6: 3281       strh     r2, [r6, #8]
010028d8: 2281       strh     r2, [r4, #8]
010028da: 1281       strh     r2, [r2, #8]
010028dc: 0281       strh     r2, [r0, #8]
010028de: f3c1       stm      r1!, {r0, r1, r4, r5, r6, r7}
010028e0: e3c1       stm      r1!, {r0, r1, r5, r6, r7}
010028e2: d3c1       stm      r1!, {r0, r1, r4, r6, r7}
010028e4: c3c1       stm      r1!, {r0, r1, r6, r7}
010028e6: b3c1       stm      r1!, {r0, r1, r4, r5, r7}
010028e8: a3c1       stm      r1!, {r0, r1, r5, r7}
010028ea: 93c1       stm      r1!, {r0, r1, r4, r7}
010028ec: 83c1       stm      r1!, {r0, r1, r7}
010028ee: 73c1       stm      r1!, {r0, r1, r4, r5, r6}
010028f0: 63c1       stm      r1!, {r0, r1, r5, r6}
010028f2: 53c1       stm      r1!, {r0, r1, r4, r6}
010028f4: 43c1       stm      r1!, {r0, r1, r6}
010028f6: 33c1       stm      r1!, {r0, r1, r4, r5}
010028f8: 23c1       stm      r1!, {r0, r1, r5}
010028fa: 13c1       stm      r1!, {r0, r1, r4}
010028fc: 03c1       stm      r1!, {r0, r1}
010028fe: 8481       strh     r4, [r0, #0xc]
01002900: 7481       strh     r4, [r6, #0xa]
01002902: 6481       strh     r4, [r4, #0xa]
01002904: 5481       strh     r4, [r2, #0xa]
01002906: 4481       strh     r4, [r0, #0xa]
01002908: 3481       strh     r4, [r6, #8]
0100290a: 2481       strh     r4, [r4, #8]
0100290c: 1481       strh     r4, [r2, #8]
0100290e: 0f00       movs     r7, r1
01002910: 8500       lsls     r5, r0, #2
01002912: 4580       strh     r5, [r0, #2]
01002914: 3580       strh     r5, [r6]
01002916: 2580       strh     r5, [r4]
01002918: 1580       strh     r5, [r2]
0100291a: 0580       strh     r5, [r0]
0100291c: 0480       strh     r4, [r0]
0100291e: d280       strh     r2, [r2, #6]
01002920: 8180       strh     r1, [r0, #4]
01002922: 7180       strh     r1, [r6, #2]
01002924: 6180       strh     r1, [r4, #2]
01002926: 5180       strh     r1, [r2, #2]
01002928: 4180       strh     r1, [r0, #2]
0100292a: 3180       strh     r1, [r6]
0100292c: 2180       strh     r1, [r4]
0100292e: 1180       strh     r1, [r2]
01002930: 0100       movs     r1, r0
01002932: 1080       strh     r0, [r2]
01002934: 0000       movs     r0, r0
01002936: 0f00       movs     r7, r1
01002938: 880d       lsrs     r0, r1, #0x16
0100293a: 0000       movs     r0, r0
0100293c: b200       lsls     r2, r6, #2
0100293e: 0000       movs     r0, r0
01002940: 030c       lsrs     r3, r0, #0x10
01002942: 0000       movs     r0, r0
01002944: 0000       movs     r0, r0
01002946: 0002       lsls     r0, r0, #8
01002948: 0d82       strh     r5, [r1, #0x10]
0100294a: 0480       strh     r4, [r0]
0100294c: 0583       strh     r5, [r0, #0x18]
0100294e: 0400       movs     r4, r0
01002950: 8029       cmp      r1, #0x80
01002952: 0001       lsls     r0, r0, #4
01002954: 0000       movs     r0, r0
01002956: 0101       lsls     r1, r0, #4
01002958: 6c00       lsls     r4, r5, #1
0100295a: 0000       movs     r0, r0
0100295c: 2424       movs     r4, #0x24
0100295e: 0001       lsls     r0, r0, #4
01002960: ec29       cmp      r1, #0xec
01002962: 0001       lsls     r0, r0, #4
01002964: 6c00       lsls     r4, r5, #1
01002966: 0101       lsls     r1, r0, #4
01002968: 3c14       asrs     r4, r7, #0x10
0100296a: 0000       movs     r0, r0
0100296c: 3424       movs     r4, #0x34
0100296e: 0001       lsls     r0, r0, #4
01002970: ec29       cmp      r1, #0xec
01002972: 0001       lsls     r0, r0, #4
01002974: 0000       movs     r0, r0
01002976: 0020       movs     r0, #0
01002978: 4002       lsls     r0, r0, #9
0100297a: 0000       movs     r0, r0
0100297c: 3424       movs     r4, #0x34
0100297e: 0001       lsls     r0, r0, #4
01002980: 0000       movs     r0, r0
01002982: 0000       movs     r0, r0
01002984: 0000       movs     r0, r0
01002986: 0000       movs     r0, r0
01002988: 0000       movs     r0, r0
0100298a: 0000       movs     r0, r0
0100298c: 0000       movs     r0, r0
0100298e: 0000       movs     r0, r0
01002990: 0000       movs     r0, r0
01002992: 0000       movs     r0, r0
01002994: 0000       movs     r0, r0
01002996: 0000       movs     r0, r0
01002998: 0000       movs     r0, r0
0100299a: 0000       movs     r0, r0
0100299c: 0000       movs     r0, r0
0100299e: 0000       movs     r0, r0
010029a0: 0000       movs     r0, r0
010029a2: 0000       movs     r0, r0
010029a4: 0000       movs     r0, r0
010029a6: 0000       movs     r0, r0
010029a8: 0000       movs     r0, r0
010029aa: 0000       movs     r0, r0
010029ac: 0000       movs     r0, r0
010029ae: 0000       movs     r0, r0
010029b0: 0000       movs     r0, r0
010029b2: 0000       movs     r0, r0
010029b4: 0000       movs     r0, r0
010029b6: 0000       movs     r0, r0
010029b8: 0000       movs     r0, r0
010029ba: 0000       movs     r0, r0
010029bc: 0000       movs     r0, r0
010029be: 0000       movs     r0, r0
010029c0: 0000       movs     r0, r0
010029c2: 0000       movs     r0, r0
010029c4: 0000       movs     r0, r0
010029c6: 0000       movs     r0, r0
010029c8: 0000       movs     r0, r0
010029ca: 0000       movs     r0, r0
010029cc: 0000       movs     r0, r0
010029ce: 0000       movs     r0, r0
010029d0: 0000       movs     r0, r0
010029d2: 0000       movs     r0, r0
010029d4: 0000       movs     r0, r0
010029d6: 0000       movs     r0, r0
010029d8: 0000       movs     r0, r0
010029da: 0000       movs     r0, r0
010029dc: 0000       movs     r0, r0
010029de: 0000       movs     r0, r0
010029e0: 0000       movs     r0, r0
010029e2: 0000       movs     r0, r0
010029e4: 0000       movs     r0, r0
010029e6: 0000       movs     r0, r0
010029e8: 0000       movs     r0, r0
010029ea: 0000       movs     r0, r0
