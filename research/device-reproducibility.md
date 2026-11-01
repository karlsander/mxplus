# Device candidate reproducibility audit

## Observed result

A fresh build in a separate output directory with a separate empty compiler
cache produced byte-identical candidate updater, decoded main application,
compiled extension, and generated descriptor header. This was a real second
compilation, not a copy of the existing outputs.

| Artifact | Bytes | SHA256 |
| --- | ---: | --- |
| Candidate updater | 4,194,320 | `b17f9005dd2b32b9fd89ccdd07c3a2ef0dda0854fb67ad5732a76390cc005d57` |
| Candidate main application | 919,500 | `59bf5d2e7d206315cbc6ae59e8072bff410ea3c2ff850062da5f405148642a9e` |
| Compiled extension | 900 | `9d40e88164364cf4996aed88e65abf870a0258ab6439cbc383891311d6f431e8` |
| Generated descriptor header | 1,814 | `109e8917baf0f80986e89bdb3a0ebf3b2da6fc35271623a7fb2eaf0ffbf5ca27` |

Machine-readable comparison:
`sources/hardware/uac2_reproduction_audit.json`. The audit did not require
re-running a hardware simulation; identical code and data reproduce the
candidate already subjected to the offline verification described below.

## Environment and dependencies

The observed build/test environment was Linux with Python 3.12.14. The native
C test used GCC 13.3.0. The ARM compiler is bundled in the pinned `ziglang`
Python package; a separate `arm-none-eabi-gcc` installation is not required.

| Dependency | Tested version | Use |
| --- | --- | --- |
| Python | 3.12.14 | All command-line tooling |
| `ziglang` | 0.13.0 | Compile/link the new Cortex-M3 Thumb code |
| `capstone` | 5.0.6 | Recover startup relocation maps |
| `pyelftools` | 0.33 | Read symbols and loadable extension bytes from ELF |
| `unicorn` | 2.1.4 | Execute original/patched ARM routines in offline checks |
| C compiler | GCC 13.3.0 observed | Native clock-request test only |

Ghidra, Java, a USB analyzer, a connected mixer, and a proprietary Roland
development kit are not prerequisites for reproducing this particular build
and these offline checks. They serve different analysis or physical
validation roles.

From the project root, create a local environment and install the packaged
requirements:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The device-specific dependency set is exactly:

```text
ziglang==0.13.0
capstone==5.0.6
pyelftools==0.33
unicorn==2.1.4
```

The unchanged input is packaged at `inputs/MX1_UPD.original.bin`. Its expected
SHA256 is
`26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`.
The build rejects a different original. These observations establish
reproducibility with the tested versions, not an assertion that every other
operating system or compiler version produces identical bytes.

## Source files required for a device-only reproduction

Keep these files together with their existing relative paths:

- `patches/uac2_device_probe.c`
- `patches/uac2_device.ld`
- `sources/hardware/uac2_adapter.c`
- `sources/hardware/uac2_adapter_native_test.c`
- `sources/hardware/uac2_pump_harness.py`
- `tools/build_device_probe.py`
- `tools/device_probe_verify.py`
- `tools/container_tool.py`
- `tools/memory_map.py`
- `tools/uac2_design.py`
- `tools/usb_descriptors.py`
- `tools/build_host_probe.py`
- `tools/host_probe_verify.py`

The two host-named modules are genuine import dependencies: the device
builder imports `exact_patch`, and the device verifier imports `Machine`.
They do not cause the device build to modify the host-port application.

The original-decoder/updater candidate check additionally uses
`tools/container_candidate_verify.py`, `tools/container_verify.py`, and
`tools/container_updater_verify.py`.

## Prepare original-image evidence for the pump test

The builder and ARM integration verifier read the original container
directly. The standalone pump harness instead expects two derived files at
fixed project-relative paths:

- `analysis/container_app_main.bin`
- `analysis/map-main.json`

The extractor writes `app_main.bin`; the explicit rename below is required
when recreating this evidence manually:

