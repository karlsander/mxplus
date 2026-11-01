# mxplus roadmap

The first investigation produced reproducible binary analysis and two compiled, offline-verified USB experiments. A separate channel-routing experiment now extends that work. Physical evidence remains necessary for all three. This roadmap sets milestones and exit criteria; it does not promise dates or imply that an untested feature already works on a mixer.

The [research report](docs/RESEARCH_REPORT.md) explains the original conclusions, with the [routing report](docs/CHANNEL_ROUTING.md) covering the follow-up. [docs/HARDWARE_VALIDATION.md](docs/HARDWARE_VALIDATION.md) supplies the staged bench plan. Keep the USB1–4, USB-B and routing experiments separate while establishing their behavior.

## 1. Preserve a reproducible research baseline

**Present result:** all six embedded programs are extracted; container structure, runtime maps and selected original ARM paths are understood. All three firmware experiments rebuild with exact-input and exact-patch guards. The offline runner records 22 stages, and the committed-evidence check binds regenerated binary identities to both the actual committed artifact files and reviewed build reports.

**Next work:** maintain those guards and evidence as changes arrive, add real descriptor captures as fixtures, and resolve new discrepancies before changing an expected result. Keep the original input and frozen archive manifests intact. Optional Ghidra annotation can improve function names and analysis without pretending the exports are complete source code.

**Exit criterion for each change:** a reviewer can identify the input, every changed byte range, relevant runtime addresses, the exact candidate and the tests that apply to it. All claimed results refer to that candidate or are explicitly labeled historical.

## 2. Establish the stock hardware and USB baseline

**Present result:** software identifies the ESC2 family and supports a strong STM32F100 panel-controller identification. Main-board package count, exact memory/codec parts, electrical connections and a failed-update recovery procedure remain unverified.

**Next work:** collect stock live descriptors and audio behavior at 44.1, 48 and 96 kHz; record host driver binding and known-good Roland/AIRA transactions. Obtain legible MX-1 board photographs and part markings where accessible. Relate each observed component to the binary evidence without promoting related-product schematics into an MX-1 bill of materials.

**Exit criterion before experimental installation:** a documented device-specific recovery route, identified hardware and power arrangement, preserved original/settings, and an exact candidate with passing offline evidence. Ordinary update mode and intact boot bytes alone do not satisfy this milestone. Stock descriptor captures and external-bridge work can proceed independently of installing a candidate.

## 3. Validate USB-B UAC2 behavior on a physical mixer

This is the most developed native class-driver experiment. The 900-byte extension supplies UAC2 descriptors and fixed-rate controls, retains stereo/18-channel alternate settings, and removes one identified capture-startup dependency on playback. Actual original instructions and compiled extension paths have been exercised offline.

**First question:** can real capture IN packets start and become stable before any playback OUT packets? A bus trace must resolve whether the physical USB peripheral supplies the readiness and phase conditions assumed by the pump model. Enumeration by itself does not answer this.

Then establish:

- Standard class-driver binding, descriptor/control responses, and correct fixed-rate reporting at all three mixer rates.
- Capture-first, playback-first and duplex startup; stereo, 18-channel and both mixed alternate combinations.
- Sample polarity, bit alignment, levels, channel mapping and real OUT packet-tail behavior. The modeled independent branches do not validate physical stereo/mixed-mode packet boundaries.
- Sustained audio and clock behavior, stop/restart, USB reset, unplug/reconnect, retained MIDI and backup-mode regressions.
- The same evidence on a named iPhone/iPad, adapter and app, with the host driver and selected alternates recorded.

**Exit criterion:** repeatable bidirectional audio on a documented setup, including capture-first traces and sustained runs, with remaining device/rate/mode limits stated precisely. Clock validity currently reflects a supported configured rate, not measured PLL lock. Proprietary MIDI, the full-speed configuration without audio endpoints and Windows inbox implicit-feedback limitations remain separate issues.

