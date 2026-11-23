"""Capstone integration tests: real CSV -> SQLite -> reports -> verified release."""
from __future__ import annotations

import csv
from contextlib import closing
from datetime import date
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("atlas_platform", ROOT / "platform.py")
platform = importlib.util.module_from_spec(spec)
spec.loader.exec_module(platform)
FIXTURE = ROOT / "data" / "orders.csv"


class DataProductTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / "out"

    def test_end_to_end_real_sqlite_and_manifest(self):
        data = platform.build(FIXTURE, self.out)
        self.assertEqual(data["input_rows"], 8)
        self.assertEqual(data["accepted_orders"], 4)
        self.assertEqual(data["duplicate_rows"], 1)
        self.assertEqual(data["rejected_rows"], 3)
        self.assertEqual(data["paid_revenue_cents"], 22000)
        self.assertEqual(data["gold_rows"], 1)
        self.assertTrue(data["quality_passed"])
        self.assertEqual(platform.verify(self.out), data)

        path = self.out / "releases" / data["release_id"]
        with closing(sqlite3.connect(path / "orders.db")) as db:
            orders = db.execute("SELECT order_id FROM orders ORDER BY order_id").fetchall()
            self.assertEqual(orders, [("1001",), ("1002",), ("1003",), ("1005",)])
        with (path / "gold.csv").open(newline="", encoding="utf-8") as handle:
            values = list(csv.DictReader(handle))
        self.assertEqual(values, [{
            "order_date": "2026-11-20", "paid_orders": "3",
            "paid_revenue_cents": "22000"
        }])
        with (path / "rejections.csv").open(newline="", encoding="utf-8") as handle:
            rejects = list(csv.DictReader(handle))
        self.assertEqual(
            [x["reason"] for x in rejects],
            ["invalid_quantity", "conflicting_order_id", "missing_customer"]
        )

    def test_source_replay_is_idempotent(self):
        first = platform.build(FIXTURE, self.out)
        pointer = (self.out / "current.json").read_text()
        second = platform.build(FIXTURE, self.out)
        self.assertEqual(first, second)
        self.assertEqual(pointer, (self.out / "current.json").read_text())
        self.assertEqual(len(list((self.out / "releases").iterdir())), 1)

    def test_failed_quality_gate_preserves_published_release(self):
        before = platform.build(FIXTURE, self.out)
        pointer = (self.out / "current.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "quality_gate_failed"):
            platform.build(FIXTURE, self.out, max_reject_ratio=.10)
        self.assertEqual(pointer, (self.out / "current.json").read_bytes())
        self.assertEqual(platform.verify(self.out), before)

    def test_tampered_release_is_rejected(self):
        data = platform.build(FIXTURE, self.out)
        gold = self.out / "releases" / data["release_id"] / "gold.csv"
        gold.write_text("malicious replacement", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "artifact_checksum_mismatch"):
            platform.verify(self.out)
        with self.assertRaisesRegex(ValueError, "existing_release_corrupted"):
            platform.build(FIXTURE, self.out)

    def test_tampered_pointer_rejected(self):
        platform.build(FIXTURE, self.out)
        (self.out / "current.json").write_text(
            json.dumps({"release_id": "../invalid", "manifest_sha256": "x"}))
        with self.assertRaisesRegex(ValueError, "unsafe_release_id"):
            platform.verify(self.out)

    def test_freshness_is_independent_of_successful_job(self):
        platform.build(FIXTURE, self.out)
        fresh = platform.status(self.out, date(2026, 11, 21))
        stale = platform.status(self.out, date(2026, 11, 27))
        self.assertEqual(fresh["status"], "healthy")
        self.assertEqual(fresh["data_age_days"], 1)
        self.assertEqual(stale["status"], "stale")
        self.assertEqual(stale["data_age_days"], 7)

    def test_schema_drift_does_not_publish(self):
        copy = Path(self.temp.name) / "invalid.csv"
        copy.write_text("order_id,amount\n1001,20\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "source_schema_mismatch"):
            platform.build(copy, self.out)
        self.assertFalse((self.out / "current.json").exists())

    def test_conflict_and_invalid_row(self):
        data = Path(self.temp.name) / "mini.csv"
        data.write_text(
            "order_id,customer_id,order_date,quantity,unit_price,status\n"
            "A,,2026-11-20,1,1.00,paid\n"
            "A,C1,2026-11-20,1,1.00,paid\n"
            "A,C1,2026-11-20,1,1.00,paid\n"
            "A,C1,2026-11-20,1,2.00,paid\n"
        )
        accepted, rejected, metrics = platform.collect(data)
        self.assertEqual([a["order_id"] for a in accepted], ["A"])
        self.assertEqual(metrics, {
            "input_rows": 4, "accepted_orders": 1,
            "duplicate_rows": 1, "rejected_rows": 2
        })
        self.assertEqual([r["reason"] for r in rejected],
                         ["missing_customer", "conflicting_order_id"])

    def test_reject_nan_and_invalid_dates(self):
        for value in ["NaN", "Infinity", "1.999", "-2", "xyz"]:
            row = {
                "order_id": "X", "customer_id": "C", "order_date": "2026-11-20",
                "quantity": "1", "unit_price": value, "status": "paid",
            }
            with self.subTest(value=value):
                self.assertEqual(platform.validate(row)[1], "invalid_amount")
        row["unit_price"] = "1.00"
        row["order_date"] = "not-a-date"
        self.assertEqual(platform.validate(row)[1], "invalid_date")


if __name__ == "__main__":
    unittest.main()
