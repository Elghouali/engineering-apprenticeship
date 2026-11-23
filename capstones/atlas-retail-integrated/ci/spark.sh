#!/usr/bin/env bash
# Disposable real Spark/JDBC/PostgreSQL/S3 smoke; permanently deletes demo volumes.
# The scaled fixture has >1000 source events so the old driver snapshot cannot pass.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
cleanup() {
  docker compose --profile tools --profile spark --profile api down -v --remove-orphans || true
}
trap cleanup EXIT

run_checked() {
  local business_date="$1" expected_count="$2" expected_state="$3"
  local output
  output="$(docker compose run --rm -e ATLAS_DATE="$business_date" spark)"
  echo "$output"
  echo "$output" | grep -F '"source": "postgresql_partitioned_jdbc"'
  echo "$output" | grep -F '"jdbc_partitions": 4'
  echo "$output" | grep -F "\"accepted_events\": $expected_count"
  echo "$output" | grep -F "\"publish_status\": \"$expected_state\""
  echo "$output" | grep -F '"verified_against_postgres": true'
  echo "$output" | grep -F 'ATLAS_SPARK_PHYSICAL_PLAN_START'
}

docker compose up -d postgres kafka objectstore
docker compose build runner spark
docker compose run --rm runner demo

echo "Verifying fixture day: partitioned Spark JDBC -> PostgreSQL parity -> S3..."
run_checked 2026-11-20 5 created
run_checked 2026-11-20 5 replayed

echo "Inserting 2403 synthetic durable ledger events for a second date..."
docker compose run --rm --entrypoint python runner /app/seed_scale.py

echo "Verifying >1000 rows without loading raw events into the driver..."
run_checked 2026-11-21 2403 created
run_checked 2026-11-21 2403 replayed

echo "PASS: JDBC partitioning, physical plan, SQL parity and immutable replay for both dates"
