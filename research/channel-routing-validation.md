# Channel routing: independent hardware and instruction evidence

This note records the independent checks supporting channel-routing research.
It does not establish physical audio, safe installation, or processor headroom.
The original main application is the source of the register and instruction
observations below. A DSP program reconstructed through the original ARM
uploader is evidence of program contents, not an execution of its proprietary
audio instructions.

## Exact baseline and reproduction

The original update must have SHA-256
`26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`.
The decoded main application must have SHA-256
`256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b`.

Run the independent register audit from the repository root:

```bash
.venv/bin/python tools/routing_hardware_audit.py
```

The report is `analysis/routing-hardware-audit.json`. It executes original
Thumb instructions for the main DSP initializer at runtime `0x0100a282`
(decoded main offset `0x000dab0e`) at 44,100, 48,000 and 96,000 Hz. It also
executes the original AK4115 manager initializer at runtime `0x60001404`
(decoded offset `0x00001404`) for both numeric direction modes at each rate.
All nine cases return normally with the original stack restored.

The DSP initialization cases do not replace any called firmware function.
Three MMIO reads are modeled to allow initialization to complete:

| Read location | Supplied response |
| --- | --- |
| `0x4002dff4` | Ready value `1` |
| `0x40100048` | Counter incrementing on reads |
| `0x4010000c` | Reset-complete value `0` |

For the AK4115 cases, the digital GPIO/control helper at `0x600030aa` and
serial register writer at `0x600012dc` are recorded and replaced by successful
returns. Those cases test the original manager's mode-dependent register
selection, not communication with an AK4115 device. The report records these
stubs and all written register values.

## Serial interface descriptors

The original DSP initialization writes the following values at all three
sample rates. Each following word is `0x20`; the adjacent word at
`0x40100504` is also initialized to `0x20`.

| Register | Written value | Low field |
| --- | --- | --- |
| `0x40100508` | `0x88003006` | `0x3006` |
| `0x40100510` | `0x88003004` | `0x3004` |
| `0x40100518` | `0x88003002` | `0x3002` |
| `0x40100520` | `0x88003000` | `0x3000` |
| `0x40100528` | `0x98003016` | `0x3016` |
| `0x40100530` | `0x98003014` | `0x3014` |
| `0x40100538` | `0x98003012` | `0x3012` |
| `0x40100540` | `0x88223010` | `0x3010` |
| `0x40100548` | `0x8822300e` | `0x300e` |
| `0x40100550` | `0x8822300c` | `0x300c` |
| `0x40100558` | `0x8822300a` | `0x300a` |

The separate AK4115 manager selects the first descriptor at `0x40100500`:
numeric mode `0` writes `0x88113008`; numeric mode `1` writes `0x98113018`.
The manager's nearby source-path string is `driver\\ak4115_mgr.cpp`.

These are observed values. The audit does not assume undocumented register
bit names, or infer an electrical connector from a low field alone. The
combination of this initialization and the ordered source operands in the
normal DSP program supports the channel mapping described below.

## Input gain stage and source order

`tools/routing_audio_extract.py` reconstructs both normal DSP instruction
memories by executing the original descriptor wrapper and boundary uploader.
Its explicit model supplies the bulk DMA byte copy. See
`analysis/routing-audio/program-upload.json` and the accompanying program
binaries and halfword listings. In those listings, the printed offset is a
byte offset in logical DSP instruction order; the high half of each
CPU-visible 32-bit word comes first.

The program region around logical offsets `0x031a` through `0x04fc` contains
the ordered operands `0x6000` through `0x6005`, then `0x6008` through `0x6011`,
then `0x2010`/`0x2011`, and finally `0x6006`/`0x6007`. Independent ARM callback
traces associate this region with input gain:

| Parameter | Original ARM gain helper | DSP coefficient index | Matching program operand |
| --- | --- | --- | --- |
| Input 1 gain | `0x60025304` | `0x0e` | `0xc00e` at `0x033e` |
| Input 2 gain | `0x6002531e` | `0x0f` | `0xc00f` at `0x0350` |
| Input 3 gain | `0x60025338` | `0x10` | `0xc010` at `0x0364` |
| Input 4 gain | `0x60025352` | `0x11` | `0xc011` at `0x037a` |
| Input 5/6 gain | `0x6002536c` | `0x12` | `0xc012` at `0x038c` |
| Digital input gain | `0x60025386` | `0x13` | `0xc013` at `0x03c4` |

All of those helpers tail-call, or call, the original coefficient writer at
`0x0100b5ea`, through the resident thunk at `0x60055060`. The first five
load their values from the same gain table; the digital and later input
gains use a different table. The parameter registry identifies the first
gain callback as global parameter `0x11a` and the later callbacks in order.
Original analog gain callbacks also control the analog gain hardware, so a
post-gain route cannot promise an independently adjustable analog preamp for
two destinations fed from the same physical input.

