"""Public Spark mission grader: pure planner checks + optional real PySpark."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
SUBMISSION = Path(os.environ.get(
    "APPRENTICE_SUBMISSION_PATH",
    str(ROOT / "submissions" / "data-004" / "spark_job.py")
))


class SparkMissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SUBMISSION.is_file():
            raise AssertionError("Missing data-004 submission; run apprentice.py start data-004")
        spec = importlib.util.spec_from_file_location("data004", SUBMISSION)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        cls.module = mod

    def test_skew_plan_and_partition_budget(self):
        result = self.module.recommend_buckets({
            "whale": 10001, "medium": 300, "tiny": 50
        })
        self.assertEqual(result, {
            "heavy_keys": ["whale"],
            "salt_buckets": {"whale": 11},
            "num_partitions": 11
        })

    def test_no_heavy_keys_or_empty_input(self):
        self.assertEqual(self.module.recommend_buckets({
            "a": 1000, "b": 2000, "c": 1
        }), {"heavy_keys": [], "salt_buckets": {}, "num_partitions": 4})
        self.assertEqual(self.module.recommend_buckets({}), {
            "heavy_keys": [], "salt_buckets": {}, "num_partitions": 1
        })

    def test_partition_cap_and_sorted_keys(self):
        got = self.module.recommend_buckets({"z": 50000, "a": 90000}, 1000)
        self.assertEqual(got["heavy_keys"], ["a", "z"])
        self.assertEqual(got["salt_buckets"], {"a": 16, "z": 16})
        self.assertEqual(got["num_partitions"], 64)

    def test_input_validation(self):
        for stats, target in [
            ({"a": -1}, 100), ({"a": True}, 100),
            ({"a": 2.2}, 100), ({5: 2}, 100),
            ({"a": 2}, 0), ({"a": 2}, True),
            ({"a": 2}, 1.5), ([], 100)
        ]:
            with self.subTest(stats=stats, target=target):
                with self.assertRaisesRegex(ValueError, "invalid_stats"):
                    self.module.recommend_buckets(stats, target)

    @unittest.skipUnless(os.environ.get("SPARK_LIVE") == "1",
                         "Install PySpark and set SPARK_LIVE=1 for real local Spark tests")
    def test_live_spark_aggregation_and_replay(self):
        from pyspark.sql import SparkSession
        from pyspark.sql.types import (
            StructType, StructField, StringType, LongType
        )
        spark = (SparkSession.builder.master("local[2]")
                 .appName("academy-data-004")
                 .config("spark.ui.enabled", "false")
                 .config("spark.sql.shuffle.partitions", "4")
                 .getOrCreate())
        self.addClassCleanup(spark.stop)
        schema = StructType([
            StructField("event_id", StringType(), False),
            StructField("merchant_id", StringType(), False),
            StructField("amount_cents", LongType(), False),
            StructField("status", StringType(), False)
        ])
        events = [
            ("e1", "whale", 100, "paid"),
            ("e1", "whale", 100, "paid"),
            ("e2", "whale", 350, "paid"),
            ("e3", "tiny", 500, "cancelled"),
            ("e4", "tiny", 30, "paid"),
            ("e5", "zero", 200, "cancelled"),
        ]
        df = spark.createDataFrame(events, schema)
        output = self.module.aggregate_paid_revenue(df, salt_buckets=3)
        self.assertEqual(set(output.columns), {"merchant_id", "paid_revenue_cents"})
        result = {r["merchant_id"]: r["paid_revenue_cents"] for r in output.collect()}
        self.assertEqual(result, {"whale": 450, "tiny": 30, "zero": 0})

    @unittest.skipUnless(os.environ.get("SPARK_LIVE") == "1",
                         "Requires real local Spark")
    def test_live_conflicting_replayed_event(self):
        from pyspark.sql import SparkSession
        spark = (SparkSession.builder.master("local[2]")
                 .appName("academy-data-004-conflict")
                 .config("spark.ui.enabled", "false")
                 .getOrCreate())
        self.addClassCleanup(spark.stop)
        data = [
            ("same", "merchant-a", 100, "paid"),
            ("same", "merchant-a", 110, "paid")
        ]
        df = spark.createDataFrame(data, [
            "event_id", "merchant_id", "amount_cents", "status"
        ])
        with self.assertRaisesRegex(ValueError, "conflicting_event_id"):
            self.module.aggregate_paid_revenue(df, salt_buckets=4)


if __name__ == "__main__":
    unittest.main()
