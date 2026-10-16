# P2 · 05 — Integration contract (Backend & Database)

**Your role:** you **provide every interface**: C1 ingest, the C1b engine library, C1c run-record passthrough, C2, C3 and C4. You own the authoritative contract document `docs/api_contract_v3.md` (planned).

## Your obligations

1. **Backward compatibility.** Existing routes, fields, types, enum values and their meaning keep working. New things are optional.
2. **Contract first.** Any change visible to another module updates `docs/api_contract_v3.md` and `docs/team_v3/individual_handoff/SHARED_V3/contract_examples/` in the same PR, with tests. YELLOW or RED changes also need an approved CR first.
3. **Keep C1b importable.** `EngineConfig`, `Detection.from_dict/to_dict`, `classify`, `SeatEngineState`, `step` keep their names and signatures, because `cv/run_cv.py` imports them.
4. **Safety rules are part of the contract.**
   - A seat is recommendable only when `not_recommendable_reasons` is empty.
   - A report never changes `physical_state`.
   - An override wins.
   - A gap longer than the TTL resets the seat to `unknown`.
   - Out-of-order and duplicate observations never change state.
   - `scenario` and `cv` sources never mix.
5. **Error shapes stay stable.** `{"error", "message_th"}` for service errors; FastAPI `detail[]` for validation. Add new codes; never rename old ones.
6. **Response time.** Keep mutations followed by `hub.trigger()` so clients see changes immediately. The e2e criterion is about 5 s; V2 measured a 43.5 ms median for WS on loopback.

<!-- SYNC:BEGIN SHARED_V3/03_SHARED_API_CONTRACTS.md#C0 -->
> _Synced from `SHARED_V3/03_SHARED_API_CONTRACTS.md` section `C0` — edit there, then run `scripts/build_handoff_packages.py --sync`._

## C0 — Common definitions (apply to every interface)

**Transport.** One local process serves REST, the built web app and the WebSocket on `http://127.0.0.1:8000` (`scripts/start_demo_windows.ps1`). The web app calls relative paths (`/api/...`, `/ws/seats`), so there is no CORS and no base-URL setting.

**Time.** Every timestamp is UTC ISO-8601 with milliseconds and `Z`, produced by `iso()` in `services/api/app/engine/timeutil.py`, for example `"2026-10-16T07:18:28.621Z"`. Input is parsed by `parse_iso()`, which accepts `Z` or an offset; naive times are treated as UTC. Ages (`age_s`, `state_for_s`, `belongings_for_s`) are seconds, clamped at 0. Clients should compute ages from `server_time_utc`, not from the browser clock (`live.tsx` does this).

**Seat identifiers (verified seed data, `services/api/app/seed.py`).**

| Seat IDs | Zone | Camera / device | `source_mode` | On student map? | Data shown today |
|---|---|---|---|---|---|
| `A01`–`A08` | `A` quiet | `CAM-A` | `scenario` | yes (`is_active=1`) | **SIMULATION** |
| `B01`–`B08` | `B` group | `CAM-B` | `scenario` | yes | **SIMULATION** |
| `C01`–`C08` | `C` window | `CAM-C` | `scenario` | yes | **SIMULATION** |
| `LAB1`–`LAB4` | `LAB` (not public) | `CV-LAB` | `cv` | **no** (`is_active=0`) — only `GET /api/cv/lab-seats` | real YOLO output when a CV run posts |

- `POST /api/seat-reports` enforces the ID pattern `^[A-Z]{1,3}\d{1,3}$`. Other endpoints look the ID up in the `seats` table.
- Floor coordinates (`floor_x`, `floor_y`) are SVG map units in a `0 0 1000 680` view box. They are **not** metres and **not** camera pixels.
- Seat metadata (`has_power`, `quiet_zone`, `near_window`, adjacency) is `metadata_source = "demo_assumed"`, which means **illustrative, not a real library plan**.

**Source identity.** The `source` field of a seat is `"scenario"` (SIMULATION), `"cv"` (real detector output via ingest) or `null` (never observed). Both a seat's camera (`devices.source_mode`) and the ingest call must agree on the source. Otherwise the request is rejected (`NOT_A_CV_DEVICE`, `SOURCE_MISMATCH`, `CAMERA_MISMATCH`), so simulated and real data cannot mix. There is no string `"simulation"`: the value is `"scenario"`, and UIs must label it SIMULATION.

**State vocabulary (`services/api/app/engine/evidence.py`, `trust.py`).**

| Field | Values | Meaning |
|---|---|---|
| `physical_state` (engine output) | `available`, `occupied`, `reserved`, `unknown` | `reserved` means **belongings suspected**. It is not a booking and is never auto-released. |
| `manual_override.state` (staff) | `unavailable`, `maintenance`, `unknown` | Wins over any detector or scenario evidence. |
| `display_state` | override state if one is active, else `physical_state` | What to show. |
| `display_tone` | `display_state` values, or `stale` | `stale` when the observation is older than the TTL or the camera is offline (and no override is active). |
| Thai labels | `physical_state_label_th`, `display_state_label_th` | From `STATE_LABEL_TH` (e.g. `reserved` = "พบสิ่งของ / อาจถูกจับจอง"). |

