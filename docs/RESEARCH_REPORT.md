> Historical investigation: standalone build paths refer to Git history. The only active firmware is [mainline](../docs/MAINLINE.md). Historical evidence has not been rewritten as combined-image evidence.

# Roland MX-1: firmware reconstruction and USB expansion research

**Investigation date: 1 November 2026.** This report concerns the exact original firmware supplied for this investigation. It records working offline tools and two compiled firmware experiments, alongside the evidence needed to assess their limits.

The later [channel-routing experiment](CHANNEL_ROUTING.md) is documented
separately. It adds SELECT + TEMPO source assignment and a third independent
candidate; the current reproduction pipeline covers all three in 22 stages.

## 1. Outcome

The supplied firmware can be unpacked, inspected, modified and rebuilt. Its compressed programs are now decoded, its relevant runtime memory maps are reconstructed, and selected original ARM routines have been executed against newly compiled extensions. Two complete experimental update images have been produced:

| Objective | Implemented result | Status |
| --- | --- | --- |
| Connect a class-compliant device to USB1–4 | A new UAC1 classifier and selection path for a tightly constrained high-speed stereo profile | Compiled and tested through the original parser and selection code; physical transfers untested |
| Use MX-1 as an iOS audio interface | A USB-B UAC2 configuration, standard fixed-clock controls and a capture-startup modification | Compiled and tested through original USB initialization, dispatch and descriptor code; iOS enumeration and audio untested |
| Keep the original firmware while pursuing iOS use | A Linux host/UAC2-gadget bridge implementation and setup plan | Dry-run and direction tests pass; requires suitable physical hardware |

**Neither modified image has been flashed to an MX-1. No claim of working iOS audio, successful generic-device audio, safe flashing or recovery is made.** The result is substantially beyond a descriptor proposal: it includes new compiled machine code, guarded builders, rebuilt update containers, original-instruction tests, disassembly and decompiler exports. Physical USB behavior is the next decisive boundary.

The USB-B route is the stronger native path to pursue first. The host-port route has more remaining format, scheduling and clock constraints. A Linux bridge offers a separate route that can be investigated with the original mixer firmware.

## 2. Which port should do what?

Roland documents four Type-A USB host connectors and one Type-B computer connector. The computer interface supports 18 input and 18 output channels, 24-bit audio, and 44.1/48/96 kHz over high-speed USB. Bus power is advertised for host port 3. [1]

| Connection | MX-1 role | Attached equipment role | Appropriate development target |
| --- | --- | --- | --- |
| USB1–4 Type-A → audio instrument/interface | USB host | USB audio device | Generalize the mixer’s host-side audio driver |
| iPhone/iPad → MX-1 Type-B | USB audio device | USB host, using a suitable data connection/adapter | Make the existing MX-1 device stack present standard USB Audio Class behavior |
| Linux host → MX-1 Type-B | USB audio device | Host with Roland compatibility support | Keep stock MX-1 firmware and translate audio through Linux |

The iOS objective does not require turning a Type-A connector into a device port. Type-B already occupies the role needed when the iPhone or iPad is the host. Reversing a Type-A port would require proof of controller role capability, PHY wiring and power-switch behavior that the current evidence does not supply. An ordinary hub does not translate a proprietary audio protocol into a class-compliant one.

The “AIRA only” description is also incomplete historically. Roland added several other Roland instruments in later firmware updates, with version 1.05 adding SYSTEM-8 in September 2016. This demonstrates a software compatibility policy, but it does not establish generic UAC support. [2]

## 3. Firmware structure and rebuild path

### Exact input

The original file is 4,194,320 bytes: a 4 MiB image plus a 16-byte update trailer. Its SHA-256 is:

```text
26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e
```

Both application headers contain build label `1.051132` and timestamp `16-0906_11:04:55`. The updater and panel image have their own version labels. The two boot programs are different programs, rather than identical backup copies.

| Embedded program | Header offset in supplied file | Decoded program bytes | Initial load address |
| --- | --- | ---: | --- |
| Main boot | `0x000000` | 10,732 | `0x01000000` |
| USB boot | `0x008000` | 4,160 | `0x01000000` |
| Updater | `0x010000` | 182,828 | `0x60000000` |
| Panel/sub-CPU | `0x040000` | 16,404 | `0x08000000` |
| Main application | `0x080000` | 918,600 | `0x60000000` |
| USB-host application | `0x200000` | 224,868 | `0x60000000` |

