# Atlas Retail — The Fictional Company Behind Your Missions

[← Academy home](../../README.md) · [Mission directory](../../missions/README.md) · [Local reference platform](../../capstones/atlas-retail-platform/README.md)

> **Fictional training organization.** Atlas Retail has no real customer information, production infrastructure or financial accounts in this repository. The incidents are constructed to resemble professional engineering work while remaining safe to reproduce locally. The academy is still in **pre-release**.

## The business

Atlas Retail is a regional e-commerce company. Multiple storefronts send order exports and transaction events to the reporting team. Finance needs reliable paid revenue, operations needs timely dashboards, and engineering needs fault-tolerant data movement and secure infrastructure.

A typical question from the Head of Finance sounds simple:

> "Why did yesterday's report double after the pipeline retried, and how can we guarantee the correction does not create a new incident?"

The answer is never just a line of code: you must protect money calculations, handle duplicate deliveries, verify freshness, test failure recovery and communicate what you changed.

## Your simulated engineering organization

| Role | What they own | What they ask of you |
| --- | --- | --- |
| Finance Operations | Definition and approval of revenue metrics | Precise paid totals, rejected-row explanations |
| Data Engineer | Ingestion, transformations and quality | Replay-safe, validated, testable pipelines |
| Streaming Engineer | Event deliveries and consumer reliability | Correct offset handling, no double effects |
| Platform Engineer | Orchestration, deployment and uptime | Safe backfills, service discovery and recovery |
| Cloud/Security Engineer | Infrastructure change and access | Least privilege, risk review, rollback readiness |
| Reviewer / incident commander | Engineering quality and business impact | Before/after evidence and operational reasoning |

The learner assumes an engineering role for each ticket. A reviewer may be a human or an AI-assisted process, but **an automated passing grade is not professional certification**.

## How the story evolves

The mission set represents **one evolving company and its engineering responsibilities**. Today each learning exercise has a separate starter and contract, and the [local data-product reference](../../capstones/atlas-retail-platform/README.md) is a real but narrower executable system. The **full unified distributed capstone is planned**, not already deployed.

### Data Engineering incident sequence

| Stage | Ticket | What the company learns |
| --- | --- | --- |
| 1 | [RETAIL-001](../../missions/retail-001/README.md) | Raw records and retries are not trustworthy |
| 2 | [RETAIL-002](../../missions/retail-002/README.md) | SQL state must be idempotent under request retries |
| 3 | [RETAIL-003](../../missions/retail-003/README.md) | A successful job can still publish stale business data |
| 4 | [DATA-004](../../missions/data-004/README.md) | Large workloads reveal skew and replay trade-offs |
| 5 | [DATA-005](../../missions/data-005/README.md) | Broker acknowledgements and durable writes are different |
| 6 | [DATA-006](../../missions/data-006/README.md) | Backfills and DAG retries must be partition-scoped |

### Cloud and Platform incident sequence

| Stage | Ticket | What the company learns |
| --- | --- | --- |
| 1 | [CLOUD-001](../../missions/cloud-001/README.md) | HTTP errors require safe bounded retries |
| 2 | [CLOUD-002](../../missions/cloud-002/README.md) | Artifact integrity needs checksums and conflict handling |
| 3 | [CLOUD-003](../../missions/cloud-003/README.md) | Container localhost is not another service's address |
| 4 | [CLOUD-004](../../missions/cloud-004/README.md) | Terraform changes need plan review and drift awareness |
| 5 | [CLOUD-005](../../missions/cloud-005/README.md) | Storage identities should have minimum possible permissions |
| 6 | [CLOUD-006](../../missions/cloud-006/README.md) | A deployed Pod is not necessarily a Ready service |

Read the [mission catalog](../../missions/catalog.json) for the exact dependency graph: some missions can run in parallel; their table positions are not a forced linear syllabus.

## Data and business contracts

The starter data is **synthetic**. Different incidents deliberately use different schemas (orders vs payment events vs Kafka wallet changes). Do not assume all datasets use the same IDs, currency units or timestamps.

In the local reference data product, financial amounts are represented as **integer cents**, the business date is an ISO date, cancelled orders contribute no *paid* revenue, and exact duplicates never increase totals. A conflicting duplicate is an incident, not an excuse to silently choose a convenient row.

## What a professional delivery looks like

1. Link a business-facing GitHub Issue and reproduce the observed failure.
2. Identify the invariant and explain the likely mechanism.
3. Implement the smallest safe fix with regression tests.
4. Demonstrate how the system behaves after an intentional retry or failure.
5. Open a PR **in the learner's own fork**, discuss alternatives, and supply a short runbook or decision note.

See the [engineering review rubric](../../docs/ENGINEERING_LOOP.md), [GitHub field guide](../../docs/GITHUB_WORKFLOW.md) and [operator runbook](../../capstones/atlas-retail-platform/RUNBOOK.md).

**Project state:** The company story and 12 mission prototypes exist; an integrated learner-owned data/streaming/cloud platform and independent public onboarding remain [release blockers](../../docs/PUBLIC_LAUNCH.md).
