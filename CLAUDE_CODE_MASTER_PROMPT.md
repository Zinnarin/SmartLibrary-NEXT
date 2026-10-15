# SMART LIBRARY NEXT V2 — CLAUDE CODE MASTER IMPLEMENTATION PROMPT

**Mission:** Build a truthful, locally runnable, impressively usable proof of concept for the **15 October 2026** 3-minute academic progress presentation. It must solve the real issue of students walking to seats that are reported free but are occupied, blocked by belongings, or based on stale data. Deliver a real student workflow, operator workflow, measurable system behavior, an editable PowerPoint, and reproducible demonstration evidence. **Do not stop at designing or writing plans.**

**Additional mandatory design reference:** `docs/UNIFIED_ENGINEERING_SPEC_V2.md` is the authoritative integrated specification and `verification/ACCEPTANCE_TEST_MATRIX.csv` is the run-by-run gate list. The original PDF/DOCX retain priority when describing what the group actually proposed. Use the synthesized specification for new behavior, and record any unresolved ambiguity rather than silently treating a proposal as a tested result.

**Read before implementing:**
1. `reference/Smart_Library.pdf` — 15-page ORIGINAL project slide proposal dated 1 October 2026.
2. `reference/Smart_Library_Seat_Proposal.docx` — 11-page ORIGINAL, fuller technical proposal dated 30 September 2026; includes 13 topics, decision tree, offline design, initial thresholds, edge sync and 10 failure cases.
3. `docs/MERGED_SCOPE_AND_RISKS_TH.md` — approved synthesis and priority order.
4. `docs/PROFESSOR_DEMO_CHECKLIST_TH.md` — mandatory demonstration storyline and honest progress reporting.

The files are **proposals, not evidence of implementation**. Do not claim the advisor reviewed them or that anyone collected real campus data. The DOCX's suggested interval 1–2 seconds, confidence threshold 0.5, smoothing 5 seconds, belongings flag after 30 minutes, heartbeat timeout 30 seconds, buffer 24–72 hours, retry 5 seconds to 5 minutes, UPS and MQTT are **proposed defaults**, not verified performance measurements or a requirement to install full hardware tonight.

## Positioning and honest differentiation

Project name remains **Smart Library NEXT — Find. Verify. Study.** The academic contribution should be:
- reliable per-seat computer-vision **evidence and uncertainty handling**, not simply binary occupancy;
- an **explainable recommendation** that never recommends unknown/stale or staff-closed seats;
- a **student feedback / staff verification loop** for when the world contradicts the model, without automatically punishing occupants;
- a small measured usability evaluation of whether people can find appropriate seats faster/more reliably.

Existing products already show busy floors and existing studies already detect seat occupancy. Do not claim worldwide novelty. Explain novelty as the useful integration and evaluation of safety-aware, feedback-corrected, seat-level navigation in this specific deployment.

## Scope: build in this order, preserve a usable app even if camera CV fails

### P0-A: MUST WORK before slides (local scenario demonstration, clearly SIMULATED)

