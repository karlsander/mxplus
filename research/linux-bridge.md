# A Linux UAC2 bridge for using the original MX-1 with iOS

## Result and present status

A separate Linux board can plausibly translate the MX-1's existing computer USB connection into a class-compliant UAC2 connection for iOS. It would use Linux's Roland compatibility code on one USB controller and the kernel's UAC2 gadget on a second controller, with audio routed between their ALSA devices. This avoids changing the MX-1 firmware while native device-mode work continues.

The accompanying `tools/linux_bridge.py` implements the configuration and routing workflow. **This is a hardware prototype, not a demonstrated working MX-1/iOS product.** No MX-1, iOS device, USB controller, or ALSA sound card is attached to the research environment. The tool's planning, role mapping, parameter validation, and default read-only behavior were tested; actual gadget enumeration, audio, latency, and stability remain to be tested on hardware.

This bridge addresses the computer USB-B/iOS goal. It does not turn the MX-1's four AIRA host ports into generic USB inputs.

## Connections and hardware

The topology is:

| Connection | Host end | Device end |
|---|---|---|
| Original MX-1 audio link | Linux board's independent host port | MX-1 USB-B computer port |
| Class-compliant iOS audio link | iPhone/iPad in USB host mode | Linux board's USB device controller port |

The Linux machine needs an actual USB Device Controller, or UDC. A conventional USB host port cannot become a gadget merely by loading software. Linux documents the gadget/UDC distinction and the configfs procedure for binding a function to it. [B1]

An existing Raspberry Pi 4 or 5 is a candidate: Raspberry Pi documents peripheral mode on its USB-C connector and the `dwc2,dr_mode=peripheral` overlay. Its dedicated host ports can serve the MX-1. The official guide also identifies board power as a constraint. Use a board-approved arrangement that supplies enough power while the device connector carries USB data; do not assume an iPhone supplies a full board's power budget. A Pi Zero's single exposed data controller cannot provide these two independent USB roles at once. A Compute Module needs a carrier with a separate host controller if its native USB controller is used as the gadget. [B2]

Use the correct USB host adapter for a Lightning iOS device or the appropriate data connection for USB-C. The MX-1 USB-B cable goes to the Linux host port. No USB-A-to-USB-A host-to-host cable is involved. Apple's iPad documentation explicitly supports class-compliant USB audio interfaces on supported USB-C iPads; the exact phone/tablet, adapter, and audio app still need validation. [B3]

## Why this can work

The extracted MX-1 descriptors have VID:PID `0582:01a3`, vendor-specific interfaces, UAC1-like audio formats, 18-channel and stereo alternates, and 24 significant bits in four-byte samples. Linux has Roland autodetection and implicit-feedback handling for this type of vendor-specific interface; see `usb-compatibility.md` for the precise evidence and limitations. The device has not been physically tested against the selected Linux kernel. [B4]

On the iOS-facing side, Linux `f_uac2` supplies the standard descriptors, clock requests, and USB audio transport. Its topology is easy to reverse accidentally: **gadget ALSA capture receives USB OUT from the iOS host**, while **gadget ALSA playback supplies USB IN to that host**. Its asynchronous capture mode has a feedback endpoint. The script uses these directions explicitly. [B5]

| Desired audio direction | Linux capture source | Linux playback destination |
|---|---|---|
| iOS audio into MX-1 | `hw:CARD=UAC2Gadget,DEV=0` | `hw:CARD=MX1,DEV=0` |
| MX-1 audio recorded by iOS | `hw:CARD=MX1,DEV=0` | `hw:CARD=UAC2Gadget,DEV=0` |

The card names above are examples. The tool reads the actual IDs under `/proc/asound/card*/id`; the operator must use the IDs found on the board. It rejects a selected MX-1 card whose reported USB ID is different.

In configfs these directions are named `c_*` for gadget capture and `p_*` for gadget playback. They are the board's ALSA directions, not the iOS app's recording/playback labels. Reversing them is a common source of a silent or incorrectly routed test. The two commands in the generated plan explicitly state both endpoints.

## Initial audio profile

Start with a single rate of **48,000 Hz** at both ends, with the MX-1 set to that rate before connecting it. The script also supports 44,100 or 96,000 Hz as separate sessions. It deliberately advertises one rate, so an app cannot change to an unhandled nominal rate halfway through a session.

