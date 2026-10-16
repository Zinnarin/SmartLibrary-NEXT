# 02 — System architecture (as built in V2, with V3 module boundaries)

Every path in this file exists in the repository unless it is marked **(new, planned)**.

## 1. Runtime view

```
 Windows PC (local only, 127.0.0.1)
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │ Process A: uvicorn  services/api/app/main.py:create_app()   port 8000          │
 │   ├─ REST  /api/*            (FastAPI, Pydantic models in main.py)              │
 │   ├─ WS    /ws/seats         (realtime.py Hub: snapshot / delta / heartbeat)    │
 │   ├─ static web app          (apps/web/dist, built by Vite)                     │
 │   ├─ ticker every SL_TICK_S  (demo mode: scenario frames; expire overrides;     │
 │   │                           prune old scenario observations)                  │
 │   └─ SQLite file  services/api/data/smartlibrary_demo.db  (git-ignored, WAL)    │
 │                                                                                 │
 │ Process B (optional, separate .venv-cv): cv/run_cv.py                           │
 │   YOLO11n (ultralytics, torch CPU) + OpenCV quality gate + ROI (cv/roi.py)      │
 │   + imports engine/ from services/api for local preview                         │
 │   ──HTTP POST /api/ingest/observations (X-Device-Token)──▶ Process A            │
 │                                                                                 │
 │ Browser: React 18 + TypeScript + Tailwind 4 (apps/web/src)                      │
 │   live.tsx: WS + polling fallback + browser-side TTL guard (BUG-011)            │
 └───────────────────────────────────────────────────────────────────────────────┘
```

- Start with `scripts/start_demo_windows.ps1`, which has `-Reset`, port-busy and locked-DB guards (BUG-013).
- Run the tests with `scripts/run_tests_windows.ps1`.

## 2. Backend layers (`services/api/app/`, owner P2)

| Layer | File | Responsibility |
|---|---|---|
| HTTP / WS boundary | `main.py` | routes, request models, auth helpers (`require_staff`, `require_session`, device token), error handlers, `meta()`, ticker, SPA serving |
| Application services | `services.py` | `ingest_observation`, reports (`create_report`, `resolve_report`), overrides, scenario runs, `seat_views`, `device_views` |
| Pure engine (no FastAPI) | `engine/evidence.py` (`classify`), `engine/state_engine.py` (`step`), `engine/trust.py` (`build_seat_view`), `engine/config.py` (`EngineConfig`), `engine/timeutil.py` | decision rules; **also imported by `cv/run_cv.py` (C1b)** |
| Recommendation / routing | `matching.py` | StudyMatch, GroupFit, Wayfinder (Dijkstra) |
| Realtime | `realtime.py` | change detection by hash, broadcast |
| Persistence | `db.py` | explicit schema, `read()` / `write()` (single writer lock, `BEGIN IMMEDIATE`) |
| Demo data | `seed.py`, `scenarios.py` | illustrative floor, 7 SIMULATION scenarios |
| Settings | `settings.py` | DB path, mode, tokens, tick, web dist, CV evidence dir (env `SL_*`) |

**Database tables** (`db.py`):
- `zones`, `waypoints`, `waypoint_edges`, `devices`, `seats`, `seat_adjacency`.
- `seat_observations`: every ingested observation, including `late` ones; `event_id` UNIQUE.
- `seat_current`: one row per seat with the engine state JSON and a `revision`.
- `seat_reports`, `manual_overrides`, `system_events` (audit), `scenario_runs`, `settings`.

There is no migration tool. The schema uses `CREATE TABLE IF NOT EXISTS`, and the demo DB is re-seeded by `-Reset` or `POST /api/demo/reset`. Any schema change needs a migration note: see the P2 package.

## 3. Frontend structure (`apps/web/`)

| Area | Files | Owner |
|---|---|---|
| Shell, routing, banners | `src/App.tsx`, `src/main.tsx`, `src/styles.css` | P3 |
| API client + types | `src/api.ts` | P3 (types follow C2/C3/C4) |
| Live data | `src/live.tsx` | P3 + P4 approval (BUG-011 guard) |
| Labels / colours | `src/labels.ts` | P3 |
| Student page | `src/pages/StudentPage.tsx`, `src/components/FloorMap.tsx`, `SeatDetail.tsx` (contains the SeatCheck form today), `StudyMatch.tsx` | P3 |
| CV Lab page | `src/pages/CvLab.tsx` | P3 + P1 approval |
| Staff Console | `src/pages/StaffConsole.tsx` | P4 |
| Scenario Lab | `src/pages/ScenarioLab.tsx` | P4 + P2 approval |
| SeatCheck component | `src/components/SeatCheckPanel.tsx` **(new, planned)** | P4 + P3 approval |
| Browser tests | `e2e/demo.spec.ts`, `e2e/reliability.spec.ts`, `e2e/server_restart.spec.ts`, `playwright.config.ts` | P4 (`playwright.config.ts` + P3) |

## 4. CV module (`cv/`, owner P1)

| File | Role |
|---|---|
| `cv/run_cv.py` | CLI with two commands: `suite` (sample-image evidence run, `--post`) and `webcam` (needs `--consent`). It writes JSON to `evidence/cv/` (**frozen**: issue #3). |
| `cv/roi.py` | image-plane geometry: point-in-polygon, box/polygon overlap, hip anchor |
| `cv/roi_config.json` | 4 hand-drawn ROIs (`LAB1`–`LAB4`) on the sample image |
| `cv/ROI_CALIBRATION_GUIDE_TH.md` | how to calibrate a real staged scene (not done yet) |
| `cv/requirements-cv.txt` | optional `.venv-cv` dependencies; weights live in git-ignored `cv/models/` |

## 5. Module boundaries and integration seams

| Seam | Provider → consumer | Contract | Where an adapter may live if needed |
|---|---|---|---|
| CV evidence | P1 → P2 | C1 (`POST /api/ingest/observations`) + C1b (engine import) | `integration/adapters/` **(new, planned, P4)**: replays a P1 evidence file (PA-04) into C1 without editing either side |
| Seat data | P2 → P3 | C2 (REST + WS) | inside `apps/web/src/api.ts` (P3), the single client entry point |
| Staff operations | P2 ↔ P4 | C3 | `apps/web/src/pages/StaffConsole.tsx` (P4) |
| SeatCheck | P3 → P4 (→ P2) | C4 | `apps/web/src/components/SeatCheckPanel.tsx` **(new, planned)** |
| CV run record | P1 → P3 | C1c (`latest_run.json` keys) | `cv/` writes it, `CvLab.tsx` reads it |
| Cross-module checks | all | CT | `tests/test_contract_v3.py` and `integration/smoke/` **(new, planned, P4)** |

## 6. Repository rules that shape the architecture

- `docs/team_v3/OWNERSHIP_MAP.csv` assigns every tracked file to P1–P4 or FROZEN. The first matching pattern wins.
- `scripts/check_ownership.py --audit` / `--owner P# --base origin/main` enforces it, and CI runs it.
- CI (`.github/workflows/ci.yml`): Python 3.10 `pytest`, ownership audit, `npm ci && npm run build`. **Playwright is not in CI** because it uses the locally installed Edge; P4 runs it locally.
- Git-ignored, never commit: `.venv*/`, `node_modules/`, `*.db`, `*.pt`, `cv/models/`, `cv/experiments/**/raw/` and `frames/`, `artifacts/` (after PR #16).