The updater and two large applications use LZSS compression. The implementation uses a 4,096-byte ring, an initial write cursor of 4,078, least-significant-bit-first flags, and 3–18-byte back references. A significant detail is that the initial ring prefix is zero-filled; a common space-filled LZSS implementation produces incorrect output. The last 18 ring bytes are not initialized until written. The Python decoder reproduces the actual boot decoder’s output for all three programs. Modified and resized application fixtures also decode correctly through the original ARM routine. Malformed-stream rejection tests exercise the Python tool's additional validation; they do not establish that the original boot decoder safely rejects the same malformed inputs.

The four checksums in the updater, sub-CPU and application component headers are 32-bit sums of stored payload bytes, excluding their headers and padding. The two boot headers use a different layout; their remaining unknown fields are preserved. The container tool performs a byte-identical no-change rebuild and can encode modified applications. The current encoder uses literal-only LZSS: this is valid but larger than the original compressed representation. Both candidates fit the actual writable slots.

### Runtime addresses matter

The main and USB applications begin at `0x60000000`, then execute startup copy/zero routines. Their hot code moves into private SRAM at `0x01000300`; initialized data moves separately, and source storage in SDRAM is later cleared. Treating every decompressed byte as permanently resident at its load address produces wrong cross-references.

The main hot-code copy is 62,372 bytes; the USB copy is 48,100 bytes. The new extension code is inserted immediately after the appropriate hot section in the load image. The builder extends that startup copy and advances later initialized-data source addresses. Existing runtime addresses remain fixed.

The host extension occupies `0x0100bee4..0x0100c350`, end exclusive. Review identified real allocator reservations beginning at `0x0100d000`, so the linker and builder enforce that earlier bound. The main extension occupies `0x0100f6a4..0x0100fa28`; initialized data begins at `0x01010000`. No equivalent reservation or direct reference was found in that main-core gap, but bounded static review cannot exclude every computed pointer or hardware use.

### What the updater actually writes

The trailer selects blocks 64 through 767 inclusive, each 4,096 bytes. The original updater consequently writes 704 blocks in `[0x40000, 0x300000)`. This preserves the two boot programs and updater below `0x40000`, and the upper MiB beginning at `0x300000`. The host application’s usable slot ends at `0x300000`, even though the distributed image is larger.

The actual original trailer parser, component-tag check, write/readback loop and post-write checksums have accepted both final candidates in an in-memory harness. File and flash operations are explicit stubs; the address arithmetic, loop, comparisons and checksums execute as original ARM instructions.

No signature or version comparison was identified in the traced update-writer path. This is a statement about that path, not every possible immutable boot or recovery mechanism. More importantly, application checksums are verified after writing. Preserved boot bytes and correct checksums do not prove that a broken application can be recovered on real hardware. Recovery-looking filenames in the binary are clues, not an established rescue procedure.

Evidence: `research/container.md`, `analysis/container_manifest.json`, `analysis/container_verification.json`, `analysis/container_updater_verification.json`, and both candidate-verification reports.

## 4. Decompilation methods and what “recompile” means here

The investigation combined container reconstruction, direct Capstone disassembly, Ghidra analysis with corrected runtime maps, and Unicorn execution of selected original functions. New C and Thumb assembly were compiled with Zig/Clang for Cortex-M3, linked into bounded SRAM regions, and inserted with exact-byte patch guards.

The Ghidra exports contain 3,929 main-application functions, 1,392 USB-host functions, 1,630 updater functions and 171 panel-controller functions: 7,122 records total. All exported functions completed the tool’s decompilation step, but that does not certify their types, boundaries or interpretation. Some routines carry warnings, and automatic discovery missed at least one important task without a conventional prologue. That task was separately traced in assembly and exercised in the binding harness.

The result is **a reproducible binary-extension build**, not recovered original Roland source. The automatic C-like output is useful for navigation and analysis; it is not a complete source tree that can be compiled into the original product. The builders compile only the new extensions and preserve the bulk of the original machine code.

This distinction is practical: it permits narrow feature changes now while avoiding a premature rewrite of the proprietary RTOS, DSP, USB and peripheral support. It also limits confidence in broader changes and makes exact version matching essential.

Evidence and commands: `docs/DECOMPILATION.md`, `tools/MX1Map.java`, `tools/MX1Export.java`, `tools/memory_map.py`, the exported function/reference indexes, and `requirements.txt`.

