# Mainline integration

The only maintained custom firmware combines channel routing, USB-B UAC2,
white noise (`NSE`) and a per-strip bass drum sequencer (`BD`). USB-host unlocking
remains excluded. The display-marker diagnostic is not part of mainline.
Routing assignments use the stock snapshot and delayed system-save paths; see
[storage integration](ROUTING_STORAGE.md). BD patterns currently live in RAM.

The first generator/editor image failed normal boot. The exact pre-generator
mainline boots, and TAP update mode allowed restoration after this failure.
The startup-guard candidate and a location-only test also failed normal boot.
The current build moves code into an explicit SDRAM heap reservation and awaits
its hardware test; see the [boot investigation](BOOT_REGRESSION.md).

## Memory and binary integration

Only the main application changes. The USB application, boot programs, updater
and panel-controller payload remain byte-identical to stock. The recovered
internal-source candidate placed mutable state in read-only SRAM. The first
integration chose an unusable code location at `0x01018000`. This build keeps
private writable state and reserves code space from the stock SDRAM heap,
without changing the original MPU configuration.

| Runtime interval (end exclusive) | Contents |
| --- | --- |
| `0x01017264..0x0101727c` | Routing desired/applied cache and startup-ready flag, 24 bytes |
| `0x0101727c..0x010173e0` | Mutable USB descriptor and padding, 356 bytes |
| `0x010173e0..0x010173f4` | USB rate/reply state, 20 bytes |
| `0x010173f4..0x0101784c` | Generator patterns, voices, clock and transient UI state |
| `0x60664000..0x60665a4c` | Mainline code/constants, 6,732 bytes, in reserved SDRAM |
| `0x60666000..0x62000000` | Remaining stock SDRAM heap, 26,845,184 bytes |

Writable state stays inside stock MPU region 2 (`0x01010000..0x01018000`).
Code has 1,460 bytes remaining before its `0x60666000` reservation limit.
General allocation remains `0x01013e18..0x01014e18`; stacks remain
`0x01020000..0x01028000`. Neither private pool overlaps the extension. The stock
SDRAM heap start moves from `0x606634d0` to `0x60666000`, reserving 11,056 bytes
including alignment. Its initializer automatically reduces capacity while
retaining the fixed end `0x62000000`. Original MPU region 6 permits execution
and writes in SDRAM; the code reservation is excluded from heap allocation,
not made read-only by a new MPU rule. See [allocator evidence](SDRAM_CODE.md).

The 8,244-byte load image is appended at main decoded offset
`0xe0448`, after all original bytes. The originally zero-length
startup copy described by main decoded literals `0x10c/0x110/0x114` copies its
1,512 state bytes to `0x01017264`. A second originally empty copy, described by
`0x134/0x138/0x13c`, copies 6,732 code bytes from `0x600e0a30` to `0x60664000`.
Both run before the stock MPU setup. Every originally nonempty copy/zero operation,
including the original BSS clear, is unchanged. Original initialized-data
source offsets do not move. These descriptor literals reside at runtime
`0x60000000 + decoded offset`.

The builder guards the whole input hash, every overwritten byte, section
permissions/types/addresses, exported functions, state bounds, original startup
map and allocator records. `build-report.json` records exact patches, callback
and branch targets, load sections and component checksums. `mainline.load.bin`
is startup data, not another flashable firmware. The archive's old builder,
linker and firmware were not imported.

## Verification

The sole reproduction pipeline executes original startup, MPU setup, RTOS pool
initialization, boot selection/decoding, updater checks, USB descriptors/control
requests, panel gestures and DSP programming helpers against this exact image.
An integration case initializes USB and interleaves routing changes with clock
requests on the same emulated RAM at all three rates. Code pages are protected
against writes. Dirty-start tests verify the entire initialized descriptor,
initialized generator defaults, zeroed route/USB state, untouched neighbors and allocator separation.
The stock SDRAM pool creator and low-level allocator execute through exhaustion
and preserve the code reservation. The failed private code interval is unmapped
in main-application instruction harnesses.

USB hardware/FIFO start, RTOS scheduling boundaries and DSP arithmetic remain
modeled or unexecuted as specified by each report. Boot tests stop before the
final transfer and run application startup separately; they do not demonstrate
physical failed-application recovery. Offline checks do not establish audio,
USB timing or deadline margin.

## Bench sequence

1. Identify this exact image and keep monitoring muted for the first boot.
2. Confirm steady/blinking SELECT toggles, labels, end stops and routing; save/recall differing
   snapshots and restart after allowing several seconds for autosave.
3. Connect USB-B to a host using its class audio driver; record OS/driver,
   negotiated speed, sample rate and channel configuration. A Roland driver
   binding is not evidence of class-only operation.
4. Test playback, recording without playback, duplex, stop/start and reconnect.
5. Test stereo/18-channel and mixed alternates, then 44.1/48/96 kHz and sustained
   audio. Record levels, channel order and any glitches or failures.

Retain `UNTESTED` until combined-image hardware evidence supports a narrower
status. Prior routing success does not establish USB audio behavior.

Test NSE first at a low fader level, then one BD voice, then multiple voices at
all rates while monitoring USB playback/capture. The generator exchange-port
mapping and worst-case IRQ deadline margin require hardware measurement; see
[internal sources](INTERNAL_SOURCES.md). The current SDRAM placement awaits a
physical boot test; generator functions remain untested on hardware.
