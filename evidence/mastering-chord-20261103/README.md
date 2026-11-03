# Immediate MASTERING + TAP entry

On 3 November 2026 the user reported that candidate
`adb0c284b24e2813dd2a978471f43997b4e76864396d596f18554831c537c474`
still displayed the ordinary mastering preset number instead of entering the
editor. They confirmed that the update reached Fin and custom SELECT + TEMPO
routing still worked. Selecting GAIN before trying the hold did not help.
There is no firmware readback or panel-event trace from the physical mixer.

The user requested a button combination instead of a long hold. Hold MASTERING,
then press TAP: entry now happens on that TAP event without reading the clock or
waiting for the periodic callback. MASTERING alone is replayed as the original
press/release pair. TAP alone is dispatched immediately. The combination consumes
TAP and both releases; unrelated buttons/encoders retain stock modified gestures.
MASTERING exits and saves as before. Pressing TAP first remains ordinary tap tempo.

An independent guard defect was reproduced in the previous binary: the original
channel-setting buttons at main decoded `0x10516` / runtime `0x60010516` request
pages 5, 6, 7, 8, 9 and 10 through `0x6001033e`. The extension admitted only 5 and
15. It now admits 5–10 and 15, preserving boot/modal/lock exclusions. This defect
explains rejection on PAN/TONE/AUX/BFX/FADER, but **does not explain the reported
GAIN failure**. The physical cause of the previous long-hold failure remains
unresolved; it is not claimed fixed by a speculative timer change.

All changed executable bytes remain in the existing main mastering slots:
`0x1dbf4..0x1de08` and `0x1de0c..0x1e5ec`, runtime addresses
`0x6001dbf4..0x6001de08` and `0x6001de0c..0x6001e5ec`. The registration literals
at main decoded `0xf5d8` and `0xf5dc` are regenerated with the new Thumb targets.
Head usage is 508 / 532 bytes and text usage is 2,004 / 2,016 bytes.
The 140-byte state layout is retained; its former timestamp word is reserved.
No new SRAM, timer, task, allocator or MPU change is introduced. A differential
byte check against PR #14 confines all 1,940 changed main-application bytes to
those mastering code slots and registration literals; both SRAM load blobs and
the complete USB application are byte-identical.

Candidate: `35efb7ffd6486dae78f7b9acdf66d313e6861049f10429da00326cb09dd68bfc`.
The generated build report accounts for old/new bytes, branch targets, section
bounds, source hashes and both application/container identities. USB-host MIDI
code, descriptors and behavior remain unchanged from PR #14.

Regression checks execute the registered ARM callback with no tick between
MASTERING and TAP, reject a clock read, exercise all six original channel-setting
button requests, and cover standalone taps, background traffic, both release
orders, repeats, unrelated held keys, mode guards, pickup, slot saves and existing
parameter controls. The original page request is observed with display/lifecycle
boundaries modeled; the physical panel and RTOS scheduling are not emulated.

The full reproduction and committed-evidence gate must pass for the matching
candidate. No physical entry, control-surface, MIDI or audio acceptance is claimed
by this change; the filename remains UNTESTED.
