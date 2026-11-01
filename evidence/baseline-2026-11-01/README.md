# Frozen research snapshot

`ARCHIVE_MANIFEST.json` and `SHA256SUMS` describe the complete research package
delivered on 1 November 2026, before repository setup. The preserved
`research-baseline-2026-11-01` branch identifies that exact content snapshot.
Paths inside these manifests are relative to that snapshot's project root,
not this evidence directory or the current `main` branch. Their two original
manifest files are intentionally not listed in their own digests.

These manifests are historical evidence. Do not rewrite them when README,
tools or future experiments change. For current work, run:

```bash
python tools/reproduce.py
python tools/check_reproduction.py --check-committed
```

The second command checks the original input, current binary/evidence
consistency and candidate/application/extension hashes against Git `HEAD`.
It excludes volatile timing, absolute build paths and ELF debug metadata.

`tools/make_bundle.py` writes fresh root-level manifests when creating a new
archive. Those generated manifests are ignored by Git. In a Git checkout,
the bundler includes tracked research files and the regenerated HTML report;
commit or deliberately stage a new deliverable before asking it to package
that deliverable. Local untracked files and credentials are not swept into
the bundle. In an exported source archive without Git, the existing root
archive manifest supplies the input allowlist. Missing manifests, escaping
paths and symlink dereferences are rejected instead of scanning arbitrary
local files.

Neither these digests nor the offline tests establish physical flashing,
recovery, enumeration or audio operation.
