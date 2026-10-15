# Smart Library NEXT V2 — Find. Verify. Study. (local prototype)

ต้นแบบที่รันได้จริงในเครื่อง สำหรับนำเสนอความคืบหน้า 15 ต.ค. 2569
**ข้อมูลที่นั่งบนหน้าจอทั้งหมดเป็น SIMULATION (Scenario Lab) เว้นแต่จะระบุว่า source = `cv`** — ไม่มีการเชื่อมกล้อง CCTV ของมหาวิทยาลัย และเซิร์ฟเวอร์ผูกกับ `127.0.0.1` เท่านั้น

สถานะจริงของแต่ละฟีเจอร์ดูที่ [evidence/IMPLEMENTATION_REPORT.md](evidence/IMPLEMENTATION_REPORT.md) และผลตรวจความพร้อมเดโมล่าสุดที่ [evidence/FINAL_DEMO_READINESS.md](evidence/FINAL_DEMO_READINESS.md) (**READY_WITH_LIMITATIONS**)

**วันนำเสนอ:** ทำตาม [docs/DEMO_RUNBOOK_TH.md](docs/DEMO_RUNBOOK_TH.md) · สไลด์ล่าสุด `presentation/progress_update_v2.pptx` (สำรอง PDF: `presentation/preview/progress_update.pdf`)

## Quick start (Windows)

ต้องมี Python 3.10+ และ Node.js 18+ (ทดสอบกับ Python 3.10.11, Node 24.11.0) ไม่ต้องใช้ Docker / cloud key / อินเทอร์เน็ตหลังติดตั้งแพ็กเกจ

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_demo_windows.ps1
```

สคริปต์จะสร้าง `.venv` + ติดตั้ง `services/api/requirements.txt` (ครั้งแรก), build frontend (ครั้งแรก), แล้วเปิด http://127.0.0.1:8000
ใช้ `-Reset` เพื่อเริ่มฐานข้อมูลสาธิตใหม่, `-NoBrowser` ไม่เปิดเบราว์เซอร์, `-Port 8010` เปลี่ยนพอร์ต

| หน้า | URL | หมายเหตุ |
|---|---|---|
| นักศึกษา (Floor Map + StudyMatch + GroupFit + Wayfinder + SeatCheck) | http://127.0.0.1:8000/ | ไม่ต้องล็อกอิน |
| Librarian Console | http://127.0.0.1:8000/#/staff | demo PIN `staff-demo-2569` (เปลี่ยนด้วย env `SL_STAFF_TOKEN`) — *demo gate ไม่ใช่ระบบยืนยันตัวตนจริง* |
| Scenario Lab | http://127.0.0.1:8000/#/lab | ใช้ PIN เดียวกัน, มีเฉพาะ `SL_MODE=demo` |
| CV Lab | http://127.0.0.1:8000/#/cv | แสดงผล YOLO run จริงล่าสุด (ถ้ามี) |

### Two-terminal dev mode (optional)
```powershell
.venv\Scripts\python -m uvicorn app.main:get_app --factory --app-dir services/api --host 127.0.0.1 --port 8000
cd apps\web; npm run dev     # http://127.0.0.1:5173 (proxy /api, /ws -> :8000)
```

## Tests
```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1
```
* `pytest` — state engine + API + WebSocket + security tests (`tests/`), output saved to `evidence/pytest_output.txt`
* Playwright browser smoke path (`apps/web/e2e/demo.spec.ts`, ใช้ Microsoft Edge ที่ติดตั้งในเครื่อง) — รันเมื่อเซิร์ฟเวอร์เปิดอยู่ที่ :8000 และบันทึก screenshot จริงลง `presentation/screenshots/`

## Optional real CV (P1)
แยก venv เพื่อไม่ให้เดโมขึ้นกับ torch:
```powershell
py -3.10 -m venv .venv-cv
.venv-cv\Scripts\python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
.venv-cv\Scripts\python -m pip install ultralytics requests
.venv-cv\Scripts\python cv\run_cv.py suite --post        # ภาพตัวอย่างของ ultralytics + ROI 4 จุด -> API (source=cv)
```
Webcam ใช้ได้เฉพาะฉากที่จัดขึ้นและมีความยินยอม: `cv\run_cv.py webcam --roi <roi.json> --consent "<ใคร/อะไร>"` (ไม่บันทึกภาพเป็นค่าเริ่มต้น) ดู [cv/ROI_CALIBRATION_GUIDE_TH.md](cv/ROI_CALIBRATION_GUIDE_TH.md)

## Repository layout
```
services/api/app/engine/   pure-Python SeatEvidenceAdapter, SeatStateEngine, trust layer (shared by scenario + real CV)
services/api/app/          FastAPI app, SQLite schema/seed, scenarios, StudyMatch/GroupFit/Wayfinder, WebSocket hub
apps/web/                  React + TypeScript + Vite + Tailwind (student, staff, scenario lab, CV lab) + Playwright e2e
cv/                        YOLO + OpenCV + ROI runner (separate venv), ROI config, calibration guide
tests/                     pytest suite mapped to acceptance tests T01–T14
scripts/                   start_demo_windows.ps1, run_tests_windows.ps1, build_pptx.py
presentation/              progress_update_v2.pptx (latest), progress_update.pptx (first version), three_minute_script_th.md, screenshots/, preview/ (PowerPoint export)
evidence/                  FINAL_DEMO_READINESS.md, IMPLEMENTATION_REPORT.md, TEST_RESULTS.md, BUG_LOG.md, raw outputs, cv/ run logs
docs/                      DEMO_RUNBOOK_TH.md (+ original spec documents)
verification/              ACCEPTANCE_TEST_MATRIX.csv (original) + ACCEPTANCE_TEST_RESULTS.csv (results of this build)
```

## Key semantics (short)
* 5 สถานะเดิมจากข้อเสนอ: Available / Occupied / Reserved (UI: **พบสิ่งของ / อาจถูกจับจอง** — ไม่ใช่การจอง) / Unavailable / Maintenance + `Unknown` เมื่อหลักฐานไม่พอ
* ความสด (STALE), สุขภาพกล้อง, รายงาน SeatCheck ค้าง, override ของเจ้าหน้าที่ แยกเป็นคนละมิติ — ที่นั่งจะถูกแนะนำเฉพาะเมื่อทุกมิติน่าเชื่อถือ
* ค่าตั้งต้น (confidence 0.5, smoothing 5 s, reserved review 30 นาที, heartbeat 30 s, freshness TTL 30 s) มาจากข้อเสนอเดิม = *สมมติฐาน* ยังไม่ผ่านการทดลองจริง ปรับได้ด้วย env `SL_*` (ดู `services/api/app/engine/config.py`)
* `SL_MODE=production` ปิด `/api/demo/*` ทั้งหมด
