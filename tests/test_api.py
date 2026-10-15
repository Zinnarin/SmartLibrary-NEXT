"""API + persistence tests through FastAPI TestClient with an injected clock.

Acceptance IDs covered: T01 T02 T03 T04 T05 T07 T08 T09 T10 T11 T12 T13 T14 (+ scenario/source guards).
"""
import importlib
import sys
import uuid
from datetime import timedelta

from app.engine.timeutil import iso
from conftest import STAFF

EXPECTED_NORMAL = {"available": 12, "occupied": 9, "reserved": 2, "unknown": 1}


# ------------------------------------------------------------------ T01


def test_T01_normal_counts_match_and_simulation_banner(ctx):
    data = ctx.client.get("/api/seats").json()
    counts = {}
    for v in data["seats"]:
        counts[v["display_state"]] = counts.get(v["display_state"], 0) + 1
    assert len(data["seats"]) == 24
    assert counts == EXPECTED_NORMAL
    assert data["meta"]["counts"] == EXPECTED_NORMAL
    assert data["meta"]["simulation_banner"].startswith("SIMULATION — NOT REAL CAMERA DATA")
    assert all(v["source"] == "scenario" for v in data["seats"])
    h = ctx.client.get("/api/health").json()
    assert h["simulation_active"] is True and h["active_sources"] == ["scenario"]
    z = ctx.client.get("/api/zones").json()["zones"]
    assert sum(zz["seat_count"] for zz in z) == 24 and {zz["zone_id"] for zz in z} == {"A", "B", "C"}


def test_initial_seats_unknown_before_evidence(make_ctx):
    app, clock, TC = make_ctx()
    c = TC(app)
    seats = c.get("/api/seats").json()["seats"]
    assert all(v["display_state"] == "unknown" and not v["is_recommendable"] for v in seats)


# ------------------------------------------------------------------ T02


def test_T02_quiet_power_hard_constraints(ctx):
    r = ctx.client.get("/api/recommendations", params={"quiet": True, "power": True}).json()
    seats = ctx.seats()
    assert [x["seat_id"] for x in r["results"]] == ["A07", "A05"]
    for x in r["results"]:
        v = seats[x["seat_id"]]
        assert v["quiet_zone"] and v["has_power"] and v["is_recommendable"] and not v["is_stale"]
        assert any(rr["kind"] == "trust" for rr in x["reasons"])
        assert "%" not in str(x)  # no fake probability
    assert "ไม่ใช่ความน่าจะเป็น" in r["score_note_th"]


def test_window_preference_is_soft_and_must_is_hard(ctx):
    soft = ctx.client.get("/api/recommendations", params={"window": "prefer", "limit": 24}).json()["results"]
    hard = ctx.client.get("/api/recommendations", params={"window": "must", "limit": 24}).json()["results"]
    seats = ctx.seats()
    assert len(soft) == 12
    assert all(seats[x["seat_id"]]["near_window"] for x in hard)
    assert seats[soft[0]["seat_id"]]["near_window"]


# ------------------------------------------------------------------ T03


def test_T03_camera_lost_then_ttl_stale(ctx):
    ctx.scenario("CAMERA_LOST", "CAM-A")
    seats = ctx.seats()
    a07 = seats["A07"]
    assert a07["camera_health"] == "offline" and not a07["is_recommendable"]
    assert "CAMERA_OFFLINE" in a07["not_recommendable_reasons"]
    last_obs = a07["observed_at_utc"]
    ctx.tick(int(ctx.cfg.freshness_ttl_s / 2) + 2)  # other cameras keep sending; CAM-A silent beyond TTL
    seats = ctx.seats()
    a07 = seats["A07"]
    assert a07["is_stale"] and a07["display_tone"] == "stale" and a07["observed_at_utc"] == last_obs
    assert a07["physical_state"] == "available"  # last state kept as history, but never shown green
    assert all(seats[s]["is_stale"] for s in seats if s.startswith("A"))
    assert not any(seats[s]["is_stale"] for s in seats if s.startswith("B"))
    r = ctx.client.get("/api/recommendations", params={"quiet": True, "power": True}).json()
    assert r["results"] == []
    assert r["empty_message_th"] == "ไม่มีที่นั่งที่ยืนยันได้ตอนนี้ตามเงื่อนไขที่เลือก"
    assert any(e["reason"] in ("STALE", "STATE_OCCUPIED") for e in r["excluded"])
    allr = ctx.client.get("/api/recommendations", params={"limit": 24}).json()["results"]
    assert not any(x["seat_id"].startswith("A") for x in allr)


