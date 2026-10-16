# P1 · 02 — ภารกิจที่ได้รับมอบหมาย (Computer Vision)

**Branch:** `feature/v3-cv` (แตกย่อยได้ เช่น `feature/v3-cv-pose`) · **Label:** `person-1-cv` · **Issues:** #3, #4, #5, #14 (BLOCKED), #15 (BLOCKED)

## ภารกิจ
เป็นเจ้าของโมดูล Computer Vision: เปลี่ยน CV จาก "pipeline บนภาพตัวอย่าง" ให้เป็น **หลักฐานจากฉากเก้าอี้/ที่นั่งจริงที่ได้รับอนุญาต** ที่ส่งเข้า backend ตามสัญญา C1 และ **วัดความผิดพลาดอย่างซื่อตรง**

## เป้าหมาย
1. ทำงานกับฉากเก้าอี้/ที่นั่งจริง (จัดฉาก 2–4 ที่นั่ง ผู้ร่วมทดลองยินยอมเป็นลายลักษณ์อักษร)
2. ปรับปรุงการตรวจจับวัตถุ
3. ทำ/ปรับปรุงการจัดการ ROI (calibrate กับมุมกล้องจริง)
4. ประเมิน **นั่ง vs ยืน** (ปัจจุบันใช้จุดสะโพก 65% ของกล่อง + overlap ≥ 0.30 ซึ่งแยกไม่ออกถ้า ROI ไม่ตรงเก้าอี้จริง — ดู LAB1)
5. รับมือการบังบางส่วน (partial occlusion)
6. ทดสอบคนเดินผ่านเก้าอี้ (walk-by ต้องไม่กลายเป็น Occupied)
7. ประเมินวัตถุที่เกี่ยวกับที่นั่ง (กระเป๋า/โน้ตบุ๊ก/หนังสือ = belongings; แก้ว/ขวด = ไม่นับ)
8. วัดความผิดพลาดของการตรวจจับ (confusion matrix, False Available, Unknown coverage, N)
9. ผลิต **หลักฐานการตรวจจับมาตรฐาน** (standardized detection evidence — PA-04)

## สิ่งที่ทำได้อิสระ (🟢 GREEN — ไม่ต้องขออนุญาต)
* ปรับปรุง YOLO: รุ่นอื่น (`yolo11s`, `yolo11n-pose` ฯลฯ), fine-tune ด้วยข้อมูลที่ได้รับอนุญาต, ปรับ imgsz/threshold ฝั่ง CV
* ประเมิน **CiRA CORE** (ถ้าอาจารย์ยืนยัน #15) เป็น adapter แยก — อย่าลบ YOLO ที่ทำงานอยู่
* ใช้ algorithm CV อื่นที่เหมาะสม: pose keypoints, tracking, background subtraction, temporal filter ฝั่ง CV
* วิธี ROI ที่ดีกว่า: เครื่องมือวาด ROI, polygon หลายชั้น, mask
* ฟีเจอร์ CV ใหม่ที่มีประโยชน์: โหมดไฟล์ภาพ/วิดีโอ, ตัววัดคุณภาพภาพที่ดีกว่า, รายงาน metrics
* โครงสร้างโค้ดภายใน `cv/**` ทั้งหมด
**เงื่อนไขเดียว:** ผลที่ส่งเข้า backend ต้องยังเป็น evidence ต่อเฟรมตามสัญญา C1 (`cls`, `conf`, `in_seat`, `in_table`, `seat_overlap`, `table_overlap`, `bbox`) — ถ้าวิธีใหม่ของคุณให้ข้อมูลที่ฟิลด์เดิมแสดงไม่ได้ (เช่น ความน่าจะเป็นว่านั่ง) ให้เขียน CR ขอฟิลด์เพิ่มแบบ optional

## สิ่งที่ต้องคุยก่อน (🟡 YELLOW / 🔴 RED)
* ต้องการ seat ID หรือกล้องใหม่ใน backend (เช่น `LAB5`, กล้องที่สอง) → CR ถึง P2 (YELLOW)
* ให้ CV seat แสดงบนผังนักศึกษา (PA-03) → **RED** ต้องทั้งทีมอนุมัติ
* เปลี่ยน key ใน `latest_run.json` ที่หน้า CV Lab อ่าน → แจ้ง P3 (YELLOW)
* ต้องการเปลี่ยนกฎใน `services/api/app/engine/*` (threshold/การตัดสิน) → CR ถึง P2 — **ห้ามแก้เอง**

## ห้าม
* แทนที่ backend ร่วม หรือส่ง "สถานะสุดท้าย" แทน evidence
* เขียนฐานข้อมูล production/demo โดยตรง (ส่งผ่าน `POST /api/ingest/observations` + `X-Device-Token` เท่านั้น)
* ประดิษฐ์ schema API ที่ไม่เข้ากัน
* อ้างความแม่นยำที่ไม่ได้วัด / ใช้ภาพที่ไม่ได้รับอนุญาต / commit ภาพบุคคล วิดีโอ หรือ weights
* เขียนลง `evidence/` (V2 FROZEN) — ใช้ `artifacts/cv/` หรือ `evidence/team_v3/cv/`

## งานเรียงตามลำดับความสำคัญ
| # | งาน | ระดับ | ผลลัพธ์ที่ตรวจได้ |
|---|---|---|---|
| M1 | ย้ายผล CV ออกจาก `evidence/cv/` (คู่กับ PA-01 ของ P2) — issue #3 | YELLOW | รัน suite แล้ว `git status` ไม่มีไฟล์ใน `evidence/` เปลี่ยน; หน้า CV Lab ยังแสดงผลล่าสุด |
| M2 | เพิ่มโหมด input ไฟล์ภาพ/วิดีโอ (ให้ตรงกับ docstring ที่สัญญาไว้) + ไม่บันทึกเฟรมดิบโดยค่าเริ่มต้น | GREEN | `run_cv.py --help` แสดงโหมดใหม่; test |
| M3 | Evidence record มาตรฐาน (PA-04) ต่อเฟรม/ที่นั่ง + replay ได้ | GREEN (ไฟล์ของคุณ) | JSONL + schema + test |
| M4 | `tests/test_cv_v3.py`: payload ที่โค้ดคุณสร้าง validate กับโมเดล `IngestIn`; sample ได้ `applied`, ส่งซ้ำได้ `duplicate` | GREEN | pytest ผ่าน (issue #5) |
| M5 | ฉากจริง + ROI calibrate + ground truth + metrics (issue #4) — **ทำได้เมื่อได้รับอนุญาต (#14)** | GREEN (ภายใน) | `cv/experiments/<YYYYMMDD>_<scene>/` README + ROI + GT CSV + metrics |
| M6 | นั่ง vs ยืน / occlusion / walk-by: ทดลองวิธีที่ดีกว่า hip-anchor (เช่น pose) และเทียบผลกับวิธีเดิมบนคลิปเดียวกัน | GREEN | ตารางเทียบพร้อม N |
| M7 | CiRA CORE (ถ้าบังคับ, #15): adapter แยก + เทียบกับ YOLO11n บนข้อมูลเดียวกัน | GREEN | รายงานเทียบ |
ถ้า #14 ยังไม่ได้รับอนุญาต: ทำ M1–M4, M6 บนภาพ/คลิปที่อนุญาตได้ (เช่น ฉากที่สมาชิกทีมจัดเองและยินยอม) หรือสื่อสาธารณะที่ license อนุญาต — และรายงาน "ความแม่นยำบนที่นั่งห้องสมุดจริง: BLOCKED"
