# P4 — Test-artifact isolation: verification (15 ต.ค. 2569)

**ปัญหาเดิม (ยืนยันจริง):** การรัน `npx playwright test` หนึ่งครั้งบน V2 baseline ทำให้ไฟล์ที่ commit แล้วเปลี่ยน **23 ไฟล์** (`evidence/playwright_results.json` + `presentation/screenshots/*.png` 22 ภาพ) และสคริปต์หลายตัวเขียนลง `evidence/`, `presentation/` เป็นค่าเริ่มต้น

**หลังแก้ (branch `feature/v3-staff-qa`):**

| การตรวจ | ผลจริง |
|---|---|
| `scripts\run_tests_windows.ps1` (เซิร์ฟเวอร์ :8000) | exit 0 · pytest **70 passed** · Playwright **8 passed, 0 failed, 0 flaky** · `frozen-clean: OK` |
| `git diff --name-only HEAD -- evidence presentation verification reference templates` หลังรัน | **0 ไฟล์** |
| ผลที่สร้าง | `artifacts/e2e/playwright_results.json` + screenshot 22 ภาพใน `artifacts/e2e/screenshots/` (ไม่ถูก commit — `git check-ignore` ยืนยัน) |
| `tests/test_artifact_isolation.py` กับโค้ดเดิม (ก่อนแก้) | **6 failed** (ตรวจเจอปัญหาจริง) โดยไม่มีไฟล์ frozen ถูกแตะระหว่างทดสอบ |
| `tests/test_artifact_isolation.py` กับโค้ดที่แก้ | **17 passed** |
| `export_pptx_preview.ps1 -OutDir presentation\preview` | ถูกปฏิเสธ (exit 1) ก่อนเปิด PowerPoint |

ไฟล์ในโฟลเดอร์นี้คัดลอกจากผลรันจริง (`artifacts/`) เพื่อเป็นหลักฐาน: `pytest_junit.xml`, `playwright_results.json` (Playwright เริ่ม 2026-10-15T13:37:53Z)

**ข้อสังเกตระหว่างตรวจ (บัคของการทดสอบเอง — แก้แล้ว):** รุ่นแรกของ `test_build_pptx_refuses_frozen_deck_without_flag` เรียก `build_pptx.py presentation/progress_update_v2.pptx`; เมื่อทดลองรันกับโค้ด**เดิม** (ไม่มี guard) สคริปต์เขียนทับ deck V2 จริง → `--frozen-clean` จับได้ทันที → กู้คืนด้วย `git restore` (ตรวจแล้วไม่มี diff) และเปลี่ยน test ให้ใช้ไฟล์ probe ที่ไม่มีอยู่จริง

**ยังไม่ได้แก้ (นอกขอบเขต P4):** `cv/run_cv.py` ยังเขียน `evidence/cv/` — เป็นของ P1 (Issue “Move CV run output out of frozen evidence/cv/”)
