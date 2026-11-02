# mxplus

One MX-1 firmware build: channel routing, internal noise/bass drum sources and experimental USB-B UAC2 audio.

**The routing predecessor, including encoder end stops, passed the user's bench
test. The combined mainline image has not yet been tested on hardware.** USB-B
class-driver enumeration/audio and failed-application recovery remain unverified.
The word mainline identifies the maintained build, not a certification of safety.

## Build and verify

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/reproduce.py
.venv/bin/python tools/check_reproduction.py --check-committed
```

The sole update artifact is
[`build/mainline/MXPLUS_MAINLINE_UNTESTED.bin`](build/mainline/MXPLUS_MAINLINE_UNTESTED.bin).
The sole builder is `tools/build_firmware.py`; no feature-selection build flags
or separate host/device/routing firmware targets are maintained. Its adjacent
`build-report.json` records exact input/output identities, patches, relocation
and code/data placement. The verifier checks the combined image, not a mixture
of reports for different firmware variants.

The immutable original `inputs/MX1_UPD.original.bin` remains the required input:
SHA-256 `26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`.
The original is not an alternative maintained custom firmware.

## Features

- Press an already selected strip's SELECT to toggle source editing (blinking)
  and normal editing (steady). TEMPO chooses the source; the menu stops at
  `Auto` and `BD`. Holding SELECT + TEMPO also works. Routes save with mixer snapshots and restore after restart. See [routing](docs/CHANNEL_ROUTING.md).
- `NSE` generates white noise; `BD` provides a per-strip 16-step bass drum
  pattern. Patterns are currently RAM-only. See [internal sources](docs/INTERNAL_SOURCES.md).
- USB-B advertises UAC2 audio with stereo and 18-channel alternates. The mixer
  selects the fixed rate; USB MIDI remains proprietary. See [USB audio](docs/DEVICE_PROBE.md).
- AIRA USB1–4 retain the original firmware implementation. The generic-host
  unlock was retired: [research record](docs/HOST_PROBE.md). No host unlock code
  or buildable host candidate remains in the current tree.

[Mainline integration](docs/MAINLINE.md) documents memory reservations and the
bench test plan. [CI](docs/CI.md), [contribution rules](CONTRIBUTING.md),
[roadmap](ROADMAP.md), and [hardware validation](docs/HARDWARE_VALIDATION.md)
explain evidence and boundaries. Reports in `research/` and `evidence/` retain
historical findings and identities; retired source/artifacts are recoverable
from Git history rather than maintained as parallel firmware builds.

This is independent research, with no Roland endorsement. No project-wide
license has been selected; see [PROVENANCE.md](PROVENANCE.md).
