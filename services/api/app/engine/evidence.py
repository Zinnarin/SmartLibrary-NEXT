"""SeatEvidenceAdapter: normalise one frame's per-seat evidence into a raw candidate state.

This module is pure Python (no FastAPI / OpenCV / torch) so that the *same* logic is used by
the simulated ScenarioObservationSource and by the real YOLO pipeline in ``cv/``.

Decision order (refines the original DOCX figure 2 decision tree):
  0. staff override is applied later (trust layer), never here
  1. frame quality gate      -> anything not 'ok' is UNKNOWN (cannot see == cannot say empty)
  2. seated person evidence  -> OCCUPIED candidate (hip anchor inside seat polygon + overlap)
  3. person near but not seated (walking past / standing) or low-confidence person -> UNKNOWN
  4. belongings classes in table/seat zone -> RESERVED candidate ("belongings suspected", not a booking)
  5. low-confidence belongings -> UNKNOWN
  6. otherwise visible and empty -> AVAILABLE candidate (ignored items such as cups are logged only)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .config import EngineConfig

AVAILABLE = "available"
OCCUPIED = "occupied"
RESERVED = "reserved"
UNKNOWN = "unknown"
UNAVAILABLE = "unavailable"
MAINTENANCE = "maintenance"

PHYSICAL_STATES = (AVAILABLE, OCCUPIED, RESERVED, UNKNOWN)
OVERRIDE_STATES = (UNAVAILABLE, MAINTENANCE, UNKNOWN)

FRAME_QUALITIES = ("ok", "dark", "bright", "blur", "occluded", "no_frame", "uncalibrated", "clock_skew")


@dataclass
class Detection:
    """One detection already related to ONE seat's video ROI polygons.

    in_seat / in_table: the anchor point (person: estimated hip point; object: box centre) lies inside
    the seat polygon / the tabletop-belongings polygon. *_overlap: fraction of the box area inside.
    """

    cls: str
    conf: float
    in_seat: bool = False
    in_table: bool = False
    seat_overlap: float = 0.0
    table_overlap: float = 0.0
    bbox: Optional[List[float]] = None

    @staticmethod
    def from_dict(d: dict) -> "Detection":
        return Detection(
            cls=str(d["cls"]),
            conf=float(d["conf"]),
            in_seat=bool(d.get("in_seat", False)),
            in_table=bool(d.get("in_table", False)),
            seat_overlap=float(d.get("seat_overlap", 0.0)),
            table_overlap=float(d.get("table_overlap", 0.0)),
            bbox=d.get("bbox"),
        )

    def to_dict(self) -> dict:
        out = {
            "cls": self.cls,
            "conf": round(self.conf, 4),
            "in_seat": self.in_seat,
            "in_table": self.in_table,
            "seat_overlap": round(self.seat_overlap, 4),
            "table_overlap": round(self.table_overlap, 4),
        }
        if self.bbox is not None:
            out["bbox"] = [round(float(v), 1) for v in self.bbox]
        return out


@dataclass
class Candidate:
    state: str
    confidence: Optional[float]
    codes: List[str] = field(default_factory=list)


def classify(detections: List[Detection], frame_quality: str, cfg: EngineConfig) -> Candidate:
    if frame_quality != "ok":
        return Candidate(UNKNOWN, None, [f"Q_{frame_quality.upper()}"])

    low, thr = cfg.low_conf_threshold, cfg.conf_threshold
    dets = [d for d in detections if d.conf >= low]

    persons = [d for d in dets if d.cls == "person"]
    near_persons = [p for p in persons if p.in_seat or p.in_table or p.seat_overlap > 0 or p.table_overlap > 0]
    seated = [
        p for p in near_persons if p.conf >= thr and p.in_seat and p.seat_overlap >= cfg.min_seat_overlap
    ]
    if seated:
        return Candidate(OCCUPIED, max(p.conf for p in seated), ["P_SEATED"])
    if any(p.conf >= thr for p in near_persons):
        # A person box crossing the ROI is not proof of sitting (walk-through / standing nearby).
        return Candidate(UNKNOWN, max(p.conf for p in near_persons), ["P_NEAR_NOT_SEATED"])
    if near_persons:
        return Candidate(UNKNOWN, max(p.conf for p in near_persons), ["P_LOW_CONF"])

    in_zone = [d for d in dets if d.in_table or d.in_seat]
    items = [d for d in in_zone if d.cls in cfg.belongings_classes]
    strong_items = [d for d in items if d.conf >= thr]
    ignored_codes = sorted({f"IGNORED_{d.cls.upper().replace(' ', '_')}" for d in in_zone if d.cls in cfg.ignored_item_classes})
    if strong_items:
        codes = sorted({f"B_{d.cls.upper()}" for d in strong_items}) + ignored_codes
        return Candidate(RESERVED, max(d.conf for d in strong_items), codes)
    if items:
        return Candidate(UNKNOWN, max(d.conf for d in items), ["B_LOW_CONF"] + ignored_codes)

    return Candidate(AVAILABLE, None, ["E_EMPTY_VISIBLE"] + ignored_codes)