def test_recovered_requires_fresh_evidence(ctx):
    ctx.scenario("CAMERA_LOST", "CAM-A")
    ctx.tick(20)
    ctx.scenario("RECOVERED")
    ctx.tick(1)
    a07 = ctx.seats()["A07"]
    assert not a07["is_recommendable"]  # one new frame is not enough
    ctx.tick(4)
    a07 = ctx.seats()["A07"]
    assert a07["is_recommendable"] and not a07["is_stale"] and a07["camera_health"] == "healthy"


# ------------------------------------------------------------------ T04 / T05


def test_T04_low_confidence_unknown(ctx):
    ctx.scenario("LOW_CONFIDENCE")
    ctx.tick(3)
    seats = ctx.seats()
    for sid in ("C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08"):
        assert seats[sid]["display_state"] == "unknown", sid
        assert not seats[sid]["is_recommendable"]
        assert seats[sid]["camera_health"] == "degraded"
    recs = ctx.client.get("/api/recommendations", params={"limit": 24}).json()["results"]
    assert not any(x["seat_id"].startswith("C") for x in recs)
    avail_before = 12
    assert sum(1 for v in seats.values() if v["display_state"] == "available") < avail_before


def test_T05_belongings_scenario_possibly_reserved(ctx):
    ctx.scenario("BELONGINGS")
    ctx.tick(5)
    seats = ctx.seats()
    for sid in ("A04", "A05", "A08", "B06", "C07"):
        assert seats[sid]["display_state"] == "reserved"
        assert seats[sid]["display_state_label_th"] == "พบสิ่งของ / อาจถูกจับจอง"
        assert not seats[sid]["is_recommendable"]
    # time passes beyond the 30 min review threshold: still reserved, only a staff flag is raised
    for _ in range(31):
        ctx.tick(30, dt=2.0)
    seats = ctx.seats()
    assert seats["A05"]["display_state"] == "reserved" and seats["A05"]["belongings_review_flag"] is True


# ------------------------------------------------------------------ T07


def test_T07_maintenance_override_wins_and_is_audited(ctx):
    r = ctx.client.post("/api/admin/seats/A07/override", json={"state": "maintenance", "reason": "เก้าอี้ชำรุด"}, headers=STAFF)
    assert r.status_code == 200
    ctx.tick(3)  # new automatic evidence keeps saying "available"
    a07 = ctx.seats()["A07"]
    assert a07["display_state"] == "maintenance" and a07["physical_state"] == "available"
    assert not a07["is_recommendable"] and "STAFF_OVERRIDE" in a07["not_recommendable_reasons"]
    ctx.scenario("CAMERA_LOST", "CAM-A")
    a07 = ctx.seats()["A07"]
    assert a07["display_state"] == "maintenance" and a07["camera_health"] == "offline"  # health still visible
    ev = ctx.client.get("/api/admin/events", params={"category": "override"}, headers=STAFF).json()["events"]
    assert any("A07" in e["detail"] for e in ev)
    r = ctx.client.delete("/api/admin/seats/A07/override", headers=STAFF)
    assert r.status_code == 200
    ctx.scenario("RECOVERED")
    ctx.tick(5)
    a07 = ctx.seats()["A07"]
    assert a07["manual_override"] is None and a07["display_state"] == "available" and a07["is_recommendable"]


def test_override_expiry(ctx):
    from app import services as svc

    ctx.client.post("/api/admin/seats/B03/override", json={"state": "unavailable", "reason": "จัดกิจกรรม", "expires_in_minutes": 1}, headers=STAFF)
    assert ctx.seats()["B03"]["display_state"] == "unavailable"
    ctx.clock.advance(61)
    assert ctx.seats()["B03"]["display_state"] != "unavailable"
    assert svc.expire_overrides(ctx.db, ctx.clock.now()) == 1


