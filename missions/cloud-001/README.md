# CLOUD-001 — Reporting API fails intermittently

**Company:** Atlas Retail Cloud Team · **Role:** Junior Cloud/Platform Engineer

## Simulated incident

An internal reporting API returns HTTP 503 during rolling deployments. A client should retry **safe GET requests only** using bounded exponential backoff. Blindly retrying a non-idempotent payment POST is dangerous.

This first task teaches network failures, HTTP status codes, retry policies, failure budgets and reliable testing, without cloud fees.

## Required interface

Implement fetch_report(url, transport, attempts=3, sleep=None) in a copied submission module.

- transport(url) is a callable returning a tuple: (HTTP status integer, JSON-compatible response object).
- A successful 200 response returns a dictionary with exactly:
  - status: 200
  - body: object returned from transport
  - attempts: number of transport calls made
- Retry for HTTP status **429, 502, 503, 504**, plus ConnectionError and TimeoutError.
- For a non-retryable HTTP error (including 400, 401, 403, 404, 500), raise ValueError("non_retryable_http:<status>") immediately.
- Exhausting the attempt budget must raise RuntimeError("retry_exhausted") without making extra calls.
- Validate attempts is an integer from 1 through 5 and reject boolean values, otherwise ValueError("invalid_attempts").
- If sleep is supplied, call sleep(delay_seconds) *between* retries with exponential delay starting at 0.1 seconds (then 0.2, 0.4 etc.). No sleeping after the final attempt. If sleep is None, use time.sleep.

Never send a real financial request in this exercise. The transport is injected so tests can simulate outages deterministically. Later missions use real localhost networking and Docker.

## Workflow

1. Trace where DNS, TCP and HTTP fail differently.
2. Examine the starter's unbounded retry behavior.
3. Implement the smallest bounded retry policy.
4. Show initial failed tests, then the corrected run.
5. Write an incident note: what does a 503 tell you, and why might retries amplify traffic?

    python tools/apprentice.py start cloud-001
    python tools/apprentice.py check cloud-001

## Acceptance

- [ ] All retryable errors handled with bounded attempts.
- [ ] Bad 404 is never retried.
- [ ] Correct exponential backoff calls.
- [ ] Explicit final exhaustion error.
- [ ] PR explains timeouts, retries, idempotency and design trade-offs.

**Open references:** https://developer.mozilla.org/en-US/docs/Web/HTTP/Status ; https://docs.python.org/3/library/time.html
