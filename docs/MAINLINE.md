# Mainline integration

The only maintained custom firmware combines channel routing and USB-B UAC2.
The USB-host unlock is excluded, with its evidence retained as documentation.
This replaces the three separate builders, output directories and CI targets.
The display-marker diagnostic is not part of mainline.

## Memory and binary integration

Both features modify only the main application. The USB application, boot
programs, updater and panel-controller payload remain byte-identical to stock.
The descriptor, rate and reply buffer in the retired USB-B build occupied
read-only code SRAM; the combined build fixes that placement before testing.

| Runtime interval (end exclusive) | Contents | Initialization |
| --- | --- | --- |
| `0x0100f6a4..0x0100fedc` | 2,104 bytes of code/constants, read-only after MPU setup | Extended original first startup copy |
| `0x01017264..0x0101727c` | Desired/applied routing state, padded to 24 bytes | Extended original writable BSS clear |
| `0x0101727c..0x010173e0` | 355-byte mutable USB descriptor plus padding | Repurposed formerly zero-length startup copy |
| `0x010173e0..0x010173f4` | USB rate and 14-byte reply buffer, padded to 20 bytes | Extended original writable BSS clear |

The code slot has 292 bytes remaining before `0x01010000`. The 400-byte writable
reservation begins exactly at the original BSS end, stays inside stock MPU
region 2 (`0x01010000..0x01018000`), and overlaps neither RTOS pool. General
allocation remains `0x01013e18..0x01014e18`; stacks remain
`0x01020000..0x01028000`. No MPU or allocator configuration is changed.

The load-image insertion is 2,460 bytes at main decoded offset `0xdff30`:
2,104 code bytes followed by 356 descriptor bytes. Only code is copied into the
executable slot. Main decoded literal `0xe8` extends the first copy accordingly;
`0x100`, `0x128`, `0x13c`, `0x150` shift existing initialized-data sources.
`0x108` extends writable BSS clearing from `0x71dc` to `0x736c` bytes.
The originally zero-length copy described by `0x10c/0x110/0x114` now loads the
USB descriptor to `0x0101727c`. The following original stack-pool zero is
unchanged. These startup literals are resident at `0x60000000 + decoded offset`.
The existing nonempty copy/zero regions retain their destinations and contents.

The builder guards every overwritten byte and the original whole-file hash,
section types/sizes/addresses, exported functions, state objects and slot bounds.
`build-report.json` is authoritative for regenerated hashes and branch targets.
`mainline.load.bin` is the inserted load data, not a separate flashable firmware.

## Verification

The sole reproduction pipeline executes original startup, MPU setup, RTOS pool
initialization, boot selection/decoding, updater checks, USB descriptors/control
requests, panel gestures and DSP programming helpers against this exact image.
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
2. Confirm SELECT labels, end stops and routing still work.
3. Connect USB-B to a host using its class audio driver; record OS/driver,
   negotiated speed, sample rate and channel configuration. A Roland driver
   binding is not evidence of class-only operation.
4. Test playback, recording without playback, duplex, stop/start and reconnect.
5. Test stereo/18-channel and mixed alternates, then 44.1/48/96 kHz and sustained
   audio. Record levels, channel order and any glitches or failures.

Retain `UNTESTED` until combined-image hardware evidence supports a narrower
status. Prior routing success does not establish USB audio behavior.
