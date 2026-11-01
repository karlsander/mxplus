// Maps the embedded panel MCU image, including its observed ARM scatter-loader.
// @category MX1
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.SourceType;
import java.io.*;
import java.math.BigInteger;
import java.util.*;

public class MX1SubcpuMap extends GhidraScript {
    public void run() throws Exception {
        Memory m=currentProgram.getMemory();
        MemoryBlock flash=m.getBlock(toAddr(0x08000000));
        flash.setExecute(true);flash.setWrite(false);
        byte[] init=new byte[0xa0];m.getBytes(toAddr(0x08003f74),init);
        m.createInitializedBlock("RAM_init",toAddr(0x20000000),new ByteArrayInputStream(init),init.length,monitor,false).setWrite(true);
        m.createUninitializedBlock("RAM_bss",toAddr(0x200000a0),0x1510,false).setWrite(true);
        for(MemoryBlock block:m.getBlocks())
            currentProgram.getProgramContext().setValue(currentProgram.getRegister("TMode"),block.getStart(),block.getEnd(),BigInteger.ONE);
        String[] regs={"GPIOA","GPIOB","GPIOC","GPIOD","GPIOE","ADC1","TIM1","USART1","RCC"};
        long[] bases={0x40010800L,0x40010c00L,0x40011000L,0x40011400L,0x40011800L,0x40012400L,0x40012c00L,0x40013800L,0x40021000L};
        for(int i=0;i<regs.length;i++) {
            m.createUninitializedBlock(regs[i],toAddr(bases[i]),0x100,false).setWrite(true);
            createLabel(toAddr(bases[i]),regs[i],true);
        }
        Set<Long> seeds=new TreeSet<>();
        for(int i=1;i<72;i++) {
            long target=Integer.toUnsignedLong(m.getInt(toAddr(0x08000000L+4*i)))&~1L;
            if(target>=0x08000120L&&target<0x08003f34L)seeds.add(target);
        }
        for(long a=0x08000120L;a<0x08004010L;a+=4) {
            long target=Integer.toUnsignedLong(m.getInt(toAddr(a)));
            if((target&1)==0)continue;target&=~1L;
            if(target<0x08000120L||target>=0x08003f34L)continue;
            int h=Short.toUnsignedInt(m.getShort(toAddr(target)));
            if((h&0xff00)==0xb500||h==0xe92d)seeds.add(target);
        }
        seeds.add(0x08000120L);seeds.add(0x08000c64L);
        for(long target:seeds) {
            disassemble(toAddr(target));
            if(getFunctionAt(toAddr(target))==null)createFunction(toAddr(target),null);
        }
        createLabel(toAddr(0x08000314L),"Reset_Handler",true);
        createLabel(toAddr(0x08000c64L),"SystemInit_candidate",true);
        createLabel(toAddr(0x08000d34L),"TIM1_UP_TIM16_IRQHandler",true);
        createLabel(toAddr(0x08001134L),"USART1_IRQHandler",true);
        println("SUB-CPU: mapped flash, observed RAM initialization, STM32F1 MMIO, "+seeds.size()+" seeds");
    }
}
