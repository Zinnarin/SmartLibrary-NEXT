# TEAM SETUP REPORT — Smart Library NEXT V3 (เตรียมทำงานร่วมกัน 4 คน)

**จัดทำ:** 15 ต.ค. 2569 โดย Claude Code ตามคำขอของ Person 4 (Staff / SeatCheck / QA / Integration) · **ขอบเขต:** เตรียม repo และ workflow เท่านั้น — **ไม่ได้แก้พฤติกรรมของแอป** และ **ยังไม่ได้สร้าง GitHub repo หรือ push** (รอคำอนุญาต)

---

## 1. ความพร้อมของ Repository

| รายการ | สถานะ | หลักฐาน |
|---|---|---|
| Git | ก่อนหน้านี้ **ไม่ได้ initialize** → สร้าง repo ในเครื่องแล้ว, branch หลัก `main` | `git init -b main` |
| V2 baseline | commit `45a61d9` + annotated tag **`v2-demo-baseline`** (132 ไฟล์, ~15 MB) | `git show v2-demo-baseline` |
| Team docs + workflow | commit ที่สองบน `main` (docs/team_v3, PR template, CI, ownership checker, หลักฐานตรวจ) | `git log --oneline` |
| Feature branches | `feature/v3-cv`, `feature/v3-backend`, `feature/v3-student`, `feature/v3-staff-qa` แตกจาก `main` ล่าสุด | `git branch` |
| Remote / GitHub | **ยังไม่มี** — ไม่ได้สร้าง repo, ไม่ได้ push (ตามคำสั่ง) | `git remote -v` ว่าง |
| ตรวจ V2 ซ้ำวันนี้ | pytest **53/53**, frontend build OK, Playwright **8/8** | `evidence/team_v3/V3_BASELINE_VERIFICATION.md` |
| Fresh clone ทำงานได้เอง | clone → venv → `pip install -r` → pytest **53/53** → `npm ci` → build ✓ | เดียวกัน |
| `.gitignore` / `.gitattributes` | ปรับใหม่ (ข้อ 1.1) + dry-run ยืนยันว่าไม่มีไฟล์ต้องห้ามถูก add | — |
| ไฟล์ทุกไฟล์มีเจ้าของ | `python scripts/check_ownership.py --audit` → OK (ไม่มี UNASSIGNED) | ข้อ 3 |

### 1.1 สิ่งที่ห้าม commit (บังคับด้วย `.gitignore` + ตรวจซ้ำด้วย `check_ownership.py`)
| ประเภท | ตัวอย่างที่พบในเครื่องจริง | การจัดการ |
|---|---|---|
| Virtual env | `.venv/`, `.venv-cv/` (torch ~GB) | ignore — แต่ละคนสร้างเอง |
| Node / build | `apps/web/node_modules/`, `apps/web/dist/`, `apps/web/test-results/` | ignore — `start_demo_windows.ps1` build ให้เอง |
| ฐานข้อมูล | `services/api/data/smartlibrary_demo.db` (+`-wal/-shm`), DB ทดสอบใน `.pytest_tmp/` | ignore — seed ใหม่อัตโนมัติ |
| Secrets | **ไม่พบ** API key / `.env` / private key ในโปรเจกต์ | ignore `.env*`, `*.pem`, `*.key` ไว้ล่วงหน้า |
| Demo credentials | `staff-demo-2569`, `cv-device-demo-2569` เป็นค่า default ใน `services/api/app/settings.py` | **commit ได้** (เป็น demo gate ที่เปิดเผยใน README อยู่แล้ว) — ห้ามนำไปใช้กับระบบจริง; ของจริงต้องตั้งผ่าน env `SL_STAFF_TOKEN` / `SL_DEVICE_TOKEN` |
| Model weights | `cv/models/yolo11n.pt` (5.6 MB, AGPL-3.0) | ignore — แต่ละคนดาวน์โหลดเอง (README) |
| วิดีโอ/เฟรมจากกล้อง | ยังไม่มี | ignore `*.mp4/.avi/.mov/.mkv/.webm`, `cv/experiments/**/raw/`, `**/frames/` ล่วงหน้า |
| ไฟล์เครื่องมือ/ล็อก | `.claude/launch.json`, `presentation/~$progress_update.pptx` (lock ของ PowerPoint ที่เปิดอยู่) | ignore `.claude/`, `~$*` |
| ข้อมูลส่วนบุคคล (**commit แล้ว — ต้องตัดสินใจ ข้อ 7**) | ชื่อ+รหัสนักศึกษา 4 คนใน `reference/Smart_Library.pdf`, `presentation/progress_update*.pptx`, `presentation/preview/progress_update.pdf`, `scripts/build_pptx.py`; path `C:\Users\ebz14\…` ใน log 16 ไฟล์ใต้ `evidence/` | เหมาะกับ **private repo เท่านั้น** — ห้ามเปิด public |

