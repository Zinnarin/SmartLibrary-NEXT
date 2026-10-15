# Task Guide — PERSON 4: SeatCheck / Staff Console / Reliability / Testing / Integration Coordination
Branch: **`feature/v3-staff-qa`** · Labels: `person-4-qa`, `integration` · ผู้ merge เข้า `main`: P4

## 1. เป้าหมาย
พิสูจน์ว่าระบบ **แก้สถานะที่ผิดได้อย่างปลอดภัย** (Student → SeatCheck → Staff → WebSocket) และเป็น **quality gate** ของทีม: ทุก PR ผ่าน ownership check, CI, regression ในเครื่อง ก่อน merge — โดยไม่เขียน Backend/Student UI แทนคนอื่น

## 2. ไฟล์ที่เป็นเจ้าของ
`apps/web/src/pages/StaffConsole.tsx`, `pages/ScenarioLab.tsx` (+P2 approve), **ใหม่** `components/SeatCheckPanel.tsx` (+P3 approve), `apps/web/e2e/*` (ยกเว้น `student_v3.spec.ts`) รวม **ใหม่** `staff_reliability_v3.spec.ts` และ `artifacts.ts`, `apps/web/playwright.config.ts` (+P3), `tests/test_reliability.py` (+P2), `tests/test_artifact_isolation.py`, `scripts/*`, `pytest.ini` (+P2), `.github/*`, `.gitignore`, `.gitattributes`, `README.md`, `docs/team_v3/*`, `docs/DEMO_RUNBOOK_TH.md`, `evidence/team_v3/*`, `verification/TEAM_V3_*`, `presentation/v3/*`

## 3. ไฟล์ที่ห้ามแก้
`services/**` (P2 — รวม scenarios/seed: เสนอ test case ให้ P2 แทน), `cv/**` (P1), หน้า/คอมโพเนนต์ Student (`StudentPage`, `FloorMap`, `SeatDetail`, `StudyMatch`, `App.tsx`, `api.ts`, `labels.ts`, `live.tsx` — review ได้ แต่ P3 เป็นคนแก้), FROZEN V2 (`evidence/*`, `presentation/*`, `verification/*`, `reference/*`, spec ใน `docs/*`)

## 4. ฟังก์ชันที่ต้องทำ
1. ✅ **แยก test artifact ออกจากหลักฐาน V2** — ทำแล้วบน branch นี้ (commit “P4: isolate test/tool artifacts…”): ผลทดสอบไป `artifacts/`, มี `--frozen-clean` + `tests/test_artifact_isolation.py` (17 checks) → เปิด PR, ให้ P3 approve `playwright.config.ts`, merge เมื่อ CI เขียว
2. **PR-A `SeatCheckPanel.tsx`:** ย้ายตรรกะฟอร์ม SeatCheck จาก `SeatDetail.tsx` (ของ P3) มาเป็นคอมโพเนนต์ใหม่ พฤติกรรมเดิม, `data-testid` เดิม — ยังไม่มีใครเรียกใช้ → merge ได้โดยไม่กระทบ; จากนั้น P3 ทำ PR-B
3. **ความหมายของ override:** เมื่อยืนยันรายงาน “มีคนนั่ง” ปัจจุบัน default เป็น Maintenance (ความหมายไม่ตรง) → เปลี่ยน default ในคอนโซลเป็น `unknown` (รอตรวจ) ซึ่ง API รองรับอยู่แล้ว; ปรับข้อความ UI ให้ตรงความหมาย
4. **`staff_reliability_v3.spec.ts`:** report → pending → staff review + เหตุผล → override → Student อัปเดตผ่าน WS; รายงานซ้ำ/rate-limit; staff token ผิด; override หมดอายุ; เซิร์ฟเวอร์ล่ม → ไม่โชว์เขียวค้าง
5. **Merge gate:** หลังทุก PR ที่ merge รัน `scripts\run_tests_windows.ps1` บน `main` → สรุปใน `evidence/team_v3/` และ `verification/TEAM_V3_ACCEPTANCE.csv`
6. **ประสานงาน:** sprint board/Issues, ถามอาจารย์เรื่อง consent/พื้นที่จริง/CiRA CORE, ทำ runbook + สไลด์ V3 ใหม่ใน `presentation/v3/` (ห้ามเขียนทับ V2)

