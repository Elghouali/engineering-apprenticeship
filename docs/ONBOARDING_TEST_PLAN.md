# Independent Public-Learner Acceptance Test

**Status: NOT YET EXECUTED.** A green platform test does not prove a new learner can successfully use the academy.

## Test environment

- A GitHub account with no write permission to upstream.
- A fresh fork and clone, not a maintainer workstation.
- Windows PowerShell and Linux terminals, each with documented Git/Python versions.
- No cloud credentials or paid resource access.

## Acceptance procedure

1. Find the academy from its public README alone.
2. Understand that the product is pre-release and recognize the first mission prerequisites.
3. Fork upstream, clone fork and confirm origin points to the learner account.
4. Create a mission branch and run the CLI start command; first starter must fail tests.
5. Read the issue, diagnose the bug, implement an independent fix and observe deterministic tests passing.
6. Commit and push without access to upstream main.
7. Open a PR that targets **learner fork/main**, not upstream main.
8. Enable Actions in the fork if needed; observe actual CI logs and repair any failure.
9. Explain the root cause, fault recovery and trade-offs using the PR template.
10. Follow the skill graph to the next mission without direct maintainer assistance.
11. Run the end-to-end capstone, observe healthy/stale reports and verify recovery.
12. Report confusing instructions, broken links, environment blockers and costs.

## Results to capture

| Finding | Evidence |
| --- | --- |
| User's OS and installed tools | Versions and commands |
| Fork setup success | Repository and remotes (no credentials) |
| Initial failure | First real test log |
| Correct repair | Actual passing test and CI logs |
| Correct PR scope | Base/head branch names |
| Incident understanding | Review response |
| Total blockers | GitHub issues with reproduction |
| Capstone verification | Real local build, verify and HTTP output |

Do not fabricate screenshots or results. Do not mark this acceptance test complete until an independent person carries it out on actual hardware/accounts.
