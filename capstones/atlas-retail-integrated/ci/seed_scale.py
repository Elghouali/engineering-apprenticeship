"""Synthetic deterministic >1000-event durability fixture for Spark JDBC smoke tests.

This inserts into the *disposable* ledger only. It is not a Kafka/load benchmark,
not a production loader, and not meant for any real financial system.
"""
from __future__ import annotations

from contextlib import closing
import json

from psycopg2.extras import execute_values

from logic import fingerprint
from storage import open_postgres, prepare_db

DAY = "2026-11-21"
COUNT = 2403


def fixture():
    for i in range(COUNT):
        event = {
            "event_id": f"scale-{i:07d}",
            "merchant_id": "merchant-hot" if i % 10 != 0 else
                           ("merchant-cold-a" if i % 20 == 0 else "merchant-cold-b"),
            "business_date": DAY,
            "amount_cents": (i % 7 + 1) * 100,
            "status": "cancelled" if i % 5 == 0 else "paid",
        }
        yield (event["event_id"], event["merchant_id"], event["business_date"],
               event["amount_cents"], event["status"], fingerprint(event))


def main() -> None:
    with closing(open_postgres()) as conn:
        prepare_db(conn)
        with conn:
            with conn.cursor() as cur:
                execute_values(cur, """
                    INSERT INTO business_events
                    (event_id, merchant_id, business_date, amount_cents, status, payload_sha256)
                    VALUES %s
                    ON CONFLICT (event_id) DO NOTHING
                """, list(fixture()), page_size=500)
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM business_events WHERE business_date = %s",
                        (DAY,))
            (found,) = cur.fetchone()
    if found != COUNT:
        raise ValueError("scale_fixture_durable_row_count_mismatch")
    print(json.dumps({"date": DAY, "durable_rows": found,
                      "source": "synthetic_postgres_only", "event_count_gt_1000": True}))


if __name__ == "__main__":
    main()
