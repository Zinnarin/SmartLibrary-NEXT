# P1 · 06 — Acceptance criteria (Computer Vision)

**PASS** means you ran the command on your branch and attached its real output to the PR. A criterion that depends on a permission you do not have is reported as **BLOCKED** with the issue number. It is never reported as PASS.

## Mandatory (every P1 PR)

| ID | Criterion | Command / check | Pass condition |
|---|---|---|---|
| AC-P1-01 | No regression | `.venv\Scripts\python -m pytest -q` | 0 failed, 0 errors; at least 53 tests collected |
| AC-P1-02 | Ownership | `.venv\Scripts\python scripts\check_ownership.py --owner P1 --base origin/main` | no `BLOCK`; every `REVIEW` line approved by its owner in the PR |
| AC-P1-03 | Frozen V2 untouched | after running your CV commands: `git status --short -- evidence presentation verification` | prints nothing |
| AC-P1-04 | No private media or weights in git | `git diff --name-only origin/main...HEAD` | no image or video of people, no `*.pt`/`*.onnx`, nothing under `raw/` or `frames/` |
| AC-P1-05 | Sender conformance | `.venv\Scripts\python -m pytest tests\test_cv_v3.py -q` | payloads built by your code validate against `IngestIn`; a sample sent to a test app returns `applied`; the same sample again returns `duplicate`; runs **without** torch/ultralytics (CI uses plain `.venv`) |
| AC-P1-06 | Live ingest smoke | server running; your sender posts at least 1 frame | response `200` and every `results[].status` is `applied`, `duplicate` or `late`, never an unhandled error; `GET /api/cv/lab-seats` shows `source: "cv"` for the seats sent |

## Functional (the mission)

| ID | Criterion | Pass condition |
|---|---|---|
| AC-P1-10 | CV output no longer goes to frozen evidence (issue #3, with P2's PA-01) | running the suite or your new command leaves `evidence/` unchanged; the CV Lab page still shows the latest run |
| AC-P1-11 | File input mode (image and/or video) | documented in `--help` and the README; raw frames are not written to disk unless an explicit flag is given together with a consent statement |
| AC-P1-12 | Evidence record (PA-04) | one JSON line per frame; each `seats[].detections` item validates as `DetectionIn`; a replay tool or test proves the record converts to a valid C1 payload |
| AC-P1-13 | Decision-branch behaviour on labelled clips | `walk_by` never committed as `occupied`; `dark`/`occluded` frames → `unknown`; `empty` → `available` only after smoothing; `cup_only` not `reserved`; `belongings` → `reserved` and never auto-released |
| AC-P1-14 | Sitting vs standing | on the same labelled clips, a table comparing the V2 hip-anchor rule with your method: per-class counts, N frames, and where each fails |

## Measurement (only with authorized data; otherwise BLOCKED)

| ID | Criterion | Pass condition |
|---|---|---|
| AC-P1-20 | Ground truth | a CSV per clip with `start_s,end_s,seat_id,truth` labelled by a human; the labeller and method recorded in the experiment README |
| AC-P1-21 | Metrics with N | a confusion matrix over `available`/`occupied`/`reserved`/`unknown`; **False Available rate** = frames shown `available` while the truth is not available ÷ frames shown `available`; Unknown coverage; median inference ms/frame with the hardware; every number with its N and clip list |
| AC-P1-22 | Honest scope | the README states the camera, lighting, number of people, consent (no names), and what the result does **not** prove (e.g. it is not a real library and not the CCTV angle) |
| AC-P1-23 | If no permission | issue #14 updated with the reason; the final report says "no real-seat accuracy measured" |

## Optional (only if issue #15 says CiRA CORE is required)

| ID | Criterion | Pass condition |
|---|---|---|
| AC-P1-30 | CiRA CORE adapter | a separate adapter that produces the same C1 evidence; a comparison with YOLO11n on the same frames (N, per-class results, ms/frame); YOLO path still works |
