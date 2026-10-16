# P1 · 03 — Existing code and ownership (Computer Vision)

Paths were verified with `git ls-files` on 2026-10-16. Ownership comes from `docs/team_v3/OWNERSHIP_MAP.csv`, where the first matching rule wins. Check it yourself with `python scripts/check_ownership.py --owner P1 --base origin/main`.

## Files you own

| Path | Owner | Approval from | Status |
|---|---|---|---|
| `cv/run_cv.py` | P1 | — | exists |
| `cv/roi.py` | P1 | — | exists |
| `cv/roi_config.json` | P1 | — | exists |
| `cv/requirements-cv.txt` | P1 | — | exists |
| `cv/ROI_CALIBRATION_GUIDE_TH.md` | P1 | — | exists |
| `cv/experiments/README.md` | P1 | — | new, planned (a folder per run: `cv/experiments/<YYYYMMDD>_<scene>/`) |
| `tests/test_roi_geometry.py` | P1 | — | exists (4 tests) |
| `tests/test_cv_v3.py` | P1 | — | new, planned (issue #5) |

Git-ignored, so **never commit** these: `cv/models/` (weights such as `yolo11n.pt`), `cv/experiments/**/raw/`, `cv/experiments/**/frames/`, `.venv-cv/`, and `*.pt`, `*.onnx`, `*.mp4`, `*.avi`, `*.mov`, `*.mkv` everywhere.

## What the code does today (`cv/run_cv.py`, 390 lines)

| Lines | Symbol | Behaviour |
|---|---|---|
| 30–43 | constants | `EVIDENCE = ROOT/"evidence"/"cv"` (**frozen V2 location**, issue #3), `API = "http://127.0.0.1:8000"`, `DEVICE_TOKEN` is a copy of the server's demo default. If the server sets `SL_DEVICE_TOKEN`, posts fail with 401. |
| 34–37 | imports | `EngineConfig`, `Detection`, `classify`, `SeatEngineState`, `step` from `services/api/app/engine/` (P2's code, read-only for you: contract C1b), and `relate_detection` from `cv/roi.py` |
| 59 | `frame_quality()` | `dark` if mean < 40, `bright` if > 225, `blur` if Laplacian variance < 50, else `ok` |
| 76 | `load_model()` | loads Ultralytics YOLO; records weights SHA-256, versions, device (CPU) |
| 105 | `infer()` | `model.predict(conf=0.25, imgsz=640)` → `[{cls, conf, bbox}]` |
| 116 | `per_seat()` | relates every detection to every ROI with `relate_detection()` |
| 128 | `post()` | builds the C1 body (`event_id = f"{frame_id}-{seat_id}"`) and POSTs with `X-Device-Token` |
| 144 | `annotate()` | draws ROIs and boxes and **blurs the head region** in saved images |
| 177 | `run_frames()` | per frame: quality → inference → per seat `classify` + `step` (local preview of the backend decision) → optional post |
| 237 | `cmd_suite()` | sample image `bus.jpg` × N frames, plus a darkened copy (quality gate) and a missing file (camera-lost analogue); writes `latest_run.json`, `run_<id>.json`, `run_log.txt` into `evidence/cv/` |
| 339 | `cmd_webcam()` | refuses without `--consent` (≥ 10 chars); frames are not saved unless `--save-annotated` |
| 368 | `main()` | **only two sub-commands: `suite`, `webcam`.** The docstring's `image --source …` example is not implemented. |

**`cv/roi.py`** (pure geometry, no OpenCV):
- `point_in_polygon` (line 23).
- `clip_polygon_to_box` (53).
- `box_overlap_fraction` (73): fraction of the box inside the polygon.
- `anchor_point` (85): person → the point 65 % down the box (estimated hip); object → box centre.
- `relate_detection` (93): returns `{cls, conf, in_seat, in_table, seat_overlap, table_overlap, bbox}`, which is exactly the C1 `DetectionIn` shape.

**`cv/roi_config.json`:** 4 hand-drawn ROIs (`LAB1`–`LAB4`) on the 810×1080 sample image. Each has a `seat_polygon`, a `table_polygon` and a `note` describing the branch of the decision logic it exercises. **These are not real seats.**

## Code you depend on but must not edit (read-only)

| Path | Owner | Why it matters to you |
|---|---|---|
| `services/api/app/engine/evidence.py` | P2 | `classify()` decision order and class lists, the same on server and CV |
| `services/api/app/engine/state_engine.py` | P2 | smoothing: 3/3/4/2 frames + 5 s span; gap > 30 s resets to `unknown` |
| `services/api/app/engine/config.py` | P2 | thresholds (`SL_*` env) |
| `services/api/app/main.py` | P2 | `ingest()` handler + `IngestIn`/`SeatObsIn`/`DetectionIn` models (C1) |
| `services/api/app/seed.py` | P2 | registers `CV-LAB` (`source_mode="cv"`) and `LAB1`–`LAB4` (`is_active=0`) |
| `services/api/app/settings.py` | P2 | `cv_evidence_dir` (not env-configurable yet, PA-01) and `device_token` |
| `apps/web/src/pages/CvLab.tsx` | P3 | reads your `latest_run.json` keys (C1c) |

**Frozen, never write:** `evidence/cv/*` and all of `evidence/*` (except `evidence/team_v3/`), `presentation/*`, `verification/*`, `reference/*`, `templates/*`.

## Tests that cover your module today (pass on `main`)

- `tests/test_roi_geometry.py`: `test_point_in_polygon`, `test_overlap_fraction`, `test_person_anchor_is_hip_not_centre`, `test_walk_through_box_crossing_table_only`.
- `tests/test_state_engine.py` (P2's file, but it tests the rules your evidence feeds): passer-by not occupied, cup only not reserved, low confidence → unknown, dark → unknown, belongings never auto-released, out-of-order rejected, gap reset.
- `tests/test_api.py::test_T13_duplicate_and_out_of_order_observations`, `::test_clock_skew_becomes_unknown`, `::test_source_contamination_guards`, `::test_T14_app_runs_without_cv_stack` (the API must run without torch).

## Known limitations you inherit

1. A standing person whose hip point falls inside a badly placed seat polygon counts as seated (`LAB1`, a deliberate test).
2. The confidence gate is the same for every class. Small objects such as books often fall below 0.5 and become `B_LOW_CONF` → `unknown`.
3. There is no tracking, so each frame is independent; temporal smoothing happens only in the backend.
4. `frame_quality` thresholds (40 / 225 / 50) are not calibrated for a real camera.
5. COCO has no literal "bag" class; bags are `backpack`, `handbag` or `suitcase`.
6. Inference was measured on CPU only (median 37.8–42.6 ms/frame on the sample image).
