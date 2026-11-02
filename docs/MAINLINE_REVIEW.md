# Mixer-only mainline review — 2 November 2026

The review restores the pre-generator firmware exactly rather than keeping a
partially disabled generator integration. Maintained container SHA-256:
`88457445ffe1abeca8365198d0c15ed967c6f5b4dac08393da52c575a80660ba`.
It matches the artifact from `eb646b6cb3ad7f271097c4ab41f2098ab1399576` byte for
byte. All active firmware C/assembly and the linker script match that baseline;
new changes strengthen offline checks and update documentation. No additional
production defect was established by this review within the retained scope.
This is a bounded source/binary review, not proof that the firmware has no bugs.

## Failure-oriented checks

| Risk | Review and evidence | Remaining boundary |
| --- | --- | --- |
| Generator path accidentally retained | New retirement assertions check the original sample callback, transport, SELECT/pad handlers and heap literal; no generator exports remain | Does not claim stability of removed code |
| Existing saved NSE/BD IDs break startup or scenes | New actual-instruction tests load 53/54 through normal boot and scene recall; they become Auto, preserving other routes and stored scenes | Physical flash reads/writes are modeled |
| Reintroducing failed private memory | `0x01018000..0x01020000` remains unmapped in all main-app instruction harnesses; startup tests dirty only modeled intervals | Actual cause of that interval's failure is unknown |
| Writes into read-only code or overlap with stock pools | Original MPU execution, page protection, exact ELF object placement, dirty startup, pool-init sentinels and original copy/zero comparisons | No physical memory fault delivery is emulated |
| Out-of-range routing or altered ordinary controls | All 53 choices across 11 strips, mono skips, endpoint clamps, invalid indices, modal/page/multiple-key exclusion, SELECT release and original control delegation | Panel delivery and scheduler edges are modeled |
| Corrupt scenes or extra flash writes | Four existing reserved words per record; original 64-scene copies and autosave registration/deadline run; malformed records, cache-refresh preemption and unchanged unrelated bytes checked | Full scheduling races, power-loss durability and physical persistence acceptance remain open |
| Routing changes interfere with normal audio | Original input operands, command writers, connection callbacks, External Mixer/diagnostic exclusions and raw PC operand independence checked | Numeric DSP execution and click-free frame transitions are not modeled |
| USB control/descriptor regression | Fixed generated descriptor graph, all three rates, request lengths, unsupported requests, clock replies, endpoint tables, failure returns and backup-mode invariants checked | Physical packet boundaries, mixed alternates, capture-only, all channels/rates and sustained operation remain incompletely tested |
| Wrong image or collateral firmware changes | Exact immutable input hash, expected original patch bytes, relocation accounting, original decoder/updater checks and committed-artifact identity | Normal updater preservation alone is not universal recovery |

The retained sample path is Roland's original callback, with the established
capture-first instruction change. Routing edits execute in the existing DSP
parameter task. USB descriptor/control changes run in their original setup
paths. No custom generator, per-sample synthesis, transport hook, new autosave
routine, heap reservation or MPU change remains.

## Validation and observations

The full 17-stage offline reproduction passes, including 32 unit/descriptor
checks and five bridge tests, plus original ARM startup/boot/MPU, routing,
storage, USB and container checks. `check_reproduction.py` validates matching
artifact/report identities; `--check-committed` additionally compares Git's
actual candidate/application/load-image blobs. CI runs the same pipeline.

The user previously confirmed normal boot and an analog-input → iPhone/AUM
processing → another MX-1 channel round trip on this exact image. The routing
predecessor passed routing/end-stop tests. These observations do not establish
physical snapshot/restart persistence, every USB alternate/rate/channel,
long-duration stability, PLL lock, or universal recovery. The currently flashed
callback-isolation image is a different diagnostic; restoring this repository
does not itself install the restored firmware on the mixer.

## Space for future mixer features

The internal code slot is 2,396 bytes; current code/constants use 2,376 bytes,
leaving 20. The separate writable state reservation is 400 bytes. Simple
behavior changes may replace existing instructions, but larger control/routing
features need size optimization or a separately reviewed placement. An explicit
SDRAM reservation booted during the retired experiments and may be suitable
for infrequent control work; it is not enabled here, and no future feature is
prevalidated by that result. See [the DSP handoff](GENERATOR_RESEARCH.md).
