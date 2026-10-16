# P3 · 02 — ภารกิจที่ได้รับมอบหมาย (Student Frontend)

**Branch:** `feature/v3-student` · **Label:** `person-3-frontend` · **Issues:** #6, #7, #8

## ภารกิจ
เป็นเจ้าของแอปฝั่งนักศึกษา: ทำให้นักศึกษา **หาที่นั่งได้เร็วและเข้าใจถูกต้องว่าข้อมูลเชื่อได้แค่ไหน** — บนมือถือ คีย์บอร์ด และเมื่อข้อมูลเปลี่ยนแบบ realtime

## เป้าหมาย
1. ปรับปรุง Floor Map
2. ปรับปรุงการค้นหาที่นั่ง (seat discovery)
3. ปรับปรุง StudyMatch และ GroupFit
4. ปรับปรุงการนำทางและการใช้งาน
5. รับมือการอัปเดตแบบ realtime
6. แสดง **แหล่งข้อมูล (SIMULATION / CV)** และ **ความสด** อย่างถูกต้อง
7. รองรับการใช้งานบนมือถือ

## สิ่งที่ทำได้อิสระ (🟢 GREEN)
* **redesign UI/UX ได้มาก** — layout, สี, ตัวอักษร, การจัดหน้า, interaction, animation, onboarding
* ฟีเจอร์ฝั่งนักศึกษาใหม่ที่ใช้ API เดิม (เช่น มุมมองรายการ, ตัวกรองแบบใหม่, ค้นหาด้วยข้อความ, บันทึกความชอบในเครื่อง)
* ประสบการณ์แนะนำที่นั่งแบบใหม่ — ตราบใดที่ใช้ผลจาก `/api/recommendations` และกฎแสดงผล C2
* วาดโซน/ผังจากข้อมูล `/api/layout` แทนการ hard-code (PA-08)
* โครงสร้าง component ภายใน, state management, การทดสอบของคุณ

## สิ่งที่ต้องคุยก่อน (🟡 / 🔴)
* ต้องการ field/endpoint ใหม่จาก backend → CR ถึง P2 (YELLOW)
* แก้ `apps/web/src/live.tsx` (P4 ร่วมอนุมัติ — มี guard BUG-011), `package.json`/`package-lock.json` (P4 ร่วมอนุมัติ), `pages/CvLab.tsx` (P1 ร่วมอนุมัติ) (YELLOW)
* เปลี่ยน/ลบ `data-testid` ที่ e2e ใช้ (YELLOW — แจ้ง P4 และแก้ e2e พร้อมกัน)
* แสดงข้อมูล CV บนผังนักศึกษา (PA-03) (**RED** — ต้องทั้งทีม)

## ห้าม
* สร้างฐานข้อมูลหรือ backend แยก (รวมถึงเก็บสถานะที่นั่ง "ของตัวเอง" แทน backend)
* เปลี่ยน schema API แบบเงียบ ๆ หรือเรียก endpoint ที่ไม่อยู่ในสัญญา
* แสดงข้อมูลจำลองว่าเป็นข้อมูลจริง / ทำให้ที่นั่งเสี่ยงดูเป็น "ว่าง" / แสดง `rank_score` เป็น %
* แก้ `StaffConsole.tsx`, `ScenarioLab.tsx`, `SeatCheckPanel.tsx`, e2e ของ P4, `playwright.config.ts`, `services/**`, `cv/**`, ไฟล์ FROZEN

## งานเรียงตามลำดับความสำคัญ
| # | งาน | ระดับ | ผลลัพธ์ที่ตรวจได้ |
|---|---|---|---|
| S1 | ป้ายแหล่งข้อมูล + ความสดบนการ์ด/รายละเอียด/ผัง: `SIMULATION` vs `CV`, อายุข้อมูลจาก `server_time_utc`, สถานะกล้อง — ไม่ให้ unknown/stale/offline/pending ดูเป็นว่าง (#6) | GREEN | e2e + screenshot ก่อน/หลัง |
| S2 | มือถือ (360–390 px ไม่มี horizontal scroll ทั้งหน้า), คีย์บอร์ด, ข้อความ empty/error ที่ชัด | GREEN | e2e |
| S3 | ปรับ StudyMatch/GroupFit/Wayfinder ให้เข้าใจง่ายขึ้น (เหตุผล, ข้อเสนอผ่อนเงื่อนไข, ความไม่แน่นอนของเส้นทาง) — ไม่อ้างเกินจริง | GREEN | e2e |
| S4 | PA-08: วาดโซนจาก `/api/layout` (รองรับโซนใหม่ในอนาคต) — ผลลัพธ์บนหน้าจอเดิมต้องเหมือนเดิมกับข้อมูลสาธิต | GREEN | e2e เดิมผ่าน + screenshot |
| S5 | `apps/web/e2e/student_v3.spec.ts`: เงียบ+ปลั๊ก → เหตุผล → GroupFit → Wayfinder → SeatCheck → อัปเดตผ่าน WS โดยไม่ reload (#8) | GREEN | spec ผ่านร่วมกับ 8 ตัวเดิม |
| S6 | PR-B: ใช้ `SeatCheckPanel` ของ P4 ใน `SeatDetail.tsx` หลัง PR-A merge (#7) — `data-testid` เดิมครบ | YELLOW (ไฟล์ร่วม) | `demo.spec.ts` + `reliability.spec.ts` ผ่าน |
| S7 | ปรับ `api.ts` types ให้ตรง `docs/api_contract_v3.md` เมื่อ P2 merge (เพิ่ม field ที่ขาด เช่น `age_s`, `floor`) | GREEN | `npm run build` ผ่าน |
| S8 | (ถ้าทีมอนุมัติ PA-03) แสดงที่นั่ง CV จริงบนผัง พร้อมป้าย CV/model | RED | e2e |
