"""Trust layer: combine physical state, freshness, camera health, reports and staff overrides.

Physical state, evidence source, freshness, camera health, pending user report and staff override are
kept as SEPARATE dimensions. A seat is recommendable only when every dimension is trustworthy.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from .config import EngineConfig
from .evidence import AVAILABLE, RESERVED
from .state_engine import SeatEngineState, transition_pending
from .timeutil import age_seconds, parse_iso

STATE_LABEL_TH = {
    "available": "ว่าง",
    "occupied": "มีคนนั่ง",
    "reserved": "พบสิ่งของ / อาจถูกจับจอง",
    "unknown": "ไม่แน่ใจ (ข้อมูลไม่พอ)",
    "unavailable": "ปิดใช้งาน (เจ้าหน้าที่)",
    "maintenance": "ซ่อม/ทำความสะอาด (เจ้าหน้าที่)",
}

REASON_TH = {
    "STAFF_OVERRIDE": "เจ้าหน้าที่กำหนดสถานะทับไว้",
    "STATE_OCCUPIED": "ตรวจพบคนนั่ง",
    "STATE_RESERVED": "พบสิ่งของวางอยู่ (อาจถูกจับจอง)",
    "STATE_UNKNOWN": "หลักฐานไม่พอ จึงไม่ยืนยันว่าว่าง",
    "NO_OBSERVATION": "ยังไม่เคยได้รับข้อมูลที่นั่งนี้",
    "STALE": "ข้อมูลเก่าเกินเวลาที่กำหนด (stale)",
    "CAMERA_OFFLINE": "กล้องออฟไลน์",
    "CAMERA_DEGRADED": "คุณภาพภาพ/ความมั่นใจของกล้องต่ำ",
    "EVIDENCE_CHANGING": "หลักฐานล่าสุดกำลังเปลี่ยน รอยืนยันซ้ำ",
    "PENDING_REPORT": "มีรายงาน SeatCheck รอเจ้าหน้าที่ตรวจสอบ",
}


def build_seat_view(
    seat: dict,
    current: Optional[dict],
    override: Optional[dict],
    camera: Optional[dict],
    pending_reports: int,
    now: datetime,
    cfg: EngineConfig,
) -> dict:
    eng = SeatEngineState.from_dict(current.get("engine_state") if current else None)
    physical = eng.committed_state
    observed_at = current.get("observed_at_utc") if current else None
    age = age_seconds(now, observed_at)
    is_stale = observed_at is None or (age is not None and age > cfg.freshness_ttl_s)
    camera_health = camera_effective_status(camera, now, cfg) if camera else "unknown"
    override_state = override["state"] if override else None
    display_state = override_state or physical

    reasons = []
    if override:
        reasons.append("STAFF_OVERRIDE")
    if observed_at is None:
        reasons.append("NO_OBSERVATION")
    if physical != AVAILABLE:
        reasons.append(f"STATE_{physical.upper()}")
    if is_stale and observed_at is not None:
        reasons.append("STALE")
    if camera_health == "offline":
        reasons.append("CAMERA_OFFLINE")
    elif camera_health == "degraded":
        reasons.append("CAMERA_DEGRADED")
    if physical == AVAILABLE and transition_pending(eng):
        reasons.append("EVIDENCE_CHANGING")
    if pending_reports > 0:
        reasons.append("PENDING_REPORT")

    # Visual tone: an old or camera-offline observation is never painted with its automatic colour.
    if override_state:
        tone = override_state
    elif is_stale or camera_health == "offline":
        tone = "stale"
    else:
        tone = physical

    belongings_review = False
    belongings_for_s = None
    if physical == RESERVED and eng.reserved_since:
        belongings_for_s = max(0.0, (now - parse_iso(eng.reserved_since)).total_seconds())
        belongings_review = belongings_for_s >= cfg.belongings_review_after_s

    state_for_s = age_seconds(now, eng.committed_at)

    return {
        "seat_id": seat["seat_id"],
        "floor": seat["floor"],
        "zone_id": seat["zone_id"],
        "seat_type": seat["seat_type"],
        "has_power": bool(seat["has_power"]),
        "near_window": bool(seat["near_window"]),
        "quiet_zone": bool(seat["quiet_zone"]),
        "floor_x": seat["floor_x"],
        "floor_y": seat["floor_y"],
        "camera_id": seat["camera_id"],
        "metadata_source": seat.get("metadata_source"),
        "physical_state": physical,
        "physical_state_label_th": STATE_LABEL_TH.get(physical, physical),
        "display_state": display_state,
        "display_state_label_th": STATE_LABEL_TH.get(display_state, display_state),
        "display_tone": tone,
        "source": current.get("source") if current else None,
        "observed_at_utc": observed_at,
        "ingested_at_utc": current.get("ingest_time_utc") if current else None,
        "age_s": None if age is None else round(age, 1),
        "is_stale": is_stale,
        "camera_health": camera_health,
        "quality_flag": current.get("quality_flag") if current else None,
        "evidence_codes": eng.candidate_codes,
        "latest_candidate": eng.candidate_state,
        "transition_pending": transition_pending(eng),
        "state_since_utc": eng.committed_at,
        "state_for_s": None if state_for_s is None else round(state_for_s, 1),
        "last_confident_state": eng.last_confident_state,
        "last_confident_at_utc": eng.last_confident_at,
        "belongings_for_s": None if belongings_for_s is None else round(belongings_for_s, 1),
        "belongings_review_flag": belongings_review,
        "pending_discrepancy": pending_reports > 0,
        "pending_report_count": pending_reports,
        "manual_override": override,
        "is_recommendable": len(reasons) == 0,
        "not_recommendable_reasons": reasons,
        "not_recommendable_reasons_th": [REASON_TH.get(r, r) for r in reasons],
        "revision": current.get("revision", 0) if current else 0,
    }


def camera_effective_status(camera: dict, now: datetime, cfg: EngineConfig) -> str:
    """healthy / degraded / offline. Offline if reported offline or heartbeat older than timeout."""
    if camera.get("reported_status") == "offline":
        return "offline"
    last_seen = camera.get("last_seen_utc")
    age = age_seconds(now, last_seen)
    if age is None or age > cfg.heartbeat_timeout_s:
        return "offline"
    if camera.get("reported_status") == "degraded":
        return "degraded"
    return "healthy"
