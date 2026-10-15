"""Pure state-engine tests (no API). Acceptance IDs: T04, T05, T06, T13 (engine level)."""
from datetime import datetime, timedelta, timezone

from app.engine.config import EngineConfig
from app.engine.evidence import AVAILABLE, OCCUPIED, RESERVED, UNKNOWN, Detection, classify
from app.engine.state_engine import SeatEngineState, step
from app.engine.trust import build_seat_view

CFG = EngineConfig()
T0 = datetime(2026, 10, 14, 9, 0, 0, tzinfo=timezone.utc)

PERSON_SEATED = [Detection("person", 0.86, in_seat=True, in_table=True, seat_overlap=0.6)]
PASSERBY = [Detection("person", 0.88, in_seat=False, in_table=True, seat_overlap=0.1, table_overlap=0.35)]
BAG = [Detection("backpack", 0.74, in_table=True, table_overlap=0.9)]
CUP = [Detection("cup", 0.7, in_table=True, table_overlap=1.0)]
LOW_PERSON = [Detection("person", 0.35, in_seat=True, seat_overlap=0.5)]


def run(frames, start=None, dt=2.0, state=None):
    s = state or SeatEngineState()
    t = start or T0
    for dets, q in frames:
        s, _ = step(s, classify(dets, q, CFG), t, CFG)
        t = t + timedelta(seconds=dt)
    return s, t


def seat_meta(sid="X01"):
    return {"seat_id": sid, "floor": "f", "zone_id": "A", "seat_type": "single_desk", "has_power": 1, "near_window": 0,
            "quiet_zone": 1, "floor_x": 0, "floor_y": 0, "camera_id": "CAM-A"}


def test_never_observed_is_unknown_not_available():
    assert SeatEngineState().committed_state == UNKNOWN


def test_one_empty_frame_is_not_available_T06():
    s, _ = run([([], "ok")])
    assert s.committed_state == UNKNOWN
    s, _ = run([([], "ok")] * 3)  # 3 frames over 4 s: still below 4 frames / 5 s
    assert s.committed_state == UNKNOWN


def test_available_requires_consecutive_clean_frames():
    s, _ = run([([], "ok")] * 4)  # 4 frames spanning 6 s
    assert s.committed_state == AVAILABLE


def test_available_streak_broken_by_bad_frame():
    s, _ = run([([], "ok"), ([], "ok"), ([], "dark"), ([], "ok"), ([], "ok")])
    assert s.committed_state != AVAILABLE


def test_passerby_is_not_occupied_T06():
    s, t = run([([], "ok")] * 4)
    assert s.committed_state == AVAILABLE
    s, t = run([(PASSERBY, "ok")], start=t, state=s)
    assert s.committed_state == AVAILABLE  # one frame does not commit anything
    assert classify(PASSERBY, "ok", CFG).state == UNKNOWN
    assert "P_NEAR_NOT_SEATED" in classify(PASSERBY, "ok", CFG).codes
    s, t = run([(PASSERBY, "ok")] * 3, start=t, state=s)
    assert s.committed_state == UNKNOWN  # lingering ambiguity -> Unknown, never Occupied


def test_seated_person_becomes_occupied_after_smoothing():
    s, _ = run([(PERSON_SEATED, "ok")] * 2)
    assert s.committed_state == UNKNOWN
    s, _ = run([(PERSON_SEATED, "ok")] * 4)
    assert s.committed_state == OCCUPIED


def test_cup_only_is_not_reserved_T06():
    c = classify(CUP, "ok", CFG)
    assert c.state == AVAILABLE and "IGNORED_CUP" in c.codes
    s, _ = run([(CUP, "ok")] * 6)
    assert s.committed_state == AVAILABLE


def test_low_confidence_is_unknown_T04():
    s, t = run([([], "ok")] * 4)
    assert s.committed_state == AVAILABLE
    s, _ = run([(LOW_PERSON, "ok")] * 2, start=t, state=s)
    assert s.committed_state == UNKNOWN
    assert s.last_confident_state == AVAILABLE  # proposal: keep previous state visible + uncertain flag


def test_dark_frames_are_unknown():
    s, _ = run([([], "dark")] * 2)
    assert s.committed_state == UNKNOWN
    assert classify([], "blur", CFG).codes == ["Q_BLUR"]


def test_persistent_belongings_reserved_and_never_auto_released_T05():
    s, t = run([(BAG, "ok")] * 4)
    assert s.committed_state == RESERVED
    # 31 minutes of continued belongings evidence
    for i in range(31 * 30):
        s, _ = step(s, classify(BAG, "ok", CFG), t, CFG)
        t += timedelta(seconds=2)
    assert s.committed_state == RESERVED  # not auto-released to Available
    view = build_seat_view(seat_meta(), {"engine_state": s.to_dict(), "observed_at_utc": s.last_observed_at, "source": "scenario"},
                           None, {"reported_status": "healthy", "last_seen_utc": s.last_observed_at}, 0, t, CFG)
    assert view["belongings_review_flag"] is True
    assert view["display_state"] == RESERVED and view["is_recommendable"] is False
    assert view["display_state_label_th"] == "พบสิ่งของ / อาจถูกจับจอง"


def test_owner_returns_reserved_to_occupied():
    s, t = run([(BAG, "ok")] * 4)
    s, _ = run([(PERSON_SEATED + BAG, "ok")] * 4, start=t, state=s)
    assert s.committed_state == OCCUPIED


def test_out_of_order_observation_rejected_T13():
    s, t = run([([], "ok")] * 4)
    before = s.to_dict()
    s2, res = step(s, classify(PERSON_SEATED, "ok", CFG), T0 + timedelta(seconds=1), CFG)
    assert res.applied is False and res.reason == "OUT_OF_ORDER_OR_DUPLICATE"
    assert s2.to_dict() == before


def test_stale_view_is_never_green():
    s, t = run([([], "ok")] * 4)
    later = t + timedelta(seconds=CFG.freshness_ttl_s + 5)
    view = build_seat_view(seat_meta(), {"engine_state": s.to_dict(), "observed_at_utc": s.last_observed_at, "source": "scenario"},
                           None, {"reported_status": "healthy", "last_seen_utc": s.last_observed_at}, 0, later, CFG)
    assert view["physical_state"] == AVAILABLE
    assert view["is_stale"] is True and view["display_tone"] == "stale" and view["is_recommendable"] is False
    assert "STALE" in view["not_recommendable_reasons"]


def test_future_timestamp_never_gives_negative_age():
    s, t = run([([], "ok")] * 4)
    view = build_seat_view(seat_meta(), {"engine_state": s.to_dict(), "observed_at_utc": s.last_observed_at, "source": "scenario"},
                           None, {"reported_status": "healthy", "last_seen_utc": s.last_observed_at}, 0, T0, CFG)
    assert view["age_s"] == 0.0


def test_gap_longer_than_ttl_resets_to_unknown_BUG001():
    s, t = run([([], "ok")] * 4)
    assert s.committed_state == AVAILABLE
    later = t + timedelta(seconds=CFG.freshness_ttl_s + 10)
    s, res = step(s, classify([], "ok", CFG), later, CFG)
    assert s.committed_state == UNKNOWN and res.reason.startswith("GAP_RESET")
    s, _ = run([([], "ok")] * 4, start=later + timedelta(seconds=2), state=s)
    assert s.committed_state == AVAILABLE
