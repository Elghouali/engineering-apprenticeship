# CAPSTONE-003 — Bring Spark into the shared data platform

**Role:** Data Engineer · **Status:** pre-release change request. A real four-partition Spark JDBC source is verified at 2,403 events; repeatable performance benchmarks, shared snapshot consistency and learner acceptance remain open.

**Incident:** The previous Spark bridge collected at most 1,000 PostgreSQL rows on the driver. The maintained baseline now uses partitioned JDBC and has passed a 2,403-event synthetic fixture. The remaining incident concerns skew, repeated performance comparison, consistent snapshots, recovery under failure and much larger data volumes.

**Acceptance intent:** Read a durable snapshot from the PostgreSQL stage (or an immutable, verified landing artifact), transform it using a real local Spark session, compare exact integer-cent results to business state and export a provenance-aware Gold artifact. Measure physical plans and task time; do not invent a speedup.

**Delivered platform baseline (maintainer CI, 2026-11-23):** partitioned Spark JDBC reads, a PostgreSQL SQL parity oracle, deterministic S3 provenance, four physical plans, five-event and 2,403-event created/replayed outputs. [Evidence](../../../docs/INTEGRATED_CAPSTONE_EVIDENCE.md).

**Still required from this ticket:** repeated multi-size/partition-count benchmark including Spark physical plans, measured skew under a dominant merchant, failed-read/recovery evidence, immutable or consistent cross-connection source snapshot, and independent learner acceptance. This is **not** ready for release as a fully solved learner mission.

**Prerequisites:** [DATA-004](../../../missions/data-004/README.md) and [CAPSTONE-001](CAPSTONE-001.md). [← Capstone](../README.md).
