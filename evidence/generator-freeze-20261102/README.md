# Generator activation freeze — 2 November 2026

The user confirmed that maintained SDRAM image
`232a1e87a8c4378ce740c295ed9df7d5659c3645899f4c51747e656c022cfe25`
boots normally. Selecting the first generator freezes the mixer before its label
appears. That source is NSE (ID 53), immediately after PC9R. Transport state,
sample rate and selected strip were not recorded; BD was not separately tested.

## One-off RAM-publication isolation

Candidate: `b294ea0dc9ee252ba3c0e03ed52b5a8c5d64c42b8e8ecf962d41116577b6a69e`.
Base: `cb0124c49333ce0f54b091a0d7a60908fef26537`.
Local diagnostic commit: `f52d11534ca1fb88361d863095e23a78886eb6dd`.

The only feature-source change redirects the audio wrapper's output pointer
from inferred MMIO `0x40101100..0x40101130` to a 48-byte owned RAM array at
`0x0101783c..0x0101786c`. All ranges are end-exclusive. Generator computation,
callback installation, source picker and DSP operands remain unchanged. The
new state shifts later writable data; the builder accounts for those symbol
relocations. Initialized state grows from 1,512 to 1,560 bytes, within the
existing `0x01018000` bound; SDRAM code remains 6,732 bytes. Exact original
input and patch guards are retained. Build-report patch records identify the
main-component decoded offsets, runtime targets, startup copies and checksums.

The first physical publication address is beyond the established stock USB
sample bank. Actual capacity at this inferred address is unknown; synthetic
address calculations and emulator mappings do not establish physical support.
This experiment retains DSP routing to `0xa040` / `0xa041 + strip`, so it does
not test or promise generator audio or silence. Monitor muted and test whether
NSE selection updates the display and leaves controls responsive.

All 22 reproduction stages and the committed-artifact gate passed. The audio
instruction harness checks the owned RAM destination and rejects any read or
write to the original physical generator interval. Existing MMIO, USB FIFO,
scheduler and DSP models do not establish hardware behavior or real-time cost.
The candidate was copied to the MX-1 update drive, fully readback-verified and
ejected successfully. The user reported the same freeze after flashing: the
display remained on P9r when advancing toward NSE. Redirecting CPU sample
writes into RAM was therefore insufficient to prevent the failure. It does
not establish that the original MMIO bank is usable; that access was absent
from this test.

The unchanged DSP routing, active computation and interrupt timing remain
candidates. This experiment did not resolve the freeze.

Forensic reproduction: apply `historical-source-delta.patch` to the base
commit, use its pinned environment, and run `tools/reproduce.py`. Reports here
identify the resulting image; checkout paths are redacted. No second active
builder or maintained firmware artifact is added to the main tree.
