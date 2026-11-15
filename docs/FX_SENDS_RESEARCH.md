# Additional FX sends: implementation investigation

Status: **incomplete; no additional sends implemented**. This investigation is
based on main `3b3a43d` (the merged channel-control foundation). It does not
change the builder, linker, candidate, or physical mixer. The channel pages
remain empty. The active candidate remains
`dad7fbf2825a7a7ec82470cd7e4127d5567aa1cb1bed5ff3efb09c971a329ca3`.

## Requested behavior

All editing below requires a selected channel. No selection restores the
ordinary tempo surface. Existing SELECT + TEMPO source routing and mastering
ownership retain priority.

| Control | Turn TEMPO | Hold control and turn TEMPO |
| --- | --- | --- |
| First button (SHUFFLE) | Selected channel's alternate external send level | Global destination: Off, SEND R, or PHONES |
| Second button (FINE) | Selected channel's internal FX send level | Global internal FX type |
| Third button (SYNC) | Global internal FX parameter | Global internal FX time parameter |
| Fourth button (TAP) | Reserved empty page | Reserved |

Both new sends follow the **existing AUX pre/post-fader setting**, as specified
by the user. In SEND R mode, the alternate send is mono before pan; the normal
AUX becomes a mono send on SEND L. PHONES mode replaces ordinary headphone
mixing. Off restores ordinary output behavior. These are destination modes of
one shared external bus, with independent channel levels, not destinations
chosen independently for each channel.

The internal bus must be continuously active and have independent input levels,
effect type, parameter and time. Its return should join the final mix without
being processed again by MASTER FX. The preferred implementation preserves all
MASTER FX, including its delay while the send runs reverb. The user also
authorized investigating a fallback that removes delay from MASTER FX while
retaining other MASTER FX. No fallback has been enabled.

