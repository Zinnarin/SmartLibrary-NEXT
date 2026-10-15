# Task Guide — PERSON 3: Student Frontend / Floor Map / StudyMatch / GroupFit / Wayfinder
Branch: **`feature/v3-student`** · Label: `person-3-frontend` · Reviewer หลัก: P4 (UI/staff, live.tsx), P2 (API types)

## 1. เป้าหมาย
ทำให้นักศึกษา **เข้าใจสถานะที่นั่งอย่างถูกต้องและน่าเชื่อถือ**: แยก SIMULATION / ผล CV ทดลอง / stale / unknown / มีรายงานค้าง ให้อ่านง่าย, ใช้ได้บนมือถือและคีย์บอร์ด, และรับ `SeatCheckPanel` ของ P4 เข้าหน้า Student — โดยหน้าเว็บ **ไม่คำนวณสถานะเอง** (ใช้ข้อมูลจาก backend ตาม contract)

## 2. ไฟล์ที่เป็นเจ้าของ
`apps/web/src/App.tsx`, `api.ts`, `labels.ts`, `live.tsx` (+P4 approve), `main.tsx`, `styles.css`, `pages/StudentPage.tsx`, `pages/CvLab.tsx` (+P1 approve), `components/FloorMap.tsx`, `components/SeatDetail.tsx`, `components/StudyMatch.tsx`, `apps/web/vite.config.ts`, `tsconfig.json`, `index.html`, `package.json` + `package-lock.json` (+P4 approve), **ใหม่** `apps/web/e2e/student_v3.spec.ts`

## 3. ไฟล์ที่ห้ามแก้
`pages/StaffConsole.tsx`, `pages/ScenarioLab.tsx`, `components/SeatCheckPanel.tsx` (P4), `apps/web/e2e/*` อื่น ๆ + `playwright.config.ts` (P4), `services/**` (P2), `cv/**` (P1), `scripts/*`, FROZEN (`evidence/*`, `presentation/*`, `verification/*`, …)

## 4. ฟังก์ชันที่ต้องทำ
1. ป้ายแหล่งข้อมูลบนการ์ด/รายละเอียดที่นั่ง: `SIMULATION` vs `CV (ทดลอง)` + เวลา/อายุข้อมูล — ห้ามทำให้ stale / unknown / camera offline / pending report ดูเป็น “ว่าง” สีเขียว
2. ตรวจ StudyMatch (hard constraints, no-result + relax suggestions), GroupFit (adjacency ที่บันทึกด้วยมือ), Wayfinder (หน่วยผัง ไม่ใช่เมตร) — ข้อความต้องไม่อ้างเกินจริง, ไม่มี % ความแม่นยำปลอม
3. มือถือ (≥ 360 px ไม่มี horizontal scroll ทั้งหน้า), คีย์บอร์ด (Tab/Enter บนที่นั่ง), ข้อความ empty/error ชัดเจน
4. **SeatCheck (PR-B):** หลัง PR-A ของ P4 (`SeatCheckPanel.tsx`) merge แล้ว → ลบฟอร์มเดิมใน `SeatDetail.tsx` และ `import SeatCheckPanel` แทน; **คง `data-testid` เดิม** (`seatcheck-open`, `seatcheck-form`, `seatcheck-submit`, `pending-badge`, `my-reports`)
5. ถ้าแตะ `live.tsx`: ห้ามทำลาย guard BUG-011 (เซิร์ฟเวอร์ล่ม → ไม่โชว์เขียวค้าง) และ WS/polling fallback
6. Types ใน `api.ts` ต้องตาม `docs/api_contract_v3.md` ของ P2 — ต้องการ field ใหม่ เปิด Issue `integration` ถึง P2

