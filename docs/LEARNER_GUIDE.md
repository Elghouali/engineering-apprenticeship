# Public Learner Guide — GitHub Is the Classroom

**Pre-release documentation.** This describes the intended learning workflow after launch.

## Requirements

Free GitHub account, Git, Python 3.11+, and a text editor. Docker is needed only for later labs. A paid cloud account is not required for foundation missions.

## Use your own fork

1. On GitHub, select **Fork** from the public academy repository.
2. Clone **your fork**: git clone https://github.com/YOUR-USERNAME/engineering-apprenticeship.git
3. Change to its directory and run: python tools/apprentice.py doctor
4. List missions: python tools/apprentice.py list
5. Read the mission's business incident and acceptance criteria.
6. Create a branch in your fork: git switch -c mission/retail-001
7. Copy the faulty starter safely: python tools/apprentice.py start retail-001
8. Run tests: python tools/apprentice.py check retail-001. Initial failure is expected.
9. Fix the code, rerun tests, commit and push your mission branch.
10. Open a pull request **with YOUR FORK as both base and head repository**: base main, compare mission branch. GitHub sometimes defaults to the upstream repository; change the base-repository dropdown.
11. If needed, enable GitHub Actions in the Actions tab of your fork. Fork workflows may initially be disabled until you opt in.
12. Link the upstream issue in your PR description but do not submit personal answers directly to the academy upstream repository.

No public learner should need write access to the project owner account. Learner solutions remain in personal forks unless a maintainer explicitly requests an upstream contribution.

## Master GitHub through the actual workflow

The [GitHub Skills Field Guide](GITHUB_WORKFLOW.md) covers Git remote configuration, meaningful commits, PR comparisons, reviewers, Actions failures, merge conflicts and keeping your fork up to date.

## Daily engineering habits

GitHub Issues hold requirements; branches isolate experiments; commits document decisions; PRs demonstrate code review; Actions show real failing and passing checks. A successful CI run is not a professional certificate.

## Getting help

Review official documentation and ask focused questions about the observed error. The mentor policy encourages one hint at a time. Never paste secrets or private personal data.

## Cost and security

Synthetic data only. Do not commit cloud credentials or production files. Do not run unknown learner code with real credentials. The beginner missions use only Python.
