# MX-1 update container, extraction, and rebuild evidence

## Result

The attached update is not an opaque encrypted blob. It contains two small
uncompressed ARM Thumb boot programs, one raw sub-CPU program, and three LZSS
compressed ARM programs. We can extract every program, validate all four
component payload checksums, rebuild an unchanged file byte for byte, and
repack modified main/USB application payloads in a form that the **original
Roland decompression routine accepts**.

This is a working binary extraction and repacking pipeline. It is not a rebuilt
Roland source project, a fully emulated MX-1, or evidence that an experimental
feature works on physical hardware. The trailer and the updater's block-write,
tag, and checksum checks have also been recovered and tested using the original
instructions. Physical flash behavior and recovery remain separate questions.

All statements in this note derive from the supplied file and the recorded
experiments. No external firmware-format implementation was copied.

## Reproducibility

Input: `MX1_UPD.BIN`, 4,194,320 bytes (`0x400010`).

SHA-256:

```
26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e
```

Artifacts:

- `tools/container_tool.py`: standard-library-only inspector, extractor,
  strict LZSS decoder, literal-only encoder, and guarded offline repacker.
- `tools/container_verify.py`: comparison against actual original ARM decoder
  instructions executed by Unicorn, plus corruption and preservation checks.
- `tools/container_updater_verify.py`: actual updater trailer parser, tag gate,
  checksum routine, write-loop arithmetic and readback comparison, with explicit
  in-memory stubs for file/flash I/O and UI notifications.
- `tools/container_candidate_verify.py`: the same original-instruction checks
  applied to an actual candidate image, including the original LZSS decoder.
- `analysis/container_manifest.json`: complete original layout and hashes.
- `analysis/container_verification.json`: actual verification results.
- `analysis/container_updater_verification.json`: actual update-path verification.
- `analysis/container_ghidra_updater/`: 1,630 automatically decompiled updater
  functions, function table, and references; zero decompiler failures in this run.
- `analysis/container_update_path.c`: the selected relevant updater routines as
  approximate Ghidra pseudocode, for focused review.
- `analysis/container_boot_main.bin` and `container_boot_usb.bin`: raw boot code.
- `analysis/container_app_main.bin`, `container_app_usb.bin`, and
  `container_updater.bin`: decoded programs.
- `analysis/container_boot_main.asm` and `container_boot_usb.asm`: exploratory
  linear Capstone listings. These include data disassembled as code and are not
  authoritative function boundaries.

Examples, from the research project directory:

```sh
python3 tools/container_tool.py inspect /path/to/MX1_UPD.BIN
python3 tools/container_tool.py extract /path/to/MX1_UPD.BIN extracted
python3 tools/container_tool.py repack /path/to/MX1_UPD.BIN unchanged.research.bin
python3 tools/container_tool.py repack /path/to/MX1_UPD.BIN changed.research.bin \
  --replace app_usb=patched-app-usb.bin
python3 tools/container_verify.py /path/to/MX1_UPD.BIN --output verification.json
python3 tools/container_updater_verify.py /path/to/MX1_UPD.BIN --output updater-verification.json
python3 tools/container_candidate_verify.py /path/to/MX1_UPD.BIN /path/to/candidate.bin \
  --output candidate-verification.json
```

Verification requires `unicorn`; the updater harness also uses `capstone` through
the startup memory-map recovery tool. No command accesses a USB device or flashes
hardware. Repacking accepts only the exact original as its base, checks slot
capacity, preserves all unrelated components, and emits a JSON audit report.
Decoded size changes require explicit `--allow-resize` or API `allow_resize=True`,
apply only to the two applications, and still obey the encoded slot limits.
The caller must repair and verify startup/scatter-loader mappings before using
that option for real injected code. An unchanged replacement retains the original
compressed representation.

## File map

Offsets in this table are offsets in the attached update file, not CPU addresses.
The labels `boot_main`, `boot_usb`, `app_main`, and `app_usb` are analysis names.
The distinction between main and USB applications is supported by their source
paths and strings, but the physical chip assignment requires hardware evidence.

| Image | Header offset | Payload offset | Stored bytes | Decoded bytes | Program load base |
|---|---:|---:|---:|---:|---:|
| Boot main | `0x000000` | `0x000030` | 10,732 (`0x29ec`) | Same | `0x01000000` |
| Boot USB | `0x008000` | `0x008030` | 4,160 (`0x1040`) | Same | `0x01000000` |
| `PX-11:Updater` | `0x010000` | `0x010040` | 142,898 (`0x22e32`) | 182,828 (`0x2ca2c`) | `0x60000000` |
| `PX-11:SUB-CPU` | `0x040000` | `0x040040` | 16,404 (`0x4014`) | Same | `0x08000000` |
| Main `PX-11:Appli` | `0x080000` | `0x080040` | 505,462 (`0x7b676`) | 918,600 (`0xe0448`) | `0x60000000` |
| USB `PX-11:Appli` | `0x200000` | `0x200040` | 137,970 (`0x21af2`) | 224,868 (`0x36e64`) | `0x60000000` |
| Trailer | `0x400000` | — | 16 | — | Not established |

