# CLOUD-003 — Reporting API cannot reach ledger in Docker

> **PRE-RELEASE / PROTOTYPE — contract v1.** This exercise has a public grader and a confidential correct reference, but independent first-time learner onboarding has not yet passed.

**Atlas Retail | Junior Cloud Engineer | Prerequisite: CLOUD-001**

## Incident
The reporting API was moved to Docker Compose and now returns HTTP 503. Its upstream URL points to localhost, which inside the API container means the API itself—not the ledger. Publishing the ledger's port publicly is not a valid fix.

## Contract
Implement design_stack() -> dict in submissions/cloud-003/network.py.
Return a Docker Compose dict that:
- Defines api and ledger services, using python:3.11-alpine images.
- Runs ["python", "/workspace/api.py"] and ["python", "/workspace/ledger.py"] respectively.
- Mounts ./runtime:/workspace:ro in both services, connected to named backend bridge network.
- Sets api.environment.LEDGER_URL to http://ledger:8090 (Docker internal DNS).
- Publishes ONLY api port as 127.0.0.1:18081:8080.
- Does not publish the ledger port, use host networking, privileged containers or Docker sockets.

The public grader checks invariants without starting Docker. Maintainer CI has also tested real service discovery in isolated local Docker containers.

## After public launch
From a mission branch in your fork:

    python tools/apprentice.py start cloud-003
    python tools/apprentice.py check cloud-003

Use json.dump(design_stack(), output) to produce a Compose-compatible JSON file in the mission directory, run docker compose -f FILE up -d, test http://127.0.0.1:18081/health and clean up with docker compose down -v.

## Engineering review
Explain network namespaces, DNS service naming, loopback host binding vs container listening address, failure reproduction, startup readiness, firewall exposure and rollback. No cloud credentials.

**Status:** prototype; full independent learner onboarding not yet tested.

Official documentation: https://docs.docker.com/compose/how-tos/networking/


## Maintainer validation evidence

The public contract has a correct implementation in a separate private repository and passes Linux/Windows tests. See [Cloud sprint evidence](../../docs/CLOUD_SPRINT_EVIDENCE.md).

The private CI started two actual Docker containers; the host loopback API successfully requested ledger data using service DNS. Full independent learner fork testing remains open.

---

## Mission handoff: from incident to pull request

**Requirements:** Python 3.11+ for contracts; optional Docker Engine/Compose for live service networking. Read the contract above before changing code.

**Training files:** [faulty starter](starter/network.py) · [public acceptance tests](tests/test_submission.py) · personal output: `submissions/cloud-003/network.py` (created only in a learner fork, not committed upstream).

From the **root of your own fork**, after public launch:

```bash
git switch -c mission/cloud-003
python tools/apprentice.py start cloud-003
python tools/apprentice.py check cloud-003
```

The first test run must fail because the starter is intentionally defective. Implement and test only in your submission; do not edit official graders. Push to your fork and open a PR **against your own fork's main branch**, not the academy upstream.

**Failure-recovery drill:** Show that Docker service name ledger works where localhost fails and confirm the ledger is not published to the host.

In your PR, demonstrate **Explain / Build / Recover / Defend**: root cause, passing regression checks, recovery behavior and trade-offs. See the [review rubric](../../docs/ENGINEERING_LOOP.md) and [hint policy](../../mentor/REVIEW_POLICY.md).

**Continue to:** [CLOUD-004](../cloud-004/README.md), [CLOUD-006](../cloud-006/README.md). These are suggestions; use the [catalog](../catalog.json) for exact prerequisites.

[← All missions](../README.md) · [Academy](../../README.md) · [Company](../../companies/atlas-retail/README.md) · [Documentation](../../docs/README.md)
