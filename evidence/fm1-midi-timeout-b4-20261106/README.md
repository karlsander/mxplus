# B4: isolate the MIDI transmit alarm path

The [live B3 reconnect](../fm1-midi-bridge-b3-20261106/reconnect-b3.json)
captured one startup heartbeat confirming build 179, then no further reports.
Its retained TX completion result was −20; RX was −7. Those results survive
endpoint reopen, so they describe preceding transfers, not necessarily the
newly opened generation. A subsequent status command still timed out.

## Established failure path

All addresses refer to **app_usb**. Resident runtime is decoded offset plus
`60000000`; hot startup copies decoded `2b1f4..36dd8` to
`01000300..0100bee4`. [Original instructions](original-disassembly.txt).

| Decoded offset | Runtime | Finding |
| --- | --- | --- |
| `0f81a` | `6000f81a` | Core allocates an alarm for ordinary bulk requests unless timeout is −1 |
| `10066` | `60010066` | Creates/starts a per-transfer alarm and returns failures to the core |
| `13fc0` | `60013fc0` | Alarm wrapper maps a negative RTOS create result to −20 |
| `2b2dc` | `010003e8` | RTOS create returns −34 when its free alarm count is zero |
| `34998` | `01009aa4` | Original alarm configuration contains five slots |
| `0f7ae` | `6000f7ae` | Core pre-submission failure calls MIDI completion with the original error |
| `0f60a` | `6000f60a` | Normal completion invokes the callback before stopping its alarm |
| `14092` | `60014092` | Stop queues cleanup; it does not delete the alarm immediately |
| `1402a` | `6001402a` | Cleanup deletion returns the alarm to its pool |

The original normal HCD completion dispatcher does not preserve arbitrary
errors: −20 is normalized to −2. The direct pre-submission callback does
preserve −20. The captured value therefore points to that earlier path, which
includes alarm creation/start and lower queue submission. It does **not**
uniquely identify exhausted alarms on the live mixer.

The new instruction test initializes the original five-alarm pool, occupies
all five and executes core submission with timeout 100: it returns −20 through
the completion callback without reaching the HCD boundary. With timeout −1,
the same original core queues the transfer and retains normal completion/error
semantics even with all five slots occupied.

A separate fixture occupies four slots, submits one timed transfer, and models
the callback waking TX before alarm cleanup. The original code queues cleanup
after that wake. A next submission before deletion returns −20; after deletion
it succeeds. This proves a possible ordering, **not** the hardware's actual
alarm occupancy, task timing or cause. RX −7 is still unresolved.

## Bounded diagnostic change

B4 (180) passes timeout −1 only when the endpoint belongs to the currently
matched FM-1 debug session, with current VID/PID/speed checked again to
exclude a recycled object address belonging to a different device. All MIDI OUT for that session uses this setting,
including musical data and legacy diagnostics. Other generic output retains
timeout 100; Roland follows its unchanged path. IN retains timeout −1 and the
B3 short-packet flag. No error is masked and no failed write is replayed.

Each direction still has at most one outstanding buffer. An untimed write
which never completes keeps its buffer until completion or stock disconnect
cancellation; no new watchdog is provided. Close/reopen generation handling,
full-write validation and error isolation remain. This is a bench experiment,
not a production timeout/recovery solution. EHCI audio stays disabled at alt0.
The FM-1 bridge remains B1, with no firmware or Mac client update needed.

## Identity and verification

Candidate SHA-256:
`389ae886e3ab6af87804f375f9752e3099fc77bd5e157f2c7e8c6ee62d7bfd7c`.
Only the USB application changes from B3. Hot code grows 48 bytes to 3,032 at
`0100bee4..0100cabc`, leaving 1,348 bytes before allocator start `0100d000`.
Audio/debug code grows 76 bytes to 8,536 at `607f0000..607f2158`, within its
16-KiB slot. Hot state stays 1,472 bytes; SDRAM state stays 25,956 bytes inside
the existing 64-KiB reservation. Main application, boot programs, updater and
panel payload retain their bytes. No new original patch sites are introduced;
the [build report](../../build/mainline/build-report.json) accounts for exact
bytes, branch targets, source hashes, placement, relocation and checksums.

`tools/host_midi_core_verify.py` runs original core submission/completion,
alarm initialization/create/start/stop/delete and wrapper instructions.
Heap/free, endpoint-list lookup, critical sections, timer-wheel insertion,
mailbox delivery, lower HCD and task preemption are modeled. It does not test
allocator corruption, full RTOS scheduling, USB delivery or timing.

Compiled extension tests check untimed writes only for the matched device,
multi-transfer responses, one outstanding buffer, stock cancellation and
retained completion ownership. Existing tests keep generic timeout 100,
short-input handling, queue failures, Roland behavior and audio regressions.
The candidate record records final validation; hardware acceptance is pending.
