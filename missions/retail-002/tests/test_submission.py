"""Public contract checks for RETAIL-002."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SUBMISSION = Path(os.environ.get("APPRENTICE_SUBMISSION_PATH",
     str(ROOT / "submissions" / "retail-002" / "payment.py")))


class PaymentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SUBMISSION.is_file():
            raise AssertionError("Missing retail-002 submission. Run apprentice.py start retail-002.")
        spec = importlib.util.spec_from_file_location("retail_002_submission", SUBMISSION)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        cls.mod = mod

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "payments.db"
        self.db = sqlite3.connect(self.database)
        self.addCleanup(self.db.close)
        self.mod.setup(self.db)

    def n(self):
        return self.db.execute("SELECT COUNT(*) FROM payments").fetchone()[0]

    def test_first_write_and_repeat(self):
        first = self.mod.record_payment(self.db, "req-1", "order-1", 1200)
        self.assertEqual(first["status"], "created")
        self.assertIsInstance(first["payment_id"], int)
        self.assertGreater(first["payment_id"], 0)
        second = self.mod.record_payment(self.db, "req-1", "order-1", 1200)
        self.assertEqual(second, {"status": "replayed", "payment_id": first["payment_id"]})
        self.assertEqual(self.n(), 1)

    def test_conflicting_retries(self):
        original = self.mod.record_payment(self.db, "req-1", "order-1", 1200)
        for order, amount in (("order-2", 1200), ("order-1", 999)):
            with self.subTest(order=order, amount=amount):
                with self.assertRaisesRegex(ValueError, "idempotency_conflict"):
                    self.mod.record_payment(self.db, "req-1", order, amount)
        self.assertEqual(self.n(), 1)
        self.assertEqual(self.db.execute(
            "SELECT order_id, amount_cents FROM payments WHERE id=?",
            (original["payment_id"],)).fetchone(), ("order-1", 1200))

    def test_invalid_data_is_not_stored(self):
        for rid, order, amount, reason in (
            ("", "order-1", 100, "invalid_request_id"),
            ("r", "", 100, "invalid_order_id"),
            ("r", "order-1", 0, "invalid_amount"),
            ("r", "order-1", -50, "invalid_amount"),
            ("r", "order-1", True, "invalid_amount"),
            ("r", "order-1", 1.5, "invalid_amount"),
        ):
            with self.subTest(reason=reason, amount=amount):
                with self.assertRaisesRegex(ValueError, reason):
                    self.mod.record_payment(self.db, rid, order, amount)
        self.assertEqual(self.n(), 0)

    def test_replay_after_reconnect(self):
        old = self.mod.record_payment(self.db, "r2", "o2", 799)
        self.db.close()
        self.db = sqlite3.connect(self.database)
        self.mod.setup(self.db)
        result = self.mod.record_payment(self.db, "r2", "o2", 799)
        self.assertEqual(result["status"], "replayed")
        self.assertEqual(result["payment_id"], old["payment_id"])
        self.assertEqual(self.n(), 1)

    def test_unique_constraint_exists(self):
        self.mod.record_payment(self.db, "unique-test", "o1", 100)
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db:
                self.db.execute(
                    "INSERT INTO payments(request_id, order_id, amount_cents) VALUES (?,?,?)",
                    ("unique-test", "o1", 100))
        self.assertEqual(self.n(), 1)

    def test_setup_idempotent(self):
        self.mod.setup(self.db)
        self.mod.setup(self.db)
        self.assertEqual(self.n(), 0)


if __name__ == "__main__":
    unittest.main()
