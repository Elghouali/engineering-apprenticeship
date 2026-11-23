# Integrated Atlas Retail — Incident and Recovery Runbook

[← Integrated capstone](README.md) · [Mission backlog](tickets/CAPSTONE-001.md)

**Scope:** disposable local Docker Compose test stack. No production credentials, billing account or real customer records.

## Incident triage order

1. Run `docker compose ps` from the capstone folder to identify stopped or unhealthy services.
2. Read `docker compose logs --tail=100 postgres kafka objectstore runner api` as appropriate; redact any sensitive data before sharing logs.
3. Inspect local API `http://127.0.0.1:18083/health`; a 503 means the report cannot be independently verified against business state.
4. Run `docker compose run --rm runner verify` to compare PostgreSQL totals with the S3 object.
5. If the database is not ready, check PostgreSQL readiness before attempting to replay messages; do not advance Kafka offsets without durable writes.
6. If the object store is unavailable, **do not** serve a cached unverified Gold report as healthy.

## Reproducing the critical crash

From a new, empty Compose stack:

~~~bash
docker compose up -d postgres kafka objectstore
docker compose build runner
docker compose run --rm runner seed
docker compose run --rm runner consume --max 1 --fail-after-event evt-100
~~~

The last command must exit nonzero **after inserting a durable business event but before acknowledging the offset**. Starting a new consumer with the same group and earliest fallback must replay the record without creating a second ledger row.

~~~bash
docker compose run --rm runner consume --max 7
docker compose run --rm runner publish
docker compose run --rm runner verify
~~~

Expected reported paid revenue: **22000 cents**, distinct event count **5**, paid event count **4**.

## Error classes and responses

| Symptom | Likely cause | Correct response |
| --- | --- | --- |
| `postgres_not_ready` | DB not started, bad DSN or wrong credentials | Fix the local service; do not acknowledge uncommitted messages |
| `kafka_not_ready` or consumer timeout | Broker/group/partition unavailable | Inspect bootstrap address and broker logs; retry safe consumer |
| `event_conflict` | Same event ID delivered with different financial payload | Stop and escalate; never overwrite an established payment blindly |
| `offset_conflict` | One Kafka offset maps to different payload | Reject, preserve durable state and investigate broker/source integrity |
| `published_partition_conflict` | Existing daily report differs from live ledger | Stop publication and review the backfill and ownership protocol |
| HTTP 503 | S3/DB/report mismatch or missing artifact | Fail closed and restore verified state; never treat HTTP reachability as data freshness |
| Unexpected increase in accepted events | Unique ID or transaction contract broken | Review inbox constraints and Kafka acknowledgments before replay |

## Restore without destroying evidence

For debugging, first save logs and synthetic fixture hashes; never run destructive commands blindly. Preserve the existing volume while investigating. If the whole lab is disposable and you want to restart from scratch, use `docker compose --profile api --profile tools down -v`, then seed again. The `-v` flag irreversibly removes the demo's database and object-store state.

## What this runbook does not claim

It does not specify a production DR RTO/RPO, multi-broker Kafka recovery, replica failover, KMS permissions, S3 version history, SLA compliance, a public ingress or production monitoring. Those are future company incidents and need their own evidence.

Official references: https://www.postgresql.org/docs/16/index.html · https://kafka.apache.org/44/documentation/ · https://github.com/seaweedfs/minio-compat


## Stage 2: Spark and Airflow investigations

**Spark report disagrees with PostgreSQL:** Spark now reads date-filtered PostgreSQL events directly through **four hash-sharded JDBC connections** by default (`ATLAS_SPARK_JDBC_PARTITIONS=4`). It compares paid-only sums, counts and merchant totals against independent read-only PostgreSQL aggregates *before and after* processing. No raw events are collected into the driver. Inspect the marked `ATLAS_SPARK_PHYSICAL_PLAN_START/END` section of logs and check `gold-spark/<date>/revenue.json` lineage. A `spark_postgres_financial_mismatch` or `source_changed_during_spark_run` must block publishing. Confirm the durable business state and replay logic; do not force an overwrite.

**JDBC connection or load failure:** Check `ATLAS_PG_DSN`, service connectivity, the PostgreSQL JDBC jar inside the Spark image, the configured partition count (1–32) and Postgres query capacity. The deterministic hash sharding can issue multiple table scans. It is a teaching baseline, not a proven scalable benchmark. Use `bash ci/spark.sh` only with disposable volumes; the script creates a second 2,403-event synthetic date and verifies both initial publication and replay. It deletes lab volumes on exit.

**Large number of merchants:** The JSON report intentionally caps the final merchant set at 10,000 and fails closed above that limit; source event count has no such driver limit. A production warehouse should use Parquet/Delta/Iceberg partitioned output instead of driver-collected JSON.

**Cross-connection snapshot consistency:** The SQL oracle is read using repeatable-read but Spark's JDBC workers do not share that transaction's MVCC snapshot. The before/after parity check detects ordinary changes but is **not** a strict transactional source snapshot in the presence of concurrent writes. Pause ingestion or adopt an immutable exported snapshot/CDC design for production.

**Airflow DAG fails after seed or before publish:** Do not assume an unfinished task means nothing was persisted. Kafka messages and PostgreSQL rows may already exist. A retry must use the same event IDs, preserve unique business state and revalidate the published S3 object. Run `bash ci/airflow.sh` in a disposable stack, inspect task-specific Airflow logs, and distinguish `airflow dags test` from a real scheduler-managed multi-day backfill. The integrated DAG is currently manual/fixed-date; that is a deliberate outstanding change request.

**Never use S3 overwrite as a shortcut:** If a published partition differs from business state, stop and escalate. The single-writer lab's check-before-put is not a distributed conditional write or a concurrency guarantee.

## Stage 3: new pre-release incident tests

**Historical backfill:** `ci/airflow.sh` runs DAG tests for two dates and repeats the first. `ci/airflow_scheduler.sh` starts an isolated Airflow 3 scheduler and creates an explicit two-day backfill; validate each actual DagRun state rather than assuming a successful CLI creation means the tasks ran. Stop if a backfill tries to overwrite a changed historical object or mixes business dates. Both scripts destroy disposable demo data.

**Kubernetes API:** `ci/kind.sh` creates its own disposable Kind cluster, installs synthetic PostgreSQL/S3 plus a one-time seed Job, and verifies the API over localhost port-forward. `/live` tests the process; `/health` fails closed when the business report cannot be trusted. A deliberately broken image must not replace the healthy API; use `kubectl -n atlas-lab rollout undo deployment/atlas-api` and verify the reporting endpoint and Ready endpoint count after recovery. Never run this training cleanup script against a valuable cluster or give it production secrets.

**Limits:** Neither test currently proves production high availability, shared transactional snapshot, real Kubernetes Kafka, external TLS/Ingress, real secret management, durable volumes or multi-AZ DR. The two new CI jobs are **under verification**, not release-certified.

[Public integration evidence](../../docs/INTEGRATED_CAPSTONE_EVIDENCE.md).
