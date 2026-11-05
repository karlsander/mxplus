# FM-1 computer baseline, 2026-11-05

The user connected the FM-1 to the development Mac during the MX-1 host-audio
experiment. This is evidence about that FM-1 on a Mac, not MX-1 host audio.

* macOS 27.0.1, build 26A434; Apple USB audio service (`usbaudiod`).
* VID 1209, PID 0001, bcdDevice 0390; no serial number in the descriptor.
* IORegistry reported a 12,000,000 bit/s link. libusb speed enum 2 means
  full-speed. The device and configuration descriptors match the source-derived
  `../fm1-host-midi-20261103/` fixtures byte for byte.
* One audio input stream: stereo signed 16-bit PCM, nominal 44,100 Hz;
  no USB audio playback interface. Core Audio exposes float32 logical samples.
* An approximately eleven-second Core Audio run received 489,472 frames in 956
  callbacks. The interval between first/last callback timestamps corresponds to
  approximately 44,119.77 frames/s. This short timestamp estimate is not a
  precision clock measurement or a raw USB packet trace.
* Four channel-1 MIDI note-on/off pairs (60, 62, 64, 66; velocity 48) went to the
  `Felucca` MIDI destination while audio ran. No program changes or monitoring
  were enabled. Received peak 0.020294189 and RMS 0.004775440 (float full scale).
  This confirms nonzero audio during MIDI playback, not stereo separation,
  uninterrupted long-term operation, or sound quality.

`usb-descriptors.json` contains the two GET_DESCRIPTOR results.
`macos-audio-probe.json` contains aggregate counters, without a recording.
`rate-controls.json` records a separate endpoint `GET_CUR` (`a2 81 0100 0084`)
returning `44 ac 00`, followed by `SET_CUR` (`22 01 0100 0084`) accepting those
same three bytes. The nominal rate was unchanged. `rate-controls.c` is its source.
The accompanying C sources are the exact ad-hoc probes used. They are outside
offline reproduction: the audio probe opens the named FM1 input and sends the
four note pairs to `Felucca`/FM1. It must not be run against an unrelated MIDI
destination with the same name.

Build commands used on the Mac:

```
clang -I/opt/homebrew/include/libusb-1.0 descriptors.c -L/opt/homebrew/lib -lusb-1.0 -o /tmp/mxplus-fm1-descriptors
clang -Wall -Wextra audio-probe.c -framework CoreAudio -framework CoreFoundation -framework CoreMIDI -o /tmp/mxplus-fm1-audio-probe
```

The exact installed FM-1 application hash and cable model were not read back.
Neither probe changes device firmware or the Mac's default audio device.

## Earlier MX-1 MIDI result in the same session

After installing candidate
`253645edb92a09c7b0d100da01f57d5127834c109b2ad499332645487a7a1d14`, the user
reported “midi works to the fm1”. This establishes that reported direction only;
message types, clock timing, duration and MIDI return routing were not recorded.
This preceded the audio extension and cannot establish its hardware behavior.

The successful install used `MX1_UPD.BIN`. Earlier attempts with `MX-1_UPD.BIN`
flashed red after pressing TAP. Original updater bytes at decoded `59c4`,
runtime `600059c4`, independently identify `MX1_UPD.BIN` as the requested name.

## MX-1 candidate

`candidate.json` records the new image and extension identities. Implementation,
placement, original-instruction boundaries and the pending bench sequence are
in [the audio report](../../docs/USB_HOST_AUDIO.md). No physical MX-1 audio result
has been recorded. The previous working MIDI image remains available in the
main checkout and in Git at the base commit.
