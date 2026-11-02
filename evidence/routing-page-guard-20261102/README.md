# Routing page-guard evidence, 2 November 2026

The previous build/UI reports are preserved from origin/main `9c98aa3`.
The new startup-page regression fails against that exact candidate with
`AssertionError: ('Startup-selected page rejected', 0, 5)`.
Current build and UI reports are in `build/routing-probe/`.

`fixed-boot-audit.json` was generated using the unchanged
`tools/boot_path_verify.py` from PR #2, commit
`4840c9e1ed05d9f4cb1a8dadd7c69aa2a30896de`, with `--build` pointing to this
revision's routing output. Its candidate hash identifies the tested image.
The updater branch, startup relocation, allocator reservations and empty Auto
drains pass under the audit's documented stubs. This is not hardware recovery
proof. See https://github.com/karlsander/mxplus/pull/2.

The user reported that the earlier routing image updated/restarted normally,
but holding either 5/6 or USB2 SELECT in Mixer mode retained the usual tempo.
The independent display-marker image subsequently showed the expected visible
marker. These are user observations, without flash readback or instrumented
audio, timing, board-identification or failure-recovery results.
