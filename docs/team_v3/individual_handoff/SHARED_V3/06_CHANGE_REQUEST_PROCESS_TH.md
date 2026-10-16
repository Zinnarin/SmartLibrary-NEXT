# 06 — กระบวนการขอเปลี่ยนแปลง (Change Request)

## เมื่อไหร่ต้องเขียน CR
* งาน 🟡 YELLOW หรือ 🔴 RED ตาม `04_TEAM_WORKING_AGREEMENT_TH.md` — เช่น เพิ่ม/เปลี่ยน endpoint, field, enum, env, ตาราง DB, seat/กล้องใหม่, ไฟล์ที่ต้องมี approval ร่วม, dependency ใหม่
* งาน 🟢 GREEN **ไม่ต้อง** เขียน CR

## ขั้นตอน (ใช้เวลาน้อย)
1. เปิด GitHub Issue ชื่อ `[CR][P#] <สรุปสั้น>` + label `integration` (+ label ของคนที่ได้รับผลกระทบ) แล้ววาง template ด้านล่าง
2. **ยังไม่ต้องเขียนโค้ดที่กระทบคนอื่น** จนกว่า P4 จะตอบ (ทดลองใน branch ส่วนตัวได้ แต่ห้ามเปิด PR เข้า main)
3. P4 จัดระดับ (YELLOW/RED) และตอบภายใน 1 วันทำการ; RED ต้องได้ 👍 จากทั้ง 4 คนใน Issue
4. เมื่ออนุมัติ: ทำงาน + test + อัปเดตสัญญา (`docs/api_contract_v3.md` และ `contract_examples/` ถ้าเกี่ยว) ใน PR เดียวกัน และอ้าง `Closes #<CR>`
5. ฝั่งที่ได้รับผลกระทบ review/approve PR · P4 รวมตาม `FINAL_INTEGRATION_PLAYBOOK_TH.md`
6. ถ้าถูกปฏิเสธ: P4 ต้องให้เหตุผลและทางเลือก (เช่น adapter, ทำเป็น optional, เลื่อนไปหลังนำเสนอ)

<!-- SECTION:TEMPLATE -->
## แม่แบบ Change Request (คัดลอกทั้งกล่อง)

```markdown
### CR: <ชื่อสั้น>
- ผู้เสนอ: P_ (<บทบาท>) · วันที่: YYYY-MM-DD · ระดับที่คิดว่าเป็น: GREEN / YELLOW / RED
- สัญญาที่เกี่ยว: C0 / C1 / C1b / C1c / C2 / C3 / C4 / PA-__ (ระบุ)

1. Proposed change (จะเปลี่ยนอะไร):
   -
2. Reason (ทำไมต้องเปลี่ยน / ปัญหาที่พบ พร้อมหลักฐาน):
   -
3. Files affected (path จริง + เจ้าของไฟล์):
   - `path/to/file` — owner P_
4. API or database impact:
   - Endpoint/field/enum/env/table ที่เพิ่มหรือเปลี่ยน:
   - เข้ากันได้ย้อนหลังไหม (client เดิมยังทำงานโดยไม่แก้): ใช่ / ไม่ — ถ้าไม่ ต้องมีแผน migration
   - ตัวอย่าง request/response ก่อน–หลัง (JSON จริงหรือร่าง ระบุชัด):
5. Expected benefit (วัดได้อย่างไร):
   -
6. Integration risk (อะไรอาจพัง / test ไหนอาจแดง / rollback ทำอย่างไร):
   -
7. Required support from others (ใครต้องทำอะไร ภายในเมื่อไหร่):
   - P_: 
8. Test plan (test ที่จะเพิ่ม/ต้องผ่าน + คำสั่ง):
   -
```
<!-- /SECTION:TEMPLATE -->

## ตัวอย่าง CR ที่รู้แล้วว่าต้องมี (จาก `03_SHARED_API_CONTRACTS.md` ส่วน PA)
| CR | ระดับ | ผู้เสนอ → ผู้ได้รับผลกระทบ |
|---|---|---|
| PA-01 `SL_CV_EVIDENCE_DIR` (issue #3) | YELLOW | P1/P2 → P3 (CV Lab) |
| PA-02 422 แทน 500 เมื่อ timestamp เสีย | GREEN (bug fix) — แจ้ง P1 | P2 |
| PA-03 ลงทะเบียนที่นั่ง/กล้อง CV จริงให้ขึ้นผังนักศึกษา | **RED** | P1+P2 → P3, P4 |
| PA-05 props ของ `SeatCheckPanel` | YELLOW | P4 → P3 |
| PA-07 `response_model` ใน OpenAPI | YELLOW | P2 → ทุกคน |
| PA-08 วาดโซนจาก `/api/layout` | GREEN (ไฟล์ของ P3) แต่จำเป็นก่อน PA-03 | P3 |
