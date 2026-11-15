# B11 completion-relative polling, 15 November 2026

[B10 on hardware](../fm1-pipeline-b10-20261115/bench-20261115.json) delivered
1,341 packets with gaps but delayed MIDI replies until expiry. Its first/last
snapshots showed TX API/core/HCD counts 33 with only 32 application completions.
RX had entered core submission 11 times but returned only 10, even though HCD
had accepted all 11. The controller worker progressed from 93 to 137 polls while
those counters stayed fixed. This points to missing USB-core progress, without
proving the precise RTOS wait or starvation cause.

## Concrete change

B10's compiled polling callback cleared `poll_pending` before entering
`ehci_service`. An audio tick could therefore enqueue a successor while service
was still executing. With sufficiently long service, the worker could remain
continually queued. Original task creation assigns numeric priorities 1 to the
audio task, 15 to HCD and 16 to USB core. These assignments and the compiled B10
callback ordering are in [instruction-evidence.txt](instruction-evidence.txt).
Continuous worker requeue is a plausible explanation for the observed core
stall, not a measured RTOS trace or an established hardware root cause.

B11 retains the pending latch until the callback has finished service. It then
sets the next eligibility time relative to completion: 16 audio ticks for
poll-only probe 9 and 32 for IOC probe 8 (nominally 4/8 ms). A rejected enqueue
also waits the interval. Start initializes a fresh deadline. Wrap-safe elapsed
time comparisons replace global tick-modulo eligibility. This prevents our
poller from immediately queuing successors throughout a long callback and
leaves an interval in which other tasks can progress. It does not guarantee
idle CPU time, task scheduling, or that other producers leave the queue empty.

The two-second silent bypass, packet validation, split masks, DMA retirement,
watchdog, original MIDI requests, B10 pipeline diagnostics and converter policy
remain. No RTOS priority, interrupt register, queue policy, retry or controller
reset changes. Poll latency is service duration plus the configured gap, so
packet gaps can remain or increase. Transport quality is a separate acceptance
criterion. The next test is the same short silent probe and cached stage counts;
useful audio and the nonzero converter gate remain unresolved.

## Placement and checks

Wire build 187; [exact hashes and validation](candidate.json). The sole mainline
builder remains. Hot code remains 3,592 bytes; hot state remains
1,472 bytes. Audio/debug code is 14,540 bytes at `607f0000..607f38cc`, leaving
1,844 bytes. A single four-byte deadline appends at `607fb254..607fb258`, after
all prior state. Every existing DMA/counter/cache address remains fixed. Total
audio/debug state is 29,272 bytes within the same 64-KiB reservation. No new
original patch site is added; the builder records guarded startup lengths,
relocations, branch targets and component checksums. Main application, boot
programs, updater, panel and container boundaries are unchanged.

The audio tick frame grows from 184 to 192 bytes; the service and debug-command
frames remain 56 and 344 bytes. The poll callback adds an eight-byte frame.
These individual frames are not a total stack high-water measurement.

The focused ARM check passed. At the compiled worker service entry, a second
machine executes the compiled audio tick with a copied state to model preemption
after 64 elapsed audio ticks. Both policies retain the latch and enqueue no
successor. Further ticks check the complete post-callback gap. Rejected-enqueue
and 32-bit wrap fixtures also pass. Existing no-IOC packet transport, MMIO-write
exclusion, retirement, original request ABI and cached page tests remain.

This model executes extension instructions but does not run a preemptive RTOS,
measure CPU time, or establish real USB scheduling. The full reproduction and
committed-image/browser results are recorded in candidate.json. At build time B11 was not yet
installed. Keep UNTESTED and PR #21 open pending physical acceptance. FM bridge
B1 needs no update.

All 17 offline stages and the current-artifact gate passed. The subsequently
strengthened [preemption check](poll-preemption-check.json) also passes a
negative control: releasing the latch at the same eligible tick admits a
successor, while the retained latch admits none. This adds no firmware change.
The committed-image gate and all six browser-patcher tests passed against
code/artifact commit `9f04955463bbf31ff2c9aeff77eaf6e22edfc5d5`.
Hosted B11 verification also passed for `5ba9871` ([run 85](https://github.com/karlsander/mxplus/actions/runs/43735461007)).

## Observed on B11, 15 November

[Sanitized bench](bench-20261115.json). Poll-only probe 9 now returned diagnostic
MIDI status during the running stream: three phase-2 replies arrived before the
final stopped reply. First/last pipeline counters advanced (RX core 11 to 13,
TX core 78 to 88), with no MIDI fault or retained first failure. This is short
diagnostic coexistence evidence, not sustained musical MIDI or latency acceptance.

| Mode | MX packets | Malformed | Overflow | Underrun | Schedule corrections |
| --- | ---: | ---: | ---: | ---: | ---: |
| Poll-only | 999 | 0 | 0 | 267 | 660 |
| IOC | 1,638 | 0 | 4 | 151 | 212 |

The subsequent short IOC run again delayed status until expiry, with unchanged
pipeline counters and a TX urgent-queue overflow. Poll-only is the useful baseline
for further work, but its packet gaps are substantial. All final states returned
to FM alt0/tone0 and MX inactive/unclaimed. Diagnostic replies recovered; after
IOC, musical TX remains stopped by fault 4 until rebind. No converter or audible
test ran. The next candidate moves unchanged descriptor helpers into already
reserved internal SRAM and measures worker elapsed time; faster code and clean
transport remain hypotheses until observed.
