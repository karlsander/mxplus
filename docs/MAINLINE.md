# Mainline integration

The only maintained custom firmware combines channel routing, mastering editing, USB-B UAC2 and experimental USB-MIDI 1.0.
USB-host MIDI is experimental with sync output prioritized and incoming host sync blocked; see [host MIDI](USB_HOST_MIDI.md) for the earlier FM-1 output observation and current limits. Generic host audio remains excluded.
Generators and their SELECT editor are removed; their findings are in
[the DSP handoff](GENERATOR_RESEARCH.md).
The temporary d001 diagnostic menu is absent. The additional sends use a new
explicit SDRAM code reservation, with no ARM sample renderer. Routing now uses scene
and system reserved fields for snapshots and restart persistence; see
[storage integration](ROUTING_STORAGE.md).

The current candidate is
`0cff93760693e41e18e8091332c16bf425b05613242637ee498c43f8e3be975d`.
It adds [alternate external and independent internal FX sends](FX_SENDS.md)
on the channel tempo surface. This changed candidate has no physical acceptance.
It accepts [normal short USB-MIDI input](../evidence/host-midi-short-packets-20261115/README.md)
without including the separate experimental host-audio/debug path.
It fixes [host MIDI startup on an already-active alternate zero](../evidence/host-midi-alt-zero-20261104/README.md).
It retains the fix for the [held-key range that blocked mastering entry](../evidence/mastering-key-range-20261104/README.md).
It restores [long MASTERING entry and a visible selected preset pad](../evidence/mastering-hold-light-20261104/README.md)
after the user confirmed the held-key correction worked with the temporary chord. It also fixes [FM-1 host-MIDI descriptor rejection](../evidence/fm1-host-midi-20261103/README.md).
It adds [USB-B MIDI](USB_MIDI.md) and [USB-host MIDI](USB_HOST_MIDI.md) to the existing
[mastering mode](MASTERING.md) and
[stereo packet fix](USB_PACKET_FIX.md). The pre-generator image
`88457445…` was confirmed by the user to boot and pass one iPhone/AUM duplex
path. The changed image, snapshot persistence and broader USB operation still
require physical acceptance.

## Memory and binary integration

