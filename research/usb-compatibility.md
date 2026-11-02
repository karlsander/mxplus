> Historical investigation: standalone build paths refer to Git history. The only active firmware is [mainline](../docs/MAINLINE.md). Historical evidence has not been rewritten as combined-image evidence.

# MX-1 USB compatibility: evidence and implementation boundaries

Research date: 2026-11-01. This report combines primary documentation, original
user experiments, the Linux USB audio implementation, and inspection of the
supplied firmware. No physical MX-1 was connected during this work.

## What the two USB goals require

The MX-1 has two distinct USB roles. Its four AIRA Type-A ports are hosts for
attached instruments. The single Type-B computer port is a USB device that
provides the computer audio/MIDI interface. Roland documents stereo audio per
AIRA input, bus power on HOST 3, and a required vendor driver on the computer
side. The USB computer interface exposes up to 18 input and 18 output channels
at 44.1, 48, or 96 kHz. [R1, R2]

For ordinary iPhone/iPad class-compliant use, the promising physical connection
is **iPhone/iPad as USB host → MX-1 Type-B as audio device**. Apple documents
USB audio interfaces attached to the iPad's USB-C port. [A2] Whether the
MX-1's separate Type-A controllers can be electrically repurposed is a hardware
question; changing their port role is unnecessary for the requested interface
use case. An iPhone plugged into an AIRA host port is a different protocol
problem. This investigation does not establish that iOS exposes a generic UAC
peripheral to that host.

Accepting generic USB audio devices at the AIRA host ports requires changes on
the **MX-1 host side**. Presenting the mixer to iOS requires changes on its
**device side**. The firmware contains different code paths for them. A patch
to one does not supply the other.

## Confirmed firmware descriptor evidence

The reproducible extractor is `tools/usb_descriptors.py`. Run it on the
decompressed main application:

```bash
python3 tools/usb_descriptors.py analysis/container_app_main.bin \
  --output analysis/usb_descriptors.json
```

Offsets below refer to that decompressed image. Adding `0x60000000` gives the
runtime addresses used by its literal pointer table. They are not offsets into
the compressed 4 MiB updater.

| Object | Image offset | Decoded evidence |
| --- | --- | --- |
| Audio device descriptor | `0xb4980` | USB 2.0, VID `0582`, PID `01a3`, class `ff`, subclass `00`, protocol `ff`, EP0 size 64 |
| Audio device qualifier | `0xb4992` | Same vendor class/protocol, one configuration |
| Audio configuration | `0xb499c` | 258 bytes, four interfaces, self-powered, zero bus-power request |
| Minimal alternate-speed template | `0xb4aa0` | 45 bytes, four inactive vendor interfaces, no audio endpoints |
| Audio descriptor pointer table | `0xb4af8` | Device, main configuration, alternate-speed configuration, qualifier, and string pointers |
| Second device descriptor | `0xb48a8` | VID `0582`, PID `01a4`, interface-defined class; separate pair of 32-byte class-8 configurations |

The second descriptor set is consistent with a mass-storage mode. That
identification does not itself identify every firmware mode in which it is
used. The audio pointer table directly references the strings `Roland`,
`MX-1`, and `VASVMS`. A separate literal at `0xda40` also references the audio
configuration, making it a relevant initialization-code cross-reference.

### Audio configuration details

| Interface/alternate | Class/subclass/protocol | Audio format | Endpoint | Attributes | Maximum bytes | Interval |
| --- | --- | --- | --- | --- | --- | --- |
| 0 / 0 | `ff/ff/00` | None | None | — | — | — |
| 1 / 0 | `ff/02/02` | Inactive | None | — | — | — |
| 1 / 1 | `ff/02/02` | 18 channels, 4-byte subframes, 24 valid bits | `0x0d` OUT | `0x05`, asynchronous data | 1008 | 1 |
| 1 / 2 | `ff/02/02` | 2 channels, 4-byte subframes, 24 valid bits | `0x0d` OUT | `0x05`, asynchronous data | 112 | 1 |
| 2 / 0 | `ff/02/01` | Inactive | None | — | — | — |
| 2 / 1 | `ff/02/01` | 18 channels, 4-byte subframes, 24 valid bits | `0x8e` IN | `0x25`, asynchronous implicit-feedback data | 1008 | 1 |
| 2 / 2 | `ff/02/01` | 2 channels, 4-byte subframes, 24 valid bits | `0x8e` IN | `0x25`, asynchronous implicit-feedback data | 112 | 1 |

