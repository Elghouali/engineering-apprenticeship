"""Check relative Markdown links in public academy documentation.

Offline and standard-library only; does not open network URLs or GitHub APIs.
"""
from __future__ import annotations
from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]+\]\(([^)\s]+)(?:\s+[^)]*)?\)")
SCHEMES = ("https://", "http://", "mailto:", "#")


def find_broken_links() -> list[str]:
    broken = []
    for doc in ROOT.rglob("*.md"):
        if any(part in (".git", ".venv", "node_modules", ".pytest_cache")
               for part in doc.relative_to(ROOT).parts):
            continue
        for match in LINK.finditer(doc.read_text(encoding="utf-8")):
            value = match.group(1).strip("<>")
            if not value or value.startswith(SCHEMES):
                continue
            target = unquote(value.split("#", 1)[0].split("?", 1)[0])
            if not target:
                continue
            candidate = (doc.parent / target).resolve()
            if not candidate.is_relative_to(ROOT.resolve()) or not candidate.exists():
                line = doc.read_text(encoding="utf-8")[:match.start()].count("\n") + 1
                broken.append(f"{doc.relative_to(ROOT)}:{line}: {value}")
    return broken


def main() -> int:
    issues = find_broken_links()
    if issues:
        print("Broken local Markdown links:")
        for problem in issues:
            print("- " + problem)
        return 1
    print("All local Markdown document links resolve on this commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
