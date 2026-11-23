"""DATA-006 deliberately broken retry/backfill starter."""
from pathlib import Path
import json


def dag_blueprint():
    # BUG: catchup disabled and retry budget zero.
    return {"dag_id": "atlas_retail_backfill", "schedule": "0 2 * * *",
            "catchup": False, "retries": 0, "tasks": ["extract", "publish"],
            "edges": [["extract", "publish"]]}


def publish_partition(rows, run_date, output_root: Path, fail_before_publish=False):
    # BUG: unvalidated input, no dedup, overwrites old partitions without checking.
    folder = Path(output_root) / "partitions" / run_date
    folder.mkdir(parents=True, exist_ok=True)
    payload = {
        "partition_date": run_date,
        "accepted_orders": len(rows),
        "paid_revenue_cents": sum(r["amount_cents"] for r in rows),
        "source_sha256": "",
    }
    (folder / "revenue.json").write_text(json.dumps(payload))
    return {**payload, "status": "created"}


def build_airflow_dag():
    # BUG: missing actual Airflow task dependencies.
    return None
