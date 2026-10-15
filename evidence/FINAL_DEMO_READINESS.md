# FINAL DEMO READINESS — Smart Library NEXT V2

**ตรวจเมื่อ:** 14 ต.ค. 2569 ~22:15–23:00 ICT · **เครื่อง:** Windows 11 (build 26300), i7-14700HX, 23.7 GB RAM · **ผู้ตรวจ:** Claude Code (ตรวจงานที่ตัวเองสร้าง — ไม่ใช่การตรวจอิสระ)

## ข้อแก้ไขข้อความในคำสั่ง
คำสั่งรอบนี้เขียนว่า YOLO ถูกทดสอบกับ “library-provided sample media” — **ไม่ถูกต้อง**: ภาพที่ใช้คือ `bus.jpg` ซึ่งเป็นภาพตัวอย่างที่มากับ **ซอฟต์แวร์ไลบรารี Ultralytics** (ภาพถนน/รถบัส) ไม่ใช่สื่อจากห้องสมุดมหาวิทยาลัย เอกสารทุกฉบับใช้ถ้อยคำนี้

---

## 1. ผลทดสอบที่ยืนยันแล้ว (รันจริงในรอบตรวจนี้)

| ชุดทดสอบ | คำสั่ง | ผล | หลักฐาน |
|---|---|---|---|
| Backend (pytest) | `.\.venv\Scripts\python.exe -m pytest -v -rA --junitxml=evidence/pytest_junit.xml` | **53 passed / 0 failed / 0 errors** (35.1 s) | `evidence/pytest_junit.xml`, `pytest_output.txt` |
| Browser e2e (Playwright + Edge) | `cd apps\web; npx playwright test` | **8 passed / 0 failed / 0 flaky** (161.5 s) | `evidence/playwright_results.json`, `playwright_output.txt` |
| BUG-011 regression (ก่อน/หลังแก้) | `npx playwright test e2e/reliability.spec.ts` | ก่อนแก้ **FAILED** (`Received "available"`) → หลังแก้ **passed** | `evidence/bug011_before_fix_output.txt`, `bug011_after_fix_output.txt` |
| Real CV pipeline | `.venv-cv\Scripts\python cv\run_cv.py suite --post` | 4 รอบ ผลเหมือนกัน: LAB1 occupied, LAB2 unknown, LAB3 available, LAB4 unknown · median 37.8–42.6 ms/เฟรม (CPU) | `evidence/cv/run_log.txt`, `run_cv*.json` |
| WS latency | `.\.venv\Scripts\python.exe scripts\measure_ws_latency.py --trials 20` | median 43.5 ms, p90 71.2 ms, max 99.5 ms (loopback) | `evidence/ws_latency.json` |
| Launch script | 4 การรันจริง (fresh start + 3 กรณี BUG-013) | ทั้งหมดได้ผลตามคาดหลังแก้ | `evidence/launch_*.txt` |
| PPTX | `scripts\export_pptx_preview.ps1 -Deck presentation\progress_update_v2.pptx` | เปิด/ส่งออก 8 สไลด์ + PDF ได้ | `presentation/preview/` |
| Acceptance matrix | `verification/ACCEPTANCE_TEST_RESULTS.csv` | **15 PASS · 1 BLOCKED (T15)** | ไฟล์ CSV |

## 2. Phase 1 — Implementation audit
**วิธีตรวจ:** (ก) สคริปต์เทียบชื่อ test ทุกตัวที่อ้างใน `ACCEPTANCE_TEST_RESULTS.csv` และ `IMPLEMENTATION_REPORT.md` กับ JUnit/Playwright จริง → อ้าง 26 test ใน CSV: **พบครบ ผ่านทุกตัว**; screenshot ที่อ้าง: **มีครบ**; (ข) อ่าน assertion ของแต่ละ test เทียบกับคำกล่าวอ้าง

