# Additional channel sends

**Offline candidate only; no physical audio, DSP deadline or installation acceptance.**
The sole mainline build implements an alternate external send and an independent
internal effect send. Both follow the existing AUX pre/post setting. Their
levels and bus settings are volatile: scenes and restart do not save them yet.
All new channel levels start at zero; the alternate destination starts Off.

## Controls

Select a channel, then use the right display and TEMPO dial:

| Button | Press, release, then turn | Hold and turn |
| --- | --- | --- |
| SHUFFLE | Alternate send level, `A000..A127` | Global destination: `OFF`, `Sndr`, `Phon` |
| FINE | Internal effect send level, `F000..F127` | Global effect: Stereo, Pan, Cross, Stereo & Pan delay, Spiral, Room, Hall, Reverb Mod |
| SYNC | Global parameter, `P000..P127` | Global time, `t000..t127` |
| TAP | Reserved, `----` | Reserved |

The parameter is feedback for the delays and Spiral, density for the reverbs.
The full [internal engine parameter inventory](FX_ENGINE_PARAMETERS.md) records
the additional stock controls behind these two send knobs.
Time controls delay time (10–5979 ms), both Spiral pre-delays, or reverb time.
The time display is a normalized 0–127 control, not milliseconds. Internal delay
time is independent of MASTER tempo sync. Initial parameter/time are 64/10.
Selecting another variation retains these two knob values while restoring the
other settings from that variation's factory preset.

Levels belong to the current channel; destination, variation, parameter and
time belong to the shared buses. Holding a button across a channel change does
not carry its global-edit gesture to the new channel. Tempo settings become
available again when no channel is selected. SELECT + TEMPO source routing and
mastering mode retain priority. [Control ownership details](CHANNEL_CONTROLS.md).

`Sndr` averages the existing stereo AUX onto SEND L and the alternate bus onto
SEND R. The alternate tap is before pan. Mono channels retain unity at full
send; stereo channels are averaged for SEND R. `Phon` sends the alternate bus
in stereo through the headphone output, overriding headphone MIX; headphone
volume still works. Leaving `Phon` restores the **current** stock MIX setting.
Off restores stereo AUX and the normal headphone path. New sends are disabled
in External Mixer mode and their controls show `modE`; diagnostic programs do
not receive normal send-policy writes.

PRE follows the stock AUX behavior, including ignoring channel mute/fader.
POST includes both mute and fader. Internal sends follow channel pan; alternate
sends do not. Their tap is after channel BEAT FX. The internal return is wet
only and joins the final mix after performance MASTER FX, so it cannot feed
that effect or itself. The ordinary master level/mastering output chain remains
downstream.

## DSP and memory design

MASTER uses original slot 0 and the internal bus uses original slot 1. All 20
MASTER algorithms, including delay/reverb, remain available. Reserving slot 1
removes the stock two-slot MASTER type crossfade: the master return bypasses
during loading. Internal type changes clear that bus's old tail; ordinary
level/parameter/time changes do not reload it. The internal engine stays enabled
when its inputs are zero, allowing tails to finish.

The original data-descriptor table uses entries 4–38 for slot 0 and begins
slot 1 at entry 39. Across all 20 algorithms, nonzero encoded base addresses
stay in separate bands: `0x491500..0x6372ff` and `0x637300..0x7fffff`.
The implementation preserves these descriptor payloads. This is evidence for
reusing the existing two-slot allocation, not a physical test of every dynamic
delay address, rate or feedback state.

No third delay instance or ARM audio renderer is added. Factory slot-1 DSP
programs and their original initialization/control routines are reused. The
new arithmetic runs on DSP1. The original conditional slot calls, loader
gates and programming transaction remain intact, including the post-mixer's
first mute marker. No sample interrupt callback is changed.

Every ARM address below belongs to **app_main**. Resident decoded offsets equal
runtime minus `0x60000000`. Relocated private code uses the first startup copy,
decoded `0xd0b8c` → runtime `0x01000300`.