---

## 2. โครงสร้าง source ที่ยืนยันแล้ว (จาก `git ls-files`, 132 ไฟล์ใน baseline)
```
services/api/app/            FastAPI: main.py (routes+Pydantic), db.py, services.py, realtime.py (WS),
                             matching.py (StudyMatch/GroupFit/Wayfinder), settings.py, seed.py, scenarios.py
services/api/app/engine/     state_engine.py, trust.py, evidence.py, config.py, timeutil.py  ← pure Python ใช้ร่วมกับ cv/
services/api/requirements.txt
apps/web/src/                App.tsx (routing), api.ts (HTTP+types), live.tsx (WS/polling + BUG-011 guard),
                             labels.ts, main.tsx, styles.css
apps/web/src/pages/          StudentPage.tsx, StaffConsole.tsx, ScenarioLab.tsx, CvLab.tsx
apps/web/src/components/     FloorMap.tsx, SeatDetail.tsx (มีฟอร์ม SeatCheck อยู่ข้างใน), StudyMatch.tsx
apps/web/e2e/                demo.spec.ts, reliability.spec.ts, server_restart.spec.ts   (+ playwright.config.ts)
cv/                          run_cv.py, roi.py, roi_config.json, requirements-cv.txt, ROI_CALIBRATION_GUIDE_TH.md
tests/                       conftest.py, test_api.py, test_state_engine.py, test_reliability.py, test_roi_geometry.py
scripts/                     start_demo_windows.ps1, run_tests_windows.ps1, build_pptx.py, export_pptx_preview.ps1,
                             compose_test_results.py, measure_ws_latency.py, check_ownership.py (ใหม่)
docs/ evidence/ presentation/ verification/ reference/ templates/   เอกสาร/หลักฐาน V2 (FROZEN)
docs/team_v3/  evidence/team_v3/  .github/                          ใหม่สำหรับ V3
```

### 2.1 Path ในเอกสารทีมที่ไม่ตรงกับโค้ดจริง
| เอกสารเขียน | ของจริง | ผลกระทบ |
|---|---|---|
| `services/api/app/{state_engine,trust,evidence,config,timeutil}.py` | `services/api/app/engine/…` | แค่ path; เจ้าของ P2 เหมือนเดิม |
| `SeatCheckPanel.tsx` (P4) | ยังไม่มี — ฟอร์ม SeatCheck อยู่ใน `SeatDetail.tsx` (P3) | ต้องแยกแบบ 2 PR ตามลำดับ (ข้อ 3.2) |
| ไม่ได้กล่าวถึง | `live.tsx`, `main.tsx`, `styles.css`, `seed.py`, e2e V2 3 ไฟล์, test V2 4 ไฟล์, `cv/requirements-cv.txt`, scripts 4 ไฟล์ | กำหนดเจ้าของแล้วใน `OWNERSHIP_MAP.csv` |
| ไฟล์ใหม่ที่ sprint จะสร้าง (ยังไม่มี — ถูกต้อง) | `cv/experiments/`, `tests/test_cv_v3.py`, `tests/test_backend_v3.py`, `docs/api_contract_v3.md`, `apps/web/e2e/student_v3.spec.ts`, `staff_reliability_v3.spec.ts`, `verification/TEAM_V3_*.csv` | — |

---

## 3. File ownership (กฎที่ใช้จริง = `docs/team_v3/OWNERSHIP_MAP.csv`)
ผล audit บน baseline: **P1 6 ไฟล์ · P2 19 · P3 16 · P4 18 · FROZEN 73 · UNASSIGNED 0**

