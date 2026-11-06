# Mainline integration

The only maintained custom firmware combines channel routing, mastering editing, USB-B UAC2 and experimental USB-MIDI 1.0.
USB-host MIDI prioritizes sync output and blocks incoming host sync; see [host MIDI](USB_HOST_MIDI.md). The current candidate adds experimental [FM-1 stereo host audio](USB_HOST_AUDIO.md). Other generic host audio remains excluded.
Generators and their SELECT editor are removed; their findings are in
[the DSP handoff](GENERATOR_RESEARCH.md).
The temporary d001 diagnostic menu and main-processor generator SDRAM reservation are absent from this build. Routing now uses scene
and system reserved fields for snapshots and restart persistence; see
[storage integration](ROUTING_STORAGE.md).

The current candidate is
`f9d900f6a17159b89bd59bdf690942fbaa3b6f97d07e66177d4422153de2ad1b`.
B6 adds transport-only startup and converter snapshots after B5's first
device-side audio-packet progress stopped on a converter error; [B6 evidence](../evidence/fm1-converter-b6-20261106/README.md).
It retains B5's explicitly started EHCI split-ISO experiment; [implementation and limits](../research/fm1-ehci.md).
It retains B4’s isolation of the MIDI TX error −20 by using untimed writes only for
the matched FM-1 debug connection; [evidence and limits](../evidence/fm1-midi-timeout-b4-20261106/README.md).
B3 short-input and transmit-wakeup fixes remain.
It retains [stepwise MIDI diagnostics](DEBUG_BRIDGE.md) and pauses automatic audio startup on the observed EHCI controller. The new EHCI transport has offline checks; physical packet/audio acceptance remains open.
The experiment accepts the measured FM-1 full-speed, stereo PCM16 input profile and reuses
the original 44.1-to-96-kHz conversion path. The preceding `253645ed…` image
has a user-reported MIDI-output result with the FM-1; audio on the MX-1 remains unverified.
It fixes [host MIDI startup on an already-active alternate zero](../evidence/host-midi-alt-zero-20261104/README.md).
It retains the fix for the [held-key range that blocked mastering entry](../evidence/mastering-key-range-20261104/README.md).
It replaces timed mastering entry with the [MASTERING + TAP combination](../evidence/mastering-chord-20261103/README.md)
and fixes [FM-1 host-MIDI descriptor rejection](../evidence/fm1-host-midi-20261103/README.md).
It adds [USB-B MIDI](USB_MIDI.md) and [USB-host MIDI](USB_HOST_MIDI.md) to the existing
[mastering mode](MASTERING.md) and
[stereo packet fix](USB_PACKET_FIX.md). The pre-generator image
`88457445…` was confirmed by the user to boot and pass one iPhone/AUM duplex
path. The changed image, snapshot persistence and broader USB operation still
require physical acceptance.

## Memory and binary integration

