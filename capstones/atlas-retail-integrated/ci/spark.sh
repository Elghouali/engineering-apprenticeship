#!/usr/bin/env bash
# Disposable local Spark-to-PostgreSQL/S3 integration; wipes demo volumes.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
cleanup() {
  docker compose --profile tools --profile spark --profile api down -v --remove-orphans || true
}
trap cleanup EXIT

docker compose up -d postgres kafka objectstore
docker compose build runner spark
docker compose run --rm runner demo
echo "Running real Spark transform on durable Postgres events..."
docker compose run --rm spark
echo "Replaying same Spark artifact; must be idempotent..."
docker compose run --rm spark
echo "PASS: Spark computed 22000 cents and published identical S3 Gold on replay"
