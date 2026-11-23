"""RETAIL-001 intentionally broken starter. Copy to submissions before editing.

Production bug: the current implementation incorrectly counts cancelled orders
and repeated deliveries and uses imprecise floating-point money.
Your task is to implement the data contract documented in ../README.md.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path


def load_rows(source: str | Path) -> list[dict[str, str]]:
    with Path(source).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def summarize(rows: list[dict[str, str]]) -> dict:
    paid_revenue = 0.0
    accepted_order_ids = []
    for row in rows:
        # TODO: validate, classify duplicates/conflicts, avoid float money,
        # and do not count cancelled orders in paid revenue.
        paid_revenue += float(row["unit_price"]) * int(row["quantity"])
        accepted_order_ids.append(row["order_id"])
    return {
        "paid_revenue_cents": int(paid_revenue * 100),
        "accepted_order_ids": sorted(accepted_order_ids),
        "duplicate_count": 0,
        "rejections": [],
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="missions/retail-001/data/orders.csv")
    args = parser.parse_args()
    print(json.dumps(summarize(load_rows(args.source)), indent=2))
