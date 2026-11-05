# FM-1 host audio implementation notes

Implementation notes. User authorized integration into the sole mainline image on
2026-11-05. No MX-1 audio result has been observed for this work.

## Established boundaries

The live FM-1 configuration matches `evidence/fm1-host-midi-20261103/`: full-speed,
UAC1, IF1 alt1, asynchronous IN 84, 184-byte maximum packet every millisecond,
stereo 16-bit PCM at nominal 44100 Hz. IF2 alt0 has working bulk MIDI. There is
no audio OUT interface in this profile. Computer evidence is in
`evidence/fm1-host-audio-20261105/`.

All addresses below belong to **app_usb**, independently of app_main. Resident
runtime addresses are decoded offsets plus 60000000. Original hot code is
copied from decoded 2b1f4 to runtime 01000300, length bbe4; translate a hot
address with `decoded = runtime - 01000300 + 2b1f4`.

* 600080a0 requires two audio interfaces, four-byte samples and high-speed
  EHCI iTDs. Its rate division is 8000. FM-1 needs another transport.
* HCD initialization 60009f78 installs OHCI through 60013c74 and EHCI through
  60011d40. Driver pointer array is 6002b0e8. Each driver's +40 points to HCD
  state; OHCI state +8 is register base, +c is HCCA.
* MIDI API 60009464 reaches validator 600141cc with mode1, which rejects
  isochronous endpoints. The lower request queue 6000c276 and cancellation
  queue 6000c31e dispatch in the HCD worker 6000bdc8.
* OHCI request 600132d6 has an unfinished ISO branch: at 60013548 it skips
  TD-count construction, then zero-size allocation fails. Even if allocated,
  600135c4 skips construction. Completion 60013804 skips ISO processing.
  Original instructions were disassembled; decompiler output alone is not
  the basis for this conclusion.
* OHCI endpoint wrapper construction 60013086 establishes full-speed IN ISO
  bandwidth cost and ED fields. Periodic admission 60012fb8 uses the scheduler
  tree and calls ED creation 60012e72. General TDs are 30 hex bytes allocated
  on 16-byte boundaries; these cannot be substituted for 32-aligned ISO TDs.
* OHCI physical/virtual translation functions 60013f76/60013f78 are `bx lr`.
  The done queue's link is word +8 for both descriptor types.
* Original rate conversion init 600079ee(port,1,rate) calls 010082a4 with
  internal rate 96000 (literal 60007a58), independent of USB-B rate. Context
  is 20005ee0 + port*a4. Audio pump 01008c60 runs two microframes per call;
  01008baa calls 010088dc with a packet record.
* 01008476 consumes stereo four-byte samples, shifts integer input by 7 into
  converter MMIO 40040548, and feeds DSP scratch at 40140c00. It uses a
  256-frame float ring for 44100-Hz smoothing at 010157f8 + 70 + port*800.
  Its 40-call scheduling cycle requires maintaining the stock 250-us cadence.
  Drift estimation uses actual input/output counts and the DSP sample counter.
* The periodic wakeup helper 01008b26 reads EHCI frame index masked with fe
  and signals the audio interrupt when that two-microframe value changes.
  Actual call 01004f7e reaches it from IRQ callback 01004f78 (pointer
  01004f79 at decoded 171c8). Original initialization 60007faa enables
  EHCI periodic processing independently of a Roland audio stream. These
  instruction observations support the intended cadence, not measured timing.

## Implemented memory reservation

Current extension hot code: 0100bee4..0100d000, with only about 1.6 KiB spare.
Current state: 01017868..01018000, only 472 bytes spare. Do not overlap USB
allocator blocks 0100d000/0100e000/0100f000 or the RTOS pool 01020000..01028000.

USB startup zeros SDRAM 6002b1f8..604b1178. The first four MiB are an original
DMA ring and are not free. Original general heap creation 600036dc obtains
base 604b1178 from decoded literal 3754, and end 60800000 from 3750.
The extension reserves 607f0000..60800000 by reducing that heap’s end,
with exact guards and original heap-create instruction tests. Formerly empty
startup copy/zero operations initialize the new code/state. The actual startup
and MPU instructions execute in the verifier; see `docs/USB_HOST_AUDIO.md`
for the current placement and bounded test evidence.

## Implemented transport and remaining hardware checks

Keep interface 2 MIDI setup and its existing task ownership. Select only the
FM-1 input format above. Queue audio start to the existing OHCI worker. Publish stop intent for that
worker to consume at completion, avoiding requests through released USB
objects. The worker owns periodic-list edits, completion and cancellation. A
separate bounded ISO descriptor ring is necessary. Split custom ISO completions
from the mixed done queue before the original general-TD handler sees them.
Accept valid short input packets (OHCI data-underrun status), reject errored or
unaligned sample payloads, and treat lost scheduling windows as discontinuities.

Deliver each millisecond's 44/45-frame packet over four stock audio-pump calls,
with buffering for HCD task jitter. Convert signed16 to left-aligned signed32
before the original converter. Preserve its 250-us cadence and drift tracking.
Disconnect must mute before DMA retirement; do not reuse descriptors until
the controller has passed the endpoint and retired outstanding completions.
Offline checks cover controller teardown ownership and mixed general/ISO
completion handling. Real disconnect races, scheduling, converter operation
and mixed Roland/MIDI traffic still require hardware evidence.

Primary format reference: Compaq/Microsoft/National Semiconductor OpenHCI 1.0a,
sections 4.3.2 and 4.4, including 32-byte ITD alignment, modulo-65536 frames,
per-packet status/length and done-list behavior:
https://dl.xkwy2018.com/downloads/documents/hcir1_0a.pdf
