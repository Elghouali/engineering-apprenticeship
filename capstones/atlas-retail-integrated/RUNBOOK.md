# Integrated Atlas Retail — Incident and Recovery Runbook

[← Integrated capstone](README.md) · [Mission backlog](tickets/CAPSTONE-001.md)

**Scope:** disposable local Docker Compose test stack. No production credentials, billing account or real customer records.

## Incident triage order

1. Run `docker compose ps` from the capstone folder to identify stopped or unhealthy services.
2. Read `docker compose logs --tail=100 postgres kafka objectstore runner api` as appropriate; redact any sensitive data before sharing logs.
3. Inspect local API `http://127.0.0.1:18083/health`; a 503 means the report cannot be independently verified against business state.
4. Run `docker compose run --rm runner verify` to compare PostgreSQL totals with the S3 object.
5. If the database is not ready, check PostgreSQL readiness before attempting to replay messages; do not advance Kafka offsets without durable writes.
6. If the object store is unavailable, **do not** serve a cached unverified Gold report as healthy.

## Reproducing the critical crash

From a new, empty Compose stack:

~~~bash
docker compose up -d postgres kafka objectstore
docker compose build runner
docker compose run --rm runner seed
docker compose run --rm runner consume --max 1 --fail-after-event evt-100
~~~

The last command must exit nonzero **after inserting a durable business event but before acknowledging the offset**. Starting a new consumer with the same group and earliest fallback must replay the record without creating a second ledger row.

~~~bash
docker compose run --rm runner consume --max 7
docker compose run --rm runner publish
docker compose run --rm runner verify
~~~

Expected reported paid revenue: **22000 cents**, distinct event count **5**, paid event count **4**.

## Error classes and responses

| Symptom | Likely cause | Correct response |
| --- | --- | --- |
| `postgres_not_ready` | DB not started, bad DSN or wrong credentials | Fix the local service; do not acknowledge uncommitted messages |
| `kafka_not_ready` or consumer timeout | Broker/group/partition unavailable | Inspect bootstrap address and broker logs; retry safe consumer |
| `event_conflict` | Same event ID delivered with different financial payload | Stop and escalate; never overwrite an established payment blindly |
| `offset_conflict` | One Kafka offset maps to different payload | Reject, preserve durable state and investigate broker/source integrity |
| `published_partition_conflict` | Existing daily report differs from live ledger | Stop publication and review the backfill and ownership protocol |
| HTTP 503 | S3/DB/report mismatch or missing artifact | Fail closed and restore verified state; never treat HTTP reachability as data freshness |
| Unexpected increase in accepted events | Unique ID or transaction contract broken | Review inbox constraints and Kafka acknowledgments before replay |

## Restore without destroying evidence

For debugging, first save logs and synthetic fixture hashes; never run destructive commands blindly. Preserve the existing volume while investigating. If the whole lab is disposable and you want to restart from scratch, use `docker compose --profile api --profile tools down -v`, then seed again. The `-v` flag irreversibly removes the demo's database and object-store state.

## What this runbook does not claim

It does not specify a production DR RTO/RPO, multi-broker Kafka recovery, replica failover, KMS permissions, S3 version history, SLA compliance, a public ingress or production monitoring. Those are future company incidents and need their own evidence.

Official references: https://www.postgresql.org/docs/16/index.html · https://kafka.apache.org/44/documentation/ · https://github.com/seaweedfs/minio-compat
