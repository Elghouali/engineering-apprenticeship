"""Public Airflow retry/backfill mission: deterministic local task contract."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SUBMISSION = Path(os.environ.get(
    "APPRENTICE_SUBMISSION_PATH",
    str(ROOT / "submissions" / "data-006" / "orchestrator.py")
))


def rows():
    return [
        {"order_id": "O1", "order_date": "2026-11-20",
         "status": "paid", "amount_cents": 100},
        {"order_id": "O1", "order_date": "2026-11-20",
         "status": "paid", "amount_cents": 100},
        {"order_id": "O2", "order_date": "2026-11-20",
         "status": "cancelled", "amount_cents": 600},
        {"order_id": "O3", "order_date": "2026-11-20",
         "status": "paid", "amount_cents": 50}
    ]


class AirflowTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SUBMISSION.is_file():
            raise AssertionError("Missing data-006 submission")
        spec = importlib.util.spec_from_file_location("data006", SUBMISSION)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        cls.mod = mod

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / "out"
        self.day = "2026-11-20"
        self.file = self.out / "partitions" / self.day / "revenue.json"

    def test_blueprint_catchup_and_dependencies(self):
        self.assertEqual(self.mod.dag_blueprint(), {
            "dag_id": "atlas_retail_backfill", "schedule": "0 2 * * *",
            "catchup": True, "retries": 2,
            "tasks": ["extract", "validate", "publish"],
            "edges": [["extract", "validate"], ["validate", "publish"]]
        })

    def test_partition_revenue_dedup_and_manifest(self):
        result = self.mod.publish_partition(rows(), self.day, self.out)
        self.assertEqual(result["status"], "created")
        self.assertEqual(result["partition_date"], self.day)
        self.assertEqual(result["accepted_orders"], 3)
        self.assertEqual(result["paid_revenue_cents"], 150)
        self.assertRegex(result["source_sha256"], r"^[a-f0-9]{64}$")
        self.assertTrue(self.file.exists())
        self.assertEqual(json.loads(self.file.read_text()), {
            key: value for key, value in result.items() if key != "status"
        })

    def test_identical_retry_does_not_rewrite_partition(self):
        first = self.mod.publish_partition(rows(), self.day, self.out)
        mtime = self.file.stat().st_mtime_ns
        replay = self.mod.publish_partition(list(reversed(rows())), self.day, self.out)
        self.assertEqual(replay, {**{k: v for k, v in first.items() if k != "status"},
                                  "status": "replayed"})
        self.assertEqual(self.file.stat().st_mtime_ns, mtime)
        self.assertEqual(self.mod.publish_partition(rows(), self.day, self.out)["status"],
                         "replayed")

    def test_conflicting_backfill_does_not_overwrite(self):
        before = self.mod.publish_partition(rows(), self.day, self.out)
        pointer = self.file.read_bytes()
        different = rows()
        different[0] = {**different[0], "amount_cents": 999}
        # Remove original duplicate, so data is valid but changed.
        different.pop(1)
        with self.assertRaisesRegex(ValueError, "partition_conflict"):
            self.mod.publish_partition(different, self.day, self.out)
        self.assertEqual(self.file.read_bytes(), pointer)

    def test_crash_after_staging_and_safe_recovery(self):
        with self.assertRaisesRegex(RuntimeError, "simulated_failure"):
            self.mod.publish_partition(rows(), self.day, self.out,
                                       fail_before_publish=True)
        self.assertFalse(self.file.exists())
        if self.file.parent.exists():
            self.assertEqual(list(self.file.parent.iterdir()), [])
        result = self.mod.publish_partition(rows(), self.day, self.out)
        self.assertEqual(result["paid_revenue_cents"], 150)

    def test_invalid_inputs_reject_without_publication(self):
        for invalid in [
            [{**rows()[0], "amount_cents": True}],
            [{**rows()[0], "amount_cents": -1}],
            [{**rows()[0], "status": "processing"}],
            [{**rows()[0], "order_date": "2026-11-19"}],
            [{**rows()[0], "order_id": ""}],
            [],
        ]:
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "invalid_record"):
                    self.mod.publish_partition(invalid, self.day, self.out)
                self.assertFalse(self.file.exists())
        with self.assertRaisesRegex(ValueError, "invalid_run_date"):
            self.mod.publish_partition(rows(), "2026-13-40", self.out)

    def test_conflict_within_partition_rejected(self):
        different = rows()
        different.append({**rows()[0], "amount_cents": 777})
        with self.assertRaisesRegex(ValueError, "conflicting_order"):
            self.mod.publish_partition(different, self.day, self.out)
        self.assertFalse(self.file.exists())

    @unittest.skipUnless(os.environ.get("AIRFLOW_SDK_LIVE") == "1",
                         "Real Airflow DAG structural test is opt-in")
    def test_airflow_sdk_dag_structure(self):
        dag = self.mod.build_airflow_dag()
        self.assertEqual(dag.dag_id, "atlas_retail_backfill")
        self.assertTrue(dag.catchup)
        self.assertEqual(set(dag.task_ids), {"extract", "validate", "publish"})
        self.assertEqual(dag.get_task("extract").downstream_task_ids, {"validate"})
        self.assertEqual(dag.get_task("validate").downstream_task_ids, {"publish"})


if __name__ == "__main__":
    unittest.main()
