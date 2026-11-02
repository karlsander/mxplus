# Contributing to mxplus

Useful contributions make a firmware change reproducible or resolve a specific unknown about the MX-1's audio behavior. The most valuable next evidence is identified in [ROADMAP.md](ROADMAP.md). Read the [research report](docs/RESEARCH_REPORT.md) and the relevant [host](docs/HOST_PROBE.md), [device](docs/DEVICE_PROBE.md), or [routing](docs/CHANNEL_ROUTING.md) report before expanding a probe.

The sole mainline candidate combines routing, stock-storage route persistence
and USB-B UAC2. The restored pre-generator image boots and passed a user-reported
iPhone/AUM duplex path. Routing/end stops were tested in its predecessor.
Physical snapshot/restart acceptance and broad USB validation remain open.
The current stereo packet fix has offline evidence only; the preceding image's
hardware result does not validate the changed playback routine.
Generators, extra SELECT editing and USB-host unlocking are documentation only;
see [generator handoff](docs/GENERATOR_RESEARCH.md). TAP rollback was observed
for particular application failures, not every possible failure class.

## Set up and establish a baseline

The tested platform is Linux x86-64 with Python 3.12.14 and GCC 13.3.0. The pinned `ziglang` package supplies the ARM compiler; a separate Arm GNU toolchain is unnecessary. Ghidra is optional and has a separate [reproduction guide](docs/DECOMPILATION.md).

From the root of a Git checkout (the final comparison reads `HEAD`):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/reproduce.py
.venv/bin/python tools/check_reproduction.py --check-committed
```

The input is `inputs/MX1_UPD.original.bin`. Its SHA-256 must be:

```text
26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e
```

The reproduction runner executes 17 offline stages and writes `analysis/reproduction.json` plus `build/reproduction-logs/`. It regenerates the mainline container, its patched application and extension, and the relevant instruction-level evidence. It does not access USB hardware or flash a mixer. A successful baseline gives a concrete comparison for your change; retain a failed stage's log when reporting a problem.

## Choose a bounded change

Maintain one builder (`tools/build_firmware.py`), linker layout and artifact
(`build/mainline/MXPLUS_MAINLINE_UNTESTED.bin`). Do not reintroduce separate
host/device/routing build targets. The USB-host application stays stock.

Describe the observed problem, the original path that produces it, and the intended new behavior. For a parser change, supply the descriptor bytes that trigger it. For a control change, supply the setup request and expected response or stall. For a pump change, describe the start/stop sequence, stream states and required hardware inputs. Prefer one resolved behavior over an unsupported compatibility claim.

Do not replace Roland binaries with recompiled Ghidra pseudocode. The project currently compiles new extensions and integrates them into the original machine code. Work on the C/Thumb sources, descriptor generation, linker layout or builders, then regenerate the relevant outputs.

## Firmware changes and verification

Each binary change must retain exact-input and exact-old-byte guards. Identify the component, original bytes, decoded offset, runtime address and relocation map. Check the calling convention, SRAM placement, container capacity and original initialized-data layout. Preserve the boot programs, updater, panel controller and unrelated application unless the contribution explicitly investigates them with separate evidence.

The relevant candidate report contains targeted commands. Before submitting a candidate-producing change, run the full pipeline:

```bash
.venv/bin/python tools/reproduce.py
.venv/bin/python tools/check_reproduction.py
```

Review the new `build-report.json`, the actual modified bytes and the verification results together. Commit the changed sources, rebuilt candidate/application/extension artifacts and matching evidence as one reviewable change. Update documentation when the supported profile, patch locations, hashes, test scope or remaining limitations change.

The committed-evidence gate is:

```bash
.venv/bin/python tools/check_reproduction.py --check-committed
```

Without a flag, the checker validates current artifacts and evidence. Adding `--check-committed` also compares regenerated binary identities with hashes of the actual candidate/application/extension files committed at `HEAD` and the committed build-report hashes, while ignoring nonsemantic path, timestamp and debug metadata. If you intentionally change a candidate while `HEAD` still describes the old one, the committed comparison should report a difference. Review and commit the new binaries and evidence, then run the gate against that commit. Changing report hashes alone cannot validate stale committed binaries. Do not bypass a mismatch by relaxing input checks or updating hashes without reviewing the bytes they identify. [docs/CI.md](docs/CI.md) describes the automated workflow.

Tests should address the change's actual risk. Existing useful checks include execution through original ARM call boundaries, register/stack preservation, malformed and unsupported descriptor fixtures, unchanged Roland paths, startup-copy equality, endpoint-table comparison, original decoder/updater acceptance, and explicit error paths. Add tests when they distinguish correct behavior from a plausible failure. Documentation-only changes generally require link, path and factual review rather than rebuilding firmware.

State what each harness assumes. In particular, a supplied readiness bit, identity sample converter or stubbed FIFO reply is a test boundary, not a hardware observation. Offline success does not establish safe flash programming, physical recovery, timing, real packet handling or useful audio.

## Reporting a hardware result

Use [docs/HARDWARE_VALIDATION.md](docs/HARDWARE_VALIDATION.md) for the staged procedure. Collect stock evidence before changing firmware, and establish a device-specific recovery route before any candidate installation. Authorization to modify files alone does not authorize a hardware update.

A useful report includes:

- The MX-1 model/board identifiers, displayed version, exact original or candidate SHA-256 and the repository commit used to build it.
- The complete connection topology: USB port, host/device roles, cable/adapter, power arrangement and any hub.
- Host OS/kernel, driver binding, relevant app and device versions; whether a Roland driver or Linux Roland quirk is involved.
- Mixer sample rate/mode, active USB interfaces and alternates, channel mapping, start order and test duration.
- Raw descriptors, setup/control requests and packet traces where available, plus a short audio sample or measured result that addresses the hypothesis.
- Exact commands/settings, pass/failure observations, resets or reconnects, and an explanation of what remains untested.

For USB-B, an interface name appearing in an app is insufficient evidence of audio. A capture-first result needs actual IN packets before OUT traffic; some compatibility paths can open playback behind a recording application's back. Test stereo, 18-channel and both mixed combinations with the selected alternates recorded. The current clock-validity reply does not measure PLL lock.

USB1–4 retain stock behavior. The retired generic-host experiment is documented
in `docs/HOST_PROBE.md`; it is not an available test image or maintained source target.

Publish only relevant trace data. Remove unrelated device serial numbers, personal file paths, account data or audio that should not be shared, and document any redaction that affects reproduction.

## Pull request content and provenance

Explain the concrete problem, the change and its resulting behavior. Include the relevant addresses or descriptor fixture, test commands/results, current candidate identities when changed, and material limitations. Keep factual claims linked to repository evidence or primary sources. Label inferences and unresolved questions explicitly.

The baseline manifests describe the frozen initial snapshot, not every later tree. Do not rewrite them to match a new development state. Current candidate build reports and the committed-evidence gate describe the current binaries.

No project license has been chosen. Do not attach an open-source license to Roland firmware, decompiled portions or complete modified firmware containers. Record the origin of imported material and preserve applicable notices; licensing decisions for new project work are separate from the ownership of third-party firmware. See [PROVENANCE.md](PROVENANCE.md).
