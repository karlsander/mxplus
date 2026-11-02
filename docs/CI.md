# Offline continuous integration

The [verification workflow](../.github/workflows/verify.yml) rebuilds the sole
mainline candidate and runs the same offline checks used in the research.
A successful run establishes that the checked-out source, generated firmware,
and recorded hashes agree. It does not establish safe flashing, recovery, USB
enumeration, or working audio on a physical MX-1.

## When and where it runs

There is one job on GitHub's Ubuntu 24.04 x64 runner, using CPython **3.12.14**
and the exact package versions in `requirements.txt`. It runs on pushes to
`main`, pull requests, and manual dispatch from the Actions tab. A newer run
for the same branch or pull request cancels the older one. The job has a
15-minute timeout.

The workflow grants only `contents: read`, does not retain checkout credentials,
and uses the normal `pull_request` event. It does not request repository secrets
or publish releases. There is no schedule, matrix, firmware flashing, USB access,
configfs setup, package-manager system configuration, or automatic artifact
upload. A pip download cache is keyed by `requirements.txt`; compiled firmware
and verification outputs are regenerated on the runner.

“Offline” describes the reproduction and verification stages. GitHub needs
network access to fetch the repository, actions, Python, and pinned packages
before those stages. The verification tools operate on local files and explicit
CPU/peripheral models. Ghidra is not required or rerun in CI; its supplied
exports remain analysis evidence.

## Exact checks

The job runs:

```sh
python -m pip install --requirement requirements.txt
python tools/reproduce.py
python tools/check_reproduction.py --check-committed
```

`tools/reproduce.py` checks the exact original firmware, extracts its programs,
then runs these 17 stages in order:

1. `map-main`
2. `map-usb`
3. `map-updater`
4. `container_verify`
5. `container_updater_verify`
6. `container_binding_verify`
7. `usb-descriptor-scan`
8. `descriptor-tests`
9. `bridge-plan-tests`
10. `build-mainline`
11. `arm-mainline`
12. `container-mainline-candidate`
13. `boot-mainline`
14. `original-audio-pump`
15. `compile-native-controls`
16. `native-controls`
17. `subcpu-evidence`

The `arm-mainline` stage includes finite-packet playback/capture and alternate
transition tests. The final gate also requires `packet-verification.json` to
pass and identify the actual current application hash.

The final gate requires the complete ordered pipeline and compares the one
mainline container, decoded application and load-image blob against both current
reports and actual committed artifact bytes. It also checks the unchanged
original firmware. All USB/routing verification runs against the combined
candidate. Historical separate targets are not built or published.

The actual committed artifacts and their reports form the baseline. Updating
only a report's hash while leaving a stale binary committed therefore fails,
even if the local rebuild matches that new hash. There is no permanently
hardcoded old candidate hash: an intentional firmware change should rebuild
and commit the new candidate and
its matching evidence together. A shallow checkout is sufficient because the
comparison reads files from `HEAD`, not previous history. On a pull request,
the normal checkout tests GitHub's proposed merge revision.

This is a targeted byte-reproducibility check. Timestamps, elapsed timings,
absolute paths, and ELF debug metadata are not compared byte for byte. The
hosted runner image and its native C compiler can also change. The meaningful
invariants are the firmware/code bytes, their recorded hashes, and the executed
verification results.

## Reproduce locally and diagnose a failure

On a Linux x64 system with Git, Python 3.12, and `gcc`, create a project
environment and install the pinned requirements:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --requirement requirements.txt
.venv/bin/python tools/reproduce.py
.venv/bin/python tools/check_reproduction.py --check-committed
```

Use Python 3.12.14 to match CI exactly. The reproduction script writes
`analysis/reproduction.json` and one log per stage under
`build/reproduction-logs/`. A failed stage prints the end of its log in the
Actions job output; start with that error and the named stage. The consistency
checker reports missing, failed, or mismatched evidence separately.

When firmware source intentionally changes, first run reproduction and inspect
the resulting candidates, hashes, and reports. Running the checker without
`--check-committed` checks current evidence before a commit. Include the reviewed
new candidates and matching evidence in the change, then rerun
`--check-committed` against that commit. An unexpected mismatch should be
investigated instead of accepted merely to make CI pass.

The workflow does not upload new firmware artifacts. The tracked experimental
images remain reviewable in the repository, and CI logs are available in the
Actions run. A passing badge is an offline verification result, not a hardware
compatibility certification. Physical testing follows
[the hardware validation plan](HARDWARE_VALIDATION.md).

## Verified action pins

The workflow pins official actions to full commit hashes rather than movable
version tags. Their release pages link to these commits; the action metadata at
each pinned commit was also read through GitHub's repository API.

| Action | Release | Pinned commit |
|---|---|---|
| `actions/checkout` | [v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1) | [`3d3c42e5aac5ba805825da76410c181273ba90b1`](https://github.com/actions/checkout/commit/3d3c42e5aac5ba805825da76410c181273ba90b1) |
| `actions/setup-python` | [v7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0) | [`5fda3b95a4ea91299a34e894583c3862153e4b97`](https://github.com/actions/setup-python/commit/5fda3b95a4ea91299a34e894583c3862153e4b97) |

Both actions use Node 24, supplied by GitHub's hosted runner. The official
[Python distribution manifest](https://github.com/actions/python-versions/blob/main/versions-manifest.json)
lists the stable [3.12.14 distribution](https://github.com/actions/python-versions/releases/tag/3.12.14-31661455385)
for Ubuntu 24.04 x64. When updating these pins, verify the new official release
and full commit, update the accompanying comments, and rerun the same checks.
