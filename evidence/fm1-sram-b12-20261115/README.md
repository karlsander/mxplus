# B12 descriptor helpers in SRAM, 15 November 2026

[B11 bench evidence](../fm1-poll-fairness-b11-20261115/bench-20261115.json) showed
short diagnostic MIDI progress during poll-only audio transport, with no MIDI
fault. It still accepted only 999 packets with substantial scheduling gaps.
The later IOC comparison accepted 1,638 packets but again stalled MIDI until
expiry and overflowed the urgent TX queue. Poll-only is the current baseline;
clean audio and sustained musical MIDI remain unaccepted.

## Change

B12 moves the existing `ehci_path`, `ehci_arm` and `ehci_unlink` functions from
the USB processor's external SDRAM code reservation into its already reserved
executable SRAM slot. They remain out-of-line functions with the same bodies,
arguments and ownership rules. [Instruction comparison](helper-equivalence.json)
against B11 commit `35348fa` found identical mnemonics/operands after normalizing
local and named branch targets; [both disassemblies](helper-disassembly.txt).
This is a code-placement experiment, not proof of faster hardware execution.
No admission scan is cached/skipped and no packet/retirement guard is relaxed.

A new worker-owned service timing cache records entry/exit FRINDEX around the
complete service routine, including snapshots but excluding timing publication.
It records call count, total/max/last microframe delta, last/max audio-tick delta,
last/total accepted packets, first/end FRINDEX, and an ambiguity count. This is
elapsed time including preemption, not CPU execution time. The frame counter
must be running for it to be meaningful. The measured delta is modulo 16,384
microframes; observed audio-tick deltas of 8,192 or more flag a potentially long
sample and exclude it from total/max microframes. The tick guard cannot prove
that every multi-wrap or halted-counter case has been detected.

FRINDEX bit width and 125-microsecond units follow EHCI 1.0 section 2.3.4,
Table 2-12 ([Intel specification](https://www.intel.com/content/dam/www/public/us/en/documents/technical-specifications/ehci-specification-for-usb.pdf)).
The page returns counts, not inferred MHz or CPU utilization. New page 19 reads
only the sequence-guarded cache, with the same physical-owner check as the other
worker pages. It exposes no arbitrary addresses or live MMIO access to MIDI.
The cache resets per transport start and remains readable after retirement.

B11's completion-relative poll gap and pending latch remain, as do the short
silent bypass, converter policy, DMA placement and all packet checks. No RTOS
priority, interrupt register, original queue policy or USB reset changes.
The next short poll-only test will compare packet delivery and MIDI progress,
with the new timings to inform further work. The converter gate remains a
separate unresolved failure; this build makes no audible-audio claim.

## Identity, placement and verification

Wire build 188; [exact identity and checks](candidate.json). Hot code is 4,204
bytes at `0100bee4..0100cf50`, leaving 176 bytes before the original allocator
at `0100d000`. Hot writable state remains 1,472 bytes. Audio/debug code is
14,224 bytes at `607f0000..607f3790`, leaving 2,160 bytes in its reserved slot.
Every existing DMA/counter/cache address stays fixed. The 48-byte timing cache
appends at `607fb258..607fb288`; total audio/debug state is 29,320 bytes within
the existing 64-KiB reservation. The builder validates the three helpers reside
inside executable SRAM and records their addresses/sizes and all guarded
startup changes, relocation, branch targets and component checksums.

Individual audio/service/debug-command frames are 192/72/344 bytes; service
grew by 16 bytes for timing locals. The poll callback remains eight bytes.
These are not measurements of total stack high-water use.

No new original patch site or parallel builder is added. Main application,
boot programs, updater, panel and container boundaries remain unchanged.
The focused ARM checks pass all existing admission, DMA, request ABI, polling
preemption and retirement cases with the relocated helpers. New fixtures check
elapsed counter wrap, ambiguous long samples, per-start reset, owner/sequence
guards and cached page reads after controller MMIO is unmapped. USB/DSP/MMIO,
allocator and task delivery remain modeled; instruction counts are not timing.

B12 has not been installed. Keep UNTESTED and PR #21 open pending physical
acceptance. FM bridge B1 needs no update. The authorized bench script collects
page 19 alongside the existing snapshots before another start.

All 17 offline stages and the current-artifact gate passed with the same
candidate hash. Committed-image and browser checks are pending at this
source/artifact commit.
