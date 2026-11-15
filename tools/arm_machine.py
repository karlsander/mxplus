"""Shared ARM instruction harness; no firmware builder or host unlock."""
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,
                              UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,
                              UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,
                              UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC)
from memory_map import recover

BASE=0x60000000
RETURN=0x0fff0000

class Machine:
    def __init__(self,image,scatter=True):
        self.image=image
        self.uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        for address,size in [(BASE,0x800000),(0x01000000,0x30000),(0x20000000,0x20000),
                             (0x40000000,0x50000),(RETURN,0x1000)]:
            self.uc.mem_map(address,size)
        # The location-only hardware experiment fails here. Do not model this
        # unproven private address interval as usable RAM in main-app tests.
        self.uc.mem_unmap(0x01018000,0x8000)
        self.uc.mem_write(BASE,image)
        if scatter:
            for op in recover(image)['operations']:
                if not op['length']:continue
                content=(image[op['source']-BASE:op['source']-BASE+op['length']]
                         if op['kind']=='copy' else bytes(op['length']))
                self.uc.mem_write(op['destination'],content)
    def read(self,address,size):return bytes(self.uc.mem_read(address,size))
    def write(self,address,content):self.uc.mem_write(address,bytes(content))
    def call(self,address,*args,count=100000,measure=False,stack=0x2001fff0):
        u=self.uc
        u.reg_write(UC_ARM_REG_SP,stack);u.reg_write(UC_ARM_REG_LR,RETURN|1)
        for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,val)
        instructions=[0]
        handle=None
        if measure:
            def on_instruction(*_):instructions[0]+=1
            handle=u.hook_add(UC_HOOK_CODE,on_instruction)
        try:u.emu_start(address|1,RETURN,timeout=1_000_000,count=count)
        finally:
            if handle is not None:u.hook_del(handle)
        if u.reg_read(UC_ARM_REG_PC)!=RETURN:raise AssertionError(f'function did not return, pc={u.reg_read(UC_ARM_REG_PC):x}')
        if u.reg_read(UC_ARM_REG_SP)!=stack:raise AssertionError('stack pointer not restored')
        return u.reg_read(UC_ARM_REG_R0),instructions[0]