Use `S32_LE` for routing. Linux's USB format parser maps a four-byte PCM subframe to that ALSA format. This carries the MX-1's original 24-bit precision; it does not create 32 bits of analog resolution. [B6]

There are two selectable profiles:

| Profile | Configfs channel mask | Audio payload at 48 kHz, per direction | Initial requested route latency |
|---|---:|---:|---:|
| Stereo | `0x3` | 48 bytes per 125 µs | 50 ms |
| 18 channels | `0x3ffff` | 432 bytes per 125 µs | 5 ms / 240 frames |

Payload numbers are arithmetic (`channels × 4 bytes × rate ÷ 8000`), before USB overhead and feedback headroom. The script sets high-speed `bInterval=1`. The 18-channel mode requires a high-speed link and checks its negotiated speed before starting audio. At full speed, 18 × 4 × 48 frames would need 3,456 bytes each millisecond, exceeding a single full-speed isochronous endpoint's capacity.

The 18-channel mask uses named USB spatial positions to obtain 18 channels on kernels whose UAC2 ABI derives the count from that mask. Those names are not a description of the MX-1's musical routing. A multichannel iOS app must preserve or explicitly map the channel order. Likewise, the original firmware's stereo alternate is not proof that it carries precisely the mix the user wants. Check routing with one input active at a time. The script does not mix 18 channels down to two.

The shorter starting target for 18 channels is deliberate. Upstream `u_audio` limits a hardware buffer to `PAGE_SIZE × 16` bytes and a period to one page; on a 4 KiB-page kernel these are 64 KiB and 4 KiB. An 18-channel, 50 ms, 48 kHz buffer alone would consume 172,800 bytes. The script therefore starts the 18-channel case at 240 frames, and leaves ALSA to negotiate supported period and buffer sizes. This is a buffering target, not a measured end-to-end latency. [B7]

## Clock drift

Both links can claim 48 kHz while their actual clocks differ slightly. At 50 parts per million, the discrepancy is 2.4 sample frames per second. A plain `arecord | aplay` pipe has no policy for maintaining a stable long-term buffer level across that mismatch.

The script runs two `alsaloop` processes with `-S samplerate -A 1`, explicitly selecting adaptive sample-rate correction and the medium-quality sinc converter. ALSA supports this mechanism when `alsaloop` is built with libsamplerate. It requires a compatible integer sample format; `S32_LE` is appropriate on little-endian systems. The application must report an error rather than being treated as successful if libsamplerate support is unavailable. [B8]

The bridge performs resampling, so this first implementation is not bit-transparent. It also adds buffering, processing, and USB scheduling latency. The shared 18-channel stream preserves channel alignment within each direction, but the two directions have independent correction loops. Long-duration stability and round-trip delay need measurement.

## Reproducible workflow

Run these commands on the Linux board, from the research package directory. None of them were run against a physical device during this analysis.

Keep the exact board model, kernel version, iOS version, adapter, and power arrangement with the results. Run `alsaloop --help` to check the installed program's options. Its first actual route must confirm that samplerate synchronization is available; the presence of the executable alone does not establish that it was built with libsamplerate.

### 1. Inspect the unmodified MX-1 connection

With the MX-1 connected to the board's USB host port:

```sh
python3 tools/linux_bridge.py inspect
lsusb -d 0582:01a3 -v
lsusb -t
aplay -l
arecord -l
cat /proc/asound/cards
```

The tool also includes the available `/proc/asound/card*/stream*` text in its inventory. Confirm that capture and playback expose the chosen channel count, `S32_LE`, and the MX-1's current sample rate. Confirm high-speed operation. If these are absent, first resolve the Linux MX-1 driver binding; a gadget cannot repair the missing source or destination.

Close applications that have opened either hardware PCM. The script uses `hw:` devices so unexpected desktop mixing, channel conversion, or rate conversion does not obscure the experiment.

### 2. Prepare the board's gadget support

Enable the correct device controller using the board's documentation. On a Pi 4/5 this includes the documented peripheral-mode overlay and a reboot. The script does not modify boot files.

