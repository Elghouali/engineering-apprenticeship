"""Pure configuration/security contracts for the partitioned Spark source.

Does not require PySpark/Java/PostgreSQL; the real container integration is in CI.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from spark_job import jdbc_connection, partition_count, source_query, validated_date


class TestSparkConfig(unittest.TestCase):
    def test_validated_date_rejects_untrusted_sql(self):
        self.assertEqual(validated_date("2026-11-21"), "2026-11-21")
        for candidate in ("2026-11-21' OR 1=1 --", "2026-99-99", None):
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    validated_date(candidate)

    def test_partition_count_bounded(self):
        self.assertEqual(partition_count("4"), 4)
        for bad in ("0", "33", "-5", "many", None):
            with self.subTest(value=bad):
                with self.assertRaisesRegex(ValueError, "invalid_jdbc_partitions"):
                    partition_count(bad)

    def test_jdbc_query_filters_date_and_shards_by_id(self):
        query = source_query("2026-11-21", 4)
        self.assertIn("business_date = DATE '2026-11-21'", query)
        self.assertIn("hashtext(event_id)", query)
        self.assertIn("% 4", query)
        self.assertIn("AS atlas_shard", query)
        with self.assertRaises(ValueError):
            source_query("2026-11-21' --", 4)

    def test_credentials_are_separate_from_jdbc_url(self):
        url, user, password = jdbc_connection(
            "postgresql://atlas:local%40demo@postgres:5432/atlas_retail"
        )
        self.assertEqual(url, "jdbc:postgresql://postgres:5432/atlas_retail")
        self.assertEqual(user, "atlas")
        self.assertEqual(password, "local@demo")
        self.assertNotIn(password, url)
        for bad in ("sqlite:///tmp/test.db",
                    "postgresql://atlas@postgres/db",
                    "postgresql://atlas:pass@postgres/db?sslmode=disable"):
            with self.subTest(dsn=bad):
                with self.assertRaisesRegex(ValueError, "invalid_postgres_dsn"):
                    jdbc_connection(bad)


if __name__ == "__main__":
    unittest.main()
