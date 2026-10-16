# P2 · 06 — Acceptance criteria (Backend & Database)

**PASS** means you ran the check on your branch and the real output is in the PR.

## Mandatory (every P2 PR)

| ID | Criterion | Command / check | Pass condition |
|---|---|---|---|
| AC-P2-01 | No regression | `.venv\Scripts\python -m pytest -q` | 0 failed; at least 53 tests, plus your new ones |
| AC-P2-02 | Frontend still builds and runs against your API | `cd apps\web; npm run build` | exit 0 |
| AC-P2-03 | Browser regression | server running → `powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1` | Playwright 8/8 (plus any new specs) pass; frozen files restored or untouched |
| AC-P2-04 | Ownership | `.venv\Scripts\python scripts\check_ownership.py --owner P2 --base origin/main` | no `BLOCK`; `requirements.txt`/`conftest.py` changes approved |
| AC-P2-05 | Contract kept | every recorded example in `contract_examples/` still holds: same keys, same JSON types, same status codes, except where an approved CR changed it and the example was updated | test or script output in the PR |
| AC-P2-06 | C1b intact | `.venv\Scripts\python -c "import sys; sys.path.insert(0,'services/api'); from app.engine.config import EngineConfig; from app.engine.evidence import Detection, classify; from app.engine.state_engine import SeatEngineState, step; print('C1b OK')"` | prints `C1b OK` |

## Functional (the mission)

| ID | Criterion | Pass condition |
|---|---|---|
| AC-P2-10 | `docs/api_contract_v3.md` (issue #1) | covers all 26 routes + WS messages + auth headers + error codes + enums. Examples match real responses: a test checks at least a seat view, a recommendation and an ingest result. Approved by P1, P3 and P4. |
| AC-P2-11 | Ingest contract tests (issue #2) | `tests/test_backend_v3.py` covers `applied`, `duplicate`, `late`, clock skew, each non-`ok` quality → `unknown`, missing and wrong token, non-CV camera, seat on another camera, unknown seat, whole-frame rollback, malformed timestamp |
| AC-P2-12 | PA-02 | a malformed `observed_at_utc` returns **422** with a stable `error` code; nothing is stored; the device is not touched |
| AC-P2-13 | PA-01 (issue #3) | `SL_CV_EVIDENCE_DIR` works; the default behaviour is unchanged when it is unset; `GET /api/cv/status` reads the new location; a test covers it |
| AC-P2-14 | Migration (if the schema changes) | an old demo DB created by V2 opens and migrates automatically; a test proves it; the migration note is in the PR |
| AC-P2-15 | Reliability | pruning has a test. Any performance claim gives the measured number, the method and the hardware, e.g. `seat_views` time for N seats. |

## Safety invariants (must stay green after every change)

`test_T03_camera_lost_then_ttl_stale`, `test_T07_maintenance_override_wins_and_is_audited`, `test_T08_seatcheck_report_does_not_set_occupied`, `test_T13_duplicate_and_out_of_order_observations`, `test_gap_longer_than_ttl_resets_to_unknown_BUG001`, `test_source_contamination_guards`, `test_recommendations_never_include_unsafe_states_across_scenarios`.

Weakening any of their assertions is **RED**.