Each component's remaining assigned slot is filled with `0xff`. The slot limits
used by the repacker are the next component boundary and the end of the 4 MiB
image, except that the USB application's writable slot ends at `0x300000`, as
established by the update trailer. A numerical gap does not establish that arbitrary new runtime sections
can be added: startup mappings and available RAM also matter.

### Embedded versions and timestamps

| Component | Version text | Build timestamp text |
|---|---|---|
| Updater | `1.000954` | `14-1217_14:20:05` |
| Sub-CPU | `1.011052` | `15-0108_09:10:28` |
| Both applications | `1.051132` | `16-0906_11:04:55` |

The formatting strongly suggests 17 December 2014, 8 January 2015, and 6
September 2016 respectively. These are embedded build labels, not independently
verified release dates. The product's internal project name is `PX-11`.

## Component headers

The four headers beginning with `PX-11:` are 64 bytes, with little-endian words.

| Relative offset | Bytes | Observed meaning |
|---|---:|---|
| `0x00` | 16 | Padded component label |
| `0x10` | 16 | Build timestamp text |
| `0x20` | 8 | Version text |
| `0x28` | 4 | Address field; equals `0x60000000` for applications/updater and `0x08000000` for sub-CPU; likely entry address |
| `0x2c` | 4 | Stored payload offset, always `0x40` |
| `0x30` | 4 | Stored payload length |
| `0x34` | 4 | Sum of stored payload bytes modulo `2^32` |
| `0x38` | 4 | Destination/load address used by boot decoder |
| `0x3c` | 4 | Decoded payload length for compressed programs; equals raw length for sub-CPU |

Checksums verified across all four components:

| Component | Stored checksum | Computed sum |
|---|---:|---:|
| Updater | `0x010be666` | `0x010be666` |
| Sub-CPU | `0x0016818b` | `0x0016818b` |
| Main application | `0x03ab30ee` | `0x03ab30ee` |
| USB application | `0x01016e3e` | `0x01016e3e` |

The checksum covers the **stored/compressed bytes**, excluding the 64-byte header
and erased padding. Original updater routine `0x60005232` directly implements
this byte sum; the emulator tests confirm its result for every component and
its rejection of one corrupted byte. Boot-ROM behavior outside the traced updater
remains a separate question.

### Boot headers

The two boot headers begin `ESC91.000\0\0\0`. The word at `+0x0c` gives the raw
payload length; raw vectors begin at `+0x30`. Both boot programs use runtime base
`0x01000000` but differ in content, length, vectors, and reset entry. They are not
redundant identical mirrors.

| Boot | Initial stack pointer | Reset vector (Thumb bit included) |
|---|---:|---:|
| Main | `0x010114a8` | `0x010004e1` |
| USB | `0x01011248` | `0x01000491` |

Shared boot-header values include `0x00400000` at `+0x10`, `0x0aaa6808` at
`+0x14`, and `0x34224310` at `+0x1c`. Their semantics have not been established.
Simple byte-sum/CRC hypotheses for these fields did not match the whole image.
The repacker leaves both headers and programs untouched.

### Trailer

The final 16 bytes, after the 4 MiB image, are:

```
40 00 00 00 ff 02 00 00 00 10 00 00 00 00 40 00
```

The four little-endian words have the following meanings, verified from original
updater routine `0x600056d0` and the writer at `0x60005584`:

| Word | Value | Meaning |
|---|---:|---|
| 0 | `0x40` = 64 | First block to write |
| 1 | `0x2ff` = 767 | Last block to write, inclusive |
| 2 | `0x1000` = 4,096 | Block size in bytes |
| 3 | `0x400000` = 4,194,304 | Image length excluding the 16-byte trailer |

The standard file therefore writes 704 blocks, offsets `0x040000` through
`0x2fffff` inclusive. It preserves offsets `0x000000`–`0x03ffff` (both boot
programs and the updater) and `0x300000`–`0x3fffff` (the upper MiB). This is a
significant distinction from flashing the whole 4 MiB file.

The parser checks file length minus 16 against the final word, requires a nonzero
block size, and rejects an end block below the start block. The main writer also
checks that the file covers the requested final block. The analysis tool adds
its own stricter bounds checks and preserves this plan exactly.

