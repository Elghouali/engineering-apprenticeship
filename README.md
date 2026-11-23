# Engineering Apprenticeship

**Learn Big Data & Cloud Engineering by doing the work on GitHub.**

> **PUBLIC PRE-RELEASE — not ready for learners or a v1 announcement.** This repository is visible while the curriculum is being built. All 12 missions are **prototypes**, and an independent beginner-to-capstone learner journey has **not** been verified. [Track the release gates](docs/PUBLIC_LAUNCH.md). **A public repository is not automatically open-source licensed**; redistribution terms are [awaiting owner approval](docs/LICENSING_DECISION.md).

Engineering Apprenticeship is an emerging **GitHub-native, issue-driven engineering school**. You don't watch a generic course and submit a quiz. You join a fictional engineering team, investigate a business incident, learn only the necessary concepts, ship a fix on a branch, interpret CI failures, defend the design in a pull request, and recover from operational failures.

There is **no separate web academy**. GitHub is the learning interface: Issues, branches, commits, PRs, Actions, reviews, project history and eventually releases. The approach is **learning by maintaining a changing system**, not copying completed tutorials.

## Start here

| I'm here to… | Where to go |
| --- | --- |
| Understand the idea in 2 minutes | [How the engineering loop works](docs/ENGINEERING_LOOP.md) |
| Find my first challenge | [RETAIL-001](missions/retail-001/README.md) for Data; [CLOUD-001](missions/cloud-001/README.md) for Cloud |
| See the entire mission progression | [Mission directory](missions/README.md) and [skills graph](skills/graph.json) |
| Learn Git and GitHub through the tasks | [GitHub Field Guide](docs/GITHUB_WORKFLOW.md) |
| Learn how to use a personal fork | [Learner Guide](docs/LEARNER_GUIDE.md) — for use after launch |
| Understand our fictional employer | [Atlas Retail](companies/atlas-retail/README.md) |
| Inspect a running reference system | [Local data-product capstone](capstones/atlas-retail-platform/README.md) |
| Improve the academy itself | [Contributing](CONTRIBUTING.md) and [Maintainer Handbook](docs/MAINTAINER_GUIDE.md) |
| Check what is actually finished | [Public launch checklist](docs/PUBLIC_LAUNCH.md) and [evidence library](docs/README.md) |

## The method: a professional engineering loop

~~~mermaid
flowchart LR
  I["Fictional company incident"] --> B["GitHub Issue + acceptance contract"]
  B --> F["Personal fork and mission branch"]
  F --> R["Reproduce the fault"]
  R --> L["Investigate and learn"]
  L --> X["Implement + test"]
  X --> C{"GitHub Actions"}
  C -->|"Failure"| R
  C -->|"Checks pass"| P["Explain, review, recover in a PR"]
  P --> N["Next incident in the same company"]
~~~

A green check **does not mean professional certification**. The learner must explain the root cause, demonstrate before/after behavior, handle realistic failure modes, and discuss trade-offs. We assess work through **Explain → Build → Recover → Defend**, not the number of videos consumed.

### A connected company, not unrelated tutorials

Our first employer is **[Atlas Retail](companies/atlas-retail/README.md)**, a fictional retailer whose finance and engineering teams depend on reliable data. In early tickets you fix duplicated orders. Later incidents involve SQL transactions, stale dashboards, Spark skew, Kafka replay, Airflow backfills, Docker networking, infrastructure review and Kubernetes rollouts. Some missions are independent exercises sharing business context; a full learner-owned integrated platform is **still under development**.

## Curriculum: 12 working prototypes

The paths below are the **intended order based on prerequisites**, not a promise that every lab is equally easy or production-ready. Read each mission's full contract before beginning.

### Data Engineering

| Mission | Business problem | Technology | Prerequisites |
| --- | --- | --- | --- |
| [RETAIL-001](missions/retail-001/README.md) | Duplicate and invalid orders corrupt revenue | Git, Python, testing, exact money | None |
| [RETAIL-002](missions/retail-002/README.md) | A retry charges the same payment twice | SQLite, constraints, ACID | RETAIL-001 |
| [RETAIL-003](missions/retail-003/README.md) | The job is green but reporting is stale | Freshness, data-quality SLIs | RETAIL-001 + 002 |
| [DATA-004](missions/data-004/README.md) | One merchant skews an aggregation | PySpark, shuffle, salting | RETAIL-003 |
| [DATA-005](missions/data-005/README.md) | A consumer crash doubles wallet credit | Kafka offsets, durable inbox | RETAIL-002 |
| [DATA-006](missions/data-006/README.md) | Retry/backfill overwrites the wrong partition | Airflow 3, DAGs, recovery | RETAIL-003 + DATA-004 + 005 |

### Cloud Computing and Platform Engineering

