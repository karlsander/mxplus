# Additional-send candidate installation attempt, 16 November 2026

Candidate SHA-256:
`0cff93760693e41e18e8091332c16bf425b05613242637ee498c43f8e3be975d`.
Source/artifact commit at staging: `67db15aaee76801231a8d4624a903c2a8475157d`.
The committed-evidence gate and that commit's hosted offline workflow passed.

The user authorized installation on the connected MX-1. macOS identified the
Roland USB updater (VID/PID `0582:01a4`) and its 5.2 MB FAT16 MX-1 volume.
The first copy incorrectly used `MX-1_UPD.BIN`, following the website's install
instructions. Its readback matched the candidate, and the disk was ejected.
The user then reported a red flash. This is a user observation, not a captured
panel trace or proof of where the updater stopped.

Inspection confirmed the supported original updater searches for `MX1_UPD.BIN`
without a hyphen: updater decoded offset `0x59c4`, runtime `0x600059c4`.
The installation instructions are corrected, with a browser-package regression
check against that literal. The original archive-selection instructions can
still refer to Roland's hyphenated download name.

The reconnected update volume was empty. The same candidate bytes were copied
as `MX1_UPD.BIN`, flushed, unmounted and remounted. Full file readback still
matched the SHA-256 above, then the disk was safely ejected. Original/candidate
update-file backups and local installation records were retained. These are
not device-flash, calibration or settings backups.

**Pending:** user-triggered TAP update, Fin, normal boot and audio acceptance.
No successful flash, boot, audio, recovery or DSP-headroom result is claimed.