## The actual update path

`0x60005784`, in the region associated with `writer\\force_updater.cpp`, is the
main update operation. Its relevant call path is:

| Routine | Observed behavior |
|---|---|
| `0x60005784` | Selects an update/backup filename, obtains the plan, invokes validation and writing, then verifies all components and triggers sub-CPU update handling |
| `0x600056d0` | Seeks to EOF minus 16 and reads the update trailer |
| `0x60005458` | Checks a 16-byte component label at the selected starting offset; for the normal plan the start is the sub-CPU header at `0x40000` |
| `0x60005584` | Opens the file, seeks/reads each complete block, programs it, performs a readback comparison, and reports progress |
| `0x600051fa` | Flash mode/erase/program wrapper used by the loop |
| `0x600051d0` | Compares programmed bytes through flash mapping `0x03000000 + block*size` |
| `0x600052e8` | Verifies the four component checksums after writing |
| `0x60005232` | Checks component tag and sums stored payload bytes, using header offset/length/checksum fields |

No version-string comparison or cryptographic signature check appears in this
inspected writer path. Keeping the version string `1.051132` does not trigger a
same-version rejection here. This is a finding about the traced code, not proof
that every behavior of the immutable ROM is known.

The writer checks component byte sums **after** programming. Its pre-write check
is a label check, and its per-sector check is a readback comparison. Consequently,
an offline checksum check remains important before an experimental file reaches
the device; the original updater is not a comprehensive preflight validator.

The filename search gives `MX1_ROM.BIN`/`PX11_ROM.BIN` precedence over
`MX1_UPD.BIN`/`PX11_UPD.BIN`. The raw ROM path uses `ROMINFO.TXT` for its block plan.
This code establishes that a separate backup/restore-oriented mechanism exists,
but it has not been exercised on hardware and should not be confused with a
verified recovery procedure.

The independent updater harness executes the exact original machine code for
trailer parsing, component tag comparisons, component checksums, block iteration,
and `memcmp`. File access and actual flash erase/program are replaced with
explicit memory operations. With a synthetic repacked USB component, the original
loop writes exactly 704 blocks, leaves both outer ranges unchanged, and passes
all four original post-write checksum checks. A simulated readback fault stops
on the first block with error code 7. A bad file-length field and zero block size
are rejected with error code 3. This verifies control logic without asserting
that the physical flash-controller interactions have been modeled.

## LZSS format and independent verification

The compressed images use an Okumura-style 4,096-byte ring:

1. Initial write index is 4,078 (`0xfee`).
2. Ring bytes 0 through 4,077 initialize to zero. The final 18 bytes are not
   explicitly initialized by the original decoder.
3. A flag byte controls eight tokens, least-significant bit first.
4. A one bit means one following literal byte.
5. A zero bit means two following bytes `a, b` encoding ring position
   `a | ((b & 0xf0) << 4)` and length `(b & 0x0f) + 3`.
6. Copy one byte at a time, adding every emitted byte to the ring. This permits
   overlapping references and wraps modulo 4,096.

Initial experiments with the space-filled ring used by some classic LZSS
implementations produced the expected output lengths but corrupted initial
pointer values. **Matching decompressed length alone is insufficient.** The
zero initialization was then verified directly in the firmware instructions.

The USB boot program's decoder starts at runtime `0x0100052e` (file `0x855e`).
Its aligned-word byte reader is at `0x01000514`. Its ring is at `0x01010034`,
and its cached word is at `0x01010004`. Registers at entry are:

| Register | Meaning |
|---|---|
| `r0` | Stored input pointer |
| `r1` | Destination pointer |
| `r2` | Expected output length |

The loop at `0x01000542` clears the ring up to `0xfee`. Flag processing at
`0x0100055a`, reference decoding at `0x010005a0`, and byte-copy operations at
`0x010005ca` establish the details above. The routine returns the requested
output length in `r0`.

The verifier maps the **unmodified boot program bytes** into Unicorn, provides
RAM, input, and output buffers, and calls this routine. No decoder behavior is
stubbed. Each output matches the Python decoder byte for byte:

| Decoded program | SHA-256 |
|---|---|
| Updater | `8984a4e0c668dcf6fce981f2c2e9223dfe93bb0f115bc43c8bb9ba95b3f1d3ec` |
| Main application | `256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b` |
| USB application | `fe52cf6c9e8ec8677963b1c4b876ddeaefae5136b7a5f1f49010e3cda9203a6e` |

The original decoder does not take a compressed-length argument. It also reads
one further token/literal before determining that output is full. The test maps
the real slot's `0xff` padding after the input, and the repacker retains such
padding. The Python decoder is intentionally stricter: truncated tokens,
unconsumed bytes, output overruns, and references to still-undefined initial
ring positions are rejected.

