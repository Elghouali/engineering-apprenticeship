"""Pure business contracts shared by the local integrated-capstone stages.

No infrastructure dependency is needed to test this module.
"""
from __future__ import annotations

from datetime import date
import hashlib
import json

FIELDS = frozenset({"event_id", "merchant_id", "business_date",
                    "amount_cents", "status"})


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")


def validate_event(raw: object) -> dict:
    if not isinstance(raw, dict) or set(raw) != FIELDS:
        raise ValueError("invalid_event")
    for field in ("event_id", "merchant_id"):
        if type(raw[field]) is not str or not raw[field].strip():
            raise ValueError("invalid_event")
    day = raw["business_date"]
    try:
        if type(day) is not str or date.fromisoformat(day).isoformat() != day:
            raise ValueError("invalid_date")
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid_event") from exc
    if (type(raw["amount_cents"]) is not int or raw["amount_cents"] <= 0
            or raw["status"] not in ("paid", "cancelled")):
        raise ValueError("invalid_event")
    return dict(raw)


def fingerprint(event: dict) -> str:
    return hashlib.sha256(canonical(validate_event(event))).hexdigest()


def daily_report(events: list[dict], business_date: str) -> dict:
    """Deduplicated, deterministic report for a business date.

    A conflicting event_id is rejected rather than silently overwritten.
    """
    try:
        if date.fromisoformat(business_date).isoformat() != business_date:
            raise ValueError("invalid_business_date")
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid_business_date") from exc
    distinct = {}
    for raw in events:
        event = validate_event(raw)
        key = event["event_id"]
        if key in distinct and distinct[key] != event:
            raise ValueError("conflicting_event")
        distinct[key] = event
    selected = [e for e in distinct.values() if e["business_date"] == business_date]
    merchants = {}
    paid_events = 0
    for e in selected:
        merchants.setdefault(e["merchant_id"], 0)
        if e["status"] == "paid":
            merchants[e["merchant_id"]] += e["amount_cents"]
            paid_events += 1
    return {
        "business_date": business_date,
        "accepted_events": len(selected),
        "paid_events": paid_events,
        "paid_revenue_cents": sum(merchants.values()),
        "merchants": [
            {"merchant_id": merchant, "paid_revenue_cents": merchants[merchant]}
            for merchant in sorted(merchants)
        ],
    }
