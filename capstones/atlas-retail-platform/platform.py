"""Local end-to-end retail data product: safe immutable releases and freshness.

Python 3.11+ / standard library only. Educational, not a cloud deployment.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile

FIELDS = ("order_id", "customer_id", "order_date", "quantity", "unit_price", "status")
RELEASE_ID = re.compile(r"^[a-f0-9]{16}$")
ARTIFACTS = ("orders.db", "gold.csv", "rejections.csv")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(row: dict) -> tuple[dict | None, str | None]:
    oid = (row.get("order_id") or "").strip()
    customer = (row.get("customer_id") or "").strip()
    if not oid:
        return None, "missing_order_id"
    if not customer:
        return None, "missing_customer"
    day = (row.get("order_date") or "").strip()
    try:
        if date.fromisoformat(day).isoformat() != day:
            return None, "invalid_date"
    except ValueError:
        return None, "invalid_date"
    qty = (row.get("quantity") or "").strip()
    if not qty.isdecimal() or int(qty) < 1:
        return None, "invalid_quantity"
    amount = (row.get("unit_price") or "").strip()
    try:
        price = Decimal(amount)
        if not price.is_finite() or price < 0 or price.as_tuple().exponent < -2:
            return None, "invalid_amount"
        cents = int(price * 100)
    except (InvalidOperation, ValueError, TypeError, OverflowError):
        return None, "invalid_amount"
    status = (row.get("status") or "").strip()
    if status not in ("paid", "cancelled"):
        return None, "invalid_status"
    return {
        "order_id": oid, "customer_id": customer, "order_date": day,
        "quantity": int(qty), "unit_price_cents": cents, "status": status
    }, None


def collect(source: Path) -> tuple[list[dict], list[dict], dict]:
    accepted, rejected = [], []
    seen = {}
    with source.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or []) != FIELDS:
            raise ValueError("source_schema_mismatch")
        total, duplicate = 0, 0
        for position, raw in enumerate(reader, 2):
            total += 1
            record, reason = validate(raw)
            if reason:
                rejected.append({"line": position, "order_id": raw.get("order_id") or "",
                                 "reason": reason})
                continue
            oid = record["order_id"]
            if oid in seen:
                if seen[oid] == record:
                    duplicate += 1
                else:
                    rejected.append({"line": position, "order_id": oid,
                                     "reason": "conflicting_order_id"})
                continue
            seen[oid] = record
            accepted.append(record)
    if total == 0:
        raise ValueError("empty_source")
    metrics = {"input_rows": total, "accepted_orders": len(accepted),
               "duplicate_rows": duplicate, "rejected_rows": len(rejected)}
    return accepted, rejected, metrics


def write_artifacts(folder: Path, accepted: list[dict], rejected: list[dict]) -> dict:
    db_path = folder / "orders.db"
    with sqlite3.connect(db_path) as db:
        with db:
            db.execute("""
                CREATE TABLE orders(
                  order_id TEXT PRIMARY KEY, customer_id TEXT NOT NULL,
                  order_date TEXT NOT NULL, quantity INTEGER NOT NULL,
                  unit_price_cents INTEGER NOT NULL, status TEXT NOT NULL)
            """)
            db.executemany(
                "INSERT INTO orders VALUES (:order_id,:customer_id,:order_date,"
                ":quantity,:unit_price_cents,:status)", accepted)
        rows = db.execute("""
            SELECT order_date, COUNT(*), SUM(quantity * unit_price_cents)
            FROM orders WHERE status='paid'
            GROUP BY order_date ORDER BY order_date
        """).fetchall()
    with (folder / "gold.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["order_date", "paid_orders", "paid_revenue_cents"])
        writer.writerows(rows)
    with (folder / "rejections.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["line", "order_id", "reason"])
        writer.writeheader()
        writer.writerows(rejected)
    return {
        "paid_revenue_cents": sum(row[2] for row in rows),
        "latest_order_date": max((row["order_date"] for row in accepted), default=None),
        "gold_rows": len(rows),
        "files": {name: digest(folder / name) for name in ARTIFACTS}
    }


def verify(output: Path) -> dict:
    current = json.loads((output / "current.json").read_text(encoding="utf-8"))
    release = current.get("release_id", "")
    if not isinstance(release, str) or not RELEASE_ID.fullmatch(release):
        raise ValueError("unsafe_release_id")
    folder = output / "releases" / release
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("release_id") != release:
        raise ValueError("release_manifest_mismatch")
    if current.get("manifest_sha256") != digest(folder / "manifest.json"):
        raise ValueError("manifest_checksum_mismatch")
    for name in ARTIFACTS:
        if manifest["files"].get(name) != digest(folder / name):
            raise ValueError("artifact_checksum_mismatch:" + name)
    with sqlite3.connect(f"file:{(folder / 'orders.db').resolve()}?mode=ro",
                         uri=True) as db:
        count = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        revenue = db.execute(
            "SELECT COALESCE(SUM(quantity * unit_price_cents),0)"
            " FROM orders WHERE status='paid'").fetchone()[0]
    if count != manifest["accepted_orders"] or revenue != manifest["paid_revenue_cents"]:
        raise ValueError("database_metrics_mismatch")
    return manifest


def build(source: Path, output: Path, max_reject_ratio: float = .5) -> dict:
    if not 0 <= max_reject_ratio <= 1:
        raise ValueError("invalid_reject_threshold")
    accepted, rejected, metrics = collect(source)
    ratio = metrics["rejected_rows"] / metrics["input_rows"]
    if ratio > max_reject_ratio:
        raise ValueError("quality_gate_failed")
    source_hash = digest(source)
    release_id = source_hash[:16]
    output.mkdir(parents=True, exist_ok=True)
    versions = output / "releases"
    versions.mkdir(exist_ok=True)
    target = versions / release_id
    if target.exists():
        manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("source_sha256") != source_hash:
            raise ValueError("existing_release_collision")
        for name in ARTIFACTS:
            if manifest.get("files", {}).get(name) != digest(target / name):
                raise ValueError("existing_release_corrupted:" + name)
    else:
        with tempfile.TemporaryDirectory(prefix=".stage-", dir=output) as tmp:
            staging = Path(tmp) / "payload"
            staging.mkdir()
            details = write_artifacts(staging, accepted, rejected)
            manifest = {
                "release_id": release_id, "source_sha256": source_hash,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "reject_ratio": round(ratio, 4), "quality_passed": True,
                **metrics, **details,
            }
            (staging / "manifest.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            os.replace(staging, target)
    pointer = {
        "release_id": release_id,
        "manifest_sha256": digest(target / "manifest.json"),
    }
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output,
                                     prefix=".pointer-", suffix=".json",
                                     delete=False) as temp:
        temporary_pointer = Path(temp.name)
        json.dump(pointer, temp, indent=2)
    try:
        os.replace(temporary_pointer, output / "current.json")
    finally:
        temporary_pointer.unlink(missing_ok=True)
    return verify(output)


def status(output: Path, as_of: date | None = None,
           max_age_days: int = 1) -> dict:
    if max_age_days < 0:
        raise ValueError("invalid_freshness_threshold")
    manifest = verify(output)
    latest = manifest.get("latest_order_date")
    now = as_of or datetime.now(timezone.utc).date()
    age = (now - date.fromisoformat(latest)).days if latest else None
    health = ("healthy" if age is not None and 0 <= age <= max_age_days
              else "stale")
    return {"status": health, "data_age_days": age,
            "latest_order_date": latest, "release_id": manifest["release_id"]}


def main() -> int:
    p = argparse.ArgumentParser(description="Atlas Retail local data platform")
    sub = p.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="Validate source and publish immutable release")
    b.add_argument("--source", type=Path, required=True)
    b.add_argument("--output", type=Path, required=True)
    b.add_argument("--max-reject-ratio", type=float, default=.5)
    v = sub.add_parser("verify", help="Verify release and business metrics")
    v.add_argument("--output", type=Path, required=True)
    s = sub.add_parser("status", help="Check business event freshness")
    s.add_argument("--output", type=Path, required=True)
    s.add_argument("--as-of", type=date.fromisoformat)
    s.add_argument("--max-age-days", type=int, default=1)
    args = p.parse_args()
    if args.command == "build":
        result = build(args.source, args.output, args.max_reject_ratio)
    elif args.command == "verify":
        result = verify(args.output)
    else:
        result = status(args.output, args.as_of, args.max_age_days)
    print(json.dumps(result, indent=2))
    return 2 if args.command == "status" and result["status"] != "healthy" else 0


if __name__ == "__main__":
    raise SystemExit(main())
