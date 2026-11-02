# mxplus

One Roland MX-1 firmware build: channel source routing, routing snapshots and
restart persistence, and experimental USB-B UAC2 audio. USB1–4 stay stock.

The maintained image restores the pre-generator firmware (`88457445…`). The
user confirmed normal boot and an analog-input → iPhone/AUM effect → another
MX-1 channel audio round trip with a direct USB-B–USB-C cable. Routing and
encoder end stops were also tested in its predecessor. See the
[hardware record](evidence/iphone-aum-20261102/README.md) for limitations.
This is experimental firmware, not a certified safe or universally compatible
upgrade. Snapshot/restart persistence still needs its physical acceptance test.

## Controls

Hold a destination strip's **SELECT** and turn **TEMPO** to choose its source.
The menu stops at **Auto** and **P9 R**. Release SELECT to return to ordinary
controls. SELECT taps and the no-channel-selected view retain Roland behavior.
Routes use the stock snapshot and delayed system-save paths; no extra autosave
routine is added. [Routing instructions](docs/CHANNEL_ROUTING.md) include the
analog 5/6 split and [storage details](docs/ROUTING_STORAGE.md) explain persistence.

USB-B advertises stereo and 18-channel UAC2 alternates at the mixer-selected
sample rate. MIDI remains proprietary. See [USB audio](docs/DEVICE_PROBE.md).

Generators, the blinking SELECT edit mode and generic USB-host unlocking are
retired. Their findings are documentation only:
[generator/DSP handoff](docs/GENERATOR_RESEARCH.md), [host research](docs/HOST_PROBE.md).

## Build and verify

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/reproduce.py
.venv/bin/python tools/check_reproduction.py --check-committed
```

The sole update artifact is
[`build/mainline/MXPLUS_MAINLINE_UNTESTED.bin`](build/mainline/MXPLUS_MAINLINE_UNTESTED.bin).
`tools/build_firmware.py` and `patches/mainline.ld` define the only maintained
build. The adjacent build report records input/output identities, exact patch
bytes and placement. There are no feature-selection flags or parallel builds.

Keep `inputs/MX1_UPD.original.bin` unchanged. Its SHA-256 is
`26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`.

[Integration](docs/MAINLINE.md), [review](docs/MAINLINE_REVIEW.md),
[CI](docs/CI.md), [contributing](CONTRIBUTING.md), [roadmap](ROADMAP.md) and
[hardware validation](docs/HARDWARE_VALIDATION.md) describe evidence and limits.
Historical reports remain in `evidence/`; retired source/artifacts are in Git
history. This is independent research with no Roland endorsement or
repository-wide license; see [provenance](PROVENANCE.md).