**Frame quality** (`FRAME_QUALITIES`): `ok`, `dark`, `bright`, `blur`, `occluded`, `no_frame`, `uncalibrated`, `clock_skew`. Anything other than `ok` makes the frame's candidate `unknown`.

**Evidence codes** (per frame, from `classify()`):
- `P_SEATED`, `P_NEAR_NOT_SEATED`, `P_LOW_CONF`
- `B_<CLASS>` (e.g. `B_BACKPACK`), `B_LOW_CONF`
- `E_EMPTY_VISIBLE`
- `IGNORED_<CLASS>` (e.g. `IGNORED_CUP`)
- `Q_<QUALITY>` (e.g. `Q_DARK`)

**Not-recommendable reason codes:**
- From the server (`trust.py`): `STAFF_OVERRIDE`, `NO_OBSERVATION`, `STATE_OCCUPIED`, `STATE_RESERVED`, `STATE_UNKNOWN`, `STALE`, `CAMERA_OFFLINE`, `CAMERA_DEGRADED`, `EVIDENCE_CHANGING`, `PENDING_REPORT`. A seat is recommendable **only** if the list is empty.
- Added by the browser (`live.tsx`): `STALE` and `LINK_DOWN`, when the browser's own TTL check fails or the server has been silent for more than 10 s.

**Freshness and health parameters** (`services/api/app/engine/config.py`). Every value can be set through an `SL_*` environment variable. They are proposal defaults, **not validated measurements**.

| Parameter | Default | Env |
|---|---|---|
| freshness TTL (stale after) | 30 s | `SL_FRESHNESS_TTL_S` |
| camera heartbeat timeout (offline after) | 30 s | `SL_HEARTBEAT_TIMEOUT_S` |
| clock-skew tolerance | 5 s | `SL_CLOCK_SKEW_TOLERANCE_S` |
| detection confidence threshold / ignore floor | 0.5 / 0.25 | `SL_CONF_THRESHOLD` / `SL_LOW_CONF_THRESHOLD` |
| smoothing span | 5 s | `SL_SMOOTHING_S` |
| consecutive frames to commit `occupied` / `reserved` / `available` / `unknown` | 3 / 3 / 4 / 2 | `SL_MIN_FRAMES_*` |
| person-box overlap with seat polygon for "seated" | 0.30 | `SL_MIN_SEAT_OVERLAP` |
| belongings staff-review flag after | 1800 s | `SL_BELONGINGS_REVIEW_AFTER_S` |
| simulated capture tick (demo mode) | 2 s | `SL_TICK_S` |

- The current values are visible at runtime in `GET /api/health` → `engine_config`.
- Seat staleness: `is_stale = (never observed) OR (age_s > TTL)`.
- `camera_health` is `healthy`, `degraded`, `offline` or `unknown` (no device row). Device views use `never_seen` for a device that has never reported.

**Authentication headers.** Values are deliberately not written in any handoff document; they are in `services/api/app/settings.py` and the onboarding guide.

| Header | Used by | How it is obtained |
|---|---|---|
| `X-Session-Token` | student SeatCheck (C4) | `GET /api/session` gives an anonymous, HMAC-signed token valid for 8 h, format `<sid>.<exp_unix>.<sig>` |
| `X-Staff-Token` | staff + Scenario Lab (C3) | demo gate (env `SL_STAFF_TOKEN`). **Not real authentication**: every staff action is audited as actor `"staff-demo"` |
| `X-Device-Token` | CV ingest (C1) | env `SL_DEVICE_TOKEN` |

**Modes.** `SL_MODE=demo` (default) enables `/api/demo/*`, the Scenario Lab and the scenario ticker that emits SIMULATION frames every `SL_TICK_S`. `SL_MODE=production` disables them (`404 {"error":"Not Found"}`), and seats then change only through CV ingest or staff overrides.

**Error shapes.** Clients must handle both. `apps/web/src/api.ts` already reads `message_th`, then `detail[0].msg`, then `error`.
1. Service or HTTP errors: `{"error": "<CODE>", "message_th": "<Thai text>"}`. `DEVICE_AUTH_REQUIRED` and `BAD_FRAME_QUALITY` return only `{"error": "<CODE>"}`.
2. Pydantic validation (HTTP 422): `{"detail": [{"type", "loc", "msg", "input", "ctx"?}]}`, e.g. `contract_examples/C4__report_bad_seat_pattern_422.json`.

