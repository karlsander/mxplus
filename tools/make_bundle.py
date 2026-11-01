#!/usr/bin/env python3
"""Build the self-contained research report and archive without external packages.

The small renderer supports the deliberately limited Markdown used by this
project's report: headings, paragraphs, flat lists, tables, links and code.
It is not intended as a general Markdown implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]


def inline(text: str) -> str:
    saved: list[str] = []

    def protect(value: str) -> str:
        saved.append(value)
        return f"\x00{len(saved)-1}\x00"

    text = re.sub(r"`([^`]+)`", lambda m: protect("<code>" + html.escape(m[1]) + "</code>"), text)
    text = re.sub(r"\[([^\]]+)\]\((https://[^\s)]+)\)",
                  lambda m: protect('<a href="' + html.escape(m[2], quote=True) + '">' +
                                    html.escape(m[1]) + "</a>"), text)
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: saved[int(m[1])], text)


def render_markdown(markdown: str) -> str:
    lines = markdown.splitlines()
    blocks: list[str] = []
    headings: list[tuple[str, str]] = []
    section = "Report"
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            code: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            blocks.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
            i += 1
            continue
        h = re.match(r"^(#{1,6}) (.+)$", line)
        if h:
            level = len(h[1])
            label = h[2]
            ident = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
            blocks.append(f'<h{level} id="{ident}">{inline(label)}</h{level}>')
            if level == 2:
                headings.append((ident, label))
                section = label
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c.replace(" ", "")) for c in cells):
                    rows.append(cells)
                i += 1
            table = ['<div class="table-wrap"><table><caption class="sr-only">' +
                     html.escape(section) + "</caption><thead><tr>"]
            table.extend('<th scope="col">' + inline(c) + "</th>" for c in rows[0])
            table.append("</tr></thead><tbody>")
            for row in rows[1:]:
                table.append("<tr>" + "".join("<td>" + inline(c) + "</td>" for c in row) + "</tr>")
            table.append("</tbody></table></div>")
            blocks.append("".join(table))
            continue
        match = re.match(r"^(- |\d+\. )(.+)$", line)
        if match:
            ordered = not line.startswith("- ")
            kind = "ol" if ordered else "ul"
            items = []
            while i < len(lines):
                m = re.match(r"^(- |\d+\. )(.+)$", lines[i])
                if not m or (not lines[i].startswith("- ")) != ordered:
                    break
                items.append("<li>" + inline(m[2]) + "</li>")
                i += 1
            blocks.append(f"<{kind}>" + "".join(items) + f"</{kind}>")
            continue
        paragraph = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||```|- |\d+\. )", lines[i]):
            paragraph.append(lines[i])
            i += 1
        blocks.append("<p>" + inline(" ".join(paragraph)) + "</p>")
    nav = '<nav aria-label="Contents"><h2>Contents</h2><ol>' + "".join(
        f'<li><a href="#{ident}">{html.escape(label)}</a></li>' for ident, label in headings) + "</ol></nav>"
    return blocks[0] + nav + "\n".join(blocks[1:])


STYLE = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { margin: 0; color: #18222d; background: #f4f6f8;
       font-family: system-ui, -apple-system, 'Segoe UI', sans-serif; line-height: 1.65; }
main { max-width: 1060px; margin: 0 auto; padding: 44px 50px 64px; background: white; }
h1 { font-size: 2.1rem; line-height: 1.2; letter-spacing: -.025em; margin: 0 0 24px; }
h2 { font-size: 1.5rem; line-height: 1.35; margin-top: 42px; border-top: 1px solid #d4dce3; padding-top: 24px; }
h3 { font-size: 1.15rem; margin-top: 26px; }
p, li { max-width: 88ch; }
li { margin-bottom: 9px; }
a { color: #095b96; text-underline-offset: .15em; }
a:focus { outline: 3px solid #d87809; outline-offset: 3px; }
nav { background: #eef4f8; padding: 16px 24px; margin: 24px 0; border-left: 4px solid #245d80; }
nav h2 { border: 0; padding: 0; margin: 0 0 10px; font-size: 1.1rem; }
nav ol { list-style: none; padding: 0; margin: 0; }
nav li { margin: 4px 0; }
code { font-family: ui-monospace, Consolas, monospace; font-size: .9em; overflow-wrap: anywhere; }
pre { background: #edf1f4; padding: 14px 18px; border-radius: 4px; white-space: pre-wrap; overflow-wrap: anywhere; }
.table-wrap { margin: 20px 0; }
table { border-collapse: collapse; width: 100%; font-size: .91rem; }
th, td { padding: 11px 12px; border: 1px solid #cbd5de; vertical-align: top; text-align: left; }
th { background: #e8eff4; font-weight: 650; }
tbody tr:nth-child(even) { background: #f7f9fa; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
           overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
.skip { position: absolute; left: -9999px; }
.skip:focus { position: static; display: block; padding: 10px; }
@media(max-width: 720px) { main { padding: 25px 18px 40px; } h1 { font-size: 1.7rem; }
  th,td { padding: 7px; } table { font-size: .82rem; } }
@media print { body { background: white; } main { padding: 0; max-width: none; }
  nav { display: none; } h2,h3 { break-after: avoid; } tr,pre { break-inside: avoid; }
  a { color: inherit; } }
"""


