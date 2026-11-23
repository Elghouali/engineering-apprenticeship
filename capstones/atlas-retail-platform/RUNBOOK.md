# Atlas Retail — Operator Runbook for the Local Data Product

## Scope and limitations

This capstone is a teaching reference, not a production finance system. Synthetic records only. The reporting API is deliberately localhost-only; no public port binding, authentication service or cloud deployment exists.

## Expected invariants

- Every accepted order_id appears only once in the SQLite database.
- An exact repeated row increments the duplicate counter but never revenue.
- A conflicting later row for an existing valid order is quarantined.
- Cancelled orders remain in accepted records but do not contribute paid revenue.
- Gold revenue uses exact integer cents.
- A release has an immutable folder identified by source SHA-256 prefix, matching file checksums in its manifest.
- current.json is replaced only when publication succeeds.
- A stale source date can trigger an alert despite successful ingestion.

## Incident: A finance dashboard is stale

**Symptom:** a new job succeeded but the published latest_order_date is older than expected.

1. Run the status command with an explicit --as-of date in a reproducible test.
2. Verify the current release, including checksum and source provenance.
3. Identify whether the source file was late, the feed was empty, or an older partition was reprocessed.
4. Never mark a stale business date healthy because generated_at_utc is recent.
5. Reprocess a verified source in a new immutable release, update the pointer and rerun freshness status.
6. Record actual observed event dates and the expected freshness SLO. The fixture is intentionally historical.

## Incident: Quality gate fails during a new publication

**Symptom:** build raises quality_gate_failed.

1. Preserve the last known good current.json pointer.
2. Inspect rejected records and identify schema drift, missing fields or conflicting order IDs.
3. Fix the upstream feed or input contract—not the reject threshold without business approval.
4. Rerun build on the corrected source. Verify the release and read the Gold output.
5. Add the failure case to CI regression tests.

**Important:** a failed run may create output directories, but it must not change the published release pointer.

## Incident: Published artifact is corrupted

**Symptom:** verify raises artifact_checksum_mismatch and /v1/revenue returns HTTP 503.

1. Do not serve an unverified report or bypass checksum verification.
2. Isolate the corrupted release directory and compare trusted source SHA-256.
3. Rebuild into a clean release destination from known good input.
4. Confirm correct SQLite business totals and checksum validity before switching clients.
5. Document a new release ID and post-incident root cause.

## Failure drill

~~~bash
python capstones/atlas-retail-platform/platform.py build --source capstones/atlas-retail-platform/data/orders.csv --output capstones/atlas-retail-platform/output
python capstones/atlas-retail-platform/platform.py verify --output capstones/atlas-retail-platform/output
python capstones/atlas-retail-platform/platform.py status --output capstones/atlas-retail-platform/output --as-of 2026-11-27
~~~

The last command should report stale status with exit code 2; this is an intentional teaching signal, not an unexpected failure. The unit/integration test suite validates recovery cases in disposable directories.

## Production gap analysis

This reference deliberately does not implement production authentication, distributed locking, API autoscaling, cloud object storage, storage encryption policies, a managed database, complete metrics/traces or real backup/restore. Each is a future engineering task and must be validated before public claims of deployment readiness.