## 5. USB1–4: restrictions found and the implemented experiment

### Two policy barriers, followed by transport constraints

The original USB audio driver registration is wildcard: its match flags impose no earlier vendor or interface-class filter. The original binder accepts a non-Roland/class-1 fixture and calls the audio probe. The rejection happens later.

The interface classifier at `0x6000a11e` expects vendor class `0xff` and Roland’s direction/protocol conventions. Standard UAC1 streaming interfaces use class 1 and protocol 0, so they fail that classification. The application policy at `0x60007bf8` independently requires Roland vendor ID `0x0582`, along with rate, alternate and sample-layout constraints.

Changing the vendor ID check alone therefore does not create a generic audio driver. Even after descriptors are admitted, the transport expects particular packet layouts, high-speed microframe scheduling and clock behavior. The identified engine uses EHCI isochronous transfer descriptors, two per device and eight microframes per descriptor. It assumes four-byte samples and a specific stereo-oriented path. No general explicit-feedback engine or standard endpoint sample-rate SET_CUR path was found in the traced setup path.

### Implemented host profile

The new 1,132-byte extension hooks the classifier, configuration parser and selection policy. Existing Roland vendor descriptors go through a trampoline into original instructions, and Roland vendor-ID policy delegates to the original routine. Generic admission is limited to:

- High speed as reported by the original stack; a full-speed fixture is rejected at selection.
- Standard UAC1 AudioStreaming class/subclass/protocol.
- A validated inactive alternate 0 and active alternate 1 in each direction, designed for separate IN and OUT streaming interfaces.
- Stereo linear PCM, 24 significant bits in four-byte containers.
- One fixed advertised rate: 44.1, 48 or 96 kHz; both directions must agree.
- One supported asynchronous isochronous data endpoint per active interface, a 125-microsecond service interval and adequate packet headroom.
- No explicit-feedback endpoint, generic MIDI, multichannel selection or variable-rate negotiation.

This is a deliberately narrow enumeration and selection experiment. Many common class-compliant devices are full-speed, use packed 24-bit or 16-bit samples, advertise multiple rates, implement UAC2, or need explicit feedback. They remain unsupported.

The high-speed restriction is enforced in the selection path: original routine `0x60008580` converts the USB-stack speed field at device offset `0x58` into the boolean at `info+8`, and the new policy requires that boolean to be one. The test changes the field from high-speed value `0x400` to full-speed value `0x200` while retaining the same descriptors and observes rejection. Descriptor classification alone is independent of bus speed.

The implemented endpoint attributes are `0x05` for OUT and `0x05` or `0x25` for IN. Packet capacity must be at least 56 bytes at 44.1/48 kHz or 104 bytes at 96 kHz, and at most 1,023 bytes. The wrapper also limits configurations to 4,096 bytes and interface numbers to 0–7. These checks do not constitute a complete AudioControl or descriptor-topology validator; the accepted fixtures exercise the selected streaming path. `docs/HOST_PROBE.md` records the remaining parser limits.

Review found and fixed several concrete weaknesses: a memory bound that would have allowed overlap with USB allocator blocks; vendor-class descriptors bypassing the standard-format checks; a later descriptor overwriting a validated alternate while retaining its marker; and duplicate active alternates imitating the required inactive/active pair. The final implementation tracks the origin of selected records and rejects these cases.

### What passed

Ten host verification groups pass. They execute startup copies, hooks, original parser, original stream-summary builder and replacement policy. Positive fixtures at all three rates reach selection. Twenty unsupported format/speed/endpoint/alternate cases remain unselected. The embedded Roland descriptor fixture keeps identical classifier behavior. Register and stack preservation is checked across seven relevant paths.

The exact final update image also passes the original decoder and updater harness. None of these tests executes the host controller against a physical audio device. Successful selection is a prerequisite to streaming, not evidence of stable audio.

The next host-side work should begin with a device whose descriptors actually match the narrow profile. A bus trace then needs to establish interface setup, packet production/consumption, IN-to-OUT clock behavior and disconnect/reconnect. Broader support should be added one format or clock mechanism at a time after the transport is understood.

Evidence: `docs/HOST_PROBE.md`, `research/container-binding.md`, `research/usb-compatibility.md`, `patches/uac1_host_probe.c`, `analysis/host_probe_verification.json`.

