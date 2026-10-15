"""Engine configuration.

Every numeric default below is a *proposed initial value* taken from the original
group proposal (Smart_Library_Seat_Proposal.docx, section 11) unless noted.
They are NOT measured or validated performance settings. They can be overridden
with environment variables (prefix ``SL_``) so they can be tuned experimentally.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return float(raw)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return int(raw)


# COCO classes that the proposal counts as "belongings" (proposal said bag/laptop/book;
# COCO has no literal "bag" class, so bag -> backpack/handbag/suitcase).
BELONGINGS_CLASSES = frozenset({"backpack", "handbag", "suitcase", "laptop", "book"})
# Objects explicitly NOT treated as a claim on the seat (proposal failure case #4: cup, trash bin).
IGNORED_ITEM_CLASSES = frozenset({"cup", "bottle", "wine glass", "cell phone", "chair", "dining table", "couch"})


@dataclass(frozen=True)
class EngineConfig:
    # Detection confidence threshold (proposal: 0.5)
    conf_threshold: float = 0.5
    # Below this a detection is ignored entirely; between low and threshold => uncertain
    low_conf_threshold: float = 0.25
    # Temporal smoothing window (proposal: 5 s)
    smoothing_s: float = 5.0
    # Minimum consecutive frames for each committed state (V2 design choice)
    min_frames_occupied: int = 3
    min_frames_reserved: int = 3
    min_frames_available: int = 4  # Available needs *more* consecutive clean negatives
    min_frames_unknown: int = 2    # moving to Unknown is fast (safety first)
    # Fraction of a person's box that must overlap the seat polygon, plus the hip anchor
    min_seat_overlap: float = 0.30
    # Reserved timeout before raising a staff review flag (proposal: 30 min). Never auto-releases.
    belongings_review_after_s: float = 30 * 60
    # Freshness TTL: observation older than this => STALE overlay (V2; proposal heartbeat 30 s)
    freshness_ttl_s: float = 30.0
    # Heartbeat timeout before a camera is considered offline (proposal: 30 s)
    heartbeat_timeout_s: float = 30.0
    # Clock skew tolerance: observations further in the future are treated as clock skew
    clock_skew_tolerance_s: float = 5.0
    belongings_classes: frozenset = field(default=BELONGINGS_CLASSES)
    ignored_item_classes: frozenset = field(default=IGNORED_ITEM_CLASSES)

    @staticmethod
    def from_env() -> "EngineConfig":
        return EngineConfig(
            conf_threshold=_env_float("SL_CONF_THRESHOLD", 0.5),
            low_conf_threshold=_env_float("SL_LOW_CONF_THRESHOLD", 0.25),
            smoothing_s=_env_float("SL_SMOOTHING_S", 5.0),
            min_frames_occupied=_env_int("SL_MIN_FRAMES_OCCUPIED", 3),
            min_frames_reserved=_env_int("SL_MIN_FRAMES_RESERVED", 3),
            min_frames_available=_env_int("SL_MIN_FRAMES_AVAILABLE", 4),
            min_frames_unknown=_env_int("SL_MIN_FRAMES_UNKNOWN", 2),
            min_seat_overlap=_env_float("SL_MIN_SEAT_OVERLAP", 0.30),
            belongings_review_after_s=_env_float("SL_BELONGINGS_REVIEW_AFTER_S", 1800.0),
            freshness_ttl_s=_env_float("SL_FRESHNESS_TTL_S", 30.0),
            heartbeat_timeout_s=_env_float("SL_HEARTBEAT_TIMEOUT_S", 30.0),
            clock_skew_tolerance_s=_env_float("SL_CLOCK_SKEW_TOLERANCE_S", 5.0),
        )

    def public_dict(self) -> dict:
        return {
            "conf_threshold": self.conf_threshold,
            "low_conf_threshold": self.low_conf_threshold,
            "smoothing_s": self.smoothing_s,
            "min_frames": {
                "occupied": self.min_frames_occupied,
                "reserved": self.min_frames_reserved,
                "available": self.min_frames_available,
                "unknown": self.min_frames_unknown,
            },
            "min_seat_overlap": self.min_seat_overlap,
            "belongings_review_after_s": self.belongings_review_after_s,
            "freshness_ttl_s": self.freshness_ttl_s,
            "heartbeat_timeout_s": self.heartbeat_timeout_s,
            "clock_skew_tolerance_s": self.clock_skew_tolerance_s,
            "belongings_classes": sorted(self.belongings_classes),
            "ignored_item_classes": sorted(self.ignored_item_classes),
            "provenance": "Proposed initial defaults from the group proposal (DOCX s.11) + V2 design choices; not validated measurements.",
        }
