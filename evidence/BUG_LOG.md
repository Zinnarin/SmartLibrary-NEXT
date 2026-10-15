# BUG LOG — Smart Library NEXT V2 (14 ต.ค. 2569)

แยกเป็น **(A) บัคที่เกิดขึ้นจริงระหว่างพัฒนา/ทดสอบ** (มีอาการ วิธี reproduce สาเหตุ วิธีแก้ และหลักฐาน retest) กับ **(B) ความเสี่ยงที่คาดการณ์แต่ยังไม่เกิดในการทดสอบ** — (B) ไม่ใช่บัค

## (A) Actual bugs observed

| ID | ประเภท | อาการที่เห็นจริง | Reproduce | สาเหตุ | วิธีแก้ | Retest / หลักฐาน |
|---|---|---|---|---|---|---|
| BUG-001 | **Logic (สำคัญ)** | หลังกล้อง CAM-A หลุด 40 วินาทีแล้ว RECOVERED, เพียง **1 เฟรมใหม่** A07 กลับมาเป็น `is_recommendable=true` ทันที | `tests/test_api.py::test_recovered_requires_fresh_evidence` (CAMERA_LOST → tick 20 → RECOVERED → tick 1) — **FAILED ในการรันครั้งแรก** (`assert not True`) | SeatStateEngine นับ streak หลักฐานต่อจากก่อนกล้องหลุด ช่วงที่ไม่มีข้อมูลถูกมองข้าม = ตีความ “ไม่ได้เห็น” เป็น “ยังว่าง” | `state_engine.step`: ถ้าช่องว่างระหว่าง observation > freshness TTL → รีเซ็ต committed เป็น `UNKNOWN` (`GAP_RESET`) ต้องยืนยันใหม่ครบ 4 เฟรม/5 วินาที | test ผ่านหลังแก้ + เพิ่ม `test_gap_longer_than_ttl_resets_to_unknown_BUG001`; e2e ยืนยันว่า A05 กลับเป็นว่างหลัง RECOVERED เมื่อครบเกณฑ์ |
| BUG-002 | Environment | รัน pytest ครั้งแรก 26 errors: `PermissionError: [WinError 5] Access is denied: 'C:\Users\ebz14\AppData\Local\Temp\pytest-of-ebz14'` | `python -m pytest tests` | สิทธิ์เขียนโฟลเดอร์ temp ของ Windows ถูกจำกัดใน sandbox ที่ใช้รัน | `pytest.ini`: `--basetemp=.pytest_tmp` (ใน project) | รอบต่อไป 37 passed + 3 failed (BUG-001/003/004) จากนั้น 41 passed |
| BUG-003 | Test | `test_T13...` และ `test_source_contamination_guards` ได้ HTTP 422 แทน 200/401 | ส่ง `event_id="evt-0"` | API กำหนด `event_id` min_length=6; validation ของ body เกิดก่อนการตรวจ device token | แก้ test ให้ใช้ ID ที่ยาวพอ (พฤติกรรม API คงเดิมและบันทึกไว้) | ผ่าน |
| BUG-004 | Test (พฤติกรรมถูกต้อง) | `test_T13` เฟรมที่ 4 ได้สถานะ `late` แทน `applied` | ส่ง observed_at = now+6 s | เกิน clock-skew tolerance 5 s → ถูกจัดเป็น `clock_skew` และใช้เวลา server แทน ซึ่งเก่ากว่าเฟรมก่อนหน้า (now+4 s) → ถูกปฏิเสธเป็น out-of-order ตามที่ออกแบบ | แก้ test ให้ใช้ timestamp ในอดีต และเพิ่ม `test_clock_skew_becomes_unknown` | ผ่าน |
| BUG-005 | Test tooling | Playwright: `ReferenceError: __dirname is not defined in ES module scope` → “No tests found” | `npx playwright test` | `package.json` เป็น `"type": "module"` | ใช้ `fileURLToPath(import.meta.url)` | e2e ผ่าน |
| BUG-006 | UI (mobile) | ภาพ `16_mobile_student.png` (390 px): ผังถูกย่อเหลือ ~300 px อ่านรหัสที่นั่งไม่ออก | เปิดหน้า student ที่ 390×844 | SVG `w-full` ย่อตามความกว้างจอ | ใส่ container `overflow-x-auto` + `min-w-[640px]` ให้เลื่อนผังในการ์ด (หน้าเว็บเองไม่เลื่อนแนวนอน) | e2e ตรวจ `scrollWidth <= innerWidth` บนมือถือ ผ่าน |
| BUG-007 | UI | Wayfinder: เส้นทางทับข้อความ “▲ ทางเข้า”; ข้อความ “4 จุดเลี้ยว” ผิดความหมาย (เป็นจำนวน waypoint ไม่ใช่จุดเลี้ยว) | ภาพ `12_wayfinder.png` (ก่อนแก้) | ตำแหน่ง label อยู่บนแนวเส้น ENTRANCE→J_HALL | ย้าย label ไปขวาของประตู, เปลี่ยนเป็น “ผ่าน N จุดทางเดิน (waypoint)” | capture ใหม่ใน e2e |
| BUG-008 | Presentation | สไลด์ 6 รอบแรก: ภาพที่ crop ถูกยืด/ทับคำบรรยาย และป้าย SIMULATION ทับหัวข้อ | export ผ่าน PowerPoint (`scripts/export_pptx_preview.ps1`) แล้วดู PNG | ใช้ `crop_*` ของ python-pptx โดยไม่ปรับความสูง shape | crop ด้วย Pillow ก่อนใส่ (คงสัดส่วน) + grid คงที่ + ย้ายป้ายไป footer | export ใหม่ตรวจด้วยตา |
| BUG-009 | Tooling | `.claude/launch.json` เขียนผ่าน bash heredoc แล้วได้ `.venv\Scripts` (escape JSON ผิด) | ดูไฟล์หลังเขียน | backslash ถูกตีความ | เขียนใหม่ด้วย forward slash | preview server เปิดได้ |
| BUG-010 | Tooling (ความผิดพลาดของผู้รันคำสั่ง) | export PPTX จบด้วย exit 255 และค้าง `POWERPNT.EXE` | ต่อท้ายคำสั่ง export ด้วย `| Select-Object -First 1` | Select-Object หยุด pipeline กลางคันก่อน `Quit()` | รันใหม่โดยไม่ตัด pipeline และปิด process ที่ค้าง | export 8 สไลด์สำเร็จ |