## 4. Validate the USB1–4 host transport

The 1,132-byte host extension admits a deliberately narrow profile: high-speed UAC1, stereo, 24 significant bits in four-byte containers, a single matching supported rate and the documented asynchronous endpoint arrangement. It extends enumeration and selection; it does not add a general USB audio host implementation.

**First question:** is there a real device whose full descriptor set matches the implemented profile, and does the retained MX-1 engine exchange correctly timed audio with it? Capture the device on a computer first. Compare actual MX-1 setup and transfer behavior with a known-good Roland baseline.

**Exit criterion:** one independently reproducible matching-device result showing correct audio in both directions, clock behavior, reconnect and sustained operation. Then cover the individual host ports, power arrangements and multiple devices. Add each discovered transport requirement with a targeted regression test and a separate hardware result.

Packed 24-bit or 16-bit formats, full-speed devices, UAC2 hosts, multiple advertised rates, sample-rate writes, explicit feedback and arbitrary channel layouts are future work. Broadening admission before the associated transport is understood would not establish support for them.

## 5. Validate the stock-firmware Linux bridge independently

The bridge keeps stock MX-1 firmware and connects it to a Linux USB host, while an independent USB device controller presents UAC2 to iOS. A suitable controller topology and power arrangement are prerequisites; a passive cable or ordinary hub cannot provide those roles.

**Next work:** select a board by its actual independent host/device-controller capability, establish both links, and verify routing at stereo/48 kHz before multichannel work. Measure drift, underruns, latency and long-running resampling behavior; matching nominal sample rates does not synchronize two clocks.

**Exit criterion:** repeatable iOS-to-MX-1 and MX-1-to-iOS audio on stock mixer firmware, with board, kernel, gadget configuration, routing commands and measured limitations recorded. Success here does not validate either native firmware probe. See [research/linux-bridge.md](research/linux-bridge.md).

## 6. Validate channel source routing on a physical mixer

The independent [routing candidate](docs/CHANNEL_ROUTING.md) assigns raw analog,
digital, AIRA, return and computer sources to the eleven physical strips.
Holding a destination SELECT and turning TEMPO chooses its source. The DSP task
applies changes after the original parameter queue, with no new ARM audio copy
loop. Mono strips expose individual source lanes; stereo strips also expose
pairs. The requested split selects `An5` on 5/6 and `An6` on USB2.

**First question:** do distinct test signals on inputs 5 and 6 emerge separately
through the 5/6 and USB2 strips with USB2 disconnected, and does Auto restore the
stock path? Then establish native/computer source levels, stereo ordering,
duplication, return-bus behavior, all three rates, reconnect, rate changes,
mode changes and source switching during ordinary parameter updates.

**Exit criterion:** documented physical routing results tied to the candidate
hash, including the requested split and independent copies of a source.
Source-bank compatibility is supported by original DSP instruction patterns,
but the offline model does not execute numerical DSP arithmetic. Live stereo
operand writes are sequential; click-free switching and real-time margin
remain unmeasured. Routes currently reset to Auto on power-up and do not apply
in External Mixer mode. Persistent scene integration and that additional mode
need separate work.

## 7. Expand compatibility and define a release boundary

After the individual experiments have physical evidence, evaluate specific additions such as explicit feedback, real clock-lock reporting, more host formats, class-compliant MIDI or a combined image. Each addition needs its own original-path analysis, byte guards, tests and hardware scope. Retained Roland VID/PID and host driver caching must be accounted for when interpreting class-driver results; USB identity policy also needs a deliberate decision before a distributable release.

A release would require a defined hardware/support matrix, demonstrated update and recovery procedure, reproducible candidates tied to exact commits, regression evidence, user-facing installation guidance and clear provenance/licensing decisions. Until then, preserve the `UNTESTED` candidate labels and describe successes only as broadly as the collected evidence supports.
