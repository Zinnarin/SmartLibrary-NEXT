# P2 · 02 — ภารกิจที่ได้รับมอบหมาย (Backend & Database)

**Branch:** `feature/v3-backend` · **Label:** `person-2-backend` · **Issues:** #1 (สัญญา — PR แรกของทีม), #2, #3

## ภารกิจ
เป็นเจ้าของ FastAPI backend, Seat State Engine, ฐานข้อมูลและ migration, สัญญา API และการส่งข้อมูล realtime — ทำให้ backend **รับหลักฐาน CV จริงได้อย่างปลอดภัย** และ **คงความเข้ากันได้** กับเว็บนักศึกษาและ Staff Console

## เป้าหมาย
1. รับ CV evidence (C1)
2. ตรวจสอบความถูกต้องของ observation ที่เข้ามา (validation)
3. ประเมินสถานะที่นั่ง
4. จัดการ smoothing และ freshness
5. เก็บข้อมูลอย่างสอดคล้อง (transaction, idempotency)
6. รักษาความเข้ากันได้ของ API ฝั่ง student/staff
7. ปรับปรุงความทนทานและประสิทธิภาพ

## สิ่งที่ทำได้อิสระ (🟢 GREEN)
* refactor ภายใน (`services.py`, `main.py`, `engine/*` ภายใน) โดย JSON/ความหมายเท่าเดิม และ **ชื่อ/signature ใน C1b คงเดิม**
* validation ที่ดีขึ้นซึ่ง **ไม่ปฏิเสธ request ที่ถูกต้องตามสัญญาเดิม** (เช่น PA-02: 500 → 422)
* ปรับ DB: index, query, pruning, migration ภายในที่ไม่เปลี่ยน JSON
* ความทนทาน: logging, error handling, test เพิ่ม, ประสิทธิภาพ WS
* ฟีเจอร์ backend ใหม่ที่เป็น **endpoint/field ใหม่แบบ optional** → เป็น 🟡 (แจ้งก่อน) แต่คุณออกแบบภายในได้อิสระ

## สิ่งที่ต้องคุยก่อน (🟡 / 🔴)
* เพิ่ม field/endpoint/env/enum ใหม่ (YELLOW) — อัปเดต `docs/api_contract_v3.md` + `contract_examples/` ใน PR เดียวกัน
* เปลี่ยน `requirements.txt`, `tests/conftest.py` (YELLOW — P4/ทุกคน review)
* เปลี่ยนกฎที่มีผลต่อสิ่งที่ผู้ใช้เห็น เช่น threshold ใน `EngineConfig`, rate limit, TTL (YELLOW)
* ลบ/เปลี่ยนชื่อ route หรือ field, เปลี่ยนความหมาย state, เปลี่ยน DB engine, เพิ่มที่นั่งจริงบนผัง (PA-03) (**RED**)

## ห้าม
* เปลี่ยนสัญญาร่วมแบบเงียบ ๆ · ทำให้ client นักศึกษา/เจ้าหน้าที่พัง · เปลี่ยนสถาปัตยกรรมทั้งหมดโดยทีมไม่อนุมัติ
* แก้ `apps/web/**`, `cv/**`, `scripts/*`, `.github/*`, ไฟล์ FROZEN
* ลด assertion ใน test เดิมเพื่อให้ผ่าน

## งานเรียงตามลำดับความสำคัญ
| # | งาน | ระดับ | ผลลัพธ์ที่ตรวจได้ |
|---|---|---|---|
| B1 | **`docs/api_contract_v3.md`** จาก `SHARED_V3/03_SHARED_API_CONTRACTS.md` + ตรวจกับโค้ดอีกรอบ + test ยืนยันว่าตัวอย่างตรงกับ response จริง (#1) | YELLOW (เอกสารสัญญา — P1/P3/P4 review) | PR แรกของทีม merge แล้ว |
| B2 | PA-02: `observed_at_utc` ผิดรูปแบบ → 422 `BAD_TIMESTAMP` (ไม่เก็บอะไร) | GREEN + แจ้ง P1 | test ใหม่ผ่าน |
| B3 | `tests/test_backend_v3.py`: valid / duplicate / late / clock skew / quality ไม่ ok / token หาย-ผิด / กล้องไม่ใช่ CV / ที่นั่งไม่ใช่ของกล้อง / ที่นั่งไม่มี / rollback ทั้งเฟรม / timestamp เสีย (#2) | GREEN | pytest ผ่าน |
| B4 | PA-01: `SL_CV_EVIDENCE_DIR` ใน `AppSettings.from_env()` (ค่าเริ่มต้นเดิมคงไว้) — ตกลงตำแหน่งกับ P1 (#3) | YELLOW | CV Lab อ่านตำแหน่งใหม่ได้; `evidence/cv/` ไม่ถูกเขียน |
| B5 | Migration แบบเบา: บันทึก schema version (เช่น `PRAGMA user_version`) + ฟังก์ชัน migrate ตามลำดับ ใน `db.py` — DB สาธิตเดิมยังเปิดได้ | GREEN (ภายใน) | test เปิด DB เก่าแล้ว migrate ได้ |
| B6 | ความทนทาน/ประสิทธิภาพ: test สำหรับ pruning (ยังไม่มี), วัดเวลา `seat_views` เมื่อมีที่นั่งมากขึ้น, index ที่จำเป็น | GREEN | ตัวเลขวัดจริง + test |
| B7 | PA-07 `response_model` ให้ OpenAPI มี response schema โดย JSON เท่าเดิม | YELLOW | contract tests ผ่าน, OpenAPI ใหม่ |
| B8 | (ถ้าทีมอนุมัติ RED) PA-03 การลงทะเบียนที่นั่ง/กล้อง CV จริงให้ขึ้นผังนักศึกษา — ออกแบบ + migration + rollback | RED | CR อนุมัติ 4/4 ก่อนเริ่ม |
| B9 | รักษา C1b (engine API ที่ P1 import) ตลอด sprint | — | `cv/run_cv.py` ยัง import ได้ |
