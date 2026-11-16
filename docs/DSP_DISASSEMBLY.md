> Historical stock-disassembly investigation. The current [send implementation](FX_SENDS.md)
> adds separate arithmetic, routing and verification evidence. Statements below
> about unimplemented sends describe the earlier research stage.

# Partial ESC2 DSP disassembly

The stock firmware contains two relocated effect instances, including distinct
coefficient banks and distinct delay-address records. This is stronger evidence
for reusing one existing instance as a send than merely finding room for its
program. It does **not** yet establish the complete delay-buffer bounds or the
processing budget for arbitrary simultaneous effects.

This investigation changes no firmware. The additional sends remain
unimplemented; their behavior and remaining integration work are described in
[FX_SENDS_RESEARCH.md](FX_SENDS_RESEARCH.md).

## Reproduce and inspect

```sh
.venv/bin/python tools/test_esc2_disassemble.py
.venv/bin/python tools/esc2_disassemble.py --check
```

Omit `--check` to regenerate the deterministic listings and report. Both the
whole original update and decoded main hashes are checked. The program bytes
come through the original ARM uploader and boundary-write helper, with bulk
DMA modeled as copying, as in [the earlier routing investigation](../research/channel-routing-audio.md).
Simply concatenating ROM chunks gives incorrect results at partial-word edges.

Start with these outputs:

- [DSP1 mixer and effect dispatch](../analysis/esc2-disassembly/dsp1.txt).
- [DSP0 source routing and output processing](../analysis/esc2-disassembly/dsp0.txt).
- [Factory input-copy program](../analysis/esc2-disassembly/factory-dsp0.txt).
- [Internal algorithm 1, both slots and differences](../analysis/esc2-disassembly/fx01.txt).
  Files `fx00.txt` through `fx19.txt` cover all twenty internal algorithm IDs;
  these IDs have not been equated with the eight panel DELAY variations.
- [Machine-readable evidence](../analysis/esc2-disassembly/report.json), including
  original control calls, relocation contexts and delay-address updates.

These are **partial structural disassemblies**, not recovered DSP source code.
Unknown operations remain raw words. `bindings?` and `flow?` explicitly mark
inferences. There is no DSP arithmetic emulator or invented ADD/MAC mnemonic.

## Packet structure

The low five bits of a packet's first halfword give its length in halfwords
throughout the examined corpus: 77 descriptor-bounded chunks, 54,526 bytes and
4,393 packets. This includes 36 normal-program chunks, forty effect variants
and one factory program. Every chunk round-trips byte-for-byte without scanning
past failures or guessing a new alignment. This is corpus evidence for the
framing rule, not a published or complete ESC2 instruction specification.

Three explicit gate records (`0000 0001` at program offset zero) and three
terminal zero words are retained as opaque records. They are only accepted in
the known chunks that contain them; a zero-length header elsewhere is an error.

The conservative `xfeN` binding annotation treats the low five bits as byte
offsets into a packet's literal tail. For example, the factory packet at DSP0
logical `0x0170` reads:

```text
1e05 0fe0 8fe2 6001 000c
     ---- ---- ---- ----
     bindings  literals
```

The tool associates `0fe0` with `6001` and `8fe2` with `000c`. The earlier
factory-copy evidence supports this association. The decoder does not infer
the arithmetic, operand width or pipeline latency from this pattern alone.

For packets beginning `0b03`, the third halfword times two is a candidate
logical byte target. Twenty of the 22 occurrences point to packet starts in
their corresponding program. The two exceptions both point to the factory
program's explicit terminal zero at `0x0a30`; they remain reported as exceptions.
DSP1's root has candidate targets at `0x4000` and `0x6000`, matching the separately
uploaded effect slots. This is not yet a complete control-flow graph.

## Mixer controls now have instruction anchors

Another 127 original ARM callback cases establish the DSP1 coefficient indices
for all eleven channels' pan, AUX send, MASTER FX switch and fader, plus AUX
master and return levels. Original soft-float and coefficient-writing routines
run unchanged, with callee-saved register and return-stack checks. Parameter
names come from the stock string table at main decoded `0x6f278`.

| Control | DSP1 coefficient indices | Encodings found in mixer binding tails |
| --- | --- | --- |
| Channel pan | `0x01..0x0b`, `0x0c..0x16` | `c001..c016` |
| Channel AUX | `0x2d..0x37` | `c02d..c037` |
| Channel fader | `0x38..0x42` | `c038..c042` |
| Channel MASTER FX switch | `0x43..0x4d` | `c043..c04d` |
| AUX return level | `0x4e` | `c04e` |
| AUX master level | `0x4f` | `c04f` |

Every anchored index has a corresponding binding-tail encoding in the normal
DSP1 program. The association of the `c000` operand bank with these coefficient
indices is an inference supported by both the original callbacks and program
structure. The report records each callback's main runtime and decoded offset.

For example, the mixer packet at DSP1 logical `0x11ec` references channel 1 AUX
and MASTER FX switch coefficients, while `0x120c` references its fader. The
mixer chunk source is main runtime `0x600bb448`, decoded `0xbb448`; listing
offsets are DSP logical byte offsets, not linear offsets into that ROM source.
This locates the relevant operations, but does not by itself prove the order
of accumulation, stereo normalization, or a safe pre-pan tap.

