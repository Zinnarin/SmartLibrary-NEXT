# 07 — Final acceptance criteria for the integrated V3 system

Every criterion is measured on **one final commit** of `main`, the one tagged `v3-integrated-demo`. **PASS** means the command or check was actually run on that commit and its output is saved under `evidence/team_v3/final/`. A criterion that cannot be run is reported as **BLOCKED** with the reason. Nobody marks PASS without running the check.

Paths marked *(planned)* do not exist yet. They are created during the sprint by their owner.

## A. V2 must not regress (all mandatory)

| ID | Criterion | How to verify | Pass condition |
|---|---|---|---|
| FA-01 | All backend tests pass, including the 53 V2 tests | `.venv\Scripts\python -m pytest -q` | 0 failed, 0 errors; at least 53 tests collected |
| FA-02 | All browser tests pass: the 8 V2 tests plus the new V3 specs | `powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1` (server running) | exit 0; Playwright 0 failed, 0 flaky |
| FA-03 | Frontend builds | `cd apps\web; npm run build` | exit 0 |
| FA-04 | Ownership is complete and frozen V2 files are untouched | `python scripts\check_ownership.py --audit`; after the full test run, `git status --short -- evidence presentation verification reference templates` | `audit: OK`; the git command prints nothing (V3 output only in `artifacts/` or `evidence/team_v3/`) |
| FA-05 | CI green | GitHub Actions on the final commit | `backend` and `frontend` jobs succeed |

## B. Interfaces (contracts C1–C4 in `03_SHARED_API_CONTRACTS.md`)

| ID | Criterion | How to verify | Pass condition |
|---|---|---|---|
| FA-10 | C1 provider behaviour | `tests/test_backend_v3.py` *(planned, P2)* | covers `applied`, `duplicate`, `late`, clock skew, non-`ok` quality, bad/missing token, non-CV camera, seat on another camera, unknown seat, whole-frame rollback; all pass |
| FA-11 | C1 sender conformance | `tests/test_cv_v3.py` *(planned, P1)* | every payload produced by the CV code validates against `IngestIn`; a sample is accepted by a test server and returns `applied`; a replay returns `duplicate` |
| FA-12 | A malformed timestamp is a client error | test in `tests/test_backend_v3.py` | `observed_at_utc: "yesterday"` returns 422 and no row is stored (PA-02 fixed) |
| FA-13 | C2/C3 compatibility | `tests/test_contract_v3.py` *(planned, P4)* | for every recorded example in `contract_examples/`, all recorded keys still exist in the live response with the same JSON type; the enum values in C0 are unchanged |
| FA-14 | Full SeatCheck loop (C4 + C3) | `apps/web/e2e/staff_reliability_v3.spec.ts` *(planned, P4)* | student report → seat shows pending and leaves the recommendations → staff resolves with a reason and the `unknown` override → the student page updates **without reload within 5 s** → audit events `report` and `report_resolved` exist |
| FA-15 | Student flow on V3 UI | `apps/web/e2e/student_v3.spec.ts` *(planned, P3)* | filters → reasons → GroupFit → Wayfinder → SeatCheck → WS update; no horizontal scroll at 360–390 px; 0 console errors |

## C. Safety and truthfulness

| ID | Criterion | How to verify | Pass condition |
|---|---|---|---|
| FA-20 | Unsafe seats are never recommended | `tests/test_reliability.py::test_recommendations_never_include_unsafe_states_across_scenarios` (+ any V3 extension) | pass |
| FA-21 | Server loss never leaves seats green (BUG-011) | `reliability.spec.ts`, `server_restart.spec.ts` | pass |
| FA-22 | One report never changes the physical state | `tests/test_api.py::test_T08_seatcheck_report_does_not_set_occupied` | pass |
| FA-23 | Camera loss / stale | `test_T03_camera_lost_then_ttl_stale`, `test_heartbeat_timeout_marks_silent_camera_offline_without_lwt` | pass; seat not recommendable within TTL + heartbeat timeout (30 s defaults) |
| FA-24 | Honest labelling | manual check of every page, screenshots saved to `evidence/team_v3/final/` | every SIMULATION seat or screen is labelled; CV data shows `source = cv` and the model version; no accuracy figure unless FA-30 passed |

## D. Computer vision measurement (P1)

| ID | Criterion | Pass condition |
|---|---|---|
| FA-30 | **Real-seat accuracy, only if authorized footage exists** (issue #14) | For each clip: a ground-truth CSV per time interval, the number of frames N, a confusion matrix over `available` / `occupied` / `reserved` / `unknown`, **False Available rate** = frames shown `available` while the truth is not available ÷ frames shown `available` (with N), Unknown coverage, and median inference ms/frame with the hardware named. Required behaviours: `walk_by` never committed as `occupied`; `dark` or `occluded` frames give `unknown`; `empty` becomes `available` only after smoothing. |
| FA-31 | **If no authorization** | Issue #14 stays `BLOCKED`; the final report and slides say "no real-seat accuracy measured"; the demo uses SIMULATION plus the sample-image CV pipeline, labelled as such. This counts as an honest PASS of the reporting criterion, **not** of FA-30. |

## E. One integrated system

| ID | Criterion | Pass condition |
|---|---|---|
| FA-40 | One-command start | `scripts\start_demo_windows.ps1 -Reset` on the demo laptop. The student page, Staff Console, Scenario Lab and CV Lab load with 0 console errors (journey e2e). |
| FA-41 | CV path visible end to end | A CV run posts through C1 and the result is visible with its source label: on the CV Lab page (LAB seats) **or**, only if PA-03 was approved and merged, on the student map |
| FA-42 | Release | Tag `v3-integrated-demo` on the verified commit, plus release notes listing what is REAL, SIMULATED, PARTIAL and BLOCKED |
| FA-43 | Evidence | `evidence/team_v3/final/` holds `pytest_junit.xml`, `playwright_results.json`, CV metrics (if FA-30), screenshots and the commit hash; `verification/TEAM_V3_ACCEPTANCE.csv` *(planned, P4)* has one row per FA ID with PASS / FAIL / BLOCKED and the evidence path |

## F. Process

| ID | Criterion | Pass condition |
|---|---|---|
| FA-50 | Every merged PR | CI green; `check_ownership.py --owner P#` has no `BLOCK`; `REVIEW` files approved by their owners |
| FA-51 | Every contract change | has a CR issue, an updated `docs/api_contract_v3.md` and updated examples |
| FA-52 | Credit | the final report lists who built what, and where AI tools helped |
