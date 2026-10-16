# P4 · 07 — Change request template (Staff, QA & Integration)

You both **write** CRs (for your own cross-module changes) and **decide** on them (as the coordinator).

## When P4 needs a CR

| Your idea | Level | Who reviews |
|---|---|---|
| Staff Console UI or workflow using existing C3 routes; new tests; scripts; docs; adapters in `integration/**` | 🟢 GREEN, no CR | — |
| `SeatCheckPanel.tsx` props (PA-05), changing `data-testid` values | 🟡 YELLOW | P3 |
| `ScenarioLab.tsx`, `tests/test_reliability.py`, `pytest.ini`, `scripts/start_demo_windows.ps1` | 🟡 YELLOW | P2 |
| New staff API needs (e.g. per-staff identity, bulk resolve) | 🟡 YELLOW | P2 |
| Making CI stricter (a new required check) | 🟡 YELLOW | all |
| Anything that would change another module's internals | not allowed: report to the owner instead | — |

## How you decide on others' CRs (answer within 1 working day)

1. **Classify.** If it is not optional, or changes a meaning, or touches the public map or a safety rule, it is RED. If it adds something optional or touches a co-approved file, it is YELLOW.
2. **Check the impact.** Which contract section (C0–C4)? Which consumer tests would break (`03_SHARED_API_CONTRACTS.md` → CT)?
3. **Reply** in the issue with ✅ (level, conditions, reviewers), ❓ (questions) or ⛔ (reason plus an alternative: optional field, adapter, or postpone).
4. **RED** needs 👍 from all four in the issue before work starts.

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