Install ALSA utilities with an `alsaloop` build that includes libsamplerate. The kernel needs `snd-usb-audio`, configfs/libcomposite, and `usb_f_uac2`. Typical module-loading commands are:

```sh
sudo modprobe snd_usb_audio
sudo modprobe libcomposite
sudo modprobe usb_f_uac2
```

If configfs is not already mounted, mount it once using the kernel's documented procedure:

```sh
sudo mount -t configfs none /sys/kernel/config
```

Then run `python3 tools/linux_bridge.py inspect` again. There must be a usable entry in `/sys/class/udc`. An Ethernet or mass-storage gadget may already occupy it. The script refuses to take a controller away from an existing gadget. [B1]

### 3. Review and create the gadget

The default invocation is an inventory. Every action also remains read-only without `--apply`:

```sh
python3 tools/linux_bridge.py plan --channels 2 --rate 48000 --power-mode self
python3 tools/linux_bridge.py setup --channels 2 --rate 48000 --power-mode self
```

For a board actually powered independently of the iOS USB bus, the explicit application command is:

```sh
sudo python3 tools/linux_bridge.py setup --apply --channels 2 --rate 48000 --power-mode self
```

If the board really draws power from that USB connection, use `--power-mode bus --max-power-ma N` with its actual USB 2 power requirement. If that arrangement cannot supply the board, fix the power arrangement instead of claiming self-powered operation. `--udc NAME` selects among multiple controllers. The tool uses prototype Linux gadget IDs `1d6b:0104`, also used in upstream gadget examples; it does not impersonate a Roland device. [B9]

The created function is audio-only, with no network or storage function. Setup creates a named gadget, fills its configfs attributes, and binds it last. Partial setup errors attempt cleanup of only the objects just created. The kernel UAC2 ABI provides the channel masks, sample sizes/rates, feedback mode, interval, and feature-unit settings used here; an older kernel missing one of these attributes is rejected rather than silently receiving a different setup. [B10]

### 4. Connect iOS and run a short route test

Connect the Linux device port to iOS, unlock iOS, and open a recording/playback app capable of choosing the external interface. Repeat inventory and substitute the actual card IDs:

```sh
python3 tools/linux_bridge.py inspect
python3 tools/linux_bridge.py route --channels 2 --rate 48000 --mx1-card MX1 --gadget-card UAC2Gadget --seconds 30
python3 tools/linux_bridge.py route --apply --channels 2 --rate 48000 --mx1-card MX1 --gadget-card UAC2Gadget --seconds 30
```

The first `route` command prints the exact commands. The second opens the audio devices and passes audio. Run as a user with ALSA device access. It starts both directions, uses explicit drift compensation, and stops the other direction if one process fails. A foreground run without `--seconds` continues until Ctrl-C.

For a direct view of the underlying stereo commands:

```sh
alsaloop -C hw:CARD=UAC2Gadget,DEV=0 -P hw:CARD=MX1,DEV=0 -f S32_LE -r 48000 -c 2 -t 50000 -S samplerate -A 1 -v
alsaloop -C hw:CARD=MX1,DEV=0 -P hw:CARD=UAC2Gadget,DEV=0 -f S32_LE -r 48000 -c 2 -t 50000 -S samplerate -A 1 -v
```

These need to run concurrently; the Python launcher handles that. Send a quiet test signal and verify the intended MX-1/iOS routing before raising monitoring levels. In particular, avoid enabling app monitoring back into an input already included in its source mix.

### 5. Test 18 channels and clean up

Stop routing before changing the gadget. Preview and apply teardown:

```sh
python3 tools/linux_bridge.py teardown
sudo python3 tools/linux_bridge.py teardown --apply
```

Repeat setup and routing with `--channels 18`. For a self-powered board at 48 kHz, after the previous gadget has been removed:

```sh
python3 tools/linux_bridge.py setup --channels 18 --rate 48000 --power-mode self
sudo python3 tools/linux_bridge.py setup --apply --channels 18 --rate 48000 --power-mode self
python3 tools/linux_bridge.py inspect
python3 tools/linux_bridge.py route --channels 18 --rate 48000 --mx1-card MX1 --gadget-card UAC2Gadget --seconds 30
python3 tools/linux_bridge.py route --apply --channels 18 --rate 48000 --mx1-card MX1 --gadget-card UAC2Gadget --seconds 30
```

