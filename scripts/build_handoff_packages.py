"""Sync, validate and zip the V3 individual handoff packages (docs/team_v3/individual_handoff/).

  python scripts/build_handoff_packages.py --sync            copy SHARED_V3 sections into every <!-- SYNC:BEGIN --> region
  python scripts/build_handoff_packages.py --check           validate (exit 1 on any problem)
  python scripts/build_handoff_packages.py --check --write-report   also refresh the AUTO block of VALIDATION_REPORT.md
  python scripts/build_handoff_packages.py --zip [--out DIR] build the 5 ZIPs (default artifacts/handoff_v3, git-ignored)

Documentation tooling only: it never touches application code, never prints tokens or student IDs.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs" / "team_v3" / "individual_handoff"
SHARED = HANDOFF / "SHARED_V3"
EXAMPLES = SHARED / "contract_examples"
REPORT = HANDOFF / "VALIDATION_REPORT.md"
sys.path.insert(0, str(ROOT / "scripts"))
import check_ownership as co  # noqa: E402

PACKAGES = {
    "P1": ("P1_COMPUTER_VISION", "SmartLibrary_P1_ComputerVision.zip", ["C1"]),
    "P2": ("P2_BACKEND_DATABASE", "SmartLibrary_P2_Backend.zip", ["C1", "C2", "C3", "C4"]),
    "P3": ("P3_STUDENT_FRONTEND", "SmartLibrary_P3_StudentFrontend.zip", ["C2", "C4", "C1__cv_"]),
    "P4": ("P4_STAFF_QA_INTEGRATION", "SmartLibrary_P4_StaffIntegration.zip", ["C1", "C2", "C3", "C4"]),
}
SHARED_ZIP = "SmartLibrary_V3_Shared_Contracts.zip"
REQUIRED = ["01_PROJECT_CONTEXT_TH.md", "02_ASSIGNED_MISSION_TH.md", "03_EXISTING_CODE_AND_OWNERSHIP.md",
            "04_DEVELOPMENT_ROADMAP_TH.md", "05_INTEGRATION_CONTRACT.md", "06_ACCEPTANCE_CRITERIA.md",
            "07_CHANGE_REQUEST_TEMPLATE.md", "08_DELIVERY_CHECKLIST.md", "09_CLAUDE_CODE_MASTER_PROMPT.md"]

# Files/dirs that the packages name but that do not exist yet (created during the sprint) or are git-ignored.
PLANNED = ["docs/api_contract_v3.md", "tests/test_cv_v3.py", "tests/test_backend_v3.py", "tests/test_contract_v3.py",
           "apps/web/e2e/student_v3.spec.ts", "apps/web/e2e/staff_reliability_v3.spec.ts",
           "apps/web/src/components/SeatCheckPanel.tsx", "cv/experiments*", "integration*",
           "verification/TEAM_V3_ACCEPTANCE.csv", "verification/TEAM_V3_*", "presentation/v3*", "evidence/team_v3*",
           "evidence/team_v3/integration/INTEGRATION_LOG.md",
           ".github/CODEOWNERS", "docs/team_v3/individual_handoff/VALIDATION_REPORT.md"]
IGNORED = ["artifacts*", "cv/models*", ".venv*", "*node_modules*", "apps/web/dist*", "services/api/data*",
           ".pytest_tmp*", "cv/experiments/**/raw*", "cv/experiments/**/frames*"]
PR16_BRANCH = "origin/feature/v3-staff-qa"
ROOTS = ("apps", "services", "cv", "tests", "scripts", "docs", "evidence", "presentation", "verification", "reference",
         "templates", ".github", "integration", "artifacts", ".venv", ".venv-cv")
ROOT_FILES = {"README.md", "pytest.ini", ".gitignore", ".gitattributes", "START_HERE.md", "CLAUDE_CODE_MASTER_PROMPT.md"}
EXT = (".md", ".py", ".ts", ".tsx", ".json", ".csv", ".ps1", ".ini", ".txt", ".yml", ".html", ".css", ".jpg", ".pptx", ".pdf")
# Paths written relative to a module folder (e.g. `pages/CvLab.tsx`, `e2e/demo.spec.ts`, `engine/trust.py`).
REL_BASES = ("apps/web", "apps/web/src", "services/api/app", "services/api", "cv")
REL_FIRST = {"e2e", "src", "pages", "components", "engine", "app"}
EXTERNAL = {"bus.jpg",       # Ultralytics sample image: lives in the installed package, not in this repo
            "MANIFEST.txt"}  # written into each ZIP by --zip
LINE_SUFFIX = re.compile(r":\d+([–-]\d+)?$")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, encoding="utf-8").stdout


# ------------------------------------------------------------------ sync

SECTION_RE = r"<!-- SECTION:{name} -->\n(.*?)<!-- /SECTION:{name} -->"
SYNC_RE = re.compile(r"(<!-- SYNC:BEGIN (?P<src>[^#\s]+)#(?P<sec>\w+) -->\n)(?P<body>.*?)(<!-- SYNC:END -->)", re.S)


def section(src: str, name: str) -> str:
    text = (HANDOFF / src).read_text(encoding="utf-8")
    m = re.search(SECTION_RE.format(name=re.escape(name)), text, re.S)
    if not m:
        raise SystemExit(f"section {name} not found in {src}")
    return m.group(1).strip("\n")


def synced_text(text: str) -> str:
    def repl(m: re.Match) -> str:
        body = section(m.group("src"), m.group("sec"))
        note = f"> _Synced from `SHARED_V3/{Path(m.group('src')).name}` section `{m.group('sec')}` — edit there, then run `scripts/build_handoff_packages.py --sync`._\n\n"
        return m.group(1) + note + body + "\n" + m.group(5)
    return SYNC_RE.sub(repl, text)


def package_files() -> list[Path]:
    return sorted(p for d, _, _ in PACKAGES.values() for p in (HANDOFF / d).glob("*.md"))


def do_sync() -> int:
    changed = 0
    for p in package_files():
        old = p.read_text(encoding="utf-8")
        new = synced_text(old)
        if new != old:
            p.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
            print(f"synced {p.relative_to(ROOT).as_posix()}")
    print(f"sync: {changed} file(s) updated")
    return 0


# ------------------------------------------------------------------ check

def all_docs() -> list[Path]:
    return sorted(HANDOFF.rglob("*.md"))


def sensitive_values() -> dict[str, str]:
    """name -> value, never printed. Demo tokens from settings + ID-like numbers from the private deck builder."""
    out = {}
    sys.path.insert(0, str(ROOT / "services" / "api"))
    from app.settings import AppSettings  # noqa: E402
    s = AppSettings()
    out["staff token default"] = s.staff_token
    out["device token default"] = s.device_token
    pptx = ROOT / "scripts" / "build_pptx.py"
    if pptx.exists():
        for i, n in enumerate(sorted(set(re.findall(r"\b\d{8,11}\b", pptx.read_text(encoding="utf-8"))))):
            out[f"student-ID-like number #{i + 1} from scripts/build_pptx.py"] = n
    return out


def path_candidates(text: str) -> set[str]:
    out = set()
    for tok in re.findall(r"`([^`\n]+)`", text):
        tok = tok.strip()
        if " " in tok or tok.startswith(("/", "http", "$", "-", "#", "<", "{")) or "=" in tok:
            continue
        if not re.fullmatch(r"[A-Za-z0-9_.\-/*{},<>:#–]+", tok):
            continue
        bare = LINE_SUFFIX.sub("", tok.split("::")[0])   # pytest node ids: file.py::test_name
        if bare.startswith(".") and "/" not in bare and bare not in ROOT_FILES:
            continue                                      # a bare extension such as `.jpg`
        first = bare.split("/")[0]
        if re.match(r"C\d__", bare):
            out.add("contract_examples/" + bare)
        elif "/" in bare and (first in ROOTS or first in REL_FIRST or first in ("SHARED_V3", "contract_examples")) \
                or bare in ROOT_FILES or ("/" not in bare and bare.endswith(EXT)):
            out.add(tok)
    return out


def expand(tok: str) -> list[str]:
    tok = LINE_SUFFIX.sub("", tok.split("::")[0])        # file.py:123, :12–34, file.py::test_name
    tok = tok.split("#")[0].rstrip("/")
    m = re.search(r"\{([^}]+)\}", tok)
    if m:
        return [x for alt in m.group(1).split(",") for x in expand(tok[:m.start()] + alt + tok[m.end():])]
    return [tok]


def _in_repo(pat: str, tracked: set[str]) -> bool:
    if pat in tracked or any(fnmatch.fnmatch(t, pat) or t.startswith(pat + "/") for t in tracked):
        return True
    # new, not yet committed files in this working tree
    return (ROOT / pat).exists() if "*" not in pat else bool(list(ROOT.glob(pat)))


def _planned(pat: str) -> bool:
    return any(fnmatch.fnmatch(pat, p) or fnmatch.fnmatch(pat, p + "/*") or pat == p for p in PLANNED)


def check_paths(tracked: set[str], pr16: set[str], here: Path, text: str, problems: list, stats: dict):
    names = {Path(t).name for t in tracked}
    for raw in sorted(path_candidates(text)):
        for tok in expand(raw):
            pat = re.sub(r"<[^>]+>", "*", tok)
            first = pat.split("/")[0]
            if any(fnmatch.fnmatch(pat, p) or fnmatch.fnmatch(pat, p + "/*") for p in IGNORED) or pat in EXTERNAL:
                stats["ignored"] += 1
            elif "/" not in pat:
                if (pat in names or any(fnmatch.fnmatch(n, pat) for n in names) or list(HANDOFF.rglob(pat))
                        or (ROOT / pat).exists() or any(Path(p).name == pat for p in pr16)):
                    stats["exists"] += 1
                elif any(Path(p).name == pat for p in PLANNED):
                    stats["planned"] += 1
                else:
                    problems.append(f"UNKNOWN FILE  {here.relative_to(ROOT).as_posix()}: `{raw}`")
            elif first in REL_FIRST and first not in ROOTS:
                cands = [f"{b}/{pat}" for b in REL_BASES]
                if any(_in_repo(c, tracked) for c in cands):
                    stats["exists"] += 1
                elif any(c in pr16 for c in cands):
                    stats["pr16"] += 1
                elif any(_planned(c) for c in cands):
                    stats["planned"] += 1
                else:
                    problems.append(f"UNKNOWN PATH  {here.relative_to(ROOT).as_posix()}: `{raw}`")
            elif (_in_repo(pat, tracked) or (here.parent / pat).exists() or (HANDOFF / pat).exists()
                  or list(HANDOFF.glob(pat)) or (first == "contract_examples" and list(EXAMPLES.glob(pat.split("/")[-1])))):
                stats["exists"] += 1
            elif pat in pr16:
                stats["pr16"] += 1
            elif _planned(pat):
                stats["planned"] += 1
            else:
                problems.append(f"UNKNOWN PATH  {here.relative_to(ROOT).as_posix()}: `{raw}`")


def check_ownership_tables(rules, pr16: set[str], problems: list, stats: dict):
    """'## Files you own' table: owner + approval + package must match OWNERSHIP_MAP.csv.
    Any other `| `path` | P# | ...` row in the 03 file: owner must match."""
    row_re = re.compile(r"^\| `([^`]+)` \| (P[1-4]|FROZEN) \|(.*)$", re.M)
    norm = lambda s: "" if s.strip() in ("—", "-", "") else s.strip().replace(" ", "")  # noqa: E731
    for key, (folder, _, _) in PACKAGES.items():
        text = (HANDOFF / folder / "03_EXISTING_CODE_AND_OWNERSHIP.md").read_text(encoding="utf-8")
        m = re.search(r"^## Files you own\n(.*?)(?=^## )", text, re.S | re.M)
        own_part = m.group(1) if m else ""
        if not row_re.search(own_part):
            problems.append(f"NO OWNERSHIP TABLE in {folder}/03")
        for part, is_own in ((own_part, True), (text.replace(own_part, ""), False)):
            for path, owner, rest in row_re.findall(part):
                cells = [c for c in rest.split("|")]
                approval, status = (cells[0], cells[1]) if len(cells) >= 2 else ("", "")
                if is_own and "PR #16" in status:
                    if path not in pr16:
                        problems.append(f"OWNERSHIP {folder}: `{path}` said to be on PR #16 but not found on {PR16_BRANCH}")
                    stats["own_pr16"] += 1
                    continue
                r = co.owner_of(path, rules)
                if r["owner"] != owner:
                    problems.append(f"OWNERSHIP {folder}: `{path}` listed as {owner}, OWNERSHIP_MAP says {r['owner']} ({r['pattern']})")
                    continue
                if is_own:
                    want = norm(r.get("approval_required_from", "") or "")
                    if norm(approval) != want:
                        problems.append(f"APPROVAL  {folder}: `{path}` lists '{norm(approval)}', OWNERSHIP_MAP says '{want}'")
                        continue
                    if owner != key:
                        problems.append(f"OWNERSHIP {folder}: `{path}` is in {key}'s own-files table but its owner is {owner}")
                        continue
                stats["own_ok"] += 1


def do_check(write_report: bool) -> int:
    problems: list[str] = []
    stats = {"exists": 0, "planned": 0, "ignored": 0, "pr16": 0, "own_ok": 0, "own_pr16": 0}
    tracked = set(git("ls-files").split())
    pr16 = set(git("ls-tree", "-r", "--name-only", PR16_BRANCH).split()) - tracked
    rules = co.load_rules()
    # 1. structure
    for key, (folder, _, _) in PACKAGES.items():
        have = sorted(p.name for p in (HANDOFF / folder).glob("*.md"))
        if have != REQUIRED:
            problems.append(f"STRUCTURE {folder}: expected {REQUIRED}, found {have}")
    for name in ("00_PROJECT_OVERVIEW_TH.md", "01_V2_CURRENT_STATUS.md", "02_SYSTEM_ARCHITECTURE.md", "03_SHARED_API_CONTRACTS.md",
                 "04_TEAM_WORKING_AGREEMENT_TH.md", "05_INTEGRATION_ROADMAP_TH.md", "06_CHANGE_REQUEST_PROCESS_TH.md",
                 "07_FINAL_ACCEPTANCE_CRITERIA.md"):
        if not (SHARED / name).exists():
            problems.append(f"STRUCTURE SHARED_V3 missing {name}")
    if not (HANDOFF / "FINAL_INTEGRATION_PLAYBOOK_TH.md").exists():
        problems.append("STRUCTURE missing FINAL_INTEGRATION_PLAYBOOK_TH.md")
    # 2. sync up to date
    n_sync = 0
    for p in package_files():
        text = p.read_text(encoding="utf-8")
        n_sync += len(SYNC_RE.findall(text))
        if synced_text(text) != text:
            problems.append(f"OUT OF SYNC {p.relative_to(ROOT).as_posix()} (run --sync)")
    # 3. paths (the generated AUTO block quotes earlier problems verbatim, so it is not re-scanned)
    for d in all_docs():
        text = re.sub(r"<!-- AUTO:BEGIN -->.*?<!-- AUTO:END -->", "", d.read_text(encoding="utf-8"), flags=re.S)
        check_paths(tracked, pr16, d, text, problems, stats)
    # 4. ownership tables
    check_ownership_tables(rules, pr16, problems, stats)
    # 5. contract examples
    ex = sorted(EXAMPLES.glob("*.json"))
    for e in ex:
        try:
            json.loads(e.read_text(encoding="utf-8"))
        except ValueError as exc:
            problems.append(f"BAD JSON {e.name}: {exc}")
    # 6. secrets / private data (values never printed)
    sens = sensitive_values()
    scan = all_docs() + ex
    for p in scan:
        t = p.read_text(encoding="utf-8")
        for label, val in sens.items():
            if val and val in t:
                problems.append(f"SENSITIVE {p.relative_to(ROOT).as_posix()}: contains the {label}")
        for pat, label in ((r"[A-Za-z0-9._%+-]+@gmail\.com", "a Gmail address"), (r"ghp_[A-Za-z0-9]{20,}", "a GitHub token"),
                           (r"github_pat_", "a GitHub token"), (r"-----BEGIN [A-Z ]*PRIVATE KEY", "a private key")):
            if re.search(pat, t):
                problems.append(f"SENSITIVE {p.relative_to(ROOT).as_posix()}: contains {label}")
    summary = {
        "packages": len(PACKAGES), "files_per_package": len(REQUIRED), "markdown_docs": len(all_docs()),
        "sync_regions": n_sync, "contract_examples": len(ex),
        "path_refs_existing": stats["exists"], "path_refs_planned": stats["planned"],
        "path_refs_pr16": stats["pr16"], "path_refs_gitignored": stats["ignored"],
        "ownership_rows_ok": stats["own_ok"], "ownership_rows_pr16": stats["own_pr16"],
        "sensitive_values_checked": len(sens) + 4, "problems": len(problems),
    }
    for p in problems:
        print(p)
    print("check:", json.dumps(summary))
    print("check:", "OK" if not problems else f"FAIL ({len(problems)} problem(s))")
    if write_report:
        write_auto_block(summary, problems)
    return 0 if not problems else 1


def write_auto_block(summary: dict, problems: list[str]):
    head = git("rev-parse", "--short", "HEAD").strip()
    lines = [f"Generated by `scripts/build_handoff_packages.py --check --write-report` on "
             f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} (working tree based on commit `{head}`).", "",
             "| Check | Result |", "|---|---|"]
    labels = {
        "packages": "Packages", "files_per_package": "Required files per package (all present)",
        "markdown_docs": "Markdown documents scanned", "sync_regions": "SYNC regions (all identical to SHARED_V3)",
        "contract_examples": "Recorded contract examples (valid JSON)",
        "path_refs_existing": "Path references that exist in the repo", "path_refs_planned": "Path references to planned (new) files",
        "path_refs_pr16": "Path references that exist only on PR #16 branch", "path_refs_gitignored": "Path references to git-ignored locations",
        "ownership_rows_ok": "Ownership-table rows matching OWNERSHIP_MAP.csv (owner + approval)",
        "ownership_rows_pr16": "Ownership rows for PR #16 files (exist on that branch)",
        "sensitive_values_checked": "Sensitive patterns checked (demo tokens, student-ID-like numbers, Gmail, tokens, keys)",
        "problems": "**Problems found**",
    }
    for k, v in summary.items():
        lines.append(f"| {labels[k]} | {v} |")
    if problems:
        lines += ["", "Problems:", ""] + [f"- {p}" for p in problems]
    block = "<!-- AUTO:BEGIN -->\n" + "\n".join(lines) + "\n<!-- AUTO:END -->"
    text = REPORT.read_text(encoding="utf-8")
    text = re.sub(r"<!-- AUTO:BEGIN -->.*?<!-- AUTO:END -->", lambda _m: block, text, flags=re.S)
    REPORT.write_text(text, encoding="utf-8", newline="\n")
    print(f"report: updated {REPORT.relative_to(ROOT).as_posix()}")


# ------------------------------------------------------------------ zip

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_zip(target: Path, top: str, members: list[tuple[Path, str]]):
    head = git("rev-parse", "--short", "HEAD").strip()
    dirty = bool(git("status", "--porcelain", "--", str(HANDOFF.relative_to(ROOT))).strip())
    manifest = [f"{top} - Smart Library NEXT V3 documentation package (NOT a code repository)",
                f"Built: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} from repo commit {head}"
                + (" + uncommitted handoff edits" if dirty else ""),
                "Source of truth: docs/team_v3/individual_handoff/ in the PRIVATE repo Zinnarin/SmartLibrary-NEXT.",
                "Internal team material: share only inside the team. Contains no code, tokens, databases, images of people or student IDs.",
                "", "sha256  path"]
    stamp = (2026, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in members:
            manifest.append(f"{sha(src)}  {top}/{arc}")
            info = zipfile.ZipInfo(f"{top}/{arc}", date_time=stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, src.read_bytes())
        info = zipfile.ZipInfo(f"{top}/MANIFEST.txt", date_time=stamp)
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, ("\n".join(manifest) + "\n").encode("utf-8"))
    print(f"zip: {target.relative_to(ROOT).as_posix() if target.is_relative_to(ROOT) else target}  ({len(members)} files + MANIFEST)")


def do_zip(out: Path) -> int:
    if do_check(False):
        print("zip: refused - fix the check problems first")
        return 1
    out.mkdir(parents=True, exist_ok=True)
    for key, (folder, zname, prefixes) in PACKAGES.items():
        members = [(p, p.name) for p in sorted((HANDOFF / folder).glob("*.md"))]
        members += [(e, f"contract_examples/{e.name}") for e in sorted(EXAMPLES.glob("*.json"))
                    if any(e.name.startswith(pre if "__" in pre else pre + "__") for pre in prefixes)]
        if key == "P4":
            members.append((HANDOFF / "FINAL_INTEGRATION_PLAYBOOK_TH.md", "FINAL_INTEGRATION_PLAYBOOK_TH.md"))
        write_zip(out / zname, zname[:-4], members)
    shared = [(p, p.name) for p in sorted(SHARED.glob("*.md"))]
    shared += [(e, f"contract_examples/{e.name}") for e in sorted(EXAMPLES.glob("*.json"))]
    shared += [(HANDOFF / "FINAL_INTEGRATION_PLAYBOOK_TH.md", "FINAL_INTEGRATION_PLAYBOOK_TH.md"),
               (HANDOFF / "README_TH.md", "README_TH.md")]
    write_zip(out / SHARED_ZIP, SHARED_ZIP[:-4], shared)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sync", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write-report", action="store_true")
    ap.add_argument("--zip", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "artifacts" / "handoff_v3"))
    a = ap.parse_args()
    if not (a.sync or a.check or a.zip):
        ap.print_help()
        return 2
    rc = 0
    if a.sync:
        rc |= do_sync()
    if a.check:
        rc |= do_check(a.write_report)
    if a.zip:
        rc |= do_zip(Path(a.out).resolve())
    return rc


if __name__ == "__main__":
    sys.exit(main())