**ช่องว่างที่พบ (คำกล่าวอ้างที่หลักฐานยังอ่อน) → ปิดแล้วด้วย test ใหม่**
| คำกล่าวอ้างเดิม | ปัญหา | สิ่งที่ทำ |
|---|---|---|
| T07 “override ชนะ CV update” | ทดสอบผ่านข้อมูล scenario เท่านั้น | `test_T07_override_wins_over_real_cv_ingest_path` (ผ่าน `/api/ingest`, source=cv) |
| “WebSocket reconnect” | มีแค่กรณี WS ถูกบล็อก → polling | e2e reconnect หลังตัดการเชื่อมต่อ + kill เซิร์ฟเวอร์จริงแล้วเปิดใหม่ |
| Keyboard map (WORKING_UNVERIFIED) | ไม่มี test | e2e keyboard (focus + Enter + Tab) |
| “ไม่แนะนำสถานะเสี่ยง” | ทดสอบเป็นกรณี ๆ | property test ทุก scenario × หลายจังหวะเวลา × 4 ชุดตัวกรอง × single/GroupFit (ตรวจ >100 คำแนะนำ) |
| staff override “unknown” | ไม่มี test | `test_staff_unknown_override_pending_inspection` |
| `GET /api/seats/{id}`, `/api/layout` | ไม่มี test | `test_seat_detail_and_layout_endpoints` |
| อ้าง “test_T04/T05” แบบย่อในรายงาน | ไม่ใช่ชื่อจริง | แก้เป็นชื่อเต็ม |

**ไม่มีคำกล่าวอ้าง PASS ใดถูกลดสถานะ** — แต่การตรวจเชิงพฤติกรรมพบบัคจริงใหม่ 3 ตัว (BUG-011, -012, -013) ดูข้อ 4

## 3. Feature readiness matrix

