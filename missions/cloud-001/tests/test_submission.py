"""Public contract checks for CLOUD-001."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
SUBMISSION = Path(os.environ.get("APPRENTICE_SUBMISSION_PATH",
    str(ROOT / "submissions" / "cloud-001" / "client.py")))


class CloudClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SUBMISSION.is_file():
            raise AssertionError("Missing cloud-001 submission. Run apprentice.py start cloud-001.")
        spec = importlib.util.spec_from_file_location("cloud_001_submission", SUBMISSION)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        cls.mod = mod

    def test_success_on_first_attempt(self):
        calls = []
        def get(url):
            calls.append(url)
            return (200, {"ready": True})
        result = self.mod.fetch_report("http://local/test", get, sleep=lambda _: None)
        self.assertEqual(result, {"status": 200, "body": {"ready": True}, "attempts": 1})
        self.assertEqual(calls, ["http://local/test"])

    def test_503_then_success_backoff(self):
        statuses = iter([503, 429, 200])
        sleeps = []
        calls = []
        def get(url):
            calls.append(url)
            return (next(statuses), {"payload": "yes"})
        result = self.mod.fetch_report("service", get, attempts=3, sleep=sleeps.append)
        self.assertEqual(result["attempts"], 3)
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [0.1, 0.2])

    def test_connection_error_retry(self):
        sleeps = []
        state = [0]
        def get(url):
            state[0] += 1
            if state[0] == 1:
                raise ConnectionError("connection refused")
            return (200, {"ok": True})
        result = self.mod.fetch_report("local", get, attempts=2, sleep=sleeps.append)
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(sleeps, [0.1])

    def test_retry_budget_and_no_extra_sleep(self):
        calls, sleeps = [], []
        def get(url):
            calls.append(url)
            return (503, {})
        with self.assertRaisesRegex(RuntimeError, "retry_exhausted"):
            self.mod.fetch_report("svc", get, attempts=3, sleep=sleeps.append)
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [0.1, 0.2])

    def test_non_retryable_error_immediate(self):
        calls = []
        def get(url):
            calls.append(url)
            return (404, {"missing": True})
        with self.assertRaisesRegex(ValueError, "non_retryable_http:404"):
            self.mod.fetch_report("svc", get, sleep=lambda _: None)
        self.assertEqual(len(calls), 1)

    def test_validation(self):
        def get(url):
            raise AssertionError("invalid argument must fail before transport")
        for bad in (0, -1, 6, True, 1.5, "3"):
            with self.subTest(value=bad):
                with self.assertRaisesRegex(ValueError, "invalid_attempts"):
                    self.mod.fetch_report("svc", get, attempts=bad, sleep=lambda _: None)


if __name__ == "__main__":
    unittest.main()
