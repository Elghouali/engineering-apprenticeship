# GitHub Skills Field Guide — Learn Through Real Engineering Work

**For public learners after academy launch.** No web academy is needed; GitHub itself is where you work. These are the actual mechanics you will repeat in each company mission.

## 0. One-time setup

Install Git and Python 3.11+. In a terminal:

~~~bash
git --version
python --version
git config --global user.name "YOUR DISPLAY NAME"
git config --global user.email "YOUR VERIFIED GITHUB EMAIL OR NOREPLY ADDRESS"
~~~

Use your GitHub account's private no-reply email if you do not want to expose your personal email in public commits. For HTTPS Git operations use a credential manager or GitHub CLI; GitHub account passwords cannot be entered directly as Git HTTPS credentials.

**Fork** the public academy in GitHub. Clone YOUR copy:

~~~bash
git clone https://github.com/YOUR-USERNAME/engineering-apprenticeship.git
cd engineering-apprenticeship
git remote -v
git remote add upstream https://github.com/Elghouali/engineering-apprenticeship.git
git status
~~~

Expected: origin points to your fork; upstream points to the academy. The default branch is main.

## 1. Convert a company Issue into a branch

Open the mission issue on upstream and read the business failure and acceptance criteria. Create an isolated branch on YOUR fork:

~~~bash
git switch main
git switch -c mission/retail-001
python tools/apprentice.py start retail-001
python tools/apprentice.py check retail-001
~~~

A broken starter is expected to fail. Capture the real output; the failure is your first investigation signal.

## 2. Read diffs and commit intentionally

After fixing code:

~~~bash
git status
git diff
git add submissions/retail-001/pipeline.py
git diff --cached
git commit -m "fix(retail-001): make paid-revenue totals replay-safe"
git push -u origin mission/retail-001
~~~

Good commit messages identify **what invariant changed**, not "stuff" or "update". Prefer a small, reviewable commit that changes only the mission submission and its relevant additional tests.

## 3. Open the correct pull request

In your fork's GitHub Pull Requests tab, select New pull request. Choose:
- **Base repository:** YOUR-USERNAME/engineering-apprenticeship
- **Base branch:** main
- **Head repository:** YOUR-USERNAME/engineering-apprenticeship
- **Compare branch:** mission/retail-001

The default GitHub "Compare across forks" flow may point to the upstream academy. **Check the base owner carefully.** Individual solution PRs should NOT target the shared upstream repository.

Use the PR template to link the upstream ticket, show a failed-before/fixed-after demonstration, explain root cause and include your uncertainty.

## 4. Inspect a failed GitHub Actions run

Open your PR -> Checks / Actions -> the failing job -> failed step. Read the **first relevant trace** and find:
- Is the environment wrong, or is the solution wrong?
- Which exact contract assertion failed?
- Can it be reproduced with python tools/apprentice.py check <mission-id>?
- Does the code handle malformed input and retries rather than only the happy path?

Fix the problem locally, rerun tests and push a second commit. GitHub updates the existing PR automatically. Do not "fix" a mission by editing official graders or bypassing checks.

## 5. Respond to code review

A professional reviewer asks about:
- data contracts and business effects
- error handling, retries and idempotency
- security, operational cost and observability
- edge cases and reproduction of the original incident
- alternatives considered

Reply to comments with evidence or a follow-up commit. If you disagree, explain the trade-off respectfully.

## 6. Handle changes from upstream

On your own fork, avoid overwriting your working branch. Fetch upstream:

~~~bash
git fetch upstream
git switch main
git merge --ff-only upstream/main
git push origin main
git switch mission/retail-001
git merge main
~~~

If a merge conflict appears, inspect the conflict markers, reconcile the intended data contract, rerun tests, stage resolved files and complete the merge. Never blindly overwrite a solution you want to keep.

Some missions have contract versions; before updating to latest, check [Mission Versioning](MISSION_VERSIONING.md). A breaking mission revision should be announced rather than silently replacing a learner's contract.

## 7. Keep evidence that shows real expertise

A strong PR links the business issue, demonstrates actual tests, explains failure and recovery, and includes a short architecture decision. A long commit history or green badge does not prove skill by itself.

**Optional GitHub tools:** GitHub CLI (gh), GitHub Desktop and VS Code's Git interface are valid; use whichever makes git concepts clear, but still understand branches, remotes and PR bases.

## Mistakes and how to recover

| Symptom | Investigation |
| --- | --- |
| You committed directly to your fork's main | Before pushing, create a new branch pointing at that commit; do not force-push published main without understanding the consequences |
| No permission to push to academy | Correct: you should push to your personal fork origin |
| Authentication failed | Verify credential manager, token scope or gh auth status |
| Cannot find newly created submission | Check your working directory and selected mission ID |
| A PR appears to target Elghouali/main | Change the base repository to your fork before creation |
| Tests pass locally but CI fails | Compare Python versions, filesystem case sensitivity, environment and untracked files |
| Remote changed while you worked | Fetch upstream, reconcile safely, rerun checks and push |

Official references:
- https://docs.github.com/en/get-started
- https://docs.github.com/en/pull-requests
- https://docs.github.com/en/actions
- https://git-scm.com/book/en/v2
