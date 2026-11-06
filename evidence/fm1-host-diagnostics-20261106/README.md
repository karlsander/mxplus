# FM-1 monitor / MX-1 host diagnostic experiment

User report on 6 November 2026 (Europe/Berlin), with FM-1 connected to MX-1
HOST3. The MX-1 had not been reflashed after candidate
`1087e7256c0b76b512a5bf28f8264e6c5385e986bc45effb3a964c9a59e46db3`.
The FM-1 had received DIAG A1 package
`9108c3a2ff59013b1acc0dbfc5516dfc309ce0e91e90d7fa9cc4a87dd7ced148`,
from [FM-1 PR #2](https://github.com/karlsander/fm1-instrument/pull/2).

The user read WAITING FOR HOST; ALT 1; RATE HZ 44100; RATE SET 3; STARTS 3;
PACKETS 0; MISSED/STALL 0/0; EMPTY/FULL 0/0; WAIT/FILL 255/0. They reported
RATE SET/STARTS increasing on each MX-1 restart. The preceding audio attempts
had MIDI but no USB3 meter activity with source Auto/USB3. System rate,
observation duration and cable model were not recorded. This is a user-read
screen report, not a raw control/packet capture.

In the pinned FM-1 BSP, this combination means alternate 1 was selected but
the initial queued audio packet was not consumed. PACKETS excludes initial
unprimed silence; WAIT saturates at 255 while TX-ready remains set. Zero FILL
is expected before consumption starts. The reading narrows the problem to
host startup/transfer, but cannot alone distinguish the failure point.

## Next MX-1 candidate

`candidate.json` identifies a diagnostic-only revision of the same transport.
It sends startup/controller status through MIDI SysEx for the existing FM-1
monitor to display. No FM-1 flash is needed. The host periodic schedule,
descriptors, sample conversion and accepted format are unchanged; diagnostic
observations do add code execution and a bounded MIDI report.

Original OHCI periodic-tree construction and HCD queue/worker dispatch now
execute in the offline verifier. All 32 HCCA entries reach the custom ED, and
the queued request reaches the patched driver. These successful checks do
not demonstrate actual controller transfers. No physical result is claimed
for the new candidate until installation and the next readings are recorded.

All 17 offline reproduction stages and the current-artifact evidence audit
passed for this candidate. Targeted checks include actual queue/worker dispatch,
original HCCA construction, unchanged converter/sample-buffer extents, report
formatting and TX integration, no clock/poll reporting flood, user SysEx
continuity, full-note-transfer priority and replacement-device isolation.
USB/DSP hardware and RTOS queue delivery are modeled boundaries.

See [report decoding and bench controls](../../docs/USB_HOST_AUDIO.md#host-diagnostic-report).

## Staged on the MX-1

After the user confirmed update mode, the candidate was copied as `MX1_UPD.BIN`
to the verified Roland USB updater volume, read back with matching SHA-256
and ejected. [Copy receipt](copy.json). The prior `1087e725…` image is retained
locally for rollback. The user was instructed to press TAP, wait for Fin and
restart; this staging record does not establish completion of that update.

The committed-artifact gate and all six browser-patcher tests also passed.
The requested next observation is the five raw SysEx rows from the FM-1 MIDI
monitor with CHAN ALL and TYPE SYSEX, after a note sent through the MX-1.
