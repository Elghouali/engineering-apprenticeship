# CAPSTONE-001 — Accept a complete Atlas Retail data release

**Fictional employer:** Atlas Retail · **Role:** Junior Data Engineer · **Status:** proposed public capstone ticket, not yet graded.

### Business request

Finance needs proof that seven Kafka deliveries represent five unique business events and exactly 22,000 cents of paid revenue. The API must never report healthy when the durable ledger and published object disagree.

### Evidence expected from a learner PR

- Reproduce the baseline from a fresh fork and attach the *actual* failed/healthy states.
- Document the Kafka → PostgreSQL → object storage → HTTP lineage.
- Write an additional negative regression test without modifying official acceptance criteria.
- Explain cancelled transactions, exact duplicates and conflicting event IDs.
- Verify recovery in an ephemeral environment; provide a runbook excerpt.

**Prerequisites:** RETAIL-001, RETAIL-002, CLOUD-002 and [GitHub Field Guide](../../../docs/GITHUB_WORKFLOW.md). [← Capstone](../README.md).
