# Atlas Retail — Integrated Data + Cloud Capstone

[← All capstones](../README.md) · [Academy home](../../README.md) · [Atlas Retail](../../companies/atlas-retail/README.md) · [Mission directory](../../missions/README.md)

> **PRE-RELEASE / EARLY INTEGRATED VERTICAL SLICE.** This is an evolving, synthetic company platform, not a complete production system or a finished learner-assigned capstone. The source code is a maintained baseline; future assignments are **changes and incidents against it**, not copying it.

## Why a connected platform?

Individual missions teach one failure at a time. The capstone shows how their decisions interact: a Kafka replay can affect PostgreSQL business state, financial aggregation and an S3-style published report. A healthy API must not serve unverified data. Learners will own the same system through GitHub Issues, commits, CI, review, failure injection and rollback.

## Currently implemented: Stage 1

~~~mermaid
flowchart LR
  E["Synthetic transaction events"] --> K["Kafka 4.4 KRaft"]
  K --> C["Replay-aware consumer"]
  C --> DB[("PostgreSQL 16\nInbox + business ledger")]
  DB --> G["Deterministic daily Gold revenue"]
  G --> S["S3-compatible SeaweedFS object store"]
  DB --> API["Reporting API"]
  S --> API
  API --> H["Loopback HTTP /health and /v1/revenue"]
~~~

**Every arrow above is a real software integration, not an architectural drawing of already finished Spark/Airflow/Kubernetes components.** The CI workflow exercises this connection (including a simulated process crash at the DB commit/Kafka acknowledgment boundary). The baseline uses a single broker, database, object-store instance and report writer.

### Tech and interface boundaries

| Component | Implementation | Invariant |
| --- | --- | --- |
| Event delivery | Real single-node Apache Kafka 4.4.0 | At-least-once; manually commit offset only after DB commit |
| Durable state | PostgreSQL 16, unique inbox position and business event ID | Exact replays cannot inflate revenue; conflicting IDs fail |
| Business contract | [logic.py](logic.py), integer cents, fixed event date | Paid only, cancelled contributes zero, deterministic totals |
| Published artifact | S3-compatible SeaweedFS/MinIO compatibility image, AWS SDK | Replays retain byte-identical report; conflicts detected |
| Reporting API | Python HTTP server inside a container | Compare report to live DB; serve 503 for missing/corrupt report |
| Local orchestration | [Docker Compose](compose.yaml) | No mandatory cloud account; only API binds host port 127.0.0.1 |

