
; Reset_Handler 0x08000314
08000314: 0948         ldr      r0, [pc, #0x24] ; [0x0800033c] = 0x08000c65
08000316: 8047         blx      r0
08000318: 0948         ldr      r0, [pc, #0x24] ; [0x08000340] = 0x08000121
0800031a: 0047         bx       r0

; GPIO_init 0x08000884
08000884: f8b5         push     {r3, r4, r5, r6, r7, lr}
08000886: fff70eff     bl       #0x80006a6
0800088a: 654f         ldr      r7, [pc, #0x194] ; [0x08000a20] = 0x40010800
0800088c: 3846         mov      r0, r7
0800088e: fff715ff     bl       #0x80006bc
08000892: 6846         mov      r0, sp
08000894: fff7eeff     bl       #0x8000874
08000898: 7815         asrs     r0, r7, #0x15
0800089a: adf80000     strh.w   r0, [sp]
0800089e: 0224         movs     r4, #2
080008a0: 8df80240     strb.w   r4, [sp, #2]
080008a4: 1820         movs     r0, #0x18
080008a6: 8df80300     strb.w   r0, [sp, #3]
080008aa: 6946         mov      r1, sp
080008ac: 3846         mov      r0, r7
080008ae: fff771ff     bl       #0x8000794
080008b2: 6846         mov      r0, sp
080008b4: fff7deff     bl       #0x8000874
080008b8: 6002         lsls     r0, r4, #9
080008ba: adf80000     strh.w   r0, [sp]
080008be: 8df80240     strb.w   r4, [sp, #2]
080008c2: 0425         movs     r5, #4
080008c4: 8df80350     strb.w   r5, [sp, #3]
080008c8: 6946         mov      r1, sp
080008ca: 3846         mov      r0, r7
080008cc: fff762ff     bl       #0x8000794
080008d0: 6846         mov      r0, sp
080008d2: fff7cfff     bl       #0x8000874
080008d6: 0f20         movs     r0, #0xf
080008d8: adf80000     strh.w   r0, [sp]
080008dc: 8df80240     strb.w   r4, [sp, #2]
080008e0: 0020         movs     r0, #0
080008e2: 8df80300     strb.w   r0, [sp, #3]
080008e6: 6946         mov      r1, sp
080008e8: 3846         mov      r0, r7
080008ea: fff753ff     bl       #0x8000794
080008ee: 6846         mov      r0, sp
080008f0: fff7c0ff     bl       #0x8000874
080008f4: f020         movs     r0, #0xf0
080008f6: adf80000     strh.w   r0, [sp]
080008fa: 8df80240     strb.w   r4, [sp, #2]
080008fe: 1026         movs     r6, #0x10
08000900: 8df80360     strb.w   r6, [sp, #3]
08000904: 6946         mov      r1, sp
08000906: 3846         mov      r0, r7
08000908: fff744ff     bl       #0x8000794
0800090c: 454f         ldr      r7, [pc, #0x114] ; [0x08000a24] = 0x40010c00
0800090e: 3846         mov      r0, r7
08000910: fff7d4fe     bl       #0x80006bc
08000914: 6846         mov      r0, sp
08000916: fff7adff     bl       #0x8000874
0800091a: 40f2e310     movw     r0, #0x1e3
0800091e: adf80000     strh.w   r0, [sp]
08000922: 8df80240     strb.w   r4, [sp, #2]
08000926: 8df80360     strb.w   r6, [sp, #3]
0800092a: 6946         mov      r1, sp
0800092c: 3846         mov      r0, r7
0800092e: fff731ff     bl       #0x8000794
08000932: 6846         mov      r0, sp
08000934: fff79eff     bl       #0x8000874
08000938: 4ff47040     mov.w    r0, #0xf000
0800093c: adf80000     strh.w   r0, [sp]
08000940: 8df80240     strb.w   r4, [sp, #2]
08000944: 8df80350     strb.w   r5, [sp, #3]
08000948: 6946         mov      r1, sp
0800094a: 3846         mov      r0, r7
0800094c: fff722ff     bl       #0x8000794
08000950: 354f         ldr      r7, [pc, #0xd4] ; [0x08000a28] = 0x40011000
08000952: 3846         mov      r0, r7
08000954: fff7b2fe     bl       #0x80006bc
08000958: 6846         mov      r0, sp
0800095a: fff78bff     bl       #0x8000874
0800095e: 40f20f40     movw     r0, #0x40f
08000962: adf80000     strh.w   r0, [sp]
08000966: 8df80240     strb.w   r4, [sp, #2]
0800096a: 8df80360     strb.w   r6, [sp, #3]
0800096e: 6946         mov      r1, sp
08000970: 3846         mov      r0, r7
08000972: fff70fff     bl       #0x8000794
08000976: 6846         mov      r0, sp
08000978: fff77cff     bl       #0x8000874
0800097c: 4ff47070     mov.w    r0, #0x3c0
08000980: adf80000     strh.w   r0, [sp]
08000984: 8df80240     strb.w   r4, [sp, #2]
08000988: 8df80350     strb.w   r5, [sp, #3]
0800098c: 6946         mov      r1, sp
0800098e: 3846         mov      r0, r7
08000990: fff700ff     bl       #0x8000794
08000994: 254f         ldr      r7, [pc, #0x94] ; [0x08000a2c] = 0x40011400
08000996: 3846         mov      r0, r7
08000998: fff790fe     bl       #0x80006bc
0800099c: 6846         mov      r0, sp
0800099e: fff769ff     bl       #0x8000874
080009a2: 4ff6c040     movw     r0, #0xfcc0
080009a6: adf80000     strh.w   r0, [sp]
080009aa: 8df80240     strb.w   r4, [sp, #2]
080009ae: 8df80360     strb.w   r6, [sp, #3]
080009b2: 6946         mov      r1, sp
080009b4: 3846         mov      r0, r7
080009b6: fff7edfe     bl       #0x8000794
080009ba: 6846         mov      r0, sp
080009bc: fff75aff     bl       #0x8000874
080009c0: 40f23f30     movw     r0, #0x33f
080009c4: adf80000     strh.w   r0, [sp]
080009c8: 8df80240     strb.w   r4, [sp, #2]
080009cc: 8df80350     strb.w   r5, [sp, #3]
080009d0: 6946         mov      r1, sp
080009d2: 3846         mov      r0, r7
080009d4: fff7defe     bl       #0x8000794
080009d8: 154f         ldr      r7, [pc, #0x54] ; [0x08000a30] = 0x40011800
080009da: 3846         mov      r0, r7
080009dc: fff76efe     bl       #0x80006bc
080009e0: 6846         mov      r0, sp
080009e2: fff747ff     bl       #0x8000874
080009e6: 4ff67000     movw     r0, #0xf870
080009ea: adf80000     strh.w   r0, [sp]
080009ee: 8df80240     strb.w   r4, [sp, #2]
080009f2: 8df80360     strb.w   r6, [sp, #3]
080009f6: 6946         mov      r1, sp
080009f8: 3846         mov      r0, r7
080009fa: fff7cbfe     bl       #0x8000794
080009fe: 6846         mov      r0, sp
08000a00: fff738ff     bl       #0x8000874
08000a04: 4ff4f060     mov.w    r0, #0x780
08000a08: adf80000     strh.w   r0, [sp]
08000a0c: 8df80240     strb.w   r4, [sp, #2]
08000a10: 8df80350     strb.w   r5, [sp, #3]
08000a14: 6946         mov      r1, sp
08000a16: 3846         mov      r0, r7
08000a18: fff7bcfe     bl       #0x8000794
08000a1c: f8bd         pop      {r3, r4, r5, r6, r7, pc}

; clock_enable 0x08000c18
08000c18: 10b5         push     {r4, lr}
08000c1a: 0020         movs     r0, #0
08000c1c: fff774ff     bl       #0x8000b08
08000c20: 0121         movs     r1, #1
08000c22: 0420         movs     r0, #4
08000c24: fff786ff     bl       #0x8000b34
08000c28: 0121         movs     r1, #1
08000c2a: 0820         movs     r0, #8
08000c2c: fff782ff     bl       #0x8000b34
08000c30: 0121         movs     r1, #1
08000c32: 1020         movs     r0, #0x10
08000c34: fff77eff     bl       #0x8000b34
08000c38: 0121         movs     r1, #1
08000c3a: 2020         movs     r0, #0x20
08000c3c: fff77aff     bl       #0x8000b34
08000c40: 0121         movs     r1, #1
08000c42: 4020         movs     r0, #0x40
08000c44: fff776ff     bl       #0x8000b34
08000c48: 0121         movs     r1, #1
08000c4a: c802         lsls     r0, r1, #0xb
08000c4c: fff772ff     bl       #0x8000b34
08000c50: 0121         movs     r1, #1
08000c52: 8803         lsls     r0, r1, #0xe
08000c54: fff76eff     bl       #0x8000b34
08000c58: 0121         movs     r1, #1
08000c5a: bde81040     pop.w    {r4, lr}
08000c5e: 4802         lsls     r0, r1, #9
08000c60: fff768bf     b.w      #0x8000b34

; SystemInit 0x08000c64
08000c64: 3048         ldr      r0, [pc, #0xc0] ; [0x08000d28] = 0x40021000
08000c66: 82b0         sub      sp, #8
08000c68: 0168         ldr      r1, [r0]
08000c6a: 41f00101     orr      r1, r1, #1
08000c6e: 0160         str      r1, [r0]
08000c70: 4268         ldr      r2, [r0, #4]
08000c72: 2e49         ldr      r1, [pc, #0xb8] ; [0x08000d2c] = 0xf8ff0000
08000c74: 1140         ands     r1, r2
08000c76: 4160         str      r1, [r0, #4]
08000c78: 0168         ldr      r1, [r0]
08000c7a: 21f41021     bic      r1, r1, #0x90000
08000c7e: 21f08071     bic      r1, r1, #0x1000000
08000c82: 0160         str      r1, [r0]
08000c84: 0168         ldr      r1, [r0]
08000c86: 21f48021     bic      r1, r1, #0x40000
08000c8a: 0160         str      r1, [r0]
08000c8c: 4168         ldr      r1, [r0, #4]
08000c8e: 21f4fe01     bic      r1, r1, #0x7f0000
08000c92: 4160         str      r1, [r0, #4]
08000c94: 4ff41f01     mov.w    r1, #0x9f0000
08000c98: 8160         str      r1, [r0, #8]
08000c9a: 0022         movs     r2, #0
08000c9c: c262         str      r2, [r0, #0x2c]
08000c9e: 0092         str      r2, [sp]
08000ca0: 0192         str      r2, [sp, #4]
08000ca2: 0168         ldr      r1, [r0]
08000ca4: 41f48031     orr      r1, r1, #0x10000
08000ca8: 0160         str      r1, [r0]
08000caa: 0168         ldr      r1, [r0]
08000cac: 01f40031     and      r1, r1, #0x20000
08000cb0: 0191         str      r1, [sp, #4]
08000cb2: 0099         ldr      r1, [sp]
08000cb4: 491c         adds     r1, r1, #1
08000cb6: 0091         str      r1, [sp]
08000cb8: 0199         ldr      r1, [sp, #4]
08000cba: 19b9         cbnz     r1, #0x8000cc4
08000cbc: 0099         ldr      r1, [sp]
08000cbe: b1f5a06f     cmp.w    r1, #0x500
08000cc2: f2d1         bne      #0x8000caa
08000cc4: 0168         ldr      r1, [r0]
08000cc6: 11f4003f     tst.w    r1, #0x20000
08000cca: 08bf         it       eq
08000ccc: 0192         streq    r2, [sp, #4]
08000cce: 24d0         beq      #0x8000d1a
08000cd0: 0121         movs     r1, #1
08000cd2: 0191         str      r1, [sp, #4]
08000cd4: 4168         ldr      r1, [r0, #4]
08000cd6: 4160         str      r1, [r0, #4]
08000cd8: 4168         ldr      r1, [r0, #4]
08000cda: 4160         str      r1, [r0, #4]
08000cdc: 4168         ldr      r1, [r0, #4]
08000cde: 4160         str      r1, [r0, #4]
08000ce0: 4168         ldr      r1, [r0, #4]
08000ce2: 21f47c11     bic      r1, r1, #0x3f0000
08000ce6: 4160         str      r1, [r0, #4]
08000ce8: 4168         ldr      r1, [r0, #4]
08000cea: 41f44031     orr      r1, r1, #0x30000
08000cee: 4160         str      r1, [r0, #4]
08000cf0: 0168         ldr      r1, [r0]
08000cf2: 41f08071     orr      r1, r1, #0x1000000
08000cf6: 0160         str      r1, [r0]
08000cf8: 0168         ldr      r1, [r0]
08000cfa: 11f0007f     tst.w    r1, #0x2000000
08000cfe: fbd0         beq      #0x8000cf8
08000d00: 4168         ldr      r1, [r0, #4]
08000d02: 21f00301     bic      r1, r1, #3
08000d06: 4160         str      r1, [r0, #4]
08000d08: 4168         ldr      r1, [r0, #4]
08000d0a: 41f00201     orr      r1, r1, #2
08000d0e: 4160         str      r1, [r0, #4]
08000d10: 4168         ldr      r1, [r0, #4]
08000d12: 01f00c01     and      r1, r1, #0xc
08000d16: 0829         cmp      r1, #8
08000d18: fad1         bne      #0x8000d10
08000d1a: 0549         ldr      r1, [pc, #0x14] ; [0x08000d30] = 0xe000ed08
08000d1c: 4ff00060     mov.w    r0, #0x8000000
08000d20: 0860         str      r0, [r1]
08000d22: 02b0         add      sp, #8
08000d24: 7047         bx       lr

; USART1_init 0x08001354
08001354: 10b5         push     {r4, lr}
08001356: 1b4c         ldr      r4, [pc, #0x6c] ; [0x080013c4] = 0x40013800
08001358: 84b0         sub      sp, #0x10
0800135a: 0021         movs     r1, #0
0800135c: 2046         mov      r0, r4
0800135e: fff7f0fe     bl       #0x8001142
08001362: 2046         mov      r0, r4
08001364: fff7f6fe     bl       #0x8001154
08001368: 6846         mov      r0, sp
0800136a: fff7e7ff     bl       #0x800133c
0800136e: 4ff22441     movw     r1, #0xf424
08001372: 0091         str      r1, [sp]
08001374: 0021         movs     r1, #0
08001376: adf80410     strh.w   r1, [sp, #4]
0800137a: adf80610     strh.w   r1, [sp, #6]
0800137e: adf80810     strh.w   r1, [sp, #8]
08001382: adf80c10     strh.w   r1, [sp, #0xc]
08001386: 0c21         movs     r1, #0xc
08001388: adf80a10     strh.w   r1, [sp, #0xa]
0800138c: 6946         mov      r1, sp
0800138e: 2046         mov      r0, r4
08001390: fff772ff     bl       #0x8001278
08001394: 0122         movs     r2, #1
08001396: 4ff45871     mov.w    r1, #0x360
0800139a: 2046         mov      r0, r4
0800139c: fff754ff     bl       #0x8001248
080013a0: 0122         movs     r2, #1
080013a2: 4ff4b071     mov.w    r1, #0x160
080013a6: 2046         mov      r0, r4
080013a8: fff74eff     bl       #0x8001248
080013ac: 0122         movs     r2, #1
080013ae: 40f22551     movw     r1, #0x525
080013b2: 2046         mov      r0, r4
080013b4: fff748ff     bl       #0x8001248
080013b8: 0121         movs     r1, #1
080013ba: 2046         mov      r0, r4
080013bc: fff7c1fe     bl       #0x8001142
080013c0: 04b0         add      sp, #0x10
080013c2: 10bd         pop      {r4, pc}

; main_startup 0x08002934
08002934: fef770f9     bl       #0x8000c18
08002938: fef77df8     bl       #0x8000a36
0800293c: fdf7a2ff     bl       #0x8000884
08002940: fdf77afe     bl       #0x8000638
08002944: fef706fd     bl       #0x8001354
08002948: fef7a4fb     bl       #0x8001094
0800294c: 0a4a         ldr      r2, [pc, #0x28] ; [0x08002978] = 0xe000e104
0800294e: 2021         movs     r1, #0x20
08002950: 1160         str      r1, [r2]
08002952: 4903         lsls     r1, r1, #0xd
08002954: 101f         subs     r0, r2, #4
08002956: 0160         str      r1, [r0]
08002958: c901         lsls     r1, r1, #7
0800295a: 0160         str      r1, [r0]
0800295c: 8912         asrs     r1, r1, #0xa
0800295e: 0748         ldr      r0, [pc, #0x1c] ; [0x0800297c] = 0x40011800
08002960: fdf786ff     bl       #0x8000870
08002964: fdf732fc     bl       #0x80001cc
08002968: 0022         movs     r2, #0
0800296a: 0921         movs     r1, #9
0800296c: 0448         ldr      r0, [pc, #0x10] ; [0x08002980] = 0x08001f71
0800296e: dff814c0     ldr.w    ip, [pc, #0x14] ; [0x08002984] = 0x08003149
08002972: 00df         svc      #0
08002974: fee7         b        #0x8002974
