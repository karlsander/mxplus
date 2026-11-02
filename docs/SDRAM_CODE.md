# SDRAM code reservation

The location-only hardware test fails with previously working feature code
linked at `0x01018000`; see [boot investigation](BOOT_REGRESSION.md). Code now
lives at `0x60664000` in the address range of the stock SDRAM heap. This is an
explicit reservation, not memory borrowed while leaving it allocatable.
The user confirmed normal boot of this placement. NSE activation still freezes;
that observation does not yet establish whether the cause is the generator
exchange write, DSP route operand or execution timing.

All runtime addresses below refer to the main application. Resident SDRAM
instruction offsets equal runtime minus `0x60000000`; relocated private RTOS
instructions use `analysis/map-main.json`.

## Original allocator evidence

Original instructions at `0x6000d6f4` construct a pool descriptor on the stack:

- `0x6000d6fc` loads the end `0x62000000` from decoded literal `0xd768`.
- `0x6000d6fe` loads the start `0x606634d0` from literal `0xd76c`.
- `0x6000d700` subtracts start from end; `0x6000d702` stores size and start.
- `0x6000d708` calls thunk `0x60054ee4`, which transfers to pool creation at
  `0x010033b8` (decoded `0xd3c44`).
- The original initialization path at `0x6000d740` calls this heap initializer.

Only the start literal at `0xd76c` changes, from `d0346660` to `00606660`.
The descriptor remains entirely within the stock heap interval. Its end is
unchanged, and the original subtraction derives the smaller capacity.

A second literal containing `0x606634d0` occurs at decoded `0xd8a64`, relocated
to `0x010081d8`. Executing the unchanged helper at `0x010081c8` returns
`r0/r1/r2/r3 = 0x01015368/0x606634d0/0x01015368/0x606632d0`. This matches
[Arm's legacy stack/heap-boundary ABI](https://support.arm.com/documentation/dui0378/e/the-c-and-c---library-functions/legacy-function---user-initial-stackheap--):
equal heap bounds and a 512-byte stack ending at the original heap start.
That identification is an inference from the instructions and ABI, not a
recovered symbol name. These bounds are preserved; neither interval overlaps
the code reservation.

| Interval, end exclusive | Use |
| --- | --- |
| `0x606634d0..0x60664000` | Reserved alignment gap after static SDRAM |
| `0x60664000..0x60665a4c` | 6,732 bytes of mainline code/constants |
| `0x60665a4c..0x60666000` | 1,460 bytes of reserved code headroom |
| `0x60666000..0x62000000` | Stock heap after reservation |

The reservation is 11,056 bytes, about 0.041% of the original 26,856,240-byte
heap. Remaining capacity is 26,845,184 bytes. Original private stack/general
pools are unchanged. Stock SDRAM MPU region 6 remains read/write/executable;
the reservation is not an MPU write-protection claim.

## Startup and verification

The 1,512 state bytes and 6,732 code bytes are packed at decoded offset
`0xe0448`. Empty startup copy 4 loads the state into `0x01017264`; empty copy 8
loads code into `0x60664000`. The original final SDRAM zero ends exactly at
`0x606634d0` and cannot erase the code. No originally nonempty copy/zero operation
is modified. Build evidence records both copies, section file offsets, all
expected/replacement bytes and the heap reservation.

`tools/sdram_code_verify.py` executes original RTOS pool initialization,
`0x6000d6f4`, pool creation and allocation primitive `0x01007604` (decoded
`0xd7e90`). The test compares original/candidate pool records, performs small,
4-KiB and 1-MiB allocations, allocates the remaining largest block, and checks
that another request returns null. All allocator writes stay in the adjusted
heap; the complete reserved interval remains unchanged.

SCB state is modeled as thread mode. The scheduling decision at `0x01008e02`
returns 1 to avoid a task switch. Allocations enter the original low-level
primitive rather than task wait/free wrappers. No allocator or arithmetic
routine is replaced. Harness code pages are write-protected as an additional
test guard; this is stronger than the unchanged hardware MPU policy.

Main-application instruction harnesses leave `0x01018000..0x01020000` unmapped,
so the old faulty placement can no longer pass by assuming that region is RAM.
Dirty-start tests verify state, both copies and neighboring sentinels.

The tests establish allocation exclusion, not peak memory usage. A workload
that formerly needed nearly the entire heap could exhaust it earlier. SDRAM
execution may have different latency from private SRAM; real generator IRQ
margin, USB interaction and sustained workload behavior require hardware tests.