| Resource | Placement / original evidence |
| --- | --- |
| New mixer / output kernels | DSP1 logical program bytes `0x2000` / `0x2800`, below original MASTER `0x4000` and internal `0x6000` slots |
| Per-channel gains / policy | DSP1 coefficients `0x80..0x9a`; original controls occupy through `0x7e` |
| Same-frame bus sums / mono temporaries | DSP1 data words `0x20b0..0x20b5` |
| New ARM code, program bytes, descriptor table | `0x60664000..0x60666000` reserved; actual used size in build report |
| New control state | SRAM `0x010174e0..0x01017508`, 40 bytes |
| SDRAM heap | Start moves from `0x606634d0` to `0x60666000`; end stays `0x62000000` |
| Normal DSP1 descriptor count/table | Decoded `0x777c4`; 18 → 20 descriptors, including both new kernels |
| Mixer extension branch | Original DSP1 `0x1ac4`; source in main decoded `0xbb448` chunk |
| Output extension branch | Original DSP1 `0x1ace`; source in main decoded `0xbbd4c` chunk; original marker at `0x1aca` retained |
| Effect loader wrapper | Main decoded `0x29ee4`, runtime `0x60029ee4` |
| Graph reload wrapper | Main decoded `0x267b4`, runtime `0x600267b4` |
| MASTER slot-selection arithmetic | Main decoded `0x2abfe`, `0x2acce`, `0x2b150` |

The original AUX level curve at `0x60077af4` supplies both new level controls.
Stock pan, mute and fader coefficients are read directly by the new mixer.
The first eight factory records at `0x60060ab0`, stride 652 bytes, select
algorithms 1, 3 and 4. Internal program reads of `0x2006/7` are redirected to
`0x20b0/1`; all MASTER program bytes remain unchanged. Slot 1 already returns
its own scratch `0x0100/1` to `0x2002/3` in the original image.

Original callback `0x6002a39c` sets the selected instance's dry level; zero
removes dry feedthrough. `0x6002a9da` enables that instance. Parameter callbacks
run with selector `0x600ccdbc` temporarily set to 1, then restore it to 0 before
the DSP task returns. Internal settings do not modify MASTER parameter storage.
The loader's ordinary MASTER parameter replay finishes while the new return
gate is zero; independent factory settings replace it before the return opens.

Startup copy eight loads the new code. Decoded literals `0x134/138/13c` describe
that copy, `0xd76c` excludes its region from allocation, and `0x108` extends BSS
clearing to `0x7480` bytes. The final original SDRAM zero ends at `0x606634d0`.
Original stack/heap boundary helper, private pools and MPU setup are unchanged.
This costs 11,056 bytes of the old SDRAM heap, including alignment/headroom.
The placement has historical boot evidence, but that does not validate this
candidate's new DSP behavior. [Historical placement](SDRAM_CODE.md).

## Evidence and remaining hardware work

- [Build report](../build/mainline/build-report.json): input/component hashes,
  original/replacement bytes, DSP logical offsets, veneers, section bounds and
  initialization. Original update, boot programs, updater, panel payload and
  the predecessor's USB application are preserved.
- [Send verification](../build/mainline/extra-sends-verification.json): 480
  numerical mixer/output cases, all 40 original effect uploads, eight internal
  variations, live edits, destinations and reset guards. All 20 MASTER loaders
  leave slot-1 program/coefficient memory unchanged.
- [Memory verification](../build/mainline/sends-memory-verification.json): actual
  original heap creation and allocation through exhaustion, preserving the
  entire reserved interval.
- [Channel verification](../build/mainline/channel-controls-verification.json):
  original selection behavior, hold ownership, endpoint clamps, every effect
  and destination, and parameter versus time gestures.

The independently written emitter/model uses A arithmetic and FE transfers
found in the original MX-1 mixer. Encoding and parallel-operation semantics
were cross-referenced against [enorrmann's primary ESC2 investigation, sections
6 and 10](https://github.com/enorrmann/roland-plugout-reveng/blob/34a25b46b63d807e3b42407914258ac46d369515/docs/vol2_dsp_core_isa/instruction_set_reference.md).
Those hardware measurements concern related Roland devices, not this MX-1.
A local 60-case cross-check agreed with that pinned reference emulator. No
upstream implementation is imported and no network dependency enters reproduction.
Some packed factory instruction classes still differ; this is not complete
factory DSP source recovery.

The numerical model covers the new arithmetic, not complete factory delay RAM
or physical execution. ARM tests execute factory loaders/initializers, but model
program DMA, data-memory transport, command completion, RTOS waits and parameter
database boundaries as recorded in the report. Instruction counts are not
timing measurements. Simultaneous algorithms and worst-case feedback/tail
behavior still need physical audio and deadline measurements at 44.1/48/96 kHz,
with USB audio/MIDI and mastering active. Check destination changes, MASTER
type changes/bypass/COMBI, rate/mode reloads, headphone MIX restoration, channel
mute/pan/fader and zero-send dry equivalence. No hardware was accessed here.
