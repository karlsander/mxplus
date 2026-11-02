# Mainline roadmap

One maintained firmware contains routing and USB-B UAC2. The routing predecessor
passed user bench tests including encoder end stops. The combined image has
offline evidence but still needs its own physical test.

1. Verify combined-image boot, routing, snapshot save/recall, delayed restart
   persistence and unchanged ordinary controls.
2. Establish class-driver USB-B enumeration, playback, capture-only and duplex.
3. Cover stop/restart, reconnect, stereo/18-channel and mixed alternates, all
   three rates, channel order/levels and sustained audio.
4. Record a reproducible host/cable/driver/setup and candidate hash. Establish
   device-specific failed-application recovery before claiming a safe upgrade.
5. Promote validation status only as supported by the measured results.

Generic AIRA-host support is excluded. Its narrow former implementation is
[documented](docs/HOST_PROBE.md); no separate research build is maintained.
Future reconsideration requires suitable devices and an explicit scope change.

The immutable stock input and historical evidence remain. Source/build history
is in Git, not parallel maintained firmware trees. There is no claim of class-
compliant MIDI, host-selected sample-rate changes, full-speed audio, measured
PLL lock, click-free switching, or universal USB-device compatibility.