**Important provider change:** In 2026, the old MinIO community images became unreliable/unavailable. The lab therefore uses the maintained [SeaweedFS MinIO-compatible S3 adapter](https://github.com/seaweedfs/minio-compat); it offers a familiar S3 endpoint but is not an identical MinIO server. Use an **empty dedicated volume** and never mount old MinIO storage directories.

## Quick start — run locally

Prerequisites: Docker Engine/Desktop with Compose v2, an editor/terminal, and enough space for PostgreSQL, Kafka, SeaweedFS and a small Python container. Python 3.11+ is additionally useful for host-side test scripts.

Run from **this directory** (the repository path is `capstones/atlas-retail-integrated`):

~~~bash
docker compose config --quiet
docker compose up -d postgres kafka objectstore
docker compose build runner
docker compose run --rm runner demo
docker compose --profile api up -d api
~~~

Then open **http://127.0.0.1:18083/health** and **http://127.0.0.1:18083/v1/revenue**.

Expected fixture data: **7 Kafka messages** representing **5 distinct events**, including **two exact replays** and a cancelled event; **4 paid events**, **22,000 integer cents** of paid revenue, and merchant totals of 12,000 / 7,500 / 2,500 cents.

Run `docker compose run --rm runner demo` a second time: it seeds another copy of the seven synthetic broker messages, consumes and acknowledges them, but the PostgreSQL ledger stays at five unique event IDs and the report is replayed byte-for-byte.

### Crash/recovery demonstration

Run this sequence on a **fresh, disposable stack** rather than one containing useful data:

~~~bash
docker compose run --rm runner seed
docker compose run --rm runner consume --max 1 --fail-after-event evt-100
# The preceding command is EXPECTED to fail after the PostgreSQL commit.
docker compose run --rm runner consume --max 7
docker compose run --rm runner publish
docker compose run --rm runner verify
~~~

The second consumer must process the unacknowledged first offset again, recognize it as an exact replay, finish the remaining messages and commit Kafka offsets. The source report should still show **22,000 cents**, not a double payment.

For a full automated demonstration using isolated disposable volumes, on Linux/macOS/Git Bash:

~~~bash
bash ci/smoke.sh
~~~

This script **deletes the Compose volumes on exit**. Do not run it against any stack containing data you want to retain.

### Stop / reset

~~~bash
docker compose --profile api --profile tools down
# Only to discard ALL demo PostgreSQL and object-store data:
docker compose --profile api --profile tools down -v
~~~

If host port **18083** is already used, stop the conflicting local server before running this lab. The API has no authentication and must not be exposed to the public internet.

## Pure Python tests (without Docker)

From the **repository root**:

~~~bash
python -m unittest discover -s capstones/atlas-retail-integrated/tests -v
~~~

These tests verify the deterministic business contract even when Docker is unavailable. The separate [end-to-end CI workflow](../../.github/workflows/atlas-integrated.yml) exercises the real containers. A Docker fixture is not a production resiliency, security or scale test.


## Stage 2 — Verified real Spark and Airflow integration

The first baseline remains unchanged and fully tested. Stage 2 adds **two independently executed runtime paths over the SAME PostgreSQL/Kafka/S3 setup**.

~~~mermaid
flowchart LR
  K["Kafka real events"] --> PG[("PostgreSQL unique ledger")]
  PG --> SQL["Python Gold publication"]
  PG --> S["Spark 4.0.3 local transform"]
  SQL --> O[("S3-compatible object store")]
  S --> O
  A["Airflow 3 DAG tasks"] --> K
  A --> PG
  A --> O
  O --> API["Verified reporting API"]
~~~

### Spark: partitioned PostgreSQL JDBC ingestion, SQL parity, S3 replay

The Spark runtime now reads the durable `business_events` table **directly with PostgreSQL JDBC**. It filters a validated business date in PostgreSQL and partitions the read using a deterministic hash of `event_id` (default **four JDBC partitions**). The prior 1,000-event driver snapshot is no longer used. Spark performs the financial aggregation in executors; **only the bounded final merchant aggregates** are collected for a JSON report (maximum 10,000 merchants).

An independent PostgreSQL SQL aggregate is read before and after the Spark job and must exactly match Spark's paid-only integer-cent totals, paid event count, accepted event count and merchant totals. The report is published under `gold-spark/<date>/revenue.json` with deterministic provenance metadata (source table, input count, partition count, Spark version and SHA-256 of the SQL reference). A replay must yield byte-identical data; unexpected changes **fail closed** rather than overwriting a published object.

~~~bash
# Disposable lab only. Run from capstones/atlas-retail-integrated:
docker compose up -d postgres kafka objectstore
docker compose build runner spark
docker compose run --rm runner demo
docker compose run --rm spark                     # creates 2026-11-20 artifact
docker compose run --rm spark                     # byte-identical replay
docker compose run --rm --entrypoint python runner /app/seed_scale.py
docker compose run --rm -e ATLAS_DATE=2026-11-21 spark  # 2,403 durable events
~~~

**Verified on real GitHub Actions:** both five-event and **2,403-event** dates used four JDBC partitions, SQL reconciliation and created/replayed S3 artifacts. [Job evidence](https://github.com/Elghouali/engineering-apprenticeship/actions/runs/45238994332) · [full evidence and limitations](../../docs/INTEGRATED_CAPSTONE_EVIDENCE.md).

**What this does *not* prove:** Spark still runs in local mode, the hash-based JDBC strategy may scan PostgreSQL multiple times, the underlying JDBC connections do not share one exported MVCC snapshot, the report is JSON with bounded merchant cardinality, and no statistically sound multi-run skew/scale benchmark or concurrent-writer recovery test has been completed. Production-style CDC or immutable Parquet snapshots and distributed Spark clusters remain future work. [CAPSTONE-003](tickets/CAPSTONE-003.md) stays open.

### Airflow: real shared-pipeline tasks

The [Airflow 3 Task SDK DAG](airflow/dags/atlas_integrated.py) invokes the actual Kafka producer, PostgreSQL consumer, S3 publisher and final verification logic, with task order:

~~~text
seed_kafka -> persist_postgres -> publish_s3_gold -> verify_lineage
~~~

~~~bash
# From the capstone directory, with a disposable stack:
docker compose up -d postgres kafka objectstore
docker compose build airflow runner
docker compose --profile airflow run --rm airflow bash -c "airflow db migrate && airflow dags test atlas_integrated_pipeline 2026-11-20"
docker compose run --rm runner verify
~~~

A full CI run executed and marked all four DAG tasks successful, returning 5 accepted unique events and 22,000 paid cents. This particular integrated DAG uses **manual execution and a fixed synthetic business date**: a scheduler-managed, partitioned multi-day historical backfill for this new platform has **not** yet been verified. See [CAPSTONE-004](tickets/CAPSTONE-004.md).

### Reproducible isolated CI smoke scripts

- `bash ci/smoke.sh` — real Kafka/Postgres/S3/API, crash-after-commit replay, verification.
- `bash ci/spark.sh` — same durable records, Spark calculation, S3 artifact and replay.
- `bash ci/airflow.sh` — actual shared Airflow DAG task execution and financial verification.

**All three scripts delete disposable Docker volumes after finishing**. Never run them against existing valuable data or a shared production context. See the [verified CI evidence report](../../docs/INTEGRATED_CAPSTONE_EVIDENCE.md).


## Repository structure

~~~text
atlas-retail-integrated/
├── app.py                  # Kafka producer, manual-ack consumer, report and HTTP CLI
├── logic.py                # Pure deterministic business contracts
├── storage.py              # PostgreSQL inbox/ledger + S3-compatible report publishing
├── data/events.json        # Synthetic records incl. deliberate exact duplicates
├── Dockerfile              # Non-root Python runtime
├── compose.yaml            # Real local PostgreSQL, Kafka, object store and API
├── tests/test_logic.py     # Portable contract/failure tests
├── ci/smoke.sh             # Disposable end-to-end crash/replay smoke run
├── ci/smoke_http.py        # Independent health and financial verification
├── spark_job.py            # Partitioned JDBC Spark; SQL parity and provenance
├── Dockerfile.spark        # Java 17 / PySpark 4.0.3 runtime
├── airflow/dags/           # Airflow 3 Task SDK shared application tasks
├── Dockerfile.airflow      # Real Airflow 3 task runtime
├── ci/spark.sh             # Spark/PostgreSQL/S3 integration
├── ci/airflow.sh           # Integrated Airflow DAG execution
├── tickets/                # Upcoming GitHub-native learner change requests
└── RUNBOOK.md              # Investigation and recovery procedures
~~~

## Learner assignment structure

The baseline is **not** the student's completed answer. The academy will publish **company-style GitHub Issues** asking learners to improve the system in stages. Each ticket will require evidence: reproduce the bug, reason about the data contract, fix code, add tests, verify operational recovery, and submit a PR **to the learner's own fork**. Confidential acceptance references for future changes remain private.

1. [CAPSTONE-001 — Observe and verify the first complete release](tickets/CAPSTONE-001.md) — incident intake, architecture and baseline metrics.
2. [CAPSTONE-002 — Protect streaming replay under consumer restarts](tickets/CAPSTONE-002.md) — rollback, conflicting event IDs and durability under retries.
3. [CAPSTONE-003 — Replace a snapshot with a true Spark transformation](tickets/CAPSTONE-003.md) — measured shuffle/partition decisions.
4. [CAPSTONE-004 — Orchestrate backfills with Airflow](tickets/CAPSTONE-004.md) — task dependencies, deterministic business dates, failure recovery.
5. [CAPSTONE-005 — Deploy and recover the reporting API on Kubernetes](tickets/CAPSTONE-005.md) — Service, probes, rollout and incident triage.

**Status distinction:** Tickets are an engineering backlog, not automatically finished graded assignments. A partitioned JDBC Spark ingestion path with a 2,403-event CI fixture and manually triggered Airflow are verified; scale/performance benchmarking, scheduler-managed integrated backfills and Kubernetes deployment remain future incident deliverables. The existing [12 standalone missions](../../missions/README.md) already have public contracts and private correct references, but the *integrated* assignment has not been independently completed.

## Honest scope and security

This is a **single-writer educational stack**, not production exactly-once Kafka semantics or transactional writes across PostgreSQL and S3. S3 publication checks for an existing key before writing but does **not** protect against concurrent writers; use conditional requests/locking or versioned immutable objects in a production design. Kafka producer retries and consumer acknowledgements are demonstrated only in a one-broker setting.

The repository includes **clearly labeled local demo credentials** because it is a disposable tutorial. Do not reuse them, push real secrets, attach existing private volumes, run arbitrary student Dockerfiles with maintainer credentials, or expose host ports beyond the loopback mapping. Further hardening (TLS, IAM, network policies, external secrets, HA, observability, image scanning and backup/restore) remains a work item.

See [RUNBOOK.md](RUNBOOK.md) and the [public launch checklist](../../docs/PUBLIC_LAUNCH.md).
