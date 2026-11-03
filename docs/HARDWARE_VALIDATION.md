> Current scope: one routing + persistence + mastering + USB-B/host-MIDI mainline image, now with [display diagnostics](DISPLAY_DIAGNOSTICS.md). Generic host audio and generators remain excluded. The pre-generator baseline passed one iPhone/AUM duplex path; this does not validate the changed candidate. Historical generic-audio host sections below are research guidance, not an available firmware build. See [MAINLINE.md](MAINLINE.md).

# Staged MX-1 hardware validation

## Purpose and present boundary

The package maintains one experimental firmware candidate and an
external Linux bridge prototype. Offline checks establish the container
format, selected original ARM execution paths, and the new code's behavior
under explicit models. They do not establish safe flashing, physical recovery,
USB enumeration, or reliable audio. This plan starts with the original firmware
and separates those questions so a failure produces useful evidence.

Stages 1–3 can be performed without changing MX-1 firmware. Stages 5–6 apply
only after a device-specific recovery route has been established. No step in
this document is an instruction to treat the candidate as a safe release.

## 1. Label the connections and establish power

| Experiment | USB host | USB device | Connection |
|---|---|---|---|
| Stock computer baseline | Linux or Mac | MX-1 | Computer host port to MX-1 USB-B |
| Native iOS UAC2 candidate | iPhone/iPad in host mode | MX-1 | Correct iOS data/host adapter to MX-1 USB-B |
| Generic AIRA-port candidate | MX-1 USB1–4 | Audio interface/instrument | MX-1 USB-A to the interface's device port |
| External bridge, first link | Linux board's host controller | Original MX-1 | Linux host port to MX-1 USB-B |
| External bridge, second link | iPhone/iPad in host mode | Linux board's independent UDC | iOS to the board's device-mode connector |

Use the MX-1's normal power supply. Roland documents USB bus power on **HOST 3**;
do not assume ports 1, 2, and 4 can power a generic interface. Use a compatible
self-powered device or HOST 3 within its documented power limit. Do not add a
hub to the first experiment, because it adds another enumeration/topology
variable. A USB-A-to-USB-A host-to-host cable is not a substitute for the
connections above. The Linux bridge requires separate host and device
controllers and an adequate, board-approved power arrangement. [V1, V2]

Mute monitoring, turn physical output levels down, and use a quiet identifiable
test signal. Establish the audio routing before enabling software monitoring;
a monitored return can feed back into the same mix.

## 2. Preserve the original and collect a stock baseline

Record the unit's displayed firmware version, hardware labels, current sample
rate, mixer mode, scenes, and connected devices. Save the original supplied
file separately. Its SHA-256 is:

`26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`

Use Roland's documented settings backup procedure if those settings matter.
That backup is **not** a full flash or factory-calibration backup. [V3]

Set the MX-1 to 48 kHz using Roland's procedure before connecting USB. On a
Linux test host, run the following from the package directory. They create
local log files but do not alter the mixer:

```sh
mkdir -p mx1-validation/stock-48000
uname -a > mx1-validation/stock-48000/kernel.txt
lsusb -t > mx1-validation/stock-48000/topology.txt
sudo lsusb -v -d 0582:01a3 > mx1-validation/stock-48000/descriptors.txt
aplay -l > mx1-validation/stock-48000/playback-devices.txt
arecord -l > mx1-validation/stock-48000/capture-devices.txt
cat /proc/asound/cards > mx1-validation/stock-48000/cards.txt
python3 tools/linux_bridge.py inspect > mx1-validation/stock-48000/inventory.json
```

Keep any permission warnings from descriptor capture; an incomplete dump is
not evidence that a descriptor is absent. The inventory includes each USB
sound card's `/proc/asound/cardN/stream*` text. Confirm the actual MX-1 card ID,
480 Mbit/s connection, rates, formats, and available channel counts.

Verify stock stereo recording and playback with the known working driver,
then 18-channel audio if available. Activate one mixer input at a time and
write down which recorded channel receives it. Save a short original WAV and
the exact application/device settings. On a Mac, also save Audio MIDI Setup
screenshots and a System Information USB/audio report. Label whether the
Roland driver is installed; its success does not demonstrate class compliance.

Repeat the descriptor/rate record at 44.1 and 96 kHz in separately named
sessions. The original binary stores 96 kHz templates that are edited at
initialization, so the live descriptor is the evidence for each setting. [V4]

## 3. Try the external bridge independently

Follow `research/linux-bridge.md` using **original MX-1 firmware**. First verify
that Linux can capture from and play to the MX-1 before creating the gadget.
Start with stereo, 48 kHz, and the actual card IDs from `inspect`.

