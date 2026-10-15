# TEST RESULTS — raw outputs (composed by scripts/compose_test_results.py)

Composed: 2026-10-14T22:55:16 (local time, Asia/Bangkok)

## 1. Backend tests (pytest)

Command:
```
.\.venv\Scripts\python.exe -m pytest -v -rA --junitxml=evidence/pytest_junit.xml
```

JUnit summary: tests=53 failures=0 errors=0 skipped=0 time=35.086s

| test | result | time (s) |
|---|---|---|
| tests.test_api::test_T01_normal_counts_match_and_simulation_banner | PASS | 0.219 |
| tests.test_api::test_initial_seats_unknown_before_evidence | PASS | 0.065 |
| tests.test_api::test_T02_quiet_power_hard_constraints | PASS | 0.146 |
| tests.test_api::test_window_preference_is_soft_and_must_is_hard | PASS | 0.439 |
| tests.test_api::test_T03_camera_lost_then_ttl_stale | PASS | 0.341 |
| tests.test_api::test_recovered_requires_fresh_evidence | PASS | 0.336 |
| tests.test_api::test_T04_low_confidence_unknown | PASS | 0.146 |
| tests.test_api::test_T05_belongings_scenario_possibly_reserved | PASS | 15.543 |
| tests.test_api::test_T07_maintenance_override_wins_and_is_audited | PASS | 1.491 |
| tests.test_api::test_override_expiry | PASS | 0.254 |
| tests.test_api::test_T08_seatcheck_report_does_not_set_occupied | PASS | 0.171 |
| tests.test_api::test_T09_resolve_with_reason_audits_and_pushes_websocket | PASS | 0.301 |
| tests.test_api::test_reject_report_keeps_sensor_state | PASS | 0.137 |
| tests.test_api::test_T10_admin_requires_staff_token | PASS | 0.202 |
| tests.test_api::test_T10_report_rate_limit_duplicate_and_replay | PASS | 0.200 |
| tests.test_api::test_demo_endpoints_hidden_in_production | PASS | 0.094 |
| tests.test_api::test_T11_groupfit_pairs_are_adjacent_and_eligible | PASS | 0.208 |
| tests.test_api::test_T11_groupfit_excludes_reported_seat | PASS | 0.201 |
| tests.test_api::test_T12_routes_only_use_declared_edges | PASS | 0.350 |
| tests.test_api::test_T13_duplicate_and_out_of_order_observations | PASS | 0.316 |
| tests.test_api::test_clock_skew_becomes_unknown | PASS | 0.121 |
| tests.test_api::test_source_contamination_guards | PASS | 0.126 |
| tests.test_api::test_T14_app_runs_without_cv_stack | PASS | 0.270 |
| tests.test_api::test_false_free_report_scenario | PASS | 0.206 |
| tests.test_api::test_exam_rush | PASS | 0.171 |
| tests.test_api::test_scenario_state_is_persisted_in_backend | PASS | 0.103 |
| tests.test_api::test_BUG012_index_html_is_not_cached | PASS | 0.158 |
| tests.test_reliability::test_recommendations_never_include_unsafe_states_across_scenarios | PASS | 11.573 |
| tests.test_reliability::test_scenario_switch_is_smoothed_and_changing_seat_is_withheld | PASS | 0.204 |
| tests.test_reliability::test_T07_override_wins_over_real_cv_ingest_path | PASS | 0.209 |
| tests.test_reliability::test_staff_unknown_override_pending_inspection | PASS | 0.151 |
| tests.test_reliability::test_camera_offline_is_immediate_and_stale_follows_ttl | PASS | 0.139 |
| tests.test_reliability::test_heartbeat_timeout_marks_silent_camera_offline_without_lwt | PASS | 0.124 |
| tests.test_reliability::test_seat_detail_and_layout_endpoints | PASS | 0.166 |
| tests.test_roi_geometry::test_point_in_polygon | PASS | 0.001 |
| tests.test_roi_geometry::test_overlap_fraction | PASS | 0.001 |
| tests.test_roi_geometry::test_person_anchor_is_hip_not_centre | PASS | 0.000 |
| tests.test_roi_geometry::test_walk_through_box_crossing_table_only | PASS | 0.000 |
| tests.test_state_engine::test_never_observed_is_unknown_not_available | PASS | 0.000 |
| tests.test_state_engine::test_one_empty_frame_is_not_available_T06 | PASS | 0.001 |
| tests.test_state_engine::test_available_requires_consecutive_clean_frames | PASS | 0.001 |
| tests.test_state_engine::test_available_streak_broken_by_bad_frame | PASS | 0.001 |
| tests.test_state_engine::test_passerby_is_not_occupied_T06 | PASS | 0.001 |
| tests.test_state_engine::test_seated_person_becomes_occupied_after_smoothing | PASS | 0.001 |
| tests.test_state_engine::test_cup_only_is_not_reserved_T06 | PASS | 0.001 |
| tests.test_state_engine::test_low_confidence_is_unknown_T04 | PASS | 0.001 |
| tests.test_state_engine::test_dark_frames_are_unknown | PASS | 0.000 |
| tests.test_state_engine::test_persistent_belongings_reserved_and_never_auto_released_T05 | PASS | 0.022 |
| tests.test_state_engine::test_owner_returns_reserved_to_occupied | PASS | 0.001 |
| tests.test_state_engine::test_out_of_order_observation_rejected_T13 | PASS | 0.001 |
| tests.test_state_engine::test_stale_view_is_never_green | PASS | 0.001 |
| tests.test_state_engine::test_future_timestamp_never_gives_negative_age | PASS | 0.001 |
| tests.test_state_engine::test_gap_longer_than_ttl_resets_to_unknown_BUG001 | PASS | 0.001 |

