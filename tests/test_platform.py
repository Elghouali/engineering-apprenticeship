"""Test the apprenticeship itself, not a learner submission."""
from __future__ import annotations
import csv
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "missions" / "catalog.json"
GRAPH = ROOT / "skills" / "graph.json"


class PlatformTests(unittest.TestCase):
    def test_mission_catalog_is_valid(self):
        payload = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], 1)
        ids = []
        for item in payload["missions"]:
            ids.append(item["id"])
            self.assertTrue((ROOT / item["path"] / "README.md").is_file())
            self.assertTrue((ROOT / item["starter"]).is_file())
            self.assertTrue((ROOT / item["grader"]).is_dir())
            self.assertTrue(item["review"])
            self.assertEqual(item["status"], "ready")
        self.assertEqual(len(ids), len(set(ids)))

    def test_skill_dependency_graph_is_acyclic(self):
        payload = json.loads(GRAPH.read_text(encoding="utf-8"))
        skills = {x["id"]: x["prerequisites"] for x in payload["skills"]}
        self.assertEqual(len(skills), len(payload["skills"]))
        visited = set()
        active = set()

        def visit(skill):
            self.assertIn(skill, skills)
            self.assertNotIn(skill, active, "Cycle in prerequisite graph")
            if skill in visited:
                return
            active.add(skill)
            for previous in skills[skill]:
                visit(previous)
            active.remove(skill)
            visited.add(skill)

        for skill in skills:
            visit(skill)
        for mission in json.loads(CATALOG.read_text())["missions"]:
            for skill in mission["skills"]:
                self.assertIn(skill, skills)

    def test_company_fixture_is_eight_synthetic_records(self):
        fixture = ROOT / "missions" / "retail-001" / "data" / "orders.csv"
        with fixture.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 8)
        self.assertEqual(len([r for r in rows if r["order_id"] == "1001"]), 2)

    def test_cli_lists_first_mission(self):
        p = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "apprentice.py"), "list"],
            capture_output=True, text=True, check=False
        )
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("retail-001", p.stdout)

    def test_deliberate_starter_fails_grader(self):
        """Guard against accidentally shipping a pre-solved first mission."""
        import os
        env = os.environ.copy()
        env["APPRENTICE_SUBMISSION_PATH"] = str(
            ROOT / "missions" / "retail-001" / "starter" / "pipeline.py"
        )
        p = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s",
             "missions/retail-001/tests", "-v"],
            cwd=ROOT, env=env, capture_output=True, text=True, check=False
        )
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("FAILED", p.stderr)


if __name__ == "__main__":
    unittest.main()
