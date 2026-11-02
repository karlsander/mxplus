# Internal-source startup placement and state ownership

The NSE/BD candidate needs more code and state than the routing-only
candidate's 2,396-byte SRAM interval. It uses a separate guarded builder and
linker script instead of growing the old interval into initialized data.
This note records evidence for the exact frozen main application; it does not
claim physical SRAM occupancy has been measured.

## Original ranges and the added copy

[`tools/build_generator_probe.py`](../tools/build_generator_probe.py) requires
decoded-main SHA-256
`256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b`.
The original scatter table has a zero-length copy at operation index 4, called
from `0x60000032`. Its literal words at decoded offsets `0x10c`, `0x110` and
`0x114` hold destination `0x01020000`, length 0 and source `0x600dffb4`.

The candidate appends the initialized extension at the original decoded EOF,
offset `0xe0448`. Only those three scatter literals change: destination becomes
`0x01018000`, length becomes the complete extension size, and source becomes
`0x600e0448`. All other copy/zero operations and all original image offsets
remain unchanged. The original final SDRAM zero pass subsequently erases the
temporary load copy after the SRAM copy has completed.

| Range or record | Evidence and treatment |
| --- | --- |
| Original private data end | Last original private zero range ends at `0x01017264`. |
| Extension interval | `0x01018000..0x0101c000`, 16,384 bytes; linker and builder both enforce the bound. |
| Gap before interval | 3,484 bytes after the original private data end. |
| Gap after interval | 16,384 bytes before the original stack pool. |
| Stack pool | `0x01020000`, size `0x8000`; original record at runtime `0x0100f234`, decoded offset `0xdfac0`. |
| General pool | `0x01013e18`, size `0x1000`; original record at runtime `0x0100f244`, decoded offset `0xdfad0`. |

The allocator records are guarded as exact four-word structures, not inferred
from empty-looking firmware bytes. The builder also rejects overlaps with
every original recovered startup range. The linker emits one initialized
PROGBITS section containing code, tables, state and explicit zero data. It
rejects an oversized extension, and the builder rejects additional allocated
sections, unresolved relocations, missing exports and exports outside the
injected section.

## Executed startup and allocator evidence

[`tools/internal_sources_memory_verify.py`](../tools/internal_sources_memory_verify.py)
executes the original startup copies and zeros, then checks the exact
extension bytes and every original initialized/zeroed region. It accounts for
every modified original byte using the three scatter literals and all eleven
guarded application hook sites; the only additional bytes are the extension
at EOF.

It then executes the original static-pool initializer at `0x01006338` in both
the original and candidate memory images. No function is stubbed on this
initializer path. The fixture maps a reset-zero SCB page, and the path takes
507 instructions, creating pool control objects at `0x01014e18` and
`0x01014e5c`.

The unchanged allocator at `0x01007604` is exercised until exhaustion using
512-byte allocations. Original and candidate produce the same 63 successful
stack-pool addresses and seven general-pool addresses, followed by failure.
An extension-interval canary is unchanged throughout. This checks the concrete
stack/general-pool collision risk, rather than assuming a startup gap is free
of dynamically allocated memory.

The proof is bounded by these original startup and allocator paths. It does
not establish arbitrary debugger/diagnostic memory behavior, undocumented
hardware aliases, interrupt-stack depth or physical memory stability.

## Control and sample state

[`patches/internal_sources.c`](../patches/internal_sources.c) stores 176
aligned 32-bit step records: eleven strips times sixteen steps. Bit 0 enables
the note, bits 8–15 hold signed semitone pitch, and bits 16–23 hold decay.
Each edit publishes one complete word. Only the UI writes those records;
sample generation snapshots the addressed word when a new step triggers.

The DSP parameter task publishes one aligned active-source mask. Noise uses
bit 16, and BD strip voices use bits 0–10. The audio callback owns all voice
and noise-generator state. UI and DSP-control work never modify a ringing
voice directly or use the sample callback's arithmetic state.

The native clock callback publishes a validity bit, an event serial and a
separate modulo-16 counter. It does not reuse the native step number because
the native LAST STEP limit can be shorter than 16. Start/stop reset the phase
and advance a separate transport generation. The latter ensures a complete
stop/start/first-step transition between sample callbacks still clears an old
tail even if the new first step is disabled.

The renderer resets voices on rate changes, transport changes and newly
activated BD routes. Removing a route clears its exchange word once. An idle
renderer avoids recurring generator-port writes. Integer bit construction
converts signed Q15 samples exactly into binary32 words without using the
original shared hardware converter.

While a diagnostic program owns the exchange bank, the audio wrapper only
invalidates its remembered mask/rate and snapshots the current clock. It does
not write generator ports. Returning to a normal program then clears foreign
sample words and resets selected voices, including an assigned but stopped BD.
This prevents a stale diagnostic sample from surviving the stopped fast path.

[`tools/internal_sources_core_verify.py`](../tools/internal_sources_core_verify.py)
checks actual compiled state publications, all 176 records, per-step bounds,
independent strip snapshots, next-cycle retriggering, transport races, rate
and route changes, sample conversion and clock-hook ABI equivalence. The
original clock functions and displaced instructions execute; the report
enumerates unrelated parameter/transaction/timer boundaries supplied by the
harness. These checks do not model physical interrupt arrival or preemption
priority.
