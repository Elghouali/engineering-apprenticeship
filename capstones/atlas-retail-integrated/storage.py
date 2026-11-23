"""PostgreSQL durable inbox/ledger and S3-compatible immutable report sink.

All connections point only at disposable local services in the demo.
"""
from __future__ import annotations

from contextlib import closing
from datetime import date
import json
import os

from logic import canonical, daily_report, fingerprint, validate_event


def open_postgres():
    import psycopg2
    return psycopg2.connect(os.environ["ATLAS_PG_DSN"], connect_timeout=3)


def prepare_db(connection) -> None:
    with connection:
        with connection.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS business_events (
                    event_id TEXT PRIMARY KEY,
                    merchant_id TEXT NOT NULL,
                    business_date DATE NOT NULL,
                    amount_cents BIGINT NOT NULL CHECK (amount_cents > 0),
                    status TEXT NOT NULL CHECK(status IN ('paid','cancelled')),
                    payload_sha256 CHAR(64) NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS kafka_inbox (
                    topic TEXT NOT NULL,
                    partition_id INTEGER NOT NULL,
                    offset_id BIGINT NOT NULL,
                    event_id TEXT NOT NULL REFERENCES business_events(event_id),
                    payload_sha256 CHAR(64) NOT NULL,
                    PRIMARY KEY(topic, partition_id, offset_id)
                )
            """)


def store_message(connection, event: dict, topic: str,
                  partition: int, offset: int) -> bool:
    """Atomically persist the event and Kafka delivery identity.

    The caller MUST acknowledge the Kafka offset after the function returns.
    """
    payload = validate_event(event)
    sha = fingerprint(payload)
    if (not topic or type(topic) is not str or
            type(partition) is not int or partition < 0 or
            type(offset) is not int or offset < 0):
        raise ValueError("invalid_kafka_position")
    with connection:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT event_id, payload_sha256 FROM kafka_inbox
                WHERE topic=%s AND partition_id=%s AND offset_id=%s
            """, (topic, partition, offset))
            existing_offset = cur.fetchone()
            if existing_offset is not None and existing_offset != (payload["event_id"], sha):
                raise ValueError("offset_conflict")
            cur.execute(
                "SELECT payload_sha256 FROM business_events WHERE event_id=%s",
                (payload["event_id"],)
            )
            existing_event = cur.fetchone()
            if existing_event is not None and existing_event[0] != sha:
                raise ValueError("event_conflict")
            created = existing_event is None
            if created:
                cur.execute("""
                    INSERT INTO business_events(event_id, merchant_id, business_date,
                                                amount_cents, status, payload_sha256)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (payload["event_id"], payload["merchant_id"],
                      payload["business_date"], payload["amount_cents"],
                      payload["status"], sha))
            if existing_offset is None:
                cur.execute("""
                    INSERT INTO kafka_inbox(topic,partition_id,offset_id,event_id,payload_sha256)
                    VALUES (%s,%s,%s,%s,%s)
                """, (topic, partition, offset, payload["event_id"], sha))
    return created


def load_events(connection) -> list[dict]:
    with connection.cursor() as cur:
        cur.execute("""
            SELECT event_id,merchant_id,business_date,amount_cents,status
            FROM business_events ORDER BY event_id
        """)
        return [
            {"event_id": row[0], "merchant_id": row[1],
             "business_date": row[2].isoformat(), "amount_cents": row[3],
             "status": row[4]}
            for row in cur.fetchall()
        ]


def s3_client():
    import boto3
    from botocore.config import Config
    return boto3.client(
        "s3", endpoint_url=os.environ["ATLAS_S3_ENDPOINT"],
        aws_access_key_id=os.environ["ATLAS_S3_ACCESS"],
        aws_secret_access_key=os.environ["ATLAS_S3_SECRET"],
        region_name="us-east-1",
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def ensure_bucket(s3) -> None:
    from botocore.exceptions import ClientError
    bucket = os.environ["ATLAS_S3_BUCKET"]
    try:
        s3.head_bucket(Bucket=bucket)
    except ClientError as err:
        code = str(err.response.get("Error", {}).get("Code", ""))
        if code not in ("404", "NoSuchBucket", "NotFound"):
            raise
        s3.create_bucket(Bucket=bucket)


def published_bytes(s3, key: str) -> bytes | None:
    from botocore.exceptions import ClientError
    try:
        return s3.get_object(
            Bucket=os.environ["ATLAS_S3_BUCKET"], Key=key
        )["Body"].read()
    except ClientError as err:
        code = str(err.response.get("Error", {}).get("Code", ""))
        if code in ("404", "NoSuchKey", "NotFound"):
            return None
        raise


def publish_report(connection, s3, business_date: str) -> dict:
    ensure_bucket(s3)
    report = daily_report(load_events(connection), business_date)
    key = f"gold/{business_date}/revenue.json"
    body = canonical(report)
    previous = published_bytes(s3, key)
    if previous is not None:
        if previous != body:
            raise ValueError("published_partition_conflict")
        return {**report, "publish_status": "replayed", "key": key}
    # Single-writer teaching environment. A multi-writer release must use
    # conditional S3 writes, versioning or distributed coordination.
    s3.put_object(Bucket=os.environ["ATLAS_S3_BUCKET"], Key=key,
                  Body=body, ContentType="application/json")
    if published_bytes(s3, key) != body:
        raise ValueError("publish_readback_mismatch")
    return {**report, "publish_status": "created", "key": key}


def verify_report(connection, s3, business_date: str) -> dict:
    expected = daily_report(load_events(connection), business_date)
    key = f"gold/{business_date}/revenue.json"
    raw = published_bytes(s3, key)
    if raw is None or raw != canonical(expected):
        raise ValueError("report_integrity_mismatch")
    return {**expected, "verified": True, "key": key}
