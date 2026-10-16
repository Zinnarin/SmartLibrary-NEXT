# TEAM AI ASSISTANT GUIDE — ใช้ AI ช่วยพัฒนาอย่างปลอดภัย (ใช้ได้กับทุกเครื่องมือ)

> ใช้ได้กับ ChatGPT, Gemini, Claude, GitHub Copilot, เครื่องมืออื่น หรือเขียนเองล้วน ๆ — **ไม่จำเป็นต้องใช้ Claude Code**
> หลักสำคัญ: **AI ส่วนใหญ่มองไม่เห็นไฟล์ในเครื่องคุณ** ต้องแนบ/วางเนื้อหาให้เอง และ **คุณเป็นคนรับผิดชอบโค้ดที่ส่ง** ไม่ใช่ AI

## 1. ใช้ AI ให้เข้าใจโปรเจกต์ก่อนเขียนโค้ด
1. เริ่มจากให้ AI อ่าน **ภาพรวม + งานของคุณ** (ข้อ 2) แล้วถามให้สรุปกลับว่า: โมดูลของคุณรับ/ส่งข้อมูลอะไร, ไฟล์ไหนเป็นของคุณ, อะไรห้ามแก้
2. ถามทีละเรื่องเล็ก ๆ เช่น "ฟังก์ชัน `classify()` ตัดสินสถานะตามลำดับอย่างไร" แล้ว **เปิดไฟล์จริงตรวจคำตอบ** — AI อาจเดาผิดเมื่อไม่ได้เห็นโค้ด
3. ถ้า AI อ้างไฟล์/ฟังก์ชันที่คุณหาไม่เจอใน repo → ถือว่าผิด จนกว่าจะยืนยันได้

## 2. เอกสารที่ควรให้ AI (แนบไฟล์ หรือคัดลอกเนื้อหาไปวาง)
**ทุกคน (ชุดพื้นฐาน):**
* `docs/team_v3/individual_handoff/SHARED_V3/00_PROJECT_OVERVIEW_TH.md` — ภาพรวม
* `docs/team_v3/individual_handoff/P#_…/02_ASSIGNED_MISSION_TH.md` — ภารกิจของคุณ
* `docs/team_v3/individual_handoff/P#_…/03_EXISTING_CODE_AND_OWNERSHIP.md` — ไฟล์ของคุณ/ไฟล์ห้ามแก้
* `docs/team_v3/individual_handoff/P#_…/05_INTEGRATION_CONTRACT.md` — สัญญาที่ต้องรักษา (ยาว: ถ้าเครื่องมือรับไม่ไหว ให้ส่งเฉพาะหัวข้อที่เกี่ยว เช่น C1 สำหรับ P1)
**เพิ่มตามบทบาท (ไฟล์โค้ดหลัก):**
| คน | ไฟล์โค้ดที่ควรแนบเมื่อทำงาน |
|---|---|
| P1 CV | `cv/run_cv.py`, `cv/roi.py`, `cv/roi_config.json`, (อ่านอย่างเดียว) `services/api/app/engine/evidence.py`, `services/api/app/engine/state_engine.py`, `services/api/app/engine/config.py` |
| P2 Backend | `services/api/app/main.py`, `services/api/app/services.py`, `services/api/app/engine/trust.py`, `services/api/app/db.py` + ไฟล์ที่กำลังแก้ + test ที่เกี่ยว (`tests/test_api.py`) |
| P3 Student | `apps/web/src/api.ts`, `apps/web/src/live.tsx`, ไฟล์หน้า/คอมโพเนนต์ที่กำลังแก้ (เช่น `apps/web/src/components/FloorMap.tsx`), ตัวอย่าง JSON จริงใน `SHARED_V3/contract_examples/C2__*.json` |
| P4 Staff/QA | `apps/web/src/pages/StaffConsole.tsx`, `apps/web/src/components/SeatDetail.tsx`, `apps/web/e2e/*.spec.ts`, `tests/test_reliability.py`, `FINAL_INTEGRATION_PLAYBOOK_TH.md` |
> ตัวอย่าง request/response **จริง** อยู่ใน `docs/team_v3/individual_handoff/SHARED_V3/contract_examples/` — ส่งให้ AI แทนการให้มันเดารูปแบบ JSON

