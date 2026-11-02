# Mixer snapshots: original serial-flash storage mechanics

This report records the original main application's storage path for mixer
scenes and the capacity available for a separate NSE/BD snapshot extension.
It does not establish physical flash operation, programming latency or
power-loss recovery. All addresses below refer to the frozen MX-1 main
application; these resident routines have decoded-image offsets equal to
their runtime addresses minus `0x60000000`.

The reproducible audit is
[tools/internal_sources_storage_audit.py](../tools/internal_sources_storage_audit.py).
Its report is
[analysis/internal-sources-storage-audit.json](../analysis/internal-sources-storage-audit.json).
The audit requires original container SHA-256
`26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e`
and decoded main SHA-256
`256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b`.

```sh
.venv/bin/python tools/internal_sources_storage_audit.py \
  inputs/MX1_UPD.original.bin \
  --output analysis/internal-sources-storage-audit.json
```

## Native storage uses registered ring records

The source-name strings around decoded `0xdf84` identify `storage\sf_bios.cpp`.
The actual instructions establish a registry of payload ranges, each with an
append cursor, a sequence counter and one or more flash sectors. This is not
a filesystem write performed by the scene UI.

The storage manager object is at `0x606621e0`; its first backend pointer is at
offset eight and points to `0x6064c108`. The latter is the serial-flash backend.
Its vtable is the original table at `0x600a9100`.

| Operation | Main runtime address | Decoded offset | Calling interface |
| --- | --- | --- | --- |
| Initialize backend | `0x6000db96` | `0xdb96` | `backend` |
| Register all stock parameter groups | `0x6000c8e0` | `0xc8e0` | Original parameter-storage object; no field is read from it in this routine |
| Register payload | `0x6000dc7a` | `0xdc7a` | `backend, group, automatic, source, bytes, copies, flash_offset` |
| Read latest payload | `0x6000ddd6` | `0xddd6` | `backend, group`; returns one only when every registered chunk has a valid record |
| Mark a RAM range dirty | `0x6000de7c` | `0xde7c` | `backend, group, source, bytes, reset`; returns one when the range is consumed |
| Consume dirty flags | `0x6000e058` | `0xe058` | `backend`; returns packed work flags |
| Assemble and write pending records | `0x6000dee6` | `0xdee6` | `backend` |
| Compare automatically saved RAM ranges | `0x6000e0f0` | `0xe0f0` | `backend`; marks work after the original delay |

Arguments beyond the fourth occupy the caller's stack under the existing
Thumb ABI. A group registered with `automatic = 0` is written only after an
explicit dirty publication. Normal saves use `reset = 0`. The reset flag
requests erasing the whole allocation and restarting its history; it is not
needed for ordinary append saves.

The generic manager adapter at `0x6000e1c2` forwards dirty notifications to the
backend. In contrast, the read adapter at `0x6000e1e4` also writes a status
array sized for the fifteen stock groups. A new group outside that range must
use the backend reader directly, or separately extend that status contract.

The normal boot sequence calls the stock registration routine at resident
`0x6000d800` (original four bytes `fff76ef8`, a `BL` to `0x6000c8e0`) and the
stock group-read routine at `0x6000d808` (bytes `fff7b2f8`, a `BL` to
`0x6000c970`). Registration finishes before that read begins. Any extension
must be initialized and loaded before the subsequent scene-to-current copy.

### Initialization precondition

Registration initializes both record and sector cursors to `0xffffffff`.
The original reader resets them to a defined zero position even if it finds
no valid record. Every newly registered extension group therefore needs an
initial read before its first dirty publication. Skipping this read can leave
the sector cursor at minus one for a small record and produce an incorrect
write address.

## The unchanged stock allocation ends at `0x348000`

The backend initializer sets its first and next allocation offsets to
`0x300000`. The configuration pointer at main decoded `0xcd40` refers to
`0x60068658`: eight tag bytes `P1T01   `, fifteen requested-copy counts, then
fifteen explicit-address values. Each persistent stock group requests two
copies and uses `0xffffffff` to request automatic placement.

The group-description pointer at decoded `0xcda4` refers to `0x6006ed08`.
Each sixteen-byte entry contains the first parameter number, word count per
instance, instance count and persistence kind. The scene group is entry two:
268 words by 65 stored instances, or 69,680 bytes. Its stored RAM range is
`0x604f4444`–`0x60505474`; its current working instance is immediately before
that range. The 65 stored instances cover the temporary/current snapshot and
the 64 numbered scenes.

The audit executes the unchanged stock registration routine with the real
configuration and parameter-area tables. Only heap allocation is supplied
by the harness. It constructs these thirty-six backend descriptors:

| Stock group | Payload bytes | Descriptor chunks | Allocated flash offsets, end exclusive |
| --- | ---: | ---: | --- |
| 0 | 564 | 1 | `0x300000`–`0x302000` |
| 2, mixer scenes | 69,680 | 18 | `0x302000`–`0x326000` |
| 6 | 4,160 | 2 | `0x326000`–`0x32a000` |
| 7 | 1,280 | 1 | `0x32a000`–`0x32c000` |
| 8 | 1,856 | 1 | `0x32c000`–`0x32e000` |
| 9 | 704 | 1 | `0x32e000`–`0x330000` |
| 10 | 31,296 | 8 | `0x330000`–`0x340000` |
| 11 | 4 | 1 | `0x340000`–`0x342000` |
| 12 | 56 | 1 | `0x342000`–`0x344000` |
| 13 | 5,888 | 2 | `0x344000`–`0x348000` |

