"""Contract tests for an on-call data freshness monitor."""
from datetime import datetime, timezone
import importlib.util
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
SUBMISSION = Path(os.environ.get(
    "APPRENTICE_SUBMISSION_PATH",
    str(ROOT / "submissions" / "retail-003" / "monitor.py")
))
NOW = datetime(2026, 11, 21, 9, 0, tzinfo=timezone.utc)
GOOD = {
    "generated_at_utc": "2026-11-21T08:00:00+00:00",
    "latest_order_date": "2026-11-20",
    "quality_passed": True,
}


class MonitorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SUBMISSION.is_file():
            raise AssertionError("Missing retail-003 submission")
        spec = importlib.util.spec_from_file_location("retail003", SUBMISSION)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        cls.module = module

    def test_healthy(self):
        result = self.module.inspect(dict(GOOD), NOW)
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["issues"], [])
        self.assertEqual(result["metrics"], {
            "job_age_minutes": 60.0, "data_age_days": 1
        })

    def test_stale_source_even_when_job_completed(self):
        result = self.module.inspect(
            {**GOOD, "generated_at_utc": NOW.isoformat(),
             "latest_order_date": "2026-11-17"}, NOW
        )
        self.assertEqual(result["status"], "alert")
        self.assertIn("stale_data", result["issues"])
        self.assertNotIn("stale_job", result["issues"])
        self.assertEqual(result["metrics"]["data_age_days"], 4)

    def test_stale_job_even_when_source_fresh(self):
        result = self.module.inspect(
            {**GOOD, "generated_at_utc": "2026-11-21T04:00:00+00:00",
             "latest_order_date": "2026-11-21"}, NOW
        )
        self.assertIn("stale_job", result["issues"])
        self.assertNotIn("stale_data", result["issues"])
        self.assertEqual(result["metrics"]["job_age_minutes"], 300.0)

    def test_broken_manifest_collects_all_errors(self):
        result = self.module.inspect(
            {"quality_passed": "yes"}, NOW)
        self.assertEqual(result["issues"],
                         sorted(["missing_run_timestamp", "missing_source_date",
                                 "quality_not_confirmed"]))
        self.assertEqual(result["metrics"], {})
        self.assertEqual(result["status"], "alert")

    def test_future_times_alert(self):
        result = self.module.inspect(
            {**GOOD, "generated_at_utc": "2026-11-22T10:00:00+00:00",
             "latest_order_date": "2026-11-30"}, NOW)
        self.assertIn("future_run_timestamp", result["issues"])
        self.assertIn("future_source_date", result["issues"])

    def test_bad_timestamp_does_not_crash_monitor(self):
        result = self.module.inspect(
            {**GOOD, "generated_at_utc": "nonsense",
             "latest_order_date": "invalid"}, NOW)
        self.assertIn("invalid_run_timestamp", result["issues"])
        self.assertIn("invalid_source_date", result["issues"])
        self.assertEqual(result["metrics"], {})

    def test_invalid_monitor_parameters_rejected(self):
        for as_of, job, data in [
            (datetime(2026, 11, 21), 120, 1),
            (NOW, -1, 1), (NOW, 120, -1), (NOW, True, 1)
        ]:
            with self.subTest(as_of=as_of, job=job, data=data):
                with self.assertRaisesRegex(ValueError, "invalid_monitor_arguments"):
                    self.module.inspect(GOOD, as_of, job, data)


if __name__ == "__main__":
    unittest.main()
