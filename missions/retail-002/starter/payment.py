"""RETAIL-002 deliberately broken starter: retrying inserts duplicate payments."""
import sqlite3


def setup(db: sqlite3.Connection) -> None:
    db.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            request_id TEXT,
            order_id TEXT,
            amount_cents INTEGER
        )
    """)


def record_payment(db: sqlite3.Connection, request_id: str,
                   order_id: str, amount_cents: int) -> dict:
    # The missing unique constraint and idempotency check are the incident.
    with db:
        cursor = db.execute(
            "INSERT INTO payments(request_id,order_id,amount_cents) VALUES (?,?,?)",
            (request_id, order_id, amount_cents),
        )
    return {"status": "created", "payment_id": cursor.lastrowid}
