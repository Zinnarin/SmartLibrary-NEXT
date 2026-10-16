# P2 · 01 — บริบทโครงการ (Backend & Database)

> ชุดเอกสารนี้อ่านจบในตัว — ไฟล์ 01–09 ในโฟลเดอร์นี้คือทุกอย่างที่ P2 ต้องรู้ (ฉบับเต็มของเอกสารร่วมอยู่ใน `docs/team_v3/individual_handoff/SHARED_V3/`)

## 1. Smart Library NEXT คืออะไร
ระบบแสดงสถานะที่นั่งห้องสมุด **เท่าที่หลักฐานยืนยันได้** (ไม่แน่ใจ = Unknown/Stale ไม่ใช่ "ว่าง") ต่อยอดจากต้นแบบ V2 ที่รันได้จริง (repo private `Zinnarin/SmartLibrary-NEXT`, tag `v2-demo-baseline`)

## 2. เป้าหมายร่วม V3 (ย่อ)
1) รับหลักฐานภาพที่ได้รับอนุญาต (P1) · **2) ประเมินสถานะด้วย Seat State Engine ← คุณ** · **3) เก็บ/เรียกข้อมูล ← คุณ** · 4) แสดงข้อมูลที่น่าเชื่อถือบนเว็บนักศึกษา (P3 ใช้ API ของคุณ) · 5) ค้นหา/แนะนำ (logic `matching.py` ของคุณ) · 6) ผู้ใช้รายงาน (API ของคุณ) · 7) เจ้าหน้าที่ตรวจ (API ของคุณ, UI ของ P4) · **8) รับมือข้อมูลเก่า/กล้องหาย/ข้อมูลขัดกัน/ข้อผิดพลาด ← กฎของคุณ** · **9) แยกข้อมูลจำลองกับ CV จริง ← guard ของคุณ** · 10) รันเป็นระบบเดียว
**คุณคือศูนย์กลางของสัญญาทั้งหมด** — ทุกโมดูลคุยกันผ่าน API ของคุณ

## 3. ตำแหน่งของ P2 ในระบบ
```
P1 CV ──C1: POST /api/ingest/observations──►┐
Scenario Lab (SIMULATION) ──ticker──────────►├─► classify() ► SeatStateEngine ► SQLite ► trust layer (build_seat_view)
                                             │                                             │
P3 Student ◄──C2: REST + WS /ws/seats───────┤◄────────────────────────────────────────────┘
P4 Staff  ◄──C3: /api/admin/*───────────────┤
P3→P4 SeatCheck ──C4: /api/session, /api/seat-reports──┘
```

## 4. สถานะ backend วันนี้ (ตรวจกับโค้ดจริง 16 ต.ค. 2569)
| เรื่อง | สถานะ |
|---|---|
| FastAPI 26 routes + SQLite (WAL, `BEGIN IMMEDIATE`, single-writer lock) | **IMPLEMENTED** — pytest 53 passed (CI เขียว 15 ต.ค.) |
| Engine: 4 physical states, smoothing (3/3/4/2 เฟรม + 5 วินาที), gap reset (BUG-001), out-of-order/duplicate guard, clock-skew → unknown | **IMPLEMENTED** |
| Trust layer: TTL 30 วินาที, camera health, pending report, override, `is_recommendable` | **IMPLEMENTED** |
| WebSocket snapshot/delta/heartbeat/pong | **IMPLEMENTED** |
| Ingest CV + guard กันข้อมูลจำลอง/CV ปนกัน | **IMPLEMENTED** — แต่ timestamp ผิดรูปแบบ → **HTTP 500** (พบ 16 ต.ค., PA-02) |
| ข้อมูลที่นั่ง/ผัง/ปลั๊ก/ความติดกัน | **SIMULATED** (`metadata_source = "demo_assumed"`) |
| ที่นั่งที่รับ CV | `LAB1`–`LAB4` บนกล้อง `CV-LAB` — **ซ่อนจากผังนักศึกษา** (`is_active=0`) |
| Migration | ไม่มีเครื่องมือ — schema ใช้ `CREATE TABLE IF NOT EXISTS`, ข้อมูลสาธิต re-seed |
| ตำแหน่งไฟล์ผล CV | `settings.cv_evidence_dir = evidence/cv` (FROZEN) และ **ยังตั้งผ่าน env ไม่ได้** (PA-01, issue #3) |
| Staff auth | demo gate (token เดียว, actor `staff-demo` เสมอ) — ไม่ใช่ระบบยืนยันตัวตนจริง |
| Rate limit SeatCheck | ต่อ session เท่านั้น (ขอ session ใหม่เลี่ยงได้ — ข้อจำกัดที่รู้แล้ว) |

## 5. เพื่อนร่วมทีม
* **P1 (CV):** ส่ง evidence ผ่าน C1 และ **import โค้ด engine ของคุณ** (`EngineConfig`, `Detection`, `classify`, `SeatEngineState`, `step`) — ห้ามเปลี่ยน signature โดยไม่แจ้ง (C1b)
* **P3 (Student):** ใช้ C2 + C4 ผ่าน `apps/web/src/api.ts`; TypeScript types ตาม field ของคุณ
* **P4 (Staff/QA/Integration):** ใช้ C3; เขียน e2e/contract test; เสนอ test case ของ `scenarios.py`/`seed.py` ให้คุณแก้; รวมงานทั้งหมด

## 6. กติกาที่ห้ามละเมิด
ห้ามเปลี่ยนสัญญาแบบเงียบ ๆ · ห้ามทำให้ client ของ student/staff พัง · ห้ามเปลี่ยนสถาปัตยกรรมทั้งระบบโดยทีมไม่อนุมัติ · ห้ามลดกฎความปลอดภัย (stale/unknown/offline/pending ห้ามถูกแนะนำ; รายงาน 1 ครั้งห้ามตั้ง Occupied) · ห้ามแต่งผล/เรียกข้อมูลจำลองว่าข้อมูลจริง · ไม่ commit DB/token