## Effect-instance relocation

Executing the original constructor at main runtime `0x60024228`, decoded
`0x24228`, produces these contexts at ARM RAM `0x60515440` and `0x60515458`:

| Context field | Slot 0 | Slot 1 |
| --- | --- | --- |
| DSP core | 1 | 1 |
| Source program halfword base | `0x3000` | `0x3000` |
| Destination program halfword base | `0x2000` | `0x3000` |
| Eight-byte data-entry base | `0x04` | `0x27` |
| Coefficient base | `0x60` | `0x70` |
| Shared-port base | `0x50` | `0xa8` |

These fields are consumed by original wrappers at main runtime `0x60023904`
(program float), `0x60023954` (program selector), `0x60023a24` (coefficient),
`0x60023a60` (shared port), and `0x60023b2e` (data entry). Their decoded offsets
are the runtime addresses minus `0x60000000`.

All twenty effect pairs have identical packet lengths and headers. Across the
pairs, 1,238 changed halfwords have the low-operand delta `+0x100`, and 256 have
the coefficient encoding delta `c060..c06f` to `c070..c07f`. Another 394 changed
halfwords are deliberately unclassified; equal headers do not prove equal
arithmetic or that every differing word is an address.

Four additional original-wrapper cases use stock coefficient metadata at
`0x6007c0d0` (decoded `0x7c0d0`, relative coefficient 3). The same metadata
resolves to coefficient `0x63` in slot 0 and `0x73` in slot 1. Both zero and unity
reach the original writer at relocated runtime `0x0100b5ea`, decoded `0xdbe76`.

## Delay-state and address updates

The stock driver has eight-byte records in CPU windows `0x4014e000` (DSP0)
and `0x4016e000` (DSP1). Original read/write helpers `0x0100c206` / `0x0100c0d0`
select the window and access `base + entry_index * 8`. These are record windows,
not a demonstrated mapping of all delay sample memory into ARM space.

The following cases execute the original wrappers and driver helpers without
stubs. The record windows are modeled as ordinary storage seeded with the exact
corresponding ROM data entries. A temporary wrapper object is initialized by
the original constructor and points to the original slot context. This is a
focused driver test, not a complete effect-load or audio-processing test.

**Record-field update:** algorithm 2 metadata at main runtime `0x6009ade8`,
decoded `0x9ade8`, specifies relative entry byte offset `0x18`. The wrapper at
`0x60023b2e` resolves this to DSP1 window address `0x4016e038` for slot 0 and
`0x4016e150` for slot 1. Original helper `0x0100c7ca` (decoded `0xdd056`) replaces
the low 16 bits of the second word. Eight cases cover four values in both slots;
the first word, second-word upper bits and opposite slot remain unchanged.
This does not establish the field's units or valid musical time range.

**Address update:** algorithm 19 destination metadata at `0x600a39dc`
(decoded `0xa39dc`) and base metadata 24 bytes before it feed original wrapper
`0x6002397e` and helper `0x0100c5da` (decoded `0xdce66`). Eight cases confirm
that the base is taken from the low 23 bits of the selected instance's base
record, then the supplied offset is added. Corresponding base fields are
`0x491500` and `0x637300`. With offset 123, the resulting address fields are
`0x49157b` and `0x63737b`, written to `0x4016e028` and `0x4016e140` respectively.
The destination's other fields and the other slot's records remain unchanged.
These numbers are **driver address-field units**, not asserted byte counts.

All runtime helpers in the relocated `0x0100xxxx` region use the main mapping
`decoded = 0xd0b8c + runtime - 0x01000300`. No USB or updater address space is
involved. Raw static data records for each effect variant are included in the
report. Six slot-0 data sources point to runtime RAM; those remain unresolved
rather than treating their startup contents as initialized effect data.

## Consequences for the additional send

There is no established need to allocate a second large delay buffer merely
because the send is a second effect: the original firmware already has two
relocated instances and different base-address fields. Removing DELAY from
MASTER FX is therefore not yet justified as a memory requirement.

The ownership problem remains real. MASTER FX's stock type-change path
alternates both slots, so reserving one for a send still requires changing
loading, switching, parameter replay and COMBI behavior. Prohibiting a menu
category alone would not reserve a slot.

The next decoding work is to establish every delay read/write extent, dynamic
allocation/reset path and scratch dependency, then resolve the mixer arithmetic
and effect input/return operands. The low-23-bit address mask is not proof of
installed RAM capacity. Packet counts are not timing measurements. No current
result establishes arbitrary simultaneous delay/reverb, a wet-only parallel
return, real-time headroom, or physical audio correctness.

## Verification scope

The six parser tests cover CPU/logical ordering, round trips, truncation,
zero-length rejection, explicit special words, candidate flow recognition and
rejection of impossible binding annotations. Corpus regeneration additionally
checks all 77 chunk boundaries, all twenty paired header sequences, all mixer
coefficient anchors, and the original ARM cases described above. CI runs these
alongside the existing stock-send audit and full offline reproduction.

The builder, linker, candidate and USB application are unchanged. Passing these
checks is disassembly/control evidence only; no device was flashed or tested.
