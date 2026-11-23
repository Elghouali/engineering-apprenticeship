# How a GitHub Apprenticeship Mission Works

The learner should become fluent in the everyday GitHub workflow **by using it**. This is not a course hidden behind a web UI.

## The complete loop

1. **Backlog** — Open a GitHub Issue. Read the stakeholder impact, acceptance criteria and existing symptoms.
2. **Planning** — Identify what you understand, what you must investigate, and the expected behavior. Add a short comment with your approach.
3. **Branch** — Create `mission/<issue-id>` from the base branch. Don't make unrelated changes.
4. **Reproduction** — Run failing code, capture an actual output and state the suspected root cause.
5. **Learn** — Read the precise official docs you need. Theory is *pulled in by the problem*, not delivered as a compulsory chapter before the problem.
6. **Implement** — Submit the smallest correct change. Think about data contracts, error handling, idempotency and testing.
7. **Verification** — Run local tests, push, inspect GitHub Actions, and repair failed checks.
8. **Review** — Open a PR. Explain before/after, failure mode, architectural choices and alternative solutions.
9. **Retrospective** — Record a production lesson and the weakness that should influence the next mission.

## Review rubric

| Dimension | 0 — Missing | 2 — Functional | 4 — Independent engineer |
| --- | --- | --- | --- |
| Understand | Cannot explain problem | Explains data flow | Explains mechanisms, contracts and trade-offs |
| Build | Does not run | Correct expected cases | Reproducible, tested, maintainable solution |
| Recover | Cannot reproduce failure | Handles specified failure | Handles edge cases and produces an incident runbook |
| Defend | No reasoning | Explains changes | Provides evidence, considers alternatives and security |

**Passing CI is a necessary but insufficient condition**. Learning completion requires a PR with evidence and explanation.

## GitHub features to learn deliberately

- Issues: requirements, discussion and task boundaries
- Git branches and commits: isolated changes and readable history
- Pull requests: review, discussion, diffs and merge
- Actions: CI, logs, checks and diagnosing failures
- Projects: a backlog board (optional; can be added once several missions exist)
- Releases and tags: durable capstone milestones

## What we intentionally do not build now

No web dashboard, complex user database, microservices, cloud execution platform or autonomous coding agent. We first prove that one mission can be completed end to end on GitHub.

## Safety

Every first-release exercise runs locally or with a least-privilege GitHub Actions job. No PR-target privileged workflow, no production secrets in CI and no automatic cloud provisioning.