The program order and serial descriptors strongly support this physical
source interpretation:

| DSP source operands | Interpretation supported by program order |
| --- | --- |
| `0x6000`–`0x6003` | Analog inputs 1–4 |
| `0x6004`, `0x6005` | Analog 5/6 left and right |
| `0x6006`, `0x6007` | Aux return left and right |
| `0x6008`, `0x6009` | Digital left and right |
| `0x600a`–`0x6011` | Four AIRA input stereo pairs |
| `0x2010`, `0x2011` | Computer stereo source at this stage |

This remains firmware-derived mapping. Injecting distinct signals into the
physical connectors and observing each destination is the decisive hardware
check. In particular, simply substituting an analog operand in an AIRA input
path would not prove that the path behaves independently of that port's
connection and clock state. Routing should use an established common input
stage and explicitly account for the existing connection selectors.

## Existing connection selectors

The normal callbacks for digital and AIRA connection state are
`0x60027b44`, `0x60027b7c`, `0x60027bf8`, `0x60027c20`, and `0x60027c48`.
They update embedded DSP constants through `0x0100bb12`. The metadata at
`0x600b82dc` identifies the paired logical program offsets:

| Input | Selector offsets |
| --- | --- |
| Digital | `0x01de`, `0x01f8` |
| AIRA USB 1 | `0x0212`, `0x022c` |
| AIRA USB 2 | `0x0246`, `0x0260` |
| AIRA USB 3 | `0x027a`, `0x0294` |
| AIRA USB 4 | `0x02ae`, `0x02c8` |

The callbacks also consult the mixer mode and, for digital, digital direction.
These existing writes must not silently undo an explicit route. Their
existence alone does not prove a general source matrix or a sample-rate
converter architecture.

The independent audit executes all five original connection callbacks for
both connection states in modes `0` and `2`. It replaces only the system
parameter getter, supplying the stated mode and digital-input direction.
All 20 cases write just the two embedded computer selectors for that input;
none writes the native input coefficient gates. A separate execution of the
unchanged initializer at `0x600251f2` sets native coefficient indices `1`
through `13` to unity (`0x3f800000`) using 52 MMIO writes through the original
coefficient API. This distinguishes the existing native-input gate values
from the computer summand selectors; it does not claim that no other driver
or diagnostic path can change an input's state.

## Program writes and concurrency boundary

Three original write mechanisms are relevant and should not be conflated:

| Original runtime function | Observed behavior |
| --- | --- |
| `0x0100b5ea` | Writes coefficient command/value pairs twice through `0x4014c000` or `0x4016c000`, at index times `0x10`. The command includes flags supplied by the caller. |
| `0x0100baee`, called by `0x0100bb12` | Writes `0x40000000 | (kind << 28) | (core program base + offset)` to `0x40100900`, followed by the supplied value at `0x40100904`. |
| `0x0100ab04` | Writes a raw program command through the same command/data pair, without the `0x40000000` flag. It left-shifts kind `0` payloads by 16 bits, kind `1` payloads by eight bits, and leaves kind `2` payloads unchanged. |

The original program reader at `0x0100bbac` writes a command and polls bit
30 of `0x40100008` before returning a value from `0x40100904`. The original
bitfield rewrite helper at `0x0100bc6c` reads through that function, clears
the metadata-specified bit range, inserts the new field, and writes through
`0x0100ab04`.

These instruction traces establish the command formats used by this
firmware. They do not establish sample-boundary atomicity or a hardware
queue's depth. Disabling interrupts only inside a new UI writer would not
protect an already interrupted stock command/data transaction. Routing
updates should therefore run at the existing DSP task boundary described
below. They must preserve neighboring instruction fields and avoid assuming
that coefficient and raw instruction operand updates have interchangeable
semantics.

The USB-B sample pump at runtime `0x01009840` accesses 18 playback words
starting at `0x40101000` and 18 capture words starting at `0x40101048`.
That is an established computer-audio exchange window. It is not evidence
of a universal ARM callback exposing all raw analog and AIRA input samples.

## Direct computer-source format evidence

Reading a computer source directly from an `0xa000` operand must not rely
only on the apparent correspondence with the USB exchange window. The
normal DSP program contains another processing block before its ordinary
`0x2000`–`0x2011` computer-source buffers; bypassing an indispensable format
conversion there would produce incorrect samples.

