# Cloud Engineering Sprint — Maintainer Test Evidence

**Verified November 23, 2026; status: PRE-RELEASE.** This is evidence from synthetic local CI, not a claim of production cloud certification.

## Missions and real test boundaries

| Mission | Professional incident | What actually passed | What is still unverified |
| --- | --- | --- | --- |
| [CLOUD-003](../missions/cloud-003/README.md) | API cannot reach private ledger in Docker Compose | Two real Python containers; shared bridge DNS and loopback-only API; successful HTTP response; clean teardown | Multi-host container networking, fault tolerance, TLS |
| [CLOUD-004](../missions/cloud-004/README.md) | Terraform plan threatens protected services | Terraform 1.12.2 init, provider-free terraform_data plan, terraform show -json, correct plan reviewer approval; simulated destructive/drift/SSH tests | Real external provider drift, remote backend/state locking, apply safety |
| [CLOUD-005](../missions/cloud-005/README.md) | Identity policy grants unrestricted S3 access | Private reference passes public structural unit tests for scoped ListBucket, GetObject and PutObject | Actual AWS policy evaluation, SCP, KMS permissions, bucket policy and access analyzer |
| [CLOUD-006](../missions/cloud-006/README.md) | Kubernetes rollout never becomes Ready | Real local kind cluster; two HTTP-ready nginx pods behind ClusterIP Service; deliberately broken image rollout followed by successful rollback | Production HA, multi-AZ, NetworkPolicies, ingress/TLS, pod security hardening |

All 12 current mission contract suites pass correct private reference implementations on Ubuntu and Windows. Every starter remains intentionally broken, so learners have something real to diagnose and repair.

## Runtime evidence links

- [GitHub Actions: public platform and contract checks](https://github.com/Elghouali/engineering-apprenticeship/actions) — accessible publicly.
- [GitHub Actions: private maintainer runtime checks](https://github.com/Elghouali/engineering-apprenticeship-solutions/actions) — requires authorized private repo access.
- [Sprint tracker](https://github.com/Elghouali/engineering-apprenticeship/issues/6) — milestones and remaining gaps.

## Real engineering lessons

Docker's localhost is scoped to the container, while the Compose network resolves peers by service name. Terraform JSON can express destructive replacement and drift and should be evaluated before approval; a saved plan is not permanent authorization. IAM object and bucket actions have different resource scopes, and a simulated JSON structure is not enough to prove authorization. Kubernetes Ready endpoints depend on correct Service selectors and readiness probes; maxUnavailable=0 preserves healthy old Pods during an unsuccessful rollout, subject to capacity constraints.

## Public launch remains blocked

Independent first-time GitHub fork/branch/PR/Actions onboarding; additional multi-cloud and resiliency missions; a learner-assigned full distributed capstone; reviewed code and curriculum licenses; and security/release controls are mandatory before v1.

No private reference solutions, real customer data, tokens, paid cloud accounts or API credentials were published in the public repository.
