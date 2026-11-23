# Atlas Retail — Your First Simulated Employer

Atlas Retail is a fictional regional e-commerce retailer. It sells consumer goods and receives daily order exports from several storefronts. The finance team needs accurate paid revenue, even when ingestion jobs retry after outages.

## Engineering team

- **Business stakeholder:** Finance Ops, who defines the revenue metric and acceptance criteria.
- **Data Engineering:** You, the apprentice engineer responsible for ingestion quality and reliability.
- **Platform Engineering:** Responsible for scheduling, observability and infrastructure.
- **Reviewer:** An AI-assisted or human reviewer who checks tests, reasoning and operational risks.

## System progression

The *same codebase and business requirements* evolve:

| Sprint | Workplace problem | Skill focus |
| --- | --- | --- |
| 1 — RETAIL-001 | Incorrect revenue from duplicate, invalid and cancelled orders | Git, Python, contracts, tests |
| 2 — RETAIL-002 (prototype ready) | An API retry creates duplicate order records | SQL constraints, idempotency, transactions |
| 3 — RETAIL-003 (prototype) | ETL passes but yesterday's report is stale | monitoring, freshness SLOs, on-call response |
| 4 — RETAIL-004 (planned) | Source feed no longer fits on one worker | Spark plans, shuffle, partitions |
| 5 — RETAIL-005 (planned) | Event consumer replays and doubles downstream effects | Kafka offset semantics, dedup |

Later changes will **build upon existing decisions**, teaching ownership and maintenance instead of isolated toy exercises.

**A second concrete Cloud track prototype is available:** [CLOUD-001](../../missions/cloud-001/README.md), addressing HTTP outage retries, followed by [CLOUD-002](../../missions/cloud-002/README.md), protecting artifact integrity.
The [local end-to-end reference data platform](../../capstones/atlas-retail-platform/README.md) links these operational concerns into an actual system. Both tracks still require deeper advanced missions before public launch.

## What counts as success

Explain how a record moves through the system; reproduce a failure; implement a safe fix; verify with tests; and present an operational explanation in the PR. We deliberately avoid artificial time pressure in the beginner stage.

All events, customers and currencies in this fictional company are synthetic. No real financial data is used.
