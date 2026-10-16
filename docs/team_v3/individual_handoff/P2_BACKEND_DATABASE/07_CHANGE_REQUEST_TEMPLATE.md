# P2 · 07 — Change request template (Backend & Database)

## When P2 needs a CR

| Your idea | Level | Who reviews |
|---|---|---|
| Internal refactor, an index, query tuning, logging, more tests, with the same JSON and C1b signatures | 🟢 GREEN, no CR | — |
| Turning an accidental 500 into a 4xx for input that was already invalid (e.g. PA-02) | 🟢 GREEN, notify P1 | P1 |
| New optional field, endpoint, env variable or error code | 🟡 YELLOW | consumers (P1, P3 and/or P4) |
| Changing thresholds, TTL, rate limits or other defaults users can see | 🟡 YELLOW | P3, P4 (and P1 for CV thresholds) |
| `services/api/requirements.txt` or `tests/conftest.py` | 🟡 YELLOW | P4 / everyone |
| A schema change visible through the API, or `response_model` | 🟡 YELLOW | all |
| Removing or renaming a route or field, changing what a state means, changing the DB engine, registering real CV seats on the public map (PA-03), weakening a safety rule | 🔴 RED | all 4 |

Open an issue titled `[CR][P2] …` with the label `integration`, paste the template below, and wait for P4's answer before writing code that affects others.

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
