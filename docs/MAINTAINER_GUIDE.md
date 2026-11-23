# Maintainer Handbook

## Founder role

The founder builds a publicly shareable academy and does not practice as a student. Keep the shared repository as the trusted curriculum distribution source.

## Separation of responsibility

- Upstream main: trusted mission content, fixtures, graders, official documentation.
- Upstream feature branches: project changes reviewed with CI before merge.
- Learner forks: personal answers, tests and retrospective evidence.
- Upstream PRs: fixes or curriculum improvements, NOT homework submissions.
- Learner PRs: inside a learner's own fork with their own main as base.

## Required mission definition

Every mission needs a believable engineering ticket, role, prerequisites, acceptance contract, deliberately faulty or incomplete starter, tests, failure-recovery drill, official resources and rubric. The starter must fail; a separately validated maintainer solution must pass. Don't publish the solution in the starter repository.

## Code review standards

Review correctness, data contracts, repeatability, incident recovery, design decisions, security and realistic operation. Use the Explain / Build / Recover / Defend rubric; passing automated tests alone is insufficient.

## CI safety and publishing

Default to read-only permissions; never run learner-supplied code in a privileged workflow or with cloud secrets. Assume GitHub Actions on a public fork can execute arbitrary code. Test on a sandboxed account, not a maintainer workstation with personal files. Require branch protections via GitHub repository settings, then review release gates.

No license has been approved. Do not silently grant redistribution rights without explicit maintainer choice.

## Launch

Follow the [Public Launch Gate](PUBLIC_LAUNCH.md). Only publish a versioned stable release after independent learner testing and end-to-end integration checks.
