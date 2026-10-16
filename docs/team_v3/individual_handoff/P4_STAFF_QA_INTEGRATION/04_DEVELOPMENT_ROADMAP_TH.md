# P4 · 04 — Roadmap การพัฒนาและการรวมระบบ (Staff, QA & Integration)

> คุณมีสองบทบาท: **นักพัฒนา** (Staff/SeatCheck/QA) และ **ผู้รวมระบบ** — งานรวมระบบทำตาม `FINAL_INTEGRATION_PLAYBOOK_TH.md`

## G0 — Kickoff & baseline
- [ ] แจก ZIP ให้แต่ละคน + ZIP ร่วม (ดู `docs/team_v3/individual_handoff/README_TH.md`)
- [ ] เชิญ collaborator เมื่อได้ username (สิทธิ์ write ไม่ใช่ admin) และตรวจ `/invitations`
- [ ] ขอผล baseline จริงจากทุกคน (pytest 53, build, Playwright 8) — บันทึกใน Issue
- [ ] กำหนดวันที่จริงของ G1–G5 และประกาศในแชท/Issue
- [ ] ส่งคำถาม #14 (อนุญาตกล้อง/ฟุตเทจ/ผังจริง) และ #15 (CiRA CORE) ถึงอาจารย์

## G1 — Contract freeze + smoke
- [ ] review PR สัญญาของ P2 (`docs/api_contract_v3.md`) เทียบกับ `SHARED_V3/03_SHARED_API_CONTRACTS.md` + `SHARED_V3/contract_examples/`
- [ ] Q1 merge PR #16 หลัง P3 approve → รัน `run_tests_windows.ps1` บน main → `frozen-clean: OK`
- [ ] Q2 smoke C1–C4 ตาม playbook ข้อ 5 บน main
- [ ] ตอบ CR ทุกอันภายใน 1 วันทำการ (จัดระดับ GREEN/YELLOW/RED)

## G2 — งานพัฒนาของคุณ (ขนานกับคนอื่น)
- [ ] Q3 PR-A `SeatCheckPanel.tsx` (ตกลง props กับ P3 ก่อน)
- [ ] Q4 override `unknown` เป็นค่าเริ่มต้น (#11)
- [ ] Q5 `staff_reliability_v3.spec.ts` (#12)
- [ ] Q6 `tests/test_contract_v3.py`
- [ ] Q7 ปรับ Staff operations (แท็บอุปกรณ์, คิวรายงาน)
- [ ] Q8 `integration/smoke/` (+ adapter เฉพาะเมื่อจำเป็น)

## G3 — Integration (คุณนำ)
- [ ] รวมตามลำดับใน playbook ข้อ 3, ทีละ PR, บน `integration/v3-rN`
- [ ] regression เต็มหลังทุก PR + บันทึก `evidence/team_v3/integration/INTEGRATION_LOG.md`
- [ ] โมดูลที่ผิดสัญญา → Issue ถึงเจ้าของ (ข้อความแม่แบบใน playbook ข้อ 7) — ไม่แก้แทน
- [ ] Q9 CODEOWNERS เมื่อได้ username ครบ

## G4 — Stabilize
- [ ] ประกาศ feature freeze 24 ชม. ก่อนนำเสนอ
- [ ] regression บนเครื่องที่ใช้นำเสนอ + fault injection (กล้องหาย, ฆ่าเซิร์ฟเวอร์, WS ถูกบล็อก)
- [ ] Q11 runbook V3 + สไลด์ `presentation/v3/` + ซ้อมจับเวลา

## G5 — Release
- [ ] Q10 `verification/TEAM_V3_ACCEPTANCE.csv` ครบทุก FA (PASS/FAIL/BLOCKED + path หลักฐาน)
- [ ] `evidence/team_v3/final/` (junit, playwright json, screenshot, metrics CV ถ้ามี, commit hash)
- [ ] release notes (REAL / SIMULATED / PARTIAL / BLOCKED) + เครดิตใครทำอะไร/AI ช่วยตรงไหน
- [ ] ทีมอนุมัติ → tag `v3-integrated-demo` (push ตามสิทธิ์เจ้าของ repo)
