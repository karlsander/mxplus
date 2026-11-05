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

## First MX-1 audio attempt

Candidate `56b9fa0e3b9a6f1ebcbdcf278a2222da0aa46d5b0d2b3431ddebcf82c1c828ae`
was copied as `MX1_UPD.BIN` to the Roland update volume, read back with the
matching hash, and ejected. After the requested update/restart test, the user
reported: “MIDI works, but no audio.” No packet trace or converter counters were
available. The user then confirmed no USB3 meter activity with source mapping
set to Auto/USB3. The exact system rate was not recorded.
The candidate identity is retained in `first-candidate.json`.

Investigation found an audio-open rejection before queue submission. Original
USB endpoint construction at decoded `e040`, runtime `6000e040`, copies the
complete endpoint address at `6000e0d0..6000e0d2` into record byte 8: `84` for
this input. The new audio check incorrectly required `04`; its modeled fixture
had also masked the direction bit. Re-running that first candidate with the
original `84` address reproduced state `0005` (MIDI ready), zero audio requests
and zero converter initializations. This is a concrete software fault consistent
with the observed silence; it does not rule out later transport problems.

The correction requires `84` and executes the original endpoint constructor
and list helpers in the regression, with only allocation and critical-section
entry/exit modeled. Combined setup now uses that exact endpoint record.

The audio extension correction is `04 29` → `84 29` (`cmp r1, #0x84`) at
USB runtime `607f034e`, decoded `37cea` in the extended component. It changes
one executable byte without growing code or state; container checksums change
accordingly. This location belongs to the appended extension, not stock code.
