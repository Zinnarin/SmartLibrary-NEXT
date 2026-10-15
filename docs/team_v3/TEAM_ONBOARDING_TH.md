# TEAM ONBOARDING — Smart Library NEXT V3 (สมาชิกทั้ง 4 คน)

> อ่านไฟล์นี้ก่อนเริ่มงาน แล้วอ่าน task guide ของตัวเองใน `docs/team_v3/tasks/`
> หลักใหญ่: **หนึ่ง repo · หนึ่ง backend · หนึ่ง frontend · หนึ่งฐานข้อมูล** — ห้ามสร้างระบบใหม่มาแทนของเดิม V2

## 1. ข้อมูล Repository
| รายการ | ค่า |
|---|---|
| URL | https://github.com/Zinnarin/SmartLibrary-NEXT |
| Visibility | **Private** (ห้ามเปลี่ยนเป็น public — มีชื่อ/รหัสนักศึกษาในเอกสารต้นฉบับ) |
| Branch หลัก | `main` — **ห้าม push ตรง**; เข้า main ได้ทาง Pull Request เท่านั้น (P4 เป็นผู้ merge) |
| Baseline V2 | tag `v2-demo-baseline` (ระบบที่นำเสนอได้: pytest 53/53, Playwright 8/8) |
| Branch ของแต่ละคน | P1 `feature/v3-cv` · P2 `feature/v3-backend` · P3 `feature/v3-student` · P4 `feature/v3-staff-qa` |
| เจ้าของไฟล์ | `docs/team_v3/OWNERSHIP_MAP.csv` (ตรวจด้วย `scripts/check_ownership.py`) |
| สัญญา API | `docs/team_v3/api_baseline_v2_openapi.json` (ของจริงจากโค้ด V2) → P2 จะเขียน `docs/api_contract_v3.md` |

## 2. เครื่องมือที่ต้องมี (Windows)
| เครื่องมือ | เวอร์ชันที่ทดสอบแล้ว | หมายเหตุ |
|---|---|---|
| Git for Windows | 2.53 | ตั้ง `core.longpaths` (ข้อ 3) |
| Python | **3.10** (3.10.11) | ใช้ผ่าน `py -3.10` |
| Node.js | 22 LTS ขึ้นไป (ทดสอบ 24.11) | มากับ npm |
| Microsoft Edge | มีใน Windows อยู่แล้ว | Playwright ใช้ Edge ในเครื่อง |
| GitHub CLI (ไม่บังคับ) | 2.102 | `winget install --id GitHub.cli -e` — ช่วยสร้าง PR จาก terminal |
| P1 เพิ่ม | `.venv-cv` (torch CPU + ultralytics) | ดู README หัวข้อ “Optional real CV” |

## 3. Clone ครั้งแรก
```powershell
git config --global core.longpaths true      # กัน "Filename too long" (เจอจริงตอนตรวจ)
git config --global user.name  "ชื่อจริงของคุณ"
git config --global user.email "อีเมลที่ผูกกับ GitHub (หรือ noreply ของ GitHub)"
mkdir C:\dev -ErrorAction SilentlyContinue; cd C:\dev     # path สั้น, ไม่อยู่ใน OneDrive/Google Drive
git clone https://github.com/Zinnarin/SmartLibrary-NEXT.git
cd SmartLibrary-NEXT
```
ถ้าถูกถามรหัสผ่านตอน clone/push ให้ล็อกอินผ่านหน้าต่าง Git Credential Manager (เบราว์เซอร์) หรือรัน `gh auth login --web` — **ห้ามส่งรหัสผ่าน/token ให้ใครหรือใส่ในไฟล์**

## 4. ติดตั้ง dependency และเปิดแอป
```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_demo_windows.ps1 -Reset
```
สคริปต์นี้สร้าง `.venv` + ติดตั้ง `services\api\requirements.txt`, รัน `npm ci` + build frontend (ครั้งแรก), แล้วเปิด http://127.0.0.1:8000
* นักศึกษา `/` · เจ้าหน้าที่ `/#/staff` (PIN สาธิต `staff-demo-2569`) · Scenario Lab `/#/lab` · CV Lab `/#/cv`
* 6–8 วินาทีแรกที่นั่งเป็น “ไม่แน่ใจ” — **ปกติ** (ระบบรอหลักฐาน)
* ข้อความ `ERROR: port 8000 is already in use` = มีเซิร์ฟเวอร์เปิดอยู่แล้ว (ใช้ตัวเดิม หรือ `-Port 8010`)
* ข้อมูลที่นั่งในเดโมเป็น **SIMULATION** ทั้งหมด — ห้ามพูด/เขียนว่าเป็นกล้องจริง

