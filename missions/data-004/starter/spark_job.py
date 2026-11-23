"""DATA-004 deliberately broken Spark starter: no replay handling and no salting."""
from __future__ import annotations


def recommend_buckets(stats: dict[str, int],
                      target_rows_per_partition: int = 1000) -> dict:
    # BUG: ignores skew and always chooses one partition.
    return {"heavy_keys": [], "salt_buckets": {}, "num_partitions": 1}


def aggregate_paid_revenue(df, salt_buckets: int = 4):
    # BUG: duplicate deliveries double count. No two-level salted grouping.
    from pyspark.sql import functions as F
    return (
        df.filter(F.col("status") == "paid")
        .groupBy("merchant_id")
        .agg(F.sum("amount_cents").alias("paid_revenue_cents"))
    )
