"""GitHub-native apprenticeship CLI: list, doctor, start, check and check-all.

Pure Python standard library, no cloud accounts, no privileged services.
Submission code is executable: do not run unknown people's submissions
on machines with secrets or valuable personal files.
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


def missions() -> list[dict]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))["missions"]


def get_mission(mission_id: str) -> dict | None:
    return next((m for m in missions() if m["id"] == mission_id), None)


def path_under(root: Path, relative: str) -> Path:
    """Keep catalog-defined paths inside the expected working tree."""
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Unsafe catalog path outside repository")
    return path


def branch_name(root: Path = ROOT) -> str:
    try:
        command = subprocess.run(
            ["git", "branch", "--show-current"], cwd=root, capture_output=True,
            text=True, check=False
        )
    except FileNotFoundError:
        return ""
    return command.stdout.strip() if command.returncode == 0 else ""


def start(mission_id: str, *, root: Path = ROOT,
          enforce_branch: bool = True) -> Path:
    """Copy an intentionally broken starter to a personal submission path.

    This function never overwrites an existing submission or modifies a starter.
    """
    mission = get_mission(mission_id)
    if mission is None:
        raise ValueError("Unknown mission: " + mission_id)
    if enforce_branch:
        branch = branch_name(root)
        if not branch or branch in ("main", "master"):
            raise ValueError(
                "Create a personal mission branch first, for example: "
                "git switch -c mission/" + mission_id
            )
    source = path_under(root, mission["starter"])
    destination = path_under(root, mission["submission"])
    if not source.is_file():
        raise ValueError("Starter file not found: " + str(source))
    if destination.exists():
        raise FileExistsError("Submission already exists; refusing to overwrite: "
                              + str(destination))
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return destination


def check(mission_id: str) -> int:
    mission = get_mission(mission_id)
    if mission is None:
        print("Unknown mission: " + mission_id, file=sys.stderr)
        return 2
    if not path_under(ROOT, mission["submission"]).is_file():
        print("No submission yet. Use a personal fork and mission branch, then run: "
              "python tools/apprentice.py start " + mission_id, file=sys.stderr)
        return 2
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover",
         "-s", mission["grader"], "-v"], cwd=ROOT, check=False
    )
    return result.returncode


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Learn real engineering through GitHub issues, missions and PRs"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List ready missions")
    sub.add_parser("doctor", help="Inspect local Git/Python availability")
    starter = sub.add_parser("start", help="Copy mission starter on your own branch")
    starter.add_argument("mission_id")
    grader = sub.add_parser("check", help="Grade one learner submission")
    grader.add_argument("mission_id")
    sub.add_parser("check-all", help="Grade all present learner submissions")
    args = parser.parse_args(argv)

    if args.command == "list":
        for mission in missions():
            dependency = ",".join(mission.get("prerequisites", [])) or "none"
            print(f"{mission['id']:<14} {mission['level']:<10} "
                  f"{mission['status']:<8} {mission['name']} (after: {dependency})")
        return 0
    if args.command == "doctor":
        print(json.dumps({
            "python": sys.version.split()[0],
            "python_supported": sys.version_info >= (3, 11),
            "git_installed": shutil.which("git") is not None,
            "branch": branch_name(),
            "cloud_account_required": False,
            "warning": "Never execute unknown learner submissions with secrets present",
        }, indent=2))
        return 0
    if args.command == "start":
        try:
            file = start(args.mission_id)
        except (ValueError, FileExistsError) as error:
            parser.error(str(error))
        print("Starter copied to " + str(file.relative_to(ROOT)))
        print("Initial tests are supposed to fail. Investigate and fix the code.")
        return 0
    if args.command == "check":
        return check(args.mission_id)
    if args.command == "check-all":
        selected = [
            mission["id"] for mission in missions()
            if path_under(ROOT, mission["submission"]).is_file()
        ]
        if not selected:
            print("No learner submissions. Platform integrity checks run separately.")
            return 0
        outcomes = [check(mission_id) for mission_id in selected]
        return int(any(code != 0 for code in outcomes))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