## 5. รันทดสอบ
```powershell
# หน้าต่าง PowerShell ใหม่ (ให้เซิร์ฟเวอร์ข้อ 4 เปิดค้างไว้):
powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1
```
* ทำ pytest (backend) + Playwright 8 สถานการณ์ (ถ้าเซิร์ฟเวอร์ :8000 เปิด)
* **ก่อนเริ่มแก้อะไร ต้องผ่านในเครื่องตัวเองก่อน** (baseline: pytest 53 passed, Playwright 8 passed)
* ทดสอบเร็ว ๆ เฉพาะ backend: `.venv\Scripts\python -m pytest -q` · build frontend: `cd apps\web; npm run build`
* ⚠ **จนกว่า PR “P4: isolate test/tool artifacts” จะถูก merge เข้า main:** การรัน Playwright จะเขียนทับไฟล์ V2 ใน `evidence/` และ `presentation/screenshots/` — หลังรันทุกครั้งให้
  ```powershell
  git restore evidence/ presentation/screenshots/
  ```
  หลัง merge แล้ว ผลทั้งหมดจะไปที่ `artifacts/` (ไม่ถูก commit) และสคริปต์จะตรวจ `--frozen-clean` ให้อัตโนมัติ

## 6. สลับ branch และอัปเดตงานล่าสุด
```powershell
git switch feature/v3-<cv|backend|student|staff-qa>     # branch ของตัวเองเท่านั้น
git fetch origin
git merge origin/main          # ดึงของที่ merge แล้วเข้ามา (อย่างน้อยวันละครั้ง และก่อนเปิด PR)
```
ถ้าเกิด conflict ในไฟล์ของคนอื่น: **หยุด** แล้วถามเจ้าของไฟล์/P4 ในกลุ่ม อย่าแก้ทับเอง

## 7. ใครเป็นเจ้าของไฟล์อะไร (สรุป — รายละเอียดใน `OWNERSHIP_MAP.csv`)
| คน | เป็นเจ้าของ | ห้ามแก้ (ขอผ่าน Issue/PR review) |
|---|---|---|
| **P1 CV** | `cv/**`, `tests/test_roi_geometry.py`, `tests/test_cv_v3.py` | `services/**` (รวม `engine/` — import ได้แต่ห้ามแก้), `apps/web/**` |
| **P2 Backend** | `services/api/**` (main, db, services, realtime, matching, settings, seed, scenarios, `engine/*`), `tests/conftest.py`, `tests/test_api.py`, `tests/test_state_engine.py`, `tests/test_backend_v3.py`, `docs/api_contract_v3.md` | `apps/web/**`, `cv/**` |
| **P3 Student** | `apps/web/src/**` (App, api, labels, live*, main, styles, StudentPage, CvLab*, FloorMap, SeatDetail, StudyMatch), `apps/web/{vite.config.ts,tsconfig.json,index.html,package.json*}`, `apps/web/e2e/student_v3.spec.ts` | StaffConsole, ScenarioLab, SeatCheckPanel, e2e อื่น, `services/**`, `cv/**` |
| **P4 Staff/QA/Integration** | StaffConsole, ScenarioLab*, SeatCheckPanel*, `apps/web/e2e/*` (ยกเว้น student_v3), `playwright.config.ts`*, `tests/test_reliability.py`*, `scripts/*`, `.github/*`, `docs/team_v3/*`, `evidence/team_v3/*`, `verification/TEAM_V3_*`, `presentation/v3/*` | `services/**`, `cv/**`, หน้า student |
| **FROZEN (ห้ามใครแก้)** | `evidence/*` (V2), `presentation/*` (V2), `verification/*` (V2), `reference/*`, `templates/*`, spec ใน `docs/*` | ผลงาน V3 ใส่ `evidence/team_v3/`, `presentation/v3/` |

`*` = ต้องได้ approval จากเจ้าของที่เกี่ยวข้องใน PR (ดูคอลัมน์ `approval_required_from`)

ตรวจก่อน push ทุกครั้ง:
```powershell
.venv\Scripts\python scripts\check_ownership.py --owner P? --base origin/main
```
`OK` = ไฟล์ของคุณ · `REVIEW` = ไฟล์คนอื่น (ต้องให้เจ้าของ approve ใน PR) · `BLOCK` = ไฟล์ freeze หรือไฟล์ห้าม commit (ต้องเอาออก)