| คน | Branch | เป็นเจ้าของ | แก้ได้เมื่อเจ้าของอื่นอนุมัติใน PR |
|---|---|---|---|
| **P1 CV** | `feature/v3-cv` | `cv/**` (รวม `cv/experiments/`), `tests/test_roi_geometry.py`, `tests/test_cv_v3.py` | — (ใช้ `services/api/app/engine/` ของ P2 แบบ import เท่านั้น ห้ามแก้) |
| **P2 Backend** | `feature/v3-backend` | `services/api/app/**` (รวม `engine/`, `seed.py`, `scenarios.py`), `tests/conftest.py`, `tests/test_api.py`, `tests/test_state_engine.py`, `tests/test_backend_v3.py`, `docs/api_contract_v3.md` | `services/api/requirements.txt` (+P4); `docs/api_contract_v3.md` ต้องให้ P1/P3/P4 review; `conftest.py` ต้องให้ทุกคน review |
| **P3 Student** | `feature/v3-student` | `apps/web/src/**` ยกเว้นไฟล์ของ P4 ด้านล่าง (`App.tsx`, `api.ts`, `labels.ts`, `live.tsx`, `main.tsx`, `styles.css`, `pages/StudentPage.tsx`, `pages/CvLab.tsx`, `components/*`), `apps/web/{vite.config.ts,tsconfig.json,index.html}`, `apps/web/e2e/student_v3.spec.ts` | `live.tsx` (+P4: มี BUG-011 guard), `package.json`/`package-lock.json` (+P4), `CvLab.tsx` (+P1) |
| **P4 Staff/QA/Integration (คุณ)** | `feature/v3-staff-qa` | `pages/StaffConsole.tsx`, `pages/ScenarioLab.tsx` (+P2), `components/SeatCheckPanel.tsx` (ใหม่, +P3), `apps/web/e2e/*` (V2 regression + `staff_reliability_v3.spec.ts`), `apps/web/playwright.config.ts` (+P3), `tests/test_reliability.py` (+P2), `scripts/*`, `pytest.ini` (+P2), `.github/*`, `.gitignore`, `.gitattributes`, `README.md`, `docs/team_v3/*`, `docs/DEMO_RUNBOOK_TH.md`, `evidence/team_v3/*`, `verification/TEAM_V3_*`, `presentation/v3/*` | — |
| **FROZEN** | — | `evidence/*` (V2), `presentation/*` (V2 รวม `progress_update_v2.pptx`, screenshots), `verification/*` (V2), `reference/*`, `templates/*`, spec ใน `docs/*`, `CLAUDE_CODE_MASTER_PROMPT.md`, `START_HERE.md` | ห้ามแก้ — ผลใหม่ลง `*/team_v3/` หรือ `presentation/v3/` |

### 3.1 การตรวจอัตโนมัติ
```powershell
.venv\Scripts\python scripts\check_ownership.py --audit            # ทุกไฟล์มีเจ้าของ / ไม่มีไฟล์ต้องห้าม
.venv\Scripts\python scripts\check_ownership.py --owner P3 --base main   # ก่อนเปิด PR: OK / REVIEW (ต้องได้ approval) / BLOCK (frozen หรือห้าม commit)
```
ทดสอบตัวตรวจแล้วด้วย branch ทดลอง (ข้อ 8) — ทำงานแบบ read-only ไม่แก้ไฟล์

### 3.2 การแยก SeatCheck ออกจาก SeatDetail (ป้องกัน 2 คนแก้ไฟล์เดียว)
1. **PR-A (P4, `feature/v3-staff-qa`)**: สร้าง `components/SeatCheckPanel.tsx` (ย้ายตรรกะฟอร์ม/submit จาก `SeatDetail.tsx` มาแบบพฤติกรรมเดิม) — ยังไม่มีใครเรียกใช้ → merge ได้โดยไม่กระทบแอป
2. **PR-B (P3, `feature/v3-student`)** หลัง PR-A merge: ลบฟอร์มเดิมใน `SeatDetail.tsx` แล้ว `import SeatCheckPanel` · ต้องผ่าน e2e `demo.spec.ts` (`seatcheck-open/submit` testid เดิมต้องคงไว้)

---

## 4. Shared API contracts
**เจ้าของ contract ทั้งหมด: P2.** จุดเริ่มต้นจากโค้ดจริง: `docs/team_v3/api_baseline_v2_openapi.json` (สกัดด้วย `app.openapi()` — 24 HTTP paths, 9 component schemas (request models 7 + validation error 2)) → P2 เขียน `docs/api_contract_v3.md` (routes + schema + ตัวอย่าง response + error codes) ภายใน Day 0–1

