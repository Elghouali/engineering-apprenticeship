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

    def test_mission_prerequisites_exist(self):
        items = json.loads(CATALOG.read_text(encoding="utf-8"))["missions"]
        by_id = {m["id"]: m for m in items}
        self.assertEqual(len(by_id), len(items))
        for mission in items:
            for prerequisite in mission.get("prerequisites", []):
                self.assertIn(prerequisite, by_id)

    def test_start_copies_but_never_overwrites_submission(self):
        import tempfile
        from tools import apprentice
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for mission in apprentice.missions():
                source = root / mission["starter"]
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text("starter for " + mission["id"], encoding="utf-8")
                target = apprentice.start(mission["id"], root=root, enforce_branch=False)
                self.assertTrue(target.is_file())
                self.assertEqual(target.read_text(), source.read_text())
                with self.assertRaises(FileExistsError):
                    apprentice.start(mission["id"], root=root, enforce_branch=False)

    def test_start_refuses_untrusted_parent_directory(self):
        import tempfile
        from tools import apprentice
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                apprentice.path_under(Path(d), "../secret.py")

    def test_all_starters_are_intentionally_broken(self):
        """All published starter missions should fail the full contract."""
        import os
        for mission in json.loads(CATALOG.read_text())["missions"]:
            with self.subTest(mission=mission["id"]):
                env = os.environ.copy()
                env["APPRENTICE_SUBMISSION_PATH"] = str(ROOT / mission["starter"])
                result = subprocess.run(
                    [sys.executable, "-m", "unittest", "discover", "-s",
                     mission["grader"], "-v"],
                    cwd=ROOT, env=env,
                    capture_output=True, text=True, check=False,
                    timeout=10
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("FAILED", result.stderr)


if __name__ == "__main__":
    unittest.main()
