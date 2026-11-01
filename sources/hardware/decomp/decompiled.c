/* AUTOMATIC GHIDRA DECOMPILATION: approximate pseudocode, not original or recompilable C. */

/* Address 08000120; body bytes 8 */

void FUN_08000120(void)

{
  int iVar1;
  code *UNRECOVERED_JUMPTABLE;
  int iVar2;
  undefined4 *puVar3;
  
  FUN_08000128();
  FUN_080001a0();
  iVar1 = DAT_08000154;
  puVar3 = (undefined4 *)((int)&DAT_08000154 + DAT_08000154);
  iVar2 = DAT_08000154 + 0x8000153;
  if (puVar3 == (undefined4 *)((int)&DAT_08000154 + DAT_08000158)) {
    FUN_080001a0();
  }
  UNRECOVERED_JUMPTABLE = *(code **)(&UNK_08000160 + iVar1);
  if (((uint)UNRECOVERED_JUMPTABLE & 1) != 0) {
    UNRECOVERED_JUMPTABLE = (code *)(iVar2 - (int)UNRECOVERED_JUMPTABLE);
  }
                    /* WARNING: Could not recover jumptable at 0x08000152. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)
            (*puVar3,*(undefined4 *)((int)&DAT_08000158 + iVar1),
             *(undefined4 *)(&UNK_0800015c + iVar1));
  return;
}



/* Address 08000128; body bytes 44 */

void FUN_08000128(void)

{
  int iVar1;
  code *UNRECOVERED_JUMPTABLE;
  int iVar2;
  undefined4 *puVar3;
  
  iVar1 = DAT_08000154;
  puVar3 = (undefined4 *)((int)&DAT_08000154 + DAT_08000154);
  iVar2 = DAT_08000154 + 0x8000153;
  if (puVar3 == (undefined4 *)((int)&DAT_08000154 + DAT_08000158)) {
    FUN_080001a0();
  }
  UNRECOVERED_JUMPTABLE = *(code **)(&UNK_08000160 + iVar1);
  if (((uint)UNRECOVERED_JUMPTABLE & 1) != 0) {
    UNRECOVERED_JUMPTABLE = (code *)(iVar2 - (int)UNRECOVERED_JUMPTABLE);
  }
                    /* WARNING: Could not recover jumptable at 0x08000152. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)
            (*puVar3,*(undefined4 *)((int)&DAT_08000158 + iVar1),
             *(undefined4 *)(&UNK_0800015c + iVar1));
  return;
}



/* Address 08000194; body bytes 8 */

undefined8 FUN_08000194(undefined4 param_1,undefined4 param_2)

{
  FUN_08000364();
  return CONCAT44(param_2,param_1);
}



/* Address 0800019c; body bytes 4 */

void FUN_0800019c(void)

{
  return;
}



/* Address 080001a0; body bytes 18 */

undefined4 FUN_080001a0(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  bool bVar1;
  undefined4 uVar2;
  undefined8 uVar3;
  
  uVar2 = FUN_080003dc();
  FUN_08000194(uVar2,param_3);
  FUN_08002934();
  uVar3 = FUN_08000426();
  FUN_0800019c();
  uVar2 = FUN_080003d0((int)uVar3,(int)((ulonglong)uVar3 >> 0x20));
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setProcessStackPointer(uVar2);
  }
  return uVar2;
}



/* Address 080001b2; body bytes 14 */

undefined4 FUN_080001b2(undefined4 param_1,undefined4 param_2)

{
  bool bVar1;
  undefined4 uVar2;
  
  FUN_0800019c();
  uVar2 = FUN_080003d0(param_1,param_2);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setProcessStackPointer(uVar2);
  }
  return uVar2;
}



/* Address 080001c0; body bytes 6 */

void FUN_080001c0(undefined4 param_1)

{
  bool bVar1;
  
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setProcessStackPointer(param_1);
  }
  return;
}



/* Address 080001c6; body bytes 6 */

undefined4 FUN_080001c6(void)

{
  undefined4 uVar1;
  
  uVar1 = getProcessStackPointer();
  return uVar1;
}



/* Address 080001cc; body bytes 24 */

uint FUN_080001cc(void)

{
  bool bVar1;
  char cVar2;
  uint uVar3;
  
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setProcessStackPointer(&stack0x00000000);
  }
  if ((*DAT_080001e4 & 1) == 0) {
    uVar3 = 3;
  }
  else {
    uVar3 = 2;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setThreadModePrivileged((uVar3 & 1) == 0);
    bVar1 = (bool)isThreadMode();
    if (bVar1) {
      cVar2 = isUsingMainStack();
      setStackMode(cVar2 == '\x01');
    }
  }
  return uVar3;
}



/* Address 08000228; body bytes 124 */

void FUN_08000228(void)

{
  bool bVar1;
  int *piVar2;
  undefined4 *puVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  uint unaff_r4;
  uint unaff_r5;
  uint unaff_r6;
  uint unaff_r7;
  uint unaff_r8;
  uint unaff_r9;
  uint unaff_r10;
  uint unaff_r11;
  uint *puVar9;
  undefined8 *puVar10;
  undefined8 uVar11;
  
  puVar3 = (undefined4 *)getProcessStackPointer();
  uVar4 = (uint)*(byte *)(puVar3[6] + -2);
  if (uVar4 != 0) {
    if (uVar4 <= *DAT_080002a8) {
      uVar7 = puVar3[2];
      uVar8 = puVar3[3];
      uVar11 = (**(code **)(DAT_080002ac + uVar4 * 4))(*puVar3,puVar3[1]);
      puVar10 = (undefined8 *)getProcessStackPointer();
      *puVar10 = uVar11;
      *(undefined4 *)(puVar10 + 1) = uVar7;
      *(undefined4 *)((int)puVar10 + 0xc) = uVar8;
    }
    return;
  }
  uVar4 = (*(code *)puVar3[4])(*puVar3,puVar3[1],puVar3[2],puVar3[3]);
  piVar2 = DAT_080002a4;
  puVar9 = (uint *)getProcessStackPointer();
  iVar5 = *DAT_080002a4;
  iVar6 = DAT_080002a4[1];
  if (iVar5 != iVar6) {
    if (iVar5 != 0) {
      *(undefined *)(iVar5 + 0x21) = 1;
      puVar9[-1] = unaff_r11;
      puVar9[-2] = unaff_r10;
      puVar9[-3] = unaff_r9;
      puVar9[-4] = unaff_r8;
      puVar9[-5] = unaff_r7;
      puVar9[-6] = unaff_r6;
      puVar9[-7] = unaff_r5;
      puVar9[-8] = unaff_r4;
      *(uint **)(iVar5 + 0x24) = puVar9 + -8;
      FUN_080030fc();
    }
    *piVar2 = iVar6;
    puVar9 = (uint *)(*(int *)(iVar6 + 0x24) + 0x20);
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      setProcessStackPointer(puVar9);
    }
    if (*(char *)(iVar6 + 0x21) == '\0') goto LAB_0800027e;
    uVar4 = (uint)*(byte *)(iVar6 + 0x20);
  }
  *puVar9 = uVar4;
LAB_0800027e:
  (*(code *)0xfffffffd)();
  return;
}



/* Address 080002b0; body bytes 76 */

void FUN_080002b0(void)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined4 unaff_r4;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  undefined4 unaff_r7;
  undefined4 unaff_r8;
  undefined4 unaff_r9;
  undefined4 unaff_r10;
  undefined4 unaff_r11;
  int iVar5;
  uint *puVar6;
  
  FUN_08002eb8();
  piVar2 = DAT_080002fc;
  iVar3 = *DAT_080002fc;
  iVar4 = DAT_080002fc[1];
  if (iVar3 != iVar4) {
    *(undefined *)(iVar3 + 0x21) = 0;
    iVar5 = getProcessStackPointer();
    *(undefined4 *)(iVar5 + -4) = unaff_r11;
    *(undefined4 *)(iVar5 + -8) = unaff_r10;
    *(undefined4 *)(iVar5 + -0xc) = unaff_r9;
    *(undefined4 *)(iVar5 + -0x10) = unaff_r8;
    *(undefined4 *)(iVar5 + -0x14) = unaff_r7;
    *(undefined4 *)(iVar5 + -0x18) = unaff_r6;
    *(undefined4 *)(iVar5 + -0x1c) = unaff_r5;
    *(undefined4 *)(iVar5 + -0x20) = unaff_r4;
    *(undefined4 **)(iVar3 + 0x24) = (undefined4 *)(iVar5 + -0x20);
    FUN_080030fc();
    *piVar2 = iVar4;
    puVar6 = (uint *)(*(int *)(iVar4 + 0x24) + 0x20);
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      setProcessStackPointer(puVar6);
    }
    if (*(char *)(iVar4 + 0x21) != '\0') {
      *puVar6 = (uint)*(byte *)(iVar4 + 0x20);
    }
  }
  (*(code *)0xfffffffd)();
  return;
}



/* Address 08000300; body bytes 6 */

void FUN_08000300(void)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined4 unaff_r4;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  undefined4 unaff_r7;
  undefined4 unaff_r8;
  undefined4 unaff_r9;
  undefined4 unaff_r10;
  undefined4 unaff_r11;
  int iVar5;
  uint *puVar6;
  
  FUN_080032a0();
  piVar2 = DAT_080002fc;
  iVar3 = *DAT_080002fc;
  iVar4 = DAT_080002fc[1];
  if (iVar3 != iVar4) {
    *(undefined *)(iVar3 + 0x21) = 0;
    iVar5 = getProcessStackPointer();
    *(undefined4 *)(iVar5 + -4) = unaff_r11;
    *(undefined4 *)(iVar5 + -8) = unaff_r10;
    *(undefined4 *)(iVar5 + -0xc) = unaff_r9;
    *(undefined4 *)(iVar5 + -0x10) = unaff_r8;
    *(undefined4 *)(iVar5 + -0x14) = unaff_r7;
    *(undefined4 *)(iVar5 + -0x18) = unaff_r6;
    *(undefined4 *)(iVar5 + -0x1c) = unaff_r5;
    *(undefined4 *)(iVar5 + -0x20) = unaff_r4;
    *(undefined4 **)(iVar3 + 0x24) = (undefined4 *)(iVar5 + -0x20);
    FUN_080030fc();
    *piVar2 = iVar4;
    puVar6 = (uint *)(*(int *)(iVar4 + 0x24) + 0x20);
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      setProcessStackPointer(puVar6);
    }
    if (*(char *)(iVar4 + 0x21) != '\0') {
      *puVar6 = (uint)*(byte *)(iVar4 + 0x20);
    }
  }
  (*(code *)0xfffffffd)();
  return;
}



/* Address 08000314; body bytes 8 */

void Reset_Handler(void)