| ความสามารถ | สถานะ | หลักฐาน / หมายเหตุ |
|---|---|---|
| FastAPI + SQLite + REST ตามสัญญา spec | **IMPLEMENTED_AND_TESTED** | pytest |
| Seat State Engine: 5 สถานะเดิม + Unknown, smoothing, Available ต้องยืนยันซ้ำ, gap reset | **IMPLEMENTED_AND_TESTED** | `test_state_engine.py`, `test_scenario_switch_is_smoothed…` |
| Freshness/TTL + สุขภาพกล้อง (server **และ** browser) | **IMPLEMENTED_AND_TESTED** | T03, BUG-011 e2e, real-crash e2e |
| Staff override ชนะผลตรวจจับ (Maintenance/Unavailable/Unknown + หมดอายุ) + audit | **IMPLEMENTED_AND_TESTED** | T07 ×2, expiry, unknown override |
| SeatCheck (ไม่ระบุตัวตน, ไม่ตั้ง Occupied เอง, rate-limit, replay) | **IMPLEMENTED_AND_TESTED** | T08, T10 |
| Librarian Console + audit log | **IMPLEMENTED_AND_TESTED** | T09, journey e2e |
| WebSocket + polling fallback + auto-reconnect | **IMPLEMENTED_AND_TESTED** | T09, 3 e2e |
| StudyMatch (hard constraint, เหตุผล, no-result, ไม่มี % ปลอม) | **IMPLEMENTED_AND_TESTED** | T02, property test |
| GroupFit (ติดกันตาม adjacency ที่บันทึกด้วยมือ) | **IMPLEMENTED_AND_TESTED** | T11 — *ข้อมูล adjacency เป็นของสมมติ* |
| Wayfinder (Dijkstra บนกราฟที่ประกาศ) | **IMPLEMENTED_AND_TESTED** | T12 — *ผัง/หน่วยเป็นของสาธิต ไม่ใช่เมตร* |
| SeatWatch (แจ้งในแอป) | **IMPLEMENTED_AND_TESTED** | e2e |
| Scenario Lab 7 สถานการณ์ (ขับจาก backend, banner) | **IMPLEMENTED_AND_TESTED** | หลาย test |
| Demo/production guard, staff demo gate, กันข้อมูลจำลองปนข้อมูล CV | **IMPLEMENTED_AND_TESTED** | T10, contamination test |
| Launch script (รวมกันพอร์ตชน/กัน -Reset ลบ DB ที่ใช้อยู่) | **IMPLEMENTED_AND_TESTED** | 4 การรันจริง |
| Mobile layout (ไม่มี horizontal scroll ที่ 390 px) | **IMPLEMENTED_AND_TESTED** | e2e + screenshot 16 |
| Keyboard map | **IMPLEMENTED_AND_TESTED** (พื้นฐาน) | ยังไม่ได้ทดสอบ screen reader |
| CV pipeline: YOLO11n + OpenCV quality gate + ROI + engine + ingest | **IMPLEMENTED_AND_TESTED** (pipeline บนภาพตัวอย่างเท่านั้น) | `evidence/cv/` |
| สถานะที่นั่งทุกหน้าจอ, สถิติ Scenario Lab (simulated False Available) | **SIMULATION_ONLY** | banner + `source=scenario` |
| ธง “ของวางเกิน 30 นาที” ใน UI จริง | **IMPLEMENTED_NOT_FULLY_TESTED** | ทดสอบด้วยนาฬิกาจำลองใน pytest; ยังไม่เคยเห็นใน UI จริง (ต้องรอ 30 นาที) |
| Webcam runner (`run_cv.py webcam --consent`) | **IMPLEMENTED_NOT_FULLY_TESTED** | ไม่เคยรัน — ไม่มีการอนุญาตใช้กล้อง |
| Session rate-limit เมื่อมีคนขอ session ใหม่ซ้ำ ๆ | **IMPLEMENTED_NOT_FULLY_TESTED** | จำกัดต่อ session เท่านั้น — ช่องโหว่ที่รู้แล้ว |
| การลบ observation เก่า (> 2 ชม.) | **IMPLEMENTED_NOT_FULLY_TESTED** | ไม่มี test |
| Edge (Pi/Jetson), PoE/RTSP, MQTT QoS1/TLS/LWT, store-and-forward, PostgreSQL/cloud, จอหน้าห้อง, LED, UPS, กราฟ analytics, prediction | **DESIGNED_ONLY** | สไลด์ 4 (กล่องเส้นประ) |
| User study (ผังธรรมดา vs StudyMatch), ROI calibration กับกล้องจริง | **DESIGNED_ONLY** | `cv/ROI_CALIBRATION_GUIDE_TH.md` |
| CV บนที่นั่งห้องสมุดจริง: accuracy, mAP, False Available จริง | **BLOCKED** | ไม่มีวิดีโอ/กล้องที่ได้รับอนุญาต |
| ผังจริง + ข้อมูลปลั๊ก/โซนเงียบ/ที่นั่งติดกันที่ยืนยันแล้ว | **BLOCKED** | ต้องได้ข้อมูลจากห้องสมุด |

## 4. Phase 2–3 — UX และความน่าเชื่อถือ (ผลจริง)

**เส้นทางนักศึกษา 12 ขั้นตามลำดับที่กำหนด** (e2e `student journey in the requested order…`): เปิดระบบ → ดูที่นั่ง → กรอง → StudyMatch (A07 อันดับ 1) → GroupFit (เงียบ+ปลั๊ก ไม่มีคู่ = แจ้งตรง ๆ; ผ่อนเงื่อนไขเองแล้วได้ A07+A08) → Wayfinder → SeatCheck → A07 ถูกถอนจากคำแนะนำ (สถานะยังว่าง) → Staff Console → ตรวจรายงาน → override Unavailable → หน้านักศึกษาเปลี่ยนเองผ่าน WebSocket — **ผ่าน, 0 console error / 0 page error** (รวมหน้า Scenario Lab และ CV Lab)