| กลุ่ม | Endpoint (V2 baseline) | Auth | Producer → Consumer |
|---|---|---|---|
| อ่านสถานะ | `GET /api/health`, `/api/zones`, `/api/layout`, `/api/seats`, `/api/seats/{seat_id}` | — | P2 → P3 (`api.ts`, `live.tsx`), P4 (QA) |
| แนะนำ/นำทาง | `GET /api/recommendations`, `GET /api/route` | — | P2 → P3 |
| SeatCheck นักศึกษา | `GET /api/session`, `POST /api/seat-reports`, `GET /api/seat-reports/mine` | session token (`X-Session-Token`) | P2 → P4 `SeatCheckPanel` (ปัจจุบันเรียกจาก `SeatDetail.tsx`) |
| Staff | `GET /api/admin/check`, `GET /api/admin/seat-reports`, `POST /api/admin/seat-reports/{id}/resolve`, `POST/DELETE /api/admin/seats/{id}/override`, `GET /api/admin/events`, `GET /api/admin/devices` | `X-Staff-Token` | P2 → P4 `StaffConsole.tsx` |
| Demo (เฉพาะ `SL_MODE=demo`) | `GET /api/demo/scenarios`, `POST /api/demo/scenario`, `POST /api/demo/reset` | `X-Staff-Token` (scenarios list ไม่ต้อง) | P2 → P4 `ScenarioLab.tsx` |
| CV ingest | `POST /api/ingest/observations` (`IngestIn` → `SeatObsIn` → `DetectionIn`) | `X-Device-Token` | **P1 → P2** |
| CV แสดงผล | `GET /api/cv/status`, `/api/cv/annotated/{name}`, `/api/cv/lab-seats`, `/api/stats` | — | P2 (อ่านไฟล์ของ P1) → P3 `CvLab.tsx`, P4 |
| Realtime | `WS /ws/seats` — server ส่ง `snapshot` / `delta` (เฉพาะที่นั่งที่เปลี่ยน + `meta` หรือ null) / `heartbeat` (เมื่อเงียบเกิน ~5 วิ) / `pong`; client ส่ง `"ping"` | — | P2 → P3 `live.tsx` |

**สัญญาที่ไม่ได้อยู่ใน OpenAPI (ต้องใส่ใน `api_contract_v3.md`):**
1. **รูปทรง response** ของ seat/meta ไม่มี `response_model` — นิยามจริงอยู่ที่ `engine/trust.py::build_seat_view()` และ `main.py::meta()`; ฝั่ง client ลอก type ไว้ใน `apps/web/src/api.ts` (`Seat`, `Meta`, …)
2. **WS message** ข้างต้น (ไม่มีใน OpenAPI)
3. **Python contract ภายใน**: `cv/run_cv.py` import `app.engine.config.EngineConfig`, `app.engine.evidence.{Detection, classify}`, `app.engine.state_engine.{SeatEngineState, step}` — P2 ห้ามเปลี่ยน signature โดยไม่แจ้ง P1
4. **ตำแหน่งไฟล์ผล CV**: runner เขียน `evidence/cv/latest_run.json` และ API อ่านจาก `settings.cv_evidence_dir` (= `evidence/cv`) — แต่ `evidence/` เป็น FROZEN → ต้องตกลงตำแหน่งใหม่ (ข้อ 7)

**ขั้นตอนเปลี่ยน contract:** Issue (`ต้องการอะไร / endpoint / input-output / เหตุผล / deadline / test case`) → P2 แก้ `api_contract_v3.md` + backend + test ใน PR ของ `feature/v3-backend` (**merge ก่อน**) → consumer ปรับตาม · ระหว่าง sprint ให้เปลี่ยนแบบ **เพิ่มเท่านั้น** (additive) ห้ามลบ/เปลี่ยนชื่อ field เว้นแต่ทั้ง 4 คนอนุมัติ

---

## 5. ขั้นตอน GitHub (ยังไม่ได้ทำ — รอคำอนุญาตของคุณ)
> ไม่ได้สร้าง repo และไม่ได้ push · GitHub CLI (`gh`) **ไม่ได้ติดตั้ง**ในเครื่อง → ใช้หน้าเว็บ หรือ `winget install GitHub.cli` แล้ว `gh auth login`