# ------------------------------------------------------------------ T08 / T09


def test_T08_seatcheck_report_does_not_set_occupied(ctx):
    sess = ctx.session()
    r = ctx.client.post("/api/seat-reports", json={"seat_id": "A07", "reason": "reported_occupied", "client_report_id": uuid.uuid4().hex},
                        headers=sess)
    assert r.status_code == 201, r.text
    assert r.json()["review_status"] == "pending"
    ctx.tick(2)
    a07 = ctx.seats()["A07"]
    assert a07["physical_state"] == "available" and a07["display_state"] == "available"  # no automatic Occupied
    assert a07["pending_discrepancy"] and not a07["is_recommendable"] and "PENDING_REPORT" in a07["not_recommendable_reasons"]
    recs = ctx.client.get("/api/recommendations", params={"quiet": True, "power": True}).json()["results"]
    assert [x["seat_id"] for x in recs] == ["A05"]
    staff = ctx.client.get("/api/admin/seat-reports", headers=STAFF).json()["reports"]
    assert staff[0]["seat_id"] == "A07" and staff[0]["review_status"] == "pending"
    assert "pseudo_session_id" not in r.json()


def test_T09_resolve_with_reason_audits_and_pushes_websocket(make_ctx):
    from app import services as svc

    app, clock, TC = make_ctx(background=True)
    with TC(app) as client:
        for _ in range(5):
            clock.advance(2)
            svc.emit_scenario_tick(app.state.db, app.state.cfg, clock.now())
        sess = {"X-Session-Token": client.get("/api/session").json()["session_token"]}
        rep = client.post("/api/seat-reports", json={"seat_id": "A07", "reason": "reported_occupied"}, headers=sess).json()
        with client.websocket_connect("/ws/seats") as ws:
            snap = ws.receive_json()
            assert snap["type"] == "snapshot"
            a07 = next(v for v in snap["seats"] if v["seat_id"] == "A07")
            assert a07["pending_discrepancy"] is True
            # missing reason is rejected
            bad = client.post(f"/api/admin/seat-reports/{rep['id']}/resolve", json={"decision": "accepted", "reason": ""}, headers=STAFF)
            assert bad.status_code == 422
            res = client.post(f"/api/admin/seat-reports/{rep['id']}/resolve",
                              json={"decision": "accepted", "reason": "ตรวจแล้วมีคนนั่งจริง กล้องมองไม่เห็น", "override_state": "maintenance",
                                    "override_minutes": 30}, headers=STAFF)
            assert res.status_code == 200 and res.json()["review_status"] == "accepted"
            got = None
            for _ in range(10):
                msg = ws.receive_json()
                if msg["type"] == "delta":
                    hit = [v for v in msg["seats"] if v["seat_id"] == "A07"]
                    if hit and hit[0]["display_state"] == "maintenance":
                        got = (hit[0], msg)
                        break
            assert got is not None, "no websocket delta for A07"
            v, msg = got
            assert v["pending_discrepancy"] is False
            assert msg["meta"]["recent_resolved_reports"][0]["id"] == rep["id"]
        ev = client.get("/api/admin/events", params={"category": "report_resolved"}, headers=STAFF).json()["events"]
        assert ev and ev[0]["payload"]["report_id"] == rep["id"] and ev[0]["actor_id"] == "staff-demo"
        twice = client.post(f"/api/admin/seat-reports/{rep['id']}/resolve", json={"decision": "rejected", "reason": "again"}, headers=STAFF)
        assert twice.status_code == 409


def test_reject_report_keeps_sensor_state(ctx):
    sess = ctx.session()
    rep = ctx.client.post("/api/seat-reports", json={"seat_id": "B03", "reason": "belongings_present"}, headers=sess).json()
    ctx.client.post(f"/api/admin/seat-reports/{rep['id']}/resolve", json={"decision": "rejected", "reason": "ตรวจแล้วว่างจริง"}, headers=STAFF)
    b03 = ctx.seats()["B03"]
    assert b03["display_state"] == "available" and b03["is_recommendable"] and not b03["pending_discrepancy"]


