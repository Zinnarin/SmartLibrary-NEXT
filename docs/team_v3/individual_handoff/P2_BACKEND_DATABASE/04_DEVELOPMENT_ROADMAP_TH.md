# P2 · 04 — Roadmap การพัฒนา (Backend & Database)

> คุณเป็น **ทางผ่านวิกฤต (critical path)** ของทีม: สัญญา `docs/api_contract_v3.md` ต้อง merge ก่อนใครเปลี่ยน payload/types

## G0 — Baseline (วันแรก)
- [ ] `git switch feature/v3-backend` → `git merge origin/main`
- [ ] `.venv\Scripts\python -m pytest -q` → บันทึกผลจริง (ควร 53 passed)
- [ ] เปิดแอป `scripts\start_demo_windows.ps1 -Reset` และลองทุกหน้า
- [ ] อ่าน `05_INTEGRATION_CONTRACT.md` ทั้งหมด + ดู `contract_examples/` (response จริงจากโค้ดวันนี้)

## G1 — Contract freeze (เร็วที่สุด เพราะทุกคนรอ)
- [ ] B1 `docs/api_contract_v3.md`: เริ่มจากสัญญา snapshot (C0–C4) → ตรวจทุก route กับโค้ดอีกครั้ง → ใส่ตัวอย่าง JSON จริง → test ที่ยืนยันตัวอย่าง (seat, recommendation, ingest อย่างน้อย)
- [ ] เปิด PR และขอ review จาก P1, P3, P4 (ไฟล์นี้ต้องมี approval ทั้งสาม)
- [ ] ตอบ CR ที่เกี่ยวกับ backend (PA-01 จาก P1, PA-05 ไม่เกี่ยว API)

## G2 — Module complete
- [ ] B2 PA-02 (422 แทน 500) + test
- [ ] B3 `tests/test_backend_v3.py` ครบรายการใน `02`
- [ ] B4 PA-01 `SL_CV_EVIDENCE_DIR` (หลังตกลงกับ P1)
- [ ] B5 migration แบบเบา (ถ้าจะเปลี่ยน schema ใด ๆ ต้องทำก่อน)
- [ ] B6 test pruning + วัดประสิทธิภาพ `seat_views`/WS ด้วยตัวเลขจริง
- [ ] B7 `response_model` (ถ้าทำ) — contract tests ต้องยืนยันว่า JSON ไม่เปลี่ยน
- [ ] ทุก PR: อัปเดต `docs/api_contract_v3.md` + `contract_examples/` ถ้าเกี่ยว

## G3 — Integration (P4 นำ)
- [ ] ตรวจ log ingest จากการทดลองของ P1 (event ที่ `applied`/`late`/`duplicate`, error) และยืนยันใน Issue
- [ ] แก้บั๊กสัญญาที่ P4 รายงาน (owner-led) ภายใน 1 วัน
- [ ] ถ้าทีมอนุมัติ PA-03 (RED): ออกแบบ registry ที่นั่ง/กล้องจริง + migration + rollback → P1 ROI → P3 แสดงผล → P4 e2e

## G4–G5 — Stabilize & release
- [ ] แก้บั๊กเท่านั้น; ไม่เปลี่ยนสัญญาหลัง feature freeze
- [ ] หลักฐานใน `evidence/team_v3/backend/` (ผล test, ตัวเลขประสิทธิภาพ) + สรุปการเปลี่ยนสัญญาทั้งหมดของ V3

## สิ่งที่ทำได้ทันทีโดยไม่ต้องรอใคร
B1, B2, B3, B5, B6 — ทั้งหมดอยู่ใน `services/**`, `tests/test_backend_v3.py`, `docs/api_contract_v3.md` ของคุณ
