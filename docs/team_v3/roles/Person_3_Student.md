# PERSON 3 — Student Frontend / StudyMatch / Wayfinder Owner

**ความรับผิดชอบ:** UX นักศึกษา — ค้นหา/เลือก/เข้าใจสถานะ, ไม่ทำนายข้อมูลเองจากหน้าเว็บ.

**ไฟล์หลัก**: `apps/web/src/pages/StudentPage.tsx`, `apps/web/src/components/FloorMap.tsx`, `apps/web/src/components/SeatDetail.tsx`, `apps/web/src/components/StudyMatch.tsx`, `apps/web/src/api.ts`, `apps/web/src/labels.ts` (ขออนุมัติก่อนแก้ `App.tsx`). เพิ่ม `apps/web/e2e/student_v3.spec.ts`.

**สิ่งที่มีอยู่:** Floor Map 24 ที่นั่งจำลอง, StudyMatch, GroupFit 2 คน, Wayfinder, SeatWatch.

**งานที่จะทำต่อ:**
1. ปรับ UI ให้แยก `SIMULATION` / ผล CV ทดสอบ / stale / unknown / report pending อ่านง่าย (ไม่ทำสีเขียวค้าง).
2. ตรวจ StudyMatch hard constraints, GroupFit adjacency, route details/เดินจริง vs layout fake; ไม่แสดง % ความแม่นยำปลอม.
3. ปรับ mobile responsiveness, keyboard/tab usability, no-result explanation และ feedback.
4. Person 4 จะสร้าง/ดูแล `SeatCheckPanel.tsx`; **คุณเป็นผู้ import เข้าสู่ `SeatDetail.tsx`** ตาม contract ร่วมกัน.
5. เพิ่ม/รัน browser tests สำหรับ student flow, ระบุ screenshot before/after.

**ต้องส่ง:** screenshots/UI demo, code PR, student e2e test & results, issue list จากผู้ทดลอง 2–3 คนถ้าทำได้ (ไม่อ้างเป็น user study ที่สมบูรณ์).

**ผ่านเมื่อ:** จาก Student page เลือก quiet+power, ดู reason, GroupFit/Wayfinder, ส่ง SeatCheck, เห็น status อัปเดต ผ่าน API/WS จริง แม้ websocket หลุด.
