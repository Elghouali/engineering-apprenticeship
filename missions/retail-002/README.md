# RETAIL-002 — Payment recorded twice after an API timeout

> **PRE-RELEASE / PROTOTYPE — contract v1.** This exercise has a public grader and a confidential correct reference, but independent first-time learner onboarding has not yet passed.

**Company:** Atlas Retail · **Role:** Junior Backend/Data Engineer · **Prerequisite:** RETAIL-001 (idempotency basics)

## Business incident

A payment API writes to SQLite successfully, but the HTTP response gets lost. The client retries with the SAME request identifier. The old implementation inserts a new row for every retry, so finance sees double payments.

Your task is to protect business state under retries using **database constraints and transactions**. No bank accounts, payment gateways or real customer data are involved.

## Required interface

Implement two functions in a copied submission file:

- setup(db: sqlite3.Connection) -> None — prepare the payments table, safe to call repeatedly.
- record_payment(db, request_id: str, order_id: str, amount_cents: int) -> dict.

A successful **first call** returns:
- status: "created"
- payment_id: the positive integer primary key.

A repeated request_id with the exact same order_id and amount returns:
- status: "replayed"
- payment_id: the SAME integer primary key.

A repeated request_id with a conflicting order_id or amount must raise ValueError("idempotency_conflict"). Invalid inputs raise ValueError with one of:
- invalid_request_id
- invalid_order_id
- invalid_amount

Amounts must be positive integer cents (reject booleans), and payment records must not change after failed operations. Database schema must enforce UNIQUE(request_id) so competing callers cannot insert two payments.

## Investigation

1. Open the starter and identify why a second call inserts again.
2. Draw a timeline: commit succeeds -> response lost -> retry received.
3. Read SQLite transaction semantics and unique constraints.
4. Implement a safe database write and run contract tests.
5. Add evidence explaining which parts are truly atomic.

## Run after starting a mission branch

    python tools/apprentice.py start retail-002
    python tools/apprentice.py check retail-002

The starter intentionally fails. Do not change the original starter or grader.

## Acceptance criteria

- [ ] First request creates exactly one record.
- [ ] Identical retry returns the same payment ID.
- [ ] Conflicting retry raises an explicit exception and preserves the existing payment.
- [ ] Invalid inputs leave the database unchanged.
- [ ] Correctness remains after a connection close and reopen.
- [ ] A professional PR explains the underlying failure and transaction/constraint design.

This is an educational local SQLite example; concurrency under different database engines and external payment service coordination require further design.

**Open reference:** https://www.sqlite.org/lang_conflict.html ; https://www.sqlite.org/lang_transaction.html

---

## Mission handoff: from incident to pull request

**Requirements:** Python 3.11+ and bundled SQLite; no real payment gateway. Read the contract above before changing code.

**Training files:** [faulty starter](starter/payment.py) · [public acceptance tests](tests/test_submission.py) · personal output: `submissions/retail-002/payment.py` (created only in a learner fork, not committed upstream).

From the **root of your own fork**, after public launch:

```bash
git switch -c mission/retail-002
python tools/apprentice.py start retail-002
python tools/apprentice.py check retail-002
```

The first test run must fail because the starter is intentionally defective. Implement and test only in your submission; do not edit official graders. Push to your fork and open a PR **against your own fork's main branch**, not the academy upstream.

**Failure-recovery drill:** Commit a payment, retry the same request ID, and prove only one durable payment exists.

In your PR, demonstrate **Explain / Build / Recover / Defend**: root cause, passing regression checks, recovery behavior and trade-offs. See the [review rubric](../../docs/ENGINEERING_LOOP.md) and [hint policy](../../mentor/REVIEW_POLICY.md).

**Continue to:** [RETAIL-003](../retail-003/README.md), [DATA-005](../data-005/README.md). These are suggestions; use the [catalog](../catalog.json) for exact prerequisites.

[← All missions](../README.md) · [Academy](../../README.md) · [Company](../../companies/atlas-retail/README.md) · [Documentation](../../docs/README.md)
