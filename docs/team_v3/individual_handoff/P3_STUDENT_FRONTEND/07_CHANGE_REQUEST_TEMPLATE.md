# P3 · 07 — Change request template (Student Frontend)

## When P3 needs a CR

| Your idea | Level | Who reviews |
|---|---|---|
| Redesign of layout, colours, components, interaction, new student features that use the existing API and keep the display rules | 🟢 GREEN, no CR | — |
| Drawing zones from `/api/layout` (PA-08), richer use of existing fields | 🟢 GREEN | — |
| Need a new field, query parameter or endpoint from the backend | 🟡 YELLOW | P2 |
| Editing `live.tsx`, `package.json`/`package-lock.json` (new dependency) | 🟡 YELLOW | P4 |
| Editing `CvLab.tsx` in a way that changes what CV data is shown | 🟡 YELLOW | P1 |
| Renaming or removing a `data-testid` used by e2e | 🟡 YELLOW | P4 |
| Showing real CV seats on the student map (PA-03), changing what states mean to users, relaxing a display safety rule | 🔴 RED | all 4 |

Open an issue titled `[CR][P3] …` with the label `integration`, paste the template below, and wait for P4's answer before writing code that affects others.

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
