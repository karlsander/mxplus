// Export C-like decompiler output and function/data references. Not buildable source.
// @category MX1
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.address.*;
import java.io.*;
import java.nio.file.*;

public class MX1Export extends GhidraScript {
    public void run() throws Exception {
        Path out=Path.of(getScriptArgs()[0]);Files.createDirectories(out);
        DecompInterface decomp=new DecompInterface();
        decomp.openProgram(currentProgram);
        int count=0,failed=0;
        try(PrintWriter c=new PrintWriter(Files.newBufferedWriter(out.resolve("decompiled.c")));
            PrintWriter functions=new PrintWriter(Files.newBufferedWriter(out.resolve("functions.tsv")));
            PrintWriter refs=new PrintWriter(Files.newBufferedWriter(out.resolve("references.tsv")))) {
            c.println("/* AUTOMATIC GHIDRA DECOMPILATION: approximate pseudocode, not original or recompilable C. */");
            functions.println("address\tname\tbody_bytes\tstatus");
            refs.println("from\tto\ttype\tfunction");
            FunctionIterator iterator=currentProgram.getFunctionManager().getFunctions(true);
            while(iterator.hasNext()&&!monitor.isCancelled()) {
                Function f=iterator.next();
                DecompileResults r=decomp.decompileFunction(f,45,monitor);
                String status=r.decompileCompleted()?"ok":r.getErrorMessage();
                functions.println(f.getEntryPoint()+"\t"+f.getName()+"\t"+f.getBody().getNumAddresses()+"\t"+status);
                c.println("\n/* Address "+f.getEntryPoint()+"; body bytes "+f.getBody().getNumAddresses()+" */");
                if(r.decompileCompleted())c.println(r.getDecompiledFunction().getC());else{c.println("/* "+status+" */");failed++;}
                InstructionIterator instructions=currentProgram.getListing().getInstructions(f.getBody(),true);
                while(instructions.hasNext()) {
                    Instruction ins=instructions.next();
                    for(Reference ref:ins.getReferencesFrom())refs.println(ref.getFromAddress()+"\t"+ref.getToAddress()+"\t"+ref.getReferenceType()+"\t"+f.getEntryPoint());
                }
                count++;
            }
        } finally{decomp.dispose();}
        println("MX1 exported functions="+count+" decompiler failures="+failed+" to "+out);
    }
}
