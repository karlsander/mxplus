# iPhone/AUM hardware observation — 2 November 2026

User-reported test on the pre-generator mainline from commit
`eb646b6cb3ad7f271097c4ab41f2098ab1399576`:

- Firmware SHA-256: `88457445ffe1abeca8365198d0c15ed967c6f5b4dac08393da52c575a80660ba`.
- Host: USB-C iPhone, connected directly to MX-1 USB-B by USB-B–to–USB-C cable.
- App: AUM. No adapter or hub reported.
- Observed path: MX-1 analog input → USB capture into AUM → an AUM effect →
  USB playback to a different MX-1 channel, successfully heard by the user.
- User saw multiple channels and subsequently recalled 18, initially saying
  "17?". This matches the advertised 18-channel configuration, but no channel
  enumeration screenshot, descriptor capture or exhaustive channel test exists.

This is the first reported working iPhone audio round trip for the combined
routing + USB-B mainline. It establishes simultaneous capture and playback for
the tested path, not separate capture-only operation or every channel/rate.
The iPhone model, iOS/AUM versions, exact mixer mode/sample rate, input/return
channel numbers, buffer size, latency and test duration were not recorded.
No packet trace, selected-alternate trace, sustained-load test, mixed/stereo
alternate test, or MIDI compatibility result is available.

The user identified this exact earlier image. The later generator/editor
mainline and its startup-guard revision both failed normal boot; the iPhone
result must not be attributed to those images.