All four format templates contain one discrete 96,000 Hz value. These are
static templates: firmware can copy and edit them according to the selected
rate. They must not be reported as proof that the real device is restricted to
96 kHz. Roland documents the three selectable computer rates. [R3]

The streaming-specific descriptors have UAC1 layout even though the interfaces
are vendor-specific. Interface 0 does **not** contain a standard AudioControl
header, input/output terminals, or a standard clock graph. There is no explicit
audio feedback endpoint in this configuration. At high speed, interval 1 means
one service interval every 125 microseconds.

Interface 3 is separate vendor MIDI. Alternate 0 uses bulk endpoints `0x03`
and `0x84`; alternate 1 uses interrupt endpoints `0x03` and `0x85`. It contains
a Roland `0xf1` class-specific descriptor instead of a standard USB MIDI jack
graph. Merely setting its interface class to Audio would not make that MIDI
function standard.

The extractor preserves all raw descriptor bytes, checks chain bounds and
endpoint counts, decodes the format fields, and records aligned literal
pointer occurrences. It does not claim that a static template is the live
enumeration response. Five tests cover malformed descriptor boundaries,
truncated sample-rate lists, endpoint decoding, and exact correspondence with
the original MX-1 descriptor bytes.

## Why Linux and MPC support do not prove iOS compatibility

Linux explicitly recognizes Roland vendor-class interfaces. Its broad VID
`0582` quirk invokes autodetection. The PCM autodetector looks for an active
alternate, an isochronous endpoint, and UAC1-format streaming descriptors, then
uses the regular audio parser. Another parser rule interprets Roland interface
protocols 0, 1, and 2 using UAC1 layout. [L1, L2, L3]

Linux additionally has Roland-specific implicit-feedback handling. It pairs
an asynchronous output interface with the following input interface and sets
playback-first behavior. Its capture path also activates the matching output
stream. The code therefore performs more work than simply overlooking a
vendor class byte. [L4]

Original users report an MX-1 working as an external interface for an MPC One
running 2.14.0 at 44.1 kHz. Another report says changing the connection to
**MX-1 Type-B → MPC Type-A** resolved the problem. These are useful physical
observations, not a standards compliance test. [M1, M2] The Linux Roland quirk
is a plausible explanation for this behavior; the exact MPC kernel and driver
configuration were not examined here.

This distinction also matters on the instrument side. Roland explicitly tells
MC-101 owners to select its VENDOR USB driver mode for AIRA Link in relevant
firmware versions. A device working with AIRA does not thereby demonstrate that
the host accepts that device's generic class mode. [R4]

## Host-side barriers found in the original code

The USB application was separately decompiled by the main investigation. The
following observations were independently checked against that output; the
interface-class rejection was also checked in Thumb disassembly.

| Function address | Observed purpose | Relevant constraint |
| --- | --- | --- |
| `0x6000a11e` | Interpret one interface and following descriptors | Immediately rejects interface class other than `0xff`; expects Roland subclass/protocol combinations |
| `0x6000a1e2` | Walk configuration into per-direction alternate records | Uses fixed records and rejects active alternate indices over 4 |
| `0x6000a3ce` / `0x6000a466` | Gather device/configuration/string information | Bridge raw enumeration to application records |
| `0x60008580` | Construct application compatibility inquiry | Includes VID/PID/revision, bus-speed predicate, and per-alternate rate/format/channel fields |
| `0x60007bf8` | User/application compatibility policy | Generic Roland route requires VID `0582`, matching direction/alternate formats and supported rates; prefers two channels, four-byte subframes |
| `0x6000865c` | Apply selected audio/MIDI alternatives | Issues standard `SET_INTERFACE` for selected streams |
| `0x600080a0` | Create audio transport | Constructs two EHCI isochronous paths, with eight microframe transactions and four-byte samples |

