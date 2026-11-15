# B13 service code in SRAM, 15 November 2026

B12's [two short silent probes](../fm1-sram-b12-20261115/bench-20261115.json)
accepted 1,293/1,287 packets with diagnostic MIDI progress, but service elapsed
means of 17.73/18.55 ms, maxima of 26.25/26.63 ms and substantial scheduling gaps.
Those measurements include preemption; they do not identify CPU utilization or
which instructions consume the time. Clean transport remains unresolved.

## Placement experiment

Move `ehci_service` into the existing executable SRAM reservation. Its inlined
packet-copy and asynchronous-capture loops move with it. Make room by placing
five infrequent MIDI enumeration/open/close bodies into the existing SDRAM code
slot. MIDI polling, enqueue, completion and their port state remain in SRAM.
No allocator grows and no additional MPU region, task priority, interrupt mask,
controller register, queue policy, timing interval or transport rule changes.

All nine selected functions match B12 after normalizing local/named branch
targets, resolving named linker thunks and omitting alignment NOPs. Service
has one additional alignment NOP and grows from 1,654 to 1,656 bytes. The other
eight bodies retain their sizes. See [comparison](function-comparison.json)
and [complete disassembly](function-disassembly.txt); the baseline ELF is the
actual Git blob at `d6290453abb5b41be74f86983bb5faab59b88f22`. This is instruction
comparison, not a hardware timing result.

All addresses below are **app_usb**, a separate processor from app_main.
The existing original hot-code mapping is decoded `2b1f4` to runtime `01000300`,
length `bbe4`. Injected hot code begins at decoded `36dd8` / runtime `0100bee4`.
The SDRAM code copy source begins at decoded `37f1c` / resident `60037f1c` and
is copied to `607f0000`. The builder records the changed copy lengths, moved
initialized-data source literals, exact expected/replacement bytes and callback
or branch destinations. There are no new original patch sites.

| Function | B12 runtime | B13 runtime | B13 decoded offset | Bytes |
|---|---|---|---|---:|
| ehci_service | 607f2102 | 0100c654 | 37548 | 1,656 |
| ehci_unlink | 0100cca0 | 0100cccc | 37bc0 | 102 |
| ehci_arm | 0100cd06 | 0100cd32 | 37c26 | 224 |
| ehci_path | 0100cde6 | 0100ce12 | 37d06 | 284 |
| mx1_host_config | 0100bee4 | 607f0000 | 37f1c | 1,008 |
| mx1_host_select | 0100c2d4 | 607f03f0 | 3830c | 70 |
| mx1_host_setup | 0100c31a | 607f0436 | 38352 | 128 |
| open_port | 0100c57c | 607f04b6 | 383d2 | 288 |
| close_port | 0100c6a4 | 607f05d6 | 384f2 | 128 |

Runtime entry pointers set Thumb bit zero to one; the table gives instruction
addresses. Original call ABI, stack/register preservation and function results
are unchanged. Individual audio/service/debug-command frames remain 192/72/344
bytes; poll callback is eight bytes. These are not stack high-water measurements.

## Bounds and identity

Wire build 189; [exact hashes and validation state](candidate.json).
Hot code is 4,280 bytes at `0100bee4..0100cf9c`, leaving 100 bytes before the
original allocator at `0100d000`. Hot writable state remains 1,472 bytes.
Audio/debug and setup code is 14,252 bytes at `607f0000..607f37ac`, leaving
2,132 bytes before the state slot. Audio/debug state remains exactly 29,320
bytes at `607f4000..607fb288`, within the existing 64-KiB reservation.
Every DMA, MIDI-state, counter and timing-cache address stays fixed.

Original firmware SHA-256 and all overwrite guards remain unchanged. The main
application is byte-identical to B12; [component/slot comparison](component-comparison.json).
Boot programs, updater, panel payload and
container boundaries remain unchanged. Only the maintained mainline builder,
linker layout and candidate are used. FM-1 bridge B1 needs no update.

## Verification and next bench

Targeted ARM audio checks and the function comparison passed. The builder and
EHCI verifier now enforce the service's SRAM placement and the five setup
functions' SDRAM placement. Existing tests exercise original startup copying,
MPU/allocator bounds, MIDI descriptors and original setup/open/close paths,
request ABI, polling preemption, packet validation, admission and retirement.
USB/DSP/MMIO, allocator and RTOS delivery remain explicit models.
All 17 offline stages, current and committed-artifact gates, and all six
browser-patcher tests passed for code/artifact commit
`c8e03b6566acaa508ce1477daf4eb392009918c0`. Hosted B13 verification also passed for commit `e1d24a883bd9d9d728ee09f8b19a0b4c6e753715`: [run 89](https://github.com/karlsander/mxplus/actions/runs/43747902186).

At build time B13 had not been installed. The planned comparison was the same short
silent poll-only probe, page 19 service elapsed times, packet/error deltas and
MIDI pipeline progress. Do not infer a speedup from placement or instruction
counts. Converter gate repair and audible acceptance remain separate work.
Keep UNTESTED and PR #21 open pending physical audio acceptance.

The candidate was copied as `MX1_UPD.BIN`, readback hash verified and safely
ejected on 15 November 2026; [copy receipt](copy-20261115.json). TAP installation
was pending at that copy; the later boot/bench results follow below.

## Observed on B13

The user confirmed restart on HOST3 and the bridge reported wire build 189.
[Sanitized evidence](bench-20261115.json) retains status delivery times, cached
pages, setup and cleanup; private Bluetooth identifiers are omitted.

| Short policy | MX accepted | FM sent | Malformed | Overflow | Underrun | Schedule corrections | Mean service | Max service |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Poll-only | 1,813 | 2,042 | 0 | 225 | 84 | 22 | 3.596 ms | 5.875 ms |
| IOC | 1,949 | 1,977 | 0 | 25 | 12 | 8 | 1.674 ms | 8.750 ms |

Poll-only returned four running status replies; RX/TX pipeline counts advanced
and no first MIDI failure was recorded. The 275 service calls totaled 7,911
microframes, with zero ambiguity flags. This was substantially shorter elapsed
service than B12's two means of 17.73/18.55 ms. It is not a CPU-time measurement.
FM packet delivery approached the nominal one-per-ms cadence, but the eight-entry
software queue dropped 225 otherwise valid packets. Scheduling gaps remain.

The IOC comparison again delayed status until expiry. First/last RX/TX pipeline
counts were identical; the first TX failure was urgent-queue overflow during
phase 2. Its 491 service calls totaled 6,577 microframes, ambiguity zero.
Diagnostic replies recovered after expiry; musical TX retains fault 4 until
rebind/reboot. Both tests ended MX inactive/unclaimed and FM alt0/tone0. No
converter submission, sustained musical-MIDI timing or audible acceptance was
performed. Poll-only remains the baseline for the queue-depth follow-up.
