# HOST3 uses EHCI; stepwise bridge diagnostics

On 6 November 2026 the user confirmed installing candidate
`b6122583727323d36f227fccbcb58f70efb75921d083b4c5bfe4ba4359b15b36`
and connecting the dedicated FM-1 bridge to MX-1 HOST3. The Mac read the bridge
over Bluetooth. FM-1 package:
`f13e43fcb9b34db7c8387751871b9a045fa55572b33c3b1759594c0451c54da0`.
Mac: macOS 27.0.1 (26A434), Bleak 3.0.2, native platform BLE-MIDI codec.
No vendor audio driver participated in this Bluetooth readout. MX-1 board
revision, system rate, cable model, and precise power/start sequence were not
re-recorded; prior source mapping was Auto/USB3. This is not an audio acceptance.

## Observed on B1

[Sanitized readout](live-b1.json) retains all relevant setup/status values but no
Bluetooth identifier or unrelated personal data. FM-1 saw reset, configuration,
MIDI IF2 alt0, endpoint SET_CUR 44100, and audio IF1 alt1. Its last received
legacy report was stage 4, controller 1, result 0, phase 0. Packet count stayed
18,216 across both reads: that nonzero total was left from the earlier Mac bench,
not new MX-1 audio. WAIT remained 255. Three MX-1 status attempts timed out;
FM-1 Bluetooth status kept responding with zero parser errors/drops. FM-1 queued
one USB MIDI transfer but later commands did not advance its USB TX count.

Stage 4 is the last **received** report, not proof of the current program counter
or a specific deadlock. The full MIDI command round trip remains unproven.

## Original instructions and inference

All addresses are app_usb. [Original instruction excerpts](original-disassembly.txt).
Resident runtime = decoded offset + `60000000`.
The original hot relocation is decoded `2b1f4` to runtime `01000300`, length `bbe4`.

- `09f78` / `60009f78` binds index 0 through OHCI `13c74` / `60013c74`,
  and index 1 through EHCI `11d40` / `60011d40`. The live controller field is
  therefore EHCI. A full-speed device behind a high-speed hub is a plausible
  explanation; B2 adds parent-hub fields to establish the actual topology.
- `096c6` / `600096c6` packs endpoint lookup request `02000012`, calls
  `093b0` / `600093b0`, queues and waits. Core dispatcher `0fd0e` / `6000fd0e`
  invokes list helper `1424a` / `6001424a` and signals completion.
- Binding callback `0837c` / `6000837c` only queues manager event 0 through
  `07e10` / `60007e10`. The patched handler table at `28278` / `60028278`
  runs later in the manager. A same-task bind/lookup deadlock is **not**
  established; the earlier endpoint-lookup stub hid that distinction.
- EHCI request `111ee` / `600111ee` has control, bulk and interrupt branches,
  but rejects endpoint type 1 with −5. The custom OHCI request hook is installed
  only in driver 0. Handing its private callback to driver 1 cannot start ISO.
- Original EHCI QH construction `10982` / `60010982` and ancestor lookup
  `10954` / `60010954` read device `+ec`, parent hub `+4`, downstream slots
  `+8..+20`, device address `+4c`, controller `+4a`, and speed `+58`.
  B2 caches those bounded object fields; it does not read arbitrary addresses.

## B2 candidate

The single mainline candidate now stops automatic EHCI audio startup before
rate/alternate selection, endpoint lookup, DSP initialization or ISO submission.
MIDI setup continues. OHCI behavior is retained for the existing offline path.
This isolates the debug baseline and is not EHCI audio support.

MIDI operation 5 queues one of four manager actions: set 44100 Hz, select AS alt1,
look up/validate EP84, or return AS to alt0. It acknowledges queue acceptance;
status contains pending/done/result. Each can be observed separately. No action
submits ISO, writes controller registers, resets USB or flashes firmware.
Pages 3 and 4 report cached topology and MIDI task software state. A small
unsolicited status packet every 512 eligible TX polls can expose an RX failure
without requiring a received command. It waits behind user SysEx.

Exact candidate identity, section sizes and verification are in candidate.json;
patch bytes and targets remain in build/mainline/build-report.json. Existing
sample/DMA state is unmoved; only appended debug state grows. Main app, original
boot programs, updater and panel payload are unchanged. Physical B2 behavior
and EHCI audio implementation remain pending.


## Verified updater copy

At 12:23 UTC on 6 November, B2 was copied to the identified MX-1 updater
volume as `MX1_UPD.BIN`. All 4,194,320 bytes read back with the expected
SHA-256 `360b316352e7f762d5752813dfa73a45ab13d7203676d16e232ffd29165077ee`.
The volume was ejected successfully; [copy receipt](copy.json).
Updater completion, normal restart and the B2 HOST3 diagnostic run remain
pending user confirmation. Offline CI also passed for code commit `6ebed4a`
([run 42215428754](https://github.com/karlsander/mxplus/actions/runs/42215428754)).
