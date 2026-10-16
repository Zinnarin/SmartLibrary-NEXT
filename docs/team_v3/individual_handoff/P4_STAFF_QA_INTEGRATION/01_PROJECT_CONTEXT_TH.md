# P4 · 01 — บริบทโครงการ (Staff, QA & Integration)

> ชุดเอกสารนี้อ่านจบในตัว — ไฟล์ 01–09 ในโฟลเดอร์นี้ + `FINAL_INTEGRATION_PLAYBOOK_TH.md` คือทุกอย่างที่ P4 ต้องใช้ (เอกสารร่วมฉบับเต็มอยู่ใน `docs/team_v3/individual_handoff/SHARED_V3/`)

## 1. Smart Library NEXT คืออะไร
ระบบแสดงสถานะที่นั่งห้องสมุด **เท่าที่หลักฐานยืนยันได้** (ไม่แน่ใจ = Unknown/Stale ไม่ใช่ "ว่าง") ต่อยอดจากต้นแบบ V2 ที่รันได้จริง (repo private `Zinnarin/SmartLibrary-NEXT`, tag `v2-demo-baseline`)

## 2. เป้าหมายร่วม V3 และส่วนของ P4
1) หลักฐานภาพ (P1) · 2) Seat State Engine (P2) · 3) เก็บข้อมูล (P2) · 4) เว็บนักศึกษา (P3) · 5) ค้นหา/แนะนำ (P3+P2) · **6) workflow SeatCheck ← คุณ (ร่วมกับ P3/P2)** · **7) เจ้าหน้าที่ตรวจและจัดการรายงาน ← คุณ** · **8) ทดสอบข้อมูลเก่า/กล้องหาย/ข้อผิดพลาด ← คุณ (QA)** · 9) แยก SIMULATION/CV (ทุกคน — คุณตรวจ) · **10) รันเป็นระบบเดียว ← คุณ (Integration)**

## 3. ตำแหน่งของ P4 ในระบบ
```
              ┌──────────── Integration (คุณ): PR → trial merge → regression → merge → evidence → release ────────────┐
P1 CV ─C1─► P2 Backend ─C2─► P3 Student ─C4 (SeatCheck)─► [P2 API] ─C3─► Staff Console (คุณ) ─override─► WS ─► P3 Student
              └── QA (คุณ): contract tests, e2e, fault injection (กล้องหาย/เซิร์ฟเวอร์ล่ม), test-artifact isolation ──┘
```

## 4. สถานะส่วนของคุณวันนี้ (ตรวจ 16 ต.ค. 2569)
| เรื่อง | สถานะ |
|---|---|
| Staff Console: รายงานรอตรวจ + ตัดสินพร้อมเหตุผล + override (unavailable/maintenance/unknown + หมดอายุ) + ตารางที่นั่ง + audit log | **IMPLEMENTED** (`StaffConsole.tsx`) |
| ค่าเริ่มต้น override ตอนยืนยันรายงาน "มีคนนั่ง" | **ต้องแก้ (#11)** — ยังเป็น `maintenance` (ผิดความหมาย; ข้อตกลง C ให้ใช้ `unknown`) |
| SeatCheck form | อยู่ใน `SeatDetail.tsx` ของ P3 — คุณต้องแยกเป็น `SeatCheckPanel.tsx` (PR-A, #10) |
| Staff identity | demo gate token เดียว, actor `staff-demo` เสมอ (ไม่ใช่ auth จริง) |
| e2e (Playwright + Edge) 8 specs, `tests/test_reliability.py` 7 tests | **IMPLEMENTED**, ผ่านทั้งหมด |
| Test artifacts เขียนทับหลักฐาน V2 | **แก้แล้วบน `feature/v3-staff-qa` (PR #16)** — CI เขียว, **ยังไม่ merge** (รอ P3 approve `playwright.config.ts`) |
| CI | pytest + ownership audit + web build (ไม่มี Playwright ใน CI) — เขียวทุก run |
| Branch protection | ใช้ไม่ได้บน private repo แผนฟรี (HTTP 403) → ใช้กติกา manual: P4 merge คนเดียว (#13) |
| GitHub collaborators | P1–P3 **ยังไม่ได้เชิญ** (รอ username) |
| สัญญา C0–C4 | สกัดจากโค้ดแล้ว + ตัวอย่าง request/response จริง 57 ไฟล์ (`SHARED_V3/contract_examples/`) |
| ข้อบกพร่องที่พบระหว่างสกัดสัญญา | timestamp ผิดรูปแบบที่ ingest → HTTP 500 (PA-02, เจ้าของ P2) |

## 5. หลักการทำงานของ P4 (สำคัญ)
* **ไม่เขียนทับงานภายในของเพื่อน** แม้จะแก้ได้เร็วกว่า — แจ้งเจ้าของ (owner-led fix) หรือทำ **adapter** ใน `integration/**` เมื่อจำเป็น
* **คุณเป็น quality gate:** ไม่ merge อะไรที่ CI แดง, ownership `BLOCK`, ขาด approval, หรือ regression ไม่ผ่าน
* **คุณประสานงานภายนอก:** ขออนุญาตกล้อง/ฟุตเทจ/ผังจริง (#14) และถาม CiRA CORE (#15) กับอาจารย์
* **ความจริงมาก่อน:** หลักฐานทุกชิ้นต้องมาจากการรันจริง; SIMULATION ต้องติดป้าย; ความแม่นยำ CV จริงไม่มีจนกว่าจะวัด
