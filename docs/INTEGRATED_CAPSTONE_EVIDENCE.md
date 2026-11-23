# Atlas Retail Integrated Capstone — Evidence and Limitations

**Maintainer verification: November 23, 2026.** This is a real local GitHub Actions integration, not a claim of production security, distributed exactly-once guarantees or a completed learner certification.

## What has run and passed

[GitHub Actions: integrated local platform, all five jobs PASS](https://github.com/Elghouali/engineering-apprenticeship/actions/runs/45232923675)

| Validation | Exact evidence | Important limit |
| --- | --- | --- |
| Pure business contract | Ubuntu and Windows tests confirm 7 messages, 5 distinct events, 4 paid events and **22,000 cents** | Only a small synthetic business-date fixture |
| Kafka 4.4 KRaft + PostgreSQL 16 | Real broker delivery, PostgreSQL event/inbox uniqueness, forced crash after DB commit before Kafka ack, safe replay of offset | One broker/consumer group; no cross-system distributed transaction |
| S3-compatible artifact | SeaweedFS MinIO-compatible API stores deterministic Gold bytes, replay does not alter them; read-back compared to live SQL | Single writer, no conditional multiwriter publication or provider IAM |
| Reporting API | Real HTTP 200 on loopback for verified financial report, 503 intended when state is untrusted | No public ingress/TLS/auth |
| PySpark 4.0.3 + Java 17 | Real local Spark transform over PostgreSQL-derived bounded snapshot; checks merchant financial parity and S3 publish `created` then `replayed` | Max 1,000 driver-collected records; not scalable JDBC/CDC/Parquet |
| Airflow 3 Task SDK DAG | Real container executing `seed_kafka`, `persist_postgres`, `publish_s3_gold`, `verify_lineage`. DagRun marked success and returned accepted_events=5, revenue=22,000, verified=true | Manual `airflow dags test` only; no scheduler-managed integrated multi-day backfill |

Actual Spark CI logged `spark_version=4.0.3` and the S3 key `gold-spark/2026-11-20/revenue.json`. The first run reported `publish_status=created` and the second `publish_status=replayed`, both with paid revenue of **22,000 cents**.

The initial end-to-end Kafka CI failed because the default KRaft broker advertised a name that sibling containers could not reach. The verified version explicitly advertises `PLAINTEXT://kafka:9092` inside the Compose bridge. This is a real networking investigation, now reflected in the runbook.

## Architecture that has been exercised

~~~mermaid
flowchart TD
    S["Synthetic event records"] --> K["Single-node Kafka 4.4 KRaft"]
    K --> P["PostgreSQL inbox and deduplicated ledger"]
    P --> G["Deterministic Gold report"]
    P --> SP["Real PySpark local computation"]
    G --> O[("S3-compatible SeaweedFS artifact store")]
    SP --> O
    O --> A["Read-only HTTP reporting API"]
    AF["Airflow 3 four-task manual DAG"] --> K
    AF --> P
    AF --> O
~~~

**Source of truth:** PostgreSQL durable ledger. The Gold S3 objects are derived output; a consumer must compare them with trusted business state. Kafka offsets are only committed after durable persistence.

## Learner experience — still pre-release

The integrated [capstone README](../capstones/atlas-retail-integrated/README.md) includes Docker Compose commands and destructive test cleanup warnings. Five real company Issues were created ([CAPSTONE-001](https://github.com/Elghouali/engineering-apprenticeship/issues/7), [002](https://github.com/Elghouali/engineering-apprenticeship/issues/8), [003](https://github.com/Elghouali/engineering-apprenticeship/issues/9), [004](https://github.com/Elghouali/engineering-apprenticeship/issues/10), [005](https://github.com/Elghouali/engineering-apprenticeship/issues/11)). They are **pre-release**; independent accepted learner solutions and the whole progression have not been demonstrated.

## Next acceptance gates

- [ ] Replace driver-loaded Spark snapshot with scalable ingestion and demonstrate larger workloads/real performance trade-offs.
- [ ] Schedule and backfill multiple *independent* business dates with the integrated Airflow DAG, preserving immutable reports and recovery.
- [ ] Deploy the **integrated** API in a disposable Kubernetes cluster with real service dependency connectivity and rollback; the standalone CLOUD-006 kind test does not count for this.
- [ ] Add monitoring, audit/recovery metrics, secret isolation and stronger object-store conditional write policy.
- [ ] Independently validate the complete fork → mission Issues → Actions → learner PR → capstone workflow on a fresh Windows and Linux environment.
- [ ] Complete security and license approval before a public release.

[Return to the integrated capstone](../capstones/atlas-retail-integrated/README.md) · [Public release gates](PUBLIC_LAUNCH.md).
