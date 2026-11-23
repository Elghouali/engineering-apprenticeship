# CLOUD-006 — Kubernetes rollout never becomes Ready

> **PRE-RELEASE / PROTOTYPE — contract v1.** This exercise has a public grader and a confidential correct reference, but independent first-time learner onboarding has not yet passed.

**Atlas Retail | Cloud Platform Engineer | Prerequisites: CLOUD-003 and CLOUD-004**

## Production-style incident

A new reporting API rollout appears to have created pods, but Kubernetes keeps reporting that no instances are Ready. The Service has zero endpoints, one replica cannot tolerate node trouble, and an unconstrained rolling update risks downtime.

Repair the manifest by understanding Deployment selectors, Pod labels, readiness probes, liveness probes, and Service networking—not by disabling the checks.

## Required function

Implement build_resources() -> dict in submissions/cloud-006/k8s.py.
Return a dictionary with exactly two objects named deployment and service.

Deployment:
- apps/v1, kind Deployment, metadata.name reports-api.
- spec.replicas = 2, strategy.type RollingUpdate, maxUnavailable=0, maxSurge=1.
- spec.selector.matchLabels and template.metadata.labels are exactly {"app":"reports-api"}.
- One container named api, image nginx:1.28-alpine, exposing containerPort 80.
- readinessProbe uses HTTP GET path / and port 80; initialDelaySeconds=1 and periodSeconds=2.
- livenessProbe uses HTTP GET path / and port 80; initialDelaySeconds=5 and periodSeconds=5.
- requests cpu=50m, memory=32Mi; limits cpu=250m, memory=128Mi.

Service:
- v1, kind Service, metadata.name reports-api, type ClusterIP.
- selector {"app":"reports-api"}, ports one item port=80 targetPort=80.

Do not add host networking, hostPath or privileged containers. The starter is deliberately broken: the readiness probe points to a nonexistent path, replicas=1, and the Service selector does not match the Pods.

## Verification

The public unit grader checks manifest invariants, while the separate **private maintainer CI** applies the corrected manifests to a local Kubernetes-in-Docker (kind) cluster, waits for rollout, and tests an actual HTTP response through the Service.

A real kind cluster tests these local behaviors only; it does not demonstrate high availability across multiple cloud availability zones or a full secure production deployment.

After public launch on your own fork:

    python tools/apprentice.py start cloud-006
    python tools/apprentice.py check cloud-006

## Engineering review

Explain Ready vs Running, startup/readiness/liveness probes, how Services select endpoints, rolling updates and maxUnavailable, and which signals to inspect using kubectl describe pods, kubectl get endpoints, and kubectl rollout status. Document how to roll back a bad deployment.

**Status:** prototype; independent public learner workflow and production resilience remain outstanding.

Official docs: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ and https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/


## Maintainer validation evidence

The public contract has a correct implementation in a separate private repository and passes Linux/Windows tests. See [Cloud sprint evidence](../../docs/CLOUD_SPRINT_EVIDENCE.md).

The private CI created a disposable kind Kubernetes cluster, reached the two Ready pods through a Service, introduced a bad image rollout, and rolled back to a healthy state. This is a local cluster, not verified multi-AZ resilience.

---

## Mission handoff: from incident to pull request

**Requirements:** Python 3.11+ for manifest tests; optional local kind/Kubernetes for readiness and rollback drills. Read the contract above before changing code.

**Training files:** [faulty starter](starter/k8s.py) · [public acceptance tests](tests/test_submission.py) · personal output: `submissions/cloud-006/k8s.py` (created only in a learner fork, not committed upstream).

From the **root of your own fork**, after public launch:

```bash
git switch -c mission/cloud-006
python tools/apprentice.py start cloud-006
python tools/apprentice.py check cloud-006
```

The first test run must fail because the starter is intentionally defective. Implement and test only in your submission; do not edit official graders. Push to your fork and open a PR **against your own fork's main branch**, not the academy upstream.

**Failure-recovery drill:** Explain unready pods, mismatched selectors and bad image rollouts; prove a safe rollback in a disposable cluster.

In your PR, demonstrate **Explain / Build / Recover / Defend**: root cause, passing regression checks, recovery behavior and trade-offs. See the [review rubric](../../docs/ENGINEERING_LOOP.md) and [hint policy](../../mentor/REVIEW_POLICY.md).

**Continue to:** [Local reference capstone](../../capstones/atlas-retail-platform/README.md) and [planned integrated project](../../docs/PUBLIC_CURRICULUM.md). These are suggestions; use the [catalog](../catalog.json) for exact prerequisites.

[← All missions](../README.md) · [Academy](../../README.md) · [Company](../../companies/atlas-retail/README.md) · [Documentation](../../docs/README.md)
