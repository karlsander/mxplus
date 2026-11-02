# Internal sources: original sample callback and exchange ports

This report establishes the ARM integration used by the NSE/BD experiment for
the frozen MX-1 1.05-generation image. It does **not** establish audible output,
physical callback timing, CPU headroom, or successful installation. The
implementation retains the original computer-audio transfer and adds generator
samples through separate DSP exchange indices.

The audit is [tools/internal_sources_audio_audit.py](../tools/internal_sources_audio_audit.py).
It requires original container SHA-256
`26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`
and decoded main SHA-256
`256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b`.
Run it with:

```sh
.venv/bin/python tools/internal_sources_audio_audit.py \
  inputs/MX1_UPD.original.bin \
  --output analysis/internal-sources-audio-audit.json
```

## A sample callback exists independently of a connected USB computer

The original main routine at resident runtime `0x60001670`, decoded offset
`0x1670`, registers `0x01009841` as DSP0 callback slot zero. Its callback literal
is at decoded main offset `0x168c`; the adjacent literal at `0x1690` is the DSP
context `0x20000b24`.

The original registration API, relocated runtime `0x0100c8f0`, selects a
16-entry callback table at `context + 0x80c` for DSP0 or `context + 0x84c` for
DSP1. It refuses to overwrite a nonzero callback. DSP0 slot zero therefore
resides at `0x20001330`.

The original program-mode switch at `0x60023d84` invokes this registration in
normal program modes 0–3 without testing USB connection state. The same pump
also remains registered in diagnostic modes 4–11; the generator wrapper must
therefore explicitly reject diagnostic modes. Inspecting only the normal
registration is insufficient to justify writing into a diagnostic graph.

Original interrupt setup at `0x0100a524` registers the handler descriptor at
`0x0100f524`, whose handler word is `0x01009cc1`. The setup uses logical
interrupt `0x90` and priority argument 2. The actual interrupt handler executes:

| Step | Runtime address | Original operation |
| --- | --- | --- |
| Read interrupt state | `0x01009cc0` | Read `0x40100640` |
| Select callback slot | `0x01009cc8` | Extract bits 24–27 |
| Acknowledge interrupt | `0x01009ccc` | Write zero to `0x40100640` |
| Select DSP0 table | `0x0100c8e0` | Add `0x80c` to context |
| Dispatch callback | `0x0100a900` | Load slot pointer, call it if nonzero |
| Transfer computer frame | `0x01009840` | Run the registered stock sample pump |

The audit executes this chain unchanged with USB endpoint state inactive. The
stock pump still runs and writes eighteen zero playback words to
`0x40101000`–`0x40101044`. It leaves capture and other exchange indices
untouched. The fixture executes 133 ARM instructions from interrupt entry to
return, at each supplied 44.1/48/96 kHz rate state. This is an instruction
count, not a cycle or timing measurement.

One callback invocation transfers one frame. Running generation once at this
same boundary follows the existing sample-transfer structure. The statement
that physical interrupts arrive once per sample is an inference from the stock
audio path, not an emulated or measured hardware timing result. The harness
invokes an interrupt explicitly and does not execute the DSP instruction that
causes it.

## Exchange-bank address and occupancy evidence

The generic original writer at relocated runtime `0x0100bdfc`, main decoded
offset `0xdc688`, writes the supplied 32-bit word to:

```text
DSP0: 0x40101000 + 4 * index
DSP1: 0x40101400 + 4 * index
```

The index is descriptor word two. The separate read helper `0x0100be62` uses
the corresponding address calculation. The `0x400`-byte core stride suggests
256 words per core; a hardware register specification confirming that capacity
has not been recovered. The audit executes the unchanged writer for indices
`0x40`–`0x4b` in both cores and checks each exact MMIO write. This proves the
ARM calculation under the mapped-MMIO model, not physical register capacity.

