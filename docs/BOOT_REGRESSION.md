# Generator/editor boot investigation

## Hardware observations, 2 November 2026

These are user-reported results on the same MX-1, not instrumented fault traces.
Normal boot was checked with USB disconnected. The unit's board revision,
sample rate, precise test duration and fault registers were not recorded.
No USB streaming or generator audio result follows from a boot result.

| Image | SHA-256 | Observed result |
| --- | --- | --- |
| First generator/editor mainline, PR #6 | `08b8f2f783718b8039dc66ddfc14aa2ce13f63447df4df73eb10fa098e77fd94` | Completely dark panel on normal power-on; TAP update mode still available |
| Routing/end-stop predecessor, commit `7bad049115021af47a30b9d91bbc2ec4c92c211e` | `221e5ffb2a858a25d5691a1c818324fafa117bfa48d6a79aac0d666140ff2b95` | Restored via TAP updater; user confirmed normal operation |
| Exact pre-generator mainline, commit `eb646b6cb3ad7f271097c4ab41f2098ab1399576` | `88457445ffe1abeca8365198d0c15ed967c6f5b4dac08393da52c575a80660ba` | Copied from historical Git blob, readback verified and ejected; user confirmed normal boot after update |
| Startup guards, commit `689019e32348370c4fcd0686fa1a153c11522d89` | `3c9d769e97366f7b0e7a929b4d47c0ad7f697928306e5d8f7e4a852ddbcc728f` | Copied and readback verified; user reported the panel still completely dark after normal power-on |
| Pre-generator code relocated to `0x01018000` | `dac455b5634088e9d8f235d9af397821d2dedd46175fc51caca55ad406fa2c12` | Repeated copy/readback/eject on request; user confirmed successful flash and completely dark normal boot |
| Full mainline with reserved SDRAM code | `232a1e87a8c4378ce740c295ed9df7d5659c3645899f4c51747e656c022cfe25` | Normal boot succeeds; selecting the first generator (NSE) freezes before its label appears |

The pre-generator image includes routing, end stops, stock-storage integration and USB-B
UAC2. It excludes generators, the SELECT editor and the new code placement.
This narrows the regression to that later batch. The user separately reported
successful iPhone/AUM duplex audio on the pre-generator image: see the
[hardware record](../evidence/iphone-aum-20261102/README.md). Persistence has
not been separately confirmed, nor has recovery from other fault types.
Historical artifacts remain in Git, not as maintained parallel builds.

## Concrete startup defects corrected

All addresses below are in the main application context.

1. The sample callback pointer at decoded `0x168c` / runtime `0x6000168c`
   invokes the new wrapper after registration, even without USB connected.
   `internal_sources.c` initialized `previous_mask` to `0xffffffff`. Therefore
   its first all-Auto frame wrote twelve zero words to inferred DSP exchange
   ports `0x40101100..0x4010112c`. This was unnecessary hardware access before
   any source selection. Initialize ownership to zero. Diagnostic invalidation
   now resets the rate marker while retaining actual ownership; active voices
   still reset and removed owned ports still clear.
2. The SELECT renderer hook at decoded `0x14692` / runtime `0x60014692` called
   `mx1_sources_ui_edit_target`, which queried mixer parameter `0xfb` through
   `0x6001e65e` before checking the inactive editor or startup/view guards.
   The SELECT press hook at decoded `0x10516` had the same ordering issue.
   Both now gate extension queries first. Stock rendering/dispatch still runs.

The new tests fail against the failed image: an access trap on the exact
generator-port range catches its first idle write, and the UI test observes
parameter queries from the inactive overlay. The corrected code must pass both.
These establish unwanted accesses, **not that either caused the hardware boot
failure**. The inferred port mapping remains unverified when a generator is
selected; parameter storage and hardware delivery remain modeled in UI tests.

## Startup-guard experiment

The startup-guard candidate is
`3c9d769e97366f7b0e7a929b4d47c0ad7f697928306e5d8f7e4a852ddbcc728f`.
It still boots with a completely dark panel. It retains the new code placement at
`0x01018000`, generator features, clock hooks and SELECT editor so the test
addresses the startup accesses without reverting those features. Those guards
are therefore insufficient to resolve the hardware failure.

Original hook instructions and PC-relative literals were rechecked against
the input bytes. Startup, MPU permissions, allocator separation, register/stack
preservation and modeled audio/UI regressions run in the reproduction pipeline.
Code is 6,732 bytes; load data is 10,216 bytes at decoded `0xe0448`, copied to
`0x01017264` by the previously empty copy slot. No original nonempty startup
operation, allocator, MPU configuration, boot/updater, panel or USB-processor
component changes. These sizes describe that historical startup-guard image,
not the subsequent SDRAM build.

The emulated SRAM mapping does not establish physical availability of the new
code interval. The boot harness still stops before the final branch and runs
application startup separately; it does not model complete RTOS scheduling,
interrupt stack margin or board initialization. The location isolation used the
exact pre-generator feature sources and links their code at `0x01018000`.
It preserves the historical startup copies, including an unused duplicate of
the relocated code in the old slot, and repurposes empty copy operation 8 to
also load the code at the test address. This separates execution at the new
address from the generator/editor hooks and their startup-copy redesign. It
also boots dark. This demonstrates that using the new code location/load is
sufficient to reproduce the failure without the generator/editor changes.
It does not distinguish absent memory, aliasing, bus access restrictions or
another physical constraint. See the [isolation record](../evidence/boot-location-20261102/README.md).

## SDRAM reservation correction

The current image is
`232a1e87a8c4378ce740c295ed9df7d5659c3645899f4c51747e656c022cfe25`.
It restores all generator/editor features and links code at `0x60664000` in
the stock SDRAM heap address range. An explicit heap-start adjustment reserves
11,056 bytes, so the original allocator cannot reuse them. Private state stays
at its existing addresses; startup copies state and code separately. Every
original nonempty initialization region, private pool and MPU setup remains
unchanged. [SDRAM code evidence](SDRAM_CODE.md) documents the original
instructions, heap exclusion and remaining performance/workload risks.

The user confirmed normal boot with this corrected placement. Selecting the
first generator in the list (NSE) freezes the mixer before the display shows
its label. Transport state was not recorded; NSE runs independently of transport.
This is a new activation failure, not a continued dark-boot failure. BD, USB
audio on this image, sustained timing and peak heap usage remain unverified.

The next one-off test keeps generator computation and DSP routing unchanged
but sends the twelve computed sample words to owned private RAM. It forbids
CPU accesses to `0x40101100..0x4010112f` in its instruction harness. This is a
selection-stability test, not a working generator-audio image. If selecting
NSE becomes stable, it implicates the physical publication path, including bus
access/timing, rather than the unchanged generator math or route operands.
If it still freezes, route operands and callback timing remain candidates.

The exact diagnostic identity, source delta and offline reports are recorded in
[generator-freeze evidence](../evidence/generator-freeze-20261102/README.md).
