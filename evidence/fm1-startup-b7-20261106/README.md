# B7 input priming and retained MIDI failures, 6 November 2026

[B6](../fm1-converter-b6-20261106/README.md#observed-on-b6) accepted 52,631
packets in transport-only mode, with scheduling gaps and MIDI loss until
reconnect. A separate muted converter test succeeded twice and then rejected
a nonzero DSP entry gate. No audible result exists. The immediate MIDI failure
was not recorded, and reconnect erased the controller snapshot.

B7 changes three bounded behaviors in the same mainline candidate:

- Normal/muted conversion waits for the first two accepted packets instead of
  submitting zero blocks before the input is primed. Explicit local-tone mode
  remains independent of USB input; subsequent underrun handling and
  stop-on-converter-error are unchanged. This tests a startup-order hypothesis;
  it does not establish why B6's DSP gate became nonzero.
- Urgent clock/transport queue overflow retains a distinct fault bit (4).
  Musical output stops until rebind, while the independent debug response can
  still use a healthy endpoint. Completion/length and submission failures
  retain terminal bit 1; there is no automatic retry or buffer reuse. Ordinary
  queue overflow retains bit 2 and leaves sync priority intact.
- Pages 9/10 retain the first RX/TX failure since boot: source, tick, audio
  phase, signed immediate result and page-4 software fields. An atomic
  first-writer claim prevents replacement by a later cancellation or failure.
  Fields can advance while copied, so this is not an atomic hardware snapshot.
  Rebind also preserves the cached controller pages without following any
  saved pointers. Protocol and topology state still reset for the new device.

The split masks, admission restrictions, periodic list edits, deadlines and
DMA retirement are unchanged. Automatic EHCI audio startup remains disabled.
FM-1 keeps bridge B1. The Mac bench script expects MX wire build 183 and reads
the new pages, including after failures; its independent FM cleanup/readout
remains available when MIDI fails. Normal firmware startup clears the failure
records; no arbitrary memory, reset or flash command is introduced.

## Evidence and placement

All original findings concern **app_usb**. Resident runtime is decoded offset
+60000000; hot code relocates decoded 2b1f4 to runtime 01000300, length bbe4.
Original decoded 33b54/runtime 01008c60 holds off normal converter submission
for sixteen task calls, then checks completed input transactions at 01008d14
before calling 01008baa/010088dc. The custom path's wait for two received
packets is its own priming rule, not a claim to reproduce stock timing.
[Original instruction excerpt](original-disassembly.txt).

Hot code is 3,180 bytes, 0100bee4..0100cb50; hot state remains 1,472 bytes.
Audio/debug code is 12,992 bytes, 607f0000..607f32c0. Existing audio/DMA,
controller and converter snapshot addresses are retained. Eight 116-byte
MIDI failure records append at 607fa8ac..607fac4c, raising audio/debug state to
27,724 bytes in the existing 64-KiB heap reservation. The compiled audio wrapper
still uses 184 bytes including saved registers; this does not measure total
stack high-water use. Main application, boot programs, updater, panel and
container boundaries remain unchanged. Whole-input and exact-site guards are
retained; the build report records bytes, targets, relocation and checksums.

Targeted instruction checks cover no initial converter submission without
priming, the original gate error after priming, urgent-overflow diagnostics,
continued isolation after real transfer/length failures, first-failure
retention through later errors/rebind, cached controller retention and rejection
of incomplete failure snapshots. The original converter boundary still runs
with DSP/MMIO/RTOS responses modeled. USB timing, TT interaction, DSP gate
clearance and audible audio remain physical-test questions. Full validation
and exact candidate identity are recorded in [candidate.json](candidate.json).

B7 has not been installed at candidate preparation. Keep `UNTESTED` and the
PR open pending physical audio acceptance.
