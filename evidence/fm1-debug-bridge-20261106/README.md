# Dedicated FM-1 bridge and MX-1 hooks

The user requested a dedicated FM-1 USB/Bluetooth bridge, without the instrument
app, and explicitly authorized MIDI commands for MX-1 modes and diagnostics.
The FM-1 was connected to the Mac and flashed; its Mac USB/BLE bench passed.
See [implementation, protocol and boundaries](../../docs/DEBUG_BRIDGE.md).

The MX-1 candidate identity and offline checks are in [candidate.json](candidate.json).
It has **not been installed or boot-tested**. The user must return to put the
MX-1 in update mode and move the FM-1 to HOST3. No new MX-1 audio success is claimed.

All 17 offline reproduction stages passed with hardware boundaries modeled.
The changed image retains the same main app, boot programs, updater and panel
payload. The input/old-byte guards and existing audio/DMA placement are intact.
The new state follows the old arrays; there is no new firmware build variant.

FM-1 evidence: [dedicated bridge bench](https://github.com/karlsander/fm1-instrument/blob/codex/host-debug-bridge/debug-bridge/evidence/bench-20261106.json).
The Mac modeled MX-1 replies for the forwarding test. Those test messages were
cleared from the FM-1 afterward. Instrument backups remain local and private.
