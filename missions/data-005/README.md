# DATA-005 — Kafka replay duplicates wallet credits after a consumer crash

**Company:** Atlas Retail · **Role:** Streaming Data Engineer · **Prerequisite:** RETAIL-002

## Production-style incident

A consumer writes a payment event to the ledger but crashes **before** committing the Kafka offset. Kafka delivers the record again. The original code grants wallet credit twice and acknowledges messages too early.

Your job is to build a durable **SQLite inbox + ledger** and establish the correct order: validate -> DB transaction commit -> acknowledge broker offset. The SQLite checkpoint is not a Kafka offset commit.

## Contract

Implement:

~~~python
setup(db: sqlite3.Connection) -> None
apply_messages(
    db: sqlite3.Connection,
    messages: list[dict],
    acknowledge: Callable[[str, int, int], None],
    crash_after_event: str | None = None
) -> dict
~~~

Each message has: topic (nonempty string), partition (int >= 0), offset (int >= 0), event_id (nonempty string), account_id (nonempty string), delta_cents (positive integer).

- In one SQLite transaction per message, persist the inbox topic/partition/offset and add the event exactly once to the ledger.
- Enforce unique (topic, partition, offset) in the inbox and unique event_id in the ledger.
- Exact delivery replay must not add balance again. An event ID repeated at a *different* offset with matching account/amount is also replay-safe.
- Identical offset with a different event ID raises ValueError("offset_conflict").
- Existing event ID with a different account or amount raises ValueError("event_conflict").
- Invalid messages raise ValueError("invalid_message") and must not acknowledge or change the DB.
- After durable DB commit, call acknowledge(topic, partition, offset), including for safe replays.
- When crash_after_event equals a newly committed event, raise RuntimeError("simulated_crash") **after the DB commit but before acknowledgement**.
- A failed acknowledgement propagates the exception, but the DB state must stay committed so redelivery is safe.
- Return {"new_events": int, "replayed_events": int, "balances_cents": {account_id: sum}} for a successful batch, with account keys sorted.
- setup is safe to run repeatedly. Never use floating-point money.

## Failure drill and learner workflow

~~~bash
git switch -c mission/data-005
python tools/apprentice.py start data-005
python tools/apprentice.py check data-005
~~~

The base grader simulates a real crash/replay boundary against persistent SQLite. **Optional real broker integration** is available in this repository; it should not be called verified until executed.

~~~bash
# From missions/data-005:
docker compose up -d
python -m pip install -r requirements-kafka.txt
# From the repository root, after starting a personal mission branch:
python tools/apprentice.py start data-005
python missions/data-005/tools/broker_smoke.py --module submissions/data-005/inbox.py
# Cleanup:
docker compose -f missions/data-005/docker-compose.yml down
~~~

The local broker binds only to 127.0.0.1. The smoke harness produces synthetic events to a unique topic, crashes after SQLite commit but before broker acknowledgement, restarts with the same group, checks the replayed offset and verifies the final ledger and committed Kafka offset. Use a dedicated local environment: the harness executes the provided Python submission.

Do not claim that running unit tests is the same as verifying live Kafka semantics.

## Engineer's PR must explain

1. Why at-least-once delivery means duplicates are normal.
2. The difference between SQLite durability and Kafka offset acknowledgements.
3. Why committing the broker offset before the DB write can lose events.
4. What changes when partitions rebalance, and how event IDs enforce idempotence.
5. How the inbox/ledger approach differs from Kafka transactions and outbox design.

**Official references:** https://kafka.apache.org/documentation/#semantics and https://www.sqlite.org/lang_transaction.html

**Status:** prototype. The broker smoke harness has now passed in maintainer CI against a real local Apache Kafka Docker broker and confidential reference solution. This verifies a single-node, one-partition crash/replay test, **not** a production multi-broker deployment, partition rebalance exercise or independent learner submission.
