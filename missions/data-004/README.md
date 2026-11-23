# DATA-004 — Skewed Spark aggregation overwhelms one worker

> **PRE-RELEASE / PROTOTYPE — contract v1.** This exercise has a public grader and a confidential correct reference, but independent first-time learner onboarding has not yet passed.

**Company:** Atlas Retail · **Role:** Data Engineer · **Prerequisite:** RETAIL-003

## The workplace incident

Finance added 10 million transaction events. Most merchants have normal traffic, but one huge merchant dominates the groupBy stage. The job's last shuffle task runs far longer than the rest. A bad retry also doubled paid revenue for a few event IDs.

You must **measure a real Spark plan**, identify the skew, and deliver a correct salting/replay-safe aggregation. Do not promise a speedup without a measured benchmark.

## Contract

Implement these functions in your branch's submission:

~~~python
recommend_buckets(stats: dict[str, int], target_rows_per_partition: int = 1000) -> dict
aggregate_paid_revenue(df, salt_buckets: int = 4) -> DataFrame
~~~

The partition plan returns exactly:
- heavy_keys: lexicographically sorted merchant names with count **strictly greater** than twice target_rows_per_partition
- salt_buckets: mapping of each heavy merchant to min(16, ceil(count / target_rows_per_partition))
- num_partitions: max(1, min(64, ceil(total_rows / target_rows_per_partition)))

Reject invalid stats, negative counts, booleans and zero/noninteger targets with ValueError("invalid_stats").

The PySpark transformation accepts a DataFrame with event_id, merchant_id, amount_cents and status. The output has merchant_id and paid_revenue_cents, one row per merchant. Requirements:

1. Only paid events contribute revenue; cancelled events contribute zero.
2. Exact replayed events with the same event_id must not double-count.
3. Different payloads with the same event_id are a conflict; raise ValueError("conflicting_event_id").
4. Keep all valid merchants including merchants with only cancelled events (zero revenue).
5. Implement a deterministic salted partial aggregation and merge final groups; explain key skew.
6. Never call DataFrame.collect() or toPandas() to process the full business dataset in the implementation.
7. No Python UDFs or floating-point money. salt_buckets must be an integer from 1 to 32.

The starter is intentionally buggy and lacks replay handling.

## How a learner will work *after launch*

~~~bash
git switch -c mission/data-004
python tools/apprentice.py start data-004
python tools/apprentice.py check data-004
~~~

The standard-library partition planner tests run without Spark. For the actual Spark transformation you need Python 3.11+, Java 17+, and an installed compatible PySpark (e.g. 4.0.3):

~~~bash
python -m pip install pyspark==4.0.3
# Linux/macOS:
SPARK_LIVE=1 python tools/apprentice.py check data-004
# Windows PowerShell:
# $env:SPARK_LIVE = "1"; python tools/apprentice.py check data-004
~~~

A valid PySpark version and Java runtime are required for SPARK_LIVE=1. The dedicated private validation workflow uses a real local Spark session; no cloud resources are provisioned.

**Measured maintainer evidence:** see the [Spark Skew Benchmark Report](../../docs/SPARK_BENCHMARK_EVIDENCE.md). A controlled comparison with the same replay checks showed no clear benefit from salting on an 80,000-row fixture. Your PR should explain when the technique is justified instead of promising faster execution.

## Engineering evidence

- [ ] Screenshot or copied text of actual input skew counts and physical plan.
- [ ] Explain shuffle, partition imbalance, salting and why duplicate event IDs matter.
- [ ] Validate financial correctness before investigating speed.
- [ ] Benchmark baseline vs corrected implementation using identical input, hardware, cache/warm-up and repeated runs. State measured results only.
- [ ] PR includes regression tests and trade-offs (extra shuffle, salt overhead, skew thresholds).
- [ ] Incident report with observed failure and recovery.

**Official references:** https://spark.apache.org/docs/4.0.3/sql-performance-tuning.html and https://spark.apache.org/docs/4.0.3/api/python/getting_started/install.html

**Status:** prototype. A correct public mission contract is not proof of measured production scalability.

---

## Mission handoff: from incident to pull request

**Requirements:** Python 3.11+ for planner tests; live Spark tests require Java 17, compatible PySpark and SPARK_LIVE=1. Read the contract above before changing code.

**Training files:** [faulty starter](starter/spark_job.py) · [public acceptance tests](tests/test_submission.py) · personal output: `submissions/data-004/spark_job.py` (created only in a learner fork, not committed upstream).

From the **root of your own fork**, after public launch:

```bash
git switch -c mission/data-004
python tools/apprentice.py start data-004
python tools/apprentice.py check data-004
```

The first test run must fail because the starter is intentionally defective. Implement and test only in your submission; do not edit official graders. Push to your fork and open a PR **against your own fork's main branch**, not the academy upstream.

**Failure-recovery drill:** Compare replay-safe aggregation with and without salting. Never claim speedup without measuring.

In your PR, demonstrate **Explain / Build / Recover / Defend**: root cause, passing regression checks, recovery behavior and trade-offs. See the [review rubric](../../docs/ENGINEERING_LOOP.md) and [hint policy](../../mentor/REVIEW_POLICY.md).

**Continue to:** [DATA-006](../data-006/README.md). These are suggestions; use the [catalog](../catalog.json) for exact prerequisites.

[← All missions](../README.md) · [Academy](../../README.md) · [Company](../../companies/atlas-retail/README.md) · [Documentation](../../docs/README.md)
