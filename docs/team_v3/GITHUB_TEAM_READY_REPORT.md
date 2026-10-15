# GITHUB_TEAM_READY_REPORT — Smart Library NEXT V3

วันที่ตรวจ: **15 ต.ค. 2569 (2026-10-15)** · ผู้จัดทำ: P4 (`Zinnarin`) ร่วมกับ Claude Code
ทุกตัวเลขในรายงานนี้มาจากคำสั่งที่รันจริงในวันที่ระบุ (คำสั่งอยู่ในแต่ละหัวข้อ) — ไม่มีผลใดที่ “คาดว่า” ผ่าน

## สรุปสถานะ (แยกตามระดับความแน่นอน)

| ระดับ | รายการ |
|---|---|
| ✅ **ตรวจยืนยันแล้ว** | repo เป็น **PRIVATE**; `main` + 4 branches + tag `v2-demo-baseline` บน GitHub ตรงกับในเครื่องทุก ref; CI สำเร็จ 2 runs (push `main`, PR #16); labels 7 อัน; issues 15 อัน; PR #16 (P4 artifact isolation) เปิดแล้ว CI เขียว; pytest/build/audit บน `main`; ไม่พบ secret / อีเมลส่วนตัวในประวัติ git; ไม่มีใครได้สิทธิ์ admin นอกจากเจ้าของ |
| ⚙️ **ตั้งค่าแล้วแต่ยังไม่ได้ทดสอบจริง** | PR template ผ่านหน้าเว็บ (PR #16 สร้างด้วย `gh` + body เอง); ขั้นตอน `--frozen-clean` ใน CI บน `main` (เข้ามาพร้อม PR #16 เท่านั้น); `CODEOWNERS.proposed` (ยังไม่เปิดใช้); ขั้นตอน onboarding โดยสมาชิกจริงบนเครื่องอื่น |
| ⏳ **รอการเชิญ** | P1, P2, P3 — **ยังไม่ได้ username** จากเจ้าของ repo จึงยังไม่เชิญ (ไม่เดา username) · pending invitations = 0 |
| ⛔ **ติดขัด** | Branch protection/rulesets (ต้อง GitHub Pro — API ตอบ 403); CV กับเก้าอี้จริง (รอการอนุญาตเรื่องกล้อง/ฟุตเทจ, #14); คำถาม CiRA CORE (#15) |

---

## 1. Repository URL
- **https://github.com/Zinnarin/SmartLibrary-NEXT**
- เจ้าของ: บัญชีส่วนตัว `Zinnarin` (ไม่ใช่ organization) · default branch: `main`
- Issues: https://github.com/Zinnarin/SmartLibrary-NEXT/issues · Actions: https://github.com/Zinnarin/SmartLibrary-NEXT/actions

## 2. Visibility
- **PRIVATE** — ตรวจด้วย `gh api repos/Zinnarin/SmartLibrary-NEXT` → `private=true visibility=private`
- ⚠ **ห้ามเปลี่ยนเป็น public และห้าม fork ออกไปเป็น public** — repo มีชื่อและรหัสนักศึกษาของสมาชิกทั้ง 4 คน (`reference/Smart_Library.pdf`, `presentation/*.pptx`, PDF preview, `scripts/build_pptx.py`) ซึ่งเจ้าของ repo ตัดสินใจอัปโหลด **เฉพาะใน private repo** เท่านั้น

## 3. Latest commit hashes
ตรวจด้วย `git ls-remote origin` เทียบ `git for-each-ref` → **ตรงกันทุก ref**

| Ref | Commit | ความหมาย |
|---|---|---|
| `main` | `c33545b` | Team Sprint V3: onboarding guide and per-member task guides |
| `feature/v3-cv` / `feature/v3-backend` / `feature/v3-student` | `c33545b` | เท่ากับ `main` (ยังไม่มีงาน) |
| `feature/v3-staff-qa` | `7e78483` | P4: record artifact-isolation verification evidence (ต่อจาก `04de68b` P4: isolate test/tool artifacts…) |
| `94f9904` | — | Team Sprint V3: collaboration setup |
| `7df4d90` | — | V2 demo baseline |

หมายเหตุ: commit ที่เพิ่มรายงานฉบับนี้จะทำให้ `main` เดินหน้าไป 1 commit (เอกสารอย่างเดียว) — สมาชิกใช้ `git merge origin/main` บน branch ตัวเองตามคู่มือ onboarding

## 4. Branch status

| Branch | เจ้าของ | สถานะ |
|---|---|---|
| `main` | P4 เป็นผู้ merge | มีเฉพาะ V2 baseline + เอกสาร/เครื่องมือทีม · **ไม่มี branch protection** (ดูข้อ 8) → ใช้กติกา merge แบบ manual |
| `feature/v3-cv` | P1 | = `main`, ยังไม่มี commit |
| `feature/v3-backend` | P2 | = `main`, ยังไม่มี commit |
| `feature/v3-student` | P3 | = `main`, ยังไม่มี commit |
| `feature/v3-staff-qa` | P4 | นำหน้า `main` 2 commits — **PR [#16](https://github.com/Zinnarin/SmartLibrary-NEXT/pull/16)** (draft): CI success, mergeable; **ยังไม่ merge** เพราะ `apps/web/playwright.config.ts` ต้องได้ approval จาก P3 ตามกติกา ownership |

## 5. Baseline tag
- `v2-demo-baseline` (annotated, tag object `c59957b`) → commit `7df4d90` — อยู่บน GitHub แล้ว (`refs/tags/v2-demo-baseline^{}` = `7df4d901…`)
- tree hash `5d30619975cf597b073b66b801032107fc0f2d99` **เหมือนเดิมทุกไบต์** ก่อนและหลังการเปลี่ยนอีเมล commit (ข้อ 6) — โค้ด/หลักฐาน V2 ไม่ถูกแก้
- กลับไปดู V2 ได้เสมอ: `git checkout v2-demo-baseline`

## 6. Security audit

| ตรวจ | วิธี | ผล |
|---|---|---|
| Visibility | GitHub API | ✅ private |
| อีเมลผู้ commit | `git log --all --format='%ae \| %ce'` | ✅ ทั้ง 5 commits ใช้ `109527005+Zinnarin@users.noreply.github.com` — เขียนประวัติใหม่ **ครั้งเดียวก่อน push ครั้งแรก** โดยเจ้าของยืนยันแล้ว; หลัง publish ไม่มี force-push |
| อีเมลส่วนตัว | `git grep -E '@gmail\.com' $(git rev-list --all)` | ✅ 0 |
| Token / key | `git grep` ทุก commit: `ghp_…`, `github_pat_`, `sk-…`, `AKIA…`, `BEGIN … PRIVATE KEY` | ✅ 0 |
| ไฟล์ต้องห้ามในประวัติ | `.db/.sqlite/.pt/.onnx/.mp4/.avi/.mov/.env` จาก `git log --all --name-only` | ✅ ไม่มี |
| ถูก ignore | `.gitignore` | `.venv/`, `.venv-cv/`, `node_modules/`, `*.db` (+ `-wal`/`-shm`), `*.pt` (yolo11n), `.pytest_tmp/`, `artifacts/` (บน branch P4) |
| ข้อมูลบุคคล | ตรวจด้วยมือ | ⚠ ชื่อ + รหัสนักศึกษา 4 คนในเอกสารนำเสนอ/อ้างอิง — อัปโหลดตามการตัดสินใจของเจ้าของ **เฉพาะ private** · `evidence/team_v3/p4_artifact_isolation/playwright_results.json` มี path ในเครื่อง (ชื่อโฟลเดอร์ผู้ใช้ Windows) — ความเสี่ยงต่ำ |
| GitHub CLI token | `gh auth status` | เก็บโดย `gh` ใน Windows Credential Manager, ไม่เคยแสดง/บันทึกลงไฟล์ · scopes: `gist, read:org, repo, workflow` |
| สิทธิ์ | `gh api …/collaborators` | ✅ มีเพียง `Zinnarin` (owner) — ไม่มีการให้ admin กับใคร |
| ฟุตเทจ/กล้อง | — | ✅ ไม่มีภาพ/คลิปบุคคล, ไม่เชื่อม CCTV มหาวิทยาลัย |

## 7. Test results

| ที่ไหน | คำสั่ง | ผล (15 ต.ค. 2569) |
|---|---|---|
| `main` ในเครื่อง | `.venv\Scripts\python -m pytest -q` | **53 passed** |
| `main` ในเครื่อง | `npm run build` (apps/web) | ✅ built |
| `main` ในเครื่อง | `scripts/check_ownership.py --audit` | **OK** — 157 ไฟล์: FROZEN 73, P1 6, P2 19, P3 16, P4 43; `git status` สะอาดหลังรัน |
| `feature/v3-staff-qa` ในเครื่อง | `scripts\run_tests_windows.ps1` | exit 0 — pytest **70 passed**, Playwright **8 passed / 0 failed / 0 flaky**, `frozen-clean: OK` |
| `feature/v3-staff-qa` ในเครื่อง | `git diff --name-only HEAD -- evidence presentation verification reference templates` หลังรันชุดเต็ม | **0 ไฟล์** (ก่อนแก้: 23 ไฟล์ถูกเขียนทับ) |
| regression ของการแก้ | `tests/test_artifact_isolation.py` | โค้ดเดิม → 6 failed (จับปัญหาได้จริง) · โค้ดที่แก้ → 17 passed |

**ไม่ได้รัน:** Playwright บน `main` — เพราะบน `main` ยังเขียนทับภาพหน้าจอ V2 ที่ freeze (สิ่งที่ PR #16 แก้) · CV suite (`.venv-cv`) — ไม่ได้เปลี่ยนในภารกิจนี้

## 8. CI status
Workflow: `.github/workflows/ci.yml` — job `backend` (Python 3.10: pytest + ownership audit; + `--frozen-clean` บน branch P4) และ `frontend` (Node: `npm ci` + `npm run build`)

| Run | Trigger | ผล | หลักฐานใน log |
|---|---|---|---|
| [38746046600](https://github.com/Zinnarin/SmartLibrary-NEXT/actions/runs/38746046600) | push `main` | ✅ success | `53 passed`, `audit: OK`, `✓ built` |
| [38746635714](https://github.com/Zinnarin/SmartLibrary-NEXT/actions/runs/38746635714) | PR #16 | ✅ success | `70 passed`, `frozen-clean: OK (no frozen V2 file changed)`, `audit: OK`, `✓ built` |

- **ไม่อยู่ใน CI:** Playwright (ต้องมีเซิร์ฟเวอร์ + Edge — รันในเครื่องด้วย `run_tests_windows.ps1`) และ CV
- คำเตือนจาก GitHub (ยังไม่ทำให้ CI พัง): `actions/checkout@v4`, `actions/setup-node@v4` ใช้ Node 20 ที่ deprecated (GitHub บังคับรันบน Node 24 แทน) · `ubuntu-latest` จะย้ายเป็น Ubuntu 26 ตั้งแต่ 19 ต.ค. 2569 — ให้ P4 ดูผล run แรกหลังวันนั้น
- **Branch protection / rulesets: ใช้ไม่ได้** — `gh api …/branches/main/protection` และ `…/rulesets` ตอบ **HTTP 403 “Upgrade to GitHub Pro or make this repository public”** → **ไม่เปลี่ยนเป็น public** ใช้กติกา manual แทน:
  1. ห้าม push ตรงเข้า `main` — ทุกการเปลี่ยนต้องผ่าน PR (collaborator ในบัญชีส่วนตัว **push เข้า main ได้ทางเทคนิค** กติกานี้จึงสำคัญ)
  2. **P4 เป็นคนเดียวที่กด Merge** และใช้ **Squash and merge**
  3. merge ได้เมื่อ: CI เขียว · `check_ownership.py --owner <P#> --base origin/main` ไม่มี `BLOCK` · ไฟล์ที่ขึ้น `REVIEW`/`OK*` ได้ approval จากเจ้าของที่ระบุ · P4 รัน `scripts\run_tests_windows.ps1` บน branch ของ PR ในเครื่องแล้ว exit 0
  4. ลำดับ merge: contract P2 → adapter P1 → backend P2 → UI P3 → Staff/QA P4 · ถ้า regression พัง ให้ revert PR นั้น ไม่แก้สดบน `main`
  - ทางเลือก: เจ้าของ repo ขอ **GitHub Student Developer Pack** (ได้ GitHub Pro ฟรี) → แล้วเปิด protection บน `main`: require PR, 1 approval, required checks `backend` + `frontend`, require Code Owners review (ติดตามใน #13)

## 9. File ownership
- กฎที่ใช้จริง: `docs/team_v3/OWNERSHIP_MAP.csv` (บรรทัดแรกที่ตรงชนะ) ตรวจด้วย `scripts/check_ownership.py`
  - `--audit` ทุกไฟล์มีเจ้าของ + ไม่มีไฟล์ต้องห้าม · `--owner P# --base origin/main` ตรวจ PR · `--frozen-clean` ไม่มีไฟล์ V2 ที่ freeze ถูกแก้
- เจ้าของหลัก: P1 `cv/**` · P2 `services/**`, test ของ backend · P3 `apps/web/src/**` ฝั่ง Student · P4 Staff Console, `apps/web/e2e/*`, `scripts/*`, `.github/*`, `docs/team_v3/*`, `evidence/team_v3/*`
- ไฟล์ร่วม (ต้อง approval 2 ฝ่าย): `playwright.config.ts` (P4+P3), `live.tsx` (P3+P4), `ScenarioLab.tsx` (P4+P2), `SeatCheckPanel.tsx` (P4+P3), `CvLab.tsx` (P3+P1), `docs/api_contract_v3.md` (ทุกคน), `package*.json` (P3+P4), `requirements.txt` (P2+P4)
- **FROZEN V2** (73 ไฟล์): `evidence/*` (ยกเว้น `team_v3/`), `presentation/*` (ยกเว้น `v3/`), `verification/*`, `reference/*`, `templates/*`, spec ใน `docs/*`
- **CODEOWNERS: ยังไม่เปิดใช้** — `docs/team_v3/CODEOWNERS.proposed` รอ username จริงของทุกคน (ตามคำสั่ง “อย่าเปิด CODEOWNERS ที่ต้องใช้ username จนกว่าจะรู้”) → issue #13

## 10. Collaborator invitation status

| สมาชิก | GitHub username | สถานะ |
|---|---|---|
| P4 — Staff/QA/Integration | `Zinnarin` | ✅ owner |
| P1 — CV | **ยังไม่ทราบ** | ⏳ ยังไม่เชิญ — รอเจ้าของ repo ให้ username (ไม่เดา) |
| P2 — Backend | **ยังไม่ทราบ** | ⏳ ยังไม่เชิญ |
| P3 — Student frontend | **ยังไม่ทราบ** | ⏳ ยังไม่เชิญ |

- ตรวจ `gh api repos/Zinnarin/SmartLibrary-NEXT/invitations` → **0 pending** · collaborators → มีแต่ `Zinnarin`
- วิธีเชิญเมื่อได้ username (สิทธิ์ collaborator ของ repo บัญชีส่วนตัว = อ่าน/เขียน/เปิด PR, **ไม่ใช่ admin** — แก้ Settings, ลบ repo, เปลี่ยน visibility ไม่ได้):
  ```powershell
  gh api -X PUT repos/Zinnarin/SmartLibrary-NEXT/collaborators/<username>
  gh api repos/Zinnarin/SmartLibrary-NEXT/invitations --jq '.[].invitee.login'
  ```
- สมาชิกต้องกดยอมรับที่ https://github.com/Zinnarin/SmartLibrary-NEXT/invitations (หรืออีเมลจาก GitHub) ภายใน 7 วัน
- หลังยอมรับ: assign issue ของแต่ละคน (label `person-1-cv` #3–#5, `person-2-backend` #1–#3, `person-3-frontend` #6–#8)

## 11. Onboarding instructions (สำหรับสมาชิกใหม่)
1. ยอมรับคำเชิญ → เปิด repo ได้
2. อ่าน **`docs/team_v3/TEAM_ONBOARDING_TH.md`** (clone, ติดตั้ง, เปิดแอป, ทดสอบ, branch, commit/push/PR, blocker)
3. Clone:
   ```powershell
   git clone https://github.com/Zinnarin/SmartLibrary-NEXT.git
   cd SmartLibrary-NEXT
   git config core.longpaths true
   git switch feature/v3-<cv|backend|student|staff-qa>
   ```
4. ตั้งค่าและเปิดแอป: `powershell -ExecutionPolicy Bypass -File scripts\start_demo_windows.ps1 -Reset` → http://127.0.0.1:8000
5. รัน baseline: `.venv\Scripts\python -m pytest -q` (ต้อง 53 passed บน `main`) และ `npm run build` ใน `apps/web`
6. อ่าน task guide ของตัวเองใน `docs/team_v3/tasks/P#_…_TASK_GUIDE_TH.md` — มี Claude Code prompt พร้อมใช้ท้ายไฟล์
7. ก่อนเปิด PR: `python scripts\check_ownership.py --owner P# --base origin/main` แล้วใช้ `.github/pull_request_template.md`
8. ⚠ จนกว่า PR #16 จะ merge: ถ้ารัน Playwright บน `main` แล้ว `git status` มีไฟล์ใน `evidence/` หรือ `presentation/screenshots/` ให้ `git restore evidence/ presentation/screenshots/` — **ห้าม commit**

## 12. Remaining blockers

| # | เรื่อง | ใครทำ | ทางออก |
|---|---|---|---|
| 1 | username ของ P1, P2, P3 | เจ้าของ repo | ให้ username → เชิญ + ตรวจ invitations (ข้อ 10) |
| 2 | Branch protection บน private repo | เจ้าของ repo | ขอ GitHub Student Developer Pack (Pro) หรือใช้กติกา manual ข้อ 8 ต่อไป |
| 3 | เปิด CODEOWNERS | P4 หลังได้ username | ใส่ username ใน `CODEOWNERS.proposed` → `.github/CODEOWNERS` ใน PR ที่ทุกคน approve (#13) |
| 4 | PR #16 รอ approval จาก P3 | P3 → P4 merge | ระหว่างนี้ Playwright บน `main` ยังเขียนทับไฟล์ V2 (ใช้ `git restore`); คำอธิบาย PR #16 ยังมีช่อง “CI บน GitHub” ไม่ได้ติ๊ก — ผล CI จริงอยู่ในข้อ 8 |
| 5 | `cv/run_cv.py` เขียนลง `evidence/cv/` (frozen) | P1 + P2 | issue #3 |
| 6 | การอนุญาตเรื่องกล้อง/ฟุตเทจ + ผังที่นั่งจริง | อาจารย์/ห้องสมุด | issue #14 (BLOCKED) — ระหว่างนี้ข้อมูลที่นั่งเป็น **SIMULATION** และต้องติดป้ายแบบนั้นเสมอ |
| 7 | CiRA CORE บังคับหรือไม่ | อาจารย์ | issue #15 (BLOCKED) — ใช้ YOLO11n ที่ทำงานได้อยู่ต่อไป |
| 8 | Node 20 deprecation / Ubuntu 26 | P4 | ดูผล CI หลัง 19 ต.ค. 2569; ถ้าพังให้อัปเดต action version ใน PR แยก |
