"""Real localhost Kafka smoke test for DATA-005.

An intentionally crashed consumer commits the SQLite ledger transaction but
never acknowledges Kafka. The next consumer must replay safely. No public
cloud resources and no network listener beyond loopback.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import time
import uuid

from kafka import KafkaAdminClient, KafkaConsumer, KafkaProducer, TopicPartition
from kafka.admin import NewTopic
from kafka.structs import OffsetAndMetadata

ROOT = Path(__file__).resolve().parents[3]


def load_solution(path: Path):
    spec = importlib.util.spec_from_file_location("kafka_mission_solution", path.resolve())
    if spec is None or spec.loader is None:
        raise RuntimeError("Missing a submission module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def wait_for_broker(bootstrap: str, timeout_seconds: int = 120):
    deadline = time.monotonic() + timeout_seconds
    last_error = None
    while time.monotonic() < deadline:
        try:
            client = KafkaAdminClient(
                bootstrap_servers=bootstrap, request_timeout_ms=3000,
                api_version_auto_timeout_ms=3000
            )
            return client
        except Exception as exc:
            last_error = exc
            time.sleep(1)
    raise RuntimeError(f"Kafka broker not ready before timeout: {last_error}")


def consume_one(consumer: KafkaConsumer, deadline: float):
    while time.monotonic() < deadline:
        chunks = consumer.poll(timeout_ms=1000, max_records=1)
        for records in chunks.values():
            if records:
                return records[0]
    raise RuntimeError("No Kafka record received before deadline")


def normalize(record):
    payload = record.value
    return {
        "topic": record.topic,
        "partition": record.partition,
        "offset": record.offset,
        "event_id": payload["event_id"],
        "account_id": payload["account_id"],
        "delta_cents": payload["delta_cents"],
    }


def run(module_path: Path, bootstrap: str):
    solution = load_solution(module_path)
    admin = wait_for_broker(bootstrap)
    ident = uuid.uuid4().hex[:12]
    topic, group = "academy-wallet-" + ident, "academy-consumer-" + ident
    producer = None
    first_consumer = None
    second_consumer = None
    try:
        admin.create_topics([NewTopic(
            name=topic, num_partitions=1, replication_factor=1
        )])
        producer = KafkaProducer(
            bootstrap_servers=bootstrap,
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            acks="all", retries=3
        )
        values = [
            {"event_id": "payment-1", "account_id": "acct-a", "delta_cents": 100},
            {"event_id": "payment-2", "account_id": "acct-b", "delta_cents": 250},
            {"event_id": "payment-1", "account_id": "acct-a", "delta_cents": 100},
        ]
        for payload in values:
            producer.send(topic, value=payload).get(timeout=20)
        producer.flush(timeout=20)

        def new_consumer():
            instance = KafkaConsumer(
                bootstrap_servers=bootstrap,
                group_id=group, auto_offset_reset="earliest",
                enable_auto_commit=False,
                value_deserializer=lambda blob: json.loads(blob.decode("utf-8")),
                max_poll_records=1
            )
            instance.subscribe([topic])
            return instance

        first_consumer = new_consumer()
        first_record = consume_one(first_consumer, time.monotonic() + 45)
        if first_record.offset != 0:
            raise AssertionError("Expected first record at offset 0")

        with tempfile.TemporaryDirectory() as tmp:
            db = sqlite3.connect(Path(tmp) / "inbox.db")
            try:
                solution.setup(db)
                first_acks = []

                def early_ack(topic_name, partition, offset):
                    first_acks.append((topic_name, partition, offset))

                try:
                    solution.apply_messages(
                        db, [normalize(first_record)], early_ack,
                        crash_after_event="payment-1"
                    )
                except RuntimeError as exc:
                    if str(exc) != "simulated_crash":
                        raise
                else:
                    raise AssertionError("Crash injection did not happen")
                if first_acks:
                    raise AssertionError("Offset was acknowledged before crash")

                count = db.execute("SELECT COUNT(*) FROM ledger").fetchone()[0]
                if count != 1:
                    raise AssertionError("Crash did not persist exactly one business event")
                first_consumer.close()
                first_consumer = None

                second_consumer = new_consumer()

                def ack(topic_name, partition, offset):
                    tp = TopicPartition(topic_name, partition)
                    second_consumer.commit({tp: OffsetAndMetadata(offset + 1, "", -1)})

                replay = consume_one(second_consumer, time.monotonic() + 45)
                if replay.offset != first_record.offset:
                    raise AssertionError("Consumer did not replay uncommitted offset")
                result = solution.apply_messages(db, [normalize(replay)], ack)
                if result["new_events"] != 0 or result["replayed_events"] != 1:
                    raise AssertionError("Replay changed the durable ledger")
                for expected in (1, 2):
                    event = consume_one(second_consumer, time.monotonic() + 45)
                    if event.offset != expected:
                        raise AssertionError("Unexpected Kafka offset")
                    solution.apply_messages(db, [normalize(event)], ack)
                ledger = dict(db.execute(
                    "SELECT account_id, SUM(delta_cents) "
                    "FROM ledger GROUP BY account_id"
                ).fetchall())
                if ledger != {"acct-a": 100, "acct-b": 250}:
                    raise AssertionError(f"Ledger was double credited: {ledger}")
                tp = TopicPartition(topic, 0)
                if second_consumer.committed(tp) != 3:
                    raise AssertionError("Broker offset was not durably committed")
                print("PASS: actual Kafka offset 0 replayed after DB commit; "
                      "consumer committed offset 3; ledger has 2 unique events")
            finally:
                db.close()
    finally:
        if first_consumer is not None:
            first_consumer.close()
        if second_consumer is not None:
            second_consumer.close()
        if producer is not None:
            producer.close()
        admin.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", type=Path, required=True)
    parser.add_argument("--bootstrap", default="127.0.0.1:9092")
    args = parser.parse_args()
    run(args.module, args.bootstrap)


if __name__ == "__main__":
    main()
