# Generator callback isolation

The user reports that the preceding RAM-publication and established-DSP-source
image still freezes when advancing beyond P9r, before NSE appears. This third
one-off test retains those two substitutions and makes the sample wrapper call
only the original USB sample pump. It does not call the generator renderer or
its invalidate function in any DSP mode. NSE/BD IDs, labels, routing active-mask
publications, UI, storage and P9r operand `0xa011` remain unchanged. The renderer
stays linked and separately tested, but is not invoked by the sample interrupt.

Candidate SHA-256:
`f4f5b93ed7b92ee0bb27a2a594b351a04bd10913100f8038ceb302e0a274f497`.

The production source change relative to the preceding diagnostic is confined
to `patches/internal_sources_audio.c`. Code shrinks from 6,748 to 6,700 bytes;
writable state stays 1,560 bytes. Both stay within the existing reservations.
The main application's original callback pointer at decoded offset `0x168c`
still registers the compiled wrapper. Build-report patch records include exact
old/new bytes, runtime targets, startup copies and component hashes. Boot,
updater, panel and USB-processor components remain stock.

The diagnostic audio harness traps entry to the linked renderer, marks all
eleven BD sources and noise active, and runs the original interrupt dispatch
and USB pump across three rates, seven DSP-mode fixtures and eight USB stream
fixtures. It compares original MMIO/FIFO traces and state, checks preserved
registers/stack, and verifies that the RAM sample sentinel and active mask stay
unchanged. The inferred physical generator bank remains forbidden. This
replaces the production callback's rendering expectation with the experiment's
explicit bypass contract; standalone core tests still execute the renderer.
FIFO readiness, conversion and clock phase remain modeled. No real interrupt
cadence, execution cycles, DSP arithmetic or physical stack margin is measured.

Test with monitoring muted and USB disconnected: advance from P9r to NSE and
check the label and controls. This intentionally produces no generator audio;
the selected channel still reads P9r. A stable result implicates the active
renderer or interrupt cost; another freeze leaves selection/display/control
behavior as the next target. The original physical generator exchange mapping
remains unvalidated regardless of this test's result.

Forensic reproduction: apply `historical-source-delta.patch` to maintained
commit `cb0124c49333ce0f54b091a0d7a60908fef26537`, use the pinned environment,
then run `tools/reproduce.py`. The patch includes the previous RAM-sink and
DSP-source substitutions. This is not another maintained firmware build.

All 22 offline stages and the committed-artifact gate passed. The diagnostic
sources, artifacts and reports are recorded in local commit
`116a59994ac23e4e4d7099f2129b8f0ce2867283`. The image was copied to the MX-1 update drive,
fully readback-verified and successfully ejected. Hardware selection result
is pending.