| รายการความน่าเชื่อถือ | ผล | หลักฐาน |
|---|---|---|
| กล้องออฟไลน์ (LWT จำลอง) → ไม่แนะนำทันที | PASS | `test_camera_offline_is_immediate…`, e2e 09 |
| กล้องเงียบโดยไม่มี LWT → offline หลัง heartbeat timeout | PASS | `test_heartbeat_timeout…` |
| Stale หลัง TTL (server) | PASS | T03 |
| **Stale เมื่อเซิร์ฟเวอร์/เครือข่ายล่ม (browser)** | **FAIL → แก้ → PASS** (BUG-011) | before/after logs, real crash e2e |
| Unknown (low confidence/มืด/ถูกบัง/คนยืนใกล้) | PASS | T04, T06, CV quality gate |
| WebSocket reconnection (ตัดเครือข่าย และ kill server จริง) | PASS | 2 e2e |
| Polling fallback | PASS | e2e |
| Smoothing (เปลี่ยน scenario แล้วไม่พลิกในเฟรมเดียว; ระหว่างเปลี่ยนถูกถอนจากคำแนะนำ) | PASS | `test_scenario_switch…` |
| Override ชนะ (scenario และ CV จริง) | PASS | T07 ×2 |
| คำแนะนำไม่มีสถานะเสี่ยงเลย (property test) | PASS | `test_recommendations_never_include_unsafe_states_across_scenarios` |

**บัคจริงที่พบและแก้ในรอบนี้ (รายละเอียด `evidence/BUG_LOG.md`)**
* **BUG-011** เซิร์ฟเวอร์ล่ม 43 วินาที หน้าเว็บยังโชว์ 12 ที่นั่งสีเขียว + 7 การ์ดคำแนะนำ → browser ตรวจความสดเอง, แถบแดง, ถอนคำแนะนำ
* **BUG-012** เบราว์เซอร์ใช้ bundle เก่าหลัง rebuild → `index.html` ส่ง `Cache-Control: no-cache`
* **BUG-013** สคริปต์ `-Reset` ลบไฟล์ DB ที่เซิร์ฟเวอร์อื่นใช้อยู่ → เซิร์ฟเวอร์ขึ้น Internal Server Error → สคริปต์ตรวจพอร์ต/โปรเซสก่อน (การแก้รอบแรกที่พึ่ง file lock **ไม่ได้ผล** บน Windows — ตรวจพบจากการทดสอบและแก้ใหม่)
* **BUG-014** สคริปต์ export PPTX อาจปิด PowerPoint ของผู้ใช้ → ไม่ quit ถ้าเปิดอยู่ก่อน
* **UX-001/002** ป้ายกล้องจำลองที่ทำให้เข้าใจผิด, ป้ายทางเข้าทับเส้น

**สิ่งที่เปลี่ยนในโค้ด (ไม่มีฟีเจอร์ใหม่ / ไม่เปลี่ยนสถาปัตยกรรม):** `apps/web/src/live.tsx`, `App.tsx`, `pages/StudentPage.tsx`, `components/SeatDetail.tsx`, `components/FloorMap.tsx`, `services/api/app/main.py` (1 header), `services/api/app/matching.py` (ข้อความ), `scripts/start_demo_windows.ps1`, `scripts/export_pptx_preview.ps1`, `scripts/build_pptx.py`, `scripts/compose_test_results.py` · tests ใหม่: `tests/test_reliability.py` (7), `tests/test_api.py` (+1), `apps/web/e2e/reliability.spec.ts` (3), `apps/web/e2e/server_restart.spec.ts` (1)

## 5. Remaining blockers
1. **CV บนที่นั่งห้องสมุดจริง — BLOCKED:** ไม่มีวิดีโอ/กล้องที่ได้รับอนุญาต → ไม่มี accuracy / mAP / False Available จริง
2. **ผังและข้อมูลที่นั่งจริง — BLOCKED:** ต้องได้จากห้องสมุด
3. ไม่มีอุปกรณ์ edge / เครือข่ายจริงสำหรับทดสอบ store-and-forward (P2)

## 6. Known limitations
* ข้อมูลที่นั่งในเดโมเป็น SIMULATION ทั้งหมด; truth ของ scenario เขียนโดยผู้พัฒนา
* ข้อจำกัด CV ที่เห็นจริง: คนยืนในพื้นที่ ROI ถูกตีเป็น “นั่ง” ถ้า ROI ไม่ calibrate (LIM-CV-01); quality gate อาจระวังเกิน (LIM-CV-02)
* Staff PIN เดียว = demo gate ไม่ใช่ระบบยืนยันตัวตน; ไม่มี HTTPS; ผูก 127.0.0.1
* Rate-limit SeatCheck ต่อ session เท่านั้น
* latency วัดบนเครื่องเดียว ไม่ใช่เครือข่ายจริง
* ไม่ได้อ้าง PDPA compliance, ไม่ใช่ production
* หลังเปิดเซิร์ฟเวอร์หรือหลังข้อมูลขาดช่วง ที่นั่งเป็น “ไม่แน่ใจ” 6–8 วินาที (ตั้งใจ)
* เบราว์เซอร์ที่เคยเปิดหน้าเว็บก่อน BUG-012 fix ต้อง Ctrl+F5 หนึ่งครั้ง