| HTTP | `error` codes (where) |
|---|---|
| 401 | `SESSION_REQUIRED`, `SESSION_INVALID` (C4) · `STAFF_AUTH_REQUIRED` (C3) · `DEVICE_AUTH_REQUIRED` (C1) |
| 404 | `SEAT_NOT_FOUND` · `NO_ROUTE` · `REPORT_NOT_FOUND` · `NO_ACTIVE_OVERRIDE` · `Not Found` (demo routes in production mode) |
| 409 | `REPLAY_CONFLICT` (C4) · `ALREADY_RESOLVED` (C3) |
| 422 | `BAD_REASON` · `BAD_DECISION` · `REASON_REQUIRED` · `OVERRIDE_REQUIRES_ACCEPT` · `BAD_OVERRIDE_STATE` · `BAD_EXPIRY` · `GROUP_SIZE_NOT_SUPPORTED` · `BAD_SEAT_TYPE` · `BAD_FRAME_QUALITY` · `NOT_A_CV_DEVICE` · `CAMERA_MISMATCH` · `SOURCE_MISMATCH` · `UNKNOWN_SCENARIO` · `UNKNOWN_CAMERA` · Pydantic `detail[]` |
| 429 | `DUPLICATE_SEAT_REPORT`, `RATE_LIMITED` (C4) |
| 500 | **Known defect:** a malformed `observed_at_utc` on ingest raises an unhandled `ValueError` (verified, `contract_examples/C1__ingest_malformed_timestamp.json`). See **PA-02**. |
<!-- SYNC:END -->

<!-- SYNC:BEGIN SHARED_V3/03_SHARED_API_CONTRACTS.md#C1 -->
> _Synced from `SHARED_V3/03_SHARED_API_CONTRACTS.md` section `C1` — edit there, then run `scripts/build_handoff_packages.py --sync`._

## C1 — P1 → P2: CV evidence to backend

**Endpoint:** `POST /api/ingest/observations` with header `X-Device-Token`. Handler: `ingest()` in `services/api/app/main.py`. Per-seat logic: `ingest_observation()` in `services/api/app/services.py`.

**One request = one frame from one camera.** Each seat in the frame becomes one observation. CV sends **evidence, not final truth**: the backend's `classify()` + `SeatStateEngine` decide the state. CV must never write the database directly and never send a "final state".

### Request body (Pydantic models `IngestIn`, `SeatObsIn`, `DetectionIn`)

| Field | Type | Constraint (enforced) | Meaning |
|---|---|---|---|
| `camera_id` | string | must exist in `devices` with `source_mode="cv"` → else 422 `NOT_A_CV_DEVICE` | today only `CV-LAB` |
| `frame_id` | string | ≤ 80 chars | stored as `observation_group_id`; counted as "frames" in `/api/stats` |
| `observed_at_utc` | string | ISO-8601 UTC (see C0). Malformed → **500 (defect, PA-02)** | capture time of the frame |
| `frame_quality` | string | one of the 8 `FRAME_QUALITIES` → else 422 `BAD_FRAME_QUALITY` | CV's own image-quality verdict |
| `model_version` | string \| null | ≤ 120 chars | free text; shown in `/api/stats` → `real_cv.model_versions` and the device detail |
| `seats` | array of `SeatObsIn` | may be empty (code-read: still marks the device seen) | |
| `seats[].seat_id` | string | must exist (404 `SEAT_NOT_FOUND`) and belong to `camera_id` (422 `CAMERA_MISMATCH`) | today `LAB1`–`LAB4` for `CV-LAB` |
| `seats[].event_id` | string | 6–80 chars, **globally unique** across all seats and runs (DB `UNIQUE`) | `cv/run_cv.py` uses `<frame_id>-<seat_id>` |
| `seats[].detections` | array of `DetectionIn` | default `[]` | detections **already related to this seat's ROI** |
| `detections[].cls` | string | ≤ 40 chars | COCO class name (see below) |
| `detections[].conf` | number | 0–1 | detector confidence |
| `detections[].in_seat` / `in_table` | bool | default false | anchor point inside the seat / table polygon (person anchor = hip point 65 % down the box, objects = box centre — `cv/roi.py::anchor_point`) |
| `detections[].seat_overlap` / `table_overlap` | number | 0–1, default 0 | fraction of the box area inside the polygon |
| `detections[].bbox` | number[] \| null | optional | image-plane pixels `[x1, y1, x2, y2]` |

**Classes the backend understands** (`services/api/app/engine/config.py`):
- `person`.
- Belongings: `backpack`, `handbag`, `suitcase`, `laptop`, `book`.
- Ignored items, logged as `IGNORED_*` only: `cup`, `bottle`, `wine glass`, `cell phone`, `chair`, `dining table`, `couch`.
- Any other class has no effect.

Detections below 0.25 are discarded. Those between 0.25 and 0.5 produce `unknown`.

