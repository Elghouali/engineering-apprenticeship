# Mission RETAIL-001 — Incorrect Revenue After an ETL Retry

**Company:** [Atlas Retail](../../companies/atlas-retail/README.md)  
**Role:** Junior Data Engineer (Trainee)  
**Priority:** P0 — finance reporting is incorrect  
**Mode:** GitHub Issue → branch → investigation → fix → tests → PR review

## The fictional incident

At 06:00, Atlas Retail re-ran its daily orders ingestion after a temporary outage. The finance dashboard now reports too much paid revenue. The raw CSV contains an exact duplicate from a retry, a conflicting repeated order ID, invalid records and an order that was cancelled.

Your manager wants an **auditable, deterministic daily revenue calculation** that safely handles the feed without silently dropping important errors.

## Real business acceptance criteria

Input: CSV records with `order_id,customer_id,quantity,unit_price,status`.

Output of `summarize(rows)`: JSON-serializable dictionary containing:

- `paid_revenue_cents`: integer cents from **paid** accepted orders only.
- `accepted_order_ids`: **sorted** list of unique valid order IDs, including valid cancelled orders.
- `duplicate_count`: number of repeated identical valid records ignored.
- `rejections`: a list of objects each with `order_id` and `reason`.

Rules:

1. Required non-empty `order_id` and `customer_id`.
2. `quantity` must be an integer greater than zero.
3. `unit_price` must be a finite nonnegative decimal with at most **two decimal places**; represent money exactly.
4. `status` is `paid` or `cancelled` only. Cancelled orders are valid but add **zero** paid revenue.
5. Validate before reserving a business key. An invalid row must not prevent a later valid version of that ID from being accepted.
6. If the same order ID appears again with an identical valid payload, count it as a duplicate.
7. If the same order ID appears with a *different valid payload*, quarantine it as `conflicting_order_id` and keep the first accepted version.
8. Reject other bad records with meaningful reason codes: `missing_order_id`, `missing_customer`, `invalid_quantity`, `invalid_amount`, `invalid_status`.
9. Do not modify the input collection; do not depend on external services.
10. Deterministic output on repeated calls.

## Fixture target

The synthetic [orders CSV](data/orders.csv) contains eight lines of data. Expected:

| Signal | Expected |
|---|---|
| Input rows | 8 |
| Accepted unique orders | 4 |
| Exact duplicates | 1 |
| Rejected records | 3 |
| Paid revenue | **220.00 MAD** / **22000 cents** |

A green test suite is only a starting point. You must also be able to explain the incident and defend your decisions.

## GitHub workflow — your task

From repo root:

~~~bash
git switch -c mission/retail-001
mkdir -p submissions/retail-001
cp missions/retail-001/starter/pipeline.py submissions/retail-001/pipeline.py
python tools/apprentice.py check retail-001
~~~

On Windows PowerShell, use `New-Item -ItemType Directory -Force submissions/retail-001` and `Copy-Item missions/retail-001/starter/pipeline.py submissions/retail-001/pipeline.py` instead of mkdir/cp if needed.

**The starter has deliberate bugs. The first test run should fail.**

Understand the failing tests and implement a correct version under `submissions/retail-001/pipeline.py`. Keep the original starter and grader unchanged.

Then:

~~~bash
git add submissions/retail-001/pipeline.py
git commit -m "fix(retail-001): validate and deduplicate daily orders"
git push -u origin mission/retail-001
~~~

Open a PR to `main`, link the mission issue, wait for CI, explain root cause, and request review.

## Required engineering evidence

- [ ] Actual failed output from the starter
- [ ] Explanation of the root cause and input contract
- [ ] Successful regression tests from your solution
- [ ] One additional edge-case test and why it matters
- [ ] Recovery behavior for duplicated/conflicting rows
- [ ] A short reflection: why binary floating-point is risky for money

## Open resources

- [Python CSV](https://docs.python.org/3/library/csv.html)
- [Python Decimal](https://docs.python.org/3/library/decimal.html)
- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [Git branching](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell)

If blocked, consult the [mentor hint policy](../../mentor/REVIEW_POLICY.md). Ask for one hint, not the full solution.
