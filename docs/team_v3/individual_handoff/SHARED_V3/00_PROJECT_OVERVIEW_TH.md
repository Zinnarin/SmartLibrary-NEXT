# 00 — ภาพรวมโครงการ Smart Library NEXT V3

**Repository:** `Zinnarin/SmartLibrary-NEXT` (GitHub, **private**) · **ทีม:** นักศึกษา 4 คน (CPE447) · **ผู้ประสานการรวมระบบ:** P4
**ฐานตั้งต้น:** ต้นแบบ V2 ที่รันได้จริงในเครื่อง (tag `v2-demo-baseline`) — V3 คือการ **ต่อยอด** ไม่ใช่สร้างใหม่

## 1. ปัญหาที่ระบบแก้
นักศึกษาเดินหาที่นั่งในห้องสมุดแล้วพบว่า "ที่ว่าง" ที่เห็นมีคนนั่ง/มีของวางจอง → Smart Library NEXT แสดงสถานะที่นั่ง **เท่าที่หลักฐานยืนยันได้**: ถ้าไม่แน่ใจต้องบอกว่าไม่แน่ใจ (Unknown/Stale) ไม่ใช่เดาว่าว่าง

## 2. เป้าหมายร่วมของ V3 (Final shared goal)
Smart Library NEXT V3 คือ **ระบบเดียวที่รวมกันแล้วรันได้จริง** ซึ่ง:

