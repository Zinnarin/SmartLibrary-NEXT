# TEAM GITHUB WORKFLOW — ทำงานร่วมกันผ่าน GitHub (ฉบับละเอียด)

> Repository: **`Zinnarin/SmartLibrary-NEXT`** (**private**) · เข้าได้หลังจากเจ้าของ repo (P4) ส่งคำเชิญ และคุณกด **Accept** ในอีเมล/หน้า GitHub แล้วเท่านั้น
> เอกสารนี้ขยายความจาก `docs/team_v3/TEAM_ONBOARDING_TH.md` — กติกาเหมือนกัน

## 0. เข้าใจก่อน: ZIP, clone และการแชร์งาน
* **ZIP ซอร์สโค้ด** = สำเนาไว้อ่าน/รัน ไม่มีประวัติ git → **ห้ามใช้ส่งงาน** (อย่าคัดลอกไฟล์ที่แก้ใน ZIP ไปทับใน clone)
* **`git clone`** = สร้าง **สำเนา repo ในเครื่องคุณ** (มีประวัติทั้งหมด) — **ไม่ได้ sync อัตโนมัติ** กับเครื่องเพื่อน:
  งานที่คุณแก้แต่ยังไม่ commit/push จะอยู่แค่ในเครื่องคุณ และงานของเพื่อนจะมาถึงเครื่องคุณก็ต่อเมื่อเพื่อน **commit → push** และคุณ **fetch/merge** เท่านั้น
* ลำดับการแชร์งาน: **แก้ไฟล์ → `git add` → `git commit` → `git push` → เปิด Pull Request → P4 ตรวจและ merge → ทุกคน `git fetch` + `git merge origin/main`**

## 1. ติดตั้งและตั้งค่า Git ครั้งแรก
```powershell
git --version                                   # ควรได้ git version 2.x
git config --global core.longpaths true         # กัน "Filename too long" บน Windows
git config --global user.name  "ชื่อของคุณ"
git config --global user.email "อีเมลที่ผูกกับ GitHub หรืออีเมล noreply ของ GitHub"
```
> อีเมล noreply ดูได้ที่ GitHub → Settings → Emails (ช่วยไม่ให้อีเมลส่วนตัวไปอยู่ในประวัติ commit)

## 2. ยืนยันตัวตนกับ GitHub (ปลอดภัย ผ่านเบราว์เซอร์)
* Git for Windows มาพร้อม **Git Credential Manager**: ครั้งแรกที่ `clone`/`push` repo private จะเด้งหน้าต่างให้ **Sign in with your browser** → ล็อกอิน GitHub ในเบราว์เซอร์ → อนุญาต
* หรือใช้ GitHub CLI: `gh auth login` → เลือก GitHub.com → HTTPS → Login with a web browser
* **ห้าม** ส่ง/วางรหัสผ่านหรือ token ในแชท, ในไฟล์ หรือในคำสั่ง; ห้าม commit token

## 3. Clone (ครั้งเดียว)
```powershell
cd C:\dev
git clone https://github.com/Zinnarin/SmartLibrary-NEXT.git
cd SmartLibrary-NEXT
```
ติดตั้งและรันตาม `docs/team_v3/TEAM_LOCAL_SETUP_TH.md` (ขั้นที่ 5–13 ใช้ได้กับ clone เหมือน ZIP)

## 4. สลับไปยัง branch ของคุณ และตรวจว่าอยู่ branch ถูก
| คน | Branch |
|---|---|
| P1 Computer Vision | `feature/v3-cv` |
| P2 Backend & Database | `feature/v3-backend` |
| P3 Student Frontend | `feature/v3-student` |
| P4 Staff, QA & Integration | `feature/v3-staff-qa` |
```powershell
git switch feature/v3-<cv|backend|student|staff-qa>
git branch --show-current        # ต้องแสดงชื่อ branch ของคุณ
git status                       # ต้องเห็น "On branch feature/v3-..." และ "nothing to commit" ก่อนเริ่มงาน
```
ถ้าต้องการ branch ย่อยสำหรับงานหนึ่ง: `git switch -c feature/v3-cv-pose` (ให้ขึ้นต้นด้วย branch ของคุณ เพื่อให้ CI รู้ว่าเป็นของใคร)

## 5. ดึงงานล่าสุด (ทำทุกวัน และก่อนเปิด PR)
```powershell
git fetch origin
git merge origin/main
```
> ครั้งแรกหลังได้รับคำเชิญ: ทำ 2 คำสั่งนี้เพื่อให้ branch ของคุณมีเอกสาร V3 ล่าสุดที่ merge เข้า `main` แล้ว
> `git pull` บน branch ของคุณ = ดึงงานที่ **คุณเอง** push ไว้จากอีกเครื่อง (ไม่ได้ดึง `main`)