The host library has a separate driver-matching layer at `0x6000ee16` that can
filter VID, PID, device class, and interface class. Inspection of the actual
audio registration shows that it does **not** add another vendor/class gate.
The audio worker at `0x60008958`, missed as a standalone function by this Ghidra
pass and therefore checked with Capstone, loads the driver record
`0x6002b0ac` at `0x60008974` and calls `0x600093f8`. Its first eight bytes,
including the match-flags byte at offset 6, are all zero. Its connect callback
`0x6000837c` queues event 0 and returns zero without testing the interface.
The event table at `0x60028278` maps that event to `0x60008426`, the audio
connection handler. The restrictions below therefore reside in the audio
descriptor classifier and application policy, not this registry record.

### Removing only the vendor-ID check is insufficient

At `0x6000a136`, original Thumb code compares the interface class with `0xff`;
the conditional branch at `0x6000a13a` returns on a mismatch. A normal Audio
class interface (`01/02/00` for UAC1 streaming) fails here before reaching the
policy callback. In addition, the parser uses protocol 1 versus 2 to identify
Roland inactive IN and OUT alternates. Standard UAC1 uses protocol 0 for both.
An extension must therefore determine stream direction from endpoint evidence
and handle inactive alternates correctly.

The original format parser reads the first three-byte frequency directly from
the UAC1 format block. It does not implement a general choice among a discrete
rate list, nor a continuous range. UAC2 supplies clocks differently and uses
different class-specific layouts, so accepting protocol `0x20` in this parser
would be incorrect.

### The transport is specialized too

The selected-stream path sends `SET_INTERFACE`; no audio frequency `SET_CUR`
call was found among all direct call sites of the general host control-request
builder `0x60009558`. This is evidence about the inspected implementation,
not a proof that no indirect or hidden call could exist. Until a rate-control
implementation is added, the conservative profile is a device that starts at
the one fixed advertised rate.

`0x600080a0` computes packet sizes from `rate / 8000`, configures all eight
microframes, and uses four bytes per sample. It creates the audio IN and OUT
paths; no independent explicit-feedback receive path was found there. Its
endpoint setup uses one transaction and masks packet-size bits with `0x3ff`.
Consequently, the investigated path cannot simply be assumed to support
full-speed 1 ms transfers, arbitrary high-speed intervals, 1024-byte packets,
high-bandwidth multipliers, or an extra explicit feedback endpoint.

An initial host patch should therefore be described as a **restricted parser
and admission experiment**, unless transport changes are also implemented and
tested. A conservative experiment would admit only high-speed full-duplex
stereo PCM, four-byte subframes, one matching discrete rate, endpoints fitting
the existing per-microframe schedule, and no additional feedback endpoint.
That does not cover the large population of full-speed 16/24-bit UAC1 devices
or typical UAC2 interfaces. It may also admit very few real standard devices:
Apple's documented high-speed ADC1 design uses interval 4, whereas this
transport assumes interval 1. [A1]

## A concrete device-side UAC2 design

`tools/uac2_design.py` generates **unintegrated descriptor designs**, not a
firmware image. It retains the early audio-only design separately from a
second design that preserves the original streaming alternates and MIDI
hardware endpoints.

```bash
python3 tools/uac2_design.py \
  --output research/usb_sources/uac2-audio-only-design.json
```

The proposed configuration is 211 bytes, so the descriptor data alone fits
within the original 258-byte main-configuration area. This is useful for
planning, but not permission to overwrite the old descriptor: the original
initialization code has references and format assumptions that must change
with it.

The early 211-byte design preserves 18 input/output channels, alternate setting 1,
interface numbers 0/1/2, endpoint addresses `0x0d/0x8e`, four-byte subslots,
24 valid bits, and the 125 microsecond schedule. It supplies an AudioControl
interface with a shared clock and terminal graph, then two UAC2 streaming
interfaces. It omits MIDI and the two-channel alternate for the first audio
experiment. Later tracing found a reason to retain those hardware interfaces,
so the 355-byte design below is the better integration candidate.

### Revised design preserving the original hardware modes

```bash
python3 tools/uac2_design.py --variant preserve-modes \
  --output research/usb_sources/uac2-preserve-modes-design.json
```

This configuration is **355 bytes** and requires relocation. It retains
alternate 1 with 18 channels and alternate 2 with two channels on both audio
interfaces. Endpoint addresses, attributes, maximum packet sizes (1008/112),
and service interval remain unchanged. The IAD covers interfaces 0 through 2
only; the configuration contains four interfaces. All 52 original bytes for
vendor MIDI interface 3 are appended unchanged, including both of its
alternates and endpoints. This preserves the interface on which existing
firmware MIDI routines depend. It does not provide class-compliant MIDI to iOS.