1. **สร้าง repo แบบ Private** (เจ้าของ = บัญชี GitHub ของคุณหรือ organization ของกลุ่ม): github.com/new → ชื่อเช่น `smart-library-next` → เลือก **Private** → **ไม่ติ๊ก** README / .gitignore / license (มีอยู่แล้ว) → Create
   (ทางเลือก CLI: `gh repo create smart-library-next --private --source . --remote origin` — ห้ามใช้ `--public`)
2. **เชื่อม remote และ push ครั้งแรก** (ทำเมื่อคุณอนุญาตเท่านั้น):
   ```powershell
   git remote add origin https://github.com/<OWNER>/smart-library-next.git
   git push -u origin main
   git push origin v2-demo-baseline
   git push origin feature/v3-cv feature/v3-backend feature/v3-student feature/v3-staff-qa
   ```
3. **Settings → Collaborators** → เชิญอีก 3 คนด้วย GitHub username (repo ส่วนตัวของบุคคล: ผู้ร่วมทุกคนได้สิทธิ์ write)
4. **ป้องกัน `main`** (Settings → Branches/Rules): ต้องผ่าน PR, approve ≥1, ต้องผ่าน status checks `ci / backend` และ `ci / frontend`, ห้าม force-push, ห้ามลบ
   ⚠ ตามเอกสาร GitHub: branch protection/rulesets บน **private** repo ต้องใช้ GitHub **Pro/Team** (นักศึกษาขอ Pro ฟรีผ่าน GitHub Student Developer Pack) — ถ้าไม่มี ให้ใช้กติกาทีม + CI + `check_ownership.py` และ **P4 เป็นคนเดียวที่กด Merge** (ตรวจหน้าจอ Settings จริงของบัญชีอีกครั้ง)
5. **เปิด CODEOWNERS**: ใส่ username ใน `docs/team_v3/CODEOWNERS.proposed` แล้วคัดลอกเป็น `.github/CODEOWNERS` ใน PR ที่ทั้ง 4 คน approve
6. **CI** (`.github/workflows/ci.yml`): pytest + ownership audit + frontend build ทุก PR — **ยังไม่ได้รันบน GitHub** (คำสั่งเดียวกันผ่านแล้วบน fresh clone ในเครื่อง); Playwright รันในเครื่องโดย P4
7. **วิธี merge**: “Squash and merge”, ชื่อ PR `[P1][CV] …` / `[P2][API] …` / `[P3][Student] …` / `[P4][Staff] …`; ลำดับ: contract P2 → adapter P1 → backend P2 → UI P3 → Staff/QA P4 (merge ทีละ PR และรัน regression ทุกครั้ง) · ก่อนนำเสนอ tag `v3-integrated-demo`

---

## 6. คำสั่งที่สมาชิกแต่ละคนต้องทำ

### 6.1 ทุกคน (ครั้งแรก, Windows PowerShell)
```powershell
git config --global core.longpaths true          # กัน "Filename too long" (เจอจริงตอนตรวจ)
git config --global core.autocrlf true
mkdir C:\dev; cd C:\dev                           # ใช้ path สั้น ไม่ใช้ OneDrive/Google Drive sync
git clone https://github.com/<OWNER>/smart-library-next.git
cd smart-library-next
git switch feature/v3-<cv|backend|student|staff-qa>
powershell -ExecutionPolicy Bypass -File scripts\start_demo_windows.ps1 -Reset   # สร้าง .venv, npm ci, build, เปิด :8000
# หน้าต่างใหม่:
.venv\Scripts\python -m pytest -q                 # ต้องได้ 53 passed ก่อนเริ่มแก้อะไร
```
ต้องมี: Git, Python 3.10, Node.js 22+ (ทดสอบกับ 24.11), Microsoft Edge (สำหรับ Playwright)

