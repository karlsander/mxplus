# Channel source routing

This independent firmware experiment assigns a source to any of the MX-1's
eleven physical channel strips. It supports the requested 5/6 split onto USB2,
and extends the same mechanism to analog, digital, AIRA, return and computer
sources. More than one strip can read the same source.

**Status: built and verified offline; no physical MX-1 audio, panel operation,
installation or recovery has been tested.** The candidate is
[`MX1_CHANNEL_ROUTING_UNTESTED.bin`](../build/routing-probe/MX1_CHANNEL_ROUTING_UNTESTED.bin).
Its [build report](../build/routing-probe/build-report.json) records the exact
input, output identities, source hashes, patch bytes and memory placement.
It is a separate main-application experiment, with the original USB transport.

## Using the source selector

On the normal main page, hold the **SELECT button of the destination strip**
and turn **TEMPO**. The four-character tempo display shows that strip's source.
Each nonzero encoder event advances or reverses one source choice. Release
SELECT to return the display and encoder to their normal operation.

The destination order is 1, 2, 3, 4, 5/6, DIGITAL, USB1, USB2, USB3, USB4 and
COMPUTER. Only the strip whose physical SELECT is held changes its assignment.
The existing SELECT press/release actions still run, so an ordinary tap keeps
its normal channel-selection behavior. VALUE remains unchanged.

The selector is inactive while another physical button is held, two SELECTs
are held, a menu is open, or a modal display is busy. This preserves the
original multi-button gestures. A normal display refresh cannot overwrite the
source label during an active hold.

### Split inputs 5 and 6 across two faders

1. Hold **5/6 SELECT**, turn TEMPO until the display reads **`An5`**, then release.
2. Hold **USB2 SELECT**, turn TEMPO until the display reads **`An6`**, then release.

The 5/6 strip reads analog input 5 on both sides of its stereo path. USB2 reads
analog input 6 on both sides of its stereo path. Each retains its destination
strip's processing and fader. The implementation suppresses USB2's old computer
return contribution, including when no AIRA device is plugged into USB2.

To undo the split, select **`Auto`** on both strips. `Auto` restores the original
source assignment and the current connection policy. It does not mean a
permanently hardcoded physical input.

## Source choices

There are **53 choices including Auto** on a stereo strip. The four mono strips
offer **37 choices**, skipping stereo-pair entries. Select a pair's left or
right member when assigning it to a mono strip. A mono source assigned to a
stereo destination is copied to both sides; the patch does not sum a stereo
pair into mono.

All labels occupy exactly four display characters, padded with spaces where
needed. The table omits trailing padding.

| Display | Source | Available on |
| --- | --- | --- |
| `Auto` | Original source and current Roland connection/mode policy | All strips |
| `An1`–`An6` | Individual analog inputs 1–6 | All strips |
| `A56` | Analog 5/6 stereo pair | Stereo strips |
| `dIG` | Digital stereo pair | Stereo strips |
| `dI L`, `dI R` | Individual digital left/right input | All strips |
| `US1`–`US4` | AIRA USB1–4 stereo pair | Stereo strips |
| `U1 L` / `U1 R` through `U4 L` / `U4 R` | Individual side of an AIRA input | All strips |
| `rtn` | Return stereo pair | Stereo strips |
| `rt L`, `rt R` | Individual return input | All strips |
| `PC1`–`PC9` | Computer playback stereo pairs, mapped below | Stereo strips |
| `P1 L` / `P1 R` through `P9 L` / `P9 R` | Individual computer playback lane | All strips |

The PC number identifies a stereo pair, not a single playback lane:

| Pair label | Computer playback lanes | Individual labels |
| --- | --- | --- |
| `PC1` | 1 / 2 | `P1 L` / `P1 R` |
| `PC2` | 3 / 4 | `P2 L` / `P2 R` |
| `PC3` | 5 / 6 | `P3 L` / `P3 R` |
| `PC4` | 7 / 8 | `P4 L` / `P4 R` |
| `PC5` | 9 / 10 | `P5 L` / `P5 R` |
| `PC6` | 11 / 12 | `P6 L` / `P6 R` |
| `PC7` | 13 / 14 | `P7 L` / `P7 R` |
| `PC8` | 15 / 16 | `P8 L` / `P8 R` |
| `PC9` | 17 / 18, the original COMPUTER stereo pair | `P9 L` / `P9 R` |