**Decision order** (`classify()`, `services/api/app/engine/evidence.py`):
1. `frame_quality != ok` → `unknown`.
2. A person with conf ≥ 0.5, `in_seat` and `seat_overlap ≥ 0.30` → `occupied`.
3. A person near the seat but not seated, or a low-confidence person → `unknown`.
4. Belongings in the seat or table zone → `reserved`.
5. Low-confidence belongings → `unknown`.
6. Otherwise → `available`.

The engine then needs the consecutive frames and smoothing span from C0 before it commits a change.

### Response `200`

```json
{"results": [{"status": "applied", "seat_id": "LAB1", "raw_candidate": "occupied", "committed_state": "unknown",
              "committed_changed": false, "reason": "PENDING_OCCUPIED_1/3"}]}
```

The example above is real; the full recording is `contract_examples/C1__ingest_applied.json`.

| `status` | When | Stored? | Changes state? |
|---|---|---|---|
| `applied` | new `event_id`, newer than the seat's last applied observation | yes | when the smoothing requirement is met (`committed_changed`) |
| `late` | `observed_at_utc` not newer than the last applied observation of that seat (`reason: OUT_OF_ORDER_OR_DUPLICATE`) | yes (`applied=0`) | never |
| `duplicate` | `event_id` already stored (`reason: DUPLICATE_EVENT_ID`) | no | never |

- `reason` values: `CONFIRMED_SAME`, `COMMIT_<STATE>`, `PENDING_<STATE>_<n>/<needed>`, `GAP_RESET;<…>` (a gap larger than the TTL resets the seat to `unknown`, BUG-001), `OUT_OF_ORDER_OR_DUPLICATE`, `DUPLICATE_EVENT_ID`.
- Future timestamps more than 5 s ahead of the server are treated as `clock_skew`: the candidate is `unknown` and the effective time is server now (`contract_examples/C1__ingest_future_clock_skew.json`).
- A `200` can still contain `duplicate` or `late` results. **The sender must check every `results[].status`.**

### Errors (all verified, see `contract_examples/C1__*.json`)

- `401 DEVICE_AUTH_REQUIRED` — missing or wrong token.
- `422 BAD_FRAME_QUALITY`.
- `422 NOT_A_CV_DEVICE` — e.g. `CAM-A`.
- `422 CAMERA_MISMATCH` — seat not on this camera.
- `404 SEAT_NOT_FOUND`.
- `422` Pydantic `detail[]` — a missing or invalid field.
- `500` — malformed timestamp (defect).
- **A single bad seat rejects the whole frame.** The transaction rolls back; verified that `LAB4` stored nothing when the same frame also contained `A01`.

### C1b — Shared engine library (P1 imports P2 code)

`cv/run_cv.py` imports P2's pure-Python engine so that offline CV runs use the same logic as the server:
- `EngineConfig()`
- `Detection.from_dict(d)` / `Detection.to_dict()`
- `classify(detections, frame_quality, cfg) -> Candidate(state, confidence, codes)`
- `SeatEngineState()`
- `step(state, candidate, observed_at: datetime, cfg) -> (SeatEngineState, StepResult)`

These come from `services/api/app/engine/{config,evidence,state_engine}.py`. **P2 keeps these names and signatures importable.** Changing them is a YELLOW change that needs P1's review. **P1 must not edit them.**

### C1c — CV run record shown on the CV Lab page

- `GET /api/cv/status` returns the JSON in `<settings.cv_evidence_dir>/latest_run.json`, or `{"status": "NOT_RUN", "message_th": …}` when the file is missing.
- The default directory is `evidence/cv`, which is **FROZEN V2 evidence**. `AppSettings.from_env()` does **not** read a variable for it yet: see PA-01 and issue #3.
- `apps/web/src/pages/CvLab.tsx` reads these keys: `status` (`WORKING_TESTED` \| `BLOCKED` \| `NOT_RUN`), `scope`, `headline_th`, `library_cv_status`, `library_cv_blocker`, `not_claimed_th[]`, `run_at_utc`, `model`, `environment`, `source`, `rois[]`, `inference`, `ingest`, `robustness_checks[]`, `annotated_image`, `errors[]`, `message_th`.
- `GET /api/cv/annotated/{name}` serves `<dir>/<name>`, but only names ending in `.jpg` with no path separators.
- `GET /api/cv/lab-seats` returns `{server_time_utc, seats: [SeatView of LAB1–LAB4]}`.

### Sender obligations (P1)

- Use a clock synchronised by NTP, and send frames in capture order.
- For any seat to commit within the 30 s TTL, send at least one frame every few seconds. `available` needs ≥ 4 consecutive clean frames spanning ≥ 5 s.
- Never reuse an `event_id`.
- Only send seats that the backend has registered for that camera.
- Report `frame_quality` honestly. A frame you cannot see is not `ok`.
<!-- SYNC:END -->

<!-- SYNC:BEGIN SHARED_V3/03_SHARED_API_CONTRACTS.md#C2 -->
> _Synced from `SHARED_V3/03_SHARED_API_CONTRACTS.md` section `C2` — edit there, then run `scripts/build_handoff_packages.py --sync`._

