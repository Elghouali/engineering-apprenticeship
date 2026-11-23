# CAPSTONE-004 — Orchestrate retries and backfills with Airflow

**Role:** Data Platform Engineer · **Status:** pre-release change request. A real manual Airflow DAG runs the shared stack; scheduler-managed business-date backfills remain planned.

**Incident:** The current integrated DAG successfully runs four tasks for a fixed synthetic business date, but lacks scheduler-managed historical backfill partitions. Future backfills could race with the daily ingestion schedule and overwrite trusted Gold.

**Acceptance intent:** Schedule and backfill the capstone stages using an actual Airflow 3 DAG. Tasks must be idempotent, partitioned by logical business date, and safe to rerun after a crash. Record evidence from scheduler-managed DagRuns, not just a DAG parser test. The separate DATA-006 lab provides an already-tested smaller example.

**Deliverable:** DAG source, successful bounded two-day backfill, replay/rollback checks, PR review and runbook.

**Prerequisites:** [DATA-006](../../../missions/data-006/README.md). [← Capstone](../README.md).