Last lines of `evidence/pytest_output.txt`:
```
PASSED tests/test_state_engine.py::test_owner_returns_reserved_to_occupied
PASSED tests/test_state_engine.py::test_out_of_order_observation_rejected_T13
PASSED tests/test_state_engine.py::test_stale_view_is_never_green
PASSED tests/test_state_engine.py::test_future_timestamp_never_gives_negative_age
PASSED tests/test_state_engine.py::test_gap_longer_than_ttl_resets_to_unknown_BUG001
======================= 53 passed, 1 warning in 35.11s ========================
```

History of real failures before fixes (see BUG_LOG.md): run 1 → 14 passed, 26 errors (WinError 5, BUG-002); run 2 → 37 passed, 3 failed (BUG-001 logic, BUG-003/004 test issues); run 3+ → all passed.

## 2. Browser end-to-end (Playwright + Microsoft Edge, headless)

Command (server running on 127.0.0.1:8000):
```
cd apps\web; npx playwright test
```

Stats: expected(passed)=8 unexpected(failed)=0 flaky=0 skipped=0 duration=161.5 s start=2026-10-14T15:40:18.538Z

| test | status | duration (s) |
|---|---|---|
| CV Lab page shows the recorded real-CV run (or NOT_RUN/BLOCKED) without resetting data | passed | 1.5 |
| professor demo path (SIMULATION) | passed | 63.8 |
| WebSocket blocked -> polling fallback keeps data visible and honest | passed | 0.6 |
| SeatWatch alerts in-app when a verified matching seat becomes available | passed | 12.4 |
| BUG-011 regression: server unreachable -> seats not shown as fresh, recommendations withdrawn; reconnect restores live data | passed | 25.6 |
| student journey in the requested order, with zero console/page errors | passed | 29.7 |
| map is keyboard-operable (Tab to a seat, Enter opens details) | passed | 0.4 |
| real server crash + restart: page goes not-current, then reconnects and re-confirms seats | passed | 26.2 |

Screenshots produced by these runs: `presentation/screenshots/*.png` (01–19).

## 3. Staff action → WebSocket latency (loopback, one machine)

```
.\.venv\Scripts\python.exe scripts\measure_ws_latency.py --trials 20
```

trials=20 median=43.5 ms p90=71.2 ms max=99.5 ms — REST staff override (POST/DELETE) -> WebSocket delta received by a client, loopback 127.0.0.1; NOT: not camera-event latency, not over Wi-Fi/LAN, not production hardware

## 4. CV pipeline run (real Ultralytics inference)

```
.venv-cv\Scripts\python cv\run_cv.py suite --post
```

