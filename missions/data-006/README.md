# DATA-006 — Airflow retry/backfill republishes stale or conflicting daily totals

**Company:** Atlas Retail · **Role:** Data Platform Engineer · **Prerequisites:** RETAIL-003, DATA-004 and DATA-005

## The incident

The nightly orchestration reports success. After a retry, two different totals exist for the same business date. A historical backfill also overwrote the current daily report. The company needs **partition-scoped idempotent publishing**, explicit retry semantics and a safe backfill strategy.

This mission has two components: (1) a real local file-based partition publisher with fault-injection tests and (2) an Airflow 3 DAG factory for scheduling extract -> validate -> publish. The public grader checks the local behavior without requiring Airflow to be installed; optional DAG tests require Airflow's Task SDK.

## Contract A — local task and backfill

~~~python
dag_blueprint() -> dict
publish_partition(rows: list[dict], run_date: str, output_root: Path,
                  fail_before_publish: bool = False) -> dict
~~~

dag_blueprint must return exactly:

~~~json
{
  "dag_id": "atlas_retail_backfill",
  "schedule": "0 2 * * *",
  "catchup": true,
  "retries": 2,
  "tasks": ["extract", "validate", "publish"],
  "edges": [["extract", "validate"], ["validate", "publish"]]
}
~~~

Input rows each contain order_id, order_date, status and amount_cents. For the requested ISO business date:

- Require a nonempty list with nonblank order IDs, valid ISO dates matching run_date, status paid or cancelled and nonnegative integer amount_cents (reject bool).
- Exact duplicate order rows are ignored. Two different valid rows with the same order_id reject the entire run with ValueError("conflicting_order").
- Invalid rows/dates reject the run with ValueError("invalid_record") or ValueError("invalid_run_date").
- Cancelled orders contribute zero; all unique valid order IDs count as accepted orders.
- Publish a JSON object at output_root/partitions/YYYY-MM-DD/revenue.json containing partition_date, accepted_orders, paid_revenue_cents and source_sha256.
- Compute source_sha256 from deterministic JSON of the normalized **unique** source rows, sorted by order ID; changing input row order or repeating an identical record must not change the hash.
- Return the object above plus status="created" on new publish, or status="replayed" on identical retry. Do not modify a previously published file on replay.
- If an existing partition has a different source hash, raise ValueError("partition_conflict") and do not overwrite.
- Stage the complete output file in the same directory/filesystem before moving into place. If fail_before_publish=True, raise RuntimeError("simulated_failure") after staging but before publication, and leave **no published partition** or temporary files.

This local pattern does not make filesystem writes and external database commits one distributed transaction. Real concurrent writers also need a stronger conditional publication design. Explain these limitations in your PR.

## Contract B — optional Airflow DAG

Implement build_airflow_dag() to return a DAG using the **Airflow 3 public Task SDK** and the blueprint above: schedule at 02:00 daily, catchup enabled, 2 retries, and extract -> validate -> publish dependencies. The DAG must use logical run date, not the wall-clock date, when materializing partitions.

The default platform CI does not install or start Airflow. A future containerized Airflow scheduler/backfill test is a separate public launch gate; don't claim it passed.

## Learner workflow

~~~bash
git switch -c mission/data-006
python tools/apprentice.py start data-006
python tools/apprentice.py check data-006
~~~

For an optional Airflow SDK examination, follow current docs at https://airflow.apache.org/docs/task-sdk/stable/ . The Task SDK belongs to the modern airflow.sdk public API, rather than old internal airflow.models import paths.

## Engineer's incident report

1. Why does catchup/backfill differ from retrying a single DAG run?
2. How is business date different from the date the process executes?
3. Why are tasks expected to be idempotent and recoverable?
4. How would two concurrent task attempts safely coordinate publication?
5. What is your rollback protocol when an incorrect partition has already been published?

**Status:** prototype; local partition/failure behavior testable, Airflow scheduler execution not yet verified.
