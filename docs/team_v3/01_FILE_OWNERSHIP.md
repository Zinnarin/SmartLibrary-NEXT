# ขอบเขตหน้าที่และเจ้าของไฟล์ (Proposed V3)

**คำเตือน:** ชื่อ path อ้างจาก V2 implementation report/รายการไฟล์ที่ Claude ระบุ ไม่ใช่การเปิดดู repository ล่าสุด. ให้ `git ls-files` ตรวจ ก่อน commit สัญญา ownership.

| คน | ส่วนที่รับผิดชอบ | แฟ้ม/ไฟล์ที่แก้ได้เป็นหลัก | งานใหม่ที่ต้องส่ง |
|---|---|---|---|
| 1 CV | Detect คน/สิ่งของ, ROI, การทดลอง | `cv/run_cv.py`, `cv/roi.py`, `cv/roi_config.json`, `cv/ROI_CALIBRATION_GUIDE_TH.md`, **ใหม่** `cv/experiments/`, `tests/test_cv_v3.py` | วิดีโอฉากเก้าอี้ที่ได้รับอนุญาต, ground truth, calibration, logs/metrics |
| 2 Backend | State Engine, persistence, API, WS | `services/api/app/{main,db,services,state_engine,trust,evidence,realtime,matching,config,settings,timeutil}.py` (ตรวจ path), **ใหม่** `tests/test_backend_v3.py`, `docs/api_contract_v3.md` | contract ที่ freeze, ingest real CV observation, กฎความปลอดภัย, migration/test |
| 3 Student Web | ผัง/แนะนำที่นั่ง/GroupFit/Wayfinder | `apps/web/src/pages/StudentPage.tsx`, `apps/web/src/components/{FloorMap,SeatDetail,StudyMatch}.tsx`, `apps/web/src/api.ts`, `apps/web/src/labels.ts`, **ใหม่** `apps/web/e2e/student_v3.spec.ts` | UI พร้อมข้อมูลจริง, แสดง source/freshness, usability fixes |
| 4 Staff + QA + Coordinator | SeatCheck, staff review, demo, regression | `apps/web/src/pages/{StaffConsole,ScenarioLab}.tsx`, **ใหม่** `apps/web/src/components/SeatCheckPanel.tsx`, `apps/web/e2e/staff_reliability_v3.spec.ts`, `docs/team_v3/`, `verification/TEAM_V3_*.csv`, `evidence/team_v3/` | workflow staff, audit, tests, evidence, integration notes & demo |

## ไฟล์คาบเกี่ยว — ห้ามแก้พร้อมกัน

1. **`services/api/app/main.py`, `db.py`, `state_engine.py`, `realtime.py`** = คนที่ 2 เป็นเจ้าของ; CV/Staff ขอ API change ด้วย Issue/PR review ไม่แก้เอง.
2. **`apps/web/src/App.tsx` (routing), `apps/web/src/api.ts` (HTTP client), `apps/web/src/labels.ts`** = คนที่ 3 เป็นเจ้าของ; คนที่ 4 ส่ง request/branch ที่ไม่แตะไฟล์หรือให้คนที่ 3 เพิ่ม import.
3. **`SeatDetail.tsx`** = คนที่ 3 เป็นเจ้าของ; ส่วน SeatCheck ที่คนที่ 4 ดูแล ให้ย้ายเป็น `SeatCheckPanel.tsx` แล้วคนที่ 3 รับหน้าที่ import/เรียกใช้. ห้าม 2 คนแก้ `SeatDetail.tsx` พร้อมกัน.
4. **`services/api/app/scenarios.py`/seed script / demo reset** = คนที่ 2 เป็นเจ้าของ; คนที่ 4 เสนอ test cases และ expected outcomes แทน.
5. **`apps/web/src/pages/CvLab.tsx`** = คนที่ 3 ดูแลส่วน UI; คนที่ 1 ส่ง payload/ตัวอย่างและ requirements ไม่แก้ไฟล์ร่วมกัน.
6. **`.github/workflows/*`, `package.json`, lock files, `pytest.ini`, scripts launch/export** = Integration Lead อนุมัติร่วมกับ owner ที่เกี่ยวข้องก่อนเปลี่ยน.
7. **`tests/conftest.py`** = คนที่ 2 ดูแล; คนที่ 1/3/4 สร้าง test ใหม่แยกไฟล์ ห้ามเปลี่ยน fixtures กลางฝ่ายเดียว.
8. **`presentation/*` และรายงานหลัก V2** = freeze เป็นหลักฐานเก่า; สำหรับรอบ V3 สร้างเวอร์ชันใหม่ ไม่เขียนทับ `progress_update_v2.pptx` หรือผลทดสอบเดิม.

## กติกาแก้ไฟล์ข้ามทีม
ส่ง issue รูปแบบ: `ต้องการอะไร / endpoint หรือ component / input-output / เหตุผล / deadline / test case`. เจ้าของไฟล์แก้เองหรือให้ code-owner approve จึง merge ได้.

**คนที่ 4 ไม่จำเป็นต้องเขียน Backend แทนคนที่ 2** แม้เป็นผู้เริ่มต้นและวางสถาปัตยกรรมของต้นแบบ — ให้เป็นผู้ประสานภาพรวม ตรวจคุณภาพ และ owner Staff/QA ตามบทบาทเดิม.
