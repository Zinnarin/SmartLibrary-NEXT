# SMART LIBRARY NEXT — UNIFIED ENGINEERING SPECIFICATION V2

**วันที่เอกสาร:** 14 ตุลาคม 2569  
**สถานะ:** Approved design direction / awaiting implementation and verification  
**เป้าหมาย:** สร้างต้นแบบในเครื่องที่อาจารย์ทดลอง workflow ได้ในวันที่ 15 ตุลาคม 2569 โดยรายงานผลจริง ไม่ใช้ข้อมูลจำลองแอบอ้างเป็น Computer Vision  
**ชื่อเต็ม:** Smart Library NEXT — An Edge-AI-Based Intelligent Seat Discovery and Reliable Space Monitoring System  
**Tagline:** Find. Verify. Study.

> **SOURCE OF TRUTH:** เอกสารนี้รวม (1) สไลด์ข้อเสนอโครงงาน Smart_Library.pdf 15 หน้า ลงวันที่ 1 ต.ค. 2569 และ (2) Smart_Library_Seat_Proposal.docx 11 หน้า 13 หัวข้อ ลงวันที่ 30 ก.ย. 2569 เข้ากับคุณสมบัติที่ร่วมออกแบบภายหลัง เช่น StudyMatch, GroupFit, Wayfinder, SeatCheck. ข้อเสนอต้นฉบับเป็นแผน ไม่ใช่หลักฐานว่าระบบถูก implement แล้ว. ค่า threshold/hardware เป็น *สมมติฐานตั้งต้น*.

## 1. Problem, outcome and differentiator

**ปัญหาที่ต้องแก้จริง:** นักศึกษาต้องเดินหาที่นั่งเอง; ที่นั่งเหมือนว่างแต่มีคน/ของ; ไม่รู้พื้นที่เงียบหรือปลั๊กไฟ; มากับเพื่อนแล้วไม่พบที่นั่งติดกัน; ข้อมูลกล้อง/เครือข่ายอาจเก่าจนพาไปยังที่นั่งผิด; เจ้าหน้าที่ไม่มี workflow รับแจ้งความคลาดเคลื่อนอย่างเป็นระบบ. (ปัญหา 3 ข้อแรกเป็นปัญหาจากเอกสารต้นฉบับ; ข้อ feedback loop เป็นข้อเสนอเพิ่ม)

**ผลลัพธ์ที่ต้องแสดงให้เห็น:** นักศึกษาเลือกเงื่อนไข -> ได้ที่นั่งว่างที่มีหลักฐานสด/น่าเชื่อถือ -> ดูเส้นทางจำลอง -> ถ้าถึงที่แล้วสถานะผิดกด SeatCheck -> เจ้าหน้าที่ตรวจ/แก้ -> ทุกหน้าจออัปเดตอย่างถูกต้อง -> มีหลักฐานทดสอบ.

**Novelty claim อย่างระมัดระวัง:** ระบบตรวจจับที่นั่งมีงานมาก่อนแล้ว. จุดแตกต่างของโครงงานนี้คือการบูรณาการ *trust-aware seat discovery + explainable matching + student-to-staff discrepancy resolution* และวัด False Available รวมถึงผลกระทบต่อเวลาหาที่นั่ง. ไม่อ้างว่าเป็นระบบแรกของโลก.

## 2. Requirement priority / non-goals

