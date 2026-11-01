/* SELECTED ORIGINAL UPDATER ROUTINES: automatic Ghidra pseudocode, not recompilable source.
   See research/container.md for evidence, interpretations, and emulation scope. */

/* Address 600051d0; body bytes 42 */

bool FUN_600051d0(int param_1,undefined4 param_2,int param_3)

{
  int iVar1;
  
  iVar1 = FUN_6002173c(param_1 * param_3 + 0x3000000,param_2,param_3);
  return iVar1 == 0;
}




/* Address 600051fa; body bytes 56 */

void FUN_600051fa(int param_1,undefined4 param_2,int param_3)

{
  FUN_60003278(0);
  FUN_60003350();
  FUN_600034b6(param_1 * param_3);
  FUN_6000342c(param_1 * param_3,param_3,param_2);
  FUN_60003278(3);
  FUN_600032f8();
  return;
}




/* Address 60005232; body bytes 182 */

undefined8 FUN_60005232(int param_1,byte *param_2,int *param_3,byte *param_4,uint param_5)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  byte *local_40;
  uint local_3c;
  
  FUN_60003278(0);
  FUN_60003478(param_1,0x40,param_4);
  FUN_60003278(3);
  local_40 = param_2;
  if ((*DAT_60005560 == '\0') && (iVar1 = FUN_6002173c(param_4,param_2,0x10), iVar1 != 0)) {
    uVar2 = 0;
  }
  else {
    iVar1 = *(int *)(param_4 + 0x34);
    uVar6 = *(uint *)(param_4 + 0x30);
    param_1 = param_1 + *(int *)(param_4 + 0x2c);
    iVar5 = 0;
    for (local_3c = 0; local_3c < uVar6; local_3c = local_3c + uVar4) {
      uVar4 = uVar6 - local_3c;
      if (param_5 < uVar4) {
        uVar4 = param_5;
      }
      FUN_60003278(0);
      FUN_60003478(param_1,param_5,param_4);
      FUN_60003278(3);
      local_40 = param_4;
      for (uVar3 = 0; uVar3 < uVar4; uVar3 = uVar3 + 1) {
        iVar5 = iVar5 + (uint)*local_40;
        local_40 = local_40 + 1;
      }
      param_1 = param_1 + uVar4;
    }
    if (iVar5 == iVar1) {
      *param_3 = iVar1;
      uVar2 = 1;
    }
    else {
      uVar2 = 0;
    }
  }
  return CONCAT44(local_40,uVar2);
}




/* Address 600052e8; body bytes 142 */

undefined4 FUN_600052e8(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;
  
  local_c = param_1;
  local_8 = param_2;
  FUN_600051b6(0);
  iVar1 = FUN_60005232(0x10000,DAT_60005564,&local_1c,local_c,local_8);
  if ((((iVar1 != 0) &&
       (iVar1 = FUN_60005232(0x40000,DAT_60005568,&local_18,local_c,local_8), iVar1 != 0)) &&
      (iVar1 = FUN_60005232(0x80000,DAT_6000556c,&local_10,local_c,local_8), iVar1 != 0)) &&
     (iVar1 = FUN_60005232(0x200000,DAT_60005570,&local_14,local_c,local_8), iVar1 != 0)) {
    FUN_600051b6(1,local_1c);
    FUN_600051b6(2,local_18);
    FUN_600051b6(3,local_10);
    FUN_600051b6(4,local_14);
    return 1;
  }
  FUN_60005186(6);
  return 0;
}




/* Address 60005458; body bytes 274 */

undefined4 FUN_60005458(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uStack_20;
  int iStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  uStack_20 = param_1;
  iStack_1c = param_2;
  uStack_18 = param_3;
  uStack_14 = param_4;
  if (param_2 == 0) {
    FUN_60006cf6(param_1,0x40000,0);
    iVar1 = FUN_60006ce8(&uStack_20,1,0x10,param_1);
    if (iVar1 == 0x10) {
      iVar1 = FUN_60005428(&uStack_20);
      if (iVar1 == 0) {
        uVar2 = 5;
      }
      else {
        FUN_60006cf6(param_1,0x10000,0);
        iVar1 = FUN_60006ce8(&uStack_20,1,0x10,param_1);
        if (iVar1 == 0x10) {
          iVar1 = FUN_60005440(&uStack_20);
          if (iVar1 == 0) {
            uVar2 = 5;
          }
          else {
            FUN_60006cf6(param_1,0x80000,0);
            iVar1 = FUN_60006ce8(&uStack_20,1,0x10,param_1);
            if (iVar1 == 0x10) {
              iVar1 = FUN_600053f8(&uStack_20);
              if (iVar1 == 0) {
                uVar2 = 5;
              }
              else {
                FUN_60006cf6(param_1,0x200000,0);
                iVar1 = FUN_60006ce8(&uStack_20,1,0x10,param_1);
                if (iVar1 == 0x10) {
                  iVar1 = FUN_60005410(&uStack_20);
                  if (iVar1 == 0) {
                    uVar2 = 5;
                  }
                  else {
                    uVar2 = 0;
                  }
                }
                else {
                  uVar2 = 5;
                }
              }
            }
            else {
              uVar2 = 5;
            }
          }
        }
        else {
          uVar2 = 5;
        }
      }
    }
    else {
      uVar2 = 5;
    }
  }
  else {
    FUN_60006cf6(param_1,param_2,0);
    iVar1 = FUN_60006ce8(&uStack_20,1,0x10,param_1);
    if (iVar1 == 0x10) {
      iVar1 = FUN_60005440(&uStack_20);
      if (iVar1 == 0) {
        iVar1 = FUN_60005428(&uStack_20);
        if (iVar1 == 0) {
          iVar1 = FUN_600053f8(&uStack_20);
          if (iVar1 == 0) {
            iVar1 = FUN_60005410(&uStack_20);
            if (iVar1 == 0) {
              uVar2 = 5;
            }
            else {
              uVar2 = 4;
            }
          }
          else {
            uVar2 = 3;
          }
        }
        else {
          uVar2 = 2;
        }
      }
      else {
        uVar2 = 1;
      }
    }
    else {
      uVar2 = 5;
    }
  }
  return uVar2;
}




