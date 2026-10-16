# FINAL INTEGRATION PLAYBOOK — Smart Library NEXT V3 (คู่มือรวมระบบของ P4)

> ผู้ใช้หลัก: **P4 (Staff, QA & Integration)** · ทุกคนควรอ่านข้อ 1–4 เพื่อรู้ว่างานของตัวเองจะถูกรวมอย่างไร
> อ้างอิง: `SHARED_V3/03_SHARED_API_CONTRACTS.md` (สัญญา C0–C4), `SHARED_V3/04_TEAM_WORKING_AGREEMENT_TH.md` (GREEN/YELLOW/RED), `SHARED_V3/07_FINAL_ACCEPTANCE_CRITERIA.md` (FA-xx)

## 1. หลักการรวมระบบ
1. **รักษางานของเจ้าของ:** P4 ไม่เขียนทับ algorithm/การออกแบบภายในของใคร — รวมตาม "สัญญา" ไม่ใช่ตาม "วิธีทำ"
2. **adapter ก่อน แก้โค้ดคนอื่นทีหลัง (และไม่แก้เอง):** ถ้าโมดูลเข้ากันไม่ได้แต่ไม่ผิดความหมาย → adapter ชั่วคราวใน `integration/**` (P4) + Issue ให้เจ้าของแก้ถาวร
3. **ไม่รับประกันว่าโมดูลที่เข้ากันไม่ได้จะรวมได้โดยไม่แก้:** ถ้าต้องเปลี่ยนสัญญา → เขียน CR และบันทึกใน Issue; ถ้าไม่ทัน → ไม่ merge ส่วนนั้นและรายงานเป็นข้อจำกัด
4. **ทีละ PR + regression ทุกครั้ง:** ไม่รวมหลาย PR พร้อมกันบน `main`; ถ้าพังให้ revert PR นั้น ไม่แก้สดบน `main`
5. **หลักฐานจริงเท่านั้น:** ทุกผลที่บันทึกต้องมาจากคำสั่งที่รันจริง (log/JSON)

## 2. โมเดล branch
```
feature/v3-cv | feature/v3-backend | feature/v3-student | feature/v3-staff-qa   (เจ้าของ push เอง)
        │  PR เข้า main (CI + ownership + review)
        ▼
integration/v3-r<N>   ← P4 สร้างใหม่จาก origin/main ทุกรอบ (ไม่ force-push, ไม่ใช้ซ้ำชื่อเดิม)
        │  trial-merge PR ที่จะรวม → regression เต็ม → ถ้าผ่าน
        ▼
main  ← P4 กด "Squash and merge" PR นั้นบน GitHub (ทีละอัน)  →  สุดท้าย tag v3-integrated-demo
```
* `integration/v3-rN` เป็น branch **ทดลองรวมในเครื่อง P4**; push ขึ้น GitHub เฉพาะเมื่ออยากให้คนอื่นดู (ชื่อใหม่ทุกครั้ง)
* PR หลายอันที่ต้องไปด้วยกัน (เช่น P2 PA-01 + P1 ย้ายผล CV) → trial-merge ทั้งชุดใน `integration/v3-rN` แล้วค่อย merge เข้า main ตามลำดับ dependency

