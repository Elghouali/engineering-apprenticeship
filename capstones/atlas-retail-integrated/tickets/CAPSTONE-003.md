# CAPSTONE-003 — Bring Spark into the shared data platform

**Role:** Data Engineer · **Status:** planned, not a finished Spark capstone implementation.

**Incident:** Increasing daily reporting volume makes direct single-process aggregation a bottleneck. One merchant dominates a shuffle stage; event replay also creates duplicates.

**Acceptance intent:** Read a durable snapshot from the PostgreSQL stage (or an immutable, verified landing artifact), transform it using a real local Spark session, compare exact integer-cent results to business state and export a provenance-aware Gold artifact. Measure physical plans and task time; do not invent a speedup.

**Deliverable:** tested PySpark transformation with repeatable performance comparison, input/output lineage and operational recovery notes. Scaling/failure test must run independently before the ticket becomes ready.

**Prerequisites:** [DATA-004](../../../missions/data-004/README.md) and [CAPSTONE-001](CAPSTONE-001.md). [← Capstone](../README.md).
