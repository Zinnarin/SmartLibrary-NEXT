# P3 · 01 — บริบทโครงการ (Student Frontend)

> ชุดเอกสารนี้อ่านจบในตัว — ไฟล์ 01–09 ในโฟลเดอร์นี้คือทุกอย่างที่ P3 ต้องรู้ (ฉบับเต็มของเอกสารร่วมอยู่ใน `docs/team_v3/individual_handoff/SHARED_V3/`)

## 1. Smart Library NEXT คืออะไร
ระบบแสดงสถานะที่นั่งห้องสมุด **เท่าที่หลักฐานยืนยันได้** (ไม่แน่ใจ = Unknown/Stale ไม่ใช่ "ว่าง") ต่อยอดจากต้นแบบ V2 ที่รันได้จริง (repo private `Zinnarin/SmartLibrary-NEXT`, tag `v2-demo-baseline`)

## 2. เป้าหมายร่วม V3 (ย่อ)
1) รับหลักฐานภาพ (P1) · 2) ประเมินสถานะ (P2) · 3) เก็บข้อมูล (P2) · **4) แสดงข้อมูลที่น่าเชื่อถือบนเว็บนักศึกษา ← คุณ** · **5) ค้นหา/แนะนำที่นั่ง (UI) ← คุณ** · **6) ผู้ใช้รายงานสถานะผิด (จุดกด) ← คุณ** · 7) เจ้าหน้าที่ตรวจ (P4) · **8) แสดงข้อมูลเก่า/กล้องหาย/ขาดการเชื่อมต่ออย่างซื่อตรง ← คุณ** · **9) แยกข้อมูลจำลองกับ CV จริงบนหน้าจอ ← คุณ** · 10) รันเป็นระบบเดียว (P4)

## 3. ตำแหน่งของ P3 ในระบบ
```
backend (P2) ──C2: GET /api/seats, /api/recommendations, /api/route, … + WS /ws/seats──► apps/web/src/api.ts + live.tsx ──► StudentPage, FloorMap, SeatDetail, StudyMatch (คุณ)
                                                                                                            └─ SeatCheck ──C4──► POST /api/seat-reports ──► Staff Console (P4)
CV run record (P1) ──C1c: GET /api/cv/status, /api/cv/lab-seats──► pages/CvLab.tsx (คุณ + P1 อนุมัติ)
```
**หน้าเว็บไม่คำนวณสถานะเอง** — แสดงตามที่ backend ตัดสิน; ข้อยกเว้นเดียวคือ guard ความปลอดภัยใน `live.tsx` ที่ทำให้ข้อมูล "ไม่เป็นปัจจุบัน" เมื่อเซิร์ฟเวอร์เงียบ (BUG-011)

## 4. สถานะหน้าเว็บวันนี้ (ตรวจกับโค้ดจริง 16 ต.ค. 2569)
| เรื่อง | สถานะ |
|---|---|
| ผังที่นั่ง SVG (24 ที่นั่ง, โซน A/B/C), รายละเอียดที่นั่ง, ป้าย SIMULATION/ความสด/กล้อง, legend | **IMPLEMENTED** — โซน A/B/C **วาดแบบ hard-code** ใน `FloorMap.tsx` และ `ZONE_TH` ใน `labels.ts` |
| StudyMatch (เงื่อนไขบังคับ, เหตุผล, ไม่มีผล + ข้อเสนอผ่อนเงื่อนไข, ไม่มี % ปลอม) | **IMPLEMENTED** (ข้อมูลผังเป็นของสาธิต) |
| GroupFit (2 คน, ที่นั่งติดกันตามตารางที่บันทึกด้วยมือ) | **IMPLEMENTED** (มากกว่า 2 คน → API ตอบ 422) |
| Wayfinder (เส้นทางบนกราฟ หน่วยผัง ไม่ใช่เมตร) | **IMPLEMENTED** |
| SeatWatch (แจ้งเตือนในแอปเมื่อมีที่นั่งตรงเงื่อนไขว่างขึ้น — ไม่จอง) | **IMPLEMENTED** |
| SeatCheck (ฟอร์มรายงานอยู่ใน `SeatDetail.tsx`) | **IMPLEMENTED** — จะย้ายเป็น `SeatCheckPanel.tsx` ของ P4 (PR-A) แล้วคุณนำมาใช้ (PR-B) |
| WS + polling fallback + reconnect + guard เซิร์ฟเวอร์ล่ม (BUG-011) | **IMPLEMENTED** ใน `live.tsx` |
| มือถือ 390 px ไม่มี horizontal scroll, คีย์บอร์ดบนผัง | **IMPLEMENTED** (พื้นฐาน; ยังไม่ทดสอบ screen reader) |
| ข้อมูล CV บนผังนักศึกษา | **ยังไม่มี** — CV ไปที่ `LAB1`–`LAB4` ซึ่งซ่อนจากผัง ดูได้ที่หน้า CV Lab เท่านั้น (PA-03 ต้องทีมอนุมัติ) |
| ข้อมูลที่แสดงบนผังทั้งหมด | **SIMULATION** (`source = "scenario"`) |

## 5. เพื่อนร่วมทีม
* **P2 (Backend):** เจ้าของ API ทุกตัวที่คุณเรียก — ต้องการ field ใหม่ ให้เขียน CR ถึง P2 ห้ามสร้าง backend/DB แยก
* **P4 (Staff/QA/Integration):** ร่วมอนุมัติ `live.tsx`, `package.json`; สร้าง `SeatCheckPanel.tsx` ให้คุณใช้; เขียน e2e ฝั่งเจ้าหน้าที่; รวมงาน
* **P1 (CV):** ร่วมอนุมัติ `CvLab.tsx` — เป็นเจ้าของรูปแบบ `latest_run.json` ที่หน้า CV Lab อ่าน

## 6. กติกาที่ห้ามละเมิด
ห้ามสร้างฐานข้อมูลแยก · ห้ามเปลี่ยน schema API แบบเงียบ ๆ · ห้ามแสดงข้อมูลจำลองว่าเป็นข้อมูลจริง · ห้ามทำให้ที่นั่งที่ `is_recommendable = false` (unknown/stale/กล้องออฟไลน์/มีรายงานค้าง/override) ดูเป็น "ว่าง" · ห้ามแสดง % ความแม่นยำ/ความน่าจะเป็นปลอม · ห้ามทำลาย guard BUG-011 · คง `data-testid` ที่ e2e ใช้