## 5. สิ่งที่ต้องส่ง
PR artifact isolation, PR-A SeatCheckPanel, `staff_reliability_v3.spec.ts` + ผล, merge notes + regression log ต่อ PR, `verification/TEAM_V3_ACCEPTANCE.csv`, runbook V3, สไลด์/สคริปต์ V3 ที่ทุกตัวเลขมาจากหลักฐาน, รายงาน “ใครทำอะไร / AI ช่วยตรงไหน”

## 6. Acceptance tests
```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1   # pytest + Playwright + frozen-clean ต้อง exit 0
.venv\Scripts\python scripts\check_ownership.py --audit                    # ทุกไฟล์มีเจ้าของ
.venv\Scripts\python scripts\check_ownership.py --owner P4 --base origin/main
git status                                                                 # ไม่มีไฟล์ใน evidence/ presentation/ (V2) เปลี่ยน
```
* BUG-001 / BUG-011 / BUG-013 regression ต้องผ่านทุกครั้ง · journey 0 console error

## 7. เกณฑ์เสร็จ
นักศึกษารายงาน → ticket pending → staff ตรวจ + เหตุผล + override ที่ความหมายถูกต้อง → Student อัปเดตผ่าน WS; เซิร์ฟเวอร์ล่มไม่โชว์เขียวค้าง; ทุก test ผ่าน; release ติด tag `v3-integrated-demo` และเดโมรันได้จริง

## 8. ข้อกำหนดการรวมระบบ
* ลำดับ merge: contract P2 → adapter P1 → backend P2 → UI P3 → Staff/QA P4 · merge ทีละ PR, regression หลังทุก PR
* ใช้ Squash and merge; ห้าม merge PR ที่ CI แดงหรือมี `BLOCK` จาก ownership check; `REVIEW` ต้องมี approval ของเจ้าของ
* ถ้า regression พัง: revert เฉพาะ PR นั้น ไม่แก้สด ๆ บน main
* ห้ามอ้างว่าเพื่อนเขียน V2 ถ้าไม่ได้ทำจริง; ระบุ SIMULATION / REAL_CV / DESIGNED_ONLY ให้ตรง

## Claude Code prompt (คัดลอกไปใช้)
```text
We are working on an EXISTING Smart Library NEXT application (shared repo SmartLibrary-NEXT). Do not rebuild or redesign it.
I am PERSON 4 (SeatCheck / Staff Console / Reliability / Testing / Integration coordinator). My branch is feature/v3-staff-qa.

Before changing anything:
1. Run `git status`, `git branch --show-current`; switch to feature/v3-staff-qa; `git fetch origin` and merge origin/main.
2. Read docs/team_v3/TEAM_ONBOARDING_TH.md, docs/team_v3/tasks/P4_STAFF_QA_TASK_GUIDE_TH.md, docs/team_v3/OWNERSHIP_MAP.csv,
   docs/team_v3/04_MERGE_CHECKLIST.md, docs/team_v3/02_INTEGRATION_CONTRACT.md and evidence/FINAL_DEMO_READINESS.md.
3. Inspect the real code: apps/web/src/pages/StaffConsole.tsx, ScenarioLab.tsx, components/SeatDetail.tsx (SeatCheck form today),
   apps/web/e2e/*.spec.ts, apps/web/e2e/artifacts.ts, playwright.config.ts, scripts/run_tests_windows.ps1,
   scripts/check_ownership.py, and the /api/seat-reports + /api/admin/* handlers in services/api/app/main.py (read-only).
4. Start the app (scripts\start_demo_windows.ps1) and run scripts\run_tests_windows.ps1; report the exact baseline result.

Rules: modify ONLY files I own (see my task guide). Do not edit services/**, cv/** or Student UI files (SeatDetail.tsx is
Person 3's: create SeatCheckPanel.tsx and let Person 3 import it). Never modify frozen V2 files (evidence/*, presentation/*,
verification/*); test output goes to artifacts/ and curated evidence to evidence/team_v3/. Do not weaken tests or CI to make
them pass; never mark a test PASS without running it; never present simulated seats as real CV.

Implement my task guide items one PR at a time, add tests, run the full test script (must end with frozen-clean OK) and
`scripts\check_ownership.py --owner P4 --base origin/main`. Report exact results and a PR description using
.github/pull_request_template.md. As integration coordinator, review other members' PRs against 04_MERGE_CHECKLIST.md;
only merge to main after CI is green, ownership approvals exist and the local regression passes.
```
