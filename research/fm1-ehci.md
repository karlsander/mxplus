# FM-1 EHCI split input, B5

This is an authorized bench experiment for the measured FM-1 profile, not a
generic host-audio driver. B4 established working bidirectional MIDI commands
and all four setup probes. B5 adds an explicitly started input transport on
controller 1. The later [B5 bench](../evidence/fm1-ehci-split-b5-20261106/README.md#observed-on-b5)
established brief FM-1 packet-counter progress followed by a converter error;
no MX accepted PCM or audible result. [B6](../evidence/fm1-converter-b6-20261106/README.md)
adds transport-only probe 7, mode 3 and converter page 8, and delays running
publication until the complete ring is initialized. The B5 topology, split
masks, admission and DMA retirement below remain unchanged.

## Original instruction findings

All addresses are **app_usb**. Resident runtime = decoded offset + 60000000.
Original hot code relocates decoded 2b1f4 to runtime 01000300, length bbe4.
The original image remains identified by the whole-input hash in the builder.
Disassembly is preserved in
[the B5 evidence](../evidence/fm1-ehci-split-b5-20261106/original-disassembly.txt).

* Binding at 60011d40 (decoded 11d40) installs request 600111ef, cancel
  600113af, reset 600107f7 and event 60011be5. Driver array 6002b0e8 index 1
  selects EHCI; driver +40 holds the controller context. Its +0 is capability
  MMIO, +4 operational MMIO, +8 the original driver's periodic table.
* 60010356 constructs a 256-entry table, one asynchronous anchor and ten
  periodic dummy queue heads. Original allocation 60010316 requests 56 bytes
  aligned to 64. The QH pool comes from allocator class 4: initialization
  6000ad42 uses literal 6000b0d0 = 604807f8, length 14d0. EHCI initialization
  60010576 requests that class through 6000b124 and QH creation uses the
  resulting handle. A queue head can therefore be outside the general heap.
* **That first frame list is not the running audio schedule.** 60010278 calls
  60007faa. The latter creates the active table at 4000b000, links eight
  64-byte stock audio iTDs at 4000b420..4000b620, and writes operational +14
  to 4000b000. It retains a dummy root for entries whose index modulo 8 is 4;
  those heads have link type zero and inactive transaction words. Most entries
  point directly to the shared stock iTD chain. Context +8 is unchanged.
* 60010278 sets USBCMD frame-list size bits to 8 (256 entries), interrupt
  threshold to 00010000, USBINTR to include 33, and starts the controller.
  60007faa enables periodic traversal. B5 requires that existing running
  configuration and does not change these registers.
* The stock general request handler at 600111ee has no ISO construction path.
  Its wrapper handles control, bulk, interrupt and proprietary type 15; ISO
  type 1 is rejected. Stock Roland audio has its own iTD producer, gated by
  the halfword at 4000bbb0; B5 requires that mask to be zero.
* 6000c376 queues opcode 03000020|controller, callback at request +28 and token
  at +24. Original worker 6000bdc8 dispatches at 6000bf46 through driver +1c,
  then calls callback(controller, result, token). This is a controller-status
  query, not an endpoint request. The worker frees the queue record afterward.
  It provides fallback service without retaining a USB object that unplug may
  free. The actual queue and dispatch instructions execute in the verifier.
* Reset 600107f6 can release controller allocations even when cleanup returns
  an error. The wrapper caches only the independent MMIO address across that
  call, clears its context pointer unconditionally after destroy, and releases
  static descriptor ownership only if HCHalted is observed. Otherwise it
  quarantines the buffers until reboot.

The binding patch replaces `fd4a00eb400032f82000` at decoded 11d40. Its
trampoline loads original literal 6002b0f0, repeats the displaced index/halfword
operations, and resumes at 60011d4b. The builder records replacement bytes and
all four wrapper addresses. All other original code remains guarded and intact.

## Transport and admission

One FM-1 stream is admitted at a time. Manager probe 5 requires the existing
validated IF1 alt1 record, initializes the stock converter and queues the same
private start callback used by the OHCI path. The EHCI wrapper recognizes that
callback; ordinary requests retain their original handler. Setup and rebind
still leave EHCI audio off unless this explicit command is running.

The worker validates the current child/parent objects against cached topology:
full-speed child, controller 1, high-speed parent, valid hub address and actual
downstream port. The measured HOST3 topology was parent address 1, port 1; this
does not identify a physical chip or board revision.

Admission allows the inactive stock audio iTDs, original dummy roots and at
most four small (maximum packet 8 bytes) high-speed interrupt QHs per chain.
It rejects any other periodic stream, foreign descriptor type, unknown QH
allocation, active stock audio or unexpected controller/table configuration.
Distinct roots are checked once, with at most 16 roots and 24 nodes per chain.
Each insertion rechecks its chain. This is a narrow admission policy, not a
shared TT bandwidth allocator. A new periodic request during the experiment
gets bandwidth-unavailable −13 while our stream retires; that other endpoint
may need reconnecting. Do not test coexistence with another audio device yet.

The first 32 bytes of each existing 224-byte aligned buffer hold an EHCI siTD;
the 184-byte PCM buffer stays at offset 32. Sixteen slots are used. The endpoint
word encodes IN, EP4, device address, parent-hub address and downstream port.
SS is in microframe 0 and CS opportunities in 2/3/4 (mask 1c01). Backlinks are
terminated. The last-page pointer covers buffers crossing a 4-KiB boundary.

The descriptor format, progress bits and cache window follow Intel EHCI 1.0
§§2.3.4, 3.4, 4.7.2.1 and 4.12.3:
[specification](https://www.intel.com/content/dam/www/public/us/en/documents/technical-specifications/ehci-specification-for-usb.pdf).
The three CS opportunities for a packet below 188 bytes are independently
consistent with Linux's `iso_stream_init` implementation of USB 2.0
§11.18.4 3.c: [primary source](https://github.com/torvalds/linux/blob/master/drivers/usb/host/ehci-sched.c).
No Linux code is copied into the extension.

Publication precedes the target H-frame by at least four frames. The next link
retains the exact old head, including its type bits. Completion is inspected
only at least two frames after its scheduled frame. The inactive descriptor's
remaining-byte count gives the received length; SplitXState bit 1 is not an
error. Active, ERR, buffer, babble, transaction and missed-microframe statuses
are rejected. Accepted 40–46-frame packets use the existing PCM16 queue and
original 44.1-to-96-kHz converter. Per-channel absolute peaks and nonzero-packet
counts are accumulated from accepted packets.

Stop clears wanted/mode, restores only matching heads, and retains all DMA
storage for two more H-frame boundaries. A frozen frame counter retains
ownership; an observed halt allows release. A mismatched head is never
overwritten and prevents release until reset establishes quiescence. Snapshots
are worker-owned, sequence-checked RAM copies, not atomic DMA captures.

IOC normally drives service. A maximum of one controller-status callback is
queued every 32 audio-task calls as fallback (nominally 8 ms). No endpoint
pointer is queued. Service gaps exceeding 400 calls stop the stream. The run
also expires after 240,000 audio-task calls (nominally 60 seconds); those are
cadence assumptions, not measured timing. No automatic restart or USB reset is
added. Explicit stop clears the manager audio-ready bit and stops the converter.

## Verification boundary

`tools/host_ehci_audio_verify.py` runs inside the existing host-audio stage.
It executes original table construction/replacement and controller-query
packing/worker dispatch, then the compiled extension. Heap, IRQ/task setup,
MMIO/DMA completion, queue delivery, general EHCI completion/teardown and DSP
responses are modeled. It checks 300 packet completions across both table and
frame-counter wraps, stereo data, malformed/error rejection, bounded polling,
readout pages, explicit start/stop, unchanged stock chains, frozen counters,
unplugged object lifetime and context release on reset error. This establishes
neither bus transactions nor task timing, sound quality or failed-flash recovery.

The prior converter regression's modeled write hook is now restricted to its
actual register 40040548. With Unicorn 2.1.4, a global memory-write hook caused
incorrect IT-state progression after an unrelated conditional descriptor store
in the new layout. Restricting that hook preserves the original initializer,
audio task and converter instructions under test; no firmware condition is
relaxed to accommodate the emulator.