| ID | Priority | Requirement | Acceptance outcome |
|---|---|---|---|
| R01 | P0 | Student Floor Map พร้อม 24 ที่นั่งสาธิต, 3 โซน, filter หลายเงื่อนไข | เลือกดูข้อมูลที่นั่งได้บน desktop/mobile; metadata สมมติมีป้าย |
| R02 | P0 | Seat State Engine + ความสดใหม่ของข้อมูล | เมื่อข้อมูลเก่า/unknown ห้ามแนะนำเป็นว่างแน่ชัด |
| R03 | P0 | Backend SQLite + REST + WebSocket จริง | อีกหน้าต่างเห็นสถานะเปลี่ยนหลัง API update |
| R04 | P0 | StudyMatch แบบ explainable | hard constraints ถูกต้อง, แสดงเหตุผลและ no-result state |
| R05 | P0 | SeatCheck รายงานข้อมูลไม่ตรง | บันทึก report, รายงานรอตรวจ, ไม่เปลี่ยนสถานะจริงเอง |
| R06 | P0 | Staff Console + audit log | ตรวจ report, override, ปิดเคสพร้อมเหตุผล, เห็น log |
| R07 | P0 | Scenario Lab จาก backend | NORMAL, EXAM_RUSH, BELONGINGS, FALSE_FREE_REPORT, LOW_CONFIDENCE, CAMERA_LOST, RECOVERED |
| R08 | P0 | Tests + proof + 3-min presentation | มีคำสั่งรัน, tests output, screenshot จริง, editable PPTX |
| R09 | P0-B | GroupFit 2 ที่นั่งติดกันจริงตาม adjacency graph | คู่ที่แนะนำผ่าน seat eligibility และ adjacency |
| R10 | P0-B | Wayfinder บน waypoint graph | route เป็น path ต่อเนื่องที่มี edges จริง; demo floor เท่านั้น |
| R11 | P1 | CV vertical slice: OpenCV + YOLO + ROI (authorized media) | มี inference log จริง หรือ blocker ที่ตรวจสอบได้ |
| R12 | P1 | SeatWatch in-app + admin analytics | ทำเมื่อ P0 ผ่าน; mock traffic แยกจากข้อมูลจริง |
| R13 | P2 | Hardware edge, PoE/RTSP, MQTT, TLS, store-forward, cloud, TV, LED/UPS | เอกสารสถาปัตยกรรม/plan เท่านั้นจนกว่าจะทดลองจริง |

**Non-goals:** ทำระบบจองที่นั่งอย่างเป็นทางการ, ยึดสิ่งของ, รู้ตัวบุคคล/recognition, GPS indoor จริง, วิเคราะห์อารมณ์, วัดเสียงโดยไม่มีอุปกรณ์หรือความยินยอม, ติดตั้ง/เข้าถึง CCTV มหาวิทยาลัยเอง, อ้างว่า PDPA-compliant ผ่านการรับรอง.

## 3. Architecture and module boundaries

```text
Camera / authorized local clip           Demo scenario control (explicitly labelled)
             |                                          |
      ObservationSource: YOLO                      ScenarioSource
       OpenCV + detection                              |
             |                                         |
       SeatEvidenceAdapter ----------------------------+
         class normalization; frame quality; video ROI
                             |
                       SeatStateEngine
             confidence/visibility + temporal smoothing
                 state, timestamps, uncertainty
                             |
     FastAPI + SQLite transaction / idempotent event ingestion
                             |
           REST API + WebSocket + health/freshness
                             |
             +---------------+-----------------+
          Student           Staff            Scenario Lab
      map / StudyMatch    reports/admin     simulated events
      GroupFit/Route      audit/overrides   for test only

FUTURE separated adapter: edge SQLite buffer -> MQTT QoS1/TLS -> server
```

**Enforcement:** Core state computation is independent of frontend and observation source. Simulation **must** use the same seat engine and state persistence path as genuine CV data. Keep demo fixtures separate from actual measured data.

**Local implementation choices:** React + TypeScript + Vite + Tailwind (frontend), Python + FastAPI + SQLAlchemy/SQLite + pytest (backend), WebSocket for updates (polling fallback). Use package-lock and python venv, Windows PowerShell scripts. No API keys, paid cloud, global package install or Docker requirement for tomorrow. Tool/library selection can be adapted if local environment blocks it; log deviations.

## 4. Domain ontology: avoid false certainty

The original proposals defined 5 statuses: **Available**, **Occupied**, **Reserved**, **Unavailable**, **Maintenance**. Keep them for traceability. Add `Unknown` as an algorithmic output. Separately model freshness (`fresh/stale`), device health (`healthy/degraded/offline`), active student report (`yes/no`), evidence source (`scenario/cv/staff`), and staff override (`none/unavailable/maintenance`).

