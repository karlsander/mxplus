# mxplus

Firmware research, channel routing and experimental USB audio extensions for the **Roland MX-1**.

The project investigates channel source reassignment, compatible USB audio devices on the four AIRA host ports, and a standard audio driver for the computer USB-B port, including on iPhone and iPad. It contains the original firmware, reverse-engineering evidence, reproducible build tools, and three separately compiled firmware experiments.

**The user reports successful channel rerouting on their MX-1 after the page-guard and writable-state fixes.** This revision makes the source selector stop at its endpoints and awaits a new bench test. The report does not establish every source/rate/mode combination or recovery behavior. The current results establish selected code paths and binary integration through offline tests. They do not establish working iOS audio, general USB-device compatibility, audible channel routing, or a verified recovery procedure.

## Current status

The initial investigation and offline evidence were completed on **1 November 2026**.

| Area | Implemented or established | Next evidence needed |
| --- | --- | --- |
| Firmware reconstruction | Six embedded programs extracted; compression, checksums and runtime mappings recovered; original ARM decoder/updater exercised against rebuilt images | Physical update and recovery behavior |
| Channel source routing | SELECT + TEMPO source selection on all 11 strips; 53 choices on stereo strips, mono-side choices on mono strips, duplication and the 5/6-to-USB2 split | Physical source order, levels, live switching and sustained audio |
| USB1–4 host ports | Compiled extension admits a narrow high-speed, stereo UAC1 profile while retaining Roland selection paths | Matching real-device descriptors, transfer behavior and clock handling |
| USB-B computer port | Compiled UAC2 descriptor, fixed-clock controls and capture-startup change; stereo and 18-channel modes retained | Class-driver enumeration, capture-first packets and sustained audio |
| External Linux bridge | Stock-firmware host-to-UAC2-gadget planner and setup helper | A suitable board with independent host/device controllers and bench testing |
| Hardware identification | ESC2-family software evidence and strong STM32F100 panel-controller identification | Direct MX-1 board identification, memories, codecs and recovery connections |

Read the [research report](docs/RESEARCH_REPORT.md) for the findings and evidence, or open the [standalone HTML report](MX1_Research_Report.html). The [roadmap](ROADMAP.md) defines the next milestones; the [hardware validation plan](docs/HARDWARE_VALIDATION.md) explains what a useful bench result must establish.

## Quick start: reproduce the offline results

The tested environment is Linux x86-64, Python 3.12.14 and GCC 13.3.0. A native C compiler is required; the pinned Python requirements supply the ARM compiler, disassembler, ELF reader and instruction emulator. Ghidra is optional.

From the root of a Git checkout (the final comparison reads `HEAD`):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/reproduce.py
.venv/bin/python tools/check_reproduction.py --check-committed
```

The reproduction runner regenerates decoded images, maps, all three candidates and their offline checks. It records the 22 stages in [analysis/reproduction.json](analysis/reproduction.json) and logs under `build/reproduction-logs/`. The final check compares rebuilt firmware/application/extension hashes with the current evidence, hashes of the actual artifact files committed at Git `HEAD`, and the committed build-report hashes. After dependencies are installed, these checks operate on local files: they do not connect to a mixer, flash hardware or configure a USB gadget.

The only supported input is [inputs/MX1_UPD.original.bin](inputs/MX1_UPD.original.bin), **4,194,320 bytes**, with SHA-256:

```text
26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e
```

Both application headers identify `1.051132`, dated `16-0906_11:04:55`, matching the version-1.05 generation. Builders reject a different input hash or unexpected bytes at a patch site. See [CONTRIBUTING.md](CONTRIBUTING.md) for intentional candidate changes and [docs/DECOMPILATION.md](docs/DECOMPILATION.md) for the optional Ghidra workflow.

## Separate firmware experiments

| Candidate | Changed component | Scope and details |
| --- | --- | --- |
| `build/host-probe/MX1_UAC1_HOST_PROBE_UNTESTED.bin` | USB-host application only | [UAC1 host probe](docs/HOST_PROBE.md): restricted stereo enumeration and selection; the transport remains unverified |
| `build/device-probe/MX1_UAC2_DEVICE_PROBE_UNTESTED.bin` | Main application only | [UAC2 device probe](docs/DEVICE_PROBE.md): high-speed audio presentation, read-only clock and capture-first startup |
| `build/routing-probe/MX1_CHANNEL_ROUTING_UNTESTED.bin` | Main application only | [Channel-routing probe](docs/CHANNEL_ROUTING.md): select a strip's source by holding SELECT and turning TEMPO |

Each image is an independent experiment. All three preserve the original boot programs, updater and panel-controller payload. Their adjacent `build-report.json` files record patch sites, relocation changes, extension placement and exact hashes. Preserving boot bytes does not prove that a failed update can be recovered.

The USB-B probe retains proprietary MIDI and implicit feedback; its clock-validity response describes the configured rate, not measured PLL lock. The original full-speed configuration has no audio endpoints. It is not a universal class-compliance claim. The [device report](docs/DEVICE_PROBE.md) and [compatibility analysis](research/usb-compatibility.md) explain these boundaries.

## Repository guide

| Start here | Contents |
| --- | --- |
| [docs/RESEARCH_REPORT.md](docs/RESEARCH_REPORT.md) | Integrated conclusions, evidence and uncertainties |
| [docs/DECOMPILATION.md](docs/DECOMPILATION.md) | Recovery methods, runtime maps and decompiler limitations |
| [research/](research/) | Detailed container, USB, hardware, control-flow and bridge investigations |
| [patches/](patches/) and [sources/hardware/](sources/hardware/) | New C/Thumb extensions, linker scripts and focused analysis harnesses |
| [tools/](tools/) and [tests/](tests/) | Extraction, rebuilding, actual-instruction checks and descriptor fixtures |
| [docs/CI.md](docs/CI.md) | Automated offline verification and candidate-hash checks |
| [analysis/](analysis/) and [build/](build/) | Decoded images, decompiler exports, verification records and experimental builds |
| [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) | Reproduction, review and evidence requirements |
| [PROVENANCE.md](PROVENANCE.md) | Source origins, frozen snapshot semantics and licensing status |

Decompiler exports are approximate pseudocode, not a recovered source tree that can be recompiled into the complete product. The builders compile new extensions and integrate them with retained original machine code. Detailed reports remain the source for the assumptions behind each test.

This is an independent research project, with no claimed Roland endorsement. **No project license has been selected.** Original firmware and its derivatives are third-party material; see [PROVENANCE.md](PROVENANCE.md).
