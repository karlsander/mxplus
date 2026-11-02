# Channel routing: audio path and patch evidence

This is a new, independent main-application experiment for the repository's
frozen MX-1 1.05-generation image. It has compiled and passed offline ARM
instruction checks. No physical MX-1 audio, panel operation, flashing, recovery,
or real-time deadline margin has been established.

The audio implementation is
[`patches/channel_routing_audio.c`](../patches/channel_routing_audio.c), with
the UI contract in [`patches/channel_routing.h`](../patches/channel_routing.h).
The reproducible patch contract is
[`tools/routing_audio_patch.py`](../tools/routing_audio_patch.py); the candidate
instruction tests are
[`tools/routing_audio_verify.py`](../tools/routing_audio_verify.py). See also
[`channel-routing-validation.md`](channel-routing-validation.md) for independent
serial-I/O, coefficient, task, and factory-program evidence.

## Result and user-facing behavior

The candidate changes source-read operands in the existing DSP input block.
It adds no ARM sample-copy loop and no additional per-sample DSP instructions.
Each existing destination strip retains its original downstream processing and
controls. An explicit stereo source feeds the destination's two existing input
lanes; a single left or right source is copied to both lanes of a stereo strip.
The four mono strips offer only mono/single-side choices.

There are 53 menu entries including `Auto`. PC1 through PC9 mean consecutive
computer **playback** pairs 1/2 through 17/18, respectively. They are raw
computer-to-mixer lanes, before the stock USB/DIG connection selection. Selecting
a PC source does not depend on a different destination's connection selector.

| Display | Source |
| --- | --- |
| `Auto` | Current Roland source and connection policy for this destination |
| `An1 `–`An4 ` | Analog inputs 1–4 |
| `A56 ` | Analog inputs 5/6 as a stereo pair |
| `An5 `, `An6 ` | Analog 5/6 left or right as a mono source |
| `dIG `, `dI L`, `dI R` | Digital pair, left, or right |
| `US1 `–`US4 ` | Native AIRA USB pairs 1–4 |
| `U1 L`/`U1 R` through `U4 L`/`U4 R` | One side of a native AIRA USB pair |
| `rtn `, `rt L`, `rt R` | Raw analog Return pair, left, or right |
| `PC1 `–`PC9 ` | Computer playback pairs 1/2 through 17/18 |
| `P1 L`/`P1 R` through `P9 L`/`P9 R` | One side of a computer playback pair |

The requested split is selectable without changing the boot defaults: assign
`An5 ` to the original 5/6 strip and `An6 ` to USB2. Both can then use their
existing independent strip processing and faders. Routes reset to `Auto` on
boot; they are not saved to flash or scenes.

Routing copies a source. It does not remove that source from another strip.
The original Return bus and its AUX controls also remain available. To use only
the new Return destination, lower the original Return level. Returning an
externally connected AUX send to a strip with AUX send enabled can create an
external feedback loop; bench validation should begin with sends at zero.

Mixer and Control Surface modes use this input path. External Mixer mode uses
separate downstream computer/native selection. Entering that mode restores
stock operands and source policy, retains the desired routes in RAM, displays
`modE` while SELECT is held, and ignores route adjustments. Returning to a
supported mode reapplies the saved routes. Diagnostic DSP programs are excluded
because their instruction layout differs.

## Binary identity and address conventions

The complete original update must have SHA-256
`26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`.
Its decoded `app_main` component has SHA-256
`256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b`.

Resident main addresses are `0x60000000 + decoded offset`. The relocated hot
block starts at decoded offset `0x0d0b8c`, is copied to `0x01000300`, and is
originally `0xf3a4` bytes long. For a helper in that block, its decoded offset is
`0x0d0b8c + runtime_address - 0x01000300`. The extension begins immediately after
it at `0x0100f6a4`; the builder bounds the complete extension below `0x01010000`.

DSP program offsets in this report are **logical byte offsets**, not ARM
halfword addresses. The first logical halfword is the high half of a CPU-visible
little-endian 32-bit word. Thus logical halfword `p` is observed at CPU address
`0x40150000 + (p XOR 2)` for DSP0. The original upload routines also merge
partially covered boundary words. Simple byte concatenation of ROM chunks gives
the wrong result for the input block starting at logical `0x031a`.

[`tools/routing_audio_extract.py`](../tools/routing_audio_extract.py) executes
the original descriptor wrapper `0x0100bfe2`, uploader `0x0100ab32`, and boundary
writer `0x0100ab04`. Bulk DMA is modeled as a byte transfer. It reconstructs all
36 normal-program chunks and writes evidence under `analysis/routing-audio/`.
This executes ARM upload code; it does not execute the ESC2 DSP program.