## 6. ก่อน commit: ตรวจว่าไม่ได้แก้ไฟล์ของคนอื่น
```powershell
git status                                                                   # ดูว่าแก้ไฟล์อะไรบ้าง
git diff                                                                     # ดูรายละเอียดที่แก้
.venv\Scripts\python scripts\check_ownership.py --owner P<1|2|3|4> --base origin/main
```
* `OK` = ไฟล์ของคุณ · `OK*`/`REVIEW` = ต้องได้ approval ของเจ้าของที่ระบุใน PR · `BLOCK` = **แก้ไฟล์ของคนอื่น/ไฟล์ FROZEN/ไฟล์ต้องห้าม → ต้องเอาออกก่อน**
* คืนไฟล์ที่ไม่ได้ตั้งใจแก้: `git restore <path>` (เช่น `git restore evidence/ presentation/screenshots/` หลังรัน test)
* เจ้าของไฟล์ทั้งหมดอยู่ใน `docs/team_v3/OWNERSHIP_MAP.csv` และสรุปใน `docs/team_v3/individual_handoff/P*/03_EXISTING_CODE_AND_OWNERSHIP.md`

## 7. Commit
```powershell
git add <ไฟล์ที่ตั้งใจแก้ทีละไฟล์>          # หลีกเลี่ยง git add -A ถ้าไม่แน่ใจ
git commit -m "[P3][Student] แสดงป้าย SIMULATION/CV บนการ์ดที่นั่ง"
```
commit เล็ก ๆ บ่อย ๆ ข้อความบอกว่าทำอะไร · **ห้าม commit:** `.venv`, `node_modules`, `*.db`, weights, วิดีโอ/ภาพบุคคล, token/รหัสผ่าน (ส่วนใหญ่ถูก `.gitignore` กันไว้แล้ว แต่ต้องตรวจเองด้วย `git status`)

## 8. Push
```powershell
git push origin feature/v3-<ของคุณ>          # ครั้งแรกของ branch ย่อยใช้: git push -u origin <ชื่อ branch>
```
**ห้าม** `git push origin main` · **ห้าม** `git push --force` · **ห้าม** push branch ของคนอื่น

## 9. เปิด Pull Request
1. เปิด `https://github.com/Zinnarin/SmartLibrary-NEXT` → แถบ **Compare & pull request** (หรือ Pull requests → New) 
2. **base: `main`** ← **compare: branch ของคุณ**
3. กรอกตาม template ที่ขึ้นมาอัตโนมัติ (`.github/pull_request_template.md`): อะไรใหม่, ผล test จริง, ผล ownership check, ข้อจำกัด, ส่วนที่ AI ช่วย
4. ใส่ label ของคุณ (`person-1-cv` / `person-2-backend` / `person-3-frontend` / `person-4-qa`) และ `Closes #<issue>`
5. รอ CI (backend + frontend) เขียว + review — **P4 เป็นคนเดียวที่ merge** (Squash and merge) ตาม `docs/team_v3/individual_handoff/FINAL_INTEGRATION_PLAYBOOK_TH.md`
6. ถูกขอให้แก้: แก้ใน branch เดิม → commit → push อีกครั้ง (PR อัปเดตเอง)

## 10. แก้ conflict ทั่วไป
เกิดเมื่อ `git merge origin/main` แล้วไฟล์เดียวกันถูกแก้ทั้งสองฝั่ง:
```powershell
git status                      # ดูไฟล์ที่ขึ้นว่า "both modified"
# เปิดไฟล์ใน VS Code → เลือก Accept Current / Incoming / Both ตรงเครื่องหมาย <<<<<<< ======= >>>>>>>
git add <ไฟล์ที่แก้เสร็จ>
git commit                      # ปิด merge
.venv\Scripts\python -m pytest -q   # ตรวจว่ายังผ่าน
```
* ถ้า conflict อยู่ใน **ไฟล์ของคนอื่น** → อย่าเดา: เลือกฝั่ง `main` (`git checkout --theirs <file>` แล้ว `git add`) หรือถามเจ้าของไฟล์/P4
* ยกเลิก merge ที่ยุ่งเกินไป: `git merge --abort` (กลับไปสถานะก่อน merge)

## 11. ไม่แก้ไฟล์ของคนอื่น — ถ้าจำเป็นต้องเปลี่ยน
* เปลี่ยนภายในไฟล์ของตัวเอง (🟢 GREEN) → ทำได้เลย
* ต้องแตะไฟล์/API ของคนอื่น (🟡 YELLOW / 🔴 RED) → เปิด Issue `[CR][P#] …` ตาม `07_CHANGE_REQUEST_TEMPLATE.md` ในชุดของคุณ แล้วรอ P4 ตอบก่อน
* เจอบั๊กในโมดูลคนอื่น → เปิด Issue `bug` ถึงเจ้าของ (ขั้นตอนทำซ้ำ + ผลจริง + ผลที่คาด) — เจ้าของเป็นคนแก้

## 12. สรุปคำสั่งประจำวัน
```powershell
git switch feature/v3-<ของคุณ>
git fetch origin
git merge origin/main
# ... แก้งาน + รัน test ...
git status
.venv\Scripts\python scripts\check_ownership.py --owner P<#> --base origin/main
git add <ไฟล์>
git commit -m "[P#][...] ..."
git push origin feature/v3-<ของคุณ>
```