These are playback sources coming from the computer into the mixer. The patch
does not change the computer's capture channel map or add a USB audio driver.
All eighteen playback lanes require the existing multichannel playback path;
the original stereo alternate uses the last pair. An input must still have a
working signal and transport before source selection can make it useful.

### Duplication and existing paths

Assignment selects the raw input read before the destination's input gain,
effects and fader. It does not copy another strip's processed output. Two
strips assigned to `An6`, for example, share the analog input but retain their
own downstream processing. Changing either destination's source does not
change the raw source used by the other.

The source's original destination continues to operate unless its own
assignment or level is changed. This also applies to returns: selecting `rtn`
on USB2 adds a return path through USB2 while the original Return bus remains.
Use the original Return level if only the reassigned path is wanted. AUX send
controls retain their original behavior; a returned signal sent back through
the same external effect can create a feedback loop.

Analog input gain ahead of the ADC belongs to the physical input. Duplicating
an analog source cannot create independent analog preamps. Destination DSP
gain and fader controls remain in their original paths. An analog strip's
original GAIN callback also continues to control its original physical jack,
even if that strip reads a different source. Adjusting it can therefore change
the level of another routed strip that reads that jack. Source assignment does
not remap the physical preamp controls.

## Modes and saved settings

| Situation | Routing behavior |
| --- | --- |
| Mixer mode | Assignments apply after the normal parameter queue drains |
| Control Surface mode | Assignments remain available |
| External Mixer mode | Original routing is restored; a held SELECT shows `modE`; TEMPO movement during that hold changes neither routing nor tempo |
| Return from External Mixer | The remembered assignments in RAM apply again |
| Sample-rate/DSP program reload | Active assignments are reapplied on the subsequent stock parameter-queue notification |
| Diagnostic programs | No routing program writes |
| Power cycle | All strips start at Auto |

Assignments are held in RAM. They are not written into scenes or persistent
settings. The patch does not add a storage format or a flash-write operation.
External Mixer has a separate downstream source switch; preserving its stock
path avoids presenting an assignment that the active graph would bypass.

## How the patch works

The implementation changes the source operands in DSP0's existing input gain
block, at logical program offsets `0x0328` through `0x04bc`. Serial inputs use
the original `0x6000`–`0x6011` source bank. Computer playback uses the original
`0xa000`–`0xa011` exchange bank. Source assignment does not add an ARM audio
copy loop or a new DSP arithmetic stage.

The original factory DSP program provides independent evidence for reading
both source banks through the same operand bindings into ordinary DSP RAM.
That evidence is reconstructed through the original ARM uploader and guarded
against the exact original bytes. It supports the source-bank interpretation;
it is not a numerical emulator for the proprietary DSP.

Digital and AIRA strips can also add their own computer return under the stock
connection policy. An explicit assignment suppresses that destination's extra
contribution. Raw computer choices read the exchange bank directly, so this
suppression cannot remove a computer source assigned elsewhere. Returning a
strip to Auto restores the current stock policy, including digital direction
and connection state.

The UI stores one desired source byte and posts the existing DSP parameter
event, **8**. The patched DSP handler first completes the original parameter
queue drain, then applies the routes in the same DSP task. The UI never writes
the DSP programming port. Active routes are reapplied after later parameter
updates, so stock connection callbacks cannot silently restore a different
source on a manually assigned destination.

The event choice matters: the original event `0x80` performs output unmuting
and is not used as a routing wakeup. The independent audit executes the real
event-8 dispatcher and confirms that an empty parameter drain itself writes no
DSP MMIO. The original event flags clear when delivered, allowing a new post
during handler execution to remain pending for the next dispatch.

### Binary integration

Only the main application changes. The USB application, both boot programs,
updater and panel-controller payload remain original.