The established raw computer source bank is DSP operands `0xa000`–`0xa011`,
corresponding to the first eighteen CPU exchange words. The original normal
program's prefix and independent factory input-copy program establish the
shared bank's use as an audio source; see
[channel-routing-validation.md](channel-routing-validation.md#direct-computer-source-format-evidence).

All normal program chunks are reconstructed through the original descriptor
wrapper and boundary uploader, with bulk DMA copying modeled. A conservative
scan of **every** reconstructed logical halfword finds these `0xa0xx` values:

| DSP core | Existing `0xa0xx` values in the complete normal program |
| --- | --- |
| DSP0 | `0xa000`–`0xa023`, `0xa026`–`0xa031` |
| DSP1 | `0xa000`–`0xa011` |

The scan includes immediates and data as well as operand fields; it does not
pretend to decode the proprietary DSP ISA. There is no `0xa040`–`0xa04b`
halfword anywhere in either reconstructed normal program. Indices `0x26`–
`0x31` are already referenced by the normal DSP0 control prefix, so simply
placing new sources immediately after computer capture would be unsafe.

The new experiment reserves:

| Source | DSP0 operand | CPU exchange address |
| --- | --- | --- |
| Shared white noise | `0xa040` | `0x40101100` |
| BD for strip 1 | `0xa041` | `0x40101104` |
| BD for strip 2 | `0xa042` | `0x40101108` |
| BD for strip 3 | `0xa043` | `0x4010110c` |
| BD for strip 4 | `0xa044` | `0x40101110` |
| BD for strip 5/6 | `0xa045` | `0x40101114` |
| BD for DIGITAL | `0xa046` | `0x40101118` |
| BD for USB1 | `0xa047` | `0x4010111c` |
| BD for USB2 | `0xa048` | `0x40101120` |
| BD for USB3 | `0xa049` | `0x40101124` |
| BD for USB4 | `0xa04a` | `0x40101128` |
| BD for COMPUTER | `0xa04b` | `0x4010112c` |

This reservation is an evidence-backed extension of the established bank. It
still needs physical validation of address decoding and DSP source reads.
The static exclusion does not prove that arbitrary diagnostic or debugger
operations could never write these indices. Diagnostic programs are excluded
from the generator path rather than treated as compatible.

## Production wrapper and sample representation

[patches/internal_sources_audio.c](../patches/internal_sources_audio.c) exports
`mx1_internal_audio_frame`. The builder replaces only the guarded callback
literal at main offset `0x168c` with its Thumb function pointer. The wrapper:

1. Calls the original pump at `0x01009841` unchanged.
2. Reads program mode at `0x6051deb8`; modes greater than three invalidate the
   renderer's cached ownership state and skip all generator exchange writes.
3. Passes the current rate from `0x20000b24` and exchange destination
   `0x40101100` to `mx1_internal_render` in normal modes. The first normal
   callback after diagnostic use resets voices and clears unused or stopped
   outputs even if the rate, source assignment and transport state are unchanged.

Invalidation also consumes the current step publication, preventing an old
diagnostic-period step from retriggering when normal operation resumes. A newly
published step after invalidation is processed normally. This ownership reset
is necessary because skipping diagnostic writes alone would allow a foreign
nonzero exchange word to survive indefinitely in a stopped, assigned BD port.

The original DSP initializer at `0x0100a282` stores the selected rate in that
context word; the independent serial-I/O audit exercises its 44.1/48/96 kHz
cases. No new high-frequency timer, USB endpoint, DMA channel, or separate
sample-scheduling mechanism is introduced.

The retained pump converts fixed-point USB words through `0x4004056c` and
`0x40040574`. Its explicit special case maps `0x80000000` to IEEE-754 `-1.0`
(`0xbf800000`). The extension renderer publishes normalized IEEE-754 words
using integer bit construction, avoiding the hardware converter and software
floating-point arithmetic in its sample loop. The full numerical behavior of
the proprietary DSP and fixed-point conversion ports remains outside the
offline model. Original use of IEEE-754 constants, shared audio inputs, and
that special case supports the chosen representation; it is not an audible
level-calibration result.

The shared-port writes are separate from the DSP programming command/data
pair used by source-routing edits. The sample wrapper does not write program
instructions or coefficients. Routing continues to publish assignments and
apply source operands in the existing DSP parameter task.

## Final candidate regression checks

[tools/internal_sources_audio_verify.py](../tools/internal_sources_audio_verify.py)
executes the actual rebuilt main application, including its registered
callback pointer, compiled wrapper and compiled generator renderer. Its
results are recorded alongside the candidate in
`build/generator-probe/audio-verification.json`.

The integration cases cover:

- The original registration API installing the exact compiled wrapper address.
- Twenty-one rate/program-mode combinations checking the wrapper's call ABI,
  original-pump preservation and diagnostic exclusion. Only the render body is
  stubbed in these boundary-isolation cases.
- Twenty-four differential USB scenarios with the actual idle renderer:
  disconnected, capture-only, duplex, stereo, both mixed stereo/multichannel
  combinations, stop/restart and playback stopping while capture continues,
  each at three supplied sample rates. Every original MMIO/FIFO trace and
  corresponding original stream state must match the unmodified application.
- Twelve active-source scenarios: noise alone, one BD voice, eleven BD voices,
  and noise plus eleven BD voices, each at three rates. The original USB pump
  traces must remain identical, all selected generator ports must vary, all
  unselected ports must remain zero, and generated floating-point values must
  remain finite and bounded.
- Stopping transport silences BD while noise continues. Removing assignments
  clears the output words once and then avoids recurring idle bank writes.
- Diagnostic callbacks leave all generator exchange words untouched, and the
  first resumed normal callback restores silence for a stopped, assigned BD
  after a foreign diagnostic word is explicitly placed in its port. This is
  an ownership-change fixture, not an emulation of diagnostic DSP arithmetic.

The report records executed instructions for the complete interrupt path and
the additional instructions relative to the same original IRQ, separating the
initial trigger from later samples after the crossfade. These counts can
identify implementation overhead and compare candidate revisions; they are
not a measured core frequency, cycle count, deadline or CPU-utilization result.

USB FIFO readiness and phase are supplied synthetic values. The retained USB
sample converter is modeled as an identity conversion to make the original
transfer paths comparable. The new generator renderer uses its actual integer
arithmetic and float-word construction and does not use that converter model.
The DSP does not execute those generated samples in this harness.

## Boundaries that remain

The audit establishes original callback registration, dispatch, inactive-USB
behavior, address calculations and normal-program static exclusion. It does
not execute DSP arithmetic, model interrupt arrival timing, or measure spare
CPU time. Additional work must validate real sound and level, port aliasing,
sample phase, interrupt scheduling, sample-rate changes, simultaneous computer
traffic and multiple active BD voices. In particular, eleven addressable BD
sources do not imply that eleven simultaneous voices have measured real-time
headroom at 96 kHz.