### เพิ่มระหว่าง Final Demo Stabilization (14 ต.ค. 2569 ~22:20–22:50)

| ID | ประเภท | อาการที่เห็นจริง | Reproduce | สาเหตุ | วิธีแก้ | Retest / หลักฐาน |
|---|---|---|---|---|---|---|
| BUG-011 | **Reliability (สำคัญต่อเดโม)** | ปิดเซิร์ฟเวอร์จริงแล้วรอ 43 วินาที: หน้านักศึกษายังโชว์ **12 ที่นั่งสีเขียว**, การ์ดคำแนะนำ 7 ใบยังเขียน “ข้อมูลสด 0 วินาทีที่แล้ว”, ตัวนับยัง “ว่าง 12” — ขัดกับข้อเสนอเดิม (“แสดง ‘ข้อมูลไม่เป็นปัจจุบัน’ เสมอ”) | เปิดหน้า student → หยุด server → รอ > TTL (วัดใน browser pane: `green=12, recCards=7` หลัง 43 s) | กฎ TTL ทำงานเฉพาะฝั่ง server; browser แสดง snapshot ล่าสุดไปเรื่อย ๆ เมื่อไม่ได้รับข้อมูล | `apps/web/src/live.tsx`: browser ใช้กฎ TTL ซ้ำเอง + ถ้าไม่ได้ข้อมูล/heartbeat > 10 s → ทุกที่นั่งเป็น “ข้อมูลไม่เป็นปัจจุบัน”, ถอนคำแนะนำ, แถบแดง; ตัวนับคำนวณจากสิ่งที่แสดงจริง; คำแนะนำถูกล้างเมื่อ fetch ล้ม | e2e `BUG-011 regression…` **FAILED ก่อนแก้** (`evidence/bug011_before_fix_output.txt`: Received "available") → **ผ่านหลังแก้** (`bug011_after_fix_output.txt`); e2e `real server crash + restart…` (kill process จริงแล้วเปิดใหม่) ผ่าน; screenshot `20/21/22_*.png` |
| BUG-012 | Deployment/demo | หลัง rebuild frontend แท็บเบราว์เซอร์ยังรัน **bundle เก่า** (`index-CRWQd6O6.js` ไม่มีโค้ดที่แก้) ทั้งที่ server เสิร์ฟ bundle ใหม่ | rebuild แล้วเปิดแท็บเดิม/`navigate` | `index.html` ถูกเสิร์ฟโดยไม่มี `Cache-Control` → เบราว์เซอร์ cache ไว้ | ส่ง `Cache-Control: no-cache, must-revalidate` กับ `index.html` (assets มี hash จึง cache ได้ตามเดิม) | pytest `test_BUG012_index_html_is_not_cached`; `curl -D -` เห็น header; หมายเหตุ: เบราว์เซอร์ที่ cache ไว้ก่อนแก้ต้องกด Ctrl+F5 หนึ่งครั้ง |
| BUG-013 | **Data loss (launch script)** | `-Reset` พิมพ์ “Demo database removed” แต่ (1) ไม่สนใจ `SL_DB_PATH` (ลบไฟล์ default แทน) และ (2) ลบ `-wal/-shm` ของ DB ที่เซิร์ฟเวอร์อื่นกำลังใช้ → เซิร์ฟเวอร์ :8000 ตอบ **Internal Server Error** | รัน `start_demo_windows.ps1 -Reset -Port 8011` ขณะที่ :8000 ยังเปิด | path ฮาร์ดโค้ด + `-ErrorAction SilentlyContinue` กลบความล้มเหลว; **และ** Windows อนุญาตให้ลบไฟล์ SQLite ที่โปรเซสอื่นเปิดอยู่ได้ (ทดสอบแล้ว: การแก้รอบแรกที่หวังพึ่ง file lock **ใช้ไม่ได้**) | สคริปต์: (a) ปฏิเสธการเริ่มถ้าพอร์ตถูกใช้, (b) `-Reset` ใช้ `SL_DB_PATH`, (c) `-Reset` ปฏิเสธถ้ามีโปรเซส `app.main:get_app` ทำงานอยู่, (d) ตรวจว่าลบสำเร็จจริงก่อนพิมพ์ข้อความ | 3 กรณีทดสอบจริง: `evidence/launch_test_busy_port.txt` (exit 1), `launch_test_reset_locked.txt` (exit 1, DB ยังอยู่, :8000 ยังตอบ 24 ที่นั่ง), `launch_test_case3_custom_db.txt` (ใช้ DB ที่กำหนด, DB default ไม่ถูกแตะ) |
| BUG-014 | Tooling hazard (จับได้ก่อนเกิดผล) | `scripts/export_pptx_preview.ps1` เรียก `PowerPoint.Application.Quit()` ทุกครั้ง — COM จะเกาะ PowerPoint ที่ผู้ใช้เปิดอยู่ (เปิด `progress_update.pptx` ไว้ตั้งแต่ 22:32) จึงอาจปิดงานของผู้ใช้ได้ | สังเกตจาก `build_pptx.py` เขียนไฟล์ไม่ได้ (PermissionError: ไฟล์ถูกเปิดใน PowerPoint) | สคริปต์ไม่ตรวจว่า PowerPoint ทำงานอยู่ก่อน | ตรวจ `POWERPNT` ก่อน; ถ้าเปิดอยู่จะปิดเฉพาะไฟล์ที่ตัวเองเปิดแบบ read-only และไม่ `Quit()`; deck ใหม่เขียนเป็นไฟล์ใหม่ `progress_update_v2.pptx` | รันแล้วได้ข้อความ “PowerPoint was already running: left open (not quit)” และหน้าต่างของผู้ใช้ยังเปิดอยู่ |
| UX-001 | Misleading label | เหตุผลใน StudyMatch เขียน “กล้องปกติ” และหน้า seat detail เขียน “CAM-A · ปกติ” ทั้งที่เป็นกล้อง **จำลอง** | เปิด StudyMatch/seat detail | ข้อความไม่แยก source | “กล้องจำลองปกติ (SIMULATION)” และ “CAM-A (กล้องจำลอง)” เมื่อ source=scenario | e2e journey ผ่าน; ตรวจด้วยตาใน screenshot ใหม่ |
| UX-002 | Cosmetic | ป้าย “ทางเข้าหลัก (ENTRANCE)” ทับเส้นผนังล่าง | ภาพ `20_*.png` | ตำแหน่ง y | ย้ายลง 20 หน่วย | screenshot ใหม่ |

