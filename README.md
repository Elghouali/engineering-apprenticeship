# Engineering Apprenticeship — Learn Engineering by Shipping on GitHub

> **PRE-RELEASE: Building for public learners. Not yet a complete academy.** This public repository is under active development. See [Public Launch Gate](docs/PUBLIC_LAUNCH.md) before recommending it as a finished training product.

Our goal is an open-source, **GitHub-native Big Data and Cloud Engineering apprenticeship**. No course website. Learners become engineers by receiving realistic tickets, investigating intentionally broken code, fixing it, documenting operational decisions and reviewing pull requests.

**Two audiences:**
- **Public learners (after launch):** [Learner Guide](docs/LEARNER_GUIDE.md) and [GitHub skills field guide](docs/GITHUB_WORKFLOW.md) — fork the repository, work in your own branch, use your own GitHub Actions, keep assignments out of the upstream main branch.
- **Maintainers and contributors:** [Maintainer Guide](docs/MAINTAINER_GUIDE.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Licensing decision](docs/LICENSING_DECISION.md).

## The method: PR-Driven Apprenticeship

~~~mermaid
flowchart LR
  I[Company work ticket] --> F[Personal GitHub fork + branch]
  F --> B[Reproduce real incident]
  B --> L[Learn necessary concepts]
  L --> C[Build + run tests]
  C --> CI[GitHub Actions]
  CI -->|Fail| B
  CI -->|Pass| R[Explain, review and recover]
  R --> N[Next evolving task]
~~~

GitHub itself is the classroom: Issues are work requests, branches are experiments, CI exposes failures, reviews demand reasoning, and accepted projects build a verifiable portfolio. A successful CI run **is not** a certification.

## Available mission prototypes (for maintainer evaluation)

| ID | Company role | Incident | Concepts |
| --- | --- | --- | --- |
| [RETAIL-001](missions/retail-001/README.md) | Trainee Data Engineer | Duplicate/cancelled sales distort revenue | Git, Python, validation, exact money |
| [RETAIL-002](missions/retail-002/README.md) | Junior Data Engineer | Payment API retry creates duplicate row | SQL, transactions, idempotency |
| [CLOUD-001](missions/cloud-001/README.md) | Trainee Cloud Engineer | HTTP 503 interrupts reporting API | HTTP, network errors, bounded retries |
| [RETAIL-003](missions/retail-003/README.md) | On-call Data Engineer | Pipeline green but source data stale | Freshness SLOs, monitoring, incidents |
| [CLOUD-002](missions/cloud-002/README.md) | Junior Cloud Engineer | Published artifact silently overwritten | Object storage, SHA-256, safe keys |
| [DATA-004](missions/data-004/README.md) | Data Engineer | Slow skewed Spark job and replayed transactions | PySpark, shuffle, salting, correctness |
| [DATA-005](missions/data-005/README.md) | Streaming Engineer | Kafka replay after durable ledger commit | Broker offsets, SQLite inbox, idempotency |
| [DATA-006](missions/data-006/README.md) | Platform Engineer | Airflow backfill overwrites daily report | DAGs, retries, partitioned atomic publication |
| [CLOUD-003](missions/cloud-003/README.md) | Cloud Engineer | Reporting API cannot resolve internal ledger | Docker DNS, bridge networks, port exposure |
| [CLOUD-004](missions/cloud-004/README.md) | Cloud Platform Engineer | Dangerous Terraform replacement and drift | Plan JSON, drift, protected resources |
| [CLOUD-005](missions/cloud-005/README.md) | Cloud Security Engineer | Reporting service has wildcard S3 access | IAM, least privilege, object ARN scoping |

Advanced missions include **maintainer-verified real local PySpark aggregation** (DATA-004) and **a real local Kafka broker crash/replay smoke test** (DATA-005), plus a validated Airflow Task SDK DAG structure (DATA-006). A measured Spark comparison and a controlled **real Airflow scheduler-managed historical backfill** have now passed maintainer CI. These validate a local synthetic environment, not production scalability or a public learner rollout. These are still prototypes pending wider public learner acceptance testing.

These starter missions are part of the academy **under construction**. The full progression from foundations through Spark, Kafka, Cloud and capstone delivery has not yet been completed or integration-verified.

## Runnable end-to-end reference system

The [Atlas Retail Data Platform](capstones/atlas-retail-platform/README.md) combines CSV contracts, idempotent processing, SQLite, Gold revenue output, immutable release folders, cryptographic artifact checks and data freshness monitoring. It runs locally without any paid cloud services, and CI executes its integration tests.

This reference is for **maintainer validation and future cumulative incidents**; the learner capstone assignment is still being developed.

## Core developer commands

~~~bash
python tools/apprentice.py doctor
python tools/apprentice.py list
python -m unittest discover -s tests -v
~~~

For learners in **their own fork and personal mission branch**:

~~~bash
python tools/apprentice.py start retail-001
python tools/apprentice.py check retail-001
~~~

The starter is deliberately faulty; initial test failures are expected. The start command refuses to overwrite submissions and will not run on main.

## Existing resources

- [Big Data & Cloud Academy technical references](https://github.com/Elghouali/BigData/tree/feature/academy-data-cloud-from-zero/academy)
- [Skills and prerequisites](skills/graph.json)
- [Mission catalog](missions/catalog.json)
- [Company scenario: Atlas Retail](companies/atlas-retail/README.md)
- [Engineering workflow](docs/ENGINEERING_LOOP.md)
- [Public curriculum roadmap](docs/PUBLIC_CURRICULUM.md) and [mission roadmap](docs/NEXT_MISSIONS.md)
- [AI mentor policy](mentor/REVIEW_POLICY.md) — guidelines only, no bot deployed

## Public release principles

1. No unfinished mission advertised as ready.
2. One end-to-end successful learner journey must be independently validated.
3. Local-only foundation exercises; no mandatory cloud billing.
4. No privileged code execution, data leaks or fake skill certifications.
5. Code and educational-content licenses must be approved before v1 release.

**Current status: product build in progress. Not accepting personal exercise submissions to upstream.**
