# Checklist รวมระบบ — Person 4 (คุณเป็น coordinator)

## ตั้ง Git แบบปลอดภัย
1. ในโฟลเดอร์ **V2 ที่รันได้จริง** ตรวจ `git status`, `git ls-files`, ตรวจ `.gitignore` ไม่ให้มี `.env`, tokens, `.venv/`, `.venv-cv/`, `node_modules/`, DB จริง, private videos, screenshots sensitive.
2. หากยังไม่ใช้ Git ให้ initialize จากไฟล์โค้ด V2 ภายใต้การอนุมัติของทีมและ commit/tag baseline; สร้าง repository ส่วนตัวของกลุ่ม แล้วเชิญเพื่อน.
3. เพื่อนแต่ละคน **clone คนละเครื่อง/โฟลเดอร์**, branch ตัวเองจาก `main`, ห้ามแก้ folder เดียวกันบน cloud sync แบบสด.
4. ตัวอย่างชื่อ branch: `feature/v3-cv`, `feature/v3-backend`, `feature/v3-student`, `feature/v3-staff-qa`. ห้าม push ขึ้น main ตรง.

## ก่อนทุก PR
- [ ] เปลี่ยนเฉพาะไฟล์ที่ถือ ownership หรือมี approval จาก owner
- [ ] อธิบายว่าสิ่งใดใหม่/สิ่งใดเป็นของ V2 อยู่แล้ว
- [ ] Tests ที่เกี่ยวข้องผ่าน; แนบคำสั่ง, console log, screenshot ที่ไม่เปิดข้อมูลส่วนบุคคล
- [ ] ไม่ทำ source simulation ดูเหมือน CV จริง
- [ ] ไม่เปลี่ยน `/api/*` schema โดยไม่อัปเดต `docs/api_contract_v3.md`
- [ ] ไม่มี tokens/passwords, `.venv`, DB หรือคลิปส่วนตัวหลุดเข้า Git
- [ ] คนอื่น review อย่างน้อย 1 คน (cross owner ถ้าแตะ contract)

## ลำดับ merge ที่แนะนำ
1. Contract ของ P2 (docs first) → P1 adapter/test → P2 backend support → P3 Student UI → P4 Staff/QA/integration. หาก PR ใดทำเร็ว merge ก่อนก็ได้ *ถ้า compatible* แต่ schema change ต้องมาก่อน consumer.
2. หลัง **ทุก PR** ให้รัน backend pytest + frontend build + key Playwright (ไม่รอรวมทีเดียว).
3. ก่อน release ยึด snapshot ใหม่/แท็กชื่อ `v3-integrated-demo` และสร้างรายงาน test จากการรันครั้งสุดท้าย.
4. หาก regression fail ให้ revert เฉพาะ PR ที่ทำให้พังหรือแก้พร้อม test; ไม่แก้ production baseline สด ๆ ระหว่างพรีเซนต์.

## สคริปต์ V2 สำหรับ Windows (ตามรายงาน; ตรวจว่ามีจริงใน repo)
```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_demo_windows.ps1 -Reset
powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1
```
`-Reset` สำหรับ demo database เท่านั้น; ห้ามใช้กับ DB จริงและห้ามกดเมื่อ server อื่นยังรัน. ก่อนอัปเดต baseline ควร backup DB/README และผลทดสอบ.

## ปล่อยงานให้ทีมทดลอง
- P1 สาธิต scene + ROI + inference log; P2 แสดง API/DB response; P3 หน้า Student; P4 SeatCheck/Staff + negative tests.
- ทดลองเรื่อง **แหล่งข้อมูล**, **ความสด**, **แยกคนเดินผ่าน**, **Unknown**, **reports** และ **การใช้ระบบจริง**.
- ตัวเลข confidence detector ≠ seat occupancy accuracy; precision/recall ของที่นั่งต้องมาจาก dataset ที่ติด ground truth.