## 6. USB-B: implemented UAC2/iOS experiment

### Existing capability and missing class behavior

The original Type-B configuration uses Roland vendor-class interfaces. It already contains the audio endpoints and alternate modes needed for 18-channel and stereo operation, but its presentation and control protocol are not a normal UAC2 device.

The new 900-byte extension creates a 355-byte UAC2 configuration with AudioControl and two AudioStreaming interfaces, a shared fixed clock and standard terminal links. It retains the existing hardware-facing modes:

| Direction relative to computer/iOS | Interface | Active alternate | Channels | Endpoint |
| --- | ---: | ---: | ---: | --- |
| Playback to mixer | 1 | 1 | 18 | `0x0d` OUT |
| Playback to mixer | 1 | 2 | 2 | `0x0d` OUT |
| Capture from mixer | 2 | 1 | 18 | `0x8e` IN |
| Capture from mixer | 2 | 2 | 2 | `0x8e` IN |

The original vendor MIDI interface 3 is retained byte for byte outside the audio interface association. The device and qualifier class fields are updated consistently with the association descriptor. The USB-IF specification permits different channel clusters across streaming alternate settings; the descriptor graph was audited against that requirement. [3]

### Clock controls

The mixer’s existing 44.1/48/96 kHz setting determines the rate. The extension reports that current rate through standard CUR and RANGE requests, handles short range-header probes and clock-validity queries, and stalls unsupported writes or malformed requests. It recalculates the original endpoint packet maxima for the selected rate instead of exposing a stale 96 kHz template.

The clock is intentionally read-only. Software on the iPhone/iPad does not gain authority to change the mixer’s hardware rate during a session. Clock validity currently means that the configured rate is supported; it is not a measurement of PLL lock. MIDI remains proprietary, and the stock full-speed descriptor remains an empty vendor configuration with no audio endpoints. This experiment attempts high-speed audio only.

### The important startup problem

The original endpoints use implicit feedback: the input stream supplies timing information that can govern the asynchronous output stream. Apple documents that its driver waits for consistent IN timing before transmitting OUT data. [4]

The original MX-1 audio pump has the opposite startup dependency in two state transitions: it waits for playback availability before advancing capture startup. That can create a deadlock with an input-first host. Linux’s Roland handling includes special implicit-feedback and playback-first behavior, supporting the interpretation that this is a real protocol distinction rather than a cosmetic descriptor issue. [5]

The relevant instruction is at runtime `0x01009a06`. The prototype changes `mov.w r12,#0` to `mov.w r12,#1` on the no-OUT branch. Other priming, IN-readiness, phase and commit checks remain. The playback path still supplies silence when no OUT data exists.

The original Thumb pump was executed with an explicit model of readiness and phase inputs. The stock capture-only case stays in startup state 1 with no IN writes. The candidate reaches normal state 4 and produces capture without OUT FIFO reads. Duplex traces are unchanged; stop/restart, stereo and mixed 18/2-channel branches were also exercised. This model does not prove that the physical ESC2 USB hardware produces the same readiness conditions without preceding OUT traffic.

### Integrated checks

Eight actual-ARM integration groups pass, including 84 positive clock-control cases, 10 negative request cases, startup relocation, callback registration, original control dispatch, descriptor and other-speed reads, initialization failures and backup descriptor/callback equality. An independent native C harness passes 4,881 boundary and request cases.

A useful result is that the original descriptor walker produces identical endpoint hardware-table writes from the old vendor descriptors and the new UAC2 descriptors at all three rates and both speed selections. This supports preserving the existing endpoint engine. It does not substitute for enumeration or audio measurements.

An independent fresh build with a separate compiler cache reproduces the candidate and extension bytes. The exact image passes the original decoder/updater harness.

### Remaining platform and hardware limits

The decisive first measurement is a capture-first bus trace: does the mixer supply stable IN packets before any OUT packets? Next come sample alignment, channel mapping, packet-length boundaries, long-running clock behavior, resets and all rate/alternate combinations. Mixed-alternate code branches are independent, but the original OUT tail bookkeeping subtracts 72 bytes even in stereo; the simplified pump model does not certify real mixed-mode packet boundaries.

The prototype is oriented toward Apple’s implicit-feedback behavior. Microsoft explicitly states that its inbox UAC2 driver does not support implicit feedback for asynchronous OUT. This build should not be advertised as universally class-compliant across host operating systems. [6] It also retains Roland’s VID/PID; an installed Roland driver or a cached device binding can affect Mac testing and must be controlled when interpreting results.