# ------------------------------------------------------------------ T10


def test_T10_admin_requires_staff_token(ctx):
    for method, url, body in [
        ("get", "/api/admin/seat-reports", None),
        ("post", "/api/admin/seats/A07/override", {"state": "maintenance", "reason": "xxx"}),
        ("delete", "/api/admin/seats/A07/override", None),
        ("get", "/api/admin/events", None),
        ("post", "/api/demo/scenario", {"scenario": "EXAM_RUSH"}),
    ]:
        r = getattr(ctx.client, method)(url, json=body) if body else getattr(ctx.client, method)(url)
        assert r.status_code == 401, (url, r.status_code)
        r = (getattr(ctx.client, method)(url, json=body, headers={"X-Staff-Token": "wrong"}) if body
             else getattr(ctx.client, method)(url, headers={"X-Staff-Token": "wrong"}))
        assert r.status_code == 401
    assert ctx.seats()["A07"]["manual_override"] is None
    sec = ctx.client.get("/api/admin/events", params={"category": "security"}, headers=STAFF).json()["events"]
    assert len(sec) >= 10


def test_T10_report_rate_limit_duplicate_and_replay(ctx):
    sess = ctx.session()
    cid = uuid.uuid4().hex
    r1 = ctx.client.post("/api/seat-reports", json={"seat_id": "A07", "reason": "reported_occupied", "client_report_id": cid}, headers=sess)
    assert r1.status_code == 201
    replay = ctx.client.post("/api/seat-reports", json={"seat_id": "A07", "reason": "reported_occupied", "client_report_id": cid}, headers=sess)
    assert replay.status_code == 201 and replay.json()["id"] == r1.json()["id"] and replay.json()["duplicate"] is True
    dup = ctx.client.post("/api/seat-reports", json={"seat_id": "A07", "reason": "other"}, headers=sess)
    assert dup.status_code == 429 and dup.json()["error"] == "DUPLICATE_SEAT_REPORT"
    assert ctx.client.post("/api/seat-reports", json={"seat_id": "B03", "reason": "other"}, headers=sess).status_code == 201
    assert ctx.client.post("/api/seat-reports", json={"seat_id": "B04", "reason": "other"}, headers=sess).status_code == 201
    lim = ctx.client.post("/api/seat-reports", json={"seat_id": "C01", "reason": "other"}, headers=sess)
    assert lim.status_code == 429 and lim.json()["error"] == "RATE_LIMITED"
    with ctx.db.read() as conn:
        n = conn.execute("SELECT COUNT(*) FROM seat_reports").fetchone()[0]
    assert n == 3
    # forged / missing session token
    assert ctx.client.post("/api/seat-reports", json={"seat_id": "C01", "reason": "other"}).status_code == 401
    assert ctx.client.post("/api/seat-reports", json={"seat_id": "C01", "reason": "other"},
                           headers={"X-Session-Token": "abc.99999999999.deadbeef"}).status_code == 401
    # bounded reason / validated seat id
    assert ctx.client.post("/api/seat-reports", json={"seat_id": "C01", "reason": "hacked"}, headers=ctx.session()).status_code == 422
    assert ctx.client.post("/api/seat-reports", json={"seat_id": "Z99", "reason": "other"}, headers=ctx.session()).status_code == 404
    assert ctx.client.post("/api/seat-reports", json={"seat_id": "A07; DROP", "reason": "other"}, headers=ctx.session()).status_code == 422


def test_demo_endpoints_hidden_in_production(make_ctx):
    app, clock, TC = make_ctx(mode="production")
    c = TC(app)
    assert c.post("/api/demo/scenario", json={"scenario": "NORMAL"}, headers=STAFF).status_code == 404
    assert c.get("/api/demo/scenarios").status_code == 404
    assert c.post("/api/demo/reset", headers=STAFF).status_code == 404
    h = c.get("/api/health").json()
    assert h["simulation_active"] is False and h["simulation_banner"] is None


# ------------------------------------------------------------------ T11 / T12