- `AVAILABLE`: observed seat has no detected person/belongings *with adequate visibility and stability*. Must not be inferred from one missing bounding box.
- `OCCUPIED`: evidence of seated person is sufficient over time. Generic person bbox overlap alone is not proof; walking near the chair may be unknown.
- `RESERVED` (UI: `พบสิ่งของ / อาจถูกจับจอง`): persistent supported personal belongings in a calibrated belongings/table ROI, no confirmed seated occupant. It is **not** a real booking. After timeout flag for staff; never auto-release/clear belongings.
- `UNAVAILABLE`/`MAINTENANCE`: administrative manual overrides; have precedence over automatic seat state but do **not** hide sensor connectivity status.
- `UNKNOWN`: camera view unavailable, object detection inconclusive, heavy occlusion, uncalibrated ROI, clock skew or insufficient evidence. `STALE` is a **separate freshness overlay**, not an automatic occupied/available replacement.

| Observed evidence | Physical state | Can appear in high-trust recommendation? |
|---|---|---|
| Repeatable empty and visible ROI, recent | Available | Yes, absent unresolved mismatch report |
| Seated person evidenced, recent | Occupied | No |
| Belongings sustained, no seated person | Reserved (possibly) | No |
| Occlusion / movement ambiguity / low quality | Unknown | No |
| Data older than freshness TTL | Last state + Stale overlay | No |
| Staff closes chair | Unavailable/Maintenance override | No regardless of camera |
| Unresolved user discrepancy report | Keep observed status + pending flag | Exclude/deprioritize from *high trust* matches |

Initial interval 1–2 s, smoothing ~5 s, confidence ~0.5, report 30 minutes, heartbeat ~30 s are from peer's **proposed settings**, not performance claims. Expose safe config and assess experimentally. `observed_at` from source and `ingested_at` are separate; normalized timestamps UTC, Thai UI local timezone. Old out-of-order events never roll back current state; idempotent `event_id/message_id` prevents duplicate histories. For a state transition, store evidence codes and actual source. Failure to observe cannot be interpreted as empty.

## 5. CV design: proof without exaggeration

1. In P1 use only operator-authorized video or controlled staged webcam scene. No live institution camera without formal consent. Process locally; video/frame retention disabled by default.
2. Enumerate pretrained model's actual classes (e.g. COCO `person/chair/laptop/book/backpack/handbag`); do not assume a generic class `bag`. Fine-tuning requires actual labeled dataset + training log; none currently supplied.
3. Video ROIs are distinct from *floor-map seat coordinates*. For each seat, define seating area and tabletop/belongings area polygons. Calibrate against camera position. Give a basic ROI editor/JSON mapping if feasible.
4. Account for walk-through, occlusion, partial views, chairs moved, ambiguous items (cup), lighting changes, and camera movement. Use quality checks + Unknown rather than make unsafe Available claims.
5. Actual YOLO run requires: source, permission, model artifact, model version/weight, actual inference execution log, platform, image/video sample size, and explicit limitation. Do not fabricate detections in a canvas and call it CV.
6. If unavailable/blocked, tag CV as `BLOCKED` or `WORKING_UNVERIFIED`; demonstrate P0 state engine with backend-driven, visibly simulated inputs and a reproducible CV setup guide.

## 6. Seat discovery and feedback algorithms

**StudyMatch:** filter seats using hard constraints first: `physical_state=Available`, `fresh`, `source trust sufficient`, no staff block, no unresolved serious SeatCheck, same acceptable floor/seat type/power/quiet requirements. Then rank by explainable preferences such as proximity and window. Do not represent ranking score as a calibrated probability. Return reason codes and human-readable explanations. If no match, suggest which optional preference could be relaxed; never relax must-have constraints automatically.

**GroupFit:** use a *manually authored adjacency graph* `SeatAdjacency` representing actual side-by-side seats, not nearest pixel distance. For 2 people, find eligible edges; for more, explicitly label future algorithm and do not fabricate continuous tables. If unavailable, show explanatory empty state.