## 7. Presentation readiness (Phase 5)
| เกณฑ์ | ผล |
|---|---|
| 8 สไลด์ render ถูกต้อง | ✅ export จาก PowerPoint ได้ครบ (`presentation/preview/slide_01..08.png`) |
| ฟอนต์ไทย | ✅ บนเครื่องนี้ (Leelawadee UI) · ⚠ PPTX ไม่ได้ฝังฟอนต์ → ใช้เครื่องนี้หรือใช้ PDF (ฝังฟอนต์แล้ว ตรวจด้วย pypdf) |
| ข้อความไม่ถูกตัด/ไม่ทับกัน | ✅ หลังแก้ — พบคำบรรยายสไลด์ 6 ถูกตัด 1 จุดและแก้แล้ว; ตรวจด้วยตาทุกสไลด์ |
| Screenshot มาจากระบบจริง | ✅ Playwright capture จาก UI ที่รันจริง (14 ต.ค.) |
| ข้อมูลจำลองติดป้ายชัด | ✅ แถบ SIMULATION ในทุก screenshot + ป้ายส้มในสไลด์ 5–6 |
| อธิบาย CV ถูกต้อง | ✅ “pipeline บนภาพตัวอย่าง / ห้องสมุดจริง BLOCKED / ไม่มี accuracy / ไม่ได้ fine-tune” |
| ตัวเลข test ตรงหลักฐาน | ✅ ใน **`progress_update_v2.pptx`** (53/53, 8/8 อ่านจาก evidence อัตโนมัติ) · ⚠ ฉบับเดิม `progress_update.pptx` ยังเป็น 45/45 และ 4/4 (ไม่ได้เขียนทับเพราะผู้ใช้เปิดไฟล์อยู่ใน PowerPoint) → **ใช้ v2** |
| พูดจบใน 3 นาที | ⚠ ประมาณจากจำนวนตัวอักษร ≈ 2 นาทีพูด + เวลาคลิกเดโม; พบช่วงสไลด์ 7 เกินเวลาและตัดให้สั้นแล้ว — **ยังไม่ได้ซ้อมจับเวลาจริง** |

## 8. คำสั่งเริ่มระบบ
```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_demo_windows.ps1 -Reset
```
นักศึกษา http://127.0.0.1:8000/ · เจ้าหน้าที่ http://127.0.0.1:8000/#/staff (PIN `staff-demo-2569`) · Scenario Lab `/#/lab` · CV Lab `/#/cv`
ทดสอบ: `powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1` · คู่มือเต็ม: `docs/DEMO_RUNBOOK_TH.md`

## 9. Overall recommendation: **READY_WITH_LIMITATIONS**
พร้อมสำหรับ **การนำเสนอความคืบหน้าเชิงวิชาการแบบต้นแบบในเครื่อง** — เส้นทางเดโมหลักทั้งหมดรันได้และผ่านการทดสอบอัตโนมัติซ้ำได้ รวมถึงกรณีล้มเหลวที่เสี่ยงต่อเดโม (เซิร์ฟเวอร์ล่ม, กล้องหลุด, เริ่มสคริปต์ซ้ำ)
เงื่อนไข: (1) ใช้ `progress_update_v2.pptx`, (2) ซ้อมจับเวลา 1 รอบ, (3) พูดตามข้อ 7 ของ runbook เรื่อง SIMULATION และ CV ที่ยัง BLOCKED, (4) ห้ามอ้างการติดตั้งจริง ความแม่นยำบนที่นั่งจริง หรือความพร้อมใช้งานจริง
