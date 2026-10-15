## สรุป PR (Smart Library NEXT V3)

**ผู้ส่ง / บทบาท:** P_ (CV / Backend / Student / Staff-QA)  
**Branch:** `feature/v3-...` → `main`  
**ประเภท:** feature / bugfix / test / docs / contract

### อะไรใหม่ และอะไรเป็นของ V2 อยู่แล้ว
- ใหม่:
- ของเดิมจาก V2 (ไม่ได้ทำใหม่):

### Ownership check (บังคับ)
```text
python scripts/check_ownership.py --owner P_ --base main
(วางผลลัพธ์ที่นี่ — บรรทัด REVIEW/BLOCK ต้องมีคำอธิบายและ approval ของ owner ที่เกี่ยวข้อง)
```

### API contract
- [ ] ไม่ได้เปลี่ยน `/api/*` หรือ WS message
- [ ] เปลี่ยน และอัปเดต `docs/api_contract_v3.md` แล้ว + แนบ request/response sample + P2 review แล้ว

### ผลทดสอบ (แนบคำสั่งและผลจริง ห้ามเขียน PASS โดยไม่ได้รัน)
- [ ] `.\.venv\Scripts\python.exe -m pytest -q` → ผล:
- [ ] `cd apps\web; npm run build` → ผล:
- [ ] Playwright ที่เกี่ยวข้อง (ถ้าแตะ UI/flow) → ผล:
- [ ] Screenshot/log ที่ไม่มีข้อมูลส่วนบุคคล (ถ้ามี)

### Checklist ความจริงและความปลอดภัย
- [ ] เปลี่ยนเฉพาะไฟล์ที่ถือ ownership หรือมี approval จาก owner (ระบุใครอนุมัติ)
- [ ] ไม่แตะไฟล์ FROZEN ของ V2 (`evidence/*`, `presentation/*`, `verification/*`, `reference/*`, spec ใน `docs/`) — ผลใหม่อยู่ใน `evidence/team_v3/`
- [ ] ไม่ทำข้อมูล SIMULATION ให้ดูเหมือน CV จริง; ผล CV ระบุ dataset/consent/model/version
- [ ] ไม่มี token/password, `.venv`, `node_modules`, DB, model weights, คลิป/ภาพบุคคลที่ไม่ได้รับอนุญาต
- [ ] Reviewer อย่างน้อย 1 คน (cross-owner ถ้าแตะ contract หรือไฟล์ของคนอื่น)

### ข้อจำกัด / สิ่งที่ยังไม่เสร็จ
-
