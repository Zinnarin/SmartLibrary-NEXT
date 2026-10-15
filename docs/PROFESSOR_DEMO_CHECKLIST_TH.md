# แผนอัปเดตอาจารย์ 15 ตุลาคม 2569 — Smart Library NEXT V2

## คำสั่งอาจารย์ที่ต้องครอบคลุมในคลิป 3 นาที
1. **สรุปงานก่อนหน้า:** เพื่อนทำเอกสาร technical proposal 13 หัวข้อ (30 ก.ย.) และสไลด์นำเสนอหัวข้อ 15 หน้า (1 ต.ค.) โดยยังไม่เคยรับคำติชมจากการพรีเซนต์อาจารย์. ห้ามเรียกเป็นระบบที่ implement แล้ว.
2. **ปัญหาหรือบัคที่เกิดและวิธีแก้:** หลังให้ Claude Code รันจริงเท่านั้นจึงกรอก `bug, reproduction, fix, evidence`; ความเสี่ยง “คนเดินผ่าน/แสงมืด/กล้องหลุด” ถ้ายังไม่เกิดในการทดสอบให้เขียน **ความเสี่ยงที่คาดการณ์** ไม่ใช่ bug จริง.
3. **ผลงานเพิ่มเติม:** เดโมเว็บที่คลิกได้จริงและเชื่อม backend พร้อมหลักฐาน screenshot/test result.

## เนื้อหา 8 สไลด์ / คลิป 3 นาที
- 0:00–0:20 — ปัญหา: เสียเวลาเดินหาเก้าอี้, เจอเก้าอี้ที่บอกว่างแต่มีคน/ของ.
- 0:20–0:40 — งานเดิมจาก PDF + DOCX: YOLO, 5 states, floor map, Edge-first, 10 failure cases.
- 0:40–1:00 — ยกระดับเป็น “Find. Verify. Study.” พร้อมแยก state, reliability และที่นั่งที่มี report.
- 1:00–1:45 — **เดโมจริง:** เปิด student map → filter quiet+power → StudyMatch เหตุผล → แกล้งเลือก seat ที่ตรวจพบผิด → SeatCheck ส่ง report.
- 1:45–2:10 — staff dashboard เห็นรายงาน → mark maintenance/resolve reason → student app sync; จำลอง camera disconnect + stale (ต้องมีป้าย simulation).
- 2:10–2:35 — โชว์ CV inference จริงและ ROI **เฉพาะหากรันได้จริง**; ถ้าไม่สำเร็จโชว์ state engine + error evidence และบอกขั้นตอนที่จะถ่ายวิดีโอทดสอบ.
- 2:35–2:50 — อธิบาย bug ที่พบจริงพร้อมสิ่งที่แก้/ยังติดขัด และ test log; ไม่ใช้ dummy pass.
- 2:50–3:00 — next steps และขออนุญาตภาพ+ผังจริง.

## ขั้นตอนเดโมที่อาจารย์ทดลองเองได้
1. `NORMAL` scenario → ดูจำนวนที่นั่งตามสถานะ + เวลาของข้อมูล + badge SIMULATION.
2. filter quiet + power → ระบบแนะนำเฉพาะที่นั่งสดและมีข้อมูลจริง (ใน demo คือ metadata สมมติ).
3. คลิก A07 (หรือที่นั่ง test) → `ที่นั่งจริงไม่ตรงกับระบบ` → เลือก `มีคนนั่ง` → ส่ง report.
4. Recommendation ลดอันดับหรือเอา A07 ออกจากผลคำแนะนำที่น่าเชื่อถือสูง (ไม่ปลอมว่ากล้องยืนยันว่ามีคน).
5. Staff page → รายงานใหม่ → รับเรื่อง ตรวจสอบ → Override `Maintenance` / ปิดเคสมีเหตุผล → กลับ student เห็นป้ายที่เปลี่ยนผ่าน WebSocket.
6. `CAMERA_LOST` → ไม่มี Available เก่าถูกแสดงเหมือนข้อมูลสด; แสดงเวลาล่าสุด/Unknown/Stale (ถ้า override ยังคง Maintenance พร้อม sensor offline).
7. (ถ้า implemented) GroupFit สองที่ติดกัน, Wayfinder เป็นแผนที่ทดลอง; (ถ้า CV working) local lab showing genuine model and source.

## หลักฐานที่ต้องขอจาก Claude ก่อนส่งอาจารย์
- `evidence/IMPLEMENTATION_REPORT.md` แยกรายการผ่านจริง/จำลอง/แค่แผน/ยังไม่ผ่าน
- screenshot **จาก UI ที่รันจริง** ≥ 3 หน้า (student, report, admin/health)
- test summary และ command สำหรับ run app บน Windows
- export `.pptx` ที่แก้ได้ + script 3 นาที
- ถ้ามี CV ให้รายงาน source, model, inference log จริง, ภาพที่ได้รับอนุญาต และข้อจำกัด

## ข้อควรระวังเรื่องความจริง
ห้ามเอาไฟล์แผนงานนี้ไปพูดว่า “พัฒนาแล้วครบทั้งหมด”. ปรับคลิปให้ตรงสถานะจริงจาก implementation report ทุกครั้ง.
