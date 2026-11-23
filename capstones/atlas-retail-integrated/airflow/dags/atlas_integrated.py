"""Airflow 3 Task SDK DAG for historical partitions on the SAME Atlas platform.

Every Task SDK task receives the immutable logical business date from Airflow,
not the worker wall clock. Replay re-seeds the same event IDs, consumes newly
appended broker offsets, and publishes to date-scoped S3 keys only.

Caution: one Kafka consumer group and single writer. This intentionally does
not claim production concurrency isolation or multi-scheduler HA.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from airflow.sdk import dag, task


@dag(
    dag_id="atlas_integrated_pipeline",
    start_date=datetime(2026, 11, 20, 2, tzinfo=timezone.utc),
    schedule="0 2 * * *",
    catchup=False,  # historical windows are created explicitly by the backfill CLI
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(seconds=10)},
    tags=["atlas-retail", "pre-release", "integrated", "backfill"],
)
def pipeline():
    @task(task_id="select_business_date")
    def select_business_date() -> str:
        from airflow.sdk import get_current_context
        from app import events_for_date
        logical_date = get_current_context()["logical_date"]
        if logical_date is None:
            raise ValueError("missing_logical_date")
        day = logical_date.date().isoformat()
        events_for_date(day)  # validates date without external side effects
        return day

    @task(task_id="seed_kafka")
    def seed_kafka(day: str) -> dict:
        from app import seed
        return seed(day)

    @task(task_id="persist_postgres")
    def persist_postgres(day: str, seeded: dict) -> dict:
        from app import consume
        if seeded["business_date"] != day or seeded["published_messages"] < 1:
            raise ValueError("invalid_seeded_partition")
        return consume(seeded["published_messages"])

    @task(task_id="publish_s3_gold")
    def publish_s3_gold(day: str, stats: dict) -> str:
        if stats["processed_messages"] < 1:
            raise ValueError("no_durable_events")
        from app import publish
        return publish(day)["publish_status"]

    @task(task_id="verify_lineage")
    def verify_lineage(day: str, published: str) -> dict:
        if published not in ("created", "replayed"):
            raise ValueError("invalid_publish_state")
        from app import verify, events_for_date
        from logic import daily_report
        report = verify(day)
        expected = daily_report(events_for_date(day), day)
        if any(report[field] != expected[field] for field in
               ("accepted_events", "paid_events", "paid_revenue_cents", "merchants")):
            raise ValueError("business_revenue_mismatch")
        return {
            "business_date": day,
            "accepted_events": report["accepted_events"],
            "paid_revenue_cents": report["paid_revenue_cents"],
            "verified": report["verified"],
        }

    day = select_business_date()
    seeded = seed_kafka(day)
    persisted = persist_postgres(day, seeded)
    state = publish_s3_gold(day, persisted)
    verify_lineage(day, state)


atlas_integrated_pipeline = pipeline()