/* Address 60005584; body bytes 188 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_60005584(uint param_1,uint param_2,uint param_3,undefined4 param_4,uint param_5)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  
  uVar5 = 1;
  if (param_5 < param_3) {
    FUN_600215f0(s__s__d___ASSERT___s_60005978,s_writer_force_updater_cpp_6000595c,0x20d,
                 s___theBuf_size_<_theInfo_size)_6000593c);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  iVar1 = FUN_60006c88(_DAT_60005990,&DAT_6000598c);
  uVar4 = param_1;
  if (iVar1 == 0) {
    FUN_60005186(4);
    uVar5 = 0;
  }
  else {
    for (; uVar4 <= param_2; uVar4 = uVar4 + 1) {
      iVar2 = FUN_60006cf6(iVar1,param_3 * uVar4,0);
      if (iVar2 != 0) {
        FUN_60005186(4);
        uVar5 = 0;
        break;
      }
      uVar3 = FUN_60006ce8(param_4,1,param_3,iVar1);
      if (uVar3 != param_3) {
        FUN_60005186(4);
        uVar5 = 0;
        break;
      }
      FUN_600051fa(uVar4,param_4,param_3);
      iVar2 = FUN_600051d0(uVar4,param_4,param_3);
      if (iVar2 == 0) {
        FUN_60005186(7);
        uVar5 = 0;
        break;
      }
      FUN_6000519c((uVar4 - param_1) + 1,(param_2 - param_1) + 1);
    }
  }
  FUN_60006c78(iVar1);
  return uVar5;
}




/* Address 60005640; body bytes 144 */

undefined4 FUN_60005640(uint *param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined auStack_30 [15];
  undefined local_21;
  undefined auStack_20 [20];
  
  iVar1 = FUN_60006d04(s__ROMINFO_TXT_60005993 + 1,auStack_20);
  if (iVar1 == 0) {
    iVar1 = FUN_60006c88(s__ROMINFO_TXT_60005993 + 1,&DAT_6000598c);
    if (iVar1 == 0) {
      FUN_60005186(3);
      uVar3 = 0xffffffff;
    }
    else {
      iVar2 = FUN_60006ce8(auStack_30,1,0xe,iVar1);
      if (iVar2 == 0xe) {
        local_21 = 0;
        FUN_600053a8(auStack_30,param_1,param_1 + 1,param_1 + 2);
        FUN_60006c78(iVar1);
        if ((param_1[2] == 0) || (param_1[1] < *param_1)) {
          FUN_60005186(3);
          uVar3 = 0xffffffff;
        }
        else {
          uVar3 = 0;
        }
      }
      else {
        FUN_60006c78(iVar1);
        FUN_60005186(3);
        uVar3 = 0xffffffff;
      }
    }
  }
  else {
    FUN_60005186(3);
    uVar3 = 0xffffffff;
  }
  return uVar3;
}




/* Address 600056d0; body bytes 180 */

undefined4 FUN_600056d0(uint *param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  int local_28;
  int local_24 [5];
  
  iVar1 = FUN_60006d04(param_2,local_24);
  if (iVar1 == 0) {
    iVar1 = FUN_60006c88(param_2,&DAT_6000598c);
    if (iVar1 == 0) {
      FUN_60005186(3);
      uVar2 = 0xffffffff;
    }
    else {
      FUN_60006cf6(iVar1,0xfffffff0,2);
      FUN_60006ce8(param_1,4,1,iVar1);
      FUN_60006ce8(param_1 + 1,4,1,iVar1);
      FUN_60006ce8(param_1 + 2,4,1,iVar1);
      FUN_60006ce8(&local_28,4,1,iVar1);
      FUN_60006c78(iVar1);
      if (local_24[0] + -0x10 == local_28) {
        if ((param_1[2] == 0) || (param_1[1] < *param_1)) {
          FUN_60005186(3);
          uVar2 = 0xffffffff;
        }
        else {
          uVar2 = 0;
        }
      }
      else {
        FUN_60005186(3);
        uVar2 = 0xffffffff;
      }
    }
  }
  else {
    FUN_60005186(3);
    uVar2 = 0xffffffff;
  }
  return uVar2;
}