## Where input selection occurs

The normal DSP0 graph descriptor table is at runtime `0x600ba008` (decoded
offset `0xba008`). Its input gain block starts at DSP logical `0x031a`, spans
`0x1e2` bytes, and is sourced from runtime `0x600b88e8` (decoded `0xb88e8`).
That chunk's source halfword for a logical offset `p` is at decoded offset
`0xb88e8 + ((p - 0x0318) XOR 2)`.

The following original input operands are guarded independently by the builder
and checked against the memory reconstructed by the original uploader:

| Destination | DSP logical operand offsets | Original operands |
| --- | --- | --- |
| Analog 1 | `0x328` | `0x6000` |
| Analog 2 | `0x33a` | `0x6001` |
| Analog 3 | `0x34c` | `0x6002` |
| Analog 4 | `0x360` | `0x6003` |
| Analog 5/6 | `0x376`, `0x38a` | `0x6004`, `0x6005` |
| Digital | `0x3ac`, `0x3c2` | `0x6008`, `0x6009` |
| USB1 | `0x3e2`, `0x3f8` | `0x600a`, `0x600b` |
| USB2 | `0x418`, `0x42e` | `0x600c`, `0x600d` |
| USB3 | `0x44e`, `0x464` | `0x600e`, `0x600f` |
| USB4 | `0x484`, `0x49a` | `0x6010`, `0x6011` |
| COMPUTER | `0x4ac`, `0x4bc` | `0x2010`, `0x2011` |
| Original Return bus, preserved | `0x4ce`, `0x4e0` | `0x6006`, `0x6007` |

The raw native source ordering is corroborated by two separate original paths:

* Serial-I/O initialization at `0x0100a282` configures input descriptors for
  the four analog/Return pairs at `0x3000`–`0x3007`, digital at `0x3008/9`,
  and native USB at `0x300a`–`0x3011`. The digital manager `0x60001404`
  selects input or output operation for its port.
* The input DSP block pairs these reads with gain coefficients whose original
  parameter callbacks identify analog 1–5/6, digital, USB1–4 and COMPUTER in
  that order. For example, global GAIN5 calls `0x6002536c` and sets coefficient
  `0x12`, used by the analog 5/6 block. The independent audit records the
  actual callback instructions and the associated initialized coefficient
  bank. Coefficients `0x01`–`0x0d` initialize to unity; only the first five
  native mute gates have additional direct users for analog gain changes.

This is stronger than guessing connector order from numeric slot addresses.
Physical connector-to-lane identity still needs the proposed single-input
hardware measurement.

## Why raw computer sources can be selected independently

The USB-B sample pump at relocated runtime `0x01009840` writes its 18 converted
playback words to `0x40101000`–`0x40101044`; capture occupies the next 18 words.
Those are hardware exchange ports, not a general-purpose ARM audio buffer.
The normal DSP prefix reads operands `0xa000`–`0xa011` and produces internal
scratch values `0x2000`–`0x2011`. Some scratch values have already been gated by
the stock digital/USB connection policy. Routing those gated scratch values
would make one destination's assignment affect another destination's source.
The candidate therefore reads the original raw `0xa000`–`0xa011` ports.

The read representation has additional original-program evidence. The factory
DSP0 descriptor at runtime `0x600cb780` (decoded `0xcb780`) uploads a program
from `0x600cad4c` (decoded `0xcad4c`) to DSP offset zero. Executing the original
uploader reconstructs these two import chains:

* DSP offsets `0x20`–`0x166` import all 18 raw PC operands `0xa000`–`0xa011`
  into ordinary DSP RAM `0x20`–`0x31`.
* DSP offsets `0x16a`–`0x220` import all 18 native operands `0x6000`–`0x6011`
  into ordinary DSP RAM `0x0c`–`0x1d`, with the Return pair in physical order.

Both use the same plain-copy read binding `0x0fe0` and corresponding `0x8fe2`
write binding. For example, PC and native imports occur in these original
instruction groups, with the previous read written in the following group:

```
0x002a: 7809 0fe0 8fe2 1fe4 9fe6 a001 0020 0035 a012
0x0170: 1e05 0fe0 8fe2 6001 000c
```

There is no extra normal-prefix `0x1040`/`0x44c7`/`0xbeda` arithmetic in these
raw imports. Together with the original shared-port variable descriptors and
CPU read/write helpers `0x0100bdfc`/`0x0100be62`, this supports using both raw
banks as compatible DSP audio operands. It is original DSP-program evidence,
not a numerical simulation or a measured bit-perfect audio result.

## Preserving destination independence and AUTO

Digital and native USB strips can also receive their own computer return. The
stock connection callbacks change the corresponding two embedded floats:

| Destination | DSP float locations | Original callback |
| --- | --- | --- |
| Digital | `0x1de`, `0x1f8` | `0x60027b44` |
| USB1 | `0x212`, `0x22c` | `0x60027b7c` |
| USB2 | `0x246`, `0x260` | `0x60027bf8` |
| USB3 | `0x27a`, `0x294` | `0x60027c20` |
| USB4 | `0x2ae`, `0x2c8` | `0x60027c48` |

An explicit assignment sets those destination-specific PC terms to zero. This
prevents, for example, selecting analog 6 on an unplugged USB2 strip while also
hearing computer playback 11/12 on that strip. No other source or destination is
changed by that suppression.

Returning to `Auto` restores the *current* policy, not a value saved before a
possible hotplug. The implementation queries the same parameter accessor used
by the stock callbacks, runtime `0x6001a896`, object `0x600b5390`: mode `0x19`,
digital direction `0x0c`, and connection parameters `0x92`–`0x96`. Offline tests
execute all five actual stock callbacks and compare their emitted float command
requests with the candidate's restoration across modes, connection states and
digital directions.

Mode `0x19 == 2` sets global DSP floats at `0x326` and `0x508` through the
original callback `0x60027c70`. Those downstream mode switches are why External
Mixer receives stock restoration instead of an unsupported routing claim.

## Task context, live writes and reloads

The UI performs only an atomic route-byte store and the original event post
`0x0100e266(task=0x6051dea8, event=8)`. It never writes the DSP programming port.
The DSP task has higher priority than the UI task, so its routing flush cannot
be interrupted by another UI route edit. If an existing DSP event observes the
new byte before the explicit post, the subsequent post is harmless and the
latest state remains queued.

The sole audio hook is the original event-8 queue handler at main runtime
`0x60024bae`, decoded offset `0x24bae`. Its exact displaced bytes are:

```
2d e9 f0 43 87 b0 ea f7 02 fb
```

They implement the original register push, 28-byte stack allocation, and call
to `0x6000f1bc`. A flag/register-preserving absolute jump enters the extension;
the trampoline recreates this prologue and resumes at `0x60024bb8`. The entire
original parameter queue drain and epilogue execute before the new flush.
The routing harness checks the return stack and all AAPCS callee-saved registers.

The flush calls original raw writer `0x0100ab04` and float writer `0x0100baee`.
They program DSP0 through command/data registers `0x40100900/04`. Using the
existing DSP task avoids adding a competing UI-side command writer. The test
also feeds one real queued connection update through the original group
metadata, callback lookup and USB2 callback, then observes its stock `1.0`
selector writes followed by the routing flush's `0.0` writes.

A rate change can reload the complete DSP program through event `0x200`.
The original reload path queues parameter groups through event 8 afterward.
Active route operands are therefore reasserted on every parameter drain; the
implementation does not trust its previous-application cache after a graph
reload. The cache is used only to restore a destination that was previously
explicit and is now `Auto` or temporarily disabled.

The write pairs follow the original driver's protocol. Stereo source changes
still require sequential writes, and the ARM task is not synchronized to a DSP
frame boundary by this patch. Offline evidence therefore does not establish
click-free transitions, a one-frame stereo-atomic change, or programming-port
completion timing.

## Verification boundaries

The candidate audio harness executes the compiled route API, actual hook and
trampoline, original parameter drain control, original callback lookup and
connection callback, original float conversion and DSP writers, and original
program upload/boundary logic. It verifies every permitted source/destination
choice, duplicate sources, the requested 5/6 split, suppression and restoration
of PC terms, diagnostic exclusion, External Mixer behavior, graph reload and
four-character source labels.

Its models are explicit: parameter-store values, supplied queue contents,
recorded RTOS posts, bulk DMA transfers, DSP programming-port storage, and
symbolic source tokens. The DSP arithmetic itself is not emulated. The float
programming requests are checked as requests; the hardware's immediate-format
conversion is not replaced with an invented numerical implementation.

Final integrated evidence belongs to `build/routing-probe/audio-verification.json`
and `build/routing-probe/arm-verification.json`. Source and container hashes
must be read from the matching build report. The experiment retains the
physical front-end gain and input availability of each selected source; it
cannot create an absent external clock, connected AIRA device, or computer
playback stream.

## Encoder freeze and writable state, 2 November 2026

The earlier state-placement assumption was wrong: main SRAM code becomes
read-only when the original MPU setup runs. The first route-byte store faults
before the event post. Desired and applied route bytes now occupy a guarded
24-byte reservation immediately after original writable BSS, initialized by
an extended startup clear. See [the MPU investigation](routing-state-mpu.md).
All audio-control instruction cases now enforce read-only code pages.