`tests/test_uac2_design.py` verifies configuration lengths, channel alternates,
endpoint framing, the IAD boundary, the shared clock controls, and exact MIDI
byte equality against the original firmware. Six tests pass, including terminal
and clock references and 96 kHz packet headroom. These are byte
and structure checks, not host compatibility tests. In particular, actual
stereo routing and the relationship of the two-channel streaming alternate
to the fixed 18-channel internal terminal graph still need host validation.

The design's descriptors and request numbers were checked against the Linux
UAC2 type definitions and the USB-IF specification entry. [L5, U1] The proposed
clock is fixed during one USB session, with its current frequency selected on
the mixer before enumeration. That avoids promising a host-controlled clock
change before its hardware consequences are understood.

The minimum new request contract for clock entity `0x10` on AudioControl
interface 0 is:

| Request | Setup packet | Response |
| --- | --- | --- |
| Frequency `GET_CUR` | `a1 01 00 01 00 10 04 00` | Actual current rate as a 32-bit little-endian integer |
| Frequency `GET_RANGE` | `a1 02 00 01 00 10 0e 00` | One subrange: minimum=current, maximum=current, resolution=0 |
| Validity `GET_CUR` | `a1 01 00 02 00 10 01 00` | One byte, true only when the advertised clock is valid |

Responses must honor the host's requested length, including a two-byte range
header probe. Unsupported writes to the read-only clock and invalid requests
must stall rather than report success. The same discipline applies to the
standard descriptor, configuration, and alternate-setting requests.

### The main unresolved compatibility problem is startup

Apple supports implicit feedback when input and output share a clock, but
waits for consistent input timing before sending output data. [A1] The Linux
Roland path's playback-first behavior led to tracing the actual firmware pump.
The subsequent `research/device-control.md` investigation found that its IN
start transitions depend on OUT endpoint activity or buffered OUT data. This
supports the suspected descriptor-only startup deadlock: each side can wait
for the other to start. The integration experiment must explicitly address
that dependency.

This design must be accompanied by verified input-first startup or an explicit
feedback implementation, truthful full-speed behavior, real EP0 handlers,
and a check of the audio sample alignment. Four-byte subslots and a 24-bit
resolution field do not prove which bit positions the existing DMA path uses.
No physical iOS enumeration or audio test has been performed.

The subsequent offline integration in `build/device-probe` implements the
relocated 355-byte design, a compiled fixed-clock class-request handler, and
the targeted capture-start instruction change. Eight groups in
`build/device-probe/arm-verification.json` verify original ARM startup,
registration, request dispatch, rejection, descriptor responses, hardware
table construction, failure returns, and the unchanged backup initializer.
The independent structural audit in `research/uac2-descriptor-audit.md`
records the UAC2 requirements and remaining host/transport limits. These
results support a concrete experimental candidate; they do not establish
physical enumeration or sustained audio.

### A separate route using the original firmware

`research/linux-bridge.md` and `tools/linux_bridge.py` provide a concrete
external Linux UAC2 bridge prototype: the MX-1 USB-B connects to a Linux host
controller, while a separate USB device controller presents UAC2 to iOS.
The tool configures stereo or 18-channel audio and routes both directions
with adaptive clock correction. All operations are read-only without
`--apply`; actual hardware interoperability remains untested. This supports
testing the iOS goal independently of a native firmware patch.

## Physical evidence that would resolve the remaining questions

The least invasive next measurements use the original firmware. On a Linux
host, collect the actual descriptors and ALSA stream information:

```bash
lsusb -d 0582:01a3
lsusb -v -d 0582:01a3 > mx1-original-descriptors.txt
cat /proc/asound/cards
```

Then read `stream0` under the MX-1's actual `/proc/asound/cardN/` directory.
Repeat descriptor collection with the mixer set to 44.1, 48, and 96 kHz and
record the firmware version and mixer mode. This establishes which template
fields change at runtime. Keep the unchanged original firmware available.

