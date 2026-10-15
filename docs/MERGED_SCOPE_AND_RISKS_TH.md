# SMART LIBRARY NEXT V2 — ผลการผสานเอกสารเดิมกับแนวคิดยกระดับ

**สถานะ:** เอกสารแผนงาน ไม่ใช่หลักฐานว่าพัฒนาระบบสำเร็จแล้ว

## ที่มา

- `Smart_Library.pdf` วันที่ 1 ต.ค. 2569 เป็น **สไลด์ 15 หน้า** เพื่อเสนอหัวข้อ: 5 สถานะ, YOLO+ROI, Edge, Floor Map, Dashboard, Offline, Failure Case
- `Smart_Library_Seat_Proposal.docx` วันที่ 30 ก.ย. 2569 เป็น **ข้อเสนอเชิงเทคนิค 11 หน้า 13 หัวข้อ**: มีผู้ใช้งาน IT, IP camera, temporal smoothing, MQTT QoS 1, SQLite buffer + sync, ค่า initial threshold, diagram และ 10 failure cases
- แนวคิด NEXT (ก่อนมี DOCX): StudyMatch, GroupFit, Wayfinder, SeatWatch, Admin, freshness/trust

**ข้อสรุป:** DOCX ไม่ใช่คู่แข่งกับ NEXT; มันคือรากฐานเชิงวิศวกรรมที่ต้องรักษา ส่วน NEXT ทำให้ข้อมูลถูกนำไปใช้แก้ปัญหาจริง

## สิ่งที่เดิมมีดีอยู่แล้ว ต้องไม่ทำหาย

1. ข้อเท็จจริงว่าที่นั่งมี 5 สถานะ พร้อม priority ของ manual override.
2. เวลาและแหล่งข้อมูล (`observed_at`) สำคัญ; กล้อง/เน็ตล่มต้องไม่แสดงข้อมูลเก่าเหมือนปัจจุบัน.
3. ของที่วางอยู่ไม่ควร auto-release หลัง 30 นาที; แค่ขึ้นรายการให้เจ้าหน้าที่ตรวจ.
4. วิดีโอควรประมวลผลที่ Edge และไม่เก็บ raw frames เป็นค่าเริ่มต้น; ใช้จริงต้องขออนุญาต.
5. DOCX ระบุ Failure Cases อย่างเป็นระบบ เช่น แสง, การบัง, คนเดินผ่าน, แก้วน้ำ, power-loss และ sync.
6. ค่า threshold, interval, UPS, QoS, buffer เป็น proposed defaults ยังไม่มีหลักฐานว่าเหมาะกับกล้องจริง.

## ช่องว่างที่ต้องแก้ก่อนเพิ่มลูกเล่น

- พูดว่า “มีกระเป๋าจอง” อย่างมั่นใจไม่ได้; จริง ๆ อาจเป็นกระเป๋าของคนนั่งข้าง ๆ หรือไม่ได้จับจอง.
- ตรวจพบ person ใน ROI ไม่ได้แปลว่าเขานั่ง; ต้องแยก walking path และมุมที่นั่ง.
- ถ้าไม่เห็นคนเพราะกล้องถูกบัง ต้องไม่แสดง available.
- ข้อมูล sensor confidence ไม่ใช่ probability ว่าที่นั่งว่างแน่นอน.
- คนอาจเดินไปถึงแล้วพบสถานะจริงไม่ตรงกับหน้าเว็บ: **ระบบเดิมไม่มีทางให้ผู้ใช้รายงานและให้เจ้าหน้าที่แก้ข้อมูลอย่างเป็นระบบ**.
- ไม่มีหลักฐานแสดงว่าคำแนะนำช่วยลดเวลาในการหาที่นั่งจริงจนกว่าจะทดลองกับผู้ใช้.

## จุดแตกต่างสำคัญ V2: Find → Verify → Resolve

1. **Find:** นักศึกษาเลือกโซนเงียบ + ปลั๊ก; StudyMatch เลือกที่นั่งที่ `fresh & reliable` เท่านั้น.
2. **Check:** เมื่อเดินถึงแล้วพบว่าในความเป็นจริง A07 มีคนนั่ง กด **SeatCheck: สถานะไม่ตรงจริง** โดยไม่ต้องอัปโหลดรูปหรือระบุตัวตน.
3. **Verify:** ระบบบันทึก report + เวลาพบ ปักธง “มีรายงานรอตรวจสอบ” และไม่นำ A07 ไปแสดงเป็นคำแนะนำที่มั่นใจสูง โดย **ไม่เปลี่ยนสถานะ Occupied อัตโนมัติจากการกดเพียงครั้งเดียว**.
4. **Resolve:** เจ้าหน้าที่ดูรายการรายงาน ตรวจพื้นที่ แล้วปรับ override/ปิดเคส พร้อมเหตุผลและ audit log.
5. **Learn:** เก็บเฉพาะข้อมูลระดับสถานะสำหรับวัดความถี่ข้อมูลคลาดเคลื่อน (ข้อมูลจำลองแยกจากข้อมูลจริง) เพื่อวิเคราะห์/ปรับ ROI ในอนาคต.

