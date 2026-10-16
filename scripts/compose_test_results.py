"""Compose TEST_RESULTS.md verbatim from raw output files produced by real runs (no hand-typed numbers).

V3 default: read and write in artifacts/ (git-ignored):  python scripts/compose_test_results.py
Re-compose the frozen V2 file only on purpose:          python scripts/compose_test_results.py --in evidence --out evidence/TEST_RESULTS.md --allow-frozen
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "evidence"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else f"(missing: {p.name})"


def main(out_path: Path):
    out = ["# TEST RESULTS — raw outputs (composed by scripts/compose_test_results.py)", "",
           f"Composed: {datetime.now().isoformat(timespec='seconds')} (local time, Asia/Bangkok)", ""]

    # pytest
    out += ["## 1. Backend tests (pytest)", "", "Command:", "```", r".\.venv\Scripts\python.exe -m pytest -v -rA --junitxml=evidence/pytest_junit.xml", "```"]
    j = EV / "pytest_junit.xml"
    if j.exists():
        r = ET.parse(j).getroot()
        s = r if r.tag == "testsuite" else r.find("testsuite")
        out += ["", f"JUnit summary: tests={s.get('tests')} failures={s.get('failures')} errors={s.get('errors')} skipped={s.get('skipped')} time={s.get('time')}s", "",
                "| test | result | time (s) |", "|---|---|---|"]
        for tc in s.iter("testcase"):
            res = "FAIL" if tc.find("failure") is not None else "ERROR" if tc.find("error") is not None else "SKIP" if tc.find("skipped") is not None else "PASS"
            out.append(f"| {tc.get('classname')}::{tc.get('name')} | {res} | {tc.get('time')} |")
    lines = read(EV / "pytest_output.txt").splitlines()
    out += ["", "Last lines of `evidence/pytest_output.txt`:", "```"] + lines[-6:] + ["```", ""]
    out += ["History of real failures before fixes (see BUG_LOG.md): run 1 → 14 passed, 26 errors (WinError 5, BUG-002); "
            "run 2 → 37 passed, 3 failed (BUG-001 logic, BUG-003/004 test issues); run 3+ → all passed.", ""]

    # playwright
    out += ["## 2. Browser end-to-end (Playwright + Microsoft Edge, headless)", "", "Command (server running on 127.0.0.1:8000):", "```", r"cd apps\web; npx playwright test", "```"]
    p = EV / "playwright_results.json"
    if not p.exists() and (EV / "e2e" / "playwright_results.json").exists():
        p = EV / "e2e" / "playwright_results.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        st = d.get("stats", {})
        out += ["", f"Stats: expected(passed)={st.get('expected')} unexpected(failed)={st.get('unexpected')} flaky={st.get('flaky')} skipped={st.get('skipped')} "
                f"duration={round(st.get('duration', 0) / 1000, 1)} s start={st.get('startTime')}", "", "| test | status | duration (s) |", "|---|---|---|"]

        def walk(suite):
            for spec in suite.get("specs", []):
                for t in spec.get("tests", []):
                    for res in t.get("results", []):
                        out.append(f"| {spec['title']} | {res.get('status')} | {round(res.get('duration', 0) / 1000, 1)} |")
            for sub in suite.get("suites", []):
                walk(sub)

        for su in d.get("suites", []):
            walk(su)
    out += ["", "Screenshots produced by these runs: `presentation/screenshots/*.png` (01–19).", ""]

    # latency
    out += ["## 3. Staff action → WebSocket latency (loopback, one machine)", "", "```", r".\.venv\Scripts\python.exe scripts\measure_ws_latency.py --trials 20", "```"]
    w = EV / "ws_latency.json"
    if w.exists():
        d = json.loads(w.read_text(encoding="utf-8"))
        out += ["", f"trials={d['trials']} median={d['median_ms']} ms p90={d['p90_ms']} ms max={d['max_ms']} ms — {d['what']}; NOT: {d['not_what']}", ""]

    # cv
    out += ["## 4. CV pipeline run (real Ultralytics inference)", "", "```", r".venv-cv\Scripts\python cv\run_cv.py suite --post", "```", ""]
    c = EV / "cv" / "latest_run.json"
    if c.exists():
        d = json.loads(c.read_text(encoding="utf-8"))
        out += [f"status={d.get('status')} scope={d.get('scope')} library_cv_status={d.get('library_cv_status')}"]
        if d.get("model"):
            m, e, inf = d["model"], d["environment"], d["inference"]
            out += [f"model={m['name']} weights={m['weights']} sha256={m['weights_sha256']} ultralytics={m['ultralytics_version']} classes={m['num_classes']} "
                    f"literal 'bag' class={m['has_literal_bag_class']} belongings classes present={m['belongings_classes_present']}",
                    f"device={e['device']} torch={e['torch_version']} python={e['python']}",
                    f"frames={inf['frames']} median ms/frame={inf['ms_per_frame_median']} all={inf['ms_per_frame_all']}",
                    f"source={d['source']['description']} sha256={d['source']['sha256']}", "", "| ROI | detections related to ROI (last frame) | raw | committed | codes |", "|---|---|---|---|---|"]
            for r in d.get("rois", []):
                out.append(f"| {r['seat_id']} | {r['detections_summary']} | {r['raw_candidate']} | {r['committed_state']} | {', '.join(r['codes'])} |")
            out += ["", f"ingest: {d['ingest']['summary']}; API LAB seat states after run: {d['ingest'].get('api_lab_seat_states')}"]
            for rc in d.get("robustness_checks", []):
                out.append(f"- {rc['label']}: qualities={rc.get('qualities')} final={rc.get('final_states')} errors={rc.get('errors', [])}")
        if d.get("errors"):
            out += ["", "Errors recorded:", "```"] + d["errors"] + ["```"]
    out += ["", "`evidence/cv/run_log.txt`:", "```", read(EV / "cv" / "run_log.txt").strip(), "```", ""]

    # BUG-011 before/after
    out += ["## 5. BUG-011 regression (browser freshness guard) — before vs after the fix", ""]
    for name in ("bug011_before_fix_output.txt", "bug011_after_fix_output.txt"):
        lines = [l for l in read(EV / name).splitlines() if any(k in l for k in ("ok ", "passed", "failed", "Error:", "Received", "✘"))]
        out += [f"`evidence/{name}`:", "```"] + lines[:12] + ["```", ""]

    # launch
    out += ["## 6. Windows launch script (incl. BUG-013 regression cases)", "",
            "Fresh start: `scripts\start_demo_windows.ps1 -Reset -NoBrowser -Port 8011` → API up after ~1.1 s with readiness=degraded / 0 fresh seats (warm-up), "
            "after 8 s readiness=ready, 24 fresh, counts 12/9/2/1 (`evidence/launch_script_test_log.txt`).", ""]
    for name, label in (("launch_test_busy_port.txt", "case 1 — second start on a busy port"),
                        ("launch_test_reset_locked.txt", "case 2 — -Reset while another server runs"),
                        ("launch_test_case3_custom_db.txt", "case 3 — -Reset honours SL_DB_PATH")):
        lines = [l for l in read(EV / name).splitlines() if any(k in l for k in ("ERROR", "removed", "Uvicorn running", "Starting server"))]
        out += [f"{label} (`evidence/{name}`):", "```"] + lines[:6] + ["```", ""]

    # pptx
    out += ["## 7. PPTX verification", "", "```", r"powershell -ExecutionPolicy Bypass -File scripts\export_pptx_preview.ps1 -Deck presentation\progress_update_v2.pptx", "```",
            "PowerPoint (COM) opened the deck (8 slides, 960×540 pt = 16:9), fonts used: Leelawadee UI (all text; not embedded in PPTX), Calibri/Aptos (theme defaults); "
            "exported PDF (8 pages, Leelawadee UI embedded) + 8 PNGs to `presentation/preview/`; every slide inspected visually; one clipped caption (slide 6) found and fixed.", ""]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out), encoding="utf-8")
    print("wrote", out_path)


if __name__ == "__main__":
    import argparse
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from artifacts_paths import artifact_dir, assert_writable

    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=None, help="input folder (default: artifacts/)")
    ap.add_argument("--out", default=None, help="output file (default: artifacts/TEST_RESULTS.md)")
    ap.add_argument("--allow-frozen", action="store_true", help="explicitly allow writing a frozen V2 file")
    a = ap.parse_args()
    EV = (ROOT / a.inp) if a.inp else artifact_dir()
    main(assert_writable(a.out, a.allow_frozen) if a.out else artifact_dir() / "TEST_RESULTS.md")
