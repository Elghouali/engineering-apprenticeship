"""Deterministic contract tests for the learner's RETAIL-001 submission.

The baseline repo intentionally has no submission. CI invokes these tests only
after a learner creates submissions/retail-001/pipeline.py.
"""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "missions" / "retail-001" / "data" / "orders.csv"
SUBMISSION = Path(
    os.environ.get("APPRENTICE_SUBMISSION_PATH",
                   str(ROOT / "submissions" / "retail-001" / "pipeline.py"))
)


def row(order_id="001", customer_id="C1", quantity="1",
        unit_price="10.00", status="paid"):
    return {"order_id": order_id, "customer_id": customer_id,
            "quantity": quantity, "unit_price": unit_price, "status": status}


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SUBMISSION.is_file():
            raise AssertionError(
                "No learner submission. Copy the mission starter into "
                "submissions/retail-001/pipeline.py and fix the bugs."
            )
        spec = importlib.util.spec_from_file_location("learner_retail_001", SUBMISSION)
        if spec is None or spec.loader is None:
            raise AssertionError("Could not load submission")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        cls.pipeline = module

    def call(self, rows):
        result = self.pipeline.summarize(copy.deepcopy(rows))
        self.assertIsInstance(result, dict)
        self.assertEqual(set(result), {
            "paid_revenue_cents", "accepted_order_ids", "duplicate_count", "rejections"
        })
        self.assertIsInstance(result["paid_revenue_cents"], int)
        self.assertIsInstance(result["accepted_order_ids"], list)
        self.assertIsInstance(result["duplicate_count"], int)
        self.assertIsInstance(result["rejections"], list)
        json.dumps(result)  # Must be serializable for our reporting API.
        return result

    def test_fictional_company_fixture(self):
        self.assertTrue(hasattr(self.pipeline, "load_rows"))
        result = self.call(self.pipeline.load_rows(FIXTURE))
        self.assertEqual(result["paid_revenue_cents"], 22000)
        self.assertEqual(result["accepted_order_ids"], ["1001", "1002", "1003", "1005"])
        self.assertEqual(result["duplicate_count"], 1)
        self.assertEqual(len(result["rejections"]), 3)
        reasons = {x["order_id"]: x["reason"] for x in result["rejections"]}
        self.assertEqual(reasons, {
            "1004": "invalid_quantity",
            "1002": "conflicting_order_id",
            "1006": "missing_customer",
        })

    def test_money_exact_to_cents(self):
        entries = [row(str(i), unit_price="0.10") for i in range(1, 31)]
        result = self.call(entries)
        self.assertEqual(result["paid_revenue_cents"], 300)
        self.assertEqual(result["duplicate_count"], 0)

    def test_cancelled_orders_are_valid_but_not_revenue(self):
        result = self.call([
            row("A", unit_price="99.00", status="cancelled"),
            row("B", unit_price="0.01", status="paid"),
        ])
        self.assertEqual(result["paid_revenue_cents"], 1)
        self.assertEqual(result["accepted_order_ids"], ["A", "B"])
        self.assertEqual(result["rejections"], [])

    def test_exact_duplicate_versus_conflicting_repeat(self):
        first = row("D", unit_price="11.00")
        result = self.call([
            first, copy.deepcopy(first),
            row("D", unit_price="12.00"),
            row("E", unit_price="1.00")
        ])
        self.assertEqual(result["duplicate_count"], 1)
        self.assertEqual(result["paid_revenue_cents"], 1200)
        self.assertEqual(result["accepted_order_ids"], ["D", "E"])
        self.assertEqual(result["rejections"],
                         [{"order_id": "D", "reason": "conflicting_order_id"}])

    def test_rejected_row_does_not_reserve_business_key(self):
        result = self.call([
            row("NEW", customer_id=""),
            row("NEW", customer_id="C7", unit_price="9.00")
        ])
        self.assertEqual(result["accepted_order_ids"], ["NEW"])
        self.assertEqual(result["paid_revenue_cents"], 900)
        self.assertEqual(result["rejections"],
                         [{"order_id": "NEW", "reason": "missing_customer"}])

    def test_invalid_quantity(self):
        for quantity in ("0", "-2", "1.5", "n/a", ""):
            with self.subTest(quantity=quantity):
                result = self.call([row("q", quantity=quantity)])
                self.assertEqual(result["paid_revenue_cents"], 0)
                self.assertEqual(result["accepted_order_ids"], [])
                self.assertEqual(result["rejections"],
                                 [{"order_id": "q", "reason": "invalid_quantity"}])

    def test_invalid_amount(self):
        for amount in ("-1.00", "1.999", "NaN", "Infinity", "oops", ""):
            with self.subTest(amount=amount):
                result = self.call([row("p", unit_price=amount)])
                self.assertEqual(result["paid_revenue_cents"], 0)
                self.assertEqual(result["rejections"],
                                 [{"order_id": "p", "reason": "invalid_amount"}])

    def test_bad_status_and_required_fields(self):
        result = self.call([
            row("z", status="refunded"),
            row("", customer_id="C1"),
            row("x", customer_id="")
        ])
        self.assertEqual(result["accepted_order_ids"], [])
        self.assertEqual(
            [item["reason"] for item in result["rejections"]],
            ["invalid_status", "missing_order_id", "missing_customer"]
        )

    def test_empty_input_and_purity(self):
        result = self.call([])
        self.assertEqual(result, {
            "paid_revenue_cents": 0,
            "accepted_order_ids": [], "duplicate_count": 0, "rejections": []
        })
        source = [row("one", unit_price="2.50"), row("two", status="cancelled")]
        original = copy.deepcopy(source)
        result = self.call(source)
        self.assertEqual(source, original)
        self.assertEqual(result["paid_revenue_cents"], 250)
        self.assertEqual(self.call(source), result)


if __name__ == "__main__":
    unittest.main()
