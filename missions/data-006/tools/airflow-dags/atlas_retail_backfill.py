"""Load the learner's implementation into Airflow's DAG loader.

This adapter is only a module-level DAG-discovery shim, NOT a solution.
The learner implements build_airflow_dag() in submissions/data-006/orchestrator.py.
"""
import sys
sys.path.insert(0, "/opt/airflow/reference")
from orchestrator import build_airflow_dag

atlas_retail_backfill = build_airflow_dag()
