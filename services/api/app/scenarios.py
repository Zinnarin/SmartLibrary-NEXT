"""Scenario Lab: a SIMULATED observation source.

Each scenario describes, per seat, what a *simulated camera* would report (``view``) and the
developer-authored ground truth of the simulated scene (``truth``). Frames are generated on the
backend, persisted, and pushed through exactly the same SeatEvidenceAdapter + SeatStateEngine
path that real CV observations use. Nothing here is camera inference.
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Tuple

from .engine.evidence import Detection

SCENARIOS = ("NORMAL", "EXAM_RUSH", "BELONGINGS", "FALSE_FREE_REPORT", "LOW_CONFIDENCE", "CAMERA_LOST", "RECOVERED")
OVERLAY_SCENARIOS = ("CAMERA_LOST", "RECOVERED")
SCENARIO_CAMERAS = ("CAM-A", "CAM-B", "CAM-C")

SCENARIO_INFO_TH = {
    "NORMAL": "สถานการณ์ปกติ: มีทั้งที่นั่งว่าง มีคน มีของวาง และ 1 ที่นั่งถูกบัง (ไม่แน่ใจ)",
    "EXAM_RUSH": "ช่วงสอบ: ที่นั่งเกือบเต็ม เหลือว่างไม่กี่ที่ มีของวางจองหลายจุด",
    "BELONGINGS": "พบสิ่งของวางต่อเนื่องหลายที่นั่ง: แสดงเป็น 'พบสิ่งของ / อาจถูกจับจอง' ไม่ใช่การจอง และไม่ปลดอัตโนมัติ",
    "FALSE_FREE_REPORT": "กล้องจำลองมองไม่เห็นคนที่ A07 (ระบบจึงเห็นว่าว่าง) และมีรายงาน SeatCheck จำลอง 1 รายการ",
    "LOW_CONFIDENCE": "กล้องโซน C ภาพมืด/ความมั่นใจต่ำ: ต้องกลายเป็น 'ไม่แน่ใจ' ไม่ใช่สีเขียว",
    "CAMERA_LOST": "กล้องหลุด (จำลอง LWT): ไม่มีข้อมูลใหม่ ที่นั่งเดิมต้องไม่ถูกแนะนำ และเป็น STALE เมื่อเกิน TTL",
    "RECOVERED": "กล้องกลับมา: ต้องเห็นหลักฐานซ้ำครบตามเกณฑ์ก่อนกลับเป็น 'ว่าง'",
}

# view -> truth for the simulated scene
VIEW_TRUTH = {
    "empty": "available",
    "person": "occupied",
    "belongings": "reserved",
    "cup": "available",
    "hidden_person": "occupied",   # camera misses a person -> the system will (wrongly) see empty
    "lowconf": "occupied",
    "dark": "occupied",
    "occluded": "occupied",
}

_NORMAL = {
    "A01": "person", "A02": "person", "A03": "empty", "A04": "belongings",
    "A05": "empty", "A06": "person", "A07": "empty", "A08": "empty",
    "B01": "person", "B02": "person", "B03": "empty", "B04": "empty",
    "B05": "person", "B06": "empty", "B07": "empty", "B08": "person",
    "C01": "empty", "C02": "person", "C03": "cup", "C04": "person",
    "C05": "empty", "C06": "empty", "C07": "belongings", "C08": "occluded",
}


def _layout(name: str) -> Dict[str, str]:
    v = dict(_NORMAL)
    if name == "NORMAL":
        return v
    if name == "EXAM_RUSH":
        for k in v:
            v[k] = "person"
        for k in ("A08", "B07", "C05"):
            v[k] = "empty"
        for k in ("A03", "A05", "B03", "B06", "C01"):
            v[k] = "belongings"
        v["C08"] = "occluded"
        return v
    if name == "BELONGINGS":
        for k in ("A05", "A08", "B06"):
            v[k] = "belongings"
        return v
    if name == "FALSE_FREE_REPORT":
        v["A07"] = "hidden_person"
        return v
    if name == "LOW_CONFIDENCE":
        for k in ("C01", "C02", "C03", "C04"):
            v[k] = "dark"
        for k in ("C05", "C06", "C07", "C08"):
            v[k] = "lowconf"
        return v
    raise ValueError(name)


def build_run(name: str, previous_run: dict | None, camera_id: str | None = None) -> Tuple[str, dict, dict, dict]:
    """Return (base_scenario, truth, cameras, params) for a new scenario run."""
    if name not in SCENARIOS:
        raise ValueError(f"unknown scenario {name}")
    if name in OVERLAY_SCENARIOS:
        if previous_run is None:
            base, truth, cameras = "NORMAL", _truth(_layout("NORMAL")), _cameras_for("NORMAL")
        else:
            base, truth, cameras = previous_run["base_scenario"], previous_run["truth"], dict(previous_run["cameras"])
        if name == "CAMERA_LOST":
            target = camera_id or "CAM-A"
            for cam in SCENARIO_CAMERAS:
                if target == "ALL" or cam == target:
                    cameras[cam] = "lost"
            return base, truth, cameras, {"camera_id": target}
        # RECOVERED: every simulated camera back, keeping the degraded flag of the base scenario
        rec = _cameras_for(base)
        return base, truth, rec, {}
    return name, _truth(_layout(name)), _cameras_for(name), {}


def _cameras_for(base: str) -> dict:
    cams = {c: "online" for c in SCENARIO_CAMERAS}
    if base == "LOW_CONFIDENCE":
        cams["CAM-C"] = "degraded"
    return cams


def _truth(layout: Dict[str, str]) -> dict:
    return {sid: {"view": view, "truth": VIEW_TRUTH[view]} for sid, view in layout.items()}


def _jitter(seat_id: str, n: int, span: float) -> float:
    h = hashlib.sha256(f"{seat_id}:{n}".encode()).digest()
    return ((h[0] / 255.0) * 2 - 1) * span


def simulated_frame(seat_id: str, view: str, n: int) -> Tuple[str, List[Detection]]:
    """Deterministic simulated detections for one seat at frame index n. Labelled source='scenario'."""
    j = lambda span: _jitter(seat_id, n, span)  # noqa: E731
    if view in ("empty", "hidden_person"):
        return "ok", []
    if view == "person":
        return "ok", [Detection("person", 0.84 + j(0.06), in_seat=True, in_table=True, seat_overlap=0.62 + j(0.05), table_overlap=0.25)]
    if view == "belongings":
        return "ok", [
            Detection("backpack", 0.72 + j(0.06), in_table=True, table_overlap=0.9),
            Detection("laptop", 0.66 + j(0.05), in_table=True, table_overlap=1.0),
        ]
    if view == "cup":
        return "ok", [Detection("cup", 0.61 + j(0.05), in_table=True, table_overlap=1.0)]
    if view == "lowconf":
        return "ok", [Detection("person", 0.36 + j(0.06), in_seat=True, seat_overlap=0.5)]
    if view == "dark":
        return "dark", []
    if view == "occluded":
        return "occluded", []
    raise ValueError(view)
