// Create runtime SRAM mappings before headless analysis. See tools/memory_map.py.
// @category MX1
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.lang.Register;
import java.io.*;
import java.nio.file.*;
import java.math.BigInteger;
import java.util.*;

public class MX1Map extends GhidraScript {
    public void run() throws Exception {
        String[] args=getScriptArgs();
        Memory memory=currentProgram.getMemory();
        MemoryBlock original=memory.getBlock(toAddr(0x60000000L));
        byte[] image=new byte[(int)original.getSize()];
        memory.getBytes(original.getStart(),image);
        long entry=0,residentEnd=0;
        List<String[]> rows=new ArrayList<>();
        for(String line:Files.readAllLines(Path.of(args[0]))) {
            String[] row=line.split("\\t"); rows.add(row);
            if(row[0].equals("entry"))entry=Long.parseLong(row[1],16);
            if(row[0].equals("resident_end"))residentEnd=Long.parseLong(row[1],16);
        }
        // Use post-scatter memory, with source bytes retained in the input file.
        memory.removeBlock(original,monitor);
        MemoryBlock resident=memory.createInitializedBlock("SDRAM_code",toAddr(0x60000000L),
            new ByteArrayInputStream(image,0,(int)(residentEnd-0x60000000L+4)),
            residentEnd-0x60000000L+4,monitor,false);
        resident.setExecute(true);resident.setWrite(true);
        int index=0;
        for(String[] row:rows) {
            if(!row[0].equals("copy")&&!row[0].equals("zero"))continue;
            long destination=Long.parseLong(row[1],16), length=Long.parseLong(row[2],16),source=Long.parseLong(row[3],16);
            MemoryBlock block;
            if(row[0].equals("copy")) {
                block=memory.createInitializedBlock("copy_"+(index++),toAddr(destination),
                    new ByteArrayInputStream(image,(int)(source-0x60000000L),(int)length),length,monitor,false);
            } else block=memory.createUninitializedBlock("bss_"+(index++),toAddr(destination),length,false);
            block.setWrite(true);block.setRead(true);block.setExecute(destination==0x01000300L);
        }
        Register tmode=currentProgram.getRegister("TMode");
        for(MemoryBlock block:memory.getBlocks()) {
            currentProgram.getProgramContext().setValue(tmode,block.getStart(),block.getEnd(),BigInteger.ONE);
        }
        for(long a:new long[]{0x60000000L,0x01000300L,entry&~1L}) {
            disassemble(toAddr(a));
            if(getFunctionAt(toAddr(a))==null)createFunction(toAddr(a),a==0x60000000L?"scatter_start":a==(entry&~1L)?"runtime_entry":null);
        }
        // Seed obvious function-pointer targets; indirect task/vtable calls are
        // abundant. Requiring a PUSH-with-LR reduces accidental numeric matches.
        HashSet<Long> seeds=new HashSet<>();
        for(MemoryBlock block:memory.getBlocks()) {
            if(!block.isInitialized())continue;
            for(long off=0;off+4<=block.getSize();off+=4) {
                long value=Integer.toUnsignedLong(memory.getInt(block.getStart().add(off)));
                if((value&1)==0)continue;
                long target=value&~1L;
                MemoryBlock targetBlock=memory.getBlock(toAddr(target));
                if(targetBlock==null||!targetBlock.isExecute()||!targetBlock.isInitialized())continue;
                int h=Short.toUnsignedInt(memory.getShort(toAddr(target)));
                if((h&0xff00)==0xb500||h==0xe92d)seeds.add(target);
            }
        }
        for(long target:seeds) {
            Address a=toAddr(target);
            if(getFunctionAt(a)==null){disassemble(a);createFunction(a,null);}
        }
        println("MX1 runtime mappings and "+seeds.size()+" indirect-function seeds created; entry="+Long.toHexString(entry));
    }
}
