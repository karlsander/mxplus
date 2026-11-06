# Mainline roadmap

Maintain one mixer-focused firmware: channel routing with end stops, stock
snapshot/restart route storage, mastering editing, USB-B UAC2 and experimental USB-MIDI 1.0. The restored pre-generator image
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
3. Physically validate [mastering mode](docs/MASTERING.md), now entered with
   MASTERING then TAP after the previous timed hold failed on hardware. Check
   the [held-key range fix](evidence/mastering-key-range-20261104/README.md),
   gesture isolation, all parameter assignments, pickup/blink, save/recall and
   sustained audio. The new UI reclaims an existing stock lookup footprint;
   its offline checks do not establish hardware stability.
4. Physically validate [USB-MIDI](docs/USB_MIDI.md) on class-only hosts: both
   ports, clock/transport, SysEx, reconnect and simultaneous audio.
5. Physically validate [FM-1 host audio](docs/USB_HOST_AUDIO.md): stereo input,
   simultaneous MIDI, unplug/reconnect, connected boot, sustained operation and
   USB-B operation. B4 established the Bluetooth/MIDI command bridge; B5 adds
   an explicitly started EHCI split-input experiment. Other host-audio
   coexistence needs shared bandwidth/TT admission beyond B5. The computer
   probe and offline tests do not establish an MX-1 audio result.
6. Consider small control/routing improvements individually. The internal code
   slot has only 20 bytes free; measure compiled size before claiming capacity.
   A main-processor SDRAM design remains research. The separate USB processor
   now reserves 64 KiB for the FM-1 experiment. [Memory and DSP findings](docs/GENERATOR_RESEARCH.md).
7. Keep exact image identities and scoped hardware results. TAP rollback worked
   for the observed application failures; other recovery classes are unverified.

MIDI output to an FM-1 succeeded after the [alternate-zero startup fix](evidence/host-midi-alt-zero-20261104/README.md) for [USB-host MIDI](docs/USB_HOST_MIDI.md). Validate sync output, rejection of incoming host sync, notes/controllers/SysEx and routing on the changed candidate. Any future routing configuration belongs in the existing GAIN-at-boot system menu.

Generators, extra SELECT editing and generic USB-host audio beyond the measured
FM-1 input profile are excluded.
Future DSP work needs a separate explicit experiment and evidence about real
interrupt timing, memory placement and sample transport before reintegration.
No alternate generator or host-unlock firmware is maintained.

Known USB-B limits remain: fixed read-only rate, validity based on configuration
rather than PLL lock, implicit feedback, unverified USB-MIDI host compatibility, high-speed audio/MIDI
only, and incomplete physical stereo/mixed-alternate and sustained testing.