| Mission | Business problem | Technology | Prerequisites |
| --- | --- | --- | --- |
| [CLOUD-001](missions/cloud-001/README.md) | Reporting API intermittently returns 503 | HTTP, retries, backoff | None |
| [CLOUD-002](missions/cloud-002/README.md) | Published report was overwritten | SHA-256, object-storage contracts | CLOUD-001 |
| [CLOUD-003](missions/cloud-003/README.md) | API cannot resolve a private ledger | Docker, DNS, bridge network | CLOUD-001 |
| [CLOUD-004](missions/cloud-004/README.md) | Infrastructure plan contains dangerous changes | Terraform, plan JSON, drift | CLOUD-002 + 003 |
| [CLOUD-005](missions/cloud-005/README.md) | Service receives wildcard storage permissions | S3 IAM, least privilege | CLOUD-002 + 004 |
| [CLOUD-006](missions/cloud-006/README.md) | Deployment has no Ready endpoints | Kubernetes, probes, rollback | CLOUD-003 + 004 |

**Maturity:** All 12 are marked \`prototype\` in the [machine-readable catalog](missions/catalog.json). Correct private references have passed the public contracts, and selected real local runtime integrations were validated. This does **not** replace independent learner testing. Advanced SQL/warehouse work, multi-cloud resilience and the full learner-assigned capstone are still planned in the [curriculum roadmap](docs/PUBLIC_CURRICULUM.md).

## Preview the learner workflow (do not submit homework upstream yet)

**Required for basic missions:** free GitHub account, Git, Python **3.11+**, a terminal and an editor. Docker/Java/PySpark/Terraform/Kubernetes tooling is **optional and mission-specific**. A paid cloud account is **not required** for the currently documented local labs.

~~~bash
# After forking the academy on GitHub, clone YOUR own copy.
git clone https://github.com/YOUR-USERNAME/engineering-apprenticeship.git
cd engineering-apprenticeship
git switch -c mission/retail-001

python tools/apprentice.py doctor
python tools/apprentice.py list
python tools/apprentice.py start retail-001
python tools/apprentice.py check retail-001
~~~

The first \`check\` **is expected to fail**: the copied starter deliberately contains the business bug. Correct only \`submissions/retail-001/pipeline.py\`; do not edit the official grader to make it green. The starter command will not overwrite existing work or run on \`main\`.

After correcting the solution in a learner's **own fork**, run checks, commit, push and open a PR **within that fork** (base = the learner's main; compare = the mission branch). Never send homework to the central academy's upstream main. See the [full fork-to-PR procedure](docs/GITHUB_WORKFLOW.md).

**Maintainer check, independent of homework:**

~~~bash
python -m unittest discover -s tests -v
python -m unittest discover -s capstones/atlas-retail-platform/tests -v
python tools/verify_links.py
~~~

On Windows, \`py -3\` may replace \`python\`; in PowerShell use the same Python CLI arguments. Some advanced tests require explicit opt-in environment variables; see the relevant mission README. Running untrusted learner code outside a disposable environment is unsafe.

## Reference platform and verification evidence

The [Atlas Retail local data product](capstones/atlas-retail-platform/README.md) currently implements synthetic CSV ingestion → validation/deduplication → SQLite → Gold revenue → checked release manifests → freshness checks → a **localhost-only HTTP API**. It runs without installing distributed services.

Maintainer-only CI separately tested correct references on Linux and Windows and selected runtime paths: [Spark benchmark](docs/SPARK_BENCHMARK_EVIDENCE.md), [Kafka replay](missions/data-005/README.md), [Airflow scheduler backfill](docs/AIRFLOW_BACKFILL_EVIDENCE.md) and [Docker/Terraform/Kubernetes evidence](docs/CLOUD_SPRINT_EVIDENCE.md). **S3 IAM was structurally tested, not authorized against AWS.** Correct reference implementations are kept in a separate **private** maintainer repository and are never part of public exercises.

This repo is **already public to inspect**, but the educational release has not launched. Public CI and private reference success do not prove that a new learner can finish the academy unaided.

## Open development roadmap

1. **Complete the README and onboarding system**, then test it with real first-time users.
2. Build the **learner-assigned, end-to-end Data + Cloud capstone** connecting ingestion, Kafka, Spark, orchestration, storage, deployment, observability and incident recovery.
3. Expand SQL/warehousing, multi-cloud foundations, production operations and resilient workloads.
4. Run independent Windows/Linux fork → branch → CI → PR acceptance tests.
5. Finalize licenses, repo security and protected-branch rules, conduct a release review and only then tag v1.

See the [active release checklist](docs/PUBLIC_LAUNCH.md), [curriculum plan](docs/PUBLIC_CURRICULUM.md) and [contributor guidance](CONTRIBUTING.md). Please do not treat \`prototype\` as \`ready\` or represent this repository as a finished training product.

## License, community and safety

- **Licenses not granted yet.** Code MIT and educational text CC BY 4.0 have been proposed, but must be approved by the owner before redistribution.
- **Synthetic data only.** No real financial records, production credentials, mandatory paid services or automatic cloud provisioning.
- **Security:** [Security policy](SECURITY.md); [code of conduct](CODE_OF_CONDUCT.md); [contributing guidelines](CONTRIBUTING.md).
- **Trust boundaries:** Public learner code runs in personal forks, never in a privileged maintainer job. Green tests measure contract behavior, not human competence.

**Current state: public source, private answer validation, pre-release curriculum.**
