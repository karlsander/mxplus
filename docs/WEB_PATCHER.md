# Browser firmware patcher

The public patcher is hosted at <https://karlsander.github.io/mxplus/> using
GitHub Pages. GitHub Actions packages, tests and deploys it after mainline
offline verification passes. No separate hosting account, server, database,
upload endpoint or deployment secret is needed.

This is an **experimental preview**, not hardware acceptance or a stable
firmware release. The current candidate retains `UNTESTED`. The website's
installation section explains preparation, the updater filename and the
transfer sequence. [Hardware validation](HARDWARE_VALIDATION.md) remains the
prerequisite for a hardware experiment.

## Use the patcher

1. Download the MX-1 System Program v1.05 from
   [Roland](https://www.roland.com/uk/support/by_product/mx-1/updates_drivers/82415302-0466-4c5c-be4e-138a8946d4a7/)
   and extract its ZIP archive.
2. Open the patcher in a current browser over HTTPS. Choose or drop the
   extracted `MX-1_UPD.BIN`. The original remains on the computer.
3. After the exact original hash is verified, select **Create patched firmware**.
4. Download `MXPLUS_MAINLINE_UNTESTED.bin`.
   The output must match the maintained mainline candidate's SHA-256.
5. Read the site's installation instructions before any device operation.
   Keep the labelled experimental file. Only the separate copy prepared for
   the updater is named `MX-1_UPD.BIN`; keep the stock file elsewhere.

The page does not use WebUSB or perform a hardware update. It rejects other
revisions, corrupt or truncated files, ZIP archives and already patched images.
No filenames or firmware bytes are uploaded. The page requests its own static
assets from GitHub; it has no analytics or third-party scripts. Original and
output files are held in browser memory, without persistent browser storage.

## Distribution design

`tools/build_firmware.py` remains the only firmware builder.
`tools/build_web_patcher.py` is a distribution exporter: it reads the existing
stock and mainline artifacts after `audit(check_committed=True)` passes. It
does not compile another variant or alter firmware. The exact original hash
and container size are enforced independently in both the exporter and client.

The exporter emits ordered, nonoverlapping XOR runs over the **encoded update
container**, identified as `mxplus-xor-v1`. These are container file offsets,
not decoded-image or runtime addresses. Firmware patch sites, relocation,
ABI and component checksums remain in the mainline build report; XOR distribution
adds no new firmware patch sites or runtime memory use.

`manifest.json` records input/output hashes and sizes, experimental filename,
source commit, and a hash-named patch asset. The browser validates the manifest,
hashes the input, verifies the patch asset, checks range bounds/encoding, applies
XOR to a copy, and checks the whole output hash before offering a download.
These checks detect corruption and mismatched releases; they are not
a signature or protection against a compromised hosting account.

Only explicitly listed website files, the manifest and XOR patch are copied
to `build/web-patcher/`. Complete original/patched firmware, build reports,
source trees and historical evidence are not in the Pages artifact. The
repository still contains its existing firmware material; this exporter does
not remove it from Git or settle its redistribution rights. The patch is
derived from the two containers and creates no new licensing grant. See
[provenance](../PROVENANCE.md).

## Deploy and maintain

The [existing verification workflow](../.github/workflows/verify.yml) runs full
firmware reproduction, checks committed evidence, packages the site and runs
the Node tests on every PR. PRs do not deploy. Pushes to `main` and manual runs
on `main` upload only the site directory, then deploy with the `github-pages`
environment. Deployment depends on the successful verification job; it cannot
publish a candidate that failed that run's evidence or patcher tests.

One-time repository setting: **Settings → Pages → Build and deployment →
Source → GitHub Actions**. Retain the environment's main-branch restriction.
Subsequent merges deploy automatically. The maintainer can also rerun **Offline
verification** on `main` from Actions. Check the deployment job's URL and result
before reporting publication. See GitHub's
[custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

To preview an already verified checkout:

```sh
.venv/bin/python tools/build_web_patcher.py
node --test web/patcher.test.mjs
python3 -m http.server 8000 --bind 127.0.0.1 --directory build/web-patcher
```

Open `http://127.0.0.1:8000`. Web Crypto requires HTTPS or localhost; opening
the HTML directly as a file is unsupported. Node 24 or later runs the tests
without dependencies. A fresh checkout first needs the pinned environment
and full reproduction from [CI](CI.md).

For a firmware update, rebuild and review the sole candidate and its evidence,
commit them together, and update the website's feature/limitation text if
needed. Candidate hashes and patch bytes are generated from that commit.
Do not hand-edit a delta or loosen the original-file guard. A broken deployment
can be corrected by reverting its source change on `main` and letting the
same verified workflow redeploy.

## Public release boundary

The patcher makes the current experiment easier to prepare. A stable public
firmware release still needs the [roadmap's](../ROADMAP.md) physical acceptance:
mastering, snapshots/restart, real stereo/18-channel and mixed alternates,
sustained audio and scoped recovery evidence. This work neither authorizes
a bench operation nor claims those tests passed. Review the project's and
imported material's notices before a wider release; no project-wide license
has been selected.
