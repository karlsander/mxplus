# B9 short polling comparison, 15 November 2026

[B8 on hardware](../fm1-async-b8-20261115/README.md#observed-on-b8-15-november)
accepted 974 packets but stalled MIDI replies. Both running snapshots found
the FM's Active MIDI IN request and no matching MIDI OUT wrapper, with no
pointer/count validation error. Software TX was busy. These samples motivate
checking request processing and interrupt pressure; they do not establish
which task was delayed or why. The converter rejection remains unresolved.

## Concrete experiment

B9 retains probe 8 and adds probe 9 in the sole mainline image. Both initialize
the existing converter context, bypass converter submissions, enable no tone,
and expire after 8,000 audio-task calls (nominally two seconds). Probe 9 clears
IOC only on the experiment's siTDs and uses the existing controller-status
worker queue every 16 ticks (nominally four ms). Probe 8 retains IOC and the
32-tick fallback. This compares two service policies; polling cadence also
differs, so a successful comparison cannot attribute causality only to IOC.

The original MIDI API, bulk/control interrupts, controller registers, split
masks, packet validation, ownership and retirement are unchanged. One query
at most remains pending. The existing service-gap watchdog remains. A delayed
worker can still cause gaps or retain ownership; no new reset/retry is added.

The manager packs the policy in the private start request's flags word before
clearing its command. Only the recognized start callback/token interprets it;
unknown policy values are rejected. The worker copies it before arming the
ring. Later ordinary starts reset the policy. No stale manager command is
consulted by the worker. Other devices and periodic profiles remain excluded.

The bench script defaults to probe 9. `--compare-ioc` runs both short modes,
with stop/alt0/setup between runs; `--short-probe 8` reverses their order.
It records acknowledgement times, samples live MIDI status if available, and
reads retained snapshots before another start. Final FM status is now read
after alt0. First-failure pages remain first-since-boot; async pages reset per
start. FM bridge B1 needs no reflash. No bench command runs in reproduction.

## Original instruction evidence

All addresses here are **app_usb**, not main/updater. Resident runtime equals
decoded offset plus `60000000`. Hot relocation maps decoded `2b1f4` to runtime
`01000300`, length `bbe4`. [Original excerpts](original-disassembly.txt).

- Decoded `9464`, runtime `60009464`, constructs the asynchronous MIDI API
  request and queues it; a software busy flag does not imply HCD submission.
- Decoded `34480`, runtime `0100958c`, acknowledges EHCI status and wakes the
  original IRQ task for completion status when its active-list count is nonzero.
- Decoded `10526`, runtime `60010526`, waits for a wake, allocates an event and
  posts the saved status to the HCD worker. No timing follows from this code.
- Worker decoded `beac`, `bf46`, `bf7e` / runtime `6000beac`, `6000bf46`,
  `6000bf7e` dispatches requests, status queries and events through the driver.
  The existing actual-instruction query/worker test establishes the callback ABI.

siTD IOC interpretation follows EHCI 1.0 section 3.4.3
([Intel specification](https://www.intel.com/content/dam/www/public/us/en/documents/technical-specifications/ehci-specification-for-usb.pdf)).
This build does not modify the original ISR or its task, infer a queue policy
from decompiler arguments, or assert interrupt starvation as the root cause.

## Binary identity and checks

[candidate.json](candidate.json) records exact hashes and validation status.
Wire build is 185. USB hot code is 3,180 bytes, hot state 1,472 bytes;
audio/debug code is 13,980 bytes at `607f0000..607f369c` (2,404 bytes spare).
The four-byte policy appends at `607fae60`; existing state/DMA addresses and
cached snapshot offsets stay fixed. Audio/debug state is 28,260 bytes ending
at `607fae64`, within the existing 64-KiB reservation. No allocator boundary
or new original patch site changes. Individual compiled audio/worker-service/
debug-command stack frames remain 184/56/344 bytes; total stack high-water
use is unmeasured. The builder records all original and new
bytes, branch targets, startup relocation and component checksums.

The focused instruction tests pass. They execute compiled probe dispatch and
policy packing, no-IOC descriptors, 128 modeled milliseconds serviced only by
poll callbacks, successful packet validation, bounded pending queries,
stop/grace/retirement, and policy reset on a subsequent ordinary start. A write
hook checks that this path changes no controller register. The original
controller-status constructor and worker dispatcher still execute in the
existing check. DMA/frame progression, RTOS delivery and DSP are modeled;
instruction execution is not USB timing evidence.

Main application, boot programs, updater, panel and container boundaries remain
unchanged. Preserve `UNTESTED` and leave PR #21 open. B9 has not been installed;
MIDI coexistence, useful audio and sustained operation remain physical checks.

All 17 offline stages and the current-artifact gate passed. A mocked bench
control-flow check also passed both-policy ordering, live-status sampling,
mute and the final alt0 read; it accessed no device. The committed-artifact
gate and all six browser-patcher tests passed for code/artifact commit
`cfb88652b1e49c7f76b906cc7ea6758d360ad9ce`. Hosted B9 verification is pending.
