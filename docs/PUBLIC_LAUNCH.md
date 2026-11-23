# Public Launch Gate — Engineering Apprenticeship

**Status: PRE-RELEASE / BUILDING. This is not yet a complete public academy.**

Public visibility on GitHub is not the same as launch readiness. The founder builds and maintains the product; the founder is NOT expected to complete learner assignments.

## Definition of v1

A complete public learner journey must work without founder intervention: read a role-specific pathway, fork the academy, diagnose faulty starter code, write an original repair, run tests, see CI feedback, submit a PR to their own fork, and complete an end-to-end portfolio capstone.

## Technical gates

- [x] GitHub-native mission scaffolding, company story and skills graph
- [x] Basic platform tests and least-privilege CI
- [x] Twelve current mission prototype contracts pass correct confidential reference solutions on Ubuntu and Windows
- [x] Live single-node local Kafka replay and local PySpark functional integration verified in maintainer CI
- [x] Airflow 3 Task SDK DAG object/dependency verification in maintainer CI
- [x] Measured Spark physical plan and baseline versus controlled salt=1/salt=8 timings documented, without claiming performance gains
- [x] Real Airflow 3 `dags test` executed extract, validate, publish for two historical dates, including replay, with verified file output
- [x] Airflow 3 standalone scheduler + LocalExecutor created and completed two historical backfill runs; outputs independently verified
- [ ] Independent larger-scale Spark performance experiments and production-like multi-worker Airflow resilience
- [ ] Complete advanced Big Data curriculum including SQL optimization and advanced production operations
- [x] CLOUD-003/004/005 correct references passed; Docker service-to-service DNS and provider-free Terraform plan JSON integration verified on local CI
- [x] CLOUD-006 real local kind: two Ready pods, Service HTTP, deliberately broken image rollout and successful rollback
- [ ] Broader Cloud Engineering, including resilient workloads, multi-AZ and multicloud recovery
- [x] Local end-to-end reference data product: real SQLite, immutable release, replay/tamper/quality failure tests in CI

- [x] Verify Stage 1 integrated Kafka 4.4 broker -> PostgreSQL 16 event inbox -> S3-compatible Gold -> localhost HTTP against actual Docker services; includes a crash before broker acknowledgement, safe replay and 22,000-cent parity
- [x] Verify initial bounded PySpark 4.0.3 bridge against PostgreSQL and S3 (superseded by partitioned JDBC read below)
- [x] Verify an actual Airflow 3 Task SDK DAG executing the SAME Kafka, PostgreSQL and S3 stages, with 5 accepted events and verified 22,000 cents
- [x] Replace the fixed 1,000-event driver snapshot with direct partitioned PostgreSQL JDBC Spark reads; verify 2,403 durable events and immutable report replay in real local CI
- [ ] Prove much larger and multi-worker Spark performance/recovery, integrated historical Airflow scheduler backfills and Kubernetes deployment/recovery
- [ ] Verify newly added integrated Airflow scheduler-managed two-date backfills and protected/replay-safe business partitions in CI (implementation exists; evidence pending)
- [ ] Verify new Kind integration: genuine API->PostgreSQL/S3, readiness, failed image rollout and rollback (implementation exists; CI pending; Kafka remains outside Kind)
- [ ] Build and independently grade learner-authored changes across all five connected capstone GitHub Issues
- [ ] Complete **learner-assigned** end-to-end Data/Cloud project, independently validated on a clean checkout with operations runbook
- [x] Platform integrity, local SQLite/HTTP capstone and prototype-starter checks passed on Ubuntu and Windows GitHub runners
- [ ] Independent Windows and Linux learner-submission and distributed-lab verification with documented prerequisites
- [ ] Failure injection and cleanup instructions for every mission
- [ ] Versioning policy that does not break ongoing learner work

## Public learner experience

- [x] Public onboarding and fork-based workflow documented
- [ ] First-time user flow validated by someone unfamiliar with the repository
- [x] GitHub-native fork, branch, PR and CI troubleshooting reference authored
- [ ] Independent beginner confirmation that the instructions work on a fresh account and laptop
- [ ] Navigation from beginner to capstone with real prerequisites
- [ ] Correct accessible documentation and link checks
- [ ] Example PR review demonstrating expected reasoning without exposing solutions

## Community, licensing and security

- [x] Contribution and community rules documented
- [ ] Maintainer approves appropriate code and content licenses before adding grants
- [ ] GitHub Actions and third-party dependency security review
- [ ] Protected default branch and required checks configured in GitHub settings
- [ ] Private vulnerability reporting method established
- [ ] Release tag and change log produced after all gates pass

## Branding and founder announcement gate

**Founder decision (2026-11-23):** Hold Academy launch advertising and the LinkedIn founder announcement until **v1.0 is complete and independently validated**. Keep the [announcement draft](../branding/FOUNDER_ANNOUNCEMENT.md) unpublished. A visible development repository is not a v1 launch.

- [ ] Approve final Academy brand name, trademark/domain/handle research, and visual identity.
- [ ] Prepare a factual v1.0 announcement using only shipped, validated features and a main/release link.
- [ ] Founder explicitly approves and publishes the LinkedIn launch announcement **after** all mandatory release gates, merge and versioned release.

## What is deliberately out of scope

No website, expensive hosted cloud sandbox, automated learning certification, or privileged autonomous code executor. GitHub already provides Issues, branches, reviews and CI.

## Release decision

**Do not announce public v1 until the mandatory gates pass.** Being a public repository does not signify readiness or an open-source redistribution license. Use feature PRs, CI and issues while developing. Maintainers validate solutions and graders in isolated environments. Public learners only begin after launch.