## C2 — P2 → P3: Backend to student website

All student data goes through `apps/web/src/api.ts` (`api()` helper) and `apps/web/src/live.tsx` (`LiveProvider`/`useLive`).

| Endpoint | Used by (today) | Response (top-level keys) |
|---|---|---|
| `GET /api/seats` | `live.tsx` polling fallback | `server_time_utc`, `seats[]` (SeatView, active seats only), `meta` |
| `WS /ws/seats` | `live.tsx` | `snapshot` / `delta` / `heartbeat` / `pong` (below) |
| `GET /api/seats/{seat_id}` | (not used by the UI yet) | `server_time_utc`, `seat`, `recent_observations[≤8]` (`observed_at_utc`, `raw_candidate`, `committed_state`, `evidence_codes[]`, `frame_quality`, `source`, `applied` 0/1). LAB seats return 404 |
| `GET /api/recommendations` | `StudentPage.tsx` (StudyMatch / GroupFit) | see below |
| `GET /api/route?to=<seat>&from=<waypoint>` | `StudentPage.tsx` (Wayfinder) | `from`, `to`, `waypoints[]`, `points[{id,label_th,x,y}]`, `edges[[a,b]]`, `total_cost_units`, `disclaimer_th` · 404 `NO_ROUTE` |
| `GET /api/layout` | (not used; FloorMap zones are hard-coded) | `zones[]`, `waypoints[]`, `edges[]`, `adjacency[]`, `seat_types_th`, `note_th` |
| `GET /api/zones` | (not used) | `server_time_utc`, `zones[]` (+ `seat_count`, `recommendable`, `counts`) |
| `GET /api/health`, `GET /api/stats` | `ScenarioLab.tsx` (stats) | readiness, freshness, engine config / simulation and real-CV counters (`real_cv.accuracy` is always `null`) |
| `GET /api/cv/status`, `GET /api/cv/lab-seats` | `CvLab.tsx` | see C1c |

### SeatView (one seat; built by `build_seat_view()` in `services/api/app/engine/trust.py`)

| Field | Type | Notes |
|---|---|---|
| `seat_id`, `floor`, `zone_id`, `seat_type`, `camera_id`, `metadata_source` | string | `seat_type` ∈ `single_desk`, `computer_desk`, `group_table`, `sofa` (`lab_roi` for LAB seats) |
| `has_power`, `near_window`, `quiet_zone` | bool | demo metadata |
| `floor_x`, `floor_y` | number | map units |
| `physical_state`, `physical_state_label_th`, `display_state`, `display_state_label_th`, `display_tone` | string | see C0 |
| `source` | `"scenario"` \| `"cv"` \| null | |
| `observed_at_utc`, `ingested_at_utc`, `state_since_utc`, `last_confident_at_utc` | string \| null | |
| `age_s`, `state_for_s`, `belongings_for_s` | number \| null | **volatile**: excluded from WS change detection, so compute them on the client |
| `is_stale`, `transition_pending`, `belongings_review_flag`, `pending_discrepancy`, `is_recommendable` | bool | |
| `camera_health`, `quality_flag`, `latest_candidate`, `last_confident_state` | string \| null | |
| `evidence_codes`, `not_recommendable_reasons`, `not_recommendable_reasons_th` | string[] | |
| `pending_report_count`, `revision` | int | |
| `manual_override` | object \| null | `{id, state, reason, actor_id, created_at_utc, expires_at_utc, report_id}` |

Real full example: `contract_examples/C2__seat_view_A07_full.json`. The TypeScript `Seat` interface in `api.ts` declares a subset; it omits `floor`, `age_s`, `state_for_s` and `belongings_for_s`.

**`meta`:**
- `mode`, `simulation_active`, `simulation_banner` (string \| null).
- `scenario` (`{run_id, name, base, started_at_utc, cameras{CAM-x: online|degraded|lost}, description_th}` \| null).
- `cameras[{camera_id, label_th, zone_id, source_mode, status}]`.
- `pending_reports`, `counts{state|stale: n}`, `recommendable`, `total_seats`.
- `recent_resolved_reports[≤20 PublicReport]`, `freshness_ttl_s`.

### Recommendations

`GET /api/recommendations` query parameters:
- `quiet`, `power` (bool).
- `window` = `must` \| `prefer`.
- `seat_type`; an unknown value → 422 `BAD_SEAT_TYPE`.
- `zone`.
- `group_size` 1–8, but only 1 or 2 are supported (3–8 → 422 `GROUP_SIZE_NOT_SUPPORTED`).
- `limit` 1–24.

