# Public Engineering Apprenticeship — Curriculum Architecture

**Status: course-design roadmap, not a claim these missions are all built.**
The founder is constructing a reusable academy. Learner assignments begin after the v1 release gate.

## Learning philosophy

The unit of learning is a professional incident or engineering change request. Theory is introduced as an explanation for an observable failure, followed by design work, implementation, tests, an operational drill and a peer-style PR review.

A company codebase evolves; earlier schema, deployment and reliability decisions have downstream effects. A new challenge revisits previously learned concepts under higher constraints. Being able to debug, reason and recover matters more than simply passing tests.

## GitHub skills are mandatory, not a side lesson

- GH-001 — Clone, remote, status, diff, commits and readable history
- GH-002 — Isolated branches and pull requests between branches in a fork
- GH-003 — Interpret CI logs, fix failing checks, submit updated code
- GH-004 — Code review, architecture decision records and merge conflicts
- GH-005 — Release tags, semver, changelog, milestones and incident retrospectives

A learner gains this experience naturally while delivering each mission. The first mission deliberately includes Git and GitHub onboarding.

## Track A: Data Engineering

| Level | Real engineering challenge | Core mechanisms | Current status |
| --- | --- | --- | --- |
| Trainee | Deduplicate dirty retail feed | Python types, exact money, validation | RETAIL-001 prototype |
| Junior | Prevent duplicate payment after API retry | SQL ACID, constraints, idempotency | RETAIL-002 prototype |
| Junior | Green ETL publishes stale business data | Watermarks, freshness SLOs, on-call | RETAIL-003 prototype |
| Junior | Restore a broken warehouse SQL query | OLTP/OLAP, modeling, indexes, execution plan | Planned |
| Engineer | Data pipeline fails during Airflow retry | DAGs, scheduling, backfill, retries | DATA-006 prototype; real local scheduler-managed backfill passed (limited synthetic scope) |
| Engineer | Spark job runs slowly under skew | Shuffle, partitioning, physical plans | DATA-004 prototype; live Spark correctness and measured skew comparison |
| Engineer | Kafka replay produces duplicate side effect | Consumer offsets, transactions, inbox/outbox | DATA-005 prototype; local broker smoke checked in maintainer CI |
| Senior simulation | Lakehouse table evolves and CDC consumer breaks | Schema evolution, Iceberg/Delta, data contracts | Planned |

## Track B: Cloud Engineering

| Level | Real engineering challenge | Core mechanisms | Current status |
| --- | --- | --- | --- |
| Trainee | HTTP reporting API returns 503 | TCP/HTTP, bounded retries, timeout budgets | CLOUD-001 prototype |
| Junior | Object artifact overwritten or corrupted | Object keys, checksum, immutability | CLOUD-002 prototype |
| Junior | Container cannot reach ledger service | Docker networks, DNS, port binding, firewall | CLOUD-003 prototype, real Docker validation pending |
| Engineer | Terraform drift compromises a protected service | Terraform plan JSON, destructive plans, drift | CLOUD-004 prototype, real Terraform plan check pending |
| Engineer | Reporting service receives excessive S3 permissions | Least privilege, resource ARNs, IAM conditions | CLOUD-005 prototype, local policy contract pending verification |
| Engineer | Kubernetes rollout fails readiness | Probes, Services, rolling updates, rollback | Planned |
| Engineer | AZ outage exposes a single point of failure | RTO/RPO, multi-AZ, backup/restore | Planned |
| Engineer | Cloud bill increases unexpectedly | FinOps, storage lifecycle, quotas, monitoring | Planned |
| Senior simulation | Design secure multi-cloud analytics deployment | AWS/GCP/Azure comparison, IaC, observability | Planned |

## Integrated capstones

**Working local reference:** [Atlas Retail Data Product](../capstones/atlas-retail-platform/README.md) — CSV input to SQLite, quality checks, Gold revenue, immutable checksummed release, freshness monitor, and localhost API. Its tests exercise actual SQLite and HTTP, not cloud deployment.

**Learner capstone to build:** extend and maintain this service across multiple incident tickets, including bad-source backfills, monitoring, historical data correction, idempotent upload, cloud architecture review and disaster recovery. The learner must demonstrate an independent solution in their own fork with test evidence and a design review.

**Advanced capstone planned:** event-driven retail lakehouse using PostgreSQL, Kafka, Spark, object storage, Airflow, warehouse queries, Docker-based CI and optional AWS/GCP/Azure deployments. Never mark as verified until the full distributed stack has actually run.

## Evidence rubric

Every submitted change should include four separate areas:

1. Explain — understand the data flow and failure mechanism.
2. Build — implement a reproducible, tested change.
3. Recover — recreate the failure, demonstrate mitigation and rollback.
4. Defend — reason about consistency, security, cost and alternatives.

The scoring scale is 0–4 each, with CI as one necessary but incomplete source of evidence. Claims that a learner is job-ready require stronger independent assessment.

## Public-readiness milestones

- P0: First complete learner journey, safe fork workflow, reference test verification.
- P1: Breadth of core missions in both tracks and two independent company scenarios.
- P2: One truly learner-deliverable end-to-end capstone and operational review.
- P3: Live Kafka/Spark/Airflow/container validation, then optional controlled cloud drills.
- P4: Independent onboarding study, documentation, licensing and release.

Do not add a website just to imitate other online academies. GitHub is the primary learner interface; minimal local developer tooling supports it.
