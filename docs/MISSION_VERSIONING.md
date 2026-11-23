# Mission Contracts and Backward Compatibility

Public missions are versioned learning APIs, not mutable homework questions.

Each entry in [catalog.json](../missions/catalog.json) contains:
- Stable mission ID, e.g. retail-001.
- Integer contract_version starting at 1.
- Explicit prerequisites, starter path, submission path, grading test folder, required skills and maturity status.

## Contract changes

- A typo or clearer explanation that does not change expected behavior may be patched without incrementing contract_version.
- Changing a function name, business rule, fixture meaning, exception, data schema or expected output **requires a version increment** and a migration note.
- Do not change a mission contract while public learners are halfway through it without keeping an old branch/tag and clearly communicating the migration.
- Learner forks keep their selected Git commit; do not assume they have automatically updated.
- Grading should be tied to the exact commit or release tag in the learner's fork, not silently upgraded to latest.

## Maturity statuses

- prototype: exercise exists and is undergoing reference/independent verification. Not suitable for a public launch announcement.
- ready: reference solution proven against contract tests, docs checked, cross-platform setup verified, maintainer signoff complete.
- archived: preserved for historical learner submissions but excluded from new recommendations.

Do not mark a mission ready merely because the **broken starter** fails tests. A correct solution must pass the same contract, and a full learner onboarding journey needs independent validation.

## Maintainer checks

Run Python platform unit tests and link checker. Inspect the GitHub Actions build. For integration missions, use real service startup and failure recovery rather than mock-only tests. Retain evidence of what was actually verified.

Reference solutions should be kept out of public starter code; keep them in a private and access-controlled maintainer workspace after the owner creates/approves one. Do not claim CI validation of a correct solution until it actually happened.
