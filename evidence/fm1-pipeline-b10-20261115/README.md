# B10 MIDI request pipeline diagnostics, 15 November 2026

B9's poll-only and IOC probes both delivered PCM packets while MIDI replies
waited until stream expiry. In poll-only mode the controller worker processed
155 status queries with only two event callbacks, yet software TX was busy and
no matching TX wrapper was sampled. [B9 bench evidence](../fm1-poll-b9-20261115/bench-20261115.json).
This does not establish whether the API call was blocked, the USB core had not
submitted the request, or a controller completion was awaiting dispatch.

## Change and limits

B10 adds seven independent lifetime counters per MIDI direction: API entry and
return, USB-core submission entry and return, HCD submission entry and return,
and application completion callback. Each stage records count, latest audio
tick, and a stage-specific value. No counter is reset on another request or
USB rebind; an older return cannot erase the next request's entry. Counts can
wrap. Cross-stage reads are observations of separate tasks, not an atomic
transaction, a per-request trace, or measurements of task execution time.

The worker copies these fields alongside its existing first/last snapshots.
Pages 15/16 return the first RX/TX counters; pages 17/18 return the last. They
use the corresponding async snapshot's sequence, tick and phase. MIDI reads
only cached RAM and cannot follow a saved pointer. Incomplete or wrong-port
snapshots return unavailable. Cache publication is sequence-guarded; the live
stage triples themselves may change between fields. No arbitrary memory or
controller-write command is added.

Probe 9 and probe 8 retain B9's service policies, expiry and converter bypass.
There is no proposed transport or converter fix in B10. The next short silent
capture should identify the missing submission/completion handoff before any
scheduling change. Musical MIDI and audio coexistence remain unaccepted.

## Original instructions and ABI

All addresses below are **app_usb**. Resident runtime is decoded offset plus
`60000000`; hot relocation maps decoded `2b1f4` to runtime `01000300`, length
`bbe4`. [Original disassembly](original-disassembly.txt).

- `9464` / `60009464`: the asynchronous API allocates a 48-byte request and
  queues it. The extension sets busy before this call, so busy alone is not
  proof the call returned or the HCD saw a request.
- `f81a` / `6000f81a`: core submission validates the request and allocates
  completion state before enqueueing the HCD operation. The only new original
  patch site replaces exactly `2de9f04704464d480027`. The trampoline reproduces
  the push of r4-r10/lr, r4 assignment, literal load of `6002b0dc`, and r7 zero,
  then resumes at `6000f825`. The wrapper preserves the original integer return
  and records only requests carrying our callback and token 0..7. It saves the
  token before calling the original body because that body can free the request.
- Existing driver wrapper `mx1_ehci_request` records entry/return around original
  `111ee` / `600111ee` only for a managed MIDI flight endpoint. All nine ABI
  arguments and the original result are retained. Audio private requests still
  take their existing paths.
- Original `f60a` / `6000f60a` invokes the application completion callback before
  releasing its request. B10 records that callback without changing the original
  dispatcher, cancellation, retry, queue policy, interrupt masks or priorities.

The build report records replacement bytes, branch targets, relocation and
component checksums. The original whole-input hash guard remains unchanged.

## Placement and verification

[candidate.json](candidate.json) records exact identities. Wire build is 186.
Hot code is 3,592 bytes at `0100bee4..0100ccec`; hot state stays 1,472 bytes.
Audio/debug code is 14,416 bytes at `607f0000..607f3850`, leaving 1,968 bytes in
its code slot. Existing DMA buffers and all pre-B10 diagnostic fields stay at
their prior addresses. The async structure grows from 536 to 872 bytes ending
at `607fafb4`; 672 bytes of lifetime counters follow through `607fb254`.
Total audio/debug state is 29,268 bytes within the existing 64-KiB reservation.
Main application, boot programs, updater, panel and container boundaries remain
unchanged. No second builder or candidate is added.

Individual compiled audio/service/debug-command frames remain 184/56/344 bytes;
the EHCI request wrapper frame is 120 bytes. These are function frames, not a
proof of total stack high-water use. Actual interrupt/RTOS timing is unmeasured.

Targeted MIDI and audio checks passed. New instruction tests execute the patched
original core prologue/body for success, timed-allocation failure and completion;
compare unrelated callbacks with the original image; reject invalid tokens; and
check API accepted/rejected counters plus HCD arguments, results and callee-saved
registers. Snapshot fixtures check first/last retention, port/sequence guards,
and cached reads after live controller/heap memory is unmapped. Allocator,
queues, RTOS delivery, DMA and hardware remain modeled boundaries. Full pipeline,
committed-image and browser checks are recorded in candidate.json.

B10 has not been installed. Keep UNTESTED and PR #21 open pending physical
transport, converter, audible and sustained coexistence results. FM bridge B1
needs no update. The authorized bench script defaults to one short silent
probe and collects pages 15..18 before another start; both-policy comparison
remains optional.

All 17 offline stages and the current-artifact gate passed. The candidate hash
remained unchanged through reproduction. The committed-image gate and all six
browser-patcher tests passed against code/artifact commit
`1fc19931e19ea99f8867ab8d06bc0e73ab2f44b3`. Hosted B10 verification remains pending.
