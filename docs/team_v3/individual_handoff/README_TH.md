# Individual Handoff Packages — Smart Library NEXT V3

ชุดเอกสารนี้ทำให้สมาชิกแต่ละคน **พัฒนาโมดูลของตัวเองได้อิสระ** โดยยังรวมเป็นระบบเดียวได้ เพราะทุกคนยึด **สัญญาการเชื่อมต่อชุดเดียวกัน** (สกัดจากโค้ด V2 จริงเมื่อ 16 ต.ค. 2569 ที่ commit `edc7903`)
เป็น **เอกสาร** ไม่ใช่ repo สำรอง — โค้ดจริงอยู่ใน `Zinnarin/SmartLibrary-NEXT` (private) เท่านั้น

## โครงสร้าง
| โฟลเดอร์/ไฟล์ | สำหรับ | เนื้อหา |
|---|---|---|
| `P1_COMPUTER_VISION/` | P1 | 01 บริบท · 02 ภารกิจ · 03 โค้ดเดิม+ความเป็นเจ้าของ · 04 roadmap · 05 สัญญา · 06 เกณฑ์ยอมรับ · 07 แม่แบบ CR · 08 checklist ส่งงาน · 09 Claude Code prompt |
| `P2_BACKEND_DATABASE/` | P2 | 9 ไฟล์เดียวกัน |
| `P3_STUDENT_FRONTEND/` | P3 | 9 ไฟล์เดียวกัน |
| `P4_STAFF_QA_INTEGRATION/` | P4 | 9 ไฟล์เดียวกัน |
| `SHARED_V3/` | ทุกคน | 00 ภาพรวม · 01 สถานะ V2 จริง · 02 สถาปัตยกรรม · 03 **สัญญา API ร่วม** · 04 ข้อตกลงการทำงาน (GREEN/YELLOW/RED) · 05 roadmap การรวม · 06 กระบวนการ CR · 07 เกณฑ์ยอมรับสุดท้าย · `contract_examples/` (request/response จริง 57 ไฟล์) |
| `FINAL_INTEGRATION_PLAYBOOK_TH.md` | P4 (ทุกคนอ่านข้อ 1–4) | วิธีรวมระบบ, ลำดับ, smoke tests, adapter, การจัดการความล้มเหลว |
| `VALIDATION_REPORT.md` | P4 | ผลตรวจชุดเอกสารนี้ (paths, ownership, sync, ความลับ) |

ส่วน `05_INTEGRATION_CONTRACT.md` และ `07_CHANGE_REQUEST_TEMPLATE.md` ของแต่ละคน **คัดลอกอัตโนมัติ** จาก `SHARED_V3/03_…` และ `SHARED_V3/06_…` ระหว่างเครื่องหมาย `<!-- SYNC:BEGIN … -->` — **แก้ที่ไฟล์ SHARED แล้วรัน** `.venv\Scripts\python scripts\build_handoff_packages.py --sync` (อย่าแก้ในส่วน SYNC ของแต่ละคนโดยตรง)

## แจกอะไรให้ใคร (P4 ทำ)
| ไฟล์ ZIP (สร้างด้วย `scripts\build_handoff_packages.py --zip` → `artifacts/handoff_v3/`) | ให้ใคร |
|---|---|
| `SmartLibrary_P1_ComputerVision.zip` | P1 |
| `SmartLibrary_P2_Backend.zip` | P2 |
| `SmartLibrary_P3_StudentFrontend.zip` | P3 |
| `SmartLibrary_P4_StaffIntegration.zip` | P4 (ตัวคุณ) |
| `SmartLibrary_V3_Shared_Contracts.zip` | **ทุกคน** (4 คน) |
* ทุกคนได้ **2 ไฟล์**: ZIP ของตัวเอง + ZIP ร่วม
* ZIP ไม่มีโค้ด, token, ฐานข้อมูล, ภาพบุคคล หรือรหัสนักศึกษา — แต่ยังเป็นเอกสารภายในทีม: แจกผ่านช่องทางส่วนตัวของทีม ไม่โพสต์สาธารณะ
* แหล่งจริงคือโฟลเดอร์นี้ใน repo — ถ้าเอกสารเปลี่ยน ให้สร้าง ZIP ใหม่ (ไฟล์ `MANIFEST.txt` ใน ZIP ระบุ commit ที่ใช้สร้าง)

## ลำดับการอ่านสำหรับสมาชิกใหม่
1. `SHARED_V3/00_PROJECT_OVERVIEW_TH.md` → 2. ไฟล์ 01–04 ของตัวเอง → 3. `05_INTEGRATION_CONTRACT.md` ของตัวเอง → 4. `SHARED_V3/04_TEAM_WORKING_AGREEMENT_TH.md` → 5. `06`, `08` ของตัวเอง → 6. วาง `09_CLAUDE_CODE_MASTER_PROMPT.md` ใน Claude Code
ก่อนเริ่มโค้ด อ่าน `docs/team_v3/TEAM_ONBOARDING_TH.md` (clone, ติดตั้ง, เปิดแอป) — ต้องเป็น collaborator ของ repo ก่อน

## ความสัมพันธ์กับเอกสารเดิม
* `docs/team_v3/tasks/P*_TASK_GUIDE_TH.md` = สรุปสั้นรุ่นก่อน (15 ต.ค.) — **ชุดนี้ละเอียดกว่าและมาแทนสำหรับงาน V3**; เนื้อหาไม่ขัดกัน (ownership เดียวกันจาก `OWNERSHIP_MAP.csv`)
* `docs/team_v3/02_INTEGRATION_CONTRACT.md` = ข้อตกลง A–D ต้นฉบับ (ไม่แก้) — สัญญา C0–C4 ในชุดนี้คือรายละเอียดจากโค้ดจริงของข้อตกลงเหล่านั้น
* `docs/api_contract_v3.md` (P2 จะสร้าง) = **สัญญาฉบับทางการ** เมื่อ merge แล้วจะมีผลเหนือ snapshot ใน `SHARED_V3/03_SHARED_API_CONTRACTS.md`