```bash
.venv/bin/python tools/container_tool.py extract \
  inputs/MX1_UPD.original.bin build/original
mkdir -p analysis
cp build/original/app_main.bin analysis/container_app_main.bin
.venv/bin/python tools/memory_map.py analysis/container_app_main.bin \
  --output analysis/map-main.json
```

The expected decoded main SHA256 is
`256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b`.
The pump harness verifies it before executing the original instructions.
The descriptor-fixture test also uses this file for the exact original MIDI
comparison; without it that test reports a skip, not a successful original
byte comparison.

## Build and verification commands

Build the isolated USB-B candidate:

```bash
.venv/bin/python tools/build_device_probe.py inputs/MX1_UPD.original.bin \
  --output build/device-probe
```

The observed output reports `OFFLINE EXPERIMENT; NOT HARDWARE VALIDATED`,
900 extension bytes, the candidate hash above, and all five guarded patch
sites. The generated `build-report.json` records symbols, relocation changes,
component checksums, and preserved regions.

Execute the original ARM initialization/descriptor/control code with the
compiled extension:

```bash
.venv/bin/python tools/device_probe_verify.py inputs/MX1_UPD.original.bin \
  --build build/device-probe \
  --output build/device-probe/arm-verification.json
```

Observed result: `status: pass`, with eight groups covering startup copies,
initializer and callback setup, 84 positive class-control cases, 10 negative
stall cases, standard descriptor responses, identical original/new hardware
endpoint tables at six rate/speed combinations, initialization failures, and
unchanged backup descriptor/callback tables. Only task creation, hardware
start, and EP0 FIFO reply delivery are stubbed in this check.

Run the original-pump control-flow comparison:

```bash
.venv/bin/python sources/hardware/uac2_pump_harness.py
```

Observed result:

```text
PASS: actual Thumb control flow under a deliberately limited MMIO model
```

Thirteen cases cover original versus modified capture-only, duplex,
stop/restart, playback-then-silence, stereo capture, and both mixed channel
combinations. For the modeled capture-only 18-channel run, original output
is zero IN words/state1; the variant produces 1,494 IN words/state4 and makes
zero OUT reads. Both mixed alternate combinations follow independent channel
branches. Real packet-tail handling is explicitly not certified by this model.

Run the new C request logic's boundary cases:

```bash
gcc -std=c11 -Wall -Wextra -Werror -O2 -DMX1_UAC2_NATIVE_TEST \
  sources/hardware/uac2_adapter.c \
  sources/hardware/uac2_adapter_native_test.c \
  -o sources/hardware/uac2_adapter_native_test
sources/hardware/uac2_adapter_native_test
```

Observed result:

```text
PASS: 4881 EP0 request cases; start ordering and error propagation
```

The separate original-decoder/updater check is invoked as follows; its own
report describes the file/flash/UI stubs and does not claim physical flashing:

```bash
.venv/bin/python tools/container_candidate_verify.py \
  inputs/MX1_UPD.original.bin \
  build/device-probe/MX1_UAC2_DEVICE_PROBE_UNTESTED.bin \
  --output build/device-probe/container-verification.json
```

## Files to retain and conclusions that must stay qualified

Retain the input, source files, build report, candidate binary, decoded patched
main application, extension ELF/code binary, generated descriptor header,
ARM-verification JSON, pump results, native test source, and this reproduction
audit. Compiler caches, Python bytecode caches, and the native test executable
are regenerable. ELF debug bytes may contain paths; the reproduced hashes
above concern the firmware-bearing bytes and generated descriptor header.

The documentation hashes were checked against the actual artifacts. All
portable commands now use a project-local `.venv` and
`inputs/MX1_UPD.original.bin`; they do not depend on the temporary research
workspace's sibling `upload` directory.

The retained caveats are material: clock validity reflects a supported
configured rate, not measured PLL lock; full-speed audio is absent; MIDI
remains vendor-specific; mixed-alternate packet boundaries, sample alignment,
physical capture-first startup, long-running audio, flashing, and recovery
remain unverified. Rebuilding exact bytes and passing the CPU checks do not
remove those limitations.