status=WORKING_TESTED scope=เฉพาะ pipeline บนภาพตัวอย่างของ Ultralytics — ไม่ใช่ภาพห้องสมุด library_cv_status=BLOCKED
model=yolo11n weights=yolo11n.pt sha256=0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1 ultralytics=8.4.177 classes=80 literal 'bag' class=False belongings classes present=['backpack', 'book', 'handbag', 'laptop', 'suitcase']
device=cpu (torch CPU build; GPU not used) torch=2.14.1+cpu python=3.10.11
frames=8 median ms/frame=37.8 all=[2269.3, 42.0, 37.6, 36.3, 33.3, 38.0, 42.2, 37.7]
source=ultralytics/assets/bus.jpg (ภาพตัวอย่างที่มากับแพ็กเกจ ultralytics) sha256=c02019c4979c191eb739ddd944445ef408dad5679acab6fd520ef9d434bfbc63

| ROI | detections related to ROI (last frame) | raw | committed | codes |
|---|---|---|---|---|
| LAB1 | bus 0.94 (in_seat=False, seat_overlap=0.06, in_table=False), person 0.88 (in_seat=True, seat_overlap=0.41, in_table=False), person 0.86 (in_seat=False, seat_overlap=0.07, in_table=False), person 0.62 (in_seat=False, seat_overlap=0.09, in_table=False) | occupied | occupied | P_SEATED |
| LAB2 | bus 0.94 (in_seat=False, seat_overlap=0.03, in_table=False), person 0.86 (in_seat=False, seat_overlap=0.04, in_table=False) | unknown | unknown | P_NEAR_NOT_SEATED |
| LAB3 | ไม่มี | available | available | E_EMPTY_VISIBLE |
| LAB4 | bus 0.94 (in_seat=False, seat_overlap=0.00, in_table=False), person 0.89 (in_seat=False, seat_overlap=0.00, in_table=False) | unknown | unknown | P_NEAR_NOT_SEATED |

ingest: ส่ง 32 observation เข้า /api/ingest/observations (CV-LAB); API LAB seat states after run: {'LAB1': {'physical_state': 'occupied', 'source': 'cv'}, 'LAB2': {'physical_state': 'unknown', 'source': 'cv'}, 'LAB3': {'physical_state': 'available', 'source': 'cv'}, 'LAB4': {'physical_state': 'unknown', 'source': 'cv'}}
- same image darkened x0.12 (synthetic perturbation, quality-gate check): qualities=['dark', 'dark', 'dark'] final={'LAB1': 'unknown', 'LAB2': 'unknown', 'LAB3': 'unknown', 'LAB4': 'unknown'} errors=[]
- missing source file (camera-lost analogue): qualities=['no_frame', 'no_frame'] final={'LAB1': 'unknown', 'LAB2': 'unknown', 'LAB3': 'unknown', 'LAB4': 'unknown'} errors=['cv2.imread returned None for C:\\Users\\ebz14\\CPE447\\Project\\SmartLibraryNEXT\\SmartLibrary_NEXT_V2_Ready_Handoff\\SmartLibrary_NEXT_V2_Ready\\cv\\__missing_source__.jpg (file missing or unreadable)', 'cv2.imread returned None for C:\\Users\\ebz14\\CPE447\\Project\\SmartLibraryNEXT\\SmartLibrary_NEXT_V2_Ready_Handoff\\SmartLibrary_NEXT_V2_Ready\\cv\\__missing_source__.jpg (file missing or unreadable)']

