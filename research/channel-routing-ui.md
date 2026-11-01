# Channel-source selection with SELECT and TEMPO

This investigation implements the requested gesture: hold one destination
channel's SELECT button and turn TEMPO to change its input source. The source
label occupies the four-character TEMPO display during the hold. Releasing the
button restores the original display and normal encoder behavior.

The UI extension has original-instruction and compiled-code tests. These are
offline results; no physical panel, audible routing, or flashing result is
claimed by this report. The audio-routing implementation and its evidence are
separate.

## Original firmware evidence

All addresses in this report belong to the main application from the exact
supported original firmware. For resident `0x600xxxxx` code, the decoded image
offset is its runtime address minus `0x60000000`. The SRAM text API has its own
startup relocation, as noted below.

| Finding | Original location | Evidence |
| --- | --- | --- |
| Panel event callback registration | Decoded `0xf5d8`, runtime `0x6000f5d8` | Pointer is `0x60010b49`, loaded at `0x6000f448` and registered by `0x6000f740`. |
| Callback ABI | `0x60010b48` | `mov r1,r0; ldr r0,[pc,#0xac]; b 0x60010a94`: the callback receives the event packet in r0. |
| Physical press and release events | `0x60010a94` | Event type 2 calls `0x600106e2`, enqueueing logical type 5; type 1 calls `0x600105b4`, enqueueing type 6. |
| Physical encoder movement | `0x60010a94` | Type 4 loads a signed 16-bit delta from packet offset 2 and the encoder ID from offset 1, then calls `0x6001077e` to enqueue logical type 7. |
| Original event queue | `0x60010580`, `0x60010602`, `0x600106bc` | Twelve-byte records are queued and drained into `0x60010636`. |
| Live logical held-key bits | `0x60010636` and its dispatch branches | Press sets and release clears the bit for the unchanged key ID at `0x605129a4 + id/8`. |
| SELECT IDs | `0x60016532` | Subtracts `0x29` from key IDs `0x29..0x33`, operates on the 11 channel-selected parameters and current-channel parameter `0xfb`, and honors existing links for channels 1/2 and 3/4. |
| TEMPO encoder ID | `0x600109d8`, `0x6001782e` | Encoder 1 reaches the tempo adjustment path. In normal internal-clock mode it adjusts system parameter `0x1a`; encoder 0 follows the VALUE path. |
| Normal main page | `0x6000fd34`, `0x6000fc4e` | Initializes the current-page short at `0x600b4b5e` to zero. Other pages use the original event handling. |
| Normal boot mode | `0x60010a4e`, literal `0x60010bf8` | Original panel setup stores the boot mode at `0x600b4b94`; the extension is enabled only for mode zero. |
| Modal display busy query | `0x60018258` | Loads a global pointer from literal `0x600182ac`, reads `0x600b53a4`, and returns whether it is nonzero. Its incoming r0 is ignored; the extension nevertheless passes the original renderer's `0x605144cc` context. |
| TEMPO display renderer | `0x60013356` | Original normal-tempo branch uses display index 1. VALUE is rendered separately by `0x60013740` using index 0. |
| Text display API | `0x60054f84` to SRAM `0x01002a00` | Draws a fixed number of characters from the supplied buffer. Display 1 has four positions; display 0 has three. |

The SELECT identity also agrees with the firmware's parameter-name table:
`CHANNEL SELECT(1)` at decoded offset `0xabd3a` is referenced by the channel
parameter name table at `0x6f6b4`; `CURRENT CHANNEL SELECT` at `0xb09d7` is
referenced at `0x6fab4`. The routing destination order is the existing physical
strip order: 1, 2, 3, 4, 5/6, DIGITAL, USB1, USB2, USB3, USB4, PC.

The test executes the original decoder, queue, key-bit update and encoder
dispatch for all 11 SELECT IDs, both encoders, and signed-delta boundaries.
It also executes the original encoder handler to observe encoder 1 reaching
the tempo parameter. The physical switch-to-logical-ID wiring is not emulated;
that remains a bench check, distinct from these firmware observations.

## Gesture behavior

The extension uses the original held-key bitset rather than a new timer or
independent key-state copy. It activates only when:

- The panel is in normal boot mode and on the main page.
- The modal display is idle.
- Exactly one SELECT button is held.
- No other physical button in the original `0..0x54` range is held.

This preserves the existing multi-button gestures, including pressing two
SELECT buttons for stereo linking. It also leaves menus and special boot modes
under their original handlers.

SELECT press and release always go through the original registered callback.
The extension does not delay, synthesize, or suppress a normal SELECT action.
Consequently, an ordinary SELECT tap retains its existing selection semantics.
When the gesture is active, only TEMPO movement is intercepted. A positive or
negative nonzero event changes the source by one step; zero does not change it.
The original tempo event is not enqueued. VALUE movement remains unchanged.

