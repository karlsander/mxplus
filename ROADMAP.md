# Mainline roadmap

Maintain one mixer-focused firmware: channel routing with end stops, stock
snapshot/restart route storage, mastering editing and USB-B UAC2. The restored pre-generator image
boots and passed a user-reported iPhone/AUM duplex audio path. The routing
predecessor passed routing/end-stop tests. These are bounded observations,
not sustained or comprehensive validation.

1. Physically verify snapshot save/recall, delayed restart persistence, ordinary
   SELECT behavior, reset behavior and existing routing across mixer modes.
2. Physically validate the [stereo playback packet fix](docs/USB_PACKET_FIX.md).
   Extend evidence with device/OS/app versions,
   rates, channel maps and duration. Verify capture-only, stereo/18-channel
   and mixed alternates, stop/restart, reconnect and sustained audio at all
   three rates.
3. Physically validate [mastering mode](docs/MASTERING.md), including
   gesture isolation, all parameter assignments, pickup/blink, save/recall and
   sustained audio. The new UI reclaims an existing stock lookup footprint;
   its offline checks do not establish hardware stability.
4. Consider small control/routing improvements individually. The internal code
   slot has only 20 bytes free; measure compiled size before claiming capacity.
   An explicitly reserved SDRAM design is possible research, not enabled in
   the current candidate. [Memory and DSP findings](docs/GENERATOR_RESEARCH.md).
5. Keep exact image identities and scoped hardware results. TAP rollback worked
   for the observed application failures; other recovery classes are unverified.

Generators, extra SELECT editing and generic USB-host unlocking are excluded.
Future DSP work needs a separate explicit experiment and evidence about real
interrupt timing, memory placement and sample transport before reintegration.
No alternate generator or host-unlock firmware is maintained.

Known USB limits remain: fixed read-only rate, validity based on configuration
rather than PLL lock, implicit feedback, proprietary MIDI, high-speed audio
only, and incomplete physical stereo/mixed-alternate and sustained testing.
