# P1 · 04 — Roadmap การพัฒนา (Computer Vision)

> Gate G0–G5 เป็นของทั้งทีม (วันที่จริง P4 กำหนด) — ทำตามลำดับนี้เพื่อไม่ให้ใครรอคุณ และคุณไม่ต้องรอใครเกินจำเป็น

## G0 — Baseline (วันแรก)
- [ ] clone, `git switch feature/v3-cv`, `git merge origin/main`
- [ ] `.venv\Scripts\python -m pytest -q` → บันทึกผลจริง (ควร 53 passed)
- [ ] สร้าง `.venv-cv` ตาม `cv/requirements-cv.txt` (torch CPU) และวาง weights ใน `cv/models/` (git-ignored)
- [ ] เปิดเซิร์ฟเวอร์ (`scripts\start_demo_windows.ps1`) แล้วรัน `.venv-cv\Scripts\python cv\run_cv.py suite --post` → ดูผลที่หน้า CV Lab
- [ ] ⚠ คำสั่งนี้ยังเขียน `evidence/cv/` (FROZEN) → หลังรัน `git restore evidence/` (คืนไฟล์ที่ถูกแก้) และย้ายไฟล์ใหม่ที่ `git status` แสดงเป็น untracked ใน `evidence/cv/` ไปไว้ `artifacts/cv/` ด้วยมือ (อย่า commit) — จนกว่าจะทำ M1 เสร็จ
- [ ] ส่งเรื่องขออนุญาตฉากจริง (#14) และคำถาม CiRA CORE (#15) ผ่าน P4

## G1 — Contract smoke (ก่อนพัฒนาหนัก)
- [ ] อ่านสัญญา C1 (`05_INTEGRATION_CONTRACT.md`) และ `docs/api_contract_v3.md` เมื่อ P2 merge
- [ ] ส่ง sample 1 เฟรมเข้า `CV-LAB` แล้วได้ `applied`; ส่งซ้ำได้ `duplicate`; ส่งเวลาเก่ากว่าได้ `late` → เก็บ request/response จริงไว้ใน PR
- [ ] เปิด CR สำหรับสิ่งที่ต้องการจาก P2 (PA-01 และถ้าต้องการ seat/กล้องใหม่)

## G2 — Module complete (ทำอิสระบน branch ตัวเอง)
- [ ] M1 ย้ายผลไป `artifacts/cv/` (+ อ่าน env ที่ตกลงกับ P2) — `git status` สะอาดหลังรัน
- [ ] M2 โหมดไฟล์ภาพ/วิดีโอ (ไม่เก็บเฟรมดิบโดยค่าเริ่มต้น)
- [ ] M3 evidence record (PA-04) + replay
- [ ] M4 `tests/test_cv_v3.py` (ไม่ต้องใช้ torch — test ต้องรันใน `.venv` ปกติและใน CI ได้; แยกส่วนที่ต้องใช้โมเดลออก หรือ skip อย่างมีเหตุผลเมื่อไม่มี ultralytics)
- [ ] M5 ฉากจริง/คลิปที่อนุญาต → ROI → GT → metrics (ถ้า #14 อนุมัติ) / หรือรายงาน BLOCKED
- [ ] M6 ทดลองวิธีแยกนั่ง/ยืน/เดินผ่าน/บังบางส่วน และเทียบกับวิธีเดิมบนข้อมูลชุดเดียวกัน
- [ ] M7 CiRA CORE (ถ้าบังคับ)
- [ ] เปิด PR (`.github/pull_request_template.md`) + ผล `check_ownership.py --owner P1 --base origin/main`

## G3 — Integration (P4 นำ)
- [ ] ตอบ comment/Issue จาก P4 ภายใน 1 วัน; แก้บน branch ตัวเอง (owner-led)
- [ ] ถ้า P4 ทำ adapter ชั่วคราวให้ evidence ของคุณ — ตรวจว่าแปลงความหมายถูก แล้ววางแผนแก้ถาวร

## G4–G5 — Stabilize & release
- [ ] แก้บั๊กเท่านั้น; ไม่เพิ่มฟีเจอร์ 24 ชม. ก่อนนำเสนอ
- [ ] หลักฐานสุดท้ายใน `evidence/team_v3/cv/` (metrics, ตัวอย่าง event, log — ไม่มีภาพบุคคล) + บรรทัดในรายงานว่า REAL/SIMULATED/BLOCKED อะไร
- [ ] สไลด์ส่วน CV: ตัวเลขทุกตัวมาจากไฟล์หลักฐาน มี N และข้อจำกัด

## สิ่งที่ทำได้ทันทีโดยไม่ต้องรอใคร
M2, M3, M4, M6 (บนภาพ/คลิปที่อนุญาต) — ทั้งหมดอยู่ใน `cv/**` และ `tests/test_cv_v3.py` ของคุณ