The display overlay is also installed at the original tempo renderer, so a
normal periodic refresh cannot overwrite the source label while the gesture
is active. Releasing the last held SELECT redraws the original tempo display.
SELECT actions on another page never force a main-page display redraw.

The audio API permits source editing in Mixer and Control Surface modes. In
External Mixer mode it returns the four-character label `modE` and ignores
source adjustments, preserving the remembered routes. While SELECT remains
held, TEMPO movement is still consumed, so it changes neither source nor tempo.
Release restores the original display and tempo handling. Diagnostic DSP
programs use the same blocked indication. These guards belong to the audio
component; the UI needs no additional mode state.

The route API is supplied by the audio-routing component:

```c
unsigned mx1_route_get(unsigned strip);
void mx1_route_adjust(unsigned strip, int delta);
const char *mx1_route_label(unsigned strip);
```

`mx1_route_label` must return at least four initialized display bytes, padded
with spaces when needed. A fifth NUL is permissible. The original text API
does not stop at a NUL while drawing its four-character field. The UI adds no
writable state, storage format, polling task, or sample-rate processing.

## Binary hooks and trampoline

`patches/channel_routing_ui.c` exports `mx1_route_ui_event` and
`mx1_route_ui_display`. The common routing builder guards and replaces the
original event callback pointer at decoded offset `0xf5d8`.

The tempo renderer entry at `0x60013356` is two bytes past a word boundary.
Its first ten original bytes are:

```text
fe b5 04 46 c5 48 04 f0 7c ff
```

They represent the original push, context move, PC-relative literal load, and
call to the modal-display query. The replacement is a two-byte NOP followed
by a word-aligned `ldr.w pc,[pc,#0]` and a four-byte Thumb target. No instruction
is partially overwritten.

`patches/channel_routing_ui.S` provides an explicit displaced-instruction
trampoline. It reproduces the register push and context move, substitutes the
resolved value `0x605144cc` for the old PC-relative literal, calls the untouched
`0x60018258` query, and resumes at `0x60013360`. The original resume address is
entered with the Thumb bit set. The trampoline does not copy a PC-relative
instruction to a new address and hope that its reference remains valid.

## Reproducing the UI evidence

Run the UI harness from the repository root:

```bash
.venv/bin/python tools/routing_ui_verify.py inputs/MX1_UPD.original.bin \
  --ui-only --output analysis/channel_routing_ui_only_verification.json
```

This links the actual UI sources with an explicitly inert route API fixture.
It generates no update container and is not a flashable experiment. The source
API calls are intercepted in the emulator. Its size includes the test stubs
and is not the size of a complete routing implementation.

Once the integrated routing candidate exists, run the same tests against its
actual main application and symbols:

```bash
.venv/bin/python tools/routing_ui_verify.py inputs/MX1_UPD.original.bin \
  --build build/routing-probe \
  --output analysis/channel_routing_ui_verification.json
```

The main routing verifier can also import
`verify(original: bytes, patched: bytes, build: dict)` from this tool. This API
tests exactly the supplied main component and its build symbols; it does not
compile or substitute a fixture.

The harness tests:

- Original physical event decoding, the original queue, logical key state,
  and signed encoder event delivery.
- The original distinction between VALUE and TEMPO.
- Exact callback and aligned renderer patch bytes.
- Original versus patched inactive display output, including other pages,
  other boot modes and modal-display state.
- Source adjustment on all 11 destinations, positive/negative/zero movement,
  release restoration, and normal TEMPO movement after release.
- Ordinary SELECT taps on every strip, with identical original press/release
  calls and no source adjustment.
- Unheld TEMPO movement through the original event pipeline to the tempo
  parameter adjustment.
- Every SELECT combined with each other physical key: 924 ordered pairs,
  covering all SELECT pairs, modifier IDs and bitset byte boundaries.
- Overlapping SELECT press/release order, menus, modal state and VALUE movement.
- Against the final candidate, actual compiled route APIs on all 11 strips in
  Mixer and Control Surface modes: selected-state changes, four-character source
  labels and the original task/event-8 posting call.
- Actual compiled External Mixer and diagnostic guards on all 11 strips:
  `modE`, remembered routes unchanged, no tempo or event-post side effect during
  the hold, and original tempo behavior after release.
- Preservation of r4-r11, the stack pointer and normal return control across
  every tested compiled/original entry.

The original character loop runs through its four positions. Final font/LED
delivery is stubbed, as are higher-level key actions, modal actions and parameter
storage. The panel-isolation groups intercept route calls; the final-candidate
integration groups execute the compiled route APIs unchanged. In those groups,
the original parameter getter supplies the requested mixer mode and the RTOS
post is recorded without scheduling the DSP task. Their call boundaries are
recorded explicitly. These tests therefore establish binary integration and UI
control flow under those assumptions. They
do not establish physical button wiring, LED appearance, real-time deadline
margin, source routing, or audio quality.
