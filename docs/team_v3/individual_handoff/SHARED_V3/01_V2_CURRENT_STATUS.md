# 01 — Current V2 status (what is real, what is not)

Checked on 2026-10-16 against `main` (commit `edc7903`). The verification evidence is:
- `pytest` 53 passed (local run and GitHub CI run 38747341282, 15 Oct 2026).
- Playwright 8/8 passed (local, 14–15 Oct 2026; `evidence/FINAL_DEMO_READINESS.md`).
- A contract probe of every API route on 16 Oct 2026 (`contract_examples/`).

Nothing in this file is a promise of future work.

| Label | Meaning |
|---|---|
| **IMPLEMENTED** | Code exists, runs, and has automated tests that pass. |
| **SIMULATED** | Works, but the data is authored by developers (Scenario Lab / demo seed). It is not from a camera or the real library. |
| **PARTIAL** | Part of the feature exists. The missing part is stated. |
| **DESIGN ONLY** | Only described in documents or slides. No code. |
| **BLOCKED** | Cannot be done without an external permission or decision. |

## Status matrix

| Capability | Status | Where (verified paths) | Evidence / note |
|---|---|---|---|
| FastAPI REST API (26 routes) + SQLite (WAL, `BEGIN IMMEDIATE` transactions) | **IMPLEMENTED** | `services/api/app/main.py`, `db.py`, `services.py` | pytest; `docs/team_v3/api_baseline_v2_openapi.json` |
| Seat State Engine: 4 physical states + overrides, temporal smoothing, Available needs more frames, gap reset (BUG-001), out-of-order/duplicate rejection | **IMPLEMENTED** | `services/api/app/engine/state_engine.py`, `evidence.py` | `tests/test_state_engine.py` (15 tests) |
| Trust layer: freshness TTL, camera health, pending report, override, `is_recommendable` | **IMPLEMENTED** | `services/api/app/engine/trust.py` | T03, `test_camera_offline_is_immediate_and_stale_follows_ttl` |
| CV evidence ingest endpoint with device token, idempotency, source-contamination guards | **IMPLEMENTED** | `POST /api/ingest/observations` | T13, `test_source_contamination_guards`, probe |
| CV pipeline: YOLO11n (COCO pretrained) + OpenCV quality gate + hand-drawn ROI + same engine + ingest | **IMPLEMENTED on a sample image only** | `cv/run_cv.py suite`, `cv/roi.py`, `cv/roi_config.json` | `evidence/cv/run_log.txt`. The image is `bus.jpg`, shipped with the Ultralytics package: **not a library, no seats**. |
| CV results on the student map | **PARTIAL** | — | CV data reaches only `LAB1`–`LAB4`, which are hidden from the map (`is_active=0`). Students see them only on the CV Lab page (`/api/cv/lab-seats`). The map shows SIMULATION only. Closing this gap is PA-03 (RED). |
| `run_cv.py` input modes | **PARTIAL** | `cv/run_cv.py` | Only `suite` and `webcam` exist in `argparse`. The `image --source …` usage in the file's docstring is **not implemented**, and there is no video-file mode. |
| Webcam runner with a consent flag | **PARTIAL** (implemented, never run) | `cv/run_cv.py webcam --consent` | No permission to use a camera yet |
| CV evidence location | **PARTIAL** | `settings.cv_evidence_dir` = `evidence/cv` (frozen), not env-configurable | issue #3, PA-01 |
| Student website: floor map, seat detail, source/freshness labels, mobile layout, keyboard map | **IMPLEMENTED** | `apps/web/src/pages/StudentPage.tsx`, `components/FloorMap.tsx`, `SeatDetail.tsx` | e2e journey + keyboard + mobile 390 px |
| StudyMatch (hard constraints, reasons, no-result + relax suggestions, no fake %) | **IMPLEMENTED** (logic) / data **SIMULATED** | `services/api/app/matching.py`, `components/StudyMatch.tsx` | T02, property test over all scenarios |
| GroupFit (2 adjacent seats) | **IMPLEMENTED** for 2 people; **PARTIAL** for more (`group_size>2` → 422) | `matching.py` | T11; adjacency is hand-authored demo data |
| Wayfinder (Dijkstra on a declared graph) | **IMPLEMENTED** (logic) / map **SIMULATED** | `matching.py::Graph` | T12; map units, not metres; not checked for wheelchair access |
| WebSocket snapshot/delta/heartbeat + polling fallback + reconnect + browser stale guard (BUG-011) | **IMPLEMENTED** | `services/api/app/realtime.py`, `apps/web/src/live.tsx` | T09, 3 e2e incl. a real server kill |
| SeatCheck (anonymous session, rate limit, replay-safe, never sets Occupied) | **IMPLEMENTED** | `POST /api/seat-reports`, `SeatDetail.tsx` | T08, T10 |
| SeatCheck rate limit across new sessions | **PARTIAL** | per session only | known limitation |
| Staff Console: review reports with a reason, override (unavailable / maintenance / unknown, with expiry), audit log, devices | **IMPLEMENTED** | `apps/web/src/pages/StaffConsole.tsx`, `/api/admin/*` | T07, T09, T10, expiry |
| Override meaning for "someone is sitting" | **PARTIAL** | console default is `maintenance` | team agreement C says `unknown`; issue #11 |
| Staff identity | **PARTIAL** | single demo token; every action audited as `staff-demo` | not real authentication |
| Scenario Lab: 7 scenarios, server-driven, SIMULATION banner, simulated False-Available stats | **SIMULATED** (by design) | `services/api/app/scenarios.py`, `pages/ScenarioLab.tsx` | many tests; the statistics are on developer-authored ground truth |
| All seat states shown on the student map (`A01`–`C08`) | **SIMULATED** | `source = "scenario"` | banner `SIMULATION — NOT REAL CAMERA DATA` |
| Floor plan, power/quiet/window flags, adjacency | **SIMULATED** (illustrative) | `services/api/app/seed.py` (`metadata_source = "demo_assumed"`) | not a real plan |
| Belongings > 30 min staff flag in a real UI session | **PARTIAL** | `belongings_review_flag` | tested with a fake clock only |
| Old observation pruning (> 2 h, scenario only) | **PARTIAL** (no test) | `main.py::prune_observations` | — |
| Test-output isolation from frozen V2 evidence | **PARTIAL** | fixed on `feature/v3-staff-qa` (PR #16, CI green, **not merged**) | on `main`, Playwright still overwrites `presentation/screenshots/` and `evidence/` |
| Automated tests | **IMPLEMENTED** | `tests/` (53), `apps/web/e2e/` (8), CI `.github/workflows/ci.yml` (pytest, ownership audit, web build; no Playwright in CI) | CI green 15 Oct 2026 |
| Edge devices (Pi/Jetson), RTSP/PoE, MQTT/TLS/LWT, store-and-forward, PostgreSQL/cloud, room displays, LEDs, analytics, prediction | **DESIGN ONLY** | slides / blueprint | — |
| User study; ROI calibration on a real camera view | **DESIGN ONLY** | `cv/ROI_CALIBRATION_GUIDE_TH.md` | — |
| CV accuracy on real library seats (confusion matrix, False Available, mAP) | **BLOCKED** | — | no authorized footage or camera (issue #14). `/api/stats` → `real_cv.accuracy` is always `null`. |
| Real floor plan and verified seat attributes | **BLOCKED** | — | needs data from the library (issue #14) |
| Whether CiRA CORE is mandatory | **BLOCKED** (question to the professor) | — | issue #15; keep YOLO11n until answered |

## Known defects and risks found while extracting the contracts (16 Oct 2026)

1. `POST /api/ingest/observations` with an unparsable `observed_at_utc` raises an unhandled `ValueError` (HTTP 500), where it should be 422. This is PA-02. It was found by the probe, and no test covers it yet.
2. One bad seat in an ingest frame (wrong camera or unknown seat) rolls back the **whole** frame. This is by design (atomic), but a single wrong ROI ID silently drops all its seats unless the sender checks the response.
3. `FloorMap.tsx` draws zones A/B/C as hard-coded SVG and `labels.ts` hard-codes `ZONE_TH`. A new zone from the backend would not be drawn (PA-08).
4. `apps/web/src/api.ts` reads the session expiry from the token text (`token.split(".")[1]`). The token format is therefore a contract (C4).
5. `cv/run_cv.py` hard-codes the API URL `http://127.0.0.1:8000` and its own copy of the device token default (`DEVICE_TOKEN = …`). If `SL_DEVICE_TOKEN` changes on the server, CV posts fail with 401.
