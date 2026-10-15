# INTEGRATION CONTRACT — สัญญาระหว่าง 4 ส่วน

> เอกสารนี้เป็น **interface agreement draft**. รูปทรง JSON ที่แน่นอนต้องให้ **คนที่ 2 สกัดจากโค้ด FastAPI/Pydantic ที่รันอยู่** แล้วลง `docs/api_contract_v3.md` ภายในวันแรก; ห้ามเดาชื่อฟิลด์แล้วให้ทีมส่ง payload ไม่ตรง. ใช้ endpoint จริงที่มีอยู่ เช่น `POST /api/ingest/observations` และ `WS /ws/seats`.

## Data flow เป้าหมาย

```
Authorized chair video / camera (person 1)
   -> YOLO/CiRA adapter + camera-calibrated ROIs
   -> OBSERVATION/EVIDENCE event (NOT final truth)
   -> POST /api/ingest/observations (person 2 owner)
   -> SeatStateEngine -> SQLite -> REST/WS
   -> Student UI (person 3) / Staff UI & QA (person 4)
```

## Agreement A: CV -> Backend (person 1 + person 2)
- คนที่ 2 freeze exact schema: ID อีเวนต์, camera/device ID, seat ID, source=`cv`, timestamps/timezone, evidence/quality codes, version, authentication and constraints.
- คนที่ 1 แปลง output YOLO/CiRA เป็น format ที่ API ยอมรับ; **ห้ามเขียน DB โดยตรงหรือปลอม `occupied` เป็นผลตรวจที่ยืนยันแล้ว**.
- ROI ต้องอ้าง seat ID ที่ mapping กับกล้องจริงชัดเจน; วิดีโอ test พร้อม ground truth แยกจาก simulation. CV-LAB ไม่ overwrite A01–C08 จนผ่านการอนุญาตและ policy ย้ายข้อมูล.
- Person 2 เขียน contract test ingest (valid, duplicate, outdated, uncertain, bad token). Person 1 เขียน adapter conformance test.

## Agreement B: Backend -> Student (person 2 + person 3)
- Frontend เรียก API จริงที่ backend รองรับ (`/api/seats`, `/api/seats/{id}`, `/api/recommendations`, `/api/layout` ฯลฯ) ใช้ `apps/web/src/api.ts` จุดเดียว.
- Field status, `freshness`, `source`, pending report, admin override ต้องแสดงอย่างซื่อสัตย์.
- Unknown/Stale/offline/มีรายงานค้าง ห้ามเสนอเป็น Available ที่ยืนยันแล้ว. ห้ามเปลี่ยน logic ให้ผ่านแค่หน้าจอแต่ backend ไม่ตรง.
- หากต้องการ field ใหม่: เปิด Issue; Person 2 เพิ่ม schema+tests; Person 3 ปรับ types/UI. ห้ามแก้ API และ UI พร้อมกันคนละแบบ.

## Agreement C: SeatCheck -> Staff -> Student (persons 2, 3, 4)
- คนที่ 4 เป็นเจ้าของ Staff Console และ logic การทดสอบ workflow; คนที่ 2 เป็นเจ้าของ API/DB; คนที่ 3 เป็นเจ้าของจุดกด SeatCheck บน Student page.
- 1 report **ไม่เปลี่ยนเป็น occupied เอง**; ต้องแสดง pending แล้วพักจาก recommendations ที่เสี่ยง.
- เจ้าหน้าที่ review/resolve พร้อมเหตุผล, audit event; สถานะ manual override ถ้าใช้ ต้องสอดคล้องความหมาย (พิจารณา `Unknown/Pending Inspection` ระหว่างตรวจ ไม่ใช้ Maintenance แปลว่าคนนั่งจริง).
- เมื่อ Staff เปลี่ยนสถานะ ให้ delta/refresh ถึง Student; fallback polling ทำงานเมื่อ WS หลุด.
- Person 4 มี test อัตโนมัติเต็มเส้นทางและหลักฐาน before/after.

## Agreement D: Failure safety
- เมื่อ server หาย, browser ไม่ค้างสีเขียว (BUG-011 regression).
- กล้องหาย/เฟรมไม่ถึงตาม TTL -> Unknown/Stale/recommendation suppression; กลับมาแล้วต้องสะสมหลักฐานใหม่ (BUG-001 regression).
- Out-of-order / replay event ห้าม roll back state.
- Demo scenarios ติดป้าย `SIMULATION`; real CV ติดป้าย dataset, consent, model/version; ผลที่นั่งจริงไม่มี accuracy หากยังไม่ได้วัด.

## Interface freeze checklist
- [ ] คนที่ 2 อัปเดต `docs/api_contract_v3.md` จากโค้ดจริง (routes+Pydantic schema+sample response+error codes)
- [ ] คนที่ 1 ทดสอบ POST real observation เข้า CV-LAB อย่างน้อย 1 sample (มีแหล่งภาพที่ได้รับอนุญาต)
- [ ] คนที่ 3 รองรับ source=simulation/cv, freshness + status โดยไม่ต้อง hard-code
- [ ] คนที่ 4 ทดสอบ report→staff resolution→WS + server kill→stale
- [ ] PR cross-team ทุกอันมี request/response sample และผลทดสอบ