1. **Student application:** Fast-loading responsive Thai interface with SVG floor map (illustrative floor, 3 zones, ~24 demo seats), zone/filter chips for seat type, power outlet, quiet zone, window, and seat details. Show timestamp, source mode, last valid observation, trust/health indicator, and the note that availability can change before arrival. No real location/floor claim unless a verified floor plan is supplied.
2. **Seat state engine:** Preserve 5 baseline domain labels from both original proposals: `Available`, `Occupied`, `Reserved` (user-facing: `มีสิ่งของ / อาจถูกจับจอง`, not a confirmed reservation), `Unavailable`, `Maintenance`. Add `Unknown` decision when reliable evidence is insufficient and a **freshness/health overlay** `STALE` when observations age out. Manual staff override always takes priority for physical status, while health remains visible as a separate dimension. Never paint an old `Available` observation green after TTL.
3. **StudyMatch:** Deterministic explainable matches and rankings from fresh eligible `Available` seats only. Hard constraints first; never generate bogus 99% availability odds or invent seat qualities. Show clear match reasons and graceful zero-results alternatives.
4. **SeatCheck — critical V2 addition:** One-click student action on a seat: `ที่นั่งจริงไม่ตรงกับระบบ` with simple reason (`reported occupied`, `belongings present`, `seat inaccessible`, `other`). Store event and timestamp (no personal photo/video uploads, no required account); show a subtle `มีรายงานที่ต้องตรวจสอบ` badge and de-prioritize / suppress that seat in HIGH-TRUST recommendations pending verification. **A single anonymous report must NOT silently overwrite the CV's factual status, apply a definitive booking status, or authorize removing possessions.** Add basic per-session/seat rate limiting. Staff must be able to accept/resolve/reject a report with a reason, update a temporary manual label if appropriate, and create an audit record.
5. **Librarian Console:** View seat states and health, incoming SeatCheck reports, manual `Unavailable` and `Maintenance` overrides, clear override, review status and timestamps. Modifications visible immediately on student screen via actual API + WebSocket. Demo gate only, never describe it as production-grade authentication.
6. **Scenario Lab:** At least `NORMAL`, `EXAM_RUSH`, `BELONGINGS`, `FALSE_FREE_REPORT`, `LOW_CONFIDENCE`, `CAMERA_LOST`, and `RECOVERED`. Must run from backend persisted state, not React-only effects. Always banner `SIMULATION — NOT REAL CAMERA DATA` whenever showing seeded/scenario data. Low confidence and camera lost never increase confirmed availability counts. Simulated feeds must not contaminate measured real-CV metrics.
7. **Local stack:** Windows-friendly Python/FastAPI + SQLite + WebSocket backend; React/TypeScript/Vite frontend. Use simple repo structure, local-only config, deterministic dataset, no cloud key, no compulsory Docker. Write one-command launch scripts or clear two-terminal commands. Use access controls for staff changes, even in demo. Handle reconnect/fallback refresh, empty states, and mobile layout. Do not expose `/api/demo/scenario` in production mode.

### P0-B: after P0-A, improve user impact

8. **GroupFit:** Find 2 adjacent `Available`, `fresh`, non-reported, non-overridden seats using a manually recorded physical adjacency graph (not a guess from SVG distance). Highlight both seats and explain why. If impossible, say so.
9. **Wayfinder:** Show static indoor route from a named demo entry point to selected seat using an authored waypoint graph + shortest path. Route is illustrative until geometry and accessibility paths are verified on site. Do not claim GPS, positioning sensors, real distances or accessible route certification without ground truth.
10. **SeatWatch (if time):** In-app-only alert for a confirmed newly available seat matching an opted-in filter; no OS notification/claim to reserve/hold a seat.

### P1: must make an attempt to prove a small true Computer Vision slice

Use a source **actually available and permitted to process**: an original controlled staged video / a user-provided authorized clip / webcam after explicit permission. If none exists, say **CV NOT VERIFIED**, preserve working P0, provide a 4–8-seat video ROI calibration guide. Never use live university CCTV without permission.

- OpenCV frame capture and actual Ultralytics pretrained model; inspect installed dependencies and supported model weights first rather than assuming any filename is valid. COCO detector includes `person`, `chair`, `laptop`, `book`, `backpack`, `handbag`; generic `bag` is NOT a literal COCO class. Record model name, environment, source, and inference result honestly. Existing original DOCX proposes fine-tuning; **do not claim fine-tuning took place** unless it really did.
- Define image-plane polygons distinctly for **seating/torso zone** and **tabletop belongings zone** for every test seat. Floor-map SVG coordinates are not video ROI coordinates. A person crossing a table ROI does not prove they are seated, a cup does not imply reserved, and belongings alone suggest potential occupancy rather than a legal reservation. If person-seat assignment cannot be distinguished, use `Unknown` instead of a false `Available`.
- Temporal state engine: observed repeatedly, valid frame quality, no occlusion, configurable initial thresholds from proposal only. `Available` requires consecutive high-quality negative evidence, not just one frame without detected people; must implement camera failure/blur/darkness handling. `Reserved` pending longer than timeout only raises staff review flag; NEVER auto-release belongings.
- Run at least ONE truthful inference through the pipeline if possible, collect a small evidence report and local screenshot (redact/not disclose people publicly). Raw frames are not stored by default. Any lab with frames is restricted to the demo machine and consented content.
- If CV is not runnable, log the actual error and build a swappable `ObservationSource` interface (`ScenarioObservationSource`, `YOLOObservationSource`) with visible source labels. Never mock YOLO detections while calling them actual inference.

### P2 / FUTURE (design but DO NOT consume deadline before evidence)

