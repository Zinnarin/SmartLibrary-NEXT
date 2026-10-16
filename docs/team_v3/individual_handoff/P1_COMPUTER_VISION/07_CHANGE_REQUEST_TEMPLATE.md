# P1 · 07 — Change request template (Computer Vision)

## When P1 needs a CR

| Your idea | Level | Who reviews |
|---|---|---|
| New detector, model, ROI method, pose, tracking or thresholds **inside `cv/**`**, still sending C1 evidence | 🟢 GREEN, no CR | — |
| New output files in `artifacts/cv/` or `evidence/team_v3/cv/` | 🟢 GREEN | — |
| Change keys of `latest_run.json` that `CvLab.tsx` reads (C1c) | 🟡 YELLOW | P3 |
| Need `SL_CV_EVIDENCE_DIR` (PA-01), a new seat ID (`LAB5`…) or a second CV camera | 🟡 YELLOW | P2 |
| A new optional field in `DetectionIn` (e.g. `seated_score`, keypoints) | 🟡 YELLOW | P2 (+ P4 tests) |
| A different decision rule in `services/api/app/engine/*` | 🟡 YELLOW, or 🔴 RED if a meaning changes | P2 + team |
| CV seats on the student map (PA-03), or CV deciding the final state itself | 🔴 RED | all 4 |

Open an issue titled `[CR][P1] …` with the label `integration`, paste the template below, and wait for P4's answer before writing code that affects others.

<!-- SYNC:BEGIN SHARED_V3/06_CHANGE_REQUEST_PROCESS_TH.md#TEMPLATE -->
> _Synced from `SHARED_V3/06_CHANGE_REQUEST_PROCESS_TH.md` section `TEMPLATE` — edit there, then run `scripts/build_handoff_packages.py --sync`._

## แม่แบบ Change Request (คัดลอกทั้งกล่อง)

```markdown
### CR: <ชื่อสั้น>
- ผู้เสนอ: P_ (<บทบาท>) · วันที่: YYYY-MM-DD · ระดับที่คิดว่าเป็น: GREEN / YELLOW / RED
- สัญญาที่เกี่ยว: C0 / C1 / C1b / C1c / C2 / C3 / C4 / PA-__ (ระบุ)

1. Proposed change (จะเปลี่ยนอะไร):
   -
2. Reason (ทำไมต้องเปลี่ยน / ปัญหาที่พบ พร้อมหลักฐาน):
   -
3. Files affected (path จริง + เจ้าของไฟล์):
   - `path/to/file` — owner P_
4. API or database impact:
   - Endpoint/field/enum/env/table ที่เพิ่มหรือเปลี่ยน:
   - เข้ากันได้ย้อนหลังไหม (client เดิมยังทำงานโดยไม่แก้): ใช่ / ไม่ — ถ้าไม่ ต้องมีแผน migration
   - ตัวอย่าง request/response ก่อน–หลัง (JSON จริงหรือร่าง ระบุชัด):
5. Expected benefit (วัดได้อย่างไร):
   -
6. Integration risk (อะไรอาจพัง / test ไหนอาจแดง / rollback ทำอย่างไร):
   -
7. Required support from others (ใครต้องทำอะไร ภายในเมื่อไหร่):
   - P_: 
8. Test plan (test ที่จะเพิ่ม/ต้องผ่าน + คำสั่ง):
   -
```
<!-- SYNC:END -->