| # | ความสามารถ | เจ้าของหลัก | สถานะ V2 วันนี้ (ดู `01_V2_CURRENT_STATUS.md`) |
|---|---|---|---|
| 1 | รับหลักฐานภาพเกี่ยวกับที่นั่งจาก **ภาพ/วิดีโอที่ได้รับอนุญาต** | P1 | PARTIAL — pipeline รันได้บนภาพตัวอย่าง `bus.jpg` เท่านั้น; ภาพห้องสมุดจริง BLOCKED |
| 2 | ประเมินสถานะผ่าน **Seat State Engine** ฝั่ง backend | P2 | IMPLEMENTED |
| 3 | เก็บและเรียกข้อมูลที่นั่ง | P2 | IMPLEMENTED (SQLite) |
| 4 | แสดงข้อมูลที่นั่งที่ **น่าเชื่อถือ** บนเว็บนักศึกษา | P3 | IMPLEMENTED สำหรับข้อมูลจำลอง; ข้อมูล CV ยังไม่ขึ้นผัง (PARTIAL → PA-03) |
| 5 | ค้นหา/แนะนำที่นั่ง (StudyMatch, GroupFit, Wayfinder) | P3 (UI) + P2 (logic) | IMPLEMENTED (ข้อมูลผังเป็นของสาธิต) |
| 6 | ผู้ใช้รายงานสถานะผิด (SeatCheck) | P3 (จุดกด) + P4 (workflow) + P2 (API) | IMPLEMENTED |
| 7 | เจ้าหน้าที่ตรวจและจัดการรายงาน | P4 | IMPLEMENTED (ความหมาย override ต้องปรับ #11) |
| 8 | รับมือข้อมูลเก่า กล้องหาย ข้อมูลขัดกัน และข้อผิดพลาด | P2 (กฎ) + P3/P4 (แสดงผล/ทดสอบ) | IMPLEMENTED (+ ข้อบกพร่องที่พบ 1 จุด: PA-02) |
| 9 | แยก **ข้อมูลจำลอง** กับ **ข้อมูลจาก CV จริง** อย่างชัดเจน | ทุกคน | IMPLEMENTED (`source = scenario` / `cv`) |
| 10 | รันเป็น **ระบบเดียว** | P4 | IMPLEMENTED สำหรับ V2; V3 ต้องรวมงาน 4 คนตาม `FINAL_INTEGRATION_PLAYBOOK_TH.md` |

> **ความแม่นยำบนห้องสมุดจริงต้อง "วัด" ไม่ใช่ "สมมติ"** — ถ้ายังไม่ได้วัดด้วยข้อมูลที่ได้รับอนุญาต ต้องรายงานว่า BLOCKED/ไม่มีตัวเลข

## 3. การไหลของข้อมูล (ของจริงใน V2 + ส่วนที่ V3 จะเติม)
```
[ภาพ/วิดีโอที่ได้รับอนุญาต] --P1--> detector (YOLO11n / CiRA CORE? / อื่น ๆ) + ROI ต่อที่นั่ง
        |  evidence ต่อเฟรม (ไม่ใช่สถานะสุดท้าย)            สัญญา C1
        v
POST /api/ingest/observations --P2--> classify() -> SeatStateEngine -> SQLite (seat_observations, seat_current)
        |                                   trust layer: freshness / camera health / report / override
        v                                                                  สัญญา C2 / C3
GET /api/* + WS /ws/seats --> เว็บนักศึกษา (P3): ผัง, StudyMatch, GroupFit, Wayfinder, SeatCheck
                         \--> Staff Console (P4): ตรวจรายงาน, override, audit, อุปกรณ์
SeatCheck ของนักศึกษา --(C4)--> รายงาน pending --> เจ้าหน้าที่ตัดสิน --> WS delta กลับไปหน้านักศึกษา
[Scenario Lab] --P2/P4--> ข้อมูล SIMULATION (source=scenario) สำหรับเดโมและทดสอบความทนทาน
```

## 4. บทบาท 4 คน (สรุป)
| คน | โมดูล | ทำอะไรได้อิสระ | ต้องคุยก่อน |
|---|---|---|---|
| **P1** Computer Vision | `cv/**` | เลือก detector/ROI/algorithm, ทดลอง CiRA CORE, เครื่องมือวัดผล | รูปแบบ payload ที่ส่ง backend (C1), seat ID/กล้องใหม่ |
| **P2** Backend & Database | `services/api/**` | refactor ภายใน, validation, ประสิทธิภาพ, migration ที่ไม่กระทบสัญญา | เปลี่ยน route/field/enum/ความหมาย (C1–C4), schema DB ที่คนอื่นเห็น |
| **P3** Student Frontend | `apps/web/src/**` (ฝั่งนักศึกษา) | redesign UI/UX, ฟีเจอร์นักศึกษาใหม่ | ต้องการ field/API ใหม่, `live.tsx` (P4 ร่วมอนุมัติ) |
| **P4** Staff, QA & Integration | Staff Console, SeatCheck workflow, e2e, `scripts/*`, CI, `integration/**` | ปรับ Staff Console, เพิ่ม test, adapter | แก้โค้ดภายในของคนอื่น (ห้าม — แจ้งเจ้าของแทน) |

## 5. หลักการร่วม (ทุกคนต้องยึด)
1. **ความจริงมาก่อน:** ห้ามแต่งผลทดสอบ/ภาพ/ตัวเลขความแม่นยำ; ห้ามบอกว่าข้อมูลจำลองคือผลกล้องจริง
2. **ไม่ทำลาย V2:** test เดิม 53 + Playwright 8 ต้องผ่านทุกครั้งที่ merge; ไฟล์หลักฐาน V2 (`evidence/*`, `presentation/*`, `verification/*`, `reference/*`, `templates/*`, spec ใน `docs/*`) เป็น FROZEN
3. **อิสระภายใน สัญญาภายนอกคงที่:** ทำภายในโมดูลของตัวเองได้ตามแบบของตัวเอง แต่สัญญา C1–C4 ต้องเข้ากันได้ย้อนหลัง
4. **ความเป็นส่วนตัว:** ไม่ commit วิดีโอ/ภาพบุคคล/ฐานข้อมูล/weights/token; ใช้เฉพาะภาพที่ได้รับอนุญาตเป็นลายลักษณ์อักษร; ไม่เชื่อม CCTV มหาวิทยาลัย; ไม่ deploy สู่ public network
5. **ทุกอย่างผ่าน PR:** branch ของตัวเอง → PR → CI + ownership check + review → P4 รวมตาม playbook

## 6. เอกสารชุดนี้
`00` ภาพรวม · `01` สถานะ V2 จริง · `02` สถาปัตยกรรม · `03` สัญญา API ร่วม (+ `contract_examples/` ของจริง) · `04` ข้อตกลงการทำงาน (GREEN/YELLOW/RED) · `05` roadmap การรวมระบบ · `06` กระบวนการขอเปลี่ยนแปลง · `07` เกณฑ์ยอมรับขั้นสุดท้าย · `FINAL_INTEGRATION_PLAYBOOK_TH.md` คู่มือรวมระบบของ P4
