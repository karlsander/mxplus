# B5 EHCI input candidate, 6 November 2026

The user authorized FM-1 host audio and the dedicated Bluetooth/MIDI development
bridge. The [B4 physical bench](../fm1-midi-timeout-b4-20261106/README.md#observed-on-b4)
established working commands, continuous telemetry and rate/alternate/endpoint
setup, with no audio packets. B5 adds a controlled EHCI split-ISO input stream
for that observed full-speed device behind a high-speed hub.

Candidate: `e40b809672c7ef5d4be190b48eb01c5116835e88ae0d67a896d279ba02b3e0b4`,
4,194,320 bytes, wire build 181. At build completion it had not been installed.
The dedicated FM-1 bridge stays on B1, hash
`f13e43fcb9b34db7c8387751871b9a045fa55572b33c3b1759594c0451c54da0`.
Exact identities and validation state are in [candidate.json](candidate.json).
No physical audio, task timing, coexistence or failed-application recovery is
claimed from these offline results.

Hosted offline workflow [42236511542](https://github.com/karlsander/mxplus/actions/runs/42236511542)
passed for commit `a41865e766cb6c291d3782d700c1967d502f6c79`.
At 14:54 UTC, B5 was copied to the Roland updater as `MX1_UPD.BIN`, read back
with the candidate SHA-256, and ejected. The [copy receipt](copy.json) records
that delivery; update completion and normal boot were not yet observed then.

The [implementation report](../../research/fm1-ehci.md) distinguishes original
instruction findings, new code and modeled boundaries. The crucial original
finding is that 60007faa replaces the initial EHCI frame list with 4000b000;
using controller context +8 would modify the wrong table. See
[original disassembly](original-disassembly.txt). All addresses there belong
to app_usb; resident addresses are decoded offsets plus 60000000.

Only app_usb changes from B4. The existing 64-KiB reservation is retained:
3,056 bytes of hot code, 1,472 hot state, 12,000 audio/debug code and 26,220
audio/debug state. Original audio buffers and diagnostic/bridge offsets remain
fixed; 264 EHCI state bytes are appended. The new binding hook is at decoded
11d40, runtime 60011d40. Exact overwritten/new bytes, trampoline and callback
targets, startup relocation and checksums are in the sole mainline build report.

All 17 reproduction stages, current/committed-artifact gates and six browser
patcher tests passed. Targeted
checks execute original EHCI table construction/replacement and controller
query queue/worker dispatch, compiled siTD construction, 300 packet completions,
sample conversion, wrap, error handling, explicit start/stop, readout pages,
poll bounding, frozen-frame retention, changed-link quarantine, freed-device
lifetime and reset-error ownership. An additional targeted run checked the
actual HOST3 port-2 layout: descriptor slot 3's 184-byte buffer crosses a
4-KiB boundary and both page pointers are correct. This additional case was
added after the full pipeline finished; no candidate bytes changed.

Heap, task/IRQ setup, MMIO/DMA transactions, RTOS delivery, stock EHCI completion
and teardown outcomes, and DSP hardware are modeled as documented. Original
converter and OHCI/MIDI regressions remain. The converter MMIO write hook was
narrowed to 40040548 to avoid a reproduced Unicorn 2.1.4 global-hook IT-state
failure at an unrelated conditional store. Firmware guards were not weakened.

For the bench, retain the exact installed/copy identity, use normal MX-1 power,
connect FM-1 directly to HOST3 and keep it near the Mac for BLE. Leave other
host-audio devices disconnected. Keep monitoring low. The optional hardware
script `tools/fm1_audio_bench.py` uses the existing FM-1 client, waits for build
181, runs probes 1/2/3/5, records silence and quiet stereo/local-converter tone
windows, then mutes, stops and returns to alt0. It is excluded from reproduction.
Raw JSONL includes Bluetooth identifiers and stays private; review result JSON
before publishing any physical evidence.

The experiment admits one stream, no other active stock audio, and only small
HS interrupt traffic alongside its stock dummy chains. It is not a general TT
bandwidth allocator. New periodic endpoints may be refused with −13 while it
retires. A run expires after nominally 60 seconds, and unresolved DMA ownership
is retained until a halted reset or reboot.

## Observed on B5

The user completed the update and B5 returned wire build 181 over the existing
FM-1 B1 Bluetooth bridge. [Bench summary](bench-summary.json) and the three
sanitized result files preserve the measured counters and snapshots. Raw BLE
logs containing local identifiers remain private. The Mac ran macOS 27.0.1,
Python 3.14.6 and Bleak 3.0.2; it was the BLE controller, not the USB-audio host.
MX-1 hosted FM-1 directly on HOST3. The requested mapping was Auto/USB3. Cable,
board revision and mixer system-mode/rate were not independently measured.

| Run | Start result | FM-1 packet/frame delta | MX accepted packets | DSP errors |
| --- | --- | --- | --- | --- |
| [Startup](startup.json), Demora connected during boot | Stage 51, configuration/admission rejection | 0 / 0 | 0 | 0 |
| [After Demora unplug](after-demora-unplug.json), no reboot | Starts briefly, then stage 57 stop | 1 / 44 | 0 | 1 |
| [Clean boot](clean-boot.json), only FM-1 | Starts briefly, then stage 57 stop | 5 / 220 | 0 | 1 |

Each run completed rate/alternate/endpoint probes successfully. The first
snapshot reported USBCMD 00010b39, USBSTS 0000c000, segment zero and live table
4000b000. Those sampled conditions pass B5's configuration guard. A nonzero
stock-audio mask is the remaining likely rejection, consistent with the user's
Demora report, but that mask was not included in B5 telemetry. Unplug timing
relative to the first start was not measured; no stale-allocation defect is
established by that run.

Both later runs incremented the FM-1 endpoint's counters and then stopped
after one converter error. The FM-1 also recorded one stall and three overruns
per run. The MX packet consumer never accepted a packet before retirement.
This is initial device-side transfer progress, not successful end-to-end audio
or a bus-analyzer trace. None of the tone windows ran. All three cleanups
returned FM-1 to alt0/tone0 and MX-1 to phase0/unclaimed; MIDI commands continued.

B5 does not expose the converter return value or distinguish its entry-gate,
DSP-completion and drift-estimation failures. The [B6 diagnostic candidate](../fm1-converter-b6-20261106/README.md)
separates transport testing from converter calls and records the original
converter state. The B5 counter failure does not by itself identify its cause.
