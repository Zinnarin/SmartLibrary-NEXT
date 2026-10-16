# P3 · 04 — Roadmap การพัฒนา (Student Frontend)

## G0 — Baseline (วันแรก)
- [ ] `git switch feature/v3-student` → `git merge origin/main`
- [ ] `cd apps\web; npm ci; npm run build` → ผ่าน
- [ ] เปิดเซิร์ฟเวอร์ `scripts\start_demo_windows.ps1 -Reset` แล้วรัน `scripts\run_tests_windows.ps1` → บันทึกผลจริง (Playwright 8/8)
- [ ] ⚠ ก่อน PR #16 merge: Playwright เขียนภาพลง `presentation/screenshots/` (FROZEN) → `git restore presentation/screenshots/ evidence/` หลังรัน (อย่า commit)
- [ ] อ่าน `05_INTEGRATION_CONTRACT.md` (C2 + C4) และดู JSON จริงใน `contract_examples/C2__*.json`, `C4__*.json`

## G1 — Contract check
- [ ] เทียบ types ใน `apps/web/src/api.ts` กับสัญญา (และ `docs/api_contract_v3.md` เมื่อ P2 merge) — จดสิ่งที่ขาด/ไม่ตรง
- [ ] approve PR #16 ของ P4 (ไฟล์ `playwright.config.ts` ต้องได้ approval ของคุณ) — ตรวจว่าไม่กระทบ e2e ของคุณ
- [ ] ตกลง props ของ `SeatCheckPanel` กับ P4 (PA-05)

## G2 — Module complete (ทำอิสระ)
- [ ] S1 ป้ายแหล่งข้อมูล + ความสด (#6)
- [ ] S2 มือถือ/คีย์บอร์ด/ข้อความ error
- [ ] S3 ปรับ StudyMatch/GroupFit/Wayfinder
- [ ] S4 PA-08 วาดโซนจาก `/api/layout`
- [ ] S5 `apps/web/e2e/student_v3.spec.ts` (#8)
- [ ] S7 types ตามสัญญา
- [ ] screenshot ก่อน/หลังเก็บใน `artifacts/` (แนบใน PR; ไม่ commit ลง `presentation/`)

## G3 — Integration (P4 นำ)
- [ ] S6 PR-B ใช้ `SeatCheckPanel` หลัง PR-A ของ P4 merge (#7)
- [ ] แก้ตามที่ P4 รายงาน (owner-led) ภายใน 1 วัน
- [ ] ถ้า P2 เพิ่ม field (YELLOW) → ปรับ types/UI ใน PR แยก

## G4–G5 — Stabilize & release
- [ ] แก้บั๊กเท่านั้น; ตรวจทุกหน้าบนมือถือจริง 1 เครื่อง + เดสก์ท็อป
- [ ] screenshot สุดท้ายของทุกหน้าใน `evidence/team_v3/student/` (ติดป้าย SIMULATION ชัดเจน)

## สิ่งที่ทำได้ทันทีโดยไม่ต้องรอใคร
S1, S2, S3, S4, S5 — ใช้ API เดิมทั้งหมด และอยู่ในไฟล์ของคุณ