The direction names are from iOS's perspective:

- iOS playback travels through **gadget ALSA capture**, then MX-1 ALSA playback.
- MX-1 recording travels through **MX-1 ALSA capture**, then gadget ALSA playback
  to iOS.

Preview `setup` and `route` without `--apply`; only then run the explicit
application commands on the board. Use a 30-second first test. Save the
inventory, exact plan, ALSA output, iOS app settings, and a recording from each
direction. Run 30 minutes once the short test works. Equal nominal sample rates
do not remove clock drift: check for underruns, overruns, growing delay, or
periodic clicks while the two `alsaloop` resamplers are active. [V5]

Stop routing and recreate the gadget with 18 channels before trying that
profile. Use a multichannel-capable iOS app and verify every channel's mapping.
Do not expect a stereo app to automatically expose or downmix all 18 channels.
Measure round-trip latency with a quiet pulse or other known test signal;
the command's buffering target is not the end-to-end latency.

## 4. Establish recovery before any firmware candidate

Review `research/container.md`, the candidate's build report, and Roland's
official update instructions with the person responsible for the hardware.
The traced standard updater preserves both boot regions and the updater
region, but a preserved region alone does not prove recovery from every
application failure. File-copy update mode and settings-restore mode are not
demonstrations of recovery from a failed experimental image. [V3, V6]

Before a candidate reaches the mixer, establish:

1. A documented, device-specific way to restore the original application if
   the experiment no longer boots or enumerates. If external programming is
   needed, verify the actual board, flash part, voltage, pinout, and a readable
   backup first; this package does not provide a verified MX-1 programming
   header or electrical recovery procedure.
2. Stable power, the original update file, preserved user settings, the exact
   candidate SHA-256, and an offline verification report for that same file.
3. Agreement on who performs the hardware operation and how a failed update
   will be handled. If recovery cannot be established, continue with stock
   captures and the external bridge rather than treating this prerequisite
   as satisfied by emulation.

Do not combine the host-port and USB-B candidates for the first tests. Use the
device-specific update procedure only after this preparation; this plan does
not replace it. Keep the original filename/candidate identity unambiguous, and
do not place raw-ROM or other competing image files on the update disk.

## 5. Test mainline USB-B audio and MIDI in small steps

Candidate: `build/mainline/MXPLUS_MAINLINE_UNTESTED.bin`.
After an authorized installation with the established recovery route:

