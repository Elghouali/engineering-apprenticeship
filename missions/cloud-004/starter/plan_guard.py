"""CLOUD-004 intentionally unsafe approval logic."""
def assess_plan(plan: dict) -> dict:
    # BUG: hides replacement, public SSH, and out-of-band drift.
    return {"decision": "approve", "reasons": [],
            "destructive_resources": [], "drift_resources": []}
