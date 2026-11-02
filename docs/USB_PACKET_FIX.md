# Stereo USB playback packet fix

The current mainline corrects the [stereo accounting defect](ADVERSARIAL_REVIEW.md)
in the original playback pump. Candidate SHA-256:
`dacb12ae966da96176a4c40c8fb736a021ff0a5091d06c800192bcb547474211`.
This image has offline validation only. The preceding `88457445…` image's
boot and iPhone/AUM result do not constitute acceptance of this change.

## Behavior

| OUT alternate | Frame size | Normal two-frame prefetch | Playback lanes |
| --- | ---: | ---: | --- |
| 1, 18 channels | 72 bytes | 36 words / 144 bytes | 0..17 |
| 2, stereo | 8 bytes | 4 words / 16 bytes | 16..17; other lanes zero |

The byte counter now decreases by the selected frame size. One or two
remaining frames are prefetched into the end of Roland's existing 144-byte
buffer; playback returns to packet loading exactly at that buffer's end.
One-frame packets also re-arm correctly without unsigned underflow.

The pump remembers the previous OUT alternate in one byte. An alternate
change, including alternate 0, discards the previous software playback state
and tail, then uses the original phase-based startup handshake. It cannot
interpret a stereo tail as 18-channel data or keep playing an old 18-channel
tail as stereo. IN configuration is independent.

Zero-length and partial-frame lengths take the silent reset path before any
FIFO reads. This bounds software accesses; recovery from a malformed packet
still depends on real peripheral packet/reset behavior, which is not emulated.
No new endpoint reset or stall sequence is invented.

## Placement and ABI

The change is in **app_main** only. The new Thumb assembly replaces 438 bytes
at decoded offset `0xda0ec`, runtime `0x01009860..0x01009a16`. The original
startup mapping copies decoded `0xd0b8c` to runtime `0x01000300`.
`patches/usb_playback.S` assembles into this exact existing instruction window;
the linker and builder reject overflow, unexpected sections or entry points.
`tools/usb_playback_patch.py` guards every original overwritten byte. The build
report records both byte strings, hashes, runtime bounds and continuation.

The original callback entry at `0x01009840`, its stack frame and phase tracking
remain unchanged. The replacement makes no calls or extra stack allocation.
It uses the same integer/float conversion registers and the original
`INT_MIN` → float(-1) special case. Capture at `0x01009a16`, its constants and
the original epilogue remain byte-identical. Registers required by capture
are checked at its entry in every new pump test. Keeping `r12=1` preserves
capture-first priming; the former isolated patch at `0x01009a06` is superseded
by the complete guarded playback window.

The alternate byte is at `0x010173f2`, formerly padding after the 14-byte EP0
reply buffer. It remains inside the existing 400-byte writable reservation
and is cleared by the existing startup BSS clear. Descriptor, reply and
routing addresses do not move. Clock replies are tested for leaving this byte
unchanged. MPU and allocator configuration do not change.

The extension load image remains byte-identical:
`859b0ffc16473fcefcce41c53029821f1013c206f8b00d32203fbbc0e166be68`.
Its code slot still has 20 bytes free. No SDRAM code, generator callback or
additional firmware build is introduced.

## Verification

`tools/usb_packet_verify.py` runs the actual candidate pump with a finite
packet FIFO. A read beyond the supplied packet fails even if another packet
is queued. The tests cover:

- Stereo and 18-channel packets containing 1..14 complete frames, with exact
  output order, bounded counters, tail consumption and next-packet re-arming.
- The old 48-byte stereo packet as a negative control: its counter still
  reproduces `0xffffffe8` with the predecessor instructions.
- Direct and buffered silence, positive/negative samples and the minimum
  integer special case.
- All four IN/OUT alternate combinations at 44.1, 48 and 96 kHz with varying
  packet lengths. For 18-channel OUT, output samples, FIFO reads, capture
  samples, commits, reset writes and state/counter traces match the predecessor.
- Cold startup, capture without OUT, readiness loss/restart, alternate 0,
  and 2↔18 transitions during direct playback and either buffered-tail frame.
- Zero/partial-frame lengths, callee-saved registers, stack restoration and
  the original capture entry's register contract.

The seven packet groups are part of the normal `arm-mainline` stage. Their
report is `build/mainline/packet-verification.json`; the final evidence gate
requires its application hash to match the current image. All 17 reproduction
stages, 33 unit/descriptor tests and five bridge tests passed locally.

FIFO readiness, packet delivery, conversion and peripheral flushing on an
alternate change are modeled. These results establish instruction behavior,
not USB feedback timing, real reset handling, converter scaling or deadline
margin. The loops remain bounded by 18 sample lanes and at most 36 prefetched
words. Instruction counts are not cycle measurements.

Hardware acceptance still needs stereo and 18-channel playback/capture,
mixed alternates, all rates, stop/start, reconnect and sustained operation.
No device was accessed or flashed while producing this fix.
