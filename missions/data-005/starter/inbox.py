"""DATA-005 intentionally unsafe starter: acknowledges too soon, credits twice."""
import sqlite3


def setup(db: sqlite3.Connection) -> None:
    db.execute("CREATE TABLE IF NOT EXISTS ledger (id INTEGER PRIMARY KEY, event_id TEXT, account_id TEXT, delta_cents INTEGER)")


def apply_messages(db, messages, acknowledge, crash_after_event=None):
    new_events = 0
    for msg in messages:
        # BUG: acknowledging before durable DB writes can lose messages.
        acknowledge(msg["topic"], msg["partition"], msg["offset"])
        with db:
            db.execute(
                "INSERT INTO ledger(event_id,account_id,delta_cents) VALUES (?,?,?)",
                (msg["event_id"], msg["account_id"], msg["delta_cents"])
            )
        new_events += 1
        if msg["event_id"] == crash_after_event:
            raise RuntimeError("simulated_crash")
    balances = {
        row[0]: row[1] for row in db.execute(
            "SELECT account_id, SUM(delta_cents) FROM ledger GROUP BY account_id"
        )
    }
    return {"new_events": new_events, "replayed_events": 0, "balances_cents": balances}