**Wayfinder:** demo indoor graph `Waypoint/WaypointEdge` from a specified entrance waypoint to each demo seat; shortest path uses Dijkstra/BFS depending on weight. Do not claim physical meter distance, GPS precision, wheelchair accessibility or actual building route before validation.

**SeatCheck:** `student submits reason -> new report pending -> badge on seat -> candidate excluded/deprioritized -> staff review -> optional staff override (with reason/expiration) -> resolve/reject -> audit event -> live student update`. One anonymous report never unilaterally labels seat occupied. Apply rate limits + a bounded anonymous demo session token; protect admin endpoints; avoid collecting photos, identity, or free text unless necessary. No punitive policy for personal belongings.

## 7. Minimal persistence and API contract

**Tables:** `seats`, `seat_adjacency`, `waypoints`, `waypoint_edges`, `seat_observations`, `seat_current`, `seat_reports`, `manual_overrides`, `system_events`, `device_health`, `scenario_runs`. Required event metadata: unique ID, seat ID, `observed_at_utc`, `ingested_at_utc`, source (`scenario/cv/staff`), raw evidence, derived state, confidence (nullable), frame quality, revision, event sequence. Ensure referential integrity and repeatable seed/reset in demo DB.

**REST:**

```text
GET    /api/health
GET    /api/zones
GET    /api/seats
GET    /api/seats/{seat_id}
GET    /api/recommendations?power=true&quiet=true&group_size=1
GET    /api/route?from=ENTRANCE&to=A07
POST   /api/seat-reports
GET    /api/admin/seat-reports                 [demo-staff auth]
POST   /api/admin/seat-reports/{id}/resolve    [demo-staff auth]
POST   /api/admin/seats/{id}/override          [demo-staff auth]
DELETE /api/admin/seats/{id}/override          [demo-staff auth]
GET    /api/admin/events                       [demo-staff auth]
POST   /api/demo/scenario                      [demo-mode only]
WS     /ws/seats
```

**Example seat response:**

```json
{
  "seat_id": "A07", "zone": "Quiet A", "has_power": true,
  "physical_state": "available", "source": "scenario",
  "observed_at_utc": "2026-10-14T09:00:00Z", "is_stale": false,
  "camera_health": "healthy", "quality_flag": "normal",
  "pending_discrepancy": false, "manual_override": null,
  "is_recommendable": true
}
```

This is a **contract example**, not evidence of live measurements. Source `scenario` + visible SIMULATION banner must accompany sample UI. Database changes and overrides should be atomic; WebSocket event can be retried/replaced by a fresh GET after reconnect. Do not expose admin writes publicly on a hosted production deployment; localhost demo gate is explicitly not production authentication.

## 8. Acceptance tests / scenarios

| Test | Input/action | Required observable behavior |
|---|---|---|
| T01 | NORMAL, load 24 seeded seats | UI/API counts match; SIMULATION visible |
| T02 | Quiet + power hard filters | All recommended seats satisfy both and eligible state |
| T03 | CAMERA_LOST, wait TTL | Former green seats no longer recommended; stale warning shows last update |
| T04 | LOW_CONFIDENCE | Unknown/nonrecommendable, not secretly green |
| T05 | BELONGINGS persisted | Mark possibly reserved, not booked; no 30-min auto-release |
| T06 | Cup, passerby, one empty frame | No immediate false Reserved/Occupied/Available |
| T07 | Staff Maintenance, then detection | Manual block wins; events logged; health still visible |
| T08 | SeatCheck mismatch report | Case logged and displayed; no automatic occupied status |
| T09 | Staff resolves with reason | Audit event + student UI change via WS/poll; state transition correct |
| T10 | Duplicate report / no auth admin write | Rate limited/denied as configured; log suitable errors |
| T11 | GroupFit | Both seats eligible and adjacent as stored |
| T12 | Wayfinder | Route consists solely of declared graph edges |
| T13 | Out-of-order/double event | Idempotent; current seat not reverted |
| T14 | App runs with YOLO absent | Backend/frontend still work in openly labeled demo mode |
| T15 | CV source authorized | Real model/ROI observation logged, not generic mock inference |
| T16 | Screenshot / PPTX audit | Screenshot is from actual running app; status claims match evidence |

