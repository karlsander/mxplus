# FM-1 host-MIDI descriptor compatibility

## Observation and reproduced blocker

On 3 November 2026 the user reported no MIDI visible on an FM-1 running the
custom INSTRUMENT MIDI monitor. The MX-1 was first set to USB3 clock; switching
to INT, trying host port 1, and restarting both devices did not produce visible
MIDI. The installed MX-1 candidate was the previously transferred
`adb0c284b24e2813dd2a978471f43997b4e76864396d596f18554831c537c474`;
there is no physical firmware readback or USB packet capture. The monitor can
hide clock rows with its EVENTS filter; RX counts all captured packets. Monitor
filter state and RX count were not supplied with this observation.

Executing the installed candidate's USB configuration parser against the
175-byte configuration extracted from the FM-1 monitor ELF returns `-1`, before
selection or endpoint opening. The USB application SHA-256 for that before case
is `b601ca64f700ecf28241b86cf3c8a90270854845a0d40cb299f3efe3bdd44d05`.
The rejecting extension is reached from app_usb decoded `0xa1e2`, runtime
`0x6000a1e2`; its placement starts at decoded `0x36dd8`, runtime `0x0100bee4`.
The fixture is extracted from a built image, not read from the attached bus.

The MIDI header at configuration offset `0x6e` advertises `wTotalLength=65`.
The parser required 37 (header plus four jack descriptors), while the FM-1
counts the two standard endpoints and their class descriptors too. Both forms
occur in the [USB MIDI 1.0 specification](https://www.usb.org/sites/default/files/midi10.pdf):
table 6-2 defines the header/jack/element count; appendix B, table B-6 gives
`0x0041` for the corresponding two-endpoint example.

The parser now accepts either the exact class-interface sum or the complete
validated MIDI span after its standard interface descriptor. It does not skip
length checks or permit arbitrary totals. All descriptor bounds, endpoint,
jack graph, single-cable and class/version restrictions remain. Selection is
MIDI interface 2 only; audio streaming interface 1 remains unselected. No audio
unlock, incoming-sync permission or routing change is included.

## Fixture origin

`configuration.hex` and `device.hex` record USB protocol data extracted from
INSTRUMENT monitor commit `43ed2be038cf10e00c3d8e0704b7fdd5fe30535f` in
[fm1-instrument](https://github.com/karlsander/fm1-instrument).
Its platform revision is `2d8ed748cdade582c65d9fc8d8cf17da4ddadec8`, and its
[felucca-bsp](https://github.com/hugelton/felucca-bsp) revision is
`773b0b99f5ade1a30d1879b2618c6c3c3e6ba031`. The passive monitor patches were
applied; those patches do not change the descriptors. The descriptor definitions
are in `platform/bsp/chip/usb.c`, under MPL-2.0, copyright 2026 Leo Kuroshita
(@kurogedelic), Hugelton Instruments, and Kerem Kilic (Ellic Studio). This change
imports descriptor data, not FM-1 executable code or implementation source.

| Artifact | SHA-256 |
| --- | --- |
| Installed monitor package `instrument.fwsc` | `02b6bcf6401db30ba56a7cfb0bb640b420c05d296682ae588a1df2cd6ac7bd5d` |
| Monitor `instrument.elf` | `863ef653ac0ba1080f4c12472a8a29985835d9b43ed5da5266c97c5477a674d9` |
| Monitor `instrument.bin` | `57b8a27c76f9bdc2d0b409b0d8baec204745f886de3e9f68895f41705921c997` |
| Configuration bytes | `9d0d30219e1228a7809ef0abe08bda1068a4a0de5487737445d4f06f7e9162b0` |
| Device bytes | `3d15b0b23702b6dae0db3a850dc1229d31700f62416a9b4521bd302e7cc7d40a` |

ELF symbols `CFG_DESC_PLAIN` and `DEV_DESC_PLAIN` are at FM-1 virtual addresses
`0x0201384e` (175 bytes) and `0x0201383c` (18 bytes); corresponding ELF file offsets
are `0x13a4e` and `0x13a3c`, and raw image offsets are `0x1372e` and `0x1371c`.
These are FM-1 addresses, not MX-1 memory. Extraction uses the ELF symbol's
section, `st_value - sh_addr`, and `st_size`; no descriptor bytes were edited.
Device identity is VID `1209`, PID `0001`, bcdDevice `0390`, full-speed USB.

## Verification boundary

The ARM harness executes the new parser through the original configuration ABI
constructor at USB `0x60008580` and the new selection callback. It verifies the
exact FM-1 fixture, sweeps 177 header lengths (only 37 and 65 accepted), rejects
166 truncated configurations, and checks both counts for one-way and
bidirectional endpoints with 7- and 9-byte standard endpoint descriptors. A
following unrelated interface cannot be included in the accepted MIDI length.
The existing transport, sync-blocking, priority, reconnect and malformed-descriptor
regressions remain in the full reproduction pipeline.

This establishes a concrete enumeration blocker and its software fix. It does
not prove that it was the only cause of the physical no-MIDI result, or that
USB scheduling, clock output and the FM-1 receiver now work together. Physical
acceptance remains open; the candidate stays UNTESTED.

## Candidate placement

Candidate SHA-256: `a21259c0c896fa06db18e87f8a3d997fe1661c7e9ee14ad7c8077fdf6446292b`.
USB application SHA-256: `d01abbe0142470cf990147aef59698c0a36a541b8bfd113479aeb84319946ae3`.
Host extension SHA-256: `c742b9aba872b5eb48baa220ce0796195663e4c0f839cca1f5e673583ec3c6f8`.

The USB code grows from 2,624 to 2,640 bytes, ending at `0x0100c934`,
1,740 bytes before the existing allocator at `0x0100d000`. Writable USB state
remains 1,472 bytes at `0x01017868..0x01017e28`. The builder regenerates the
startup source adjustments, branch/callback targets and checksums with exact
original-byte guards; see `build/mainline/build-report.json`. The main application
and its SRAM extension are byte-identical to the MASTERING + TAP candidate
`35efb7ffd6486dae78f7b9acdf66d313e6861049f10429da00326cb09dd68bfc`.
Boot programs, updater, panel payload, descriptors exposed by USB-B, host
queue/transport policy and SRAM reservations are unchanged.
