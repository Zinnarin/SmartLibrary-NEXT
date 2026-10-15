# Task Guide — PERSON 2: Backend / Database / Seat State Engine / API Contract
Branch: **`feature/v3-backend`** · Label: `person-2-backend` · Reviewer หลัก: P1/P3/P4 (contract), P4 (merge/QA)

## 1. เป้าหมาย
เป็นเจ้าของ **API contract เดียวของทั้งทีม**: freeze สัญญาจากโค้ดจริง, เสริมความแข็งแรงของ backend/ingest และรองรับข้อมูล CV จริงจาก P1 โดยไม่ปนกับข้อมูลจำลอง — ทั้งหมดต้องไม่ทำให้ระบบ V2 ถอยหลัง

## 2. ไฟล์ที่เป็นเจ้าของ
`services/api/app/main.py`, `db.py`, `services.py`, `realtime.py`, `matching.py`, `settings.py`, `seed.py`, `scenarios.py`, `services/api/app/engine/{state_engine,trust,evidence,config,timeutil}.py`, `services/api/requirements.txt` (+P4 approve), `tests/conftest.py` (+ทุกคน review), `tests/test_api.py`, `tests/test_state_engine.py`, **ใหม่** `tests/test_backend_v3.py`, **ใหม่** `docs/api_contract_v3.md` (+P1/P3/P4 review)

## 3. ไฟล์ที่ห้ามแก้
`apps/web/**` (P3/P4), `cv/**` (P1), `scripts/*`, `.github/*`, `pytest.ini` (P4 — ขอผ่าน PR review), FROZEN: `evidence/*`, `presentation/*`, `verification/*`, `reference/*`, spec ใน `docs/*`

## 4. ฟังก์ชันที่ต้องทำ
1. **`docs/api_contract_v3.md` (งานแรก, Day 0–1):** สกัดจาก `docs/team_v3/api_baseline_v2_openapi.json` (26 routes ของจริง) + รูปทรง response ใน `engine/trust.py::build_seat_view()` และ `main.py::meta()` + WebSocket (`snapshot`/`delta`/`heartbeat`/`pong`, client ส่ง `"ping"`) + auth headers (`X-Session-Token`, `X-Staff-Token`, `X-Device-Token`) + error codes ตัวอย่าง
2. **Contract tests ingest** (`tests/test_backend_v3.py`): valid / duplicate event_id / out-of-order / clock skew / uncertain quality / bad token / wrong source / seat ที่ไม่ใช่ของกล้องนั้น
3. **ตำแหน่งผล CV:** เพิ่ม env (เช่น `SL_CV_EVIDENCE_DIR`) ให้ API อ่านผล CV ของ V3 จาก `evidence/team_v3/cv/` หรือ `artifacts/cv/` ตามที่ตกลงกับ P1 (V2 `evidence/cv/` คงไว้ไม่แก้)
4. (ถ้าทำ) ใส่ `response_model` แบบไม่เปลี่ยน JSON เดิม เพื่อให้ OpenAPI มี response schema
5. ถ้าต้องการสถานะ “Pending Inspection” แยก: ทำเป็น **contract proposal** ก่อน (ตอนนี้ใช้ override `unknown` ได้อยู่แล้ว) — เปลี่ยนแบบ additive เท่านั้น
6. ห้ามเปลี่ยน signature ใน `engine/` ที่ `cv/run_cv.py` ใช้ (`EngineConfig`, `Detection.from_dict`, `classify`, `SeatEngineState`, `step`) โดยไม่แจ้ง P1

## 5. สิ่งที่ต้องส่ง
`docs/api_contract_v3.md` (เปิด PR แยกเป็น **PR แรกของทีม**), `tests/test_backend_v3.py`, ตัวอย่าง request/response จริง, migration notes (ถ้ามี), regression log

## 6. Acceptance tests
```powershell
.venv\Scripts\python -m pytest -q                         # ทุก test เดิม (≥53) + test ใหม่ผ่าน
cd apps\web; npm run build; cd ..\..                      # frontend ยัง build ได้กับ API
powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1   # Playwright 8/8 (เซิร์ฟเวอร์เปิด)
.venv\Scripts\python scripts\check_ownership.py --owner P2 --base origin/main
```
* ตัวอย่างใน `api_contract_v3.md` ต้องตรงกับ response จริง (มี test ยืนยันอย่างน้อย seat, recommendation, ingest)
* BUG-001 (gap reset), T13 (idempotent/out-of-order), T07 (override ชนะ) ต้องยังผ่าน

## 7. เกณฑ์เสร็จ
event ของ P1 ถูก accept/reject ตาม contract พร้อม test; P3/P4 ใช้ API ได้โดยไม่ hard-code; stale/unknown/idempotency ถูกต้อง; ไม่มี regression

## 8. ข้อกำหนดการรวมระบบ
* **Contract PR merge ก่อน consumer เสมอ** · ทุกการเปลี่ยน schema → อัปเดต `api_contract_v3.md` + แจ้ง P3 (types ใน `apps/web/src/api.ts`) และ P1
* เปลี่ยน `conftest.py` หรือ `requirements.txt` ต้องให้ทุกคน/P4 review
* `scenarios.py`/`seed.py`/demo reset: P4 เสนอ test case, P2 เป็นคนแก้

## Claude Code prompt (คัดลอกไปใช้)
```text
We are working on an EXISTING Smart Library NEXT application (shared repo SmartLibrary-NEXT). Do not rebuild or replace it.
I am PERSON 2 (Backend / Database / Seat State Engine / API contract owner). My branch is feature/v3-backend.

Before changing anything:
1. Run `git status`, `git branch --show-current`; switch to feature/v3-backend; `git fetch origin` and merge origin/main.
2. Read docs/team_v3/TEAM_ONBOARDING_TH.md, docs/team_v3/tasks/P2_BACKEND_TASK_GUIDE_TH.md, docs/team_v3/OWNERSHIP_MAP.csv,
   docs/team_v3/02_INTEGRATION_CONTRACT.md and docs/team_v3/api_baseline_v2_openapi.json.
3. Inspect the real code: services/api/app/main.py (routes + Pydantic models), services.py, realtime.py, matching.py,
   settings.py, engine/*.py (note: state_engine/trust/evidence/config/timeutil live in services/api/app/engine/), and tests/.
   Confirm every path exists. Note that cv/run_cv.py imports engine/*: keep those signatures stable.
4. Run the baseline `.venv\Scripts\python -m pytest -q` and report the exact result before editing.

Rules: modify ONLY files I own (services/api/**, tests/conftest.py, tests/test_api.py, tests/test_state_engine.py,
tests/test_backend_v3.py, docs/api_contract_v3.md). Do not edit apps/web/**, cv/**, scripts/*, .github/* or frozen V2 files
(evidence/*, presentation/*, verification/*). API changes must be additive and documented in docs/api_contract_v3.md first.
Do not weaken safety rules (stale/unknown/offline/pending report must never be recommended; one report must not set Occupied).
Never claim simulated data is real CV.

First deliverable: docs/api_contract_v3.md extracted from the real code (routes, request/response JSON, WS messages, auth,
error codes) plus tests proving the examples match. Then the ingest contract tests in tests/test_backend_v3.py.
Run all tests and `scripts\check_ownership.py --owner P2 --base origin/main`. Report exact pass/fail.
Deliver a PR description using .github/pull_request_template.md. Do not merge to main.
```
