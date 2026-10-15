# Task Guide — PERSON 1: Computer Vision / ROI / Real Seat Experiments
Branch: **`feature/v3-cv`** · Label: `person-1-cv` · Reviewer หลัก: P2 (ingest contract), P4 (merge/QA)

## 1. เป้าหมาย
พิสูจน์ CV จริงบน **ฉากที่นั่งจริงที่ได้รับอนุญาต** (2–4 ที่นั่ง) แทน `bus.jpg`: วิดีโอ/กล้อง → YOLO11n (หรือ CiRA CORE ถ้าวิชาบังคับ) → ROI ที่ calibrate กับภาพจริง → evidence event → `POST /api/ingest/observations` → state engine เดิม และวัดผลอย่างซื่อตรง (ถ้าไม่ได้รับอนุญาต: รายงาน `BLOCKED` พร้อมเหตุผล)

## 2. ไฟล์ที่เป็นเจ้าของ
`cv/run_cv.py`, `cv/roi.py`, `cv/roi_config.json`, `cv/requirements-cv.txt`, `cv/ROI_CALIBRATION_GUIDE_TH.md`, **ใหม่** `cv/experiments/**`, `tests/test_roi_geometry.py`, **ใหม่** `tests/test_cv_v3.py`

## 3. ไฟล์ที่ห้ามแก้
* `services/api/**` ทั้งหมด รวม `services/api/app/engine/*` (P2) — `cv/run_cv.py` **import ได้** (`EngineConfig`, `Detection`, `classify`, `SeatEngineState`, `step`) แต่ห้ามแก้
* `apps/web/**` (P3/P4) รวม `pages/CvLab.tsx` — ส่ง payload/ความต้องการให้ P3 แทน
* FROZEN: `evidence/*` (V2 รวม `evidence/cv/`), `presentation/*`, `verification/*`, `reference/*`, spec ใน `docs/*`
* ห้าม commit: วิดีโอ/เฟรม/ภาพบุคคล (`cv/experiments/**/raw/`, `**/frames/` ถูก ignore), `*.pt` weights, `.venv-cv/`

## 4. ฟังก์ชันที่ต้องทำ
1. **ย้ายผล CV ออกจากหลักฐาน V2:** ตอนนี้ `run_cv.py` เขียน `evidence/cv/latest_run.json` (FROZEN) — เปลี่ยนให้เขียน `artifacts/cv/` เป็นค่าเริ่มต้น (หรือ env `SL_ARTIFACT_DIR`) และผลที่คัดแล้วไป `evidence/team_v3/cv/`; ตกลงกับ P2 ให้ API (`settings.cv_evidence_dir`) อ่านตำแหน่งใหม่ผ่าน env เพื่อให้หน้า CV Lab ยังทำงาน
2. ถามอาจารย์ (ผ่าน P4): **CiRA CORE บังคับหรือไม่** — ถ้าบังคับ ทำ adapter ทดลองแยกไฟล์ อย่าลบ YOLO ที่ทำงานอยู่
3. จัดฉาก 2–4 เก้าอี้ + โต๊ะ, ผู้ร่วมทดลอง **ยินยอมเป็นลายลักษณ์อักษร**; คลิป `empty`, `seated`, `walk_by`, `standing_near`, `belongings`, `cup_only`, `dark/occluded`
4. ROI ใหม่จากภาพมุมกล้องจริง (seat polygon + table polygon) map กับ `LAB1`–`LAB4` (ห้ามเขียน A01–C08)
5. Ground truth รายช่วงเวลา (CSV) → confusion matrix, **False Available**, Unknown coverage, N เฟรม/วินาที
6. ส่ง event ผ่าน API เท่านั้น (`X-Device-Token`) ตาม `docs/api_contract_v3.md`; ห้ามเขียน DB ตรง; ห้ามปลอม `occupied`

## 5. สิ่งที่ต้องส่ง
* `cv/experiments/<YYYYMMDD>_<scene>/README.md`: แหล่งภาพ, consent (ไม่ระบุตัวตนใน Git), กล้อง, แสง, N, ข้อจำกัด
* `roi_config` ของฉากจริง, inference log (ไม่มีภาพบุคคล), ground-truth CSV, metrics JSON/MD
* ตัวอย่าง event JSON ที่ API ตอบ `applied` / `duplicate` / `late`
* `tests/test_cv_v3.py` + ผลรัน · PR สรุปพร้อม label `person-1-cv`

