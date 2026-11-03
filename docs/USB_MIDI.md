# USB-B MIDI class experiment

Mainline advertises two bidirectional USB-MIDI 1.0 ports alongside UAC2 audio.
This has offline instruction and descriptor evidence only. No iOS, macOS,
Windows or Linux class-driver enumeration, real MIDI transfer, latency or
simultaneous audio/MIDI result has been established for this candidate.
The prior audio-only bench result does not validate it.

## Descriptor change

The original main application descriptor at decoded offset `0xb4a6a`, resident
address `0x600b4a6a`, is 52 bytes: interface 3 alternate 0 has bulk OUT `0x03`
and IN `0x84`; alternate 1 has interrupt OUT `0x03` and IN `0x85`.
The Roland-specific `06 24 f1 02 02 02` describes two cables in each direction
under Linux's Roland detector. Linux retains its standard USB-MIDI packet
handlers for that detector. This motivated the investigation; actual stock
instruction execution supplies the local packet-format evidence below.
[Linux MIDI implementation](https://github.com/torvalds/linux/blob/master/sound/usb/midi.c),
`snd_usbmidi_detect_roland` and `snd_usbmidi_create`.

`tools/usb_midi_descriptors.py` replaces that tail with a 132-byte MIDI function:

- IAD for interfaces 3/4, separate from the unchanged UAC2 IAD for 0–2.
- UAC1 AudioControl interface 3 with a header referencing MIDIStreaming interface 4.
- MIDIStreaming interface 4 alternate 0, protocol 0, eight jack descriptors
  representing two cable pairs, and matching endpoint jack associations.
- Original 512-byte bulk endpoints `0x03`/`0x84`; no interrupt alternate.

Cable order is preserved: embedded IN jacks 1/5 map to cable 0/1 on USB OUT;
embedded OUT jacks 3/7 map to cable 0/1 on USB IN. Names and physical routing
must be confirmed on the device; this change does not create new MIDI routing.
The configuration is 435 bytes with five interfaces. USB-MIDI 1.0 §6.1.2.1
specifies `wTotalLength` as header plus jack/element descriptors: 67 bytes here.
Appendix B's example counts endpoint bytes too; this implementation follows the
normative field definition. §6.2 defines the nine-byte standard bulk endpoint
and class-specific jack association. Appendix B.3 describes the mandatory AC
collection. [USB-IF MIDI 1.0 specification](https://www.usb.org/sites/default/files/midi10.pdf).

High-speed audio descriptors are byte-identical apart from the configuration
header length/interface count. Full-speed still returns the stock 45-byte
empty vendor configuration: neither audio nor MIDI is offered at full speed.
Roland VID/PID are retained; installed vendor drivers or host quirks can affect
binding. Generic-host acceptance must be checked explicitly.

## Original instruction evidence

`tools/usb_midi_verify.py` runs stock and candidate instructions after their
respective startup scatter copies. `build/mainline/midi-verification.json`
records exact decoded offsets, runtime addresses, byte hashes and cases.
All functions below belong to **app_main**, not the USB-host application.

| Function | Main decoded offset | Runtime address | Evidence |
| --- | --- | --- | --- |
| USB OUT event task | `0xd0c24` | `0x01000398` | Finite FIFO reads arrive unchanged at listener dispatch `0x01002580` |
| Bulk IN batch send | `0xd0f50` | `0x010006c4` | Complete event words written unchanged to the original FIFO access at `0x40010190` |
| Raw MIDI packetizer | `0xd1c20` | `0x01001394` | CIN, cable nibble and padding match note, CC, program, pressure, bend, system-common, real-time and SysEx fixtures |
| USB-B cable dispatcher | `0xd204e` | `0x010017c2` | Cable 0/1 select original route objects `0x2000671c`/`0x20006938` (source IDs 1/2) |

The stock raw-byte packetizer drops Active Sensing (`FE`); that behavior is
recorded and unchanged. It is not a general byte-stream parser: the tests
supply complete messages, and do not establish running-status or interleaved
real-time reconstruction inside that helper. Bulk transport itself carries
already packetized records without translation.

Finite FIFO cases cover 0, 4, 8, 64, 508 and 512 bytes in both directions,
including mixed cables and SysEx fragments. Both single-word and batch sends
are checked under all nine audio alternate combinations. The stock MIDI send
selector reads interface 3’s alternate field in `0x4001017c`; the new MIDI
control interface 3 and streaming interface 4 both have only alternate zero,
so the original code continues selecting bulk IN. The harness supplies FIFO
readiness/counts, RTOS event delivery and queue input. It stubs IRQ masking,
records the receive-listener boundary and records downstream routing targets.
It does not emulate the USB PHY, FIFO timing, task scheduling or application
clock settings. These checks do not establish physical packet boundaries,
queue-overflow recovery or safe malformed-host behavior.

The original descriptor walker at resident `0x6003d026` (decoded `0x3d026`)
executes on the new graph at 44.1/48/96 kHz. Only these endpoint table words
change at high speed; all audio writes and all full-speed writes compare equal:

| Table address | Stock | Candidate | Meaning derived from walker instructions |
| --- | --- | --- | --- |
| `0x40010208` | `0x100018c3` | `0x100020c3` | Bulk OUT interface association 3 → 4 |
| `0x4001020c` | `0x100098e3` | `0` | Remove interrupt OUT alternate |
| `0x40010210` | `0x100018d4` | `0x100020d4` | Bulk IN interface association 3 → 4 |
| `0x40010218` | `0x100098f5` | `0` | Remove interrupt IN alternate |

Interface-count/alternate register `0x400100fc` changes from `0x04002334` to
`0x05005334`. These are observations of the original walker, not independent
hardware-register documentation. Actual GET_DESCRIPTOR and other-speed
requests return the new graph through the original dispatcher. Control/FIFO
reply delivery remains modeled as described in `usb-verification.json`.

## Placement and reproduction

The descriptor grows by 80 bytes in the existing writable SRAM reservation:
`0x0101727c..0x01017430` (436 bytes including padding). USB state moves to
`0x01017430..0x01017444`; mastering state moves to `0x01017444..0x010174d0`.
The full reservation is 620 bytes. Original MPU settings, RTOS pools and
stack reservations remain unchanged. Dirty-start and allocator tests cover
the new bounds. No executable code growth occurs; 20 code bytes remain free.
Compiled state references and the existing playback state literal are relinked.

The inserted load data is 2,812 bytes: 2,376 code plus 436 descriptor bytes.
Startup zero length at decoded `0x108` becomes `0x7448`; descriptor copy length
at `0x110` becomes 436. Other source shifts, exact old/new patch bytes,
component checksums and candidate identity are in `build-report.json`.
No new transport hook, callback or calling convention is introduced.
The USB-host application, boot programs, updater and panel payload remain stock.

Run the sole `tools/reproduce.py` pipeline and then
`tools/check_reproduction.py --check-committed` after committing the matching
candidate and reports. MIDI cases are part of the mainline instruction stage;
the evidence gate also requires a MIDI report for that application hash.

## Hardware acceptance

Follow [hardware preparation](HARDWARE_VALIDATION.md) before an authorized
installation. Use the exact mainline hash in `build/mainline/build-report.json`.

1. Confirm ordinary mixer startup, analog audio and existing routing.
2. On a host using its class driver, record the high-speed descriptors and
   driver binding. Confirm two MIDI inputs and outputs appear, alongside audio.
3. Identify each port's actual routing. Test notes, CCs and long SysEx in both
   directions, checking bytes and cable separation rather than names alone.
4. Test clock, Start/Continue/Stop and the existing clock-source settings.
   Measure timing under load; successful packet decoding is not a latency test.
5. Run simultaneous stereo/18-channel audio and MIDI, then disconnect,
   reconnect, stop/restart and repeat at each mixer sample rate.
6. Record OS/app/driver versions, cables, selected alternates, duration,
   dropped/stuck notes, SysEx corruption and audio glitches. Preserve failures.

Keep `UNTESTED` until these observations justify a narrowly stated status.
The audio limits remain fixed read-only rate, configuration-based clock
validity, implicit feedback and incomplete stereo/mixed-alternate validation.
