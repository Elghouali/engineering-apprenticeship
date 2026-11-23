# Atlas Retail Data Product — Working Local Reference

[← Capstone index](../README.md) · [Academy home](../../README.md) · [Atlas Retail](../../companies/atlas-retail/README.md) · [Operator runbook](RUNBOOK.md)

> **Status: implemented and locally integration-tested, but not a finished learner capstone.** This is a Python/SQLite/HTTP reference platform, not an already deployed Kafka + Spark + Airflow + Kubernetes system. Its data is synthetic and no cloud account is required.

This mini-platform demonstrates a full **data product release lifecycle**: ingest orders, validate a business contract, quarantine bad records, deduplicate retries, calculate paid revenue, publish versioned outputs, verify checksums and check whether the underlying business date is fresh.

## Architecture

~~~mermaid
flowchart TD
    S["Synthetic CSV order feed"] --> V["Schema validation + exact decimal money"]
    V --> R["Rejected rows CSV"]
    V --> D["Deduplicate order IDs / check conflicts"]
    D --> DB["SQLite accepted orders"]
    DB --> G["Gold: paid revenue by date CSV"]
    G --> M["SHA-256 manifest"]
    DB --> M
    R --> M
    M --> P["Atomically updated current.json"]
    P --> H["Freshness and provenance checks"]
    H --> API["Loopback HTTP reporting API"]
~~~

It intentionally uses a single local machine. The design isolates **source replay** from **publishing the latest accepted release** and shows how a quality failure or corrupted artifact should stop downstream consumers.

## What is in this directory?

| Path | Purpose |
| --- | --- |
| [platform.py](platform.py) | \`build\`, \`verify\`, and \`status\` commands |
| [api.py](api.py) | Local HTTP server; binds to \`127.0.0.1\` only |
| [data/orders.csv](data/orders.csv) | Eight synthetic retail order records |
| [tests/](tests/) | End-to-end SQLite, integrity, freshness and live HTTP tests |
| [RUNBOOK.md](RUNBOOK.md) | Reproduction, incident triage and recovery |
| \`output/\` | Generated, local-only release data; excluded from Git |

**Dependencies:** Python **3.11+**; standard library only. On Windows, use PowerShell with each command on a single line; use \`py -3\` instead of \`python\` if necessary. No Docker, Java, cloud subscription or credentials are needed for this reference system.

## First verified run

Run all commands **from the repository root**. These single-line commands work in macOS/Linux shells and Windows PowerShell.

~~~bash
python capstones/atlas-retail-platform/platform.py build --source capstones/atlas-retail-platform/data/orders.csv --output capstones/atlas-retail-platform/output
python capstones/atlas-retail-platform/platform.py verify --output capstones/atlas-retail-platform/output
python capstones/atlas-retail-platform/platform.py status --output capstones/atlas-retail-platform/output --as-of 2026-11-21 --max-age-days 1
python -m unittest discover -s capstones/atlas-retail-platform/tests -v
~~~

**Expected outputs from the fixture:** 8 input rows; **4 accepted orders**, **1 exact replay duplicate**, **3 rejected rows**, and **22,000 integer cents** paid revenue (220.00 in the fixture's monetary units). The fixture's business date is **2026-11-20**. The 2026-11-21 freshness test reports healthy with a one-day age.

If you check freshness against a much later current date, **stale data is the correct result**, and the CLI returns exit code 2. A historical fixture is not a live production feed.

## Generated release layout

~~~text
output/
├── current.json                 # Pointer to last accepted release
└── releases/
    └── <source-hash-prefix>/
        ├── orders.db            # SQLite accepted order records
        ├── gold.csv             # Paid revenue by date, integer cents
        ├── rejections.csv       # Quarantined invalid/conflicting rows
        └── manifest.json        # Checksums, source identity and metrics
~~~

A repeated build from identical input has the same source hash, does not double revenue and reuses the existing release. A new input that exceeds the configured rejection threshold is refused **without replacing** the published pointer. On verification, file checksums and business metrics are checked before downstream use.

**Important:** An atomic pointer update on one filesystem is not an exactly-once distributed transaction. Concurrent writers, shared object storage and hostile filesystem mutation require additional controls.

## View the live local API

After a successful build, run:

~~~bash
python capstones/atlas-retail-platform/api.py --output capstones/atlas-retail-platform/output --port 8081
~~~

From another terminal, visit the following **local-only** endpoints:

- [Health](http://127.0.0.1:8081/health) — verifies the release and returns its ID
- [Revenue](http://127.0.0.1:8081/v1/revenue) — returns typed daily Gold revenue records
- [Manifest](http://127.0.0.1:8081/v1/manifest) — shows selected release metadata

The endpoints only work while the local server is running. If there is no verified release or an artifact is corrupted, the API returns **HTTP 503** instead of serving untrusted numbers. Stop the server with **Ctrl+C**.

## Professional failure drills

Do not modify a published release in a valuable workspace. Reproduce these drills in a **disposable copy** or rely on the isolated automated tests.

| Drill | Expected invariant |
| --- | --- |
| Build the same feed twice | One release, identical totals |
| Tighten the rejection ratio to 0.10 | Quality gate fails, current pointer unchanged |
| Tamper with a released \`gold.csv\` | \`verify\` fails with checksum error, API reports unavailable |
| Check date 2026-11-21 vs 2026-11-27 | Healthy with 1-day age vs stale with 7-day age |
| Rebuild from a trusted source into a clean destination | Verified metrics recovered without trusting tampered artifacts |

For reproduction instructions and failure response, see the [operator runbook](RUNBOOK.md).

## Design decisions and limits

- **Data contracts:** Strict columns, IDs and status validation; cancelled transactions are kept but excluded from paid revenue.
- **Money:** Parse decimal input, store/aggregate integer cents, avoid binary floating-point totals.
- **Retry safety:** Duplicate/conflicting business keys are handled deterministically.
- **Release integrity:** Source SHA-256, artifact checksums, immutable release directories, atomic current pointer.
- **Monitoring:** Source business-date freshness is independent of job completion.
- **Security scope:** Synthetic data; loopback server with no authentication, no TLS, no authorization, no distributed locking and no real cloud resources.

These are valuable professional design patterns, but **not a production payment/data platform**.

## How this becomes the future learner capstone

The next major product build will connect existing mission concepts through a **learner-owned, incident-driven platform** using PostgreSQL, Kafka, Spark, Airflow, object storage, containerization, CI and recovery. Those capabilities are **planned**, not already part of this reference code. Learners will deliver changes through GitHub Issues and their own PRs; the founder does not need to practice the missions during development.

Explore the [mission directory](../../missions/README.md), [curriculum roadmap](../../docs/PUBLIC_CURRICULUM.md) and [public launch gates](../../docs/PUBLIC_LAUNCH.md).

**Technical references:** [Python decimal](https://docs.python.org/3/library/decimal.html), [SQLite atomic commit](https://www.sqlite.org/atomiccommit.html), [Python hashlib](https://docs.python.org/3/library/hashlib.html).