Proposed production camera PoE/RTSP, Raspberry Pi/Jetson edge inference, Mosquitto MQTT QoS 1 / TLS / LWT, SQLite store-forward buffer, cloud Postgres, offline LAN entrance display, LED GPIO, UPS, QR codes, prediction after enough genuine history, mic-based noise measurement only if truly consented and needed. Preserve this original plan as a **future architecture** slide, not a set of already running modules. Do not install cloud services or modify network/firewall without authorization. Offline on a local laptop is not proof of edge-first network failover. Physical seat allocation/true booking is outside initial scope.

## Data model and trust semantics (implement with migrations or simple repeatable schema)

- `Seat(seat_id, floor, zone, seat_type, has_power, near_window, quiet_zone, floor_x, floor_y, roi_id, is_active)`
- `SeatAdjacency(seat_a, seat_b)`; `Waypoint` + `WaypointEdge` for routing
- `SeatObservation(id, seat_id, observed_at_utc, source, raw_candidate, committed_state, detector_confidence_nullable, evidence_codes, frame_quality, model_version_nullable, observation_group_id)`
- `SeatCurrent(seat_id, physical_state, observed_at_utc, ingest_time_utc, source, is_stale, quality_flag, user_report_pending, manual_override_id_nullable)`
- `SeatReport(id, seat_id, reason, created_at_utc, pseudo_session_id, review_status, reviewed_at_utc, decision_reason, actor_id_nullable)`
- `ManualOverride(id, seat_id, state, reason, actor_id, created_at_utc, cleared_at_utc, expires_at_utc_nullable)`
- `SystemEvent(id, created_at_utc, category, detail, source)`

Precise semantics:
- Keep **physical status**, **source of evidence**, **freshness**, **camera health**, **pending user report**, and **staff override** as separate fields; do not conflate camera failure with a chair being genuinely unoccupied.
- Timestamp data in UTC, render local Thai time; use `observed_at` (not request arrival time) for staleness; clock skew must not produce negative elapsed times.
- Staff override `Maintenance`/`Unavailable` wins for display even if camera disconnected; still show sensor as offline. Staff may optionally mark temporarily unknown pending inspection, with reason and expiration.
- Ranking excludes unknown/stale/maintenance and excludes or visibly penalizes pending mismatch reports. If no trustworthy seats, show honest "ไม่มีที่นั่งที่ยืนยันได้ตอนนี้" rather than green placeholders.
- Store reports without student identity by default. No face recognition, identity linkage, long-term per-user tracking, video upload or automated accusations about "seat hogging".

## Minimal HTTP/WS contract

- `GET /api/health` server, active source, camera last-seen, readiness, data freshness.
- `GET /api/seats`, `GET /api/seats/{id}`, `GET /api/zones` return status + trust + attributes.
- `GET /api/recommendations?quiet=true&power=true&group_size=1` returns valid seat(s) + plain-language explanation; group endpoint may be separate.
- `POST /api/seat-reports` accepts validated seat ID and bounded reason; replay/rate-limit protection; `GET /api/admin/seat-reports` + `POST /api/admin/seat-reports/{id}/resolve` staff only.
- `POST /api/admin/seats/{id}/override`, `DELETE /api/admin/seats/{id}/override`, `GET /api/admin/events` audited and guarded.
- `POST /api/demo/scenario` local development/demo ONLY.
- `WS /ws/seats` deltas for status, health and report flags; browser reconnect with polling fallback.
- `GET /api/stats` separate scenario statistics from any actual inference/human-labelled evaluation.

## Automated tests and objective acceptance gates

1. After `CAMERA_LOST` + freshness TTL, a previously free seat stops being ranked/recommended; visible `Stale` with last timestamp.
2. Staff `Maintenance` override wins against new CV and camera loss, and is recoverable and audited.
3. `person walking past seat` is not automatically `Occupied` solely from a box overlap; ambiguous becomes `Unknown`.
4. `bag/laptop persistently in assigned belongings zone` without person => `มีสิ่งของ / อาจถูกจับจอง` not definitive booking.
5. `cup only` => NOT `Reserved`; one clean detection absence => NOT immediately `Available`.
6. `LOW_CONFIDENCE` => unknown / non-recommendable, never silently green.
7. SeatCheck report creates staff review ticket; screen indicates pending report; recommendation responds; unreviewed anonymous reports do not silently set occupancy to `Occupied` or `Unavailable`; rate-limit works.
8. Staff resolves report with reason and audit event; report state surfaces in student UI after WebSocket event.
9. StudyMatch never recommends stale/unknown/overridden/pending high-risk seat; no-result explanation is truthful.
10. GroupFit pair must be physically adjacent in seat graph and eligible; route path must consist of real graph edges.
11. Scenario state changes go through backend and WS, not a frontend fake; label `SIMULATION` remains visible.
12. App still functions without model/camera; if model fails startup, error is explicit and no fake inference results appear.
13. Any metrics slide says dataset size, simulated vs actual, measurement conditions, and NEVER invents accuracy.