An independent original program resolves much of that concern. The test
program descriptor at runtime `0x600cb780` (decoded main offset `0x000cb780`)
contains offset `0`, length `0x0a32`, and source `0x600cad4c`. Its parent
descriptor is at `0x600779cc`, adjacent to the test-mode parameter metadata.
The audit executes the original uploader at `0x0100bfe2` for this descriptor,
models its 2,608-byte DMA copy, and executes its final boundary write.

The resulting program has two corresponding import chains:

| Logical DSP byte offset | Original instruction halfwords | Observed role in the chain |
| --- | --- | --- |
| `0x0020` | `1e05 0fe0 1fe2 a000 0033` | First computer source read |
| `0x002a` | `7809 0fe0 8fe2 1fe4 9fe6 a001 0020 0035 a012` | Next computer read and ordinary-buffer store |
| `0x015c` | `1e05 8fe0 9fe2 0031 a023` | Final computer-buffer and capture stores |
| `0x016a` | `0c03 0fe0 6000` | First serial input source read |
| `0x0170` | `1e05 0fe0 8fe2 6001 000c` | Next serial input read and ordinary-buffer store |
| `0x021a` | `0c03 8fe0 0013` | Final serial input buffer store |

The intermediate rows repeat for all 18 computer sources and all 18 serial
sources. Both imports use the same `0fe0` read binding and ordinary `8feX`
store binding, placing their samples into ordinary DSP buffers. This stock
computer import does not contain the normal program's `1040`/`44c7`/`beda`
processing block. The matching original import encodings support treating
the `0xa000`–`0xa011` source operands as compatible with the native serial
sample operands, without reusing a computer buffer already suppressed by a
destination's connection selector.

`pc_operand_format` in the audit report records the descriptor, reconstructed
program hash, transport assumptions, and every checked instruction in both
chains. This is stronger evidence than a naming or address inference, but
it remains firmware-derived: the audit does not execute the proprietary DSP
arithmetic or establish physical audio results.

## DSP task event boundary

The existing DSP task registers event `0x08` to the parameter-update handler
at runtime `0x60024bae` (decoded main offset `0x00024bae`). That handler drains
the parameter queue and then returns through `0x60024c52`, whose original
six bytes are `07 b0 bd e8 f0 83`: release the 28-byte local frame, then restore
`r4` through `r9` and the return address. A routing flush after that drain
executes on the same task as the original parameter callbacks. UI code can
publish a desired route and post this event without accessing the DSP command
registers itself.

The original event-post wrapper is runtime `0x0100e266` (Thumb pointer
`0x0100e267`). Its arguments are the task object in `r0` and event bits in
`r1`. It loads the signed 16-bit event-flag identifier from task offset `8`,
then tail-calls `0x010032f2`. The DSP task object is `0x6051dea8`; the route
request uses event bits `8`. The underlying setter ORs event bits under the
kernel's existing BASEPRI critical section.

The generic loop at `0x0100e220` waits for an enabled event, scans the returned
bits, and invokes the registered callbacks in that task. Event `8` uses the
callback at task offset `0x20`. Its flag object's creation record at
`0x600751c0` enables automatic clearing. The original match helper at
`0x010073b8` copies the matched flags out and clears the pending word; a
subsequent event post is available to the next wait.

The task creation table provides another useful consistency check:

| Task record | Entry point | Priority value |
| --- | --- | --- |
| `0x600751c8`, DSP | `0x60024a45` | `11` |
| `0x60075234`, panel | `0x6000f3bd` | `15` |

The kernel installs the supplied priority at `0x01007d8c`; the ordered queue
insertion at `0x010087a4` puts smaller priorities first. The panel therefore
does not normally preempt the running DSP task. The desired-route store must
still precede marking it pending and posting its event: the higher-priority
DSP task can interrupt the panel while it is publishing a request. Pending
state should tolerate a redundant flush rather than lose a newer request.

`analysis/routing-hardware-audit.json` includes an actual-instruction check of
this boundary. The unchanged dispatcher receives one modeled event `8`, runs
the unchanged parameter handler with an explicitly empty queue, reaches the
original epilogue, and starts its next wait with its stack intact. That empty
dispatch performs no MMIO writes. Separate checks execute the original
event-post wrapper and the original flag-match helper, confirming the wrapper
arguments and flag clearing. They do not emulate RTOS scheduling or interrupts.

Event `0x80` must not be used as an otherwise idle route notification: its
original handler calls `0x6002408c`, which changes output mute and gain state.

## Limits of the offline evidence

No proprietary DSP instruction arithmetic, analog converter, serial audio
stream, asynchronous clock behavior, USB host/device hardware, or physical
audio is emulated by these audits. Register readiness and DMA transport are
explicit assumptions. Original ARM instruction counts are not CPU cycles,
DSP utilization, or spare processing capacity. The mapping and protocol
findings narrow the implementation and hardware checks; they do not replace
those checks.
