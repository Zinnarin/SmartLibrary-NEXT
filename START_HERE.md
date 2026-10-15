# SMART LIBRARY NEXT V2 — CLAUDE CODE BUILD HANDOFF

**สถานะ 14 ตุลาคม 2569:** ชุดนี้เป็น **เอกสารสั่งพัฒนาและต้นฉบับอ้างอิง** ไม่ใช่แอปที่สร้างเสร็จหรือผลทดลอง CV จริง.

## คุณได้รับอะไร
- `docs/UNIFIED_ENGINEERING_SPEC_V2.md` ข้อกำหนดระบบฉบับรวมล่าสุด: สถานะ, ความน่าเชื่อถือ, UX, API, test gates, privacy, scope.
- `CLAUDE_CODE_MASTER_PROMPT.md` คำสั่งละเอียดให้ Claude Code **ลงมือเขียนและทดสอบ** ไม่หยุดแค่แผน.
- `docs/MERGED_SCOPE_AND_RISKS_TH.md` เปรียบเทียบข้อเสนอเพื่อนกับ NEXT และข้อควรระวัง.
- `docs/PROFESSOR_DEMO_CHECKLIST_TH.md` ลำดับเดโม, เนื้อหา 8 สไลด์, คลิป 3 นาที.
- `verification/ACCEPTANCE_TEST_MATRIX.csv` เกณฑ์ทดสอบ T01–T16 ทั้งหมดเริ่มจาก `NOT_RUN`.
- `templates/IMPLEMENTATION_REPORT_TEMPLATE.md` แม่แบบรายงานหลักฐานงานจริง.
- `reference/Smart_Library.pdf` และ `reference/Smart_Library_Seat_Proposal.docx` ไฟล์ต้นฉบับเพื่อน (คงไว้ไม่แก้ไข).

## ขั้นตอนบน Claude Code Desktop
1. แตก ZIP ไปยังโฟลเดอร์โปรเจกต์ใหม่ เช่น `C:\Projects\SmartLibraryNEXT` (อย่าปนกับโปรเจกต์อื่น).
2. เปิดโฟลเดอร์นี้เป็น Workspace ใน Claude Code Desktop.
3. ส่งข้อความคำสั่งนี้ในแชต Claude Code:

```text
You are the lead implementation engineer for Smart Library NEXT V2. Read CLAUDE_CODE_MASTER_PROMPT.md and docs/UNIFIED_ENGINEERING_SPEC_V2.md completely. Treat the two documents under reference/ as the original project requirements; read both before coding. Also review docs/MERGED_SCOPE_AND_RISKS_TH.md, docs/PROFESSOR_DEMO_CHECKLIST_TH.md and verification/ACCEPTANCE_TEST_MATRIX.csv.

Proceed immediately with a functioning Windows-local implementation, not just planning. Check installed tools first, then implement and verify P0 in order: backend seat/state/freshness + demo scenarios, responsive student map + StudyMatch, SeatCheck report -> staff review/override -> WebSocket update, then P0-B GroupFit/Wayfinder. Make a legitimate small YOLO+ROI attempt using only an authorized video/camera; if no authorized source, report CV as BLOCKED and preserve the demo. Build an editable 16:9 Thai PowerPoint from ACTUAL screens and a truthful 3-minute script, plus implementation report, genuine bug log, test outputs and Windows launch command.

Never present simulated occupancy as actual camera inference, never invent measurements, never silently mark tests PASS. Never connect to institutional CCTV or deploy to public networks without approval. Do not stop after producing architecture files. Continue through coding, execution, tests and evidence, and summarize exactly what is verified vs blocked.
```

4. เมื่อ Claude Code ทำงาน รายงานกลับมาควรมี `README.md`, โฟลเดอร์แอป/Backend, URL local, คำสั่งรัน, ชุดทดสอบ, `presentation/progress_update.pptx`, สคริปต์พูด และ `evidence/IMPLEMENTATION_REPORT.md`.
5. ก่อนถ่ายคลิป ให้อ่านสถานะจริงที่ Claude รายงาน หากบางฟังก์ชันยังไม่สำเร็จให้พูดอย่างตรงไปตรงมา; ห้ามนำ Scenario Mode ไปอ้างเป็นกล้องจริง.

## เวลานำเสนอพรุ่งนี้ ควรเห็นอะไร
เปิด Student Map -> กรองเงียบ/ปลั๊ก -> แนะนำที่นั่งสดพร้อมเหตุผล -> กด `SeatCheck` รายงานผิด -> เจ้าหน้าที่ตรวจและ override -> กลับหน้าผู้ใช้เห็นเปลี่ยนทันที -> จำลองกล้องหลุดแล้วที่นั่งเก่าไม่นำมาแนะนำ. หากทำ GroupFit/Wayfinder/YOLO ได้จริงค่อยโชว์เพิ่ม.

**คุณจะต้องส่ง ZIP นี้ให้ Claude Code ใช้รันในเครื่องของคุณ.** ชุดเอกสารนี้ไม่ได้ติดตั้ง Python, Node หรือโปรแกรมใดให้โดยอัตโนมัติ.
