# P2 · 09 — Claude Code master prompt (Backend & Database)

How to use it:
1. Open the repository folder in Claude Code.
2. Make sure you are on `feature/v3-backend`.
3. Paste everything inside the box below.

The prompt is self-contained.

```text
ROLE AND PROJECT
You are helping PERSON 2 (Backend & Database owner) of a 4-student team improve an EXISTING, working system:
Smart Library NEXT (private repo Zinnarin/SmartLibrary-NEXT). It shows library seat status only as far as evidence
supports it (unknown/stale instead of guessing available). Do NOT rebuild, redesign or replace it.
Backend = FastAPI + stdlib sqlite3 (WAL, BEGIN IMMEDIATE) in services/api/app (MINE), pure-Python engine in
services/api/app/engine (MINE), WebSocket hub realtime.py (MINE). Web app apps/web (Persons 3/4), CV cv/ (Person 1).
V2 baseline tag: v2-demo-baseline. Person 4 integrates all work.

MY MISSION
Own the FastAPI backend, Seat State Engine, database + migrations, API contracts and realtime delivery:
receive CV evidence, validate observations, evaluate seat states, handle smoothing/freshness, store consistent data,
keep student/staff API compatibility, improve reliability and performance. Internal refactoring, better validation,
DB optimization, reliability work and useful backend features are allowed. Never silently change shared contracts,
never break student/staff clients, never replace the architecture without team approval.

STEP 0 - INSPECT BEFORE CHANGING ANYTHING (report findings to me first)
1. git status; git branch --show-current (must be feature/v3-backend); git fetch origin; git merge origin/main.
2. Read my package docs/team_v3/individual_handoff/P2_BACKEND_DATABASE/01..08, the full contract snapshot
   docs/team_v3/individual_handoff/SHARED_V3/03_SHARED_API_CONTRACTS.md (C0-C4, PA, CT) and the recorded real
   responses in SHARED_V3/contract_examples/*.json, plus docs/team_v3/OWNERSHIP_MAP.csv.
3. Read the real code: services/api/app/main.py (models + 26 routes), services.py, engine/{evidence,state_engine,
   trust,config,timeutil}.py, realtime.py, matching.py, db.py, settings.py, seed.py, scenarios.py, tests/*.py.
   Note consumers: cv/run_cv.py imports EngineConfig, Detection, classify, SeatEngineState, step (contract C1b);
   apps/web/src/api.ts and live.tsx consume SeatView/meta/WS; api.ts parses the session token as <sid>.<exp>.<sig>.
4. Baseline: .venv\Scripts\python -m pytest -q (expected 53 passed). Report the exact output.

KNOWN FACTS FROM THE 2026-10-16 CONTRACT PROBE
- POST /api/ingest/observations with observed_at_utc="yesterday" raises an unhandled ValueError (HTTP 500) -> fix as
  422 (PA-02). One bad seat in a frame rolls back the whole frame (by design; document it).
- settings.cv_evidence_dir = evidence/cv (FROZEN V2 evidence) and AppSettings.from_env() has no variable for it (PA-01).
- No schema versioning/migrations; LAB1-LAB4 (CV-LAB) are hidden from the student map (is_active=0).

CHANGE LEVELS
GREEN (do it): internal refactor, indexes, tests, logging, 500->4xx for already-invalid input.
YELLOW (draft a change request for Person 4 BEFORE coding; update docs/api_contract_v3.md + contract_examples in the
same PR): new optional field/endpoint/env/error code, user-visible default changes, requirements.txt, conftest.py,
response_model, schema changes visible via the API.
RED (all 4 approve in an issue): removing/renaming routes or fields, changing state meanings, changing the DB engine,
real CV seats on the public map (PA-03), weakening any safety rule.
Template: P2_BACKEND_DATABASE/07_CHANGE_REQUEST_TEMPLATE.md.

HARD RULES
- Modify ONLY: services/api/**, tests/conftest.py (needs P1/P3/P4 review), tests/test_api.py,
  tests/test_state_engine.py, tests/test_backend_v3.py, docs/api_contract_v3.md. Never edit apps/**, cv/**, scripts/*,
  .github/*, pytest.ini or frozen V2 files (evidence/*, presentation/*, verification/*, reference/*, templates/*,
  spec docs in docs/*).
- Keep every safety invariant: recommendable only when not_recommendable_reasons is empty; one report never sets
  occupied; override wins; gap > TTL resets to unknown; out-of-order/duplicate never change state; scenario and cv
  sources never mix. Never weaken an existing test assertion.
- Keep C1b signatures importable. Keep error shapes ({error, message_th} and FastAPI detail[]).
- Never fabricate results; never mark a test PASS without running it; never call simulated data real; never commit
  DB files or tokens. Do not merge to main.

WORK PLAN (one item at a time; test; report)
B1 docs/api_contract_v3.md from the snapshot, re-verified against code, with tests proving examples (team's first PR);
B2 PA-02; B3 tests/test_backend_v3.py (applied, duplicate, late, clock skew, non-ok quality, missing/wrong token,
non-CV camera, seat on another camera, unknown seat, whole-frame rollback, malformed timestamp); B4 PA-01
SL_CV_EVIDENCE_DIR (agree location with Person 1); B5 lightweight migrations (schema version + ordered migrations,
old V2 demo DB must still open); B6 pruning test + measured performance; B7 response_model without JSON changes;
B8 PA-03 only after RED approval.

BEFORE EACH PR
Run pytest; npm run build in apps/web; with the server running scripts\run_tests_windows.ps1 (Playwright);
scripts\check_ownership.py --owner P2 --base origin/main; the C1b import check. Give me exact outputs and a PR
description using .github/pull_request_template.md that lists every contract change and which consumers must review.
```
