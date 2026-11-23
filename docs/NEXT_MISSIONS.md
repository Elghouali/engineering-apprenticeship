# Mission Roadmap — One Evolving Engineering Career

This is a **proposal**, not a claim that the following missions already have working implementations.

| Priority | Mission | Real engineering ticket | Planned lab |
| --- | --- | --- | --- |
| P0 | RETAIL-001 | Correct bad revenue under duplicate order ingestion | Python, data contracts, tests, GitHub PR |
| P1 | RETAIL-002 | Make invoice creation idempotent under retries | SQLite/PostgreSQL, transactions |
| P1 | RETAIL-003 | Detect stale reports despite green jobs | metrics, freshness and runbooks |
| P2 | RETAIL-004 | Tune a Spark job with data skew | PySpark, partitioning, explain plans |
| P2 | RETAIL-005 | Recover a Kafka consumer without double effects | Kafka, offsets, SQLite inbox |
| P2 | CLOUD-001 | Repair private-network access and health checks | HTTP/TCP, Docker networking, VPC principles |
| P3 | CLOUD-002 | Reproduce infrastructure and test backup recovery | Terraform, IAM, RTO/RPO |
| P3 | DATA-PLATFORM-001 | Deliver a secure analytical data platform | Kafka, Spark, object store, orchestration, CI/CD |

**Expansion rule:** introduce new companies or separate repositories only when they create a new realistic engineering context, independent deployment lifecycle, or substantial complexity. Reuse the existing [BigData Academy](https://github.com/Elghouali/BigData/tree/feature/academy-data-cloud-from-zero/academy) projects, but require the learner to rebuild the solution, not copy it.

The longer-term aspiration is adaptive missions, human or AI-assisted code reviews, progressively evolving incidents and verified professional evidence. These are staged features, not shipped features.