**กติกาประจำวัน**
- แก้เฉพาะไฟล์ของตัวเอง → `check_ownership.py --owner P? --base main` ก่อน push · commit เล็ก ๆ ข้อความชัด
- ดึงงานล่าสุด: `git fetch origin` แล้ว `git merge origin/main` (หรือ rebase) บน branch ตัวเองอย่างน้อยวันละครั้ง
- **ห้าม push เข้า `main`** · ห้ามแก้ไฟล์ FROZEN · ห้าม commit `.venv`, DB, weights, คลิป/ภาพบุคคล, secrets
- ⚠ จนกว่า P4 จะแก้ (ข้อ 7 #7): หลังรัน `npx playwright test` หรือ `cv\run_cv.py` ให้รัน `git status` และ `git restore evidence/ presentation/screenshots/` ก่อน commit
- Stand-up เย็นละ 4 บรรทัด (ตาม `03_SPRINT_PLAN.md`)

### 6.2 P1 — CV (`feature/v3-cv`)
1. สร้าง CV env ตาม README (`.venv-cv`, torch CPU, ultralytics) และดาวน์โหลด `yolo11n.pt` เอง (ไม่ commit)
2. งานแรก: ตกลงกับ P2 เรื่องตำแหน่งผล CV ของ V3 (เช่น `evidence/team_v3/cv/`) แล้วแก้ `cv/run_cv.py` ให้ไม่เขียนทับ `evidence/cv/`
3. ฉากทดลองต้องมี consent; เก็บคลิปนอก Git (`cv/experiments/**/raw/` ถูก ignore); commit เฉพาะ ROI, log ที่ไม่มีข้อมูลส่วนบุคคล, ground truth, metrics พร้อม N
4. ส่ง event ผ่าน `POST /api/ingest/observations` เท่านั้น (CV-LAB / LAB1–4) — ห้ามเขียน DB ตรง ห้ามแก้ `services/api/**`

### 6.3 P2 — Backend (`feature/v3-backend`)
1. เขียน `docs/api_contract_v3.md` จาก `api_baseline_v2_openapi.json` + `trust.py::build_seat_view` + WS messages (ข้อ 4) แล้วเปิด PR แรก (ให้ P1/P3/P4 review)
2. เพิ่ม `tests/test_backend_v3.py` (contract tests ingest: valid / duplicate / outdated / uncertain / bad token)
3. ตกลงตำแหน่งผล CV กับ P1 (เช่น env `SL_CV_EVIDENCE_DIR`); ห้ามเปลี่ยน signature ใน `engine/` โดยไม่แจ้ง P1
4. เปลี่ยน `conftest.py` / `requirements.txt` ต้องผ่าน review ทุกคน / P4

### 6.4 P3 — Student (`feature/v3-student`)
1. แสดง source/freshness/unknown/pending ให้ชัดโดยอิงสัญญาจาก P2 (ห้ามคำนวณสถานะเองฝั่งหน้าเว็บนอกจาก guard BUG-011 ที่มีอยู่)
2. แก้ `live.tsx` ต้องให้ P4 approve และต้องผ่าน e2e `reliability.spec.ts` + `server_restart.spec.ts`
3. รอ PR-A ของ P4 (SeatCheckPanel) แล้วทำ PR-B (ข้อ 3.2); คง `data-testid` เดิม
4. เพิ่ม `apps/web/e2e/student_v3.spec.ts`

### 6.5 P4 — Staff/QA/Integration (`feature/v3-staff-qa`) — คุณ
1. ตัดสินใจข้อ 7 ที่เป็นของคุณ แล้วทำ GitHub ข้อ 5 เมื่อพร้อม
2. **งานแรก (กันปัญหาทั้งทีม):** ให้ Playwright เขียนผล/ภาพไป `apps/web/test-results/` (ถูก ignore) หรือ `evidence/team_v3/` เว้นแต่ตั้ง env เพื่อเก็บหลักฐานโดยตั้งใจ (`playwright.config.ts` + `e2e/*.spec.ts` เป็นของคุณ)
3. PR-A `SeatCheckPanel.tsx`; `staff_reliability_v3.spec.ts`; ตัดสินความหมาย override เมื่อรายงานว่า “มีคนนั่ง” (ข้อ 7)
4. เป็นผู้กด Merge, รัน pytest + build + Playwright หลังทุก PR, บันทึกผลใน `evidence/team_v3/` และ `verification/TEAM_V3_*.csv`

---

## 7. ข้อที่ยังต้องตัดสินใจ / Blockers
| # | เรื่อง | ใครตัดสิน | ข้อเสนอ |
|---|---|---|---|
| 1 | **อนุญาตให้ push** + บัญชีเจ้าของ repo + ชื่อ repo + GitHub username ของ 3 คน | คุณ / ทีม | blocker ของข้อ 5 ทั้งหมด |
| 2 | Branch protection บน private repo ต้องใช้ Pro/Team | คุณ | ขอ GitHub Student Developer Pack หรือใช้กติกา “P4 merge คนเดียว” |
| 3 | `gh` CLI ไม่มีในเครื่อง | คุณ | ใช้หน้าเว็บ (พอ) หรือ `winget install GitHub.cli` |
| 4 | ชื่อ+รหัสนักศึกษาในไฟล์ที่ commit แล้ว (reference PDF, deck, PDF, `build_pptx.py`) และ path `C:\Users\ebz14` ใน log | ทีม 4 คน | ยอมรับได้สำหรับ private repo ของสมาชิกที่มีชื่ออยู่แล้ว — **ห้ามเปิด public** โดยไม่ลบออกก่อน |
| 5 | อีเมลผู้เขียน commit: baseline ใช้ `(personal Gmail)` จาก git config ของคุณ | คุณ | ถ้าไม่ต้องการให้เห็น ให้ตั้ง noreply ของ GitHub แล้วแก้ author ของ 2 commit นี้ **ก่อน push ครั้งแรก** |
| 6 | ตำแหน่งผล CV ของ V3 (runner เขียน / API อ่าน `evidence/cv/` ที่ FROZEN) | P1 + P2 | `evidence/team_v3/cv/` + env ใน `settings.py` |
| 7 | Test/เครื่องมือเขียนทับไฟล์ FROZEN: e2e (23 ไฟล์ — ยืนยันแล้ว), `cv/run_cv.py`, `scripts/build_pptx.py`, `scripts/compose_test_results.py` | P4 (+P1) | งานแรกของ P4/P1 (ข้อ 6); ชั่วคราวใช้ `git restore` |
| 8 | Override เมื่อยืนยันรายงาน “มีคนนั่ง”: V2 ตั้ง default เป็น **Maintenance** (ซ่อม/ทำความสะอาด) ซึ่งความหมายไม่ตรง; Agreement C เสนอ `Unknown / Pending Inspection` | P4 (+P2 ถ้าต้องเพิ่มสถานะใหม่) | ใช้ `unknown` override ที่มีอยู่แล้วแทน (ไม่ต้องเปลี่ยน API) |
| 9 | CiRA CORE เป็นเครื่องมือบังคับของวิชาหรือไม่ | ถามอาจารย์ (P4 ประสาน) | ระหว่างรอ: คง YOLO11n |
| 10 | Ultralytics/YOLO เป็น AGPL-3.0 | ทีม | ใช้ใน private repo ได้; ถ้าจะเปิดเผยโค้ดต้องพิจารณาเงื่อนไข AGPL; weights ไม่ commit |
| 11 | CI ยังไม่เคยรันบน GitHub; Playwright ไม่อยู่ใน CI (ใช้ Edge ในเครื่อง) | P4 | ตรวจ run แรกหลัง push |
| 12 | CV บนที่นั่งจริง / ผังจริง ยัง **BLOCKED** จาก V2 (ไม่มีภาพที่ได้รับอนุญาต, ไม่มีผังจริง) | อาจารย์ / ห้องสมุด | P4 ประสานขออนุญาต |

---

## 8. สิ่งที่ทำ / ไม่ได้ทำ ในรอบนี้
**ทำ (ในเครื่องเท่านั้น):** `git init`, ปรับ `.gitignore` + เพิ่ม `.gitattributes`, commit+tag baseline V2, ตรวจ V2 ซ้ำ (pytest/build/Playwright/fresh clone), คัดลอกเอกสารทีม 11 ไฟล์ (ตรงต้นฉบับทุกไบต์), `OWNERSHIP_MAP.csv` + `scripts/check_ownership.py`, OpenAPI snapshot, `.github/pull_request_template.md`, `.github/workflows/ci.yml`, `CODEOWNERS.proposed`, `evidence/team_v3/V3_BASELINE_VERIFICATION.md`, รายงานนี้, สร้าง 4 branches

**ไม่ได้ทำ:** แก้โค้ดแอป/พฤติกรรม production (ไม่มีไฟล์ใน `services/`, `apps/web/src/`, `cv/` ถูกแก้), สร้าง GitHub repo, push, เชิญสมาชิก, ตั้ง branch protection, เพิ่มฟีเจอร์ใหม่

**หมายเหตุการตรวจ:** ผลทดสอบในรายงานนี้รันโดย Claude Code บนเครื่องของคุณวันที่ 15 ต.ค. 2569; สมาชิกแต่ละคนต้องรันซ้ำในเครื่องตัวเอง (ข้อ 6.1)
