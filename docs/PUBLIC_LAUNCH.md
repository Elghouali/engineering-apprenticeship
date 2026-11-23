# Public Launch Gate — Engineering Apprenticeship

**Status: PRE-RELEASE / BUILDING. This is not yet a complete public academy.**

Public visibility on GitHub is not the same as launch readiness. The founder builds and maintains the product; the founder is NOT expected to complete learner assignments.

## Definition of v1

A complete public learner journey must work without founder intervention: read a role-specific pathway, fork the academy, diagnose faulty starter code, write an original repair, run tests, see CI feedback, submit a PR to their own fork, and complete an end-to-end portfolio capstone.

## Technical gates

- [x] GitHub-native mission scaffolding, company story and skills graph
- [x] Basic platform tests and least-privilege CI
- [ ] Multiple connected Big Data missions with verified correct reference implementations (five prototypes exist across tracks)
- [ ] Multiple connected Cloud Engineering missions including local networking and containers
- [x] Local end-to-end reference data product: real SQLite, immutable release, replay/tamper/quality failure tests in CI
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

## What is deliberately out of scope

No website, expensive hosted cloud sandbox, automated learning certification, or privileged autonomous code executor. GitHub already provides Issues, branches, reviews and CI.

## Release decision

**Do not announce public v1 until the mandatory gates pass.** Being a public repository does not signify readiness or an open-source redistribution license. Use feature PRs, CI and issues while developing. Maintainers validate solutions and graders in isolated environments. Public learners only begin after launch.
