# Standalone host-MIDI short-packet fix

This extracts the receive correction introduced by `7dc82037e0ec715e0b251e027c0231e82765abb9`
on [PR #21](https://github.com/karlsander/mxplus/pull/21), onto main after
[PR #20](https://github.com/karlsander/mxplus/pull/20), commit
`3e3282962c887e144cedfe19addc5a8e3b7e3e4e`. Only the stock short-input option,
its instruction-level tests and their supporting stack-fixture parameter are
extracted. The main application retains PR #20's mastering hold and preset light.

## Problem and correction

Generic MIDI IN previously used asynchronous request flags zero. Original EHCI
completion returns -15 for otherwise successful short data unless flag bit 13
was supplied. A four-byte MIDI event returned to a 64-byte receive request could
therefore fault input until reconnection. Supply `0x2000` only for IN. The
unchanged completion validator still rejects non-four-byte lengths, oversize
lengths and controller errors. OUT still uses flags zero, timeout 100 and exact
write lengths; IN still waits without a timeout. No driver error is masked.

All following findings are in **app_usb**, with resident runtime equal to decoded
offset plus `0x60000000`. The [instruction excerpts](original-disassembly.txt)
were extracted from the earlier B3 report and their 154 instruction byte strings
were checked against the guarded original component:

| Decoded offset | Runtime | Behavior |
| --- | --- | --- |
| `0x9464` | `0x60009464` | Async request API; seventh argument packed at request +0x28 |
| `0xf908` | `0x6000f908` | Core loads that halfword before HCD submission |
| `0x112ae` | `0x600112ae` | EHCI copies flag bit 13 to wrapper +0x16 |
| `0x11af2` | `0x60011af2` | Short completion tests wrapper +0x16 before returning -15 |

These original instructions remain unchanged. The compiled extension passes
the option through the existing API, retaining its AAPCS callback and token ABI.

## Identity and placement

Candidate SHA-256:
`cde8a1039be813d6eba7cddb6b10c6eb22b72dd8507d46c3d7c842fcf99f2418`.
Main application: `cfab5a905d27497f74e40f8147346307a3aaae56497eac520324f6d0c0ab1281`.
USB application: `3185602fe763043f81b4bb79cbe70faa61f14a4f2c3b7dcc8f7961b358c22712`.

USB startup retains decoded `0x2b1f4` to runtime `0x01000300`, length `0xbbe4`,
for the original hot section. Extension insertion remains decoded `0x36dd8`,
runtime `0x0100bee4`. It grows from 2,772 to 2,784 bytes, ending at `0x0100c9c4`,
with 1,596 bytes before the allocator at `0x0100d000`. Five initialized-data
sources move with the insertion; their destinations are unchanged. Existing
state remains 1,472 bytes at `0x01017868..0x01017e28`, with 472 bytes spare.
There is no new SRAM state, SDRAM reservation, allocator change or original patch
site. Existing callback/branch and startup patches are regenerated for the new
layout; the [build report](../../build/mainline/build-report.json) records exact
old/new bytes, targets, bounds, relocation updates and component checksums.

[Component comparison](component-comparison.json) checks the actual prior Git
artifact against this candidate. Only the USB application slot changes; every
byte outside `0x200000..0x300000` is identical, including main, boot, updater,
panel payload and container trailer. The original whole-input hash is unchanged.

## Verification and limits

The extracted `tools/host_midi_ehci_verify.py` executes unchanged original EHCI
wrapper/QH/qTD construction, schedule linking, toggle handling and completion.
For full- and high-speed fixtures, 0/4/16/60-byte completions of a 64-byte request
fail with old flags and succeed with `0x2000`; full completion succeeds in both.
Those original-driver results then drive compiled MIDI callbacks/polling to
check continued reception. Stalls and malformed input still fault reception.
Existing tests retain exact OUT length/timeout, all four ports, incoming sync
filtering, overload isolation, disconnect generations and Roland behavior.
Original request packing now checks both flag values. The shared harness's
optional stack parameter is needed for the original constructor's stack arguments;
its default, limits and exact SP-return assertion are retained.

Heap allocation, critical sections, controller status/DMA writeback and RTOS
delivery are modeled. These tests do not establish physical DMA, USB timing,
end-to-end musical input, long SysEx or broad compatibility. Full reproduction
and committed-image results are recorded in the accompanying validation record.

The user previously confirmed MIDI output to the FM-1 on candidate
`253645edb92a09c7b0d100da01f57d5127834c109b2ad499332645487a7a1d14` after the
alternate-zero startup fix. Message types, timing and duration were not captured.
Later debug-bridge round trips used changed audio-branch images and an FM-specific
untimed OUT experiment; they do not establish acceptance of this standalone image.
This candidate has not been installed and keeps its `UNTESTED` filename.

PR #21 retains the host-audio transport/converter, SDRAM placement, debug command
parser/reply wakeups, diagnostic counters, queue-fault distinctions and FM-specific
untimed OUT behavior. Those changes are tied to the experiment and are not promoted
as general MIDI fixes here. The earlier display diagnostics in PR #17 are closed.
