# B8 asynchronous MIDI snapshots, 15 November 2026

[B7 on hardware](../fm1-startup-b7-20261106/README.md#observed-on-b7-15-november)
accepted 53,971 audio packets, but MIDI replies stalled during the stream.
They resumed after expiry without reconnect. The first TX failure was urgent
queue overflow while a transfer was busy, with no terminal transfer error.
B7's software fields cannot distinguish a still-active controller transaction
from a completed qTD whose callback has not been processed. Its separately
primed converter run also rejected a nonzero entry gate after three successes.

B8 adds the missing controller-side evidence. It does not alter split masks,
periodic placement, MIDI submission/completion, USB interrupt handling or the
converter's rejection behavior. FM-1 keeps its installed bridge B1. Automatic
EHCI audio startup remains disabled; other generic audio profiles stay disabled.

## New bounded diagnostic behavior

The HCD worker copies the current FM's original EP1 bulk request wrappers,
QH overlays and first/last qTD status. A snapshot is taken at most once per
128 audio ticks (nominally 32 ms), plus an observation when worker service sees
stop intent. One record freezes after 4,000 ticks; the other retains the last
sampled running state. A new transport start attempt resets both records.
Stop/rebind does not dereference or erase saved descriptor addresses.

The worker bounds the original active-list walk to 16 requests and accepts
only matching device pointer, EP1, bulk type and direction 0/128. Wrapper,
private structure and qTD array reads require aligned SDRAM pointers within
`60400000..607f0000`; QHs must be 64-byte aligned in the original QH pool;
qTD count is limited to four and qTD pointers must be 32-byte aligned. Rejected
pointers/counts set diagnostic error flags instead of being followed. This is
a bounded read of live, worker-owned structures, not arbitrary memory access.

Pages 11/12 expose the frozen RX/TX record; 13/14 expose the last RX/TX record.
Each response is 40 words (210 SysEx bytes), within the existing 240-byte
buffer. It includes software sequence/tick/phase, IRQ-event and fallback-poll
counts, event bits, validation flags, live controller registers and 26 words
for that direction. MIDI reads only the cached record. Sequence checks detect
a concurrent software writer; DMA can still advance between copied words.
[Exact protocol and field order](../../docs/DEBUG_BRIDGE.md).

Probe 8 runs the existing transport-only mode for 8,000 audio ticks (nominally
two seconds). It uses the same normal retirement path and never enables a tone
or falls back to conversion. Probes 5/7 and explicit modes remain available.
The default bench script now runs the short silent probe and reads pages
through 14 after retirement. `--extended` explicitly selects the longer
tone/converter sequence. Neither sequence runs in offline reproduction.

## Original instruction and hardware-register basis

All findings here concern **app_usb**. Resident runtime equals decoded offset
plus `60000000`. Hot code relocates decoded `2b1f4` to runtime `01000300`,
length `bbe4`. [Original instruction excerpts](original-disassembly.txt).

- Decoded `111ee`, runtime `600111ee`, constructs a 72-byte request wrapper,
  puts the controller/address at +8/+10, speed at +12, endpoint/direction/type
  at +14/+15/+16, request/completed byte counts at +40/+44, device and endpoint
  objects at +48/+52, and its 16-byte private structure at +68. It adds the
  wrapper to the controller's list at +`84` through `6000a9f8`.
- Decoded `a8ee`/`a9f8`, runtime `6000a8ee`/`6000a9f8`, initialize the list and
  add a member. The count is list +8, hence controller +`8c`. Decoded `ac44`,
  runtime `6000ac44`, traverses the indexed member. The new check executes this
  original constructor and traversal; it does not infer layout only from C
  fixtures or decompiler types.
- The private structure's QH, qTD pointer array and count are exercised through
  the original bulk constructor `60011fde` and existing instruction harness.
  Original allocator/QH placement is established in
  [B5 evidence](../fm1-ehci-split-b5-20261106/README.md).
- Decoded `34480`, runtime `0100958c`, reads EHCI status, stores controller
  +`14`, acknowledges status and conditionally wakes the original IRQ task.
  B8 counts calls into the existing worker event wrapper; it does **not** claim
  to count physical interrupts or change this ISR.

QH overlay and qTD token interpretation follow Intel EHCI 1.0 §§3.5.3 and
3.6.3 ([primary specification](https://www.intel.com/content/dam/www/public/us/en/documents/technical-specifications/ehci-specification-for-usb.pdf)).
An Active bit distinguishes pending from completed controller work; neither
value alone explains why progress or callback delivery stopped.

## Placement, checks and remaining work

Exact identity and validation results are in [candidate.json](candidate.json).
Hot code remains 3,180 bytes and hot state 1,472 bytes. Audio/debug code is
13,920 bytes at `607f0000..607f3660`, with 2,464 bytes remaining in its slot.
Existing DMA, converter and first-failure addresses remain unchanged. The new
532-byte state appends at `607fac4c..607fae60`; total audio/debug state is
28,256 bytes, inside the existing 64-KiB USB SDRAM reservation.

The compiled audio wrapper still has a 184-byte frame including saved
registers. The worker service frame is 56 bytes; debug command frame is 344
bytes. These are individual frames, not total stack high-water measurements.
Original HCD worker creation reserves 2,048 bytes; original audio task reserves
1,024. No extra allocator reservation or original patch site is added.

Focused checks run original bulk construction/list traversal and the compiled
capture/readout, then model DMA completion to distinguish active/completed
tokens. They check frozen-versus-latest records, pointer/count rejection,
incomplete-record rejection and cached reads with live MMIO/descriptor memory
unmapped. The short probe's manager dispatch and timeout value are checked;
the existing mode-3 expiry and retirement instruction checks remain. Heap,
DMA/MMIO, RTOS delivery and DSP responses remain modeled. No timing or audio
acceptance follows from these tests.

Only app_usb changes. Main application, boot programs, updater, panel payload
and container boundaries remain unchanged. Whole-input and exact-site guards
remain; the builder records bytes, relocation, callback targets and component
checksums. Keep `UNTESTED` and PR #21 open pending physical audio acceptance.

All 17 offline reproduction stages, current and committed-artifact gates,
and six browser patcher tests passed for code/artifact commit
`5613a1a2d5b3299eba9284532b9c53f1a3e49a94`. Hosted verification and B8
installation are pending at preparation.

On 15 November B8 was copied as `MX1_UPD.BIN` to the identified Roland updater
volume, readback hash-verified and safely ejected. [Copy receipt](copy-20261115.json).
Update completion and normal boot remain unobserved at the time of copying.
