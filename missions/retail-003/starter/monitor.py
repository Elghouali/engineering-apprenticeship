"""RETAIL-003 broken incident monitor: checks successful job, ignores data freshness."""


def inspect(manifest, as_of, max_job_age_minutes=120, max_data_age_days=1):
    # BUG: a green job does not guarantee a new source partition was ingested.
    return {
        "status": "healthy",
        "issues": [],
        "metrics": {"job_age_minutes": 0.0, "data_age_days": 0}
    }
