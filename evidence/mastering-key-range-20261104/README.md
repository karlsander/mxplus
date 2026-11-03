# Mastering held-key range: observed failure and bounded fix

The user ran diagnostic build d001 (`72050c85919774c40cad920a97b6a31bf03571380a71e0885f7052f4f5f7a695`,
PR #17, commit `57b93d7b48b3f4ae452aeabf366a3247ce6519be`) on the MX-1.
The displays worked and reported:

```text
btn MASTERING: 0217
btn TAP: 200
Mgd: 0010
MPg: 0005
MKy: 0055
MHi: 0020
MSt: 0000
tgd: 0010
tPr: 0055
tPo: 0000
CAn: 0000
```

`0217`/`0200` match the expected physical event IDs. `Mgd=0010` says the held-key
bitmap blocked entry, with no boot/page/lock/modal blocker sampled. `MKy=0055`
identifies bit 85; `MHi=0020` independently identifies the same bit in byte 10.
The reported `tPr=0055` is inconsistent with the two state bits exposed on that
page; it may have been the adjacent tKy page. It is retained verbatim and is not
needed for the conclusion. No electrical meaning for bit 85 is established.

The former mastering `no_keys()` checked eleven whole bytes (88 bits), while
both the routing gesture and mastering event classifier use physical IDs
`0..0x54`. The replacement checks ten whole bytes and only the low five bits
of byte 10. It does not clear or rewrite the upper bits. Boot/page/modal/lock,
ordered MASTERING + TAP entry, standalone TAP tempo, deferred MASTERING short
press, save/recall and pickup logic are retained.

All code findings are **app_main**. `KEYS` is the existing bitmap at runtime
`0x605129a4`; byte 10 is `0x605129ae`. The replacement is compiled into the
reclaimed head slot at decoded `0x1dbf4..0x1de08`, runtime
`0x6001dbf4..0x6001de08`. Exact function/branch targets and full overwritten
stock bytes are recorded in the [build report](../../build/mainline/build-report.json).
No handwritten changes are made to generated firmware.

Candidate: `9f6da91f9aaaedfb406ed1fa2d6af1a51900b44ecc950d4294cc6a513d5d8d38`.
This builds from mainline after PR #16, without d001's diagnostic hooks/menu,
SDRAM code reservation or diagnostic state. The stock SDRAM heap start remains
`0x606634d0`. Internal code remains 2,376 bytes (20 bytes free), main writable
extension state remains 620 bytes, and the mastering head shrinks from 508 to
500 bytes within its 532-byte slot. USB application bytes match PR #16 exactly.
Boot programs, updater, panel payload and original input are unchanged.

## Offline evidence and next physical test

The preceding PR #16 image was executed with only key bit 85 set and reproduces
blocked entry. The new [ARM verification](../../tools/mastering_verify.py)
executes registered event/periodic callbacks for all eight combinations of
bits 85–87, checks successful entry/exit without altering those bits, and checks
that all 85 physical held keys still prevent entry even with upper bits set.
A physical key appearing after MASTERING still cancels the pending modifier.
Standalone MASTERING and TAP retain their original event pairs with bit 85 set.
Full reproduction also covers all existing mastering parameters/slots/pickup,
routing, USB/MIDI, startup/MPU/pools and original container/boot checks.

The test harness still models the physical panel delivery, higher key actions,
periodic callback body, parameter notifications and final storage writes as
specified in [mastering evidence](../../docs/MASTERING.md). The new guard's
hardware acceptance is pending. After installing this exact candidate, hold
MASTERING and press TAP after normal boot; it should enter immediately. Release
both, test pickup, then press MASTERING once to save and exit. Confirm ordinary
TAP tempo and SELECT + TEMPO routing afterward.

## Separate host-MIDI observation

In the same diagnostic session, the user reported FM-1 on host USB3:
`U3=0001`, `C3=0001`, `RX=0`; also `C1=0101`, `C2=0001`, and `U1=0007`
for an AIRA Demora on USB1. This establishes main-side reported connection but
no MIDI-ready flag for the FM-1, with its clock-output enable on and destination
availability gate off. The Demora reports connection/audio/MIDI readiness.
It does not establish the exact failing setup stage or real USB transactions.
This mastering-only change does not claim to resolve that separate failure.

Successful d001 displays establish SDRAM execution for those control-task
callbacks on this mixer. They do not establish audio/DSP deadlines or sustained
stability, and the present candidate does not use that diagnostic reservation.
