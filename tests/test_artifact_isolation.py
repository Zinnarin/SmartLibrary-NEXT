"""Regression: running tests or project tools must never overwrite frozen V2 evidence (P4 / QA).

Background: before V3 a single Playwright run rewrote 23 committed files (evidence/playwright_results.json and
22 screenshots in presentation/screenshots/). Generated output now goes to artifacts/ (git-ignored).
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import artifacts_paths as ap  # noqa: E402
import check_ownership as co  # noqa: E402

WEB = ROOT / "apps" / "web"
FROZEN_WRITE = re.compile(r"""["'`][^"'`]*(presentation[/\\]screenshots|presentation[/\\]preview|evidence[/\\](?!team_v3)[\w./-]*\.(json|png|txt|md))""")


def _code_lines(path: Path):
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith(("//", "*", "/*", "#")):
            continue  # comments may mention the old locations
        yield n, line


def test_e2e_specs_and_config_do_not_write_frozen_paths():
    files = sorted((WEB / "e2e").glob("*.ts")) + [WEB / "playwright.config.ts"]
    hits = [f"{f.name}:{n}: {l.strip()}" for f in files for n, l in _code_lines(f) if FROZEN_WRITE.search(l)]
    assert hits == [], "test code still targets frozen V2 files:\n" + "\n".join(hits)
    specs = [f for f in (WEB / "e2e").glob("*.spec.ts") if "screenshot(" in f.read_text(encoding="utf-8")]
    assert specs, "expected specs that take screenshots"
    for f in specs:
        assert 'from "./artifacts"' in f.read_text(encoding="utf-8"), f"{f.name} must take SHOTS from ./artifacts"


def test_playwright_results_go_to_artifacts():
    cfg = (WEB / "playwright.config.ts").read_text(encoding="utf-8")
    assert "E2E_DIR" in cfg and "outputFile" in cfg and "evidence/playwright_results.json" not in cfg


def test_artifact_dir_helper_refuses_frozen_targets():
    src = (WEB / "e2e" / "artifacts.ts").read_text(encoding="utf-8")
    for token in ('"evidence"', '"presentation"', '"evidence/team_v3"', '"presentation/v3"', "throw new Error"):
        assert token in src


def test_powershell_tools_write_to_artifacts():
    rt = (ROOT / "scripts" / "run_tests_windows.ps1").read_text(encoding="utf-8")
    assert "evidence\\pytest_output.txt" not in rt and "evidence\\playwright_output.txt" not in rt
    assert '"artifacts"' in rt and "--frozen-clean" in rt
    ex = (ROOT / "scripts" / "export_pptx_preview.ps1").read_text(encoding="utf-8")
    assert '$OutDir = "artifacts\\pptx_preview"' in ex and "frozen V2 output" in ex


@pytest.mark.parametrize("target,frozen", [
    ("evidence/playwright_results.json", True),
    ("evidence/TEST_RESULTS.md", True),
    ("evidence/ws_latency.json", True),
    ("presentation/screenshots/01_student_normal.png", True),
    ("presentation/progress_update_v2.pptx", True),
    ("presentation/preview/progress_update.pdf", True),
    ("artifacts/e2e/playwright_results.json", False),
    ("evidence/team_v3/run1/TEST_RESULTS.md", False),
    ("presentation/v3/progress_update_v3.pptx", False),
])
def test_python_tools_path_policy(target, frozen):
    assert ap.is_frozen(target) is frozen
    if frozen:
        with pytest.raises(SystemExit):
            ap.assert_writable(target)
        assert ap.assert_writable(target, allow_frozen=True)  # only with an explicit flag


def test_python_tool_defaults_are_not_frozen():
    for script, needle in (("compose_test_results.py", 'artifact_dir() / "TEST_RESULTS.md"'),
                           ("measure_ws_latency.py", 'artifact_dir() / "ws_latency.json"'),
                           ("build_pptx.py", 'ROOT / "artifacts" / "pptx" / "progress_update_draft.pptx"')):
        assert needle in (ROOT / "scripts" / script).read_text(encoding="utf-8"), script
    assert not ap.is_frozen(ROOT / "artifacts" / "pptx" / "progress_update_draft.pptx")


def test_build_pptx_refuses_frozen_deck_without_flag():
    # Probe with a NON-existing file inside the frozen folder: even if an old/broken build_pptx.py ignored the
    # guard, no real V2 deck can be overwritten by this test (a probe file would be removed again).
    probe = ROOT / "presentation" / "__frozen_probe__.pptx"
    try:
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_pptx.py"), "presentation/__frozen_probe__.pptx"],
                           cwd=ROOT, capture_output=True, text=True, timeout=120)
        assert r.returncode != 0 and "refusing to write frozen V2 file" in (r.stdout + r.stderr)
        assert not probe.exists()
    finally:
        probe.unlink(missing_ok=True)


def test_artifacts_folder_is_git_ignored():
    assert "artifacts/" in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    if shutil.which("git") and (ROOT / ".git").exists():
        r = subprocess.run(["git", "check-ignore", "-q", "artifacts/e2e/screenshots/x.png"], cwd=ROOT)
        assert r.returncode == 0


@pytest.mark.skipif(not (ROOT / ".git").exists() or not shutil.which("git"), reason="not a git checkout")
def test_frozen_files_unchanged_in_working_tree():
    """Fails if anything (a test run, a tool) has modified frozen V2 files in this checkout."""
    assert co.frozen_clean(co.load_rules()) == 0
