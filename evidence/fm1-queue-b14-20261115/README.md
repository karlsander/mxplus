# B14 EHCI packet queue, 15 November 2026

B13's [short poll-only probe](../fm1-service-sram-b13-20261115/bench-20261115.json)
returned diagnostic MIDI and reduced mean elapsed service from B12's roughly
18 ms to 3.596 ms. FM-1 sent 2,042 packets; MX accepted 1,813, dropped 225 at its
eight-entry software queue, and recorded 84 underruns and 22 schedule corrections.
The IOC comparison reduced packet loss but again stalled MIDI and overflowed
its urgent TX queue. Poll-only remains the baseline. Neither run submitted
converter work or established audible audio.

## Change and ownership

Append one 32-entry, 6,016-byte packet queue in the existing SDRAM reservation
for the single admitted EHCI stream. Producer validation and drop-new-on-full
policy are unchanged. The audio task checks the EHCI owner before reading it,
preserves 44/45-frame packet lengths and signed stereo samples, and starts or
restarts consumption after sixteen published packets. The original OHCI queue
remains eight entries with two-packet priming. All AudioPort/DMA addresses stay
fixed. Existing admission prevents concurrent EHCI streams.

Sixteen packets add buffering delay, nominally around sixteen USB frames;
end-to-end latency is unmeasured. This absorbs batches but cannot repair a lost
wire packet, an unbounded worker stall, clock drift or converter failure.
Counters still expose overflow, underrun, malformed packets and schedule gaps.
Publication/consumption barriers and unsigned counter arithmetic remain. A new
start resets counters/priming; old packet bytes are never valid without a new
publication. No allocator, RTOS priority, IRQ/controller register or polling
interval changes. DMA ownership and retirement checks are preserved.

New probe 10 is the existing poll-only bypass policy with the existing long
240,000-audio-tick expiry (nominal 60 seconds). The default bench remains short
probe 9. `--long-silent` observes probe 10 without tone/converter submission;
`--extended` also starts through probe 10 before its explicitly selected tones
and converter modes. No arbitrary memory/flash/reset command is added. The
FM bridge B1 understands the existing generic command envelope unchanged.

## Placement and identity

All changes are in **app_usb**. [Exact hashes](candidate.json), wire build 190.
Hot code stays 4,280 bytes at `0100bee4..0100cf9c`, 100 bytes before the original
allocator. Hot state remains 1,472 bytes. SDRAM code is 14,368 bytes at
`607f0000..607f3820`, with 2,016 bytes spare. Existing state ends at `607fb288`;
new queue `607fb288..607fca08` brings state to 35,336 bytes, leaving 13,816 bytes
inside the reserved state slot. The overall heap reservation stays 64 KiB.

Original hot relocation remains decoded `2b1f4` to runtime `01000300`, length
`bbe4`; inserted hot code begins at decoded `36dd8`, runtime `0100bee4`.
`ehci_service` stays at decoded `37548`, runtime `0100c654`. SDRAM code is copied
from decoded `37f1c` / resident `60037f1c` to `607f0000`. The builder records
exact overwritten/replacement bytes, copy/zero lengths, exported callbacks,
branch destinations, original/data relocation and component checksums. There
are no new original patch sites. Service frame is 64 bytes (B13: 72); audio,
debug-command and poll-callback frames remain 192, 344 and eight bytes. These
are individual compiled frames, not measured stack high-water values.

[Component/slot comparison](component-comparison.json) against B13 confirms
only the USB application slot changes. Main application, boot programs,
updater, panel payload and container boundaries remain unchanged. Original
whole-input hash and exact-byte guards remain intact. There is one mainline
builder, linker layout and candidate.

## Verification and next bench

Targeted ARM audio tests passed. A new fixture completes packets with the
consumer stopped, fills all 32 entries across uint32 counter wrap, rejects
full-queue arrivals and reads every stereo sample/length back in FIFO order.
It poisons the old OHCI queue, checks another claimed port cannot consume the
EHCI queue, verifies sixteen-packet re-priming and rejects restart while the
old poll callback still owns its latch. Only after modeled callback delivery
may the next start reset counters and ignore stale data. Existing OHCI source
clock/priming tests are unchanged. The actual manager/start request path now
checks probe 10's poll-only flag and long bypass expiry alongside probes 8/9.

USB/DSP/MMIO, allocation and RTOS delivery remain models. These checks do not
measure real-time scheduling or establish converter/audio behavior. All 17
offline stages passed on the full rerun, followed by the current-artifact gate.
The committed-artifact gate and all six browser-patcher tests also passed
for code/artifact commit `71bfedc22d8c9461990f344e3eb5398127bdc172`.
Hosted B14 verification subsequently passed on `db23acb576d4e2f856196e0c5e1d48b48cd7be0c`:
[run 43752150201](https://github.com/karlsander/mxplus/actions/runs/43752150201).
The candidate record's pending status describes its original build-time state.
See the [resume guide](../../docs/FM1_AUDIO_HANDOFF.md) before continuing:
main now includes #20/#22, while these B14 firmware bytes retain their older base.

B14 has not been installed. Run the same short silent poll-only probe first;
compare packet/error deltas, MIDI progress and page 19 timings. Use the longer
silent probe only after those results justify it. Converter gate repair and
audible acceptance remain open. Keep UNTESTED and PR #21 open.

The first full run stopped during unchanged app_main mastering initialization:
original setter decoded `161f6` / runtime `600161f6`, stopped PC decoded `c6e6` /
runtime `6000c6e6`. The [failure trace](first-run-arm-failure.txt) and
[three successful case replays](failure-replay.json) are retained. The main
image matches B13 byte for byte. No timeout, instruction limit, assertion or
guard was changed. The cause remains unproven. The complete subsequent
17-stage run passed with the same candidate hash.