## 3. ลำดับการรวม (dependencies)
| ลำดับ | PR | ต้องรอ | ไฟล์ที่ต้องมีใน PR |
|---|---|---|---|
| 1 | **P2** `docs/api_contract_v3.md` | — | สัญญาเต็ม + ตัวอย่าง JSON + test ยืนยันตัวอย่าง |
| 2 | **P4** PR #16 artifact isolation | P3 approve `playwright.config.ts` | (มีแล้ว) |
| 3 | **P2** hardening: PA-02 (422 timestamp), PA-01 (`SL_CV_EVIDENCE_DIR`), `tests/test_backend_v3.py` | 1 | code + tests + อัปเดตสัญญา |
| 4 | **P1** CV adapter/experiment: payload ตาม C1, เขียนผลนอก `evidence/cv/`, `tests/test_cv_v3.py`, `cv/experiments/<run>/README.md` | 1, 3 | code + tests + sample payload/response จริง |
| 5 | **P4** PR-A `components/SeatCheckPanel.tsx` (PA-05) | 1 | component + test เดิมผ่าน |
| 6 | **P3** UI: source/freshness/mobile, PA-08, `apps/web/e2e/student_v3.spec.ts` | 1 | code + e2e + screenshot ก่อน/หลังใน `artifacts/` |
| 7 | **P3** PR-B ใช้ `SeatCheckPanel` ใน `SeatDetail.tsx` | 5 | data-testid เดิมครบ |
| 8 | **P4** override `unknown` (#11), `apps/web/e2e/staff_reliability_v3.spec.ts`, `tests/test_contract_v3.py` | 1, 7 | tests |
| 9 | **RED เท่านั้นถ้าทีมอนุมัติ:** PA-03 ที่นั่ง CV จริงบนผัง (P2 → P1 → P3 → P4) | 1–8 | CR อนุมัติ 4/4 + migration + rollback |

## 4. ขั้นตอนต่อ 1 PR (P4 ทำ — ใช้ PowerShell ที่ root ของ repo)
```powershell
# 0) เตรียม
git fetch origin
git switch -c integration/v3-r<N> origin/main          # รอบใหม่ = ชื่อใหม่
git merge --no-ff origin/<feature-branch>                # trial merge (ถ้า conflict: หยุด → ให้เจ้าของ rebase/merge main เอง)

# 1) ownership + frozen
.venv\Scripts\python scripts\check_ownership.py --owner P<#> --base origin/main   # BLOCK = ไม่รับ, REVIEW/OK* = ต้องมี approval
.venv\Scripts\python scripts\check_ownership.py --audit

# 2) backend + frontend build
.venv\Scripts\python -m pytest -q                       # ต้อง 0 failed (≥ 53 + test ใหม่)
cd apps\web; npm ci; npm run build; cd ..\..

# 3) ระบบเต็ม (หน้าต่าง PowerShell ที่ 2: เปิดเซิร์ฟเวอร์)
powershell -ExecutionPolicy Bypass -File scripts\start_demo_windows.ps1 -Reset
# หน้าต่างที่ 1:
powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1   # pytest + Playwright (+ frozen-clean หลัง PR #16)

# 4) frozen V2 ต้องไม่ถูกแตะ
git status --short -- evidence presentation verification reference templates   # ต้องว่าง

# 5) smoke ของสัญญาที่ PR นี้แตะ (ข้อ 5)
```
⚠ **ก่อน PR #16 merge:** `run_tests_windows.ps1` บน `main` ยังเขียน `evidence\pytest_output.txt`, `evidence\playwright_output.txt` และ Playwright เขียนภาพลง `presentation\screenshots\` (FROZEN) → หลังรันให้ `git restore evidence/ presentation/screenshots/` ก่อนตรวจข้อ 4 และห้าม commit ไฟล์เหล่านั้น

**ตัดสินใจ:** ผ่านทุกข้อ + approval ครบ → Squash and merge บน GitHub → บันทึกข้อ 8 · ไม่ผ่าน → ข้อ 7

## 5. Smoke tests ต่อสัญญา (เซิร์ฟเวอร์เปิดที่ `http://127.0.0.1:8000`)
ค่า token: อ่านจาก `services/api/app/settings.py` (ค่า demo) หรือค่าที่ตั้งผ่าน env — **ห้ามเขียนลงเอกสาร/commit**
```powershell
$B = "http://127.0.0.1:8000"
$env:SL_DEVICE_TOKEN = "<device token>"; $env:SL_STAFF_TOKEN = "<staff token>"     # ตั้งในหน้าต่างนี้เท่านั้น

# C2 — ข้อมูลที่นั่ง + สถานะระบบ
$s = Invoke-RestMethod "$B/api/seats"; "seats=$($s.seats.Count) recommendable=$($s.meta.recommendable) sim=$($s.meta.simulation_active)"
(Invoke-RestMethod "$B/api/health").readiness

# C1 — ส่ง 1 เฟรม (ที่นั่ง LAB3 ว่าง) แล้วส่งซ้ำ: ต้องได้ applied แล้ว duplicate
$id  = "smoke-" + (Get-Date).ToUniversalTime().ToString("yyyyMMddHHmmssfff")
$now = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
$frame = @{ camera_id = "CV-LAB"; frame_id = $id; observed_at_utc = $now; frame_quality = "ok"; model_version = "smoke test (not a model)";
            seats = @(@{ seat_id = "LAB3"; event_id = "$id-LAB3"; detections = @() }) } | ConvertTo-Json -Depth 6
$h = @{ "X-Device-Token" = $env:SL_DEVICE_TOKEN }
(Invoke-RestMethod -Method Post "$B/api/ingest/observations" -Headers $h -ContentType "application/json" -Body $frame).results | Format-Table status, seat_id, reason
(Invoke-RestMethod -Method Post "$B/api/ingest/observations" -Headers $h -ContentType "application/json" -Body $frame).results | Format-Table status, seat_id, reason

# C4 — นักศึกษารายงาน (ต้องได้ pending และที่นั่งหลุดจากคำแนะนำ แต่ physical_state ไม่เปลี่ยน)
$tok = (Invoke-RestMethod "$B/api/session").session_token
$rep = Invoke-RestMethod -Method Post "$B/api/seat-reports" -Headers @{ "X-Session-Token" = $tok } -ContentType "application/json" `
       -Body (@{ seat_id = "A07"; reason = "reported_occupied"; client_report_id = "smoke-$id" } | ConvertTo-Json)
"report #$($rep.id) $($rep.review_status)"
$a07 = (Invoke-RestMethod "$B/api/seats/A07").seat; "A07 physical=$($a07.physical_state) recommendable=$($a07.is_recommendable) reasons=$($a07.not_recommendable_reasons -join ',')"

# C3 — เจ้าหน้าที่ปิดเคส + override unknown 5 นาที แล้วยกเลิก override
$sh = @{ "X-Staff-Token" = $env:SL_STAFF_TOKEN }
$res = Invoke-RestMethod -Method Post "$B/api/admin/seat-reports/$($rep.id)/resolve" -Headers $sh -ContentType "application/json; charset=utf-8" `
       -Body (@{ decision = "accepted"; reason = "smoke test: checked on site"; override_state = "unknown"; override_minutes = 5 } | ConvertTo-Json)
"resolved: $($res.review_status) override_id=$($res.override_id)"
(Invoke-RestMethod "$B/api/seats/A07").seat.display_state                      # ต้องเป็น unknown
Invoke-RestMethod -Method Delete "$B/api/admin/seats/A07/override?reason=smoke-done" -Headers $sh | Select-Object id, cleared_by
```
ผลที่ถูกต้อง: C1 รอบแรก `applied` รอบสอง `duplicate` · C4 `pending`, `recommendable=False`, reasons มี `PENDING_REPORT`, physical ไม่เปลี่ยน · C3 `accepted`, `display_state = unknown`, ล้าง override ได้
**หมายเหตุ:** smoke เขียนข้อมูลลง DB สาธิต — รันบนเครื่องทดสอบแล้ว `-Reset` ก่อนเดโมจริง

## 6. Adapters (ที่อยู่และกติกา)
| ตำแหน่ง (ใหม่, P4) | ใช้เมื่อ | กติกา |
|---|---|---|
| `integration/adapters/` | P1 ผลิต evidence ในรูปแบบอื่น (เช่น CiRA CORE หรือ PA-04 evidence file) ที่ยังไม่ตรง C1 | แปลง **รูปแบบ** เท่านั้น ไม่ตัดสินสถานะ, ส่งผ่าน `POST /api/ingest/observations` ด้วย device token เท่านั้น, ไม่เขียน DB, มี test, ติดชื่อ `model_version` ตามต้นทางจริง |
| `integration/smoke/` | สคริปต์ smoke ข้อ 5 แบบรันซ้ำได้ | อ่าน token จาก env, ไม่เก็บ token, ไม่ commit ผลที่มีข้อมูลบุคคล |
| `tests/test_contract_v3.py` | ตรวจว่า response จริงยังมี key/type ตาม `contract_examples/` | อ่านตัวอย่างจาก `docs/team_v3/individual_handoff/SHARED_V3/contract_examples/` |
| ฝั่ง frontend | **ไม่มี adapter ของ P4** — ถ้า type ไม่ตรง ให้ P3 แก้ที่ `apps/web/src/api.ts` (จุดเดียว) | — |
ทุก adapter ต้องมี Issue คู่กันให้เจ้าของโมดูลแก้ถาวร และต้องลบเมื่อไม่จำเป็น

## 7. การจัดการความล้มเหลว
| อาการ | ทำอะไร | ใครแก้ |
|---|---|---|
| CI แดง | ไม่ merge; comment log จริงใน PR | เจ้าของ PR |
| ownership `BLOCK` (แก้ไฟล์คนอื่น/FROZEN/ไฟล์ต้องห้าม) | ไม่ merge; ขอให้แยกเป็น CR หรือย้ายไฟล์ | เจ้าของ PR |
| test ของโมดูลอื่นแดงหลัง trial merge | ระบุว่าละเมิดสัญญาข้อไหน (C?) → Issue `bug`+`integration` ถึงเจ้าของ PR พร้อมขั้นตอนทำซ้ำ | เจ้าของ PR (owner-led) |
| สัญญาไม่ตรง แต่ทั้งสองฝั่ง "ถูกตามที่เข้าใจ" | หยุด → CR → P2 ชี้ขาดสัญญา (หรือทีมถ้า RED) | ตาม CR |
| เข้ากันไม่ได้และไม่ทันเวลา | adapter ชั่วคราว (ข้อ 6) **หรือ** ไม่ merge + รายงานข้อจำกัด — ห้ามแก้โค้ดของเจ้าของเอง | P4 + เจ้าของ |
| ไฟล์ FROZEN ถูกแก้ระหว่างทดสอบ | `git restore -- <file>`; ถ้ามาจาก PR → ไม่ merge | เจ้าของ PR |
| test flaky | รันซ้ำ 3 ครั้ง บันทึกผลทุกครั้ง; ห้ามลบ/ลด assertion เพื่อให้ผ่าน → Issue ถึงเจ้าของ test | เจ้าของ test |
| merge conflict | ให้เจ้าของ branch `git merge origin/main` แก้เอง | เจ้าของ branch |
| regression หลัง merge เข้า main | `git revert <squash-commit>` ผ่าน PR (ไม่ force-push) → แจ้งเจ้าของ | P4 revert, เจ้าของแก้ |
| เจ้าของติดต่อไม่ได้ > 1 วัน | label `blocked`; ส่วนนั้นไม่เข้า release | P4 รายงาน |

**ข้อความแจ้งเจ้าของเมื่อโมดูลละเมิดสัญญา (คัดลอกใช้):**
```text
[integration] <C1/C2/C3/C4> ไม่ตรงสัญญา — PR #<n> (<branch>) @ <commit>
ทำซ้ำ: <คำสั่ง>   ผลจริง: <log/JSON>   ตามสัญญาควรเป็น: <อ้างหัวข้อใน 03_SHARED_API_CONTRACTS.md>
ผลกระทบ: <test ที่แดง / หน้าจอ>   ขอให้: แก้ใน branch ของคุณ หรือเปิด CR ถ้าต้องการเปลี่ยนสัญญา
```

## 8. Regression log หลังทุก merge
บันทึกใน `evidence/team_v3/integration/INTEGRATION_LOG.md` (P4): วันที่, PR, commit หลัง merge, ผล `pytest`/build/Playwright/frozen check (ตัวเลขจริง), smoke ที่รัน, ปัญหา/Issue ที่เปิด; เก็บ output ไฟล์ใน `artifacts/` และคัดลอกฉบับสำคัญไป `evidence/team_v3/integration/`

## 9. Final acceptance checklist (ก่อน tag)
- [ ] FA-01…FA-05 (regression, build, ownership/frozen, CI) — รันบน commit สุดท้าย
- [ ] FA-10…FA-15 (สัญญา C1–C4 + e2e ใหม่)
- [ ] FA-20…FA-24 (ความปลอดภัย/ความซื่อสัตย์ + screenshot ทุกหน้า)
- [ ] FA-30 **หรือ** FA-31 (CV วัดจริง หรือ BLOCKED อย่างซื่อตรง)
- [ ] FA-40…FA-43 (start คำสั่งเดียว, เส้นทาง CV, release notes, หลักฐาน)
- [ ] FA-50…FA-52 (PR ทุกอันผ่านกระบวนการ, CR ครบ, เครดิต)
- [ ] ทีมอนุมัติ release ใน Issue → P4 สร้าง tag `v3-integrated-demo` (push tag ตามที่เจ้าของ repo อนุญาต)

## 10. สิ่งที่ P4 ห้ามทำ
แก้โค้ดภายใน `cv/**`, `services/**`, หน้า Student โดยไม่ผ่านเจ้าของ · merge PR ที่ CI แดง/ไม่มี approval · ลด/ลบ test เพื่อให้ผ่าน · force-push `main` · ใส่ผลที่ไม่ได้รัน · ทำ repo เป็น public
