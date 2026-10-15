# PERSON 2 — Backend / Database / API Contract Owner

**ความรับผิดชอบ:** รับ observations, ประเมินสถานะอย่างเชื่อถือได้, persistence/audit, REST/WS. ไม่สร้าง Computer Vision pipeline ใหม่และไม่ออกแบบหน้า Student ใหม่.

**ไฟล์หลัก**: `services/api/app/main.py`, `services/api/app/db.py`, `services/api/app/state_engine.py`, `services/api/app/services.py`, `services/api/app/trust.py`, `services/api/app/realtime.py`, `services/api/app/evidence.py`, `services/api/app/matching.py` และไฟล์ API core อื่นที่ตรวจเจอ. เพิ่ม `docs/api_contract_v3.md`, `tests/test_backend_v3.py`.

**สิ่งที่มีอยู่:** FastAPI/SQLite/Seat State Engine/WebSocket ที่ V2 รายงานว่าผ่านทดสอบ.

**งานที่จะทำต่อ:**
1. ภายในวันแรก extract routes & payload จาก FastAPI/Pydantic ของจริง ลง schema + examples + error status.
2. ตรวจ `/api/ingest/observations`: valid/invalid source, device auth, event ID replay, time skew, out-of-order, uncertain quality, smoothing/gap reset.
3. เปิดทางรับ real CV experimental seats โดยไม่ปน demo A01–C08 และไม่ให้ CV ผลผิดกลายเป็นสีเขียวแน่ชัด.
4. อธิบาย SeatCheck/Staff API, audit semantics, expiry; ถ้าต้องเพิ่ม `pending inspection` ให้ออกเป็น contract proposal พร้อม migration/tests.
5. Test backend end-to-end, reconcile API schema กับ Person 1/3/4.

**ต้องส่ง:** `docs/api_contract_v3.md` ที่ใช้ได้จริง, test report, sample responses, migration notes ถ้ามี, PR, regression logs.

**ผ่านเมื่อ:** P1 event ผ่านหรือถูก reject ตาม contract; ทุก seat state ฝั่ง student/staff sync, stale/unknown/idempotency ถูกต้อง, baseline tests ไม่ regress.
