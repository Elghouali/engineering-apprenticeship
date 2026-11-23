# CAPSTONE-005 — Deploy and recover the reporting API on Kubernetes

**Role:** Cloud/Platform Engineer · **Status:** planned, not yet verified against the integrated services.

**Incident:** A reporting API rollout succeeds at deployment creation but returns no healthy endpoints; an erroneous image may leave users without revenue reporting.

**Acceptance intent:** Deploy the API into a disposable kind cluster with readiness/liveness checks, non-public Service access, least-privilege runtime settings and deterministic rollback. Establish connectivity to PostgreSQL and the S3-compatible report store without public credentials. Test a broken rollout and recovery.

**Deliverable:** manifests, cluster integration evidence, incident timeline, rollback plan and GitHub PR review.

**Prerequisites:** [CLOUD-006](../../../missions/cloud-006/README.md), [CLOUD-003](../../../missions/cloud-003/README.md). [← Capstone](../README.md).
