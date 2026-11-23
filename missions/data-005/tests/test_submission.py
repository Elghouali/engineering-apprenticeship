"""Public Kafka semantics contract tests — durable SQLite, simulated redelivery."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SUBMISSION = Path(os.environ.get(
    "APPRENTICE_SUBMISSION_PATH",
    str(ROOT / "submissions" / "data-005" / "inbox.py")
))


def record(offset, event_id=None, account="acct-a", amount=100):
    return {"topic": "wallet-events", "partition": 0, "offset": offset,
            "event_id": event_id or f"ev-{offset}",
            "account_id": account, "delta_cents": amount}


class InboxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SUBMISSION.is_file():
            raise AssertionError("Missing data-005 submission")
        spec = importlib.util.spec_from_file_location("data005", SUBMISSION)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        cls.mod = mod

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "wallet.db"
        self.db = sqlite3.connect(self.path)
        self.addCleanup(lambda: self.db.close())
        self.mod.setup(self.db)
        self.acks = []

    def ack(self, topic, partition, offset):
        self.acks.append((topic, partition, offset))

    def balance(self):
        return self.db.execute(
            "SELECT COALESCE(SUM(delta_cents),0) FROM ledger"
        ).fetchone()[0]

    def test_first_batch_and_exact_replay(self):
        events = [record(0, amount=100), record(1, account="acct-b", amount=300)]
        first = self.mod.apply_messages(self.db, events, self.ack)
        self.assertEqual(first, {
            "new_events": 2, "replayed_events": 0,
            "balances_cents": {"acct-a": 100, "acct-b": 300}
        })
        second = self.mod.apply_messages(self.db, events, self.ack)
        self.assertEqual(second, {
            "new_events": 0, "replayed_events": 2,
            "balances_cents": {"acct-a": 100, "acct-b": 300}
        })
        self.assertEqual(self.balance(), 400)
        self.assertEqual(len(self.acks), 4)

    def test_crash_after_db_commit_before_ack_then_reconnect(self):
        with self.assertRaisesRegex(RuntimeError, "simulated_crash"):
            self.mod.apply_messages(self.db, [record(3)], self.ack,
                                    crash_after_event="ev-3")
        self.assertEqual(self.balance(), 100)
        self.assertEqual(self.acks, [])
        self.db.close()
        self.db = sqlite3.connect(self.path)
        self.mod.setup(self.db)
        res = self.mod.apply_messages(self.db, [record(3)], self.ack)
        self.assertEqual(res["new_events"], 0)
        self.assertEqual(res["replayed_events"], 1)
        self.assertEqual(self.balance(), 100)
        self.assertEqual(self.acks, [("wallet-events", 0, 3)])

    def test_different_offset_same_event_id(self):
        first = record(0, "same", amount=15)
        replay = record(42, "same", amount=15)
        self.mod.apply_messages(self.db, [first], self.ack)
        result = self.mod.apply_messages(self.db, [replay], self.ack)
        self.assertEqual(result["replayed_events"], 1)
        self.assertEqual(self.balance(), 15)

    def test_conflicts_roll_back_and_are_not_acknowledged(self):
        self.mod.apply_messages(self.db, [record(0, "keep")], self.ack)
        before = len(self.acks)
        with self.assertRaisesRegex(ValueError, "offset_conflict"):
            self.mod.apply_messages(self.db, [record(0, "wrong")], self.ack)
        with self.assertRaisesRegex(ValueError, "event_conflict"):
            self.mod.apply_messages(self.db, [record(1, "keep", amount=101)], self.ack)
        self.assertEqual(self.balance(), 100)
        self.assertEqual(before, len(self.acks))

    def test_invalid_message_no_effect(self):
        for item in [
            record(0, amount=0), record(0, amount=True),
            record(-1), {**record(0), "topic": ""},
            {**record(0), "partition": -1},
        ]:
            with self.subTest(item=item):
                with self.assertRaisesRegex(ValueError, "invalid_message"):
                    self.mod.apply_messages(self.db, [item], self.ack)
        self.assertEqual(self.balance(), 0)
        self.assertEqual(self.acks, [])

    def test_ack_failure_keeps_durable_event(self):
        def no_ack(*args):
            raise ConnectionError("broker unavailable")
        with self.assertRaises(ConnectionError):
            self.mod.apply_messages(self.db, [record(7)], no_ack)
        self.assertEqual(self.balance(), 100)
        replay = self.mod.apply_messages(self.db, [record(7)], self.ack)
        self.assertEqual(replay["replayed_events"], 1)
        self.assertEqual(self.balance(), 100)

    def test_uniqueness_in_schema_and_idempotent_setup(self):
        self.mod.setup(self.db)
        self.mod.apply_messages(self.db, [record(0)], self.ack)
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db:
                self.db.execute(
                    "INSERT INTO ledger(event_id,account_id,delta_cents)"
                    " VALUES (?,?,?)", ("ev-0", "acct-a", 100)
                )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db:
                self.db.execute(
                    "INSERT INTO inbox(topic,partition,offset,event_id)"
                    " VALUES (?,?,?,?)", ("wallet-events", 0, 0, "ev-0")
                )


if __name__ == "__main__":
    unittest.main()
