# CLOUD-004 — Terraform plan would destroy a protected service

> **PRE-RELEASE / PROTOTYPE — contract v1.** This exercise has a public grader and a confidential correct reference, but independent first-time learner onboarding has not yet passed.

**Atlas Retail | Cloud Platform Engineer | Prerequisites: CLOUD-003, CLOUD-002**

## Incident
A proposed infrastructure change includes a resource replacement and a security-group rule exposing SSH. The reviewer is about to approve a destructive apply. A separate out-of-band change (drift) may not be visible in a regular code diff.

## Contract
Implement assess_plan(plan: dict) -> dict in submissions/cloud-004/plan_guard.py. Accept the machine-readable output of terraform show -json PLAN (subset of official plan JSON).

The plan must include format_version beginning with "1." and resource_changes as a list. resource_drift is optional, default [].
For each entry in resource_changes and resource_drift, require a nonempty address and a change object containing an actions list. Invalid structure or unrecognized actions raise ValueError("invalid_plan").

Valid action sequences: ["no-op"], ["create"], ["update"], ["delete"], ["delete","create"], ["create","delete"], ["read"].
- A delete or replacement in resource_changes is destructive and blocks the plan.
- Resource drift with any action other than no-op needs manual review.
- A security group (type aws_security_group) with a newly proposed inbound TCP/any rule exposing port 22 to 0.0.0.0/0 blocks the plan. Read the after.ingress list. Entries use from_port, to_port, protocol and cidr_blocks.

Return exactly:
{
 "decision": "approve" | "review" | "block",
 "reasons": sorted(["destructive_change", "public_ssh", "unmanaged_drift"]),
 "destructive_resources": sorted(addresses),
 "drift_resources": sorted(addresses)
}
Only include reasons that apply. Block takes priority over review. A clean create/update/no-op plan may be approved. The grader includes a synthetic IAM-exposure-like network rule, but this is NOT a comprehensive security policy engine.

## Real Terraform practice
The public terraform/ directory contains a fully local, provider-free terraform_data configuration. Use Terraform CLI to init, plan -out, and show -json; the private maintainer CI does this automatically with a pinned Terraform version and checks your reviewer against actual plan JSON. No AWS/GCP/Azure account or backend is involved.

After launch, use:
    python tools/apprentice.py start cloud-004
    python tools/apprentice.py check cloud-004

## Engineering review
Explain replacement action ordering, why resource_drift differs from resource_changes, what -refresh-only observes, why a saved plan cannot be treated as a permanent approval, why no terraform apply belongs in an untrusted PR, and your rollback/approval process.

**Status: prototype.** Official references: https://developer.hashicorp.com/terraform/internals/json-format and https://developer.hashicorp.com/terraform/cli/commands/plan


## Maintainer validation evidence

The public contract has a correct implementation in a separate private repository and passes Linux/Windows tests. See [Cloud sprint evidence](../../docs/CLOUD_SPRINT_EVIDENCE.md).

The private CI generated Terraform 1.12.2 plan JSON from the built-in terraform_data resource. Destructive/drift/public-SSH cases were simulated and unit-checked, not reproduced in a real cloud provider.

---

## Mission handoff: from incident to pull request

**Requirements:** Python 3.11+ for policy tests; optional Terraform CLI and built-in terraform_data resource, no cloud credentials. Read the contract above before changing code.

**Training files:** [faulty starter](starter/plan_guard.py) · [public acceptance tests](tests/test_submission.py) · personal output: `submissions/cloud-004/plan_guard.py` (created only in a learner fork, not committed upstream).

From the **root of your own fork**, after public launch:

```bash
git switch -c mission/cloud-004
python tools/apprentice.py start cloud-004
python tools/apprentice.py check cloud-004
```

The first test run must fail because the starter is intentionally defective. Implement and test only in your submission; do not edit official graders. Push to your fork and open a PR **against your own fork's main branch**, not the academy upstream.

**Failure-recovery drill:** Detect delete/replacement actions, public SSH and resource drift before approving a saved plan.

In your PR, demonstrate **Explain / Build / Recover / Defend**: root cause, passing regression checks, recovery behavior and trade-offs. See the [review rubric](../../docs/ENGINEERING_LOOP.md) and [hint policy](../../mentor/REVIEW_POLICY.md).

**Continue to:** [CLOUD-005](../cloud-005/README.md), [CLOUD-006](../cloud-006/README.md). These are suggestions; use the [catalog](../catalog.json) for exact prerequisites.

[← All missions](../README.md) · [Academy](../../README.md) · [Company](../../companies/atlas-retail/README.md) · [Documentation](../../docs/README.md)
