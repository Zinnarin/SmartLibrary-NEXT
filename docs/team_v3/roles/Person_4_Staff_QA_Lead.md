# PERSON 4 — Staff / Reliability / QA / Integration Lead (คุณ)

**ความรับผิดชอบ:** Staff Console และการพิสูจน์ว่าระบบแก้สถานะผิดได้ปลอดภัย เป็น coordinator/ผู้ตรวจ PR โดย **ไม่ต้องเขียน Backend หรือ Frontend นักศึกษาแทนทุกคน**.

**ไฟล์หลัก**: `apps/web/src/pages/StaffConsole.tsx`, `apps/web/src/pages/ScenarioLab.tsx` (ให้ P2 owner demo APIs), เพิ่ม `apps/web/src/components/SeatCheckPanel.tsx`, `apps/web/e2e/staff_reliability_v3.spec.ts`, `evidence/team_v3/`, `docs/team_v3/`, `verification/TEAM_V3_*.csv`.

**งานที่จะทำต่อ:**
1. นัด kickoff อธิบาย V2 baseline+limitations, freeze contract, ติดตาม status ทุกวัน/ทำ sprint board.
2. ตรวจ Staff Console: report queue, approve/reject reason, override/expiry, audit log, camera health, ID ตรงกัน.
3. รับผิดชอบ SeatCheck UX component ใหม่; ให้ P3 import ไม่แก้ SeatDetail ซ้อนกัน.
4. ทดสอบ BUG-001/BUG-011/BUG-013 regression, server crash/WS fallback/stale, duplicates & report abuse; เขียน tests ใหม่แยกไฟล์.
5. รวม PR ทีละโมดูลกับ code owner; run regression หลัง PR ทุกครั้ง, prepare integrated demo/screenshot/report พร้อม track source=simulation vs CV.
6. เป็นผู้ประสานถามอาจารย์เรื่อง consent/CiRA CORE/พื้นที่จริง, **ไม่อ้างว่าทีมคนอื่นเขียน V2 ถ้ายังไม่ได้ทำจริง**.

**ต้องส่ง:** Staff workflow tests + bug log, merge notes, project board, updated demo runbook, integrated acceptance result, 3-minute presentation update ที่ยืนยันจากหลักฐาน.

**ผ่านเมื่อ:** นักศึกษา report → ticket pending → Staff review + reason + valid override → Student update via WS; server outage ไม่แสดง green ค้าง; tests ผ่าน; merged release มี tagged version และ demo จริง.
