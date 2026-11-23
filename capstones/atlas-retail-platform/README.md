# Capstone — Atlas Retail Data Product (working reference system)

**Status:** Runnable local reference application and integration-test target; this is NOT a claimed cloud deployment.

Build a small but real end-to-end retail data product:

~~~mermaid
flowchart LR
    CSV["Daily order CSV"] --> VALIDATE["Validate + deduplicate"]
    VALIDATE --> QUARANTINE["Rejected rows CSV"]
    VALIDATE --> DB["SQLite accepted orders"]
    DB --> GOLD["Revenue by date CSV"]
    GOLD --> MANIFEST["SHA-256 release manifest"]
    DB --> MANIFEST
    MANIFEST --> POINTER["Atomic current.json pointer"]
    POINTER --> STATUS["Freshness + recovery checks"]
~~~

## Run locally (Python 3.11+; no dependencies)

From the repository root:

~~~bash
python capstones/atlas-retail-platform/platform.py build \
  --source capstones/atlas-retail-platform/data/orders.csv \
  --output capstones/atlas-retail-platform/output

python capstones/atlas-retail-platform/platform.py verify \
  --output capstones/atlas-retail-platform/output

python capstones/atlas-retail-platform/platform.py status \
  --output capstones/atlas-retail-platform/output \
  --as-of 2026-11-21 --max-age-days 1

python -m unittest discover -s capstones/atlas-retail-platform/tests -v
~~~

The fixture has **8 synthetic records** dated 2026-11-20: **4 accepted orders**, **1 exact replay duplicate**, **3 rejects**, and **22000 cents of paid revenue**. It is intentionally historical; a freshness check using today's date can report stale data. Use --as-of to reproduce expected on-call states.

## Serve the verified Gold report over HTTP

After building the release, start a local read-only reporting API:

~~~bash
python capstones/atlas-retail-platform/api.py --output capstones/atlas-retail-platform/output --port 8081
~~~

Local endpoints:

- http://127.0.0.1:8081/health — checks artifact integrity, returns a release ID
- http://127.0.0.1:8081/v1/revenue — returns typed Gold revenue rows
- http://127.0.0.1:8081/v1/manifest — returns selected release provenance data

If output has not been published or is corrupted, the API returns HTTP 503 instead of pretending the report is healthy. The service **binds only to 127.0.0.1** and has no authentication; it is for local training, not public deployment.

The integration suite starts the server on an ephemeral port and tests live HTTP responses with a real SQLite release.

## Demonstrate workplace failure recovery

1. Run build twice on the same file. The second run must not double counts or create a new release.
2. Set --max-reject-ratio to 0.10, expect a quality failure, then verify the last published pointer remains unchanged.
3. Change a CSV file *inside a released directory* and run verify. SHA-256 checking must reject the tampered release.
4. Restore by rebuilding from an unchanged source into a clean output path; don't pretend a tampered immutable release can be trusted.
5. Compare fresh vs stale status using --as-of 2026-11-21 and --as-of 2026-11-27.

## Operational design

- Input: well-defined schema and exact decimal money.
- Validation: business keys, required fields, positive integer quantities, dates, status, nonnegative cents and conflict detection.
- Idempotence: source SHA-256 generates a deterministic release identifier. Exact replays do not create extra business effects.
- Publication: source is processed into an immutable release folder; a small current.json pointer is atomically replaced only on successful quality gate and checksums.
- Consumer contract: consumers **verify the manifest and checksums** before reading published artifacts. A pointer replacement is atomic on the same filesystem, but this is not a multi-machine transaction.
- Monitoring: verifies source date age independently of job completion.
- Threat model: synthetic data and local filesystem; no authentication, object storage, TLS, service-level locking, distributed workers or concurrency guarantee. Not ready for production deployment.

## Learner apprenticeship use

This is a maintained system to evolve through future GitHub tickets. Do not ask the founder to solve the educational mission. Planned follow-up issues: backfill, schema evolution, artifact upload, parallel retries, incident observability, Spark migration and controlled cloud deployment. Each must be validated before launch.

**Technical references:** [Python decimal](https://docs.python.org/3/library/decimal.html), [SQLite ACID](https://www.sqlite.org/atomiccommit.html), [hashlib](https://docs.python.org/3/library/hashlib.html).