def test_T11_groupfit_pairs_are_adjacent_and_eligible(ctx):
    r = ctx.client.get("/api/recommendations", params={"group_size": 2}).json()
    seats = ctx.seats()
    with ctx.db.read() as conn:
        edges = {(a, b) for a, b in conn.execute("SELECT seat_a, seat_b FROM seat_adjacency").fetchall()}
    assert r["group_results"]
    for p in r["group_results"]:
        a, b = p["seats"]
        assert (min(a, b), max(a, b)) in edges
        assert seats[a]["is_recommendable"] and seats[b]["is_recommendable"]
    # no adjacent fresh pair with quiet+power+window -> honest empty state
    e = ctx.client.get("/api/recommendations", params={"group_size": 2, "quiet": True, "power": True, "window": "must"}).json()
    assert e["group_results"] == [] and "ไม่มีที่นั่ง 2 ที่ติดกัน" in e["empty_message_th"]
    assert ctx.client.get("/api/recommendations", params={"group_size": 3}).status_code == 422


def test_T11_groupfit_excludes_reported_seat(ctx):
    ctx.client.post("/api/seat-reports", json={"seat_id": "A08", "reason": "other"}, headers=ctx.session())
    r = ctx.client.get("/api/recommendations", params={"group_size": 2}).json()
    assert all("A08" not in p["seats"] for p in r["group_results"])


def test_T12_routes_only_use_declared_edges(ctx):
    with ctx.db.read() as conn:
        edges = {(a, b) for a, b in conn.execute("SELECT a, b FROM waypoint_edges").fetchall()}
        access = dict(conn.execute("SELECT seat_id, access_waypoint_id FROM seats WHERE is_active=1").fetchall())
    for sid in access:
        r = ctx.client.get("/api/route", params={"to": sid}).json()
        wps = r["waypoints"]
        assert wps[0] == "ENTRANCE" and wps[-1] == access[sid]
        for a, b in zip(wps, wps[1:]):
            assert (min(a, b), max(a, b)) in edges, (sid, a, b)
        assert r["edges"][-1] == [access[sid], f"SEAT:{sid}"]
        assert "ไม่ใช่เมตร" in r["disclaimer_th"]
    assert ctx.client.get("/api/route", params={"to": "ZZ1"}).status_code == 404


# ------------------------------------------------------------------ T13


def _ingest(ctx, seat, event_id, observed, dets, cam="CV-LAB", quality="ok", token="cv-device-demo-2569"):
    return ctx.client.post("/api/ingest/observations", headers={"X-Device-Token": token}, json={
        "camera_id": cam, "frame_id": event_id, "observed_at_utc": iso(observed), "frame_quality": quality,
        "model_version": "test-fixture (not a model)", "seats": [{"seat_id": seat, "event_id": event_id, "detections": dets}]})


def test_T13_duplicate_and_out_of_order_observations(ctx):
    now = ctx.clock.now() - timedelta(seconds=20)  # past timestamps: future ones beyond skew tolerance are clock_skew
    for i in range(4):
        r = _ingest(ctx, "LAB1", f"evt-lab1-{i:03d}", now + timedelta(seconds=2 * i), [])
        assert r.status_code == 200 and r.json()["results"][0]["status"] == "applied"
    lab = {v["seat_id"]: v for v in ctx.client.get("/api/cv/lab-seats").json()["seats"]}
    assert lab["LAB1"]["physical_state"] == "available"
    rev = lab["LAB1"]["revision"]
    dup = _ingest(ctx, "LAB1", "evt-lab1-003", now + timedelta(seconds=6), [])
    assert dup.json()["results"][0]["status"] == "duplicate"
    late = _ingest(ctx, "LAB1", "evt-lab1-old", now - timedelta(seconds=10), [{"cls": "person", "conf": 0.9, "in_seat": True, "seat_overlap": 0.7}])
    assert late.json()["results"][0]["status"] == "late"
    lab = {v["seat_id"]: v for v in ctx.client.get("/api/cv/lab-seats").json()["seats"]}
    assert lab["LAB1"]["physical_state"] == "available" and lab["LAB1"]["revision"] == rev
    with ctx.db.read() as conn:
        assert conn.execute("SELECT COUNT(*) FROM seat_observations WHERE event_id='evt-lab1-003'").fetchone()[0] == 1
        assert conn.execute("SELECT applied FROM seat_observations WHERE event_id='evt-lab1-old'").fetchone()[0] == 0


