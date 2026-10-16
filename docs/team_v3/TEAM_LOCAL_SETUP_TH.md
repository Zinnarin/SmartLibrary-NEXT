# TEAM LOCAL SETUP — ติดตั้งและรัน Smart Library NEXT บนเครื่อง Windows ของคุณ

> ใช้ได้ทั้งกับ **ZIP ซอร์สโค้ด** (`SmartLibrary_NEXT_V3_Team_Source.zip`) และกับ **git clone** ของ repo (ขั้นตอนเหมือนกันหลังได้โฟลเดอร์โปรเจกต์)
> ไม่ต้องใช้ไฟล์ส่วนตัวจากเครื่องของใคร ไม่ต้องใช้ cloud key — ใช้ค่าตั้งต้นสำหรับ **สาธิตในเครื่อง (demo) เท่านั้น**

## ⚠ อ่านก่อน: ระบบนี้ทำอะไรได้จริงแค่ไหน
* **ข้อมูลที่นั่งบนหน้าจอทั้งหมดเป็น SIMULATION** (สร้างโดย Scenario Lab) — ไม่ใช่ข้อมูลจากกล้องจริง
* **YOLO pipeline ทดสอบแล้วกับภาพตัวอย่างเท่านั้น** (`bus.jpg` ที่มากับแพ็กเกจ Ultralytics — ภาพถนน ไม่ใช่ห้องสมุด) **ยังไม่เคยแสดงว่าตรวจจับที่นั่งห้องสมุดจริงได้อย่างน่าเชื่อถือ** และไม่มีตัวเลขความแม่นยำบนที่นั่งจริง
* เซิร์ฟเวอร์ผูกกับ `127.0.0.1` เท่านั้น (เปิดได้เฉพาะเครื่องตัวเอง) และ PIN เจ้าหน้าที่เป็น **demo gate** ไม่ใช่ระบบยืนยันตัวตนจริง

## 1. ซอฟต์แวร์ที่ต้องมี
| โปรแกรม | เวอร์ชันที่ใช้ได้ (ตรวจจริง) | ใช้ทำอะไร | ดาวน์โหลด |
|---|---|---|---|
| Windows | 10/11 (ทดสอบบน Windows 11) | — | — |
| **Python 3.10** | **3.10.x** (ทดสอบ 3.10.11; CI ใช้ 3.10) — ติดตั้งพร้อม **py launcher** (ค่าเริ่มต้นของตัวติดตั้ง) | backend + tests | python.org → Windows installer 3.10.x |
| **Node.js** | **22 LTS หรือ 24** (CI build ด้วย 22, ทดสอบในเครื่องด้วย 24.11.0) พร้อม npm (ทดสอบ 11.12.1) | build หน้าเว็บ | nodejs.org |
| Git | 2.x (ทดสอบ 2.53) | ทำงานร่วมกันผ่าน GitHub, ตรวจ ownership — *ไม่จำเป็นสำหรับแค่รันจาก ZIP* | git-scm.com |
| VS Code | ล่าสุด (แนะนำ ไม่บังคับ) | แก้โค้ด | code.visualstudio.com |
| Microsoft Edge | ที่มากับ Windows | ใช้รัน browser tests (Playwright `channel: msedge`) เท่านั้น | — |

> ทำไมต้อง 3.10: สคริปต์ `scripts\start_demo_windows.ps1` สร้าง venv ด้วย `py -3.10` (ถ้ามี py launcher) และแพ็กเกจใน `services/api/requirements.txt` ถูก pin และทดสอบกับ 3.10 — เวอร์ชันอื่นยัง **ไม่ได้ทดสอบ**
> ตรวจเวอร์ชันใน PowerShell: `py -3.10 --version` · `node --version` · `npm --version` · `git --version`

