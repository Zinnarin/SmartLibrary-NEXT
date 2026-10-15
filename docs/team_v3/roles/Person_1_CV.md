# PERSON 1 — Computer Vision / ROI Owner

**ความรับผิดชอบ:** ตรวจคน/สิ่งของในบริเวณที่นั่งจากภาพหรือวิดีโอที่ได้รับอนุญาต และผลิต evidence ที่ Backend ตัดสินสถานะต่อได้ ไม่ใช่สร้างหน้าเว็บ/ฐานข้อมูลใหม่.

**ไฟล์หลัก**: `cv/run_cv.py`, `cv/roi.py`, `cv/roi_config.json`, `cv/ROI_CALIBRATION_GUIDE_TH.md`; เพิ่ม `cv/experiments/*`, `tests/test_cv_v3.py` (หลังตรวจชื่อไฟล์จริง).

**สิ่งที่มีอยู่:** YOLO11n ตรวจภาพ `bus.jpg` ของ Ultralytics, 4 hand-drawn ROI. **ยังไม่ใช่ seat occupancy validation**.

**งานที่จะทำต่อ:**
1. ตกลงกับอาจารย์/กลุ่มว่า CiRA CORE บังคับหรือเป็นแค่เครื่องมือเสนอไว้; หากต้องใช้ ให้ศึกษาทางออกผล detection และทำ adapter ทดลอง แต่อย่าแทน YOLO ที่ทำงานอยู่ทันที.
2. จัดฉาก 2–4 เก้าอี้ + โต๊ะ + ผู้ร่วมทดลองยินยอม; แยกคลิป `empty`, `seated`, `walk_by`, `standing_near`, `belongings`.
3. วาด ROI ของ seat และ belongings zone ให้ตรงภาพจริง + map seat ID; ทดลอง quality gate และ temporal model.
4. สร้าง ground truth ต่อช่วงเวลาและ confusion matrix / false available / unknown coverage ตามข้อมูลที่มีจริง; ข้อมูลน้อยต้องระบุ N.
5. ส่ง schema-compatible events สู่ CV-LAB ผ่าน API ของ Person 2 (ห้ามแก้ backend เอง).

**ต้องส่ง:** `roi_config` สำหรับฉากจริง, source+consent log (ไม่แนบภาพบุคคลใน Git), inference logs (ลบข้อมูลส่วนบุคคล), sample event JSON ที่ผ่าน endpoint, metrics/limitations, tests.

**ผ่านเมื่อ:** 1 คลิปจริงที่ได้รับอนุญาตไหลผ่าน YOLO/CiRA→adapter→ingest API, Person 2 ยืนยัน status และ log; พบเดินผ่านต้องไม่ถูกยืนยันเป็นคนนั่งโดยไม่มีหลักฐาน. ถ้ายังไม่ผ่านต้องรายงาน BLOCKED และ cause.
