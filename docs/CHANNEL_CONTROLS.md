# Channel pages on the tempo surface

**Status: offline tested candidate, not installed or physically accepted.**
This first stage changes control ownership only. It adds no effect sends,
parameter values, DSP, MIDI mapping or persistent storage.

On the normal mixer and channel-setting pages, selecting a channel assigns
the right display, TEMPO dial and four buttons to that channel. The existing
SELECT behavior is retained: tap another channel to switch, or tap the current
channel again to clear selection. Linked and multiple selection keep Roland's
current-channel rules; the page belongs to the current selected channel.

| Button | Empty page | Display |
| --- | --- | --- |
| SHUFFLE | 1 | `P1--` |
| FINE | 2 | `P2--` |
| SYNC | 3 | `P3--` |
| TAP | 4 | `P4--` |

The selected page button lights steadily. TAP's background beat indicator cannot
overwrite that page indication. The dial is intentionally inactive on these
empty pages, including with another modifier held. Each channel remembers its
page in RAM; all start on page 1 after boot. Scenes and restart do not save pages.

With no channel selected, the tempo display, dial, SHUFFLE, FINE, SYNC and TAP
retain their original operation and settings. Running tempo, incoming clock and
transport continue while a channel is selected; the change prevents these panel
controls from editing tempo or its settings in channel mode.

**SELECT + TEMPO source routing retains priority.** Holding exactly one SELECT
on the main mixer page still shows and edits its source. On release, the display
returns to the channel page if a channel remains selected, or to tempo if the
stock SELECT action cleared selection. VALUE and the left-side controls retain
their existing behavior. Mastering mode takes over as before; leaving it restores
the channel page when appropriate. Menus, startup, UI lock and modal screens
retain their existing control handling.

A button press owned by channel mode consumes its repeat, duplicate press and
release even if selection changes. A button originally pressed in tempo mode
still gets its release for stock cleanup. A channel-page button held down blocks
new mastering hold entry, like other held surface keys.

## Main-processor integration

Every address here belongs to **app_main**. Resident runtime addresses are
`0x60000000 + decoded offset`. The existing executable SRAM extension is relocated
by the first startup copy; its current size and all literal updates are recorded
in [the build report](../build/mainline/build-report.json).

The stock system parameter lookup at decoded `0x1a40c` / runtime `0x6001a40c`
returns its input for IDs 0–140. Its replacement retains the unsigned bounds
check and original invalid-input diagnostic. The original zero-return epilogue
at `0x6001a654..0x6001a658` and diagnostic at `0x6001a888..0x6001a896` remain
byte-identical. The remaining lookup footprint holds the new UI, the existing
routing held-key guard and the existing mastering eligibility guard. No new
executable memory region, MPU setting, heap reservation or sample callback is used.

| Main decoded interval | Runtime interval | Purpose |
| --- | --- | --- |
| `0x1a40c..0x1a41c` | `0x6001a40c..0x6001a41c` | Equivalent system lookup, 16-byte capacity |
| `0x1a41c..0x1a654` | `0x6001a41c..0x6001a654` | UI code, 568-byte capacity |
| `0x1a658..0x1a888` | `0x6001a658..0x6001a888` | UI code, 560-byte capacity |
| `0x14a78..0x14a80` | `0x60014a78..0x60014a80` | Mono LED helper veneer |
| `0x108..0x10c` | `0x60000108..0x6000010c` | BSS clear extends through `0x010174e0` |

Thirteen state bytes, padded to 16, occupy writable SRAM
`0x010174d0..0x010174e0`: eleven page indices, button ownership and the last
rendered selection. The complete mainline reservation grows from 620 to 636
bytes. Original allocators and all preceding state addresses are unchanged.

Original SELECT action at decoded `0x16532` / runtime `0x60016532` owns channel
selection. The new code reads mixer index `0xfb` and confirms that channel's
selected flag through the original getter at `0x6001e65e`. Physical keys
`0x1b`, `0x1c`, `0x1d`, `0` map to SHUFFLE, FINE, SYNC, TAP; logical LEDs
are `10..13`. These key and LED IDs are distinct. The original tempo renderer
at `0x60013356`, registered event wrapper and mastering redraw wrapper provide
the existing entry points. Mono LED calls preserve the original five-argument
call to relocated driver `0x01002ad2` (main decoded `0xd335e`), including
color zero and brightness. The original first startup copy maps decoded
`0xd0b8c` to SRAM `0x01000300`; its existing bytes retain that mapping.

The whole original hash, exact overwritten bytes, branch targets, section bounds,
startup relocation and component checksums remain guarded in the sole builder.
[Guarded lookup bytes](../patches/channel_control_sites.json) are specific to the
supported firmware revision. Boot programs, updater, panel payload and USB
application remain byte-identical to the starting mainline candidate.

## Verification and physical acceptance

[Instruction evidence](../build/mainline/channel-controls-verification.json)
executes the actual stock SELECT actions, parameter storage/getters, text loops
and compiled UI. It compares all 141 lookup results and invalid diagnostics,
preserves the shared return, checks exported cross-references and scans literal
pointers. Cases cover all eleven channels, page switching, signed dial boundaries,
linked/multiple selection, held releases, modifiers, external selection updates,
mastering priority, and asynchronous LED updates. The existing routing and
mastering regressions remain in the complete reproduction pipeline.

Object construction, RTOS scheduling, final display/LED delivery, parameter
notifications and hardware I/O are modeled or stubbed. Instruction counts are
not timing measurements. Physical switch mapping, visibility, timing, audio
stability and continued clock operation require a separately authorized bench
run. The filename remains `MXPLUS_MAINLINE_UNTESTED.bin`.

For that run, check every SELECT/deselect path, all four pages, held buttons
across selection changes, tempo controls with no selection, linked channels,
source routing, left-side controls and mastering entry/exit. Repeat while audio
and clock run, then check scene recall and reboot. Record exact candidate hash,
connections and observations under the existing [hardware procedure](HARDWARE_VALIDATION.md).