## 8. Commit
```powershell
git status                        # ดูว่ามีอะไรเปลี่ยน — ต้องไม่มี .venv, .db, node_modules, วิดีโอ, ภาพบุคคล
git add <ไฟล์ที่ตั้งใจ>            # หลีกเลี่ยง git add -A ถ้าไม่แน่ใจ
git commit -m "[P3][Student] แสดงป้าย SIMULATION/CV บนการ์ดที่นั่ง"
```
ข้อความ commit: `[P?][โมดูล] ทำอะไร` สั้น ชัด หนึ่งเรื่องต่อหนึ่ง commit

## 9. Push
```powershell
git push origin feature/v3-<ของคุณ>
```
**ห้าม** `git push origin main` · **ห้าม** `git push --force` · ห้าม push branch ของคนอื่น

## 10. สร้าง Pull Request
1. เข้า repo บน GitHub → แถบ **Pull requests** → **New pull request** → base: `main` ← compare: `feature/v3-<ของคุณ>` (หรือ `gh pr create --base main --draft`)
2. กรอกแบบฟอร์มที่ขึ้นมาอัตโนมัติ (`.github/pull_request_template.md`): อะไรใหม่/อะไรของ V2, ผล ownership check, ผลทดสอบจริง (ห้ามเขียน PASS ถ้าไม่ได้รัน), ข้อจำกัด
3. ใส่ label ของตัวเอง (`person-1-cv` / `person-2-backend` / `person-3-frontend` / `person-4-qa`) และอ้าง Issue (`Closes #<เลข>`)
4. ขอ review จากอย่างน้อย 1 คน (ถ้าแตะ contract หรือไฟล์คนอื่น ต้องเป็นเจ้าของไฟล์นั้น)
5. รอ CI เขียว (`ci / backend`, `ci / frontend`) — **ห้ามแก้ test ให้ผ่านโดยไม่แก้สาเหตุ**
6. P4 เป็นผู้กด **Squash and merge** หลังตรวจ (รัน regression ในเครื่องด้วย)

## 11. รายงานปัญหา / Blocker
* เปิด GitHub Issue: หัวข้อ `[BLOCKED][P?] …` + label `blocked` (+ label ของตัวเอง) — ใส่: ต้องการอะไร / จากใคร / ผลกระทบ / deadline
* ต้องการเปลี่ยนไฟล์หรือ API ของคนอื่น: Issue รูปแบบ `ต้องการอะไร / endpoint หรือ component / input-output / เหตุผล / deadline / test case` + label `integration`
* บัค: Issue + label `bug` พร้อมขั้นตอน reproduce และ log จริง
* Stand-up ทุกเย็นในแชทกลุ่ม 4 บรรทัด: (1) ทำอะไรไป + commit/PR (2) วันนี้จะทำอะไร (3) ติดอะไร/ต้องการ API จากใคร (4) หลักฐาน/ผลทดสอบ

## 12. การรวมระบบ (Integration)
* ลำดับ merge: **สัญญา API ของ P2 ก่อน** → adapter P1 → backend P2 → UI P3 → Staff/QA P4 · merge ทีละ PR
* หลัง **ทุก** PR ที่ merge: P4 รัน `scripts\run_tests_windows.ps1` บน `main` และบันทึกผลใน `evidence/team_v3/`
* เปลี่ยน API ได้แบบ **เพิ่ม** เท่านั้นระหว่าง sprint (ห้ามลบ/เปลี่ยนชื่อ field) เว้นแต่ทั้ง 4 คนอนุมัติ
* SeatCheck UI: P4 สร้าง `SeatCheckPanel.tsx` ก่อน (PR-A) → P3 จึงย้ายไปใช้ใน `SeatDetail.tsx` (PR-B) ห้ามแก้ `SeatDetail.tsx` พร้อมกัน
* ปิดรับ feature 24 ชม. ก่อนนำเสนอ · release = tag `v3-integrated-demo`
* ผล CV/ความแม่นยำ ต้องมีหลักฐานจริง (dataset, consent, model, N) — ไม่มีก็รายงาน `BLOCKED`

## 13. ใช้ Claude Code / AI ช่วยงาน
ใช้ prompt ในไฟล์ task guide ของตัวเอง (ข้อ “Claude Code prompt”) — prompt บังคับให้ AI **ตรวจโค้ดจริงก่อนแก้**, แก้เฉพาะไฟล์ของคุณ, และรายงานผลทดสอบจริง · ต้องระบุใน PR ว่าส่วนไหน AI ช่วย
