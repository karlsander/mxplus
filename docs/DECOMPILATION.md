# Decompilation methods and reproducibility

## What was actually recovered

The supplied update is a container, not a single executable. Signature, header, size, entropy, string and instruction inspection separated two boot programs, an updater, the panel/sub-CPU image, the main application and the USB-host application. Three components use a zero-initialized 4,096-byte-ring LZSS variant; the panel program is raw Cortex-M3 code. The extraction and repacking implementation is in `tools/container_tool.py`.

Four complementary methods were used:

1. **Container and codec reconstruction.** The Python decoder was compared with execution of the boot program's actual Thumb decoder, including controlled initial-ring fixtures. Stored-byte checksums, slot sizes and trailer semantics were checked independently. A no-change rebuild is byte-identical to the original.
2. **Capstone disassembly and manual data flow.** Startup copy/zero operations, literal pools, pointer tables, descriptor bytes, register accesses, USB selection paths and selected control handlers were traced directly. `tools/memory_map.py` derives startup mappings from instructions. Linear assembly is supplementary because embedded constants also decode as plausible instructions.
3. **Ghidra decompilation with runtime mappings.** Automatic analysis used ARM little-endian Cortex/Thumb with post-startup SRAM and SDRAM regions. Function and reference indexes accompany the pseudocode. Critical routines were reconciled with Capstone instead of relying on inferred C types.
4. **Execution of selected original instructions.** Unicorn executes the original codec, updater, binding, parsing, descriptor, control and audio-pump paths. Explicit stubs supply file/flash I/O, hardware start or selected MMIO conditions. Newly compiled C/Thumb extensions are tested in the same paths. This is not a complete or cycle-accurate emulator of the mixer.

The initial assumption that all decompressed code executes at `0x60000000 + file_offset` was insufficient. Both applications first move a hot code section to `0x01000300` and move initialized data into additional RAM regions. The startup subsequently clears SDRAM that held these copy sources. Correct runtime mapping was necessary to resolve USB interrupt/control and pump calls.

| Component | Load address | Hot code source | Hot code runtime | Bytes copied |
| --- | --- | --- | --- | ---: |
| Main application | `0x60000000` | `0x600d0b8c` | `0x01000300` | 62,372 |
| USB-host application | `0x60000000` | `0x6002b1f4` | `0x01000300` | 48,100 |
| Updater | `0x60000000` | `0x600275f8` | `0x01000300` | 20,458 |

The shared numerical addresses belong to distinct execution contexts. They must not be merged into one program map. This alone does not determine the number of physical ESC2 packages.

## Export coverage and its limits

| Export | Functions exported | Tool-reported failures |
| --- | ---: | ---: |
| Main application | 3,929 | 0 |
| USB-host application | 1,392 | 0 |
| Updater | 1,630 | 0 |
| Panel/sub-CPU | 171 | 0 |

The total is 7,122 function records in these exports. Zero tool-reported failures does not mean correct or complete source recovery. Some bodies contain warnings or unresolved instructions; some data and tail calls can be misidentified. One important example is the USB audio worker at `0x60008958`: it lacks the PUSH-with-LR prologue used by the indirect-function seed heuristic, so the automatic export misses it. Its actual disassembly, driver record and binding behavior are documented and tested in `research/container-binding.md` and `tools/container_binding_verify.py`.

No complete original symbol table, source comments, build system, full type system or proprietary peripheral definitions were recovered. Some original source-path and diagnostic strings survive in the binary, but they do not restore the missing source tree. The new firmware candidates retain original machine code and add independently compiled extensions. The automatic C output cannot simply be passed to a compiler to recreate the complete product.

## Optional Ghidra rerun

The supplied exports used **Ghidra 11.0.3** and **JDK 17**, ARM language `ARM:LE:32:Cortex`, default compiler specification. Obtain Ghidra from its [official release repository](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_11.0.3_build). Install a full 64-bit JDK 17, including `javac`, and make it available to the Ghidra launcher; a Java runtime alone is insufficient for these Java scripts. The toolchain and Ghidra project database are deliberately omitted from the research archive; the export and mapping scripts are included. Ghidra's official installation documentation is authoritative for the installed version's Java requirement.

First run `tools/reproduce.py` to regenerate decoded images and maps. Set a local path to the matching Ghidra installation and run from the project root:

```bash
GHIDRA_HOME=/absolute/path/to/ghidra_11.0.3_PUBLIC
mkdir -p build/ghidra-projects

"$GHIDRA_HOME/support/analyzeHeadless" build/ghidra-projects main \
  -import analysis/container_app_main.bin \
  -loader BinaryLoader -loader-baseAddr 0x60000000 \
  -processor ARM:LE:32:Cortex -cspec default \
  -scriptPath tools \
  -preScript MX1Map.java analysis/map-main.tsv \
  -postScript MX1Export.java analysis/ghidra-main

"$GHIDRA_HOME/support/analyzeHeadless" build/ghidra-projects usb \
  -import analysis/container_app_usb.bin \
  -loader BinaryLoader -loader-baseAddr 0x60000000 \
  -processor ARM:LE:32:Cortex -cspec default \
  -scriptPath tools \
  -preScript MX1Map.java analysis/map-usb.tsv \
  -postScript MX1Export.java analysis/ghidra-usb

"$GHIDRA_HOME/support/analyzeHeadless" build/ghidra-projects updater \
  -import analysis/container_updater.bin \
  -loader BinaryLoader -loader-baseAddr 0x60000000 \
  -processor ARM:LE:32:Cortex -cspec default \
  -scriptPath tools \
  -preScript container_Map.java analysis/container_map-updater.tsv \
  -postScript MX1Export.java analysis/container_ghidra_updater

"$GHIDRA_HOME/support/analyzeHeadless" build/ghidra-projects subcpu \
  -import analysis/container_subcpu.bin \
  -loader BinaryLoader -loader-baseAddr 0x08000000 \
  -processor ARM:LE:32:Cortex -cspec default \
  -scriptPath "tools;sources/hardware" \
  -preScript MX1SubcpuMap.java \
  -postScript MX1Export.java sources/hardware/decomp
```

These commands assume fresh Ghidra project names. Do not use overwrite options on an independently annotated project without preserving it. Main/USB mappings retain the four-byte startup boundary that precedes cleared SDRAM; the updater uses its own mapper because its BSS begins exactly at its hot-code source.

## Other useful commands

```bash
.venv/bin/python tools/container_tool.py inspect inputs/MX1_UPD.original.bin
.venv/bin/python tools/container_tool.py extract inputs/MX1_UPD.original.bin build/extracted
.venv/bin/python tools/memory_map.py analysis/container_app_main.bin --output analysis/map-main.json
.venv/bin/python sources/hardware/disasm_main.py 01009840 732
.venv/bin/python sources/hardware/show_main_functions.py 01004646 6003b664
```

The command-line disassembler maps a runtime address through the original scatter table. Use the build report and candidate map when inspecting injected code; the original helper is not a general relocation-aware debugger.
