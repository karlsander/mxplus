#!/usr/bin/env python3
"""Package the verified mainline artifact for a static browser patcher.

This is a distribution exporter, not another firmware builder. It never
compiles, decodes or modifies firmware sources or the maintained candidate.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from check_reproduction import audit
from container_tool import IMAGE_SIZE, ORIGINAL_SHA256

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build/web-patcher"
ASSETS = ("index.html", "style.css", "app.mjs", "patcher.mjs", "favicon.svg")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_patch(original: bytes, candidate: bytes) -> dict:
    if len(original) != IMAGE_SIZE or len(candidate) != IMAGE_SIZE:
        raise ValueError("Unexpected update-container size")
    if sha256(original) != ORIGINAL_SHA256:
        raise ValueError("Original firmware identity changed")
    # Coalesce differences separated by at most 32 unchanged bytes. XOR data
    # requires the visitor's exact original; no complete firmware is published.
    spans = []
    start = end = None
    for offset, (before, after) in enumerate(zip(original, candidate)):
        if before == after:
            continue
        if end is not None and offset - end > 32:
            spans.append((start, end))
            start = None
        if start is None:
            start = offset
        end = offset + 1
    if start is not None:
        spans.append((start, end))
    if not spans:
        raise ValueError("Candidate is identical to stock")
    return {"format": "mxplus-xor-v1", "runs": [
        {"offset": start, "xor": base64.b64encode(bytes(
            a ^ b for a, b in zip(original[start:end], candidate[start:end])
        )).decode("ascii")} for start, end in spans
    ]}


def main() -> None:
    # Includes actual Git artifact blobs and the complete offline evidence gate.
    audit(check_committed=True)
    original = (ROOT / "inputs/MX1_UPD.original.bin").read_bytes()
    candidate = (ROOT / "build/mainline/MXPLUS_MAINLINE_UNTESTED.bin").read_bytes()
    patch = json.dumps(make_patch(original, candidate), separators=(",", ":")).encode()
    patch_hash = sha256(patch)
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    manifest = {
        "format": "mxplus-release-v1",
        "status": "UNTESTED",
        "sourceCommit": commit,
        "input": {"size": len(original), "sha256": ORIGINAL_SHA256},
        "output": {"size": len(candidate), "sha256": sha256(candidate),
                   "filename": "MXPLUS_MAINLINE_UNTESTED.bin"},
        "patch": {"file": f"patch-{patch_hash}.json", "sha256": patch_hash},
    }
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)
    for name in ASSETS:
        shutil.copyfile(ROOT / "web" / name, OUTPUT / name)
    (OUTPUT / manifest["patch"]["file"]).write_bytes(patch)
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (OUTPUT / ".nojekyll").touch()
    print(f"Packaged {manifest['output']['sha256']} at {OUTPUT}")
    print(f"XOR patch: {len(patch):,} bytes; no full firmware in site output")


if __name__ == "__main__":
    main()