The response contains:
- `mode` (`single` \| `group`), `filters`, `hard_constraint_rules_th[]`, `score_note_th`, `matching_candidates`.
- `excluded[{reason, text_th, seats[]}]`, `availability_note_th`, `server_time_utc`.
- `source_note_th` (string \| null; set when SIMULATION data is used).
- Single mode: `results[{seat_id, zone_id, seat_type, seat_type_th, rank_score, walk_units, reasons[{kind: must|trust|prefer|group, text_th}], observed_at_utc}]`.
- Group mode: `group_results[{seats[2], relation, note_th, rank_score, walk_units, reasons[]}]` and `adjacency_source_th`.
- When empty: `empty_message_th`, `relax_suggestions[{filter, label_th, would_match, text_th}]`.
- Only seats with `is_recommendable = true` can appear.
- `rank_score` only orders the results. It is **not a probability** and must never be shown as a percentage.

### WebSocket `/ws/seats` (`services/api/app/realtime.py`)

| Direction | Message | When |
|---|---|---|
| server → client | `{"type": "snapshot", "server_time_utc", "seats": [all active SeatViews], "meta"}` | once, on connect |
| server → client | `{"type": "delta", "server_time_utc", "seats": [changed SeatViews only, full objects], "meta": meta or null}` | after any mutation (immediately) or on the ≤ 1 s sweep when a seat or meta hash changed |
| server → client | `{"type": "heartbeat", "server_time_utc"}` | nothing changed for > 5 s |
| client → server | text `ping` | optional |
| server → client | `{"type": "pong", "server_time_utc"}` | reply to `ping` |

Client duties, as implemented in `live.tsx` (BUG-011 regression must keep passing):
- On close, poll `GET /api/seats` every 3 s.
- Reconnect with backoff from 1 s up to 15 s.
- Treat more than 10 s with no message as link down. Then mark every seat stale and not recommendable (`LINK_DOWN`) and re-apply the TTL in the browser.

### Display rules (MUST, from the V2 safety design)

1. A seat with `is_recommendable = false` must never be presented as a confirmed free seat. This covers `unknown`, `stale`, `camera_health` offline/degraded, a pending report, an override, and `transition_pending`.
2. `source = "scenario"` or `meta.simulation_active` must be visibly labelled **SIMULATION**. Only `source = "cv"` may be called camera/CV data, and today it exists only for LAB seats.
3. No accuracy percentages, and no "probability free" language.
4. Wayfinder distances are map units, not metres. `disclaimer_th` must stay visible.
<!-- SYNC:END -->

<!-- SYNC:BEGIN SHARED_V3/03_SHARED_API_CONTRACTS.md#C3 -->
> _Synced from `SHARED_V3/03_SHARED_API_CONTRACTS.md` section `C3` — edit there, then run `scripts/build_handoff_packages.py --sync`._

## C3 — P2 ↔ P4: Backend and staff operations

Every endpoint needs `X-Staff-Token`; otherwise it returns `401 STAFF_AUTH_REQUIRED`, and the failure is logged as a `security` event. The Staff Console is `apps/web/src/pages/StaffConsole.tsx` and the Scenario Lab is `apps/web/src/pages/ScenarioLab.tsx`.

| Endpoint | Body / query | Success response |
|---|---|---|
| `GET /api/admin/check` | — | `{ok: true, actor: "staff-demo", note_th}` |
| `GET /api/admin/seat-reports?status=` | `pending` (default) \| `accepted` \| `rejected` \| `all` (last 200) | `{reports: [StaffReport]}` |
| `POST /api/admin/seat-reports/{id}/resolve` | `{decision: "accepted"\|"rejected", reason: 3–300 chars, override_state?: "unavailable"\|"maintenance"\|"unknown", override_minutes?: 1–10080}` | the updated StaffReport |
| `POST /api/admin/seats/{seat_id}/override` | `{state, reason: 3–300, expires_in_minutes?: 1–10080 or null = no expiry}` | Override row |
| `DELETE /api/admin/seats/{seat_id}/override?reason=` | — | the cleared Override row · 404 `NO_ACTIVE_OVERRIDE` |
| `GET /api/admin/events?limit=1..500&category=` | | `{events: [{id, created_at_utc, category, detail, source, seat_id, actor_id, payload}]}` |
| `GET /api/admin/devices` | | `{devices: [{camera_id, label_th, zone_id, source_mode, reported_status, last_seen_utc, last_quality, detail, updated_at_utc, status, last_seen_age_s}]}` |
| `GET /api/demo/scenarios` (demo mode, no token) | | `{scenarios[{name, description_th}], cameras[], active, history[], banner}` |
| `POST /api/demo/scenario` (demo mode + token) | `{scenario: NORMAL\|EXAM_RUSH\|BELONGINGS\|FALSE_FREE_REPORT\|LOW_CONFIDENCE\|CAMERA_LOST\|RECOVERED, camera_id?: CAM-A\|CAM-B\|CAM-C\|ALL}` | `{run_id, scenario, base_scenario, cameras, params, banner}` |
| `POST /api/demo/reset` (demo mode + token) | — | `{ok: true, message_th}`; re-seeds the demo DB |

