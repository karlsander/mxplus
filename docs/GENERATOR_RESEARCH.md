# Generator/DSP handoff — retired 2 November 2026

## Current decision

Keep the MX-1 a mixer. The user explicitly retired NSE/BD generators and the
steady/blinking SELECT editing mode after activation repeatedly froze the
mixer. They are absent from the active sources, builder, tests and firmware.
There is one maintained build. Reintroduction requires a new explicit task;
this document is evidence for planning, not authorization to flash or restart
that experiment. Host-port unlocking remains separately retired.

Mainline restores the exact pre-generator image
`88457445ffe1abeca8365198d0c15ed967c6f5b4dac08393da52c575a80660ba`:
routing/end stops, stock snapshot/restart route storage and USB-B UAC2. It
previously booted and passed the user's iPhone/AUM duplex path. The per-sample
callback is original again, apart from the established capture-first edit
inside the USB pump. Current code/state layout: [MAINLINE.md](MAINLINE.md).

## Hardware observations

All observations were user reports from this MX-1, not debugger or bus traces.
Full identities and offline reports are linked below.

| Image SHA prefix | Change tested | Observed result |
| --- | --- | --- |
| `88457445` | Pre-generator internal-code build | Normal boot; iPhone/AUM audio round trip |
| `08b8f2f7` | Generators/editor with code at `0x01018000` | Dark normal boot; TAP updater available |
| `3c9d769e` | Guard inactive generator writes and startup UI | Still dark |
| `dac455b5` | Pre-generator features alone at `0x01018000` | Still dark; isolates placement/load change |
| `232a1e87` | Full features in reserved SDRAM | Boots; P9r → NSE freezes before label changes |
| `b294ea0d` | Compute samples into owned RAM | Same freeze |
| `4010c85b` | Also use established P9r DSP operand for NSE/BD | Same freeze |
| `f4f5b93e` | Also bypass renderer in sample callback | User confirms selection no longer freezes |

The last test establishes that removing active renderer invocation changes the
outcome. The inferred physical sample writes and new DSP read operands were
already absent in the preceding failing test. It does **not** establish a
precise CPU fault, interrupt overload, stack failure or SDRAM timing defect.
Slow SDRAM execution was a working hypothesis, never measured. No internal-
SRAM renderer test was performed. Neither generator sound nor the proposed
exchange bank was validated. BD was not independently tested. Exact rate,
transport state and duration were not consistently recorded.

TAP rollback restored working firmware after the observed dark application
boots. That is evidence for those failures, not a universal recovery route.
See [boot investigation](BOOT_REGRESSION.md), [freeze evidence](../evidence/generator-freeze-20261102/README.md),
[route isolation](../evidence/generator-freeze-20261102/route-isolation/README.md),
[callback isolation](../evidence/generator-freeze-20261102/callback-isolation/README.md)
and [iPhone evidence](../evidence/iphone-aum-20261102/README.md).

## Memory findings

The established internal code slot is `0x0100f6a4..0x01010000` (end-exclusive),
2,396 bytes. The restored extension uses 2,376 bytes: **20 bytes remain**.
Its 400-byte writable state lives separately at `0x01017264..0x010173f4`.
Code pages become read-only under the original MPU; moving mutable objects
there caused earlier problems. Remaining writable address space is not extra
executable space. Do not treat a permissive emulator mapping as physical RAM.

The location-only test at `0x01018000` failed even without generators. The
underlying cause—absent memory, aliasing, bus permissions or another constraint—
was not identified. Current instruction harnesses leave `0x01018000..0x01020000`
unmapped to prevent that unsupported assumption from returning.

An explicit SDRAM reservation at `0x60664000..0x60666000` did boot. The old heap
began at `0x606634d0`; moving its start to `0x60666000` reserved 11,056 bytes,
including alignment, with end `0x62000000` unchanged. Original pool creation
and allocation-through-exhaustion checks passed offline. This reservation is
**removed from current mainline**. Its instruction evidence is in
[SDRAM_CODE.md](SDRAM_CODE.md), scoped to the historical build. SDRAM remained
writable/executable under the stock MPU; emulator RX protection was stronger
than hardware. Peak heap usage and interrupt-time costs were not measured.

Ordinary control/routing changes may replace existing instructions or fit after
size optimization. Larger features need a separately reviewed placement plan.
Reserved SDRAM is a plausible option for infrequent control logic; the boot
result does not guarantee every future feature's stability. A split placing
only time-critical DSP routines into internal SRAM was proposed but never
built or tested. Check compiled call-graph size, constants, branch reach and
stack usage before assuming it fits.

## Addresses and integration cautions

These refer to the main application. Resident runtime addresses are decoded
offsets plus `0x60000000`. For the original hot block, runtime `0x01000300`
corresponds to decoded `0xd0b8c`.

- Sample callback pointer: decoded `0x168c`, runtime `0x6000168c`, original
  target `0x01009841` (Thumb pump entry `0x01009840`). The retired wrapper ran
  that pump first, then the renderer. Registration and original IRQ dispatch
  were traced without requiring an attached USB host; physical cadence and
  timing were not measured.
- Retained capture-first change: decoded `0xda292`, relocated runtime
  `0x01009a06`, within the original USB pump. It is independent of generators.
- Proven stock CPU USB sample ports: playback `0x40101000..0x40101044`, capture
  the following 18 words. Proposed generator writes were
  `0x40101100..0x4010112c`, with DSP operands `0xa040` and `0xa041 + strip`.
  No physical capacity or validity at those inferred indices was established.
  The generic writer's address calculation does not prove hardware support.
- Transport hooks were decoded `0xa7dc`, `0xa810`, `0xa894`. Extra panel hooks
  were `0x10516`, `0x10538`, `0x140c2`, `0x13740`, `0x14692`. All are stock again.
  Existing routing retains the event callback at `0xf5d8` and display hook at
  `0x13356`, without the extra editor.
- Source IDs 53/54 were NSE/BD. Current restore treats them as invalid/Auto;
  IDs 0..52 are unchanged. No BD patterns were ever persisted.

The retired renderer used integer synthesis and aligned state publications,
without allocation, parameter lookups, flash calls or DSP command writes in
its audio path. Offline numerical/ABI tests passed, but the hardware froze.
Instruction counts are not timing measurements. An emulator's mapped MMIO,
thread-mode stack and explicit interrupt calls omit critical hardware behavior.

## Recoverable history and next investigation

The last maintained full-feature source is commit
`5f13f99cb69468ee0d1e930b05d0752e09a5de68` on PR #7 before retirement. The SDRAM
implementation originated at `cb0124c49333ce0f54b091a0d7a60908fef26537`.
The user-supplied recovery archive's attribution and hashes remain in the
[import record](../evidence/internal-sources-import-20261102/README.md).
Diagnostic source deltas and reports are retained in evidence; no alternate
active firmware codebase is needed to preserve the research.

If separately authorized later, first establish a bounded execution budget
from actual sample interrupts and available cycle counters or instrumentation.
Capture fault/status evidence where practical and establish the real stack
budget. Separate IRQ scheduling from synthesis math and from sample transport.
Prove an exchange location from original usage or hardware evidence before
using it. Do not guess spare ports, reuse live PC channels, expand MPU regions,
or borrow allocator-owned memory without independently verifying the effects.
Keep unrelated routing/USB/boot components unchanged in each isolation test.