Groups 1, 3, 4, 5 and 14 have no persistent allocation in this registry.
The allocator's upper comparison literal at decoded `0xdf80` is
`0x003fefff`. The separate factory flash test at `0x60001872` explicitly
erases and writes the sector selected by decoded literal `0x1ac0`, which is
`0x003ff000`. That last sector must remain excluded.

Thus the recovered stock allocation contract leaves
`0x348000`–`0x3ff000` outside all existing registered payloads and below the
diagnostic sector. This conclusion comes from executed allocation arithmetic
and recovered flash users, not from observing zero or erased padding in an
update file. It is still evidence about this firmware revision's map, rather
than a certification of an undocumented physical flash part.

## Record layout and rotation

For payloads of at most 4,064 bytes, registration rounds `payload + 32` up to
a multiple of 256 bytes. It packs as many complete records as fit in a
4,096-byte sector and allocates enough sectors for the requested count, with
a minimum of two sectors. Larger payloads are split into 4,064-byte chunks;
each chunk retains a full 4,096-byte record and its own sector history.

| Record location | Contents |
| --- | --- |
| `+0x00..+0x07` | Eight-byte backend tag |
| `+0x08..+0x0b` | 32-bit sequence counter |
| `+0x0c` | Group identifier |
| `+0x0d` | Chunk identifier within that group |
| `+0x0e..+0x0f` | Remaining backend header bytes; not compared by the recovered validator |
| `+0x10` onward | Registered payload bytes |
| After payload | `0xff` padding up to the trailer |
| Final sixteen bytes | Mirrored header |

The validator at `0x6000dc10` checks both tags, both group identifiers, both
chunk identifiers and matching sequence counters. The reader scans every
record position and selects the largest valid counter independently for each
registered chunk. It copies only the registered payload length into RAM.

The writer advances the record cursor. Crossing a sector boundary advances
and wraps the sector cursor, erases that next sector, then programs the new
record. It constructs the header, payload, erased padding and trailer in the
backend's existing working buffer. No write occurs merely from marking a
range dirty; the existing storage task later consumes and writes it.

There is **no payload checksum in this backend validation**. The audit flips
one payload byte while retaining both headers and observes the original
reader accepting the altered payload. A new snapshot format needs its own
integrity check. Mirrored headers also do not establish atomicity across the
eighteen independent native scene-bank chunks.

## Extension capacity demonstrated with the original implementation

The audit appends 65 independent groups, identifiers 15–79, with a synthetic
740-byte payload per scene. This is a capacity fixture rather than a mandate
for the final serialization format. It keeps every existing descriptor's
payload, address, record size and sector allocation unchanged.

Each new group uses a 1,024-byte record and two 4,096-byte sectors. All 65
groups consume `0x82000` flash bytes, from `0x348000` through `0x3ca000`.
The remaining space before the excluded diagnostic sector is `0x35000`
bytes. The descriptor allocations consume 65 × 88 = 5,720 heap bytes, in
addition to the extension's own scene-data buffers.

The fixture executes eleven saves to the final scene through the original
dirty publication, polling, record construction and flash-read selection.
The modeled flash enforces erase-before-program bit transitions. These saves
exercise appending, both sectors and sector wraparound. Every recalled
payload matches its saved bytes, and every flash byte outside that scene's
two-sector allocation remains unchanged.

A separate small record per scene keeps the entire extension payload in one
record, unlike a large combined extension bank that could split a scene
across independently committed chunks. Its own format version and checksum
can reject uninitialized, unsupported or damaged extension data. Binding the
extension to the corresponding stock scene contents can additionally reject
stale data after stock-only restore or an interrupted combined save. That
binding alone does not detect a factory reset which happens to produce
identical stock bytes; unconditional reset semantics require a reset hook.

## Physical flash boundary and backup behavior

The low-level routines called by the backend are:

| Operation | Main runtime address | Behavior established from instructions |
| --- | --- | --- |
| Program bytes | `0x60003238` | Splits writes into 256-byte calls to `0x6000336e` |
| Read bytes | `0x60003286` | Copies words from mapped flash at `0x03000000 + offset` |
| Erase sector | `0x600032be` | Supplies the flash address and erase command through controller registers rooted at `0x40005000` |
| Change access mode | `0x60003158` | Switches original controller mode |
| Write-protection transitions | `0x600031e6`, `0x60003194` | Perform original controller/boot-service operations around writes |

The audit models these physical operations, heap allocation and RTOS critical
sections. All storage-list traversal, allocation arithmetic, dirty scheduling,
record byte assembly, append/erase selection, validation and payload copies
execute as unchanged ARM instructions. No hardware is accessed.

The recovered non-backend flash writers are the factory test and raw user-area
restore. The raw backup at `0x6000e9ac` copies the full mapped one-megabyte user
area; its corresponding restore at `0x6000ea2e` rewrites that whole range.
Those raw paths include a new allocation in the same area. The ordinary
text-form mixer backup serializes known stock parameters and will not include
the extension without an additional format change.

Physical erase/program timing, flash-controller behavior, power interruption,
concurrent task behavior and boot/recovery remain hardware validation tasks.
