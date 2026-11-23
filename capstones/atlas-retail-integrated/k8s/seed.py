"""One-time disposable Kubernetes seed job for the *real* integrated API.

This bypasses Kafka (Kafka replay is verified in the separate Compose integration).
The same durable PostgreSQL/S3 business functions are used as the integrated demo.
"""
from __future__ import annotations

from contextlib import closing
import json
import os
import time

from app import events_for_date
from storage import (open_postgres, prepare_db, store_message, s3_client,
                     publish_report, verify_report)


def retry(operation, attempts=40):
    for index in range(attempts):
        try:
            return operation()
        except Exception:
            if index == attempts - 1:
                raise
            time.sleep(2)


def main():
    day = os.environ["ATLAS_DATE"]
    events = events_for_date(day)
    with closing(retry(open_postgres)) as conn:
        prepare_db(conn)
        for position, event in enumerate(events):
            store_message(conn, event, "synthetic-k8s-seed", 0, position)

        def connect_store():
            store = s3_client()
            store.list_buckets()
            return store
        s3 = retry(connect_store)
        report = publish_report(conn, s3, day)
        verified = verify_report(conn, s3, day)
    if (not verified["verified"] or verified["paid_revenue_cents"] != 22000
            or verified["accepted_events"] != 5):
        raise RuntimeError("k8s_seed_financial_integrity_failure")
    print(json.dumps({"source": "synthetic_postgres_seed_without_kafka",
                      "publish_status": report["publish_status"],
                      "paid_revenue_cents": verified["paid_revenue_cents"],
                      "accepted_events": verified["accepted_events"],
                      "verified": True}))


if __name__ == "__main__":
    main()
