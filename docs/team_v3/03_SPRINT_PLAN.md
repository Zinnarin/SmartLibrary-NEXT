# แผนพัฒนาร่วมกัน 1 รอบ (ตัวอย่าง 5–7 วัน; ปรับตามตารางเรียน)

## Day 0 — Freeze baseline & kickoff (30–45 นาที)
- คนที่ 4 เปิด V2 demo, แจกงาน, ตั้ง Git Repository; ยืนยันทั้งกลุ่มว่าผลงานเดิมเป็น shared baseline และเครดิตตามงานจริง.
- คนที่ 2 `git ls-files` ตรวจ paths, freeze API contract, run pytest.
- คนที่ 3 run Playwright / start web; คนที่ 1 run CV suite ของ V2 พร้อมอธิบายข้อจำกัด `bus.jpg`.
- ตกลงว่าจะใช้ **YOLO11n, CiRA CORE หรือ benchmark เทียบกัน**; ถ้าอาจารย์บังคับ CiRA ต้องศึกษาการ export/integration ก่อนเปลี่ยน.

## Day 1–2 — Build in parallel, without shared-file conflicts
- P1: จัดฉากที่นั่งจริง (ได้รับอนุญาต), define ROI, ground-truth plan, เก็บ sample clips โดยไม่เผยแพร่ภาพบุคคลโดยไม่ได้รับอนุญาต.
- P2: พิมพ์ contract `/api/ingest` จากของจริง, backend hardening/test; เตรียม staging CV-LAB.
- P3: ตรวจ student UX บนมือถือ, source/freshness UI, สร้าง tests แยกไฟล์.
- P4: ปรับ staff workflow/SeatCheck review UX, tests camera/server loss, test evidence.

## Day 3 — First integration gate (อย่ารอวันสุดท้าย)
- P1 ส่ง **sample payload + actual inference log**; P2 ตรวจ accepted/rejected outcome และ test.
- P2 publish test API and contract; P3/P4 เช็ก client ทุกหน้า.
- P4 ใช้ `main` หรือ integration branch รวม PR ที่ผ่านทีละอัน และ re-run baseline.

## Day 4 — Quality + cross-person review
- ทุกคนสร้าง PR แยก; คู่ review: P1 ↔ P2 (CV/ingest), P3 ↔ P4 (UI/staff), P4 ดู CI/quality ทั้งหมด.
- ทดสอบ real staged scene (ถ้าได้รับอนุญาต): empty/sit/stand/walk-by/bag, tag unknown correctly, save ground truth metrics if possible.
- P4 ทดสอบ end-to-end (student→staff→status) และ fault injection + screenshots.

## Day 5–7 — Stabilize + evaluation + presentation
- ปิด merge feature 24 ชั่วโมงก่อนนำเสนอ, เหลือ bug fixes เท่านั้น.
- รัน scripts `run_tests_windows.ps1` + browser E2E + CV test บนเครื่องที่นำเสนอ.
- ผลงานรวม: demo + scenario mode แยกจาก real CV + PDF/PPTX + evidence + ใครทำอะไร.
- หาก real seat accuracy ยังไม่มี: รายงาน `BLOCKED` หรือข้อจำกัด ไม่เติมเลขเดา.

## Daily stand-up ใช้เวลา 10 นาที
ทุกคนส่ง 4 บรรทัดในแชทกลุ่มทุกเย็น: `(1) เมื่อวานทำอะไรและ commit/PR (2) วันนี้จะทำอะไร (3) ติดอะไร/ต้องการ API จากใคร (4) หลักฐาน/ผลทดสอบ`.

## Sprint goals
- **P1:** 1 controlled, authorized chair-based CV experiment with dated log, not bus.jpg as final proof
- **P2:** frozen API + integration/regression tests passing
- **P3:** student UX responds correctly to simulated and lab CV metadata; accessible/reliable
- **P4:** Staff/SeatCheck end-to-end and failure-safety tests + integrated demo + evidence

**Success ไม่เท่ากับทุก feature ต้องเสร็จ:** ถ้าอุปกรณ์/permission ไม่พร้อม ให้ส่ง demo ที่จริงและ stable พร้อม blocker list.
