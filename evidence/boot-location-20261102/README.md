# One-off code-location isolation — 2 November 2026

This records a temporary diagnostic derived from the booting pre-generator
mainline at `eb646b6cb3ad7f271097c4ab41f2098ab1399576`. It is not a second maintained
builder or feature branch. The normal mainline sources remain unchanged by
this experiment. After a repeated copy with full readback and successful eject,
the user confirmed that flashing succeeded but normal boot stayed dark.

Candidate SHA-256:
`dac455b5634088e9d8f235d9af397821d2dedd46175fc51caca55ad406fa2c12`.

All feature C/assembly, descriptor generation, routing patch logic and immutable
stock input are identical to that historical commit. The linker moves code
from `0x0100f6a4` to `0x01018000`. Code remains 2,376 bytes; all 18 compiled
functions keep their sizes and relative positions. The changed 43 code bytes
encode internal address relocations. Mutable state stays at its proven earlier
addresses `0x01017264..0x010173f4`; USB descriptor content is unchanged.

The historical first startup copy and descriptor copy are preserved. The first
copy also leaves an unused duplicate of relocated code at `0x0100f6a4`. Every
external hook targets the copy linked at `0x01018000`. Originally empty copy
operation 8 (call `0x60000056`) now loads the same 2,376 inserted code bytes
from `0x600dff30` into `0x01018000..0x01018948`. Its literals at decoded
`0x134/0x138/0x13c` are guarded and recorded. No original nonempty destination
changes relative to the pre-generator builder, and no allocator, MPU, generator,
SELECT-editor, boot, updater, panel or USB-processor code is modified.

The source of copy operation 8 is explicitly accounted for in two steps:
the historical insertion relocates it from `0x600e0448` to `0x600e0ef4`, then
the isolated builder redirects it to the inserted code at `0x600dff30`.
The verifier replays and checks both exact values, including the deliberate
overlap at `0x13c`. Bounds remain 2,396 bytes in both code slots; no input or
byte guards are relaxed.

The historical pipeline's 17 stages and committed-artifact gate pass. Its 32
unit/descriptor tests and five bridge tests pass. MPU permissions and both code
copies are checked; instruction harnesses protect the new code pages against
writes. This does not establish physical SRAM at the test address. The existing
boot/RTOS/MMIO modeling limits still apply.

Forensic reproduction: check out the historical commit, apply
`historical-source-delta.patch`, use its pinned requirements, and run
`tools/reproduce.py`. The build report and selected instruction reports here
identify that exact output. The committed gate was run against a temporary
local commit containing matching sources, binary artifacts and reports; no
additional active firmware build is introduced in the main tree.

The new code-location/load operation is therefore sufficient to reproduce the
failure without generator/editor hooks. This implicates the location but does
not distinguish absent RAM, aliasing, bus permissions, or another physical
memory constraint without further evidence.