ฟีเจอร์นี้แก้ pain point ที่เกิดขึ้น *หลังการตรวจจับ* โดยไม่ต้องฝืนเพิ่มโมเดล AI แพง ๆ ตั้งแต่วันแรก

## Architecture อย่างย่อ

Camera / permitted video (future production Edge)
→ YOLO inference + ROI geometry + frame quality
→ temporal seat state engine
→ FastAPI + SQLite observations + reports + staff overrides
→ WebSocket state changes
→ Student Floor Map / StudyMatch / GroupFit / Wayfinder
→ SeatCheck feedback → Staff Review & Audit

For tomorrow: use **backend-driven scenario mode** + optional small true CV demo; MQTT/PoE/Jetson/PostgreSQL/UPS are future architecture only.

## Priority matrix

| ความสำคัญ | สิ่งที่ต้องทำ | เหตุผล |
|---|---|---|
| P0-A | App + API + SQLite + real WS | มี demo กดได้และทดสอบได้จริง |
| P0-A | status/Unknown/Stale + manual override | ป้องกัน “ว่างผิด” |
| P0-A | StudyMatch แบบมีเหตุผล | ช่วยตัดสินใจแทนการดูไฟเขียว |
| P0-A | SeatCheck report → staff verify → audit | แก้ความคลาดเคลื่อนจริงและสร้าง feedback loop |
| P0-A | Scenario ที่ชัดเจนว่าเป็น simulation | ทดสอบเคสเสี่ยงได้แม้ไม่มีกล้อง |
| P0-B | GroupFit + Wayfinder | น่าสนใจและมีผลต่อ UX ถ้าผังรองรับ |
| P1 | YOLO + ROI กับภาพที่ได้รับอนุญาต | ยืนยันแกน Computer Vision ของโครงงาน |
| P2 | MQTT / Pi/Jetson / PoE / Cloud / LED / prediction | ต้องมีเครื่องและข้อมูลจริงก่อน |

## เกณฑ์วัดที่ตอบอาจารย์ได้

**Technical:** False Available rate (สำคัญสุด), seat-status confusion matrix, Unknown coverage, observed event-to-UI latency, stale failover time, false reserved, staff override precedence, group adjacency, user report resolution accuracy.

**User Impact:** เวลาหาที่นั่งตรงเงื่อนไขจริง, อัตราหาที่นั่งสำเร็จ, จำนวนเที่ยวที่เดินไปผิด, ความเข้าใจ trust badge. ยังไม่มีผลตัวเลขจนกว่าจะทดลองและบันทึกจริง.

## เรื่องที่ต้องขอคำตอบ/การอนุญาต

1. ห้องสมุดหรือพื้นที่ทดลองใดให้เข้าถึงได้ และถ่ายตัวอย่างแบบมี consent ได้หรือไม่?
2. ผังที่นั่งและเงื่อนไข (`quiet`, `power`, ทางเข้า, adjacency) เป็นข้อมูลจริงที่ใครยืนยัน?
3. อาจารย์อยากเน้นหลักฐาน CV Accuracy หรือผลจาก UX เช่น search success/false free?
4. ใครเป็นผู้อนุมัติการใช้กล้อง/IP/CCTV และนโยบายดูแลที่นั่งที่มีทรัพย์สินวางอยู่?

## สิ่งที่ไม่ควรกล่าวอ้างในวันอัปเดต

- “ติดตั้งกล้องแล้ว/โมเดลแม่น X%/ปรับ fine-tune แล้ว” หากยังไม่ได้ทำ
- “ออนไลน์แบบ real-time ทุกกรณี” เมื่อมีแค่เครื่อง local scenario
- “Reserved คือที่นั่งมีเจ้าของจองแล้ว” จากการมองเห็นของเท่านั้น
- “ระบบแรกของโลก” หรือ “แก้การแย่งที่นั่งด้วยการยึดของ”
- “ผ่าน PDPA แล้ว” เพียงเพราะไม่เก็บภาพ
- “แก้บัคได้แล้ว” โดยไม่มีบัคและหลักฐานทดสอบจริง
