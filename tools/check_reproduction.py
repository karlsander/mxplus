#!/usr/bin/env python3
"""Audit offline evidence and rebuilt bytes, optionally against Git HEAD.

Run tools/reproduce.py first. --check-committed detects source changes that
produce firmware different from the candidate recorded in the current commit.
It checks the committed artifact bytes as well as the committed report hashes.
It intentionally ignores timing, local paths and ELF/debug metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from container_tool import ORIGINAL_SHA256

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_STAGES = (
    "map-main", "map-usb", "map-updater", "container_verify",
    "container_updater_verify", "container_binding_verify",
    "usb-descriptor-scan", "descriptor-tests", "bridge-plan-tests",
    "build-mainline", "arm-mainline", "container-mainline-candidate", "boot-mainline", "original-audio-pump",
    "compile-native-controls", "native-controls", "subcpu-evidence",
)
ARTIFACTS = {
    "mainline": {
        "container_sha256": "MXPLUS_MAINLINE_UNTESTED.bin",
        "patched_app_sha256": "app_main.mainline.bin",
        "extension_sha256": "mainline.load.bin",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text())


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def committed_bytes(relative: str) -> bytes:
    return subprocess.check_output(["git", "show", "HEAD:" + relative], cwd=ROOT)


def audit(check_committed: bool = False) -> dict:
    require(digest("inputs/MX1_UPD.original.bin") == ORIGINAL_SHA256,
            "Original firmware identity changed")
    if check_committed:
        require(hashlib.sha256(committed_bytes("inputs/MX1_UPD.original.bin")).hexdigest()
                == ORIGINAL_SHA256, "Committed original firmware identity changed")
    for retired in ("build/host-probe/MX1_UAC1_HOST_PROBE_UNTESTED.bin",
                    "build/device-probe/MX1_UAC2_DEVICE_PROBE_UNTESTED.bin",
                    "build/routing-probe/MX1_CHANNEL_ROUTING_UNTESTED.bin",
                    "build/display-marker/MX1_DISPLAY_MARKER_UNTESTED.bin",
                    "tools/build_host_probe.py", "tools/build_device_probe.py", "tools/build_routing_probe.py"):
        require(not (ROOT / retired).exists(), "Retired parallel build remains: " + retired)
    reproduction = read("analysis/reproduction.json")
    require(reproduction.get("status") == "passed", "Reproduction did not pass")
    require(reproduction.get("hardware_access") is False, "Unexpected hardware-access claim")
    require(reproduction.get("input_sha256") == ORIGINAL_SHA256, "Reproduction input mismatch")
    checks = reproduction.get("checks", [])
    require(tuple(c.get("name") for c in checks) == EXPECTED_STAGES,
            f"Expected the complete ordered {len(EXPECTED_STAGES)}-stage reproduction run")
    require(all(c.get("passed") is True for c in checks), "A reproduction stage failed")

    for relative in ("analysis/container_verification.json",
                     "analysis/container_updater_verification.json",
                     "analysis/container_binding_verification.json"):
        result = read(relative)
        require(result.get("status") == "passed", relative + " did not pass")
        require(result.get("input_sha256") == ORIGINAL_SHA256, relative + " has wrong input")

    hashes = {}
    for kind, names in ARTIFACTS.items():
        prefix = "build/" + kind + "/"
        report_path = prefix + "build-report.json"
        report = read(report_path)
        require(report.get("input_sha256") == ORIGINAL_SHA256, kind + " build input mismatch")
        require(report.get("status") == "OFFLINE EXPERIMENT; NOT HARDWARE VALIDATED",
                kind + " build lost the experimental status")
        actual = {key: digest(prefix + filename) for key, filename in names.items()}
        for key, value in actual.items():
            require(report.get(key) == value, kind + " artifact/report mismatch: " + key)
        require(reproduction["candidate_sha256"].get(kind) == actual["container_sha256"],
                kind + " reproduction/candidate mismatch")
        candidate = read("analysis/container_" + kind + "_candidate_verification.json")
        require(candidate.get("status") == "passed", kind + " decoder/updater check failed")
        require(candidate.get("original_sha256") == ORIGINAL_SHA256,
                kind + " updater input mismatch")
        require(candidate.get("candidate_sha256") == actual["container_sha256"],
                kind + " updater report belongs to another candidate")
        require(candidate.get("hardware_flash_or_audio_functionality_verified") is False,
                kind + " updater report has an unexpected hardware claim")
        decoded = candidate.get("changed_decoded_components", [])
        require(len(decoded) == 1 and
                decoded[0].get("component") == "app_main",
                kind + " updater report must identify only the intended changed application")
        require(decoded[0].get("candidate_decoded_sha256") == actual["patched_app_sha256"] and
                decoded[0].get("original_decoder_matches") is True,
                kind + " decoded candidate evidence does not match the application artifact")
        application = (ROOT / prefix / names["patched_app_sha256"]).read_bytes()
        extension = (ROOT / prefix / names["extension_sha256"]).read_bytes()
        scatter = report.get("scatter_extension", {})
        offset = scatter.get("insert_offset")
        require(type(offset) is int and offset >= 0 and len(extension) > 0 and
                scatter.get("insert_length") == len(extension),
                kind + " extension placement metadata is invalid")
        require(application[offset:offset + len(extension)] == extension,
                kind + " extension artifact is not embedded at the recorded application offset")
        arm = read(prefix + "arm-verification.json")
        require(arm.get("status") == "pass", kind + " ARM integration check failed")
        require(arm.get("patched_app_sha256") == actual["patched_app_sha256"],
                kind + " ARM report belongs to another application")
        boot = read(prefix + "boot-verification.json")
        require(boot.get("status") == "pass" and boot.get("candidate_sha256") == actual["container_sha256"],
                "Mainline boot evidence missing or belongs to another candidate")
        if check_committed:
            committed = json.loads(committed_bytes(report_path))
            for key, value in actual.items():
                artifact_path = prefix + names[key]
                committed_digest = hashlib.sha256(committed_bytes(artifact_path)).hexdigest()
                require(committed.get(key) == committed_digest,
                        kind + " committed artifact/report mismatch: " + artifact_path)
                require(committed_digest == value,
                        kind + " rebuilt " + key + " differs from Git HEAD; "
                        "rebuild, review and commit the matching candidate/evidence for an intentional change")
        hashes[kind] = actual
    return {"status": "passed", "stage_count": len(checks),
            "original_sha256": ORIGINAL_SHA256, "checked_against_git_head": check_committed,
            "hardware_validation": False, "candidate_artifacts": hashes}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-committed", action="store_true")
    args = parser.parse_args()
    try:
        result = audit(args.check_committed)
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, "Artifact verification failed: " + str(exc) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
