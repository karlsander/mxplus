# Mastering hold cancelled by unrelated panel events

## User observation

On 3 November 2026 the user reported installing firmware produced by the live
web patcher, operating in normal Mixer mode, trying different MASTERING hold
lengths without entering the editor, and successfully using SELECT + TEMPO
channel routing. This establishes a reported entry failure on a modified image;
it does not identify the physical packet stream or validate other functions.

At investigation time the live manifest identified source commit
`d8eefd0570eab992a5bc7ad0c4435da72a646841` and candidate
`f9e91cdc5fa2b2aa73cfc75671e570651893484bd35d09a8d7c2d23192d81133`.
Applying the actual hosted XOR asset to the exact original produced bytes
identical to that maintained candidate. It contained the mastering callbacks.
This was not an old-image or missing-feature packaging result. No hash was
read back from the user's mixer, and its incoming panel traffic was not traced.

The previous build report and mastering test report are retained here. The
previous candidate/application bytes remain in Git at the source commit above.

## Instruction reproduction and correction

The registered **app_main** event callback is selected by decoded offset
`0xf5d8`, resident runtime `0x6000f5d8`. Both candidates point to Thumb entry
`0x6001dffb`. Its pending-hold branch previously cleared the pending flag and
fabricated the deferred stock MASTERING press for every event except another
MASTERING key event. A physical ADC sample (type `0x0b`) or unrelated panel
notification (type `0x1d`) therefore cancelled an otherwise valid hold.

The failure is reproduced with the old compiled instructions: MASTERING down,
a tick advance, an ADC sample or notification, and another tick advance past
the threshold leaves the editor inactive. With no intervening event, the same
candidate enters the editor. This establishes a software failure mode consistent
with the user's symptom. It does not prove which event caused their failure.

`patches/mastering_ui.c` now cancels a pending hold only for physical control
types 1 through 5: button release/press/repeat and the two encoder event types.
The existing MASTERING-specific handling still runs first. ADC samples and
other notifications retain their original dispatch without synthesizing a
MASTERING press. The 1,200-tick threshold, clock ABI, eligibility checks and
registered periodic callback are unchanged.

The correction is rebuilt by the sole maintained builder. Code and constants
remain within the existing resident slots at app_main decoded
`0x1dbf4..0x1de08` and `0x1de0c..0x1e5ec`, runtime
`0x6001dbf4..0x6001de08` and `0x6001de0c..0x6001e5ec` (end exclusive).
The shared literal and return remain intact. There is no new callback target,
startup relocation or runtime reservation. Text usage is 1,976 / 2,016 bytes;
head usage remains 508 / 532 bytes. Writable state remains 140 bytes within the
existing 540-byte combined reservation; SRAM code still has 20 bytes free.
The load extension is byte-identical. The generated build report records exact
original/replacement bytes, placements and component checksums.

New candidate:
`1ed56e3569df508f8d099eb9d162ff9c37d8915a895ef7d2cc64696662e221cf`.
Decoded application:
`56d7b7c8a3259e37c6e1a276c377e3dcecbed4a4fa84088754f7426d52a7c1b6`.
USB application, boot programs, updater and panel payload remain unchanged.

## Regression coverage and limits

`verify_hold_traffic` in `tools/mastering_verify.py` fails on the old candidate.
It interleaves twelve ADC samples and twelve unrelated notifications across
the hold interval, checks threshold entry and original dispatch, then verifies
release/exit. It also checks a short tap with background traffic and cancellation
by another button, VALUE, TEMPO and the second encoder event type. The existing
mastering tests cover guards, pickup, slot changes, parameter transactions,
storage submission, rendering and register/stack preservation.

These tests execute the compiled registered callbacks and original dispatch
instructions under the existing harness. Time and the periodic callback body,
physical ADC delivery, final panel I/O, scheduling and storage completion remain
modeled or stubbed as recorded in the mastering report. The actual hardware
event stream and hold timing remain unmeasured. No hardware was accessed or
flashed to produce this correction; the new candidate still needs physical
entry and subsequent mastering acceptance.
