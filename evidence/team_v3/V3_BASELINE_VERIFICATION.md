# V3 baseline verification — 15 ต.ค. 2569 (Person 4 / QA)

ตรวจซ้ำว่า V2 ที่ commit เป็น `v2-demo-baseline` (`45a61d9`) ยังทำงานได้ก่อนเริ่ม Team Sprint V3.
เครื่อง: Windows 11 (build 26300), Python 3.10.11, Node 24.11.0, Microsoft Edge (Playwright channel `msedge`).

| การตรวจ | คำสั่ง | ผลจริง | เวลา |
|---|---|---|---|
| Backend tests | `.\.venv\Scripts\python.exe -m pytest -q` | **53 passed, 0 failed, 0 errors** (31.0 s) | 2026-10-15 16:37 ICT |
| Frontend build | `cd apps\web; npm run build` | ✓ built | 16:37 ICT |
| Browser e2e (เซิร์ฟเวอร์ :8000) | `cd apps\web; npx playwright test` | **8 passed, 0 failed, 0 flaky** (164.9 s) | เริ่ม 16:39 ICT |
| **Fresh clone** (ไม่พึ่งไฟล์ที่ถูก ignore) | `git clone` → `py -3.10 -m venv .venv` → `pip install -r services\api\requirements.txt` → `pytest -q` → `npm ci` → `npm run build` | clone 132 ไฟล์; pip OK; **53 passed**; `npm ci` 95 packages; ✓ built | 16:4x ICT |
| Ownership coverage | `python scripts/check_ownership.py --audit` | ทุกไฟล์ที่ track มีเจ้าของ 1 ราย, ไม่มีไฟล์ห้าม commit | ดู TEAM_SETUP_REPORT |

## ปัญหาที่พบระหว่างตรวจ (ยังไม่แก้ — เป็นงาน sprint แรก)
1. **การรัน e2e เขียนทับไฟล์ V2 ที่ freeze** — หลัง `npx playwright test` มีไฟล์ที่ commit แล้วเปลี่ยน 23 ไฟล์ (`evidence/playwright_results.json` + `presentation/screenshots/*.png` 22 ภาพ) → กู้คืนด้วย `git restore evidence/playwright_results.json presentation/screenshots/`. ทางแก้ถาวร (P4): ให้ config/spec เขียนผลไป `apps/web/test-results/` หรือ `evidence/team_v3/` เว้นแต่ตั้ง env ตั้งใจเก็บหลักฐาน
2. **`cv/run_cv.py` เขียนผลลง `evidence/cv/`** (frozen) และ API อ่าน `evidence/cv/latest_run.json` สำหรับหน้า CV Lab → ต้องตกลงตำแหน่งใหม่ระหว่าง P1 (runner) และ P2 (`settings.cv_evidence_dir`)
3. **Clone ไปยัง path ยาว ~195 ตัวอักษรล้มเหลว** `fatal: … Filename too long` (Git for Windows ยังไม่ได้ตั้ง `core.longpaths`) → ทุกคนตั้ง `git config --global core.longpaths true` และ clone ไว้ใน path สั้น เช่น `C:\dev\smart-library-next`

ข้อมูลที่นั่งในการทดสอบทั้งหมดเป็น SIMULATION; ไม่มีการรัน CV ใหม่ในรอบนี้