| Main decoded offset | Runtime location | Change |
| --- | --- | --- |
| `0x0f5d8` | `0x6000f5d8` | Panel callback pointer to the SELECT/TEMPO event wrapper |
| `0x13356` | `0x60013356` | Tempo-renderer entry to the source-label overlay and original-instruction trampoline |
| `0x24bae` | `0x60024bae` | DSP event-8 handler entry to the original drain followed by route application |
| `0xdff30` | `0x0100f6a4` | Inserted extension in the first startup SRAM copy |

The current extension occupies **1,596 bytes**, leaving **800 bytes** before the
original initialized SRAM at `0x01010000`. Existing runtime destinations and
BSS clears are preserved. Startup load-source literals shift with the inserted
bytes. The builder rejects another original firmware hash, unexpected hook or
DSP source bytes, unresolved relocations, orphan allocated ELF sections,
function exports outside the injected interval, or an SRAM overflow.

The verifier independently reconstructs every recorded application change and
executes both original and patched startup copies. An unrecorded change fails
even if its application hash is updated.

## Verification and its boundaries

The integrated [ARM report](../build/routing-probe/arm-verification.json) links
the [panel](../build/routing-probe/ui-verification.json),
[audio control](../build/routing-probe/audio-verification.json), and
[independent hardware-initialization](../build/routing-probe/hardware-audit.json)
reports. The [container report](../analysis/container_routing_candidate_verification.json)
checks the rebuilt image with original decoder/updater instructions.

The tests exercise all permitted source/destination combinations, source-menu
wraparound, four-character labels, the explicit 5/6-to-USB2 split, simultaneous
duplicates, original Return preservation, Auto restoration, mode transitions,
DSP reloads, invalid strip IDs and excluded diagnostic modes. They execute the
compiled extension and original ARM programming helpers. The UI tests also
cover every SELECT, plain taps, signed encoder boundaries, all 924 ordered
SELECT/other-key combinations, menu/modal guards, restoration and calling
conventions.

The DSP command model checks which program operands are changed and records
float-selector requests. Its source oracle uses distinct symbolic inputs to
check selection and independence. **It does not execute DSP arithmetic or
establish audible sample values.** Likewise, original serial-I/O setup at all
three rates is exercised with explicit readiness responses, not physical
clocks or converters. The reports identify every stub and modeled boundary.

Live stereo operand writes are sequential. This experiment has no demonstrated
sample-boundary commit or click-free transition. Physical tests must establish
connector order, levels, silence when a source stops, stable operation at each
rate, button/display behavior, routing while parameters change, and the
absence of interference with the original USB transport. Processor deadline
margin cannot be inferred from emulator instruction counts.

## Reproduce

Run the complete repository pipeline and verify the committed bytes:

```bash
.venv/bin/python tools/reproduce.py
.venv/bin/python tools/check_reproduction.py --check-committed
```

The pipeline has 22 stages and builds all three independent candidates. For
focused development of this candidate:

```bash
.venv/bin/python tools/build_routing_probe.py inputs/MX1_UPD.original.bin \
  --output build/routing-probe
.venv/bin/python tools/routing_probe_verify.py inputs/MX1_UPD.original.bin \
  --build build/routing-probe --output build/routing-probe/arm-verification.json
.venv/bin/python tools/container_candidate_verify.py inputs/MX1_UPD.original.bin \
  build/routing-probe/MX1_CHANNEL_ROUTING_UNTESTED.bin \
  --output analysis/container_routing_candidate_verification.json
```

Detailed evidence is in [the UI trace](../research/channel-routing-ui.md),
[the audio-routing analysis](../research/channel-routing-audio.md), and
[the independent validation note](../research/channel-routing-validation.md).
Physical work follows the repository's
[hardware validation plan](HARDWARE_VALIDATION.md); successful offline checks
do not change the candidate's `UNTESTED` status.

An additional [TAP-entry and cold-start audit](../research/tap-boot-audit.md)
executes original boot selection/decompression with application flash unmapped,
checks dirty-SRAM routing initialization and original RTOS pool reservations,
and records the final SDRAM-handoff emulation limit. Run it separately with
`.venv/bin/python tools/boot_path_verify.py`. It does not establish physical
recovery or continuous boot execution, and it changes no candidate bytes.
