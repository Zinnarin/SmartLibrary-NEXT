# docs/team_v3 — Team Sprint V3 (เริ่ม 15 ต.ค. 2569)

| ไฟล์ | สถานะ |
|---|---|
| `TEAM_ONBOARDING_TH.md` | **สมาชิกใหม่อ่านก่อน** — clone, ติดตั้ง, เปิดแอป, ทดสอบ, branch, commit/push/PR, blocker, integration |
| `tasks/P1_CV_TASK_GUIDE_TH.md` … `tasks/P4_STAFF_QA_TASK_GUIDE_TH.md` | งานของแต่ละคน (8 หัวข้อ) + Claude Code prompt พร้อมใช้ |
| `GITHUB_TEAM_READY_REPORT.md` | สถานะ GitHub repo (private), branch, tag, CI, issues, การเชิญสมาชิก |
| `TEAM_SETUP_REPORT.md` | ความพร้อมของ repo, ownership ที่ตรวจกับโค้ดจริงแล้ว, contract, ขั้นตอน GitHub (ก่อนสร้าง repo) |
| `OWNERSHIP_MAP.csv` | **กฎที่ใช้จริง** (เครื่องตรวจได้ด้วย `python scripts/check_ownership.py`) — ถ้าขัดกับ path ใน `01_FILE_OWNERSHIP.md` หรือ `roles/*.md` ให้ยึดไฟล์นี้ |
| `api_baseline_v2_openapi.json` | OpenAPI ที่ **สกัดจากโค้ด V2 จริง** (26 routes) — จุดเริ่มต้นให้ P2 เขียน `docs/api_contract_v3.md` |
| `CODEOWNERS.proposed` | ร่าง CODEOWNERS (ยังไม่เปิดใช้ ต้องใส่ GitHub username ก่อน) |
| `00_…05_*.md`, `roles/*.md`, `SPRINT_BOARD.csv` | **สำเนาต้นฉบับแบบไม่แก้ไข** จาก Team Sprint V3 handoff (ตรวจแล้วว่าตรงต้นฉบับทุกไบต์) |

## Path ที่ต้นฉบับเขียนไม่ตรงกับโค้ดจริง (ตรวจด้วย `git ls-files` 15 ต.ค.)
- `services/api/app/{state_engine,trust,evidence,config,timeutil}.py` → อยู่ที่ **`services/api/app/engine/`** (เจ้าของ P2 เหมือนเดิม)
- SeatCheck UI ปัจจุบันอยู่ **ภายใน** `apps/web/src/components/SeatDetail.tsx` (ยังไม่มี `SeatCheckPanel.tsx`) — ต้องแยกแบบ 2 PR ตามลำดับ (ดู report ข้อ 3)
- ไฟล์ที่ต้นฉบับไม่ได้กำหนดเจ้าของ แต่มีอยู่จริง: `apps/web/src/live.tsx` (P3 + P4 อนุมัติ — มีตรรกะ BUG-011), `apps/web/e2e/{demo,reliability,server_restart}.spec.ts` (P4), `services/api/app/seed.py` (P2), `tests/{test_api,test_state_engine}.py` (P2), `tests/test_reliability.py` (P4), `tests/test_roi_geometry.py` และ `cv/requirements-cv.txt` (P1), `scripts/*` (P4), `apps/web/src/{main.tsx,styles.css}` (P3)