`evidence/cv/run_log.txt`:
```
[2026-10-14T13:54:01.082Z] cv20261014205348 model=yolo11n device=cpu (torch CPU build; GPU not used) frames=8 median_ms=41.0 final={'LAB1': 'occupied', 'LAB2': 'unknown', 'LAB3': 'available', 'LAB4': 'unknown'} ingested=32 dark={'LAB1': 'unknown', 'LAB2': 'unknown', 'LAB3': 'unknown', 'LAB4': 'unknown'} missing={'LAB1': 'unknown', 'LAB2': 'unknown', 'LAB3': 'unknown', 'LAB4': 'unknown'} errors=0
[2026-10-14T13:54:57.035Z] cv20261014205445 model=yolo11n device=cpu (torch CPU build; GPU not used) frames=8 median_ms=42.6 final={'LAB1': 'occupied', 'LAB2': 'unknown', 'LAB3': 'available', 'LAB4': 'unknown'} ingested=32 dark={'LAB1': 'unknown', 'LAB2': 'unknown', 'LAB3': 'unknown', 'LAB4': 'unknown'} missing={'LAB1': 'unknown', 'LAB2': 'unknown', 'LAB3': 'unknown', 'LAB4': 'unknown'} errors=0
[2026-10-14T13:57:31.465Z] cv20261014205720 model=yolo11n device=cpu (torch CPU build; GPU not used) frames=8 median_ms=40.6 final={'LAB1': 'occupied', 'LAB2': 'unknown', 'LAB3': 'available', 'LAB4': 'unknown'} ingested=32 dark={'LAB1': 'unknown', 'LAB2': 'unknown', 'LAB3': 'unknown', 'LAB4': 'unknown'} missing={'LAB1': 'unknown', 'LAB2': 'unknown', 'LAB3': 'unknown', 'LAB4': 'unknown'} errors=0
[2026-10-14T15:40:15.759Z] cv20261014224004 model=yolo11n device=cpu (torch CPU build; GPU not used) frames=8 median_ms=37.8 final={'LAB1': 'occupied', 'LAB2': 'unknown', 'LAB3': 'available', 'LAB4': 'unknown'} ingested=32 dark={'LAB1': 'unknown', 'LAB2': 'unknown', 'LAB3': 'unknown', 'LAB4': 'unknown'} missing={'LAB1': 'unknown', 'LAB2': 'unknown', 'LAB3': 'unknown', 'LAB4': 'unknown'} errors=0
```

## 5. BUG-011 regression (browser freshness guard) — before vs after the fix

`evidence/bug011_before_fix_output.txt`:
```
  ok 2 e2e\reliability.spec.ts:54:1 › student journey in the requested order, with zero console/page errors (30.2s)
  ok 3 e2e\reliability.spec.ts:113:1 › map is keyboard-operable (Tab to a seat, Enter opens details) (406ms)
    Error: a seat must not stay green when no data can arrive
    Received string: [31m"[7mavailab[27mle"[39m
    test-results\reliability-BUG-011-regres-c63c0-econnect-restores-live-data\test-failed-1.png
  1 failed
  2 passed (57.4s)
```

`evidence/bug011_after_fix_output.txt`:
```
  ok 1 e2e\reliability.spec.ts:18:1 › BUG-011 regression: server unreachable -> seats not shown as fresh, recommendations withdrawn; reconnect restores live data (24.8s)
  ok 2 e2e\reliability.spec.ts:54:1 › student journey in the requested order, with zero console/page errors (28.4s)
  ok 3 e2e\reliability.spec.ts:113:1 › map is keyboard-operable (Tab to a seat, Enter opens details) (411ms)
  3 passed (54.7s)
```

## 6. Windows launch script (incl. BUG-013 regression cases)

Fresh start: `scripts\start_demo_windows.ps1 -Reset -NoBrowser -Port 8011` → API up after ~1.1 s with readiness=degraded / 0 fresh seats (warm-up), after 8 s readiness=ready, 24 fresh, counts 12/9/2/1 (`evidence/launch_script_test_log.txt`).

case 1 — second start on a busy port (`evidence/launch_test_busy_port.txt`):
```
ERROR: port 8000 is already in use (pid 41476). A demo server is probably already running.
```

case 2 — -Reset while another server runs (`evidence/launch_test_reset_locked.txt`):
```
ERROR: -Reset refused: a Smart Library server is still running (pid 45272, 41476).
```

case 3 — -Reset honours SL_DB_PATH (`evidence/launch_test_case3_custom_db.txt`):
```
[3/3] Starting server at http://127.0.0.1:8011  (mode=demo)
INFO:     Uvicorn running on http://127.0.0.1:8011 (Press CTRL+C to quit)
```

## 7. PPTX verification

```
powershell -ExecutionPolicy Bypass -File scripts\export_pptx_preview.ps1 -Deck presentation\progress_update_v2.pptx
```
PowerPoint (COM) opened the deck (8 slides, 960×540 pt = 16:9), fonts used: Leelawadee UI (all text; not embedded in PPTX), Calibri/Aptos (theme defaults); exported PDF (8 pages, Leelawadee UI embedded) + 8 PNGs to `presentation/preview/`; every slide inspected visually; one clipped caption (slide 6) found and fixed.
