# Empty channel pages on the tempo surface

Built from `origin/main` commit `f0ab337` (PR #22), in a clean worktree. The
starting checkout was detached at an older revision with local changes; those
files were left untouched. PR #20's mastering hold/light and PR #22's short MIDI
receive fix were already merged before this work started.

Candidate SHA-256:
`dad7fbf2825a7a7ec82470cd7e4127d5567aa1cb1bed5ff3efb09c971a329ca3`.
Status remains **UNTESTED**; no device was accessed or flashed.

Selecting a channel assigns the right display, dial and SHUFFLE/FINE/SYNC/TAP
buttons to four empty pages (`P1--` through `P4--`). The dial changes no value.
No-selection restores stock tempo controls. SELECT + TEMPO source routing and
mastering retain priority. Page selection is volatile and belongs to the stock
current selected channel. No additional sends, audio processing or storage
format is introduced. [Behavior and binary addresses](../../docs/CHANNEL_CONTROLS.md).

The new main-only UI uses 14/16, 408/568 and 444/560 bytes in split slots reclaimed
from the stock identity system-parameter lookup. The original zero-return
and invalid diagnostic remain in place. Lookup equivalence covers all 141 IDs,
invalid values and diagnostic arguments, with reference and literal-pointer
checks. The existing routing target and mastering eligibility guards move into
those resident slots. The executable SRAM extension shrinks from 2,376 to
2,308 bytes, leaving 88 bytes. Writable state grows by 16 bytes to 636 total,
ending at `0x010174e0`, within the unchanged MPU/allocator boundaries.

The new original hook is the mono LED helper at main decoded `0x14a78`, runtime
`0x60014a78`; it retains the original five-argument driver ABI, including color
zero and caller brightness, while overriding logical LEDs 10–13 in channel
mode. This includes background TAP updates. Existing event/display/redraw hooks
are reused. All old/new bytes, targets, relocations and component checksums are
in [build-report.json](../../build/mainline/build-report.json).

[Component comparison](component-comparison.json) checks the actual candidates:
only the main application changes. Every byte outside its container slot remains
unchanged, including both boot programs, USB application, updater, panel payload
and trailer. The original input SHA-256 guard remains unchanged.

The dedicated [instruction report](../../build/mainline/channel-controls-verification.json)
covers all eleven stock SELECT toggle paths, four pages, dial boundaries,
per-channel page memory, stock-held and channel-held release ownership,
duplicate presses, page/modal/boot guards, external selection redraw,
mastering precedence, source routing and linked/multiple selection.
During development a concrete stock-held duplicate-press case left its key bit
set after selection changed. The implementation now consumes that duplicate
without taking ownership of its release; the regression checks that the original
key bit clears. The reproduction identity fixtures were also extended for the
new mandatory candidate-bound channel report.

All instruction tests model or stub final panel delivery, RTOS scheduling,
notifications and physical I/O. Original selection actions, parameter storage,
lookup, startup and the existing DSP programming helpers execute. This evidence
does not establish physical switch/LED operation, timing, audio, clock stability
or safe recovery. Use the separately authorized bench sequence in the feature
report before changing acceptance status.

Validation: all 17 local offline stages passed for this exact candidate. The
current-artifact gate passed. Committed-artifact and browser-patcher checks are
recorded in the PR after committing the matching binaries and reports.