The intervals below describe the **main processor**. The independent USB processor
adds 2,784 bytes of executable SRAM and 1,472 bytes of writable SRAM for host MIDI;
see [host placement and allocator evidence](USB_HOST_MIDI.md#integration-and-memory).

USB-host MIDI additionally modifies the USB application. Boot programs, updater and panel-controller payload remain byte-identical to stock. The USB application adds the short-packet receive option to the alternate-zero startup fix. The main application adds channel ownership of the tempo surface on top of the timed mastering entry and RGB preset-pad correction. The USB application is byte-identical to PR #22; physical acceptance of this combined candidate remains open.
The descriptor, rate and reply buffer in the retired USB-B build occupied
read-only code SRAM; the combined build fixes that placement before testing.

| Runtime interval (end exclusive) | Contents | Initialization |
| --- | --- | --- |
| `0x01009860..0x01009a16` | Replacement playback instructions within the original callback | Existing first startup copy, no growth |
| `0x0100f6a4..0x0100ffb8` | 2,324 bytes of code/constants, read-only after MPU setup | Extended original first startup copy |
| `0x01017264..0x0101727c` | Desired/applied routing cache and startup-ready flag, padded to 24 bytes | Extended original writable BSS clear |
| `0x0101727c..0x01017430` | 435-byte mutable USB descriptor plus padding | Repurposed formerly zero-length startup copy |
| `0x01017430..0x01017444` | USB rate, 14-byte reply buffer and one-byte OUT alternate at `0x01017442`, padded to 20 bytes | Extended original writable BSS clear |
| `0x01017444..0x010174d0` | 140-byte mastering UI state | Extended original writable BSS clear |
| `0x010174d0..0x010174e0` | 13-byte channel UI state plus padding | Extended original writable BSS clear |
| `0x010174e0..0x01017508` | 40-byte send state | Extended original writable BSS clear |
| `0x60664000..0x60666000` | Reserved send code/constants and DSP program data; used size in build report | Repurposed empty startup copy eight |
| `0x6001a40c..0x6001a888` (split slots) | Equivalent system lookup, channel controls and relocated UI guards; zero return and diagnostic retained | Existing resident main image, no new copy |
| `0x6001dbd6..0x6001e5ec` (split slots) | Reclaimed stock mixer lookup: compressed lookup, mastering UI, redraw trampoline; shared literal retained | Existing resident main image, no new copy |

The SRAM code slot has 72 bytes remaining before `0x01010000`. The 676-byte writable
reservation begins exactly at the original BSS end, stays inside stock MPU
region 2 (`0x01010000..0x01018000`), and overlaps neither RTOS pool. General
allocation remains `0x01013e18..0x01014e18`; stacks remain
`0x01020000..0x01028000`. MPU setup and private allocators are unchanged. The SDRAM heap begins at
`0x60666000` to exclude the new send code. Mastering and channel UI code use reclaimed resident lookup footprints, with no
new executable region for those ownership controls. [Channel control evidence](CHANNEL_CONTROLS.md) records
the new slots and unchanged system-lookup behavior.
[Mastering evidence](MASTERING.md#placement-and-original-instruction-evidence)
records exact slots and preserved cross-references.

The load-image insertion at main decoded offset `0xdff30` contains 2,324 SRAM
code bytes, 436 descriptor bytes, then the send code/constants. Its exact size
is recorded in the build report. Only the first part extends the original
private executable copy. The USB descriptor uses the formerly empty copy at
`0x10c/110/114`; the send section uses the empty copy at `0x134/138/13c`.
Other initialized-data source pointers shift by the entire insertion. Decoded
`0x108` extends writable BSS clearing from `0x71dc` to `0x7480` bytes. Existing
nonempty copy/zero destinations, original private pools, and the final SDRAM
zero ending at `0x606634d0` are preserved. [Send memory accounting](FX_SENDS.md).

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
reviewed MIDI entries; audio entries are unchanged.
Finite-packet tests execute playback/capture, malformed lengths and alternate
changes; 18-channel traces are compared against the predecessor.
An integration case initializes USB and interleaves routing changes with clock
requests on the same emulated RAM at all three rates. Code pages are protected
against writes. Dirty-start tests verify the entire initialized descriptor,
zeroed state, untouched neighbors and allocator separation.

USB hardware/FIFO start, RTOS scheduling and complete factory effect execution
remain modeled or unexecuted as specified by each report. The new send kernels
have separate numerical checks; these are not physical DSP timing measurements. Boot tests stop before the
final transfer and run application startup separately; they do not demonstrate
physical failed-application recovery. Offline checks do not establish audio,
USB timing or deadline margin.

## Bench sequence

1. Identify this exact image and keep monitoring muted for the first boot.
2. Confirm long MASTERING entry, selected preset-pad light and MASTERING exit, all mapped controls and ten slot pads, pickup and original shortcuts;
   the [mastering procedure](MASTERING.md#verification-and-limits) scopes this new check.
3. Confirm channel pages, dial/button tempo isolation, no-selection tempo controls
   and SELECT labels/end stops/routing still work; save/recall differing
   snapshots and restart after allowing several seconds for autosave.
4. Connect USB-B to a host using its class audio driver; record OS/driver,
   negotiated speed, sample rate and channel configuration. A Roland driver
   binding is not evidence of class-only operation.
5. Test playback, recording without playback, duplex, stop/start and reconnect.
6. Follow the [MIDI bench checks](USB_MIDI.md#hardware-acceptance) for both ports
   in both directions, including simultaneous audio.
7. Follow the [host MIDI bench checks](USB_HOST_MIDI.md#verification-and-remaining-work),
   especially sync output and rejection of incoming host clock/transport.
8. Follow the [send audio checks](FX_SENDS.md#evidence-and-remaining-hardware-work),
   including both destinations, all internal types, simultaneous MASTER FX and
   AUX pre/post behavior.
9. Test stereo/18-channel and mixed alternates, then 44.1/48/96 kHz and sustained
   audio. Record levels, channel order and any glitches or failures.

The filename retains `UNTESTED` because acceptance is incomplete. The
[hardware record](../evidence/iphone-aum-20261102/README.md) scopes the successful
iPhone/AUM result; it does not establish every channel, rate or stream mode.

A separate retirement guard verifies the original sample callback pointer, transport,
SELECT/pad handlers. The send reservation has separate heap-exclusion checks. Saved retired source IDs 53/54 fall
back to Auto on normal boot and recall; remaining routes keep their IDs.

## USB-processor MIDI extension

See [host MIDI](USB_HOST_MIDI.md) for its separate SRAM map, ABI, queues and limitations. Exact current sizes and hashes are recorded in `build/mainline/build-report.json` under `host_midi`. Host reports are checked against the USB artifact as well as the complete candidate.
