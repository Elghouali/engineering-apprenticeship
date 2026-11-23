"""PySpark integration against a bounded PostgreSQL snapshot.

This deliberately materializes at most 1,000 records in the driver for a
training fixture. It is NOT a scalable production JDBC/CDC/Parquet design.
"""
from __future__ import annotations

from contextlib import closing
import json
import os

from logic import canonical, daily_report
from storage import (open_postgres, prepare_db, load_events,
                     s3_client, ensure_bucket, published_bytes)


def run() -> dict:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.types import (
        StructType, StructField, StringType, LongType
    )

    with closing(open_postgres()) as conn:
        prepare_db(conn)
        events = load_events(conn)

    if len(events) > 1000:
        raise ValueError("snapshot_too_large_for_driver")
    day = os.environ["ATLAS_DATE"]
    reference = daily_report(events, day)

    spark = (SparkSession.builder.master("local[2]")
             .appName("atlas-retail-integrated-spark")
             .config("spark.ui.enabled", "false")
             .config("spark.sql.shuffle.partitions", "2")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    try:
        schema = StructType([
            StructField("event_id", StringType(), False),
            StructField("merchant_id", StringType(), False),
            StructField("business_date", StringType(), False),
            StructField("amount_cents", LongType(), False),
            StructField("status", StringType(), False)
        ])
        source = spark.createDataFrame([
            (row["event_id"], row["merchant_id"], row["business_date"],
             row["amount_cents"], row["status"])
            for row in events
        ], schema)
        selected = source.filter(F.col("business_date") == day)
        aggregated = selected.groupBy("merchant_id").agg(
            F.sum(
                F.when(F.col("status") == "paid", F.col("amount_cents"))
                .otherwise(F.lit(0))
            ).alias("paid_revenue_cents")
        )
        merchants = sorted([
            {"merchant_id": row["merchant_id"],
             "paid_revenue_cents": row["paid_revenue_cents"]}
            for row in aggregated.collect()
        ], key=lambda row: row["merchant_id"])
        paid_events = selected.filter(F.col("status") == "paid").count()
        total = sum(item["paid_revenue_cents"] for item in merchants)
        if (merchants != reference["merchants"]
                or total != reference["paid_revenue_cents"]
                or paid_events != reference["paid_events"]
                or selected.count() != reference["accepted_events"]):
            raise ValueError("spark_postgres_financial_mismatch")

        s3 = s3_client()
        ensure_bucket(s3)
        key = f"gold-spark/{day}/revenue.json"
        body = canonical(reference)
        existing = published_bytes(s3, key)
        if existing is not None and existing != body:
            raise ValueError("spark_artifact_conflict")
        state = "replayed" if existing is not None else "created"
        if existing is None:
            s3.put_object(Bucket=os.environ["ATLAS_S3_BUCKET"],
                          Key=key, Body=body, ContentType="application/json")
        if published_bytes(s3, key) != body:
            raise ValueError("spark_artifact_readback_failed")
        return {
            "spark_version": spark.version,
            "source": "postgresql_durable_events_bounded_driver_snapshot",
            "business_date": day,
            "accepted_events": reference["accepted_events"],
            "paid_revenue_cents": total,
            "s3_key": key,
            "publish_status": state,
            "verified_against_postgres": True
        }
    finally:
        spark.stop()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
