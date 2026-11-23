#!/usr/bin/env bash
# Disposable Airflow 3 full DAG execution on two dates + replay; wipes demo volumes.
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
  airflow dags test atlas_integrated_pipeline 2026-11-20T02:00:00+00:00 &&
  airflow dags test atlas_integrated_pipeline 2026-11-21T02:00:00+00:00 &&
  airflow dags test atlas_integrated_pipeline 2026-11-20T02:00:00+00:00
'
docker compose run --rm -e ATLAS_DATE=2026-11-20 runner verify
docker compose run --rm -e ATLAS_DATE=2026-11-21 runner verify
echo "PASS: Airflow ran two isolated logical dates and replay on shared Kafka/PostgreSQL/S3"
