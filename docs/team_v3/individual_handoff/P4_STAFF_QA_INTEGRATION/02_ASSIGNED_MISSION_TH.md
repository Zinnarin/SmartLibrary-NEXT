# P4 · 02 — ภารกิจที่ได้รับมอบหมาย (Staff, QA & Integration)

**Branch:** `feature/v3-staff-qa` (+ branch ย่อย เช่น `feature/v3-staff-qa-seatcheck`) · **Label:** `person-4-qa`, `integration` · **Issues:** #9–#15

## ภารกิจ
เป็นเจ้าของ Staff Console, workflow SeatCheck, การทดสอบความทนทาน, integration tests, integration adapters และการตรวจรับระบบขั้นสุดท้าย — **รวมงานทั้ง 4 โมดูลให้เป็นระบบเดียวที่ทำงานจริง** โดยรักษาความสามารถของ V2 และรักษางานของเพื่อนแต่ละคนไว้ให้มากที่สุด

## เป้าหมาย
1. ปรับปรุงงานของเจ้าหน้าที่ (Staff operations)
2. ตรวจรายงานของผู้ใช้
3. จัดการสถานะที่ผิด (override ที่ความหมายถูกต้อง)
4. ทดสอบสถานการณ์ล้มเหลว (กล้องหาย, เซิร์ฟเวอร์ล่ม, WS หลุด, ข้อมูลเก่า, รายงานซ้ำ/spam, token ผิด)
5. รักษาความสามารถของ V2
6. รวมโมดูลของทีม
7. สร้างเดโมสุดท้ายและหลักฐานการทดสอบ

## สิ่งที่ทำได้อิสระ (🟢 GREEN)
* ปรับ Staff Console (`StaffConsole.tsx`) ทั้ง UI และ workflow โดยใช้ API เดิม (C3) — เช่น เรียงคิวรายงาน, แท็บอุปกรณ์จาก `GET /api/admin/devices` (มี API แล้วแต่ UI ยังไม่ใช้), ตัวกรอง audit log
* เพิ่ม test ทุกชนิดในไฟล์ของคุณ (e2e, contract, reliability, fault injection)
* `scripts/*`, CI (`.github/*` — แจ้งเจ้าของที่ได้รับผล), เอกสารทีม, runbook, สไลด์ V3 ใน `presentation/v3/`
* adapter ใน `integration/**` (แปลงรูปแบบเท่านั้น)

## สิ่งที่ต้องคุยก่อน (🟡 / 🔴)
* `SeatCheckPanel.tsx` (P3 ร่วมอนุมัติ — PA-05) · `ScenarioLab.tsx` (P2 ร่วมอนุมัติ) · `tests/test_reliability.py`, `pytest.ini`, `scripts/start_demo_windows.ps1` (P2 ร่วมอนุมัติ) · `playwright.config.ts` (P3 ร่วมอนุมัติ)
* ต้องการ API/field ใหม่สำหรับ Staff (เช่น ตัวตนเจ้าหน้าที่จริง) → CR ถึง P2
* เปลี่ยน CI ให้เข้มขึ้น (เช่น บังคับ check ใหม่) → แจ้งทุกคน

## ห้าม
* เขียนทับ implementation ภายในของคนอื่นโดยไม่ตกลง (`cv/**`, `services/**`, หน้า Student)
* merge PR ที่ไม่ผ่าน gate · ลด/ลบ test เพื่อให้ผ่าน · ทำให้ CI ดูเขียวโดยข้ามการตรวจ
* force-push `main` · ทำ repo เป็น public · แต่งผล

## งานเรียงตามลำดับความสำคัญ
| # | งาน | ระดับ | ผลลัพธ์ที่ตรวจได้ |
|---|---|---|---|
| Q1 | Merge PR #16 (artifact isolation) หลัง P3 approve — แล้วยืนยันบน main ว่า `run_tests_windows.ps1` จบด้วย `frozen-clean: OK` (#9) | GREEN (PR ของคุณ) + approval P3 | log หลัง merge |
| Q2 | Smoke C1–C4 บนทุก PR ตาม playbook ข้อ 5 (คำสั่งตรวจแล้วว่าใช้ได้จริง 16 ต.ค.) | GREEN | ผลใน PR comment |
| Q3 | PR-A `components/SeatCheckPanel.tsx` (PA-05): ย้ายตรรกะฟอร์มจาก `SeatDetail.tsx` มาเป็น component ใหม่ พฤติกรรม/`data-testid` เดิม — ยังไม่มีใครเรียกใช้ (#10) | YELLOW (props ตกลงกับ P3) | build + e2e เดิมผ่าน |
| Q4 | Override semantics (#11): ค่าเริ่มต้นตอนยืนยัน "มีคนนั่ง" = `unknown` (รอตรวจ), ปรับข้อความให้ตรงความหมาย; maintenance = ซ่อม/ทำความสะอาด | GREEN (ไฟล์ของคุณ) + แจ้ง P3 | e2e ใหม่ครอบคลุม |
| Q5 | `apps/web/e2e/staff_reliability_v3.spec.ts` (#12): report → pending → staff review + เหตุผล → override → WS อัปเดตหน้านักศึกษา; รายงานซ้ำ/rate limit; staff token ผิด; override หมดอายุ; เซิร์ฟเวอร์ล่มไม่โชว์เขียวค้าง | GREEN | spec ผ่านร่วมกับของเดิม |
| Q6 | `tests/test_contract_v3.py`: ตัวอย่างจริงใน `contract_examples/` เทียบ response สด (key/type/status/enum) | GREEN (+P2 review) | pytest ผ่าน; จับการเปลี่ยนสัญญาเงียบได้ |
| Q7 | Staff operations: แท็บอุปกรณ์ (`/api/admin/devices`: `last_seen_age_s`, `last_quality`), คิวรายงานเรียงตามอายุ, แสดง `display_state_at_report` | GREEN | e2e/screenshot |
| Q8 | `integration/smoke/` (สคริปต์ smoke ซ้ำได้) และ `integration/adapters/` (เมื่อจำเป็นเท่านั้น) | GREEN | รันได้ + test |
| Q9 | CODEOWNERS + นโยบาย merge (#13) เมื่อได้ username ครบ | GREEN | `.github/CODEOWNERS` |
| Q10 | Integration + evidence: รวมตาม playbook, `evidence/team_v3/integration/INTEGRATION_LOG.md`, `verification/TEAM_V3_ACCEPTANCE.csv`, `evidence/team_v3/final/`, release notes, tag `v3-integrated-demo` | GREEN | FA-01…FA-52 |
| Q11 | เดโม: runbook V3 (`docs/DEMO_RUNBOOK_TH.md`), สไลด์/สคริปต์ใน `presentation/v3/` (ห้ามเขียนทับ V2) — ทุกตัวเลขมาจากหลักฐาน | GREEN | ซ้อมจับเวลา |
| Q12 | ประสานอาจารย์: การอนุญาตฉาก/ฟุตเทจ/ผังจริง (#14), CiRA CORE (#15) | — | คำตอบบันทึกใน Issue |
