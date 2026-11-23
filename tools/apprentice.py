"""GitHub-native apprenticeship CLI (stdlib only).

The command does not install dependencies, create cloud resources or run a
privileged evaluation system. A learner executes their code locally / in CI.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "missions" / "catalog.json"


def missions():
    return json.loads(CATALOG.read_text(encoding="utf-8"))["missions"]


def checks(mission_id: str):
    selected = [m for m in missions() if m["id"] == mission_id]
    if not selected:
        print("Unknown mission: " + mission_id, file=sys.stderr)
        return 2
    entry = selected[0]
    if not (ROOT / entry["submission"]).is_file():
        print("No submission yet. Copy the deliberately faulty starter to: "
              + entry["submission"] + "\nThen fix it, run checks and open a PR.",
              file=sys.stderr)
        return 2
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", entry["grader"], "-v"],
        cwd=ROOT, check=False
    )
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Learn engineering through GitHub missions")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List ready missions")
    sub.add_parser("doctor", help="Inspect local Git/Python availability")
    check = sub.add_parser("check", help="Grade a learner submission")
    check.add_argument("mission_id")
    args = parser.parse_args()
    if args.command == "list":
        for item in missions():
            print(f"{item['id']:<15} {item['level']:<10} {item['status']:<8} {item['name']}")
        return 0
    if args.command == "doctor":
        print(json.dumps({
            "python": sys.version.split()[0],
            "python_supported": sys.version_info >= (3, 11),
            "git_installed": shutil.which("git") is not None,
            "github_access": "Verify login/permissions using git push or gh auth status",
            "first_mission_requires_cloud": False
        }, indent=2))
        return 0
    return checks(args.mission_id)


if __name__ == "__main__":
    raise SystemExit(main())
