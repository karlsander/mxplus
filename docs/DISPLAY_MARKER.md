# Display identity diagnostic

Candidate: [`MX1_DISPLAY_MARKER_UNTESTED.bin`](../build/display-marker/MX1_DISPLAY_MARKER_UNTESTED.bin).

This temporary diagnostic makes normal display characters become **8**. On the
normal panel, expect **`888` on VALUE** and **`8888` on TEMPO**, without holding
SELECT. Normal menus, values and error text rendered by the same application
routine are masked. Do not use this image for ordinary operation.

It starts from the exact original firmware. It contains no channel-routing or
USB extension. The separate updater remains original, so its update messages,
including `Fin`, are unaffected. Raw segment writes can bypass this patch;
the claim applies to the shared text/number character path.

**Status: built and verified offline; visible physical output from this
diagnostic has not been observed.** The preceding routing update was reported
to finish and restart, but SELECT did not show its source label. That observation
does not distinguish an inactive hook from an image-installation problem.

## Exact change

The input is `inputs/MX1_UPD.original.bin`, SHA-256
`26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`.
The diagnostic container SHA-256 is
`f65983ecad6850bc88968a01ff5f008dea62e4e06410d451144a72514cd98e9c`.
The [build report](../build/display-marker/build-report.json) records the decoded
application hash, component checksum, patch bytes, source hash and slot bounds.

| Component | Decoded offset | Runtime address | Old bytes | New bytes |
| --- | --- | --- | --- | --- |
| Main application | `0xd3098` | `0x0100280c` | `1c46` (`mov r4,r3`) | `3824` (`movs r4,#0x38`) |

The first original startup copy takes main decoded bytes beginning at `0xd0b8c`
to SRAM `0x01000300`. This maps decoded `0xd3098` to runtime `0x0100280c`.
No source, destination, length, initialized data, BSS or allocator reservation
changes. The decoded application retains its original size; no extension or
new runtime storage is added.

The character function at `0x0100280a` still performs its original register
push/pop, display guard, font-table lookup and segment-delivery call. The changed
instruction substitutes ASCII `8` for the incoming character before the lookup.
The original font supplies segment bits `0x7f`. A later original `cmp r1,#2`
overwrites the MOVS condition flags before the function consumes flags. There
is no new branch or callback target, and the original stack frame is unchanged.
The incoming character's decimal-point bit is also suppressed by the constant.
Display and digit positions and the separate delivery flags are retained.

Only two **decoded application** bytes change. The stored main application is
repacked with the existing literal-only encoder, so many container bytes and
the stored main checksum change. The container size, component boundaries and
standard update plan remain unchanged. Every container byte below `0x80000`
and from `0x200000` through the trailer matches stock: both boot programs,
updater, panel controller and USB-host application are preserved.

## Reproduce and verify

Install the pinned root requirements and run:

```sh
.venv/bin/python tools/build_display_marker.py
.venv/bin/python tools/display_marker_verify.py
.venv/bin/python tools/reproduce.py
.venv/bin/python tools/check_reproduction.py --check-committed
.venv/bin/python tools/display_marker_verify.py --check-committed
```

The final diagnostic gate compares the actual candidate/application blobs and
build report committed at Git `HEAD`, so it follows a commit of the reviewed
artifacts. A newly created candidate cannot pass that gate before it is committed.
The original three candidates remain byte-identical and retain their separate
22-stage reproduction gate. CI additionally builds and checks this diagnostic.

The [verification report](../build/display-marker/verification.json) records:

- Reconstruction of the complete decoded change from the one guarded site.
- Execution of actual startup copies and confirmation of the changed SRAM
  instruction, with every initialized/zeroed region checked.
- 3,584 direct-character cases: all 256 byte values at all seven positions of
  the two displays, with two delivery-flag values. Every result matches the
  original `8` glyph; r4–r11 and SP are preserved. Three invalid positive
  display indices retain the original no-output behavior.
- Original text, signed integer and decimal-format loops for both displays.
- Original normal tempo-renderer execution, with no held keys, producing four
  `8` glyphs instead of the stock parameter fixture's output.
- Original decoder acceptance, update-label/trailer handling, all 704 modeled
  sector writes/readbacks and post-write component checksums for this exact file.

Direct character and formatter tests stub only the final segment-delivery
boundary at main runtime `0x0100d134` (decoded offset `0xdd9c0`). The normal
tempo-renderer case additionally uses the existing UI harness's explicit
parameter/modal/RTOS boundaries. Font lookup executes unchanged; the tests do
not stop at the earlier character boundary used by the routing UI tests.
File/flash I/O in the updater tests is modeled. These are not observations of
panel communication, visible LEDs, actual flash, complete boot or recovery.

## First observation

Use the documented MX-1 update procedure for this specifically authorized
experiment. Keep the `UNTESTED` source filename and make only the update-volume
copy `MX1_UPD.BIN`. After `Fin`, turn off, then start normally without buttons
held. Look for `888` and `8888` before pressing anything. Record the exact file
hash and what each display shows. Return to the original firmware when the
identity observation is complete; ordinary display values are masked here.

The existing device-specific recovery uncertainty remains. This diagnostic
does not alter boot/updater bytes or establish a new recovery method. Physical
work still follows [the hardware-validation plan](HARDWARE_VALIDATION.md).
