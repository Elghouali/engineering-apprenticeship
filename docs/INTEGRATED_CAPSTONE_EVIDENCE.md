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
| PySpark 4.0.3 + Java 17 | Real four-way partitioned PostgreSQL JDBC reads (no raw event collect); SQL parity and S3 `created`/`replayed` for 5 and **2,403** distinct synthetic rows | Local single driver; multi-worker scalability, consistent cross-connection snapshots and multi-run benchmark not established |
| Airflow 3 Task SDK DAG | Real container executing `seed_kafka`, `persist_postgres`, `publish_s3_gold`, `verify_lineage`. DagRun marked success and returned accepted_events=5, revenue=22,000, verified=true | Manual `airflow dags test` only; no scheduler-managed integrated multi-day backfill |

The original integrated Spark CI logged `spark_version=4.0.3` and the S3 key `gold-spark/2026-11-20/revenue.json`. The first run reported `publish_status=created` and the second `publish_status=replayed`, both with paid revenue of **22,000 cents**.

**New JDBC validation — [GitHub Actions run 45238994332](https://github.com/Elghouali/engineering-apprenticeship/actions/runs/45238994332) (November 23, 2026):** all five integrated CI jobs passed. Spark job logs record `spark_version=4.0.3`, `jdbc_partitions=4`, the formatted Spark physical plan and SQL parity. The original date has 5 events and 22,000 cents; a separate synthetic date contains **2,403 durable PostgreSQL events**, above the old hard 1,000-row limit. Both dates produced an S3 artifact with source lineage and then returned `publish_status=replayed` without overwriting the identical artifact. The scaled fixture is inserted directly into the same disposable durable ledger and is **not** a 2,403-message Kafka throughput test.

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

- [x] Replace the max-1,000 driver-collected Spark snapshot with partitioned JDBC reads and verify an input larger than 1,000 events in real integration CI.
- [ ] Independently demonstrate performance trade-offs and skew on multiple much larger workloads, plus safe consistent snapshots, distributed workers and failure recovery.
- [ ] Schedule and backfill multiple *independent* business dates with the integrated Airflow DAG, preserving immutable reports and recovery.
- [ ] Deploy the **integrated** API in a disposable Kubernetes cluster with real service dependency connectivity and rollback; the standalone CLOUD-006 kind test does not count for this.
- [ ] Add monitoring, audit/recovery metrics, secret isolation and stronger object-store conditional write policy.
- [ ] Independently validate the complete fork → mission Issues → Actions → learner PR → capstone workflow on a fresh Windows and Linux environment.
- [ ] Complete security and license approval before a public release.

[Return to the integrated capstone](../capstones/atlas-retail-integrated/README.md) · [Public release gates](PUBLIC_LAUNCH.md).
