# Retired separate candidates

These JSON reports preserve historical evidence from commit 6322349, before
mainline consolidation. They are not reports for the current combined image.
The corresponding source/build artifacts remain in Git history, not as active
builders or candidate binaries. The USB-host unlock is documentation only in
`docs/HOST_PROBE.md`. The old USB-B build had read-only-memory placement defects;
its earlier offline report did not enforce MPU write protection.

The user confirmed the routing endpoint build
`221e5ffb2a858a25d5691a1c818324fafa117bfa48d6a79aac0d666140ff2b95`
worked on their MX-1 on 2 November 2026. No exhaustive source/rate/mode matrix
or instrumented timing/recovery data was supplied. The combined mainline image
has not inherited that physical validation automatically.

The boot audit incorporated into mainline originated in PR #2, commit
4840c9e1ed05d9f4cb1a8dadd7c69aa2a30896de. Its state-location guard and startup
expectations were updated explicitly for the mainline code/data reservations.
The former display-marker diagnostic (PR #3) is excluded from the maintained
firmware; its purpose and user-reported result remain in the historical notes.
