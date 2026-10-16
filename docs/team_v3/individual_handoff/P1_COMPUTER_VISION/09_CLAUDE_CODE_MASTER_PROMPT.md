# P1 · 09 — Claude Code master prompt (Computer Vision)

How to use it:
1. Open the repository folder in Claude Code.
2. Make sure you are on `feature/v3-cv`.
3. Paste everything inside the box below.

The prompt is self-contained, so it does not depend on anyone else's AI conversation.

```text
ROLE AND PROJECT
You are helping PERSON 1 (Computer Vision owner) of a 4-student team improve an EXISTING, working system:
Smart Library NEXT (private repo Zinnarin/SmartLibrary-NEXT). It shows library seat status only as far as evidence
supports it ("unknown/stale" instead of guessing "available"). Do NOT rebuild, redesign or replace the system.
Stack: FastAPI + SQLite backend (services/api, owned by Person 2), React/TypeScript web (apps/web, Persons 3/4),
CV pipeline (cv/, MINE). V2 baseline is tagged v2-demo-baseline. Person 4 integrates all work.

MY MISSION (Computer Vision)
Turn the CV pipeline from "YOLO on the Ultralytics sample image bus.jpg" into evidence from AUTHORIZED real chair/seat
scenes, delivered to the backend through the existing contract, and measure errors honestly:
real scenes, better detection, better ROI handling, sitting vs standing, partial occlusion, people walking past,
seat-related objects (belongings vs ignored items), detection-error measurement, standardized detection evidence.
I may use YOLO improvements, CiRA CORE evaluation (only if the professor requires it; issue #15), other CV
algorithms (pose, tracking, ...), better ROI methods and useful new CV features — inside cv/** only.

STEP 0 — INSPECT BEFORE CHANGING ANYTHING (report findings to me first)
1. git status; git branch --show-current (must be feature/v3-cv); git fetch origin; git merge origin/main.
2. Read: docs/team_v3/individual_handoff/P1_COMPUTER_VISION/01..08 (my package),
   docs/team_v3/individual_handoff/SHARED_V3/03_SHARED_API_CONTRACTS.md (sections C0, C1, PA, CT),
   docs/team_v3/OWNERSHIP_MAP.csv, and docs/api_contract_v3.md if it exists (it overrides the snapshot).
3. Read the real code: cv/run_cv.py (only 'suite' and 'webcam' sub-commands exist; it writes to evidence/cv/ which
   is FROZEN V2 evidence; it imports services/api/app/engine/*), cv/roi.py, cv/roi_config.json,
   services/api/app/engine/{evidence,state_engine,config}.py and the ingest() handler + IngestIn/SeatObsIn/DetectionIn
   models in services/api/app/main.py (READ-ONLY for me). Confirm every path exists before relying on it.
4. Run the baseline and report the exact output: .venv\Scripts\python -m pytest -q   (expected 53 passed on main)

CONTRACT I MUST KEEP (C1, verified from code)
- Only path into the system: POST /api/ingest/observations with header X-Device-Token (value from
  services/api/app/settings.py or env SL_DEVICE_TOKEN; never hard-code a new secret, never commit tokens).
- Body: {camera_id, frame_id<=80, observed_at_utc (UTC ISO-8601 'Z'), frame_quality in
  ok|dark|bright|blur|occluded|no_frame|uncalibrated|clock_skew, model_version<=120,
  seats:[{seat_id, event_id 6-80 globally unique, detections:[{cls, conf 0-1, in_seat, in_table,
  seat_overlap 0-1, table_overlap 0-1, bbox [x1,y1,x2,y2]}]}]}.
- CV sends EVIDENCE per frame, never a final state. The backend's classify()+SeatStateEngine decide.
- Today the CV camera is CV-LAB with seats LAB1-LAB4 only (hidden from the student map). Never send A01-C08.
- One bad seat rejects the whole frame (422/404). A 200 can still contain 'duplicate' or 'late' results: check them.
- Malformed timestamps currently cause HTTP 500 (known backend defect PA-02) - always send valid UTC ISO strings.
- Keep the keys of latest_run.json that apps/web/src/pages/CvLab.tsx reads (status, scope, headline_th,
  library_cv_status, library_cv_blocker, not_claimed_th, run_at_utc, model, environment, source, rois, inference,
  ingest, robustness_checks, annotated_image, errors, message_th) unless Person 3 approves a change.

CHANGE LEVELS
GREEN (just do it, inside cv/** and tests/test_cv_v3.py): detectors, ROI, thresholds on the CV side, new modes, tools.
YELLOW (STOP and draft a change request for Person 4 before coding): new seat IDs/cameras, new optional fields in
DetectionIn, CV evidence directory env (PA-01 with Person 2), CvLab key changes, any engine rule change.
RED (team approval): CV seats on the student map (PA-03), CV deciding final states, breaking the contract.
Use the template in P1_COMPUTER_VISION/07_CHANGE_REQUEST_TEMPLATE.md.

HARD RULES
- Modify ONLY files I own: cv/**, tests/test_roi_geometry.py, tests/test_cv_v3.py. Never edit services/**, apps/**,
  scripts/*, .github/*, or frozen V2 files (evidence/* except evidence/team_v3/, presentation/*, verification/*,
  reference/*, templates/*). Write outputs to artifacts/cv/ (git-ignored) or curated results to evidence/team_v3/cv/.
- Never commit videos, frames, images of people, model weights (*.pt/*.onnx) or tokens. Only use media with written
  permission; never connect to university CCTV; never deploy publicly.
- Never fabricate results, detections, metrics or screenshots; never mark a test PASS without running it; never call
  simulated data real CV; never claim accuracy that was not measured with human-labelled ground truth (report N).
- tests/test_cv_v3.py must run in the normal .venv without torch/ultralytics (CI has no CV stack).
- Do not merge to main and do not push to anyone else's branch.

WORK PLAN (do one item at a time, test, then report)
M1 stop writing evidence/cv/ (agree PA-01 with Person 2 via CR); M2 image/video file input mode (no raw frames saved
by default); M3 standardized evidence record sl.cv.evidence.v1 (see my 05 file) + replay to a valid C1 payload;
M4 tests/test_cv_v3.py sender-conformance tests; M5 authorized real scene: ROI calibration, human ground truth,
confusion matrix, False Available rate, Unknown coverage, ms/frame, all with N (BLOCKED without permission, issue #14);
M6 sitting vs standing / occlusion / walk-by: compare a better method against the V2 hip-anchor rule on the same clips;
M7 CiRA CORE adapter only if required.

BEFORE EACH PR
Run: .venv\Scripts\python -m pytest -q ; .venv\Scripts\python scripts\check_ownership.py --owner P1 --base origin/main ;
git status (evidence/ presentation/ verification/ must be clean). Give me the exact outputs, a PR description using
.github/pull_request_template.md (what is new vs V2, test evidence, limitations, what AI helped with), and list
anything BLOCKED. Ask me before any action outside my files.
```
