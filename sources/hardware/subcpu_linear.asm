08000120: 00f002f8     bl        #0x8000128
08000124: 00f03cf8     bl        #0x80001a0
08000128: 0aa0         adr       r0, #0x28
0800012a: 90e8000c     ldm.w     r0, {sl, fp}
0800012e: 8244         add       sl, r0
08000130: 8344         add       fp, r0
08000132: aaf10107     sub.w     r7, sl, #1
08000136: da45         cmp       sl, fp
08000138: 01d1         bne       #0x800013e
0800013a: 00f031f8     bl        #0x80001a0
0800013e: aff2090e     subw      lr, pc, #9
08000142: bae80f00     ldm.w     sl!, {r0, r1, r2, r3}
08000146: 13f0010f     tst.w     r3, #1
0800014a: 18bf         it        ne
0800014c: fb1a         subne     r3, r7, r3
0800014e: 43f00103     orr       r3, r3, #1
08000152: 1847         bx        r3
08000154: e03d         subs      r5, #0xe0
08000156: 0000         movs      r0, r0
08000158: 003e         subs      r6, #0
0800015a: 0000         movs      r0, r0
0800015c: 103a         subs      r2, #0x10
0800015e: 24bf         itt       hs
08000160: 78c8         ldmhs     r0!, {r3, r4, r5, r6}
08000162: 78c1         stmhs     r1!, {r3, r4, r5, r6}
08000164: fad8         bhi       #0x800015c
08000166: 5207         lsls      r2, r2, #0x1d
08000168: 24bf         itt       hs
0800016a: 30c8         ldmhs     r0!, {r4, r5}
0800016c: 30c1         stmhs     r1!, {r4, r5}
0800016e: 44bf         itt       mi
08000170: 0468         ldrmi     r4, [r0]
08000172: 0c60         strmi     r4, [r1]
08000174: 7047         bx        lr
08000176: 0000         movs      r0, r0
08000178: 0023         movs      r3, #0
0800017a: 0024         movs      r4, #0
0800017c: 0025         movs      r5, #0
0800017e: 0026         movs      r6, #0
08000180: 103a         subs      r2, #0x10
08000182: 28bf         it        hs
08000184: 78c1         stmhs     r1!, {r3, r4, r5, r6}
08000186: fbd8         bhi       #0x8000180
08000188: 5207         lsls      r2, r2, #0x1d
0800018a: 28bf         it        hs
0800018c: 30c1         stmhs     r1!, {r4, r5}
0800018e: 48bf         it        mi
08000190: 0b60         strmi     r3, [r1]
08000192: 7047         bx        lr
08000194: 1fb5         push      {r0, r1, r2, r3, r4, lr}
08000196: 00f0e5f8     bl        #0x8000364
0800019a: 1fbd         pop       {r0, r1, r2, r3, r4, pc}
0800019c: 10b5         push      {r4, lr}
0800019e: 10bd         pop       {r4, pc}
080001a0: 00f01cf9     bl        #0x80003dc
080001a4: 1146         mov       r1, r2
080001a6: fff7f5ff     bl        #0x8000194
080001aa: 02f0c3fb     bl        #0x8002934
080001ae: 00f03af9     bl        #0x8000426
080001b2: 03b4         push      {r0, r1}
080001b4: fff7f2ff     bl        #0x800019c
080001b8: 03bc         pop       {r0, r1}
080001ba: 00f009f9     bl        #0x80003d0
080001be: 0000         movs      r0, r0
080001c0: 80f30988     msr       psp, r0
080001c4: 7047         bx        lr
080001c6: eff30980     mrs       r0, psp
080001ca: 7047         bx        lr
080001cc: 6846         mov       r0, sp
080001ce: 80f30988     msr       psp, r0
080001d2: 0448         ldr       r0, [pc, #0x10]
080001d4: 0078         ldrb      r0, [r0]
080001d6: c007         lsls      r0, r0, #0x1f
080001d8: 14bf         ite       ne
080001da: 0220         movne     r0, #2
080001dc: 0320         moveq     r0, #3
080001de: 80f31488     msr       control, r0
080001e2: 7047         bx        lr
080001e4: c83e         subs      r6, #0xc8
080001e6: 0008         lsrs      r0, r0, #0x20
080001e8: dff818c0     ldr.w     ip, [pc, #0x18]
080001ec: eff30583     mrs       r3, ipsr
080001f0: 1b06         lsls      r3, r3, #0x18
080001f2: 18bf         it        ne
080001f4: 6047         bxne      ip
080001f6: eff31483     mrs       r3, control
080001fa: db07         lsls      r3, r3, #0x1f
080001fc: 08bf         it        eq
080001fe: 6047         bxeq      ip
08000200: 00df         svc       #0
08000202: 7047         bx        lr
08000204: b929         cmp       r1, #0xb9
08000206: 0008         lsrs      r0, r0, #0x20
08000208: dff818c0     ldr.w     ip, [pc, #0x18]
0800020c: eff30583     mrs       r3, ipsr
08000210: 1b06         lsls      r3, r3, #0x18
08000212: 18bf         it        ne
08000214: 6047         bxne      ip
08000216: eff31483     mrs       r3, control
0800021a: db07         lsls      r3, r3, #0x1f
0800021c: 08bf         it        eq
0800021e: 6047         bxeq      ip
08000220: 00df         svc       #0
08000222: 7047         bx        lr
08000224: c52b         cmp       r3, #0xc5
08000226: 0008         lsrs      r0, r0, #0x20
08000228: eff30980     mrs       r0, psp
0800022c: 8169         ldr       r1, [r0, #0x18]
0800022e: 11f8021c     ldrb      r1, [r1, #-0x2]
08000232: 39bb         cbnz      r1, #0x8000284
08000234: 90e80f10     ldm.w     r0, {r0, r1, r2, r3, ip}
08000238: e047         blx       ip
0800023a: eff3098c     mrs       ip, psp
0800023e: 194b         ldr       r3, [pc, #0x64]
08000240: 93e80600     ldm.w     r3, {r1, r2}
08000244: 9142         cmp       r1, r2
08000246: 18d0         beq       #0x800027a
08000248: 59b1         cbz       r1, #0x8000262
0800024a: 0cb4         push      {r2, r3}
0800024c: 4ff00103     mov.w     r3, #1
08000250: 81f82130     strb.w    r3, [r1, #0x21]
08000254: 2ce9f00f     stmdb     ip!, {r4, r5, r6, r7, r8, sb, sl, fp}
08000258: c1f824c0     str.w     ip, [r1, #0x24]
0800025c: 02f04eff     bl        #0x80030fc
08000260: 0cbc         pop       {r2, r3}
08000262: 1a60         str       r2, [r3]
08000264: d2f824c0     ldr.w     ip, [r2, #0x24]
08000268: bce8f00f     ldm.w     ip!, {r4, r5, r6, r7, r8, sb, sl, fp}
0800026c: 92f82130     ldrb.w    r3, [r2, #0x21]
08000270: 8cf30988     msr       psp, ip
08000274: 1bb1         cbz       r3, #0x800027e
08000276: 92f82000     ldrb.w    r0, [r2, #0x20]
0800027a: ccf80000     str.w     r0, [ip]
0800027e: 6ff0020e     mvn       lr, #2
08000282: 7047         bx        lr
08000284: 10b5         push      {r4, lr}
08000286: 084a         ldr       r2, [pc, #0x20]
08000288: 1268         ldr       r2, [r2]
0800028a: 9142         cmp       r1, r2
0800028c: 09d8         bhi       #0x80002a2
0800028e: 074c         ldr       r4, [pc, #0x1c]
08000290: 54f82140     ldr.w     r4, [r4, r1, lsl #2]
08000294: 90e80f10     ldm.w     r0, {r0, r1, r2, r3, ip}
08000298: a047         blx       r4
0800029a: eff3098c     mrs       ip, psp
0800029e: 8ce80f00     stm.w     ip, {r0, r1, r2, r3}
080002a2: 10bd         pop       {r4, pc}
080002a4: 8000         lsls      r0, r0, #2
080002a6: 0020         movs      r0, #0
080002a8: 7404         lsls      r4, r6, #0x11
080002aa: 0008         lsrs      r0, r0, #0x20
080002ac: 7404         lsls      r4, r6, #0x11
080002ae: 0008         lsrs      r0, r0, #0x20
080002b0: 02f002fe     bl        #0x8002eb8
080002b4: 114b         ldr       r3, [pc, #0x44]
080002b6: 93e80600     ldm.w     r3, {r1, r2}
080002ba: 9142         cmp       r1, r2
080002bc: 1bd0         beq       #0x80002f6
080002be: 0cb4         push      {r2, r3}
080002c0: 4ff00003     mov.w     r3, #0
080002c4: 81f82130     strb.w    r3, [r1, #0x21]
080002c8: eff3098c     mrs       ip, psp
080002cc: 2ce9f00f     stmdb     ip!, {r4, r5, r6, r7, r8, sb, sl, fp}
080002d0: c1f824c0     str.w     ip, [r1, #0x24]
080002d4: 02f012ff     bl        #0x80030fc
080002d8: 0cbc         pop       {r2, r3}
080002da: 1a60         str       r2, [r3]
080002dc: d2f824c0     ldr.w     ip, [r2, #0x24]
080002e0: bce8f00f     ldm.w     ip!, {r4, r5, r6, r7, r8, sb, sl, fp}
080002e4: 8cf30988     msr       psp, ip
080002e8: 92f82130     ldrb.w    r3, [r2, #0x21]
080002ec: 1bb1         cbz       r3, #0x80002f6
080002ee: 92f82030     ldrb.w    r3, [r2, #0x20]
080002f2: ccf80030     str.w     r3, [ip]
080002f6: 6ff0020e     mvn       lr, #2
080002fa: 7047         bx        lr
080002fc: 8000         lsls      r0, r0, #2
080002fe: 0020         movs      r0, #0
08000300: 02f0ceff     bl        #0x80032a0
08000304: d6e7         b         #0x80002b4
08000306: 0000         movs      r0, r0
08000308: 02f054fb     bl        #0x80029b4
0800030c: 02f0c8ff     bl        #0x80032a0
08000310: d0e7         b         #0x80002b4
08000312: 0000         movs      r0, r0
08000314: 0948         ldr       r0, [pc, #0x24]
08000316: 8047         blx       r0
08000318: 0948         ldr       r0, [pc, #0x24]
0800031a: 0047         bx        r0
0800031c: fee7         b         #0x800031c
0800031e: fee7         b         #0x800031e
08000320: fee7         b         #0x8000320
08000322: fee7         b         #0x8000322
08000324: fee7         b         #0x8000324
08000326: fee7         b         #0x8000326
08000328: fee7         b         #0x8000328
0800032a: fee7         b         #0x800032a
0800032c: fee7         b         #0x800032c
0800032e: fee7         b         #0x800032e
08000330: 0448         ldr       r0, [pc, #0x10]
08000332: 0549         ldr       r1, [pc, #0x14]
08000334: 054a         ldr       r2, [pc, #0x14]
08000336: 064b         ldr       r3, [pc, #0x18]
08000338: 7047         bx        lr
0800033a: 0000         movs      r0, r0
0800033c: 650c         lsrs      r5, r4, #0x11
0800033e: 0008         lsrs      r0, r0, #0x20
08000340: 2101         lsls      r1, r4, #4
08000342: 0008         lsrs      r0, r0, #0x20
08000344: b00f         lsrs      r0, r6, #0x1e
08000346: 0020         movs      r0, #0
08000348: b015         asrs      r0, r6, #0x16
0800034a: 0020         movs      r0, #0
0800034c: b011         asrs      r0, r6, #6
0800034e: 0020         movs      r0, #0
08000350: b011         asrs      r0, r6, #6
08000352: 0020         movs      r0, #0
08000354: 0048         ldr       r0, [pc, #0]
08000356: 7047         bx        lr
08000358: 4c0f         lsrs      r4, r1, #0x1d
0800035a: 0020         movs      r0, #0
0800035c: 7047         bx        lr
0800035e: 7047         bx        lr
08000360: 7047         bx        lr
08000362: 0000         movs      r0, r0
08000364: 70b5         push      {r4, r5, r6, lr}
08000366: 064c         ldr       r4, [pc, #0x18]
08000368: 7c44         add       r4, pc
0800036a: 064d         ldr       r5, [pc, #0x18]
0800036c: 7d44         add       r5, pc
0800036e: 03e0         b         #0x8000378
08000370: 2068         ldr       r0, [r4]
08000372: 2044         add       r0, r4
08000374: 8047         blx       r0
08000376: 241d         adds      r4, r4, #4
08000378: ac42         cmp       r4, r5
0800037a: f9d1         bne       #0x8000370
0800037c: 70bd         pop       {r4, r5, r6, pc}
0800037e: 0000         movs      r0, r0
08000380: e83b         subs      r3, #0xe8
08000382: 0000         movs      r0, r0
08000384: 043c         subs      r4, #4
08000386: 0000         movs      r0, r0
08000388: 10b5         push      {r4, lr}
0800038a: 00f009f8     bl        #0x80003a0
0800038e: bde81040     pop.w     {r4, lr}
08000392: aff30080     nop.w     
08000396: 0028         cmp       r0, #0
08000398: 01d0         beq       #0x800039e
0800039a: 00f019b8     b.w       #0x80003d0
0800039e: 7047         bx        lr
080003a0: 10b5         push      {r4, lr}
080003a2: 0021         movs      r1, #0
080003a4: 02a0         adr       r0, #8
080003a6: 00f044f8     bl        #0x8000432
080003aa: 0120         movs      r0, #1
080003ac: 10bd         pop       {r4, pc}
080003ae: 0000         movs      r0, r0
080003b0: 5349         ldr       r1, [pc, #0x14c]
080003b2: 4750         str       r7, [r0, r1]
080003b4: 5646         mov       r6, sl
080003b6: 4e3a         subs      r2, #0x4e
080003b8: 2050         str       r0, [r4, r0]
080003ba: 7572         strb      r5, [r6, #9]
080003bc: 6520         movs      r0, #0x65
080003be: 7669         ldr       r6, [r6, #0x14]
080003c0: 7274         strb      r2, [r6, #0x11]
080003c2: 7561         str       r5, [r6, #0x14]
080003c4: 6c20         movs      r0, #0x6c
080003c6: 666e         ldr       r6, [r4, #0x64]
080003c8: 2063         str       r0, [r4, #0x30]
080003ca: 616c         ldr       r1, [r4, #0x44]
080003cc: 6c65         str       r4, [r5, #0x54]
080003ce: 6400         lsls      r4, r4, #1
080003d0: 0149         ldr       r1, [pc, #4]
080003d2: 1820         movs      r0, #0x18
080003d4: abbe         bkpt      #0xab
080003d6: fee7         b         #0x80003d6
080003d8: 2600         movs      r6, r4
080003da: 0200         movs      r2, r0
080003dc: 7546         mov       r5, lr
080003de: fff7b9ff     bl        #0x8000354
080003e2: ae46         mov       lr, r5
080003e4: 0500         movs      r5, r0
080003e6: 6946         mov       r1, sp
080003e8: 5346         mov       r3, sl
080003ea: 20f00700     bic       r0, r0, #7
080003ee: 8546         mov       sp, r0
080003f0: 18b0         add       sp, #0x60
080003f2: 20b5         push      {r5, lr}
080003f4: fff79cff     bl        #0x8000330
080003f8: bde82040     pop.w     {r5, lr}
080003fc: 4ff00006     mov.w     r6, #0
08000400: 4ff00007     mov.w     r7, #0
08000404: 4ff00008     mov.w     r8, #0
08000408: 4ff0000b     mov.w     fp, #0
0800040c: 21f00701     bic       r1, r1, #7
08000410: ac46         mov       ip, r5
08000412: ace8c009     stm.w     ip!, {r6, r7, r8, fp}
08000416: ace8c009     stm.w     ip!, {r6, r7, r8, fp}
0800041a: ace8c009     stm.w     ip!, {r6, r7, r8, fp}
0800041e: ace8c009     stm.w     ip!, {r6, r7, r8, fp}
08000422: 8d46         mov       sp, r1
08000424: 7047         bx        lr
08000426: 0446         mov       r4, r0
08000428: aff30080     nop.w     
0800042c: 2046         mov       r0, r4
0800042e: fff7c0fe     bl        #0x80001b2
08000432: 70b5         push      {r4, r5, r6, lr}
08000434: 0546         mov       r5, r0
08000436: 0c46         mov       r4, r1
08000438: 0a20         movs      r0, #0xa
0800043a: 00e0         b         #0x800043e
0800043c: 6d1c         adds      r5, r5, #1
0800043e: 00f011f8     bl        #0x8000464
08000442: 35b1         cbz       r5, #0x8000452
08000444: 2878         ldrb      r0, [r5]
08000446: 0028         cmp       r0, #0
08000448: f8d1         bne       #0x800043c
0800044a: 02e0         b         #0x8000452
0800044c: 641c         adds      r4, r4, #1
0800044e: 00f009f8     bl        #0x8000464
08000452: 14b1         cbz       r4, #0x800045a
08000454: 2078         ldrb      r0, [r4]
08000456: 0028         cmp       r0, #0
08000458: f8d1         bne       #0x800044c
0800045a: bde87040     pop.w     {r4, r5, r6, lr}
0800045e: 0a20         movs      r0, #0xa
08000460: aff30080     nop.w     
08000464: 08b5         push      {r3, lr}
08000466: 6946         mov       r1, sp
08000468: 8df80000     strb.w    r0, [sp]
0800046c: 0320         movs      r0, #3
0800046e: abbe         bkpt      #0xab
08000470: 08bd         pop       {r3, pc}
08000472: 7047         bx        lr
08000474: 0000         movs      r0, r0
08000476: 0000         movs      r0, r0
08000478: 0029         cmp       r1, #0
0800047a: 8168         ldr       r1, [r0, #8]
0800047c: 14bf         ite       ne
0800047e: 41f00101     orrne     r1, r1, #1
08000482: 21f00101     biceq     r1, r1, #1
08000486: 8160         str       r1, [r0, #8]
08000488: 7047         bx        lr
0800048a: 10b5         push      {r4, lr}
0800048c: a0f18041     sub.w     r1, r0, #0x40000000
08000490: b1f59231     subs.w    r1, r1, #0x12400
08000494: 0ad1         bne       #0x80004ac
08000496: 0121         movs      r1, #1
08000498: 4802         lsls      r0, r1, #9
0800049a: 00f057fb     bl        #0x8000b4c
0800049e: bde81040     pop.w     {r4, lr}
080004a2: 0021         movs      r1, #0
080004a4: 4ff40070     mov.w     r0, #0x200
080004a8: 00f050bb     b.w       #0x8000b4c
080004ac: a0f18041     sub.w     r1, r0, #0x40000000
080004b0: b1f59431     subs.w    r1, r1, #0x12800
080004b4: 0ad1         bne       #0x80004cc
080004b6: 0121         movs      r1, #1
080004b8: 8802         lsls      r0, r1, #0xa
080004ba: 00f047fb     bl        #0x8000b4c
080004be: bde81040     pop.w     {r4, lr}
080004c2: 0021         movs      r1, #0
080004c4: 4ff48060     mov.w     r0, #0x400
080004c8: 00f040bb     b.w       #0x8000b4c
080004cc: a0f18041     sub.w     r1, r0, #0x40000000
080004d0: b1f59e31     subs.w    r1, r1, #0x13c00
080004d4: 18bf         it        ne
080004d6: 10bd         popne     {r4, pc}
080004d8: 0121         movs      r1, #1
080004da: c803         lsls      r0, r1, #0xf
080004dc: 00f036fb     bl        #0x8000b4c
080004e0: bde81040     pop.w     {r4, lr}
080004e4: 0021         movs      r1, #0
080004e6: 4ff40040     mov.w     r0, #0x8000
080004ea: 00f02fbb     b.w       #0x8000b4c
080004ee: 0146         mov       r1, r0
080004f0: 0020         movs      r0, #0
080004f2: 8968         ldr       r1, [r1, #8]
080004f4: 11f0040f     tst.w     r1, #4
080004f8: 18bf         it        ne
080004fa: 0120         movne     r0, #1
080004fc: 7047         bx        lr
080004fe: c06c         ldr       r0, [r0, #0x4c]
08000500: 80b2         uxth      r0, r0
08000502: 7047         bx        lr
08000504: 0246         mov       r2, r0
08000506: 0020         movs      r0, #0
08000508: 1268         ldr       r2, [r2]
0800050a: 0a42         tst       r2, r1
0800050c: 18bf         it        ne
0800050e: 0120         movne     r0, #1
08000510: 7047         bx        lr
08000512: 0146         mov       r1, r0
08000514: 0020         movs      r0, #0
08000516: 8968         ldr       r1, [r1, #8]
08000518: 11f0080f     tst.w     r1, #8
0800051c: 18bf         it        ne
0800051e: 0120         movne     r0, #1
08000520: 7047         bx        lr
08000522: 0000         movs      r0, r0
08000524: 4268         ldr       r2, [r0, #4]
08000526: 91f804c0     ldrb.w    ip, [r1, #4]
0800052a: 22f48072     bic       r2, r2, #0x100
0800052e: 22f47022     bic       r2, r2, #0xf0000
08000532: 0b68         ldr       r3, [r1]
08000534: 42ea0c22     orr.w     r2, r2, ip, lsl #8
08000538: 1a43         orrs      r2, r3
0800053a: 4260         str       r2, [r0, #4]
0800053c: 8268         ldr       r2, [r0, #8]
0800053e: 0b4b         ldr       r3, [pc, #0x2c]
08000540: 1a40         ands      r2, r3
08000542: d1e902c3     ldrd      ip, r3, [r1, #8]
08000546: 43ea0c03     orr.w     r3, r3, ip
0800054a: 91f805c0     ldrb.w    ip, [r1, #5]
0800054e: 42ea4c02     orr.w     r2, r2, ip, lsl #1
08000552: 1a43         orrs      r2, r3
08000554: 8260         str       r2, [r0, #8]
08000556: c26a         ldr       r2, [r0, #0x2c]
08000558: 097c         ldrb      r1, [r1, #0x10]
0800055a: 22f47002     bic       r2, r2, #0xf00000
0800055e: 491e         subs      r1, r1, #1
08000560: c9b2         uxtb      r1, r1
08000562: 42ea0151     orr.w     r1, r2, r1, lsl #20
08000566: c162         str       r1, [r0, #0x2c]
08000568: 7047         bx        lr
0800056a: 0000         movs      r0, r0
0800056c: fdf7f1ff     bl        #0x7ffe552
08000570: 30b4         push      {r4, r5}
08000572: 0725         movs      r5, #7
08000574: 0929         cmp       r1, #9
08000576: 0cd9         bls       #0x8000592
08000578: c468         ldr       r4, [r0, #0xc]
0800057a: a1f10a0c     sub.w     ip, r1, #0xa
0800057e: 0ceb4c0c     add.w     ip, ip, ip, lsl #1
08000582: 05fa0cf5     lsl.w     r5, r5, ip
08000586: ac43         bics      r4, r5
08000588: 03fa0cf3     lsl.w     r3, r3, ip
0800058c: 2343         orrs      r3, r4
0800058e: c360         str       r3, [r0, #0xc]
08000590: 09e0         b         #0x80005a6
08000592: 0469         ldr       r4, [r0, #0x10]
08000594: 01eb410c     add.w     ip, r1, r1, lsl #1
08000598: 05fa0cf5     lsl.w     r5, r5, ip
0800059c: ac43         bics      r4, r5
0800059e: 03fa0cf3     lsl.w     r3, r3, ip
080005a2: 2343         orrs      r3, r4
080005a4: 0361         str       r3, [r0, #0x10]
080005a6: 4ff01f0c     mov.w     ip, #0x1f
080005aa: 072a         cmp       r2, #7
080005ac: 0cd2         bhs       #0x80005c8
080005ae: 436b         ldr       r3, [r0, #0x34]
080005b0: 521e         subs      r2, r2, #1
080005b2: 02eb8202     add.w     r2, r2, r2, lsl #2
080005b6: 0cfa02fc     lsl.w     ip, ip, r2
080005ba: 23ea0c03     bic.w     r3, r3, ip
080005be: 9140         lsls      r1, r2
080005c0: 1943         orrs      r1, r3
080005c2: 4163         str       r1, [r0, #0x34]
080005c4: 30bc         pop       {r4, r5}
080005c6: 7047         bx        lr
080005c8: 0d2a         cmp       r2, #0xd
080005ca: 0cd2         bhs       #0x80005e6
080005cc: 036b         ldr       r3, [r0, #0x30]
080005ce: d21f         subs      r2, r2, #7
080005d0: 02eb8202     add.w     r2, r2, r2, lsl #2
080005d4: 0cfa02fc     lsl.w     ip, ip, r2
080005d8: 23ea0c03     bic.w     r3, r3, ip
080005dc: 9140         lsls      r1, r2
080005de: 1943         orrs      r1, r3
080005e0: 0163         str       r1, [r0, #0x30]
080005e2: 30bc         pop       {r4, r5}
080005e4: 7047         bx        lr
080005e6: c36a         ldr       r3, [r0, #0x2c]
080005e8: 0d3a         subs      r2, #0xd
080005ea: 02eb8202     add.w     r2, r2, r2, lsl #2
080005ee: 0cfa02fc     lsl.w     ip, ip, r2
080005f2: 23ea0c03     bic.w     r3, r3, ip
080005f6: 9140         lsls      r1, r2
080005f8: 1943         orrs      r1, r3
080005fa: c162         str       r1, [r0, #0x2c]
080005fc: 30bc         pop       {r4, r5}
080005fe: 7047         bx        lr
08000600: 8168         ldr       r1, [r0, #8]
08000602: 41f00801     orr       r1, r1, #8
08000606: 8160         str       r1, [r0, #8]
08000608: 7047         bx        lr
0800060a: 0029         cmp       r1, #0
0800060c: 8168         ldr       r1, [r0, #8]
0800060e: 14bf         ite       ne
08000610: 41f4a001     orrne     r1, r1, #0x500000
08000614: 21f4a001     biceq     r1, r1, #0x500000
08000618: 8160         str       r1, [r0, #8]
0800061a: 7047         bx        lr
0800061c: 8168         ldr       r1, [r0, #8]
0800061e: 41f00401     orr       r1, r1, #4
08000622: 8160         str       r1, [r0, #8]
08000624: 7047         bx        lr
08000626: 0021         movs      r1, #0
08000628: 0160         str       r1, [r0]
0800062a: 0171         strb      r1, [r0, #4]
0800062c: 4171         strb      r1, [r0, #5]
0800062e: 8160         str       r1, [r0, #8]
08000630: c160         str       r1, [r0, #0xc]
08000632: 0121         movs      r1, #1
08000634: 0174         strb      r1, [r0, #0x10]
08000636: 7047         bx        lr
08000638: 10b5         push      {r4, lr}
0800063a: 194c         ldr       r4, [pc, #0x64]
0800063c: 86b0         sub       sp, #0x18
0800063e: 0021         movs      r1, #0
08000640: 2046         mov       r0, r4
08000642: fff719ff     bl        #0x8000478
08000646: 2046         mov       r0, r4
08000648: fff71fff     bl        #0x800048a
0800064c: 6846         mov       r0, sp
0800064e: fff7eaff     bl        #0x8000626
08000652: 0022         movs      r2, #0
08000654: 4ff46021     mov.w     r1, #0xe0000
08000658: cde90212     strd      r1, r2, [sp, #8]
0800065c: 0121         movs      r1, #1
0800065e: 8df80420     strb.w    r2, [sp, #4]
08000662: 8df81010     strb.w    r1, [sp, #0x10]
08000666: 0092         str       r2, [sp]
08000668: 8df80520     strb.w    r2, [sp, #5]
0800066c: 6946         mov       r1, sp
0800066e: 2046         mov       r0, r4
08000670: fff758ff     bl        #0x8000524
08000674: 0121         movs      r1, #1
08000676: 2046         mov       r0, r4
08000678: fff7fefe     bl        #0x8000478
0800067c: 2046         mov       r0, r4
0800067e: fff7bfff     bl        #0x8000600
08000682: 2046         mov       r0, r4
08000684: fff745ff     bl        #0x8000512
08000688: 0028         cmp       r0, #0
0800068a: fad1         bne       #0x8000682
0800068c: 2046         mov       r0, r4
0800068e: fff7c5ff     bl        #0x800061c
08000692: 2046         mov       r0, r4
08000694: fff72bff     bl        #0x80004ee
08000698: 0028         cmp       r0, #0
0800069a: fad1         bne       #0x8000692
0800069c: 06b0         add       sp, #0x18
0800069e: 10bd         pop       {r4, pc}
080006a0: 0024         movs      r4, #0
080006a2: 0140         ands      r1, r0
080006a4: fee7         b         #0x80006a4
080006a6: 10b5         push      {r4, lr}
080006a8: 0121         movs      r1, #1
080006aa: 0846         mov       r0, r1
080006ac: 00f04efa     bl        #0x8000b4c
080006b0: 0021         movs      r1, #0
080006b2: bde81040     pop.w     {r4, lr}
080006b6: 0120         movs      r0, #1
080006b8: 00f048ba     b.w       #0x8000b4c
080006bc: 10b5         push      {r4, lr}
080006be: a0f18041     sub.w     r1, r0, #0x40000000
080006c2: b1f58431     subs.w    r1, r1, #0x10800
080006c6: 09d1         bne       #0x80006dc
080006c8: 0121         movs      r1, #1
080006ca: 0420         movs      r0, #4
080006cc: 00f03efa     bl        #0x8000b4c
080006d0: 0021         movs      r1, #0
080006d2: bde81040     pop.w     {r4, lr}
080006d6: 0420         movs      r0, #4
080006d8: 00f038ba     b.w       #0x8000b4c
080006dc: a0f18041     sub.w     r1, r0, #0x40000000
080006e0: b1f58631     subs.w    r1, r1, #0x10c00
080006e4: 09d1         bne       #0x80006fa
080006e6: 0121         movs      r1, #1
080006e8: 0820         movs      r0, #8
080006ea: 00f02ffa     bl        #0x8000b4c
080006ee: 0021         movs      r1, #0
080006f0: bde81040     pop.w     {r4, lr}
080006f4: 0820         movs      r0, #8
080006f6: 00f029ba     b.w       #0x8000b4c
080006fa: a0f18041     sub.w     r1, r0, #0x40000000
080006fe: b1f58831     subs.w    r1, r1, #0x11000
08000702: 09d1         bne       #0x8000718
08000704: 0121         movs      r1, #1
08000706: 1020         movs      r0, #0x10
08000708: 00f020fa     bl        #0x8000b4c
0800070c: 0021         movs      r1, #0
0800070e: bde81040     pop.w     {r4, lr}
08000712: 1020         movs      r0, #0x10
08000714: 00f01aba     b.w       #0x8000b4c
08000718: a0f18041     sub.w     r1, r0, #0x40000000
0800071c: b1f58a31     subs.w    r1, r1, #0x11400
08000720: 09d1         bne       #0x8000736
08000722: 0121         movs      r1, #1
08000724: 2020         movs      r0, #0x20
08000726: 00f011fa     bl        #0x8000b4c
0800072a: 0021         movs      r1, #0
0800072c: bde81040     pop.w     {r4, lr}
08000730: 2020         movs      r0, #0x20
08000732: 00f00bba     b.w       #0x8000b4c
08000736: a0f18041     sub.w     r1, r0, #0x40000000
0800073a: b1f58c31     subs.w    r1, r1, #0x11800
0800073e: 09d1         bne       #0x8000754
08000740: 0121         movs      r1, #1
08000742: 4020         movs      r0, #0x40
08000744: 00f002fa     bl        #0x8000b4c
08000748: 0021         movs      r1, #0
0800074a: bde81040     pop.w     {r4, lr}
0800074e: 4020         movs      r0, #0x40
08000750: 00f0fcb9     b.w       #0x8000b4c
08000754: a0f18041     sub.w     r1, r0, #0x40000000
08000758: b1f58e31     subs.w    r1, r1, #0x11c00
0800075c: 09d1         bne       #0x8000772
0800075e: 0121         movs      r1, #1
08000760: 8020         movs      r0, #0x80
08000762: 00f0f3f9     bl        #0x8000b4c
08000766: 0021         movs      r1, #0
08000768: bde81040     pop.w     {r4, lr}
0800076c: 8020         movs      r0, #0x80
0800076e: 00f0edb9     b.w       #0x8000b4c
08000772: a0f18041     sub.w     r1, r0, #0x40000000
08000776: b1f59031     subs.w    r1, r1, #0x12000
0800077a: 18bf         it        ne
0800077c: 10bd         popne     {r4, pc}
0800077e: 0121         movs      r1, #1
08000780: 0802         lsls      r0, r1, #8
08000782: 00f0e3f9     bl        #0x8000b4c
08000786: bde81040     pop.w     {r4, lr}
0800078a: 0021         movs      r1, #0
0800078c: 4ff48070     mov.w     r0, #0x100
08000790: 00f0dcb9     b.w       #0x8000b4c
08000794: 2de9f001     push.w    {r4, r5, r6, r7, r8}
08000798: 91f803c0     ldrb.w    ip, [r1, #3]
0800079c: 0022         movs      r2, #0
0800079e: 0cf00f03     and       r3, ip, #0xf
080007a2: 1cf0100f     tst.w     ip, #0x10
080007a6: 1cbf         itt       ne
080007a8: 91f802c0     ldrbne.w  ip, [r1, #2]
080007ac: 4cea0303     orrne.w   r3, ip, r3
080007b0: 91f800c0     ldrb.w    ip, [r1]
080007b4: 0f27         movs      r7, #0xf
080007b6: 0126         movs      r6, #1
080007b8: bcf1000f     cmp.w     ip, #0
080007bc: 18bf         it        ne
080007be: 0468         ldrne     r4, [r0]
080007c0: 1cd0         beq       #0x80007fc
080007c2: 0d88         ldrh      r5, [r1]
080007c4: 06fa02fc     lsl.w     ip, r6, r2
080007c8: 05ea0c05     and.w     r5, r5, ip
080007cc: 6545         cmp       r5, ip
080007ce: 11d1         bne       #0x80007f4
080007d0: 9500         lsls      r5, r2, #2
080007d2: 07fa05f8     lsl.w     r8, r7, r5
080007d6: 24ea0804     bic.w     r4, r4, r8
080007da: 03fa05f5     lsl.w     r5, r3, r5
080007de: 2c43         orrs      r4, r5
080007e0: cd78         ldrb      r5, [r1, #3]
080007e2: 282d         cmp       r5, #0x28
080007e4: 08bf         it        eq
080007e6: c0f814c0     streq.w   ip, [r0, #0x14]
080007ea: 03d0         beq       #0x80007f4
080007ec: 482d         cmp       r5, #0x48
080007ee: 08bf         it        eq
080007f0: c0f810c0     streq.w   ip, [r0, #0x10]
080007f4: 521c         adds      r2, r2, #1
080007f6: 082a         cmp       r2, #8
080007f8: e3d3         blo       #0x80007c2
080007fa: 0460         str       r4, [r0]
080007fc: 0a88         ldrh      r2, [r1]
080007fe: ff2a         cmp       r2, #0xff
08000800: 87bf         ittee     hi
08000802: 4468         ldrhi     r4, [r0, #4]
08000804: 0022         movhi     r2, #0
08000806: bde8f001     popls.w   {r4, r5, r6, r7, r8}
0800080a: 7047         bxls      lr
0800080c: 02f1080c     add.w     ip, r2, #8
08000810: 0d88         ldrh      r5, [r1]
08000812: 06fa0cfc     lsl.w     ip, r6, ip
08000816: 05ea0c05     and.w     r5, r5, ip
0800081a: 6545         cmp       r5, ip
0800081c: 11d1         bne       #0x8000842
0800081e: 9500         lsls      r5, r2, #2
08000820: 07fa05f8     lsl.w     r8, r7, r5
08000824: 24ea0804     bic.w     r4, r4, r8
08000828: 03fa05f5     lsl.w     r5, r3, r5
0800082c: 2c43         orrs      r4, r5
0800082e: cd78         ldrb      r5, [r1, #3]
08000830: 282d         cmp       r5, #0x28
08000832: 08bf         it        eq
08000834: c0f814c0     streq.w   ip, [r0, #0x14]
08000838: cd78         ldrb      r5, [r1, #3]
0800083a: 482d         cmp       r5, #0x48
0800083c: 08bf         it        eq
0800083e: c0f810c0     streq.w   ip, [r0, #0x10]
08000842: 521c         adds      r2, r2, #1
08000844: 082a         cmp       r2, #8
08000846: e1d3         blo       #0x800080c
08000848: 4460         str       r4, [r0, #4]
0800084a: bde8f001     pop.w     {r4, r5, r6, r7, r8}
0800084e: 7047         bx        lr
08000850: 0246         mov       r2, r0
08000852: 0020         movs      r0, #0
08000854: 9268         ldr       r2, [r2, #8]
08000856: 0a42         tst       r2, r1
08000858: 18bf         it        ne
0800085a: 0120         movne     r0, #1
0800085c: 7047         bx        lr
0800085e: 0246         mov       r2, r0
08000860: 0020         movs      r0, #0
08000862: d268         ldr       r2, [r2, #0xc]
08000864: 0a42         tst       r2, r1
08000866: 18bf         it        ne
08000868: 0120         movne     r0, #1
0800086a: 7047         bx        lr
0800086c: 4161         str       r1, [r0, #0x14]
0800086e: 7047         bx        lr
08000870: 0161         str       r1, [r0, #0x10]
08000872: 7047         bx        lr
08000874: 4ff6ff71     movw      r1, #0xffff
08000878: 0180         strh      r1, [r0]
0800087a: 0221         movs      r1, #2
0800087c: 8170         strb      r1, [r0, #2]
0800087e: 0421         movs      r1, #4
08000880: c170         strb      r1, [r0, #3]
08000882: 7047         bx        lr
08000884: f8b5         push      {r3, r4, r5, r6, r7, lr}
08000886: fff70eff     bl        #0x80006a6
0800088a: 654f         ldr       r7, [pc, #0x194]
0800088c: 3846         mov       r0, r7
0800088e: fff715ff     bl        #0x80006bc
08000892: 6846         mov       r0, sp
08000894: fff7eeff     bl        #0x8000874
08000898: 7815         asrs      r0, r7, #0x15
0800089a: adf80000     strh.w    r0, [sp]
0800089e: 0224         movs      r4, #2
080008a0: 8df80240     strb.w    r4, [sp, #2]
080008a4: 1820         movs      r0, #0x18
080008a6: 8df80300     strb.w    r0, [sp, #3]
080008aa: 6946         mov       r1, sp
080008ac: 3846         mov       r0, r7
080008ae: fff771ff     bl        #0x8000794
080008b2: 6846         mov       r0, sp
080008b4: fff7deff     bl        #0x8000874
080008b8: 6002         lsls      r0, r4, #9
080008ba: adf80000     strh.w    r0, [sp]
080008be: 8df80240     strb.w    r4, [sp, #2]
080008c2: 0425         movs      r5, #4
080008c4: 8df80350     strb.w    r5, [sp, #3]
080008c8: 6946         mov       r1, sp
080008ca: 3846         mov       r0, r7
080008cc: fff762ff     bl        #0x8000794
080008d0: 6846         mov       r0, sp
080008d2: fff7cfff     bl        #0x8000874
080008d6: 0f20         movs      r0, #0xf
080008d8: adf80000     strh.w    r0, [sp]
080008dc: 8df80240     strb.w    r4, [sp, #2]
080008e0: 0020         movs      r0, #0
080008e2: 8df80300     strb.w    r0, [sp, #3]
080008e6: 6946         mov       r1, sp
080008e8: 3846         mov       r0, r7
080008ea: fff753ff     bl        #0x8000794
080008ee: 6846         mov       r0, sp
080008f0: fff7c0ff     bl        #0x8000874
080008f4: f020         movs      r0, #0xf0
080008f6: adf80000     strh.w    r0, [sp]
080008fa: 8df80240     strb.w    r4, [sp, #2]
080008fe: 1026         movs      r6, #0x10
08000900: 8df80360     strb.w    r6, [sp, #3]
08000904: 6946         mov       r1, sp
08000906: 3846         mov       r0, r7
08000908: fff744ff     bl        #0x8000794
0800090c: 454f         ldr       r7, [pc, #0x114]
0800090e: 3846         mov       r0, r7
08000910: fff7d4fe     bl        #0x80006bc
08000914: 6846         mov       r0, sp
08000916: fff7adff     bl        #0x8000874
0800091a: 40f2e310     movw      r0, #0x1e3
0800091e: adf80000     strh.w    r0, [sp]
08000922: 8df80240     strb.w    r4, [sp, #2]
08000926: 8df80360     strb.w    r6, [sp, #3]
0800092a: 6946         mov       r1, sp
0800092c: 3846         mov       r0, r7
0800092e: fff731ff     bl        #0x8000794
08000932: 6846         mov       r0, sp
08000934: fff79eff     bl        #0x8000874
08000938: 4ff47040     mov.w     r0, #0xf000
0800093c: adf80000     strh.w    r0, [sp]
08000940: 8df80240     strb.w    r4, [sp, #2]
08000944: 8df80350     strb.w    r5, [sp, #3]
08000948: 6946         mov       r1, sp
0800094a: 3846         mov       r0, r7
0800094c: fff722ff     bl        #0x8000794
08000950: 354f         ldr       r7, [pc, #0xd4]
08000952: 3846         mov       r0, r7
08000954: fff7b2fe     bl        #0x80006bc
08000958: 6846         mov       r0, sp
0800095a: fff78bff     bl        #0x8000874
0800095e: 40f20f40     movw      r0, #0x40f
08000962: adf80000     strh.w    r0, [sp]
08000966: 8df80240     strb.w    r4, [sp, #2]
0800096a: 8df80360     strb.w    r6, [sp, #3]
0800096e: 6946         mov       r1, sp
08000970: 3846         mov       r0, r7
08000972: fff70fff     bl        #0x8000794
08000976: 6846         mov       r0, sp
08000978: fff77cff     bl        #0x8000874
0800097c: 4ff47070     mov.w     r0, #0x3c0
08000980: adf80000     strh.w    r0, [sp]
08000984: 8df80240     strb.w    r4, [sp, #2]
08000988: 8df80350     strb.w    r5, [sp, #3]
0800098c: 6946         mov       r1, sp
0800098e: 3846         mov       r0, r7
08000990: fff700ff     bl        #0x8000794
08000994: 254f         ldr       r7, [pc, #0x94]
08000996: 3846         mov       r0, r7
08000998: fff790fe     bl        #0x80006bc
0800099c: 6846         mov       r0, sp
0800099e: fff769ff     bl        #0x8000874
080009a2: 4ff6c040     movw      r0, #0xfcc0
080009a6: adf80000     strh.w    r0, [sp]
080009aa: 8df80240     strb.w    r4, [sp, #2]
080009ae: 8df80360     strb.w    r6, [sp, #3]
080009b2: 6946         mov       r1, sp
080009b4: 3846         mov       r0, r7
080009b6: fff7edfe     bl        #0x8000794
080009ba: 6846         mov       r0, sp
080009bc: fff75aff     bl        #0x8000874
080009c0: 40f23f30     movw      r0, #0x33f
080009c4: adf80000     strh.w    r0, [sp]
080009c8: 8df80240     strb.w    r4, [sp, #2]
080009cc: 8df80350     strb.w    r5, [sp, #3]
080009d0: 6946         mov       r1, sp
080009d2: 3846         mov       r0, r7
080009d4: fff7defe     bl        #0x8000794
080009d8: 154f         ldr       r7, [pc, #0x54]
080009da: 3846         mov       r0, r7
080009dc: fff76efe     bl        #0x80006bc
080009e0: 6846         mov       r0, sp
080009e2: fff747ff     bl        #0x8000874
080009e6: 4ff67000     movw      r0, #0xf870
080009ea: adf80000     strh.w    r0, [sp]
080009ee: 8df80240     strb.w    r4, [sp, #2]
080009f2: 8df80360     strb.w    r6, [sp, #3]
080009f6: 6946         mov       r1, sp
080009f8: 3846         mov       r0, r7
080009fa: fff7cbfe     bl        #0x8000794
080009fe: 6846         mov       r0, sp
08000a00: fff738ff     bl        #0x8000874
08000a04: 4ff4f060     mov.w     r0, #0x780
08000a08: adf80000     strh.w    r0, [sp]
08000a0c: 8df80240     strb.w    r4, [sp, #2]
08000a10: 8df80350     strb.w    r5, [sp, #3]
08000a14: 6946         mov       r1, sp
08000a16: 3846         mov       r0, r7
08000a18: fff7bcfe     bl        #0x8000794
08000a1c: f8bd         pop       {r3, r4, r5, r6, r7, pc}
08000a1e: 0000         movs      r0, r0
08000a20: 0008         lsrs      r0, r0, #0x20
08000a22: 0140         ands      r1, r0
08000a24: 000c         lsrs      r0, r0, #0x10
08000a26: 0140         ands      r1, r0
08000a28: 0010         asrs      r0, r0, #0x20
08000a2a: 0140         ands      r1, r0
08000a2c: 0014         asrs      r0, r0, #0x10
08000a2e: 0140         ands      r1, r0
08000a30: 0018         adds      r0, r0, r0
08000a32: 0140         ands      r1, r0
08000a34: fee7         b         #0x8000a34
08000a36: 38b5         push      {r3, r4, r5, lr}
08000a38: 4ff4a060     mov.w     r0, #0x500
08000a3c: 00f05af8     bl        #0x8000af4
08000a40: 2520         movs      r0, #0x25
08000a42: 8df80000     strb.w    r0, [sp]
08000a46: 0024         movs      r4, #0
08000a48: 8df80140     strb.w    r4, [sp, #1]
08000a4c: 8df80240     strb.w    r4, [sp, #2]
08000a50: 8df80340     strb.w    r4, [sp, #3]
08000a54: 6846         mov       r0, sp
08000a56: 00f011f8     bl        #0x8000a7c
08000a5a: 1920         movs      r0, #0x19
08000a5c: 8df80000     strb.w    r0, [sp]
08000a60: 0120         movs      r0, #1
08000a62: 8df80100     strb.w    r0, [sp, #1]
08000a66: 8df80240     strb.w    r4, [sp, #2]
08000a6a: 8df80340     strb.w    r4, [sp, #3]
08000a6e: 6846         mov       r0, sp
08000a70: 00f004f8     bl        #0x8000a7c
08000a74: 38bd         pop       {r3, r4, r5, pc}
08000a76: fee7         b         #0x8000a76
08000a78: fee7         b         #0x8000a78
08000a7a: 0000         movs      r0, r0
08000a7c: 30b4         push      {r4, r5}
08000a7e: c278         ldrb      r2, [r0, #3]
08000a80: 0178         ldrb      r1, [r0]
08000a82: 4ff00f0c     mov.w     ip, #0xf
08000a86: 0124         movs      r4, #1
08000a88: 4ff0e025     mov.w     r5, #-0x1fff2000
08000a8c: 12b3         cbz       r2, #0x8000ad4
08000a8e: 174a         ldr       r2, [pc, #0x5c]
08000a90: 1268         ldr       r2, [r2]
08000a92: 02f4e062     and       r2, r2, #0x700
08000a96: c2f5e062     rsb.w     r2, r2, #0x700
08000a9a: 120a         lsrs      r2, r2, #8
08000a9c: c2f10403     rsb.w     r3, r2, #4
08000aa0: 2cfa02f2     lsr.w     r2, ip, r2
08000aa4: 90f801c0     ldrb.w    ip, [r0, #1]
08000aa8: 0cfa03f3     lsl.w     r3, ip, r3
08000aac: 90f802c0     ldrb.w    ip, [r0, #2]
08000ab0: 0cea0202     and.w     r2, ip, r2
08000ab4: 1a43         orrs      r2, r3
08000ab6: 0e4b         ldr       r3, [pc, #0x38]
08000ab8: 1201         lsls      r2, r2, #4
08000aba: ca54         strb      r2, [r1, r3]
08000abc: 0078         ldrb      r0, [r0]
08000abe: 00f01f01     and       r1, r0, #0x1f
08000ac2: 04fa01f1     lsl.w     r1, r4, r1
08000ac6: 4009         lsrs      r0, r0, #5
08000ac8: 05eb8000     add.w     r0, r5, r0, lsl #2
08000acc: c0f80011     str.w     r1, [r0, #0x100]
08000ad0: 30bc         pop       {r4, r5}
08000ad2: 7047         bx        lr
08000ad4: 01f01f00     and       r0, r1, #0x1f
08000ad8: 04fa00f0     lsl.w     r0, r4, r0
08000adc: 4909         lsrs      r1, r1, #5
08000ade: 05eb8101     add.w     r1, r5, r1, lsl #2
08000ae2: c1f88001     str.w     r0, [r1, #0x180]
08000ae6: 30bc         pop       {r4, r5}
08000ae8: 7047         bx        lr
08000aea: 0000         movs      r0, r0
08000aec: 0ced00e0     stc       p0, c14, [ip, #-0]
08000af0: 00e4         b         #0x80002f4
08000af2: 00e0         b         #0x8000af6
08000af4: 0349         ldr       r1, [pc, #0xc]
08000af6: 40f0fd70     orr       r0, r0, #0x1fa0000
08000afa: 40f08060     orr       r0, r0, #0x4000000
08000afe: 0860         str       r0, [r1]
08000b00: 7047         bx        lr
08000b02: 0000         movs      r0, r0
08000b04: 0ced00e0     stc       p0, c14, [ip, #-0]
08000b08: 034a         ldr       r2, [pc, #0xc]
08000b0a: 5168         ldr       r1, [r2, #4]
08000b0c: 21f44041     bic       r1, r1, #0xc000
08000b10: 0843         orrs      r0, r1
08000b12: 5060         str       r0, [r2, #4]
08000b14: 7047         bx        lr
08000b16: 0000         movs      r0, r0
08000b18: 0010         asrs      r0, r0, #0x20
08000b1a: 0240         ands      r2, r0
08000b1c: 044a         ldr       r2, [pc, #0x10]
08000b1e: 0029         cmp       r1, #0
08000b20: 1169         ldr       r1, [r2, #0x10]
08000b22: 14bf         ite       ne
08000b24: 0843         orrne     r0, r1
08000b26: 21ea0000     biceq.w   r0, r1, r0
08000b2a: 1061         str       r0, [r2, #0x10]
08000b2c: 7047         bx        lr
08000b2e: 0000         movs      r0, r0
08000b30: 0010         asrs      r0, r0, #0x20
08000b32: 0240         ands      r2, r0
08000b34: 044a         ldr       r2, [pc, #0x10]
08000b36: 0029         cmp       r1, #0
08000b38: 9169         ldr       r1, [r2, #0x18]
08000b3a: 14bf         ite       ne
08000b3c: 0843         orrne     r0, r1
08000b3e: 21ea0000     biceq.w   r0, r1, r0
08000b42: 9061         str       r0, [r2, #0x18]
08000b44: 7047         bx        lr
08000b46: 0000         movs      r0, r0
08000b48: 0010         asrs      r0, r0, #0x20
08000b4a: 0240         ands      r2, r0
08000b4c: 044a         ldr       r2, [pc, #0x10]
08000b4e: 0029         cmp       r1, #0
08000b50: d168         ldr       r1, [r2, #0xc]
08000b52: 14bf         ite       ne
08000b54: 0843         orrne     r0, r1
08000b56: 21ea0000     biceq.w   r0, r1, r0
08000b5a: d060         str       r0, [r2, #0xc]
08000b5c: 7047         bx        lr
08000b5e: 0000         movs      r0, r0
08000b60: 0010         asrs      r0, r0, #0x20
08000b62: 0240         ands      r2, r0
08000b64: 274a         ldr       r2, [pc, #0x9c]
08000b66: 10b4         push      {r4}
08000b68: 5168         ldr       r1, [r2, #4]
08000b6a: 274b         ldr       r3, [pc, #0x9c]
08000b6c: 11f00c01     ands      r1, r1, #0xc
08000b70: 08d0         beq       #0x8000b84
08000b72: dff898c0     ldr.w     ip, [pc, #0x98]
08000b76: 0429         cmp       r1, #4
08000b78: 08bf         it        eq
08000b7a: c0f800c0     streq.w   ip, [r0]
08000b7e: 19d0         beq       #0x8000bb4
08000b80: 0829         cmp       r1, #8
08000b82: 01d0         beq       #0x8000b88
08000b84: 0360         str       r3, [r0]
08000b86: 15e0         b         #0x8000bb4
08000b88: 5168         ldr       r1, [r2, #4]
08000b8a: 5368         ldr       r3, [r2, #4]
08000b8c: 01f47011     and       r1, r1, #0x3c0000
08000b90: 4ff00204     mov.w     r4, #2
08000b94: 13f4803f     tst.w     r3, #0x10000
08000b98: 04eb9141     add.w     r1, r4, r1, lsr #18
08000b9c: 04bf         itt       eq
08000b9e: 1c4b         ldreq     r3, [pc, #0x70]
08000ba0: 5943         muleq     r1, r3, r1
08000ba2: 06d0         beq       #0x8000bb2
08000ba4: d36a         ldr       r3, [r2, #0x2c]
08000ba6: 03f00f03     and       r3, r3, #0xf
08000baa: 5b1c         adds      r3, r3, #1
08000bac: bcfbf3f3     udiv      r3, ip, r3
08000bb0: 5943         muls      r1, r3, r1
08000bb2: 0160         str       r1, [r0]
08000bb4: 5168         ldr       r1, [r2, #4]
08000bb6: 0f23         movs      r3, #0xf
08000bb8: dff858c0     ldr.w     ip, [pc, #0x58]
08000bbc: 03ea1111     and.w     r1, r3, r1, lsr #4
08000bc0: 1cf80110     ldrb.w    r1, [ip, r1]
08000bc4: 0368         ldr       r3, [r0]
08000bc6: 23fa01f1     lsr.w     r1, r3, r1
08000bca: 4160         str       r1, [r0, #4]
08000bcc: 5368         ldr       r3, [r2, #4]
08000bce: 0724         movs      r4, #7
08000bd0: 04ea1323     and.w     r3, r4, r3, lsr #8
08000bd4: 1cf80330     ldrb.w    r3, [ip, r3]
08000bd8: 21fa03f3     lsr.w     r3, r1, r3
08000bdc: 8360         str       r3, [r0, #8]
08000bde: 5368         ldr       r3, [r2, #4]
08000be0: 04ead323     and.w     r3, r4, r3, lsr #11
08000be4: 1cf80330     ldrb.w    r3, [ip, r3]
08000be8: d940         lsrs      r1, r3
08000bea: c160         str       r1, [r0, #0xc]
08000bec: 5268         ldr       r2, [r2, #4]
08000bee: 0323         movs      r3, #3
08000bf0: 03ea9232     and.w     r2, r3, r2, lsr #14
08000bf4: acf10403     sub.w     r3, ip, #4
08000bf8: 9a5c         ldrb      r2, [r3, r2]
08000bfa: b1fbf2f1     udiv      r1, r1, r2
08000bfe: 0161         str       r1, [r0, #0x10]
08000c00: 10bc         pop       {r4}
08000c02: 7047         bx        lr
08000c04: 0010         asrs      r0, r0, #0x20
08000c06: 0240         ands      r2, r0
08000c08: 0012         asrs      r0, r0, #8
08000c0a: 7a00         lsls      r2, r7, #1
08000c0c: 0036         adds      r6, #0
08000c0e: 6e01         lsls      r6, r5, #5
08000c10: 0009         lsrs      r0, r0, #4
08000c12: 3d00         movs      r5, r7
08000c14: 7000         lsls      r0, r6, #1
08000c16: 0020         movs      r0, #0
08000c18: 10b5         push      {r4, lr}
08000c1a: 0020         movs      r0, #0
08000c1c: fff774ff     bl        #0x8000b08
08000c20: 0121         movs      r1, #1
08000c22: 0420         movs      r0, #4
08000c24: fff786ff     bl        #0x8000b34
08000c28: 0121         movs      r1, #1
08000c2a: 0820         movs      r0, #8
08000c2c: fff782ff     bl        #0x8000b34
08000c30: 0121         movs      r1, #1
08000c32: 1020         movs      r0, #0x10
08000c34: fff77eff     bl        #0x8000b34
08000c38: 0121         movs      r1, #1
08000c3a: 2020         movs      r0, #0x20
08000c3c: fff77aff     bl        #0x8000b34
08000c40: 0121         movs      r1, #1
08000c42: 4020         movs      r0, #0x40
08000c44: fff776ff     bl        #0x8000b34
08000c48: 0121         movs      r1, #1
08000c4a: c802         lsls      r0, r1, #0xb
08000c4c: fff772ff     bl        #0x8000b34
08000c50: 0121         movs      r1, #1
08000c52: 8803         lsls      r0, r1, #0xe
08000c54: fff76eff     bl        #0x8000b34
08000c58: 0121         movs      r1, #1
08000c5a: bde81040     pop.w     {r4, lr}
08000c5e: 4802         lsls      r0, r1, #9
08000c60: fff768bf     b.w       #0x8000b34
08000c64: 3048         ldr       r0, [pc, #0xc0]
08000c66: 82b0         sub       sp, #8
08000c68: 0168         ldr       r1, [r0]
08000c6a: 41f00101     orr       r1, r1, #1
08000c6e: 0160         str       r1, [r0]
08000c70: 4268         ldr       r2, [r0, #4]
08000c72: 2e49         ldr       r1, [pc, #0xb8]
08000c74: 1140         ands      r1, r2
08000c76: 4160         str       r1, [r0, #4]
08000c78: 0168         ldr       r1, [r0]
08000c7a: 21f41021     bic       r1, r1, #0x90000
08000c7e: 21f08071     bic       r1, r1, #0x1000000
08000c82: 0160         str       r1, [r0]
08000c84: 0168         ldr       r1, [r0]
08000c86: 21f48021     bic       r1, r1, #0x40000
08000c8a: 0160         str       r1, [r0]
08000c8c: 4168         ldr       r1, [r0, #4]
08000c8e: 21f4fe01     bic       r1, r1, #0x7f0000
08000c92: 4160         str       r1, [r0, #4]
08000c94: 4ff41f01     mov.w     r1, #0x9f0000
08000c98: 8160         str       r1, [r0, #8]
08000c9a: 0022         movs      r2, #0
08000c9c: c262         str       r2, [r0, #0x2c]
08000c9e: 0092         str       r2, [sp]
08000ca0: 0192         str       r2, [sp, #4]
08000ca2: 0168         ldr       r1, [r0]
08000ca4: 41f48031     orr       r1, r1, #0x10000
08000ca8: 0160         str       r1, [r0]
08000caa: 0168         ldr       r1, [r0]
08000cac: 01f40031     and       r1, r1, #0x20000
08000cb0: 0191         str       r1, [sp, #4]
08000cb2: 0099         ldr       r1, [sp]
08000cb4: 491c         adds      r1, r1, #1
08000cb6: 0091         str       r1, [sp]
08000cb8: 0199         ldr       r1, [sp, #4]
08000cba: 19b9         cbnz      r1, #0x8000cc4
08000cbc: 0099         ldr       r1, [sp]
08000cbe: b1f5a06f     cmp.w     r1, #0x500
08000cc2: f2d1         bne       #0x8000caa
08000cc4: 0168         ldr       r1, [r0]
08000cc6: 11f4003f     tst.w     r1, #0x20000
08000cca: 08bf         it        eq
08000ccc: 0192         streq     r2, [sp, #4]
08000cce: 24d0         beq       #0x8000d1a
08000cd0: 0121         movs      r1, #1
08000cd2: 0191         str       r1, [sp, #4]
08000cd4: 4168         ldr       r1, [r0, #4]
08000cd6: 4160         str       r1, [r0, #4]
08000cd8: 4168         ldr       r1, [r0, #4]
08000cda: 4160         str       r1, [r0, #4]
08000cdc: 4168         ldr       r1, [r0, #4]
08000cde: 4160         str       r1, [r0, #4]
08000ce0: 4168         ldr       r1, [r0, #4]
08000ce2: 21f47c11     bic       r1, r1, #0x3f0000
08000ce6: 4160         str       r1, [r0, #4]
08000ce8: 4168         ldr       r1, [r0, #4]
08000cea: 41f44031     orr       r1, r1, #0x30000
08000cee: 4160         str       r1, [r0, #4]
08000cf0: 0168         ldr       r1, [r0]
08000cf2: 41f08071     orr       r1, r1, #0x1000000
08000cf6: 0160         str       r1, [r0]
08000cf8: 0168         ldr       r1, [r0]
08000cfa: 11f0007f     tst.w     r1, #0x2000000
08000cfe: fbd0         beq       #0x8000cf8
08000d00: 4168         ldr       r1, [r0, #4]
08000d02: 21f00301     bic       r1, r1, #3
08000d06: 4160         str       r1, [r0, #4]
08000d08: 4168         ldr       r1, [r0, #4]
08000d0a: 41f00201     orr       r1, r1, #2
08000d0e: 4160         str       r1, [r0, #4]
08000d10: 4168         ldr       r1, [r0, #4]
08000d12: 01f00c01     and       r1, r1, #0xc
08000d16: 0829         cmp       r1, #8
08000d18: fad1         bne       #0x8000d10
08000d1a: 0549         ldr       r1, [pc, #0x14]
08000d1c: 4ff00060     mov.w     r0, #0x8000000
08000d20: 0860         str       r0, [r1]
08000d22: 02b0         add       sp, #8
08000d24: 7047         bx        lr
08000d26: 0000         movs      r0, r0
08000d28: 0010         asrs      r0, r0, #0x20
08000d2a: 0240         ands      r2, r0
08000d2c: 0000         movs      r0, r0
08000d2e: fff8         .byte     0xff, 0xf8
08000d30: 08ed00e0     stc       p0, c14, [r8, #-0]
08000d34: 10b5         push      {r4, lr}
08000d36: 00f05dfd     bl        #0x80017f4
08000d3a: 124c         ldr       r4, [pc, #0x48]
08000d3c: 0021         movs      r1, #0
08000d3e: 2046         mov       r0, r4
08000d40: 00f027f8     bl        #0x8000d92
08000d44: 104a         ldr       r2, [pc, #0x40]
08000d46: 1078         ldrb      r0, [r2]
08000d48: 0028         cmp       r0, #0
08000d4a: 5068         ldr       r0, [r2, #4]
08000d4c: 12d0         beq       #0x8000d74
08000d4e: 411c         adds      r1, r0, #1
08000d50: 5160         str       r1, [r2, #4]
08000d52: b1f5966f     cmp.w     r1, #0x4b0
08000d56: 28bf         it        hs
08000d58: 0020         movhs     r0, #0
08000d5a: 00d3         blo       #0x8000d5e
08000d5c: 1070         strb      r0, [r2]
08000d5e: 9088         ldrh      r0, [r2, #4]
08000d60: 81b2         uxth      r1, r0
08000d62: 2046         mov       r0, r4
08000d64: 00f039f9     bl        #0x8000fda
08000d68: 2046         mov       r0, r4
08000d6a: bde81040     pop.w     {r4, lr}
08000d6e: 0121         movs      r1, #1
08000d70: 00f00fb8     b.w       #0x8000d92
08000d74: 411e         subs      r1, r0, #1
08000d76: 5160         str       r1, [r2, #4]
08000d78: b1f5167f     cmp.w     r1, #0x258
08000d7c: 98bf         it        ls
08000d7e: 0120         movls     r0, #1
08000d80: edd8         bhi       #0x8000d5e
08000d82: ebe7         b         #0x8000d5c
08000d84: 002c         cmp       r4, #0
08000d86: 0140         ands      r1, r0
08000d88: 6400         lsls      r4, r4, #1
08000d8a: 0020         movs      r0, #0
08000d8c: c943         mvns      r1, r1
08000d8e: 0182         strh      r1, [r0, #0x10]
08000d90: 7047         bx        lr
08000d92: 0029         cmp       r1, #0
08000d94: 0188         ldrh      r1, [r0]
08000d96: 14bf         ite       ne
08000d98: 41f00101     orrne     r1, r1, #1
08000d9c: 21f00101     biceq     r1, r1, #1
08000da0: 0180         strh      r1, [r0]
08000da2: 7047         bx        lr
08000da4: 10b5         push      {r4, lr}
08000da6: a0f18041     sub.w     r1, r0, #0x40000000
08000daa: b1f59631     subs.w    r1, r1, #0x12c00
08000dae: 0ad1         bne       #0x8000dc6
08000db0: 0121         movs      r1, #1
08000db2: c802         lsls      r0, r1, #0xb
08000db4: fff7cafe     bl        #0x8000b4c
08000db8: bde81040     pop.w     {r4, lr}
08000dbc: 0021         movs      r1, #0
08000dbe: 4ff40060     mov.w     r0, #0x800
08000dc2: fff7c3be     b.w       #0x8000b4c
08000dc6: b0f1804f     cmp.w     r0, #0x40000000
08000dca: 0ed0         beq       #0x8000dea
08000dcc: a0f18041     sub.w     r1, r0, #0x40000000
08000dd0: b1f58061     subs.w    r1, r1, #0x400
08000dd4: 13d1         bne       #0x8000dfe
08000dd6: 0121         movs      r1, #1
08000dd8: 0220         movs      r0, #2
08000dda: fff79ffe     bl        #0x8000b1c
08000dde: 0021         movs      r1, #0
08000de0: bde81040     pop.w     {r4, lr}
08000de4: 0220         movs      r0, #2
08000de6: fff799be     b.w       #0x8000b1c
08000dea: 0121         movs      r1, #1
08000dec: 0846         mov       r0, r1
08000dee: fff795fe     bl        #0x8000b1c
08000df2: 0021         movs      r1, #0
08000df4: bde81040     pop.w     {r4, lr}
08000df8: 0120         movs      r0, #1
08000dfa: fff78fbe     b.w       #0x8000b1c
08000dfe: a0f18041     sub.w     r1, r0, #0x40000000
08000e02: b1f50061     subs.w    r1, r1, #0x800
08000e06: 09d1         bne       #0x8000e1c
08000e08: 0121         movs      r1, #1
08000e0a: 0420         movs      r0, #4
08000e0c: fff786fe     bl        #0x8000b1c
08000e10: 0021         movs      r1, #0
08000e12: bde81040     pop.w     {r4, lr}
08000e16: 0420         movs      r0, #4
08000e18: fff780be     b.w       #0x8000b1c
08000e1c: a0f18041     sub.w     r1, r0, #0x40000000
08000e20: b1f54061     subs.w    r1, r1, #0xc00
08000e24: 09d1         bne       #0x8000e3a
08000e26: 0121         movs      r1, #1
08000e28: 0820         movs      r0, #8
08000e2a: fff777fe     bl        #0x8000b1c
08000e2e: 0021         movs      r1, #0
08000e30: bde81040     pop.w     {r4, lr}
08000e34: 0820         movs      r0, #8
08000e36: fff771be     b.w       #0x8000b1c
08000e3a: a0f18041     sub.w     r1, r0, #0x40000000
08000e3e: b1f58051     subs.w    r1, r1, #0x1000
08000e42: 09d1         bne       #0x8000e58
08000e44: 0121         movs      r1, #1
08000e46: 1020         movs      r0, #0x10
08000e48: fff768fe     bl        #0x8000b1c
08000e4c: 0021         movs      r1, #0
08000e4e: bde81040     pop.w     {r4, lr}
08000e52: 1020         movs      r0, #0x10
08000e54: fff762be     b.w       #0x8000b1c
08000e58: a0f18041     sub.w     r1, r0, #0x40000000
08000e5c: b1f5a051     subs.w    r1, r1, #0x1400
08000e60: 09d1         bne       #0x8000e76
08000e62: 0121         movs      r1, #1
08000e64: 2020         movs      r0, #0x20
08000e66: fff759fe     bl        #0x8000b1c
08000e6a: 0021         movs      r1, #0
08000e6c: bde81040     pop.w     {r4, lr}
08000e70: 2020         movs      r0, #0x20
08000e72: fff753be     b.w       #0x8000b1c
08000e76: a0f18041     sub.w     r1, r0, #0x40000000
08000e7a: b1f59a31     subs.w    r1, r1, #0x13400
08000e7e: 0ad1         bne       #0x8000e96
08000e80: 0121         movs      r1, #1
08000e82: 4803         lsls      r0, r1, #0xd
08000e84: fff762fe     bl        #0x8000b4c
08000e88: bde81040     pop.w     {r4, lr}
08000e8c: 0021         movs      r1, #0
08000e8e: 4ff40050     mov.w     r0, #0x2000
08000e92: fff75bbe     b.w       #0x8000b4c
08000e96: a0f18041     sub.w     r1, r0, #0x40000000
08000e9a: b1f5a631     subs.w    r1, r1, #0x14c00
08000e9e: 0ad1         bne       #0x8000eb6
08000ea0: 0121         movs      r1, #1
08000ea2: c804         lsls      r0, r1, #0x13
08000ea4: fff752fe     bl        #0x8000b4c
08000ea8: bde81040     pop.w     {r4, lr}
08000eac: 0021         movs      r1, #0
08000eae: 4ff40020     mov.w     r0, #0x80000
08000eb2: fff74bbe     b.w       #0x8000b4c
08000eb6: a0f18041     sub.w     r1, r0, #0x40000000
08000eba: b1f5a831     subs.w    r1, r1, #0x15000
08000ebe: 0ad1         bne       #0x8000ed6
08000ec0: 0121         movs      r1, #1
08000ec2: 0805         lsls      r0, r1, #0x14
08000ec4: fff742fe     bl        #0x8000b4c
08000ec8: bde81040     pop.w     {r4, lr}
08000ecc: 0021         movs      r1, #0
08000ece: 4ff48010     mov.w     r0, #0x100000
08000ed2: fff73bbe     b.w       #0x8000b4c
08000ed6: a0f18041     sub.w     r1, r0, #0x40000000
08000eda: b1f5aa31     subs.w    r1, r1, #0x15400
08000ede: 0ad1         bne       #0x8000ef6
08000ee0: 0121         movs      r1, #1
08000ee2: 4805         lsls      r0, r1, #0x15
08000ee4: fff732fe     bl        #0x8000b4c
08000ee8: bde81040     pop.w     {r4, lr}
08000eec: 0021         movs      r1, #0
08000eee: 4ff40010     mov.w     r0, #0x200000
08000ef2: fff72bbe     b.w       #0x8000b4c
08000ef6: a0f18041     sub.w     r1, r0, #0x40000000
08000efa: b1f5c051     subs.w    r1, r1, #0x1800
08000efe: 09d1         bne       #0x8000f14
08000f00: 0121         movs      r1, #1
08000f02: 4020         movs      r0, #0x40
08000f04: fff70afe     bl        #0x8000b1c
08000f08: 0021         movs      r1, #0
08000f0a: bde81040     pop.w     {r4, lr}
08000f0e: 4020         movs      r0, #0x40
08000f10: fff704be     b.w       #0x8000b1c
08000f14: a0f18041     sub.w     r1, r0, #0x40000000
08000f18: b1f5e051     subs.w    r1, r1, #0x1c00
08000f1c: 09d1         bne       #0x8000f32
08000f1e: 0121         movs      r1, #1
08000f20: 8020         movs      r0, #0x80
08000f22: fff7fbfd     bl        #0x8000b1c
08000f26: 0021         movs      r1, #0
08000f28: bde81040     pop.w     {r4, lr}
08000f2c: 8020         movs      r0, #0x80
08000f2e: fff7f5bd     b.w       #0x8000b1c
08000f32: a0f18041     sub.w     r1, r0, #0x40000000
08000f36: b1f50051     subs.w    r1, r1, #0x2000
08000f3a: 0ad1         bne       #0x8000f52
08000f3c: 0121         movs      r1, #1
08000f3e: 0802         lsls      r0, r1, #8
08000f40: fff7ecfd     bl        #0x8000b1c
08000f44: bde81040     pop.w     {r4, lr}
08000f48: 0021         movs      r1, #0
08000f4a: 4ff48070     mov.w     r0, #0x100
08000f4e: fff7e5bd     b.w       #0x8000b1c
08000f52: a0f18041     sub.w     r1, r0, #0x40000000
08000f56: b1f5a031     subs.w    r1, r1, #0x14000
08000f5a: 0ad1         bne       #0x8000f72
08000f5c: 0121         movs      r1, #1
08000f5e: 0804         lsls      r0, r1, #0x10
08000f60: fff7f4fd     bl        #0x8000b4c
08000f64: bde81040     pop.w     {r4, lr}
08000f68: 0021         movs      r1, #0
08000f6a: 4ff48030     mov.w     r0, #0x10000
08000f6e: fff7edbd     b.w       #0x8000b4c
08000f72: a0f18041     sub.w     r1, r0, #0x40000000
08000f76: b1f5a231     subs.w    r1, r1, #0x14400
08000f7a: 0ad1         bne       #0x8000f92
08000f7c: 0121         movs      r1, #1
08000f7e: 4804         lsls      r0, r1, #0x11
08000f80: fff7e4fd     bl        #0x8000b4c
08000f84: bde81040     pop.w     {r4, lr}
08000f88: 0021         movs      r1, #0
08000f8a: 4ff40030     mov.w     r0, #0x20000
08000f8e: fff7ddbd     b.w       #0x8000b4c
08000f92: a0f18041     sub.w     r1, r0, #0x40000000
08000f96: b1f5a431     subs.w    r1, r1, #0x14800
08000f9a: 18bf         it        ne
08000f9c: 10bd         popne     {r4, pc}
08000f9e: 0121         movs      r1, #1
08000fa0: 8804         lsls      r0, r1, #0x12
08000fa2: fff7d3fd     bl        #0x8000b4c
08000fa6: bde81040     pop.w     {r4, lr}
08000faa: 0021         movs      r1, #0
08000fac: 4ff48020     mov.w     r0, #0x40000
08000fb0: fff7ccbd     b.w       #0x8000b4c
08000fb4: 038a         ldrh      r3, [r0, #0x10]
08000fb6: 0022         movs      r2, #0
08000fb8: 8089         ldrh      r0, [r0, #0xc]
08000fba: 0b42         tst       r3, r1
08000fbc: 00ea0100     and.w     r0, r0, r1
08000fc0: 1cbf         itt       ne
08000fc2: 0028         cmpne     r0, #0
08000fc4: 0122         movne     r2, #1
08000fc6: 1046         mov       r0, r2
08000fc8: 7047         bx        lr
08000fca: 002a         cmp       r2, #0
08000fcc: 8289         ldrh      r2, [r0, #0xc]
08000fce: 14bf         ite       ne
08000fd0: 1143         orrne     r1, r2
08000fd2: 22ea0101     biceq.w   r1, r2, r1
08000fd6: 8181         strh      r1, [r0, #0xc]
08000fd8: 7047         bx        lr
08000fda: 8185         strh      r1, [r0, #0x2c]
08000fdc: 7047         bx        lr
08000fde: 8184         strh      r1, [r0, #0x24]
08000fe0: 7047         bx        lr
08000fe2: 0000         movs      r0, r0
08000fe4: 10b4         push      {r4}
08000fe6: 0288         ldrh      r2, [r0]
08000fe8: dff88cc0     ldr.w     ip, [pc, #0x8c]
08000fec: 234b         ldr       r3, [pc, #0x8c]
08000fee: 6045         cmp       r0, ip
08000ff0: 18bf         it        ne
08000ff2: 9842         cmpne     r0, r3
08000ff4: 11d0         beq       #0x800101a
08000ff6: b0f1804f     cmp.w     r0, #0x40000000
08000ffa: 1cbf         itt       ne
08000ffc: a0f18044     subne.w   r4, r0, #0x40000000
08001000: b4f58064     subsne.w  r4, r4, #0x400
08001004: 09d0         beq       #0x800101a
08001006: a0f18044     sub.w     r4, r0, #0x40000000
0800100a: b4f50064     subs.w    r4, r4, #0x800
0800100e: 1cbf         itt       ne
08001010: a0f18044     subne.w   r4, r0, #0x40000000
08001014: b4f54064     subsne.w  r4, r4, #0xc00
08001018: 03d1         bne       #0x8001022
0800101a: 4c88         ldrh      r4, [r1, #2]
0800101c: 22f07002     bic       r2, r2, #0x70
08001020: 2243         orrs      r2, r4
08001022: a0f18044     sub.w     r4, r0, #0x40000000
08001026: b4f58054     subs.w    r4, r4, #0x1000
0800102a: 1cbf         itt       ne
0800102c: a0f18044     subne.w   r4, r0, #0x40000000
08001030: b4f5a054     subsne.w  r4, r4, #0x1400
08001034: 03d0         beq       #0x800103e
08001036: cc88         ldrh      r4, [r1, #6]
08001038: 22f44072     bic       r2, r2, #0x300
0800103c: 2243         orrs      r2, r4
0800103e: 0280         strh      r2, [r0]
08001040: 8a88         ldrh      r2, [r1, #4]
08001042: 8285         strh      r2, [r0, #0x2c]
08001044: 0a88         ldrh      r2, [r1]
08001046: 0285         strh      r2, [r0, #0x28]
08001048: 6045         cmp       r0, ip
0800104a: 18bf         it        ne
0800104c: 9842         cmpne     r0, r3
0800104e: 0dd0         beq       #0x800106c
08001050: a0f18042     sub.w     r2, r0, #0x40000000
08001054: b2f5a032     subs.w    r2, r2, #0x14000
08001058: 1fbf         itttt     ne
0800105a: a0f18042     subne.w   r2, r0, #0x40000000
0800105e: b2f5a232     subsne.w  r2, r2, #0x14400
08001062: a0f18042     subne.w   r2, r0, #0x40000000
08001066: b2f5a432     subsne.w  r2, r2, #0x14800
0800106a: 01d1         bne       #0x8001070
0800106c: 097a         ldrb      r1, [r1, #8]
0800106e: 0186         strh      r1, [r0, #0x30]
08001070: 0121         movs      r1, #1
08001072: 8182         strh      r1, [r0, #0x14]
08001074: 10bc         pop       {r4}
08001076: 7047         bx        lr
08001078: 002c         cmp       r4, #0
0800107a: 0140         ands      r1, r0
0800107c: 0034         adds      r4, #0
0800107e: 0140         ands      r1, r0
08001080: 4ff6ff71     movw      r1, #0xffff
08001084: 8180         strh      r1, [r0, #4]
08001086: 0021         movs      r1, #0
08001088: 0180         strh      r1, [r0]
0800108a: c180         strh      r1, [r0, #6]
0800108c: 4180         strh      r1, [r0, #2]
0800108e: 0172         strb      r1, [r0, #8]
08001090: 7047         bx        lr
08001092: 0000         movs      r0, r0
08001094: 10b5         push      {r4, lr}
08001096: 184c         ldr       r4, [pc, #0x60]
08001098: 84b0         sub       sp, #0x10
0800109a: 0021         movs      r1, #0
0800109c: 2046         mov       r0, r4
0800109e: fff778fe     bl        #0x8000d92
080010a2: 2046         mov       r0, r4
080010a4: fff77efe     bl        #0x8000da4
080010a8: 0021         movs      r1, #0
080010aa: 2046         mov       r0, r4
080010ac: fff797ff     bl        #0x8000fde
080010b0: 6846         mov       r0, sp
080010b2: fff7e5ff     bl        #0x8001080
080010b6: 0021         movs      r1, #0
080010b8: 40f25722     movw      r2, #0x257
080010bc: adf80010     strh.w    r1, [sp]
080010c0: adf80420     strh.w    r2, [sp, #4]
080010c4: adf80610     strh.w    r1, [sp, #6]
080010c8: 8df80810     strb.w    r1, [sp, #8]
080010cc: adf80210     strh.w    r1, [sp, #2]
080010d0: 6946         mov       r1, sp
080010d2: 2046         mov       r0, r4
080010d4: fff786ff     bl        #0x8000fe4
080010d8: 0121         movs      r1, #1
080010da: 2046         mov       r0, r4
080010dc: fff756fe     bl        #0x8000d8c
080010e0: 0122         movs      r2, #1
080010e2: 1146         mov       r1, r2
080010e4: 2046         mov       r0, r4
080010e6: fff770ff     bl        #0x8000fca
080010ea: 0121         movs      r1, #1
080010ec: 2046         mov       r0, r4
080010ee: fff750fe     bl        #0x8000d92
080010f2: 04b0         add       sp, #0x10
080010f4: 10bd         pop       {r4, pc}
080010f6: 0000         movs      r0, r0
080010f8: 002c         cmp       r4, #0
080010fa: 0140         ands      r1, r0
080010fc: 1201         lsls      r2, r2, #4
080010fe: 0270         strb      r2, [r0]
08001100: 0022         movs      r2, #0
08001102: c260         str       r2, [r0, #0xc]
08001104: 4361         str       r3, [r0, #0x14]
08001106: 0261         str       r2, [r0, #0x10]
08001108: c0e90121     strd      r2, r1, [r0, #4]
0800110c: 7047         bx        lr
0800110e: 0000         movs      r0, r0
08001110: 064a         ldr       r2, [pc, #0x18]
08001112: 535c         ldrb      r3, [r2, r1]
08001114: 4268         ldr       r2, [r0, #4]
08001116: 02eb420c     add.w     ip, r2, r2, lsl #1
0800111a: 0cebc202     add.w     r2, ip, r2, lsl #3
0800111e: dff810c0     ldr.w     ip, [pc, #0x10]
08001122: 0ceb8202     add.w     r2, ip, r2, lsl #2
08001126: 52f82320     ldr.w     r2, [r2, r3, lsl #2]
0800112a: 1047         bx        r2
0800112c: ac3b         subs      r3, #0xac
0800112e: 0008         lsrs      r0, r0, #0x20
08001130: ac3c         subs      r4, #0xac
08001132: 0008         lsrs      r0, r0, #0x20
08001134: 10b5         push      {r4, lr}
08001136: 00f0eff9     bl        #0x8001518
0800113a: bde81040     pop.w     {r4, lr}
0800113e: 00f03fba     b.w       #0x80015c0
08001142: 0029         cmp       r1, #0
08001144: 8189         ldrh      r1, [r0, #0xc]
08001146: 14bf         ite       ne
08001148: 41f40051     orrne     r1, r1, #0x2000
0800114c: 21f40051     biceq     r1, r1, #0x2000
08001150: 8181         strh      r1, [r0, #0xc]
08001152: 7047         bx        lr
08001154: 10b5         push      {r4, lr}
08001156: a0f18041     sub.w     r1, r0, #0x40000000
0800115a: b1f59c31     subs.w    r1, r1, #0x13800
0800115e: 0ad1         bne       #0x8001176
08001160: 0121         movs      r1, #1
08001162: 8803         lsls      r0, r1, #0xe
08001164: fff7f2fc     bl        #0x8000b4c
08001168: bde81040     pop.w     {r4, lr}
0800116c: 0021         movs      r1, #0
0800116e: 4ff48040     mov.w     r0, #0x4000
08001172: fff7ebbc     b.w       #0x8000b4c
08001176: a0f18041     sub.w     r1, r0, #0x40000000
0800117a: b1f58841     subs.w    r1, r1, #0x4400
0800117e: 0ad1         bne       #0x8001196
08001180: 0121         movs      r1, #1
08001182: 4804         lsls      r0, r1, #0x11
08001184: fff7cafc     bl        #0x8000b1c
08001188: bde81040     pop.w     {r4, lr}
0800118c: 0021         movs      r1, #0
0800118e: 4ff40030     mov.w     r0, #0x20000
08001192: fff7c3bc     b.w       #0x8000b1c
08001196: a0f18041     sub.w     r1, r0, #0x40000000
0800119a: b1f59041     subs.w    r1, r1, #0x4800
0800119e: 0ad1         bne       #0x80011b6
080011a0: 0121         movs      r1, #1
080011a2: 8804         lsls      r0, r1, #0x12
080011a4: fff7bafc     bl        #0x8000b1c
080011a8: bde81040     pop.w     {r4, lr}
080011ac: 0021         movs      r1, #0
080011ae: 4ff48020     mov.w     r0, #0x40000
080011b2: fff7b3bc     b.w       #0x8000b1c
080011b6: a0f18041     sub.w     r1, r0, #0x40000000
080011ba: b1f59841     subs.w    r1, r1, #0x4c00
080011be: 0ad1         bne       #0x80011d6
080011c0: 0121         movs      r1, #1
080011c2: c804         lsls      r0, r1, #0x13
080011c4: fff7aafc     bl        #0x8000b1c
080011c8: bde81040     pop.w     {r4, lr}
080011cc: 0021         movs      r1, #0
080011ce: 4ff40020     mov.w     r0, #0x80000
080011d2: fff7a3bc     b.w       #0x8000b1c
080011d6: a0f18041     sub.w     r1, r0, #0x40000000
080011da: b1f5a041     subs.w    r1, r1, #0x5000
080011de: 18bf         it        ne
080011e0: 10bd         popne     {r4, pc}
080011e2: 0121         movs      r1, #1
080011e4: 0805         lsls      r0, r1, #0x14
080011e6: fff799fc     bl        #0x8000b1c
080011ea: bde81040     pop.w     {r4, lr}
080011ee: 0021         movs      r1, #0
080011f0: 4ff48010     mov.w     r0, #0x100000
080011f4: fff792bc     b.w       #0x8000b1c
080011f8: 0246         mov       r2, r0
080011fa: 0020         movs      r0, #0
080011fc: 1288         ldrh      r2, [r2]
080011fe: 0a42         tst       r2, r1
08001200: 18bf         it        ne
08001202: 0120         movne     r0, #1
08001204: 7047         bx        lr
08001206: 10b4         push      {r4}
08001208: 01f01f02     and       r2, r1, #0x1f
0800120c: 0124         movs      r4, #1
0800120e: c1f34213     ubfx      r3, r1, #5, #3
08001212: 04fa02f2     lsl.w     r2, r4, r2
08001216: 4ff0000c     mov.w     ip, #0
0800121a: 012b         cmp       r3, #1
0800121c: 04bf         itt       eq
0800121e: 8389         ldrheq    r3, [r0, #0xc]
08001220: 1a40         andeq     r2, r3
08001222: 04d0         beq       #0x800122e
08001224: 022b         cmp       r3, #2
08001226: 0cbf         ite       eq
08001228: 038a         ldrheq    r3, [r0, #0x10]
0800122a: 838a         ldrhne    r3, [r0, #0x14]
0800122c: 1a40         ands      r2, r3
0800122e: 090a         lsrs      r1, r1, #8
08001230: 0088         ldrh      r0, [r0]
08001232: 04fa01f1     lsl.w     r1, r4, r1
08001236: 0840         ands      r0, r1
08001238: 002a         cmp       r2, #0
0800123a: 1cbf         itt       ne
0800123c: 0028         cmpne     r0, #0
0800123e: 4ff0010c     movne.w   ip, #1
08001242: 6046         mov       r0, ip
08001244: 10bc         pop       {r4}
08001246: 7047         bx        lr
08001248: c1f34213     ubfx      r3, r1, #5, #3
0800124c: 01f01f01     and       r1, r1, #0x1f
08001250: 4ff0010c     mov.w     ip, #1
08001254: 0cfa01f1     lsl.w     r1, ip, r1
08001258: 012b         cmp       r3, #1
0800125a: 08bf         it        eq
0800125c: 0c30         addeq     r0, #0xc
0800125e: 03d0         beq       #0x8001268
08001260: 022b         cmp       r3, #2
08001262: 0cbf         ite       eq
08001264: 1030         addeq     r0, #0x10
08001266: 1430         addne     r0, #0x14
08001268: 002a         cmp       r2, #0
0800126a: 0268         ldr       r2, [r0]
0800126c: 14bf         ite       ne
0800126e: 1143         orrne     r1, r2
08001270: 22ea0101     biceq.w   r1, r2, r1
08001274: 0160         str       r1, [r0]
08001276: 7047         bx        lr
08001278: 30b5         push      {r4, r5, lr}
0800127a: 0446         mov       r4, r0
0800127c: 008a         ldrh      r0, [r0, #0x10]
0800127e: 85b0         sub       sp, #0x14
08001280: 0d46         mov       r5, r1
08001282: 4cf6ff71     movw      r1, #0xcfff
08001286: 0840         ands      r0, r1
08001288: e988         ldrh      r1, [r5, #6]
0800128a: 0843         orrs      r0, r1
0800128c: 2082         strh      r0, [r4, #0x10]
0800128e: a089         ldrh      r0, [r4, #0xc]
08001290: 4ef6f311     movw      r1, #0xe9f3
08001294: 0840         ands      r0, r1
08001296: a988         ldrh      r1, [r5, #4]
08001298: 2a89         ldrh      r2, [r5, #8]
0800129a: 1143         orrs      r1, r2
0800129c: 6a89         ldrh      r2, [r5, #0xa]
0800129e: 1043         orrs      r0, r2
080012a0: 0843         orrs      r0, r1
080012a2: a081         strh      r0, [r4, #0xc]
080012a4: a08a         ldrh      r0, [r4, #0x14]
080012a6: 4ff6ff41     movw      r1, #0xfcff
080012aa: 0840         ands      r0, r1
080012ac: a989         ldrh      r1, [r5, #0xc]
080012ae: 0843         orrs      r0, r1
080012b0: a082         strh      r0, [r4, #0x14]
080012b2: 6846         mov       r0, sp
080012b4: fff756fc     bl        #0x8000b64
080012b8: a4f18040     sub.w     r0, r4, #0x40000000
080012bc: b0f59c30     subs.w    r0, r0, #0x13800
080012c0: 0cbf         ite       eq
080012c2: 0398         ldreq     r0, [sp, #0xc]
080012c4: 0298         ldrne     r0, [sp, #8]
080012c6: a189         ldrh      r1, [r4, #0xc]
080012c8: 11f4004f     tst.w     r1, #0x8000
080012cc: 00ebc001     add.w     r1, r0, r0, lsl #3
080012d0: 01eb0010     add.w     r0, r1, r0, lsl #4
080012d4: 2968         ldr       r1, [r5]
080012d6: 14bf         ite       ne
080012d8: 4900         lslne     r1, r1, #1
080012da: 8900         lsleq     r1, r1, #2
080012dc: b0fbf1f0     udiv      r0, r0, r1
080012e0: 114a         ldr       r2, [pc, #0x44]
080012e2: 6ff0180c     mvn       ip, #0x18
080012e6: a2fb0031     umull     r3, r1, r2, r0
080012ea: 4909         lsrs      r1, r1, #5
080012ec: 0901         lsls      r1, r1, #4
080012ee: 0b09         lsrs      r3, r1, #4
080012f0: 03fb0cf3     mul       r3, r3, ip
080012f4: 00eb8300     add.w     r0, r0, r3, lsl #2
080012f8: a389         ldrh      r3, [r4, #0xc]
080012fa: 13f4004f     tst.w     r3, #0x8000
080012fe: 4ff03203     mov.w     r3, #0x32
08001302: 14bf         ite       ne
08001304: 03ebc000     addne.w   r0, r3, r0, lsl #3
08001308: 03eb0010     addeq.w   r0, r3, r0, lsl #4
0800130c: a2fb0020     umull     r2, r0, r2, r0
08001310: 4fea5010     lsr.w     r0, r0, #5
08001314: 14bf         ite       ne
08001316: 00f00700     andne     r0, r0, #7
0800131a: 00f00f00     andeq     r0, r0, #0xf
0800131e: 0843         orrs      r0, r1
08001320: 2081         strh      r0, [r4, #8]
08001322: 05b0         add       sp, #0x14
08001324: 30bd         pop       {r4, r5, pc}
08001326: 0000         movs      r0, r0
08001328: 1f85         strh      r7, [r3, #0x28]
0800132a: eb51         str       r3, [r5, r7]
0800132c: 8088         ldrh      r0, [r0, #4]
0800132e: c0f30800     ubfx      r0, r0, #0, #9
08001332: 7047         bx        lr
08001334: c1f30801     ubfx      r1, r1, #0, #9
08001338: 8180         strh      r1, [r0, #4]
0800133a: 7047         bx        lr
0800133c: 4ff41651     mov.w     r1, #0x2580
08001340: 0160         str       r1, [r0]
08001342: 0021         movs      r1, #0
08001344: 8180         strh      r1, [r0, #4]
08001346: c180         strh      r1, [r0, #6]
08001348: 0181         strh      r1, [r0, #8]
0800134a: 0c22         movs      r2, #0xc
0800134c: 4281         strh      r2, [r0, #0xa]
0800134e: 8181         strh      r1, [r0, #0xc]
08001350: 7047         bx        lr
08001352: fee7         b         #0x8001352
08001354: 10b5         push      {r4, lr}
08001356: 1b4c         ldr       r4, [pc, #0x6c]
08001358: 84b0         sub       sp, #0x10
0800135a: 0021         movs      r1, #0
0800135c: 2046         mov       r0, r4
0800135e: fff7f0fe     bl        #0x8001142
08001362: 2046         mov       r0, r4
08001364: fff7f6fe     bl        #0x8001154
08001368: 6846         mov       r0, sp
0800136a: fff7e7ff     bl        #0x800133c
0800136e: 4ff22441     movw      r1, #0xf424
08001372: 0091         str       r1, [sp]
08001374: 0021         movs      r1, #0
08001376: adf80410     strh.w    r1, [sp, #4]
0800137a: adf80610     strh.w    r1, [sp, #6]
0800137e: adf80810     strh.w    r1, [sp, #8]
08001382: adf80c10     strh.w    r1, [sp, #0xc]
08001386: 0c21         movs      r1, #0xc
08001388: adf80a10     strh.w    r1, [sp, #0xa]
0800138c: 6946         mov       r1, sp
0800138e: 2046         mov       r0, r4
08001390: fff772ff     bl        #0x8001278
08001394: 0122         movs      r2, #1
08001396: 4ff45871     mov.w     r1, #0x360
0800139a: 2046         mov       r0, r4
0800139c: fff754ff     bl        #0x8001248
080013a0: 0122         movs      r2, #1
080013a2: 4ff4b071     mov.w     r1, #0x160
080013a6: 2046         mov       r0, r4
080013a8: fff74eff     bl        #0x8001248
080013ac: 0122         movs      r2, #1
080013ae: 40f22551     movw      r1, #0x525
080013b2: 2046         mov       r0, r4
080013b4: fff748ff     bl        #0x8001248
080013b8: 0121         movs      r1, #1
080013ba: 2046         mov       r0, r4
080013bc: fff7c1fe     bl        #0x8001142
080013c0: 04b0         add       sp, #0x10
080013c2: 10bd         pop       {r4, pc}
080013c4: 0038         subs      r0, #0
080013c6: 0140         ands      r1, r0
080013c8: 2de9f047     push.w    {r4, r5, r6, r7, r8, sb, sl, lr}
080013cc: 2f4c         ldr       r4, [pc, #0xbc]
080013ce: 0025         movs      r5, #0
080013d0: 0426         movs      r6, #4
080013d2: 607c         ldrb      r0, [r4, #0x11]
080013d4: 2f46         mov       r7, r5
080013d6: 0028         cmp       r0, #0
080013d8: 88bf         it        hi
080013da: 4ff00108     movhi.w   r8, #1
080013de: 31d9         bls       #0x8001444
080013e0: e068         ldr       r0, [r4, #0xc]
080013e2: 06ebc501     add.w     r1, r6, r5, lsl #3
080013e6: 415a         ldrh      r1, [r0, r1]
080013e8: 50f83500     ldr.w     r0, [r0, r5, lsl #3]
080013ec: 89b2         uxth      r1, r1
080013ee: fff72ffa     bl        #0x8000850
080013f2: 0028         cmp       r0, #0
080013f4: 14bf         ite       ne
080013f6: 0121         movne     r1, #1
080013f8: 0021         moveq     r1, #0
080013fa: a07c         ldrb      r0, [r4, #0x12]
080013fc: 627c         ldrb      r2, [r4, #0x11]
080013fe: 00fb0252     mla       r2, r0, r2, r5
08001402: 04eb020c     add.w     ip, r4, r2
08001406: 9cf81300     ldrb.w    r0, [ip, #0x13]
0800140a: 8842         cmp       r0, r1
0800140c: 04eb8200     add.w     r0, r4, r2, lsl #2
08001410: 08bf         it        eq
08001412: 4762         streq     r7, [r0, #0x24]
08001414: 12d0         beq       #0x800143c
08001416: 436a         ldr       r3, [r0, #0x24]
08001418: 48ea4303     orr.w     r3, r8, r3, lsl #1
0800141c: 4362         str       r3, [r0, #0x24]
0800141e: 0f20         movs      r0, #0xf
08001420: 23fa00f9     lsr.w     sb, r3, r0
08001424: 19f0010f     tst.w     sb, #1
08001428: 28d0         beq       #0x800147c
0800142a: 401e         subs      r0, r0, #1
0800142c: f8d5         bpl       #0x8001420
0800142e: 8cf81310     strb.w    r1, [ip, #0x13]
08001432: 2368         ldr       r3, [r4]
08001434: 13b1         cbz       r3, #0x800143c
08001436: 2079         ldrb      r0, [r4, #4]
08001438: 1044         add       r0, r2
0800143a: 9847         blx       r3
0800143c: 607c         ldrb      r0, [r4, #0x11]
0800143e: 6d1c         adds      r5, r5, #1
08001440: a842         cmp       r0, r5
08001442: cdd8         bhi       #0x80013e0
08001444: a27c         ldrb      r2, [r4, #0x12]
08001446: a068         ldr       r0, [r4, #8]
08001448: 06ebc201     add.w     r1, r6, r2, lsl #3
0800144c: 415a         ldrh      r1, [r0, r1]
0800144e: 50f83200     ldr.w     r0, [r0, r2, lsl #3]
08001452: 89b2         uxth      r1, r1
08001454: fff70cfa     bl        #0x8000870
08001458: a07c         ldrb      r0, [r4, #0x12]
0800145a: 401c         adds      r0, r0, #1
0800145c: c0b2         uxtb      r0, r0
0800145e: a074         strb      r0, [r4, #0x12]
08001460: 217c         ldrb      r1, [r4, #0x10]
08001462: 8842         cmp       r0, r1
08001464: 28bf         it        hs
08001466: a774         strbhs    r7, [r4, #0x12]
08001468: a27c         ldrb      r2, [r4, #0x12]
0800146a: a068         ldr       r0, [r4, #8]
0800146c: 06ebc201     add.w     r1, r6, r2, lsl #3
08001470: 415a         ldrh      r1, [r0, r1]
08001472: 50f83200     ldr.w     r0, [r0, r2, lsl #3]
08001476: 89b2         uxth      r1, r1
08001478: fff7f8f9     bl        #0x800086c
0800147c: 0448         ldr       r0, [pc, #0x10]
0800147e: 02f09df8     bl        #0x80035bc
08001482: bde8f047     pop.w     {r4, r5, r6, r7, r8, sb, sl, lr}
08001486: 0348         ldr       r0, [pc, #0xc]
08001488: 02f098b8     b.w       #0x80035bc
0800148c: fc02         lsls      r4, r7, #0xb
0800148e: 0020         movs      r0, #0
08001490: 6003         lsls      r0, r4, #0xd
08001492: 0020         movs      r0, #0
08001494: 2804         lsls      r0, r5, #0x10
08001496: 0020         movs      r0, #0
08001498: 0020         movs      r0, #0
0800149a: 034a         ldr       r2, [pc, #0xc]
0800149c: 0146         mov       r1, r0
0800149e: 1154         strb      r1, [r2, r0]
080014a0: 401c         adds      r0, r0, #1
080014a2: 2028         cmp       r0, #0x20
080014a4: fbd3         blo       #0x800149e
080014a6: 7047         bx        lr
080014a8: 6406         lsls      r4, r4, #0x19
080014aa: 0020         movs      r0, #0
080014ac: 10b5         push      {r4, lr}
080014ae: 0448         ldr       r0, [pc, #0x10]
080014b0: 00f0fbfd     bl        #0x80020aa
080014b4: bde81040     pop.w     {r4, lr}
080014b8: 0248         ldr       r0, [pc, #8]
080014ba: 00f0f6bd     b.w       #0x80020aa
080014be: 0000         movs      r0, r0
080014c0: c402         lsls      r4, r0, #0xb
080014c2: 0020         movs      r0, #0
080014c4: e002         lsls      r0, r4, #0xb
080014c6: 0020         movs      r0, #0
080014c8: 70b5         push      {r4, r5, r6, lr}
080014ca: 0c4d         ldr       r5, [pc, #0x30]
080014cc: 0024         movs      r4, #0
080014ce: 95f91910     ldrsb.w   r1, [r5, #0x19]
080014d2: 0029         cmp       r1, #0
080014d4: 1cbf         itt       ne
080014d6: 6a68         ldrne     r2, [r5, #4]
080014d8: 002a         cmpne     r2, #0
080014da: 02d0         beq       #0x80014e2
080014dc: 2878         ldrb      r0, [r5]
080014de: 9047         blx       r2
080014e0: 6c76         strb      r4, [r5, #0x19]
080014e2: 074d         ldr       r5, [pc, #0x1c]
080014e4: 95f91910     ldrsb.w   r1, [r5, #0x19]
080014e8: 0029         cmp       r1, #0
080014ea: 1abf         itte      ne
080014ec: 6a68         ldrne     r2, [r5, #4]
080014ee: 002a         cmpne     r2, #0
080014f0: 70bd         popeq     {r4, r5, r6, pc}
080014f2: 2878         ldrb      r0, [r5]
080014f4: 9047         blx       r2
080014f6: 6c76         strb      r4, [r5, #0x19]
080014f8: 70bd         pop       {r4, r5, r6, pc}
080014fa: 0000         movs      r0, r0
080014fc: c402         lsls      r4, r0, #0xb
080014fe: 0020         movs      r0, #0
08001500: e002         lsls      r0, r4, #0xb
08001502: 0020         movs      r0, #0
08001504: 0020         movs      r0, #0
08001506: 034a         ldr       r2, [pc, #0xc]
08001508: 0146         mov       r1, r0
0800150a: 1154         strb      r1, [r2, r0]
0800150c: 401c         adds      r0, r0, #1
0800150e: 5828         cmp       r0, #0x58
08001510: fbd3         blo       #0x800150a
08001512: 7047         bx        lr
08001514: 2407         lsls      r4, r4, #0x1c
08001516: 0020         movs      r0, #0
08001518: 10b5         push      {r4, lr}
0800151a: 284c         ldr       r4, [pc, #0xa0]
0800151c: 40f22551     movw      r1, #0x525
08001520: d4f89000     ldr.w     r0, [r4, #0x90]
08001524: fff76ffe     bl        #0x8001206
08001528: 0028         cmp       r0, #0
0800152a: 23d0         beq       #0x8001574
0800152c: d4f89000     ldr.w     r0, [r4, #0x90]
08001530: fff7fcfe     bl        #0x800132c
08001534: c1b2         uxtb      r1, r0
08001536: 2068         ldr       r0, [r4]
08001538: 6268         ldr       r2, [r4, #4]
0800153a: 801a         subs      r0, r0, r2
0800153c: 0028         cmp       r0, #0
0800153e: b8bf         it        lt
08001540: 8030         addlt     r0, #0x80
08001542: 00b2         sxth      r0, r0
08001544: c0f17f00     rsb.w     r0, r0, #0x7f
08001548: 00b2         sxth      r0, r0
0800154a: 98b1         cbz       r0, #0x8001574
0800154c: 2268         ldr       r2, [r4]
0800154e: 04f10800     add.w     r0, r4, #8
08001552: 1154         strb      r1, [r2, r0]
08001554: 2068         ldr       r0, [r4]
08001556: 7f28         cmp       r0, #0x7f
08001558: aebf         itee      ge
0800155a: 0020         movge     r0, #0
0800155c: 2068         ldrlt     r0, [r4]
0800155e: 401c         addlt     r0, r0, #1
08001560: 2060         str       r0, [r4]
08001562: d4f88810     ldr.w     r1, [r4, #0x88]
08001566: 0029         cmp       r1, #0
08001568: 1ebf         ittt      ne
0800156a: b4f88c00     ldrhne.w  r0, [r4, #0x8c]
0800156e: 0028         cmpne     r0, #0
08001570: 01f0ccf9     blne      #0x800290c
08001574: 4ff45871     mov.w     r1, #0x360
08001578: d4f89000     ldr.w     r0, [r4, #0x90]
0800157c: fff743fe     bl        #0x8001206
08001580: 40b1         cbz       r0, #0x8001594
08001582: 0821         movs      r1, #8
08001584: d4f89000     ldr.w     r0, [r4, #0x90]
08001588: fff736fe     bl        #0x80011f8
0800158c: d4f89000     ldr.w     r0, [r4, #0x90]
08001590: fff7ccfe     bl        #0x800132c
08001594: 4ff4b071     mov.w     r1, #0x160
08001598: d4f89000     ldr.w     r0, [r4, #0x90]
0800159c: fff733fe     bl        #0x8001206
080015a0: 0028         cmp       r0, #0
080015a2: 08bf         it        eq
080015a4: 10bd         popeq     {r4, pc}
080015a6: 0221         movs      r1, #2
080015a8: d4f89000     ldr.w     r0, [r4, #0x90]
080015ac: fff724fe     bl        #0x80011f8
080015b0: d4f89000     ldr.w     r0, [r4, #0x90]
080015b4: bde81040     pop.w     {r4, lr}
080015b8: fff7b8be     b.w       #0x800132c
080015bc: f004         lsls      r0, r6, #0x13
080015be: 0020         movs      r0, #0
080015c0: 0148         ldr       r0, [pc, #4]
080015c2: 01f05bbf     b.w       #0x800347c
080015c6: 0000         movs      r0, r0
080015c8: 8405         lsls      r4, r0, #0x16
080015ca: 0020         movs      r0, #0
080015cc: 1148         ldr       r0, [pc, #0x44]
080015ce: 88b0         sub       sp, #0x20
080015d0: 0121         movs      r1, #1
080015d2: 0068         ldr       r0, [r0]
080015d4: 00f04cfc     bl        #0x8001e70
080015d8: 0123         movs      r3, #1
080015da: 0022         movs      r2, #0
080015dc: 0e49         ldr       r1, [pc, #0x38]
080015de: 6846         mov       r0, sp
080015e0: fff78cfd     bl        #0x80010fc
080015e4: 0022         movs      r2, #0
080015e6: 4ff6ff71     movw      r1, #0xffff
080015ea: 0120         movs      r0, #1
080015ec: dff82cc0     ldr.w     ip, [pc, #0x2c]
080015f0: 00df         svc       #0
080015f2: 07a8         add       r0, sp, #0x1c
080015f4: 00f088fb     bl        #0x8001d08
080015f8: 0028         cmp       r0, #0
080015fa: f3d0         beq       #0x80015e4
080015fc: 9df81c10     ldrb.w    r1, [sp, #0x1c]
08001600: 6846         mov       r0, sp
08001602: fff785fd     bl        #0x8001110
08001606: 07a8         add       r0, sp, #0x1c
08001608: 00f07efb     bl        #0x8001d08
0800160c: 0028         cmp       r0, #0
0800160e: f5d1         bne       #0x80015fc
08001610: e8e7         b         #0x80015e4
08001612: 0000         movs      r0, r0
08001614: 5800         lsls      r0, r3, #1
08001616: 0020         movs      r0, #0
08001618: 151f         subs      r5, r2, #4
0800161a: 0008         lsrs      r0, r0, #0x20
0800161c: 892b         cmp       r3, #0x89
0800161e: 0008         lsrs      r0, r0, #0x20
08001620: 614c         ldr       r4, [pc, #0x184]
08001622: 624f         ldr       r7, [pc, #0x188]
08001624: e51e         subs      r5, r4, #3
08001626: 84b0         sub       sp, #0x10
08001628: 661e         subs      r6, r4, #1
0800162a: 04f10408     add.w     r8, r4, #4
0800162e: 04f10109     add.w     sb, r4, #1
08001632: 04f1020a     add.w     sl, r4, #2
08001636: 0022         movs      r2, #0
08001638: 4ff6ff71     movw      r1, #0xffff
0800163c: 0f20         movs      r0, #0xf
0800163e: dff870c1     ldr.w     ip, [pc, #0x170]
08001642: 00df         svc       #0
08001644: dff86cc1     ldr.w     ip, [pc, #0x16c]
08001648: 00df         svc       #0
0800164a: 8346         mov       fp, r0
0800164c: 10f0010f     tst.w     r0, #1
08001650: 17d0         beq       #0x8001682
08001652: 6846         mov       r0, sp
08001654: 00f0ecf8     bl        #0x8001830
08001658: 98b1         cbz       r0, #0x8001682
0800165a: 57a0         adr       r0, #0x15c
0800165c: 0321         movs      r1, #3
0800165e: 0068         ldr       r0, [r0]
08001660: 0190         str       r0, [sp, #4]
08001662: 9df80000     ldrb.w    r0, [sp]
08001666: 8df80500     strb.w    r0, [sp, #5]
0800166a: 9df80100     ldrb.w    r0, [sp, #1]
0800166e: 8df80600     strb.w    r0, [sp, #6]
08001672: 01a8         add       r0, sp, #4
08001674: 00f06efb     bl        #0x8001d54
08001678: 6846         mov       r0, sp
0800167a: 00f0d9f8     bl        #0x8001830
0800167e: 0028         cmp       r0, #0
08001680: ebd1         bne       #0x800165a
08001682: 1bf0020f     tst.w     fp, #2
08001686: 17d0         beq       #0x80016b8
08001688: 6846         mov       r0, sp
0800168a: 00f009f9     bl        #0x80018a0
0800168e: 98b1         cbz       r0, #0x80016b8
08001690: 4aa0         adr       r0, #0x128
08001692: 0321         movs      r1, #3
08001694: 0068         ldr       r0, [r0]
08001696: 0190         str       r0, [sp, #4]
08001698: 9df80000     ldrb.w    r0, [sp]
0800169c: 8df80500     strb.w    r0, [sp, #5]
080016a0: 9df80100     ldrb.w    r0, [sp, #1]
080016a4: 8df80600     strb.w    r0, [sp, #6]
080016a8: 01a8         add       r0, sp, #4
080016aa: 00f053fb     bl        #0x8001d54
080016ae: 6846         mov       r0, sp
080016b0: 00f0f6f8     bl        #0x80018a0
080016b4: 0028         cmp       r0, #0
080016b6: ebd1         bne       #0x8001690
080016b8: 1bf0040f     tst.w     fp, #4
080016bc: 17d0         beq       #0x80016ee
080016be: 6846         mov       r0, sp
080016c0: 00f05cf9     bl        #0x800197c
080016c4: 98b1         cbz       r0, #0x80016ee
080016c6: 3ea0         adr       r0, #0xf8
080016c8: 0321         movs      r1, #3
080016ca: 0068         ldr       r0, [r0]
080016cc: 0190         str       r0, [sp, #4]
080016ce: 9df80000     ldrb.w    r0, [sp]
080016d2: 8df80500     strb.w    r0, [sp, #5]
080016d6: 9df80100     ldrb.w    r0, [sp, #1]
080016da: 8df80600     strb.w    r0, [sp, #6]
080016de: 01a8         add       r0, sp, #4
080016e0: 00f038fb     bl        #0x8001d54
080016e4: 6846         mov       r0, sp
080016e6: 00f049f9     bl        #0x800197c
080016ea: 0028         cmp       r0, #0
080016ec: ebd1         bne       #0x80016c6
080016ee: 1bf0080f     tst.w     fp, #8
080016f2: a0d0         beq       #0x8001636
080016f4: 2878         ldrb      r0, [r5]
080016f6: 2178         ldrb      r1, [r4]
080016f8: 3038         subs      r0, #0x30
080016fa: 00ebc002     add.w     r2, r0, r0, lsl #3
080016fe: 02eb0010     add.w     r0, r2, r0, lsl #4
08001702: 01eb8001     add.w     r1, r1, r0, lsl #2
08001706: 3078         ldrb      r0, [r6]
08001708: 00eb8000     add.w     r0, r0, r0, lsl #2
0800170c: 07eb4000     add.w     r0, r7, r0, lsl #1
08001710: 0844         add       r0, r1
08001712: 80b2         uxth      r0, r0
08001714: b0f57a7f     cmp.w     r0, #0x3e8
08001718: 28bf         it        hs
0800171a: 0020         movhs     r0, #0
0800171c: 29a1         adr       r1, #0xa4
0800171e: 0968         ldr       r1, [r1]
08001720: 0191         str       r1, [sp, #4]
08001722: c0f3c611     ubfx      r1, r0, #7, #7
08001726: 8df80510     strb.w    r1, [sp, #5]
0800172a: 00f07f00     and       r0, r0, #0x7f
0800172e: 8df80600     strb.w    r0, [sp, #6]
08001732: 0321         movs      r1, #3
08001734: 01a8         add       r0, sp, #4
08001736: 00f00dfb     bl        #0x8001d54
0800173a: 99f80000     ldrb.w    r0, [sb]
0800173e: 98f80010     ldrb.w    r1, [r8]
08001742: 3038         subs      r0, #0x30
08001744: 00eb4002     add.w     r2, r0, r0, lsl #1
08001748: c2ebc010     rsb       r0, r2, r0, lsl #7
0800174c: 01ebc001     add.w     r1, r1, r0, lsl #3
08001750: 9af80000     ldrb.w    r0, [sl]
08001754: 6422         movs      r2, #0x64
08001756: 4243         muls      r2, r0, r2
08001758: 1b48         ldr       r0, [pc, #0x6c]
0800175a: 0078         ldrb      r0, [r0]
0800175c: 00eb8000     add.w     r0, r0, r0, lsl #2
08001760: 02eb4000     add.w     r0, r2, r0, lsl #1
08001764: 0844         add       r0, r1
08001766: a0f5a050     sub.w     r0, r0, #0x1400
0800176a: d038         subs      r0, #0xd0
0800176c: 80b2         uxth      r0, r0
0800176e: 42f20f71     movw      r1, #0x270f
08001772: 8842         cmp       r0, r1
08001774: 88bf         it        hi
08001776: 0020         movhi     r0, #0
08001778: 14a1         adr       r1, #0x50
0800177a: 0968         ldr       r1, [r1]
0800177c: 0291         str       r1, [sp, #8]
0800177e: c0f3c611     ubfx      r1, r0, #7, #7
08001782: 8df80910     strb.w    r1, [sp, #9]
08001786: 00f07f00     and       r0, r0, #0x7f
0800178a: 8df80a00     strb.w    r0, [sp, #0xa]
0800178e: 0321         movs      r1, #3
08001790: 02a8         add       r0, sp, #8
08001792: 00f0dffa     bl        #0x8001d54
08001796: 0ea0         adr       r0, #0x38
08001798: 0121         movs      r1, #1
0800179a: 0068         ldr       r0, [r0]
0800179c: 0390         str       r0, [sp, #0xc]
0800179e: 03a8         add       r0, sp, #0xc
080017a0: 00f0d8fa     bl        #0x8001d54
080017a4: 47e7         b         #0x8001636
080017a6: 0000         movs      r0, r0
080017a8: fbff0108     vtbl.8    d16, {d11}, d1
080017ac: f0fdffff     ldc2l     p15, c15, [r0, #0x3fc]!
080017b0: 892b         cmp       r3, #0x89
080017b2: 0008         lsrs      r0, r0, #0x20
080017b4: d12a         cmp       r2, #0xd1
080017b6: 0008         lsrs      r0, r0, #0x20
080017b8: 9000         lsls      r0, r2, #2
080017ba: 0000         movs      r0, r0
080017bc: 8000         lsls      r0, r0, #2
080017be: 0000         movs      r0, r0
080017c0: 9100         lsls      r1, r2, #2
080017c2: 0000         movs      r0, r0
080017c4: b100         lsls      r1, r6, #2
080017c6: 0000         movs      r0, r0
080017c8: feff0108     vtbl.8    d16, {d14}, d1
080017cc: b000         lsls      r0, r6, #2
080017ce: 0000         movs      r0, r0
080017d0: ff00         lsls      r7, r7, #3
080017d2: 0000         movs      r0, r0
080017d4: 0149         ldr       r1, [pc, #4]
080017d6: 0860         str       r0, [r1]
080017d8: 7047         bx        lr
080017da: 0000         movs      r0, r0
080017dc: a000         lsls      r0, r4, #2
080017de: 0020         movs      r0, #0
080017e0: 0349         ldr       r1, [pc, #0xc]
080017e2: 0860         str       r0, [r1]
080017e4: 6431         adds      r1, #0x64
080017e6: 0860         str       r0, [r1]
080017e8: c831         adds      r1, #0xc8
080017ea: 0860         str       r0, [r1]
080017ec: 7047         bx        lr
080017ee: 0000         movs      r0, r0
080017f0: fc02         lsls      r4, r7, #0xb
080017f2: 0020         movs      r0, #0
080017f4: 10b5         push      {r4, lr}
080017f6: 084c         ldr       r4, [pc, #0x20]
080017f8: 0121         movs      r1, #1
080017fa: 2046         mov       r0, r4
080017fc: fff7dafb     bl        #0x8000fb4
08001800: 0028         cmp       r0, #0
08001802: 08bf         it        eq
08001804: 10bd         popeq     {r4, pc}
08001806: 0121         movs      r1, #1
08001808: 2046         mov       r0, r4
0800180a: fff7bffa     bl        #0x8000d8c
0800180e: bde81040     pop.w     {r4, lr}
08001812: 0248         ldr       r0, [pc, #8]
08001814: 00f01fbc     b.w       #0x8002056
08001818: 002c         cmp       r4, #0
0800181a: 0140         ands      r1, r0
0800181c: 1402         lsls      r4, r2, #8
0800181e: 0020         movs      r0, #0
08001820: 0249         ldr       r1, [pc, #8]
08001822: 4860         str       r0, [r1, #4]
08001824: 1c31         adds      r1, #0x1c
08001826: 4860         str       r0, [r1, #4]
08001828: 7047         bx        lr
0800182a: 0000         movs      r0, r0
0800182c: c402         lsls      r4, r0, #0xb
0800182e: 0020         movs      r0, #0
08001830: 0a49         ldr       r1, [pc, #0x28]
08001832: 4a68         ldr       r2, [r1, #4]
08001834: 0b68         ldr       r3, [r1]
08001836: 9a42         cmp       r2, r3
08001838: 04bf         itt       eq
0800183a: 0020         moveq     r0, #0
0800183c: 7047         bxeq      lr
0800183e: 4a68         ldr       r2, [r1, #4]
08001840: 01eb4202     add.w     r2, r1, r2, lsl #1
08001844: 1289         ldrh      r2, [r2, #8]
08001846: 0280         strh      r2, [r0]
08001848: 4868         ldr       r0, [r1, #4]
0800184a: 3f28         cmp       r0, #0x3f
0800184c: babf         itte      lt
0800184e: 4868         ldrlt     r0, [r1, #4]
08001850: 401c         addlt     r0, r0, #1
08001852: 0020         movge     r0, #0
08001854: 4860         str       r0, [r1, #4]
08001856: 0120         movs      r0, #1
08001858: 7047         bx        lr
0800185a: 0000         movs      r0, r0
0800185c: d405         lsls      r4, r2, #0x17
0800185e: 0020         movs      r0, #0
08001860: 2de9f041     push.w    {r4, r5, r6, r7, r8, lr}
08001864: 0d4e         ldr       r6, [pc, #0x34]
08001866: 0446         mov       r4, r0
08001868: 0d46         mov       r5, r1
0800186a: 56f82400     ldr.w     r0, [r6, r4, lsl #2]
0800186e: 1f46         mov       r7, r3
08001870: 9046         mov       r8, r2
08001872: 0168         ldr       r1, [r0]
08001874: d1f810c0     ldr.w     ip, [r1, #0x10]
08001878: 2946         mov       r1, r5
0800187a: e047         blx       ip
0800187c: 0121         movs      r1, #1
0800187e: 01fa08f1     lsl.w     r1, r1, r8
08001882: 002f         cmp       r7, #0
08001884: 14bf         ite       ne
08001886: 0143         orrne     r1, r0
08001888: 20ea0101     biceq.w   r1, r0, r1
0800188c: 56f82400     ldr.w     r0, [r6, r4, lsl #2]
08001890: 0268         ldr       r2, [r0]
08001892: d368         ldr       r3, [r2, #0xc]
08001894: 2a46         mov       r2, r5
08001896: bde8f041     pop.w     {r4, r5, r6, r7, r8, lr}
0800189a: 1847         bx        r3
0800189c: 0000         movs      r0, r0
0800189e: 0020         movs      r0, #0
080018a0: 0a49         ldr       r1, [pc, #0x28]
080018a2: 4a68         ldr       r2, [r1, #4]
080018a4: 0b68         ldr       r3, [r1]
080018a6: 9a42         cmp       r2, r3
080018a8: 04bf         itt       eq
080018aa: 0020         moveq     r0, #0
080018ac: 7047         bxeq      lr
080018ae: 4a68         ldr       r2, [r1, #4]
080018b0: 01eb4202     add.w     r2, r1, r2, lsl #1
080018b4: 1289         ldrh      r2, [r2, #8]
080018b6: 0280         strh      r2, [r0]
080018b8: 4868         ldr       r0, [r1, #4]
080018ba: 1f28         cmp       r0, #0x1f
080018bc: babf         itte      lt
080018be: 4868         ldrlt     r0, [r1, #4]
080018c0: 401c         addlt     r0, r0, #1
080018c2: 0020         movge     r0, #0
080018c4: 4860         str       r0, [r1, #4]
080018c6: 0120         movs      r0, #1
080018c8: 7047         bx        lr
080018ca: 0000         movs      r0, r0
080018cc: d406         lsls      r4, r2, #0x1b
080018ce: 0020         movs      r0, #0
080018d0: 0148         ldr       r0, [pc, #4]
080018d2: 4168         ldr       r1, [r0, #4]
080018d4: 0160         str       r1, [r0]
080018d6: 7047         bx        lr
080018d8: d405         lsls      r4, r2, #0x17
080018da: 0020         movs      r0, #0
080018dc: dff890c0     ldr.w     ip, [pc, #0x90]
080018e0: 0a1f         subs      r2, r1, #4
080018e2: 1cf81030     ldrb.w    r3, [ip, r0, lsl #1]
080018e6: 0bb1         cbz       r3, #0x80018ec
080018e8: 012b         cmp       r3, #1
080018ea: 0dd0         beq       #0x8001908
080018ec: 0429         cmp       r1, #4
080018ee: 0dd3         blo       #0x800190c
080018f0: b1f57d7f     cmp.w     r1, #0x3f4
080018f4: 0fd8         bhi       #0x8001916
080018f6: c2eb8211     rsb       r1, r2, r2, lsl #6
080018fa: 4900         lsls      r1, r1, #1
080018fc: 40f2f132     movw      r2, #0x3f1
08001900: b1fbf2f1     udiv      r1, r1, r2
08001904: 4a1c         adds      r2, r1, #1
08001906: 24e0         b         #0x8001952
08001908: 0429         cmp       r1, #4
0800190a: 01d2         bhs       #0x8001910
0800190c: 0022         movs      r2, #0
0800190e: 20e0         b         #0x8001952
08001910: b1f57d7f     cmp.w     r1, #0x3f4
08001914: 01d9         bls       #0x800191a
08001916: 7f22         movs      r2, #0x7f
08001918: 1be0         b         #0x8001952
0800191a: b1f5ec7f     cmp.w     r1, #0x1d8
0800191e: 08d2         bhs       #0x8001932
08001920: c2eb4211     rsb       r1, r2, r2, lsl #5
08001924: 4900         lsls      r1, r1, #1
08001926: 4ff4ea72     mov.w     r2, #0x1d4
0800192a: b1fbf2f1     udiv      r1, r1, r2
0800192e: 4a1c         adds      r2, r1, #1
08001930: 0fe0         b         #0x8001952
08001932: b1f50a7f     cmp.w     r1, #0x228
08001936: 38bf         it        lo
08001938: 4022         movlo     r2, #0x40
0800193a: 0ad3         blo       #0x8001952
0800193c: a1f50a71     sub.w     r1, r1, #0x228
08001940: c1eb4111     rsb       r1, r1, r1, lsl #5
08001944: 4900         lsls      r1, r1, #1
08001946: 4ff4e772     mov.w     r2, #0x1ce
0800194a: b1fbf2f1     udiv      r1, r1, r2
0800194e: 01f14102     add.w     r2, r1, #0x41
08001952: 0ceb4000     add.w     r0, ip, r0, lsl #1
08001956: 4178         ldrb      r1, [r0, #1]
08001958: 0648         ldr       r0, [pc, #0x18]
0800195a: 435c         ldrb      r3, [r0, r1]
0800195c: 9342         cmp       r3, r2
0800195e: 08bf         it        eq
08001960: 7047         bxeq      lr
08001962: d2b2         uxtb      r2, r2
08001964: 4254         strb      r2, [r0, r1]
08001966: 0023         movs      r3, #0
08001968: 0348         ldr       r0, [pc, #0xc]
0800196a: 01f0edbe     b.w       #0x8003748
0800196e: 0000         movs      r0, r0
08001970: 1400         movs      r4, r2
08001972: 0020         movs      r0, #0
08001974: 6406         lsls      r4, r4, #0x19
08001976: 0020         movs      r0, #0
08001978: d405         lsls      r4, r2, #0x17
0800197a: 0020         movs      r0, #0
0800197c: 0a49         ldr       r1, [pc, #0x28]
0800197e: 4a68         ldr       r2, [r1, #4]
08001980: 0b68         ldr       r3, [r1]
08001982: 9a42         cmp       r2, r3
08001984: 04bf         itt       eq
08001986: 0020         moveq     r0, #0
08001988: 7047         bxeq      lr
0800198a: 4a68         ldr       r2, [r1, #4]
0800198c: 01eb4202     add.w     r2, r1, r2, lsl #1
08001990: 1289         ldrh      r2, [r2, #8]
08001992: 0280         strh      r2, [r0]
08001994: 4868         ldr       r0, [r1, #4]
08001996: 1f28         cmp       r0, #0x1f
08001998: babf         itte      lt
0800199a: 4868         ldrlt     r0, [r1, #4]
0800199c: 401c         addlt     r0, r0, #1
0800199e: 0020         movge     r0, #0
080019a0: 4860         str       r0, [r1, #4]
080019a2: 0120         movs      r0, #1
080019a4: 7047         bx        lr
080019a6: 0000         movs      r0, r0
080019a8: 8406         lsls      r4, r0, #0x1a
080019aa: 0020         movs      r0, #0
080019ac: 0148         ldr       r0, [pc, #4]
080019ae: 4168         ldr       r1, [r0, #4]
080019b0: 0160         str       r1, [r0]
080019b2: 7047         bx        lr
080019b4: d406         lsls      r4, r2, #0x1b
080019b6: 0020         movs      r0, #0
080019b8: 0a00         movs      r2, r1
080019ba: 0c49         ldr       r1, [pc, #0x30]
080019bc: 0c4b         ldr       r3, [pc, #0x30]
080019be: 095c         ldrb      r1, [r1, r0]
080019c0: 13f801c0     ldrb.w    ip, [r3, r1]
080019c4: 0cbf         ite       eq
080019c6: 0120         moveq     r0, #1
080019c8: 0020         movne     r0, #0
080019ca: 8445         cmp       ip, r0
080019cc: 08bf         it        eq
080019ce: 7047         bxeq      lr
080019d0: 002a         cmp       r2, #0
080019d2: 0cbf         ite       eq
080019d4: 0120         moveq     r0, #1
080019d6: 0020         movne     r0, #0
080019d8: 5854         strb      r0, [r3, r1]
080019da: 0cbf         ite       eq
080019dc: 0122         moveq     r2, #1
080019de: 0022         movne     r2, #0
080019e0: 4ff00003     mov.w     r3, #0
080019e4: 0348         ldr       r0, [pc, #0xc]
080019e6: 01f071be     b.w       #0x80036cc
080019ea: 0000         movs      r0, r0
080019ec: 513b         subs      r3, #0x51
080019ee: 0008         lsrs      r0, r0, #0x20
080019f0: 2407         lsls      r4, r4, #0x1c
080019f2: 0020         movs      r0, #0
080019f4: d406         lsls      r4, r2, #0x1b
080019f6: 0020         movs      r0, #0
080019f8: 78b4         push      {r3, r4, r5, r6}
080019fa: 1d4d         ldr       r5, [pc, #0x74]
080019fc: 1d4e         ldr       r6, [pc, #0x74]
080019fe: 0024         movs      r4, #0
08001a00: 05eb4400     add.w     r0, r5, r4, lsl #1
08001a04: 4178         ldrb      r1, [r0, #1]
08001a06: 7f29         cmp       r1, #0x7f
08001a08: 2dd0         beq       #0x8001a66
08001a0a: 735c         ldrb      r3, [r6, r1]
08001a0c: 1a48         ldr       r0, [pc, #0x68]
08001a0e: 61f30702     bfi       r2, r1, #0, #8
08001a12: 63f30f22     bfi       r2, r3, #8, #8
08001a16: 0092         str       r2, [sp]
08001a18: 0168         ldr       r1, [r0]
08001a1a: 4268         ldr       r2, [r0, #4]
08001a1c: 891a         subs      r1, r1, r2
08001a1e: 0029         cmp       r1, #0
08001a20: b8bf         it        lt
08001a22: 4031         addlt     r1, #0x40
08001a24: 09b2         sxth      r1, r1
08001a26: c1f13f01     rsb.w     r1, r1, #0x3f
08001a2a: 09b2         sxth      r1, r1
08001a2c: b9b1         cbz       r1, #0x8001a5e
08001a2e: 0268         ldr       r2, [r0]
08001a30: 00eb4201     add.w     r1, r0, r2, lsl #1
08001a34: bdf80020     ldrh.w    r2, [sp]
08001a38: 0a81         strh      r2, [r1, #8]
08001a3a: 0168         ldr       r1, [r0]
08001a3c: 3f29         cmp       r1, #0x3f
08001a3e: aebf         itee      ge
08001a40: 0021         movge     r1, #0
08001a42: 0168         ldrlt     r1, [r0]
08001a44: 491c         addlt     r1, r1, #1
08001a46: 0246         mov       r2, r0
08001a48: 0160         str       r1, [r0]
08001a4a: d0f88810     ldr.w     r1, [r0, #0x88]
08001a4e: 0029         cmp       r1, #0
08001a50: 1fbf         itttt     ne
08001a52: b2f88c00     ldrhne.w  r0, [r2, #0x8c]
08001a56: 0028         cmpne     r0, #0
08001a58: dff820c0     ldrne.w   ip, [pc, #0x20]
08001a5c: 00df         svcne     #0
08001a5e: 0120         movs      r0, #1
08001a60: dff81cc0     ldr.w     ip, [pc, #0x1c]
08001a64: 00df         svc       #0
08001a66: 641c         adds      r4, r4, #1
08001a68: 202c         cmp       r4, #0x20
08001a6a: c9d3         blo       #0x8001a00
08001a6c: 78bc         pop       {r3, r4, r5, r6}
08001a6e: 7047         bx        lr
08001a70: 1400         movs      r4, r2
08001a72: 0020         movs      r0, #0
08001a74: 6406         lsls      r4, r4, #0x19
08001a76: 0020         movs      r0, #0
08001a78: d405         lsls      r4, r2, #0x17
08001a7a: 0020         movs      r0, #0
08001a7c: 292b         cmp       r3, #0x29
08001a7e: 0008         lsrs      r0, r0, #0x20
08001a80: c92a         cmp       r2, #0xc9
08001a82: 0008         lsrs      r0, r0, #0x20
08001a84: 1a4b         ldr       r3, [pc, #0x68]
08001a86: 82b0         sub       sp, #8
08001a88: 184a         ldr       r2, [pc, #0x60]
08001a8a: 1b5c         ldrb      r3, [r3, r0]
08001a8c: 01f14000     add.w     r0, r1, #0x40
08001a90: 63f30701     bfi       r1, r3, #0, #8
08001a94: 60f30f21     bfi       r1, r0, #8, #8
08001a98: 0091         str       r1, [sp]
08001a9a: 1068         ldr       r0, [r2]
08001a9c: 5168         ldr       r1, [r2, #4]
08001a9e: 401a         subs      r0, r0, r1
08001aa0: 0028         cmp       r0, #0
08001aa2: b8bf         it        lt
08001aa4: 2030         addlt     r0, #0x20
08001aa6: 00b2         sxth      r0, r0
08001aa8: c0f11f00     rsb.w     r0, r0, #0x1f
08001aac: 00b2         sxth      r0, r0
08001aae: 0028         cmp       r0, #0
08001ab0: 04bf         itt       eq
08001ab2: 02b0         addeq     sp, #8
08001ab4: 7047         bxeq      lr
08001ab6: 1168         ldr       r1, [r2]
08001ab8: 02eb4100     add.w     r0, r2, r1, lsl #1
08001abc: bdf80010     ldrh.w    r1, [sp]
08001ac0: 0181         strh      r1, [r0, #8]
08001ac2: 1068         ldr       r0, [r2]
08001ac4: 1f28         cmp       r0, #0x1f
08001ac6: aebf         itee      ge
08001ac8: 0020         movge     r0, #0
08001aca: 1068         ldrlt     r0, [r2]
08001acc: 401c         addlt     r0, r0, #1
08001ace: 1060         str       r0, [r2]
08001ad0: 916c         ldr       r1, [r2, #0x48]
08001ad2: 0029         cmp       r1, #0
08001ad4: 19bf         ittee     ne
08001ad6: b2f84c00     ldrhne.w  r0, [r2, #0x4c]
08001ada: 0028         cmpne     r0, #0
08001adc: 02b0         addeq     sp, #8
08001ade: 7047         bxeq      lr
08001ae0: dff810c0     ldr.w     ip, [pc, #0x10]
08001ae4: 00df         svc       #0
08001ae6: 02b0         add       sp, #8
08001ae8: 7047         bx        lr
08001aea: 0000         movs      r0, r0
08001aec: 8406         lsls      r4, r0, #0x1a
08001aee: 0020         movs      r0, #0
08001af0: 143a         subs      r2, #0x14
08001af2: 0008         lsrs      r0, r0, #0x20
08001af4: 292b         cmp       r3, #0x29
08001af6: 0008         lsrs      r0, r0, #0x20
08001af8: 6928         cmp       r0, #0x69
08001afa: 28bf         it        hs
08001afc: 7047         bxhs      lr
08001afe: 0029         cmp       r1, #0
08001b00: 0cbf         ite       eq
08001b02: 0123         moveq     r3, #1
08001b04: 0023         movne     r3, #0
08001b06: 00eb4000     add.w     r0, r0, r0, lsl #1
08001b0a: dff814c0     ldr.w     ip, [pc, #0x14]
08001b0e: 00eb0c01     add.w     r1, r0, ip
08001b12: 1cf80000     ldrb.w    r0, [ip, r0]
08001b16: 8a78         ldrb      r2, [r1, #2]
08001b18: 4978         ldrb      r1, [r1, #1]
08001b1a: fff7a1be     b.w       #0x8001860
08001b1e: 0000         movs      r0, r0
08001b20: 163a         subs      r2, #0x16
08001b22: 0008         lsrs      r0, r0, #0x20
08001b24: 78b4         push      {r3, r4, r5, r6}
08001b26: 1c4d         ldr       r5, [pc, #0x70]
08001b28: 1c4e         ldr       r6, [pc, #0x70]
08001b2a: 0024         movs      r4, #0
08001b2c: 295d         ldrb      r1, [r5, r4]
08001b2e: 7f29         cmp       r1, #0x7f
08001b30: 2cd0         beq       #0x8001b8c
08001b32: 735c         ldrb      r3, [r6, r1]
08001b34: 1a48         ldr       r0, [pc, #0x68]
08001b36: 61f30702     bfi       r2, r1, #0, #8
08001b3a: 63f30f22     bfi       r2, r3, #8, #8
08001b3e: 0092         str       r2, [sp]
08001b40: 0168         ldr       r1, [r0]
08001b42: 4268         ldr       r2, [r0, #4]
08001b44: 891a         subs      r1, r1, r2
08001b46: 0029         cmp       r1, #0
08001b48: b8bf         it        lt
08001b4a: 2031         addlt     r1, #0x20
08001b4c: 09b2         sxth      r1, r1
08001b4e: c1f11f01     rsb.w     r1, r1, #0x1f
08001b52: 09b2         sxth      r1, r1
08001b54: b1b1         cbz       r1, #0x8001b84
08001b56: 0268         ldr       r2, [r0]
08001b58: 00eb4201     add.w     r1, r0, r2, lsl #1
08001b5c: bdf80020     ldrh.w    r2, [sp]
08001b60: 0a81         strh      r2, [r1, #8]
08001b62: 0168         ldr       r1, [r0]
08001b64: 1f29         cmp       r1, #0x1f
08001b66: aebf         itee      ge
08001b68: 0021         movge     r1, #0
08001b6a: 0168         ldrlt     r1, [r0]
08001b6c: 491c         addlt     r1, r1, #1
08001b6e: 0246         mov       r2, r0
08001b70: 0160         str       r1, [r0]
08001b72: 816c         ldr       r1, [r0, #0x48]
08001b74: 0029         cmp       r1, #0
08001b76: 1fbf         itttt     ne
08001b78: b2f84c00     ldrhne.w  r0, [r2, #0x4c]
08001b7c: 0028         cmpne     r0, #0
08001b7e: dff824c0     ldrne.w   ip, [pc, #0x24]
08001b82: 00df         svcne     #0
08001b84: 0120         movs      r0, #1
08001b86: dff820c0     ldr.w     ip, [pc, #0x20]
08001b8a: 00df         svc       #0
08001b8c: 641c         adds      r4, r4, #1
08001b8e: 582c         cmp       r4, #0x58
08001b90: ccd3         blo       #0x8001b2c
08001b92: 78bc         pop       {r3, r4, r5, r6}
08001b94: 7047         bx        lr
08001b96: 0000         movs      r0, r0
08001b98: 513b         subs      r3, #0x51
08001b9a: 0008         lsrs      r0, r0, #0x20
08001b9c: 2407         lsls      r4, r4, #0x1c
08001b9e: 0020         movs      r0, #0
08001ba0: d406         lsls      r4, r2, #0x1b
08001ba2: 0020         movs      r0, #0
08001ba4: 292b         cmp       r3, #0x29
08001ba6: 0008         lsrs      r0, r0, #0x20
08001ba8: c92a         cmp       r2, #0xc9
08001baa: 0008         lsrs      r0, r0, #0x20
08001bac: 2de9f041     push.w    {r4, r5, r6, r7, r8, lr}
08001bb0: 534c         ldr       r4, [pc, #0x14c]
08001bb2: 0426         movs      r6, #4
08001bb4: 0123         movs      r3, #1
08001bb6: 227c         ldrb      r2, [r4, #0x10]
08001bb8: a068         ldr       r0, [r4, #8]
08001bba: 06ebc201     add.w     r1, r6, r2, lsl #3
08001bbe: 415c         ldrb      r1, [r0, r1]
08001bc0: 50f83200     ldr.w     r0, [r0, r2, lsl #3]
08001bc4: 1a46         mov       r2, r3
08001bc6: fef7d3fc     bl        #0x8000570
08001bca: 217c         ldrb      r1, [r4, #0x10]
08001bcc: a068         ldr       r0, [r4, #8]
08001bce: 50f83100     ldr.w     r0, [r0, r1, lsl #3]
08001bd2: 0121         movs      r1, #1
08001bd4: fef719fd     bl        #0x800060a
08001bd8: 4a4d         ldr       r5, [pc, #0x128]
08001bda: 0221         movs      r1, #2
08001bdc: 2846         mov       r0, r5
08001bde: fef791fc     bl        #0x8000504
08001be2: 0028         cmp       r0, #0
08001be4: f9d0         beq       #0x8001bda
08001be6: e07b         ldrb      r0, [r4, #0xf]
08001be8: 217c         ldrb      r1, [r4, #0x10]
08001bea: 627b         ldrb      r2, [r4, #0xd]
08001bec: 01fb0207     mla       r7, r1, r2, r0
08001bf0: 0121         movs      r1, #1
08001bf2: 04ebc705     add.w     r5, r4, r7, lsl #3
08001bf6: c1f10300     rsb.w     r0, r1, #3
08001bfa: c1f10402     rsb.w     r2, r1, #4
08001bfe: 05eb4000     add.w     r0, r5, r0, lsl #1
08001c02: 05eb4202     add.w     r2, r5, r2, lsl #1
08001c06: b0f85200     ldrh.w    r0, [r0, #0x52]
08001c0a: 491c         adds      r1, r1, #1
08001c0c: a2f85200     strh.w    r0, [r2, #0x52]
08001c10: 0429         cmp       r1, #4
08001c12: f0d3         blo       #0x8001bf6
08001c14: 207c         ldrb      r0, [r4, #0x10]
08001c16: a168         ldr       r1, [r4, #8]
08001c18: 51f83000     ldr.w     r0, [r1, r0, lsl #3]
08001c1c: fef76ffc     bl        #0x80004fe
08001c20: 4ff0000c     mov.w     ip, #0
08001c24: a5f85200     strh.w    r0, [r5, #0x52]
08001c28: 6346         mov       r3, ip
08001c2a: 40f6ff70     movw      r0, #0xfff
08001c2e: 6246         mov       r2, ip
08001c30: 05eb4201     add.w     r1, r5, r2, lsl #1
08001c34: b1f85210     ldrh.w    r1, [r1, #0x52]
08001c38: 9942         cmp       r1, r3
08001c3a: 88bf         it        hi
08001c3c: 0b46         movhi     r3, r1
08001c3e: 8142         cmp       r1, r0
08001c40: 38bf         it        lo
08001c42: 0846         movlo     r0, r1
08001c44: 8c44         add       ip, r1
08001c46: 521c         adds      r2, r2, #1
08001c48: 042a         cmp       r2, #4
08001c4a: f1d3         blo       #0x8001c30
08001c4c: 1844         add       r0, r3
08001c4e: 04eb4703     add.w     r3, r4, r7, lsl #1
08001c52: aceb0000     sub.w     r0, ip, r0
08001c56: c108         lsrs      r1, r0, #3
08001c58: 5a8a         ldrh      r2, [r3, #0x12]
08001c5a: a1f1040c     sub.w     ip, r1, #4
08001c5e: 501a         subs      r0, r2, r1
08001c60: 40f2f238     movw      r8, #0x3f2
08001c64: 0025         movs      r5, #0
08001c66: c445         cmp       ip, r8
08001c68: 13d2         bhs       #0x8001c92
08001c6a: 042a         cmp       r2, #4
08001c6c: 01d2         bhs       #0x8001c72
08001c6e: 0429         cmp       r1, #4
08001c70: 0fd2         bhs       #0x8001c92
08001c72: 04eb070c     add.w     ip, r4, r7
08001c76: 9cf85221     ldrb.w    r2, [ip, #0x152]
08001c7a: 282a         cmp       r2, #0x28
08001c7c: 03d9         bls       #0x8001c86
08001c7e: 0f30         adds      r0, #0xf
08001c80: 1f28         cmp       r0, #0x1f
08001c82: 0fd3         blo       #0x8001ca4
08001c84: 05e0         b         #0x8001c92
08001c86: 521c         adds      r2, r2, #1
08001c88: c01d         adds      r0, r0, #7
08001c8a: 8cf85221     strb.w    r2, [ip, #0x152]
08001c8e: 0f28         cmp       r0, #0xf
08001c90: 08d3         blo       #0x8001ca4
08001c92: e019         adds      r0, r4, r7
08001c94: 5982         strh      r1, [r3, #0x12]
08001c96: 80f85251     strb.w    r5, [r0, #0x152]
08001c9a: 2268         ldr       r2, [r4]
08001c9c: 002a         cmp       r2, #0
08001c9e: 1cbf         itt       ne
08001ca0: 3846         movne     r0, r7
08001ca2: 9047         blxne     r2
08001ca4: e07b         ldrb      r0, [r4, #0xf]
08001ca6: 401c         adds      r0, r0, #1
08001ca8: c0b2         uxtb      r0, r0
08001caa: e073         strb      r0, [r4, #0xf]
08001cac: 617b         ldrb      r1, [r4, #0xd]
08001cae: 8842         cmp       r0, r1
08001cb0: 08d3         blo       #0x8001cc4
08001cb2: e573         strb      r5, [r4, #0xf]
08001cb4: 207c         ldrb      r0, [r4, #0x10]
08001cb6: 401c         adds      r0, r0, #1
08001cb8: c0b2         uxtb      r0, r0
08001cba: 2074         strb      r0, [r4, #0x10]
08001cbc: a17b         ldrb      r1, [r4, #0xe]
08001cbe: 8842         cmp       r0, r1
08001cc0: 28bf         it        hs
08001cc2: 2574         strbhs    r5, [r4, #0x10]
08001cc4: 0025         movs      r5, #0
08001cc6: 207b         ldrb      r0, [r4, #0xc]
08001cc8: 0028         cmp       r0, #0
08001cca: 98bf         it        ls
08001ccc: bde8f081     popls.w   {r4, r5, r6, r7, r8, pc}
08001cd0: e07b         ldrb      r0, [r4, #0xf]
08001cd2: 06ebc501     add.w     r1, r6, r5, lsl #3
08001cd6: e840         lsrs      r0, r5
08001cd8: 10f0010f     tst.w     r0, #1
08001cdc: 6068         ldr       r0, [r4, #4]
08001cde: 415a         ldrh      r1, [r0, r1]
08001ce0: 50f83500     ldr.w     r0, [r0, r5, lsl #3]
08001ce4: 89b2         uxth      r1, r1
08001ce6: 02d0         beq       #0x8001cee
08001ce8: fef7c2fd     bl        #0x8000870
08001cec: 01e0         b         #0x8001cf2
08001cee: fef7bdfd     bl        #0x800086c
08001cf2: 207b         ldrb      r0, [r4, #0xc]
08001cf4: 6d1c         adds      r5, r5, #1
08001cf6: a842         cmp       r0, r5
08001cf8: ead8         bhi       #0x8001cd0
08001cfa: bde8f081     pop.w     {r4, r5, r6, r7, r8, pc}
08001cfe: 0000         movs      r0, r0
08001d00: a000         lsls      r0, r4, #2
08001d02: 0020         movs      r0, #0
08001d04: 0024         movs      r4, #0
08001d06: 0140         ands      r1, r0
08001d08: 0a49         ldr       r1, [pc, #0x28]
08001d0a: 4a68         ldr       r2, [r1, #4]
08001d0c: 0b68         ldr       r3, [r1]
08001d0e: 9a42         cmp       r2, r3
08001d10: 04bf         itt       eq
08001d12: 0020         moveq     r0, #0
08001d14: 7047         bxeq      lr
08001d16: 4a68         ldr       r2, [r1, #4]
08001d18: 01f10803     add.w     r3, r1, #8
08001d1c: d25c         ldrb      r2, [r2, r3]
08001d1e: 0270         strb      r2, [r0]
08001d20: 4868         ldr       r0, [r1, #4]
08001d22: 7f28         cmp       r0, #0x7f
08001d24: babf         itte      lt
08001d26: 4868         ldrlt     r0, [r1, #4]
08001d28: 401c         addlt     r0, r0, #1
08001d2a: 0020         movge     r0, #0
08001d2c: 4860         str       r0, [r1, #4]
08001d2e: 0120         movs      r0, #1
08001d30: 7047         bx        lr
08001d32: 0000         movs      r0, r0
08001d34: f004         lsls      r0, r6, #0x13
08001d36: 0020         movs      r0, #0
08001d38: 014a         ldr       r2, [pc, #4]
08001d3a: 1060         str       r0, [r2]
08001d3c: 9180         strh      r1, [r2, #4]
08001d3e: 7047         bx        lr
08001d40: 5c06         lsls      r4, r3, #0x19
08001d42: 0020         movs      r0, #0
08001d44: 024a         ldr       r2, [pc, #8]
08001d46: 9064         str       r0, [r2, #0x48]
08001d48: a2f84c10     strh.w    r1, [r2, #0x4c]
08001d4c: 7047         bx        lr
08001d4e: 0000         movs      r0, r0
08001d50: d406         lsls      r4, r2, #0x1b
08001d52: 0020         movs      r0, #0
08001d54: 2de9f041     push.w    {r4, r5, r6, r7, r8, lr}
08001d58: 2a4c         ldr       r4, [pc, #0xa8]
08001d5a: 0126         movs      r6, #1
08001d5c: 4ff0e027     mov.w     r7, #-0x1fff2000
08001d60: 94f94c20     ldrsb.w   r2, [r4, #0x4c]
08001d64: 02f01f03     and       r3, r2, #0x1f
08001d68: 06fa03f3     lsl.w     r3, r6, r3
08001d6c: 5209         lsrs      r2, r2, #5
08001d6e: 07eb8202     add.w     r2, r7, r2, lsl #2
08001d72: c2f88031     str.w     r3, [r2, #0x180]
08001d76: 2268         ldr       r2, [r4]
08001d78: 1ffa81fc     uxth.w    ip, r1
08001d7c: 6368         ldr       r3, [r4, #4]
08001d7e: d21a         subs      r2, r2, r3
08001d80: 002a         cmp       r2, #0
08001d82: b8bf         it        lt
08001d84: 4032         addlt     r2, #0x40
08001d86: 12b2         sxth      r2, r2
08001d88: c2f13f02     rsb.w     r2, r2, #0x3f
08001d8c: 12b2         sxth      r2, r2
08001d8e: 6245         cmp       r2, ip
08001d90: 16db         blt       #0x8001dc0
08001d92: 0022         movs      r2, #0
08001d94: bcf1000f     cmp.w     ip, #0
08001d98: 88bf         it        hi
08001d9a: 04f10808     addhi.w   r8, r4, #8
08001d9e: 0fd9         bls       #0x8001dc0
08001da0: 10f8015b     ldrb      r5, [r0], #1
08001da4: 2368         ldr       r3, [r4]
08001da6: 03f80850     strb.w    r5, [r3, r8]
08001daa: 2368         ldr       r3, [r4]
08001dac: 3f2b         cmp       r3, #0x3f
08001dae: babf         itte      lt
08001db0: 2368         ldrlt     r3, [r4]
08001db2: 5b1c         addlt     r3, r3, #1
08001db4: 0023         movge     r3, #0
08001db6: 2360         str       r3, [r4]
08001db8: 521c         adds      r2, r2, #1
08001dba: 92b2         uxth      r2, r2
08001dbc: 6245         cmp       r2, ip
08001dbe: efd3         blo       #0x8001da0
08001dc0: 94f94c00     ldrsb.w   r0, [r4, #0x4c]
08001dc4: 00f01f02     and       r2, r0, #0x1f
08001dc8: 06fa02f2     lsl.w     r2, r6, r2
08001dcc: 4009         lsrs      r0, r0, #5
08001dce: 07eb8000     add.w     r0, r7, r0, lsl #2
08001dd2: c0f80021     str.w     r2, [r0, #0x100]
08001dd6: 2068         ldr       r0, [r4]
08001dd8: 6268         ldr       r2, [r4, #4]
08001dda: 801a         subs      r0, r0, r2
08001ddc: 0028         cmp       r0, #0
08001dde: b8bf         it        lt
08001de0: 4030         addlt     r0, #0x40
08001de2: 00b2         sxth      r0, r0
08001de4: 8842         cmp       r0, r1
08001de6: 18bf         it        ne
08001de8: bde8f081     popne.w   {r4, r5, r6, r7, r8, pc}
08001dec: 2046         mov       r0, r4
08001dee: 01f045fb     bl        #0x800347c
08001df2: a06c         ldr       r0, [r4, #0x48]
08001df4: bde8f041     pop.w     {r4, r5, r6, r7, r8, lr}
08001df8: 0122         movs      r2, #1
08001dfa: 40f22771     movw      r1, #0x727
08001dfe: fff723ba     b.w       #0x8001248
08001e02: 0000         movs      r0, r0
08001e04: 8405         lsls      r4, r0, #0x16
08001e06: 0020         movs      r0, #0
08001e08: 1828         cmp       r0, #0x18
08001e0a: 28bf         it        hs
08001e0c: 7047         bxhs      lr
08001e0e: 0029         cmp       r1, #0
08001e10: 0cbf         ite       eq
08001e12: 0123         moveq     r3, #1
08001e14: 0023         movne     r3, #0
08001e16: 00eb4000     add.w     r0, r0, r0, lsl #1
08001e1a: dff814c0     ldr.w     ip, [pc, #0x14]
08001e1e: 00eb0c01     add.w     r1, r0, ip
08001e22: 1cf80000     ldrb.w    r0, [ip, r0]
08001e26: 8a78         ldrb      r2, [r1, #2]
08001e28: 4978         ldrb      r1, [r1, #1]
08001e2a: fff719bd     b.w       #0x8001860
08001e2e: 0000         movs      r0, r0
08001e30: 6c39         subs      r1, #0x6c
08001e32: 0008         lsrs      r0, r0, #0x20
08001e34: 2028         cmp       r0, #0x20
08001e36: 28bf         it        hs
08001e38: 7047         bxhs      lr
08001e3a: 0029         cmp       r1, #0
08001e3c: 0cbf         ite       eq
08001e3e: 0123         moveq     r3, #1
08001e40: 0023         movne     r3, #0
08001e42: 00eb4000     add.w     r0, r0, r0, lsl #1
08001e46: dff814c0     ldr.w     ip, [pc, #0x14]
08001e4a: 00eb0c01     add.w     r1, r0, ip
08001e4e: 1cf80000     ldrb.w    r0, [ip, r0]
08001e52: 8a78         ldrb      r2, [r1, #2]
08001e54: 4978         ldrb      r1, [r1, #1]
08001e56: fff703bd     b.w       #0x8001860
08001e5a: 0000         movs      r0, r0
08001e5c: b439         subs      r1, #0xb4
08001e5e: 0008         lsrs      r0, r0, #0x20
08001e60: 024a         ldr       r2, [pc, #8]
08001e62: 9064         str       r0, [r2, #0x48]
08001e64: a2f84c10     strh.w    r1, [r2, #0x4c]
08001e68: 7047         bx        lr
08001e6a: 0000         movs      r0, r0
08001e6c: 8406         lsls      r4, r0, #0x1a
08001e6e: 0020         movs      r0, #0
08001e70: 014a         ldr       r2, [pc, #4]
08001e72: 1060         str       r0, [r2]
08001e74: 9180         strh      r1, [r2, #4]
08001e76: 7047         bx        lr
08001e78: 7805         lsls      r0, r7, #0x15
08001e7a: 0020         movs      r0, #0
08001e7c: 0120         movs      r0, #1
08001e7e: dff87cc0     ldr.w     ip, [pc, #0x7c]
08001e82: 00df         svc       #0
08001e84: 1e48         ldr       r0, [pc, #0x78]
08001e86: fff7a5fc     bl        #0x80017d4
08001e8a: 1e48         ldr       r0, [pc, #0x78]
08001e8c: fff7a8fc     bl        #0x80017e0
08001e90: 1d48         ldr       r0, [pc, #0x74]
08001e92: fff7c5fc     bl        #0x8001820
08001e96: fff7fffa     bl        #0x8001498
08001e9a: fff733fb     bl        #0x8001504
08001e9e: 0024         movs      r4, #0
08001ea0: dff868c0     ldr.w     ip, [pc, #0x68]
08001ea4: 00df         svc       #0
08001ea6: fff781fe     bl        #0x8001bac
08001eaa: fff78dfa     bl        #0x80013c8
08001eae: 641c         adds      r4, r4, #1
08001eb0: b4f5967f     cmp.w     r4, #0x12c
08001eb4: f4d3         blo       #0x8001ea0
08001eb6: fff70bfd     bl        #0x80018d0
08001eba: fff777fd     bl        #0x80019ac
08001ebe: 144c         ldr       r4, [pc, #0x50]
08001ec0: 0121         movs      r1, #1
08001ec2: 2068         ldr       r0, [r4]
08001ec4: fff738ff     bl        #0x8001d38
08001ec8: 0221         movs      r1, #2
08001eca: 2068         ldr       r0, [r4]
08001ecc: fff73aff     bl        #0x8001d44
08001ed0: 0421         movs      r1, #4
08001ed2: 2068         ldr       r0, [r4]
08001ed4: fff7c4ff     bl        #0x8001e60
08001ed8: 0024         movs      r4, #0
08001eda: dff830c0     ldr.w     ip, [pc, #0x30]
08001ede: 00df         svc       #0
08001ee0: fff764fe     bl        #0x8001bac
08001ee4: fff770fa     bl        #0x80013c8
08001ee8: fff7e0fa     bl        #0x80014ac
08001eec: 641c         adds      r4, r4, #1
08001eee: 322c         cmp       r4, #0x32
08001ef0: a4bf         itt       ge
08001ef2: 0024         movge     r4, #0
08001ef4: fff7e8fa     blge      #0x80014c8
08001ef8: efe7         b         #0x8001eda
08001efa: 0000         movs      r0, r0
08001efc: a52c         cmp       r4, #0xa5
08001efe: 0008         lsrs      r0, r0, #0x20
08001f00: dd18         adds      r5, r3, r3
08001f02: 0008         lsrs      r0, r0, #0x20
08001f04: b919         adds      r1, r7, r6
08001f06: 0008         lsrs      r0, r0, #0x20
08001f08: 851a         subs      r5, r0, r2
08001f0a: 0008         lsrs      r0, r0, #0x20
08001f0c: bd2c         cmp       r4, #0xbd
08001f0e: 0008         lsrs      r0, r0, #0x20
08001f10: 5c00         lsls      r4, r3, #1
08001f12: 0020         movs      r0, #0
08001f14: c0f30722     ubfx      r2, r0, #8, #8
08001f18: fa2a         cmp       r2, #0xfa
08001f1a: 20d0         beq       #0x8001f5e
08001f1c: 0ddc         bgt       #0x8001f3a
08001f1e: c0f30743     ubfx      r3, r0, #0x10, #8
08001f22: 4fea1061     lsr.w     r1, r0, #0x18
08001f26: a02a         cmp       r2, #0xa0
08001f28: 13d0         beq       #0x8001f52
08001f2a: e02a         cmp       r2, #0xe0
08001f2c: 14d0         beq       #0x8001f58
08001f2e: e12a         cmp       r2, #0xe1
08001f30: 18bf         it        ne
08001f32: 7047         bxne      lr
08001f34: 1846         mov       r0, r3
08001f36: fff77dbf     b.w       #0x8001e34
08001f3a: fb2a         cmp       r2, #0xfb
08001f3c: 11d0         beq       #0x8001f62
08001f3e: ff2a         cmp       r2, #0xff
08001f40: 18bf         it        ne
08001f42: 7047         bxne      lr
08001f44: 0848         ldr       r0, [pc, #0x20]
08001f46: dff824c0     ldr.w     ip, [pc, #0x24]
08001f4a: 0168         ldr       r1, [r0]
08001f4c: 0820         movs      r0, #8
08001f4e: 00df         svc       #0
08001f50: 7047         bx        lr
08001f52: 1846         mov       r0, r3
08001f54: fff7d0bd     b.w       #0x8001af8
08001f58: 1846         mov       r0, r3
08001f5a: fff755bf     b.w       #0x8001e08
08001f5e: fff7e1bd     b.w       #0x8001b24
08001f62: fff749bd     b.w       #0x80019f8
08001f66: 0000         movs      r0, r0
08001f68: 5c00         lsls      r4, r3, #1
08001f6a: 0020         movs      r0, #0
08001f6c: 292b         cmp       r3, #0x29
08001f6e: 0008         lsrs      r0, r0, #0x20
08001f70: 0023         movs      r3, #0
08001f72: 0e4a         ldr       r2, [pc, #0x38]
08001f74: 4cf60201     movw      r1, #0xc802
08001f78: 0d48         ldr       r0, [pc, #0x34]
08001f7a: dff838c0     ldr.w     ip, [pc, #0x38]
08001f7e: 00df         svc       #0
08001f80: 0d4c         ldr       r4, [pc, #0x34]
08001f82: 0023         movs      r3, #0
08001f84: 0d4a         ldr       r2, [pc, #0x34]
08001f86: 2060         str       r0, [r4]
08001f88: 0d49         ldr       r1, [pc, #0x34]
08001f8a: 0e48         ldr       r0, [pc, #0x38]
08001f8c: dff824c0     ldr.w     ip, [pc, #0x24]
08001f90: 00df         svc       #0
08001f92: 6060         str       r0, [r4, #4]
08001f94: 0023         movs      r3, #0
08001f96: 0c4a         ldr       r2, [pc, #0x30]
08001f98: 0c49         ldr       r1, [pc, #0x30]
08001f9a: 0d48         ldr       r0, [pc, #0x34]
08001f9c: dff814c0     ldr.w     ip, [pc, #0x14]
08001fa0: 00df         svc       #0
08001fa2: a060         str       r0, [r4, #8]
08001fa4: 0020         movs      r0, #0
08001fa6: dff82cc0     ldr.w     ip, [pc, #0x2c]
08001faa: 00df         svc       #0
08001fac: 8007         lsls      r0, r0, #0x1e
08001fae: 0020         movs      r0, #0
08001fb0: 7d1e         subs      r5, r7, #1
08001fb2: 0008         lsrs      r0, r0, #0x20
08001fb4: 1d33         adds      r3, #0x1d
08001fb6: 0008         lsrs      r0, r0, #0x20
08001fb8: 5400         lsls      r4, r2, #1
08001fba: 0020         movs      r0, #0
08001fbc: 4808         lsrs      r0, r1, #1
08001fbe: 0020         movs      r0, #0
08001fc0: 0390         str       r0, [sp, #0xc]
08001fc2: 0100         movs      r1, r0
08001fc4: cd15         asrs      r5, r1, #0x17
08001fc6: 0008         lsrs      r0, r0, #0x20
08001fc8: d809         lsrs      r0, r3, #7
08001fca: 0020         movs      r0, #0
08001fcc: 0190         str       r0, [sp, #4]
08001fce: 0100         movs      r1, r0
08001fd0: 2116         asrs      r1, r4, #0x18
08001fd2: 0008         lsrs      r0, r0, #0x20
08001fd4: b133         adds      r3, #0xb1
08001fd6: 0008         lsrs      r0, r0, #0x20
08001fd8: 10b5         push      {r4, lr}
08001fda: 0446         mov       r4, r0
08001fdc: 407a         ldrb      r0, [r0, #9]
08001fde: 0c28         cmp       r0, #0xc
08001fe0: 2ad2         bhs       #0x8002038
08001fe2: 217a         ldrb      r1, [r4, #8]
08001fe4: d9b1         cbz       r1, #0x800201e
08001fe6: 0228         cmp       r0, #2
08001fe8: 03d1         bne       #0x8001ff2
08001fea: 2068         ldr       r0, [r4]
08001fec: 0168         ldr       r1, [r0]
08001fee: 2046         mov       r0, r4
08001ff0: 8847         blx       r1
08001ff2: 607a         ldrb      r0, [r4, #9]
08001ff4: c0f10b01     rsb.w     r1, r0, #0xb
08001ff8: 2068         ldr       r0, [r4]
08001ffa: 8268         ldr       r2, [r0, #8]
08001ffc: 2046         mov       r0, r4
08001ffe: 9047         blx       r2
08002000: 0028         cmp       r0, #0
08002002: 6068         ldr       r0, [r4, #4]
08002004: 8188         ldrh      r1, [r0, #4]
08002006: 0068         ldr       r0, [r0]
08002008: 89b2         uxth      r1, r1
0800200a: 02d0         beq       #0x8002012
0800200c: fef730fc     bl        #0x8000870
08002010: 01e0         b         #0x8002016
08002012: fef72bfc     bl        #0x800086c
08002016: 607a         ldrb      r0, [r4, #9]
08002018: 401c         adds      r0, r0, #1
0800201a: 6072         strb      r0, [r4, #9]
0800201c: 05e0         b         #0x800202a
0800201e: 6068         ldr       r0, [r4, #4]
08002020: 8188         ldrh      r1, [r0, #4]
08002022: 0068         ldr       r0, [r0]
08002024: 89b2         uxth      r1, r1
08002026: fef721fc     bl        #0x800086c
0800202a: 207a         ldrb      r0, [r4, #8]
0800202c: 0028         cmp       r0, #0
0800202e: 0cbf         ite       eq
08002030: 0120         moveq     r0, #1
08002032: 0020         movne     r0, #0
08002034: 2072         strb      r0, [r4, #8]
08002036: 10bd         pop       {r4, pc}
08002038: 2068         ldr       r0, [r4]
0800203a: 4168         ldr       r1, [r0, #4]
0800203c: 2046         mov       r0, r4
0800203e: 8847         blx       r1
08002040: 6068         ldr       r0, [r4, #4]
08002042: 8188         ldrh      r1, [r0, #4]
08002044: 0068         ldr       r0, [r0]
08002046: 89b2         uxth      r1, r1
08002048: fef712fc     bl        #0x8000870
0800204c: 0020         movs      r0, #0
0800204e: 6072         strb      r0, [r4, #9]
08002050: 0120         movs      r0, #1
08002052: 2072         strb      r0, [r4, #8]
08002054: 10bd         pop       {r4, pc}
08002056: 70b5         push      {r4, r5, r6, lr}
08002058: 0446         mov       r4, r0
0800205a: 007a         ldrb      r0, [r0, #8]
0800205c: 88b1         cbz       r0, #0x8002082
0800205e: 2068         ldr       r0, [r4]
08002060: 8188         ldrh      r1, [r0, #4]
08002062: 0068         ldr       r0, [r0]
08002064: 89b2         uxth      r1, r1
08002066: fef7fafb     bl        #0x800085e
0800206a: 0028         cmp       r0, #0
0800206c: 2068         ldr       r0, [r4]
0800206e: 8188         ldrh      r1, [r0, #4]
08002070: 0068         ldr       r0, [r0]
08002072: 89b2         uxth      r1, r1
08002074: 02d0         beq       #0x800207c
08002076: fef7f9fb     bl        #0x800086c
0800207a: 0de0         b         #0x8002098
0800207c: fef7f8fb     bl        #0x8000870
08002080: 0ae0         b         #0x8002098
08002082: 6668         ldr       r6, [r4, #4]
08002084: 002e         cmp       r6, #0
08002086: 18bf         it        ne
08002088: 3546         movne     r5, r6
0800208a: 0cd0         beq       #0x80020a6
0800208c: 2846         mov       r0, r5
0800208e: fff7a3ff     bl        #0x8001fd8
08002092: 2d69         ldr       r5, [r5, #0x10]
08002094: b542         cmp       r5, r6
08002096: f9d1         bne       #0x800208c
08002098: 207a         ldrb      r0, [r4, #8]
0800209a: 0028         cmp       r0, #0
0800209c: 18bf         it        ne
0800209e: 0020         movne     r0, #0
080020a0: 01d0         beq       #0x80020a6
080020a2: 2072         strb      r0, [r4, #8]
080020a4: 70bd         pop       {r4, r5, r6, pc}
080020a6: 0120         movs      r0, #1
080020a8: fbe7         b         #0x80020a2
080020aa: 70b5         push      {r4, r5, r6, lr}
080020ac: 0446         mov       r4, r0
080020ae: 8089         ldrh      r0, [r0, #0xc]
080020b0: 81b2         uxth      r1, r0
080020b2: a068         ldr       r0, [r4, #8]
080020b4: fef7ccfb     bl        #0x8000850
080020b8: 0028         cmp       r0, #0
080020ba: 14bf         ite       ne
080020bc: 0125         movne     r5, #1
080020be: 0025         moveq     r5, #0
080020c0: a08a         ldrh      r0, [r4, #0x14]
080020c2: 81b2         uxth      r1, r0
080020c4: 2069         ldr       r0, [r4, #0x10]
080020c6: fef7c3fb     bl        #0x8000850
080020ca: 0028         cmp       r0, #0
080020cc: 18bf         it        ne
080020ce: 0120         movne     r0, #1
080020d0: 267e         ldrb      r6, [r4, #0x18]
080020d2: 0121         movs      r1, #1
080020d4: 0222         movs      r2, #2
080020d6: 4ff0000c     mov.w     ip, #0
080020da: 052e         cmp       r6, #5
080020dc: 2cd2         bhs       #0x8002138
080020de: dfe806f0     tbb       [pc, r6]
080020e2: 030e         lsrs      r3, r0, #0x18
080020e4: 2317         asrs      r3, r4, #0x1c
080020e6: 3000         movs      r0, r6
080020e8: 30ea0503     bics.w    r3, r0, r5
080020ec: 01d0         beq       #0x80020f2
080020ee: 2276         strb      r2, [r4, #0x18]
080020f0: 70bd         pop       {r4, r5, r6, pc}
080020f2: 35ea0000     bics.w    r0, r5, r0
080020f6: 08bf         it        eq
080020f8: 70bd         popeq     {r4, r5, r6, pc}
080020fa: 2176         strb      r1, [r4, #0x18]
080020fc: 70bd         pop       {r4, r5, r6, pc}
080020fe: 55ea0001     orrs.w    r1, r5, r0
08002102: 08bf         it        eq
08002104: 0320         moveq     r0, #3
08002106: 1ad0         beq       #0x800213e
08002108: 0542         tst       r5, r0
0800210a: 08bf         it        eq
0800210c: 70bd         popeq     {r4, r5, r6, pc}
0800210e: 13e0         b         #0x8002138
08002110: 30ea0503     bics.w    r3, r0, r5
08002114: 04d0         beq       #0x8002120
08002116: 607e         ldrb      r0, [r4, #0x19]
08002118: 401e         subs      r0, r0, #1
0800211a: 6076         strb      r0, [r4, #0x19]
0800211c: 2276         strb      r2, [r4, #0x18]
0800211e: 70bd         pop       {r4, r5, r6, pc}
08002120: 35ea0000     bics.w    r0, r5, r0
08002124: e9d1         bne       #0x80020fa
08002126: 70bd         pop       {r4, r5, r6, pc}
08002128: 55ea0001     orrs.w    r1, r5, r0
0800212c: 08bf         it        eq
0800212e: 0420         moveq     r0, #4
08002130: 05d0         beq       #0x800213e
08002132: 0542         tst       r5, r0
08002134: 08bf         it        eq
08002136: 70bd         popeq     {r4, r5, r6, pc}
08002138: 84f818c0     strb.w    ip, [r4, #0x18]
0800213c: 70bd         pop       {r4, r5, r6, pc}
0800213e: 2076         strb      r0, [r4, #0x18]
08002140: 70bd         pop       {r4, r5, r6, pc}
08002142: 30ea0503     bics.w    r3, r0, r5
08002146: d2d1         bne       #0x80020ee
08002148: 35ea0000     bics.w    r0, r5, r0
0800214c: 08bf         it        eq
0800214e: 70bd         popeq     {r4, r5, r6, pc}
08002150: 607e         ldrb      r0, [r4, #0x19]
08002152: 401c         adds      r0, r0, #1
08002154: 6076         strb      r0, [r4, #0x19]
08002156: 2176         strb      r1, [r4, #0x18]
08002158: 70bd         pop       {r4, r5, r6, pc}
0800215a: 0020         movs      r0, #0
0800215c: fef714b9     b.w       #0x8000388
08002160: 1249         ldr       r1, [pc, #0x48]
08002162: 1348         ldr       r0, [pc, #0x4c]
08002164: 10b4         push      {r4}
08002166: 00f11802     add.w     r2, r0, #0x18
0800216a: c1e90102     strd      r0, r2, [r1, #4]
0800216e: 0320         movs      r0, #3
08002170: 0873         strb      r0, [r1, #0xc]
08002172: 0820         movs      r0, #8
08002174: 4873         strb      r0, [r1, #0xd]
08002176: 0420         movs      r0, #4
08002178: 0023         movs      r3, #0
0800217a: 8873         strb      r0, [r1, #0xe]
0800217c: cb73         strb      r3, [r1, #0xf]
0800217e: 0b74         strb      r3, [r1, #0x10]
08002180: 1a46         mov       r2, r3
08002182: 01eb4200     add.w     r0, r1, r2, lsl #1
08002186: 01ebc20c     add.w     ip, r1, r2, lsl #3
0800218a: 4382         strh      r3, [r0, #0x12]
0800218c: 0020         movs      r0, #0
0800218e: 0ceb4004     add.w     r4, ip, r0, lsl #1
08002192: 401c         adds      r0, r0, #1
08002194: a4f85230     strh.w    r3, [r4, #0x52]
08002198: 0428         cmp       r0, #4
0800219a: f8d3         blo       #0x800218e
0800219c: 8818         adds      r0, r1, r2
0800219e: 521c         adds      r2, r2, #1
080021a0: 80f85231     strb.w    r3, [r0, #0x152]
080021a4: 202a         cmp       r2, #0x20
080021a6: ecd3         blo       #0x8002182
080021a8: 10bc         pop       {r4}
080021aa: 7047         bx        lr
080021ac: a000         lsls      r0, r4, #2
080021ae: 0020         movs      r0, #0
080021b0: c437         adds      r7, #0xc4
080021b2: 0008         lsrs      r0, r0, #0x20
080021b4: 2de9f041     push.w    {r4, r5, r6, r7, r8, lr}
080021b8: 3648         ldr       r0, [pc, #0xd8]
080021ba: 3749         ldr       r1, [pc, #0xdc]
080021bc: 0024         movs      r4, #0
080021be: c0e90014     strd      r1, r4, [r0]
080021c2: 0472         strb      r4, [r0, #8]
080021c4: 0846         mov       r0, r1
080021c6: 8988         ldrh      r1, [r1, #4]
080021c8: 0068         ldr       r0, [r0]
080021ca: 89b2         uxth      r1, r1
080021cc: fef74efb     bl        #0x800086c
080021d0: 324b         ldr       r3, [pc, #0xc8]
080021d2: 3049         ldr       r1, [pc, #0xc0]
080021d4: a3f12802     sub.w     r2, r3, #0x28
080021d8: 01f10c00     add.w     r0, r1, #0xc
080021dc: 01f0bef9     bl        #0x800355c
080021e0: 2e4b         ldr       r3, [pc, #0xb8]
080021e2: 2c49         ldr       r1, [pc, #0xb0]
080021e4: a3f12002     sub.w     r2, r3, #0x20
080021e8: 01f13000     add.w     r0, r1, #0x30
080021ec: 01f0b6f9     bl        #0x800355c
080021f0: 2a4b         ldr       r3, [pc, #0xa8]
080021f2: 2849         ldr       r1, [pc, #0xa0]
080021f4: a3f11802     sub.w     r2, r3, #0x18
080021f8: 01f15400     add.w     r0, r1, #0x54
080021fc: 01f0aef9     bl        #0x800355c
08002200: 2748         ldr       r0, [pc, #0x9c]
08002202: 2849         ldr       r1, [pc, #0xa0]
08002204: 284b         ldr       r3, [pc, #0xa0]
08002206: c0e90031     strd      r3, r1, [r0]
0800220a: 0125         movs      r5, #1
0800220c: 0572         strb      r5, [r0, #8]
0800220e: 4472         strb      r4, [r0, #9]
08002210: c460         str       r4, [r0, #0xc]
08002212: a0f1780c     sub.w     ip, r0, #0x78
08002216: 0461         str       r4, [r0, #0x10]
08002218: dcf80410     ldr.w     r1, [ip, #4]
0800221c: 0027         movs      r7, #0
0800221e: 0029         cmp       r1, #0
08002220: 2ed0         beq       #0x8002280
08002222: ca68         ldr       r2, [r1, #0xc]
08002224: c0e90321     strd      r2, r1, [r0, #0xc]
08002228: c860         str       r0, [r1, #0xc]
0800222a: 1061         str       r0, [r2, #0x10]
0800222c: 1f4e         ldr       r6, [pc, #0x7c]
0800222e: 4761         str       r7, [r0, #0x14]
08002230: 0660         str       r6, [r0]
08002232: 0476         strb      r4, [r0, #0x18]
08002234: 4476         strb      r4, [r0, #0x19]
08002236: 0021         movs      r1, #0
08002238: 4ff6ff72     movw      r2, #0xffff
0800223c: 00eb4107     add.w     r7, r0, r1, lsl #1
08002240: 491c         adds      r1, r1, #1
08002242: 7a83         strh      r2, [r7, #0x1a]
08002244: fad0         beq       #0x800223c
08002246: 1a48         ldr       r0, [pc, #0x68]
08002248: 1a49         ldr       r1, [pc, #0x68]
0800224a: 0027         movs      r7, #0
0800224c: c0e90031     strd      r3, r1, [r0]
08002250: 0572         strb      r5, [r0, #8]
08002252: 4472         strb      r4, [r0, #9]
08002254: c460         str       r4, [r0, #0xc]
08002256: 0461         str       r4, [r0, #0x10]
08002258: dcf80410     ldr.w     r1, [ip, #4]
0800225c: a9b1         cbz       r1, #0x800228a
0800225e: cb68         ldr       r3, [r1, #0xc]
08002260: c0e90331     strd      r3, r1, [r0, #0xc]
08002264: c860         str       r0, [r1, #0xc]
08002266: 1861         str       r0, [r3, #0x10]
08002268: 4761         str       r7, [r0, #0x14]
0800226a: 0660         str       r6, [r0]
0800226c: 0476         strb      r4, [r0, #0x18]
0800226e: 4476         strb      r4, [r0, #0x19]
08002270: 0021         movs      r1, #0
08002272: 00eb4103     add.w     r3, r0, r1, lsl #1
08002276: 491c         adds      r1, r1, #1
08002278: 5a83         strh      r2, [r3, #0x1a]
0800227a: fad0         beq       #0x8002272
0800227c: bde8f081     pop.w     {r4, r5, r6, r7, r8, pc}
08002280: c060         str       r0, [r0, #0xc]
08002282: 0061         str       r0, [r0, #0x10]
08002284: ccf80400     str.w     r0, [ip, #4]
08002288: d0e7         b         #0x800222c
0800228a: c060         str       r0, [r0, #0xc]
0800228c: 0061         str       r0, [r0, #0x10]
0800228e: ccf80400     str.w     r0, [ip, #4]
08002292: e9e7         b         #0x8002268
08002294: 1402         lsls      r4, r2, #8
08002296: 0020         movs      r0, #0
08002298: fc37         adds      r7, #0xfc
0800229a: 0008         lsrs      r0, r0, #0x20
0800229c: 2c38         subs      r0, #0x2c
0800229e: 0008         lsrs      r0, r0, #0x20
080022a0: 8c02         lsls      r4, r1, #0xa
080022a2: 0020         movs      r0, #0
080022a4: 1c38         subs      r0, #0x1c
080022a6: 0008         lsrs      r0, r0, #0x20
080022a8: e83e         subs      r6, #0xe8
080022aa: 0008         lsrs      r0, r0, #0x20
080022ac: 043f         subs      r7, #4
080022ae: 0008         lsrs      r0, r0, #0x20
080022b0: a802         lsls      r0, r5, #0xa
080022b2: 0020         movs      r0, #0
080022b4: 2438         subs      r0, #0x24
080022b6: 0008         lsrs      r0, r0, #0x20
080022b8: 70b5         push      {r4, r5, r6, lr}
080022ba: 1e4c         ldr       r4, [pc, #0x78]
080022bc: 1e48         ldr       r0, [pc, #0x78]
080022be: 82b0         sub       sp, #8
080022c0: 0022         movs      r2, #0
080022c2: 00f12001     add.w     r1, r0, #0x20
080022c6: 2271         strb      r2, [r4, #4]
080022c8: c4e90201     strd      r0, r1, [r4, #8]
080022cc: 0426         movs      r6, #4
080022ce: 2674         strb      r6, [r4, #0x10]
080022d0: 6674         strb      r6, [r4, #0x11]
080022d2: a274         strb      r2, [r4, #0x12]
080022d4: 1046         mov       r0, r2
080022d6: 0121         movs      r1, #1
080022d8: 2218         adds      r2, r4, r0
080022da: d174         strb      r1, [r2, #0x13]
080022dc: 04eb8002     add.w     r2, r4, r0, lsl #2
080022e0: 401c         adds      r0, r0, #1
080022e2: 5162         str       r1, [r2, #0x24]
080022e4: 1028         cmp       r0, #0x10
080022e6: f7d3         blo       #0x80022d8
080022e8: 207c         ldrb      r0, [r4, #0x10]
080022ea: 0025         movs      r5, #0
080022ec: 0028         cmp       r0, #0
080022ee: 0cd9         bls       #0x800230a
080022f0: a068         ldr       r0, [r4, #8]
080022f2: 06ebc501     add.w     r1, r6, r5, lsl #3
080022f6: 415a         ldrh      r1, [r0, r1]
080022f8: 50f83500     ldr.w     r0, [r0, r5, lsl #3]
080022fc: 89b2         uxth      r1, r1
080022fe: fef7b7fa     bl        #0x8000870
08002302: 207c         ldrb      r0, [r4, #0x10]
08002304: 6d1c         adds      r5, r5, #1
08002306: a842         cmp       r0, r5
08002308: f2d8         bhi       #0x80022f0
0800230a: 0624         movs      r4, #6
0800230c: 0b4b         ldr       r3, [pc, #0x2c]
0800230e: 0094         str       r4, [sp]
08002310: a3f13002     sub.w     r2, r3, #0x30
08002314: 1021         movs      r1, #0x10
08002316: 0a48         ldr       r0, [pc, #0x28]
08002318: 0194         str       r4, [sp, #4]
0800231a: 01f0adf9     bl        #0x8003678
0800231e: 094b         ldr       r3, [pc, #0x24]
08002320: 0094         str       r4, [sp]
08002322: a3f13002     sub.w     r2, r3, #0x30
08002326: 3421         movs      r1, #0x34
08002328: 0748         ldr       r0, [pc, #0x1c]
0800232a: 0194         str       r4, [sp, #4]
0800232c: 01f0a4f9     bl        #0x8003678
08002330: 02b0         add       sp, #8
08002332: 70bd         pop       {r4, r5, r6, pc}
08002334: fc02         lsls      r4, r7, #0xb
08002336: 0020         movs      r0, #0
08002338: 6c38         subs      r0, #0x6c
0800233a: 0008         lsrs      r0, r0, #0x20
0800233c: dc38         subs      r0, #0xdc
0800233e: 0008         lsrs      r0, r0, #0x20
08002340: 6003         lsls      r0, r4, #0xd
08002342: 0020         movs      r0, #0
08002344: 3c39         subs      r1, #0x3c
08002346: 0008         lsrs      r0, r0, #0x20
08002348: 2804         lsls      r0, r5, #0x10
0800234a: 0020         movs      r0, #0
0800234c: 0348         ldr       r0, [pc, #0xc]
0800234e: 4168         ldr       r1, [r0, #4]
08002350: 40f8881b     str       r1, [r0], #0x88
08002354: 0021         movs      r1, #0
08002356: 0160         str       r1, [r0]
08002358: 8180         strh      r1, [r0, #4]
0800235a: 7047         bx        lr
0800235c: d405         lsls      r4, r2, #0x17
0800235e: 0020         movs      r0, #0
08002360: 0f49         ldr       r1, [pc, #0x3c]
08002362: 30b4         push      {r4, r5}
08002364: 91e83810     ldm.w     r1, {r3, r4, r5, ip}
08002368: 0c48         ldr       r0, [pc, #0x30]
0800236a: 0022         movs      r2, #0
0800236c: 0270         strb      r2, [r0]
0800236e: c0e90234     strd      r3, r4, [r0, #8]
08002372: c0e9045c     strd      r5, ip, [r0, #0x10]
08002376: 0276         strb      r2, [r0, #0x18]
08002378: 4276         strb      r2, [r0, #0x19]
0800237a: d1e90534     ldrd      r3, r4, [r1, #0x14]
0800237e: 1c30         adds      r0, #0x1c
08002380: d1f810c0     ldr.w     ip, [r1, #0x10]
08002384: c969         ldr       r1, [r1, #0x1c]
08002386: 0125         movs      r5, #1
08002388: 0570         strb      r5, [r0]
0800238a: c0e90441     strd      r4, r1, [r0, #0x10]
0800238e: c0e902c3     strd      ip, r3, [r0, #8]
08002392: 0276         strb      r2, [r0, #0x18]
08002394: 4276         strb      r2, [r0, #0x19]
08002396: 30bc         pop       {r4, r5}
08002398: 7047         bx        lr
0800239a: 0000         movs      r0, r0
0800239c: c402         lsls      r4, r0, #0xb
0800239e: 0020         movs      r0, #0
080023a0: 4c38         subs      r0, #0x4c
080023a2: 0008         lsrs      r0, r0, #0x20
080023a4: 0348         ldr       r0, [pc, #0xc]
080023a6: 4168         ldr       r1, [r0, #4]
080023a8: 0160         str       r1, [r0]
080023aa: 0021         movs      r1, #0
080023ac: 8164         str       r1, [r0, #0x48]
080023ae: a0f84c10     strh.w    r1, [r0, #0x4c]
080023b2: 7047         bx        lr
080023b4: d406         lsls      r4, r2, #0x1b
080023b6: 0020         movs      r0, #0
080023b8: 0348         ldr       r0, [pc, #0xc]
080023ba: 4168         ldr       r1, [r0, #4]
080023bc: 0160         str       r1, [r0]
080023be: 0021         movs      r1, #0
080023c0: 8164         str       r1, [r0, #0x48]
080023c2: a0f84c10     strh.w    r1, [r0, #0x4c]
080023c6: 7047         bx        lr
080023c8: 8406         lsls      r4, r0, #0x1a
080023ca: 0020         movs      r0, #0
080023cc: 0948         ldr       r0, [pc, #0x24]
080023ce: 0a4a         ldr       r2, [pc, #0x28]
080023d0: 4168         ldr       r1, [r0, #4]
080023d2: 0160         str       r1, [r0]
080023d4: 0023         movs      r3, #0
080023d6: c0f88830     str.w     r3, [r0, #0x88]
080023da: a0f88c30     strh.w    r3, [r0, #0x8c]
080023de: c0f89020     str.w     r2, [r0, #0x90]
080023e2: 9430         adds      r0, #0x94
080023e4: 2521         movs      r1, #0x25
080023e6: 4368         ldr       r3, [r0, #4]
080023e8: 0360         str       r3, [r0]
080023ea: 8264         str       r2, [r0, #0x48]
080023ec: 80f84c10     strb.w    r1, [r0, #0x4c]
080023f0: 7047         bx        lr
080023f2: 0000         movs      r0, r0
080023f4: f004         lsls      r0, r6, #0x13
080023f6: 0020         movs      r0, #0
080023f8: 0038         subs      r0, #0
080023fa: 0140         ands      r1, r0
080023fc: 10b5         push      {r4, lr}
080023fe: 002a         cmp       r2, #0
08002400: 06da         bge       #0x8002410
08002402: 22f00042     bic       r2, r2, #0x80000000
08002406: d21d         adds      r2, r2, #7
08002408: 22f00703     bic       r3, r2, #7
0800240c: 1022         movs      r2, #0x10
0800240e: 03e0         b         #0x8002418
08002410: d21c         adds      r2, r2, #3
08002412: 22f00303     bic       r3, r2, #3
08002416: 0c22         movs      r2, #0xc
08002418: 13b1         cbz       r3, #0x8002420
0800241a: 9c18         adds      r4, r3, r2
0800241c: 8c42         cmp       r4, r1
0800241e: 01d9         bls       #0x8002424
08002420: 0120         movs      r0, #1
08002422: 10bd         pop       {r4, pc}
08002424: 0244         add       r2, r0
08002426: 0144         add       r1, r0
08002428: 8360         str       r3, [r0, #8]
0800242a: c0e90021     strd      r2, r1, [r0]
0800242e: c91a         subs      r1, r1, r3
08002430: d018         adds      r0, r2, r3
08002432: 8842         cmp       r0, r1
08002434: 02d8         bhi       #0x800243c
08002436: 1060         str       r0, [r2]
08002438: 0246         mov       r2, r0
0800243a: f9e7         b         #0x8002430
0800243c: 0020         movs      r0, #0
0800243e: 1060         str       r0, [r2]
08002440: 10bd         pop       {r4, pc}
08002442: 0000         movs      r0, r0
08002444: 10b5         push      {r4, lr}
08002446: 0446         mov       r4, r0
08002448: 01f010f8     bl        #0x800346c
0800244c: 0028         cmp       r0, #0
0800244e: 08bf         it        eq
08002450: 10bd         popeq     {r4, pc}
08002452: 4ff6ff71     movw      r1, #0xffff
08002456: dff808c0     ldr.w     ip, [pc, #8]
0800245a: 2068         ldr       r0, [r4]
0800245c: 00df         svc       #0
0800245e: 10bd         pop       {r4, pc}
08002460: 552e         cmp       r6, #0x55
08002462: 0008         lsrs      r0, r0, #0x20
08002464: 10b5         push      {r4, lr}
08002466: 0446         mov       r4, r0
08002468: 01f000f8     bl        #0x800346c
0800246c: 0028         cmp       r0, #0
0800246e: 08bf         it        eq
08002470: 10bd         popeq     {r4, pc}
08002472: dff808c0     ldr.w     ip, [pc, #8]
08002476: 2068         ldr       r0, [r4]
08002478: 00df         svc       #0
0800247a: 10bd         pop       {r4, pc}
0800247c: a92d         cmp       r5, #0xa9
0800247e: 0008         lsrs      r0, r0, #0x20
08002480: 0848         ldr       r0, [pc, #0x20]
08002482: 0068         ldr       r0, [r0]
08002484: c001         lsls      r0, r0, #7
08002486: 0bd5         bpl       #0x80024a0
08002488: 0748         ldr       r0, [pc, #0x1c]
0800248a: 0068         ldr       r0, [r0]
0800248c: c007         lsls      r0, r0, #0x1f
0800248e: 07d0         beq       #0x80024a0
08002490: 0548         ldr       r0, [pc, #0x14]
08002492: 8038         subs      r0, #0x80
08002494: 0068         ldr       r0, [r0]
08002496: 0028         cmp       r0, #0
08002498: 02da         bge       #0x80024a0
0800249a: 0449         ldr       r1, [pc, #0x10]
0800249c: 0120         movs      r0, #1
0800249e: 0870         strb      r0, [r1]
080024a0: 7047         bx        lr
080024a2: 0000         movs      r0, r0
080024a4: fced00e0     ldcl      p0, c14, [ip, #0]!
080024a8: 800e         lsrs      r0, r0, #0x1a
080024aa: 00e0         b         #0x80024ae
080024ac: 8c00         lsls      r4, r1, #2
080024ae: 0020         movs      r0, #0
080024b0: 4ff06042     mov.w     r2, #-0x20000000
080024b4: d36f         ldr       r3, [r2, #0x7c]
080024b6: 002b         cmp       r3, #0
080024b8: fcd0         beq       #0x80024b4
080024ba: c36a         ldr       r3, [r0, #0x2c]
080024bc: d367         str       r3, [r2, #0x7c]
080024be: d36f         ldr       r3, [r2, #0x7c]
080024c0: 002b         cmp       r3, #0
080024c2: fcd0         beq       #0x80024be
080024c4: c078         ldrb      r0, [r0, #3]
080024c6: 40ea0120     orr.w     r0, r0, r1, lsl #8
080024ca: a2f87c00     strh.w    r0, [r2, #0x7c]
080024ce: 7047         bx        lr
080024d0: 4ff06041     mov.w     r1, #-0x20000000
080024d4: ca6f         ldr       r2, [r1, #0x7c]
080024d6: 002a         cmp       r2, #0
080024d8: fcd0         beq       #0x80024d4
080024da: 81f87c00     strb.w    r0, [r1, #0x7c]
080024de: 7047         bx        lr
080024e0: 70b5         push      {r4, r5, r6, lr}
080024e2: 0446         mov       r4, r0
080024e4: 4173         strb      r1, [r0, #0xd]
080024e6: ff20         movs      r0, #0xff
080024e8: a073         strb      r0, [r4, #0xe]
080024ea: e073         strb      r0, [r4, #0xf]
080024ec: 2078         ldrb      r0, [r4]
080024ee: 0d46         mov       r5, r1
080024f0: 40f00500     orr       r0, r0, #5
080024f4: 2073         strb      r0, [r4, #0xc]
080024f6: a268         ldr       r2, [r4, #8]
080024f8: 12b1         cbz       r2, #0x8002500
080024fa: a169         ldr       r1, [r4, #0x18]
080024fc: e068         ldr       r0, [r4, #0xc]
080024fe: 9047         blx       r2
08002500: 0020         movs      r0, #0
08002502: 6060         str       r0, [r4, #4]
08002504: 2946         mov       r1, r5
08002506: 2046         mov       r0, r4
08002508: bde87040     pop.w     {r4, r5, r6, lr}
0800250c: fef700be     b.w       #0x8001110
08002510: 70b5         push      {r4, r5, r6, lr}
08002512: 0446         mov       r4, r0
08002514: 8173         strb      r1, [r0, #0xe]
08002516: ff20         movs      r0, #0xff
08002518: e073         strb      r0, [r4, #0xf]
0800251a: 2078         ldrb      r0, [r4]
0800251c: 0d46         mov       r5, r1
0800251e: 40f00600     orr       r0, r0, #6
08002522: 2073         strb      r0, [r4, #0xc]
08002524: a268         ldr       r2, [r4, #8]
08002526: 12b1         cbz       r2, #0x800252e
08002528: a169         ldr       r1, [r4, #0x18]
0800252a: e068         ldr       r0, [r4, #0xc]
0800252c: 9047         blx       r2
0800252e: 0020         movs      r0, #0
08002530: 6060         str       r0, [r4, #4]
08002532: 2946         mov       r1, r5
08002534: 2046         mov       r0, r4
08002536: bde87040     pop.w     {r4, r5, r6, lr}
0800253a: fef7e9bd     b.w       #0x8001110
0800253e: 4269         ldr       r2, [r0, #0x14]
08002540: 002a         cmp       r2, #0
08002542: 18bf         it        ne
08002544: 7047         bxne      lr
08002546: 4174         strb      r1, [r0, #0x11]
08002548: 8268         ldr       r2, [r0, #8]
0800254a: 002a         cmp       r2, #0
0800254c: 08bf         it        eq
0800254e: 7047         bxeq      lr
08002550: 8169         ldr       r1, [r0, #0x18]
08002552: 0069         ldr       r0, [r0, #0x10]
08002554: 1047         bx        r2
08002556: 4173         strb      r1, [r0, #0xd]
08002558: ff22         movs      r2, #0xff
0800255a: c273         strb      r2, [r0, #0xf]
0800255c: 0278         ldrb      r2, [r0]
0800255e: 42ea1111     orr.w     r1, r2, r1, lsr #4
08002562: 0173         strb      r1, [r0, #0xc]
08002564: 0321         movs      r1, #3
08002566: 4160         str       r1, [r0, #4]
08002568: 7047         bx        lr
0800256a: 4173         strb      r1, [r0, #0xd]
0800256c: 0278         ldrb      r2, [r0]
0800256e: 42ea1111     orr.w     r1, r2, r1, lsr #4
08002572: 0173         strb      r1, [r0, #0xc]
08002574: 0121         movs      r1, #1
08002576: 4160         str       r1, [r0, #4]
08002578: 7047         bx        lr
0800257a: 4173         strb      r1, [r0, #0xd]
0800257c: ff21         movs      r1, #0xff
0800257e: 8173         strb      r1, [r0, #0xe]
08002580: c173         strb      r1, [r0, #0xf]
08002582: 0178         ldrb      r1, [r0]
08002584: 41f00501     orr       r1, r1, #5
08002588: 0173         strb      r1, [r0, #0xc]
0800258a: 8268         ldr       r2, [r0, #8]
0800258c: 002a         cmp       r2, #0
0800258e: 08bf         it        eq
08002590: 7047         bxeq      lr
08002592: 8169         ldr       r1, [r0, #0x18]
08002594: c068         ldr       r0, [r0, #0xc]
08002596: 1047         bx        r2
08002598: 70b5         push      {r4, r5, r6, lr}
0800259a: 0446         mov       r4, r0
0800259c: f620         movs      r0, #0xf6
0800259e: 6073         strb      r0, [r4, #0xd]
080025a0: ff20         movs      r0, #0xff
080025a2: a073         strb      r0, [r4, #0xe]
080025a4: e073         strb      r0, [r4, #0xf]
080025a6: 2078         ldrb      r0, [r4]
080025a8: 0d46         mov       r5, r1
080025aa: 40f00500     orr       r0, r0, #5
080025ae: 2073         strb      r0, [r4, #0xc]
080025b0: a268         ldr       r2, [r4, #8]
080025b2: 12b1         cbz       r2, #0x80025ba
080025b4: a169         ldr       r1, [r4, #0x18]
080025b6: e068         ldr       r0, [r4, #0xc]
080025b8: 9047         blx       r2
080025ba: 0020         movs      r0, #0
080025bc: 6060         str       r0, [r4, #4]
080025be: 2946         mov       r1, r5
080025c0: 2046         mov       r0, r4
080025c2: bde87040     pop.w     {r4, r5, r6, lr}
080025c6: fef7a3bd     b.w       #0x8001110
080025ca: 70b5         push      {r4, r5, r6, lr}
080025cc: 0446         mov       r4, r0
080025ce: f620         movs      r0, #0xf6
080025d0: a073         strb      r0, [r4, #0xe]
080025d2: ff20         movs      r0, #0xff
080025d4: e073         strb      r0, [r4, #0xf]
080025d6: 2078         ldrb      r0, [r4]
080025d8: 0d46         mov       r5, r1
080025da: 40f00600     orr       r0, r0, #6
080025de: 2073         strb      r0, [r4, #0xc]
080025e0: a268         ldr       r2, [r4, #8]
080025e2: 12b1         cbz       r2, #0x80025ea
080025e4: a169         ldr       r1, [r4, #0x18]
080025e6: e068         ldr       r0, [r4, #0xc]
080025e8: 9047         blx       r2
080025ea: 0020         movs      r0, #0
080025ec: 6060         str       r0, [r4, #4]
080025ee: 2946         mov       r1, r5
080025f0: 2046         mov       r0, r4
080025f2: bde87040     pop.w     {r4, r5, r6, lr}
080025f6: fef78bbd     b.w       #0x8001110
080025fa: 70b5         push      {r4, r5, r6, lr}
080025fc: 0446         mov       r4, r0
080025fe: f620         movs      r0, #0xf6
08002600: e073         strb      r0, [r4, #0xf]
08002602: 2078         ldrb      r0, [r4]
08002604: 0d46         mov       r5, r1
08002606: 40f00700     orr       r0, r0, #7
0800260a: 2073         strb      r0, [r4, #0xc]
0800260c: a268         ldr       r2, [r4, #8]
0800260e: 12b1         cbz       r2, #0x8002616
08002610: a169         ldr       r1, [r4, #0x18]
08002612: e068         ldr       r0, [r4, #0xc]
08002614: 9047         blx       r2
08002616: 0020         movs      r0, #0
08002618: 6060         str       r0, [r4, #4]
0800261a: 2946         mov       r1, r5
0800261c: 2046         mov       r0, r4
0800261e: bde87040     pop.w     {r4, r5, r6, lr}
08002622: fef775bd     b.w       #0x8001110
08002626: 4173         strb      r1, [r0, #0xd]
08002628: ff21         movs      r1, #0xff
0800262a: c173         strb      r1, [r0, #0xf]
0800262c: 0178         ldrb      r1, [r0]
0800262e: 41f00201     orr       r1, r1, #2
08002632: 0173         strb      r1, [r0, #0xc]
08002634: 0921         movs      r1, #9
08002636: 4160         str       r1, [r0, #4]
08002638: 7047         bx        lr
0800263a: 4173         strb      r1, [r0, #0xd]
0800263c: 0178         ldrb      r1, [r0]
0800263e: 41f00301     orr       r1, r1, #3
08002642: 0173         strb      r1, [r0, #0xc]
08002644: 0721         movs      r1, #7
08002646: 4160         str       r1, [r0, #4]
08002648: 7047         bx        lr
0800264a: 4173         strb      r1, [r0, #0xd]
0800264c: 0a21         movs      r1, #0xa
0800264e: 4160         str       r1, [r0, #4]
08002650: 7047         bx        lr
08002652: 8173         strb      r1, [r0, #0xe]
08002654: 8268         ldr       r2, [r0, #8]
08002656: 002a         cmp       r2, #0
08002658: 08bf         it        eq
0800265a: 7047         bxeq      lr
0800265c: 8169         ldr       r1, [r0, #0x18]
0800265e: c068         ldr       r0, [r0, #0xc]
08002660: 1047         bx        r2
08002662: 8173         strb      r1, [r0, #0xe]
08002664: 0221         movs      r1, #2
08002666: 4160         str       r1, [r0, #4]
08002668: 7047         bx        lr
0800266a: 10b5         push      {r4, lr}
0800266c: c173         strb      r1, [r0, #0xf]
0800266e: 8268         ldr       r2, [r0, #8]
08002670: 0446         mov       r4, r0
08002672: 12b1         cbz       r2, #0x800267a
08002674: a169         ldr       r1, [r4, #0x18]
08002676: e068         ldr       r0, [r4, #0xc]
08002678: 9047         blx       r2
0800267a: 0120         movs      r0, #1
0800267c: 6060         str       r0, [r4, #4]
0800267e: 10bd         pop       {r4, pc}
08002680: 10b5         push      {r4, lr}
08002682: 8173         strb      r1, [r0, #0xe]
08002684: 8268         ldr       r2, [r0, #8]
08002686: 0446         mov       r4, r0
08002688: 12b1         cbz       r2, #0x8002690
0800268a: a169         ldr       r1, [r4, #0x18]
0800268c: e068         ldr       r0, [r4, #0xc]
0800268e: 9047         blx       r2
08002690: 0020         movs      r0, #0
08002692: 6060         str       r0, [r4, #4]
08002694: 10bd         pop       {r4, pc}
08002696: 8173         strb      r1, [r0, #0xe]
08002698: 0821         movs      r1, #8
0800269a: 4160         str       r1, [r0, #4]
0800269c: 7047         bx        lr
0800269e: 8173         strb      r1, [r0, #0xe]
080026a0: 0b21         movs      r1, #0xb
080026a2: 4160         str       r1, [r0, #4]
080026a4: 7047         bx        lr
080026a6: 10b5         push      {r4, lr}
080026a8: c173         strb      r1, [r0, #0xf]
080026aa: 8268         ldr       r2, [r0, #8]
080026ac: 0446         mov       r4, r0
080026ae: 12b1         cbz       r2, #0x80026b6
080026b0: a169         ldr       r1, [r4, #0x18]
080026b2: e068         ldr       r0, [r4, #0xc]
080026b4: 9047         blx       r2
080026b6: 0020         movs      r0, #0
080026b8: 6060         str       r0, [r4, #4]
080026ba: 10bd         pop       {r4, pc}
080026bc: 10b5         push      {r4, lr}
080026be: 0446         mov       r4, r0
080026c0: c173         strb      r1, [r0, #0xf]
080026c2: 0078         ldrb      r0, [r0]
080026c4: 40f00300     orr       r0, r0, #3
080026c8: 2073         strb      r0, [r4, #0xc]
080026ca: a268         ldr       r2, [r4, #8]
080026cc: 12b1         cbz       r2, #0x80026d4
080026ce: a169         ldr       r1, [r4, #0x18]
080026d0: e068         ldr       r0, [r4, #0xc]
080026d2: 9047         blx       r2
080026d4: 0020         movs      r0, #0
080026d6: 6060         str       r0, [r4, #4]
080026d8: 10bd         pop       {r4, pc}
080026da: 7047         bx        lr
080026dc: 4173         strb      r1, [r0, #0xd]
080026de: 0521         movs      r1, #5
080026e0: 4160         str       r1, [r0, #4]
080026e2: 7047         bx        lr
080026e4: 8173         strb      r1, [r0, #0xe]
080026e6: 0621         movs      r1, #6
080026e8: 4160         str       r1, [r0, #4]
080026ea: 7047         bx        lr
080026ec: 10b5         push      {r4, lr}
080026ee: c173         strb      r1, [r0, #0xf]
080026f0: 8268         ldr       r2, [r0, #8]
080026f2: 0446         mov       r4, r0
080026f4: 12b1         cbz       r2, #0x80026fc
080026f6: a169         ldr       r1, [r4, #0x18]
080026f8: e068         ldr       r0, [r4, #0xc]
080026fa: 9047         blx       r2
080026fc: 0420         movs      r0, #4
080026fe: 6060         str       r0, [r4, #4]
08002700: 10bd         pop       {r4, pc}
08002702: 4173         strb      r1, [r0, #0xd]
08002704: 0178         ldrb      r1, [r0]
08002706: 41f00401     orr       r1, r1, #4
0800270a: 0173         strb      r1, [r0, #0xc]
0800270c: 0521         movs      r1, #5
0800270e: 4160         str       r1, [r0, #4]
08002710: 7047         bx        lr
08002712: 7047         bx        lr
08002714: 10b5         push      {r4, lr}
08002716: 0446         mov       r4, r0
08002718: f720         movs      r0, #0xf7
0800271a: 6073         strb      r0, [r4, #0xd]
0800271c: 2078         ldrb      r0, [r4]
0800271e: 40f00500     orr       r0, r0, #5
08002722: 2073         strb      r0, [r4, #0xc]
08002724: a268         ldr       r2, [r4, #8]
08002726: 12b1         cbz       r2, #0x800272e
08002728: a169         ldr       r1, [r4, #0x18]
0800272a: e068         ldr       r0, [r4, #0xc]
0800272c: 9047         blx       r2
0800272e: 0020         movs      r0, #0
08002730: 6060         str       r0, [r4, #4]
08002732: 10bd         pop       {r4, pc}
08002734: 10b5         push      {r4, lr}
08002736: 0446         mov       r4, r0
08002738: f720         movs      r0, #0xf7
0800273a: a073         strb      r0, [r4, #0xe]
0800273c: ff20         movs      r0, #0xff
0800273e: e073         strb      r0, [r4, #0xf]
08002740: 2078         ldrb      r0, [r4]
08002742: 40f00600     orr       r0, r0, #6
08002746: 2073         strb      r0, [r4, #0xc]
08002748: a268         ldr       r2, [r4, #8]
0800274a: 12b1         cbz       r2, #0x8002752
0800274c: a169         ldr       r1, [r4, #0x18]
0800274e: e068         ldr       r0, [r4, #0xc]
08002750: 9047         blx       r2
08002752: 0020         movs      r0, #0
08002754: 6060         str       r0, [r4, #4]
08002756: 10bd         pop       {r4, pc}
08002758: 10b5         push      {r4, lr}
0800275a: 0446         mov       r4, r0
0800275c: f720         movs      r0, #0xf7
0800275e: e073         strb      r0, [r4, #0xf]
08002760: 2078         ldrb      r0, [r4]
08002762: 40f00700     orr       r0, r0, #7
08002766: 2073         strb      r0, [r4, #0xc]
08002768: a268         ldr       r2, [r4, #8]
0800276a: 12b1         cbz       r2, #0x8002772
0800276c: a169         ldr       r1, [r4, #0x18]
0800276e: e068         ldr       r0, [r4, #0xc]
08002770: 9047         blx       r2
08002772: 0020         movs      r0, #0
08002774: 6060         str       r0, [r4, #4]
08002776: 10bd         pop       {r4, pc}
08002778: 4174         strb      r1, [r0, #0x11]
0800277a: 0178         ldrb      r1, [r0]
0800277c: 41f00f01     orr       r1, r1, #0xf
08002780: 0174         strb      r1, [r0, #0x10]
08002782: 8268         ldr       r2, [r0, #8]
08002784: 002a         cmp       r2, #0
08002786: 08bf         it        eq
08002788: 7047         bxeq      lr
0800278a: 8169         ldr       r1, [r0, #0x18]
0800278c: 0069         ldr       r0, [r0, #0x10]
0800278e: 1047         bx        r2
08002790: 70b5         push      {r4, r5, r6, lr}
08002792: 0446         mov       r4, r0
08002794: 8173         strb      r1, [r0, #0xe]
08002796: ff20         movs      r0, #0xff
08002798: e073         strb      r0, [r4, #0xf]
0800279a: 2078         ldrb      r0, [r4]
0800279c: 0d46         mov       r5, r1
0800279e: 40f00500     orr       r0, r0, #5
080027a2: 2073         strb      r0, [r4, #0xc]
080027a4: a268         ldr       r2, [r4, #8]
080027a6: 12b1         cbz       r2, #0x80027ae
080027a8: a169         ldr       r1, [r4, #0x18]
080027aa: e068         ldr       r0, [r4, #0xc]
080027ac: 9047         blx       r2
080027ae: 0020         movs      r0, #0
080027b0: 6060         str       r0, [r4, #4]
080027b2: 2946         mov       r1, r5
080027b4: 2046         mov       r0, r4
080027b6: bde87040     pop.w     {r4, r5, r6, lr}
080027ba: fef7a9bc     b.w       #0x8001110
080027be: 70b5         push      {r4, r5, r6, lr}
080027c0: 0446         mov       r4, r0
080027c2: 8173         strb      r1, [r0, #0xe]
080027c4: ff20         movs      r0, #0xff
080027c6: e073         strb      r0, [r4, #0xf]
080027c8: 2078         ldrb      r0, [r4]
080027ca: 0d46         mov       r5, r1
080027cc: 40f00500     orr       r0, r0, #5
080027d0: 2073         strb      r0, [r4, #0xc]
080027d2: a268         ldr       r2, [r4, #8]
080027d4: 12b1         cbz       r2, #0x80027dc
080027d6: a169         ldr       r1, [r4, #0x18]
080027d8: e068         ldr       r0, [r4, #0xc]
080027da: 9047         blx       r2
080027dc: 0020         movs      r0, #0
080027de: 6060         str       r0, [r4, #4]
080027e0: 2946         mov       r1, r5
080027e2: 2046         mov       r0, r4
080027e4: bde87040     pop.w     {r4, r5, r6, lr}
080027e8: fef792bc     b.w       #0x8001110
080027ec: 10b5         push      {r4, lr}
080027ee: 0446         mov       r4, r0
080027f0: 8173         strb      r1, [r0, #0xe]
080027f2: ff20         movs      r0, #0xff
080027f4: e073         strb      r0, [r4, #0xf]
080027f6: 2078         ldrb      r0, [r4]
080027f8: 40f00500     orr       r0, r0, #5
080027fc: 2073         strb      r0, [r4, #0xc]
080027fe: a268         ldr       r2, [r4, #8]
08002800: 12b1         cbz       r2, #0x8002808
08002802: a169         ldr       r1, [r4, #0x18]
08002804: e068         ldr       r0, [r4, #0xc]
08002806: 9047         blx       r2
08002808: 0020         movs      r0, #0
0800280a: 6060         str       r0, [r4, #4]
0800280c: 10bd         pop       {r4, pc}
0800280e: 70b5         push      {r4, r5, r6, lr}
08002810: 0446         mov       r4, r0
08002812: c173         strb      r1, [r0, #0xf]
08002814: 0078         ldrb      r0, [r0]
08002816: 0d46         mov       r5, r1
08002818: 40f00200     orr       r0, r0, #2
0800281c: 2073         strb      r0, [r4, #0xc]
0800281e: a268         ldr       r2, [r4, #8]
08002820: 12b1         cbz       r2, #0x8002828
08002822: a169         ldr       r1, [r4, #0x18]
08002824: e068         ldr       r0, [r4, #0xc]
08002826: 9047         blx       r2
08002828: 0020         movs      r0, #0
0800282a: 6060         str       r0, [r4, #4]
0800282c: 2946         mov       r1, r5
0800282e: 2046         mov       r0, r4
08002830: bde87040     pop.w     {r4, r5, r6, lr}
08002834: fef76cbc     b.w       #0x8001110
08002838: 70b5         push      {r4, r5, r6, lr}
0800283a: 0446         mov       r4, r0
0800283c: c173         strb      r1, [r0, #0xf]
0800283e: 0078         ldrb      r0, [r0]
08002840: 0d46         mov       r5, r1
08002842: 40f00200     orr       r0, r0, #2
08002846: 2073         strb      r0, [r4, #0xc]
08002848: a268         ldr       r2, [r4, #8]
0800284a: 12b1         cbz       r2, #0x8002852
0800284c: a169         ldr       r1, [r4, #0x18]
0800284e: e068         ldr       r0, [r4, #0xc]
08002850: 9047         blx       r2
08002852: 0020         movs      r0, #0
08002854: 6060         str       r0, [r4, #4]
08002856: 2946         mov       r1, r5
08002858: 2046         mov       r0, r4
0800285a: bde87040     pop.w     {r4, r5, r6, lr}
0800285e: fef757bc     b.w       #0x8001110
08002862: 10b5         push      {r4, lr}
08002864: 0446         mov       r4, r0
08002866: c173         strb      r1, [r0, #0xf]
08002868: 0078         ldrb      r0, [r0]
0800286a: 40f00200     orr       r0, r0, #2
0800286e: 2073         strb      r0, [r4, #0xc]
08002870: a268         ldr       r2, [r4, #8]
08002872: 12b1         cbz       r2, #0x800287a
08002874: a169         ldr       r1, [r4, #0x18]
08002876: e068         ldr       r0, [r4, #0xc]
08002878: 9047         blx       r2
0800287a: 0020         movs      r0, #0
0800287c: 6060         str       r0, [r4, #4]
0800287e: 10bd         pop       {r4, pc}
08002880: 4173         strb      r1, [r0, #0xd]
08002882: ff22         movs      r2, #0xff
08002884: c273         strb      r2, [r0, #0xf]
08002886: 0278         ldrb      r2, [r0]
08002888: 42ea1111     orr.w     r1, r2, r1, lsr #4
0800288c: 0173         strb      r1, [r0, #0xc]
0800288e: 0321         movs      r1, #3
08002890: 4160         str       r1, [r0, #4]
08002892: 7047         bx        lr
08002894: 4173         strb      r1, [r0, #0xd]
08002896: 0278         ldrb      r2, [r0]
08002898: 42ea1111     orr.w     r1, r2, r1, lsr #4
0800289c: 0173         strb      r1, [r0, #0xc]
0800289e: 0121         movs      r1, #1
080028a0: 4160         str       r1, [r0, #4]
080028a2: 7047         bx        lr
080028a4: 10b5         push      {r4, lr}
080028a6: 0446         mov       r4, r0
080028a8: f620         movs      r0, #0xf6
080028aa: 6073         strb      r0, [r4, #0xd]
080028ac: ff20         movs      r0, #0xff
080028ae: a073         strb      r0, [r4, #0xe]
080028b0: e073         strb      r0, [r4, #0xf]
080028b2: 2078         ldrb      r0, [r4]
080028b4: 40f00500     orr       r0, r0, #5
080028b8: 2073         strb      r0, [r4, #0xc]
080028ba: a268         ldr       r2, [r4, #8]
080028bc: 12b1         cbz       r2, #0x80028c4
080028be: a169         ldr       r1, [r4, #0x18]
080028c0: e068         ldr       r0, [r4, #0xc]
080028c2: 9047         blx       r2
080028c4: 0020         movs      r0, #0
080028c6: 6060         str       r0, [r4, #4]
080028c8: 10bd         pop       {r4, pc}
080028ca: 4173         strb      r1, [r0, #0xd]
080028cc: ff21         movs      r1, #0xff
080028ce: c173         strb      r1, [r0, #0xf]
080028d0: 0178         ldrb      r1, [r0]
080028d2: 41f00201     orr       r1, r1, #2
080028d6: 0173         strb      r1, [r0, #0xc]
080028d8: 0921         movs      r1, #9
080028da: 4160         str       r1, [r0, #4]
080028dc: 7047         bx        lr
080028de: 4173         strb      r1, [r0, #0xd]
080028e0: 0178         ldrb      r1, [r0]
080028e2: 41f00301     orr       r1, r1, #3
080028e6: 0173         strb      r1, [r0, #0xc]
080028e8: 0721         movs      r1, #7
080028ea: 4160         str       r1, [r0, #4]
080028ec: 7047         bx        lr
080028ee: 4173         strb      r1, [r0, #0xd]
080028f0: 0a21         movs      r1, #0xa
080028f2: 4160         str       r1, [r0, #4]
080028f4: 7047         bx        lr
080028f6: 4173         strb      r1, [r0, #0xd]
080028f8: 0178         ldrb      r1, [r0]
080028fa: 41f00401     orr       r1, r1, #4
080028fe: 0173         strb      r1, [r0, #0xc]
08002900: 0521         movs      r1, #5
08002902: 4160         str       r1, [r0, #4]
08002904: 7047         bx        lr
08002906: 0021         movs      r1, #0
08002908: 4160         str       r1, [r0, #4]
0800290a: 7047         bx        lr
0800290c: 0a46         mov       r2, r1
0800290e: 0146         mov       r1, r0
08002910: 0748         ldr       r0, [pc, #0x1c]
08002912: 10b5         push      {r4, lr}
08002914: 00eb8200     add.w     r0, r0, r2, lsl #2
08002918: 50f8040c     ldr       r0, [r0, #-0x4]
0800291c: 0028         cmp       r0, #0
0800291e: 05d0         beq       #0x800292c
08002920: 00f016fb     bl        #0x8002f50
08002924: bde81040     pop.w     {r4, lr}
08002928: 00f002bb     b.w       #0x8002f30
0800292c: 10bd         pop       {r4, pc}
0800292e: 0000         movs      r0, r0
08002930: dc0e         lsrs      r4, r3, #0x1b
08002932: 0020         movs      r0, #0
08002934: fef770f9     bl        #0x8000c18
08002938: fef77df8     bl        #0x8000a36
0800293c: fdf7a2ff     bl        #0x8000884
08002940: fdf77afe     bl        #0x8000638
08002944: fef706fd     bl        #0x8001354
08002948: fef7a4fb     bl        #0x8001094
0800294c: 0a4a         ldr       r2, [pc, #0x28]
0800294e: 2021         movs      r1, #0x20
08002950: 1160         str       r1, [r2]
08002952: 4903         lsls      r1, r1, #0xd
08002954: 101f         subs      r0, r2, #4
08002956: 0160         str       r1, [r0]
08002958: c901         lsls      r1, r1, #7
0800295a: 0160         str       r1, [r0]
0800295c: 8912         asrs      r1, r1, #0xa
0800295e: 0748         ldr       r0, [pc, #0x1c]
08002960: fdf786ff     bl        #0x8000870
08002964: fdf732fc     bl        #0x80001cc
08002968: 0022         movs      r2, #0
0800296a: 0921         movs      r1, #9
0800296c: 0448         ldr       r0, [pc, #0x10]
0800296e: dff814c0     ldr.w     ip, [pc, #0x14]
08002972: 00df         svc       #0
08002974: fee7         b         #0x8002974
08002976: 0000         movs      r0, r0
08002978: 04e1         b         #0x8002b84
0800297a: 00e0         b         #0x800297e
0800297c: 0018         adds      r0, r0, r0
0800297e: 0140         ands      r1, r0
08002980: 711f         subs      r1, r6, #5
08002982: 0008         lsrs      r0, r0, #0x20
08002984: 4931         adds      r1, #0x49
08002986: 0008         lsrs      r0, r0, #0x20
08002988: fee7         b         #0x8002988
0800298a: fee7         b         #0x800298a
0800298c: 0748         ldr       r0, [pc, #0x1c]
0800298e: 0168         ldr       r1, [r0]
08002990: 4ff0e020     mov.w     r0, #-0x1fff2000
08002994: 4161         str       r1, [r0, #0x14]
08002996: 0021         movs      r1, #0
08002998: 8161         str       r1, [r0, #0x18]
0800299a: 0721         movs      r1, #7
0800299c: 0161         str       r1, [r0, #0x10]
0800299e: 0448         ldr       r0, [pc, #0x10]
080029a0: 0168         ldr       r1, [r0]
080029a2: 41f07f41     orr       r1, r1, #0xff000000
080029a6: 0160         str       r1, [r0]
080029a8: 4017         asrs      r0, r0, #0x1d
080029aa: 7047         bx        lr
080029ac: c43e         subs      r6, #0xc4
080029ae: 0008         lsrs      r0, r0, #0x20
080029b0: 20ed00e0     stc       p0, c14, [r0, #-0]!
080029b4: 7047         bx        lr
080029b6: 7047         bx        lr
080029b8: 50e8001f     ldrex     r1, [r0]
080029bc: 31b1         cbz       r1, #0x80029cc
080029be: 0b68         ldr       r3, [r1]
080029c0: 40e80032     strex     r2, r3, [r0]
080029c4: 002a         cmp       r2, #0
080029c6: f7d1         bne       #0x80029b8
080029c8: 0846         mov       r0, r1
080029ca: 7047         bx        lr
080029cc: bff32f8f     clrex     
080029d0: fae7         b         #0x80029c8
080029d2: 0000         movs      r0, r0
080029d4: 70b5         push      {r4, r5, r6, lr}
080029d6: 0d46         mov       r5, r1
080029d8: 0028         cmp       r0, #0
080029da: 12d0         beq       #0x8002a02
080029dc: 4ff6ff71     movw      r1, #0xffff
080029e0: 084c         ldr       r4, [pc, #0x20]
080029e2: 8842         cmp       r0, r1
080029e4: 04d2         bhs       #0x80029f0
080029e6: 2268         ldr       r2, [r4]
080029e8: 0146         mov       r1, r0
080029ea: 1046         mov       r0, r2
080029ec: 00f0dcfa     bl        #0x8002fa8
080029f0: 2068         ldr       r0, [r4]
080029f2: 4570         strb      r5, [r0, #1]
080029f4: 0448         ldr       r0, [pc, #0x10]
080029f6: 00f0f5f8     bl        #0x8002be4
080029fa: bde87040     pop.w     {r4, r5, r6, lr}
080029fe: 00f08fbb     b.w       #0x8003120
08002a02: 70bd         pop       {r4, r5, r6, pc}
08002a04: 8000         lsls      r0, r0, #2
08002a06: 0020         movs      r0, #0
08002a08: 1c0f         lsrs      r4, r3, #0x1c
08002a0a: 0020         movs      r0, #0
08002a0c: 7047         bx        lr
08002a0e: 0000         movs      r0, r0
08002a10: 70b5         push      {r4, r5, r6, lr}
08002a12: 1a4d         ldr       r5, [pc, #0x68]
08002a14: e868         ldr       r0, [r5, #0xc]
08002a16: 0028         cmp       r0, #0
08002a18: 2ed0         beq       #0x8002a78
08002a1a: a88a         ldrh      r0, [r5, #0x14]
08002a1c: 401e         subs      r0, r0, #1
08002a1e: a882         strh      r0, [r5, #0x14]
08002a20: 0026         movs      r6, #0
08002a22: 23e0         b         #0x8002a6c
08002a24: a068         ldr       r0, [r4, #8]
08002a26: 38b1         cbz       r0, #0x8002a38
08002a28: 6168         ldr       r1, [r4, #4]
08002a2a: 4160         str       r1, [r0, #4]
08002a2c: 6068         ldr       r0, [r4, #4]
08002a2e: 10b1         cbz       r0, #0x8002a36
08002a30: a168         ldr       r1, [r4, #8]
08002a32: 8160         str       r1, [r0, #8]
08002a34: 6660         str       r6, [r4, #4]
08002a36: a660         str       r6, [r4, #8]
08002a38: 1048         ldr       r0, [pc, #0x40]
08002a3a: 2146         mov       r1, r4
08002a3c: 1838         subs      r0, #0x18
08002a3e: 00f0d7fa     bl        #0x8002ff0
08002a42: a08a         ldrh      r0, [r4, #0x14]
08002a44: a882         strh      r0, [r5, #0x14]
08002a46: 6078         ldrb      r0, [r4, #1]
08002a48: 0428         cmp       r0, #4
08002a4a: 04d1         bne       #0x8002a56
08002a4c: 0c49         ldr       r1, [pc, #0x30]
08002a4e: e08a         ldrh      r0, [r4, #0x16]
08002a50: 0988         ldrh      r1, [r1]
08002a52: 0844         add       r0, r1
08002a54: a082         strh      r0, [r4, #0x14]
08002a56: 0120         movs      r0, #1
08002a58: 6070         strb      r0, [r4, #1]
08002a5a: 84f82000     strb.w    r0, [r4, #0x20]
08002a5e: e068         ldr       r0, [r4, #0xc]
08002a60: e860         str       r0, [r5, #0xc]
08002a62: e068         ldr       r0, [r4, #0xc]
08002a64: 08b1         cbz       r0, #0x8002a6a
08002a66: 0561         str       r5, [r0, #0x10]
08002a68: e660         str       r6, [r4, #0xc]
08002a6a: 2661         str       r6, [r4, #0x10]
08002a6c: a88a         ldrh      r0, [r5, #0x14]
08002a6e: 0028         cmp       r0, #0
08002a70: 02d1         bne       #0x8002a78
08002a72: ec68         ldr       r4, [r5, #0xc]
08002a74: 002c         cmp       r4, #0
08002a76: d5d1         bne       #0x8002a24
08002a78: 70bd         pop       {r4, r5, r6, pc}
08002a7a: 0000         movs      r0, r0
08002a7c: 340f         lsrs      r4, r6, #0x1c
08002a7e: 0020         movs      r0, #0
08002a80: 8800         lsls      r0, r1, #2
08002a82: 0020         movs      r0, #0
08002a84: 70b5         push      {r4, r5, r6, lr}
08002a86: 0400         movs      r4, r0
08002a88: 0fd0         beq       #0x8002aaa
08002a8a: 0d4d         ldr       r5, [pc, #0x34]
08002a8c: a178         ldrb      r1, [r4, #2]
08002a8e: 0126         movs      r6, #1
08002a90: 2868         ldr       r0, [r5]
08002a92: 8278         ldrb      r2, [r0, #2]
08002a94: 9142         cmp       r1, r2
08002a96: 0cd9         bls       #0x8002ab2
08002a98: 00f0c6fa     bl        #0x8003028
08002a9c: 2868         ldr       r0, [r5]
08002a9e: 4670         strb      r6, [r0, #1]
08002aa0: 2046         mov       r0, r4
08002aa2: bde87040     pop.w     {r4, r5, r6, lr}
08002aa6: 00f03bbb     b.w       #0x8003120
08002aaa: 0648         ldr       r0, [pc, #0x18]
08002aac: 00f09af8     bl        #0x8002be4
08002ab0: f7e7         b         #0x8002aa2
08002ab2: 6670         strb      r6, [r4, #1]
08002ab4: 2146         mov       r1, r4
08002ab6: bde87040     pop.w     {r4, r5, r6, lr}
08002aba: 0248         ldr       r0, [pc, #8]
08002abc: 00f098ba     b.w       #0x8002ff0
08002ac0: 8000         lsls      r0, r0, #2
08002ac2: 0020         movs      r0, #0
08002ac4: 1c0f         lsrs      r4, r3, #0x1c
08002ac6: 0020         movs      r0, #0
08002ac8: 0321         movs      r1, #3
08002aca: fff783bf     b.w       #0x80029d4
08002ace: 0000         movs      r0, r0
08002ad0: 0148         ldr       r0, [pc, #4]
08002ad2: 0068         ldr       r0, [r0]
08002ad4: 408b         ldrh      r0, [r0, #0x1a]
08002ad6: 7047         bx        lr
08002ad8: 8000         lsls      r0, r0, #2
08002ada: 0020         movs      r0, #0
08002adc: 10b5         push      {r4, lr}
08002ade: 0446         mov       r4, r0
08002ae0: 008b         ldrh      r0, [r0, #0x18]
08002ae2: 0843         orrs      r0, r1
08002ae4: 2083         strh      r0, [r4, #0x18]
08002ae6: 6278         ldrb      r2, [r4, #1]
08002ae8: 618b         ldrh      r1, [r4, #0x1a]
08002aea: 062a         cmp       r2, #6
08002aec: 16d0         beq       #0x8002b1c
08002aee: 052a         cmp       r2, #5
08002af0: 17d1         bne       #0x8002b22
08002af2: 0842         tst       r0, r1
08002af4: 15d0         beq       #0x8002b22
08002af6: 01ea0002     and.w     r2, r1, r0
08002afa: 6283         strh      r2, [r4, #0x1a]
08002afc: 8843         bics      r0, r1
08002afe: 2083         strh      r0, [r4, #0x18]
08002b00: 2046         mov       r0, r4
08002b02: 00f0b5fa     bl        #0x8003070
08002b06: 0120         movs      r0, #1
08002b08: 6070         strb      r0, [r4, #1]
08002b0a: 0220         movs      r0, #2
08002b0c: 84f82000     strb.w    r0, [r4, #0x20]
08002b10: 2146         mov       r1, r4
08002b12: bde81040     pop.w     {r4, lr}
08002b16: 0348         ldr       r0, [pc, #0xc]
08002b18: 00f06aba     b.w       #0x8002ff0
08002b1c: 31ea0002     bics.w    r2, r1, r0
08002b20: ecd0         beq       #0x8002afc
08002b22: 10bd         pop       {r4, pc}
08002b24: 1c0f         lsrs      r4, r3, #0x1c
08002b26: 0020         movs      r0, #0
08002b28: 0246         mov       r2, r0
08002b2a: 70b5         push      {r4, r5, r6, lr}
08002b2c: 1548         ldr       r0, [pc, #0x54]
08002b2e: 00eb8100     add.w     r0, r0, r1, lsl #2
08002b32: 50f8044c     ldr       r4, [r0, #-0x4]
08002b36: 002c         cmp       r4, #0
08002b38: 22d0         beq       #0x8002b80
08002b3a: 208b         ldrh      r0, [r4, #0x18]
08002b3c: 1043         orrs      r0, r2
08002b3e: 2083         strh      r0, [r4, #0x18]
08002b40: 6178         ldrb      r1, [r4, #1]
08002b42: 658b         ldrh      r5, [r4, #0x1a]
08002b44: 0629         cmp       r1, #6
08002b46: 18d0         beq       #0x8002b7a
08002b48: 0529         cmp       r1, #5
08002b4a: 19d1         bne       #0x8002b80
08002b4c: 2842         tst       r0, r5
08002b4e: 17d0         beq       #0x8002b80
08002b50: 05ea0001     and.w     r1, r5, r0
08002b54: 6183         strh      r1, [r4, #0x1a]
08002b56: a843         bics      r0, r5
08002b58: 2083         strh      r0, [r4, #0x18]
08002b5a: 2046         mov       r0, r4
08002b5c: 00f088fa     bl        #0x8003070
08002b60: 208b         ldrh      r0, [r4, #0x18]
08002b62: a843         bics      r0, r5
08002b64: 2083         strh      r0, [r4, #0x18]
08002b66: 0120         movs      r0, #1
08002b68: 6070         strb      r0, [r4, #1]
08002b6a: 0220         movs      r0, #2
08002b6c: 84f82000     strb.w    r0, [r4, #0x20]
08002b70: 2046         mov       r0, r4
08002b72: bde87040     pop.w     {r4, r5, r6, lr}
08002b76: fff785bf     b.w       #0x8002a84
08002b7a: 35ea0001     bics.w    r1, r5, r0
08002b7e: ead0         beq       #0x8002b56
08002b80: 70bd         pop       {r4, r5, r6, pc}
08002b82: 0000         movs      r0, r0
08002b84: dc0e         lsrs      r4, r3, #0x1b
08002b86: 0020         movs      r0, #0
08002b88: 70b5         push      {r4, r5, r6, lr}
08002b8a: 0346         mov       r3, r0
08002b8c: 0c48         ldr       r0, [pc, #0x30]
08002b8e: 0d46         mov       r5, r1
08002b90: 0468         ldr       r4, [r0]
08002b92: 208b         ldrh      r0, [r4, #0x18]
08002b94: 42b1         cbz       r2, #0x8002ba8
08002b96: 33ea0001     bics.w    r1, r3, r0
08002b9a: 01d0         beq       #0x8002ba0
08002b9c: 0621         movs      r1, #6
08002b9e: 09e0         b         #0x8002bb4
08002ba0: 9843         bics      r0, r3
08002ba2: 2083         strh      r0, [r4, #0x18]
08002ba4: 0220         movs      r0, #2
08002ba6: 70bd         pop       {r4, r5, r6, pc}
08002ba8: 10ea0301     ands.w    r1, r0, r3
08002bac: 01d0         beq       #0x8002bb2
08002bae: 6183         strh      r1, [r4, #0x1a]
08002bb0: f6e7         b         #0x8002ba0
08002bb2: 0521         movs      r1, #5
08002bb4: 6383         strh      r3, [r4, #0x1a]
08002bb6: 2846         mov       r0, r5
08002bb8: fff70cff     bl        #0x80029d4
08002bbc: 0120         movs      r0, #1
08002bbe: 70bd         pop       {r4, r5, r6, pc}
08002bc0: 8000         lsls      r0, r0, #2
08002bc2: 0020         movs      r0, #0
08002bc4: 8142         cmp       r1, r0
08002bc6: 02d3         blo       #0x8002bce
08002bc8: 4268         ldr       r2, [r0, #4]
08002bca: 8a42         cmp       r2, r1
08002bcc: 01d8         bhi       #0x8002bd2
08002bce: 0120         movs      r0, #1
08002bd0: 7047         bx        lr
08002bd2: 50e8002f     ldrex     r2, [r0]
08002bd6: 0a60         str       r2, [r1]
08002bd8: 40e80012     strex     r2, r1, [r0]
08002bdc: 002a         cmp       r2, #0
08002bde: f8d1         bne       #0x8002bd2
08002be0: 0020         movs      r0, #0
08002be2: 7047         bx        lr
08002be4: 0146         mov       r1, r0
08002be6: 4068         ldr       r0, [r0, #4]
08002be8: 4268         ldr       r2, [r0, #4]
08002bea: 4a60         str       r2, [r1, #4]
08002bec: 0b78         ldrb      r3, [r1]
08002bee: 0022         movs      r2, #0
08002bf0: 022b         cmp       r3, #2
08002bf2: 05d0         beq       #0x8002c00
08002bf4: 012b         cmp       r3, #1
08002bf6: 03d0         beq       #0x8002c00
08002bf8: 032b         cmp       r3, #3
08002bfa: 01d0         beq       #0x8002c00
08002bfc: 4260         str       r2, [r0, #4]
08002bfe: 7047         bx        lr
08002c00: 4368         ldr       r3, [r0, #4]
08002c02: 0bb1         cbz       r3, #0x8002c08
08002c04: 9960         str       r1, [r3, #8]
08002c06: 4260         str       r2, [r0, #4]
08002c08: 8260         str       r2, [r0, #8]
08002c0a: 7047         bx        lr
08002c0c: 70b5         push      {r4, r5, r6, lr}
08002c0e: 0446         mov       r4, r0
08002c10: 0020         movs      r0, #0
08002c12: 1546         mov       r5, r2
08002c14: 2070         strb      r0, [r4]
08002c16: 0122         movs      r2, #1
08002c18: 6270         strb      r2, [r4, #1]
08002c1a: a170         strb      r1, [r4, #2]
08002c1c: 6060         str       r0, [r4, #4]
08002c1e: a060         str       r0, [r4, #8]
08002c20: e060         str       r0, [r4, #0xc]
08002c22: 2061         str       r0, [r4, #0x10]
08002c24: a082         strh      r0, [r4, #0x14]
08002c26: e082         strh      r0, [r4, #0x16]
08002c28: 2083         strh      r0, [r4, #0x18]
08002c2a: 6083         strh      r0, [r4, #0x1a]
08002c2c: 84f82000     strb.w    r0, [r4, #0x20]
08002c30: 84f82100     strb.w    r0, [r4, #0x21]
08002c34: 608c         ldrh      r0, [r4, #0x22]
08002c36: 18b9         cbnz      r0, #0x8002c40
08002c38: 0448         ldr       r0, [pc, #0x10]
08002c3a: fff7bdfe     bl        #0x80029b8
08002c3e: a062         str       r0, [r4, #0x28]
08002c40: 2946         mov       r1, r5
08002c42: 2046         mov       r0, r4
08002c44: bde87040     pop.w     {r4, r5, r6, lr}
08002c48: 00f004b8     b.w       #0x8002c54
08002c4c: 380c         lsrs      r0, r7, #0x10
08002c4e: 0020         movs      r0, #0
08002c50: 7047         bx        lr
08002c52: 0000         movs      r0, r0
08002c54: 10b5         push      {r4, lr}
08002c56: 428c         ldrh      r2, [r0, #0x22]
08002c58: 9208         lsrs      r2, r2, #2
08002c5a: 03d1         bne       #0x8002c64
08002c5c: 0f4a         ldr       r2, [pc, #0x3c]
08002c5e: 1288         ldrh      r2, [r2]
08002c60: c2f38d02     ubfx      r2, r2, #2, #0xe
08002c64: 836a         ldr       r3, [r0, #0x28]
08002c66: 03eb8202     add.w     r2, r3, r2, lsl #2
08002c6a: 5307         lsls      r3, r2, #0x1d
08002c6c: 00d5         bpl       #0x8002c70
08002c6e: 121f         subs      r2, r2, #4
08002c70: 403a         subs      r2, #0x40
08002c72: 4ff08073     mov.w     r3, #0x1000000
08002c76: c2e90e13     strd      r1, r3, [r2, #0x38]
08002c7a: 0023         movs      r3, #0
08002c7c: 4fea0304     mov.w     r4, r3
08002c80: 42f82340     str.w     r4, [r2, r3, lsl #2]
08002c84: 5b1c         adds      r3, r3, #1
08002c86: 0e2b         cmp       r3, #0xe
08002c88: fad3         blo       #0x8002c80
08002c8a: c369         ldr       r3, [r0, #0x1c]
08002c8c: 1362         str       r3, [r2, #0x20]
08002c8e: 4262         str       r2, [r0, #0x24]
08002c90: c162         str       r1, [r0, #0x2c]
08002c92: 806a         ldr       r0, [r0, #0x28]
08002c94: 0249         ldr       r1, [pc, #8]
08002c96: 0160         str       r1, [r0]
08002c98: 10bd         pop       {r4, pc}
08002c9a: 0000         movs      r0, r0
08002c9c: c03e         subs      r6, #0xc0
08002c9e: 0008         lsrs      r0, r0, #0x20
08002ca0: a52e         cmp       r6, #0xa5
08002ca2: 5ae2         b         #0x800315a
08002ca4: 0349         ldr       r1, [pc, #0xc]
08002ca6: 044a         ldr       r2, [pc, #0x10]
08002ca8: 0968         ldr       r1, [r1]
08002caa: c882         strh      r0, [r1, #0x16]
08002cac: 1288         ldrh      r2, [r2]
08002cae: 1044         add       r0, r2
08002cb0: 8882         strh      r0, [r1, #0x14]
08002cb2: 7047         bx        lr
08002cb4: 8000         lsls      r0, r0, #2
08002cb6: 0020         movs      r0, #0
08002cb8: 8800         lsls      r0, r1, #2
08002cba: 0020         movs      r0, #0
08002cbc: 0848         ldr       r0, [pc, #0x20]
08002cbe: 0168         ldr       r1, [r0]
08002cc0: 0848         ldr       r0, [pc, #0x20]
08002cc2: 8a8a         ldrh      r2, [r1, #0x14]
08002cc4: 0088         ldrh      r0, [r0]
08002cc6: cb8a         ldrh      r3, [r1, #0x16]
08002cc8: a2eb0000     sub.w     r0, r2, r0
08002ccc: 1a44         add       r2, r3
08002cce: 80b2         uxth      r0, r0
08002cd0: 8a82         strh      r2, [r1, #0x14]
08002cd2: 0104         lsls      r1, r0, #0x10
08002cd4: 02d4         bmi       #0x8002cdc
08002cd6: 0421         movs      r1, #4
08002cd8: fff77cbe     b.w       #0x80029d4
08002cdc: 7047         bx        lr
08002cde: 0000         movs      r0, r0
08002ce0: 8000         lsls      r0, r0, #2
08002ce2: 0020         movs      r0, #0
08002ce4: 8800         lsls      r0, r1, #2
08002ce6: 0020         movs      r0, #0
08002ce8: 2de9f041     push.w    {r4, r5, r6, r7, r8, lr}
08002cec: 0f46         mov       r7, r1
08002cee: 0446         mov       r4, r0
08002cf0: 4168         ldr       r1, [r0, #4]
08002cf2: 0020         movs      r0, #0
08002cf4: 04f10c06     add.w     r6, r4, #0xc
08002cf8: 21b1         cbz       r1, #0x8002d04
08002cfa: 6178         ldrb      r1, [r4, #1]
08002cfc: 0229         cmp       r1, #2
08002cfe: 1ad0         beq       #0x8002d36
08002d00: a189         ldrh      r1, [r4, #0xc]
08002d02: a9b3         cbz       r1, #0x8002d70
08002d04: a189         ldrh      r1, [r4, #0xc]
08002d06: e289         ldrh      r2, [r4, #0xe]
08002d08: 9142         cmp       r1, r2
08002d0a: 46d2         bhs       #0x8002d9a
08002d0c: 2189         ldrh      r1, [r4, #8]
08002d0e: 04eb8101     add.w     r1, r4, r1, lsl #2
08002d12: 0f61         str       r7, [r1, #0x10]
08002d14: d6e85f1f     ldrexh    r1, [r6]
08002d18: 491c         adds      r1, r1, #1
08002d1a: c6e8521f     strexh    r2, r1, [r6]
08002d1e: 002a         cmp       r2, #0
08002d20: f8d1         bne       #0x8002d14
08002d22: 2189         ldrh      r1, [r4, #8]
08002d24: 491c         adds      r1, r1, #1
08002d26: 89b2         uxth      r1, r1
08002d28: 2181         strh      r1, [r4, #8]
08002d2a: e289         ldrh      r2, [r4, #0xe]
08002d2c: 9142         cmp       r1, r2
08002d2e: 00d1         bne       #0x8002d32
08002d30: 2081         strh      r0, [r4, #8]
08002d32: bde8f081     pop.w     {r4, r5, r6, r7, r8, pc}
08002d36: 0746         mov       r7, r0
08002d38: 6070         strb      r0, [r4, #1]
08002d3a: 2046         mov       r0, r4
08002d3c: fff752ff     bl        #0x8002be4
08002d40: 80f82070     strb.w    r7, [r0, #0x20]
08002d44: 2189         ldrh      r1, [r4, #8]
08002d46: 0546         mov       r5, r0
08002d48: 04eb8101     add.w     r1, r4, r1, lsl #2
08002d4c: c069         ldr       r0, [r0, #0x1c]
08002d4e: 0861         str       r0, [r1, #0x10]
08002d50: d6e85f0f     ldrexh    r0, [r6]
08002d54: 401c         adds      r0, r0, #1
08002d56: c6e8510f     strexh    r1, r0, [r6]
08002d5a: 0029         cmp       r1, #0
08002d5c: f8d1         bne       #0x8002d50
08002d5e: 2089         ldrh      r0, [r4, #8]
08002d60: 401c         adds      r0, r0, #1
08002d62: 80b2         uxth      r0, r0
08002d64: 2081         strh      r0, [r4, #8]
08002d66: e189         ldrh      r1, [r4, #0xe]
08002d68: 8842         cmp       r0, r1
08002d6a: 0bd1         bne       #0x8002d84
08002d6c: 2781         strh      r7, [r4, #8]
08002d6e: 09e0         b         #0x8002d84
08002d70: ffe7         b         #0x8002d72
08002d72: 2046         mov       r0, r4
08002d74: fff736ff     bl        #0x8002be4
08002d78: 0546         mov       r5, r0
08002d7a: c069         ldr       r0, [r0, #0x1c]
08002d7c: 0421         movs      r1, #4
08002d7e: 0760         str       r7, [r0]
08002d80: 85f82010     strb.w    r1, [r5, #0x20]
08002d84: 0120         movs      r0, #1
08002d86: 6870         strb      r0, [r5, #1]
08002d88: 2846         mov       r0, r5
08002d8a: 00f071f9     bl        #0x8003070
08002d8e: 2946         mov       r1, r5
08002d90: bde8f041     pop.w     {r4, r5, r6, r7, r8, lr}
08002d94: 0348         ldr       r0, [pc, #0xc]
08002d96: 00f02bb9     b.w       #0x8002ff0
08002d9a: bde8f041     pop.w     {r4, r5, r6, r7, r8, lr}
08002d9e: 0320         movs      r0, #3
08002da0: fff7f2bd     b.w       #0x8002988
08002da4: 1c0f         lsrs      r4, r3, #0x1c
08002da6: 0020         movs      r0, #0
08002da8: 2de9f047     push.w    {r4, r5, r6, r7, r8, sb, sl, lr}
08002dac: 0546         mov       r5, r0
08002dae: 4088         ldrh      r0, [r0, #2]
08002db0: 20b1         cbz       r0, #0x8002dbc
08002db2: 264c         ldr       r4, [pc, #0x98]
08002db4: a968         ldr       r1, [r5, #8]
08002db6: 2268         ldr       r2, [r4]
08002db8: 9142         cmp       r1, r2
08002dba: 02d0         beq       #0x8002dc2
08002dbc: ff20         movs      r0, #0xff
08002dbe: bde8f087     pop.w     {r4, r5, r6, r7, r8, sb, sl, pc}
08002dc2: 401e         subs      r0, r0, #1
08002dc4: 0004         lsls      r0, r0, #0x10
08002dc6: 000c         lsrs      r0, r0, #0x10
08002dc8: 6880         strh      r0, [r5, #2]
08002dca: 3dd1         bne       #0x8002e48
08002dcc: 2168         ldr       r1, [r4]
08002dce: 6878         ldrb      r0, [r5, #1]
08002dd0: dff87c80     ldr.w     r8, [pc, #0x7c]
08002dd4: 8870         strb      r0, [r1, #2]
08002dd6: 6a68         ldr       r2, [r5, #4]
08002dd8: 4ff00009     mov.w     sb, #0
08002ddc: 0127         movs      r7, #1
08002dde: 3ab3         cbz       r2, #0x8002e30
08002de0: 2846         mov       r0, r5
08002de2: fff7fffe     bl        #0x8002be4
08002de6: 0646         mov       r6, r0
08002de8: 0520         movs      r0, #5
08002dea: 86f82000     strb.w    r0, [r6, #0x20]
08002dee: 3046         mov       r0, r6
08002df0: 00f03ef9     bl        #0x8003070
08002df4: 6f80         strh      r7, [r5, #2]
08002df6: ae60         str       r6, [r5, #8]
08002df8: b078         ldrb      r0, [r6, #2]
08002dfa: 6870         strb      r0, [r5, #1]
08002dfc: 2168         ldr       r1, [r4]
08002dfe: d8f80400     ldr.w     r0, [r8, #4]
08002e02: 8a78         ldrb      r2, [r1, #2]
08002e04: 8078         ldrb      r0, [r0, #2]
08002e06: 8242         cmp       r2, r0
08002e08: 01d3         blo       #0x8002e0e
08002e0a: 3046         mov       r0, r6
08002e0c: 0ae0         b         #0x8002e24
08002e0e: 1048         ldr       r0, [pc, #0x40]
08002e10: 00f0eef8     bl        #0x8002ff0
08002e14: 3146         mov       r1, r6
08002e16: 0e48         ldr       r0, [pc, #0x38]
08002e18: 00f0eaf8     bl        #0x8002ff0
08002e1c: 2068         ldr       r0, [r4]
08002e1e: 4770         strb      r7, [r0, #1]
08002e20: 7770         strb      r7, [r6, #1]
08002e22: 0fe0         b         #0x8002e44
08002e24: fff72efe     bl        #0x8002a84
08002e28: 2168         ldr       r1, [r4]
08002e2a: 81f82090     strb.w    sb, [r1, #0x20]
08002e2e: 0be0         b         #0x8002e48
08002e30: d8f80420     ldr.w     r2, [r8, #4]
08002e34: 9278         ldrb      r2, [r2, #2]
08002e36: 8242         cmp       r2, r0
08002e38: 06d9         bls       #0x8002e48
08002e3a: 0548         ldr       r0, [pc, #0x14]
08002e3c: 00f0d8f8     bl        #0x8002ff0
08002e40: 2068         ldr       r0, [r4]
08002e42: 4770         strb      r7, [r0, #1]
08002e44: 0020         movs      r0, #0
08002e46: ede7         b         #0x8002e24
08002e48: 0020         movs      r0, #0
08002e4a: b8e7         b         #0x8002dbe
08002e4c: 8000         lsls      r0, r0, #2
08002e4e: 0020         movs      r0, #0
08002e50: 1c0f         lsrs      r4, r3, #0x1c
08002e52: 0020         movs      r0, #0
08002e54: 70b5         push      {r4, r5, r6, lr}
08002e56: 174d         ldr       r5, [pc, #0x5c]
08002e58: 0e46         mov       r6, r1
08002e5a: 0446         mov       r4, r0
08002e5c: 4188         ldrh      r1, [r0, #2]
08002e5e: 2868         ldr       r0, [r5]
08002e60: 39b1         cbz       r1, #0x8002e72
08002e62: a168         ldr       r1, [r4, #8]
08002e64: 8142         cmp       r1, r0
08002e66: 08d1         bne       #0x8002e7a
08002e68: 6088         ldrh      r0, [r4, #2]
08002e6a: 401c         adds      r0, r0, #1
08002e6c: 6080         strh      r0, [r4, #2]
08002e6e: 0020         movs      r0, #0
08002e70: 70bd         pop       {r4, r5, r6, pc}
08002e72: a060         str       r0, [r4, #8]
08002e74: 8078         ldrb      r0, [r0, #2]
08002e76: 6070         strb      r0, [r4, #1]
08002e78: f6e7         b         #0x8002e68
08002e7a: 76b1         cbz       r6, #0x8002e9a
08002e7c: 6278         ldrb      r2, [r4, #1]
08002e7e: 8078         ldrb      r0, [r0, #2]
08002e80: 8242         cmp       r2, r0
08002e82: 03d2         bhs       #0x8002e8c
08002e84: 8870         strb      r0, [r1, #2]
08002e86: a068         ldr       r0, [r4, #8]
08002e88: 00f0d8f8     bl        #0x800303c
08002e8c: 6068         ldr       r0, [r4, #4]
08002e8e: 30b1         cbz       r0, #0x8002e9e
08002e90: 2046         mov       r0, r4
08002e92: 2968         ldr       r1, [r5]
08002e94: 00f0acf8     bl        #0x8002ff0
08002e98: 07e0         b         #0x8002eaa
08002e9a: 0120         movs      r0, #1
08002e9c: 70bd         pop       {r4, r5, r6, pc}
08002e9e: 2868         ldr       r0, [r5]
08002ea0: 6060         str       r0, [r4, #4]
08002ea2: 2868         ldr       r0, [r5]
08002ea4: 0021         movs      r1, #0
08002ea6: c0e90114     strd      r1, r4, [r0, #4]
08002eaa: 0921         movs      r1, #9
08002eac: 3046         mov       r0, r6
08002eae: fff791fd     bl        #0x80029d4
08002eb2: f2e7         b         #0x8002e9a
08002eb4: 8000         lsls      r0, r0, #2
08002eb6: 0020         movs      r0, #0
08002eb8: 70b5         push      {r4, r5, r6, lr}
08002eba: 1a48         ldr       r0, [pc, #0x68]
08002ebc: 0121         movs      r1, #1
08002ebe: 0068         ldr       r0, [r0]
08002ec0: 4170         strb      r1, [r0, #1]
08002ec2: 00f0b1f8     bl        #0x8003028
08002ec6: 184d         ldr       r5, [pc, #0x60]
08002ec8: 6c78         ldrb      r4, [r5, #1]
08002eca: 16e0         b         #0x8002efa
08002ecc: 05ebc401     add.w     r1, r5, r4, lsl #3
08002ed0: 4868         ldr       r0, [r1, #4]
08002ed2: 0278         ldrb      r2, [r0]
08002ed4: e2b1         cbz       r2, #0x8002f10
08002ed6: 012a         cmp       r2, #1
08002ed8: 1fd0         beq       #0x8002f1a
08002eda: 00f0f5f8     bl        #0x80030c8
08002ede: e878         ldrb      r0, [r5, #3]
08002ee0: 641c         adds      r4, r4, #1
08002ee2: 8442         cmp       r4, r0
08002ee4: 00d1         bne       #0x8002ee8
08002ee6: 0024         movs      r4, #0
08002ee8: 0f48         ldr       r0, [pc, #0x3c]
08002eea: 801c         adds      r0, r0, #2
08002eec: d0e84f1f     ldrexb    r1, [r0]
08002ef0: 491e         subs      r1, r1, #1
08002ef2: c0e8421f     strexb    r2, r1, [r0]
08002ef6: 002a         cmp       r2, #0
08002ef8: f8d1         bne       #0x8002eec
08002efa: a878         ldrb      r0, [r5, #2]
08002efc: 0028         cmp       r0, #0
08002efe: e5d1         bne       #0x8002ecc
08002f00: 6c70         strb      r4, [r5, #1]
08002f02: 0a48         ldr       r0, [pc, #0x28]
08002f04: fff76efe     bl        #0x8002be4
08002f08: bde87040     pop.w     {r4, r5, r6, lr}
08002f0c: 00f008b9     b.w       #0x8003120
08002f10: 0989         ldrh      r1, [r1, #8]
08002f12: 89b2         uxth      r1, r1
08002f14: fff7e2fd     bl        #0x8002adc
08002f18: e1e7         b         #0x8002ede
08002f1a: 8968         ldr       r1, [r1, #8]
08002f1c: fff7e4fe     bl        #0x8002ce8
08002f20: dde7         b         #0x8002ede
08002f22: 0000         movs      r0, r0
08002f24: 8000         lsls      r0, r0, #2
08002f26: 0020         movs      r0, #0
08002f28: d80d         lsrs      r0, r3, #0x17
08002f2a: 0020         movs      r0, #0
08002f2c: 1c0f         lsrs      r4, r3, #0x1c
08002f2e: 0020         movs      r0, #0
08002f30: 0548         ldr       r0, [pc, #0x14]
08002f32: 0178         ldrb      r1, [r0]
08002f34: 11b1         cbz       r1, #0x8002f3c
08002f36: 0121         movs      r1, #1
08002f38: 4170         strb      r1, [r0, #1]
08002f3a: 7047         bx        lr
08002f3c: 0349         ldr       r1, [pc, #0xc]
08002f3e: 4ff08050     mov.w     r0, #0x10000000
08002f42: 0860         str       r0, [r1]
08002f44: 7047         bx        lr
08002f46: 0000         movs      r0, r0
08002f48: 9000         lsls      r0, r2, #2
08002f4a: 0020         movs      r0, #0
08002f4c: 04ed00e0     stc       p0, c14, [r4, #-0]
08002f50: f0b4         push      {r4, r5, r6, r7}
08002f52: 144a         ldr       r2, [pc, #0x50]
08002f54: 941c         adds      r4, r2, #2
08002f56: d578         ldrb      r5, [r2, #3]
08002f58: 4fea0206     mov.w     r6, r2
08002f5c: d4e84f3f     ldrexb    r3, [r4]
08002f60: ab42         cmp       r3, r5
08002f62: 02d1         bne       #0x8002f6a
08002f64: bff32f8f     clrex     
08002f68: 0ee0         b         #0x8002f88
08002f6a: 5b1c         adds      r3, r3, #1
08002f6c: c4e8473f     strexb    r7, r3, [r4]
08002f70: 002f         cmp       r7, #0
08002f72: f3d1         bne       #0x8002f5c
08002f74: d6e84f3f     ldrexb    r3, [r6]
08002f78: 5c1c         adds      r4, r3, #1
08002f7a: ac42         cmp       r4, r5
08002f7c: 00d1         bne       #0x8002f80
08002f7e: 0024         movs      r4, #0
08002f80: c6e8474f     strexb    r7, r4, [r6]
08002f84: 002f         cmp       r7, #0
08002f86: f5d1         bne       #0x8002f74
08002f88: d478         ldrb      r4, [r2, #3]
08002f8a: 9c42         cmp       r4, r3
08002f8c: 05d9         bls       #0x8002f9a
08002f8e: 02ebc302     add.w     r2, r2, r3, lsl #3
08002f92: c2e90101     strd      r0, r1, [r2, #4]
08002f96: f0bc         pop       {r4, r5, r6, r7}
08002f98: 7047         bx        lr
08002f9a: f0bc         pop       {r4, r5, r6, r7}
08002f9c: 0220         movs      r0, #2
08002f9e: fff7f3bc     b.w       #0x8002988
08002fa2: 0000         movs      r0, r0
08002fa4: d80d         lsrs      r0, r3, #0x17
08002fa6: 0020         movs      r0, #0
08002fa8: 104a         ldr       r2, [pc, #0x40]
08002faa: 10b5         push      {r4, lr}
08002fac: d368         ldr       r3, [r2, #0xc]
08002fae: abb1         cbz       r3, #0x8002fdc
08002fb0: 1346         mov       r3, r2
08002fb2: 9b8a         ldrh      r3, [r3, #0x14]
08002fb4: 03e0         b         #0x8002fbe
08002fb6: 8cb1         cbz       r4, #0x8002fdc
08002fb8: 2246         mov       r2, r4
08002fba: a48a         ldrh      r4, [r4, #0x14]
08002fbc: 2344         add       r3, r4
08002fbe: d468         ldr       r4, [r2, #0xc]
08002fc0: 8b42         cmp       r3, r1
08002fc2: f8d3         blo       #0x8002fb6
08002fc4: c460         str       r4, [r0, #0xc]
08002fc6: d060         str       r0, [r2, #0xc]
08002fc8: 0261         str       r2, [r0, #0x10]
08002fca: c468         ldr       r4, [r0, #0xc]
08002fcc: 04b1         cbz       r4, #0x8002fd0
08002fce: 2061         str       r0, [r4, #0x10]
08002fd0: 591a         subs      r1, r3, r1
08002fd2: 8182         strh      r1, [r0, #0x14]
08002fd4: 908a         ldrh      r0, [r2, #0x14]
08002fd6: 401a         subs      r0, r0, r1
08002fd8: 9082         strh      r0, [r2, #0x14]
08002fda: 10bd         pop       {r4, pc}
08002fdc: 0024         movs      r4, #0
08002fde: c460         str       r4, [r0, #0xc]
08002fe0: d060         str       r0, [r2, #0xc]
08002fe2: c91a         subs      r1, r1, r3
08002fe4: 0261         str       r2, [r0, #0x10]
08002fe6: 9182         strh      r1, [r2, #0x14]
08002fe8: 8482         strh      r4, [r0, #0x14]
08002fea: 10bd         pop       {r4, pc}
08002fec: 340f         lsrs      r4, r6, #0x1c
08002fee: 0020         movs      r0, #0
08002ff0: 30b5         push      {r4, r5, lr}
08002ff2: 0278         ldrb      r2, [r0]
08002ff4: 0023         movs      r3, #0
08002ff6: 022a         cmp       r2, #2
08002ff8: 03d0         beq       #0x8003002
08002ffa: 012a         cmp       r2, #1
08002ffc: 01d0         beq       #0x8003002
08002ffe: 032a         cmp       r2, #3
08003000: 00d1         bne       #0x8003004
08003002: 0123         movs      r3, #1
08003004: 8c78         ldrb      r4, [r1, #2]
08003006: 00e0         b         #0x800300a
08003008: 1046         mov       r0, r2
0800300a: 4268         ldr       r2, [r0, #4]
0800300c: 12b1         cbz       r2, #0x8003014
0800300e: 9578         ldrb      r5, [r2, #2]
08003010: a542         cmp       r5, r4
08003012: f9d2         bhs       #0x8003008
08003014: 4a60         str       r2, [r1, #4]
08003016: 4160         str       r1, [r0, #4]
08003018: 1bb1         cbz       r3, #0x8003022
0800301a: 02b1         cbz       r2, #0x800301e
0800301c: 9160         str       r1, [r2, #8]
0800301e: 8860         str       r0, [r1, #8]
08003020: 30bd         pop       {r4, r5, pc}
08003022: 0020         movs      r0, #0
08003024: fbe7         b         #0x800301e
08003026: 0000         movs      r0, r0
08003028: 0349         ldr       r1, [pc, #0xc]
0800302a: 4a68         ldr       r2, [r1, #4]
0800302c: 4260         str       r2, [r0, #4]
0800302e: 0022         movs      r2, #0
08003030: 8260         str       r2, [r0, #8]
08003032: 4860         str       r0, [r1, #4]
08003034: 7047         bx        lr
08003036: 0000         movs      r0, r0
08003038: 1c0f         lsrs      r4, r3, #0x1c
0800303a: 0020         movs      r0, #0
0800303c: 10b5         push      {r4, lr}
0800303e: 8368         ldr       r3, [r0, #8]
08003040: 0446         mov       r4, r0
08003042: 2bb9         cbnz      r3, #0x8003050
08003044: 6078         ldrb      r0, [r4, #1]
08003046: 0128         cmp       r0, #1
08003048: 0ed1         bne       #0x8003068
0800304a: 084b         ldr       r3, [pc, #0x20]
0800304c: 03e0         b         #0x8003056
0800304e: 9b68         ldr       r3, [r3, #8]
08003050: 1878         ldrb      r0, [r3]
08003052: 0028         cmp       r0, #0
08003054: fbd0         beq       #0x800304e
08003056: 2046         mov       r0, r4
08003058: 00f01ef8     bl        #0x8003098
0800305c: 2146         mov       r1, r4
0800305e: bde81040     pop.w     {r4, lr}
08003062: 1846         mov       r0, r3
08003064: fff7c4bf     b.w       #0x8002ff0
08003068: 10bd         pop       {r4, pc}
0800306a: 0000         movs      r0, r0
0800306c: 1c0f         lsrs      r4, r3, #0x1c
0800306e: 0020         movs      r0, #0
08003070: 10b5         push      {r4, lr}
08003072: 0169         ldr       r1, [r0, #0x10]
08003074: 0029         cmp       r1, #0
08003076: 0ed0         beq       #0x8003096
08003078: c268         ldr       r2, [r0, #0xc]
0800307a: ca60         str       r2, [r1, #0xc]
0800307c: c368         ldr       r3, [r0, #0xc]
0800307e: 0022         movs      r2, #0
08003080: 3bb1         cbz       r3, #0x8003092
08003082: 8b8a         ldrh      r3, [r1, #0x14]
08003084: 848a         ldrh      r4, [r0, #0x14]
08003086: 2344         add       r3, r4
08003088: 8b82         strh      r3, [r1, #0x14]
0800308a: c368         ldr       r3, [r0, #0xc]
0800308c: 1961         str       r1, [r3, #0x10]
0800308e: c260         str       r2, [r0, #0xc]
08003090: 00e0         b         #0x8003094
08003092: 8a82         strh      r2, [r1, #0x14]
08003094: 0261         str       r2, [r0, #0x10]
08003096: 10bd         pop       {r4, pc}
08003098: 8168         ldr       r1, [r0, #8]
0800309a: 39b1         cbz       r1, #0x80030ac
0800309c: 4268         ldr       r2, [r0, #4]
0800309e: 4a60         str       r2, [r1, #4]
080030a0: 4168         ldr       r1, [r0, #4]
080030a2: 0029         cmp       r1, #0
080030a4: 01d0         beq       #0x80030aa
080030a6: 8068         ldr       r0, [r0, #8]
080030a8: 8860         str       r0, [r1, #8]
080030aa: 7047         bx        lr
080030ac: 0549         ldr       r1, [pc, #0x14]
080030ae: 06e0         b         #0x80030be
080030b0: 4a68         ldr       r2, [r1, #4]
080030b2: 8242         cmp       r2, r0
080030b4: 02d1         bne       #0x80030bc
080030b6: 4068         ldr       r0, [r0, #4]
080030b8: 4860         str       r0, [r1, #4]
080030ba: 7047         bx        lr
080030bc: 1146         mov       r1, r2
080030be: 0029         cmp       r1, #0
080030c0: f6d1         bne       #0x80030b0
080030c2: 7047         bx        lr
080030c4: 1c0f         lsrs      r4, r3, #0x1c
080030c6: 0020         movs      r0, #0
080030c8: 10b5         push      {r4, lr}
080030ca: 4168         ldr       r1, [r0, #4]
080030cc: 79b1         cbz       r1, #0x80030ee
080030ce: fff789fd     bl        #0x8002be4
080030d2: 0446         mov       r4, r0
080030d4: fff7ccff     bl        #0x8003070
080030d8: 0120         movs      r0, #1
080030da: 6070         strb      r0, [r4, #1]
080030dc: 0320         movs      r0, #3
080030de: 84f82000     strb.w    r0, [r4, #0x20]
080030e2: 2146         mov       r1, r4
080030e4: bde81040     pop.w     {r4, lr}
080030e8: 0348         ldr       r0, [pc, #0xc]
080030ea: fff781bf     b.w       #0x8002ff0
080030ee: 4188         ldrh      r1, [r0, #2]
080030f0: 491c         adds      r1, r1, #1
080030f2: 4180         strh      r1, [r0, #2]
080030f4: 10bd         pop       {r4, pc}
080030f6: 0000         movs      r0, r0
080030f8: 1c0f         lsrs      r4, r3, #0x1c
080030fa: 0020         movs      r0, #0
080030fc: 0648         ldr       r0, [pc, #0x18]
080030fe: 0068         ldr       r0, [r0]
08003100: d0e90910     ldrd      r1, r0, [r0, #0x24]
08003104: 8142         cmp       r1, r0
08003106: 03d3         blo       #0x8003110
08003108: 0068         ldr       r0, [r0]
0800310a: 0449         ldr       r1, [pc, #0x10]
0800310c: 8842         cmp       r0, r1
0800310e: 02d0         beq       #0x8003116
08003110: 0120         movs      r0, #1
08003112: fff739bc     b.w       #0x8002988
08003116: 7047         bx        lr
08003118: 8000         lsls      r0, r0, #2
0800311a: 0020         movs      r0, #0
0800311c: a52e         cmp       r6, #0xa5
0800311e: 5ae2         b         #0x80035d6
08003120: 0749         ldr       r1, [pc, #0x1c]
08003122: 0222         movs      r2, #2
08003124: 4860         str       r0, [r1, #4]
08003126: 4270         strb      r2, [r0, #1]
08003128: 064a         ldr       r2, [pc, #0x18]
0800312a: 1278         ldrb      r2, [r2]
0800312c: 002a         cmp       r2, #0
0800312e: 05d0         beq       #0x800313c
08003130: 06c9         ldm       r1, {r1, r2}
08003132: 8a42         cmp       r2, r1
08003134: 02d0         beq       #0x800313c
08003136: c078         ldrb      r0, [r0, #3]
08003138: fff7cab9     b.w       #0x80024d0
0800313c: 7047         bx        lr
0800313e: 0000         movs      r0, r0
08003140: 8000         lsls      r0, r0, #2
08003142: 0020         movs      r0, #0
08003144: 8c00         lsls      r4, r1, #2
08003146: 0020         movs      r0, #0
08003148: 2de9f047     push.w    {r4, r5, r6, r7, r8, sb, sl, lr}
0800314c: 1646         mov       r6, r2
0800314e: 8846         mov       r8, r1
08003150: 8146         mov       sb, r0
08003152: fff795f9     bl        #0x8002480
08003156: 0020         movs      r0, #0
08003158: 0446         mov       r4, r0
0800315a: 3e4a         ldr       r2, [pc, #0xf8]
0800315c: 3e49         ldr       r1, [pc, #0xf8]
0800315e: 02e0         b         #0x8003166
08003160: 42f82040     str.w     r4, [r2, r0, lsl #2]
08003164: 401c         adds      r0, r0, #1
08003166: 0b88         ldrh      r3, [r1]
08003168: 9842         cmp       r0, r3
0800316a: f9d3         blo       #0x8003160
0800316c: 3b48         ldr       r0, [pc, #0xec]
0800316e: 3022         movs      r2, #0x30
08003170: 0188         ldrh      r1, [r0]
08003172: 3b48         ldr       r0, [pc, #0xec]
08003174: fff742f9     bl        #0x80023fc
08003178: 3a48         ldr       r0, [pc, #0xe8]
0800317a: 0088         ldrh      r0, [r0]
0800317c: 80b2         uxth      r0, r0
0800317e: 40f00042     orr       r2, r0, #0x80000000
08003182: 3948         ldr       r0, [pc, #0xe4]
08003184: 0168         ldr       r1, [r0]
08003186: 3948         ldr       r0, [pc, #0xe4]
08003188: fff738f9     bl        #0x80023fc
0800318c: 3848         ldr       r0, [pc, #0xe0]
0800318e: 0822         movs      r2, #8
08003190: 0188         ldrh      r1, [r0]
08003192: 3848         ldr       r0, [pc, #0xe0]
08003194: 0068         ldr       r0, [r0]
08003196: fff731f9     bl        #0x80023fc
0800319a: 374f         ldr       r7, [pc, #0xdc]
0800319c: ff25         movs      r5, #0xff
0800319e: 374a         ldr       r2, [pc, #0xdc]
080031a0: fd70         strb      r5, [r7, #3]
080031a2: 7c84         strh      r4, [r7, #0x22]
080031a4: 0021         movs      r1, #0
080031a6: 3846         mov       r0, r7
080031a8: fff730fd     bl        #0x8002c0c
080031ac: 3448         ldr       r0, [pc, #0xd0]
080031ae: 0421         movs      r1, #4
080031b0: 0170         strb      r1, [r0]
080031b2: 4460         str       r4, [r0, #4]
080031b4: 3348         ldr       r0, [pc, #0xcc]
080031b6: 0170         strb      r1, [r0]
080031b8: c460         str       r4, [r0, #0xc]
080031ba: 0461         str       r4, [r0, #0x10]
080031bc: 8482         strh      r4, [r0, #0x14]
080031be: 786a         ldr       r0, [r7, #0x24]
080031c0: 2030         adds      r0, #0x20
080031c2: fcf7fdff     bl        #0x80001c0
080031c6: 3048         ldr       r0, [pc, #0xc0]
080031c8: 3149         ldr       r1, [pc, #0xc4]
080031ca: 0760         str       r7, [r0]
080031cc: 0220         movs      r0, #2
080031ce: 7870         strb      r0, [r7, #1]
080031d0: 2e48         ldr       r0, [pc, #0xb8]
080031d2: 0470         strb      r4, [r0]
080031d4: 4470         strb      r4, [r0, #1]
080031d6: 0978         ldrb      r1, [r1]
080031d8: c170         strb      r1, [r0, #3]
080031da: fff739fd     bl        #0x8002c50
080031de: 2d48         ldr       r0, [pc, #0xb4]
080031e0: 0168         ldr       r1, [r0]
080031e2: 41f47f01     orr       r1, r1, #0xff0000
080031e6: 0160         str       r1, [r0]
080031e8: 0068         ldr       r0, [r0]
080031ea: 2906         lsls      r1, r5, #0x18
080031ec: 01ea0020     and.w     r0, r1, r0, lsl #8
080031f0: 2849         ldr       r1, [pc, #0xa0]
080031f2: c043         mvns      r0, r0
080031f4: 1439         subs      r1, #0x14
080031f6: b0fa80f0     clz       r0, r0
080031fa: 0968         ldr       r1, [r1]
080031fc: c0f10800     rsb.w     r0, r0, #8
08003200: c1f30221     ubfx      r1, r1, #8, #3
08003204: 8142         cmp       r1, r0
08003206: 00db         blt       #0x800320a
08003208: 481c         adds      r0, r1, #1
0800320a: 2249         ldr       r1, [pc, #0x88]
0800320c: 091f         subs      r1, r1, #4
0800320e: 0b68         ldr       r3, [r1]
08003210: 6ff08072     mvn       r2, #0x1000000
08003214: 8240         lsls      r2, r0
08003216: 63f31702     bfi       r2, r3, #0, #0x18
0800321a: 0a60         str       r2, [r1]
0800321c: fff7b6fb     bl        #0x800298c
08003220: 1d49         ldr       r1, [pc, #0x74]
08003222: 0028         cmp       r0, #0
08003224: 0860         str       r0, [r1]
08003226: 0cdb         blt       #0x8003242
08003228: 1c49         ldr       r1, [pc, #0x70]
0800322a: 4554         strb      r5, [r0, r1]
0800322c: 00f01f02     and       r2, r0, #0x1f
08003230: 0121         movs      r1, #1
08003232: 9140         lsls      r1, r2
08003234: 4011         asrs      r0, r0, #5
08003236: 4ff0e022     mov.w     r2, #-0x1fff2000
0800323a: 02eb8000     add.w     r0, r2, r0, lsl #2
0800323e: c0f80011     str.w     r1, [r0, #0x100]
08003242: 3246         mov       r2, r6
08003244: 4146         mov       r1, r8
08003246: 4846         mov       r0, sb
08003248: bde8f047     pop.w     {r4, r5, r6, r7, r8, sb, sl, lr}
0800324c: 0023         movs      r3, #0
0800324e: 00f065b8     b.w       #0x800331c
08003252: 0000         movs      r0, r0
08003254: dc0e         lsrs      r4, r3, #0x1b
08003256: 0020         movs      r0, #0
08003258: bc3e         subs      r6, #0xbc
0800325a: 0008         lsrs      r0, r0, #0x20
0800325c: d43e         subs      r6, #0xd4
0800325e: 0008         lsrs      r0, r0, #0x20
08003260: 680b         lsrs      r0, r5, #0xd
08003262: 0020         movs      r0, #0
08003264: c03e         subs      r6, #0xc0
08003266: 0008         lsrs      r0, r0, #0x20
08003268: d83e         subs      r6, #0xd8
0800326a: 0008         lsrs      r0, r0, #0x20
0800326c: 380c         lsrs      r0, r7, #0x10
0800326e: 0020         movs      r0, #0
08003270: de3e         subs      r6, #0xde
08003272: 0008         lsrs      r0, r0, #0x20
08003274: 6000         lsls      r0, r4, #1
08003276: 0020         movs      r0, #0
08003278: ec0e         lsrs      r4, r5, #0x1b
0800327a: 0020         movs      r0, #0
0800327c: 8b29         cmp       r1, #0x8b
0800327e: 0008         lsrs      r0, r0, #0x20
08003280: 1c0f         lsrs      r4, r3, #0x1c
08003282: 0020         movs      r0, #0
08003284: 340f         lsrs      r4, r6, #0x1c
08003286: 0020         movs      r0, #0
08003288: 8000         lsls      r0, r0, #2
0800328a: 0020         movs      r0, #0
0800328c: d80d         lsrs      r0, r3, #0x17
0800328e: 0020         movs      r0, #0
08003290: dc3e         subs      r6, #0xdc
08003292: 0008         lsrs      r0, r0, #0x20
08003294: 20ed00e0     stc       p0, c14, [r0, #-0]!
08003298: 9400         lsls      r4, r2, #2
0800329a: 0020         movs      r0, #0
0800329c: 00e4         b         #0x8002aa0
0800329e: 00e0         b         #0x80032a2
080032a0: 0b48         ldr       r0, [pc, #0x2c]
080032a2: 10b5         push      {r4, lr}
080032a4: 0068         ldr       r0, [r0]
080032a6: 0121         movs      r1, #1
080032a8: 4170         strb      r1, [r0, #1]
080032aa: fff7bdfe     bl        #0x8003028
080032ae: fff7adfb     bl        #0x8002a0c
080032b2: 0848         ldr       r0, [pc, #0x20]
080032b4: 0168         ldr       r1, [r0]
080032b6: 491c         adds      r1, r1, #1
080032b8: 0160         str       r1, [r0]
080032ba: fff7a9fb     bl        #0x8002a10
080032be: 00f00df8     bl        #0x80032dc
080032c2: 0548         ldr       r0, [pc, #0x14]
080032c4: fff78efc     bl        #0x8002be4
080032c8: bde81040     pop.w     {r4, lr}
080032cc: fff728bf     b.w       #0x8003120
080032d0: 8000         lsls      r0, r0, #2
080032d2: 0020         movs      r0, #0
080032d4: 8800         lsls      r0, r1, #2
080032d6: 0020         movs      r0, #0
080032d8: 1c0f         lsrs      r4, r3, #0x1c
080032da: 0020         movs      r0, #0
080032dc: 70b5         push      {r4, r5, r6, lr}
080032de: 0d4c         ldr       r4, [pc, #0x34]
080032e0: 2068         ldr       r0, [r4]
080032e2: 0028         cmp       r0, #0
080032e4: 15d0         beq       #0x8003312
080032e6: a088         ldrh      r0, [r4, #4]
080032e8: 0b4e         ldr       r6, [pc, #0x2c]
080032ea: 401e         subs      r0, r0, #1
080032ec: a080         strh      r0, [r4, #4]
080032ee: 0ae0         b         #0x8003306
080032f0: e888         ldrh      r0, [r5, #6]
080032f2: fff760fb     bl        #0x80029b6
080032f6: a888         ldrh      r0, [r5, #4]
080032f8: a080         strh      r0, [r4, #4]
080032fa: 2868         ldr       r0, [r5]
080032fc: 2060         str       r0, [r4]
080032fe: 2946         mov       r1, r5
08003300: 3068         ldr       r0, [r6]
08003302: fff75ffc     bl        #0x8002bc4
08003306: a088         ldrh      r0, [r4, #4]
08003308: 0028         cmp       r0, #0
0800330a: 02d1         bne       #0x8003312
0800330c: 2568         ldr       r5, [r4]
0800330e: 002d         cmp       r5, #0
08003310: eed1         bne       #0x80032f0
08003312: 70bd         pop       {r4, r5, r6, pc}
08003314: 9800         lsls      r0, r3, #2
08003316: 0020         movs      r0, #0
08003318: 6000         lsls      r0, r4, #1
0800331a: 0020         movs      r0, #0
0800331c: 2de9f041     push.w    {r4, r5, r6, r7, r8, lr}
08003320: 1e46         mov       r6, r3
08003322: 1746         mov       r7, r2
08003324: 8046         mov       r8, r0
08003326: 0c46         mov       r4, r1
08003328: 11f0ff0f     tst.w     r1, #0xff
0800332c: 00d1         bne       #0x8003330
0800332e: 4c1c         adds      r4, r1, #1
08003330: 1a48         ldr       r0, [pc, #0x68]
08003332: fff741fb     bl        #0x80029b8
08003336: 0500         movs      r5, r0
08003338: 2dd0         beq       #0x8003396
0800333a: c4f30f20     ubfx      r0, r4, #8, #0x10
0800333e: af62         str       r7, [r5, #0x28]
08003340: 6884         strh      r0, [r5, #0x22]
08003342: e1b2         uxtb      r1, r4
08003344: 4246         mov       r2, r8
08003346: 2846         mov       r0, r5
08003348: ee61         str       r6, [r5, #0x1c]
0800334a: fff75ffc     bl        #0x8002c0c
0800334e: 0124         movs      r4, #1
08003350: 1348         ldr       r0, [pc, #0x4c]
08003352: 1449         ldr       r1, [pc, #0x50]
08003354: 06e0         b         #0x8003364
08003356: 00bf         nop       
08003358: 00eb8402     add.w     r2, r0, r4, lsl #2
0800335c: 52f8042c     ldr       r2, [r2, #-0x4]
08003360: 22b1         cbz       r2, #0x800336c
08003362: 641c         adds      r4, r4, #1
08003364: 0a88         ldrh      r2, [r1]
08003366: 9442         cmp       r4, r2
08003368: f6d9         bls       #0x8003358
0800336a: 0024         movs      r4, #0
0800336c: 00eb8400     add.w     r0, r0, r4, lsl #2
08003370: e6b2         uxtb      r6, r4
08003372: 40f8045c     str       r5, [r0, #-0x4]
08003376: 0c48         ldr       r0, [pc, #0x30]
08003378: ee70         strb      r6, [r5, #3]
0800337a: 0078         ldrb      r0, [r0]
0800337c: 18b1         cbz       r0, #0x8003386
0800337e: 0121         movs      r1, #1
08003380: 2846         mov       r0, r5
08003382: fff795f8     bl        #0x80024b0
08003386: 2846         mov       r0, r5
08003388: fff77cfb     bl        #0x8002a84
0800338c: 0748         ldr       r0, [pc, #0x1c]
0800338e: 0068         ldr       r0, [r0]
08003390: 80f82060     strb.w    r6, [r0, #0x20]
08003394: 2046         mov       r0, r4
08003396: bde8f081     pop.w     {r4, r5, r6, r7, r8, pc}
0800339a: 0000         movs      r0, r0
0800339c: 680b         lsrs      r0, r5, #0xd
0800339e: 0020         movs      r0, #0
080033a0: dc0e         lsrs      r4, r3, #0x1b
080033a2: 0020         movs      r0, #0
080033a4: bc3e         subs      r6, #0xbc
080033a6: 0008         lsrs      r0, r0, #0x20
080033a8: 8c00         lsls      r4, r1, #2
080033aa: 0020         movs      r0, #0
080033ac: 8000         lsls      r0, r0, #2
080033ae: 0020         movs      r0, #0
080033b0: 2de9f041     push.w    {r4, r5, r6, r7, r8, lr}
080033b4: 284c         ldr       r4, [pc, #0xa0]
080033b6: 274f         ldr       r7, [pc, #0x9c]
080033b8: 284e         ldr       r6, [pc, #0xa0]
080033ba: 2168         ldr       r1, [r4]
080033bc: 0025         movs      r5, #0
080033be: 10b1         cbz       r0, #0x80033c6
080033c0: ca78         ldrb      r2, [r1, #3]
080033c2: 8242         cmp       r2, r0
080033c4: 20d1         bne       #0x8003408
080033c6: 4d70         strb      r5, [r1, #1]
080033c8: fcf7fdfe     bl        #0x80001c6
080033cc: 2168         ldr       r1, [r4]
080033ce: 4862         str       r0, [r1, #0x24]
080033d0: fff794fe     bl        #0x80030fc
080033d4: 2068         ldr       r0, [r4]
080033d6: c178         ldrb      r1, [r0, #3]
080033d8: 06eb8101     add.w     r1, r6, r1, lsl #2
080033dc: 41f8045c     str       r5, [r1, #-0x4]
080033e0: 816a         ldr       r1, [r0, #0x28]
080033e2: 1f48         ldr       r0, [pc, #0x7c]
080033e4: fff7eefb     bl        #0x8002bc4
080033e8: 2068         ldr       r0, [r4]
080033ea: 8562         str       r5, [r0, #0x28]
080033ec: 3978         ldrb      r1, [r7]
080033ee: 11b1         cbz       r1, #0x80033f6
080033f0: 0021         movs      r1, #0
080033f2: fff75df8     bl        #0x80024b0
080033f6: 1b48         ldr       r0, [pc, #0x6c]
080033f8: 2168         ldr       r1, [r4]
080033fa: fff7e3fb     bl        #0x8002bc4
080033fe: 0020         movs      r0, #0
08003400: 2560         str       r5, [r4]
08003402: fff73ffb     bl        #0x8002a84
08003406: 1fe0         b         #0x8003448
08003408: 1749         ldr       r1, [pc, #0x5c]
0800340a: 0988         ldrh      r1, [r1]
0800340c: 8842         cmp       r0, r1
0800340e: 1ed8         bhi       #0x800344e
08003410: 06eb8006     add.w     r6, r6, r0, lsl #2
08003414: 56f8044c     ldr       r4, [r6, #-0x4]
08003418: ccb1         cbz       r4, #0x800344e
0800341a: 2046         mov       r0, r4
0800341c: fff73cfe     bl        #0x8003098
08003420: 2046         mov       r0, r4
08003422: fff725fe     bl        #0x8003070
08003426: 46f8045c     str       r5, [r6, #-0x4]
0800342a: 0d48         ldr       r0, [pc, #0x34]
0800342c: a16a         ldr       r1, [r4, #0x28]
0800342e: fff7c9fb     bl        #0x8002bc4
08003432: a562         str       r5, [r4, #0x28]
08003434: 3878         ldrb      r0, [r7]
08003436: 18b1         cbz       r0, #0x8003440
08003438: 0021         movs      r1, #0
0800343a: 2046         mov       r0, r4
0800343c: fff738f8     bl        #0x80024b0
08003440: 2146         mov       r1, r4
08003442: 0848         ldr       r0, [pc, #0x20]
08003444: fff7befb     bl        #0x8002bc4
08003448: 0020         movs      r0, #0
0800344a: bde8f081     pop.w     {r4, r5, r6, r7, r8, pc}
0800344e: ff20         movs      r0, #0xff
08003450: fbe7         b         #0x800344a
08003452: 0000         movs      r0, r0
08003454: 8c00         lsls      r4, r1, #2
08003456: 0020         movs      r0, #0
08003458: 8000         lsls      r0, r0, #2
0800345a: 0020         movs      r0, #0
0800345c: dc0e         lsrs      r4, r3, #0x1b
0800345e: 0020         movs      r0, #0
08003460: 380c         lsrs      r0, r7, #0x10
08003462: 0020         movs      r0, #0
08003464: 680b         lsrs      r0, r5, #0xd
08003466: 0020         movs      r0, #0
08003468: bc3e         subs      r6, #0xbc
0800346a: 0008         lsrs      r0, r0, #0x20
0800346c: 0248         ldr       r0, [pc, #8]
0800346e: 0068         ldr       r0, [r0]
08003470: 0028         cmp       r0, #0
08003472: 00d0         beq       #0x8003476
08003474: c078         ldrb      r0, [r0, #3]
08003476: 7047         bx        lr
08003478: 8000         lsls      r0, r0, #2
0800347a: 0020         movs      r0, #0
0800347c: 10b5         push      {r4, lr}
0800347e: 0446         mov       r4, r0
08003480: 806c         ldr       r0, [r0, #0x48]
08003482: 40f22771     movw      r1, #0x727
08003486: fdf7befe     bl        #0x8001206
0800348a: 0028         cmp       r0, #0
0800348c: 08bf         it        eq
0800348e: 10bd         popeq     {r4, pc}
08003490: 6068         ldr       r0, [r4, #4]
08003492: 2168         ldr       r1, [r4]
08003494: 8842         cmp       r0, r1
08003496: 0fd0         beq       #0x80034b8
08003498: 6168         ldr       r1, [r4, #4]
0800349a: 04f10800     add.w     r0, r4, #8
0800349e: 095c         ldrb      r1, [r1, r0]
080034a0: 6068         ldr       r0, [r4, #4]
080034a2: 3f28         cmp       r0, #0x3f
080034a4: aebf         itee      ge
080034a6: 0020         movge     r0, #0
080034a8: 6068         ldrlt     r0, [r4, #4]
080034aa: 401c         addlt     r0, r0, #1
080034ac: 6060         str       r0, [r4, #4]
080034ae: a06c         ldr       r0, [r4, #0x48]
080034b0: bde81040     pop.w     {r4, lr}
080034b4: fdf73ebf     b.w       #0x8001334
080034b8: a06c         ldr       r0, [r4, #0x48]
080034ba: bde81040     pop.w     {r4, lr}
080034be: 0022         movs      r2, #0
080034c0: 40f22771     movw      r1, #0x727
080034c4: fdf7c0be     b.w       #0x8001248
080034c8: 427e         ldrb      r2, [r0, #0x19]
080034ca: 00eb4200     add.w     r0, r0, r2, lsl #1
080034ce: 408b         ldrh      r0, [r0, #0x1a]
080034d0: c840         lsrs      r0, r1
080034d2: 00f00100     and       r0, r0, #1
080034d6: 7047         bx        lr
080034d8: 7047         bx        lr
080034da: 7047         bx        lr
080034dc: 00eb4100     add.w     r0, r0, r1, lsl #1
080034e0: 408b         ldrh      r0, [r0, #0x1a]
080034e2: 7047         bx        lr
080034e4: 00eb4200     add.w     r0, r0, r2, lsl #1
080034e8: 4183         strh      r1, [r0, #0x1a]
080034ea: 7047         bx        lr
080034ec: 427e         ldrb      r2, [r0, #0x19]
080034ee: 00eb4200     add.w     r0, r0, r2, lsl #1
080034f2: 408b         ldrh      r0, [r0, #0x1a]
080034f4: c840         lsrs      r0, r1
080034f6: 00f00100     and       r0, r0, #1
080034fa: 7047         bx        lr
080034fc: 10b5         push      {r4, lr}
080034fe: 0446         mov       r4, r0
08003500: 4069         ldr       r0, [r0, #0x14]
08003502: 0028         cmp       r0, #0
08003504: 08bf         it        eq
08003506: 10bd         popeq     {r4, pc}
08003508: 227e         ldrb      r2, [r4, #0x18]
0800350a: 0421         movs      r1, #4
0800350c: 01ebc201     add.w     r1, r1, r2, lsl #3
08003510: 415a         ldrh      r1, [r0, r1]
08003512: 50f83200     ldr.w     r0, [r0, r2, lsl #3]
08003516: 89b2         uxth      r1, r1
08003518: fdf7a8f9     bl        #0x800086c
0800351c: 607e         ldrb      r0, [r4, #0x19]
0800351e: 2076         strb      r0, [r4, #0x18]
08003520: 401c         adds      r0, r0, #1
08003522: c0b2         uxtb      r0, r0
08003524: 6076         strb      r0, [r4, #0x19]
08003526: 0428         cmp       r0, #4
08003528: 24bf         itt       hs
0800352a: 0020         movhs     r0, #0
0800352c: 6076         strbhs    r0, [r4, #0x19]
0800352e: 10bd         pop       {r4, pc}
08003530: 4269         ldr       r2, [r0, #0x14]
08003532: 002a         cmp       r2, #0
08003534: 08bf         it        eq
08003536: 7047         bxeq      lr
08003538: 007e         ldrb      r0, [r0, #0x18]
0800353a: 0421         movs      r1, #4
0800353c: 01ebc001     add.w     r1, r1, r0, lsl #3
08003540: 515a         ldrh      r1, [r2, r1]
08003542: 52f83000     ldr.w     r0, [r2, r0, lsl #3]
08003546: 89b2         uxth      r1, r1
08003548: fdf792b9     b.w       #0x8000870
0800354c: 00eb4100     add.w     r0, r0, r1, lsl #1
08003550: 408b         ldrh      r0, [r0, #0x1a]
08003552: 7047         bx        lr
08003554: 00eb4200     add.w     r0, r0, r2, lsl #1
08003558: 4183         strh      r1, [r0, #0x1a]
0800355a: 7047         bx        lr
0800355c: 10b4         push      {r4}
0800355e: dff854c0     ldr.w     ip, [pc, #0x54]
08003562: c0e900c2     strd      ip, r2, [r0]
08003566: 0122         movs      r2, #1
08003568: 0272         strb      r2, [r0, #8]
0800356a: 4ff0000c     mov.w     ip, #0
0800356e: 80f809c0     strb.w    ip, [r0, #9]
08003572: c0f80cc0     str.w     ip, [r0, #0xc]
08003576: c0f810c0     str.w     ip, [r0, #0x10]
0800357a: 4a68         ldr       r2, [r1, #4]
0800357c: b2b1         cbz       r2, #0x80035ac
0800357e: d168         ldr       r1, [r2, #0xc]
08003580: c0e90312     strd      r1, r2, [r0, #0xc]
08003584: d060         str       r0, [r2, #0xc]
08003586: 0861         str       r0, [r1, #0x10]
08003588: 0b49         ldr       r1, [pc, #0x2c]
0800358a: 4361         str       r3, [r0, #0x14]
0800358c: 0160         str       r1, [r0]
0800358e: 80f818c0     strb.w    ip, [r0, #0x18]
08003592: 80f819c0     strb.w    ip, [r0, #0x19]
08003596: 0021         movs      r1, #0
08003598: 4ff6ff72     movw      r2, #0xffff
0800359c: 00eb4103     add.w     r3, r0, r1, lsl #1
080035a0: 491c         adds      r1, r1, #1
080035a2: 5a83         strh      r2, [r3, #0x1a]
080035a4: 0429         cmp       r1, #4
080035a6: f9d3         blo       #0x800359c
080035a8: 10bc         pop       {r4}
080035aa: 7047         bx        lr
080035ac: c060         str       r0, [r0, #0xc]
080035ae: 0061         str       r0, [r0, #0x10]
080035b0: 4860         str       r0, [r1, #4]
080035b2: e9e7         b         #0x8003588
080035b4: e83e         subs      r6, #0xe8
080035b6: 0008         lsrs      r0, r0, #0x20
080035b8: 203f         subs      r7, #0x20
080035ba: 0008         lsrs      r0, r0, #0x20
080035bc: 2de9f047     push.w    {r4, r5, r6, r7, r8, sb, sl, lr}
080035c0: 0446         mov       r4, r0
080035c2: 0025         movs      r5, #0
080035c4: 407c         ldrb      r0, [r0, #0x11]
080035c6: 0426         movs      r6, #4
080035c8: 2f46         mov       r7, r5
080035ca: 0028         cmp       r0, #0
080035cc: 88bf         it        hi
080035ce: 4ff00108     movhi.w   r8, #1
080035d2: 33d9         bls       #0x800363c
080035d4: e068         ldr       r0, [r4, #0xc]
080035d6: 06ebc501     add.w     r1, r6, r5, lsl #3
080035da: 415a         ldrh      r1, [r0, r1]
080035dc: 50f83500     ldr.w     r0, [r0, r5, lsl #3]
080035e0: 89b2         uxth      r1, r1
080035e2: fdf735f9     bl        #0x8000850
080035e6: 0028         cmp       r0, #0
080035e8: 14bf         ite       ne
080035ea: 0121         movne     r1, #1
080035ec: 0021         moveq     r1, #0
080035ee: a07c         ldrb      r0, [r4, #0x12]
080035f0: 627c         ldrb      r2, [r4, #0x11]
080035f2: 00fb0252     mla       r2, r0, r2, r5
080035f6: 04eb020c     add.w     ip, r4, r2
080035fa: 9cf81300     ldrb.w    r0, [ip, #0x13]
080035fe: 8842         cmp       r0, r1
08003600: 04eb8200     add.w     r0, r4, r2, lsl #2
08003604: 08bf         it        eq
08003606: 8763         streq     r7, [r0, #0x38]
08003608: 14d0         beq       #0x8003634
0800360a: 836b         ldr       r3, [r0, #0x38]
0800360c: 48ea4303     orr.w     r3, r8, r3, lsl #1
08003610: 8363         str       r3, [r0, #0x38]
08003612: 0f20         movs      r0, #0xf
08003614: 23fa00f9     lsr.w     sb, r3, r0
08003618: 19f0010f     tst.w     sb, #1
0800361c: 08bf         it        eq
0800361e: bde8f087     popeq.w   {r4, r5, r6, r7, r8, sb, sl, pc}
08003622: 401e         subs      r0, r0, #1
08003624: f6d5         bpl       #0x8003614
08003626: 8cf81310     strb.w    r1, [ip, #0x13]
0800362a: 2368         ldr       r3, [r4]
0800362c: 13b1         cbz       r3, #0x8003634
0800362e: 2079         ldrb      r0, [r4, #4]
08003630: 1044         add       r0, r2
08003632: 9847         blx       r3
08003634: 607c         ldrb      r0, [r4, #0x11]
08003636: 6d1c         adds      r5, r5, #1
08003638: a842         cmp       r0, r5
0800363a: cbd8         bhi       #0x80035d4
0800363c: a27c         ldrb      r2, [r4, #0x12]
0800363e: a068         ldr       r0, [r4, #8]
08003640: 06ebc201     add.w     r1, r6, r2, lsl #3
08003644: 415a         ldrh      r1, [r0, r1]
08003646: 50f83200     ldr.w     r0, [r0, r2, lsl #3]
0800364a: 89b2         uxth      r1, r1
0800364c: fdf710f9     bl        #0x8000870
08003650: a07c         ldrb      r0, [r4, #0x12]
08003652: 401c         adds      r0, r0, #1
08003654: c0b2         uxtb      r0, r0
08003656: a074         strb      r0, [r4, #0x12]
08003658: 217c         ldrb      r1, [r4, #0x10]
0800365a: 8842         cmp       r0, r1
0800365c: 28bf         it        hs
0800365e: a774         strbhs    r7, [r4, #0x12]
08003660: a27c         ldrb      r2, [r4, #0x12]
08003662: a068         ldr       r0, [r4, #8]
08003664: 06ebc201     add.w     r1, r6, r2, lsl #3
08003668: 415a         ldrh      r1, [r0, r1]
0800366a: 50f83200     ldr.w     r0, [r0, r2, lsl #3]
0800366e: bde8f047     pop.w     {r4, r5, r6, r7, r8, sb, sl, lr}
08003672: 89b2         uxth      r1, r1
08003674: fdf7fab8     b.w       #0x800086c
08003678: 70b5         push      {r4, r5, r6, lr}
0800367a: 0446         mov       r4, r0
0800367c: dde9040c     ldrd      r0, ip, [sp, #0x10]
08003680: 2171         strb      r1, [r4, #4]
08003682: c4e90223     strd      r2, r3, [r4, #8]
08003686: 2074         strb      r0, [r4, #0x10]
08003688: 0020         movs      r0, #0
0800368a: 84f811c0     strb.w    ip, [r4, #0x11]
0800368e: a074         strb      r0, [r4, #0x12]
08003690: 0121         movs      r1, #1
08003692: 2218         adds      r2, r4, r0
08003694: d174         strb      r1, [r2, #0x13]
08003696: 04eb8002     add.w     r2, r4, r0, lsl #2
0800369a: 401c         adds      r0, r0, #1
0800369c: 9163         str       r1, [r2, #0x38]
0800369e: 2428         cmp       r0, #0x24
080036a0: f7d3         blo       #0x8003692
080036a2: 207c         ldrb      r0, [r4, #0x10]
080036a4: 0025         movs      r5, #0
080036a6: 0028         cmp       r0, #0
080036a8: 88bf         it        hi
080036aa: 0426         movhi     r6, #4
080036ac: 0cd9         bls       #0x80036c8
080036ae: a068         ldr       r0, [r4, #8]
080036b0: 06ebc501     add.w     r1, r6, r5, lsl #3
080036b4: 415a         ldrh      r1, [r0, r1]
080036b6: 50f83500     ldr.w     r0, [r0, r5, lsl #3]
080036ba: 89b2         uxth      r1, r1
080036bc: fdf7d8f8     bl        #0x8000870
080036c0: 207c         ldrb      r0, [r4, #0x10]
080036c2: 6d1c         adds      r5, r5, #1
080036c4: a842         cmp       r0, r5
080036c6: f2d8         bhi       #0x80036ae
080036c8: 2046         mov       r0, r4
080036ca: 70bd         pop       {r4, r5, r6, pc}
080036cc: 82b0         sub       sp, #8
080036ce: 61f3070c     bfi       ip, r1, #0, #8
080036d2: 62f30f2c     bfi       ip, r2, #8, #8
080036d6: cdf800c0     str.w     ip, [sp]
080036da: 0168         ldr       r1, [r0]
080036dc: 4268         ldr       r2, [r0, #4]
080036de: 891a         subs      r1, r1, r2
080036e0: 0029         cmp       r1, #0
080036e2: b8bf         it        lt
080036e4: 2031         addlt     r1, #0x20
080036e6: 09b2         sxth      r1, r1
080036e8: c1f11f01     rsb.w     r1, r1, #0x1f
080036ec: 09b2         sxth      r1, r1
080036ee: 0029         cmp       r1, #0
080036f0: 04bf         itt       eq
080036f2: 02b0         addeq     sp, #8
080036f4: 7047         bxeq      lr
080036f6: 0268         ldr       r2, [r0]
080036f8: 00eb4201     add.w     r1, r0, r2, lsl #1
080036fc: bdf80020     ldrh.w    r2, [sp]
08003700: 0a81         strh      r2, [r1, #8]
08003702: 0168         ldr       r1, [r0]
08003704: 1f29         cmp       r1, #0x1f
08003706: aebf         itee      ge
08003708: 0021         movge     r1, #0
0800370a: 0168         ldrlt     r1, [r0]
0800370c: 491c         addlt     r1, r1, #1
0800370e: 0246         mov       r2, r0
08003710: 0160         str       r1, [r0]
08003712: 816c         ldr       r1, [r0, #0x48]
08003714: 4bb1         cbz       r3, #0x800372a
08003716: 0029         cmp       r1, #0
08003718: 19bf         ittee     ne
0800371a: b2f84c00     ldrhne.w  r0, [r2, #0x4c]
0800371e: 0028         cmpne     r0, #0
08003720: 02b0         addeq     sp, #8
08003722: 7047         bxeq      lr
08003724: 02b0         add       sp, #8
08003726: fff7f1b8     b.w       #0x800290c
0800372a: 0029         cmp       r1, #0
0800372c: 19bf         ittee     ne
0800372e: b2f84c00     ldrhne.w  r0, [r2, #0x4c]
08003732: 0028         cmpne     r0, #0
08003734: 02b0         addeq     sp, #8
08003736: 7047         bxeq      lr
08003738: dff808c0     ldr.w     ip, [pc, #8]
0800373c: 00df         svc       #0
0800373e: 02b0         add       sp, #8
08003740: 7047         bx        lr
08003742: 0000         movs      r0, r0
08003744: 292b         cmp       r3, #0x29
08003746: 0008         lsrs      r0, r0, #0x20
08003748: 82b0         sub       sp, #8
0800374a: 61f3070c     bfi       ip, r1, #0, #8
0800374e: 62f30f2c     bfi       ip, r2, #8, #8
08003752: cdf800c0     str.w     ip, [sp]
08003756: 0168         ldr       r1, [r0]
08003758: 4268         ldr       r2, [r0, #4]
0800375a: 891a         subs      r1, r1, r2
0800375c: 0029         cmp       r1, #0
0800375e: b8bf         it        lt
08003760: 4031         addlt     r1, #0x40
08003762: 09b2         sxth      r1, r1
08003764: c1f13f01     rsb.w     r1, r1, #0x3f
08003768: 09b2         sxth      r1, r1
0800376a: 0029         cmp       r1, #0
0800376c: 04bf         itt       eq
0800376e: 02b0         addeq     sp, #8
08003770: 7047         bxeq      lr
08003772: 0268         ldr       r2, [r0]
08003774: 00eb4201     add.w     r1, r0, r2, lsl #1
08003778: bdf80020     ldrh.w    r2, [sp]
0800377c: 0a81         strh      r2, [r1, #8]
0800377e: 0168         ldr       r1, [r0]
08003780: 3f29         cmp       r1, #0x3f
08003782: aebf         itee      ge
08003784: 0021         movge     r1, #0
08003786: 0168         ldrlt     r1, [r0]
08003788: 491c         addlt     r1, r1, #1
0800378a: 0246         mov       r2, r0
0800378c: 0160         str       r1, [r0]
0800378e: d0f88810     ldr.w     r1, [r0, #0x88]
08003792: 4bb1         cbz       r3, #0x80037a8
08003794: 0029         cmp       r1, #0
08003796: 19bf         ittee     ne
08003798: b2f88c00     ldrhne.w  r0, [r2, #0x8c]
0800379c: 0028         cmpne     r0, #0
0800379e: 02b0         addeq     sp, #8
080037a0: 7047         bxeq      lr
080037a2: 02b0         add       sp, #8
080037a4: fff7b2b8     b.w       #0x800290c
080037a8: 0029         cmp       r1, #0
080037aa: 19bf         ittee     ne
080037ac: b2f88c00     ldrhne.w  r0, [r2, #0x8c]
080037b0: 0028         cmpne     r0, #0
080037b2: 02b0         addeq     sp, #8
080037b4: 7047         bxeq      lr
080037b6: dff808c0     ldr.w     ip, [pc, #8]
080037ba: 00df         svc       #0
080037bc: 02b0         add       sp, #8
080037be: 7047         bx        lr
080037c0: 292b         cmp       r3, #0x29
080037c2: 0008         lsrs      r0, r0, #0x20
080037c4: 0018         adds      r0, r0, r0
080037c6: 0140         ands      r1, r0
080037c8: 1000         movs      r0, r2
080037ca: 0000         movs      r0, r0
080037cc: 0018         adds      r0, r0, r0
080037ce: 0140         ands      r1, r0
080037d0: 2000         movs      r0, r4
080037d2: 0000         movs      r0, r0
080037d4: 0018         adds      r0, r0, r0
080037d6: 0140         ands      r1, r0
080037d8: 4000         lsls      r0, r0, #1
080037da: 0000         movs      r0, r0
080037dc: 0024         movs      r4, #0
080037de: 0140         ands      r1, r0
080037e0: 0000         movs      r0, r0
080037e2: 0000         movs      r0, r0
080037e4: 0024         movs      r4, #0
080037e6: 0140         ands      r1, r0
080037e8: 0100         movs      r1, r0
080037ea: 0000         movs      r0, r0
080037ec: 0024         movs      r4, #0
080037ee: 0140         ands      r1, r0
080037f0: 0200         movs      r2, r0
080037f2: 0000         movs      r0, r0
080037f4: 0024         movs      r4, #0
080037f6: 0140         ands      r1, r0
080037f8: 0300         movs      r3, r0
080037fa: 0000         movs      r0, r0
080037fc: 000c         lsrs      r0, r0, #0x10
080037fe: 0140         ands      r1, r0
08003800: 0200         movs      r2, r0
08003802: 0000         movs      r0, r0
08003804: 000c         lsrs      r0, r0, #0x10
08003806: 0140         ands      r1, r0
08003808: 0100         movs      r1, r0
0800380a: 0000         movs      r0, r0
0800380c: 0008         lsrs      r0, r0, #0x20
0800380e: 0140         ands      r1, r0
08003810: 8000         lsls      r0, r0, #2
08003812: 0000         movs      r0, r0
08003814: 0008         lsrs      r0, r0, #0x20
08003816: 0140         ands      r1, r0
08003818: 4000         lsls      r0, r0, #1
0800381a: 0000         movs      r0, r0
0800381c: 0008         lsrs      r0, r0, #0x20
0800381e: 0140         ands      r1, r0
08003820: 2000         movs      r0, r4
08003822: 0000         movs      r0, r0
08003824: 0008         lsrs      r0, r0, #0x20
08003826: 0140         ands      r1, r0
08003828: 1000         movs      r0, r2
0800382a: 0000         movs      r0, r0
0800382c: 0010         asrs      r0, r0, #0x20
0800382e: 0140         ands      r1, r0
08003830: 0100         movs      r1, r0
08003832: 0000         movs      r0, r0
08003834: 0010         asrs      r0, r0, #0x20
08003836: 0140         ands      r1, r0
08003838: 0200         movs      r2, r0
0800383a: 0000         movs      r0, r0
0800383c: 0010         asrs      r0, r0, #0x20
0800383e: 0140         ands      r1, r0
08003840: 0400         movs      r4, r0
08003842: 0000         movs      r0, r0
08003844: 0010         asrs      r0, r0, #0x20
08003846: 0140         ands      r1, r0
08003848: 0800         movs      r0, r1
0800384a: 0000         movs      r0, r0
0800384c: 0010         asrs      r0, r0, #0x20
0800384e: 0140         ands      r1, r0
08003850: 0001         lsls      r0, r0, #4
08003852: 0000         movs      r0, r0
08003854: 0010         asrs      r0, r0, #0x20
08003856: 0140         ands      r1, r0
08003858: 0002         lsls      r0, r0, #8
0800385a: 0000         movs      r0, r0
0800385c: 0010         asrs      r0, r0, #0x20
0800385e: 0140         ands      r1, r0
08003860: 4000         lsls      r0, r0, #1
08003862: 0000         movs      r0, r0
08003864: 0010         asrs      r0, r0, #0x20
08003866: 0140         ands      r1, r0
08003868: 8000         lsls      r0, r0, #2
0800386a: 0000         movs      r0, r0
0800386c: 0018         adds      r0, r0, r0
0800386e: 0140         ands      r1, r0
08003870: 0040         ands      r0, r0
08003872: 0000         movs      r0, r0
08003874: 0018         adds      r0, r0, r0
08003876: 0140         ands      r1, r0
08003878: 0020         movs      r0, #0
0800387a: 0000         movs      r0, r0
0800387c: 0018         adds      r0, r0, r0
0800387e: 0140         ands      r1, r0
08003880: 0010         asrs      r0, r0, #0x20
08003882: 0000         movs      r0, r0
08003884: 0018         adds      r0, r0, r0
08003886: 0140         ands      r1, r0
08003888: 0008         lsrs      r0, r0, #0x20
0800388a: 0000         movs      r0, r0
0800388c: 0018         adds      r0, r0, r0
0800388e: 0140         ands      r1, r0
08003890: 0004         lsls      r0, r0, #0x10
08003892: 0000         movs      r0, r0
08003894: 0018         adds      r0, r0, r0
08003896: 0140         ands      r1, r0
08003898: 0002         lsls      r0, r0, #8
0800389a: 0000         movs      r0, r0
0800389c: 0018         adds      r0, r0, r0
0800389e: 0140         ands      r1, r0
080038a0: 0001         lsls      r0, r0, #4
080038a2: 0000         movs      r0, r0
080038a4: 0018         adds      r0, r0, r0
080038a6: 0140         ands      r1, r0
080038a8: 8000         lsls      r0, r0, #2
080038aa: 0000         movs      r0, r0
080038ac: 0014         asrs      r0, r0, #0x10
080038ae: 0140         ands      r1, r0
080038b0: 0080         strh      r0, [r0]
080038b2: 0000         movs      r0, r0
080038b4: 0014         asrs      r0, r0, #0x10
080038b6: 0140         ands      r1, r0
080038b8: 0040         ands      r0, r0
080038ba: 0000         movs      r0, r0
080038bc: 0014         asrs      r0, r0, #0x10
080038be: 0140         ands      r1, r0
080038c0: 0020         movs      r0, #0
080038c2: 0000         movs      r0, r0
080038c4: 0014         asrs      r0, r0, #0x10
080038c6: 0140         ands      r1, r0
080038c8: 0010         asrs      r0, r0, #0x20
080038ca: 0000         movs      r0, r0
080038cc: 0014         asrs      r0, r0, #0x10
080038ce: 0140         ands      r1, r0
080038d0: 0008         lsrs      r0, r0, #0x20
080038d2: 0000         movs      r0, r0
080038d4: 0014         asrs      r0, r0, #0x10
080038d6: 0140         ands      r1, r0
080038d8: 0004         lsls      r0, r0, #0x10
080038da: 0000         movs      r0, r0
080038dc: 0014         asrs      r0, r0, #0x10
080038de: 0140         ands      r1, r0
080038e0: 0002         lsls      r0, r0, #8
080038e2: 0000         movs      r0, r0
080038e4: 0014         asrs      r0, r0, #0x10
080038e6: 0140         ands      r1, r0
080038e8: 0001         lsls      r0, r0, #4
080038ea: 0000         movs      r0, r0
080038ec: 000c         lsrs      r0, r0, #0x10
080038ee: 0140         ands      r1, r0
080038f0: 0080         strh      r0, [r0]
080038f2: 0000         movs      r0, r0
080038f4: 000c         lsrs      r0, r0, #0x10
080038f6: 0140         ands      r1, r0
080038f8: 0040         ands      r0, r0
080038fa: 0000         movs      r0, r0
080038fc: 000c         lsrs      r0, r0, #0x10
080038fe: 0140         ands      r1, r0
08003900: 0020         movs      r0, #0
08003902: 0000         movs      r0, r0
08003904: 000c         lsrs      r0, r0, #0x10
08003906: 0140         ands      r1, r0
08003908: 0010         asrs      r0, r0, #0x20
0800390a: 0000         movs      r0, r0
0800390c: 000c         lsrs      r0, r0, #0x10
0800390e: 0140         ands      r1, r0
08003910: 0001         lsls      r0, r0, #4
08003912: 0000         movs      r0, r0
08003914: 000c         lsrs      r0, r0, #0x10
08003916: 0140         ands      r1, r0
08003918: 2000         movs      r0, r4
0800391a: 0000         movs      r0, r0
0800391c: 000c         lsrs      r0, r0, #0x10
0800391e: 0140         ands      r1, r0
08003920: 4000         lsls      r0, r0, #1
08003922: 0000         movs      r0, r0
08003924: 000c         lsrs      r0, r0, #0x10
08003926: 0140         ands      r1, r0
08003928: 8000         lsls      r0, r0, #2
0800392a: 0000         movs      r0, r0
0800392c: 0014         asrs      r0, r0, #0x10
0800392e: 0140         ands      r1, r0
08003930: 8000         lsls      r0, r0, #2
08003932: 0000         movs      r0, r0
08003934: 0014         asrs      r0, r0, #0x10
08003936: 0140         ands      r1, r0
08003938: 4000         lsls      r0, r0, #1
0800393a: 0000         movs      r0, r0
0800393c: 0014         asrs      r0, r0, #0x10
0800393e: 0140         ands      r1, r0
08003940: 2000         movs      r0, r4
08003942: 0000         movs      r0, r0
08003944: 0014         asrs      r0, r0, #0x10
08003946: 0140         ands      r1, r0
08003948: 1000         movs      r0, r2
0800394a: 0000         movs      r0, r0
0800394c: 0014         asrs      r0, r0, #0x10
0800394e: 0140         ands      r1, r0
08003950: 0800         movs      r0, r1
08003952: 0000         movs      r0, r0
08003954: 0014         asrs      r0, r0, #0x10
08003956: 0140         ands      r1, r0
08003958: 0400         movs      r4, r0
0800395a: 0000         movs      r0, r0
0800395c: 0014         asrs      r0, r0, #0x10
0800395e: 0140         ands      r1, r0
08003960: 0200         movs      r2, r0
08003962: 0000         movs      r0, r0
08003964: 0014         asrs      r0, r0, #0x10
08003966: 0140         ands      r1, r0
08003968: 0100         movs      r1, r0
0800396a: 0000         movs      r0, r0
0800396c: 0103         lsls      r1, r0, #0xc
0800396e: 0001         lsls      r0, r0, #4
08003970: 0301         lsls      r3, r0, #4
08003972: 0103         lsls      r1, r0, #0xc
08003974: 0201         lsls      r2, r0, #4
08003976: 0303         lsls      r3, r0, #0xc
08003978: 0103         lsls      r1, r0, #0xc
0800397a: 0401         lsls      r4, r0, #4
0800397c: 0305         lsls      r3, r0, #0x14
0800397e: 0103         lsls      r1, r0, #0xc
08003980: 0601         lsls      r6, r0, #4
08003982: 0307         lsls      r3, r0, #0x1c
08003984: 0102         lsls      r1, r0, #8
08003986: 0001         lsls      r0, r0, #4
08003988: 0201         lsls      r2, r0, #4
0800398a: 0102         lsls      r1, r0, #8
0800398c: 0201         lsls      r2, r0, #4
0800398e: 0203         lsls      r2, r0, #0xc
08003990: 0102         lsls      r1, r0, #8
08003992: 0401         lsls      r4, r0, #4
08003994: 0205         lsls      r2, r0, #0x14
08003996: 0102         lsls      r1, r0, #8
08003998: 0601         lsls      r6, r0, #4
0800399a: 0207         lsls      r2, r0, #0x1c
0800399c: 0101         lsls      r1, r0, #4
0800399e: 0001         lsls      r0, r0, #4
080039a0: 0101         lsls      r1, r0, #4
080039a2: 0101         lsls      r1, r0, #4
080039a4: 0201         lsls      r2, r0, #4
080039a6: 0103         lsls      r1, r0, #0xc
080039a8: 0101         lsls      r1, r0, #4
080039aa: 0401         lsls      r4, r0, #4
080039ac: 0105         lsls      r1, r0, #0x14
080039ae: 0101         lsls      r1, r0, #4
080039b0: 0601         lsls      r6, r0, #4
080039b2: 0107         lsls      r1, r0, #0x1c
080039b4: 0003         lsls      r0, r0, #0xc
080039b6: 0000         movs      r0, r0
080039b8: 0301         lsls      r3, r0, #4
080039ba: 0003         lsls      r0, r0, #0xc
080039bc: 0200         movs      r2, r0
080039be: 0303         lsls      r3, r0, #0xc
080039c0: 0003         lsls      r0, r0, #0xc
080039c2: 0400         movs      r4, r0
080039c4: 0305         lsls      r3, r0, #0x14
080039c6: 0003         lsls      r0, r0, #0xc
080039c8: 0600         movs      r6, r0
080039ca: 0307         lsls      r3, r0, #0x1c
080039cc: 0002         lsls      r0, r0, #8
080039ce: 0000         movs      r0, r0
080039d0: 0201         lsls      r2, r0, #4
080039d2: 0002         lsls      r0, r0, #8
080039d4: 0200         movs      r2, r0
080039d6: 0203         lsls      r2, r0, #0xc
080039d8: 0002         lsls      r0, r0, #8
080039da: 0400         movs      r4, r0
080039dc: 0205         lsls      r2, r0, #0x14
080039de: 0002         lsls      r0, r0, #8
080039e0: 0600         movs      r6, r0
080039e2: 0207         lsls      r2, r0, #0x1c
080039e4: 0001         lsls      r0, r0, #4
080039e6: 0000         movs      r0, r0
080039e8: 0101         lsls      r1, r0, #4
080039ea: 0001         lsls      r0, r0, #4
080039ec: 0200         movs      r2, r0
080039ee: 0103         lsls      r1, r0, #0xc
080039f0: 0001         lsls      r0, r0, #4
080039f2: 0400         movs      r4, r0
080039f4: 0105         lsls      r1, r0, #0x14
080039f6: 0001         lsls      r0, r0, #4
080039f8: 0600         movs      r6, r0
080039fa: 0107         lsls      r1, r0, #0x1c
080039fc: 0000         movs      r0, r0
080039fe: 0000         movs      r0, r0
08003a00: 0001         lsls      r0, r0, #4
08003a02: 0000         movs      r0, r0
08003a04: 0200         movs      r2, r0
08003a06: 0003         lsls      r0, r0, #0xc
08003a08: 0000         movs      r0, r0
08003a0a: 0400         movs      r4, r0
08003a0c: 0005         lsls      r0, r0, #0x14
08003a0e: 0000         movs      r0, r0
08003a10: 0600         movs      r6, r0
08003a12: 0007         lsls      r0, r0, #0x1c
08003a14: 0001         lsls      r0, r0, #4
08003a16: 0100         movs      r1, r0
08003a18: 0601         lsls      r6, r0, #4
08003a1a: 0002         lsls      r0, r0, #8
08003a1c: 0100         movs      r1, r0
08003a1e: 0701         lsls      r7, r0, #4
08003a20: 0003         lsls      r0, r0, #0xc
08003a22: 0100         movs      r1, r0
08003a24: 0401         lsls      r4, r0, #4
08003a26: 0000         movs      r0, r0
08003a28: 0100         movs      r1, r0
08003a2a: 0501         lsls      r5, r0, #4
08003a2c: 0001         lsls      r0, r0, #4
08003a2e: 0102         lsls      r1, r0, #8
08003a30: 0b01         lsls      r3, r1, #4
08003a32: 0208         lsrs      r2, r0, #0x20
08003a34: 0102         lsls      r1, r0, #8
08003a36: 0901         lsls      r1, r1, #4
08003a38: 020a         lsrs      r2, r0, #8
08003a3a: 0000         movs      r0, r0
08003a3c: 0b00         movs      r3, r1
08003a3e: 0108         lsrs      r1, r0, #0x20
08003a40: 0003         lsls      r0, r0, #0xc
08003a42: 0900         movs      r1, r1
08003a44: 020a         lsrs      r2, r0, #8
08003a46: 0002         lsls      r0, r0, #8
08003a48: 0b00         movs      r3, r1
08003a4a: 0209         lsrs      r2, r0, #4
08003a4c: 0002         lsls      r0, r0, #8
08003a4e: 0800         movs      r0, r1
08003a50: 0308         lsrs      r3, r0, #0x20
08003a52: 0101         lsls      r1, r0, #4
08003a54: 0801         lsls      r0, r1, #4
08003a56: 0009         lsrs      r0, r0, #4
08003a58: 0101         lsls      r1, r0, #4
08003a5a: 0a02         lsls      r2, r1, #8
08003a5c: 0001         lsls      r0, r0, #4
08003a5e: 0200         movs      r2, r0
08003a60: 0402         lsls      r4, r0, #8
08003a62: 0007         lsls      r0, r0, #0x1c
08003a64: 0200         movs      r2, r0
08003a66: 0a02         lsls      r2, r1, #8
08003a68: 0101         lsls      r1, r0, #4
08003a6a: 0201         lsls      r2, r0, #4
08003a6c: 0402         lsls      r4, r0, #8
08003a6e: 0107         lsls      r1, r0, #0x1c
08003a70: 0201         lsls      r2, r0, #4
08003a72: 0a01         lsls      r2, r1, #4
08003a74: 0008         lsrs      r0, r0, #0x20
08003a76: 0101         lsls      r1, r0, #4
08003a78: 0901         lsls      r1, r1, #4
08003a7a: 000a         lsrs      r0, r0, #8
08003a7c: 0200         movs      r2, r0
08003a7e: 0202         lsls      r2, r0, #8
08003a80: 0005         lsls      r0, r0, #0x14
08003a82: 0200         movs      r2, r0
08003a84: 0802         lsls      r0, r1, #8
08003a86: 000b         lsrs      r0, r0, #0xc
08003a88: 0201         lsls      r2, r0, #4
08003a8a: 0202         lsls      r2, r0, #8
08003a8c: 0105         lsls      r1, r0, #0x14
08003a8e: 0201         lsls      r2, r0, #4
08003a90: 0802         lsls      r0, r1, #8
08003a92: 010b         lsrs      r1, r0, #0xc
08003a94: 0101         lsls      r1, r0, #4
08003a96: 0b01         lsls      r3, r1, #4
08003a98: 000b         lsrs      r0, r0, #0xc
08003a9a: 0200         movs      r2, r0
08003a9c: 0002         lsls      r0, r0, #8
08003a9e: 0003         lsls      r0, r0, #0xc
08003aa0: 0200         movs      r2, r0
08003aa2: 0602         lsls      r6, r0, #8
08003aa4: 0009         lsrs      r0, r0, #4
08003aa6: 0201         lsls      r2, r0, #4
08003aa8: 0002         lsls      r0, r0, #8
08003aaa: 0103         lsls      r1, r0, #0xc
08003aac: 0201         lsls      r2, r0, #4
08003aae: 0602         lsls      r6, r0, #8
08003ab0: 0109         lsrs      r1, r0, #4
08003ab2: 0202         lsls      r2, r0, #8
08003ab4: 0002         lsls      r0, r0, #8
08003ab6: 0201         lsls      r2, r0, #4
08003ab8: 0202         lsls      r2, r0, #8
08003aba: 0202         lsls      r2, r0, #8
08003abc: 0203         lsls      r2, r0, #0xc
08003abe: 0202         lsls      r2, r0, #8
08003ac0: 0402         lsls      r4, r0, #8
08003ac2: 0205         lsls      r2, r0, #0x14
08003ac4: 0202         lsls      r2, r0, #8
08003ac6: 0602         lsls      r6, r0, #8
08003ac8: 0207         lsls      r2, r0, #0x1c
08003aca: 0202         lsls      r2, r0, #8
08003acc: 0802         lsls      r0, r1, #8
08003ace: 0209         lsrs      r2, r0, #4
08003ad0: 0202         lsls      r2, r0, #8
08003ad2: 0a02         lsls      r2, r1, #8
08003ad4: 020b         lsrs      r2, r0, #0xc
08003ad6: 0000         movs      r0, r0
08003ad8: 0a00         movs      r2, r1
08003ada: 0109         lsrs      r1, r0, #4
08003adc: 0001         lsls      r0, r0, #4
08003ade: 0a00         movs      r2, r1
08003ae0: 0009         lsrs      r0, r0, #4
08003ae2: 0001         lsls      r0, r0, #4
08003ae4: 0b00         movs      r3, r1
08003ae6: 0008         lsrs      r0, r0, #0x20
08003ae8: 0203         lsls      r2, r0, #0xc
08003aea: 0002         lsls      r0, r0, #8
08003aec: 0301         lsls      r3, r0, #4
08003aee: 0203         lsls      r2, r0, #0xc
08003af0: 0202         lsls      r2, r0, #8
08003af2: 0303         lsls      r3, r0, #0xc
08003af4: 0203         lsls      r2, r0, #0xc
08003af6: 0402         lsls      r4, r0, #8
08003af8: 0305         lsls      r3, r0, #0x14
08003afa: 0203         lsls      r2, r0, #0xc
08003afc: 0602         lsls      r6, r0, #8
08003afe: 0307         lsls      r3, r0, #0x1c
08003b00: 0203         lsls      r2, r0, #0xc
08003b02: 0802         lsls      r0, r1, #8
08003b04: 0309         lsrs      r3, r0, #4
08003b06: 0203         lsls      r2, r0, #0xc
08003b08: 0a03         lsls      r2, r1, #0xc
08003b0a: 0000         movs      r0, r0
08003b0c: 0300         movs      r3, r0
08003b0e: 0103         lsls      r1, r0, #0xc
08003b10: 0002         lsls      r0, r0, #8
08003b12: 0300         movs      r3, r0
08003b14: 0303         lsls      r3, r0, #0xc
08003b16: 0004         lsls      r0, r0, #0x10
08003b18: 0300         movs      r3, r0
08003b1a: 0503         lsls      r5, r0, #0xc
08003b1c: 0006         lsls      r0, r0, #0x18
08003b1e: 0300         movs      r3, r0
08003b20: 0703         lsls      r7, r0, #0xc
08003b22: 0008         lsrs      r0, r0, #0x20
08003b24: 0300         movs      r3, r0
08003b26: 0903         lsls      r1, r1, #0xc
08003b28: 000a         lsrs      r0, r0, #8
08003b2a: 0300         movs      r3, r0
08003b2c: 0b04         lsls      r3, r1, #0x10
08003b2e: 0000         movs      r0, r0
08003b30: 0400         movs      r4, r0
08003b32: 0104         lsls      r1, r0, #0x10
08003b34: 0002         lsls      r0, r0, #8
08003b36: 0400         movs      r4, r0
08003b38: 0304         lsls      r3, r0, #0x10
08003b3a: 0004         lsls      r0, r0, #0x10
08003b3c: 0400         movs      r4, r0
08003b3e: 0504         lsls      r5, r0, #0x10
08003b40: 0006         lsls      r0, r0, #0x18
08003b42: 0400         movs      r4, r0
08003b44: 0704         lsls      r7, r0, #0x10
08003b46: 0008         lsrs      r0, r0, #0x20
08003b48: 0400         movs      r4, r0
08003b4a: 0904         lsls      r1, r1, #0x10
08003b4c: 000a         lsrs      r0, r0, #8
08003b4e: 0400         movs      r4, r0
08003b50: 0b15         asrs      r3, r1, #0x14
08003b52: 1617         asrs      r6, r2, #0x1c
08003b54: 1811         asrs      r0, r3, #4
08003b56: 1213         asrs      r2, r2, #0xc
08003b58: 140d         lsrs      r4, r2, #0x14
08003b5a: 0e0f         lsrs      r6, r1, #0x1c
08003b5c: 1009         lsrs      r0, r2, #4
08003b5e: 0a0b         lsrs      r2, r1, #0xc
08003b60: 0c04         lsls      r4, r1, #0x10
08003b62: 0508         lsrs      r5, r0, #0x20
08003b64: 452a         cmp       r2, #0x45
08003b66: 7f02         lsls      r7, r7, #9
08003b68: 0306         lsls      r3, r0, #0x18
08003b6a: 0729         cmp       r1, #7
08003b6c: 7f00         lsls      r7, r7, #1
08003b6e: 0146         mov       r1, r0
08003b70: 4749         ldr       r1, [pc, #0x11c]
08003b72: 4826         movs      r6, #0x48
08003b74: 1b3b         subs      r3, #0x1b
08003b76: 3c3e         subs      r6, #0x3c
08003b78: 3d25         movs      r5, #0x3d
08003b7a: 1a30         adds      r0, #0x1a
08003b7c: 3133         adds      r3, #0x31
08003b7e: 3224         movs      r4, #0x32
08003b80: 193a         subs      r2, #0x19
08003b82: 2f28         cmp       r0, #0x2f
08003b84: 274e         ldr       r6, [pc, #0x9c]
08003b86: 4f36         adds      r6, #0x4f
08003b88: 3753         strh      r7, [r6, r4]
08003b8a: 7f4c         ldr       r4, [pc, #0x1fc]
08003b8c: 4d2b         cmp       r3, #0x4d
08003b8e: 2c51         str       r4, [r5, r4]
08003b90: 7f41         adcs      r7, r7
08003b92: 4223         movs      r3, #0x42
08003b94: 2044         add       r0, r4
08003b96: 434a         ldr       r2, [pc, #0x10c]
08003b98: 4b22         movs      r2, #0x4b
08003b9a: 1f39         subs      r1, #0x1f
08003b9c: 383f         subs      r7, #0x38
08003b9e: 4021         movs      r1, #0x40
08003ba0: 1e2e         cmp       r6, #0x1e
08003ba2: 2d34         adds      r4, #0x2d
08003ba4: 351d         adds      r5, r6, #4
08003ba6: 1c52         strh      r4, [r3, r0]
08003ba8: 5000         lsls      r0, r2, #1
08003baa: 0000         movs      r0, r0
08003bac: 0000         movs      r0, r0
08003bae: 0000         movs      r0, r0
08003bb0: 0000         movs      r0, r0
08003bb2: 0000         movs      r0, r0
08003bb4: 0000         movs      r0, r0
08003bb6: 0000         movs      r0, r0
08003bb8: 0000         movs      r0, r0
08003bba: 0000         movs      r0, r0
08003bbc: 0000         movs      r0, r0
08003bbe: 0000         movs      r0, r0
08003bc0: 0000         movs      r0, r0
08003bc2: 0000         movs      r0, r0
08003bc4: 0000         movs      r0, r0
08003bc6: 0000         movs      r0, r0
08003bc8: 0000         movs      r0, r0
08003bca: 0000         movs      r0, r0
08003bcc: 0000         movs      r0, r0
08003bce: 0000         movs      r0, r0
08003bd0: 0000         movs      r0, r0
08003bd2: 0000         movs      r0, r0
08003bd4: 0000         movs      r0, r0
08003bd6: 0000         movs      r0, r0
08003bd8: 0000         movs      r0, r0
08003bda: 0000         movs      r0, r0
08003bdc: 0000         movs      r0, r0
08003bde: 0000         movs      r0, r0
08003be0: 0000         movs      r0, r0
08003be2: 0000         movs      r0, r0
08003be4: 0000         movs      r0, r0
08003be6: 0000         movs      r0, r0
08003be8: 0000         movs      r0, r0
08003bea: 0000         movs      r0, r0
08003bec: 0000         movs      r0, r0
08003bee: 0000         movs      r0, r0
08003bf0: 0000         movs      r0, r0
08003bf2: 0000         movs      r0, r0
08003bf4: 0000         movs      r0, r0
08003bf6: 0000         movs      r0, r0
08003bf8: 0000         movs      r0, r0
08003bfa: 0000         movs      r0, r0
08003bfc: 0000         movs      r0, r0
08003bfe: 0000         movs      r0, r0
08003c00: 0000         movs      r0, r0
08003c02: 0000         movs      r0, r0
08003c04: 0000         movs      r0, r0
08003c06: 0000         movs      r0, r0
08003c08: 0000         movs      r0, r0
08003c0a: 0000         movs      r0, r0
08003c0c: 0000         movs      r0, r0
08003c0e: 0000         movs      r0, r0
08003c10: 0000         movs      r0, r0
08003c12: 0000         movs      r0, r0
08003c14: 0000         movs      r0, r0
08003c16: 0000         movs      r0, r0
08003c18: 0000         movs      r0, r0
08003c1a: 0000         movs      r0, r0
08003c1c: 0000         movs      r0, r0
08003c1e: 0000         movs      r0, r0
08003c20: 0000         movs      r0, r0
08003c22: 0000         movs      r0, r0
08003c24: 0000         movs      r0, r0
08003c26: 0000         movs      r0, r0
08003c28: 0000         movs      r0, r0
08003c2a: 0000         movs      r0, r0
08003c2c: 0101         lsls      r1, r0, #4
08003c2e: 0101         lsls      r1, r0, #4
08003c30: 0101         lsls      r1, r0, #4
08003c32: 0101         lsls      r1, r0, #4
08003c34: 0101         lsls      r1, r0, #4
08003c36: 0101         lsls      r1, r0, #4
08003c38: 0101         lsls      r1, r0, #4
08003c3a: 0101         lsls      r1, r0, #4
08003c3c: 0101         lsls      r1, r0, #4
08003c3e: 0101         lsls      r1, r0, #4
08003c40: 0101         lsls      r1, r0, #4
08003c42: 0101         lsls      r1, r0, #4
08003c44: 0101         lsls      r1, r0, #4
08003c46: 0101         lsls      r1, r0, #4
08003c48: 0101         lsls      r1, r0, #4
08003c4a: 0101         lsls      r1, r0, #4
08003c4c: 0101         lsls      r1, r0, #4
08003c4e: 0101         lsls      r1, r0, #4
08003c50: 0101         lsls      r1, r0, #4
08003c52: 0101         lsls      r1, r0, #4
08003c54: 0101         lsls      r1, r0, #4
08003c56: 0101         lsls      r1, r0, #4
08003c58: 0101         lsls      r1, r0, #4
08003c5a: 0101         lsls      r1, r0, #4
08003c5c: 0101         lsls      r1, r0, #4
08003c5e: 0101         lsls      r1, r0, #4
08003c60: 0101         lsls      r1, r0, #4
08003c62: 0101         lsls      r1, r0, #4
08003c64: 0101         lsls      r1, r0, #4
08003c66: 0101         lsls      r1, r0, #4
08003c68: 0101         lsls      r1, r0, #4
08003c6a: 0101         lsls      r1, r0, #4
08003c6c: 0202         lsls      r2, r0, #8
08003c6e: 0202         lsls      r2, r0, #8
08003c70: 0202         lsls      r2, r0, #8
08003c72: 0202         lsls      r2, r0, #8
08003c74: 0202         lsls      r2, r0, #8
08003c76: 0202         lsls      r2, r0, #8
08003c78: 0202         lsls      r2, r0, #8
08003c7a: 0202         lsls      r2, r0, #8
08003c7c: 0202         lsls      r2, r0, #8
08003c7e: 0202         lsls      r2, r0, #8
08003c80: 0202         lsls      r2, r0, #8
08003c82: 0202         lsls      r2, r0, #8
08003c84: 0202         lsls      r2, r0, #8
08003c86: 0202         lsls      r2, r0, #8
08003c88: 0202         lsls      r2, r0, #8
08003c8a: 0202         lsls      r2, r0, #8
08003c8c: 0101         lsls      r1, r0, #4
08003c8e: 0101         lsls      r1, r0, #4
08003c90: 0101         lsls      r1, r0, #4
08003c92: 0101         lsls      r1, r0, #4
08003c94: 0101         lsls      r1, r0, #4
08003c96: 0101         lsls      r1, r0, #4
08003c98: 0101         lsls      r1, r0, #4
08003c9a: 0101         lsls      r1, r0, #4
08003c9c: 0304         lsls      r3, r0, #0x10
08003c9e: 0504         lsls      r5, r0, #0x10
08003ca0: 0606         lsls      r6, r0, #0x18
08003ca2: 0708         lsrs      r7, r0, #0x20
08003ca4: 0909         lsrs      r1, r1, #4
08003ca6: 0909         lsrs      r1, r1, #4
08003ca8: 0909         lsrs      r1, r1, #4
08003caa: 0a09         lsrs      r2, r1, #4
08003cac: db26         movs      r6, #0xdb
08003cae: 0008         lsrs      r0, r0, #0x20
08003cb0: 6b25         movs      r5, #0x6b
08003cb2: 0008         lsrs      r0, r0, #0x20
08003cb4: 5725         movs      r5, #0x57
08003cb6: 0008         lsrs      r0, r0, #0x20
08003cb8: 0327         movs      r7, #3
08003cba: 0008         lsrs      r0, r0, #0x20
08003cbc: 2726         movs      r6, #0x27
08003cbe: 0008         lsrs      r0, r0, #0x20
08003cc0: 3b26         movs      r6, #0x3b
08003cc2: 0008         lsrs      r0, r0, #0x20
08003cc4: 4b26         movs      r6, #0x4b
08003cc6: 0008         lsrs      r0, r0, #0x20
08003cc8: 7b25         movs      r5, #0x7b
08003cca: 0008         lsrs      r0, r0, #0x20
08003ccc: 1327         movs      r7, #0x13
08003cce: 0008         lsrs      r0, r0, #0x20
08003cd0: 7927         movs      r7, #0x79
08003cd2: 0008         lsrs      r0, r0, #0x20
08003cd4: 3f25         movs      r5, #0x3f
08003cd6: 0008         lsrs      r0, r0, #0x20
08003cd8: 6326         movs      r6, #0x63
08003cda: 0008         lsrs      r0, r0, #0x20
08003cdc: 9528         cmp       r0, #0x95
08003cde: 0008         lsrs      r0, r0, #0x20
08003ce0: 8128         cmp       r0, #0x81
08003ce2: 0008         lsrs      r0, r0, #0x20
08003ce4: f728         cmp       r0, #0xf7
08003ce6: 0008         lsrs      r0, r0, #0x20
08003ce8: cb28         cmp       r0, #0xcb
08003cea: 0008         lsrs      r0, r0, #0x20
08003cec: df28         cmp       r0, #0xdf
08003cee: 0008         lsrs      r0, r0, #0x20
08003cf0: ef28         cmp       r0, #0xef
08003cf2: 0008         lsrs      r0, r0, #0x20
08003cf4: a528         cmp       r0, #0xa5
08003cf6: 0008         lsrs      r0, r0, #0x20
08003cf8: 0729         cmp       r1, #7
08003cfa: 0008         lsrs      r0, r0, #0x20
08003cfc: 7927         movs      r7, #0x79
08003cfe: 0008         lsrs      r0, r0, #0x20
08003d00: 3f25         movs      r5, #0x3f
08003d02: 0008         lsrs      r0, r0, #0x20
08003d04: 6b26         movs      r6, #0x6b
08003d06: 0008         lsrs      r0, r0, #0x20
08003d08: 9528         cmp       r0, #0x95
08003d0a: 0008         lsrs      r0, r0, #0x20
08003d0c: 8128         cmp       r0, #0x81
08003d0e: 0008         lsrs      r0, r0, #0x20
08003d10: f728         cmp       r0, #0xf7
08003d12: 0008         lsrs      r0, r0, #0x20
08003d14: cb28         cmp       r0, #0xcb
08003d16: 0008         lsrs      r0, r0, #0x20
08003d18: df28         cmp       r0, #0xdf
08003d1a: 0008         lsrs      r0, r0, #0x20
08003d1c: ef28         cmp       r0, #0xef
08003d1e: 0008         lsrs      r0, r0, #0x20
08003d20: a528         cmp       r0, #0xa5
08003d22: 0008         lsrs      r0, r0, #0x20
08003d24: 0729         cmp       r1, #7
08003d26: 0008         lsrs      r0, r0, #0x20
08003d28: 7927         movs      r7, #0x79
08003d2a: 0008         lsrs      r0, r0, #0x20
08003d2c: 3f25         movs      r5, #0x3f
08003d2e: 0008         lsrs      r0, r0, #0x20
08003d30: 5326         movs      r6, #0x53
08003d32: 0008         lsrs      r0, r0, #0x20
08003d34: 9528         cmp       r0, #0x95
08003d36: 0008         lsrs      r0, r0, #0x20
08003d38: 8128         cmp       r0, #0x81
08003d3a: 0008         lsrs      r0, r0, #0x20
08003d3c: f728         cmp       r0, #0xf7
08003d3e: 0008         lsrs      r0, r0, #0x20
08003d40: cb28         cmp       r0, #0xcb
08003d42: 0008         lsrs      r0, r0, #0x20
08003d44: df28         cmp       r0, #0xdf
08003d46: 0008         lsrs      r0, r0, #0x20
08003d48: ef28         cmp       r0, #0xef
08003d4a: 0008         lsrs      r0, r0, #0x20
08003d4c: a528         cmp       r0, #0xa5
08003d4e: 0008         lsrs      r0, r0, #0x20
08003d50: 0729         cmp       r1, #7
08003d52: 0008         lsrs      r0, r0, #0x20
08003d54: 7927         movs      r7, #0x79
08003d56: 0008         lsrs      r0, r0, #0x20
08003d58: 3f25         movs      r5, #0x3f
08003d5a: 0008         lsrs      r0, r0, #0x20
08003d5c: dd26         movs      r6, #0xdd
08003d5e: 0008         lsrs      r0, r0, #0x20
08003d60: e124         movs      r4, #0xe1
08003d62: 0008         lsrs      r0, r0, #0x20
08003d64: e124         movs      r4, #0xe1
08003d66: 0008         lsrs      r0, r0, #0x20
08003d68: e124         movs      r4, #0xe1
08003d6a: 0008         lsrs      r0, r0, #0x20
08003d6c: e124         movs      r4, #0xe1
08003d6e: 0008         lsrs      r0, r0, #0x20
08003d70: e124         movs      r4, #0xe1
08003d72: 0008         lsrs      r0, r0, #0x20
08003d74: e124         movs      r4, #0xe1
08003d76: 0008         lsrs      r0, r0, #0x20
08003d78: 9925         movs      r5, #0x99
08003d7a: 0008         lsrs      r0, r0, #0x20
08003d7c: 1527         movs      r7, #0x15
08003d7e: 0008         lsrs      r0, r0, #0x20
08003d80: 7927         movs      r7, #0x79
08003d82: 0008         lsrs      r0, r0, #0x20
08003d84: 3f25         movs      r5, #0x3f
08003d86: 0008         lsrs      r0, r0, #0x20
08003d88: e526         movs      r6, #0xe5
08003d8a: 0008         lsrs      r0, r0, #0x20
08003d8c: 1125         movs      r5, #0x11
08003d8e: 0008         lsrs      r0, r0, #0x20
08003d90: 1125         movs      r5, #0x11
08003d92: 0008         lsrs      r0, r0, #0x20
08003d94: 1125         movs      r5, #0x11
08003d96: 0008         lsrs      r0, r0, #0x20
08003d98: 1125         movs      r5, #0x11
08003d9a: 0008         lsrs      r0, r0, #0x20
08003d9c: 1125         movs      r5, #0x11
08003d9e: 0008         lsrs      r0, r0, #0x20
08003da0: 1125         movs      r5, #0x11
08003da2: 0008         lsrs      r0, r0, #0x20
08003da4: cb25         movs      r5, #0xcb
08003da6: 0008         lsrs      r0, r0, #0x20
08003da8: 3527         movs      r7, #0x35
08003daa: 0008         lsrs      r0, r0, #0x20
08003dac: 7927         movs      r7, #0x79
08003dae: 0008         lsrs      r0, r0, #0x20
08003db0: 3f25         movs      r5, #0x3f
08003db2: 0008         lsrs      r0, r0, #0x20
08003db4: ed26         movs      r6, #0xed
08003db6: 0008         lsrs      r0, r0, #0x20
08003db8: e124         movs      r4, #0xe1
08003dba: 0008         lsrs      r0, r0, #0x20
08003dbc: e124         movs      r4, #0xe1
08003dbe: 0008         lsrs      r0, r0, #0x20
08003dc0: e124         movs      r4, #0xe1
08003dc2: 0008         lsrs      r0, r0, #0x20
08003dc4: e124         movs      r4, #0xe1
08003dc6: 0008         lsrs      r0, r0, #0x20
08003dc8: e124         movs      r4, #0xe1
08003dca: 0008         lsrs      r0, r0, #0x20
08003dcc: e124         movs      r4, #0xe1
08003dce: 0008         lsrs      r0, r0, #0x20
08003dd0: fb25         movs      r5, #0xfb
08003dd2: 0008         lsrs      r0, r0, #0x20
08003dd4: 5927         movs      r7, #0x59
08003dd6: 0008         lsrs      r0, r0, #0x20
08003dd8: 7927         movs      r7, #0x79
08003dda: 0008         lsrs      r0, r0, #0x20
08003ddc: 3f25         movs      r5, #0x3f
08003dde: 0008         lsrs      r0, r0, #0x20
08003de0: 9726         movs      r6, #0x97
08003de2: 0008         lsrs      r0, r0, #0x20
08003de4: 9528         cmp       r0, #0x95
08003de6: 0008         lsrs      r0, r0, #0x20
08003de8: 8128         cmp       r0, #0x81
08003dea: 0008         lsrs      r0, r0, #0x20
08003dec: f728         cmp       r0, #0xf7
08003dee: 0008         lsrs      r0, r0, #0x20
08003df0: cb28         cmp       r0, #0xcb
08003df2: 0008         lsrs      r0, r0, #0x20
08003df4: df28         cmp       r0, #0xdf
08003df6: 0008         lsrs      r0, r0, #0x20
08003df8: ef28         cmp       r0, #0xef
08003dfa: 0008         lsrs      r0, r0, #0x20
08003dfc: a528         cmp       r0, #0xa5
08003dfe: 0008         lsrs      r0, r0, #0x20
08003e00: 0729         cmp       r1, #7
08003e02: 0008         lsrs      r0, r0, #0x20
08003e04: 7927         movs      r7, #0x79
08003e06: 0008         lsrs      r0, r0, #0x20
08003e08: 3f25         movs      r5, #0x3f
08003e0a: 0008         lsrs      r0, r0, #0x20
08003e0c: a726         movs      r6, #0xa7
08003e0e: 0008         lsrs      r0, r0, #0x20
08003e10: 9528         cmp       r0, #0x95
08003e12: 0008         lsrs      r0, r0, #0x20
08003e14: 8128         cmp       r0, #0x81
08003e16: 0008         lsrs      r0, r0, #0x20
08003e18: f728         cmp       r0, #0xf7
08003e1a: 0008         lsrs      r0, r0, #0x20
08003e1c: cb28         cmp       r0, #0xcb
08003e1e: 0008         lsrs      r0, r0, #0x20
08003e20: df28         cmp       r0, #0xdf
08003e22: 0008         lsrs      r0, r0, #0x20
08003e24: ef28         cmp       r0, #0xef
08003e26: 0008         lsrs      r0, r0, #0x20
08003e28: a528         cmp       r0, #0xa5
08003e2a: 0008         lsrs      r0, r0, #0x20
08003e2c: 0729         cmp       r1, #7
08003e2e: 0008         lsrs      r0, r0, #0x20
08003e30: 7927         movs      r7, #0x79
08003e32: 0008         lsrs      r0, r0, #0x20
08003e34: 3f25         movs      r5, #0x3f
08003e36: 0008         lsrs      r0, r0, #0x20
08003e38: 8126         movs      r6, #0x81
08003e3a: 0008         lsrs      r0, r0, #0x20
08003e3c: 9528         cmp       r0, #0x95
08003e3e: 0008         lsrs      r0, r0, #0x20
08003e40: 8128         cmp       r0, #0x81
08003e42: 0008         lsrs      r0, r0, #0x20
08003e44: f728         cmp       r0, #0xf7
08003e46: 0008         lsrs      r0, r0, #0x20
08003e48: cb28         cmp       r0, #0xcb
08003e4a: 0008         lsrs      r0, r0, #0x20
08003e4c: df28         cmp       r0, #0xdf
08003e4e: 0008         lsrs      r0, r0, #0x20
08003e50: ef28         cmp       r0, #0xef
08003e52: 0008         lsrs      r0, r0, #0x20
08003e54: a528         cmp       r0, #0xa5
08003e56: 0008         lsrs      r0, r0, #0x20
08003e58: 0729         cmp       r1, #7
08003e5a: 0008         lsrs      r0, r0, #0x20
08003e5c: 7927         movs      r7, #0x79
08003e5e: 0008         lsrs      r0, r0, #0x20
08003e60: 3f25         movs      r5, #0x3f
08003e62: 0008         lsrs      r0, r0, #0x20
08003e64: 9f26         movs      r6, #0x9f
08003e66: 0008         lsrs      r0, r0, #0x20
08003e68: 9127         movs      r7, #0x91
08003e6a: 0008         lsrs      r0, r0, #0x20
08003e6c: 9127         movs      r7, #0x91
08003e6e: 0008         lsrs      r0, r0, #0x20
08003e70: 9127         movs      r7, #0x91
08003e72: 0008         lsrs      r0, r0, #0x20
08003e74: 9127         movs      r7, #0x91
08003e76: 0008         lsrs      r0, r0, #0x20
08003e78: 9127         movs      r7, #0x91
08003e7a: 0008         lsrs      r0, r0, #0x20
08003e7c: 9127         movs      r7, #0x91
08003e7e: 0008         lsrs      r0, r0, #0x20
08003e80: bf27         movs      r7, #0xbf
08003e82: 0008         lsrs      r0, r0, #0x20
08003e84: ed27         movs      r7, #0xed
08003e86: 0008         lsrs      r0, r0, #0x20
08003e88: 7927         movs      r7, #0x79
08003e8a: 0008         lsrs      r0, r0, #0x20
08003e8c: 3f25         movs      r5, #0x3f
08003e8e: 0008         lsrs      r0, r0, #0x20
08003e90: bd26         movs      r6, #0xbd
08003e92: 0008         lsrs      r0, r0, #0x20
08003e94: 0f28         cmp       r0, #0xf
08003e96: 0008         lsrs      r0, r0, #0x20
08003e98: 0f28         cmp       r0, #0xf
08003e9a: 0008         lsrs      r0, r0, #0x20
08003e9c: 0f28         cmp       r0, #0xf
08003e9e: 0008         lsrs      r0, r0, #0x20
08003ea0: 0f28         cmp       r0, #0xf
08003ea2: 0008         lsrs      r0, r0, #0x20
08003ea4: 0f28         cmp       r0, #0xf
08003ea6: 0008         lsrs      r0, r0, #0x20
08003ea8: 0f28         cmp       r0, #0xf
08003eaa: 0008         lsrs      r0, r0, #0x20
08003eac: 3928         cmp       r0, #0x39
08003eae: 0008         lsrs      r0, r0, #0x20
08003eb0: 6328         cmp       r0, #0x63
08003eb2: 0008         lsrs      r0, r0, #0x20
08003eb4: 7927         movs      r7, #0x79
08003eb6: 0008         lsrs      r0, r0, #0x20
08003eb8: 3f25         movs      r5, #0x3f
08003eba: 0008         lsrs      r0, r0, #0x20
08003ebc: 0400         movs      r4, r0
08003ebe: 0000         movs      r0, r0
08003ec0: c800         lsls      r0, r1, #3
08003ec2: 0301         lsls      r3, r0, #4
08003ec4: bf5d         ldrb      r7, [r7, r6]
08003ec6: 0000         movs      r0, r0
08003ec8: 0100         movs      r1, r0
08003eca: 0000         movs      r0, r0
08003ecc: e803         lsls      r0, r5, #0xf
08003ece: 0000         movs      r0, r0
08003ed0: 0000         movs      r0, r0
08003ed2: 0000         movs      r0, r0
08003ed4: cc00         lsls      r4, r1, #3
08003ed6: 0000         movs      r0, r0
08003ed8: a001         lsls      r0, r4, #6
08003eda: 0000         movs      r0, r0
08003edc: 2000         movs      r0, r4
08003ede: 0000         movs      r0, r0
08003ee0: 0000         movs      r0, r0
08003ee2: 0000         movs      r0, r0
08003ee4: 0000         movs      r0, r0
08003ee6: 0000         movs      r0, r0
08003ee8: 5b21         movs      r1, #0x5b
08003eea: 0008         lsrs      r0, r0, #0x20
08003eec: 5b21         movs      r1, #0x5b
08003eee: 0008         lsrs      r0, r0, #0x20
08003ef0: 5b21         movs      r1, #0x5b
08003ef2: 0008         lsrs      r0, r0, #0x20
08003ef4: 5b21         movs      r1, #0x5b
08003ef6: 0008         lsrs      r0, r0, #0x20
08003ef8: 5b21         movs      r1, #0x5b
08003efa: 0008         lsrs      r0, r0, #0x20
08003efc: 0000         movs      r0, r0
08003efe: 0000         movs      r0, r0
08003f00: 0000         movs      r0, r0
08003f02: 0000         movs      r0, r0
08003f04: db34         adds      r4, #0xdb
08003f06: 0008         lsrs      r0, r0, #0x20
08003f08: d934         adds      r4, #0xd9
08003f0a: 0008         lsrs      r0, r0, #0x20
08003f0c: c934         adds      r4, #0xc9
08003f0e: 0008         lsrs      r0, r0, #0x20
08003f10: e534         adds      r4, #0xe5
08003f12: 0008         lsrs      r0, r0, #0x20
08003f14: dd34         adds      r4, #0xdd
08003f16: 0008         lsrs      r0, r0, #0x20
08003f18: 0000         movs      r0, r0
08003f1a: 0000         movs      r0, r0
08003f1c: 0000         movs      r0, r0
08003f1e: 0000         movs      r0, r0
08003f20: 3135         adds      r5, #0x31
08003f22: 0008         lsrs      r0, r0, #0x20
08003f24: fd34         adds      r4, #0xfd
08003f26: 0008         lsrs      r0, r0, #0x20
08003f28: ed34         adds      r4, #0xed
08003f2a: 0008         lsrs      r0, r0, #0x20
08003f2c: 5535         adds      r5, #0x55
08003f2e: 0008         lsrs      r0, r0, #0x20
08003f30: 4d35         adds      r5, #0x4d
08003f32: 0008         lsrs      r0, r0, #0x20
08003f34: 743f         subs      r7, #0x74
08003f36: 0008         lsrs      r0, r0, #0x20
08003f38: 0000         movs      r0, r0
08003f3a: 0020         movs      r0, #0
08003f3c: a000         lsls      r0, r4, #2
08003f3e: 0000         movs      r0, r0
08003f40: 5c01         lsls      r4, r3, #5
08003f42: 0008         lsrs      r0, r0, #0x20
08003f44: 1440         ands      r4, r2
08003f46: 0008         lsrs      r0, r0, #0x20
08003f48: a000         lsls      r0, r4, #2
08003f4a: 0020         movs      r0, #0
08003f4c: 1015         asrs      r0, r2, #0x14
08003f4e: 0000         movs      r0, r0
08003f50: 7801         lsls      r0, r7, #5
08003f52: 0008         lsrs      r0, r0, #0x20
08003f54: 0de2         b         #0x8004372
08003f56: ffff         .byte     0xff, 0xff
08003f58: 5de2         b         #0x8004416
08003f5a: ffff         .byte     0xff, 0xff
08003f5c: 05e4         b         #0x800376a
08003f5e: ffff         .byte     0xff, 0xff
08003f60: 59e3         b         #0x8004616
08003f62: ffff         .byte     0xff, 0xff
08003f64: 69e4         b         #0x800383a
08003f66: ffff         .byte     0xff, 0xff
08003f68: e5e3         b         #0x8004736
08003f6a: ffff         .byte     0xff, 0xff
08003f6c: 4de4         b         #0x800380a
08003f6e: ffff35e4     vsri.32   d30, d21, #1
08003f72: ffff         .byte     0xff, 0xff
08003f74: 2002         lsls      r0, r4, #8
08003f76: 0020         movs      r0, #0
08003f78: 4402         lsls      r4, r0, #9
08003f7a: 0020         movs      r0, #0
08003f7c: 6802         lsls      r0, r5, #9
08003f7e: 0020         movs      r0, #0
08003f80: 8c02         lsls      r4, r1, #0xa
08003f82: 0020         movs      r0, #0
08003f84: a802         lsls      r0, r5, #0xa
08003f86: 0020         movs      r0, #0
08003f88: 0010         asrs      r0, r0, #0x20
08003f8a: 0012         asrs      r0, r0, #8
08003f8c: 0014         asrs      r0, r0, #0x10
08003f8e: 0016         asrs      r0, r0, #0x18
08003f90: 0017         asrs      r0, r0, #0x1c
08003f92: 0018         adds      r0, r0, r0
08003f94: 0019         adds      r0, r0, r4
08003f96: 001a         subs      r0, r0, r0
08003f98: 0011         asrs      r0, r0, #4
08003f9a: 0013         asrs      r0, r0, #0xc
08003f9c: 0015         asrs      r0, r0, #0x14
08003f9e: 0000         movs      r0, r0
08003fa0: 0002         lsls      r0, r0, #8
08003fa2: 0101         lsls      r1, r0, #4
08003fa4: 0003         lsls      r0, r0, #0xc
08003fa6: 0105         lsls      r1, r0, #0x14
08003fa8: 0109         lsrs      r1, r0, #4
08003faa: 010a         lsrs      r1, r0, #8
08003fac: 010b         lsrs      r1, r0, #0xc
08003fae: 010c         lsrs      r1, r0, #0x10
08003fb0: 010d         lsrs      r1, r0, #0x14
08003fb2: 010e         lsrs      r1, r0, #0x18
08003fb4: 010f         lsrs      r1, r0, #0x1c
08003fb6: 001b         subs      r0, r0, r4
08003fb8: 0106         lsls      r1, r0, #0x18
08003fba: 0107         lsls      r1, r0, #0x1c
08003fbc: 0108         lsrs      r1, r0, #0x20
08003fbe: 0104         lsls      r1, r0, #0x10
08003fc0: 007f         ldrb      r0, [r0, #0x1c]
08003fc2: 007f         ldrb      r0, [r0, #0x1c]
08003fc4: 007f         ldrb      r0, [r0, #0x1c]
08003fc6: 007f         ldrb      r0, [r0, #0x1c]
08003fc8: 0000         movs      r0, r0
08003fca: 0000         movs      r0, r0
08003fcc: 0000         movs      r0, r0
08003fce: 0000         movs      r0, r0
08003fd0: 0000         movs      r0, r0
08003fd2: 0000         movs      r0, r0
08003fd4: 0000         movs      r0, r0
08003fd6: 0000         movs      r0, r0
08003fd8: 0100         movs      r1, r0
08003fda: 0000         movs      r0, r0
08003fdc: 5802         lsls      r0, r3, #9
08003fde: 0000         movs      r0, r0
08003fe0: 0204         lsls      r2, r0, #0x10
08003fe2: 0608         lsrs      r6, r0, #0x20
08003fe4: 0000         movs      r0, r0
08003fe6: 0000         movs      r0, r0
08003fe8: 0102         lsls      r1, r0, #8
08003fea: 0304         lsls      r3, r0, #0x10
08003fec: 0102         lsls      r1, r0, #8
08003fee: 0304         lsls      r3, r0, #0x10
08003ff0: 0607         lsls      r6, r0, #0x1c
08003ff2: 0809         lsrs      r0, r1, #4
08003ff4: 0000         movs      r0, r0
08003ff6: 0000         movs      r0, r0
08003ff8: 0000         movs      r0, r0
08003ffa: 0000         movs      r0, r0
08003ffc: 0000         movs      r0, r0
08003ffe: 0000         movs      r0, r0
08004000: 0000         movs      r0, r0
08004002: 0000         movs      r0, r0
08004004: 0000         movs      r0, r0
08004006: 0000         movs      r0, r0
08004008: 0000         movs      r0, r0
0800400a: 0000         movs      r0, r0
0800400c: 0000         movs      r0, r0
0800400e: 0000         movs      r0, r0
08004010: 0000         movs      r0, r0
08004012: 0000         movs      r0, r0
