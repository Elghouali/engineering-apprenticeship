# DATA-006 — Verified Airflow Scheduler-Managed Historical Backfill

**Verified on November 23, 2026 in an isolated private GitHub Actions runner.** This is real execution evidence, not a production readiness claim.

## What ran

- Image: Apache Airflow 3.1.8 (single standalone container, LocalExecutor and embedded metadata database)
- Airflow processes: DAG processor, scheduler, API server and executor worker
- DAG: atlas_retail_backfill, extract -> validate -> publish
- Backfill range: from 2026-11-19 02:00 UTC through 2026-11-20 03:00 UTC
- Two real backfill DagRuns created through the Airflow backfill CLI
- Synthetic source: seven records across two business dates, including deliberate exact replays and cancelled orders
- CI-only start/end bounds prevent hundreds of out-of-scope catchup runs
- No cloud credentials, external payment systems or public network ports

## Observed DagRuns

| Logical date | Airflow result | Accepted orders | Paid revenue |
| --- | --- | ---: | ---: |
| 2026-11-19 02:00 UTC | success | 2 | 150 cents |
| 2026-11-20 02:00 UTC | success | 3 | 150 cents |

Airflow's scheduler actually scheduled and completed the tasks. A separate host-side Python script inspected the JSON files published by the container and verified both business dates, counts and financial totals.

This is separate from, and stronger than, an earlier airflow dags test run, which executed DAG tasks locally without proving scheduler-controlled backfill scheduling. The first standalone experiment failed because a paused DAG left its backfill run queued. The corrected experiment unpaused the DAG after creating a bounded backfill; both dates then completed.

## How to independently reproduce it

A learner who implements the mission can use the published [Docker Compose harness](../missions/data-006/docker-compose.yml) to run actual Airflow DAG tasks. The included [DAG discovery adapter](../missions/data-006/tools/airflow-dags/atlas_retail_backfill.py) loads the learner's own solution but does not contain the answer.

The **scheduler-managed** test requires Airflow standalone, a properly configured metadata DB and a deliberately bounded catchup interval. Its reference solution and CI scripts remain in a private maintainer repository so solutions aren't leaked to students.

## Remaining limitations

This run does not establish fault tolerance of a production deployment, distributed schedulers/workers, external PostgreSQL metadata persistence, retries across worker crashes, secrets handling, large-scale backfill correctness, or independent learner onboarding. The Airflow container uses development-oriented standalone mode.

A full deployment/recovery incident is still required before the academy can call this part production-grade.

**Official references:** https://airflow.apache.org/docs/apache-airflow/3.1.8/cli-and-env-variables-ref.html and https://airflow.apache.org/docs/apache-airflow/3.1.8/start.html