> หมายเหตุ: ทุกรายการข้างบนเกิดขึ้นจริงในเซสชันนี้ บันทึกตามลำดับเวลา ไม่มีการแต่งเพิ่ม

## (A2) ข้อจำกัดที่ “เห็นจริง” จากการรัน YOLO11n จริง (ไม่ใช่บัคของโค้ด แต่เป็นข้อค้นพบ)

| ID | สิ่งที่เห็นจริง | หลักฐาน | ความหมาย / งานต่อ |
|---|---|---|---|
| LIM-CV-01 | ROI `LAB1` วางทับช่วงสะโพกของคน **ยืน** → กฎ hip-anchor + overlap ให้ `P_SEATED` → committed **Occupied** (person 0.88, seat_overlap 0.41) ทั้ง 4 รอบที่รัน | `evidence/cv/run_cv2026101420*.json`, `run_log.txt`, ภาพ `annotated_*.jpg` | กล่อง person + ROI แยก “ยืน” กับ “นั่ง” ไม่ได้ ถ้า ROI ไม่ calibrate กับเบาะจริงและมุมกล้องไม่เหมาะ → ต้องวาง ROI จากภาพมุมกล้องจริง และพิจารณา pose/ความสูงกล่องในอนาคต |
| LIM-CV-02 | ภาพที่ทำให้มืด (×0.12, brightness 13.4) YOLO **ยังตรวจพบ 6 วัตถุ** แต่ quality gate (brightness < 40) ทำให้ทุก ROI เป็น Unknown | `latest_run.json` → `robustness_checks[0]` | gate อาจ “ระวังเกิน” — ค่า 40 เป็นสมมติฐาน ต้องวัดกับแสงจริงก่อนปรับ |
| LIM-CV-03 | เฟรมแรกของแต่ละรอบใช้ 2.0–2.8 วินาที (warm-up โมเดล) เฟรมถัดไป ~27–45 ms บน CPU | `ms_per_frame_all` | ต้อง warm-up ก่อนเริ่มนับ latency; ยังไม่ได้วัดบน Pi/Jetson |
| LIM-CV-04 | `bus` 0.94 ทับ ROI ทุกจุด (ไม่ใช่คลาสที่ใช้ตัดสิน จึงไม่มีผล) | ตาราง ROI ในหน้า CV Lab | ยืนยันว่าเฉพาะ person/belongings/ignored classes เท่านั้นที่มีผล |