## 3. ให้ AI เห็นไฟล์ซอร์สของคุณ
* **แชท AI บนเว็บ (ChatGPT/Gemini/Claude):** แนบไฟล์ หรือคัดลอกทั้งไฟล์ไปวาง พร้อมบอก path เต็ม เช่น "นี่คือ `apps/web/src/live.tsx` ทั้งไฟล์"
* **AI ใน editor (เช่น Copilot ใน VS Code):** เปิดไฟล์ที่เกี่ยวไว้ใน editor/อ้างไฟล์ในแชทของเครื่องมือนั้น — ตรวจให้แน่ใจว่ามันเห็นไฟล์ที่ถูก
* ส่งเฉพาะไฟล์ที่เกี่ยว อย่าส่งทั้ง repo; ถ้าไฟล์ยาวมาก ส่งเฉพาะฟังก์ชันที่เกี่ยวพร้อมบอกบรรทัด
* **ห้ามส่งให้ AI:** token/รหัส PIN/รหัสผ่าน, ฐานข้อมูล, ภาพ/วิดีโอบุคคล, ชื่อ-รหัสนักศึกษา, ไฟล์ `.env` — repo นี้เป็น private: ส่งเฉพาะสิ่งที่จำเป็นต่อคำถาม

## 4. ขอให้ AI ปรับปรุงโค้ด
* บอกเป้าหมาย 1 อย่างต่อครั้ง + ไฟล์ที่อนุญาตให้แก้ + สิ่งที่ห้ามเปลี่ยน (ใช้ prompt ในข้อ 9)
* ขอ **การเปลี่ยนแปลงน้อยที่สุด** และให้แสดงเป็น diff หรือโค้ดทั้งฟังก์ชันพร้อมบอกตำแหน่ง
* ขอให้ AI อธิบายว่าเปลี่ยนอะไร ทำไม และกระทบสัญญา (C1–C4) หรือไม่
* ขอ test ที่พิสูจน์การเปลี่ยนแปลงทุกครั้ง

## 5. ตรวจโค้ดที่ AI สร้าง (ห้ามข้าม)
1. อ่านทุกบรรทัดก่อนวาง — เข้าใจได้ไหม? เรียกฟังก์ชัน/field ที่มีอยู่จริงไหม (ค้นใน VS Code ด้วย Ctrl+Shift+F)
2. ชื่อ field/endpoint ตรงกับ `05_INTEGRATION_CONTRACT.md` และ `contract_examples/` ไหม
3. ไม่มีการลบ test, ลด assertion, ปิดการตรวจ, หรือ hard-code ผลให้ผ่าน
4. ไม่มีการเปลี่ยนข้อความ SIMULATION / การทำให้ที่นั่งเสี่ยงดูเป็น "ว่าง" / ตัวเลขความแม่นยำที่ไม่ได้วัด
5. ดู `git diff` ทั้งหมดก่อน commit — มีไฟล์ที่ไม่ได้ตั้งใจแก้ไหม

## 6. รัน test (ผลจริงเท่านั้น)
```powershell
.venv\Scripts\python -m pytest -q                                                 # backend: 0 failed
cd apps\web; npm run build; cd ..\..                                              # frontend build ผ่าน
powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1            # + browser tests (เปิดเซิร์ฟเวอร์ไว้)
.venv\Scripts\python scripts\check_ownership.py --owner P<#> --base origin/main   # ไม่มี BLOCK
```
* ถ้า AI บอกว่า "test ผ่านแล้ว" แต่คุณยังไม่ได้รันเอง → **ยังไม่ผ่าน**
* วางผลจริงลงใน PR; ห้ามแต่งผล

