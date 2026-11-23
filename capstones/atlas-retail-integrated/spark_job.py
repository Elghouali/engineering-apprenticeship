"""Partitioned Spark JDBC read from the durable Atlas PostgreSQL ledger.

This is a local, single-writer educational integration. JDBC workers read a
date-filtered, hash-sharded table directly; no row-level source data is
collected into the Python driver. Small final merchant aggregates are collected
to publish a deterministic JSON report, with an explicit cardinality guard.

The two SQL reference reads detect ordinary concurrent source changes, but are
NOT a shared PostgreSQL MVCC snapshot across Spark JDBC connections. A
production CDC/immutable snapshot and multiwriter S3 protocol are still needed.
"""
from __future__ import annotations

from contextlib import closing
from datetime import date
import hashlib
import json
import os
from urllib.parse import unquote, urlparse

from logic import canonical
from storage import open_postgres, s3_client, ensure_bucket, published_bytes

MAX_MERCHANT_GROUPS = 10000
POSTGRES_DRIVER = "org.postgresql.Driver"
POSTGRES_JAR = "/usr/share/java/postgresql.jar"


def validated_date(raw: str) -> str:
    try:
        if type(raw) is not str or date.fromisoformat(raw).isoformat() != raw:
            raise ValueError("invalid_business_date")
        return raw
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid_business_date") from exc


def partition_count(raw: str) -> int:
    try:
        value = int(raw)
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid_jdbc_partitions") from exc
    if type(raw) is not str or not 1 <= value <= 32:
        raise ValueError("invalid_jdbc_partitions")
    return value


def jdbc_connection(dsn: str) -> tuple[str, str, str]:
    """Convert the demo PostgreSQL DSN to Spark's JDBC URL without leaking credentials."""
    parsed = urlparse(dsn)
    if (parsed.scheme not in ("postgres", "postgresql") or not parsed.hostname
            or not parsed.path or parsed.path == "/" or not parsed.username
            or parsed.password is None or parsed.query or parsed.fragment):
        raise ValueError("invalid_postgres_dsn")
    host = parsed.hostname
    port = parsed.port or 5432
    database = parsed.path[1:]
    if "/" in database or not database:
        raise ValueError("invalid_postgres_dsn")
    if ":" in host:
        host = f"[{host}]"
    return (f"jdbc:postgresql://{host}:{port}/{database}",
            unquote(parsed.username), unquote(parsed.password))


def source_query(day: str, partitions: int) -> str:
    """Date literal and bucket count are validated, not interpolated user SQL."""
    day = validated_date(day)
    if not isinstance(partitions, int) or not 1 <= partitions <= 32:
        raise ValueError("invalid_jdbc_partitions")
    return (
        "(SELECT event_id, merchant_id, amount_cents, status, "
        f"((hashtext(event_id)::bigint & 2147483647) % {partitions}) "
        "AS atlas_shard "
        "FROM business_events "
        f"WHERE business_date = DATE '{day}') AS atlas_source"
    )


def postgres_report(day: str) -> dict:
    """Independent aggregate oracle, never loading individual source events."""
    day = validated_date(day)
    with closing(open_postgres()) as conn:
        # Both reference queries see one consistent MVCC snapshot.
        conn.set_session(readonly=True, isolation_level="REPEATABLE READ")
        with conn.cursor() as cur:
            cur.execute("""
                SELECT count(*),
                       count(*) FILTER (WHERE status = 'paid'),
                       COALESCE(sum(amount_cents) FILTER (WHERE status = 'paid'), 0)
                  FROM business_events
                 WHERE business_date = %s
            """, (day,))
            total_rows, paid_rows, revenue = cur.fetchone()
            cur.execute("""
                SELECT merchant_id,
                       COALESCE(sum(amount_cents) FILTER (WHERE status = 'paid'), 0)
                  FROM business_events
                 WHERE business_date = %s
                 GROUP BY merchant_id
                 ORDER BY merchant_id
                 LIMIT %s
            """, (day, MAX_MERCHANT_GROUPS + 1))
            rows = cur.fetchall()
    if len(rows) > MAX_MERCHANT_GROUPS:
        raise ValueError("too_many_merchant_groups_for_json_artifact")
    return {
        "business_date": day,
        "accepted_events": int(total_rows),
        "paid_events": int(paid_rows),
        "paid_revenue_cents": int(revenue),
        "merchants": [
            {"merchant_id": merchant, "paid_revenue_cents": int(amount)}
            for merchant, amount in rows
        ],
    }


