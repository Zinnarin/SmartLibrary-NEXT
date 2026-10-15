# SMART LIBRARY NEXT — TEAM SPRINT V3 / START HERE

**สถานะเริ่มต้น:** ใช้ Smart Library NEXT V2 ที่รันได้ตามรายงาน Claude Code เป็น **Shared Baseline** ไม่ใช่ให้แต่ละคนสร้างโปรเจกต์ใหม่ 4 ชุด. รายงานล่าสุดกล่าวว่า pytest 53/53 และ Playwright 8/8 ผ่าน แต่ทีมต้องรัน baseline ซ้ำในเครื่องตัวเองก่อนเริ่มงาน.

**สำคัญ:** ZIP นี้เป็น **ชุดเอกสารแจกงาน/สัญญาการเชื่อมต่อ** ไม่ใช่ Source Code ของโปรเจกต์ V2. ให้เก็บไว้ใน Git Repository ของ V2 (อาจวางภายใต้ `docs/team_v3/`) และตรวจสอบชื่อ path กับโค้ดจริงก่อนยึดเป็นกฎ. เรามีรายงานและสเปกของ V2 แต่ไม่ได้เข้าถึง Git Working Tree จริงของสมาชิก.

## หลักคิด
1. หนึ่ง Repository, หนึ่ง FastAPI, หนึ่งฐานข้อมูลหลัก, หนึ่งแอป — 4 owners ต่าง module.
2. คนที่ 1 = Computer Vision; คนที่ 2 = Backend/Database; คนที่ 3 = Student Frontend; คนที่ 4 = Staff/Quality/Integration Lead (**ผู้ใช้**).
3. ไม่รื้อ V2: แก้/เพิ่มเฉพาะงาน sprint แล้ว merge ด้วย Pull Request (PR).
4. **ห้ามรอจนสุดท้ายค่อยรวม**: freeze API contract ตั้งแต่วันแรก, ตรวจการเชื่อมต่อเป็นระยะ และ merge ทีละ PR.
5. บัค/ผลทดสอบใหม่ต้องมีหลักฐาน. ระบุ `SIMULATION`, `REAL_CV`, `DESIGNED_ONLY` ให้ตรงข้อเท็จจริง. กล้อง/วิดีโอต้องได้รับอนุญาต.

## เริ่มในกลุ่ม
- นัดประชุม kickoff 30–45 นาที ให้ทุกคนดู Demo ปัจจุบัน; ตกลงเป้าหมาย CV 2–4 ที่นั่งทดลอง; ถามก่อนว่า **CiRA CORE เป็นเครื่องมือบังคับของวิชาหรือไม่** (ต้นแบบ V2 ใช้ YOLO11n).
- ผู้ดูแล repo เก็บ V2 snapshot/tag `v2-demo-baseline`, ห้าม commit `.venv/`, `.venv-cv/`, `node_modules/`, DB, secrets หรือคลิปที่มีบุคคลโดยไม่อนุญาต.
- คนที่ 2 freeze schema/Pydantic contract และตัวอย่าง payload จากโค้ดจริง; คนที่ 1/3/4 ทดสอบตาม schema นั้น.
- แจก `roles/Person_*.md` ให้สมาชิกแต่ละคน, อ่าน `01_FILE_OWNERSHIP.md`, `02_INTEGRATION_CONTRACT.md`, `03_SPRINT_PLAN.md`, `04_MERGE_CHECKLIST.md` ร่วมกัน.

## Definition of Done ร่วมกัน
- ทุก feature มีเจ้าของชัดเจน, ตรวจโค้ด/ทดสอบ/ภาพหลักฐานใน PR
- ระบบ V2 เดิมยังรันได้; regression suite ไม่ถอยหลัง
- P1 ใช้ฉากเก้าอี้จริงที่ได้รับอนุญาตหรือรายงาน blocker; ไม่มีผลความแม่นยำแต่งขึ้น
- P2 รับ event จาก adapter ผ่าน API และบันทึกโดยไม่ซ้ำ/ไม่ย้อนเวลา
- P3 แสดงตำแหน่งและผลสถานะอย่างถูกต้อง พร้อม label source และ freshness
- P4 ทดสอบ workflow Student→SeatCheck→Staff→WebSocket และ failure cases
- รายงานงานเดิม/งานใหม่/ผู้ลงมือ/สิ่งที่ AI ช่วยอย่างโปร่งใส