Substitute the actual card IDs again: removing and recreating a gadget can change its ALSA index. Setup and route must use the same channel count and rate; the launcher checks the function's read-back attributes. Change `--power-mode` to match the real power arrangement before applying setup.

The default 18-channel route target becomes 240 frames: 5 ms at 48 kHz, 2.5 ms at 96 kHz. Use an iOS multichannel app, verify every channel individually, and measure xruns and round-trip latency before a long run. A small SBC may need a faster converter (`-A 2` in a manually reviewed command), tuned scheduling, or a different audio routing application if the 18-channel resampling load or scheduling proves excessive. Do not infer stable operation from enumeration alone.

Teardown checks this tool's manufacturer/product markers and exact function link before unbinding and removing its own gadget. It leaves modules and the configfs mount available. Nothing is installed to start automatically at boot.

## Local verification and next evidence needed

`python3 tools/linux_bridge_test.py -v` passes five tests: no action mutates without `--apply`, channel/direction/clock-correction selection, explicit power declaration before setup, the multichannel buffer-budget calculation, and input validation. A read-only inventory in the research environment correctly reports no UDC or audio device. These tests do not establish USB interoperability.

A useful first hardware result comprises the inventory JSON, MX-1 and gadget USB descriptors, kernel version, exact board and iOS version, two-direction audio test, and the `alsaloop` output. The next milestones are a 30-minute dropout test, every-channel routing check, measured round-trip latency, and reliable disconnect/reconnect handling. The current launcher intentionally stops on failure; unattended recovery is a later feature.

For a reproducible record, save `inspect` and `plan` output before the actual run, then redirect the `route --apply` command's stdout and stderr to a named log file. Note its exit status and retain a short WAV from each direction. `docs/HARDWARE_VALIDATION.md` gives the staged stock/bridge/candidate sequence and specifies what each result establishes.

## Primary sources

- **B1:** Linux kernel, [configfs gadget setup and binding](https://www.kernel.org/doc/html/latest/usb/gadget_configfs.html).
- **B2:** Raspberry Pi, [Using OTG mode on Raspberry Pi SBCs](https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-009276-WP-1-Using%20OTG%20mode%20on%20Raspberry%20Pi%20SBCs), official 2025 white paper.
- **B3:** Apple, [Charge and connect with the USB-C port on your iPad](https://support.apple.com/en-ie/108894).
- **B4:** Linux source, [Roland autodetection](https://github.com/torvalds/linux/blob/master/sound/usb/quirks.c) and [implicit feedback](https://github.com/torvalds/linux/blob/master/sound/usb/implicit.c); original firmware descriptor extraction in `analysis/usb_descriptors.json`.
- **B5:** Linux source, [`f_uac2.c`](https://github.com/torvalds/linux/blob/master/drivers/usb/gadget/function/f_uac2.c), topology and feedback endpoint definitions.
- **B6:** Linux source, [`format.c`](https://codebrowser.dev/linux/linux/sound/usb/format.c.html), `parse_audio_format_i_type`.
- **B7:** Linux source, [`u_audio.c`](https://codebrowser.dev/linux/linux/drivers/usb/gadget/function/u_audio.c.html), buffer and period constants.
- **B8:** ALSA source, [`alsaloop.c`](https://github.com/alsa-project/alsa-utils/blob/master/alsaloop/alsaloop.c) and [`pcmjob.c`](https://github.com/alsa-project/alsa-utils/blob/master/alsaloop/pcmjob.c); [upstream-authored pcmjob source snapshot](https://chromium.googlesource.com/chromiumos/third_party/alsa-utils/+/3853175d122ef368db1f653140502ec44d4b2a4a/alsaloop/pcmjob.c) exposes the complete resampling checks in the web reader.
- **B9:** Linux source, [virtual gadget example](https://github.com/torvalds/linux/blob/master/tools/usb/usbip/vudc/vudc_server_example.sh), example Linux gadget identity.
- **B10:** Linux kernel, [UAC2 configfs ABI](https://github.com/torvalds/linux/blob/master/Documentation/ABI/testing/configfs-usb-gadget-uac2) and [gadget audio testing](https://www.kernel.org/doc/html/latest/usb/gadget-testing.html).
