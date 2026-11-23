# Mission Roadmap — One Evolving Engineering Career

This is a **proposal**, not a claim that the following missions already have working implementations.

| Priority | Mission | Real engineering ticket | Planned lab |
| --- | --- | --- | --- |
| P0 | RETAIL-001 | Correct bad revenue under duplicate order ingestion | Python, data contracts, tests, GitHub PR |
| P0 | RETAIL-002 (prototype ready) | Make invoice creation idempotent under retries | SQLite, constraints, transactions |
| P0 | RETAIL-003 (prototype) | Detect stale reports despite green jobs | metrics, freshness and runbooks |
| P2 | RETAIL-004 | Tune a Spark job with data skew | PySpark, partitioning, explain plans |
| P2 | RETAIL-005 | Recover a Kafka consumer without double effects | Kafka, offsets, SQLite inbox |
| P0 | CLOUD-001 (prototype ready) | Diagnose 503 and implement safe bounded retries | HTTP, failures, client backoff |
| P0 | CLOUD-002 (prototype) | Prevent silent artifact modification | object storage, safe keys and SHA-256 |
| P3 | CLOUD-003 | Reproduce infrastructure and test backup recovery | Terraform, IAM, RTO/RPO |
| P3 | DATA-PLATFORM-001 | Deliver a secure analytical data platform | Kafka, Spark, object store, orchestration, CI/CD |

**Expansion rule:** introduce new companies or separate repositories only when they create a new realistic engineering context, independent deployment lifecycle, or substantial complexity. Reuse the existing [BigData Academy](https://github.com/Elghouali/BigData/tree/feature/academy-data-cloud-from-zero/academy) projects, but require the learner to rebuild the solution, not copy it.

The longer-term aspiration is adaptive missions, human or AI-assisted code reviews, progressively evolving incidents and verified professional evidence. These are staged features, not shipped features.

## Advanced Data Engineering sprint (prototype work)

- [DATA-004](../missions/data-004/README.md): skew investigation and replay-safe Spark aggregation; a [measured local comparison](SPARK_BENCHMARK_EVIDENCE.md) is published; larger independent benchmarks still pending.
- [DATA-005](../missions/data-005/README.md): durable inbox and ledger processing with simulated crash and a real single-node Kafka smoke test validated in maintainer CI.
- [DATA-006](../missions/data-006/README.md): real Airflow DAG tasks executed for two historical dates, with a published Docker Compose learner harness; controlled scheduler-managed backfill passed in maintainer CI; multi-worker deployment is unverified.

All prototypes must pass private maintainer reference validation and receive an independent learner test before being marked ready.

## Cloud Engineering sprint (pre-release prototypes)

- [CLOUD-003](../missions/cloud-003/README.md): a real two-service Docker Compose API cannot reach its private ledger; fix DNS, networking and host exposure.
- [CLOUD-004](../missions/cloud-004/README.md): fail-closed Terraform plan review for replacement, public SSH and unmanaged drift, using provider-free real plan generation.
- [CLOUD-005](../missions/cloud-005/README.md): implement a prefix-scoped AWS S3 IAM identity policy without broad object permissions.

These remain prototype until private correct-solution validation and real runtime evidence pass. Cloud security examples do not substitute for full provider IAM evaluation or real account policies.