Report command outputs, failure counts, screenshots and limitations, not just green words. If browser testing is possible, run Playwright smoke path: open map → filter quiet/power → report mismatch on recommended seat → staff review and mark maintenance → student view updates → simulate camera disconnect → UI refuses stale seats.

## Genuine research and usability evaluation plan

The research objective is not just object-detection mAP. Track **False Available** on a hand-labelled controlled test set (false green rate), a seat-level confusion matrix with Unknown coverage, latency event→UI, stale failover, and availability of correct recommendations. Run a small *future* task-time comparison using a conventional floor map versus StudyMatch (e.g. quiet + power + 2 adjacent), count task success and misleading seat recommendations. Never present these as completed tests without participants and results. Candidate acceptance thresholds must be labelled hypotheses, not achieved scores; prefer improving **False Available** over maximizing green seat count.

If claiming 100% freshness, zero data loss, exact shortest distance, PDPA compliance, or performance on Pi 5, require direct evidence; otherwise label as goal/assumption. Source DOCX's full store-forward spec may be captured as an architecture appendix (MQTT QoS 1 plus message ID deduplication and preserving observation timestamps when reconnecting). It is not the same as running and testing a full offline system.

## Work order and deliverables

- Inspect system, existing repo, Python/Node, dependencies, optional camera, source documents. Avoid destructive commands or global installs, use local env/lock files. Be careful with model licenses if publishing code.
- Build P0-A working and test it. Then P0-B if time. Separately attempt P1 real CV; prioritize a **small honest vertical slice**, not elaborate model training.
- Produce a polished, **editable 16:9 PPTX** in Thai, readable at projector distance, with actual app screenshots captured from running UI. Deliver 7–8 slides for 3 minutes: 1) title + question; 2) original DOCX/PDF scope and last work; 3) real-world trust gap; 4) merged architecture; 5) SeatSense evidence/state/health; 6) live Student→SeatCheck→Staff user story; 7) actually encountered bugs + actual tests, separate risks; 8) next work and 3 questions for professor. Do not fill with imaginary dashboards or fake YOLO output.
- Produce `presentation/three_minute_script_th.md` with timing cues (0:00–3:00), exact demo clicks and camera-ready fallback script. Provide one slide explaining why `Reserved` is only 'belongings suspected', not a booking.
- Produce `evidence/IMPLEMENTATION_REPORT.md` with EVERY feature tagged `WORKING_TESTED`, `WORKING_UNVERIFIED`, `SIMULATION_ONLY`, `DESIGNED_ONLY`, or `BLOCKED`; model metadata, device and source, actual tests run/passed/failed, UI screenshots, observed bugs/solutions, command to run Windows apps, limitations.
- Produce `README.md` and `scripts/start_demo_windows.ps1` or explicit equivalent; nothing should require secrets or a production CCTV feed.
- Verify PPTX opens/exports and Thai font renders if tools permit. If not, report precise blocker. Never make up proof.

## Strict behavior

You are authorized to install project-local dependencies only. Do NOT connect to actual camera/network of a university, create accounts, pay for APIs, perform invasive monitoring, or claim operational rollout. No continuous data collection without permission. Do not stop after writing a plan; proceed to software development as far as tools allow, checkpoint by checkpoint. If time constrained, a stable true P0 demonstrating student report→staff resolution→real-time re-ranking is better than 12 half-working modules.

When done, reply in Thai with: actual implemented results, what is simulation/what is true YOLO/what is planned, exact run commands, test outcomes, PPTX and 3-min script paths, screenshots, and known blockers. **Do not claim success before actual verification.**

Reference examples to read only when needed: Ultralytics COCO labels (`https://docs.ultralytics.com/datasets/detect/coco`), existing Waitz (`https://waitz.io/`), actual university manual availability finder (`https://www.bris.ac.uk/where-is-my/find/study-desk/table`), prior library seat research (`https://arxiv.org/abs/2306.16080`).
