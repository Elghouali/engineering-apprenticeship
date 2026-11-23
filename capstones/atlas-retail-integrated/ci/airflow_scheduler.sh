#!/usr/bin/env bash
# Bounded *scheduler-managed* integration backfill, not just airflow dags test.
# Airflow standalone runs its scheduler and API only inside a disposable network.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
container="atlas-integrated-scheduler"
cleanup() {
  docker rm -f "$container" >/dev/null 2>&1 || true
  docker compose --profile airflow --profile tools down -v --remove-orphans || true
}
trap cleanup EXIT

docker compose up -d postgres kafka objectstore
docker compose build airflow runner
docker compose --profile airflow run -d --name "$container" airflow standalone

echo "Waiting for standalone Airflow API and Dag processor..."
ready=0
for attempt in $(seq 1 100); do
  if docker exec "$container" airflow dags list -o plain 2>/dev/null | grep -q atlas_integrated_pipeline; then
    ready=1
    break
  fi
  sleep 3
done
[ "$ready" = 1 ] || { docker logs --tail=120 "$container"; echo "Airflow not ready"; exit 1; }

docker exec "$container" airflow dags unpause atlas_integrated_pipeline
docker exec "$container" airflow backfill create \
  --dag-id atlas_integrated_pipeline \
  --from-date 2026-11-20T02:00:00+00:00 \
  --to-date 2026-11-21T02:00:00+00:00 \
  --max-active-runs 1 \
  --reprocess-behavior none

echo "Waiting for both historical DagRuns to succeed through the scheduler..."
completed=0
for attempt in $(seq 1 100); do
  if docker exec "$container" airflow dags list-runs atlas_integrated_pipeline -o json > /tmp/atlas-backfill-state.json 2>/dev/null; then
    if python - <<'PY'
import json
from pathlib import Path
items=json.loads(Path("/tmp/atlas-backfill-state.json").read_text())
if isinstance(items, dict):
    items=items.get("dag_runs",items.get("dagRuns",[]))
matching=[v for v in items if "2026-11-20" in str(v.get("logical_date",v.get("execution_date",""))) or
                          "2026-11-21" in str(v.get("logical_date",v.get("execution_date","")))]
assert len(matching)>=2, matching
assert all(v.get("state")=="success" for v in matching), matching
PY
    then
      completed=1
      break
    fi
  fi
  sleep 3
done
if [ "$completed" != 1 ]; then
  cat /tmp/atlas-backfill-state.json || true
  docker logs --tail=130 "$container"
  exit 1
fi
docker compose run --rm -e ATLAS_DATE=2026-11-20 runner verify
docker compose run --rm -e ATLAS_DATE=2026-11-21 runner verify
echo "PASS: two actual scheduler-managed backfill partitions verified on shared Kafka/PostgreSQL/S3"