def test_clock_skew_becomes_unknown(ctx):
    r = _ingest(ctx, "LAB2", "skew-0001", ctx.clock.now() + timedelta(hours=1), [])
    assert r.json()["results"][0]["raw_candidate"] == "unknown"
    with ctx.db.read() as conn:
        assert conn.execute("SELECT frame_quality FROM seat_observations WHERE event_id='skew-0001'").fetchone()[0] == "clock_skew"


def test_source_contamination_guards(ctx):
    # real-CV device cannot write simulated seats, and a bad token is refused
    assert _ingest(ctx, "A07", "guard-001", ctx.clock.now(), [], cam="CV-LAB").status_code == 422
    assert _ingest(ctx, "A07", "guard-002", ctx.clock.now(), [], cam="CAM-A").status_code == 422
    assert _ingest(ctx, "LAB1", "guard-003", ctx.clock.now(), [], token="nope").status_code == 401
    st = ctx.client.get("/api/stats").json()
    assert st["real_cv"]["observations"] == 0 and st["real_cv"]["accuracy"] is None
    assert st["simulation"]["label"].startswith("SIMULATED")


# ------------------------------------------------------------------ T14 / scenario


def test_T14_app_runs_without_cv_stack(ctx):
    assert "ultralytics" not in sys.modules and "torch" not in sys.modules and "cv2" not in sys.modules
    cv = ctx.client.get("/api/cv/status").json()
    assert cv["status"] == "NOT_RUN"
    h = ctx.client.get("/api/health").json()
    assert h["real_cv"]["observations"] == 0 and "cv" not in h["active_sources"]


def test_false_free_report_scenario(ctx):
    ctx.scenario("FALSE_FREE_REPORT")
    ctx.tick(3)
    a07 = ctx.seats()["A07"]
    assert a07["physical_state"] == "available" and a07["pending_discrepancy"]  # sensor still thinks free
    reps = ctx.client.get("/api/admin/seat-reports", headers=STAFF).json()["reports"]
    assert reps[0]["is_simulated"] is True and reps[0]["seat_id"] == "A07"
    st = ctx.client.get("/api/stats").json()["simulation"]
    assert "A07" in st["shown_available_but_truth_not_available"]
    assert "A07" not in st["recommendable_but_truth_not_available"]  # pending report keeps it out of recommendations


def test_exam_rush(ctx):
    ctx.scenario("EXAM_RUSH")
    ctx.tick(5)
    recs = ctx.client.get("/api/recommendations", params={"limit": 24}).json()["results"]
    assert sorted(x["seat_id"] for x in recs) == ["A08", "B07", "C05"]


def test_scenario_state_is_persisted_in_backend(make_ctx, tmp_path):
    app, clock, TC = make_ctx()
    c = TC(app)
    c.post("/api/demo/scenario", json={"scenario": "EXAM_RUSH"}, headers=STAFF)
    # a second app instance on the same DB sees the same active scenario (not a frontend-only effect)
    from app.main import create_app
    from app.settings import AppSettings

    app2 = create_app(AppSettings(db_path=str(tmp_path / "test.db"), start_background=False, cv_evidence_dir=str(tmp_path / "cv"),
                                  web_dist=str(tmp_path / "nodist")))
    assert TC(app2).get("/api/health").json()["scenario"]["name"] == "EXAM_RUSH"


def test_BUG012_index_html_is_not_cached(tmp_path):
    """The SPA shell must be revalidated so a rebuilt frontend is always picked up."""
    from fastapi.testclient import TestClient

    from app.main import create_app
    from app.settings import AppSettings

    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html><title>t</title>", encoding="utf-8")
    app = create_app(AppSettings(db_path=str(tmp_path / "t.db"), start_background=False, cv_evidence_dir=str(tmp_path / "cv"), web_dist=str(dist)))
    r = TestClient(app).get("/")
    assert r.status_code == 200 and "no-cache" in r.headers.get("cache-control", "")
    assert TestClient(app).get("/#/staff").status_code == 200
