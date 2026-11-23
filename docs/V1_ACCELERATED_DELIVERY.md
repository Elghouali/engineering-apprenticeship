# Academy v1.0 — Accelerated integrated delivery plan

**Status:** implementation batches, not a launch claim. **Last verified integration:** [seven green jobs on 2026-11-23](https://github.com/Elghouali/engineering-apprenticeship/actions/runs/45243392488).

## Release principle

Optimize for a **complete, safe, independent learner experience**, not an ever-expanding curriculum or a production SLA. Build across related files/issues in coherent PR-sized batches; verify all gates with CI and an independent human acceptance pass. The founder does not need to solve learner missions.

### Batch A — Integrated platform (engineering)

**Already verified:** Kafka→PostgreSQL→S3 replay-safe data flow, direct Spark JDBC on 2,403 rows, Airflow scheduled two-day backfill, Kind reporting API→PostgreSQL/S3 readiness and rollback.

**Still needed:** reproducible Spark larger-volume benchmark (data sizes, partition counts, skew, timings, physical plans), Spark source consistency under concurrent writes, worker/scheduler failure injection, observable metrics and security hardening. Full Kafka-on-Kind is **not** required for a local-first v1 if clearly labeled as an advanced future extension; the **real integrated Compose capstone plus Kind reporting slice** can be the supported v1 target if acceptance is proven.

**Acceptance:** a fresh maintainer checkout runs all relevant CI jobs; no unsafe claims about production scale; runbooks and limitations are accurate. Any untested advanced distributed extension remains clearly marked v1.x backlog.

### Batch B — Learner-owned experience (critical release blocker)

Implement and test a coherent chain of five incident tickets with **starter state that fails for a reason**, clear contracts, no private answer leakage, expected evidence and automated grading:

1. CAPSTONE-001: reproduce broken Gold or reporting behavior, document diagnosis.
2. CAPSTONE-002: recover Kafka crash after durable DB commit without revenue duplication.
3. CAPSTONE-003: implement and measure Spark aggregation, prove financial parity.
4. CAPSTONE-004: run bounded logical-date Airflow backfills, prove replay safety.
5. CAPSTONE-005: deploy and roll back a broken reporting API image in disposable Kind.

**Important:** the maintained reference platform passing tests does *not* prove that a beginner can solve a starter assignment. Public starter/fault injection must be isolated from confidential correct solutions. Never commit answer patches or private grader assertions to the public repository.

**Acceptance:** a reviewer unfamiliar with the repo completes one full learner fork→issue→branch→PR→CI→feedback→capstone cycle without maintainer intervention; independent Windows and Linux environment validation; a real review example with reasoning and no answer leakage.

### Batch C — Documentation, security and community

- Complete a beginner→intermediate→capstone navigation graph with prerequisites and honest skill coverage; prioritize complete paths over promising exhaustive Big Data/Cloud specialization.
- Automated docs/link checks, accessible diagrams, mission failure/cleanup guides, reproducible local prerequisites.
- Review all GitHub Actions permissions, pinned third-party actions and dependency provenance.
- Founder chooses license grants (code vs educational content), configures protected main and private vulnerability reporting, and approves final brand.
- Produce version policy, release notes and public maintenance expectations.

**Acceptance:** documented sign-off checklist with evidence links; no hidden permission assumptions.

### Batch D — Release and founder launch (approval required)

- All mandatory gates in [PUBLIC_LAUNCH.md](PUBLIC_LAUNCH.md) pass.
- Draft PR reviewed and merged; versioned v1.0 tag and changelog created; release link and onboarding instructions validated from main.
- Founder approves final name and social copy **after** release validation.
- Only then publish the held LinkedIn founder announcement.

## Practical sequencing and batching

- **Batch A and C** can be developed concurrently with **Batch B**.
- Batch B is the primary critical path and must not be deferred in favor of increasingly complex infrastructure.
- Every batch should commit a runnable vertical slice, add failing-then-passing acceptance tests, and include operational docs.
- **Do not merge PR #2** solely because CI is green; the independent learner journey, licensing and security gates still apply.
- **Do not advertise v1.0** or publish LinkedIn launch copy before founder approval.

## Scope discipline

**v1 required:** practical GitHub-native missions; validated starter/grader separation; reproducible local Data + Cloud capstone; clear pathways; safe CI and license; independent beginner onboarding.

**v1.x backlog candidates:** fully distributed Spark clusters, multicloud failover, hosted labs, enterprise observability, advanced SQL curriculum expansion, automated certificates, broad multi-region deployment. These should not indefinitely block a useful v1 if documented as out of scope and approved by the founder.

**Open work tracking:** [public release issue #3](https://github.com/Elghouali/engineering-apprenticeship/issues/3), [integrated capstone issue #12](https://github.com/Elghouali/engineering-apprenticeship/issues/12), [draft PR #2](https://github.com/Elghouali/engineering-apprenticeship/pull/2).
