# DATA-006 — Airflow retry/backfill republishes stale or conflicting daily totals

> **PRE-RELEASE / PROTOTYPE — contract v1.** This exercise has a public grader and a confidential correct reference, but independent first-time learner onboarding has not yet passed.

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

The default platform CI does not install Airflow. A **separate, private maintainer CI run has executed the actual Airflow 3 DAG tasks** for two historical dates using the full Airflow Docker image and verified the resulting partitions. This was run via `airflow dags test`, which is not the same as a continuously running scheduler. A separate [local Airflow scheduler verification](../../docs/AIRFLOW_BACKFILL_EVIDENCE.md) has also passed: two scheduler-managed backfill runs completed successfully and their published output was independently checked. This does **not** validate a production multi-worker Airflow deployment.

### Optional reproducible Docker DAG test for learners

After implementing the mission on a personal branch, use the included [Docker Compose file](docker-compose.yml). The [DAG discovery wrapper](tools/airflow-dags/atlas_retail_backfill.py) is only an adapter; it imports **your** `build_airflow_dag()` and does not supply an answer.

From the repository root:

~~~bash
python tools/apprentice.py start data-006
# Then implement, unit-test and commit the solution.
~~~

For Linux/macOS from `missions/data-006`:

~~~bash
mkdir -p output
export AIRFLOW_UID=$(id -u)
docker compose run --rm airflow
docker compose down
~~~

For Windows PowerShell, create `output` using `New-Item -ItemType Directory -Force output` and then run `docker compose run --rm airflow` from the same mission folder.

The container tests 2026-11-19, 2026-11-20 and a second attempt for 2026-11-20. Expected paid revenue is 150 cents per date, with two and three accepted orders respectively. The folder `output/` is gitignored. There are no public network ports or real cloud credentials. A real scheduler/worker deployment, external persistence and security boundaries require further work.

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

**Status:** prototype. Local partition/failure tests, full-container DAG task execution and a scheduler-managed two-day backfill have passed maintainer CI. Public learner onboarding and production-like deployment remain unverified.

---

## Mission handoff: from incident to pull request

**Requirements:** Python 3.11+ for partition tests; optional Airflow 3 Task SDK/Docker for DAG execution. Read the contract above before changing code.

**Training files:** [faulty starter](starter/orchestrator.py) · [public acceptance tests](tests/test_submission.py) · personal output: `submissions/data-006/orchestrator.py` (created only in a learner fork, not committed upstream).

From the **root of your own fork**, after public launch:

```bash
git switch -c mission/data-006
python tools/apprentice.py start data-006
python tools/apprentice.py check data-006
```

The first test run must fail because the starter is intentionally defective. Implement and test only in your submission; do not edit official graders. Push to your fork and open a PR **against your own fork's main branch**, not the academy upstream.

**Failure-recovery drill:** Fail after staging a historical partition, then rerun without changing already published output.

In your PR, demonstrate **Explain / Build / Recover / Defend**: root cause, passing regression checks, recovery behavior and trade-offs. See the [review rubric](../../docs/ENGINEERING_LOOP.md) and [hint policy](../../mentor/REVIEW_POLICY.md).

**Continue to:** [Local reference capstone](../../capstones/atlas-retail-platform/README.md) and [planned integrated project](../../docs/PUBLIC_CURRICULUM.md). These are suggestions; use the [catalog](../catalog.json) for exact prerequisites.

[← All missions](../README.md) · [Academy](../../README.md) · [Company](../../companies/atlas-retail/README.md) · [Documentation](../../docs/README.md)
