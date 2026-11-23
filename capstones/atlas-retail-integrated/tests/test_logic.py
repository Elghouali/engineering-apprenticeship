"""Cross-platform, dependency-free business-contract tests for integrated lab."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from logic import canonical, daily_report, fingerprint, validate_event


def events():
    return json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))


class TestIntegratedContracts(unittest.TestCase):
    def test_fixture_has_replay_and_exact_22000_cents(self):
        fixture = events()
        self.assertEqual(len(fixture), 7)
        report = daily_report(fixture, "2026-11-20")
        self.assertEqual(report, {
            "business_date": "2026-11-20", "accepted_events": 5,
            "paid_events": 4, "paid_revenue_cents": 22000,
            "merchants": [
                {"merchant_id": "merchant-a", "paid_revenue_cents": 12000},
                {"merchant_id": "merchant-b", "paid_revenue_cents": 7500},
                {"merchant_id": "merchant-c", "paid_revenue_cents": 2500}
            ]
        })

    def test_ordering_and_replay_do_not_affect_report(self):
        original = events()
        self.assertEqual(
            canonical(daily_report(original, "2026-11-20")),
            canonical(daily_report(list(reversed(original)) + original,
                                   "2026-11-20"))
        )

    def test_fingerprint_is_deterministic(self):
        e = events()[0]
        other = dict(reversed(list(e.items())))
        self.assertEqual(fingerprint(e), fingerprint(other))
        self.assertRegex(fingerprint(e), r"^[a-f0-9]{64}$")

    def test_invalid_events_rejected(self):
        base = events()[0]
        cases = [
            {**base, "amount_cents": 3.5},
            {**base, "amount_cents": True},
            {**base, "amount_cents": 0},
            {**base, "event_id": ""},
            {**base, "business_date": "2026-11-40"},
            {**base, "status": "refunded"},
            {**base, "unknown_field": 1},
        ]
        for case in cases:
            with self.subTest(case=case):
                with self.assertRaisesRegex(ValueError, "invalid_event"):
                    validate_event(case)

    def test_conflicting_duplicate_is_fatal(self):
        fixture = events()
        fixture.append({**fixture[0], "amount_cents": 123})
        with self.assertRaisesRegex(ValueError, "conflicting_event"):
            daily_report(fixture, "2026-11-20")

    def test_earlier_date_returns_empty_valid_report(self):
        report = daily_report(events(), "2026-11-19")
        self.assertEqual(report["paid_revenue_cents"], 0)
        self.assertEqual(report["accepted_events"], 0)
        self.assertEqual(report["merchants"], [])

    def test_bad_business_date(self):
        for raw in ("2026-13-01", "Nov 20", None, 20261120):
            with self.subTest(raw=raw):
                with self.assertRaisesRegex(ValueError, "invalid_business_date"):
                    daily_report(events(), raw)


if __name__ == "__main__":
    unittest.main()
