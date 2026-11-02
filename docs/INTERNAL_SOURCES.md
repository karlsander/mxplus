# Internal sources

`NSE` and `BD` are part of the sole mainline image. Both remain untested on a
physical MX-1: their first integrated image failed before the panel lit, and
the current startup-guard correction awaits testing. See the
[boot investigation](BOOT_REGRESSION.md). They were recovered from the user's 2 November archive and
adapted to the current guarded builder, writable-memory layout, source end
stops and routing persistence. No old firmware variant is maintained.

## Controls

Select a channel, then press its SELECT again to enter source editing. SELECT
blinks. Turn TEMPO to choose `NSE` or `BD`, after the last computer channel.
Press SELECT again to return to normal editing with a steady SELECT light.

- `NSE`: continuous shared mono white noise, including while transport is
  stopped. Nominal digital peak is approximately -12 dBFS.
- `BD`: an independent mono bass drum voice and 16-step pattern for each strip.
  The pattern starts empty. Start transport to play it. Nominal peak is
  approximately -6 dBFS before the destination channel's processing.
- While editing a BD source, tap a pad to toggle its note on release. Hold a
  pad and turn VALUE to change pitch (-24 to +24 semitones around a 55 Hz base),
  or TEMPO to change decay (0–100, mapped approximately to 30–1,500 ms).
  Release after an edit does not toggle the note. Multiple held pads cancel
  taps and consume ambiguous encoder input.
- Enabled steps are violet, the playhead uses a different violet, and the held
  step is white. CHANNEL SETTING BFX focus retains its stock pad controls;
  use GAIN, PAN, TONE, AUX or FADER focus for BD notes. Modifier gestures stay
  with the original firmware.

Source assignments save in snapshots and through stock delayed system autosave.
BD patterns, pitch and decay currently live in RAM only: snapshots do not store
them, and power-on restores empty patterns. No extra autosave routine is added.
The no-selection gradient remains intact, including at startup; ordinary
same-channel SELECT taps toggle normal/source editing instead of deselecting.

## Integration and evidence

All addresses below refer to the main application. Original sample callback
registration at decoded `0x168c` (runtime `0x6000168c`) changes from pointer
`0x01009841` to the mainline wrapper. The original relocated USB sample pump
at `0x01009840` executes first, including mainline's capture-first fix at
runtime `0x01009a06` / decoded `0xda292`. The wrapper then publishes generator
words at DSP0 exchange indices `0x40..0x4b` (CPU `0x40101100..0x4010112c`).
Routing uses operand `0xa040` for noise and `0xa041 + strip` for BD, duplicated
on stereo destinations. Diagnostics skip generator publication. External Mixer
clears the active generator mask when routing drains.

Cold startup owns no generator ports. An all-Auto callback leaves the inferred
bank untouched, including after returning from diagnostics. Selecting a source
establishes ownership; removing it clears only its previously owned output.
Diagnostic return resets active voices without treating all twelve ports as
previously owned. The inactive SELECT overlay returns before parameter lookup;
startup/view guards also precede the SELECT press overlay's mixer query.

Clock hooks at decoded `0xa7dc`, `0xa810` and `0xa894` (runtime base `0x60000000`)
retain the original start/stop/step bodies and publish a separate modulo-16
position. They do not inherit BFX last-step shortening. The sample renderer
uses integer arithmetic, aligned word publications and per-strip voice state;
it allocates no memory and calls no parameter/storage routines in the IRQ.

Panel hooks are at decoded `0xf5d8`, `0x10516`, `0x10538`, `0x140c2`, `0x13740`,
`0x13356` and `0x14692`, all at runtime `0x60000000 + offset`. The last hook
retains the stock SELECT renderer and requests its existing blink mode 3 for
LED `0x34 + strip`. Original SELECT action `0x60016532` still executes; the
wrapper replaces only ordinary same-channel deselection with the edit toggle.
Original modal, multi-key and stereo-link decisions remain in that body.

The [memory layout](MAINLINE.md) records the initialized writable data and
read-only code reservations. Every overwritten instruction/literal, trampoline
target and callback is guarded and recorded in the [build report](../build/mainline/build-report.json).

Offline reproduction includes:

- Actual compiled state, clock, sample publication and numerical PCM checks.
- USB pump trace comparisons with mainline capture-first behavior, with
  generator rendering both inactive and active at all three sample rates.
- Protected code pages, dirty startup, allocator separation and original boot,
  updater and component-preservation checks.
- Original panel decoding, queue/held-key updates, SELECT body, font/LED
  dispatch, compiled source editing and held-step editing. Parameter storage,
  dispatch edges and hardware delivery are explicitly modeled in those tests.
- Snapshot/restart tests include the new source IDs and retain all older IDs.

The spare DSP exchange-bank interpretation, actual generator sound/levels,
clock jitter, LED appearance, USB interaction and worst-case IRQ deadlines
remain physical-test questions. Executed instruction counts are not CPU cycles
or measured timing. The recovery archive's offline reports are historical
research, not validation of this candidate. See the [import record](../evidence/internal-sources-import-20261102/README.md).