## (B) Predicted risks — NOT yet observed (ไม่ใช่บัค)

| ความเสี่ยง (จาก DOCX failure cases + V2) | สถานะ | การป้องกันที่มีในโค้ดตอนนี้ |
|---|---|---|
| แสงน้อย/แสงจ้าจากหน้าต่างจริง | ยังไม่ทดสอบกับกล้องจริง | quality gate (brightness/Laplacian) → Unknown; ทดสอบแค่ภาพที่ทำให้มืดสังเคราะห์ |
| คนบัง/ชั้นหนังสือบัง | จำลองเท่านั้น (C08 `occluded`) | Unknown, ไม่ถูกแนะนำ |
| คนยืนคุยใกล้โต๊ะ / เดินผ่าน | unit test เท่านั้น | hip anchor + overlap; ambiguous → Unknown |
| คนนั่งจมโซฟา/พนักพิงบัง | ยังไม่ทดสอบ | ไม่มีการป้องกันเฉพาะนอกจาก Unknown เมื่อความมั่นใจต่ำ |
| กล้องเลื่อนตำแหน่ง (ROI ไม่ตรง) | ยังไม่ทำ | ยังไม่มี reference-image check (DOCX §9) |
| Server process ล่ม (เครื่องเดียว) | **ทดสอบแล้ว** (e2e kill process จริง + เปิดใหม่) | browser แสดง “ข้อมูลไม่เป็นปัจจุบัน”, ถอนคำแนะนำ, reconnect เอง (BUG-011 fix) |
| Wi-Fi/LAN จริงล่ม, MQTT broker ล่ม, store-and-forward | ยังไม่ทำ (P2) | ฝั่ง server มี idempotent event_id + ไม่ย้อนสถานะจาก event เก่า (unit test); ฝั่ง browser เหมือนกรณี server ล่ม |
| ไฟดับ/Edge รีสตาร์ท | ยังไม่ทดสอบ | สถานะเก็บใน SQLite; เมื่อเริ่มใหม่หลังเกิน TTL จะเป็น STALE/Unknown |
| รายงาน SeatCheck ถูกสแปมจากหลาย session | บางส่วน | rate limit ต่อ session; ยังไม่มีการจำกัดการสร้าง session ใหม่/ต่อ IP |
| ผัง ปลั๊ก โซนเงียบ ความติดกัน ไม่ตรงของจริง | แน่นอนว่ายังไม่ตรง | ติดป้าย `metadata_source=demo_assumed` ทุกที่นั่ง |
