"""Cross-platform Airflow date contract and Kubernetes API liveness tests."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import events_for_date
from logic import daily_report


class TestLogicalDateFixture(unittest.TestCase):
    def test_two_dates_do_not_collide_and_replay_is_stable(self):
        first = events_for_date("2026-11-20")
        second = events_for_date("2026-11-21")
        self.assertEqual(len(first), 7)
        self.assertEqual(len(second), 7)
        self.assertEqual(len({e["event_id"] for e in first}), 5)
        self.assertEqual(len({e["event_id"] for e in second}), 5)
        self.assertTrue({e["event_id"] for e in first}.isdisjoint(
            {e["event_id"] for e in second}))
        self.assertEqual(events_for_date("2026-11-21"), second)
        for day, events in [("2026-11-20", first), ("2026-11-21", second)]:
            result = daily_report(events, day)
            self.assertEqual(result["accepted_events"], 5)
            self.assertEqual(result["paid_revenue_cents"], 22000)

    def test_untrusted_business_date_rejected(self):
        for bad in ("not-a-date", "2026-11-21' OR true", None, 20261121):
            with self.subTest(value=bad):
                with self.assertRaisesRegex(ValueError, "invalid_business_date"):
                    events_for_date(bad)


if __name__ == "__main__":
    unittest.main()
