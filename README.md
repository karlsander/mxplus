# Roland MX-1 firmware research and experimental USB extensions

Investigation: 1 November 2026. This project analyzes the original firmware supplied for this investigation and contains two independently compiled, rebuilt firmware candidates.

**The candidates have not been flashed to a mixer or demonstrated to carry audio on physical USB hardware.** They are research builds with substantial instruction-level verification, not installable releases. The original input is kept separately and unchanged.

## Results

| Goal | Concrete result | Remaining limit |
| --- | --- | --- |
| Understand and rebuild the firmware | All six embedded programs extracted; compression and checksums recovered; runtime memory maps reconstructed; original ARM decoder and updater executed against rebuilt images | No complete original source tree or verified physical recovery procedure |
| Accept other USB audio devices on USB1–4 | Compiled UAC1 enumeration/selection extension, with original Roland compatibility paths retained | Narrow stereo format only; existing transfer engine and clock behavior still need hardware work |
| Make USB-B usable as an iOS audio interface | Compiled UAC2 descriptor, fixed-clock control and capture-startup prototype, retaining 18-channel and stereo modes | Physical enumeration, implicit-feedback startup and sustained audio unverified |
| Obtain iOS audio without changing mixer firmware | Linux host-to-UAC2-gadget bridge planner and setup helper | Requires appropriate host plus device-controller hardware and bench validation |
| Identify internal hardware | ESC2-family software and separate execution contexts; strong STM32F100 panel-controller identification | Main-board chip count, exact memory/codec parts and wiring not established |

Read [docs/RESEARCH_REPORT.md](docs/RESEARCH_REPORT.md) for the integrated findings. The standalone `MX1_Research_Report.html` is the same report with accessible headings and tables. Start a continuation at [docs/HARDWARE_VALIDATION.md](docs/HARDWARE_VALIDATION.md), after reading the candidate-specific limits.

## Firmware identity

The only supported input is `inputs/MX1_UPD.original.bin`, 4,194,320 bytes, SHA-256:

```text
26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e
```

Both application headers contain `1.051132` and `16-0906_11:04:55`. This matches the version-1.05 generation. The builders require the exact hash and exact old bytes at every patch site; using another Roland model or firmware revision is unsupported.

## Reproduce the offline work

Tested platform: Linux x86-64, Python 3.12.14, GCC 13.3.0. The Python requirements include the ARM compiler, disassembler, ELF reader and instruction emulator. A system C compiler is also needed for the native clock-control boundary tests.

From this directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/reproduce.py
```

The script re-extracts the original, reconstructs maps, compiles both candidates, runs their instruction-level tests, checks both with the original decoder/updater, runs the descriptor and bridge-planning tests, tests the clock-control logic and original audio pump, and regenerates panel-controller evidence. It records results in `analysis/reproduction.json` and logs in `build/reproduction-logs`. It does not access a mixer, USB device, flash programmer, system USB gadget configuration or network service. Ghidra exports are already included and are regenerated separately using [docs/DECOMPILATION.md](docs/DECOMPILATION.md).

Individual builds:

```bash
.venv/bin/python tools/build_host_probe.py inputs/MX1_UPD.original.bin \
  --output build/host-probe
.venv/bin/python tools/build_device_probe.py inputs/MX1_UPD.original.bin \
  --output build/device-probe
```

The rebuilt candidates are separate experiments:

| File | Changed component | Intended experiment |
| --- | --- | --- |
| `build/host-probe/MX1_UAC1_HOST_PROBE_UNTESTED.bin` | USB-host application only | Restricted generic UAC1 parsing and selection |
| `build/device-probe/MX1_UAC2_DEVICE_PROBE_UNTESTED.bin` | Main application only | Standard UAC2 USB-B audio presentation and capture-first startup |

Neither includes the other's modification. Their `build-report.json` files describe every patch, the injected code, startup relocation changes, current hashes and limitations. A literal-only LZSS encoder grows the stored application but remains inside the verified update slots. No original boot program, updater or panel-controller payload is changed.

## Where to continue

| File or folder | Contents |
| --- | --- |
| `docs/RESEARCH_REPORT.md` | Main conclusions, evidence, uncertainties and development priorities |
| `docs/HOST_PROBE.md` | Exact host profile, patch integration, regression tests and transport limits |
| `docs/DEVICE_PROBE.md` | USB-B UAC2 implementation, controls, capture change and tests |
| `docs/HARDWARE_VALIDATION.md` | Staged physical validation and evidence to collect |
| `docs/DECOMPILATION.md` | Methods, runtime mapping and Ghidra reproduction |
| `research/container.md` | Container layout, LZSS, checksums and actual update path |
| `research/container-binding.md` | Original host driver's wildcard registration and binding tests |
| `research/usb-compatibility.md` | Original USB descriptor/parsing/transport evidence and primary-source context |
| `research/uac2-descriptor-audit.md` | Independent UAC2 graph and control audit |
| `research/device-control.md` | Main firmware functions, ABIs, callbacks, registers and capture state machine |
| `research/hardware.md` | Hardware evidence and explicit confidence levels |
| `research/linux-bridge.md` | Linux bridge topology, direction mapping, clocks, setup and limitations |
| `research/device-reproducibility.md` | Dependency audit and independent device-build reproduction |
| `patches/` | New C/Thumb assembly and linker scripts |
| `tools/` | Container, mapping, build, test and bridge utilities |
| `analysis/ghidra-main`, `analysis/ghidra-usb`, `analysis/container_ghidra_updater` | C-like decompiler output, function indexes and cross-references |
| `sources/hardware/decomp` | Panel-controller pseudocode and references |
| `analysis/*verification.json`, `build/device-probe/arm-verification.json` | Machine-readable instruction-level checks |
| `sources/hardware/uac2_pump_harness_results.json` | Original and patched pump traces under stated MMIO assumptions |

Decompiler output is approximate pseudocode. Its automatically assigned types, function boundaries and control flow can be wrong even when the tool reports successful decompilation. Critical paths were checked against disassembly and selected original instructions were executed. This project compiles new extension code and links it to retained original machine code; it does not compile the entire Roland application from recovered C.

## Physical work is the next boundary

The updater's normal write range preserves the boot programs, but application checksums are checked after flash writes. Preserving boot bytes does not establish recovery from a faulty application or failed write. A successful emulator run does not model the flash controller, USB PHY, RTOS timing, DMA, FIFO capacity, audio converters or real clock drift.

Do not treat the `UNTESTED` files as an ordinary firmware upgrade. Review the validation plan and establish a recoverable bench before any experimental installation. No flashing utility is included or invoked by the reproduction script.

The supplied firmware and its decompiled portions remain derived from Roland's binary. The project records independently written research tooling and extensions alongside that user-supplied material; it makes no claim to ownership of Roland's firmware or to an official Roland release.
