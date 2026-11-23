#!/usr/bin/env bash
# Disposable integrated DAG test, not a long-running scheduler proof.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
cleanup() {
  docker compose --profile airflow --profile tools --profile api down -v --remove-orphans || true
}
trap cleanup EXIT

docker compose up -d postgres kafka objectstore
docker compose build airflow runner
docker compose --profile airflow run --rm airflow bash -c '
  airflow db migrate &&
  airflow dags list &&
  airflow dags test atlas_integrated_pipeline 2026-11-20
'
docker compose run --rm runner verify
echo "PASS: Airflow 3 ran real Kafka -> PostgreSQL -> S3 -> verification tasks"
