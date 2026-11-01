# Provenance, ownership and licensing status

mxplus is an independent investigation of firmware supplied for a Roland MX-1. It brings together original third-party firmware, derived analysis and experimental images, and new research code. This document records those origins; it does not grant rights to third-party material or apply a license to the repository.

**No project license has been selected.** In particular, there is no repository-wide open-source license covering the Roland firmware or its derivatives. A future licensing decision for newly written project material must identify its scope separately.

## Original input

The investigation's user-supplied file is preserved as [inputs/MX1_UPD.original.bin](inputs/MX1_UPD.original.bin).

| Field | Recorded identity |
| --- | --- |
| Size | 4,194,320 bytes |
| SHA-256 | `26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e` |
| Main/USB application version strings | `1.051132` |
| Main/USB application timestamp strings | `16-0906_11:04:55` |
| Initial investigation date | 1 November 2026 |

The project does not claim authorship or ownership of Roland's firmware. The binary is the exact analysis input, not a new official Roland release. Its header evidence and the distinction between the supplied version and current official distribution are documented in the research reports.

## Material in this repository

| Material | Origin and treatment |
| --- | --- |
| `inputs/MX1_UPD.original.bin` | Unchanged firmware supplied for the investigation; third-party material attributed to Roland. |
| Decoded component binaries, disassembly and decompiler exports | Derived from that firmware. Automatically inferred names/types are analysis output, not recovered original source authorship or a grant of rights. |
| `build/*-probe/*UNTESTED.bin` and patched application binaries | Experimental derivatives containing substantial retained Roland machine code and newly compiled extensions. They remain separately identified research candidates. |
| Project-specific Python tools, C/Thumb extensions, linker scripts, tests and reports | Work developed during this investigation. No license has been chosen for this material; provenance of imported or adapted portions must remain explicit. |
| Toolchains and Python dependencies | External projects with their own licenses and notices. Dependency versions are recorded in `requirements.txt`; installing a dependency does not change the licensing of the firmware it analyzes. |
| Cited manuals, standards, driver sources and related-product evidence | External primary sources identified in the reports. A citation or technical inference does not transfer their ownership to this project. |

Preserve source URLs, author attribution and applicable notices when adding imported material. Do not blanket newly added open-source headers over firmware-derived files. If a future contribution changes the licensing of new project code, keep original firmware, derived exports, complete modified containers and externally sourced material clearly distinguished.

## Frozen snapshot and current development

The initial research import is retained in the preserved baseline branch `research-baseline-2026-11-01`. The original archive-wide `ARCHIVE_MANIFEST.json` and `SHA256SUMS` are stored under `evidence/baseline-2026-11-01/`; their paths and hashes describe that frozen snapshot's original layout. They are not a claim that every file in the evolving repository still has its baseline bytes. See the [evidence note](evidence/baseline-2026-11-01/README.md) for the baseline interpretation and content verification.

Current candidate identities are recorded in `build/host-probe/build-report.json`, `build/device-probe/build-report.json`, and `build/routing-probe/build-report.json`. The builders require the exact input and original patch-site bytes. `tools/reproduce.py` rebuilds the evidence, and `tools/check_reproduction.py --check-committed` compares regenerated binary identities with current evidence, hashes of the actual artifact blobs in Git `HEAD`, and committed build-report hashes. A deliberate change requires review of the new bytes and matching evidence; the historical manifests should not be rewritten to disguise that change.

An embedded Roland version string does not distinguish a patched image from the input. Identify an experiment by its candidate SHA-256, repository commit and build report. Keep the three firmware probes separate and retain their `UNTESTED` filenames until documented physical results justify a changed status.

## Naming and status

Roland, MX-1 and AIRA identify the product and compatibility target. mxplus is not presented as an official Roland release, and no endorsement or affiliation is claimed.

At the initial research baseline, neither candidate had been flashed to an MX-1 or tested for physical USB audio. Instruction-level verification establishes specific software behavior under documented assumptions. It does not establish reliable flash recovery, universal USB Audio Class compliance or working iOS audio. The candidate reports and hardware validation plan retain those limits.
