# TAP-entry and routing first-boot audit

This audit examines the exact supplied 1.05-generation firmware and the existing
independent channel-routing candidate. **No candidate bytes change.** It adds
instruction-level evidence about updater selection, application loading, cold
initialization and SRAM reservations. It does not certify hardware recovery or
complete boot execution.

## Identities and reproduction

| Item | SHA-256 |
| --- | --- |
| Original update container | `26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e` |
| Routing update container | `1810461b87255931fdce8696dff0c0b1c28758e3a95e28ac02b4e01723526c21` |
| Routing decoded main application | `03717a17250aebd42c2412439b218f02acdec5bc0258245f9dbc22740ecdd251` |
| Routing extension | `8f85f7611f95a512e797605a058af5ab05964f97a779fbe14f5630b884a92a25` |

From the checkout root, after installing `requirements.txt`:

```sh
.venv/bin/python tools/reproduce.py
.venv/bin/python tools/check_reproduction.py --check-committed
.venv/bin/python tools/boot_path_verify.py
```

The last command writes [the boot audit report](../analysis/boot_path_verification.json)
and is also a separate CI step. The existing reproduction remains 22 stages.
Local execution used macOS arm64, Python 3.12.13 and the four pinned dependency
versions. Native ELF/debug metadata differs from the committed Linux build;
the committed-evidence gate passes for the actual firmware, application and
extension byte hashes.

## Original main-boot path

These addresses belong to **boot_main**, whose raw/decoded payload starts at
container offset `0x30` and is loaded at `0x01000000`. An offset below is relative
to that payload, not to the compressed main application or updater. The separate
USB boot program also uses `0x01000000` in its own execution context.

| Decoded offset | Runtime address | Observed instructions |
| --- | --- | --- |
| `0x4e0` | `0x010004e0` | Reset vector target; branches through the literal to `0x010002c0` |
| `0x2c0` | `0x010002c0` | Establishes SP; executes original scatter initialization at `0x010023a0`; enters `0x01000486` |
| `0x2dc` | `0x010002dc` | Reads an input word at `0x425a0080`; zero selects `0x03010000`, nonzero selects `0x03080000` |
| `0x486` | `0x01000486` | Calls the selector after board setup; only the normal branch performs the extra normal peer setup and USB-application loading |
| `0x1810` | `0x01001810` | Both branches construct transfer descriptors for the USB boot payload and a four-byte peer-start value |
| `0x448` | `0x01000448` | Loads the selected component using its header; compressed components run the original main-boot decoder at `0x0100057e` |
| `0x4cc` | `0x010004cc` | Reads the selected header's entry field at `+0x28` |
| `0x2d4` | `0x010002d4` | Sets the Thumb bit on that entry, then `bx r0` at `0x010002d8` |

The flash mapping in this execution is `0x03000000 + container offset`:
`0x03010000` is the updater, `0x03080000` is the main application, and
`0x03200000` is the USB application. The selected updater and main application
both decode to `0x60000000` in separate runs.

**Observation:** with selector zero, the actual reset, scatter, selector,
transfer-descriptor construction and updater decompression run while flash
`0x03040000` onward is completely unmapped. Neither application can be read.
The result is exactly the original decoded updater and a final branch target of
`0x60000001`, for both stock and routing containers. The normal branch is the
negative control: it faults reading the absent USB-application header at
`0x0320003c`. With complete flash present, the normal branch decodes the stock
USB application and the respective stock/routing main application correctly.