1. Check normal mixer startup and analog audio before attaching USB. Set 48 kHz.
2. Attach to a class-driver test host and capture its descriptors. Expect
   `EF/02/01` device/qualifier fields, a 435-byte high-speed configuration,
   audio interfaces 0–2, stereo/18-channel modes, and MIDI interfaces 3/4
   with two bulk MIDI ports. Follow [MIDI acceptance](USB_MIDI.md#hardware-acceptance);
   class-driver operation is not yet established. Inspect which driver binds
   on a Mac; retained Roland VID/PID may match an installed vendor driver.
3. Verify the clock reports the actual current rate and a single fixed range.
   A class-only host must not depend on a Roland driver to interpret these
   controls. Log control-request failures before attempting continuous audio.
4. Test stereo capture first, playback first, and duplex as separate starts.
   Confirm real IN packets can begin before OUT audio. A recording-only app is
   insufficient evidence: Linux's Roland compatibility path can open OUT behind
   the application's back. Apple's host waits for consistent IN timing before
   starting asynchronous OUT with implicit feedback. [V7]
5. Verify sample polarity, level, bit alignment, silence, and the two-channel
   routing; the traced stereo path uses internal channels 16/17. Once stable,
   test 18-in/18-out and both mixed combinations, 18-out/2-in and 2-out/18-in.
   Record the actual selected USB alternates: two app tracks do not prove
   that the host chose a two-channel alternate rather than an 18-channel stream.
   Their code branches were emulated; real stereo OUT packet-tail handling is
   still unverified.
6. Repeat short tests, then 30-minute runs, at 44.1 and 96 kHz. Set rates on
   the mixer before a new USB session. Test stream stop/restart, playback ending
   while capture continues, USB reset, unplug/reconnect, and app relaunch.
7. Repeat the successful class-host sequence with the actual iPhone/iPad,
   correct adapter, and named app/version. Check both directions and channel
   selection rather than recording only the interface name appearing in a UI.

The unchanged full-speed configuration has no audio endpoints. Failure to
provide audio at full speed is outside this candidate's promised scope. The
Windows in-box UAC2 driver does not support this implicit-feedback OUT design;
use it to inspect descriptors if useful, but do not treat its audio failure as
an Apple compatibility result. Explicit feedback is a separate future change.
[V8]

## 6. Test the USB1–4 host candidate separately

Candidate: `build/host-probe/MX1_UAC1_HOST_PROBE_UNTESTED.bin`.
Return to the documented baseline between different candidate experiments.
Start with a known supported Roland/AIRA device to check regression behavior.
Then preflight one generic device's descriptors while it is attached to a
computer. The present experimental profile requires high-speed UAC1, stereo
in both directions, alternate 0/1, 24-bit PCM in four-byte subframes, one
matching discrete supported rate, interval 1, asynchronous endpoints, and no
separate explicit-feedback endpoint. The exact checks in
`patches/uac1_host_probe.c` and its build report govern admission.

A normal full-speed UAC1 interface or a UAC2 interface is not an appropriate
positive test. If no available device matches the narrow profile, record that
result; repeated plugs do not expand the implemented transport.

Use one direct, adequately powered device and 48 kHz at both ends initially.
Verify device-to-mixer audio, mixer-to-device audio, levels, routing, and a
30-minute stability run. Then check reconnect, each supported host port and
multiple devices. Different nominal rates and more complex topologies are
later tests, after the simple case works. The host-port candidate is stereo;
18-channel testing belongs to the USB-B or bridge experiments.

## 7. Collect logs that distinguish the failure

For every result, record the candidate SHA-256 or stock version, hardware and
OS versions, sample rate, channel/alternate selections, cable/adapter/power
topology, exact start order, commands/app settings, and elapsed time. Retain:

- Complete descriptor dumps and actual ALSA stream information.
- Kernel/application errors and a short WAV from each audio direction.
- Capture timestamps for configuration, clock requests, `SET_INTERFACE`, the
  first successful IN and OUT transfers, resets, and disconnects.
- Counts and times of xruns/clicks, channel mapping, sample level/alignment,
  and measured latency or drift over a longer run.

Linux usbmon observes requests at that Linux host's controller-driver boundary.
Capture the MX-1's bus and retain only its device traffic when sharing results;
Wireshark can filter by the recorded bus and device address. It is not an
electrical analyzer or proof of exact wire timing. It also cannot observe the
MX-1 acting as host on USB1–4 merely because the computer is connected to the
separate USB-B port. That link needs its own physical analyzer or instrumented
firmware for an actual AIRA-port transaction trace. [V9]

Distinguish **enumerates**, **opens a stream**, **starts capture before playback**,
**passes audio**, and **runs stably** as separate results. If a stage fails,
retain its logs and reproduce the corresponding stock baseline before adding
another variable.

## Primary references

- **V1:** [Roland owner's manual](https://cdn.roland.com/assets/media/pdf/MX-1_e01_W.pdf).
- **V2:** [Raspberry Pi: Using OTG mode on Raspberry Pi SBCs](https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-009276-WP-1-Using%20OTG%20mode%20on%20Raspberry%20Pi%20SBCs).
- **V3:** [Roland supplementary manual, settings backup/restore](https://cdn.roland.com/assets/media/pdf/MX-1_Supplementary_Manual_e01_W.pdf).
- **V4:** [Roland sampling-rate procedure](https://support.roland.com/hc/en-us/articles/205215985-MX-1-Changing-the-Sampling-Rate).
- **V5:** [Linux UAC2 gadget implementation](https://github.com/torvalds/linux/blob/master/drivers/usb/gadget/function/f_uac2.c) and [ALSA alsaloop](https://github.com/alsa-project/alsa-utils/tree/master/alsaloop).
- **V6:** [Roland system program and official update procedure](https://www.roland.com/global/support/by_product/mx-1/updates_drivers/82415302-0466-4c5c-be4e-138a8946d4a7/).
- **V7:** [Apple TN3190: USB audio device design considerations](https://developer.apple.com/documentation/technotes/tn3190-usb-audio-device-design-considerations); [Linux Roland implicit-feedback handling](https://github.com/torvalds/linux/blob/master/sound/usb/implicit.c).
- **V8:** [Microsoft USB Audio 2.0 driver, feedback limitations](https://learn.microsoft.com/en-us/windows-hardware/drivers/audio/usb-2-0-audio-drivers).
- **V9:** [Linux usbmon documentation](https://docs.kernel.org/usb/usbmon.html).

Firmware-specific claims and offline results are reproducible from
`research/container.md`, `research/usb-compatibility.md`,
`research/device-control.md`, and the two candidate build reports.
