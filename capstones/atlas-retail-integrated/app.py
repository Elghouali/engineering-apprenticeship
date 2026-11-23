"""Atlas Retail integrated local demo: Kafka -> PostgreSQL -> S3 -> HTTP.

A deliberately constrained single-node lab, never a production payment service.
"""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
import time

from logic import validate_event


def events_for_date(business_date: str) -> list[dict]:
    """Deterministic synthetic replay fixture for an Airflow logical business date."""
    try:
        if type(business_date) is not str or date.fromisoformat(business_date).isoformat() != business_date:
            raise ValueError("invalid_business_date")
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid_business_date") from exc
    raw = json.loads(EVENTS.read_text(encoding="utf-8"))
    base_date = raw[0]["business_date"]
    normalized = []
    for event in raw:
        item = dict(event)
        item["business_date"] = business_date
        if business_date != base_date:
            item["event_id"] = f"{item['event_id']}-{business_date}"
        normalized.append(validate_event(item))
    return normalized

from storage import (open_postgres, prepare_db, store_message, load_events,
                     s3_client, publish_report, verify_report)

EVENTS = Path(__file__).parent / "data" / "events.json"


def retry(name: str, operation, attempts: int = 50, interval: float = 2.0):
    last = None
    for _ in range(attempts):
        try:
            return operation()
        except Exception as exc:
            last = exc
            time.sleep(interval)
    raise RuntimeError(f"{name}_not_ready") from last


def connect_db():
    return retry("postgres", open_postgres)


def connect_s3():
    def available():
        client = s3_client()
        client.list_buckets()
        return client
    return retry("objectstore", available)


def topic_admin():
    from kafka.admin import KafkaAdminClient
    return retry("kafka", lambda: KafkaAdminClient(
        bootstrap_servers=os.environ["ATLAS_KAFKA"],
        request_timeout_ms=3000, api_version_auto_timeout_ms=3000
    ))


def seed(business_date: str | None = None) -> dict:
    from kafka import KafkaProducer
    from kafka.admin import NewTopic
    from kafka.errors import TopicAlreadyExistsError

    business_date = business_date or os.environ["ATLAS_DATE"]
    events = events_for_date(business_date)
    topic = os.environ["ATLAS_TOPIC"]
    admin = topic_admin()
    try:
        try:
            admin.create_topics([
                NewTopic(name=topic, num_partitions=1, replication_factor=1)
            ])
        except TopicAlreadyExistsError:
            pass
    finally:
        admin.close()
    producer = KafkaProducer(
        bootstrap_servers=os.environ["ATLAS_KAFKA"],
        acks="all", retries=3,
        value_serializer=lambda value: json.dumps(
            value, sort_keys=True
        ).encode("utf-8"),
    )
    try:
        for event in events:
            producer.send(topic, value=event).get(timeout=20)
        producer.flush(timeout=20)
    finally:
        producer.close()
    return {"published_messages": len(events), "topic": topic, "business_date": business_date}


def consume(max_messages: int, fail_after_event: str | None = None) -> dict:
    from kafka import KafkaConsumer, TopicPartition
    from kafka.structs import OffsetAndMetadata

    if max_messages <= 0:
        raise ValueError("invalid_message_limit")
    with closing(connect_db()) as connection:
        prepare_db(connection)
        consumer = retry("kafka_consumer", lambda: KafkaConsumer(
            os.environ["ATLAS_TOPIC"],
            bootstrap_servers=os.environ["ATLAS_KAFKA"],
            group_id="atlas-retail-integrated-demo",
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            max_poll_records=1,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        ))
        totals = {"processed_messages": 0, "new_events": 0, "replayed_events": 0}
        deadline = time.monotonic() + 90
        try:
            while totals["processed_messages"] < max_messages and time.monotonic() < deadline:
                batches = consumer.poll(timeout_ms=1500, max_records=1)
                for records in batches.values():
                    for message in records:
                        created = store_message(
                            connection, message.value, message.topic,
                            message.partition, message.offset
                        )
                        # Intentionally raise AFTER the PostgreSQL transaction has
                        # committed but BEFORE acknowledging Kafka, to prove replay.
                        if created and message.value["event_id"] == fail_after_event:
                            raise RuntimeError("simulated_crash_after_db_commit")
                        tp = TopicPartition(message.topic, message.partition)
                        consumer.commit({
                            tp: OffsetAndMetadata(message.offset + 1, "", -1)
                        })
                        totals["processed_messages"] += 1
                        totals["new_events" if created else "replayed_events"] += 1
                        if totals["processed_messages"] >= max_messages:
                            break
            if totals["processed_messages"] != max_messages:
                raise RuntimeError("consumer_timeout")
            return totals
        finally:
            consumer.close()


def publish(business_date: str | None = None) -> dict:
    with closing(connect_db()) as conn:
        prepare_db(conn)
        return publish_report(conn, connect_s3(), business_date or os.environ["ATLAS_DATE"])


def verify(business_date: str | None = None) -> dict:
    with closing(connect_db()) as conn:
        prepare_db(conn)
        return verify_report(conn, connect_s3(), business_date or os.environ["ATLAS_DATE"])


def demo() -> dict:
    first = seed()
    consumed = consume(len(json.loads(EVENTS.read_text(encoding="utf-8"))))
    published = publish()
    verified = verify()
    return {"seed": first, "consume": consumed,
            "publish": published["publish_status"], "report": verified}


class API(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/health", "/v1/revenue"):
            self.send_error(404)
            return
        try:
            report = verify()
            result = (
                {"status": "ok", "report_verified": True}
                if self.path == "/health" else report
            )
            code = 200
        except Exception:
            # Do not leak internal configuration, passwords or tracebacks.
            result, code = {"status": "unavailable"}, 503
        body = json.dumps(result, sort_keys=True).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Integrated Atlas Retail lab")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("seed", "publish", "verify", "demo", "serve"):
        commands.add_parser(command)
    incoming = commands.add_parser("consume")
    incoming.add_argument("--max", type=int, default=7)
    incoming.add_argument("--fail-after-event")
    args = parser.parse_args()

    if args.command == "serve":
        # The container listens internally on all interfaces; Compose restricts
        # published host exposure to 127.0.0.1:18083 only.
        ThreadingHTTPServer(("0.0.0.0", 8080), API).serve_forever()
        return 0
    if args.command == "seed":
        result = seed()
    elif args.command == "consume":
        result = consume(args.max, args.fail_after_event)
    elif args.command == "publish":
        result = publish()
    elif args.command == "verify":
        result = verify()
    else:
        result = demo()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
