"""Contract tests for local object storage safety and integrity."""
import hashlib
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SUBMISSION = Path(os.environ.get(
    "APPRENTICE_SUBMISSION_PATH",
    str(ROOT / "submissions" / "cloud-002" / "storage.py")
))


class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SUBMISSION.is_file():
            raise AssertionError("Missing cloud-002 submission")
        spec = importlib.util.spec_from_file_location("cloud002", SUBMISSION)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        cls.module = module

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source.csv"
        self.source.write_bytes(b"daily,paid_revenue\n2026-11-20,22000\n")
        self.root = self.base / "store"
        self.key = "reports/2026-11-20.csv"
        self.sha = hashlib.sha256(self.source.read_bytes()).hexdigest()

    def publish(self, source=None, key=None):
        return self.module.publish_artifact(
            source or self.source, self.root, key or self.key
        )

    def test_upload_download_and_exact_metadata(self):
        metadata = self.publish()
        self.assertEqual(metadata, {
            "key": self.key,
            "sha256": self.sha,
            "size_bytes": len(self.source.read_bytes()),
        })
        downloaded = self.module.fetch_artifact(self.root, self.key, self.sha)
        self.assertEqual(downloaded, self.source.read_bytes())

    def test_exact_retry_does_not_modify_file(self):
        first = self.publish()
        path = self.root / self.key
        first_stat = path.stat().st_mtime_ns
        second = self.publish()
        self.assertEqual(first, second)
        self.assertEqual(path.stat().st_mtime_ns, first_stat)

    def test_conflicting_retry_does_not_overwrite(self):
        self.publish()
        changed = self.base / "changed.csv"
        changed.write_bytes(b"different payload")
        with self.assertRaisesRegex(ValueError, "object_conflict"):
            self.publish(changed)
        self.assertEqual((self.root / self.key).read_bytes(),
                         self.source.read_bytes())

    def test_tamper_detected_on_download(self):
        self.publish()
        (self.root / self.key).write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "checksum_mismatch"):
            self.module.fetch_artifact(self.root, self.key, self.sha)

    def test_invalid_keys_rejected_before_writing(self):
        for key in ("", "/tmp/evil", "../outside.txt", "reports/../evil",
                    "folder\\evil", "./record", "reports/a b", "reports//a"):
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, "invalid_object_key"):
                    self.module.publish_artifact(self.source, self.root, key)
        self.assertFalse((self.base / "outside.txt").exists())

    def test_invalid_keys_rejected_on_fetch(self):
        for key in ("", "../evil", "reports/../../oops", "/etc/passwd"):
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, "invalid_object_key"):
                    self.module.fetch_artifact(self.root, key, self.sha)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_escape_is_blocked(self):
        self.root.mkdir()
        outside = self.base / "outside"
        outside.mkdir()
        try:
            (self.root / "out").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks require privileges on this system")
        with self.assertRaisesRegex(ValueError, "invalid_object_key"):
            self.module.publish_artifact(self.source, self.root, "out/escape.csv")


if __name__ == "__main__":
    unittest.main()