## 7. กันการเปลี่ยนแปลงที่ไม่ต้องการ
* ทำงานบน branch ของคุณเสมอ (`git branch --show-current`)
* commit ก่อนให้ AI แก้ชิ้นใหญ่ → ถ้าผลไม่ดี ย้อนได้ด้วย `git restore <ไฟล์>` (ยังไม่ commit) หรือ `git revert` (commit แล้ว)
* ถ้า AI แก้ไฟล์นอกความเป็นเจ้าของ → ไม่รับ; คืนด้วย `git restore <ไฟล์>`
* ไฟล์ FROZEN (`evidence/`, `presentation/`, `verification/`, `reference/`, `templates/`, เอกสาร spec ใน `docs/`) ห้ามแก้เด็ดขาด

## 8. รักษาความเข้ากันได้ของ API
* ห้ามลบ/เปลี่ยนชื่อ endpoint, field, ค่า enum (เช่น `available`/`occupied`/`reserved`/`unknown`, `source = "scenario"|"cv"`) และห้ามเปลี่ยนความหมาย
* เพิ่มได้เฉพาะแบบ **optional** และต้องผ่าน CR (🟡 YELLOW) ก่อน — ดู `07_CHANGE_REQUEST_TEMPLATE.md` ในชุดของคุณ
* ฝั่ง frontend: เรียก API ผ่าน `apps/web/src/api.ts` เท่านั้น; ฝั่ง CV: ส่งข้อมูลผ่าน `POST /api/ingest/observations` เท่านั้น
* เทียบ response จริงกับ `contract_examples/` หลังแก้

## 9. Prompt กลาง (ใช้ได้กับ ChatGPT / Gemini / Claude / Copilot)
คัดลอกกล่องนี้ เติมช่อง `<…>` แล้ว **แนบไฟล์ตามข้อ 2** ไปพร้อมกัน
```text
You are helping one member of a 4-student team improve an EXISTING, working system called Smart Library NEXT
(FastAPI + SQLite backend, React + TypeScript web app, YOLO-based computer-vision pipeline). It shows library seat
status only as far as evidence supports it: when unsure it must say "unknown"/"stale", never guess "available".
All seat data in the demo is SIMULATION; the YOLO pipeline has only been tested on a sample image, not on real
library seats. Do NOT redesign or rebuild the system.

MY ROLE: <P1 Computer Vision | P2 Backend & Database | P3 Student Frontend | P4 Staff, QA & Integration>
MY TASK NOW: <one concrete task, e.g. "add a video-file input mode to cv/run_cv.py">

I am attaching (you cannot see anything else on my computer):
- project overview, my mission, my file-ownership list and the integration contract that I must keep
- the source files involved: <list the exact paths you attach>
If you need another file, ask me for it by its path instead of guessing its content.

RULES
1. Only change files I own (see the ownership list). If my task needs a change in someone else's file or in a shared
   API/contract, STOP and write a short change request (what, why, files, API impact, risk) instead of code.
2. Keep the integration contract backward compatible: never rename/remove endpoints, JSON fields or enum values, and
   never change their meaning. New fields must be optional.
3. Keep safety rules: never show unknown/stale/offline/reported seats as available; one user report never sets a seat
   to occupied; simulated data must stay labelled SIMULATION; never invent accuracy numbers.
4. Do not weaken, delete or skip tests. Add a test that proves the change.
5. Make the smallest change that works. Show it as a unified diff (or complete functions) with file paths.
6. Never include passwords, tokens, personal data or images of people.

OUTPUT
- First: a short explanation of how the current code works for this task (based only on the attached files).
- Then: the plan, the diff, the new/updated tests, and the exact commands I should run to verify
  (pytest, npm run build, scripts/check_ownership.py --owner <P#> --base origin/main).
- Finally: risks, and anything you are unsure about because you could not see the file.
```

## 10. บันทึกการใช้ AI ใน PR
ระบุใน PR ว่าส่วนไหน AI ช่วย (เช่น "ร่างฟังก์ชัน X ด้วย ChatGPT แล้วตรวจ/แก้เอง") — เป็นข้อกำหนดของทีม (เครดิตตามงานจริง)
