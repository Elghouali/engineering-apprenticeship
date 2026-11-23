# Documentation Hub

[← Academy home](../README.md) · [Mission directory](../missions/README.md) · [Local capstone](../capstones/atlas-retail-platform/README.md)

> **Pre-release documentation.** Some pages describe the intended public learner workflow and requirements that have not yet been independently tested. Refer to the [launch checklist](PUBLIC_LAUNCH.md) for authoritative maturity status.

## For future learners

| Guide | What you will learn |
| --- | --- |
| [Learner Guide](LEARNER_GUIDE.md) | Fork safely, create branches, run starter/contract tests, push and review |
| [GitHub Field Guide](GITHUB_WORKFLOW.md) | Git remotes, commits, CI failures, PR bases, review, conflicts |
| [Engineering Loop](ENGINEERING_LOOP.md) | Incident-to-PR workflow and Explain / Build / Recover / Defend rubric |
| [Mission Directory](../missions/README.md) | All 12 prototype incidents and their prerequisites |
| [Atlas Retail](../companies/atlas-retail/README.md) | Fictional company and evolving engineering context |

## For maintainers and contributors

| Guide | Purpose |
| --- | --- |
| [Maintainer Handbook](MAINTAINER_GUIDE.md) | Mission authoring, quality standards, public/private boundaries |
| [Mission Versioning](MISSION_VERSIONING.md) | Stable contract IDs, releases and breaking changes |
| [Public Curriculum](PUBLIC_CURRICULUM.md) | Planned Data/Cloud growth and integrated capstone |
| [Next Missions](NEXT_MISSIONS.md) | Proposed future work and staged prototypes |
| [Independent Onboarding Test Plan](ONBOARDING_TEST_PLAN.md) | Repeatable fresh-fork launch acceptance |
| [Public Launch Gate](PUBLIC_LAUNCH.md) | Checklist of verified and still-blocking work |
| [Licensing Decision](LICENSING_DECISION.md) | Owner approval required before redistribution |

## Real CI evidence, with honest limits

| Evidence | What was checked |
| --- | --- |
| [Spark Benchmark](SPARK_BENCHMARK_EVIDENCE.md) | Small local skew workload and controlled salting comparison |
| [Airflow Backfill](AIRFLOW_BACKFILL_EVIDENCE.md) | Two historical dates scheduled and published by local Airflow |
| [Cloud Sprint](CLOUD_SPRINT_EVIDENCE.md) | Local Docker, provider-free Terraform and disposable Kubernetes |
| [Kafka Mission](../missions/data-005/README.md) | Local single-node broker crash/replay test described; not a production cluster |

All tests use synthetic data. Private reference source code is **not** distributed here, and there is no claim that a beginner-to-capstone course is complete.
