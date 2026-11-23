# Mission Directory — Choose Your Engineering Incident

[← Academy home](../README.md) · [Learner Guide](../docs/LEARNER_GUIDE.md) · [GitHub workflow](../docs/GITHUB_WORKFLOW.md) · [Curriculum roadmap](../docs/PUBLIC_CURRICULUM.md)

> **Pre-release:** All 12 missions are documented **prototypes** and not yet cleared for general learner enrollment. The currently published contract is version 1 for each mission. The academy will not call them ready until an independent learner walkthrough passes.

## How to read this directory

Every mission simulates a real workplace change request. Click the incident, understand the business impact, read the public contract, create a personal branch **in your own fork**, copy a faulty starter, reproduce its failure, repair the implementation, rerun tests, and explain the change in a pull request. Graders are deliberately public; correct reference solutions are kept private.

Start with **RETAIL-001** for Data Engineering or **CLOUD-001** for Cloud Engineering. You may work through both tracks, but honor prerequisite missions. A mission tests one engineering failure; do not assume all missions already run in a single deployed system.

## Track A — Data Engineering

| Stage | Mission | Scenario | Prerequisites |
| --- | --- | --- | --- |
| 1 | [RETAIL-001](retail-001/README.md) | Correct wrong revenue after ETL retry | None |
| 2 | [RETAIL-002](retail-002/README.md) | Prevent duplicate payment writes | RETAIL-001 |
| 3 | [RETAIL-003](retail-003/README.md) | Detect stale source data despite green job | RETAIL-001, RETAIL-002 |
| 4 | [DATA-004](data-004/README.md) | Diagnose skew and replay in Spark | RETAIL-003 |
| 5 | [DATA-005](data-005/README.md) | Kafka consumer crash before offset acknowledgement | RETAIL-002 |
| 6 | [DATA-006](data-006/README.md) | Airflow retry and historical backfill | RETAIL-003, DATA-004, DATA-005 |

## Track B — Cloud Engineering

| Stage | Mission | Scenario | Prerequisites |
| --- | --- | --- | --- |
| 1 | [CLOUD-001](cloud-001/README.md) | Safe HTTP retries during outages | None |
| 2 | [CLOUD-002](cloud-002/README.md) | Detect overwritten object artifacts | CLOUD-001 |
| 3 | [CLOUD-003](cloud-003/README.md) | Fix Docker DNS and host exposure | CLOUD-001 |
| 4 | [CLOUD-004](cloud-004/README.md) | Review destructive Terraform plan and drift | CLOUD-002, CLOUD-003 |
| 5 | [CLOUD-005](cloud-005/README.md) | Restrict S3 policy to one prefix | CLOUD-002, CLOUD-004 |
| 6 | [CLOUD-006](cloud-006/README.md) | Recover Kubernetes readiness and rollout | CLOUD-003, CLOUD-004 |

The machine-readable source of truth is [catalog.json](catalog.json) and the [skills dependency graph](../skills/graph.json). These tables summarize the current graph but should not override its contract definitions.

## Standard mission procedure (for learners after release)

From the root of **your own fork**, on a personal mission branch:

~~~bash
git switch -c mission/retail-001
python tools/apprentice.py start retail-001
python tools/apprentice.py check retail-001
~~~

Replace the mission ID with another listed above. The initial failure is expected. Modify only your copy in \`submissions/\`; leave official starters and graders intact. You can inspect your branch's GitHub Actions results after pushing; a PR should target **your own fork's main**, not the upstream project.

The core CLI requires Python 3.11+. Basic contracts run with the standard library; optional advanced live runtimes include Spark, a local Kafka Docker broker, Airflow 3, Terraform and Kubernetes kind. Consult individual mission instructions to decide which are required or opt-in.

## What evidence should a PR include?

- **Explain:** What broke, what business invariant was violated, and what mechanism caused it?
- **Build:** Which tests failed before and passed after your change?
- **Recover:** Can you reproduce the incident and safely roll back or replay?
- **Defend:** What trade-offs, operational risks, cost or security issues remain?

Passing tests alone does not constitute a certificate. See the [review rubric](../docs/ENGINEERING_LOOP.md) and [mentor hint policy](../mentor/REVIEW_POLICY.md).

## After the individual missions

The [local reference capstone](../capstones/atlas-retail-platform/README.md) is a maintained sample system, **not yet a complete learner-assigned distributed capstone**. The planned cumulative project and official public launch criteria are in the [roadmap](../docs/PUBLIC_CURRICULUM.md) and [release gate](../docs/PUBLIC_LAUNCH.md).