The requested DELAY family contains eight variations, including Room, Hall and
Reverb Mod; see [Roland's MFX variation list](https://support.roland.com/hc/ja/articles/4404526414363).
Those eight panel variations must be mapped to their original preset data and
algorithm/control combinations. They are not equivalent to the twenty internal
algorithm IDs examined below. Saved values, safe destination transitions and
tail handling still need an implementation design; this document does not
claim persistent settings or click-free switching.

## Reproducible original-instruction findings

Run from the repository root with the pinned dependencies:

```sh
.venv/bin/python tools/fx_sends_audit.py --check
```

The independently written [audit](../tools/fx_sends_audit.py) checks both the
whole stock update hash and decoded main hash, executes original main ARM
instructions, and compares [deterministic evidence](../analysis/fx-sends-audit.json).
It is not a second firmware builder. Its data is from the frozen original
image, not a claim about a later firmware candidate.

Resident main functions use `runtime = 0x60000000 + decoded offset`.
Relocated helpers use `decoded = 0xd0b8c + runtime - 0x01000300`.
The report records main component addresses and DSP core separately. A DSP
logical byte offset is not an ARM address; upload word/halfword ordering is
described in [routing evidence](../research/channel-routing-audio.md).

### AUX and headphone control ownership

The actual stock constructor at main decoded `0x24228`, runtime `0x60024228`,
establishes the original DSP objects before the callback cases. The callbacks,
soft-float conversions, descriptor resolution and final coefficient/embedded
float writers execute unchanged. No parameter getter or writer is stubbed in
these cases. ABI checks verify callee-saved registers and the return stack.

| Stock control | Main decoded offset / runtime | Observed destination |
| --- | --- | --- |
| Eleven channel AUX levels, global IDs `0x130..0x13a` | `0x299d6 + 10*n` / `0x600299d6 + 10*n` | DSP1 coefficient indices `0x2d..0x37` |
| AUX pre/post selector, global ID `6` | `0x29b98` / `0x60029b98` | DSP1 embedded float at logical `0x1a88` |
| Return routing selector, global ID `7` | `0x29bbc` / `0x60029bbc` | DSP1 embedded float at logical `0x1a34` |
| Headphone level, global ID `0xac` | `0x27cc4` / `0x60027cc4` | DSP0 coefficient `0x28` |
| Headphone mix, global ID `0xad` | `0x27cce` / `0x60027cce` | DSP0 coefficients `0x26`, `0x27` |

The audit executes all 128 AUX levels for each of eleven channels, both states
of both routing selectors, and three settings for each headphone control:
1,418 callback cases. The eleven AUX gain tables are identical, strictly
increasing from zero to unity. The pre/post callback writes exactly command
`0x40071a88` to `0x40100900`, then zero or float unity to `0x40100904`.

These are control/write observations. They do not prove the numerical DSP
arithmetic, mono normalization, physical connector assignment, or which
additional pre-pan operands can safely feed an independent bus. In particular,
changing the headphone mix coefficient does not create an independently
controllable eleven-channel send mixer.

### Existing effect slots are owned by MASTER FX

The original type-change path at main decoded `0x2b132`, runtime `0x6002b132`,
alternates the slot selector at `0x600ccdbc`. Starting from slot zero, three
calls with its first argument equal to one select slots **1, 0, 1**. A permanent
send in either slot would therefore be overwritten by this unchanged path.
The normal MASTER FX selection path at `0x6002ab9a` and COMBI path at
`0x6002ac4a` also manipulate this shared selector; the latter two are inspection
leads, not covered by the three executed type-change cases.

The audit separately executes the loader prefix at decoded `0x29ee4`, runtime
`0x60029ee4`, for all twenty internal algorithms in both slots. It records the
actual arguments at entry to the live transaction `0x60026f66`, including the
selected program/data descriptors, slot destination and selector argument.

Both program variants exist in the original image:

| Slot | Program descriptor-pointer table (main runtime) | DSP1 logical program start |
| --- | --- | --- |
| 0 | `0x600caaac` | `0x4000` |
| 1 | `0x600cab4c` | `0x6000` |

All forty program chunks were reconstructed through the original uploader and
boundary writer, using the existing explicit bulk-DMA byte-copy model. The
largest chunk is 2,348 bytes. These chunks fit their separate 8 KiB program
intervals, but **program space is not processing headroom**. The audit does not
establish that simultaneous algorithms have independent coefficients, scratch
data, external delay memory, or sufficient execution time. Data descriptor
locations and extents are recorded as leads, without asserting full ownership.

The three slot-alternation cases model parameter queries and stub the loader
and subsequent effect setup. The forty loader-prefix cases stub parameter-view
construction and coefficient clearing, then stop before the live load
transaction. Program upload cases execute the original upload path separately.
This separation prevents upload tests from being presented as full effect-load
or effect-execution tests. MMIO writes are recorded storage; no physical DSP
accepts them, and no audio or real-time deadlines are measured.

## Remaining implementation boundary

The following work remains necessary before a candidate can implement this
request without relying on guessed DSP semantics:

1. Establish the DSP mixer packet operations, accumulator dependencies and
   channel taps for pre/post-fader, pre-pan mono sends, including stereo
   normalization, mute and fader-curve behavior. Reserve disjoint instructions,
   coefficients and scratch state for two independent additional sums.
2. Establish SEND and PHONES output operands and normal-path restoration.
   Account for live mode changes, queued stock headphone/AUX updates, graph
   reloads, scenes and External Mixer mode. Default new levels to zero and
   alternate output mode to Off.
3. Establish the complete delay/reverb state and external-memory ranges for
   both effect instances. Isolate the send's ownership from MASTER FX type
   changes, bypass, COMBI, parameter replay and sample-rate reloads. Decide
   between a second independent instance and the authorized delay-only fallback
   using that evidence.
4. Add the requested controls only once they operate those real buses; retain
   held-key ownership across deselection/modes and prevent stale-held gestures
   from editing a different channel or clock settings.
5. Produce guarded mainline patches, exercise original control/load paths and
   before/after routing cases, regenerate artifacts, then run full reproduction
   and the committed-artifact gate. Independently measure audio and worst-case
   DSP timing on hardware at 44.1, 48 and 96 kHz with simultaneous MASTER FX.

No DSP instruction patch is emitted by this investigation. A passing audit
establishes the stated stock behavior only; the additional-send feature remains
unfinished.
