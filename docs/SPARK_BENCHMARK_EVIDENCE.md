# DATA-004 — Measured Skew Benchmark and Its Limits

**Maintainer experiment, 2026-11-23.** This is evidence from a single GitHub-hosted Ubuntu job, **not** a guaranteed speedup, performance certification or substitute for independent learner benchmarking.

## Workload

- Apache Spark 4.0.3, Java 17, local[4], adaptive execution disabled, eight shuffle partitions
- 80,000 deterministic synthetic events, one distinct event ID per record
- 95% of events belong to merchant "whale"; the remaining 5% span five small merchants
- Amount: 100 integer cents per event; results checked for complete equality
- Memory/disk-cached input; plan strings captured from Spark's JVM execution plan
- Three timed runs per approach with alternating execution order, after correctness actions warmed the engine

## Observed timings (seconds)

| Approach | Run 1 | Run 2 | Run 3 | Median |
| --- | ---: | ---: | ---: | ---: |
| Standard Spark groupBy (no replay validation) | 0.2115 | 0.1166 | 0.1601 | **0.1601** |
| Replay-safe aggregation, salt=1 | 1.2534 | 1.0575 | 0.9718 | **1.0575** |
| Replay-safe aggregation, salt=8 | 1.1290 | 1.2321 | 0.9471 | **1.1290** |

**Interpretation:** the controlled comparison is **salt=1 vs salt=8**, because both share the same replay validation and aggregation code. Eight-way salting was approximately **6.8% slower** by median for this small test (1.1290 / 1.0575 ≈ 1.068). Three noisy local runs are insufficient to establish a robust performance difference.

The naive standard groupBy is much faster, but it **does not verify event conflicts or replay safety**. Comparing it directly to the replay-safe implementation confounds correctness checks with salting overhead. Do not call the ratio an effect of salting.

## Why the result makes engineering sense

Many distributed aggregations use mapper-side partial aggregation, which may already limit skew damage. Salting adds a column and another group/merge step. It can help certain imbalanced workloads but is not universally beneficial. Inspect stage/task durations and actual shuffle behavior before optimizing.

For professional-grade evidence, rerun on a much larger, realistic dataset, keep correctness work identical, collect multiple benchmark runs, compare memory and spill metrics, and record Spark physical plans and task-duration distributions. Never infer a speedup just because a feature sounds advanced.

## Where evidence lives

The confidential maintainer CI runs a public-contract-verified implementation against this workload. It prints the physical plan and timings in its log, but does not disclose the reference solution source. The task is documented publicly so learners can design their own independent benchmark.

**Related assignment:** [DATA-004](../missions/data-004/README.md).

**References:** https://spark.apache.org/docs/4.0.3/sql-performance-tuning.html