def run() -> dict:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F

    day = validated_date(os.environ["ATLAS_DATE"])
    partitions = partition_count(os.getenv("ATLAS_SPARK_JDBC_PARTITIONS", "4"))
    jdbc_url, user, password = jdbc_connection(os.environ["ATLAS_PG_DSN"])
    before = postgres_report(day)

    spark = (SparkSession.builder.master("local[2]")
             .appName("atlas-retail-integrated-spark-jdbc")
             .config("spark.ui.enabled", "false")
             .config("spark.sql.shuffle.partitions", "4")
             .config("spark.jars", POSTGRES_JAR)
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    try:
        source = (spark.read.format("jdbc")
                  .option("url", jdbc_url)
                  .option("driver", POSTGRES_DRIVER)
                  .option("dbtable", source_query(day, partitions))
                  .option("partitionColumn", "atlas_shard")
                  .option("lowerBound", "0")
                  .option("upperBound", str(partitions))
                  .option("numPartitions", str(partitions))
                  .option("fetchsize", "1000")
                  .option("user", user)
                  .option("password", password)
                  .load())
        actual_partitions = source.rdd.getNumPartitions()
        if actual_partitions != partitions:
            raise ValueError("unexpected_jdbc_partition_count")

        # No Python collection of source events. Spark performs the aggregation.
        grouped = source.groupBy("merchant_id").agg(
            F.count(F.lit(1)).alias("accepted_events"),
            F.sum(F.when(F.col("status") == "paid", F.lit(1))
                  .otherwise(F.lit(0))).alias("paid_events"),
            F.sum(F.when(F.col("status") == "paid",
                         F.col("amount_cents").cast("decimal(38,0)"))
                  .otherwise(F.lit(0).cast("decimal(38,0)")))
             .alias("paid_revenue_cents"),
        )
        print("ATLAS_SPARK_PHYSICAL_PLAN_START")
        grouped.explain(mode="formatted")
        print("ATLAS_SPARK_PHYSICAL_PLAN_END")

        # JSON is a bounded report of merchants, not a distributed file dataset.
        results = grouped.limit(MAX_MERCHANT_GROUPS + 1).collect()
        if len(results) > MAX_MERCHANT_GROUPS:
            raise ValueError("too_many_merchant_groups_for_json_artifact")
        results.sort(key=lambda row: row["merchant_id"])
        computed = {
            "business_date": day,
            "accepted_events": sum(int(r["accepted_events"]) for r in results),
            "paid_events": sum(int(r["paid_events"]) for r in results),
            "paid_revenue_cents": sum(int(r["paid_revenue_cents"]) for r in results),
            "merchants": [
                {"merchant_id": r["merchant_id"],
                 "paid_revenue_cents": int(r["paid_revenue_cents"])}
                for r in results
            ],
        }

        after = postgres_report(day)
        if before != after:
            raise ValueError("source_changed_during_spark_run")
        if computed != after:
            raise ValueError("spark_postgres_financial_mismatch")

        lineage = {
            "source_table": "postgresql.business_events",
            "read_strategy": "partitioned_jdbc_hash",
            "business_date": day,
            "source_events": computed["accepted_events"],
            "source_report_sha256": hashlib.sha256(canonical(after)).hexdigest(),
            "jdbc_partitions": actual_partitions,
            "spark_version": spark.version,
        }
        body = canonical({**computed, "lineage": lineage})
        s3 = s3_client()
        ensure_bucket(s3)
        key = f"gold-spark/{day}/revenue.json"
        existing = published_bytes(s3, key)
        if existing is not None and existing != body:
            raise ValueError("spark_artifact_conflict")
        state = "replayed" if existing is not None else "created"
        if existing is None:
            # Single-writer demo only: no conditional write or lock here.
            s3.put_object(Bucket=os.environ["ATLAS_S3_BUCKET"],
                          Key=key, Body=body, ContentType="application/json")
        if published_bytes(s3, key) != body:
            raise ValueError("spark_artifact_readback_failed")
        return {
            "spark_version": spark.version,
            "source": "postgresql_partitioned_jdbc",
            "jdbc_partitions": actual_partitions,
            "business_date": day,
            "accepted_events": computed["accepted_events"],
            "paid_revenue_cents": computed["paid_revenue_cents"],
            "s3_key": key,
            "publish_status": state,
            "verified_against_postgres": True,
            "source_report_sha256": lineage["source_report_sha256"],
        }
    finally:
        spark.stop()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
