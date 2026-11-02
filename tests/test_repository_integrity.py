"""Artifact identity and bundle-selection regressions using temporary fixtures.

No real firmware evidence, Git index, commits or network state is modified.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK = load_tool("check_reproduction")
BUNDLE = load_tool("make_bundle")


def sha(data):
    return hashlib.sha256(data).hexdigest()


class ReproductionIdentityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        original = b"independent test firmware fixture"
        self.original_sha = sha(original)
        self.write("inputs/MX1_UPD.original.bin", original)
        self.reproduction = {
            "status": "passed", "hardware_access": False,
            "input_sha256": self.original_sha,
            "checks": [{"name": name, "passed": True} for name in CHECK.EXPECTED_STAGES],
            "candidate_sha256": {},
        }
        for name in ("container_verification", "container_updater_verification",
                     "container_binding_verification"):
            self.write_json("analysis/" + name + ".json",
                            {"status": "passed", "input_sha256": self.original_sha})
        for kind, names in CHECK.ARTIFACTS.items():
            prefix = "build/" + kind + "/"
            extension = (kind + " extension").encode()
            application = b"prefix" + extension + b"tail"
            contents = {"container_sha256": (kind + " candidate").encode(),
                        "patched_app_sha256": application, "extension_sha256": extension}
            hashes = {key: sha(data) for key, data in contents.items()}
            for key, data in contents.items():
                self.write(prefix + names[key], data)
            self.write_json(prefix + "build-report.json", {
                "input_sha256": self.original_sha,
                "status": "OFFLINE EXPERIMENT; NOT HARDWARE VALIDATED",
                "scatter_extension": {"insert_offset": 6, "insert_length": len(extension)},
                **hashes,
            })
            self.write_json(prefix + "storage-verification.json", {
                "status": "pass", "patched_app_sha256": hashes["patched_app_sha256"]})
            self.write_json(prefix + "boot-verification.json", {
                "status": "pass", "candidate_sha256": hashes["container_sha256"]})
            for generator in ('core', 'audio', 'ui'):
                self.write_json(prefix + 'generator-' + generator + '-verification.json', {
                    'status': 'pass', 'patched_app_sha256': hashes['patched_app_sha256']})
            self.write_json(prefix + 'generator-dsp-verification.json', {'status': 'passed'})
            self.write_json(prefix + 'generator-exchange-audit.json', {'status': 'pass'})
            self.reproduction["candidate_sha256"][kind] = hashes["container_sha256"]
            self.write_json("analysis/container_" + kind + "_candidate_verification.json", {
                "status": "passed", "original_sha256": self.original_sha,
                "candidate_sha256": hashes["container_sha256"],
                "hardware_flash_or_audio_functionality_verified": False,
                "changed_decoded_components": [{
                    "component": "app_usb" if kind == "host" else "app_main",
                    "candidate_decoded_sha256": hashes["patched_app_sha256"],
                    "original_decoder_matches": True,
                }],
            })
            self.write_json("analysis/host_probe_verification.json" if kind == "host"
                            else prefix + "arm-verification.json", {
                                "status": "pass",
                                "patched_app_sha256": hashes["patched_app_sha256"],
                            })
        self.write_json("analysis/reproduction.json", self.reproduction)
        self.head = {p.relative_to(self.root).as_posix(): p.read_bytes()
                     for p in self.root.rglob("*") if p.is_file()}
        self.patch_root = mock.patch.object(CHECK, "ROOT", self.root)
        self.patch_identity = mock.patch.object(CHECK, "ORIGINAL_SHA256", self.original_sha)
        self.patch_root.start()
        self.patch_identity.start()
        self.addCleanup(self.patch_root.stop)
        self.addCleanup(self.patch_identity.stop)

    def write(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def write_json(self, relative, data):
        self.write(relative, json.dumps(data).encode())

    def edit_json(self, relative, change):
        value = json.loads((self.root / relative).read_text())
        change(value)
        self.write_json(relative, value)

    def git_read(self, command, *, cwd):
        self.assertEqual(command[:2], ["git", "show"])
        self.assertEqual(cwd, self.root)
        self.assertTrue(command[2].startswith("HEAD:"))
        return self.head[command[2][5:]]

    def test_matching_working_artifacts_and_committed_bytes_pass(self):
        with mock.patch.object(CHECK.subprocess, "check_output", side_effect=self.git_read) as git:
            self.assertEqual(CHECK.audit(True)["status"], "passed")
        requested = {call.args[0][2] for call in git.call_args_list}
        for kind, names in CHECK.ARTIFACTS.items():
            for name in names.values():
                self.assertIn("HEAD:build/" + kind + "/" + name, requested)

    def test_stale_committed_binary_is_rejected_even_when_reports_match_rebuild(self):
        for kind, names in CHECK.ARTIFACTS.items():
            for filename in names.values():
                path = "build/" + kind + "/" + filename
                with self.subTest(path=path), mock.patch.dict(self.head, {path: b"stale published bytes"}), \
                        mock.patch.object(CHECK.subprocess, "check_output", side_effect=self.git_read):
                    with self.assertRaisesRegex(ValueError, "committed artifact/report mismatch"):
                        CHECK.audit(True)

    def test_committed_report_mismatch_is_rejected(self):
        path = "build/mainline/build-report.json"
        stale = json.loads(self.head[path])
        stale["container_sha256"] = "0" * 64
        with mock.patch.dict(self.head, {path: json.dumps(stale).encode()}), \
                mock.patch.object(CHECK.subprocess, "check_output", side_effect=self.git_read):
            with self.assertRaisesRegex(ValueError, "committed artifact/report mismatch"):
                CHECK.audit(True)

    def test_committed_original_must_match_the_supported_input(self):
        with mock.patch.dict(self.head, {"inputs/MX1_UPD.original.bin": b"wrong original"}), \
                mock.patch.object(CHECK.subprocess, "check_output", side_effect=self.git_read):
            with self.assertRaisesRegex(ValueError, "Committed original firmware identity changed"):
                CHECK.audit(True)

    def test_current_report_mismatch_is_rejected(self):
        self.edit_json("build/mainline/build-report.json",
                       lambda r: r.update(extension_sha256="0" * 64))
        with self.assertRaisesRegex(ValueError, "artifact/report mismatch"):
            CHECK.audit()

    def test_candidate_decoder_evidence_must_identify_the_actual_application(self):
        self.edit_json("analysis/container_mainline_candidate_verification.json",
                       lambda r: r["changed_decoded_components"][0].update(
                           candidate_decoded_sha256="0" * 64))
        with self.assertRaisesRegex(ValueError, "decoded candidate evidence"):
            CHECK.audit()

    def test_extension_hash_alone_does_not_establish_embedding(self):
        replacement = b"unrelated compiled extension"
        self.write("build/mainline/mainline.load.bin", replacement)
        def change(report):
            report["extension_sha256"] = sha(replacement)
            report["scatter_extension"]["insert_length"] = len(replacement)
        self.edit_json("build/mainline/build-report.json", change)
        with self.assertRaisesRegex(ValueError, "not embedded"):
            CHECK.audit()

    def test_retired_parallel_build_is_rejected(self):
        self.write("tools/build_host_probe.py", b"retired builder")
        with self.assertRaisesRegex(ValueError, "Retired parallel build"):
            CHECK.audit()

    def test_generator_report_from_another_candidate_is_rejected(self):
        for name in ('core', 'audio', 'ui'):
            path = 'build/mainline/generator-' + name + '-verification.json'
            before = (self.root / path).read_bytes()
            self.edit_json(path, lambda r: r.update(patched_app_sha256='0' * 64))
            with self.assertRaisesRegex(ValueError, 'Generator .* evidence failed'):
                CHECK.audit()
            self.write(path, before)

    def test_boot_report_from_another_candidate_is_rejected(self):
        self.edit_json("build/mainline/boot-verification.json",
                       lambda r: r.update(candidate_sha256="0" * 64))
        with self.assertRaisesRegex(ValueError, "boot evidence"):
            CHECK.audit()

    def test_incomplete_reproduction_is_rejected(self):
        self.reproduction["checks"].pop()
        self.write_json("analysis/reproduction.json", self.reproduction)
        with self.assertRaisesRegex(ValueError,
                                    f"complete ordered {len(CHECK.EXPECTED_STAGES)}-stage"):
            CHECK.audit()

    def test_storage_report_must_match_candidate(self):
        self.edit_json("build/mainline/storage-verification.json",
                       lambda report: report.update(patched_app_sha256="0" * 64))
        with self.assertRaisesRegex(ValueError, "storage evidence"):
            CHECK.audit()

    def test_current_evidence_mode_does_not_read_git(self):
        with mock.patch.object(CHECK.subprocess, "check_output") as git:
            self.assertEqual(CHECK.audit()["status"], "passed")
            git.assert_not_called()


class BundleAllowlistTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.report = self.root / "MX1_Research_Report.html"
        self.report.write_text("generated report")
        self.patch_root = mock.patch.object(BUNDLE, "ROOT", self.root)
        self.patch_root.start()
        self.addCleanup(self.patch_root.stop)

    def manifest(self, names):
        (self.root / "ARCHIVE_MANIFEST.json").write_text(json.dumps({
            "format": 1, "files": [{"path": name} for name in names],
        }))

    def test_source_archive_allowlist_excludes_unlisted_local_files(self):
        (self.root / "README.md").write_text("reviewed source")
        (self.root / ".env").write_text("synthetic local configuration")
        historical = self.root / "evidence/baseline-2026-11-01/SHA256SUMS"
        historical.parent.mkdir(parents=True)
        historical.write_text("historical evidence")
        self.manifest(["README.md", historical.relative_to(self.root).as_posix()])
        self.assertEqual(set(BUNDLE.bundle_inputs(self.report)),
                         {self.root / "README.md", historical, self.report})

    def test_source_archive_without_manifest_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "refusing to scan unreviewed files"):
            BUNDLE.bundle_inputs(self.report)

    def test_manifest_cannot_escape_project(self):
        for name in ("../outside", "/tmp/outside", "dir/../../outside", "C:/outside"):
            with self.subTest(path=name):
                self.manifest([name])
                with self.assertRaises(ValueError):
                    BUNDLE.bundle_inputs(self.report)

    def test_symlink_dereference_is_rejected(self):
        secret = self.root / ".env"
        secret.write_text("synthetic local configuration")
        (self.root / "reviewed-link.txt").symlink_to(secret)
        self.manifest(["reviewed-link.txt"])
        with self.assertRaisesRegex(ValueError, "symlink"):
            BUNDLE.bundle_inputs(self.report)

    def test_git_input_list_retains_historical_manifests(self):
        (self.root / ".git").mkdir()
        historical = self.root / "evidence/baseline-2026-11-01/ARCHIVE_MANIFEST.json"
        historical.parent.mkdir(parents=True)
        historical.write_text("historical evidence")
        (self.root / ".env").write_text("synthetic local configuration")
        tracked = (historical.relative_to(self.root).as_posix() + "\0ARCHIVE_MANIFEST.json\0").encode()
        with mock.patch.object(BUNDLE.subprocess, "check_output", return_value=tracked):
            self.assertEqual(set(BUNDLE.bundle_inputs(self.report)), {historical, self.report})


if __name__ == "__main__":
    unittest.main()