Evidence: `docs/DEVICE_PROBE.md`, `research/device-control.md`, `research/uac2-descriptor-audit.md`, `build/device-probe/arm-verification.json`, the native C harness and `sources/hardware/uac2_pump_harness_results.json`.

## 7. Internal hardware: confidence levels

| Finding | Confidence and evidence |
| --- | --- |
| ESC2-family main/USB software platform | Strong software evidence from firmware strings, peripheral code and separate boot/application layouts |
| Separate main and USB execution contexts | Strong: distinct programs, startup maps and private runtime addresses; not a physical package count |
| Cortex-M3 panel/sub-CPU in STM32F100 family | Very strong firmware identification: vectors, reserved IRQ pattern, GPIO/peripheral accesses on the recovered startup path and clock initialization |
| STM32F100V8 or STM32F100VB, LQFP100 | Strong candidate: GPIOA–E usage and memory footprint; exact chip marking and density unverified |
| Nominal 24 MHz panel clock | Strong firmware-based inference from the HSE constant and clock setup; physical frequency has not been measured |
| USART1 at 62,500 baud, 8N1 on PA9/PA10 | Recovered configuration; likely panel communication, but the physical peer/net is unverified |
| Exact main ESC2 package count and part marking | Unknown |
| External RAM, flash, converters, power switches and board nets | Not established from a public MX-1 schematic or internal photograph |

The panel image is 16,404 bytes. Its reset vector, STM32F1 peripheral bases, TIM1/TIM16 interrupt position and USART1 interrupt handler distinguish it from a generic ARM guess. It uses more than a 4 KiB SRAM layout, and live GPIOE usage supports a 100-pin medium-density STM32F100 candidate. ST’s documentation provides the comparison, while the identification itself comes from this binary. [7]

A related Roland service document identifies ESC2 as MB8AA4181. That is useful context, not proof of the MX-1’s exact package. No trustworthy MX-1 board photograph, service schematic or BOM was located during this investigation. The 4 MiB update image and observed address ranges must not be presented as measured physical flash or RAM capacities.

The hardware report includes GPIO direction masks, peripheral addresses, initialization functions and interrupt vectors. It provides a concrete starting point for board photographs, chip marking checks and non-invasive UART/USB observation without inventing a full schematic.

Evidence: `research/hardware.md`, `sources/hardware/subcpu_evidence.json`, `sources/hardware/subcpu_selected.asm`, and the panel decompiler export.

## 8. A route using the original firmware: Linux bridge

Linux contains Roland-specific USB-audio handling that understands vendor interfaces and their clock/startup quirks. A suitable Linux system can therefore be investigated as a host for the stock MX-1, while a separate USB device controller on that system presents a standard UAC2 gadget to iOS. Linux configfs supplies the gadget mechanism. [5, 8]

The required topology is:

1. MX-1 Type-B connects to a Linux USB host controller.
2. A separate Linux USB device-controller connection goes to iPhone/iPad acting as host.
3. Software moves audio in both directions between the two ALSA devices.

| Audio path | Linux routing |
| --- | --- |
| iOS playback to MX-1 | Gadget ALSA capture → MX-1 ALSA playback |
| MX-1 recording into iOS | MX-1 ALSA capture → gadget ALSA playback |

Two connectors alone are insufficient: the Linux board needs usable host and device-controller roles simultaneously. A charging-only connector is not a UDC. The bridge also has independent clocks, so it needs drift correction/resampling and sensible buffering; merely opening two PCM devices at “48 kHz” does not make their clocks identical.

`tools/linux_bridge.py` is read-only by default and prints discovery, configuration or route plans. Applying system changes requires its explicit `--apply` flag. It includes stereo and multichannel plans, real card-ID validation, direction checks and a power-mode requirement. Five tests check the generated operations and safeguards. The accompanying report supplies exact setup, route, teardown and logging commands, including libsamplerate requirements.

This bridge has not been assembled or audio-tested in this session, so no particular board, latency or compatibility is promised. It is nevertheless a useful next experiment because it leaves the MX-1 firmware unchanged and builds on existing Linux host support.

There is also a stock-routing possibility for the host-channel objective: Roland documents that computer audio can be assigned to USB1–4 strips when no instrument is attached to those ports. A computer/Linux host could receive generic USB instruments and route their audio to those existing returns. That would use the desired mixer strips without making the four physical AIRA ports generic. It is a separate routing option, not implemented by the native host patch. [1]

