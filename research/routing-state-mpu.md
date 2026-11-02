> Historical investigation: standalone build paths refer to Git history. The only active firmware is [mainline](../docs/MAINLINE.md). Historical evidence has not been rewritten as combined-image evidence.

# Routing state write-protection fault

On 2 November 2026 the user reported that the page-guard revision displayed
`Auto` while SELECT was held, then froze on encoder movement with `Auto` still
visible. This is a panel observation, not an instrumented exception capture.

## Original instructions and diagnosis

Main decoded offset `0xd824`, runtime `0x6000d824`, configures the Cortex-M MPU.
The original instructions write RNR/RBAR/RASR at `0xe000ed98/9c/a0`, then enable
the MPU at `0xe000ed94`. Region 1 has base `0x01000000`, RASR `0x06000021`:
128 KiB, access permission 6 (read-only). Region 2 overrides its writable
32 KiB at `0x01010000..0x01017fff` with RASR `0x1300001d` (AP 3, execute-never).
Regions 3/4 override the first 768 bytes, not the injected extension.
These AP meanings follow [Arm's CMSIS definitions](https://arm-software.github.io/CMSIS_6/latest/Core/group__mpu__defines.html).

The page-fixed candidate SHA-256 was
`74ebf3cab47631f14fe5fa8a113804ff7d99397a6898a068255cd8542f2d5d57`.
Its first 5/6 encoder increment executes `strb.w r3,[ip,r4]` at runtime
`0x0100f798`, main decoded offset `0xe0024`, targeting desired state at
`0x0100fcd4 + 4`. Code relocation is first-copy source decoded `0xd0b8c`
to runtime `0x01000300`; extension starts decoded `0xdff30` at `0x0100f6a4`.
That target is read-only. The former instruction harness mapped SRAM writable
and therefore missed the fault. With page permissions enforced, the old image
raises `UC_ERR_WRITE_PROT` at that store, without posting any event or changing
the `Auto` text. This matches the reported symptom; there is no physical fault
register capture proving the exception identity.

## Correction and reservation

Keep code/constant tables in the existing executable extension. Move the two
11-byte arrays into a separate NOBITS `.route_state` at `0x01017264`, padded to
24 bytes; `applied` starts at `0x0101726f`. The original writable BSS starts at
`0x01010088`, length `0x71dc`, ending exactly at this reservation. Change only
the guarded zero-count literal at main decoded `0x108`, runtime `0x60000108`,
from bytes `dc710000` to `f4710000`. Original startup now clears through
`0x0101727b`, before MPU enable, leaving the following bytes untouched.
The builder guards state addresses, object sizes, section type/flags, BSS
identity, input hash and every existing patch. No MPU restriction is relaxed.

Original RTOS variable-pool initialization at runtime `0x01006338` (main decoded
`0xd6bc4`) constructs the general pool at `0x01013e18..0x01014e17` and stack pool
at `0x01020000..0x01027fff`. Their fixed records at runtime `0x0100f234` (decoded
`0xdfac0`) are unchanged. Neither pool overlaps the reservation. Original
static startup destinations/contents remain intact; the new end `0x0101727c`
is inside the writable MPU region ending at `0x01018000`.

## Checks and limits

`tools/routing_mpu_verify.py` executes original MPU setup, stubbing only
exception-handler registration at `0x60054ef8`. It decodes region precedence,
size and access permissions and checks that original and patched maps agree.
Unicorn does not enforce Cortex-M MPU registers itself: the UI/audio harnesses
explicitly protect full code pages `0x01001000..0x0100ffff` against CPU writes.
This models permission rejection, not actual MemManage exception delivery.

Actual cold startup over both `0x55` and `0xaa` SRAM clears the whole reserve;
the next four bytes remain dirty. The original allocator initializer preserves
sentinels in the reserve. Its ICSR response models thread mode. Existing UI
cases, source cycling, DSP operands, Auto restoration and mode guards run with
the code protection enabled. DSP arithmetic, scheduling deadlines, physical
MMIO delivery and audible routing remain unverified.

Historical old-candidate reproduction and build identity are preserved in
`evidence/routing-state-mpu-20261102/`. Current output is in
`build/routing-probe/mpu-verification.json`, integrated into the full verifier.
