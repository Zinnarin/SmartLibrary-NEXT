# ส่ง prompt ให้ Claude Code ของสมาชิกแต่ละคนอย่างปลอดภัย

**ทุกคนควรอ่าน `00_START_HERE.md`, `01_FILE_OWNERSHIP.md`, `02_INTEGRATION_CONTRACT.md` และ role sheet ของตนเองก่อน.** ให้ทำงานบน Git branch ของตนจาก V2 baseline. Prompt นี้เป็นแม่แบบ ให้ใส่หมายเลขคนและ path ให้ถูกก่อนส่ง.

```text
We are working on an EXISTING Smart Library NEXT V2 application.
Do not rebuild it from scratch. Do not claim simulated seats are real CV observations.

You are team member PERSON_X. First read:
- docs/team_v3/00_START_HERE.md
- docs/team_v3/01_FILE_OWNERSHIP.md
- docs/team_v3/02_INTEGRATION_CONTRACT.md
- docs/team_v3/roles/Person_X_*.md
- evidence/FINAL_DEMO_READINESS.md (if present)

Inspect the actual code and confirm all file paths exist. Do not assume the handoff paths match exactly.
Create/checkout only my designated feature branch. Modify only my owned files.
If a shared file or API schema needs changes, STOP that specific edit and write a cross-owner request.

Implement the assigned next-sprint goals with project-local dependencies only.
Run the applicable tests, record exact pass/fail and limitations.
Never overwrite V2 evidence, never use unapproved cameras, and never commit secrets or videos of people without authorization.

Deliver: code changes, tests, a short Thai handoff README for my role, sample I/O, limitations, and a PR summary for integration.
Do not merge to main yourself.
```

**สำคัญ:** Person 4 ทำหน้าที่คนประสาน/merge coordinator; เปิด review ทุก PR, ไม่ต้องลงมือเขียนให้ทุกคน. Prompt ไม่ใช่คำอนุญาตให้ Claude ไปเชื่อมกล้องของมหาวิทยาลัย, เปลี่ยน repo settings, หรือเผยแพร่ข้อมูลส่วนบุคคลเอง.