Evidence: `research/linux-bridge.md`, `tools/linux_bridge.py`, `tools/linux_bridge_test.py` and `docs/HARDWARE_VALIDATION.md`.

## 9. What is ready for continuation

The archive is self-contained for this firmware revision: original input, source, linker scripts, compiled extensions, separate candidate images, maps, descriptor extractions, decompiler exports, reports and test evidence are included. Toolchain binaries and compiler/Ghidra caches are excluded. Pinned Python dependencies and a single offline reproduction script rebuild and verify the work.

| Candidate | SHA-256 |
| --- | --- |
| UAC1 host probe | `516fc0a3baeaf179e018d7eff2eba376ba21eaed8b9e43a9b9860dce6f45dd58` |
| UAC2 device probe | `b17f9005dd2b32b9fd89ccdd07c3a2ef0dda0854fb67ad5732a76390cc005d57` |

Both are 4,194,320-byte update containers. The host candidate changes only the USB application; the device candidate changes only the main application. Keeping them separate makes subsequent failures attributable. The authoritative regenerated hashes are in each `build-report.json` and the corresponding decoder/updater verification report.

The next work should proceed in this order:

1. Record stock descriptors, rates, channels and packet behavior; verify the exact mixer revision and the intended attached devices.
2. If suitable hardware is available, validate the Linux bridge with original firmware, first at stereo/48 kHz and then with the required channels and rates.
3. Establish a documented recovery-capable bench before experimental firmware installation. The present evidence is not sufficient to promise recovery.
4. Test the USB-B candidate separately, starting with enumeration and real IN-before-OUT behavior; then verify stereo, multichannel, rate changes across restarts, channel/sample correctness and long runs.
5. Test the host candidate against an exact matching descriptor profile; measure its real scheduling and clock behavior before widening supported formats.

`docs/HARDWARE_VALIDATION.md` explains the logs and traces needed at each stage. It distinguishes an application opening capture from actual IN-first traffic on the wire, and notes that computer-side usbmon cannot observe the MX-1 acting as host on its separate USB1–4 connectors.

The most valuable next evidence is physical: a board identification/recovery assessment, original USB descriptor dumps for the specific devices to be supported, and a capture-first trace from the USB-B experiment. Further broad decompilation alone would not resolve those hardware questions.

## Primary references

1. [Roland MX-1 product and specifications](https://www.roland.com/global/products/mx-1/). Port roles, computer-channel capacity, advertised bus power and computer-return routing.
2. [Roland MX-1 System Program 1.05](https://www.roland.com/global/support/by_product/mx-1/updates_drivers/82415302-0466-4c5c-be4e-138a8946d4a7/). Version history and official update procedure/cautions.
3. [USB-IF Audio Device Class 2.0 specification, with errata](https://www.usb.org/sites/default/files/Audio2_with_Errata_and_ECN_through_Sep_14_2026.pdf). Audio graph, interface association and alternate-channel-cluster requirements, especially §3.13.1.1.
4. [Apple TN3190: USB audio device design considerations](https://developer.apple.com/documentation/technotes/tn3190-usb-audio-device-design-considerations). Implicit feedback and input-before-output startup expectations.
5. [Linux USB audio implicit-feedback implementation](https://github.com/torvalds/linux/blob/master/sound/usb/implicit.c). Roland-specific endpoint matching and startup handling. See the USB research report for related primary Linux source files.
6. [Microsoft USB Audio 2.0 drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/audio/usb-2-0-audio-drivers). Explicit-feedback requirement for asynchronous OUT in the inbox driver.
7. [ST STM32F100x4/x6/x8/xB datasheet](https://www.st.com/resource/en/datasheet/stm32f100c4.pdf) and [ST STM32F100xB startup template](https://github.com/STMicroelectronics/cmsis-device-f1/blob/master/Source/Templates/gcc/startup_stm32f100xb.s). Panel-family comparison evidence.
8. [Linux USB gadget configfs documentation](https://www.kernel.org/doc/html/latest/usb/gadget_configfs.html). Gadget configuration and device-controller requirements.

Firmware-derived findings are supported by the supplied original binary and the local source/evidence files named in each section. Hypotheses and hardware limitations are identified explicitly throughout the report.
