# End-to-End Engineering Projects

[← Academy home](../README.md) · [Mission directory](../missions/README.md) · [Public roadmap](../docs/PUBLIC_CURRICULUM.md)

The capstone goal is to **maintain a real system under evolving GitHub Issues**, not to complete a disconnected collection of scripts. Each change should build upon previous decisions and include architecture, testing, observability and recovery evidence.

## Currently implemented

**[Atlas Retail Data Product](atlas-retail-platform/README.md)** — working local reference: synthetic order CSV → validation and deduplication → SQLite → paid revenue and rejection outputs → checksummed release manifest → freshness monitoring → localhost reporting API. It has real integration tests and an operator runbook. Python 3.11+ and no cloud account required.

**[Atlas Retail Integrated Platform](atlas-retail-integrated/README.md)** — first connected implementation of real Kafka event ingestion, PostgreSQL durable event storage, S3-compatible published reporting and a loopback HTTP API. This is a **pre-release vertical slice**, with [incident backlog](atlas-retail-integrated/tickets/CAPSTONE-001.md), a disposable Docker Compose stack and a real integration smoke workflow. **Real PySpark computation and Airflow 3 task execution now run against this same platform** and passed GitHub CI, with precise limits in the [integrated evidence report](../docs/INTEGRATED_CAPSTONE_EVIDENCE.md). Kubernetes is still **not** deployed against it.

The existing SQLite example remains a **maintainer reference and integration test target**, not yet a finalized learner assignment. It remains a simpler standalone SQLite reference, distinct from the verified integrated Kafka/PostgreSQL/S3/Spark/Airflow teaching stack; neither is a fully resilient production Kubernetes deployment.

## Planned learner-owned capstone

An incident backlog will progressively extend the Atlas Retail system to ingestion and event replay, PostgreSQL, Kafka, Spark, Airflow, object storage, analytics and local deployment. Each change will be delivered from a GitHub Issue through a personal learner branch and reviewed PR; the same workspace will accumulate tests, runbooks and recovery decisions.

**Not yet delivered or independently verified:** full distributed-scale and Kubernetes integration, incident-based learner acceptance tests, production-style security, multi-cloud deployment and successful novice onboarding. See [launch gates](../docs/PUBLIC_LAUNCH.md).

No new repository is required for the existing capstone planning and content. All data must be synthetic and local practice should avoid unnecessary cloud costs.