- **StaffReport** (full row): `id`, `seat_id`, `reason`, `reason_th`, `created_at_utc`, `pseudo_session_id`, `client_report_id`, `review_status`, `reviewed_at_utc`, `decision_reason`, `actor_id`, `is_simulated`, `display_state_at_report`, `override_id`.
- **Override** row: `id`, `seat_id`, `state`, `reason`, `actor_id`, `created_at_utc`, `cleared_at_utc`, `cleared_by`, `expires_at_utc`, `report_id`.
- **Event categories** in the code: `system`, `scenario`, `state`, `report`, `report_resolved` (payload has `resolution_latency_s`), `override`, `security`.

Semantics (verified by tests `test_T07_*`, `test_T09_*`, `test_override_expiry`, `test_staff_unknown_override_pending_inspection`):
- One active override per seat; a new one supersedes the old.
- Expired overrides are ignored at read time and cleared by the ticker.
- An override wins over scenario and CV evidence.
- An override in `resolve` requires `decision = "accepted"` (`OVERRIDE_REQUIRES_ACCEPT`).
- Resolving twice returns `409 ALREADY_RESOLVED`.
- **A report never changes `physical_state` by itself.**
- **Team agreement:** after confirming a report that someone is sitting, use override `unknown` (pending inspection), not `maintenance`. The V2 console still defaults to `maintenance` (`StaffConsole.tsx`, `ReportCard`), which is issue #11 (P4). No API change is needed.
<!-- SYNC:END -->

<!-- SYNC:BEGIN SHARED_V3/03_SHARED_API_CONTRACTS.md#C4 -->
> _Synced from `SHARED_V3/03_SHARED_API_CONTRACTS.md` section `C4` — edit there, then run `scripts/build_handoff_packages.py --sync`._

## C4 — P3 → P4: Student SeatCheck interaction

**Flow (verified by `test_T08_*`, `test_T10_*` and the e2e journey):**
1. `GET /api/session` returns `{session_token, expires_at_utc, note_th}`.
   - `api.ts` stores the token in `sessionStorage["sl_session_token"]` and **parses the expiry from the 2nd dot-separated part**, so the token format `<sid>.<exp>.<sig>` is part of this contract.
2. `POST /api/seat-reports` with `X-Session-Token` and body `{seat_id: ^[A-Z]{1,3}\d{1,3}$, reason: reported_occupied|belongings_present|seat_inaccessible|other, client_report_id?: 8–64 chars [A-Za-z0-9-]}` returns **201** with a `PublicReport` `{id, seat_id, reason, reason_th, created_at_utc, review_status: "pending", reviewed_at_utc, decision_reason, is_simulated, duplicate}`.
3. The seat immediately gets `pending_discrepancy = true` and `PENDING_REPORT`, so it drops out of recommendations. **Its `physical_state` and `display_state` do not change.**
4. Staff resolve the report (C3). The WS `delta` updates the seat, and `meta.recent_resolved_reports` contains the decision.
5. `GET /api/seat-reports/mine` (same session) returns `{reports: [PublicReport]}`.

| Condition | Result |
|---|---|
| same `client_report_id` again, same session | `201`, same report, `duplicate: true` (idempotent retry) |
| same `client_report_id`, other session | `409 REPLAY_CONFLICT` |
| same seat again while pending or within 10 min | `429 DUPLICATE_SEAT_REPORT` |
| > 3 reports per session per 10 min | `429 RATE_LIMITED` (limit is per session only — known limitation) |
| no / bad / expired session | `401 SESSION_REQUIRED` / `SESSION_INVALID` |

**UI contract between P3 and P4.** The Playwright suites depend on these `data-testid` values: `seatcheck-open`, `seatcheck-form`, `seatcheck-submit`, `pending-badge`, `my-reports`, `seat-detail`, `seat-state`. Today the form lives in `apps/web/src/components/SeatDetail.tsx` (P3). The planned `SeatCheckPanel.tsx` (P4) must keep these IDs; its props are **PA-05 (proposed)**.
<!-- SYNC:END -->

<!-- SYNC:BEGIN SHARED_V3/03_SHARED_API_CONTRACTS.md#PA -->
> _Synced from `SHARED_V3/03_SHARED_API_CONTRACTS.md` section `PA` — edit there, then run `scripts/build_handoff_packages.py --sync`._

## PA — Proposed additions (PROPOSED — NOT IMPLEMENTED)

Each item needs a change request (CR) and tests before anyone relies on it. GREEN, YELLOW and RED are defined in `04_TEAM_WORKING_AGREEMENT_TH.md`.

