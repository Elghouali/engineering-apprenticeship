# CAPSTONE-003 — Bring Spark into the shared data platform

**Role:** Data Engineer · **Status:** pre-release change request. A bounded real Spark-to-PostgreSQL/S3 baseline exists; scalable source ingestion and benchmarking remain to be built.

**Incident:** The current real Spark bridge first collects a maximum 1,000 PostgreSQL rows into the Spark driver. Increasing daily volume will exceed the safety bound and stop processing. One merchant may also dominate a shuffle stage.

**Acceptance intent:** Read a durable snapshot from the PostgreSQL stage (or an immutable, verified landing artifact), transform it using a real local Spark session, compare exact integer-cent results to business state and export a provenance-aware Gold artifact. Measure physical plans and task time; do not invent a speedup.

**Deliverable:** tested PySpark transformation with repeatable performance comparison, input/output lineage and operational recovery notes. Scaling/failure test must run independently before the ticket becomes ready.

**Prerequisites:** [DATA-004](../../../missions/data-004/README.md) and [CAPSTONE-001](CAPSTONE-001.md). [← Capstone](../README.md).
