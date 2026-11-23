# Engineering Apprenticeship — Learn by Shipping on GitHub

> **A GitHub-native Big Data and Cloud Engineering apprenticeship.** No learning website, virtual badges or passive video sequence. You learn by tackling engineering issues in evolving fictional companies, fixing real code, submitting pull requests, and defending your design.

## Start your first mission

**[Mission RETAIL-001: Incorrect daily revenue after ETL retry](missions/retail-001/README.md)**

1. Read the assigned **GitHub Issue** and the stakeholder brief.
2. Create your own `mission/retail-001` branch.
3. Examine the deliberately faulty starter code and reproduce the failure.
4. Learn the necessary Python, SQL/data-contract concepts, and implement the solution yourself.
5. Add code under `submissions/retail-001/pipeline.py` — leave the starter untouched.
6. Run local tests, commit/push, and open a PR using our PR template.
7. Review automated checks, diagnose failures and respond to code review.
8. Merge only after tests pass and the design is explained; record what went wrong.

~~~bash
git clone https://github.com/Elghouali/engineering-apprenticeship.git
cd engineering-apprenticeship
python tools/apprentice.py list
python tools/apprentice.py doctor
python tools/apprentice.py check retail-001
~~~

**The first `check` fails until you submit a solution.** That is intentional and part of the apprenticeship.

## Our method: problem → investigation → theory → implementation → recovery → PR

~~~mermaid
flowchart TD
 ISSUE[GitHub Issue: a real work ticket] --> BRANCH[Own branch]
 BRANCH --> BUG[Reproduce failure]
 BUG --> CONCEPT[Understand the underlying concepts]
 CONCEPT --> FIX[Implement + test]
 FIX --> CI[GitHub Actions]
 CI -->|Fails| BUG
 CI -->|Passes| REVIEW[Reasoning and code review]
 REVIEW --> MERGE[Merge and retrospect]
 MERGE --> NEXT[Next harder mission]
~~~

You do not advance based on watching content or the number of commits. Progress is based on **evidence of conceptual understanding, correct software, failure recovery and design decisions**. A green check alone is insufficient.

## First release scope

| Capability | Minimal implementation |
| --- | --- |
| Company simulator | [Atlas Retail](companies/atlas-retail/README.md), with an evolving system |
| Missions | [RETAIL-001](missions/retail-001/README.md), the first runnable engineering incident |
| Skills | [Prerequisite graph](skills/graph.json) and [mission catalog](missions/catalog.json) |
| Automated grading | GitHub Actions + standard-library unit tests |
| GitHub workflow | Issue template, PR review template, code-review and incident-retrospective rules |
| AI mentor | [Hint-first mentor policy](mentor/REVIEW_POLICY.md) (instructions only, no bot yet) |
| Cloud labs | Reuse the [BigData Academy](https://github.com/Elghouali/BigData/tree/feature/academy-data-cloud-from-zero/academy); expand after proving the method |

The **first release is not a web application**, has no deployed AI bot, and does not run paid cloud resources. The core learning loop works with Python, Git, GitHub Issues, Pull Requests and Actions.

## Learning and contribution rules

- Work on a branch and submit a PR; don't directly change `main`.
- First reproduce the bug, then explain *why* the fix works.
- Don't edit the tests, grader or original starter to make a challenge pass.
- Keep simulated customer data synthetic. Never commit credentials or company data.
- GitHub Actions runs learner code with read-only repository permissions and no cloud secrets. Code must not require real credentials.
- Academy reference work remains in [BigData](https://github.com/Elghouali/BigData); this repository hosts the apprenticeship workflow, not copied lectures.

See [the engineering loop](docs/ENGINEERING_LOOP.md), [planned missions](docs/NEXT_MISSIONS.md), and [mentor policy](mentor/REVIEW_POLICY.md).
