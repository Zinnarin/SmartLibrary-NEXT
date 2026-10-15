"""Phase-3 reliability verification (added during demo stabilisation, 14 Oct 2026)."""
from datetime import timedelta

from app.engine.timeutil import iso
from conftest import STAFF

SAFE_FIELDS = ("display_state", "display_tone", "is_stale", "camera_health", "pending_discrepancy", "manual_override", "transition_pending")


def _assert_safe(v):
    assert v["display_state"] == "available" and v["display_tone"] == "available", v["seat_id"]
    assert v["is_stale"] is False and v["camera_health"] == "healthy"
    assert v["pending_discrepancy"] is False and v["manual_override"] is None
    assert v["transition_pending"] is False and v["physical_state"] == "available"


def test_recommendations_never_include_unsafe_states_across_scenarios(ctx):
    """Property check over every scenario, several tick counts, single + GroupFit, with filters."""
    ctx.client.post("/api/seat-reports", json={"seat_id": "B03", "reason": "other"}, headers=ctx.session())
    ctx.client.post("/api/admin/seats/C05/override", json={"state": "maintenance", "reason": "ทดสอบ"}, headers=STAFF)
    checked = 0
    for name, cam in [("NORMAL", None), ("EXAM_RUSH", None), ("BELONGINGS", None), ("FALSE_FREE_REPORT", None),
                      ("LOW_CONFIDENCE", None), ("CAMERA_LOST", "CAM-A"), ("CAMERA_LOST", "ALL"), ("RECOVERED", None), ("NORMAL", None)]:
        ctx.scenario(name, cam)
        for n in (0, 1, 2, 5, 17):
            ctx.tick(n)
            seats = ctx.seats()
            for params in ({}, {"quiet": True}, {"power": True, "window": "prefer"}, {"seat_type": "group_table"}):
                r = ctx.client.get("/api/recommendations", params={**params, "limit": 24}).json()
                for x in r["results"]:
                    _assert_safe(seats[x["seat_id"]])
                    checked += 1
                g = ctx.client.get("/api/recommendations", params={**params, "group_size": 2, "limit": 24}).json()
                for p in g["group_results"]:
                    for sid in p["seats"]:
                        _assert_safe(seats[sid])
                        checked += 1
    assert checked > 100  # the property was exercised on many recommendations, not vacuously


def test_scenario_switch_is_smoothed_and_changing_seat_is_withheld(ctx):
    a07 = ctx.seats()["A07"]
    assert a07["is_recommendable"]
    ctx.scenario("EXAM_RUSH")
    ctx.tick(1)
    a07 = ctx.seats()["A07"]
    assert a07["physical_state"] == "available"  # one frame does not flip the state (smoothing)
    assert a07["transition_pending"] and not a07["is_recommendable"] and "EVIDENCE_CHANGING" in a07["not_recommendable_reasons"]
    ctx.tick(3)
    assert ctx.seats()["A07"]["physical_state"] == "occupied"


def test_T07_override_wins_over_real_cv_ingest_path(ctx):
    """T07 through the real CV ingest endpoint (source='cv'), not only scenario frames."""
    r = ctx.client.post("/api/admin/seats/LAB1/override", json={"state": "maintenance", "reason": "ปิดทดสอบ CV"}, headers=STAFF)
    assert r.status_code == 200
    t0 = ctx.clock.now() - timedelta(seconds=10)
    for i in range(5):
        body = {"camera_id": "CV-LAB", "frame_id": f"t07cv-{i:03d}", "observed_at_utc": iso(t0 + timedelta(seconds=2 * i)),
                "frame_quality": "ok", "model_version": "test-fixture (not a model)",
                "seats": [{"seat_id": "LAB1", "event_id": f"t07cv-{i:03d}-LAB1", "detections": []}]}
        assert ctx.client.post("/api/ingest/observations", json=body, headers={"X-Device-Token": "cv-device-demo-2569"}).status_code == 200
    lab1 = {v["seat_id"]: v for v in ctx.client.get("/api/cv/lab-seats").json()["seats"]}["LAB1"]
    assert lab1["source"] == "cv" and lab1["physical_state"] == "available"
    assert lab1["display_state"] == "maintenance" and not lab1["is_recommendable"]
    ev = ctx.client.get("/api/admin/events", params={"category": "override"}, headers=STAFF).json()["events"]
    assert any("LAB1" in e["detail"] for e in ev)


def test_staff_unknown_override_pending_inspection(ctx):
    r = ctx.client.post("/api/admin/seats/B07/override",
                        json={"state": "unknown", "reason": "รอตรวจมุมกล้อง", "expires_in_minutes": 15}, headers=STAFF)
    assert r.status_code == 200 and r.json()["expires_at_utc"]
    b07 = ctx.seats()["B07"]
    assert b07["display_state"] == "unknown" and b07["physical_state"] == "available" and not b07["is_recommendable"]


def test_camera_offline_is_immediate_and_stale_follows_ttl(ctx):
    ctx.scenario("CAMERA_LOST", "CAM-B")
    b = ctx.seats()["B07"]
    assert b["camera_health"] == "offline" and b["display_tone"] == "stale" and not b["is_stale"]  # offline now, not yet past TTL
    ctx.clock.advance(ctx.cfg.freshness_ttl_s + 1)
    b = ctx.seats()["B07"]
    assert b["is_stale"] and "STALE" in b["not_recommendable_reasons"] and "CAMERA_OFFLINE" in b["not_recommendable_reasons"]


def test_heartbeat_timeout_marks_silent_camera_offline_without_lwt(ctx):
    """Even without a disconnect message, a camera that stops sending is offline after the heartbeat timeout."""
    ctx.clock.advance(ctx.cfg.heartbeat_timeout_s + 1)  # nobody ticks: every simulated camera goes silent
    h = ctx.client.get("/api/health").json()
    assert all(c["status"] == "offline" for c in h["cameras"] if c["source_mode"] == "scenario")
    assert ctx.client.get("/api/recommendations", params={"limit": 24}).json()["results"] == []


def test_seat_detail_and_layout_endpoints(ctx):
    d = ctx.client.get("/api/seats/A07").json()
    assert d["seat"]["seat_id"] == "A07" and len(d["recent_observations"]) > 0
    assert all(o["source"] == "scenario" for o in d["recent_observations"])
    assert ctx.client.get("/api/seats/ZZ9").status_code == 404
    lay = ctx.client.get("/api/layout").json()
    assert len(lay["waypoints"]) == 11 and len(lay["edges"]) == 10 and len(lay["adjacency"]) == 12
    assert "ไม่ใช่ผังห้องสมุดจริง" in lay["note_th"]
