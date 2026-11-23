# End-to-End Engineering Projects

[← Academy home](../README.md) · [Mission directory](../missions/README.md) · [Public roadmap](../docs/PUBLIC_CURRICULUM.md)

The capstone goal is to **maintain a real system under evolving GitHub Issues**, not to complete a disconnected collection of scripts. Each change should build upon previous decisions and include architecture, testing, observability and recovery evidence.

## Currently implemented

**[Atlas Retail Data Product](atlas-retail-platform/README.md)** — working local reference: synthetic order CSV → validation and deduplication → SQLite → paid revenue and rejection outputs → checksummed release manifest → freshness monitoring → localhost reporting API. It has real integration tests and an operator runbook. Python 3.11+ and no cloud account required.

This is a **maintainer reference and integration test target**, not yet a finalized learner assignment. It does not currently run an integrated Spark + Kafka + Airflow + Kubernetes production-style data platform.

## Planned learner-owned capstone

An incident backlog will progressively extend the Atlas Retail system to ingestion and event replay, PostgreSQL, Kafka, Spark, Airflow, object storage, analytics and local deployment. Each change will be delivered from a GitHub Issue through a personal learner branch and reviewed PR; the same workspace will accumulate tests, runbooks and recovery decisions.

**Not yet delivered or independently verified:** full integrated stack, learner-assigned issue sequence, production-style security, multi-cloud deployment and successful novice onboarding. See [launch gates](../docs/PUBLIC_LAUNCH.md).

No new repository is required for the existing capstone planning and content. All data must be synthetic and local practice should avoid unnecessary cloud costs.
