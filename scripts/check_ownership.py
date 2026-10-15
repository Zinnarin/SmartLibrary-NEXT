"""File-ownership gate for Team Sprint V3 (rules: docs/team_v3/OWNERSHIP_MAP.csv, first matching pattern wins).

  python scripts/check_ownership.py --audit
      every tracked file must map to exactly one rule (no UNASSIGNED files)
  python scripts/check_ownership.py --owner P4 [--base main]      (or --owner auto: inferred from the branch name)
      lists files changed on this branch vs <base> and flags files outside the owner's scope.
      Exit code 1 if a FROZEN or never-commit file was touched, or a file of another owner was changed.

Read-only: it never modifies files. Approval from another owner is a review decision recorded in the PR.
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "docs" / "team_v3" / "OWNERSHIP_MAP.csv"
BRANCH_OWNER = {"feature/v3-cv": "P1", "feature/v3-backend": "P2", "feature/v3-student": "P3", "feature/v3-staff-qa": "P4"}
NEVER = ["*.db", "*.db-wal", "*.db-shm", "*.sqlite*", "*.pt", "*.onnx", "*.mp4", "*.avi", "*.mov", "*.mkv",
         ".env", ".env.*", "*.pem", "*.key", ".venv/*", ".venv-cv/*", "*node_modules/*", "apps/web/dist/*", ".claude/*", "*~$*"]


def git(*args: str) -> list[str]:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [line.strip() for line in out.splitlines() if line.strip()]


def load_rules() -> list[dict]:
    with open(MAP, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def owner_of(path: str, rules: list[dict]) -> dict:
    for r in rules:
        if fnmatch.fnmatchcase(path, r["pattern"]):
            return r
    return {"pattern": "-", "owner": "UNASSIGNED", "approval_required_from": "", "note": ""}


def audit(rules: list[dict]) -> int:
    files = git("ls-files")
    unassigned = [f for f in files if owner_of(f, rules)["owner"] == "UNASSIGNED"]
    counts: dict[str, int] = {}
    for f in files:
        o = owner_of(f, rules)["owner"]
        counts[o] = counts.get(o, 0) + 1
    print(f"tracked files: {len(files)}  by owner: {dict(sorted(counts.items()))}")
    never = [f for f in files if any(fnmatch.fnmatchcase(f, p) for p in NEVER)]
    for f in unassigned:
        print(f"UNASSIGNED  {f}")
    for f in never:
        print(f"NEVER-COMMIT tracked: {f}")
    print("audit:", "OK" if not unassigned and not never else "FAIL")
    return 0 if not unassigned and not never else 1


def check(owner: str, base: str, rules: list[dict]) -> int:
    changed = git("diff", "--name-only", f"{base}...HEAD")
    if not changed:
        print(f"no changes vs {base}")
        return 0
    bad = 0
    for f in changed:
        r = owner_of(f, rules)
        if any(fnmatch.fnmatchcase(f, p) for p in NEVER):
            print(f"BLOCK  never-commit file: {f}")
            bad += 1
        elif r["owner"] == "FROZEN":
            print(f"BLOCK  frozen V2 file: {f}  ({r['note']})")
            bad += 1
        elif r["owner"] != owner:
            print(f"REVIEW owned by {r['owner']}: {f}  -> needs that owner's approval in the PR")
            bad += 1
        elif r["approval_required_from"]:
            print(f"OK*    {f}  (also needs approval from {r['approval_required_from']})")
        else:
            print(f"OK     {f}")
    print(f"{len(changed)} changed file(s) vs {base}; {bad} need attention")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--owner", choices=["P1", "P2", "P3", "P4", "auto"])
    ap.add_argument("--base", default="main")
    a = ap.parse_args()
    rules = load_rules()
    if a.audit:
        return audit(rules)
    if a.owner == "auto":
        import os

        branch = os.environ.get("GITHUB_HEAD_REF") or git("rev-parse", "--abbrev-ref", "HEAD")[0]
        a.owner = next((o for prefix, o in BRANCH_OWNER.items() if branch.startswith(prefix)), None)
        if not a.owner:
            print(f"branch '{branch}' is not a team feature branch ({', '.join(BRANCH_OWNER)}); nothing to check")
            return 0
        print(f"branch {branch} -> owner {a.owner}")
    if a.owner:
        return check(a.owner, a.base, rules)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
