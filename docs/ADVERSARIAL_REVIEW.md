# Adversarial review of mixer-only mainline — 2 November 2026

Follow-up: the current mainline contains the [stereo packet fix](USB_PACKET_FIX.md)
and its regression tests. The record below describes the original finding on
`88457445…`; its hash-pinned reproducer requires that historical image (Git
commit `fde26fd`). Current acceptance uses `tools/usb_packet_verify.py` and the
normal reproduction pipeline. Physical acceptance of the fix remains open.

One high-priority USB defect was reproduced. No additional routing, SELECT,
end-stop or storage defect was established within the checks below. This is a
review of `36d93d1`, container SHA-256
`88457445ffe1abeca8365198d0c15ed967c6f5b4dac08393da52c575a80660ba`.
The firmware is unchanged. The preceding [retirement review](MAINLINE_REVIEW.md)
did not exercise the finite-packet cases added here.

## P1: stereo playback retains 18-channel packet accounting

**Trigger:** a host selects playback interface 1, alternate 2, which the
current descriptor advertises as two channels. The audio pump reads two
four-byte words per frame, but its shared packet accounting subtracts 72
bytes, compares the remainder with 144, and prefetches 36 words at that
threshold. Its buffered-tail end also remains 144 bytes. These constants are
appropriate to 18-channel playback, not stereo.

This behavior is inherited from Roland's original pump. Advertising it to
generic UAC2 hosts makes it part of the current feature's contract; unchanged
stock instructions alone are not evidence that this alternate is correct.
Both OUT2/IN2 and OUT2/IN18 use the affected playback branch. Stereo capture
alone does not execute it.

All following locations are in **app_main**, relocated from decoded
`0xd0b8c` to runtime `0x01000300` by the original startup map:

| Behavior | Decoded offset | Runtime address |
| --- | --- | --- |
| Read the OUT packet-length field | `0xda0fc` | `0x01009870` |
| Stereo FIFO read, used for lanes 16 and 17 | `0xda192` | `0x01009906` |
| Unconditional `subs r0, #0x48` | `0xda1d0` | `0x01009944` |
| Compare remainder with `0x90` | `0xda1d6` | `0x0100994a` |
| Fixed 36-word tail prefetch | `0xda1e2` | `0x01009956` |
| Fixed 144-byte buffered-tail end | `0xda27c` | `0x010099f0` |

The packet-length interpretation is supported by original instructions, not
just a decompiler name: helper `0x01003dfa` reads the low eleven bits at
`USBF + endpoint*8 + 0x70`; endpoint 13 maps to `0x400100d8`, read by the pump.
The original EP0 caller at `0x010049b2..0x010049ca` uses that helper's result
to bound a byte transfer. The pump's 72-byte decrement and 144-byte/36-word
tail agree with this interpretation for 18 channels.

**Reproduction:** actual candidate Thumb instructions consume finite packets
containing 5, 6 and 12 sample frames. With 18 channels, accounting and the
two-frame buffered tail are consistent. With stereo, the 40- and 48-byte
packets underflow on their first frame; the 96-byte packet underflows on its
second. The 48-byte case becomes `0xffffffe8` after consuming only eight
bytes. None reaches the normal next-packet re-arm path. All samples in these
short fixtures still emerge in order; they do not demonstrate an immediate
audible failure or FIFO overread.

An accelerated second case establishes a possible consequence. Assuming
uninterrupted stereo packets with no readiness reset, the 32-bit subtraction
eventually reaches the 144-byte threshold. The audit calculates that prefix
and seeds the preceding counter value, then executes the actual callback:
it requests **38 FIFO words with only 10 words left in the supplied packet**.
The prefix is arithmetic, not hundreds of millions of emulated callbacks.
Whether real hardware maintains that readiness pattern, and how its FIFO
responds, remain unknown. No hardware crash, dropout or time-to-failure is
claimed from this test.

**Why existing tests missed it:** the older pump harness supplies an unlimited
zero-valued FIFO and readiness stimuli. Its mixed-alternate cases check word
counts and stock/candidate equivalence while expressly excluding packet-tail
accounting. Both images share the defect, so those comparisons pass.

**Required follow-up:** make frame size, prefetch length and buffered-tail
termination consistent with the selected alternate, including stop/restart
and alternate changes. Changing only the subtraction is insufficient. If
stereo playback cannot be validated, withdraw that advertised alternate and
review the original endpoint-table assumptions. Retain one mainline build.
The 18-channel fixtures do not reproduce this accounting defect, but they
are not comprehensive USB timing tests.

## Retained features and remaining uncertainty

| Feature | Adversarial checks and result | Remaining uncertainty |
| --- | --- | --- |
| Routing and end stops | Re-ran every permitted source/destination, invalid IDs, mono pair skips, duplicate raw PC sources, Auto restoration and end-stop reversals; no new defect | Numeric DSP behavior, clicks during sequential stereo writes and worst-case command timing |
| SELECT/TEMPO gesture | Reviewed original physical callback through queue draining; existing tests cover normal taps/releases, other buttons, pages, modals and alternate modes | Physical timing and unusual simultaneous panel activity |
| UI/DSP shared routing state | New test suspends six edits at **1,997 boundaries**, runs actual routing refresh on a separate stack, then resumes; cache, current scene and latest-system records retain the intended edit | Twenty-four internal Thumb IT-block boundaries are excluded because Unicorn cannot faithfully suspend there; block entry/exit are covered. No exhaustive scheduler or scene-copy race claim |
| Snapshots/restart | Original 64-scene copies, boot restoration, invalid/retired IDs, preservation of unrelated bytes, and original autosave comparison/deadline pass | Real flash save/reload and power-loss behavior remain physically untested |
| USB initialization/control | All three configured rates, malformed requests, response lengths, endpoint tables, startup/error/backup paths pass | Capture-first bus traffic, actual clock lock, every channel/rate, reconnect and sustained operation need hardware evidence; stereo OUT has the defect above |
| Placement and boot | Original startup/MPU, allocator bounds, untouched component/container checks and committed binary identity pass | These checks cannot certify hardware stability; executable slot still has only 20 bytes free |

The packet tests model FIFO length/readiness and numeric conversion. The
routing interleavings execute the compiled get/store/flush paths with code
write protection; parameter lookup, event delivery and DSP programming are
stubbed. Their distinct UI/DSP stacks avoid corrupting the suspended frame.
The initial exploration attempted 2,021 trace positions; the final reproducible
test explicitly excludes the 24 IT-internal positions rather than claiming
coverage the emulator cannot provide.

Persistence has several established limits rather than newly found defects:
stock autosave waits 1,500 timer ticks after the last observed change; an
immediate power-off can lose a recent edit. Old snapshots restore Auto.
Roland text backups omit the custom reserved fields, and factory initialization
clears them. See [storage behavior](ROUTING_STORAGE.md).

## Reproduce the evidence

```sh
.venv/bin/python tools/reproduce.py
.venv/bin/python tools/check_reproduction.py --check-committed
.venv/bin/python evidence/adversarial-review-20261102/reproduce.py
```

All 17 normal stages and the committed-artifact gate passed during this review.
The separate audit reproducer exits successfully when these **observations,
including the known defect**, match. It is not an acceptance gate or a claim
that stereo playback passed. It pins the exact original and candidate hashes;
a future firmware fix needs its own regression expectations.

[Structured results](../evidence/adversarial-review-20261102/report.json),
[original instruction excerpts](../evidence/adversarial-review-20261102/instructions.asm)
and [the reproducer](../evidence/adversarial-review-20261102/reproduce.py)
preserve the evidence and model boundaries. No mixer was accessed or flashed.