For a candidate generic instrument/interface, collect its descriptors from a
computer first. Compare its USB speed, UAC version, alternate numbers, rate
control, channels, subframe size, endpoint synchronization, service interval,
and packet-size multiplier against the experimental profile. That can rule out
an incompatible device without flashing or plugging it into the patched host.

For startup, use Linux usbmon to capture control requests and both audio
directions during recording-only, playback-only, and duplex starts. usbmon
records requests at the host-controller-driver boundary rather than a direct
electrical bus trace. [L6] Restrict capture to the MX-1's USB bus and retain only
the MX-1 device traffic when sharing the result. The decisive measurements are
the two `SET_INTERFACE` transactions, the first successful IN transfer, the
first OUT transfer, and whether IN continues when OUT is not supplied.

The public evidence, static analysis, and emulated integration support concrete
targeted candidates and identify their missing validation. They do not establish
that a rebuilt image can safely be flashed, that a generic interface already
works, or that the implemented UAC2 experiment is a physically working iOS mode.
Use `docs/HARDWARE_VALIDATION.md` for the staged baseline, bridge, recovery, and
separate-candidate test sequence.

## Primary and original sources

All source pages were reviewed during this investigation. Claims from the
supplied binary are distinguished above from manufacturer documentation and
external experiments.

- **R1 — Roland MX-1 owner's manual:** https://cdn.roland.com/assets/media/pdf/MX-1_e01_W.pdf
- **R2 — Roland MX-1 official product/specification page:** https://www.roland.com/global/products/mx-1/
- **R3 — Roland sampling-rate instructions:** https://support.roland.com/hc/en-us/articles/205215985-MX-1-Changing-the-Sampling-Rate
- **R4 — Roland MC-101 AIRA Link instructions, including VENDOR mode:** https://support.roland.com/hc/en-us/articles/360039331632-MC-101-Is-AIRA-LINK-supported
- **R5 — Roland current AIRA Link compatible-device list:** https://support.roland.com/hc/en-us/articles/360060655791-MX-1-What-devices-can-be-connected-to-the-AIRA-LINK-USB-ports
- **M1 — Original MPC One 2.14.0 user test, 13 April 2024:** https://www.mpc-forums.com/viewtopic.php?start=480&t=211654
- **M2 — Original connection correction and successful test, 20 March 2024:** https://www.elektronauts.com/t/mpc-thread-mpc-live-mpc-x-mpc-one-part-2/173139?page=336
- **M3 — Original MPC/Force routing discussion:** https://www.mpc-forums.com/viewtopic.php?p=1880149
- **L1 — Linux USB quirk matching:** https://github.com/torvalds/linux/blob/master/sound/usb/quirks-table.h
- **L2 — Linux Roland PCM/MIDI autodetection:** https://github.com/torvalds/linux/blob/master/sound/usb/quirks.c
- **L3 — Linux streaming parser (upstream source rendered by Codebrowser):** https://codebrowser.dev/linux/linux/sound/usb/stream.c.html
- **L4 — Linux implicit-feedback and Roland duplex handling:** https://github.com/torvalds/linux/blob/master/sound/usb/implicit.c
- **L5 — Linux UAC2 descriptor/control definitions:** https://github.com/torvalds/linux/blob/master/include/linux/usb/audio-v2.h
- **L6 — Linux usbmon documentation:** https://docs.kernel.org/usb/usbmon.html
- **A1 — Apple TN3190, USB audio device design considerations:** https://developer.apple.com/documentation/technotes/tn3190-usb-audio-device-design-considerations
- **A2 — Apple iPad USB-C audio-device support:** https://support.apple.com/en-ie/108894
- **U1 — USB-IF Audio Devices revision 2.0 specification entry:** https://www.usb.org/document-library/audio-devices-rev-20-and-adopters-agreement

### Retrieval limitations

No MX-1 public `lsusb -v` dump was found that improved on the descriptor bytes
extracted here. Early VID/PID search results came from driver catalogues;
the final IDs in this report were independently confirmed in the supplied
firmware. The Apple technote's ordinary page renders a JavaScript notice to the
web reader, but its indexed primary-source text exposes the relevant sections
(including the interval and startup requirements). Direct raw GitHub downloads
from this environment failed; the browser-readable upstream source and its
rendering were used instead. No claim of a downloaded or locally built Linux
driver is made.
