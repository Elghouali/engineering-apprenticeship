"""Host-side independent verification of a real Compose reporting API."""
from __future__ import annotations
import json
import sys
import time
from urllib.request import urlopen

HOST = "http://127.0.0.1:18083"


def wait_for(path: str, attempts: int = 60):
    last = None
    for _ in range(attempts):
        try:
            with urlopen(HOST + path, timeout=3) as response:
                if response.status == 200:
                    return json.load(response)
        except Exception as exc:
            last = exc
        time.sleep(2)
    raise RuntimeError(f"API never responded at {path}: {last}")


def main() -> None:
    health = wait_for("/health")
    report = wait_for("/v1/revenue")
    assert health == {"status": "ok", "report_verified": True}, health
    assert report["verified"] is True, report
    assert report["accepted_events"] == 5, report
    assert report["paid_events"] == 4, report
    assert report["paid_revenue_cents"] == 22000, report
    assert report["merchants"] == [
        {"merchant_id": "merchant-a", "paid_revenue_cents": 12000},
        {"merchant_id": "merchant-b", "paid_revenue_cents": 7500},
        {"merchant_id": "merchant-c", "paid_revenue_cents": 2500},
    ], report
    print("PASS: PostgreSQL business totals match verified S3 report via real HTTP")
    print("PASS: Kafka duplicates did not inflate revenue; total cents=22000")


if __name__ == "__main__":
    main()