def included(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(p in {"__pycache__", "compiler-cache", "ghidra-project", "ghidra-projects", ".venv", ".git"} for p in rel.parts):
        return False
    if rel.parts[:2] == ("build", "extracted"):
        return False
    if path.name == "uac2_adapter_native_test" or path.suffix == ".pyc":
        return False
    return path.is_file()


def bundle_inputs(report: Path) -> list[Path]:
    """Select reviewed paths, never an arbitrary scan of a working directory.

    A Git checkout supplies its tracked file list. A previously exported source
    archive supplies its existing root manifest as a path allowlist; its old
    hashes describe that export, while this run records current file hashes.
    """
    if (ROOT / ".git").exists():
        tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        names = [p.decode() for p in tracked.split(b"\0") if p]
    else:
        manifest_path = ROOT / "ARCHIVE_MANIFEST.json"
        if not manifest_path.is_file():
            raise ValueError("Packaging requires a Git checkout or an existing root "
                             "ARCHIVE_MANIFEST.json; refusing to scan unreviewed files")
        manifest = json.loads(manifest_path.read_text())
        if (not isinstance(manifest, dict) or manifest.get("format") != 1 or
                not isinstance(manifest.get("files"), list) or not manifest["files"]):
            raise ValueError("Invalid source archive manifest")
        names = [entry.get("path") if isinstance(entry, dict) else None
                 for entry in manifest["files"]]
    names.append(report.relative_to(ROOT).as_posix())
    generated_manifests = {"SHA256SUMS", "ARCHIVE_MANIFEST.json"}
    paths = set()
    for name in names:
        if (not isinstance(name, str) or not name or
                any(c in name for c in ("\\", ":", "\0", "\r", "\n"))):
            raise ValueError("Invalid archive input path")
        relative = PurePosixPath(name)
        if (relative.is_absolute() or ".." in relative.parts or
                relative.as_posix() != name):
            raise ValueError("Archive input must be a normalized project-relative path: " + name)
        if name in generated_manifests:
            continue
        path = ROOT / relative
        if any(ROOT.joinpath(*relative.parts[:i]).is_symlink()
               for i in range(1, len(relative.parts) + 1)):
            raise ValueError("Archive input is a symlink or traverses one: " + name)
        if not path.is_file():
            raise ValueError("Listed archive input is missing or not a regular file: " + name)
        if included(path):
            paths.add(path)
    return sorted(paths)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT.parent / "deliverables")
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    from check_reproduction import audit
    audit()  # Check the current candidate, application, extension and evidence together.
    report = ROOT / "MX1_Research_Report.html"
    source = (ROOT / "docs/RESEARCH_REPORT.md").read_text()
    body = render_markdown(source)
    report.write_text('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Roland MX-1 Firmware and USB Research — 1 November 2026</title>'
        '<meta name="description" content="Firmware reconstruction, compiled USB experiments, evidence and hardware validation limits.">'
        '<style>' + STYLE + '</style></head><body><a class="skip" href="#report">Skip to report</a>'
        '<main id="report">' + body + '</main></body></html>\n')
    shutil.copyfile(report, out / report.name)
    paths = bundle_inputs(report)
    manifest = [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size,
                 "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
    (ROOT / "ARCHIVE_MANIFEST.json").write_text(json.dumps({"format": 1, "files": manifest,
        "hardware_validation": False, "reproduction_status": "passed"}, indent=2) + "\n")
    (ROOT / "SHA256SUMS").write_text("".join(r["sha256"] + "  " + r["path"] + "\n" for r in manifest))
    paths.extend([ROOT / "ARCHIVE_MANIFEST.json", ROOT / "SHA256SUMS"])
    archive = out / "Roland_MX1_Research_2026-11-01.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as z:
        for path in paths:
            z.write(path, str(Path("mx1-research") / path.relative_to(ROOT)))
    with ZipFile(archive) as z:
        bad = z.testzip()
        if bad:
            raise SystemExit("Archive CRC failure: " + bad)
    print(json.dumps({"archive": str(archive), "archive_bytes": archive.stat().st_size,
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "included_files": len(paths),
        "report": str(out / report.name), "report_words": len(source.split())}, indent=2))


if __name__ == "__main__":
    main()
