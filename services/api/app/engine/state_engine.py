"""SeatStateEngine: temporal smoothing of raw per-frame candidates into a committed physical state.

Rules (V2):
* A seat that has never been observed is UNKNOWN, never Available.
* A candidate must repeat for ``min_frames_<state>`` consecutive frames AND span at least
  ``smoothing_s`` seconds (UNKNOWN only needs min frames: moving to "don't know" is the safe direction).
* AVAILABLE needs more consecutive clean negative frames than the other states.
* RESERVED (belongings suspected) is NEVER auto-released after a timeout; after
  ``belongings_review_after_s`` only a staff-review flag is raised (computed at read time).
* Observations whose ``observed_at`` is not newer than the last applied one are rejected
  (out-of-order / replay protection; the caller records them as not applied).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

from .config import EngineConfig
from .evidence import AVAILABLE, OCCUPIED, RESERVED, UNKNOWN, Candidate
from .timeutil import iso, parse_iso


@dataclass
class SeatEngineState:
    committed_state: str = UNKNOWN
    committed_at: Optional[str] = None
    candidate_state: Optional[str] = None
    candidate_since: Optional[str] = None
    candidate_count: int = 0
    candidate_codes: List[str] = field(default_factory=list)
    candidate_confidence: Optional[float] = None
    last_observed_at: Optional[str] = None
    last_confident_state: Optional[str] = None
    last_confident_at: Optional[str] = None
    reserved_since: Optional[str] = None
    transitions: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: Optional[dict]) -> "SeatEngineState":
        if not d:
            return SeatEngineState()
        known = {k: d[k] for k in SeatEngineState.__dataclass_fields__ if k in d}
        return SeatEngineState(**known)


@dataclass
class StepResult:
    applied: bool
    committed_changed: bool
    previous_state: str
    new_state: str
    reason: str


def requirement(state: str, cfg: EngineConfig) -> Tuple[int, float]:
    if state == UNKNOWN:
        return cfg.min_frames_unknown, 0.0
    if state == OCCUPIED:
        return cfg.min_frames_occupied, cfg.smoothing_s
    if state == RESERVED:
        return cfg.min_frames_reserved, cfg.smoothing_s
    if state == AVAILABLE:
        return cfg.min_frames_available, cfg.smoothing_s
    raise ValueError(f"not a physical state: {state}")


def step(state: SeatEngineState, cand: Candidate, observed_at: datetime, cfg: EngineConfig) -> Tuple[SeatEngineState, StepResult]:
    prev = state.committed_state
    if state.last_observed_at is not None and observed_at <= parse_iso(state.last_observed_at):
        return state, StepResult(False, False, prev, prev, "OUT_OF_ORDER_OR_DUPLICATE")

    s = SeatEngineState.from_dict(state.to_dict())
    gap_reset = False
    if s.last_observed_at is not None:
        gap = (observed_at - parse_iso(s.last_observed_at)).total_seconds()
        if gap > cfg.freshness_ttl_s:
            # Evidence continuity was broken (camera/network gap). What happened during the gap is unknown:
            # restart from UNKNOWN so the seat must be re-confirmed (BUG-001 fix).
            gap_reset = s.committed_state != UNKNOWN
            s.committed_state = UNKNOWN
            s.committed_at = iso(observed_at)
            s.candidate_state = None
            s.candidate_count = 0
            s.reserved_since = None
    s.last_observed_at = iso(observed_at)
    if cand.state == s.candidate_state:
        s.candidate_count += 1
    else:
        s.candidate_state = cand.state
        s.candidate_since = iso(observed_at)
        s.candidate_count = 1
    s.candidate_codes = list(cand.codes)
    s.candidate_confidence = cand.confidence

    need_frames, need_span = requirement(cand.state, cfg)
    span = (observed_at - parse_iso(s.candidate_since)).total_seconds()
    changed = False
    reason = "HOLD"
    if cand.state == s.committed_state:
        reason = "CONFIRMED_SAME"
    elif s.candidate_count >= need_frames and span >= need_span:
        s.committed_state = cand.state
        s.committed_at = iso(observed_at)
        s.transitions += 1
        changed = True
        reason = f"COMMIT_{cand.state.upper()}"
        if cand.state == RESERVED:
            # belongings first seen at the start of this candidate run
            s.reserved_since = s.candidate_since
        else:
            s.reserved_since = None
    else:
        reason = f"PENDING_{cand.state.upper()}_{s.candidate_count}/{need_frames}"

    if gap_reset:
        changed = changed or s.committed_state != prev
        reason = f"GAP_RESET;{reason}"
    if s.committed_state != UNKNOWN:
        s.last_confident_state = s.committed_state
        s.last_confident_at = s.last_observed_at
    return s, StepResult(True, changed, prev, s.committed_state, reason)


def transition_pending(s: SeatEngineState) -> bool:
    """Latest raw evidence disagrees with the committed state (not yet smoothed)."""
    return s.candidate_state is not None and s.candidate_state != s.committed_state
