"""Application services: observation ingestion, reports, overrides, scenario runs, seat views.

Every mutation runs inside one SQLite transaction (``db.write()``) so state, audit events and
denormalised flags change atomically.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .db import Database, jdump, jload, row, rows
from .engine.config import EngineConfig
from .engine.evidence import Detection, classify
from .engine.state_engine import SeatEngineState, step
from .engine.timeutil import iso, parse_iso
from .engine.trust import STATE_LABEL_TH, build_seat_view
from . import scenarios as sc

REPORT_REASONS = {
    "reported_occupied": "มีคนนั่งอยู่จริง",
    "belongings_present": "มีสิ่งของวางอยู่",
    "seat_inaccessible": "เข้าไปนั่งไม่ได้ / ที่นั่งชำรุด",
    "other": "อื่น ๆ",
}

REPORT_LIMIT_PER_SESSION = 3          # reports per session per window
REPORT_WINDOW_S = 10 * 60
REPORT_SAME_SEAT_COOLDOWN_S = 10 * 60


class ServiceError(Exception):
    def __init__(self, status: int, code: str, message_th: str):
        super().__init__(message_th)
        self.status = status
        self.code = code
        self.message_th = message_th


def log_event(conn, now: datetime, category: str, detail: str, source: str, seat_id=None, actor_id=None, payload=None):
    conn.execute(
        "INSERT INTO system_events(created_at_utc,category,detail,source,seat_id,actor_id,payload) VALUES (?,?,?,?,?,?,?)",
        (iso(now), category, detail, source, seat_id, actor_id, jdump(payload) if payload is not None else None),
    )


# ---------------------------------------------------------------- observations


@dataclass
class IngestResult:
    status: str  # applied | late | duplicate
    seat_id: str
    raw_candidate: Optional[str] = None
    committed_state: Optional[str] = None
    committed_changed: bool = False
    reason: str = ""


def ingest_observation(
    conn,
    cfg: EngineConfig,
    now: datetime,
    *,
    event_id: str,
    seat_id: str,
    camera_id: str,
    source: str,
    observed_at: datetime,
    frame_quality: str,
    detections: List[Detection],
    model_version: Optional[str] = None,
    observation_group_id: Optional[str] = None,
    scenario_run_id: Optional[int] = None,
) -> IngestResult:
    if row(conn.execute("SELECT id FROM seat_observations WHERE event_id=?", (event_id,))):
        return IngestResult("duplicate", seat_id, reason="DUPLICATE_EVENT_ID")
    seat = row(conn.execute("SELECT seat_id, camera_id FROM seats WHERE seat_id=?", (seat_id,)))
    if not seat:
        raise ServiceError(404, "SEAT_NOT_FOUND", f"ไม่พบที่นั่ง {seat_id}")
    if seat["camera_id"] != camera_id:
        raise ServiceError(422, "CAMERA_MISMATCH", f"ที่นั่ง {seat_id} ไม่ได้อยู่ในมุมกล้อง {camera_id}")
    dev = row(conn.execute("SELECT source_mode FROM devices WHERE camera_id=?", (camera_id,)))
    if not dev or dev["source_mode"] != source:
        # keeps simulated feeds and real CV feeds from contaminating each other
        raise ServiceError(422, "SOURCE_MISMATCH", f"กล้อง {camera_id} ไม่ได้ตั้งค่าเป็นแหล่งข้อมูล {source}")

    effective_at = observed_at
    if observed_at > now + timedelta(seconds=cfg.clock_skew_tolerance_s):
        frame_quality = "clock_skew"
        effective_at = now

    cand = classify(detections, frame_quality, cfg)
    cur = row(conn.execute("SELECT * FROM seat_current WHERE seat_id=?", (seat_id,)))
    eng = SeatEngineState.from_dict(jload(cur["engine_state"]) if cur else None)
    new_eng, res = step(eng, cand, effective_at, cfg)

    conn.execute(
        "INSERT INTO seat_observations(event_id,seat_id,observed_at_utc,ingested_at_utc,source,camera_id,raw_candidate,"
        "committed_state,detector_confidence,evidence_codes,detections,frame_quality,model_version,observation_group_id,applied,apply_reason,scenario_run_id)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            event_id, seat_id, iso(observed_at), iso(now), source, camera_id, cand.state, new_eng.committed_state,
            cand.confidence, jdump(cand.codes), jdump([d.to_dict() for d in detections]), frame_quality, model_version,
            observation_group_id, 1 if res.applied else 0, res.reason, scenario_run_id,
        ),
    )
    if not res.applied:
        return IngestResult("late", seat_id, cand.state, eng.committed_state, False, res.reason)

    conn.execute(
        "UPDATE seat_current SET physical_state=?, observed_at_utc=?, ingest_time_utc=?, source=?, quality_flag=?,"
        " engine_state=?, revision=revision+1, last_event_id=? WHERE seat_id=?",
        (new_eng.committed_state, iso(effective_at), iso(now), source, frame_quality, jdump(new_eng.to_dict()), event_id, seat_id),
    )
    if res.committed_changed:
        log_event(
            conn, now, "state",
            f"{seat_id}: {STATE_LABEL_TH.get(res.previous_state)} → {STATE_LABEL_TH.get(res.new_state)} ({', '.join(cand.codes)})",
            source, seat_id=seat_id,
            payload={"from": res.previous_state, "to": res.new_state, "codes": cand.codes, "event_id": event_id},
        )
    return IngestResult("applied", seat_id, cand.state, new_eng.committed_state, res.committed_changed, res.reason)


def touch_device(conn, now: datetime, camera_id: str, status: str, quality: Optional[str], detail: Optional[str] = None):
    conn.execute(
        "UPDATE devices SET reported_status=?, last_seen_utc=?, last_quality=?, detail=COALESCE(?, detail), updated_at_utc=? WHERE camera_id=?",
        (status, iso(now), quality, detail, iso(now), camera_id),
    )


# ---------------------------------------------------------------- scenario source


def active_run(conn) -> Optional[dict]:
    r = row(conn.execute("SELECT * FROM scenario_runs WHERE is_active=1 ORDER BY id DESC LIMIT 1"))
    if r:
        r["truth"] = jload(r["truth"])
        r["cameras"] = jload(r["cameras"])
        r["params"] = jload(r["params"])
    return r


def start_scenario(db: Database, now: datetime, name: str, actor: str, camera_id: Optional[str] = None) -> dict:
    if name not in sc.SCENARIOS:
        raise ServiceError(422, "UNKNOWN_SCENARIO", f"ไม่รู้จักสถานการณ์ {name}")
    if camera_id is not None and camera_id not in (*sc.SCENARIO_CAMERAS, "ALL"):
        raise ServiceError(422, "UNKNOWN_CAMERA", f"ไม่รู้จักกล้อง {camera_id}")
    with db.write() as conn:
        prev = active_run(conn)
        base, truth, cameras, params = sc.build_run(name, prev, camera_id)
        conn.execute("UPDATE scenario_runs SET is_active=0, ended_at_utc=? WHERE is_active=1", (iso(now),))
        cur = conn.execute(
            "INSERT INTO scenario_runs(scenario,base_scenario,started_at_utc,params,truth,cameras,is_active) VALUES (?,?,?,?,?,?,1)",
            (name, base, iso(now), jdump(params), jdump(truth), jdump(cameras)),
        )
        run_id = cur.lastrowid
        for cam, st in cameras.items():
            if st == "lost":
                # simulated MQTT Last-Will: the broker would announce the disconnect immediately
                conn.execute(
                    "UPDATE devices SET reported_status='offline', detail=?, updated_at_utc=? WHERE camera_id=?",
                    ("SIMULATED disconnect (scenario CAMERA_LOST)", iso(now), cam),
                )
        log_event(conn, now, "scenario", f"เริ่มสถานการณ์จำลอง {name} (SIMULATION)", "scenario", actor_id=actor,
                  payload={"run_id": run_id, "base": base, "cameras": cameras, "params": params})
        if name == "FALSE_FREE_REPORT":
            _create_report_tx(conn, now, "A07", "reported_occupied", "SIMULATED-STUDENT", f"sim-{run_id}", is_simulated=True)
        return {"run_id": run_id, "scenario": name, "base_scenario": base, "cameras": cameras, "params": params}


def emit_scenario_tick(db: Database, cfg: EngineConfig, now: datetime) -> int:
    """Generate one simulated frame for every seat seen by an online simulated camera."""
    with db.write() as conn:
        run = active_run(conn)
        if not run:
            return 0
        n = run["frames_emitted"]
        seats = rows(conn.execute("SELECT seat_id, camera_id FROM seats WHERE is_active=1"))
        emitted = 0
        for cam, cam_state in run["cameras"].items():
            if cam_state == "lost":
                continue
            quality_note = "degraded" if cam_state == "degraded" else "healthy"
            touch_device(conn, now, cam, quality_note, "low_confidence" if cam_state == "degraded" else "ok",
                         "SIMULATED camera (Scenario Lab)")
            group = f"scn{run['id']}-{cam}-{n}"
            for s in [s for s in seats if s["camera_id"] == cam]:
                spec = run["truth"].get(s["seat_id"])
                if not spec:
                    continue
                quality, dets = sc.simulated_frame(s["seat_id"], spec["view"], n)
                ingest_observation(
                    conn, cfg, now, event_id=f"{group}-{s['seat_id']}", seat_id=s["seat_id"], camera_id=cam,
                    source="scenario", observed_at=now, frame_quality=quality, detections=dets,
                    model_version=None, observation_group_id=group, scenario_run_id=run["id"],
                )
                emitted += 1
        conn.execute("UPDATE scenario_runs SET frames_emitted=frames_emitted+1 WHERE id=?", (run["id"],))
        return emitted


# ---------------------------------------------------------------- reports


def _refresh_seat_flags(conn, seat_id: str, now: datetime):
    pending = row(conn.execute("SELECT COUNT(*) AS n FROM seat_reports WHERE seat_id=? AND review_status='pending'", (seat_id,)))["n"]
    ov = active_override(conn, seat_id, now)
    conn.execute(
        "UPDATE seat_current SET user_report_pending=?, manual_override_id=?, revision=revision+1 WHERE seat_id=?",
        (1 if pending else 0, ov["id"] if ov else None, seat_id),
    )


def _create_report_tx(conn, now, seat_id, reason, session_id, client_report_id, is_simulated=False) -> dict:
    view_state = row(conn.execute("SELECT physical_state FROM seat_current WHERE seat_id=?", (seat_id,)))
    cur = conn.execute(
        "INSERT INTO seat_reports(seat_id,reason,created_at_utc,pseudo_session_id,client_report_id,review_status,is_simulated,display_state_at_report)"
        " VALUES (?,?,?,?,?,'pending',?,?)",
        (seat_id, reason, iso(now), session_id, client_report_id, 1 if is_simulated else 0, view_state["physical_state"] if view_state else None),
    )
    rid = cur.lastrowid
    _refresh_seat_flags(conn, seat_id, now)
    log_event(conn, now, "report",
              f"SeatCheck ใหม่ #{rid}: {seat_id} — {REPORT_REASONS[reason]}" + (" (SIMULATED)" if is_simulated else ""),
              "scenario" if is_simulated else "student", seat_id=seat_id,
              payload={"report_id": rid, "reason": reason, "simulated": is_simulated})
    return report_by_id(conn, rid)


def create_report(db: Database, now: datetime, seat_id: str, reason: str, session_id: str, client_report_id: Optional[str]) -> dict:
    if reason not in REPORT_REASONS:
        raise ServiceError(422, "BAD_REASON", "เหตุผลไม่ถูกต้อง")
    with db.write() as conn:
        seat = row(conn.execute("SELECT seat_id FROM seats WHERE seat_id=? AND is_active=1", (seat_id,)))
        if not seat:
            raise ServiceError(404, "SEAT_NOT_FOUND", f"ไม่พบที่นั่ง {seat_id}")
        if client_report_id:
            existing = row(conn.execute("SELECT id, pseudo_session_id FROM seat_reports WHERE client_report_id=?", (client_report_id,)))
            if existing:
                if existing["pseudo_session_id"] != session_id:
                    raise ServiceError(409, "REPLAY_CONFLICT", "รหัสรายงานนี้ถูกใช้แล้ว")
                out = report_by_id(conn, existing["id"])
                out["duplicate"] = True
                return out
        window_start = iso(now - timedelta(seconds=REPORT_WINDOW_S))
        same_seat = row(conn.execute(
            "SELECT COUNT(*) AS n FROM seat_reports WHERE pseudo_session_id=? AND seat_id=? AND (review_status='pending' OR created_at_utc>=?)",
            (session_id, seat_id, iso(now - timedelta(seconds=REPORT_SAME_SEAT_COOLDOWN_S))),
        ))["n"]
        if same_seat:
            log_event(conn, now, "security", f"ปฏิเสธรายงานซ้ำที่นั่ง {seat_id} จาก session เดิม", "api", seat_id=seat_id)
            raise ServiceError(429, "DUPLICATE_SEAT_REPORT", "คุณรายงานที่นั่งนี้ไปแล้ว กรุณารอเจ้าหน้าที่ตรวจสอบ")
        recent = row(conn.execute(
            "SELECT COUNT(*) AS n FROM seat_reports WHERE pseudo_session_id=? AND created_at_utc>=?", (session_id, window_start)
        ))["n"]
        if recent >= REPORT_LIMIT_PER_SESSION:
            log_event(conn, now, "security", "จำกัดอัตราการรายงาน (rate limit) ของ session", "api")
            raise ServiceError(429, "RATE_LIMITED", f"ส่งรายงานได้ไม่เกิน {REPORT_LIMIT_PER_SESSION} ครั้งต่อ 10 นาที")
        return _create_report_tx(conn, now, seat_id, reason, session_id, client_report_id)


def report_by_id(conn, rid: int) -> dict:
    r = row(conn.execute("SELECT * FROM seat_reports WHERE id=?", (rid,)))
    if not r:
        raise ServiceError(404, "REPORT_NOT_FOUND", "ไม่พบรายงาน")
    r["reason_th"] = REPORT_REASONS.get(r["reason"], r["reason"])
    r["is_simulated"] = bool(r["is_simulated"])
    return r


def public_report(r: dict) -> dict:
    """Student-facing report view: no session id / actor."""
    return {k: r[k] for k in ("id", "seat_id", "reason", "reason_th", "created_at_utc", "review_status", "reviewed_at_utc", "decision_reason", "is_simulated")} | {
        "duplicate": r.get("duplicate", False)
    }


def list_reports(db: Database, status: Optional[str]) -> List[dict]:
    with db.read() as conn:
        if status and status != "all":
            rs = rows(conn.execute("SELECT * FROM seat_reports WHERE review_status=? ORDER BY id DESC", (status,)))
        else:
            rs = rows(conn.execute("SELECT * FROM seat_reports ORDER BY id DESC LIMIT 200"))
    for r in rs:
        r["reason_th"] = REPORT_REASONS.get(r["reason"], r["reason"])
        r["is_simulated"] = bool(r["is_simulated"])
    return rs


def resolve_report(db: Database, now: datetime, report_id: int, decision: str, reason: str, actor: str,
                   override_state: Optional[str] = None, override_minutes: Optional[int] = None) -> dict:
    if decision not in ("accepted", "rejected"):
        raise ServiceError(422, "BAD_DECISION", "decision ต้องเป็น accepted หรือ rejected")
    if not reason or len(reason.strip()) < 3:
        raise ServiceError(422, "REASON_REQUIRED", "ต้องระบุเหตุผลการตัดสิน (อย่างน้อย 3 ตัวอักษร)")
    if override_state and decision != "accepted":
        raise ServiceError(422, "OVERRIDE_REQUIRES_ACCEPT", "ตั้ง override ได้เฉพาะเมื่อยืนยันรายงาน")
    with db.write() as conn:
        rep = report_by_id(conn, report_id)
        if rep["review_status"] != "pending":
            raise ServiceError(409, "ALREADY_RESOLVED", "รายงานนี้ถูกตัดสินแล้ว")
        ov_id = None
        if override_state:
            ov_id = _set_override_tx(conn, now, rep["seat_id"], override_state, f"จากรายงาน #{report_id}: {reason.strip()}", actor,
                                     override_minutes, report_id)
        conn.execute(
            "UPDATE seat_reports SET review_status=?, reviewed_at_utc=?, decision_reason=?, actor_id=?, override_id=? WHERE id=?",
            (decision, iso(now), reason.strip(), actor, ov_id, report_id),
        )
        _refresh_seat_flags(conn, rep["seat_id"], now)
        latency = (now - parse_iso(rep["created_at_utc"])).total_seconds()
        log_event(conn, now, "report_resolved",
                  f"รายงาน #{report_id} ({rep['seat_id']}) {'ยืนยัน' if decision == 'accepted' else 'ปฏิเสธ'}: {reason.strip()}"
                  + (f" → ตั้ง {STATE_LABEL_TH[override_state]}" if override_state else ""),
                  "staff", seat_id=rep["seat_id"], actor_id=actor,
                  payload={"report_id": report_id, "decision": decision, "override_id": ov_id, "resolution_latency_s": round(latency, 1)})
        return report_by_id(conn, report_id)


# ---------------------------------------------------------------- overrides


def active_override(conn, seat_id: str, now: datetime) -> Optional[dict]:
    ov = row(conn.execute(
        "SELECT * FROM manual_overrides WHERE seat_id=? AND cleared_at_utc IS NULL ORDER BY id DESC LIMIT 1", (seat_id,)
    ))
    if ov and ov["expires_at_utc"] and parse_iso(ov["expires_at_utc"]) <= now:
        return None
    return ov


def _set_override_tx(conn, now, seat_id, state, reason, actor, minutes, report_id=None) -> int:
    if state not in ("unavailable", "maintenance", "unknown"):
        raise ServiceError(422, "BAD_OVERRIDE_STATE", "สถานะ override ต้องเป็น unavailable / maintenance / unknown")
    if not reason or len(reason.strip()) < 3:
        raise ServiceError(422, "REASON_REQUIRED", "ต้องระบุเหตุผล")
    if not row(conn.execute("SELECT seat_id FROM seats WHERE seat_id=?", (seat_id,))):
        raise ServiceError(404, "SEAT_NOT_FOUND", f"ไม่พบที่นั่ง {seat_id}")
    if minutes is not None and (minutes <= 0 or minutes > 7 * 24 * 60):
        raise ServiceError(422, "BAD_EXPIRY", "เวลาหมดอายุไม่ถูกต้อง")
    conn.execute(
        "UPDATE manual_overrides SET cleared_at_utc=?, cleared_by=? WHERE seat_id=? AND cleared_at_utc IS NULL",
        (iso(now), f"{actor} (superseded)", seat_id),
    )
    expires = iso(now + timedelta(minutes=minutes)) if minutes else None
    cur = conn.execute(
        "INSERT INTO manual_overrides(seat_id,state,reason,actor_id,created_at_utc,expires_at_utc,report_id) VALUES (?,?,?,?,?,?,?)",
        (seat_id, state, reason.strip(), actor, iso(now), expires, report_id),
    )
    _refresh_seat_flags(conn, seat_id, now)
    log_event(conn, now, "override", f"ตั้ง {seat_id} = {STATE_LABEL_TH[state]}: {reason.strip()}", "staff", seat_id=seat_id,
              actor_id=actor, payload={"override_id": cur.lastrowid, "state": state, "expires_at_utc": expires})
    return cur.lastrowid


def set_override(db: Database, now: datetime, seat_id: str, state: str, reason: str, actor: str, minutes: Optional[int]) -> dict:
    with db.write() as conn:
        oid = _set_override_tx(conn, now, seat_id, state, reason, actor, minutes)
        return row(conn.execute("SELECT * FROM manual_overrides WHERE id=?", (oid,)))


def clear_override(db: Database, now: datetime, seat_id: str, actor: str, reason: str) -> dict:
    with db.write() as conn:
        ov = active_override(conn, seat_id, now)
        if not ov:
            raise ServiceError(404, "NO_ACTIVE_OVERRIDE", f"{seat_id} ไม่มี override ที่ใช้งานอยู่")
        conn.execute("UPDATE manual_overrides SET cleared_at_utc=?, cleared_by=? WHERE id=?", (iso(now), actor, ov["id"]))
        _refresh_seat_flags(conn, seat_id, now)
        log_event(conn, now, "override", f"ยกเลิก override ของ {seat_id}: {reason or '-'}", "staff", seat_id=seat_id,
                  actor_id=actor, payload={"override_id": ov["id"]})
        return row(conn.execute("SELECT * FROM manual_overrides WHERE id=?", (ov["id"],)))


def expire_overrides(db: Database, now: datetime) -> int:
    with db.write() as conn:
        due = rows(conn.execute(
            "SELECT * FROM manual_overrides WHERE cleared_at_utc IS NULL AND expires_at_utc IS NOT NULL AND expires_at_utc<=?", (iso(now),)
        ))
        for ov in due:
            conn.execute("UPDATE manual_overrides SET cleared_at_utc=?, cleared_by='system (expired)' WHERE id=?", (iso(now), ov["id"]))
            _refresh_seat_flags(conn, ov["seat_id"], now)
            log_event(conn, now, "override", f"override ของ {ov['seat_id']} หมดอายุ", "system", seat_id=ov["seat_id"],
                      payload={"override_id": ov["id"]})
        return len(due)


# ---------------------------------------------------------------- views


def seat_views(db: Database, now: datetime, cfg: EngineConfig, include_lab: bool = False) -> List[dict]:
    with db.read() as conn:
        q = "SELECT * FROM seats" + ("" if include_lab else " WHERE is_active=1") + " ORDER BY seat_id"
        seats = rows(conn.execute(q))
        currents = {r["seat_id"]: r for r in rows(conn.execute("SELECT * FROM seat_current"))}
        devices = {r["camera_id"]: r for r in rows(conn.execute("SELECT * FROM devices"))}
        pend = {r["seat_id"]: r["n"] for r in rows(conn.execute(
            "SELECT seat_id, COUNT(*) AS n FROM seat_reports WHERE review_status='pending' GROUP BY seat_id"))}
        ovs = rows(conn.execute("SELECT * FROM manual_overrides WHERE cleared_at_utc IS NULL"))
    active_ov: Dict[str, dict] = {}
    for ov in ovs:
        if ov["expires_at_utc"] and parse_iso(ov["expires_at_utc"]) <= now:
            continue
        if ov["seat_id"] not in active_ov or ov["id"] > active_ov[ov["seat_id"]]["id"]:
            active_ov[ov["seat_id"]] = {k: ov[k] for k in ("id", "state", "reason", "actor_id", "created_at_utc", "expires_at_utc", "report_id")}
    out = []
    for s in seats:
        cur = currents.get(s["seat_id"])
        if cur:
            cur = dict(cur)
            cur["engine_state"] = jload(cur["engine_state"])
        out.append(build_seat_view(s, cur, active_ov.get(s["seat_id"]), devices.get(s["camera_id"]),
                                   pend.get(s["seat_id"], 0), now, cfg))
    return out


def device_views(db: Database, now: datetime, cfg: EngineConfig) -> List[dict]:
    from .engine.trust import camera_effective_status
    from .engine.timeutil import age_seconds

    with db.read() as conn:
        devs = rows(conn.execute("SELECT * FROM devices ORDER BY camera_id"))
    for d in devs:
        d["status"] = camera_effective_status(d, now, cfg) if d["last_seen_utc"] or d["reported_status"] == "offline" else "never_seen"
        a = age_seconds(now, d["last_seen_utc"])
        d["last_seen_age_s"] = None if a is None else round(a, 1)
    return devs


def new_event_id() -> str:
    return uuid.uuid4().hex
