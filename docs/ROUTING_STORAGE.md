# Routing snapshots and restart persistence

The mainline candidate saves routes with all 64 mixer snapshots and restores
the latest routes on normal startup, independently of the startup scene. This
has passed offline instruction tests; physical save/recall and restart tests
are still required. The previous RAM-only routing image's bench results do not
validate this new behavior.

After changing a route or recalling a snapshot, leave the mixer on for several
seconds before switching it off. The stock system autosave waits 1,500 timer
ticks after its last observed change before scheduling a write. Offline tests
establish that arithmetic, not real-time completion or power-loss durability.
Snapshots retain their explicitly saved routes; editing a route does not
silently overwrite a saved snapshot. Old snapshots without a route record
recall Auto. Returning to stock firmware ignores the custom reserved fields.

**Roland text backups do not export custom routes.** Their field whitelist
omits the reserved parameters. Factory initialization clears the reserved
fields. No custom export format or additional firmware variant is provided.

## Frozen storage contract

All addresses below are in the **main application**. Resident instruction and
metadata decoded offsets are runtime addresses minus `0x60000000`. RAM buffers
are runtime addresses, not firmware file offsets. The original startup map
establishes their allocation; the patch does not enlarge them.

| Object | Evidence | Layout |
| --- | --- | --- |
| Parameter areas | decoded `0x684f0`, runtime `0x600684f0`; original accessor `0x6000bdd6` | System current at `0x604f39a4`, saved at `+564`; mixer current at `0x604f4014`, 65 saved slots at successive `+1072` offsets |
| System group 0 | decoded `0x6ed08`, runtime `0x6006ed08` | IDs 0..140, 141 words, one saved instance, storage mode 2 (automatic) |
| Mixer group 2 | decoded `0x6ed28`, runtime `0x6006ed28` | IDs `0x10f..0x21a`, 268 words, 65 saved instances, mode 1 (explicit) |
| Parameter descriptors | decoded `0x686d8 + ID*16` | IDs `0x10..0x13` and `0x182..0x185` have min/max/default zero and names `_reservd_`; all descriptors remain unchanged |
| Scene record | runtime `0x604f41e0`, current mixer offset `0x1cc` | Four reserved words, copied unchanged by stock scene operations |
| Latest record | runtime `0x604f39e4`, current system offset `0x40` | Four reserved words; stock autosave copies them to `0x604f3c18` with the other system settings |

Each record is 16 bytes: ASCII `MXR1`, eleven stable source IDs (0..52 in
physical-strip order), and one zero padding byte. Unknown magic/version gives
all Auto; out-of-range IDs and stereo-pair IDs on mono strips individually
fall back to Auto. The fifth reserved mixer word is untouched. The original
parameter getters still see reserved parameters as zero because their range
metadata is unchanged. New code accesses only the guarded reserved words.

The builder guards the original area table, group counts/storage flags,
reserved descriptors, boot call and every overwritten instruction, in addition
to the complete input hash. It does not change flash geometry, storage headers,
block sizes, wear-leveling, erase/program routines or MPU configuration.

## Original paths and integration

- `0x6001e734` saves a mixer scene through original group-copy and storage
  request helpers. `0x6000c182` copies all 1,072 bytes, including reserved words.
- The ten-byte entry at decoded `0x1e786` / runtime `0x6001e786` is replaced
  with the guarded routing-recall veneer. Its trampoline reproduces the
  original push, register moves and stack setup, then continues at
  `0x6001e790`. The original remainder and return execute unchanged. The
  wrapper uses the original `r0=context, r1=scene index` ABI, preserves callee-
  saved registers/stack, then restores and validates routes.
- Normal startup calls recall at `0x60056990`, returning to `0x60056994`.
  Only that caller restores the latest system record instead of the startup
  scene's record. Ordinary recalls use the selected scene's routes. An event-8
  post after restoration ensures the DSP gets the final routes even if its
  higher-priority task already processed the original scene notification.
- `route_ready` occupies the former padding byte at `0x0101727a`; original
  startup clears it. Before normal recall completes, route refreshes cannot
  overwrite the system record. Desired/applied arrays retain their addresses.
- UI edits commit the locally calculated source after serializing the route
  cache. A DSP refresh that preempts the UI cannot discard that local edit.
  DSP drain refreshes read the current scene record; reset/default operations
  therefore return routing to Auto on their next parameter notification.
- Original storage registration `0x6000c8e0` is unchanged. Its system block
  registration selects autosave; scene blocks retain explicit writes.
  `0x6000e0f0` compares current system bytes with the saved shadow, copies changed
  bytes and sets the 1,500-tick deadline. `0x6000e058` marks the pending write
  after expiry. New code writes only the current system record, leaving the
  shadow dirty so the original comparison can detect the change.

Source descriptors now encode the stereo-pair flag in the otherwise unused
`0x1000` operand bit and use six bytes per entry instead of eight. Generated
operands mask that bit; the full original audio-routing regression suite
checks the resulting operands. This keeps the extension inside the same
reviewed executable SRAM slot; it does not expand executable memory.

## Evidence and limits

`build/mainline/storage-verification.json` runs original ARM scene save/copy/
recall and autosave comparison/deadline instructions. It checks all 64 user
slots, untouched scene bytes, a fresh-machine restart, edits that preserve
snapshots, invalid records, an injected DSP-cache refresh during an edit,
post-recall DSP notification, and unchanged storage registration.

Singleton lookup, notification delivery, mutexes, time and a storage-node
fixture are modeled. Save requests are captured at the storage API; flash
programming and physical power-loss recovery are not executed. Restart tests
supply persisted system bytes to a fresh machine and execute the original
system-copy and normal-boot recall call. They do not emulate physical flash
reads. These boundaries are separate from the mainline boot/MPU/USB/audio
checks and remain explicit in the generated report.

Bench acceptance: save two snapshots with different routes; alternate recalls;
edit without saving a snapshot, wait several seconds, power-cycle, and confirm
the last edited routes return while the saved snapshots remain distinct.
Confirm ordinary scene settings, reset behavior, end stops and audio routing.
Do not use abrupt power cuts as the initial persistence test.
