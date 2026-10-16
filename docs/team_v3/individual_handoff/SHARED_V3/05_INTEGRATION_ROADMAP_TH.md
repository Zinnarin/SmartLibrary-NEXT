# 05 — Roadmap การรวมระบบ (Integration Roadmap)

> วันที่จริงของแต่ละ Gate ให้ P4 กำหนดในแชทกลุ่ม/Issue ตามตารางเรียน (แผนต้นฉบับ `docs/team_v3/03_SPRINT_PLAN.md` ใช้ 5–7 วัน) — เอกสารนี้กำหนด **ลำดับและเงื่อนไขผ่าน** ไม่ได้กำหนดวัน

## Gates

| Gate | ชื่อ | ทุกคนต้องมี | P4 ตรวจอะไร | ผ่านเมื่อ |
|---|---|---|---|---|
| **G0** | Baseline | clone + เปิดแอป + รัน baseline (`pytest` 53 passed, `npm run build`) บนเครื่องตัวเอง; อ่าน package ของตัวเอง | ทุกคนรายงานผล baseline จริงใน Issue/แชท | 4/4 คนรันได้ |
| **G1** | Contract freeze + smoke | **P2:** `docs/api_contract_v3.md` (PR แรกของทีม) จากสัญญาใน `03_…` · **P1:** ส่ง sample payload 1 เฟรมเข้า CV-LAB ผ่าน API ได้ `applied` · **P3/P4:** ยืนยันว่า client ใช้ field ตามสัญญา | contract PR ผ่าน review P1/P3/P4; smoke C1–C4 ผ่าน (`integration/smoke/` เมื่อมี หรือคำสั่งใน playbook) | สัญญา merge แล้ว; CR ที่ค้างมีเจ้าของ |
| **G2** | Module complete (แยกกัน) | งานหลักของแต่ละคน + test ของตัวเอง (`test_cv_v3.py`, `test_backend_v3.py`, `student_v3.spec.ts`, `staff_reliability_v3.spec.ts`) ผ่านบน branch ตัวเอง | PR แต่ละอัน: CI + ownership + contract tests | PR พร้อม review |
| **G3** | Integration | — | P4 รวมทีละ PR บน branch `integration/v3-rN` ตามลำดับใน playbook, รัน regression เต็มหลังทุก PR | ทุก PR ที่พร้อม merge เข้า `main`; ที่ไม่ผ่านกลับไปให้เจ้าของแก้ |
| **G4** | Stabilize (feature freeze) | แก้บั๊กเท่านั้น (owner-led) | regression เต็มบนเครื่องที่ใช้นำเสนอ; ไม่รับฟีเจอร์ใหม่ 24 ชม. ก่อนนำเสนอ | FA-01…FA-24 ผ่าน |
| **G5** | Release | หลักฐานของตัวเองใน `evidence/team_v3/<role>/` | `07_FINAL_ACCEPTANCE_CRITERIA.md` ครบ, tag `v3-integrated-demo`, release notes | ทีมอนุมัติ |

## ลำดับการ merge (dependencies)
```
P2 contract (docs/api_contract_v3.md)                         ← ทุกคนรอข้อนี้ก่อนเปลี่ยน payload/types
  ├─> P4 artifact isolation (PR #16, พร้อมแล้ว รอ P3 approve playwright.config.ts)
  ├─> P2 backend hardening (PA-02, PA-01, test_backend_v3)     ← P1 ต้องการ PA-01 ก่อนย้ายผล CV
  │     └─> P1 CV adapter/experiments (test_cv_v3, payload ตาม C1)
  ├─> P4 PR-A SeatCheckPanel.tsx (PA-05)  ──> P3 PR-B ใช้ SeatCheckPanel ใน SeatDetail.tsx
  ├─> P3 UI (source/freshness, mobile, PA-08 โซนจาก /api/layout)
  └─> P4 staff (override unknown #11, staff_reliability_v3.spec.ts)
RED (ถ้าทีมอนุมัติ): PA-03 ที่นั่ง CV จริงบนผัง = P2 (registry) → P1 (ROI/seat IDs) → P3 (แสดงผล) → P4 (e2e)
```

## งานต่อคนต่อ Gate (สรุป — รายละเอียดใน `04_DEVELOPMENT_ROADMAP_TH.md` ของแต่ละคน)
| | G1 | G2 | G3–G4 |
|---|---|---|---|
| P1 | sample payload → `applied`; ขออนุญาตฉากจริง (#14); ถาม CiRA (#15) | ROI/ฉากจริงหรือคลิปที่ได้รับอนุญาต, evidence record (PA-04), `test_cv_v3.py` | แก้ตามผลรวมระบบ; metrics (FA-30) หรือ BLOCKED (FA-31) |
| P2 | `api_contract_v3.md` | PA-02, PA-01, `test_backend_v3.py`, (PA-07) | ตรวจ log ingest ของ P1, แก้บั๊ก contract |
| P3 | ยืนยัน types ตามสัญญา | UI source/freshness/mobile, `student_v3.spec.ts`, PA-08 | PR-B SeatCheckPanel, แก้บั๊ก UI |
| P4 | smoke C1–C4, merge PR #16 | PR-A, #11, `staff_reliability_v3.spec.ts`, `test_contract_v3.py` | รวมระบบ, regression, หลักฐาน, release |
