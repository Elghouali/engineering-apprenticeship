# Contributing to Engineering Apprenticeship

Contributions to public education are welcome: fix inaccurate concepts, improve official resource links, create realistic missions, strengthen tests and make instructions reproducible.

**Do not submit personal homework solutions to the upstream repository.** Learner work belongs in the learner's fork.

## Changes

1. Find or open an upstream issue about the proposed improvement.
2. Fork and branch.
3. Keep content, fixtures, contract tests and skill dependencies consistent.
4. Run: python -m unittest discover -s tests -v
5. Open a focused PR with actual results and known limitations.
6. Respond constructively to reviewer feedback.

New missions must have an explicit business problem, reproducible starter, contract test, failure drill, open documentation references and review criteria. Consult [Maintainer Guide](docs/MAINTAINER_GUIDE.md).

## Licensing

This public repository currently has no maintainer-approved license. Public GitHub visibility alone does not grant open-source reuse rights. A code/content licensing policy must be selected and applied before v1 launch. Do not paste proprietary tutorials, books or customer datasets.

## Safety

Do not commit keys, sensitive data or client records. Do not add privileged PR workflows or billable cloud provisioning to tests.