{
  (*DAT_0800033c)();
                    /* WARNING: Could not recover jumptable at 0x0800031a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*DAT_08000340)();
  return;
}



/* Address 08000328; body bytes 2 */

void FUN_08000328(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Address 0800032e; body bytes 2 */

void FUN_0800032e(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Address 08000330; body bytes 10 */

undefined8 FUN_08000330(void)

{
  return CONCAT44(DAT_08000348,DAT_08000344);
}



/* Address 08000354; body bytes 4 */

undefined4 FUN_08000354(void)

{
  return DAT_08000358;
}



/* Address 08000364; body bytes 26 */

void FUN_08000364(void)

{
  int *piVar1;
  int *piVar2;
  
  piVar2 = (int *)(DAT_08000384 + 0x8000370);
  for (piVar1 = (int *)(DAT_08000380 + 0x800036c); piVar1 != piVar2; piVar1 = piVar1 + 1) {
    (*(code *)(*piVar1 + (int)piVar1))();
  }
  return;
}



/* Address 080003a0; body bytes 14 */

undefined4 FUN_080003a0(void)

{
  FUN_08000432("SIGPVFN: Pure virtual fn called",0);
  return 1;
}



/* Address 080003d0; body bytes 8 */

void FUN_080003d0(void)

{
  software_bkpt(0xab);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Address 080003dc; body bytes 74 */

void FUN_080003dc(void)

{
  uint uVar1;
  undefined4 *puVar2;
  undefined4 in_lr;
  uint *puVar3;
  
  uVar1 = FUN_08000354();
  *(undefined4 *)((uVar1 & 0xfffffff8) + 0x5c) = in_lr;
  puVar3 = (uint *)((uVar1 & 0xfffffff8) + 0x58);
  *puVar3 = uVar1;
  FUN_08000330();
  puVar2 = (undefined4 *)*puVar3;
  *puVar2 = 0;
  puVar2[1] = 0;
  puVar2[2] = 0;
  puVar2[3] = 0;
  puVar2[4] = 0;
  puVar2[5] = 0;
  puVar2[6] = 0;
  puVar2[7] = 0;
  puVar2[8] = 0;
  puVar2[9] = 0;
  puVar2[10] = 0;
  puVar2[0xb] = 0;
  puVar2[0xc] = 0;
  puVar2[0xd] = 0;
  puVar2[0xe] = 0;
  puVar2[0xf] = 0;
  return;
}



/* Address 08000426; body bytes 12 */

undefined8 FUN_08000426(undefined4 param_1)

{
  char cVar1;
  char *pcVar2;
  char *pcVar3;
  undefined8 uVar4;
  
  uVar4 = FUN_080001b2(param_1);
  pcVar2 = (char *)((ulonglong)uVar4 >> 0x20);
  cVar1 = '\n';
  for (pcVar3 = (char *)uVar4;
      (FUN_08000464(cVar1), pcVar3 != (char *)0x0 && (cVar1 = *pcVar3, cVar1 != '\0'));
      pcVar3 = pcVar3 + 1) {
  }
  for (; (pcVar2 != (char *)0x0 && (*pcVar2 != '\0')); pcVar2 = pcVar2 + 1) {
    FUN_08000464();
  }
  software_bkpt(0xab);
  return CONCAT44(&stack0xfffffff8,3);
}



/* Address 08000432; body bytes 50 */

undefined8 FUN_08000432(char *param_1,char *param_2)

{
  char cVar1;
  
  cVar1 = '\n';
  for (; (FUN_08000464(cVar1), param_1 != (char *)0x0 && (cVar1 = *param_1, cVar1 != '\0'));
      param_1 = param_1 + 1) {
  }
  for (; (param_2 != (char *)0x0 && (*param_2 != '\0')); param_2 = param_2 + 1) {
    FUN_08000464();
  }
  software_bkpt(0xab);
  return CONCAT44(&stack0xfffffff8,3);
}



/* Address 08000464; body bytes 14 */

undefined8 FUN_08000464(void)

{
  undefined local_8 [8];
  
  software_bkpt(0xab);
  return CONCAT44(local_8,3);
}



/* Address 08000478; body bytes 18 */

void FUN_08000478(int param_1,int param_2)

{
  uint uVar1;
  
  if (param_2 == 0) {
    uVar1 = *(uint *)(param_1 + 8) & 0xfffffffe;
  }
  else {
    uVar1 = *(uint *)(param_1 + 8) | 1;
  }
  *(uint *)(param_1 + 8) = uVar1;
  return;
}



/* Address 0800048a; body bytes 100 */

void FUN_0800048a(undefined *param_1)

{
  if (param_1 == &ADC1) {
    FUN_08000b4c(0x200);
    FUN_08000b4c(0x200,0);
    return;
  }
  if (param_1 == (undefined *)0x40012800) {
    FUN_08000b4c(0x400);
    FUN_08000b4c(0x400,0);
    return;
  }
  if (param_1 != (undefined *)0x40013c00) {
    return;
  }
  FUN_08000b4c(0x8000);
  FUN_08000b4c(0x8000,0);
  return;
}



/* Address 080004ee; body bytes 16 */

bool FUN_080004ee(int param_1)

{
  return (*(uint *)(param_1 + 8) & 4) != 0;
}



/* Address 080004fe; body bytes 6 */

uint FUN_080004fe(int param_1)

{
  return *(uint *)(param_1 + 0x4c) & 0xffff;
}



/* Address 08000504; body bytes 14 */

bool FUN_08000504(uint *param_1,uint param_2)

{
  return (*param_1 & param_2) != 0;
}



/* Address 08000512; body bytes 16 */

bool FUN_08000512(int param_1)

{
  return (*(uint *)(param_1 + 8) & 8) != 0;
}



/* Address 08000524; body bytes 70 */

void FUN_08000524(int param_1,uint *param_2)

{
  *(uint *)(param_1 + 4) =
       *(uint *)(param_1 + 4) & 0xfff0feff | (uint)*(byte *)(param_2 + 1) << 8 | *param_2;
  *(uint *)(param_1 + 8) =
       *(uint *)(param_1 + 8) & DAT_0800056c | (uint)*(byte *)((int)param_2 + 5) << 1 |
       param_2[3] | param_2[2];
  *(uint *)(param_1 + 0x2c) =
       *(uint *)(param_1 + 0x2c) & 0xff0fffff | (*(byte *)(param_2 + 4) - 1 & 0xff) << 0x14;
  return;
}



/* Address 08000570; body bytes 144 */

void FUN_08000570(int param_1,uint param_2,uint param_3,int param_4)

{
  uint uVar1;
  
  if (param_2 < 10) {
    *(uint *)(param_1 + 0x10) =
         param_4 << (param_2 * 3 & 0xff) | *(uint *)(param_1 + 0x10) & ~(7 << (param_2 * 3 & 0xff));
  }
  else {
    uVar1 = (param_2 - 10) * 3;
    *(uint *)(param_1 + 0xc) =
         param_4 << (uVar1 & 0xff) | *(uint *)(param_1 + 0xc) & ~(7 << (uVar1 & 0xff));
  }
  if (param_3 < 7) {
    uVar1 = (param_3 - 1) * 5;
    *(uint *)(param_1 + 0x34) =
         param_2 << (uVar1 & 0xff) | *(uint *)(param_1 + 0x34) & ~(0x1f << (uVar1 & 0xff));
    return;
  }
  if (param_3 < 0xd) {
    uVar1 = (param_3 - 7) * 5;
    *(uint *)(param_1 + 0x30) =
         param_2 << (uVar1 & 0xff) | *(uint *)(param_1 + 0x30) & ~(0x1f << (uVar1 & 0xff));
    return;
  }
  uVar1 = (param_3 - 0xd) * 5;
  *(uint *)(param_1 + 0x2c) =
       param_2 << (uVar1 & 0xff) | *(uint *)(param_1 + 0x2c) & ~(0x1f << (uVar1 & 0xff));
  return;
}



/* Address 08000600; body bytes 10 */

void FUN_08000600(int param_1)

{
  *(uint *)(param_1 + 8) = *(uint *)(param_1 + 8) | 8;
  return;
}



/* Address 0800060a; body bytes 18 */

void FUN_0800060a(int param_1,int param_2)

{
  uint uVar1;
  
  if (param_2 == 0) {
    uVar1 = *(uint *)(param_1 + 8) & 0xffafffff;
  }
  else {
    uVar1 = *(uint *)(param_1 + 8) | 0x500000;
  }
  *(uint *)(param_1 + 8) = uVar1;
  return;
}



/* Address 0800061c; body bytes 10 */

void FUN_0800061c(int param_1)

{
  *(uint *)(param_1 + 8) = *(uint *)(param_1 + 8) | 4;
  return;
}



/* Address 08000626; body bytes 18 */

void FUN_08000626(undefined4 *param_1)

{
  *param_1 = 0;
  *(undefined *)(param_1 + 1) = 0;
  *(undefined *)((int)param_1 + 5) = 0;
  param_1[2] = 0;
  param_1[3] = 0;
  *(undefined *)(param_1 + 4) = 1;
  return;
}



/* Address 08000638; body bytes 104 */

void FUN_08000638(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 local_20;
  undefined local_1c;
  undefined local_1b;
  undefined4 local_18;
  undefined4 uStack_14;
  undefined local_10;
  
  uVar1 = DAT_080006a0;
  FUN_08000478(DAT_080006a0,0);
  FUN_0800048a(uVar1);
  FUN_08000626(&local_20);
  local_18 = 0xe0000;
  uStack_14 = 0;
  local_1c = 0;
  local_10 = 1;
  local_20 = 0;
  local_1b = 0;
  FUN_08000524(uVar1,&local_20);
  FUN_08000478(uVar1,1);
  FUN_08000600(uVar1);
  do {
    iVar2 = FUN_08000512(uVar1);
  } while (iVar2 != 0);
  FUN_0800061c(uVar1);
  do {
    iVar2 = FUN_080004ee(uVar1);
  } while (iVar2 != 0);
  return;
}



/* Address 080006a4; body bytes 2 */

void FUN_080006a4(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Address 080006a6; body bytes 22 */

void FUN_080006a6(void)

{
  FUN_08000b4c(1);
  FUN_08000b4c(1,0);
  return;
}



/* Address 080006bc; body bytes 216 */

void FUN_080006bc(undefined *param_1)

{
  if (param_1 == &GPIOA) {
    FUN_08000b4c(4,1);
    FUN_08000b4c(4,0);
    return;
  }
  if (param_1 == &GPIOB) {
    FUN_08000b4c(8,1);
    FUN_08000b4c(8,0);
    return;
  }
  if (param_1 == &GPIOC) {
    FUN_08000b4c(0x10,1);
    FUN_08000b4c(0x10,0);
    return;
  }
  if (param_1 == &GPIOD) {
    FUN_08000b4c(0x20,1);
    FUN_08000b4c(0x20,0);
    return;
  }
  if (param_1 == &GPIOE) {
    FUN_08000b4c(0x40,1);
    FUN_08000b4c(0x40,0);
    return;
  }
  if (param_1 == (undefined *)0x40011c00) {
    FUN_08000b4c(0x80,1);
    FUN_08000b4c(0x80,0);
    return;
  }
  if (param_1 != (undefined *)0x40012000) {
    return;
  }
  FUN_08000b4c(0x100);
  FUN_08000b4c(0x100,0);
  return;
}



/* Address 08000794; body bytes 188 */

void FUN_08000794(uint *param_1,ushort *param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar1 = 0;
  uVar2 = *(byte *)((int)param_2 + 3) & 0xf;
  if ((*(byte *)((int)param_2 + 3) & 0x10) != 0) {
    uVar2 = *(byte *)(param_2 + 1) | uVar2;
  }
  if (*(char *)param_2 != '\0') {
    uVar3 = *param_1;
    do {
      uVar4 = 1 << (uVar1 & 0xff);
      if ((*param_2 & uVar4) == uVar4) {
        uVar3 = uVar3 & ~(0xf << (uVar1 << 2 & 0xff)) | uVar2 << (uVar1 << 2 & 0xff);
        if (*(char *)((int)param_2 + 3) == '(') {
          param_1[5] = uVar4;
        }
        else if (*(char *)((int)param_2 + 3) == 'H') {
          param_1[4] = uVar4;
        }
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 8);
    *param_1 = uVar3;
  }
  if (*param_2 < 0x100) {
    return;
  }
  uVar3 = param_1[1];
  uVar1 = 0;
  do {
    uVar4 = 1 << (uVar1 + 8 & 0xff);
    if ((*param_2 & uVar4) == uVar4) {
      uVar3 = uVar3 & ~(0xf << (uVar1 << 2 & 0xff)) | uVar2 << (uVar1 << 2 & 0xff);
      if (*(char *)((int)param_2 + 3) == '(') {
        param_1[5] = uVar4;
      }
      if (*(char *)((int)param_2 + 3) == 'H') {
        param_1[4] = uVar4;
      }
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 8);
  param_1[1] = uVar3;
  return;
}



/* Address 08000850; body bytes 14 */

bool FUN_08000850(int param_1,uint param_2)

{
  return (*(uint *)(param_1 + 8) & param_2) != 0;
}



/* Address 0800085e; body bytes 14 */

bool FUN_0800085e(int param_1,uint param_2)

{
  return (*(uint *)(param_1 + 0xc) & param_2) != 0;
}



/* Address 0800086c; body bytes 4 */

void FUN_0800086c(int param_1,undefined4 param_2)

{
  *(undefined4 *)(param_1 + 0x14) = param_2;
  return;
}



/* Address 08000870; body bytes 4 */

void FUN_08000870(int param_1,undefined4 param_2)

{
  *(undefined4 *)(param_1 + 0x10) = param_2;
  return;
}



/* Address 08000874; body bytes 16 */

void FUN_08000874(undefined2 *param_1)

{
  *param_1 = 0xffff;
  *(undefined *)(param_1 + 1) = 2;
  *(undefined *)((int)param_1 + 3) = 4;
  return;
}



/* Address 08000884; body bytes 410 */

void FUN_08000884(void)

{
  undefined4 uVar1;
  undefined4 in_r3;
  undefined4 local_18;
  
  local_18 = in_r3;
  FUN_080006a6();
  uVar1 = DAT_08000a20;
  FUN_080006bc(DAT_08000a20);
  FUN_08000874(&local_18);
  local_18 = CONCAT13(0x18,CONCAT12(2,(short)((int)uVar1 >> 0x15)));
  FUN_08000794(uVar1,&local_18);
  FUN_08000874(&local_18);
  local_18 = 0x4020400;
  FUN_08000794(uVar1,&local_18);
  FUN_08000874(&local_18);
  local_18 = 0x2000f;
  FUN_08000794(uVar1,&local_18);
  FUN_08000874(&local_18);
  local_18 = 0x100200f0;
  FUN_08000794(uVar1,&local_18);
  uVar1 = DAT_08000a24;
  FUN_080006bc(DAT_08000a24);
  FUN_08000874(&local_18);
  local_18 = 0x100201e3;
  FUN_08000794(uVar1,&local_18);
  FUN_08000874(&local_18);
  local_18 = 0x402f000;
  FUN_08000794(uVar1,&local_18);
  uVar1 = DAT_08000a28;
  FUN_080006bc(DAT_08000a28);
  FUN_08000874(&local_18);
  local_18 = 0x1002040f;
  FUN_08000794(uVar1,&local_18);
  FUN_08000874(&local_18);
  local_18 = 0x40203c0;
  FUN_08000794(uVar1,&local_18);
  uVar1 = DAT_08000a2c;
  FUN_080006bc(DAT_08000a2c);
  FUN_08000874(&local_18);
  local_18 = 0x1002fcc0;
  FUN_08000794(uVar1,&local_18);
  FUN_08000874(&local_18);
  local_18 = 0x402033f;
  FUN_08000794(uVar1,&local_18);
  uVar1 = DAT_08000a30;
  FUN_080006bc(DAT_08000a30);
  FUN_08000874(&local_18);
  local_18 = 0x1002f870;
  FUN_08000794(uVar1,&local_18);
  FUN_08000874(&local_18);
  local_18 = 0x4020780;
  FUN_08000794(uVar1,&local_18);
  return;
}



/* Address 08000a34; body bytes 2 */

void FUN_08000a34(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Address 08000a36; body bytes 64 */

void FUN_08000a36(void)

{
  undefined4 in_r3;
  undefined4 local_10;
  
  local_10 = in_r3;
  FUN_08000af4(0x500);
  local_10 = 0x25;
  FUN_08000a7c(&local_10);
  local_10 = 0x119;
  FUN_08000a7c(&local_10);
  return;
}



/* Address 08000a76; body bytes 2 */

void FUN_08000a76(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Address 08000a78; body bytes 2 */

void FUN_08000a78(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Address 08000a7c; body bytes 110 */

void FUN_08000a7c(byte *param_1)

{
  byte bVar1;
  uint uVar2;
  
  bVar1 = *param_1;
  if (param_1[3] != 0) {
    uVar2 = 0x700 - (*DAT_08000aec & 0x700) >> 8;
    *(char *)((uint)bVar1 + DAT_08000af0) =
         (char)(((uint)param_1[2] & 0xfU >> (uVar2 & 0xff) | (uint)param_1[1] << (4 - uVar2 & 0xff))
               << 4);
    *(int *)(&DAT_e000e100 + (uint)(*param_1 >> 5) * 4) = 1 << (*param_1 & 0x1f);
    return;
  }
  *(int *)((uint)(bVar1 >> 5) * 4 + -0x1fff1e80) = 1 << (bVar1 & 0x1f);
  return;
}



/* Address 08000af4; body bytes 14 */

void FUN_08000af4(uint param_1)

{
  *DAT_08000b04 = param_1 | 0x5fa0000;
  return;
}



/* Address 08000b08; body bytes 14 */

void FUN_08000b08(uint param_1)

{
  *(uint *)(DAT_08000b18 + 4) = param_1 | *(uint *)(DAT_08000b18 + 4) & 0xffff3fff;
  return;
}



/* Address 08000b1c; body bytes 18 */

void FUN_08000b1c(uint param_1,int param_2)

{
  if (param_2 == 0) {
    param_1 = *(uint *)(DAT_08000b30 + 0x10) & ~param_1;
  }
  else {
    param_1 = param_1 | *(uint *)(DAT_08000b30 + 0x10);
  }
  *(uint *)(DAT_08000b30 + 0x10) = param_1;
  return;
}



/* Address 08000b34; body bytes 18 */

void FUN_08000b34(uint param_1,int param_2)

{
  if (param_2 == 0) {
    param_1 = *(uint *)(DAT_08000b48 + 0x18) & ~param_1;
  }
  else {
    param_1 = param_1 | *(uint *)(DAT_08000b48 + 0x18);
  }
  *(uint *)(DAT_08000b48 + 0x18) = param_1;
  return;
}



/* Address 08000b4c; body bytes 18 */

void FUN_08000b4c(uint param_1,int param_2)

{
  if (param_2 == 0) {
    param_1 = *(uint *)(DAT_08000b60 + 0xc) & ~param_1;
  }
  else {
    param_1 = param_1 | *(uint *)(DAT_08000b60 + 0xc);
  }
  *(uint *)(DAT_08000b60 + 0xc) = param_1;
  return;
}



/* Address 08000b64; body bytes 160 */

void FUN_08000b64(uint *param_1)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  iVar1 = DAT_08000c04;
  uVar2 = *(uint *)(DAT_08000c04 + 4) & 0xc;
  if (uVar2 != 0) {
    if (uVar2 == 4) {
      *param_1 = DAT_08000c0c;
      goto LAB_08000bb4;
    }
    if (uVar2 == 8) {
      iVar3 = ((*(uint *)(DAT_08000c04 + 4) & 0x3c0000) >> 0x12) + 2;
      if ((*(uint *)(DAT_08000c04 + 4) & 0x10000) == 0) {
        uVar2 = DAT_08000c10 * iVar3;
      }
      else {
        uVar2 = (DAT_08000c0c / ((*(uint *)(DAT_08000c04 + 0x2c) & 0xf) + 1)) * iVar3;
      }
      *param_1 = uVar2;
      goto LAB_08000bb4;
    }
  }
  *param_1 = DAT_08000c08;
LAB_08000bb4:
  iVar3 = DAT_08000c14;
  uVar2 = *param_1 >> *(sbyte *)(DAT_08000c14 + (*(uint *)(iVar1 + 4) >> 4 & 0xf));
  param_1[1] = uVar2;
  param_1[2] = uVar2 >> *(sbyte *)(iVar3 + (*(uint *)(iVar1 + 4) >> 8 & 7));
  uVar2 = uVar2 >> *(sbyte *)(iVar3 + (*(uint *)(iVar1 + 4) >> 0xb & 7));
  param_1[3] = uVar2;
  param_1[4] = uVar2 / *(byte *)(iVar3 + -4 + (*(uint *)(iVar1 + 4) >> 0xe & 3));
  return;
}



/* Address 08000c18; body bytes 76 */

void FUN_08000c18(void)

{
  FUN_08000b08(0);
  FUN_08000b34(4,1);
  FUN_08000b34(8,1);
  FUN_08000b34(0x10,1);
  FUN_08000b34(0x20,1);
  FUN_08000b34(0x40,1);
  FUN_08000b34(0x800);
  FUN_08000b34(0x4000);
  FUN_08000b34(0x200);
  return;
}



/* Address 08000c64; body bytes 194 */

void SystemInit_candidate(void)

{
  uint *puVar1;
  int local_8;
  
  puVar1 = DAT_08000d28;
  *DAT_08000d28 = *DAT_08000d28 | 1;
  puVar1[1] = DAT_08000d2c & puVar1[1];
  *puVar1 = *puVar1 & 0xfef6ffff;
  *puVar1 = *puVar1 & 0xfffbffff;
  puVar1[1] = puVar1[1] & 0xff80ffff;
  puVar1[2] = 0x9f0000;
  puVar1[0xb] = 0;
  local_8 = 0;
  *puVar1 = *puVar1 | 0x10000;
  do {
    local_8 = local_8 + 1;
    if ((*puVar1 & 0x20000) != 0) break;
  } while (local_8 != 0x500);
  if ((*puVar1 & 0x20000) != 0) {
    puVar1[1] = puVar1[1];
    puVar1[1] = puVar1[1];
    puVar1[1] = puVar1[1];
    puVar1[1] = puVar1[1] & 0xffc0ffff;
    puVar1[1] = puVar1[1] | 0x30000;
    *puVar1 = *puVar1 | 0x1000000;
    do {
    } while ((*puVar1 & 0x2000000) == 0);
    puVar1[1] = puVar1[1] & 0xfffffffc;
    puVar1[1] = puVar1[1] | 2;
    do {
    } while ((puVar1[1] & 0xc) != 8);
  }
  *DAT_08000d30 = 0x8000000;
  return;
}



/* Address 08000d34; body bytes 80 */

void TIM1_UP_TIM16_IRQHandler(void)

{
  undefined4 uVar1;
  char *pcVar2;
  char cVar3;
  int iVar4;
  uint uVar5;
  
  FUN_080017f4();
  uVar1 = DAT_08000d84;
  FUN_08000d92(DAT_08000d84,0);
  pcVar2 = DAT_08000d88;
  iVar4 = *(int *)(DAT_08000d88 + 4);
  if (*DAT_08000d88 == '\0') {
    uVar5 = iVar4 - 1;
    *(uint *)(DAT_08000d88 + 4) = uVar5;
    if (uVar5 < 0x259) {
      iVar4 = 1;
    }
    cVar3 = (char)iVar4;
    if (600 < uVar5) goto LAB_08000d5e;
  }
  else {
    uVar5 = iVar4 + 1;
    *(uint *)(DAT_08000d88 + 4) = uVar5;
    if (uVar5 >= 0x4b0) {
      iVar4 = 0;
    }
    cVar3 = (char)iVar4;
    if (uVar5 < 0x4b0) goto LAB_08000d5e;
  }
  *pcVar2 = cVar3;
LAB_08000d5e:
  FUN_08000fda(uVar1,*(undefined2 *)(pcVar2 + 4));
  FUN_08000d92(uVar1,1);
  return;
}



/* Address 08000d8c; body bytes 6 */

void FUN_08000d8c(int param_1,ushort param_2)

{
  *(ushort *)(param_1 + 0x10) = ~param_2;
  return;
}



/* Address 08000d92; body bytes 18 */

void FUN_08000d92(ushort *param_1,int param_2)

{
  ushort uVar1;
  
  if (param_2 == 0) {
    uVar1 = *param_1 & 0xfffe;
  }
  else {
    uVar1 = *param_1 | 1;
  }
  *param_1 = uVar1;
  return;
}



/* Address 08000da4; body bytes 528 */

void FUN_08000da4(undefined *param_1)

{
  if (param_1 == &TIM1) {
    FUN_08000b4c(0x800);
    FUN_08000b4c(0x800,0);
    return;
  }
  if (param_1 == (undefined *)0x40000000) {
    FUN_08000b1c(1);
    FUN_08000b1c(1,0);
    return;
  }
  if (param_1 == (undefined *)0x40000400) {
    FUN_08000b1c(2,1);
    FUN_08000b1c(2,0);
    return;
  }
  if (param_1 == (undefined *)0x40000800) {
    FUN_08000b1c(4,1);
    FUN_08000b1c(4,0);
    return;
  }
  if (param_1 == (undefined *)0x40000c00) {
    FUN_08000b1c(8,1);
    FUN_08000b1c(8,0);
    return;
  }
  if (param_1 == (undefined *)0x40001000) {
    FUN_08000b1c(0x10,1);
    FUN_08000b1c(0x10,0);
    return;
  }
  if (param_1 == (undefined *)0x40001400) {
    FUN_08000b1c(0x20,1);
    FUN_08000b1c(0x20,0);
    return;
  }
  if (param_1 == (undefined *)0x40013400) {
    FUN_08000b4c(0x2000);
    FUN_08000b4c(0x2000,0);
    return;
  }
  if (param_1 == (undefined *)0x40014c00) {
    FUN_08000b4c(0x80000);
    FUN_08000b4c(0x80000,0);
    return;
  }
  if (param_1 == (undefined *)0x40015000) {
    FUN_08000b4c(0x100000);
    FUN_08000b4c(0x100000,0);
    return;
  }
  if (param_1 == (undefined *)0x40015400) {
    FUN_08000b4c(0x200000);
    FUN_08000b4c(0x200000,0);
    return;
  }
  if (param_1 == (undefined *)0x40001800) {
    FUN_08000b1c(0x40,1);
    FUN_08000b1c(0x40,0);
    return;
  }
  if (param_1 == (undefined *)0x40001c00) {
    FUN_08000b1c(0x80,1);
    FUN_08000b1c(0x80,0);
    return;
  }
  if (param_1 == (undefined *)0x40002000) {
    FUN_08000b1c(0x100);
    FUN_08000b1c(0x100,0);
    return;
  }
  if (param_1 == (undefined *)0x40014000) {
    FUN_08000b4c(0x10000);
    FUN_08000b4c(0x10000,0);
    return;
  }
  if (param_1 == (undefined *)0x40014400) {
    FUN_08000b4c(0x20000);
    FUN_08000b4c(0x20000,0);
    return;
  }
  if (param_1 != (undefined *)0x40014800) {
    return;
  }
  FUN_08000b4c(0x40000);
  FUN_08000b4c(0x40000,0);
  return;
}



/* Address 08000fb4; body bytes 22 */

bool FUN_08000fb4(int param_1,ushort param_2)

{
  return (*(ushort *)(param_1 + 0x10) & param_2) != 0 && (*(ushort *)(param_1 + 0xc) & param_2) != 0
  ;
}



/* Address 08000fca; body bytes 16 */

void FUN_08000fca(int param_1,ushort param_2,int param_3)

{
  if (param_3 == 0) {
    param_2 = *(ushort *)(param_1 + 0xc) & ~param_2;
  }
  else {
    param_2 = param_2 | *(ushort *)(param_1 + 0xc);
  }
  *(ushort *)(param_1 + 0xc) = param_2;
  return;
}



/* Address 08000fda; body bytes 4 */

void FUN_08000fda(int param_1,undefined2 param_2)

{
  *(undefined2 *)(param_1 + 0x2c) = param_2;
  return;
}



/* Address 08000fde; body bytes 4 */

void FUN_08000fde(int param_1,undefined2 param_2)

{
  *(undefined2 *)(param_1 + 0x24) = param_2;
  return;
}



/* Address 08000fe4; body bytes 148 */

void FUN_08000fe4(ushort *param_1,ushort *param_2)

{
  ushort *puVar1;
  ushort *puVar2;
  ushort uVar3;
  ushort *unaff_r4;
  ushort *puVar4;
  bool bVar5;
  
  puVar2 = DAT_0800107c;
  puVar1 = DAT_08001078;
  uVar3 = *param_1;
  if (param_1 == DAT_08001078 || param_1 == DAT_0800107c) {
LAB_0800101a:
    uVar3 = uVar3 & 0xff8f | param_2[1];
  }
  else {
    if (param_1 != (ushort *)0x40000000) {
      unaff_r4 = param_1 + -0x20000000;
    }
    if (param_1 == (ushort *)0x40000000 || unaff_r4 == (ushort *)0x400) goto LAB_0800101a;
    puVar4 = param_1 + -0x20000400;
    bVar5 = puVar4 != (ushort *)0x0;
    if (bVar5) {
      puVar4 = param_1 + -0x20000000;
    }
    if (!bVar5 || puVar4 == (ushort *)0xc00) goto LAB_0800101a;
  }
  puVar4 = param_1 + -0x20000800;
  bVar5 = puVar4 != (ushort *)0x0;
  if (bVar5) {
    puVar4 = param_1 + -0x20000000;
  }
  if (bVar5 && puVar4 != (ushort *)0x1400) {
    uVar3 = uVar3 & 0xfcff | param_2[3];
  }
  *param_1 = uVar3;
  param_1[0x16] = param_2[2];
  param_1[0x14] = *param_2;
  if (param_1 != puVar1 && param_1 != puVar2) {
    bVar5 = param_1 == (ushort *)0x40014000 || param_1 == (ushort *)0x40014400;
    if (param_1 != (ushort *)0x40014000 && param_1 != (ushort *)0x40014400) {
      bVar5 = param_1 == (ushort *)0x40014800;
    }
    if (!bVar5) goto LAB_08001070;
  }
  param_1[0x18] = (ushort)*(byte *)(param_2 + 4);
LAB_08001070:
  param_1[10] = 1;
  return;
}



/* Address 08001080; body bytes 18 */

void FUN_08001080(undefined2 *param_1)

{
  param_1[2] = 0xffff;
  *param_1 = 0;
  param_1[3] = 0;
  param_1[1] = 0;
  *(undefined *)(param_1 + 4) = 0;
  return;
}



/* Address 08001094; body bytes 98 */

void FUN_08001094(void)

{
  undefined4 uVar1;
  undefined2 local_18;
  undefined2 local_16;
  undefined2 local_14;
  undefined2 local_12;
  undefined local_10;
  
  uVar1 = DAT_080010f8;
  FUN_08000d92(DAT_080010f8,0);
  FUN_08000da4(uVar1);
  FUN_08000fde(uVar1,0);
  FUN_08001080(&local_18);
  local_18 = 0;
  local_14 = 599;
  local_12 = 0;
  local_10 = 0;
  local_16 = 0;
  FUN_08000fe4(uVar1,&local_18);
  FUN_08000d8c(uVar1,1);
  FUN_08000fca(uVar1,1);
  FUN_08000d92(uVar1,1);
  return;
}



/* Address 08001134; body bytes 28 */

void USART1_IRQHandler(void)

{
  FUN_08001518();
  FUN_0800347c(DAT_080015c8);
  return;
}



/* Address 08001142; body bytes 18 */

void FUN_08001142(int param_1,int param_2)

{
  ushort uVar1;
  
  if (param_2 == 0) {
    uVar1 = *(ushort *)(param_1 + 0xc) & 0xdfff;
  }
  else {
    uVar1 = *(ushort *)(param_1 + 0xc) | 0x2000;
  }
  *(ushort *)(param_1 + 0xc) = uVar1;
  return;
}



/* Address 08001154; body bytes 164 */

void FUN_08001154(undefined *param_1)

{
  if (param_1 == &USART1) {
    FUN_08000b4c(0x4000);
    FUN_08000b4c(0x4000,0);
    return;
  }
  if (param_1 == (undefined *)0x40004400) {
    FUN_08000b1c(0x20000);
    FUN_08000b1c(0x20000,0);
    return;
  }
  if (param_1 == (undefined *)0x40004800) {
    FUN_08000b1c(0x40000);
    FUN_08000b1c(0x40000,0);
    return;
  }
  if (param_1 == (undefined *)0x40004c00) {
    FUN_08000b1c(0x80000);
    FUN_08000b1c(0x80000,0);
    return;
  }
  if (param_1 != (undefined *)0x40005000) {
    return;
  }
  FUN_08000b1c(0x100000);
  FUN_08000b1c(0x100000,0);
  return;
}



/* Address 080011f8; body bytes 14 */

bool FUN_080011f8(ushort *param_1,ushort param_2)

{
  return (*param_1 & param_2) != 0;
}



/* Address 08001206; body bytes 66 */

bool FUN_08001206(ushort *param_1,uint param_2)

{
  ushort uVar1;
  uint uVar2;
  
  uVar2 = (param_2 << 0x18) >> 0x1d;
  if (uVar2 == 1) {
    uVar1 = param_1[6];
  }
  else if (uVar2 == 2) {
    uVar1 = param_1[8];
  }
  else {
    uVar1 = param_1[10];
  }
  return (1 << (param_2 & 0x1f) & (uint)uVar1) != 0 &&
         ((uint)*param_1 & 1 << (param_2 >> 8 & 0xff)) != 0;
}



/* Address 08001248; body bytes 48 */

void FUN_08001248(int param_1,uint param_2,int param_3)

{
  uint *puVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (param_2 << 0x18) >> 0x1d;
  uVar2 = 1 << (param_2 & 0x1f);
  if (uVar3 == 1) {
    puVar1 = (uint *)(param_1 + 0xc);
  }
  else if (uVar3 == 2) {
    puVar1 = (uint *)(param_1 + 0x10);
  }
  else {
    puVar1 = (uint *)(param_1 + 0x14);
  }
  if (param_3 == 0) {
    uVar2 = *puVar1 & ~uVar2;
  }
  else {
    uVar2 = uVar2 | *puVar1;
  }
  *puVar1 = uVar2;
  return;
}



/* Address 08001278; body bytes 174 */

void FUN_08001278(undefined *param_1,int *param_2)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  bool bVar5;
  undefined auStack_20 [8];
  int iStack_18;
  int iStack_14;
  
  *(ushort *)(param_1 + 0x10) = *(ushort *)(param_1 + 0x10) & 0xcfff | *(ushort *)((int)param_2 + 6)
  ;
  *(ushort *)(param_1 + 0xc) =
       *(ushort *)(param_1 + 0xc) & 0xe9f3 | *(ushort *)((int)param_2 + 10) |
       *(ushort *)(param_2 + 1) | *(ushort *)(param_2 + 2);
  *(ushort *)(param_1 + 0x14) = *(ushort *)(param_1 + 0x14) & 0xfcff | *(ushort *)(param_2 + 3);
  FUN_08000b64(auStack_20);
  if (param_1 != &USART1) {
    iStack_14 = iStack_18;
  }
  if ((*(ushort *)(param_1 + 0xc) & 0x8000) == 0) {
    uVar3 = *param_2 << 2;
  }
  else {
    uVar3 = *param_2 << 1;
  }
  uVar3 = (uint)(iStack_14 * 0x19) / uVar3;
  uVar4 = (uint)((ulonglong)DAT_08001328 * (ulonglong)uVar3 >> 0x25);
  iVar2 = uVar3 + uVar4 * -100;
  bVar5 = (*(ushort *)(param_1 + 0xc) & 0x8000) != 0;
  if (bVar5) {
    iVar2 = iVar2 * 8;
  }
  else {
    iVar2 = iVar2 * 0x10;
  }
  uVar1 = (ushort)(uint)((ulonglong)DAT_08001328 * (ulonglong)(iVar2 + 0x32) >> 0x25);
  if (bVar5) {
    uVar1 = uVar1 & 7;
  }
  else {
    uVar1 = uVar1 & 0xf;
  }
  *(ushort *)(param_1 + 8) = uVar1 | (ushort)(uVar4 << 4);
  return;
}



/* Address 0800132c; body bytes 8 */

ushort FUN_0800132c(int param_1)

{
  return *(ushort *)(param_1 + 4) & 0x1ff;
}



/* Address 0800133c; body bytes 22 */

void FUN_0800133c(undefined4 *param_1)

{
  *param_1 = 0x2580;
  *(undefined2 *)(param_1 + 1) = 0;
  *(undefined2 *)((int)param_1 + 6) = 0;
  *(undefined2 *)(param_1 + 2) = 0;
  *(undefined2 *)((int)param_1 + 10) = 0xc;
  *(undefined2 *)(param_1 + 3) = 0;
  return;
}



/* Address 08001352; body bytes 2 */

void FUN_08001352(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Address 08001354; body bytes 112 */

void FUN_08001354(void)

{
  undefined4 uVar1;
  undefined4 local_18;
  undefined2 local_14;
  undefined2 local_12;
  undefined2 local_10;
  undefined2 local_e;
  undefined2 local_c;
  
  uVar1 = DAT_080013c4;
  FUN_08001142(DAT_080013c4,0);
  FUN_08001154(uVar1);
  FUN_0800133c(&local_18);
  local_18 = 0xf424;
  local_14 = 0;
  local_12 = 0;
  local_10 = 0;
  local_c = 0;
  local_e = 0xc;
  FUN_08001278(uVar1,&local_18);
  FUN_08001248(uVar1,0x360,1);
  FUN_08001248(uVar1,0x160,1);
  FUN_08001248(uVar1,0x525,1);
  FUN_08001142(uVar1,1);
  return;
}



/* Address 080013c8; body bytes 196 */

void FUN_080013c8(void)

{
  code **ppcVar1;
  byte bVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  code *pcVar6;
  uint uVar7;
  
  ppcVar1 = DAT_0800148c;
  uVar7 = 0;
  if (*(char *)((int)DAT_0800148c + 0x11) != '\0') {
    do {
      iVar3 = FUN_08000850(*(undefined4 *)(ppcVar1[3] + uVar7 * 8),
                           *(undefined2 *)(ppcVar1[3] + uVar7 * 8 + 4));
      iVar5 = (uint)*(byte *)((int)ppcVar1 + 0x12) * (uint)*(byte *)((int)ppcVar1 + 0x11) + uVar7;
      if ((bool)*(char *)((int)ppcVar1 + iVar5 + 0x13) == (iVar3 != 0)) {
        ppcVar1[iVar5 + 9] = (code *)0x0;
      }
      else {
        pcVar6 = (code *)((int)ppcVar1[iVar5 + 9] << 1 | 1);
        ppcVar1[iVar5 + 9] = pcVar6;
        uVar4 = 0xf;
        do {
          if (((uint)pcVar6 >> (uVar4 & 0xff) & 1) == 0) goto LAB_0800147c;
          uVar4 = uVar4 - 1;
        } while (-1 < (int)uVar4);
        *(bool *)((int)ppcVar1 + iVar5 + 0x13) = iVar3 != 0;
        if (*ppcVar1 != (code *)0x0) {
          (**ppcVar1)((uint)*(byte *)(ppcVar1 + 1) + iVar5);
        }
      }
      uVar7 = uVar7 + 1;
    } while (uVar7 < *(byte *)((int)ppcVar1 + 0x11));
  }
  FUN_08000870(*(undefined4 *)(ppcVar1[2] + (uint)*(byte *)((int)ppcVar1 + 0x12) * 8),
               *(undefined2 *)(ppcVar1[2] + (uint)*(byte *)((int)ppcVar1 + 0x12) * 8 + 4));
  bVar2 = *(char *)((int)ppcVar1 + 0x12) + 1;
  *(byte *)((int)ppcVar1 + 0x12) = bVar2;
  if (*(byte *)(ppcVar1 + 4) <= bVar2) {
    *(undefined *)((int)ppcVar1 + 0x12) = 0;
  }
  FUN_0800086c(*(undefined4 *)(ppcVar1[2] + (uint)*(byte *)((int)ppcVar1 + 0x12) * 8),
               *(undefined2 *)(ppcVar1[2] + (uint)*(byte *)((int)ppcVar1 + 0x12) * 8 + 4));
LAB_0800147c:
  FUN_080035bc(DAT_08001490);
  FUN_080035bc(DAT_08001494);
  return;
}



/* Address 08001498; body bytes 16 */

void FUN_08001498(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = DAT_080014a8;
  uVar2 = 0;
  do {
    *(undefined *)(iVar1 + uVar2) = 0;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 0x20);
  return;
}



/* Address 080014ac; body bytes 18 */

void FUN_080014ac(void)

{
  FUN_080020aa(PTR_DAT_080014c0);
  FUN_080020aa(PTR_DAT_080014c4);
  return;
}



/* Address 080014c8; body bytes 50 */

void FUN_080014c8(undefined4 param_1,undefined4 param_2,code *param_3)

{
  undefined *puVar1;
  
  puVar1 = DAT_080014fc;
  if (DAT_080014fc[0x19] != '\0') {
    param_3 = *(code **)(DAT_080014fc + 4);
  }
  if (DAT_080014fc[0x19] != '\0' && param_3 != (code *)0x0) {
    (*param_3)(*DAT_080014fc);
    puVar1[0x19] = 0;
  }
  puVar1 = DAT_08001500;
  if (DAT_08001500[0x19] != '\0') {
    param_3 = *(code **)(DAT_08001500 + 4);
  }
  if (DAT_08001500[0x19] != '\0' && param_3 != (code *)0x0) {
    (*param_3)(*DAT_08001500);
    puVar1[0x19] = 0;
    return;
  }
  return;
}



/* Address 08001504; body bytes 16 */

void FUN_08001504(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = DAT_08001514;
  uVar2 = 0;
  do {
    *(undefined *)(iVar1 + uVar2) = 0;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 0x58);
  return;
}



/* Address 08001518; body bytes 164 */

void FUN_08001518(void)

{
  uint *puVar1;
  undefined uVar2;
  int iVar3;
  uint uVar4;
  
  puVar1 = DAT_080015bc;
  iVar3 = FUN_08001206(DAT_080015bc[0x24],0x525);
  if (iVar3 != 0) {
    uVar2 = FUN_0800132c(puVar1[0x24]);
    iVar3 = *puVar1 - puVar1[1];
    if (iVar3 < 0) {
      iVar3 = iVar3 + 0x80;
    }
    if ((short)iVar3 != 0x7f) {
      *(undefined *)((int)puVar1 + *puVar1 + 8) = uVar2;
      if ((int)*puVar1 < 0x7f) {
        uVar4 = *puVar1 + 1;
      }
      else {
        uVar4 = 0;
      }
      *puVar1 = uVar4;
      if (puVar1[0x22] != 0) {
        uVar4 = (uint)*(ushort *)(puVar1 + 0x23);
      }
      if (puVar1[0x22] != 0 && uVar4 != 0) {
        FUN_0800290c();
      }
    }
  }
  iVar3 = FUN_08001206(puVar1[0x24],0x360);
  if (iVar3 != 0) {
    FUN_080011f8(puVar1[0x24],8);
    FUN_0800132c(puVar1[0x24]);
  }
  iVar3 = FUN_08001206(puVar1[0x24],0x160);
  if (iVar3 != 0) {
    FUN_080011f8(puVar1[0x24],2);
    FUN_0800132c(puVar1[0x24]);
    return;
  }
  return;
}



/* Address 080017d4; body bytes 6 */

void FUN_080017d4(undefined4 param_1)

{
  *DAT_080017dc = param_1;
  return;
}



/* Address 080017e0; body bytes 14 */

void FUN_080017e0(undefined4 param_1)

{
  undefined4 *puVar1;
  
  puVar1 = DAT_080017f0;
  *DAT_080017f0 = param_1;
  puVar1[0x19] = param_1;
  puVar1[0x4b] = param_1;
  return;
}



/* Address 080017f4; body bytes 120 */

void FUN_080017f4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  int *piVar3;
  undefined uVar4;
  int iVar5;
  undefined4 unaff_r4;
  int iVar6;
  
  uVar2 = DAT_08001818;
  iVar5 = FUN_08000fb4(DAT_08001818,1);
  if (iVar5 == 0) {
    return;
  }
  FUN_08000d8c(uVar2,1);
  piVar3 = DAT_0800181c;
  if (*(char *)(DAT_0800181c + 2) == '\0') {
    iVar6 = DAT_0800181c[1];
    iVar5 = iVar6;
    if (iVar6 != 0) {
      do {
        FUN_08001fd8(iVar5);
        piVar1 = (int *)(iVar5 + 0x10);
        iVar5 = *piVar1;
      } while (*piVar1 != iVar6);
      goto LAB_08002098;
    }
  }
  else {
    iVar5 = FUN_0800085e(*(undefined4 *)*DAT_0800181c,
                         *(undefined2 *)((undefined4 *)*DAT_0800181c + 1),param_3,param_4,unaff_r4);
    if (iVar5 == 0) {
      FUN_08000870(*(undefined4 *)*piVar3,*(undefined2 *)((undefined4 *)*piVar3 + 1));
    }
    else {
      FUN_0800086c();
    }
LAB_08002098:
    if (*(char *)(piVar3 + 2) != '\0') {
      uVar4 = 0;
      goto LAB_080020a2;
    }
  }
  uVar4 = 1;
LAB_080020a2:
  *(undefined *)(piVar3 + 2) = uVar4;
  return;
}



/* Address 08001820; body bytes 10 */

void FUN_08001820(undefined4 param_1)

{
  int iVar1;
  
  iVar1 = DAT_0800182c;
  *(undefined4 *)(DAT_0800182c + 4) = param_1;
  *(undefined4 *)(iVar1 + 0x20) = param_1;
  return;
}



/* Address 08001830; body bytes 42 */

undefined4 FUN_08001830(undefined2 *param_1)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_0800185c;
  if (DAT_0800185c[1] != *DAT_0800185c) {
    *param_1 = *(undefined2 *)((int)DAT_0800185c + DAT_0800185c[1] * 2 + 8);
    if (piVar1[1] < 0x3f) {
      iVar2 = piVar1[1] + 1;
    }
    else {
      iVar2 = 0;
    }
    piVar1[1] = iVar2;
    return 1;
  }
  return 0;
}



/* Address 080018a0; body bytes 42 */

undefined4 FUN_080018a0(undefined2 *param_1)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_080018cc;
  if (DAT_080018cc[1] != *DAT_080018cc) {
    *param_1 = *(undefined2 *)((int)DAT_080018cc + DAT_080018cc[1] * 2 + 8);
    if (piVar1[1] < 0x1f) {
      iVar2 = piVar1[1] + 1;
    }
    else {
      iVar2 = 0;
    }
    piVar1[1] = iVar2;
    return 1;
  }
  return 0;
}



/* Address 080018d0; body bytes 8 */

void FUN_080018d0(void)

{
  *DAT_080018d8 = DAT_080018d8[1];
  return;
}



/* Address 0800197c; body bytes 42 */

undefined4 FUN_0800197c(undefined2 *param_1)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_080019a8;
  if (DAT_080019a8[1] != *DAT_080019a8) {
    *param_1 = *(undefined2 *)((int)DAT_080019a8 + DAT_080019a8[1] * 2 + 8);
    if (piVar1[1] < 0x1f) {
      iVar2 = piVar1[1] + 1;
    }
    else {
      iVar2 = 0;
    }
    piVar1[1] = iVar2;
    return 1;
  }
  return 0;
}



/* Address 080019ac; body bytes 8 */

void FUN_080019ac(void)

{
  *DAT_080019b4 = DAT_080019b4[1];
  return;
}



/* Address 08001bac; body bytes 338 */

void FUN_08001bac(void)

{
  char cVar1;
  code **ppcVar2;
  undefined4 uVar3;
  byte bVar4;
  undefined2 uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  
  ppcVar2 = DAT_08001d00;
  FUN_08000570(*(undefined4 *)(DAT_08001d00[2] + (uint)*(byte *)(DAT_08001d00 + 4) * 8),
               DAT_08001d00[2][(uint)*(byte *)(DAT_08001d00 + 4) * 8 + 4],1);
  FUN_0800060a(*(undefined4 *)(ppcVar2[2] + (uint)*(byte *)(ppcVar2 + 4) * 8),1);
  uVar3 = DAT_08001d04;
  do {
    iVar6 = FUN_08000504(uVar3,2);
  } while (iVar6 == 0);
  iVar6 = (uint)*(byte *)(ppcVar2 + 4) * (uint)*(byte *)((int)ppcVar2 + 0xd) +
          (uint)*(byte *)((int)ppcVar2 + 0xf);
  uVar8 = 1;
  do {
    iVar7 = 3 - uVar8;
    iVar10 = 4 - uVar8;
    uVar8 = uVar8 + 1;
    *(undefined2 *)((int)ppcVar2 + iVar10 * 2 + iVar6 * 8 + 0x52) =
         *(undefined2 *)((int)ppcVar2 + iVar7 * 2 + iVar6 * 8 + 0x52);
  } while (uVar8 < 4);
  uVar5 = FUN_080004fe(*(undefined4 *)(ppcVar2[2] + (uint)*(byte *)(ppcVar2 + 4) * 8));
  iVar7 = 0;
  *(undefined2 *)((int)ppcVar2 + iVar6 * 8 + 0x52) = uVar5;
  uVar12 = 0;
  uVar8 = 0xfff;
  uVar11 = 0;
  do {
    uVar9 = (uint)*(ushort *)((int)ppcVar2 + uVar11 * 2 + iVar6 * 8 + 0x52);
    if (uVar12 < uVar9) {
      uVar12 = uVar9;
    }
    if (uVar9 < uVar8) {
      uVar8 = uVar9;
    }
    iVar7 = iVar7 + uVar9;
    uVar11 = uVar11 + 1;
  } while (uVar11 < 4);
  uVar8 = iVar7 - (uVar8 + uVar12) >> 3;
  uVar12 = (uint)*(ushort *)((int)ppcVar2 + iVar6 * 2 + 0x12);
  iVar7 = uVar12 - uVar8;
  if ((uVar8 - 4 < 0x3f2) && ((3 < uVar12 || (uVar8 < 4)))) {
    bVar4 = *(byte *)((int)ppcVar2 + iVar6 + 0x152);
    if (bVar4 < 0x29) {
      *(byte *)((int)ppcVar2 + iVar6 + 0x152) = bVar4 + 1;
      if (iVar7 + 7U < 0xf) goto LAB_08001ca4;
    }
    else if (iVar7 + 0xfU < 0x1f) goto LAB_08001ca4;
  }
  *(short *)((int)ppcVar2 + iVar6 * 2 + 0x12) = (short)uVar8;
  *(undefined *)((int)ppcVar2 + iVar6 + 0x152) = 0;
  if (*ppcVar2 != (code *)0x0) {
    (**ppcVar2)(iVar6);
  }
LAB_08001ca4:
  bVar4 = *(char *)((int)ppcVar2 + 0xf) + 1;
  *(byte *)((int)ppcVar2 + 0xf) = bVar4;
  if (*(byte *)((int)ppcVar2 + 0xd) <= bVar4) {
    *(undefined *)((int)ppcVar2 + 0xf) = 0;
    cVar1 = *(char *)(ppcVar2 + 4);
    *(byte *)(ppcVar2 + 4) = cVar1 + 1U;
    if (*(byte *)((int)ppcVar2 + 0xe) <= (byte)(cVar1 + 1U)) {
      *(undefined *)(ppcVar2 + 4) = 0;
    }
  }
  uVar8 = 0;
  if (*(char *)(ppcVar2 + 3) == '\0') {
    return;
  }
  do {
    if ((*(byte *)((int)ppcVar2 + 0xf) >> (uVar8 & 0xff) & 1) == 0) {
      FUN_0800086c(*(undefined4 *)(ppcVar2[1] + uVar8 * 8),
                   *(undefined2 *)(ppcVar2[1] + uVar8 * 8 + 4));
    }
    else {
      FUN_08000870();
    }
    uVar8 = uVar8 + 1;
  } while (uVar8 < *(byte *)(ppcVar2 + 3));
  return;
}



/* Address 08001d38; body bytes 8 */

void FUN_08001d38(undefined4 param_1,undefined2 param_2)

{
  undefined4 *puVar1;
  
  puVar1 = DAT_08001d40;
  *DAT_08001d40 = param_1;
  *(undefined2 *)(puVar1 + 1) = param_2;
  return;
}



/* Address 08001d44; body bytes 10 */

void FUN_08001d44(undefined4 param_1,undefined2 param_2)

{
  int iVar1;
  
  iVar1 = DAT_08001d50;
  *(undefined4 *)(DAT_08001d50 + 0x48) = param_1;
  *(undefined2 *)(iVar1 + 0x4c) = param_2;
  return;
}



/* Address 08001d54; body bytes 174 */

void FUN_08001d54(undefined *param_1,uint param_2)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  piVar1 = DAT_08001e04;
  *(int *)(((uint)(int)*(char *)(DAT_08001e04 + 0x13) >> 5) * 4 + -0x1fff1e80) =
       1 << ((int)*(char *)(DAT_08001e04 + 0x13) & 0x1fU);
  uVar4 = param_2 & 0xffff;
  iVar2 = *piVar1 - piVar1[1];
  if (iVar2 < 0) {
    iVar2 = iVar2 + 0x40;
  }
  if (((int)uVar4 <= (int)(short)(0x3f - (short)iVar2)) && (uVar3 = 0, uVar4 != 0)) {
    do {
      *(undefined *)((int)piVar1 + *piVar1 + 8) = *param_1;
      if (*piVar1 < 0x3f) {
        iVar2 = *piVar1 + 1;
      }
      else {
        iVar2 = 0;
      }
      *piVar1 = iVar2;
      uVar3 = uVar3 + 1 & 0xffff;
      param_1 = param_1 + 1;
    } while (uVar3 < uVar4);
  }
  *(int *)(&DAT_e000e100 + ((uint)(int)*(char *)(piVar1 + 0x13) >> 5) * 4) =
       1 << ((int)*(char *)(piVar1 + 0x13) & 0x1fU);
  iVar2 = *piVar1 - piVar1[1];
  if (iVar2 < 0) {
    iVar2 = iVar2 + 0x40;
  }
  if ((int)(short)iVar2 != param_2) {
    return;
  }
  FUN_0800347c(piVar1);
  FUN_08001248(piVar1[0x12],0x727,1);
  return;
}



/* Address 08001e60; body bytes 10 */

void FUN_08001e60(undefined4 param_1,undefined2 param_2)

{
  int iVar1;
  
  iVar1 = DAT_08001e6c;
  *(undefined4 *)(DAT_08001e6c + 0x48) = param_1;
  *(undefined2 *)(iVar1 + 0x4c) = param_2;
  return;
}



/* Address 08001fd8; body bytes 126 */

void FUN_08001fd8(int *param_1)

{
  int iVar1;
  
  if (0xb < *(byte *)((int)param_1 + 9)) {
    (**(code **)(*param_1 + 4))(param_1);
    FUN_08000870(*(undefined4 *)param_1[1],*(undefined2 *)((undefined4 *)param_1[1] + 1));
    *(undefined *)((int)param_1 + 9) = 0;
    *(undefined *)(param_1 + 2) = 1;
    return;
  }
  if (*(char *)(param_1 + 2) == '\0') {
    FUN_0800086c(*(undefined4 *)param_1[1],*(undefined2 *)((undefined4 *)param_1[1] + 1));
  }
  else {
    if (*(byte *)((int)param_1 + 9) == 2) {
      (**(code **)*param_1)(param_1);
    }
    iVar1 = (**(code **)(*param_1 + 8))(param_1,0xb - (uint)*(byte *)((int)param_1 + 9));
    if (iVar1 == 0) {
      FUN_0800086c(*(undefined4 *)param_1[1],*(undefined2 *)((undefined4 *)param_1[1] + 1));
    }
    else {
      FUN_08000870();
    }
    *(char *)((int)param_1 + 9) = *(char *)((int)param_1 + 9) + '\x01';
  }
  *(bool *)(param_1 + 2) = *(char *)(param_1 + 2) == '\0';
  return;
}



/* Address 080020aa; body bytes 170 */

void FUN_080020aa(int param_1)

{
  undefined uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  iVar2 = FUN_08000850(*(undefined4 *)(param_1 + 8),*(undefined2 *)(param_1 + 0xc));
  uVar4 = (uint)(iVar2 != 0);
  uVar3 = FUN_08000850(*(undefined4 *)(param_1 + 0x10),*(undefined2 *)(param_1 + 0x14));
  if (uVar3 != 0) {
    uVar3 = 1;
  }
  switch(*(undefined *)(param_1 + 0x18)) {
  case 0:
    if ((uVar3 & ~uVar4) == 0) {
      if ((uVar4 & ~uVar3) == 0) {
        return;
      }
      goto LAB_080020fa;
    }
    goto LAB_080020ee;
  case 1:
    if ((uVar4 | uVar3) == 0) {
      uVar1 = 3;
LAB_0800213e:
      *(undefined *)(param_1 + 0x18) = uVar1;
      return;
    }
    if ((uVar4 & uVar3) == 0) {
      return;
    }
    break;
  case 2:
    if ((uVar4 | uVar3) == 0) {
      uVar1 = 4;
      goto LAB_0800213e;
    }
    if ((uVar4 & uVar3) == 0) {
      return;
    }
    break;
  case 3:
    if ((uVar3 & ~uVar4) != 0) {
      *(char *)(param_1 + 0x19) = *(char *)(param_1 + 0x19) + -1;
      *(undefined *)(param_1 + 0x18) = 2;
      return;
    }
    if ((uVar4 & ~uVar3) == 0) {
      return;
    }
LAB_080020fa:
    *(undefined *)(param_1 + 0x18) = 1;
    return;
  case 4:
    if ((uVar3 & ~uVar4) == 0) {
      if ((uVar4 & ~uVar3) == 0) {
        return;
      }
      *(char *)(param_1 + 0x19) = *(char *)(param_1 + 0x19) + '\x01';
      *(undefined *)(param_1 + 0x18) = 1;
      return;
    }
LAB_080020ee:
    *(undefined *)(param_1 + 0x18) = 2;
    return;
  }
  *(undefined *)(param_1 + 0x18) = 0;
  return;
}



/* Address 08002160; body bytes 76 */

void FUN_08002160(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  
  iVar1 = DAT_080021ac;
  iVar3 = DAT_080021b0 + 0x18;
  *(int *)(DAT_080021ac + 4) = DAT_080021b0;
  *(int *)(iVar1 + 8) = iVar3;
  *(undefined *)(iVar1 + 0xc) = 3;
  *(undefined *)(iVar1 + 0xd) = 8;
  *(undefined *)(iVar1 + 0xe) = 4;
  *(undefined *)(iVar1 + 0xf) = 0;
  *(undefined *)(iVar1 + 0x10) = 0;
  uVar4 = 0;
  do {
    *(undefined2 *)(iVar1 + uVar4 * 2 + 0x12) = 0;
    uVar2 = 0;
    do {
      iVar3 = uVar2 * 2;
      uVar2 = uVar2 + 1;
      *(undefined2 *)(iVar1 + uVar4 * 8 + iVar3 + 0x52) = 0;
    } while (uVar2 < 4);
    iVar3 = iVar1 + uVar4;
    uVar4 = uVar4 + 1;
    *(undefined *)(iVar3 + 0x152) = 0;
  } while (uVar4 < 0x20);
  return;
}



/* Address 080021b4; body bytes 224 */

void FUN_080021b4(void)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  
  puVar2 = DAT_08002298;
  piVar1 = DAT_08002294;
  *DAT_08002294 = (int)DAT_08002298;
  piVar1[1] = 0;
  *(undefined *)(piVar1 + 2) = 0;
  FUN_0800086c(*puVar2,*(undefined2 *)(puVar2 + 1));
  FUN_0800355c(DAT_08002294 + 3,DAT_08002294,DAT_0800229c + -0x28);
  FUN_0800355c(DAT_08002294 + 0xc,DAT_08002294,DAT_0800229c + -0x20);
  FUN_0800355c(DAT_08002294 + 0x15,DAT_08002294,DAT_0800229c + -0x18);
  uVar4 = DAT_080022a8;
  uVar3 = DAT_080022a4;
  puVar2 = DAT_080022a0;
  *DAT_080022a0 = DAT_080022a8;
  puVar2[1] = uVar3;
  *(undefined *)(puVar2 + 2) = 1;
  *(undefined *)((int)puVar2 + 9) = 0;
  puVar2[3] = 0;
  puVar2[4] = 0;
  iVar7 = puVar2[-0x1d];
  if (iVar7 == 0) {
    puVar2[3] = puVar2;
    puVar2[4] = puVar2;
    puVar2[-0x1d] = puVar2;
  }
  else {
    iVar8 = *(int *)(iVar7 + 0xc);
    puVar2[3] = iVar8;
    puVar2[4] = iVar7;
    *(undefined4 **)(iVar7 + 0xc) = puVar2;
    *(undefined4 **)(iVar8 + 0x10) = puVar2;
  }
  uVar3 = DAT_080022ac;
  puVar2[5] = 0;
  *puVar2 = uVar3;
  *(undefined *)(puVar2 + 6) = 0;
  *(undefined *)((int)puVar2 + 0x19) = 0;
  iVar7 = 0;
  do {
    iVar8 = iVar7 * 2;
    iVar7 = iVar7 + 1;
    *(undefined2 *)((int)puVar2 + iVar8 + 0x1a) = 0xffff;
    uVar6 = DAT_080022b4;
    puVar5 = DAT_080022b0;
  } while (iVar7 == 0);
  *DAT_080022b0 = uVar4;
  puVar5[1] = uVar6;
  *(undefined *)(puVar5 + 2) = 1;
  *(undefined *)((int)puVar5 + 9) = 0;
  puVar5[3] = 0;
  puVar5[4] = 0;
  iVar7 = puVar2[-0x1d];
  if (iVar7 == 0) {
    puVar5[3] = puVar5;
    puVar5[4] = puVar5;
    puVar2[-0x1d] = puVar5;
  }
  else {
    iVar8 = *(int *)(iVar7 + 0xc);
    puVar5[3] = iVar8;
    puVar5[4] = iVar7;
    *(undefined4 **)(iVar7 + 0xc) = puVar5;
    *(undefined4 **)(iVar8 + 0x10) = puVar5;
  }
  puVar5[5] = 0;
  *puVar5 = uVar3;
  *(undefined *)(puVar5 + 6) = 0;
  *(undefined *)((int)puVar5 + 0x19) = 0;
  iVar7 = 0;
  do {
    iVar8 = iVar7 * 2;
    iVar7 = iVar7 + 1;
    *(undefined2 *)((int)puVar5 + iVar8 + 0x1a) = 0xffff;
  } while (iVar7 == 0);
  return;
}



/* Address 080022b8; body bytes 124 */

void FUN_080022b8(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  iVar1 = DAT_08002338;
  iVar2 = DAT_08002334;
  iVar4 = DAT_08002338 + 0x20;
  *(undefined *)(DAT_08002334 + 4) = 0;
  *(int *)(iVar2 + 8) = iVar1;
  *(int *)(iVar2 + 0xc) = iVar4;
  *(undefined *)(iVar2 + 0x10) = 4;
  *(undefined *)(iVar2 + 0x11) = 4;
  *(undefined *)(iVar2 + 0x12) = 0;
  uVar3 = 0;
  do {
    *(undefined *)(iVar2 + uVar3 + 0x13) = 1;
    iVar1 = uVar3 * 4;
    uVar3 = uVar3 + 1;
    *(undefined4 *)(iVar2 + iVar1 + 0x24) = 1;
  } while (uVar3 < 0x10);
  uVar3 = 0;
  if (*(char *)(iVar2 + 0x10) != '\0') {
    do {
      FUN_08000870(*(undefined4 *)(*(int *)(iVar2 + 8) + uVar3 * 8),
                   *(undefined2 *)(*(int *)(iVar2 + 8) + uVar3 * 8 + 4));
      uVar3 = uVar3 + 1;
    } while (uVar3 < *(byte *)(iVar2 + 0x10));
  }
  FUN_08003678(DAT_08002340,0x10,DAT_0800233c + -0x30,DAT_0800233c,6,6);
  FUN_08003678(DAT_08002348,0x34,DAT_08002344 + -0x30,DAT_08002344,6,6);
  return;
}



/* Address 080023fc; body bytes 70 */

undefined4 FUN_080023fc(undefined4 *param_1,uint param_2,uint param_3)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  
  if ((int)param_3 < 0) {
    uVar4 = (param_3 & 0x7fffffff) + 7 & 0xfffffff8;
    iVar2 = 0x10;
  }
  else {
    uVar4 = param_3 + 3 & 0xfffffffc;
    iVar2 = 0xc;
  }
  if ((uVar4 != 0) && (uVar4 + iVar2 <= param_2)) {
    param_1[2] = uVar4;
    *param_1 = (undefined4 *)(iVar2 + (int)param_1);
    param_1[1] = param_2 + (int)param_1;
    puVar3 = (undefined4 *)(iVar2 + (int)param_1);
    while (puVar1 = (undefined4 *)((int)puVar3 + uVar4),
          puVar1 <= (undefined4 *)((param_2 + (int)param_1) - uVar4)) {
      *puVar3 = puVar1;
      puVar3 = puVar1;
    }
    *puVar3 = 0;
    return 0;
  }
  return 1;
}



/* Address 08002444; body bytes 28 */

undefined4 FUN_08002444(undefined4 *param_1)

{
  int iVar1;
  
  iVar1 = FUN_0800346c();
  if (iVar1 == 0) {
    return 0;
  }
  software_interrupt(0);
  return *param_1;
}



/* Address 08002464; body bytes 24 */

undefined4 FUN_08002464(undefined4 *param_1)

{
  int iVar1;
  
  iVar1 = FUN_0800346c();
  if (iVar1 == 0) {
    return 0;
  }
  software_interrupt(0);
  return *param_1;
}



/* Address 08002480; body bytes 34 */

void FUN_08002480(void)

{
  if (((*DAT_080024a4 << 7 < 0) && ((*DAT_080024a8 & 1) != 0)) && ((int)DAT_080024a8[-0x20] < 0)) {
    *DAT_080024ac = 1;
  }
  return;
}



/* Address 080024b0; body bytes 32 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_080024b0(int param_1,int param_2)

{
  do {
  } while (_DAT_e000007c == 0);
  do {
  } while (*(int *)(param_1 + 0x2c) == 0);
  _DAT_e000007c =
       CONCAT22((short)((uint)*(int *)(param_1 + 0x2c) >> 0x10),
                (ushort)*(byte *)(param_1 + 3) | (ushort)(param_2 << 8));
  return;
}



/* Address 080024e0; body bytes 76 */

void FUN_080024e0(byte *param_1,int param_2)

{
  param_1[0xd] = (byte)param_2;
  param_1[0xe] = 0xff;
  param_1[0xf] = 0xff;
  param_1[0xc] = *param_1 | 5;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
                    /* WARNING: Could not recover jumptable at 0x0800112a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(DAT_08001130 + *(int *)(param_1 + 4) * 0x2c +
              (uint)*(byte *)(DAT_0800112c + param_2) * 4))();
  return;
}



/* Address 08002510; body bytes 46 */

void FUN_08002510(byte *param_1,int param_2)

{
  param_1[0xe] = (byte)param_2;
  param_1[0xf] = 0xff;
  param_1[0xc] = *param_1 | 6;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
                    /* WARNING: Could not recover jumptable at 0x0800112a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(DAT_08001130 + *(int *)(param_1 + 4) * 0x2c +
              (uint)*(byte *)(DAT_0800112c + param_2) * 4))();
  return;
}



/* Address 08002598; body bytes 50 */

void FUN_08002598(byte *param_1,int param_2)

{
  param_1[0xd] = 0xf6;
  param_1[0xe] = 0xff;
  param_1[0xf] = 0xff;
  param_1[0xc] = *param_1 | 5;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
                    /* WARNING: Could not recover jumptable at 0x0800112a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(DAT_08001130 + *(int *)(param_1 + 4) * 0x2c +
              (uint)*(byte *)(DAT_0800112c + param_2) * 4))();
  return;
}



/* Address 080025ca; body bytes 48 */

void FUN_080025ca(byte *param_1,int param_2)

{
  param_1[0xe] = 0xf6;
  param_1[0xf] = 0xff;
  param_1[0xc] = *param_1 | 6;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
                    /* WARNING: Could not recover jumptable at 0x0800112a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(DAT_08001130 + *(int *)(param_1 + 4) * 0x2c +
              (uint)*(byte *)(DAT_0800112c + param_2) * 4))();
  return;
}



/* Address 080025fa; body bytes 44 */

void FUN_080025fa(byte *param_1,int param_2)

{
  param_1[0xf] = 0xf6;
  param_1[0xc] = *param_1 | 7;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
                    /* WARNING: Could not recover jumptable at 0x0800112a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(DAT_08001130 + *(int *)(param_1 + 4) * 0x2c +
              (uint)*(byte *)(DAT_0800112c + param_2) * 4))();
  return;
}



/* Address 0800266a; body bytes 22 */

void FUN_0800266a(int param_1,undefined param_2)

{
  *(undefined *)(param_1 + 0xf) = param_2;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 1;
  return;
}



/* Address 08002680; body bytes 22 */

void FUN_08002680(int param_1,undefined param_2)

{
  *(undefined *)(param_1 + 0xe) = param_2;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
  return;
}



/* Address 080026a6; body bytes 22 */

void FUN_080026a6(int param_1,undefined param_2)

{
  *(undefined *)(param_1 + 0xf) = param_2;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
  return;
}



/* Address 080026bc; body bytes 30 */

void FUN_080026bc(byte *param_1,byte param_2)

{
  param_1[0xf] = param_2;
  param_1[0xc] = *param_1 | 3;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
  return;
}



/* Address 080026ec; body bytes 22 */

void FUN_080026ec(int param_1,undefined param_2)

{
  *(undefined *)(param_1 + 0xf) = param_2;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 4;
  return;
}



/* Address 08002714; body bytes 32 */

void FUN_08002714(byte *param_1)

{
  param_1[0xd] = 0xf7;
  param_1[0xc] = *param_1 | 5;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
  return;
}



/* Address 08002734; body bytes 36 */

void FUN_08002734(byte *param_1)

{
  param_1[0xe] = 0xf7;
  param_1[0xf] = 0xff;
  param_1[0xc] = *param_1 | 6;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
  return;
}



/* Address 08002758; body bytes 32 */

void FUN_08002758(byte *param_1)

{
  param_1[0xf] = 0xf7;
  param_1[0xc] = *param_1 | 7;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
  return;
}



/* Address 08002790; body bytes 46 */

void FUN_08002790(byte *param_1,int param_2)

{
  param_1[0xe] = (byte)param_2;
  param_1[0xf] = 0xff;
  param_1[0xc] = *param_1 | 5;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
                    /* WARNING: Could not recover jumptable at 0x0800112a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(DAT_08001130 + *(int *)(param_1 + 4) * 0x2c +
              (uint)*(byte *)(DAT_0800112c + param_2) * 4))();
  return;
}



/* Address 080027be; body bytes 46 */

void FUN_080027be(byte *param_1,int param_2)

{
  param_1[0xe] = (byte)param_2;
  param_1[0xf] = 0xff;
  param_1[0xc] = *param_1 | 5;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
                    /* WARNING: Could not recover jumptable at 0x0800112a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(DAT_08001130 + *(int *)(param_1 + 4) * 0x2c +
              (uint)*(byte *)(DAT_0800112c + param_2) * 4))();
  return;
}



/* Address 080027ec; body bytes 34 */

void FUN_080027ec(byte *param_1,byte param_2)

{
  param_1[0xe] = param_2;
  param_1[0xf] = 0xff;
  param_1[0xc] = *param_1 | 5;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
  return;
}



/* Address 0800280e; body bytes 42 */

void FUN_0800280e(byte *param_1,int param_2)

{
  param_1[0xf] = (byte)param_2;
  param_1[0xc] = *param_1 | 2;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
                    /* WARNING: Could not recover jumptable at 0x0800112a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(DAT_08001130 + *(int *)(param_1 + 4) * 0x2c +
              (uint)*(byte *)(DAT_0800112c + param_2) * 4))();
  return;
}



/* Address 08002838; body bytes 42 */

void FUN_08002838(byte *param_1,int param_2)

{
  param_1[0xf] = (byte)param_2;
  param_1[0xc] = *param_1 | 2;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
                    /* WARNING: Could not recover jumptable at 0x0800112a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(DAT_08001130 + *(int *)(param_1 + 4) * 0x2c +
              (uint)*(byte *)(DAT_0800112c + param_2) * 4))();
  return;
}



/* Address 08002862; body bytes 30 */

void FUN_08002862(byte *param_1,byte param_2)

{
  param_1[0xf] = param_2;
  param_1[0xc] = *param_1 | 2;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
  return;
}



/* Address 080028a4; body bytes 38 */

void FUN_080028a4(byte *param_1)

{
  param_1[0xd] = 0xf6;
  param_1[0xe] = 0xff;
  param_1[0xf] = 0xff;
  param_1[0xc] = *param_1 | 5;
  if (*(code **)(param_1 + 8) != (code *)0x0) {
    (**(code **)(param_1 + 8))(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x18));
  }
  *(undefined4 *)(param_1 + 4) = 0;
  return;
}



/* Address 0800290c; body bytes 56 */

void FUN_0800290c(undefined4 param_1,int param_2)

{
  int iVar1;
  
  iVar1 = *(int *)(DAT_08002930 + param_2 * 4 + -4);
  if (iVar1 == 0) {
    return;
  }
  FUN_08002f50(iVar1,param_1);
  if (*DAT_08002f48 != '\0') {
    DAT_08002f48[1] = '\x01';
    return;
  }
  *DAT_08002f4c = 0x10000000;
  return;
}



/* Address 08002934; body bytes 66 */

void FUN_08002934(void)

{
  undefined4 *puVar1;
  
  FUN_08000c18();
  FUN_08000a36();
  FUN_08000884();
  FUN_08000638();
  FUN_08001354();
  FUN_08001094();
  puVar1 = DAT_08002978;
  *DAT_08002978 = 0x20;
  puVar1[-1] = 0x40000;
  puVar1[-1] = 0x2000000;
  FUN_08000870(DAT_0800297c,0x8000);
  FUN_080001cc();
  software_interrupt(0);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Address 0800298c; body bytes 32 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_0800298c(void)

{
  uint *puVar1;
  
  puVar1 = DAT_080029b0;
  _DAT_e000e014 = *DAT_080029ac;
  _DAT_e000e018 = 0;
  _DAT_e000e010 = 7;
  *DAT_080029b0 = *DAT_080029b0 | 0xff000000;
  return (int)puVar1 >> 0x1d;
}



/* Address 080029b6; body bytes 2 */

void FUN_080029b6(void)

{
  return;
}



/* Address 080029b8; body bytes 26 */

int FUN_080029b8(int *param_1)

{
  bool bVar1;
  int *piVar2;
  
  do {
    ExclusiveAccess(param_1);
    piVar2 = (int *)*param_1;
    if (piVar2 == (int *)0x0) {
      ClearExclusiveLocal();
      return 0;
    }
    bVar1 = (bool)hasExclusiveAccess(param_1);
  } while (!bVar1);
  *param_1 = *piVar2;
  return (int)piVar2;
}



/* Address 080029d4; body bytes 64 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_080029d4(uint param_1,undefined param_2)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_08002a04;
  if (param_1 == 0) {
    return;
  }
  if (param_1 < 0xffff) {
    FUN_08002fa8(*DAT_08002a04,param_1);
  }
  *(undefined *)(*piVar1 + 1) = param_2;
  iVar2 = FUN_08002be4(DAT_08002a08);
  piVar1 = DAT_08003140;
  DAT_08003140[1] = iVar2;
  *(undefined *)(iVar2 + 1) = 2;
  if ((*DAT_08003144 != '\0') && (piVar1[1] != *piVar1)) {
    do {
    } while (_DAT_e000007c == 0);
    _DAT_e000007c = CONCAT31(DAT_e000007c_1,*(undefined *)(iVar2 + 3));
    return;
  }
  return;
}



/* Address 08002a0c; body bytes 2 */

void FUN_08002a0c(void)

{
  return;
}



/* Address 08002a10; body bytes 106 */

void FUN_08002a10(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_08002a7c;
  if (*(int *)(DAT_08002a7c + 0xc) != 0) {
    *(short *)(DAT_08002a7c + 0x14) = *(short *)(DAT_08002a7c + 0x14) + -1;
    while ((*(short *)(iVar1 + 0x14) == 0 && (iVar2 = *(int *)(iVar1 + 0xc), iVar2 != 0))) {
      if (*(int *)(iVar2 + 8) != 0) {
        *(undefined4 *)(*(int *)(iVar2 + 8) + 4) = *(undefined4 *)(iVar2 + 4);
        if (*(int *)(iVar2 + 4) != 0) {
          *(undefined4 *)(*(int *)(iVar2 + 4) + 8) = *(undefined4 *)(iVar2 + 8);
          *(undefined4 *)(iVar2 + 4) = 0;
        }
        *(undefined4 *)(iVar2 + 8) = 0;
      }
      FUN_08002ff0(DAT_08002a7c + -0x18,iVar2);
      *(undefined2 *)(iVar1 + 0x14) = *(undefined2 *)(iVar2 + 0x14);
      if (*(char *)(iVar2 + 1) == '\x04') {
        *(short *)(iVar2 + 0x14) = *(short *)(iVar2 + 0x16) + *DAT_08002a80;
      }
      *(undefined *)(iVar2 + 1) = 1;
      *(undefined *)(iVar2 + 0x20) = 1;
      *(undefined4 *)(iVar1 + 0xc) = *(undefined4 *)(iVar2 + 0xc);
      if (*(int *)(iVar2 + 0xc) != 0) {
        *(int *)(*(int *)(iVar2 + 0xc) + 0x10) = iVar1;
        *(undefined4 *)(iVar2 + 0xc) = 0;
      }
      *(undefined4 *)(iVar2 + 0x10) = 0;
    }
  }
  return;
}



/* Address 08002a84; body bytes 60 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08002a84(int param_1)

{
  int *piVar1;
  
  piVar1 = DAT_08002ac0;
  if (param_1 == 0) {
    param_1 = FUN_08002be4(DAT_08002ac4);
  }
  else {
    if (*(byte *)(param_1 + 2) <= *(byte *)(*DAT_08002ac0 + 2)) {
      *(undefined *)(param_1 + 1) = 1;
      FUN_08002ff0(DAT_08002ac4,param_1);
      return;
    }
    FUN_08003028();
    *(undefined *)(*piVar1 + 1) = 1;
  }
  piVar1 = DAT_08003140;
  DAT_08003140[1] = param_1;
  *(undefined *)(param_1 + 1) = 2;
  if ((*DAT_08003144 != '\0') && (piVar1[1] != *piVar1)) {
    do {
    } while (_DAT_e000007c == 0);
    _DAT_e000007c = CONCAT31(DAT_e000007c_1,*(undefined *)(param_1 + 3));
    return;
  }
  return;
}



/* Address 08002adc; body bytes 72 */

void FUN_08002adc(int param_1,ushort param_2)

{
  ushort uVar1;
  
  param_2 = *(ushort *)(param_1 + 0x18) | param_2;
  *(ushort *)(param_1 + 0x18) = param_2;
  uVar1 = *(ushort *)(param_1 + 0x1a);
  if (*(char *)(param_1 + 1) == '\x06') {
    if ((uVar1 & ~param_2) != 0) {
      return;
    }
  }
  else {
    if ((*(char *)(param_1 + 1) != '\x05') || ((param_2 & uVar1) == 0)) {
      return;
    }
    *(ushort *)(param_1 + 0x1a) = uVar1 & param_2;
  }
  *(ushort *)(param_1 + 0x18) = param_2 & ~uVar1;
  FUN_08003070(param_1);
  *(undefined *)(param_1 + 1) = 1;
  *(undefined *)(param_1 + 0x20) = 2;
  FUN_08002ff0(DAT_08002b24,param_1);
  return;
}



/* Address 08002b88; body bytes 56 */

undefined4 FUN_08002b88(uint param_1,undefined4 param_2,int param_3)

{
  ushort uVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  
  iVar4 = *DAT_08002bc0;
  uVar1 = *(ushort *)(iVar4 + 0x18);
  if (param_3 == 0) {
    uVar3 = uVar1 & param_1;
    if (uVar3 != 0) {
      *(short *)(iVar4 + 0x1a) = (short)uVar3;
      goto LAB_08002ba0;
    }
    uVar2 = 5;
  }
  else {
    if ((param_1 & ~(uint)uVar1) == 0) {
LAB_08002ba0:
      *(ushort *)(iVar4 + 0x18) = uVar1 & ~(ushort)param_1;
      return 2;
    }
    uVar2 = 6;
  }
  *(ushort *)(iVar4 + 0x1a) = (ushort)param_1;
  FUN_080029d4(param_2,uVar2);
  return 1;
}



/* Address 08002bc4; body bytes 32 */

undefined4 FUN_08002bc4(uint *param_1,uint *param_2)

{
  bool bVar1;
  
  if ((param_1 <= param_2) && (param_2 < param_1[1])) {
    do {
      ExclusiveAccess(param_1);
      *param_2 = *param_1;
      bVar1 = (bool)hasExclusiveAccess(param_1);
    } while (!bVar1);
    *param_1 = (uint)param_2;
    return 0;
  }
  return 1;
}



/* Address 08002be4; body bytes 40 */

void FUN_08002be4(char *param_1)

{
  char cVar1;
  int iVar2;
  
  iVar2 = *(int *)(param_1 + 4);
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)(iVar2 + 4);
  cVar1 = *param_1;
  if (((cVar1 != '\x02') && (cVar1 != '\x01')) && (cVar1 != '\x03')) {
    *(undefined4 *)(iVar2 + 4) = 0;
    return;
  }
  if (*(int *)(iVar2 + 4) != 0) {
    *(char **)(*(int *)(iVar2 + 4) + 8) = param_1;
    *(undefined4 *)(iVar2 + 4) = 0;
  }
  *(undefined4 *)(iVar2 + 8) = 0;
  return;
}



/* Address 08002c0c; body bytes 134 */

void FUN_08002c0c(undefined *param_1,undefined param_2,undefined4 param_3)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  
  *param_1 = 0;
  param_1[1] = 1;
  param_1[2] = param_2;
  *(undefined4 *)(param_1 + 4) = 0;
  *(undefined4 *)(param_1 + 8) = 0;
  *(undefined4 *)(param_1 + 0xc) = 0;
  *(undefined4 *)(param_1 + 0x10) = 0;
  *(undefined2 *)(param_1 + 0x14) = 0;
  *(undefined2 *)(param_1 + 0x16) = 0;
  *(undefined2 *)(param_1 + 0x18) = 0;
  *(undefined2 *)(param_1 + 0x1a) = 0;
  param_1[0x20] = 0;
  param_1[0x21] = 0;
  if (*(short *)(param_1 + 0x22) == 0) {
    uVar1 = FUN_080029b8(DAT_08002c4c);
    *(undefined4 *)(param_1 + 0x28) = uVar1;
  }
  uVar2 = (uint)(*(ushort *)(param_1 + 0x22) >> 2);
  if (uVar2 == 0) {
    uVar2 = ((uint)*DAT_08002c9c << 0x10) >> 0x12;
  }
  iVar3 = *(int *)(param_1 + 0x28) + uVar2 * 4;
  if (iVar3 * 0x20000000 < 0) {
    iVar3 = iVar3 + -4;
  }
  *(undefined4 *)(iVar3 + -8) = param_3;
  *(undefined4 *)(iVar3 + -4) = 0x1000000;
  uVar2 = 0;
  do {
    *(undefined4 *)(iVar3 + -0x40 + uVar2 * 4) = 0;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 0xe);
  *(undefined4 *)(iVar3 + -0x20) = *(undefined4 *)(param_1 + 0x1c);
  *(int *)(param_1 + 0x24) = iVar3 + -0x40;
  *(undefined4 *)(param_1 + 0x2c) = param_3;
  **(undefined4 **)(param_1 + 0x28) = DAT_08002ca0;
  return;
}



/* Address 08002c50; body bytes 2 */

void FUN_08002c50(void)

{
  return;
}



/* Address 08002ce8; body bytes 190 */

void FUN_08002ce8(int param_1,undefined4 param_2)

{
  bool bVar1;
  int iVar2;
  short sVar3;
  short *psVar4;
  
  psVar4 = (short *)(param_1 + 0xc);
  if (*(int *)(param_1 + 4) != 0) {
    if (*(char *)(param_1 + 1) == '\x02') {
      *(undefined *)(param_1 + 1) = 0;
      iVar2 = FUN_08002be4(param_1);
      *(undefined *)(iVar2 + 0x20) = 0;
      *(undefined4 *)(param_1 + (uint)*(ushort *)(param_1 + 8) * 4 + 0x10) =
           *(undefined4 *)(iVar2 + 0x1c);
      do {
        ExclusiveAccess(psVar4);
        bVar1 = (bool)hasExclusiveAccess(psVar4);
      } while (!bVar1);
      *psVar4 = *psVar4 + 1;
      sVar3 = *(short *)(param_1 + 8) + 1;
      *(short *)(param_1 + 8) = sVar3;
      if (sVar3 == *(short *)(param_1 + 0xe)) {
        *(undefined2 *)(param_1 + 8) = 0;
      }
    }
    else {
      if (*(short *)(param_1 + 0xc) != 0) goto LAB_08002d04;
      iVar2 = FUN_08002be4(param_1);
      **(undefined4 **)(iVar2 + 0x1c) = param_2;
      *(undefined *)(iVar2 + 0x20) = 4;
    }
    *(undefined *)(iVar2 + 1) = 1;
    FUN_08003070(iVar2);
    FUN_08002ff0(DAT_08002da4,iVar2);
    return;
  }
LAB_08002d04:
  if (*(ushort *)(param_1 + 0xc) < *(ushort *)(param_1 + 0xe)) {
    *(undefined4 *)(param_1 + (uint)*(ushort *)(param_1 + 8) * 4 + 0x10) = param_2;
    do {
      ExclusiveAccess(psVar4);
      bVar1 = (bool)hasExclusiveAccess(psVar4);
    } while (!bVar1);
    *psVar4 = *psVar4 + 1;
    sVar3 = *(short *)(param_1 + 8) + 1;
    *(short *)(param_1 + 8) = sVar3;
    if (sVar3 == *(short *)(param_1 + 0xe)) {
      *(undefined2 *)(param_1 + 8) = 0;
    }
    return;
  }
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Address 08002da8; body bytes 164 */

undefined4 FUN_08002da8(int param_1)

{
  byte bVar1;
  short sVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  
  piVar3 = DAT_08002e4c;
  sVar2 = *(short *)(param_1 + 2);
  if ((sVar2 == 0) || (*(int *)(param_1 + 8) != *DAT_08002e4c)) {
    return 0xff;
  }
  *(short *)(param_1 + 2) = sVar2 + -1;
  iVar4 = DAT_08002e50;
  if (sVar2 != 1) {
    return 0;
  }
  bVar1 = *(byte *)(param_1 + 1);
  *(byte *)(*piVar3 + 2) = bVar1;
  if (*(int *)(param_1 + 4) == 0) {
    if (*(byte *)(*(int *)(iVar4 + 4) + 2) <= bVar1) {
      return 0;
    }
    FUN_08002ff0(DAT_08002e50);
    *(undefined *)(*piVar3 + 1) = 1;
  }
  else {
    iVar5 = FUN_08002be4(param_1);
    *(undefined *)(iVar5 + 0x20) = 5;
    FUN_08003070(iVar5);
    *(undefined2 *)(param_1 + 2) = 1;
    *(int *)(param_1 + 8) = iVar5;
    *(undefined *)(param_1 + 1) = *(undefined *)(iVar5 + 2);
    if (*(byte *)(*(int *)(iVar4 + 4) + 2) <= *(byte *)(*piVar3 + 2)) goto LAB_08002e24;
    FUN_08002ff0(DAT_08002e50);
    FUN_08002ff0(DAT_08002e50,iVar5);
    *(undefined *)(*piVar3 + 1) = 1;
    *(undefined *)(iVar5 + 1) = 1;
  }
  iVar5 = 0;
LAB_08002e24:
  FUN_08002a84(iVar5);
  *(undefined *)(*piVar3 + 0x20) = 0;
  return 0;
}



/* Address 08002e54; body bytes 96 */

undefined4 FUN_08002e54(int param_1,int param_2)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_08002eb4;
  iVar2 = *DAT_08002eb4;
  if (*(short *)(param_1 + 2) == 0) {
    *(int *)(param_1 + 8) = iVar2;
    *(undefined *)(param_1 + 1) = *(undefined *)(iVar2 + 2);
  }
  else if (*(int *)(param_1 + 8) != iVar2) {
    if (param_2 != 0) {
      if (*(byte *)(param_1 + 1) < *(byte *)(iVar2 + 2)) {
        *(byte *)(*(int *)(param_1 + 8) + 2) = *(byte *)(iVar2 + 2);
        FUN_0800303c(*(undefined4 *)(param_1 + 8));
      }
      if (*(int *)(param_1 + 4) == 0) {
        *(int *)(param_1 + 4) = *piVar1;
        iVar2 = *piVar1;
        *(undefined4 *)(iVar2 + 4) = 0;
        *(int *)(iVar2 + 8) = param_1;
      }
      else {
        FUN_08002ff0(param_1,*piVar1);
      }
      FUN_080029d4(param_2,9);
    }
    return 1;
  }
  *(short *)(param_1 + 2) = *(short *)(param_1 + 2) + 1;
  return 0;
}



/* Address 08002eb8; body bytes 136 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08002eb8(void)

{
  bool bVar1;
  int *piVar2;
  char *pcVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  *(undefined *)(*DAT_08002f24 + 1) = 1;
  FUN_08003028();
  iVar4 = DAT_08002f28;
  uVar6 = (uint)*(byte *)(DAT_08002f28 + 1);
  while (*(char *)(iVar4 + 2) != '\0') {
    iVar5 = iVar4 + uVar6 * 8;
    pcVar3 = *(char **)(iVar5 + 4);
    if (*pcVar3 == '\0') {
      FUN_08002adc(pcVar3,*(undefined2 *)(iVar5 + 8));
    }
    else if (*pcVar3 == '\x01') {
      FUN_08002ce8(pcVar3,*(undefined4 *)(iVar5 + 8));
    }
    else {
      FUN_080030c8();
    }
    uVar6 = uVar6 + 1;
    if (uVar6 == *(byte *)(iVar4 + 3)) {
      uVar6 = 0;
    }
    pcVar3 = (char *)(DAT_08002f28 + 2);
    do {
      ExclusiveAccess(pcVar3);
      bVar1 = (bool)hasExclusiveAccess(pcVar3);
    } while (!bVar1);
    *pcVar3 = *pcVar3 + -1;
  }
  *(char *)(iVar4 + 1) = (char)uVar6;
  iVar4 = FUN_08002be4(DAT_08002f2c);
  piVar2 = DAT_08003140;
  DAT_08003140[1] = iVar4;
  *(undefined *)(iVar4 + 1) = 2;
  if ((*DAT_08003144 != '\0') && (piVar2[1] != *piVar2)) {
    do {
    } while (_DAT_e000007c == 0);
    _DAT_e000007c = CONCAT31(DAT_e000007c_1,*(undefined *)(iVar4 + 3));
    return;
  }
  return;
}



/* Address 08002f50; body bytes 82 */

void FUN_08002f50(undefined4 param_1,undefined4 param_2)

{
  byte *pbVar1;
  bool bVar2;
  byte *pbVar3;
  uint uVar4;
  byte *pbVar5;
  uint uVar6;
  
  pbVar3 = DAT_08002fa4;
  pbVar5 = DAT_08002fa4 + 2;
  pbVar1 = DAT_08002fa4 + 3;
  do {
    ExclusiveAccess(pbVar5);
    uVar4 = (uint)*pbVar5;
    if (uVar4 == *pbVar1) {
      ClearExclusiveLocal();
      goto LAB_08002f88;
    }
    bVar2 = (bool)hasExclusiveAccess(pbVar5);
  } while (!bVar2);
  *pbVar5 = *pbVar5 + 1;
  do {
    ExclusiveAccess(pbVar3);
    uVar4 = (uint)*pbVar3;
    uVar6 = uVar4 + 1;
    if (uVar6 == *pbVar1) {
      uVar6 = 0;
    }
    bVar2 = (bool)hasExclusiveAccess(pbVar3);
  } while (!bVar2);
  *pbVar3 = (byte)uVar6;
LAB_08002f88:
  if (uVar4 < pbVar3[3]) {
    *(undefined4 *)(pbVar3 + uVar4 * 8 + 4) = param_1;
    *(undefined4 *)(pbVar3 + uVar4 * 8 + 8) = param_2;
    return;
  }
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Address 08002fa8; body bytes 68 */

void FUN_08002fa8(int param_1,uint param_2)

{
  short sVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  uVar3 = *(uint *)(DAT_08002fec + 0xc);
  iVar2 = DAT_08002fec;
  if (uVar3 != 0) {
    uVar3 = (uint)*(ushort *)(DAT_08002fec + 0x14);
    while( true ) {
      iVar4 = *(int *)(iVar2 + 0xc);
      if (param_2 <= uVar3) {
        *(int *)(param_1 + 0xc) = iVar4;
        *(int *)(iVar2 + 0xc) = param_1;
        *(int *)(param_1 + 0x10) = iVar2;
        if (*(int *)(param_1 + 0xc) != 0) {
          *(int *)(*(int *)(param_1 + 0xc) + 0x10) = param_1;
        }
        sVar1 = (short)uVar3 - (short)param_2;
        *(short *)(param_1 + 0x14) = sVar1;
        *(short *)(iVar2 + 0x14) = *(short *)(iVar2 + 0x14) - sVar1;
        return;
      }
      if (iVar4 == 0) break;
      uVar3 = uVar3 + *(ushort *)(iVar4 + 0x14);
      iVar2 = iVar4;
    }
  }
  *(undefined4 *)(param_1 + 0xc) = 0;
  *(int *)(iVar2 + 0xc) = param_1;
  *(int *)(param_1 + 0x10) = iVar2;
  *(short *)(iVar2 + 0x14) = (short)param_2 - (short)uVar3;
  *(undefined2 *)(param_1 + 0x14) = 0;
  return;
}



/* Address 08002ff0; body bytes 54 */

void FUN_08002ff0(char *param_1,int param_2)

{
  char cVar1;
  bool bVar2;
  char *pcVar3;
  
  cVar1 = *param_1;
  bVar2 = false;
  if (((cVar1 == '\x02') || (cVar1 == '\x01')) || (cVar1 == '\x03')) {
    bVar2 = true;
  }
  do {
    pcVar3 = param_1;
    param_1 = *(char **)(pcVar3 + 4);
    if (param_1 == (char *)0x0) break;
  } while (*(byte *)(param_2 + 2) <= (byte)param_1[2]);
  *(char **)(param_2 + 4) = param_1;
  *(int *)(pcVar3 + 4) = param_2;
  if (bVar2) {
    if (param_1 != (char *)0x0) {
      *(int *)(param_1 + 8) = param_2;
    }
  }
  else {
    pcVar3 = (char *)0x0;
  }
  *(char **)(param_2 + 8) = pcVar3;
  return;
}



/* Address 08003028; body bytes 14 */

void FUN_08003028(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_08003038;
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)(DAT_08003038 + 4);
  *(undefined4 *)(param_1 + 8) = 0;
  *(int *)(iVar1 + 4) = param_1;
  return;
}



/* Address 0800303c; body bytes 46 */

void FUN_0800303c(int param_1,undefined4 param_2,undefined4 param_3)

{
  char *pcVar1;
  
  pcVar1 = *(char **)(param_1 + 8);
  if (pcVar1 == (char *)0x0) {
    pcVar1 = DAT_0800306c;
    if (*(char *)(param_1 + 1) != '\x01') {
      return;
    }
  }
  else {
    for (; *pcVar1 == '\0'; pcVar1 = *(char **)(pcVar1 + 8)) {
    }
  }
  FUN_08003098(param_1,param_2,param_3,pcVar1);
  FUN_08002ff0(pcVar1,param_1);
  return;
}



/* Address 08003070; body bytes 40 */

void FUN_08003070(int param_1)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 0x10);
  if (iVar1 != 0) {
    *(undefined4 *)(iVar1 + 0xc) = *(undefined4 *)(param_1 + 0xc);
    if (*(int *)(param_1 + 0xc) == 0) {
      *(undefined2 *)(iVar1 + 0x14) = 0;
    }
    else {
      *(short *)(iVar1 + 0x14) = *(short *)(iVar1 + 0x14) + *(short *)(param_1 + 0x14);
      *(int *)(*(int *)(param_1 + 0xc) + 0x10) = iVar1;
      *(undefined4 *)(param_1 + 0xc) = 0;
    }
    *(undefined4 *)(param_1 + 0x10) = 0;
  }
  return;
}



/* Address 08003098; body bytes 44 */

void FUN_08003098(int param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_080030c4;
  if (*(int *)(param_1 + 8) != 0) {
    *(undefined4 *)(*(int *)(param_1 + 8) + 4) = *(undefined4 *)(param_1 + 4);
    if (*(int *)(param_1 + 4) != 0) {
      *(undefined4 *)(*(int *)(param_1 + 4) + 8) = *(undefined4 *)(param_1 + 8);
    }
    return;
  }
  do {
    iVar2 = iVar1;
    if (iVar2 == 0) {
      return;
    }
    iVar1 = *(int *)(iVar2 + 4);
  } while (*(int *)(iVar2 + 4) != param_1);
  *(undefined4 *)(iVar2 + 4) = *(undefined4 *)(param_1 + 4);
  return;
}



/* Address 080030c8; body bytes 46 */

void FUN_080030c8(int param_1)

{
  int iVar1;
  
  if (*(int *)(param_1 + 4) != 0) {
    iVar1 = FUN_08002be4();
    FUN_08003070();
    *(undefined *)(iVar1 + 1) = 1;
    *(undefined *)(iVar1 + 0x20) = 3;
    FUN_08002ff0(DAT_080030f8,iVar1);
    return;
  }
  *(short *)(param_1 + 2) = *(short *)(param_1 + 2) + 1;
  return;
}



/* Address 080030fc; body bytes 28 */

void FUN_080030fc(void)

{
  int *piVar1;
  
  piVar1 = *(int **)(*DAT_08003118 + 0x28);
  if ((piVar1 <= *(int **)(*DAT_08003118 + 0x24)) && (*piVar1 == DAT_0800311c)) {
    return;
  }
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



/* Address 08003148; body bytes 266 */

void FUN_08003148(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  ushort *puVar2;
  undefined4 uVar3;
  undefined *puVar4;
  undefined *puVar5;
  uint *puVar6;
  uint uVar7;
  uint uVar8;
  
  FUN_08002480();
  puVar2 = DAT_08003258;
  iVar1 = DAT_08003254;
  for (uVar7 = 0; uVar7 < *puVar2; uVar7 = uVar7 + 1) {
    *(undefined4 *)(iVar1 + uVar7 * 4) = 0;
  }
  FUN_080023fc(DAT_08003260,*DAT_0800325c,0x30);
  FUN_080023fc(DAT_0800326c,*DAT_08003268,*DAT_08003264 | 0x80000000);
  FUN_080023fc(*DAT_08003274,*DAT_08003270,8);
  uVar3 = DAT_0800327c;
  iVar1 = DAT_08003278;
  *(undefined *)(DAT_08003278 + 3) = 0xff;
  *(undefined2 *)(iVar1 + 0x22) = 0;
  FUN_08002c0c(iVar1,0,uVar3);
  puVar4 = DAT_08003280;
  *DAT_08003280 = 4;
  *(undefined4 *)(puVar4 + 4) = 0;
  puVar4 = DAT_08003284;
  *DAT_08003284 = 4;
  *(undefined4 *)(puVar4 + 0xc) = 0;
  *(undefined4 *)(puVar4 + 0x10) = 0;
  *(undefined2 *)(puVar4 + 0x14) = 0;
  FUN_080001c0(*(int *)(iVar1 + 0x24) + 0x20);
  puVar5 = DAT_08003290;
  *DAT_08003288 = iVar1;
  *(undefined *)(iVar1 + 1) = 2;
  puVar4 = DAT_0800328c;
  *DAT_0800328c = 0;
  puVar4[1] = 0;
  puVar4[3] = *puVar5;
  FUN_08002c50();
  puVar6 = DAT_08003294;
  *DAT_08003294 = *DAT_08003294 | 0xff0000;
  uVar7 = 8 - LZCOUNT(~((*puVar6 & 0xff0000) << 8));
  uVar8 = (DAT_08003294[-5] << 0x15) >> 0x1d;
  if ((int)uVar7 <= (int)uVar8) {
    uVar7 = uVar8 + 1;
  }
  DAT_08003294[-1] = -0x1000001 << (uVar7 & 0xff) & 0xff000000U | DAT_08003294[-1] & 0xffffff;
  uVar7 = FUN_0800298c();
  *DAT_08003298 = uVar7;
  if (-1 < (int)uVar7) {
    *(undefined *)(uVar7 + DAT_0800329c) = 0xff;
    *(int *)(&DAT_e000e100 + ((int)uVar7 >> 5) * 4) = 1 << (uVar7 & 0x1f);
  }
  FUN_0800331c(param_1,param_2,param_3,0);
  return;
}



/* Address 080032a0; body bytes 48 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_080032a0(void)

{
  int *piVar1;
  int iVar2;
  
  *(undefined *)(*DAT_080032d0 + 1) = 1;
  FUN_08003028();
  FUN_08002a0c();
  *DAT_080032d4 = *DAT_080032d4 + 1;
  FUN_08002a10();
  FUN_080032dc();
  iVar2 = FUN_08002be4(DAT_080032d8);
  piVar1 = DAT_08003140;
  DAT_08003140[1] = iVar2;
  *(undefined *)(iVar2 + 1) = 2;
  if ((*DAT_08003144 != '\0') && (piVar1[1] != *piVar1)) {
    do {
    } while (_DAT_e000007c == 0);
    _DAT_e000007c = CONCAT31(DAT_e000007c_1,*(undefined *)(iVar2 + 3));
    return;
  }
  return;
}



/* Address 080032dc; body bytes 56 */

void FUN_080032dc(void)

{
  int **ppiVar1;
  undefined4 *puVar2;
  int *piVar3;
  
  puVar2 = DAT_08003318;
  ppiVar1 = DAT_08003314;
  if (*DAT_08003314 != (int *)0x0) {
    *(short *)(DAT_08003314 + 1) = *(short *)(DAT_08003314 + 1) + -1;
    while ((*(short *)(ppiVar1 + 1) == 0 && (piVar3 = *ppiVar1, piVar3 != (int *)0x0))) {
      FUN_080029b6(*(undefined2 *)((int)piVar3 + 6));
      *(undefined2 *)(ppiVar1 + 1) = *(undefined2 *)(piVar3 + 1);
      *ppiVar1 = (int *)*piVar3;
      FUN_08002bc4(*puVar2,piVar3);
    }
  }
  return;
}



/* Address 0800331c; body bytes 124 */

uint FUN_0800331c(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  uint uVar2;
  uint uVar3;
  
  if ((param_2 & 0xff) == 0) {
    param_2 = param_2 + 1;
  }
  uVar2 = FUN_080029b8(DAT_0800339c);
  uVar3 = uVar2;
  if (uVar2 != 0) {
    *(undefined4 *)(uVar2 + 0x28) = param_3;
    *(short *)(uVar2 + 0x22) = (short)(param_2 >> 8);
    *(undefined4 *)(uVar2 + 0x1c) = param_4;
    FUN_08002c0c(uVar2,param_2 & 0xff,param_1);
    for (uVar3 = 1; uVar3 <= *DAT_080033a4; uVar3 = uVar3 + 1) {
      if (*(int *)(DAT_080033a0 + uVar3 * 4 + -4) == 0) goto LAB_0800336c;
    }
    uVar3 = 0;
LAB_0800336c:
    *(uint *)(DAT_080033a0 + uVar3 * 4 + -4) = uVar2;
    pcVar1 = DAT_080033a8;
    *(char *)(uVar2 + 3) = (char)uVar3;
    if (*pcVar1 != '\0') {
      FUN_080024b0(uVar2,1);
    }
    FUN_08002a84(uVar2);
    *(char *)(*DAT_080033ac + 0x20) = (char)uVar3;
  }
  return uVar3;
}



/* Address 080033b0; body bytes 162 */

undefined4 FUN_080033b0(uint param_1)

{
  char *pcVar1;
  int *piVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = DAT_0800345c;
  piVar2 = DAT_08003458;
  pcVar1 = DAT_08003454;
  if ((param_1 == 0) || (*(byte *)(*DAT_08003458 + 3) == param_1)) {
    *(undefined *)(*DAT_08003458 + 1) = 0;
    uVar3 = FUN_080001c6();
    *(undefined4 *)(*piVar2 + 0x24) = uVar3;
    FUN_080030fc();
    iVar4 = *piVar2;
    *(undefined4 *)(iVar5 + (uint)*(byte *)(iVar4 + 3) * 4 + -4) = 0;
    FUN_08002bc4(DAT_08003460,*(undefined4 *)(iVar4 + 0x28));
    iVar5 = *piVar2;
    *(undefined4 *)(iVar5 + 0x28) = 0;
    if (*pcVar1 != '\0') {
      FUN_080024b0(iVar5,0);
    }
    FUN_08002bc4(DAT_08003464,*piVar2);
    *piVar2 = 0;
    FUN_08002a84(0);
LAB_08003448:
    uVar3 = 0;
  }
  else {
    if (param_1 <= *DAT_08003468) {
      iVar4 = DAT_0800345c + param_1 * 4;
      iVar5 = *(int *)(iVar4 + -4);
      if (iVar5 != 0) {
        FUN_08003098(iVar5);
        FUN_08003070(iVar5);
        *(undefined4 *)(iVar4 + -4) = 0;
        FUN_08002bc4(DAT_08003460,*(undefined4 *)(iVar5 + 0x28));
        *(undefined4 *)(iVar5 + 0x28) = 0;
        if (*pcVar1 != '\0') {
          FUN_080024b0(iVar5,0);
        }
        FUN_08002bc4(DAT_08003464,iVar5);
        goto LAB_08003448;
      }
    }
    uVar3 = 0xff;
  }
  return uVar3;
}



/* Address 0800346c; body bytes 12 */

uint FUN_0800346c(void)

{
  uint uVar1;
  
  uVar1 = *DAT_08003478;
  if (uVar1 != 0) {
    uVar1 = (uint)*(byte *)(uVar1 + 3);
  }
  return uVar1;
}



/* Address 0800347c; body bytes 76 */

void FUN_0800347c(int *param_1)

{
  byte bVar1;
  int iVar2;
  
  iVar2 = FUN_08001206(param_1[0x12],0x727);
  if (iVar2 == 0) {
    return;
  }
  if (param_1[1] == *param_1) {
    FUN_08001248(param_1[0x12],0x727,0);
    return;
  }
  bVar1 = *(byte *)((int)param_1 + param_1[1] + 8);
  if (param_1[1] < 0x3f) {
    iVar2 = param_1[1] + 1;
  }
  else {
    iVar2 = 0;
  }
  param_1[1] = iVar2;
  *(ushort *)(param_1[0x12] + 4) = (ushort)(((uint)bVar1 << 0x17) >> 0x17);
  return;
}



/* Address 080034fc; body bytes 52 */

void FUN_080034fc(int param_1)

{
  byte bVar1;
  int iVar2;
  bool bVar3;
  
  iVar2 = *(int *)(param_1 + 0x14);
  if (iVar2 == 0) {
    return;
  }
  FUN_0800086c(*(undefined4 *)(iVar2 + (uint)*(byte *)(param_1 + 0x18) * 8),
               *(undefined2 *)(iVar2 + (uint)*(byte *)(param_1 + 0x18) * 8 + 4));
  *(char *)(param_1 + 0x18) = *(char *)(param_1 + 0x19);
  bVar1 = *(char *)(param_1 + 0x19) + 1;
  *(byte *)(param_1 + 0x19) = bVar1;
  bVar3 = 3 < bVar1;
  if (bVar3) {
    bVar1 = 0;
  }
  if (bVar3) {
    *(byte *)(param_1 + 0x19) = bVar1;
  }
  return;
}



/* Address 0800355c; body bytes 88 */

void FUN_0800355c(undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  *param_1 = DAT_080035b4;
  param_1[1] = param_3;
  *(undefined *)(param_1 + 2) = 1;
  *(undefined *)((int)param_1 + 9) = 0;
  param_1[3] = 0;
  param_1[4] = 0;
  iVar4 = *(int *)(param_2 + 4);
  if (iVar4 == 0) {
    param_1[3] = param_1;
    param_1[4] = param_1;
    *(undefined4 **)(param_2 + 4) = param_1;
  }
  else {
    iVar2 = *(int *)(iVar4 + 0xc);
    param_1[3] = iVar2;
    param_1[4] = iVar4;
    *(undefined4 **)(iVar4 + 0xc) = param_1;
    *(undefined4 **)(iVar2 + 0x10) = param_1;
  }
  uVar1 = DAT_080035b8;
  param_1[5] = param_4;
  *param_1 = uVar1;
  *(undefined *)(param_1 + 6) = 0;
  *(undefined *)((int)param_1 + 0x19) = 0;
  uVar3 = 0;
  do {
    iVar4 = uVar3 * 2;
    uVar3 = uVar3 + 1;
    *(undefined2 *)((int)param_1 + iVar4 + 0x1a) = 0xffff;
  } while (uVar3 < 4);
  return;
}



/* Address 080035bc; body bytes 188 */

void FUN_080035bc(code **param_1)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  code *pcVar5;
  uint uVar6;
  
  uVar6 = 0;
  if (*(char *)((int)param_1 + 0x11) != '\0') {
    do {
      iVar2 = FUN_08000850(*(undefined4 *)(param_1[3] + uVar6 * 8),
                           *(undefined2 *)(param_1[3] + uVar6 * 8 + 4));
      iVar4 = (uint)*(byte *)((int)param_1 + 0x12) * (uint)*(byte *)((int)param_1 + 0x11) + uVar6;
      if ((bool)*(char *)((int)param_1 + iVar4 + 0x13) == (iVar2 != 0)) {
        param_1[iVar4 + 0xe] = (code *)0x0;
      }
      else {
        pcVar5 = (code *)((int)param_1[iVar4 + 0xe] << 1 | 1);
        param_1[iVar4 + 0xe] = pcVar5;
        uVar3 = 0xf;
        do {
          if (((uint)pcVar5 >> (uVar3 & 0xff) & 1) == 0) {
            return;
          }
          uVar3 = uVar3 - 1;
        } while (-1 < (int)uVar3);
        *(bool *)((int)param_1 + iVar4 + 0x13) = iVar2 != 0;
        if (*param_1 != (code *)0x0) {
          (**param_1)((uint)*(byte *)(param_1 + 1) + iVar4);
        }
      }
      uVar6 = uVar6 + 1;
    } while (uVar6 < *(byte *)((int)param_1 + 0x11));
  }
  FUN_08000870(*(undefined4 *)(param_1[2] + (uint)*(byte *)((int)param_1 + 0x12) * 8),
               *(undefined2 *)(param_1[2] + (uint)*(byte *)((int)param_1 + 0x12) * 8 + 4));
  bVar1 = *(char *)((int)param_1 + 0x12) + 1;
  *(byte *)((int)param_1 + 0x12) = bVar1;
  if (*(byte *)(param_1 + 4) <= bVar1) {
    *(undefined *)((int)param_1 + 0x12) = 0;
  }
  FUN_0800086c(*(undefined4 *)(param_1[2] + (uint)*(byte *)((int)param_1 + 0x12) * 8),
               *(undefined2 *)(param_1[2] + (uint)*(byte *)((int)param_1 + 0x12) * 8 + 4));
  return;
}



/* Address 08003678; body bytes 84 */

int FUN_08003678(int param_1,undefined param_2,undefined4 param_3,undefined4 param_4,
                undefined param_5,undefined param_6)

{
  int iVar1;
  uint uVar2;
  
  *(undefined *)(param_1 + 4) = param_2;
  *(undefined4 *)(param_1 + 8) = param_3;
  *(undefined4 *)(param_1 + 0xc) = param_4;
  *(undefined *)(param_1 + 0x10) = param_5;
  uVar2 = 0;
  *(undefined *)(param_1 + 0x11) = param_6;
  *(undefined *)(param_1 + 0x12) = 0;
  do {
    *(undefined *)(param_1 + uVar2 + 0x13) = 1;
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(param_1 + iVar1 + 0x38) = 1;
  } while (uVar2 < 0x24);
  uVar2 = 0;
  if (*(char *)(param_1 + 0x10) != '\0') {
    do {
      FUN_08000870(*(undefined4 *)(*(int *)(param_1 + 8) + uVar2 * 8),
                   *(undefined2 *)(*(int *)(param_1 + 8) + uVar2 * 8 + 4));
      uVar2 = uVar2 + 1;
    } while (uVar2 < *(byte *)(param_1 + 0x10));
  }
  return param_1;
}


