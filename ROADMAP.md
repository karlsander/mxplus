# Mainline roadmap

One maintained firmware contains routing, internal NSE/BD sources and USB-B UAC2. The routing predecessor
passed user bench tests including encoder end stops. The pre-generator mainline
boots, but the first generator/editor image left the panel dark. TAP-mode
rollback worked for this failure. Startup guards did not resolve the dark boot;
[a location-only test reproduces the failure](docs/BOOT_REGRESSION.md). The
current SDRAM code reservation needs its hardware test. The earlier
image passed a user-reported iPhone/AUM duplex path over a direct USB cable.

1. Verify combined-image boot, routing, snapshot save/recall, delayed restart
   persistence, SELECT editing toggles and unchanged ordinary controls. Test
   generator levels, clock behavior, exchange mapping and IRQ margin with one
   and eleven BD voices. BD pattern persistence is not yet implemented.
2. Extend the initial iPhone/AUM duplex result with a recorded device/OS/app
   setup, channel map and duration; separately establish capture-only behavior.
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
