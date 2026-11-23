#!/usr/bin/env bash
# Disposable local-integration CI. Never run this against non-demo volumes.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
cleanup() {
  docker compose --profile api --profile tools down -v --remove-orphans || true
}
trap cleanup EXIT

docker compose up -d postgres kafka objectstore
docker compose build runner
docker compose run --rm runner seed

echo "Injecting real DB-commit-before-Kafka-ack crash..."
if docker compose run --rm runner consume --max 1 --fail-after-event evt-100; then
  echo "ERROR: expected intentional crash"
  exit 1
fi

echo "Replaying unacknowledged Kafka position..."
docker compose run --rm runner consume --max 7
docker compose run --rm runner publish
docker compose run --rm runner verify

echo "Replaying the entire source feed again; business totals must stay stable..."
docker compose run --rm runner demo
docker compose --profile api up -d api
python ci/smoke_http.py

echo "PASS: end-to-end Kafka -> PostgreSQL -> S3 -> HTTP and crash recovery"
