# CLOUD-003 — Reporting API cannot reach ledger in Docker

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

The public grader checks invariants without starting Docker. The private maintainer job will also test real service discovery in isolated containers.

## After public launch
From a mission branch in your fork:

    python tools/apprentice.py start cloud-003
    python tools/apprentice.py check cloud-003

Use json.dump(design_stack(), output) to produce a Compose-compatible JSON file in the mission directory, run docker compose -f FILE up -d, test http://127.0.0.1:18081/health and clean up with docker compose down -v.

## Engineering review
Explain network namespaces, DNS service naming, loopback host binding vs container listening address, failure reproduction, startup readiness, firewall exposure and rollback. No cloud credentials.

**Status:** prototype; full independent learner onboarding not yet tested.

Official documentation: https://docs.docker.com/compose/how-tos/networking/
