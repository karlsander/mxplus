# FM-1 host-audio handoff

Snapshot: 15 November 2026. Start here when resuming in a new chat.
Goal: make FM-1 USB audio work on MX-1 HOST3 alongside MIDI, using the FM-1
Bluetooth bridge for autonomous diagnostics. No audible MX-1 host-audio result
has been established. Keep this work in draft [PR #21](https://github.com/karlsander/mxplus/pull/21).

## Repositories and exact working state

- MX branch: `codex/fm1-host-audio`. Last B14 validation commit:
  `db23acb576d4e2f856196e0c5e1d48b48cd7be0c`; code/artifacts:
  `71bfedc22d8c9461990f344e3eb5398127bdc172`. Later handoff-only commits do not
  change these firmware bytes. Local checkout:
  `/Users/kall/.codex/worktrees/mxplus-fm1-audio/mxplus`.
- FM bridge: [fm1-instrument PR #3](https://github.com/karlsander/fm1-instrument/pull/3),
  branch `codex/host-debug-bridge`, commit
  `639e392e8c831664c2272e0e6bf7a13823fc21b2`. Local checkout:
  `/Users/kall/.codex/worktrees/fm1-host-debug-bridge/fm1-instrument`.
  Its `platform` submodule has local changes and `.local` is untracked; preserve
  them. No FM reflash is needed for B14.
- `main` is now `f0ab3374a22b8487eda42ddd11537cf9a48558af`: #20 merged the long
  MASTERING hold/preset light; [#22](https://github.com/karlsander/mxplus/pull/22)
  extracted only the generic MIDI short-IN fix and its tests from this experiment.
  #17's old display diagnostics are closed.

**B14 is still based on `e8181fe`, before #20/#22.** It already includes the
short-IN correction as part of the experimental code, but retains the older
MASTERING + TAP application. Do not treat its binary as the new mainline image.
Do not merge this draft as-is. Before new firmware development, fetch/check
current main and PR state, integrate main into this branch, resolve generated
artifacts by rebuilding from source, and record a new candidate identity/build
number. Do not copy main's generated binaries over the audio candidate or rewrite
old B13/B14 evidence to describe the resulting image. The frozen B14 remains
available for its planned queue-only comparison if that experiment is chosen.

| Device/image | Wire build | SHA-256 | Last observed status |
| --- | --- | --- | --- |
| MX B13 | 189 | `af898612a1af5f6894273343d8145001c5056f9b5f382df47d52f5d7a99e8f58` | Installed; short polling and IOC comparisons completed |
| MX B14 | 190 | `e5f8404ca65ae315b782a41d90d3a1ec07bb23dbcca5a69fba08ee2e65036fd2` | Built/staged locally; not copied to updater or installed |
| FM bridge B1 | 177 | `f13e43fcb9b34db7c8387751871b9a045fa55572b33c3b1759594c0451c54da0` | Installed; retains USB-to-Bluetooth command bridge |

The sole MX artifact is `build/mainline/MXPLUS_MAINLINE_UNTESTED.bin` (4,194,320
bytes); local `build/device-staging/MX1_UPD.BIN` is a copy of B14. Required original
input SHA-256 remains `26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`.

## Read these next

1. [B14 queue design, verification and identity](../evidence/fm1-queue-b14-20261115/README.md),
   [candidate](../evidence/fm1-queue-b14-20261115/candidate.json),
   [component comparison](../evidence/fm1-queue-b14-20261115/component-comparison.json).
2. [B13 measured bench results](../evidence/fm1-service-sram-b13-20261115/bench-20261115.json)
   and [service relocation report](../evidence/fm1-service-sram-b13-20261115/README.md).
3. [EHCI implementation and history](../research/fm1-ehci.md),
   [audio profile/limits](USB_HOST_AUDIO.md), [bridge protocol](DEBUG_BRIDGE.md).
4. Sources: `patches/usb_host_midi.c`, `patches/usb_host_audio.c`,
   `patches/usb_host_ehci.inc`, `patches/usb_host_debug.inc`,
   `patches/usb_host_trace.h`; sole builder `tools/build_firmware.py`,
   integration `tools/host_midi_patch.py`, linker `patches/mainline.ld`.
   Exact guarded patch bytes, targets and placement are in
   `build/mainline/build-report.json`.

## Established progress and remaining blockers

The FM-1 profile is full-speed UAC1, 44.1-kHz stereo PCM16, interface 1 alt 1,
IN endpoint 0x84, maximum 184 bytes, interval 1. MIDI is interface 2 with bulk
0x01/0x81, maximum 64 bytes. HOST3 reaches it through a high-speed hub on EHCI
controller 1, requiring split isochronous transactions. This is a narrow admitted
input profile, not arbitrary-device audio support or USB output audio.

The bridge works through MIDI when audio is inactive. B3 fixed short-IN rejection
and debug reply wakeups. B4 isolated captured TX error -20 by removing the
per-transfer timeout only for matched FM debug sessions; this workaround is not
a general MIDI recovery fix. B5 onward adds explicit EHCI transport. Automatic
EHCI audio remains disabled; start requires a bridge probe. B10 counters located
USB-core starvation; B11 stopped the polling callback from immediately requeueing
itself. B12 measured long service time; B13 moved service into reserved SRAM.

B13 short polling accepted 1,813 packets from 2,042 sent by FM, with zero malformed
packets, 225 queue overflows, 84 underruns and 22 schedule corrections. Four MIDI
status replies arrived while running, RX/TX counters advanced, and no MIDI fault
was recorded. Mean elapsed service fell from B12's 17.73/18.55 ms to 3.596 ms,
maximum 5.875 ms. These elapsed timings include preemption, not just CPU work.

B13's IOC comparison accepted 1,949 packets but again stalled MIDI until expiry
and overflowed urgent TX. Diagnostic replies recovered, while musical TX was
stopped by fault bit 4 until rebind/reboot. Both tests ended with MX inactive and
unclaimed, FM alt 0 and tone 0. Hardware/cabling may have changed since; inspect
status on reconnect. Do not infer a fresh healthy musical path from a debug reply.

B14 appends a single 32-packet EHCI queue with sixteen-packet priming, keeping
all existing DMA/state addresses and the 64-KiB reservation. OHCI stays 8/2.
It adds probe 10: the existing polling bypass mode with nominal 60-second expiry.
Default bench remains short probe 9. This tests queue loss and sustained polling;
it does not repair converter behavior or establish audible audio.

The separate converter blocker remains: earlier B7 work saw three successful
submissions, then -1 on entry with gate `0x38800000` at `0x401010c0`. In **app_usb**,
converter entry `0x010088dc` (decoded `0x337d0`) reads a pointer at context +0x14
and rejects a nonzero pointed-to word. HOST3 context is `0x20006028` (base
`0x20005ee0`, stride 0xa4). Original initialization flows through `0x600079ee`
and `0x6001584c` to `0x010082a4`. The hypothesis that DSP work is not drained is
unproven. Establish original instruction/callback ownership before changing it;
do not blindly clear the gate or enable stock audio mask `0x4000bbb0`, which
participates in the original periodic path and experimental admission check.

## Next bench and commands

The user authorized firmware development, bridge diagnostics and updater copies;
ask for physical readiness/cabling when needed, not renewed general permission.
The last B14 readiness question received repository questions instead of a
readiness confirmation. **Do not assume the MX-1 is in update mode now.**
Last requested topology: only FM-1 on HOST3, Demora disconnected, FM powered and
near this Mac for BLE, USB3 set to Auto/USB3. Keep monitoring low for explicit
tone/converter tests. Non-USB playback does not prove audio-path independence;
updates require the user's playback/power handoff.

For a frozen B14 test, verify its hash against Git, rerun the committed-image
gate as needed, and ask the user to hold TAP while powering on and connect USB-B
to the Mac. Inspect the actual removable updater volume afresh. Copy exactly
`MX1_UPD.BIN`, fsync/sync, read back all bytes/hash and safely eject. A renamed
candidate previously flashed red until this exact updater filename was used.
Record a sanitized copy receipt; let the user press TAP, wait for Fin and restart.
No B14 copy receipt exists yet.

From the MX audio checkout, start one BLE connection with the existing client:

```sh
FM_BRIDGE_ROOT=/Users/kall/.codex/worktrees/fm1-host-debug-bridge/fm1-instrument/debug-bridge
"$FM_BRIDGE_ROOT/.venv/bin/python" tools/fm1_audio_bench.py \
  --bridge-tools "$FM_BRIDGE_ROOT/tools" \
  --candidate build/mainline/MXPLUS_MAINLINE_UNTESTED.bin \
  --output build/local/fm1-b14-next-short \
  --wait-boot 1800
```

The output directory must be new. `--wait-boot` permits capture before the user's
restart; it waits for build 190 before MX mutations and checks FM build 177.
Omit it once B14 is known to be running. A rebuilt successor needs its own
matching build guard and recorded hash. Never have two clients connected to BLE.
Raw `raw.jsonl` contains Bluetooth identifiers: keep it local and publish sanitized
`result.json` selections with candidate identity, topology and deltas.

Run the default short silent polling probe first. Compare packets, overflow,
underruns, schedule corrections, page 19 service time and running MIDI progress.
Only if that is clean enough, use a fresh output directory with `--long-silent`
for probe 10. Do not start `--extended` before assessing transport: it explicitly
enables quiet tones and converter submissions. Avoid repeating IOC unless it
resolves a new question; it has repeatedly disrupted MIDI.

Protocol quick reference (full layouts in DEBUG_BRIDGE.md): target 1 is MX,
target 0 is FM. MX op 1 reads status; op 2 reads pages 0–19; op 5 queues probes.
Setup probes are 1=rate, 2=alt1, 3=endpoint lookup; 9=short polling bypass,
10=long polling bypass, 6=stop, 4=alt0. After stop wait for phase 0/claimed 0
before alt0. Page 4 is live MIDI; 9/10 retain first failures; 11–14 cache EHCI
requests; 15–18 trace API/core/HCD handoff; 19 is service timing. FM op 3 value 0
mutes. The bench performs stop/alt0/mute cleanup and reads final FM status.
Read commands may be retried with fresh sequence numbers; inspect state after a
mutating-command timeout instead of blindly repeating it.

## Validation and local evidence

B14 passed all 17 offline stages on the full rerun, current/committed artifact
gates and all six patcher tests. Hosted run
[43752150201](https://github.com/karlsander/mxplus/actions/runs/43752150201)
passed on `db23acb`. The first full local attempt stopped inside unchanged main
mastering initialization; the retained failure and three passing case replays
use unchanged assertions/limits. Cause is unproven; the subsequent complete run
passed with identical candidate bytes. This is not physical acceptance.

Standard candidate workflow remains `.venv/bin/python tools/reproduce.py`,
then current-artifact gate, reviewed source/artifact/evidence commit, then
`.venv/bin/python tools/check_reproduction.py --check-committed` and patcher tests.
Instruction models do not establish real DMA/PHY, timing or converter behavior.

Local B13 raw results remain under `build/local/fm1-b13-live-20261115/` and
`build/local/fm1-b13-ioc-20261115/`. Sanitized evidence is committed and linked
above. B14 local logs are `/tmp/mxplus-b14-*.log`; durable failure/verification
evidence is in its committed evidence directory. The current mainline extraction
has its own worktree `/Users/kall/.codex/worktrees/mxplus-midi-short-packets/mxplus`
and evidence in merged #22. Preserve unrelated dirty worktrees.