## 6. Acceptance tests
```powershell
.venv\Scripts\python -m pytest tests\test_roi_geometry.py tests\test_cv_v3.py -q      # ผ่านทั้งหมด
.venv\Scripts\python -m pytest -q                                                      # ทั้ง repo ไม่ถอยหลัง
.venv-cv\Scripts\python cv\run_cv.py suite --post                                     # (เซิร์ฟเวอร์เปิด) ingest สำเร็จ
.venv\Scripts\python scripts\check_ownership.py --owner P1 --base origin/main          # ไม่มี BLOCK
git status                                                                             # ไม่มีไฟล์ใน evidence/ (V2) ถูกแก้
```
* คลิป `walk_by` ต้อง **ไม่** ถูกยืนยันเป็น Occupied · `empty` ต้องเป็น Available เฉพาะหลังผ่าน smoothing · ภาพมืด/บัง → Unknown

## 7. เกณฑ์เสร็จ
คลิปจริงที่ได้รับอนุญาต ≥1 ไหลครบ YOLO/CiRA → adapter → API → สถานะ LAB ใน CV Lab; P2 ยืนยัน log; metrics มี N และข้อจำกัด **หรือ** Issue `[BLOCKED][P1]` ระบุสาเหตุ (ไม่มีอนุญาต/อุปกรณ์) — ห้ามใส่ตัวเลขความแม่นยำที่ไม่ได้วัด

## 8. ข้อกำหนดการรวมระบบ
* payload ตาม contract ของ P2 (P2 merge ก่อน) — ต้องการ field ใหม่ ให้เปิด Issue `integration` ถึง P2
* แจ้ง P3 รูปแบบข้อมูลที่หน้า CV Lab ต้องแสดง (source, model, dataset, consent)
* `cv/run_cv.py` ขึ้นกับ `engine/` ของ P2: ถ้า P2 เปลี่ยน signature ต้องแจ้งก่อน
* P4 จะรัน regression หลัง merge

## Claude Code prompt (คัดลอกไปใช้)
```text
We are working on an EXISTING Smart Library NEXT application (shared repo SmartLibrary-NEXT). Do not rebuild it.
I am PERSON 1 (Computer Vision). My branch is feature/v3-cv.

Before changing anything:
1. Run `git status` and `git branch --show-current`; switch to feature/v3-cv if needed; `git fetch origin` and merge origin/main.
2. Read docs/team_v3/TEAM_ONBOARDING_TH.md, docs/team_v3/tasks/P1_CV_TASK_GUIDE_TH.md, docs/team_v3/OWNERSHIP_MAP.csv,
   docs/team_v3/02_INTEGRATION_CONTRACT.md and (if present) docs/api_contract_v3.md.
3. Inspect the real code: cv/run_cv.py, cv/roi.py, cv/roi_config.json, services/api/app/engine/*.py (read-only for me),
   and the POST /api/ingest/observations handler in services/api/app/main.py (read-only). Confirm every path exists.
4. Run the baseline: `.venv\Scripts\python -m pytest -q` and report the exact result before editing.

Rules: modify ONLY files I own (cv/**, tests/test_roi_geometry.py, tests/test_cv_v3.py). If services/api or apps/web must change,
STOP and write a cross-owner request (what/endpoint/input-output/reason/test case) instead of editing.
Never write into evidence/ (frozen V2) - use artifacts/ or evidence/team_v3/cv/. Never commit videos, frames, images of people or
model weights. Never call simulated data real CV; only use footage with documented consent; never invent accuracy numbers.
Send observations only through the API with the device token; never write the database directly; never touch seats A01-C08.

Implement the tasks in my task guide, add tests, run them, and run `scripts\check_ownership.py --owner P1 --base origin/main`.
Deliver: code + tests, exact test output, a short Thai README in cv/experiments/<run>/, sample event JSON, limitations,
and a PR description using .github/pull_request_template.md. Do not merge to main.
```