**Inference:** this is strong software evidence that updater selection and
loading do not depend on executing either application. The documented physical
entry is [TAP held during power-on](https://www.roland.com/global/support/by_product/mx-1/updates_drivers/82415302-0466-4c5c-be4e-138a8946d4a7/).
The electrical connection from TAP/panel hardware to the selector input has not
been measured or fully traced; the input is supplied by the harness. Do not
describe `0x425a0080` as a verified MX-1 pin or give it an invented register name.

### Explicit execution boundaries

The harness replaces board initialization at `0x01000540` and `0x0100037e`,
peer-transport setup/readiness/completion at `0x01001346`, `0x0100095e` and
`0x01000970`, and normal-only peer helpers at `0x01001abc` and `0x01001aea`.
It supplies the ROM cleanup callback through `0x02003018`. The report records
every stub call and transferred payload hash. It does not execute a second
processor or an immutable ROM before the supplied reset vector.

An exploratory stock run raises Unicorn `UC_ERR_EXCEPTION` on the final branch
into `0x60000000`, before a target code hook runs. Board setup/remapping is not
modeled, and the cause is unresolved. The audited path therefore stops
**immediately before `bx r0`**, verifies its selected target and all decoded
bytes, and tests application startup separately. This is deliberately not a
claim that a continuous reset-to-running-updater test passed. Physical USB
enumeration, actual flash writes and failure recovery remain unverified by this
test.

## Routing startup risks examined

Only the main application changes. Every byte below container offset `0x80000`
and from `0x200000` through the trailer is identical to stock. The component
checks additionally compare decoded updater, panel and USB applications.

Within **app_main**, the three hooks are at decoded/runtime pairs
`0xf5d8` / `0x6000f5d8`, `0x13356` / `0x60013356`, and
`0x24bae` / `0x60024bae`. They redirect the panel callback, tempo display and
DSP event-8 handler. The extension begins at decoded offset `0xdff30`, relocated
by the first startup copy to `0x0100f6a4`. Its 1,596 bytes end at `0x0100fce0`,
leaving 800 bytes before existing initialized SRAM at `0x01010000`.

The integrated routing verifier already reconstructs every patch, checks exact
old bytes and aligned branch literals, executes displaced-instruction
trampolines, checks AAPCS preservation, and compares every original initialized
region after the actual startup copies. The new audit adds:

- Actual application startup over both `0x55` and `0xaa` dirty SRAM patterns.
  Desired and applied routing bytes both become zero (`Auto`) from the copied
  extension data. The unused 800-byte gap retains its dirty pattern.
- Execution of the original RTOS pool initializer at runtime `0x01006338`
  (decoded main offset `0xd6bc4`), including its original helper calls. The
  configuration at runtime `0x0100f234` (decoded offset `0xdfac0`) reserves the
  stack pool at `0x01020000..0x01027fff` and general pool at
  `0x01013e18..0x01014e17`. Both stock and routing initialization produce the
  same pool base/size records and leave the extension region unchanged. The
  SCB ICSR read is modeled as zero/thread mode; no pool-initializer routine is
  stubbed. This covers those original static pools, not every possible runtime
  allocation or stack margin.
- Three initial/repeated event-8 drains for each of six DSP mode values and
  three mixer modes: 54 drains, no routing programming writes, no routing event
  posts, all desired routes still `Auto`. Original parameter storage, queue and
  task boundaries retain the explicit existing AudioMachine models.
- Observed empty-handler stack depth of 56 bytes stock and 64 bytes routing,
  with the same stubs. This excludes task ancestors, interrupts and stack use
  inside stubbed calls; it is not a full task-stack measurement.

No startup defect was identified in these examined paths. The tests cannot
exclude physical memory/controller behavior, interrupt races, task timing or
unexamined application paths. The source selector can still encounter the
documented sequential stereo DSP writes, unmeasured switching transients and
unmeasured deadline margin. It adds no persistent scene or flash write; routes
start at Auto after power-up. See [the routing report](../docs/CHANNEL_ROUTING.md)
for the full feature scope and limits.

## Bench status and first-boot scope

On 2 November 2026 the user reported successful installation of the unchanged
stock container through the documented TAP/file-copy procedure. The Mac-side
copy was read back and matched the original SHA-256 before ejection. This is a
reported stock-update baseline, not an instrumented failed-application recovery
test. Board identification, electrical traces and a full flash backup are absent.

The user explicitly authorized a first routing-candidate installation after
this offline audit despite the remaining recovery uncertainty. That is a
task-specific authorization, not a change to the repository's general recovery
prerequisite. At the time of this report, candidate flashing and first-boot
results are still pending. Preserve the `UNTESTED` filename and status.

For the first observation, keep monitoring muted, use stable normal power and
disconnect unrelated devices. After `Fin`, power off and start normally with
no buttons held. Establish normal display and idle behavior before changing a
route. Then hold a SELECT and verify `Auto`, and only after normal startup test
the documented 5/6-to-USB2 split with quiet distinct signals. A later TAP-mode
entry can test updater access with this normally booting candidate; even that
would not simulate recovery from arbitrary corruption.