## 5. สิ่งที่ต้องส่ง
PR พร้อม screenshot ก่อน/หลัง (เก็บใน `artifacts/` หรือแนบใน PR — ไม่ commit ลง `presentation/`), `apps/web/e2e/student_v3.spec.ts`, ผล Playwright, รายการปัญหาจากผู้ลองใช้ 2–3 คน (ถ้าทำ — **ไม่ใช่** user study ที่สมบูรณ์)

## 6. Acceptance tests
```powershell
cd apps\web; npm run build; cd ..\..                                   # TypeScript + build ผ่าน
powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1  # pytest + Playwright ทั้งหมดผ่าน (รวม student_v3)
.venv\Scripts\python scripts\check_ownership.py --owner P3 --base origin/main
```
* เส้นทาง: เลือก เงียบ+ปลั๊ก → เห็นเหตุผล → GroupFit → Wayfinder → SeatCheck → สถานะอัปเดตผ่าน WS โดยไม่ reload
* e2e เดิมต้องผ่าน: `demo.spec.ts`, `reliability.spec.ts` (BUG-011 + journey 0 console error + keyboard), `server_restart.spec.ts`

## 7. เกณฑ์เสร็จ
หน้า Student แสดง source/freshness/สถานะได้ถูกต้องทั้งข้อมูลจำลองและข้อมูล CV-LAB, SeatCheckPanel ถูก integrate, ทุก test ผ่าน, ไม่มีการเปลี่ยน logic ให้ “ผ่านแค่หน้าจอ” ขณะ backend ไม่ตรง

## 8. ข้อกำหนดการรวมระบบ
* รอ contract ของ P2 ก่อนเปลี่ยน types · รอ PR-A ของ P4 ก่อน PR-B
* `live.tsx`, `package.json`/lock ต้องให้ P4 approve · `CvLab.tsx` ต้องให้ P1 approve เรื่องข้อมูล CV
* หลัง merge P4 รัน regression บน main

## Claude Code prompt (คัดลอกไปใช้)
```text
We are working on an EXISTING Smart Library NEXT application (shared repo SmartLibrary-NEXT). Do not rebuild the frontend.
I am PERSON 3 (Student Frontend / Floor Map / StudyMatch / GroupFit / Wayfinder). My branch is feature/v3-student.

Before changing anything:
1. Run `git status`, `git branch --show-current`; switch to feature/v3-student; `git fetch origin` and merge origin/main.
2. Read docs/team_v3/TEAM_ONBOARDING_TH.md, docs/team_v3/tasks/P3_STUDENT_TASK_GUIDE_TH.md, docs/team_v3/OWNERSHIP_MAP.csv,
   docs/team_v3/02_INTEGRATION_CONTRACT.md and (if present) docs/api_contract_v3.md.
3. Inspect the real code: apps/web/src/App.tsx, api.ts, live.tsx (WebSocket/polling + BUG-011 freshness guard), labels.ts,
   pages/StudentPage.tsx, components/FloorMap.tsx, SeatDetail.tsx (currently contains the SeatCheck form), StudyMatch.tsx,
   and apps/web/e2e/*.spec.ts (data-testid values the tests rely on). Confirm every path exists.
4. Start the app (scripts\start_demo_windows.ps1) and run scripts\run_tests_windows.ps1; report the exact baseline result.

Rules: modify ONLY files I own (see my task guide). Do not edit StaffConsole.tsx, ScenarioLab.tsx, SeatCheckPanel.tsx, other
e2e specs, playwright.config.ts, services/**, cv/** or frozen V2 files. If the API must change, STOP and open a cross-owner
request to Person 2. The UI must not compute seat state itself or show stale/unknown/offline/pending seats as available;
keep the BUG-011 guard and existing data-testid attributes. Never label simulated seats as real CV; no fake percentages.

Implement my task guide items, add apps/web/e2e/student_v3.spec.ts, run npm run build + the full test script, and
`scripts\check_ownership.py --owner P3 --base origin/main`. Report exact results with before/after screenshots saved under
artifacts/. Deliver a PR description using .github/pull_request_template.md. Do not merge to main.
```
