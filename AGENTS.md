# Working on mxplus

mxplus maintains one Roland MX-1 mainline build combining channel routing and USB-B UAC2. The USB-host unlock is documented only. Read [README.md](README.md), the relevant candidate report, and [CONTRIBUTING.md](CONTRIBUTING.md) before changing a build or interpreting its evidence. Use [ROADMAP.md](ROADMAP.md) to distinguish the present result from future work.

## Scope and current boundary

The routing predecessor passed user bench tests, including encoder end stops.
The combined mainline image still needs USB-B hardware validation. Do not claim
safe upgrades, broad interoperability or verified failed-application recovery.
A hardware experiment requires user authorization.

Maintain only `tools/build_firmware.py`, `patches/mainline.ld` and
`build/mainline/MXPLUS_MAINLINE_UNTESTED.bin` as the active firmware build.
USB-host unlocking must remain documentation only; no parallel builder or code
variant. The original USB application, boot programs, updater and panel payload
remain unchanged. Read `docs/MAINLINE.md` for the combined memory layout.

## Binary identity and patch discipline

- Keep `inputs/MX1_UPD.original.bin` unchanged. Its required SHA-256 is `26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`.
- Preserve whole-input hash checks and exact expected bytes at each overwritten site. On a mismatch, investigate the revision or evidence; do not weaken a guard to make a build pass.
- State the component, decoded-image offset and runtime address for a binary finding. Account for startup relocation with the corresponding map. Main, USB and updater contexts can share numerical addresses without sharing memory.
- Make changes in the extension sources, descriptor generator, linker script or builder, then regenerate outputs. Avoid unrecorded edits to a finished firmware image or generated decompiler output.
- Record overwritten bytes, new bytes, branch/callback targets, ABI assumptions, placement bounds, relocation changes and component checksums in build evidence. Check both slot capacity and runtime memory use, including allocator reservations.
- Preserve unrelated components, boot programs, updater, panel-controller payload and container boundaries. Changes to those areas require their own explicit rationale and verification; existing application-patch evidence does not cover them.
- Keep experimental filenames and `UNTESTED` status until physical evidence justifies a narrowly stated change in status. The embedded Roland version alone cannot identify a modified candidate.

The builder and `build/mainline/build-report.json` show the required patch accounting. A second firmware revision needs a separately established map and guards; changing the accepted hash is not sufficient.

## Evidence and analysis

Use original instructions, bytes and cross-references to establish critical behavior. Ghidra output can suggest a hypothesis, but its types, function boundaries and control flow are not authoritative. Do not equate successful decompilation with complete source recovery.

Separate observations, inferences and unknowns. Cite local evidence with paths and addresses; cite external claims with primary-source URLs and relevant sections. Related Roland product schematics can support a family inference, not an asserted MX-1 bill of materials. Do not invent chip identities or register semantics from a plausible address alone.

For actual-instruction tests, document what runs unchanged and what is stubbed or modeled. Calling-convention, byte-boundary, malformed-descriptor, startup-relocation and before/after regression checks are valuable when they address a concrete failure mode. Instruction counts are not timing measurements. Mocked MMIO readiness does not establish real FIFO, DMA, PLL, packet or USB-PHY behavior.

Retain the present limitations when discussing the device probe: fixed read-only sample rate, validity based on configuration rather than PLL lock, implicit feedback, proprietary MIDI, high-speed audio only, and unverified real stereo/mixed-alternate packet boundaries. For the host probe, retain its narrow UAC1 format/profile and lack of established generic clock/feedback handling. Consult the candidate reports for exact constraints.

## Verification workflow

Use the pinned project environment from the root of a Git checkout:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/reproduce.py
.venv/bin/python tools/check_reproduction.py --check-committed
```

`reproduce.py` rebuilds and verifies offline evidence. `check_reproduction.py` without a flag checks the current artifacts and evidence. Adding `--check-committed` also compares candidate/application/extension hashes with both the actual artifact blobs and build reports in Git `HEAD`; neither mode certifies hardware behavior. A deliberate candidate change will disagree with the old committed hashes until the new artifacts and evidence are reviewed and committed together. Updating committed report hashes while leaving stale committed binaries is insufficient. Do not conceal a difference or alter expected evidence without review. See [docs/CI.md](docs/CI.md) for the automated workflow.

Run the relevant targeted checks while developing; run the full reproduction and committed-evidence gate for a candidate-producing change. Documentation-only edits need accurate links, paths and claims, not redundant firmware execution. Expand tests only to resolve an identified risk. Do not add hardware, flashing, network or privileged gadget-configuration operations to the offline reproduction path.

Generated reports may contain local paths or timestamps. Do not describe those metadata differences as changed machine code; compare the byte hashes and the verifier's substantive evidence. Preserve historical evidence in `evidence/` instead of rewriting it as if it described a later candidate.

## Hardware work and contributions

Follow [docs/HARDWARE_VALIDATION.md](docs/HARDWARE_VALIDATION.md) for any authorized bench work. Begin with a stock baseline, exact candidate identity and a device-specific recovery route. A normal updater preserving boot bytes is not that route by itself. Keep the experiment's wiring, power, host/device roles and start order explicit.

A hardware result needs enough context to reproduce: board/model identification, firmware hash, OS/driver/app versions, ports/cables/power, sample rate, selected USB alternates, control and packet traces, audio observations, duration and failures. Explain whether a vendor driver or compatibility quirk participated. Remove unrelated personal data before publishing logs.

Keep new work's origin and imported material's notices clear. No license has been selected for project-authored work, and no repository-wide open-source license applies to Roland firmware. See [PROVENANCE.md](PROVENANCE.md). Make task-scoped changes, preserve other contributors' work, and report both what changed and what the evidence still cannot establish.
