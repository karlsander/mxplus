# mxplus

mxplus is a a firmware hack for the Roland MX-1. Unsurprisingly, everything except for this README is vibe-coded. Patching your firmware with mxplus adds these features:

- **Driverless USB audio** I wouldn’t call it class compliant, but it works. Plugged straight into an iOS device, you can record any input and send to any mixer channel. This is for the USB-B port, not the AIRA host ports.
- **Channel Source Mapping** On any channel, select a source by holding down Select and rotating the Tempo encoder. Use any analog input, including 5 and 6 separately, Effect Return Stereo/L/R and digital/USB/PC channels as stereo, L or R.
- **Mastering Mode** Hold down the mastering button and press TAP to enter mastering mode, where the whole control surface is taken over to offer control over the quite comprehensive hidden mastering chain (Parametric EQ > Low Cut > Enhancer > 3-Band Expander and Compressor, with adjustable crossover > Mid/Side Processor > Limiter > Clipper). You can use any of the the 10 built-in slots to store configs.

USB MIDI on the host ports is now an offline experiment, with sync output prioritized and incoming host clock blocked. It still needs testing on the mixer; [scope and limitations](docs/USB_HOST_MIDI.md).

The channel remapping makes it possible to use all 11 channels even without much Roland gear, either by spreading mono / return channels or duplicating inputs for parallel processing.

To make better use of the channels, I want to explore unlocking the USB host ports for other devices and maybe adding internal sound generators, but most importantly I want a stable, better version of the MX-1 we love, not turn it into different instrument, so we’ll see.

USB-B MIDI class support is now an offline-tested experiment: the build advertises
two USB-MIDI 1.0 ports alongside audio. It still needs testing with a real host.
See [MIDI status and test procedure](docs/USB_MIDI.md).

## Install

Download the original Roland firmware and use the [web patcher](https://karlsander.github.io/mxplus/) to modify it. The patcher also explains how to install the resulting file.

Of course there is always some risk of bricking your device if you flash non-manufacturer firmware.
However, during development, I flashed a few problematic versions that left the device not turning on at all, and also accidentally interrupted the flashing process, and I was always able to return normally to firmware install mode (so far) and install a good version.
