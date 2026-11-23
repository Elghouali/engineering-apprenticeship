# CLOUD-002 — A published report was silently modified

> **PRE-RELEASE / PROTOTYPE — contract v1.** This exercise has a public grader and a confidential correct reference, but independent first-time learner onboarding has not yet passed.

**Company:** Atlas Retail Cloud Team · **Role:** Junior Cloud Engineer · **Prerequisite:** CLOUD-001

## Incident

A downstream reporting service downloaded a file with the expected name but unexpected contents. The object-store upload looked successful, yet an unnoticed overwrite corrupted the business result.

In a **local simulation of object storage**, create a safe artifact publisher and reader with SHA-256 verification, conflict detection and restricted object keys. Later modules can map the principles onto S3, Google Cloud Storage and Azure Blob Storage.

## Required API

~~~python
publish_artifact(source: Path, store_root: Path, key: str) -> dict
fetch_artifact(store_root: Path, key: str, expected_sha256: str) -> bytes
~~~

Successful publish returns:
- key (the same relative string)
- sha256 (lowercase hex SHA-256 of bytes)
- size_bytes (non-negative integer)

Rules:
1. Keys are relative slash-delimited paths such as reports/2026-11-20.csv.
2. Reject empty keys, absolute paths, backslashes, dot/parent segments and unsafe characters with ValueError("invalid_object_key"). Allow ASCII alphanumerics, dot, underscore, hyphen only within normal segments.
3. Do not allow reads or writes escaping store_root, including through symlinks.
4. Publishing identical bytes to an existing key is idempotent.
5. Publishing *different* bytes to an existing key raises ValueError("object_conflict") and must not replace the existing file.
6. On fetch, recompute the hash and raise ValueError("checksum_mismatch") on a mismatch.
7. Make publication crash-safe by preparing a temporary file in the same filesystem before moving into place; explain why this educational implementation is not fully concurrency-safe.
8. Never modify the source file.

## Workflow

~~~bash
python tools/apprentice.py start cloud-002
python tools/apprentice.py check cloud-002
~~~

## Engineer review

- Why do file names and successful HTTP status codes not prove data integrity?
- Why does an ETag sometimes differ from an MD5 or SHA-256 checksum?
- What does a precondition such as If-None-Match protect against in a real object store?
- Compare permissions and lifecycle policies for AWS S3, GCS and Azure Blob Storage.

**Security:** This is a local filesystem teaching simulation, not a cloud storage service. Never point it at sensitive directories or production data.

**References:** https://docs.python.org/3/library/hashlib.html , https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html

---

## Mission handoff: from incident to pull request

**Requirements:** Python 3.11+, standard library only; disposable local object store directory. Read the contract above before changing code.

**Training files:** [faulty starter](starter/storage.py) · [public acceptance tests](tests/test_submission.py) · personal output: `submissions/cloud-002/storage.py` (created only in a learner fork, not committed upstream).

From the **root of your own fork**, after public launch:

```bash
git switch -c mission/cloud-002
python tools/apprentice.py start cloud-002
python tools/apprentice.py check cloud-002
```

The first test run must fail because the starter is intentionally defective. Implement and test only in your submission; do not edit official graders. Push to your fork and open a PR **against your own fork's main branch**, not the academy upstream.

**Failure-recovery drill:** Publish the same bytes twice, then attempt a conflicting write and a tampered download.

In your PR, demonstrate **Explain / Build / Recover / Defend**: root cause, passing regression checks, recovery behavior and trade-offs. See the [review rubric](../../docs/ENGINEERING_LOOP.md) and [hint policy](../../mentor/REVIEW_POLICY.md).

**Continue to:** [CLOUD-004](../cloud-004/README.md), [CLOUD-005](../cloud-005/README.md). These are suggestions; use the [catalog](../catalog.json) for exact prerequisites.

[← All missions](../README.md) · [Academy](../../README.md) · [Company](../../companies/atlas-retail/README.md) · [Documentation](../../docs/README.md)