## Repacking without reproducing Roland's compressor

We do not need the original compressor to make a decoder-compatible image.
The encoder uses only literal tokens. This costs approximately 12.5% over the
decoded size, but both application slots have sufficient capacity.

| Application | Literal-encoded bytes | Available payload capacity | Remaining bytes |
|---|---:|---:|---:|
| Main | 1,033,425 | 1,572,800 | 539,375 |
| USB | 252,977 | 1,048,512 | 795,535 |

This approach deliberately favors a short, easy-to-audit encoder over optimal
compression. Synthetic one-byte mutations of both applications were repacked,
decoded by the original firmware routine, and matched exactly. Other components,
both boot images, and the trailer were verified unchanged. The synthetic mutation
fixtures are held in memory only; they are not delivered as feature builds.

Literal-only encoding does **not** fit the original updater slot. The tool rejects
that overflow rather than silently crossing into the sub-CPU slot. An unchanged
updater is preserved byte for byte and needs no recompression. Changing the
updater is unnecessary for the current USB goals.

The original updater's recovered block plan accommodates these larger encoded
applications, and its actual checksum routine accepts the repacked bytes. This
does not certify the timing of reading a larger application, hardware loading,
the full boot path, or any feature patch. Those remain separate checks before
treating a generated image as usable.

## Importing into a disassembler or decompiler

Use separate programs for the two boot images and three main-core applications,
even where their load addresses coincide. Their shared addresses do not mean
they coexist in one address space.

- Boot raw binaries: little-endian ARM Thumb, base `0x01000000`; first words are
  Cortex-M-style vectors. Reset vectors include the Thumb bit.
- Decoded updater/main/USB applications: little-endian ARM Thumb, initial base
  `0x60000000`; code begins immediately with instructions, not a vector table.
- Raw sub-CPU: little-endian ARM Thumb, base `0x08000000`; initial stack pointer
  `0x200015b0`, reset vector `0x08000315`.

The application startup **copies additional code/data to other addresses**.
For example, main application literals at decoded `+0xe4` specify destination
`0x01000300`, length `0xf3a4`, and source `0x600d0b8c`. Other records clear and
initialize RAM. Importing only one flat region misses references into relocated
code and gives misleading decompiler output. Follow the actual startup copies
and later scatter-load table before naming unresolved addresses.

## Verification coverage and limits

The recorded codec/repack run passes eight groups:

1. Exact original file hash and all four stored payload checksums.
2. All three original LZSS payloads match the actual firmware decoder.
3. Extract/repack with every component unchanged reproduces the complete file
   byte for byte.
4. Synthetic changed main and USB payloads survive repacking and the actual
   decoder, while unrelated slots/boot/trailer remain untouched.
5. Application-size changes require explicit opt-in; an explicitly resized codec
   fixture is accepted by the original decoder.
6. A corrupted stored payload byte is rejected.
7. Six malformed stream fixtures exercise truncation, overrun, trailing bytes,
   and uninitialized-ring references.
8. Updater-slot overflow is rejected.

The updater-path run independently passes seven groups: trailer acceptance;
trailer rejection fixtures; valid/invalid starting component tags; all original
component checksums; the 704-block repacked-image write/readback/checksum path;
post-write checksum corruption rejection; and early stop on a readback mismatch.

The actual experimental host candidate was also checked independently with
`container_candidate_verify.py`. Its SHA-256 is
`516fc0a3baeaf179e018d7eff2eba376ba21eaed8b9e43a9b9860dce6f45dd58`.
Only the decoded USB application changes, increasing by 1,132 bytes to 226,000.
The original LZSS decoder matches the modified application byte for byte, the
original trailer parser and tag gate accept it, the original block-write/readback
loop processes exactly 704 blocks, and all four original post-write checksum
checks pass. All bytes outside the update range are preserved. The report is
`analysis/container_host_candidate_verification.json`.

This candidate-specific result concerns the update envelope. The separate
host-parser/startup/policy tests address the feature code; neither test set
establishes actual physical USB enumeration, audio streaming, or safe recovery.

Unicorn here verifies CPU instruction semantics of selected routines. It does not model
USB controllers, clocks, flash writes, DSPs, DMA, interrupt timing, the physical
UI, or audio behavior. Recorded host runtime is not an MX-1 cycle measurement.

The most useful remaining evidence for the update path is a documented recovery
method and controlled hardware verification. Strings such as `BACKUP\\MX1_ROM.BIN`,
`BACKUP\\ROMINFO.TXT`, and `writer\\force_updater.cpp` show relevant code exists;
the presence of those strings alone does not establish a safe recovery procedure.
