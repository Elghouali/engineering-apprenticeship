"""Airflow 3 Task SDK DAG for the real shared Atlas Retail platform.

Uses the same Kafka, PostgreSQL and object-store services as the Docker demo;
it does not reproduce or substitute standalone toy-task implementations.

This first version is manually triggered against the fixed synthetic date.
Historical, independently partitioned backfills are a subsequent milestone.
"""
from __future__ import annotations

from datetime import datetime, timezone

from airflow.sdk import dag, task


@dag(
    dag_id="atlas_integrated_pipeline",
    start_date=datetime(2026, 11, 20, tzinfo=timezone.utc),
    schedule=None,
    catchup=False,
    default_args={"retries": 2},
    tags=["atlas-retail", "pre-release", "integrated"],
)
def pipeline():
    @task(task_id="seed_kafka")
    def seed_kafka() -> int:
        from app import seed
        return seed()["published_messages"]

    @task(task_id="persist_postgres")
    def persist_postgres(messages: int) -> dict:
        from app import consume
        return consume(messages)

    @task(task_id="publish_s3_gold")
    def publish_s3_gold(stats: dict) -> str:
        if stats["processed_messages"] < 1:
            raise ValueError("no_durable_events")
        from app import publish
        return publish()["publish_status"]

    @task(task_id="verify_lineage")
    def verify_lineage(published: str) -> dict:
        if published not in ("created", "replayed"):
            raise ValueError("invalid_publish_state")
        from app import verify
        result = verify()
        if result["paid_revenue_cents"] != 22000:
            raise ValueError("business_revenue_mismatch")
        return {
            "accepted_events": result["accepted_events"],
            "paid_revenue_cents": result["paid_revenue_cents"],
            "verified": result["verified"],
        }

    verify_lineage(publish_s3_gold(persist_postgres(seed_kafka())))


atlas_integrated_pipeline = pipeline()
