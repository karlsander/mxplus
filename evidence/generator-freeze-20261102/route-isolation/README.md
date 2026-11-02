# Generator DSP-source isolation

The preceding RAM-publication experiment still froze with P9r displayed.
This next one-off test retains its owned RAM sample sink and the complete
generator computation, and changes only the DSP input operand used when a
channel selects NSE or BD: both use the established P9r operand `0xa011`.
Their IDs, labels, generator-active masks, UI and persistence remain intact.
This intentionally routes P9r audio, not generator audio. Test selection and
control responsiveness with monitoring muted and USB disconnected.

Candidate SHA-256:
`4010c85b98b67837138ba97efecf18beac64cf2ee296c33953686abe0b530395`.

Compared with the preceding RAM-publication image, code grows by 16 bytes to
6,748 bytes; writable state stays 1,560 bytes and the sample sink stays at
`0x0101783c`. Both remain within their existing reservations. Main-component
patch offsets, runtime addresses, startup-copy adjustments and checksums are
recorded in the build report. Boot, updater, USB processor and panel components
remain unchanged.

The original main-application raw operand writer at decoded `0xdb390`, relocated
runtime `0x0100ab04`, writes command/data to `0x40100900/04` and returns. It has
no software polling loop. Its successful execution in the instruction harness
does not model how the real DSP behaves when reading an unsupported operand.
The earlier image used noise `0xa040` and per-strip BD `0xa041 + strip`; their
physical exchange indices are still unverified.

The routing harness checks all sources on all strips, confirms generator-active
masks, executes the original command writer and rejects generator operands
`0xa040..0xa04b`. The audio harness checks sample output in owned RAM and rejects
access to `0x40101100..0x4010112f`. These are modeled CPU checks; they do not
execute DSP arithmetic or establish real-time deadlines. If this test becomes
stable, the DSP source change is implicated. If it still freezes, active
callback execution and generator-specific UI/control behavior remain suspects.
Neither outcome validates the abandoned physical sample bank.

Forensic reproduction: apply `historical-source-delta.patch` to maintained
commit `cb0124c49333ce0f54b091a0d7a60908fef26537`, use the pinned environment, then
run `tools/reproduce.py`. This includes the preceding RAM-sink delta. No extra
maintained builder or firmware artifact is introduced.

All 22 offline reproduction stages and the committed-artifact gate passed.
The exact diagnostic sources, artifacts and reports were committed locally as
`c64d77632d613b563634f4a39b296a0057e28a90`. The compiled function inventory is unchanged;
only `mx1_route_flush` changes size (516 to 532 bytes). The image was copied to
the MX-1 update drive, fully readback-verified and successfully ejected. Physical
flashing and selection results are pending.
