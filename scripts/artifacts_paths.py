"""Shared output-path policy for project scripts (P4).

Generated files go to <repo>/artifacts/ (git-ignored) or $SL_ARTIFACT_DIR. Writing into a FROZEN V2 path
(see docs/team_v3/OWNERSHIP_MAP.csv) is refused unless the caller explicitly allows it.
"""
from __future__ import annotations

import os
from pathlib import Path

import check_ownership as co

ROOT = co.ROOT


def is_frozen(path: str | Path) -> bool:
    p = Path(path)
    p = (ROOT / p) if not p.is_absolute() else p
    try:
        rel = p.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return False  # outside the repository
    return co.owner_of(rel, co.load_rules())["owner"] == "FROZEN"


def assert_writable(path: str | Path, allow_frozen: bool = False) -> Path:
    p = Path(path)
    p = (ROOT / p) if not p.is_absolute() else p
    if is_frozen(p) and not allow_frozen:
        raise SystemExit(f"refusing to write frozen V2 file: {p} - use artifacts/, evidence/team_v3/ or presentation/v3/")
    return p


def artifact_dir(sub: str = "") -> Path:
    base = Path(os.environ.get("SL_ARTIFACT_DIR") or (ROOT / "artifacts"))
    base = (ROOT / base) if not base.is_absolute() else base
    d = base / sub if sub else base
    assert_writable(d / ".probe")
    d.mkdir(parents=True, exist_ok=True)
    return d