**Quality gate for tomorrow:** pass T01–T04, T07–T09, T14 plus browser happy-path before slide finalization. T05–T06 state-engine tests are highly desirable if implemented; T11–T12 only if features exist. Explicitly report `NOT_RUN`, `BLOCKED`, `FAIL` rather than fabricate PASS.

## 9. Evaluation and real-world validity plan

Primary *risk metric*: **False Available rate** = number of assessments shown as Available when a manually verified seat is not actually available / number of assessments shown as Available in the evaluation dataset. Also report *seat-state confusion matrix*, precision/recall, Unknown/abstention coverage, latency `observation -> user UI`, missed-stale rate, recommendation success, report resolution latency. For CV mAP report only if true labeled ground-truth object boxes are available. Separately compare manual floor-map search versus recommendation under a task-based timed user study; label `PLANNED` until there are consenting participants and raw records.

**Evidence provenance:** each metric must say `real CV` / `simulated scenario` / `unit test` / `future hypothesis`; include sample size, protocol, source, timestamps, test machine and commands. Never combine simulated events into actual detector accuracy or invent % improvement.

## 10. Privacy, accessibility and deployment governance

No facial recognition or identity matching. No raw camera stream on student pages. Store only necessary event metadata with minimal retention and access rules; do not add photographs to student reports. Camera installation/processing requires permission and evaluation of applicable privacy policy/PDPA, signage, role access and lifecycle. University indoor maps and seat attributes must be verified before production. Admin writes must be guarded and audited. Provide keyboard-operable map controls, clear text state labels (do not communicate only via color), responsive mobile UI, Thai labels and stale timestamps.

## 11. Definition of done, timeboxing and truthful handoff

**Milestone M0** inspect the existing workspace/tools and create a small working skeleton (do not overwrite sources).  
**M1** backend seat state/data, scenario routes, WebSocket, tests.  
**M2** student map + StudyMatch.  
**M3** SeatCheck to staff resolution & audit, all visible live.  
**M4** GroupFit/Wayfinder if M1–M3 have passed.  
**M5** make a legitimate attempt at YOLO/ROI with permitted local video; if blocked write reason and setup steps.  
**M6** capture real screenshots; build editable Thai 16:9 7–8 slide PPTX + 3-minute script + test/bug evidence.  

Artifacts Claude Code must create in its own workspace:

```text
README.md                           local Windows launch and demo modes
apps/web/                           responsive student + staff interface
services/api/                       FastAPI core, state engine and source adapters
tests/                              pytest and optionally Playwright
scripts/start_demo_windows.ps1      reproducible launch
presentation/progress_update.pptx   editable 16:9 deck
presentation/three_minute_script_th.md
presentation/screenshots/           authentic captures
evidence/IMPLEMENTATION_REPORT.md   feature-by-feature verified status
evidence/TEST_RESULTS.md            commands and logs
evidence/BUG_LOG.md                 actual bugs vs risks separated
```

**Implementation labels:** `WORKING_TESTED`, `WORKING_UNVERIFIED`, `SIMULATION_ONLY`, `DESIGNED_ONLY`, `BLOCKED`. Claude must keep these truthful for every feature and supply reproducible run commands.

## 12. Traceability and discussion points for teacher

Original PDF: pages 2–3 pain points/users, 4–6 sensors/states/decision logic, 7–10 output/protocol/persistence/architecture, 11–13 failures/parameters/scope. Original DOCX: §1 pain points and 5 labels; §3–4 sensors/ROI/smoothing; §5–6 output and MQTT/RTSP; §7 data model; §8–9 offline and health; §10 ten failure cases and metrics; §11 adjustable parameters; §12 diagrams; §13 explicit Internet-loss recovery and idempotent sync.

**Teacher decisions needed:** (1) permitted pilot area/camera and recorded video; (2) real seat plan & verification of power/quiet/adjacency; (3) acceptable metrics and minimum true CV vertical slice; (4) whether to prototype hardware GPIO/LED next, and how to handle personal belongings ethically.
