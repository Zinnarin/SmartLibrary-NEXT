# P2 · 03 — Existing code and ownership (Backend & Database)

Paths were verified with `git ls-files` on 2026-10-16. The rules live in `docs/team_v3/OWNERSHIP_MAP.csv` (first match wins). Check with `python scripts/check_ownership.py --owner P2 --base origin/main`.

## Files you own

| Path | Owner | Approval from | Status |
|---|---|---|---|
| `services/api/app/main.py` | P2 | — | exists |
| `services/api/app/services.py` | P2 | — | exists |
| `services/api/app/db.py` | P2 | — | exists |
| `services/api/app/realtime.py` | P2 | — | exists |
| `services/api/app/matching.py` | P2 | — | exists |
| `services/api/app/settings.py` | P2 | — | exists |
| `services/api/app/seed.py` | P2 | — | exists (demo reset; P4 proposes test cases) |
| `services/api/app/scenarios.py` | P2 | — | exists (SIMULATION scenarios) |
| `services/api/app/engine/evidence.py` | P2 | — | exists (imported by `cv/run_cv.py`) |
| `services/api/app/engine/state_engine.py` | P2 | — | exists (imported by `cv/run_cv.py`) |
| `services/api/app/engine/config.py` | P2 | — | exists (imported by `cv/run_cv.py`) |
| `services/api/app/engine/trust.py` | P2 | — | exists |
| `services/api/app/engine/timeutil.py` | P2 | — | exists |
| `services/api/requirements.txt` | P2 | P4 | exists |
| `tests/conftest.py` | P2 | P1;P3;P4 | exists (shared fixtures) |
| `tests/test_api.py` | P2 | — | exists (27 tests) |
| `tests/test_state_engine.py` | P2 | — | exists (15 tests) |
| `tests/test_backend_v3.py` | P2 | — | new, planned (issue #2) |
| `docs/api_contract_v3.md` | P2 | P1;P3;P4 | new, planned (issue #1 — the team's first PR) |

You also **co-approve** these files, which are owned by others:
- `tests/test_reliability.py`, `pytest.ini`, `scripts/start_demo_windows.ps1` and `apps/web/src/pages/ScenarioLab.tsx` (all P4).

The demo DB `services/api/data/smartlibrary_demo.db` is git-ignored and never committed.

## Code map (verified line numbers on `main` @ `edc7903`)

| File:line | Symbol | Notes |
|---|---|---|
| `main.py:44–90` | `ReportIn`, `ResolveIn`, `OverrideIn`, `ScenarioIn`, `DetectionIn`, `SeatObsIn`, `IngestIn` | request models = contract C1/C3/C4 |
| `main.py:96` | `create_app(settings, cfg, clock)` | app factory; seeds when empty; demo mode starts `NORMAL` |
| `main.py:124` | `meta()` | the `meta` object (C2) |
| `main.py:153` | `ticker()` | every `SL_TICK_S`: scenario frames (demo), `expire_overrides`, prune scenario observations > 2 h |
| `main.py:192–199` | error handlers | `{"error", "message_th"}` shape; Pydantic `detail[]` is FastAPI's default |
| `main.py:203` / `217` | `require_staff` / `require_session` | `X-Staff-Token` (logs a `security` event on failure) / HMAC session token |
| `main.py:232–401` | public read API | `/api/health`, `/zones`, `/layout`, `/seats`, `/seats/{id}`, `/recommendations`, `/route`, `/stats`, `/cv/status`, `/cv/annotated/{name}` |
| `main.py:405–424` | SeatCheck | `/api/session`, `POST /api/seat-reports`, `/api/seat-reports/mine` |
| `main.py:428–467` | staff | `/api/admin/*` |
| `main.py:471–491` | demo | `/api/demo/*` (demo mode only) |
| `main.py:495` | `ingest()` | C1; **`parse_iso(body.observed_at_utc)` on line 502 raises an unhandled ValueError on bad input → 500 (PA-02)** |
| `main.py:521` | `cv_lab_seats()` | LAB seats with `include_lab=True` |
| `main.py:529` | `ws_seats()` | WebSocket; replies `pong` to `ping` |
| `services.py:61` | `ingest_observation()` | duplicate → seat → camera → source checks; clock skew; `classify` + `step`; inserts the observation even when `late` |
| `services.py:233` / `293` | `create_report()` / `resolve_report()` | rate limits (3 per 10 min, same-seat cooldown), replay, audit, resolution latency |
| `services.py:335` | `_set_override_tx()` | allowed states, expiry 1–10080 min, supersedes older |
| `services.py:377` | `expire_overrides()` | called by the ticker |
| `services.py:393` / `419` | `seat_views()` / `device_views()` | build every SeatView (C2) |
| `engine/evidence.py:84` | `classify()` | decision order (C1) |
| `engine/state_engine.py:71` | `step()` | smoothing, gap reset, out-of-order |
| `engine/trust.py:39` | `build_seat_view()` | **the SeatView contract** (C2); `REASON_TH`, `STATE_LABEL_TH` |
| `engine/config.py:36` | `EngineConfig` | thresholds + `from_env()` + `public_dict()` |
| `realtime.py:28` | `Hub` | snapshot/delta/heartbeat; volatile fields excluded from hashing |
| `matching.py:196` / `73` | `recommend()` / `Graph` | StudyMatch, GroupFit (2 only), Wayfinder |
| `db.py:15` | `SCHEMA` | 13 tables, `CREATE TABLE IF NOT EXISTS`, no version number |
| `settings.py:12` / `27` | `AppSettings` / `from_env()` | env: `SL_DB_PATH`, `SL_MODE`, `SL_STAFF_TOKEN`, `SL_DEVICE_TOKEN`, `SL_TICK_S` (**no** CV dir variable) |
| `seed.py:16–103` | `ZONES`, `DEVICES`, `WAYPOINTS`, `SEATS`, `ADJACENCY`, `LAB_SEATS` | illustrative data |

## Who consumes what you provide

| Your code | Consumer | Breaks if you change… |
|---|---|---|
| `engine/{config,evidence,state_engine}.py` | `cv/run_cv.py` (P1) | names or signatures of `EngineConfig`, `Detection.from_dict/to_dict`, `classify`, `SeatEngineState`, `step` |
| `IngestIn` + `ingest()` | P1 sender, `tests/test_reliability.py` (P4) | field names, limits, status values |
| `build_seat_view()`, `meta()`, WS messages | `apps/web/src/api.ts`, `live.tsx`, every page (P3/P4), e2e | field names/types, enum values, the `stale` tone, the hash-volatile list |
| `/api/recommendations`, `/api/route` | `StudentPage.tsx`, `StudyMatch.tsx` (P3) | response keys, `rank_score` semantics |
| `/api/admin/*`, `/api/demo/*` | `StaffConsole.tsx`, `ScenarioLab.tsx` (P4) | bodies, decision/override values |
| `/api/session` token format | `api.ts::getSessionToken` parses `token.split(".")[1]` | the `<sid>.<exp>.<sig>` format |
| `latest_run.json` passthrough | `CvLab.tsx` (P3) | the passthrough behaviour of `/api/cv/status` |

## Tests on `main` that guard your code

- `tests/test_api.py`: 27 tests, T01–T14 plus extras.
- `tests/test_state_engine.py`: 15 tests.
- `tests/test_reliability.py`: 7 tests, owned by P4 and approved by you.
- `tests/test_roi_geometry.py`: 4 tests (P1).
- **Total 53 passed.**

## Known limitations and defects

1. Malformed `observed_at_utc` → 500 (PA-02).
2. Whole-frame rollback on one bad seat. This is by design, but document it.
3. `cv_evidence_dir` is not configurable from the environment (PA-01).
4. No schema versioning or migration.
5. The rate limit is per session only.
6. A single staff token, with the actor always `staff-demo`.
7. Observation pruning has no test.
8. `group_size > 2` is not supported.
9. The OpenAPI document has no response schemas (PA-07).
10. `/api/seats/{id}` returns 404 for LAB seats; use `/api/cv/lab-seats`.