/* Address 60005784; body bytes 584 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_60005784(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint local_44 [5];
  int local_30;
  int local_2c;
  int local_28;
  
  *DAT_600059a0 = param_1;
  FUN_60005174(1);
  iVar1 = FUN_60006c40(&DAT_600059a4);
  if (iVar1 < 0) {
    FUN_60005186(1);
  }
  else {
    iVar3 = -1;
    iVar1 = FUN_60006d04(s_MX1_ROM_BIN_600059a8,local_44);
    if (iVar1 == 0) {
      FUN_60021794(_DAT_60005990,s_MX1_ROM_BIN_600059a8);
      iVar3 = 0;
    }
    else {
      iVar1 = FUN_60006d04(s_PX11_ROM_BIN_600059b4,local_44);
      if (iVar1 == 0) {
        FUN_60021794(_DAT_60005990,s_PX11_ROM_BIN_600059b4);
        iVar3 = 0;
      }
      else {
        iVar1 = FUN_60006d04(s_MX1_UPD_BIN_600059c4,local_44);
        if (iVar1 == 0) {
          FUN_60021794(_DAT_60005990,s_MX1_UPD_BIN_600059c4);
          iVar3 = 1;
        }
        else {
          iVar1 = FUN_60006d04(s_PX11_UPD_BIN_600059d0,local_44);
          if (iVar1 == 0) {
            FUN_60021794(_DAT_60005990,s_PX11_UPD_BIN_600059d0);
            iVar3 = 1;
          }
        }
      }
    }
    iVar1 = FUN_60006d04(_DAT_60005990,local_44);
    if (iVar1 == 0) {
      if (iVar3 == 0) {
        iVar1 = FUN_60005640(&local_30);
      }
      else {
        if (iVar3 != 1) {
          FUN_60005186(3);
          return;
        }
        iVar1 = FUN_600056d0(&local_30,_DAT_60005990);
      }
      if (iVar1 == 0) {
        iVar1 = local_30 * local_28;
        iVar3 = (local_2c + 1) * local_28;
        if (local_44[0] < (uint)((local_2c + 1) * local_28)) {
          FUN_60005186(4);
        }
        else {
          if (*DAT_600059e0 == '\0') {
            iVar2 = FUN_60006c88(_DAT_60005990,&DAT_6000598c);
            if (iVar2 == 0) {
              FUN_60005186(4);
              return;
            }
            iVar1 = FUN_60005458(iVar2,iVar1,iVar3);
            if (iVar1 == 5) {
              FUN_60006c78(iVar2);
              FUN_60005186(6);
              return;
            }
            FUN_60006c78(iVar2);
          }
          iVar1 = FUN_60004710(local_28);
          if (iVar1 == 0) {
            FUN_600215f0(s__s__d___ASSERT___s_60005978,s_writer_force_updater_cpp_6000595c,0x312,
                         s_buf_ptr_600059e4);
            do {
                    /* WARNING: Do nothing block with infinite loop */
            } while( true );
          }
          iVar3 = FUN_60005584(local_30,local_2c,local_28,iVar1,local_28);
          FUN_6000474e(iVar1);
          if (iVar3 != 0) {
            if (*DAT_600059e0 == '\0') {
              iVar1 = FUN_60004710(local_28);
              if (iVar1 == 0) {
                FUN_600215f0(s__s__d___ASSERT___s_60005978,s_writer_force_updater_cpp_6000595c,799,
                             s_buf_ptr_600059e4);
                do {
                    /* WARNING: Do nothing block with infinite loop */
                } while( true );
              }
              iVar3 = FUN_600052e8(iVar1,local_28);
              FUN_6000474e(iVar1);
              if (iVar3 == 0) {
                return;
              }
            }
            FUN_60006d80(s__ROMINFO_TXT_60005993 + 1);
            FUN_60006d80(DAT_60005a98);
            FUN_60005174(4);
            *DAT_60005a9c = '\x01';
            while (*DAT_60005a9c != '\0') {
              thunk_FUN_01000af8(10);
            }
            FUN_60005174(6);
            FUN_60003830();
            iVar1 = FUN_60004044(0);
            if (iVar1 != 0) {
              FUN_60003096(1);
              thunk_FUN_01000af8(1);
              FUN_60003072(0);
              thunk_FUN_01000af8(1);
              FUN_60003774();
              FUN_60003096(0);
              thunk_FUN_01000af8(500);
            }
            FUN_60003828();
            FUN_60005174(4);
            do {
              thunk_FUN_01000af8(10);
            } while( true );
          }
        }
      }
    }
    else {
      FUN_60005186(4);
    }
  }
  return;
}



