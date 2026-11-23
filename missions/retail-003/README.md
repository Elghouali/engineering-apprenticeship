# RETAIL-003 — The pipeline is green but finance sees yesterday's figures

**Company:** Atlas Retail · **Role:** On-call Data Engineer · **Prerequisites:** RETAIL-001, RETAIL-002

## Incident and business risk

The scheduler says the nightly ETL completed. Yet customers complain that the dashboard shows an old business date. A successful process tells us nothing about whether **up-to-date source data** arrived.

Build a deterministic **freshness and quality evaluator** that distinguishes job freshness from source-data freshness.

## Required API

In your own fork copy the starter to submissions/retail-003/monitor.py. Implement:

    inspect(manifest: dict, as_of: datetime,
            max_job_age_minutes: int = 120,
            max_data_age_days: int = 1) -> dict

Example manifest:

~~~json
{
  "generated_at_utc": "2026-11-21T08:00:00+00:00",
  "latest_order_date": "2026-11-20",
  "quality_passed": true
}
~~~

Return exactly:

~~~json
{
  "status": "healthy",
  "issues": [],
  "metrics": {
    "job_age_minutes": 60.0,
    "data_age_days": 1
  }
}
~~~

Rules:
1. All datetime inputs must be timezone-aware. Normalize run time to UTC.
2. Validate as_of and thresholds; invalid arguments raise ValueError("invalid_monitor_arguments").
3. Missing or invalid run time produces missing_run_timestamp or invalid_run_timestamp.
4. A run time more than one minute in the future produces future_run_timestamp.
5. Too-old ETL completion produces stale_job.
6. Missing/invalid source business date produces missing_source_date or invalid_source_date.
7. Future business date produces future_source_date; older than allowed produces stale_data.
8. quality_passed must be the boolean True, else add quality_not_confirmed.
9. Return all applicable issues in alphabetical order, with status "alert"; no exception for bad *manifest* data.
10. metrics contain age values only when the corresponding timestamp/date is valid.

This teaching contract uses business dates as a proxy. A production platform should separately monitor source arrival time, partition completeness, event-time watermarks and clock drift.

## Reproduction and delivery

    python tools/apprentice.py start retail-003
    python tools/apprentice.py check retail-003

Write an incident timeline explaining how a green job can publish stale data, set an SLO and explain a safe backfill. Do not change the grader.

## Technical resources

- https://docs.python.org/3/library/datetime.html
- https://sre.google/sre-book/monitoring-distributed-systems/

**No real production alerts or cloud services are sent.**