The intervals below describe the **main processor**. The independent USB processor
adds 3,056 bytes of executable SRAM and 1,472 bytes of writable SRAM for host MIDI;
see [host placement and allocator evidence](USB_HOST_MIDI.md#integration-and-memory).

USB-host MIDI and FM-1 audio modify the USB application. The audio extension reserves 64 KiB from the USB processor’s existing SDRAM heap; see [its placement and allocator evidence](USB_HOST_AUDIO.md#usb-processor-placement-and-binary-changes). Boot programs, updater and panel-controller payload remain byte-identical to stock. The main application is byte-identical to the mastering held-key fix in PR #18.
The descriptor, rate and reply buffer in the retired USB-B build occupied
read-only code SRAM; the combined build fixes that placement before testing.

| Runtime interval (end exclusive) | Contents | Initialization |
| --- | --- | --- |
| `0x01009860..0x01009a16` | Replacement playback instructions within the original callback | Existing first startup copy, no growth |
| `0x0100f6a4..0x0100ffec` | 2,376 bytes of code/constants, read-only after MPU setup | Extended original first startup copy |
| `0x01017264..0x0101727c` | Desired/applied routing cache and startup-ready flag, padded to 24 bytes | Extended original writable BSS clear |
| `0x0101727c..0x01017430` | 435-byte mutable USB descriptor plus padding | Repurposed formerly zero-length startup copy |
| `0x01017430..0x01017444` | USB rate, 14-byte reply buffer and one-byte OUT alternate at `0x01017442`, padded to 20 bytes | Extended original writable BSS clear |
| `0x01017444..0x010174d0` | 140-byte mastering UI state | Extended original writable BSS clear |
| `0x6001dbd6..0x6001e5ec` (split slots) | Reclaimed stock mixer lookup: compressed lookup, mastering UI, redraw trampoline; shared literal retained | Existing resident main image, no new copy |

The SRAM code slot has 20 bytes remaining before `0x01010000`. The 620-byte writable
reservation begins exactly at the original BSS end, stays inside stock MPU
region 2 (`0x01010000..0x01018000`), and overlaps neither RTOS pool. General
allocation remains `0x01013e18..0x01014e18`; stacks remain
`0x01020000..0x01028000`. No MPU or allocator configuration is changed. Mastering code uses the original
resident lookup footprint, not a newly allocated executable region.
[Mastering evidence](MASTERING.md#placement-and-original-instruction-evidence)
records exact slots and preserved cross-references.

The load-image insertion is 2,812 bytes at main decoded offset `0xdff30`:
2,376 code bytes followed by 436 descriptor bytes. Only code is copied into the
executable slot. Main decoded literal `0xe8` extends the first copy accordingly;
`0x100`, `0x128`, `0x13c`, `0x150` shift existing initialized-data sources.
`0x108` extends writable BSS clearing from `0x71dc` to `0x7448` bytes.
The originally zero-length copy described by `0x10c/0x110/0x114` now loads the
USB descriptor to `0x0101727c`. The following original stack-pool zero is
unchanged. These startup literals are resident at `0x60000000 + decoded offset`.
Existing nonempty copy/zero regions retain their destinations. The playback
patch replaces instructions within the original first copy; other original
initialized data remains unchanged.

The builder guards every overwritten byte and the original whole-file hash,
section types/sizes/addresses, exported functions, state objects and slot bounds.
`build-report.json` is authoritative for regenerated hashes and branch targets.
`mainline.load.bin` is the inserted load data, not a separate flashable firmware.

## Verification

The sole reproduction pipeline executes original startup, MPU setup, RTOS pool
initialization, boot selection/decoding, updater checks, USB descriptors/control
requests, panel gestures, mastering transactions and DSP programming helpers against this exact image.
MIDI tests execute the original packetizer, bulk word transport and cable dispatch
with explicit FIFO and RTOS models. High-speed endpoint tables differ only in the
reviewed MIDI entries; USB-B audio entries are unchanged. FM-1 host checks
execute combined setup, OHCI and EHCI scheduling/completion, PCM conversion and
retirement with DMA, RTOS delivery and DSP hardware modeled explicitly.
Finite-packet tests execute playback/capture, malformed lengths and alternate
changes; 18-channel traces are compared against the predecessor.
An integration case initializes USB and interleaves routing changes with clock
requests on the same emulated RAM at all three rates. Code pages are protected
against writes. Dirty-start tests verify the entire initialized descriptor,
zeroed state, untouched neighbors and allocator separation.

USB hardware/FIFO start, RTOS scheduling boundaries and DSP arithmetic remain
modeled or unexecuted as specified by each report. Boot tests stop before the
final transfer and run application startup separately; they do not demonstrate
physical failed-application recovery. Offline checks do not establish audio,
USB timing or deadline margin.

## Bench sequence

1. Identify this exact image and keep monitoring muted for the first boot.
2. Confirm MASTERING + TAP entry and MASTERING exit, all mapped controls and ten slot pads, pickup and original shortcuts;
   the [mastering procedure](MASTERING.md#verification-and-limits) scopes this new check.
3. Confirm SELECT labels, end stops and routing still work; save/recall differing
   snapshots and restart after allowing several seconds for autosave.
4. Connect USB-B to a host using its class audio driver; record OS/driver,
   negotiated speed, sample rate and channel configuration. A Roland driver
   binding is not evidence of class-only operation.
5. Test playback, recording without playback, duplex, stop/start and reconnect.
6. Follow the [MIDI bench checks](USB_MIDI.md#hardware-acceptance) for both ports
   in both directions, including simultaneous audio.
7. Follow the [host MIDI bench checks](USB_HOST_MIDI.md#verification-and-remaining-work),
   especially sync output and rejection of incoming host clock/transport.
8. Follow the [FM-1 host-audio procedure](USB_HOST_AUDIO.md#verification-and-bench-procedure).
9. Test stereo/18-channel and mixed alternates, then 44.1/48/96 kHz and sustained
   audio. Record levels, channel order and any glitches or failures.

The filename retains `UNTESTED` because acceptance is incomplete. The
[hardware record](../evidence/iphone-aum-20261102/README.md) scopes the successful
iPhone/AUM result; it does not establish every channel, rate or stream mode.

A separate retirement guard verifies the original sample callback pointer, transport,
SELECT/pad handlers and SDRAM heap start. Saved retired source IDs 53/54 fall
back to Auto on normal boot and recall; remaining routes keep their IDs.

## USB-processor host extensions

See [host MIDI](USB_HOST_MIDI.md) for its separate SRAM map, ABI, queues and limitations. The [FM-1 audio report](USB_HOST_AUDIO.md) covers its additional SDRAM transport. Exact current sizes and hashes are recorded in `build/mainline/build-report.json` under `host_midi`. Host reports are checked against the USB artifact as well as the complete candidate.
