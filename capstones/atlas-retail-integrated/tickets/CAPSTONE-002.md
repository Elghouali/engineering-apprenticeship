# CAPSTONE-002 — Recover a Kafka consumer without double revenue

**Role:** Streaming Engineer · **Status:** proposed ticket; no private integrated grader published yet.

**Incident:** The business event is committed in PostgreSQL, but the consumer crashes before committing its Kafka offset. The next process sees the event again.

**Acceptance intent:** Demonstrate one durable ledger entry per event ID, a separate inbox keyed by topic/partition/offset, detection of conflicting event payloads, and broker acknowledgement only after the DB transaction commits. Investigate rebalances, outbox patterns and what a multi-broker deployment would change.

**Deliverable:** a tested recovery change and a PR with a failure timeline. Never publish reference answers or actual payment information.

**Prerequisites:** [DATA-005](../../../missions/data-005/README.md). [← Capstone](../README.md).