## 2. ตำแหน่งโฟลเดอร์ที่แนะนำ
ใช้ path สั้น ไม่มีช่องว่าง ไม่มีภาษาไทย และ **ไม่อยู่ใน OneDrive** เช่น `C:\dev\SmartLibrary_NEXT_V3` — `node_modules` มีไฟล์ลึกหลายชั้น path ยาว/โฟลเดอร์ sync อัตโนมัติอาจทำให้ติดตั้งช้าหรือพัง
> พบจริงตอนทดสอบติดตั้งใหม่ (16 ต.ค. 2569): โฟลเดอร์ที่ชื่อมีลักษณะเป็น UUID (เช่น `…\1a2b3c4d-5e6f-7a8b-9c0d-…\`) ทำให้ `npm ci` ล้มด้วย `spawn C:\WINDOWS\system32\cmd.exe ENOENT` — ย้ายไป path ธรรมดาแล้วผ่าน

## 3. แตกไฟล์ ZIP
1. คลิกขวา `SmartLibrary_NEXT_V3_Team_Source.zip` → **Extract All…** → เลือก `C:\dev\`
2. จะได้ `C:\dev\SmartLibrary_NEXT_V3\` ที่มี `README.md`, `services\`, `apps\`, `cv\`, `scripts\`, `docs\` อยู่ข้างในโดยตรง
หรือใช้ PowerShell:
```powershell
Expand-Archive -Path "$HOME\Downloads\SmartLibrary_NEXT_V3_Team_Source.zip" -DestinationPath C:\dev
```
> ZIP นี้ **ไม่ใช่ git repository** (ไม่มีโฟลเดอร์ `.git`) — ใช้ศึกษา/รันได้ทันที แต่ **การพัฒนาเพื่อส่งงานต้องทำใน git clone** ตาม `docs/team_v3/TEAM_GITHUB_WORKFLOW_TH.md`

## 4. เปิดใน VS Code
VS Code → **File → Open Folder…** → เลือก `C:\dev\SmartLibrary_NEXT_V3` → เปิด Terminal (**Terminal → New Terminal**, เป็น PowerShell) — ทุกคำสั่งด้านล่างรันที่โฟลเดอร์นี้

## 5. ติดตั้ง Python dependencies
**วิธีอัตโนมัติ (แนะนำ):** ขั้นที่ 8 สร้าง `.venv` และติดตั้งให้เองในครั้งแรก
**วิธีทำเอง (ถ้าต้องการรัน test ก่อน):**
```powershell
py -3.10 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r services\api\requirements.txt
```

## 6. ติดตั้ง frontend dependencies และ build
**อัตโนมัติ:** ขั้นที่ 8 ทำให้ในครั้งแรก (ถ้ายังไม่มี `apps\web\dist`)
**ทำเอง:**
```powershell
cd apps\web
npm ci
npm run build
cd ..\..
```
(ต้องใช้อินเทอร์เน็ตตอน `npm ci`/`pip install` ครั้งแรกเท่านั้น — ฟอนต์ไทยมากับแพ็กเกจ npm)

## 7. ข้อมูลสาธิต (demo data)
ฐานข้อมูล SQLite (`services\api\data\smartlibrary_demo.db`) **สร้างอัตโนมัติ** ตอนเซิร์ฟเวอร์เริ่มครั้งแรก พร้อมผังสาธิต 24 ที่นั่ง + ที่นั่ง CV Lab 4 ที่ และเริ่มสถานการณ์จำลอง `NORMAL`
อยากเริ่มใหม่ทั้งหมด: ใส่ `-Reset` ในขั้นที่ 8 (สคริปต์จะปฏิเสธถ้ายังมีเซิร์ฟเวอร์รันอยู่ — ป้องกันลบ DB ที่กำลังใช้)

## 8. เริ่มระบบ (backend + หน้าเว็บที่ build แล้ว ในพอร์ตเดียว)
```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_demo_windows.ps1
```
ตัวเลือก: `-Reset` (ฐานข้อมูลใหม่) · `-NoBrowser` (ไม่เปิดเบราว์เซอร์) · `-Port 8010` (เปลี่ยนพอร์ต)
หน้าต่างนี้ต้อง **เปิดค้างไว้** ตลอดการใช้งาน (เห็นข้อความ `Uvicorn running on http://127.0.0.1:8000`)

## 9. หน้าเว็บ (frontend)
* **ปกติ:** หน้าเว็บที่ build แล้วถูกเสิร์ฟโดย backend ที่ `http://127.0.0.1:8000/` — ไม่ต้องรันอะไรเพิ่ม
* **โหมดพัฒนา (แก้หน้าเว็บแล้วเห็นผลทันที, ไม่บังคับ):** เปิด terminal ที่สองหลังเริ่ม backend แล้ว
```powershell
cd apps\web
npm run dev
```
แล้วเปิด `http://127.0.0.1:5173/` (Vite ส่งต่อ `/api` และ `/ws` ไปที่ `:8000`)
* แก้หน้าเว็บแล้วอยากให้พอร์ต 8000 เห็นด้วย: `cd apps\web; npm run build` แล้ว refresh

## 10–13. เข้าใช้งานแต่ละหน้า
| หน้า | URL | หมายเหตุ |
|---|---|---|
| **Student Dashboard** (ผัง, StudyMatch, GroupFit, Wayfinder, SeatCheck) | `http://127.0.0.1:8000/` | ไม่ต้องล็อกอิน; แถบสีเหลืองบนสุดบอกว่าเป็น SIMULATION |
| **Staff Console** | `http://127.0.0.1:8000/#/staff` | ใส่ **demo PIN** — ค่าอยู่ในข้อความตอนเริ่มเซิร์ฟเวอร์ และใน `services\api\app\settings.py` (`staff_token`); เปลี่ยนได้ด้วย env `SL_STAFF_TOKEN` · **ห้ามใช้เป็นรหัสจริงที่ไหน** |
| **Scenario Lab** | `http://127.0.0.1:8000/#/lab` | สลับสถานการณ์จำลอง 7 แบบ (ใช้ PIN เดียวกัน) — มีเฉพาะ `SL_MODE=demo` (ค่าเริ่มต้น) |
| **CV Lab** | `http://127.0.0.1:8000/#/cv` | แสดงผล YOLO run ล่าสุดที่บันทึกไว้ (ภาพตัวอย่าง `bus.jpg`, ไม่ใช่ห้องสมุด) |

## 14. หยุดระบบ
* กด **Ctrl+C** ในหน้าต่างที่รันเซิร์ฟเวอร์ (และในหน้าต่าง `npm run dev` ถ้าเปิดไว้)
* ถ้าปิดหน้าต่างไปแล้วแต่พอร์ตยังถูกใช้:
```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | Select-Object OwningProcess
Stop-Process -Id <OwningProcess>
```

## รัน test (ตรวจว่าเครื่องคุณพร้อม)
```powershell
.venv\Scripts\python -m pytest -q                                          # ต้องได้ 53 passed
cd apps\web; npm run build; cd ..\..                                       # ต้อง build ผ่าน
powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1     # pytest + Playwright (ต้องเปิดเซิร์ฟเวอร์ที่ :8000 ไว้อีกหน้าต่าง)
```
> `scripts\check_ownership.py` (ตรวจว่าแก้เฉพาะไฟล์ของตัวเอง) ต้องรันใน **git clone** เท่านั้น — ในโฟลเดอร์จาก ZIP จะ error `not a git repository` เพราะไม่มี `.git`
> ⚠ ในโค้ดรุ่นนี้ `run_tests_windows.ps1` และ Playwright **เขียนผลทับไฟล์ใน `evidence\` และ `presentation\screenshots\`** (หลักฐาน V2) — ในโฟลเดอร์ที่แตกจาก ZIP ไม่เป็นไร; ใน git clone ให้ `git restore evidence/ presentation/screenshots/` หลังรัน และ **ห้าม commit** ไฟล์เหล่านั้น (จะแก้ถาวรเมื่อ PR #16 merge)

## 15. แก้ปัญหาที่พบบ่อย
| อาการ | สาเหตุ / วิธีแก้ |
|---|---|
| `running scripts is disabled on this system` | ใช้คำสั่งแบบ `powershell -ExecutionPolicy Bypass -File …` ตามเอกสาร (ไม่ต้องเปลี่ยน policy ของเครื่อง) |
| พิมพ์ `py` แล้วไม่รู้จักคำสั่ง หรือ `py -3.10 --version` แจ้งว่าไม่พบ 3.10 | ยังไม่ได้ติดตั้ง Python **3.10** หรือไม่ได้ติ๊ก py launcher → ติดตั้ง Python 3.10.x ใหม่ แล้วเปิด terminal ใหม่ |
| สคริปต์หยุดตอนสร้าง `.venv` ครึ่งทาง | ลบโฟลเดอร์ `.venv` แล้วรันใหม่ (สคริปต์ติดตั้งแพ็กเกจเฉพาะตอนสร้าง venv ครั้งแรก) |
| `ERROR: port 8000 is already in use` | มีเซิร์ฟเวอร์รันอยู่แล้ว → เปิด `http://127.0.0.1:8000/` หรือหยุดตัวเดิม (ข้อ 14) หรือใช้ `-Port 8010` |
| `-Reset refused: a Smart Library server is still running` | หยุดเซิร์ฟเวอร์ทุกตัวก่อน แล้วค่อย `-Reset` |
| `npm ci` ล้มเหลว | ตรวจ `node --version` (ใช้ 22 หรือ 24); ลบ `apps\web\node_modules` แล้ว `npm ci` ใหม่ |
| `npm error enoent spawn C:\WINDOWS\system32\cmd.exe ENOENT` ตอน `npm ci` | ย้ายโปรเจกต์ไป path ธรรมดา เช่น `C:\dev\SmartLibrary_NEXT_V3` (ไม่มีชื่อโฟลเดอร์แบบ UUID) → ลบ `apps\web\node_modules` → `npm ci` ใหม่ |
| `npm ci` แจ้ง `vulnerabilities` / แนะนำ `npm audit fix --force` | **อย่ารัน** `npm audit fix --force` (จะเปลี่ยนเวอร์ชันที่ทดสอบแล้ว) — ณ 16 ต.ค. 2569 มี 3 รายการระดับ high ใน **เครื่องมือ dev/test** (`vite`, `playwright`, `@playwright/test`) ไม่ใช่โค้ดที่หน้าเว็บส่งให้ผู้ใช้; การอัปเกรดต้องเสนอผ่าน CR (`package.json` = P3 + P4 อนุมัติ) |
| path ยาวเกิน / ไฟล์หาย ระหว่าง `npm ci` | ย้ายโปรเจกต์ไป path สั้น เช่น `C:\dev\…` และไม่อยู่ใน OneDrive |
| หน้าเว็บขึ้น `{"detail":"Not Found"}` หรือหน้าขาว | ยังไม่ได้ build หน้าเว็บ → `cd apps\web; npm run build` แล้ว refresh |
| แก้หน้าเว็บแล้วพอร์ต 8000 ไม่เปลี่ยน | ต้อง `npm run build` ใหม่ หรือใช้ `npm run dev` (พอร์ต 5173) |
| Staff Console บอก PIN ไม่ถูกต้อง | ใช้ค่า `staff_token` ใน `services\api\app\settings.py` (หรือค่าใน env `SL_STAFF_TOKEN` ถ้าตั้งไว้) |
| แถบสีเทา/ลาย "ข้อมูลไม่เป็นปัจจุบัน" | ตั้งใจออกแบบ: เซิร์ฟเวอร์หยุด/เชื่อมต่อไม่ได้ ระบบจะไม่โชว์ที่นั่งเป็น "ว่าง" ค้าง — เริ่มเซิร์ฟเวอร์ใหม่ |
| Playwright หา Edge ไม่เจอ | ติดตั้ง/อัปเดต Microsoft Edge (config ใช้ `channel: "msedge"` ไม่ดาวน์โหลด browser เอง) |
| อยากลอง CV (YOLO) | **ไม่จำเป็นสำหรับรันระบบ** — ทำตาม README หัวข้อ *Optional real CV* (venv แยก `.venv-cv`, ติดตั้ง torch CPU + ultralytics); ไฟล์ weights (`cv\models\`) ไม่อยู่ในแพ็กเกจ — ขั้นตอน CV บนเครื่องใหม่ **ยังไม่ได้ทดสอบ** ในรอบเตรียมแพ็กเกจนี้ |

## ไฟล์ที่ไม่อยู่ใน ZIP (ตั้งใจ)
`.git`, `.venv`, `node_modules`, `apps\web\dist`, ฐานข้อมูล `*.db`, model weights, ไฟล์ชั่วคราว — ทั้งหมดสร้างใหม่ได้ด้วยขั้นตอนข้างบน · และไฟล์ที่มี **ชื่อ/รหัสนักศึกษา** ของสมาชิก (สไลด์ V2, preview, เอกสารข้อเสนอ, สคริปต์สร้างสไลด์) — ไม่จำเป็นต่อการรันระบบ; ดูรายการใน `MANIFEST` ของ ZIP