| ID | Proposal | Owner (+ review) | Class | Why |
|---|---|---|---|---|
| PA-01 | Env `SL_CV_EVIDENCE_DIR`, read by `AppSettings.from_env()`. V3 CV runs then write to `artifacts/cv/` or `evidence/team_v3/cv/`, and `evidence/cv/` stays frozen. | P2 (+P1, P3 for CV Lab) | YELLOW | issue #3; `run_cv.py` currently writes frozen evidence |
| PA-02 | Return `422 {"error": "BAD_TIMESTAMP"}` instead of 500 for an unparsable `observed_at_utc` | P2 (+P1) | GREEN (bug fix, additive code) | verified 500 |
| PA-03 | **Real-seat registration for CV.** A way to register a real camera and its seats (e.g. a new zone, `source_mode="cv"`, `is_active=1`, `metadata_source` such as `"staged_verified"`) so CV-derived data reaches the student map. Today only the hidden `LAB1`–`LAB4` receive CV data. | P2 (+P1 seat IDs/ROIs, +P3 map rendering, +P4 tests) | **RED** (DB seed / new seats on the public map) | needed for V3 goals 1–4 |
| PA-04 | Standardised **CV detection evidence record** (one JSON object per frame and seat, written by P1 for offline evaluation and replay; format proposed in the P1 package). P4 may build `integration/adapters/` to replay it into C1. | P1 (+P4) | GREEN for P1's own files; YELLOW once the backend consumes it | lets P1 change detectors freely |
| PA-05 | `SeatCheckPanel` props `{seat: Seat; myReports: PublicReport[]; onReported: (r: PublicReport) => void}` (taken from the current `SeatDetail` props), keeping all `data-testid` values | P4 (+P3) | YELLOW | issues #10, #7 |
| PA-06 | Staff console default for "confirmed occupied" becomes override `unknown`; UI wording only, no API change | P4 | GREEN (own file), notify P3 | issue #11 |
| PA-07 | Add `response_model` declarations so OpenAPI documents responses, without changing JSON | P2 | YELLOW (notify all) | contract tooling |
| PA-08 | Render zones from `GET /api/layout` instead of the hard-coded zones in `FloorMap.tsx` and `labels.ts` `ZONE_TH` | P3 | GREEN (own files), prerequisite for PA-03 | new zones would otherwise be invisible |
<!-- SYNC:END -->

<!-- SYNC:BEGIN SHARED_V3/03_SHARED_API_CONTRACTS.md#CT -->
> _Synced from `SHARED_V3/03_SHARED_API_CONTRACTS.md` section `CT` — edit there, then run `scripts/build_handoff_packages.py --sync`._

## CT — Contract tests per interface

| Interface | Existing tests (pass on `main`, 53 pytest + 8 Playwright) | To add in V3 (owner) |
|---|---|---|
| C1 | `tests/test_api.py::test_T13_duplicate_and_out_of_order_observations`, `::test_clock_skew_becomes_unknown`, `::test_source_contamination_guards`, `::test_T14_app_runs_without_cv_stack`; `tests/test_reliability.py::test_T07_override_wins_over_real_cv_ingest_path`; `tests/test_state_engine.py` (15 engine-rule tests); `tests/test_roi_geometry.py` | provider: `tests/test_backend_v3.py` (P2) — every row of the C1 error list + whole-frame rollback; sender conformance: `tests/test_cv_v3.py` (P1) — payloads built by the CV code validate against `IngestIn` and `C1__ingest_applied.json`; end-to-end smoke: `integration/smoke/` (P4) |
| C2 | `tests/test_api.py` T01–T03, T11, T12, `test_initial_seats_unknown_before_evidence`; `tests/test_reliability.py::test_recommendations_never_include_unsafe_states_across_scenarios`, `::test_seat_detail_and_layout_endpoints`; e2e `demo.spec.ts`, `reliability.spec.ts` (BUG-011), `server_restart.spec.ts` | `apps/web/e2e/student_v3.spec.ts` (P3); `tests/test_contract_v3.py` (P4): recorded example keys ⊆ live response keys, enum values unchanged |
| C3 | `test_T07_*`, `test_T09_*`, `test_T10_admin_requires_staff_token`, `test_override_expiry`, `test_reject_report_keeps_sensor_state`, `test_staff_unknown_override_pending_inspection`, `test_demo_endpoints_hidden_in_production` | `apps/web/e2e/staff_reliability_v3.spec.ts` (P4); C3 rows of `tests/test_contract_v3.py` (P4) |
| C4 | `test_T08_seatcheck_report_does_not_set_occupied`, `test_T10_report_rate_limit_duplicate_and_replay`, `test_false_free_report_scenario`; e2e journey | `staff_reliability_v3.spec.ts` (P4) + `student_v3.spec.ts` (P3) |

**Rule:** a PR that changes a provider (P2) must keep every consumer test above green, and must update `docs/api_contract_v3.md` and `contract_examples/` in the same PR.
<!-- SYNC:END -->

All 57 recorded real examples are in `docs/team_v3/individual_handoff/SHARED_V3/contract_examples/`. A copy is in this package's `contract_examples/` folder inside the ZIP.
