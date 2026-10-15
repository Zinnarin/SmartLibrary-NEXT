"""Smart Library NEXT V2 - FastAPI application (local demo).

Run:  .venv\\Scripts\\python -m uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8000
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import scenarios as sc
from . import services as svc
from .db import Database, jdump, jload, row, rows
from .engine.config import EngineConfig
from .engine.evidence import FRAME_QUALITIES, Detection
from .engine.timeutil import Clock, iso, parse_iso
from .matching import SEAT_TYPE_TH, Filters, Graph, recommend
from .realtime import Hub
from .seed import seed
from .settings import AppSettings

log = logging.getLogger("smartlibrary")

SIMULATION_BANNER = "SIMULATION — NOT REAL CAMERA DATA (ข้อมูลจำลอง ไม่ใช่ข้อมูลจากกล้องจริง)"


# ------------------------------------------------------------------ request models


class ReportIn(BaseModel):
    seat_id: str = Field(min_length=2, max_length=12, pattern=r"^[A-Z]{1,3}\d{1,3}$")
    reason: str = Field(max_length=32)
    client_report_id: Optional[str] = Field(default=None, min_length=8, max_length=64, pattern=r"^[A-Za-z0-9\-]+$")


class ResolveIn(BaseModel):
    decision: str
    reason: str = Field(min_length=3, max_length=300)
    override_state: Optional[str] = None
    override_minutes: Optional[int] = None


class OverrideIn(BaseModel):
    state: str
    reason: str = Field(min_length=3, max_length=300)
    expires_in_minutes: Optional[int] = None


class ScenarioIn(BaseModel):
    scenario: str
    camera_id: Optional[str] = None


class DetectionIn(BaseModel):
    cls: str = Field(max_length=40)
    conf: float = Field(ge=0, le=1)
    in_seat: bool = False
    in_table: bool = False
    seat_overlap: float = Field(default=0, ge=0, le=1)
    table_overlap: float = Field(default=0, ge=0, le=1)
    bbox: Optional[List[float]] = None


class SeatObsIn(BaseModel):
    seat_id: str
    event_id: str = Field(min_length=6, max_length=80)
    detections: List[DetectionIn] = []


class IngestIn(BaseModel):
    camera_id: str
    frame_id: str = Field(max_length=80)
    observed_at_utc: str
    frame_quality: str
    model_version: Optional[str] = Field(default=None, max_length=120)
    seats: List[SeatObsIn]


# ------------------------------------------------------------------ app factory


def create_app(settings: Optional[AppSettings] = None, cfg: Optional[EngineConfig] = None, clock: Optional[Clock] = None) -> FastAPI:
    settings = settings or AppSettings.from_env()
    cfg = cfg or EngineConfig.from_env()
    clock = clock or Clock()
    db = Database(settings.db_path)

    with db.read() as conn:
        n_seats = row(conn.execute("SELECT COUNT(*) AS n FROM seats"))["n"]
    if n_seats == 0 and settings.seed_if_empty:
        seed(db)
        if settings.mode == "demo":
            svc.start_scenario(db, clock.now(), "NORMAL", "system-startup")

    # session-token secret (local, random, persisted in the demo DB)
    with db.write() as conn:
        sec = row(conn.execute("SELECT value FROM settings WHERE key='session_secret'"))
        if not sec:
            conn.execute("INSERT INTO settings(key,value) VALUES ('session_secret', ?)", (secrets.token_hex(32),))
    with db.read() as conn:
        session_secret = row(conn.execute("SELECT value FROM settings WHERE key='session_secret'"))["value"].encode()

    def compute_state() -> dict:
        now = clock.now()
        seats = svc.seat_views(db, now, cfg)
        return {"server_time_utc": iso(now), "seats": seats, "meta": meta(now, seats)}

    hub = Hub(compute_state)

    def meta(now: datetime, seats: Optional[list] = None) -> dict:
        seats = seats if seats is not None else svc.seat_views(db, now, cfg)
        with db.read() as conn:
            run = svc.active_run(conn)
            pending = row(conn.execute("SELECT COUNT(*) AS n FROM seat_reports WHERE review_status='pending'"))["n"]
            recent = rows(conn.execute("SELECT * FROM seat_reports WHERE review_status!='pending' ORDER BY reviewed_at_utc DESC LIMIT 20"))
        for r in recent:
            r["reason_th"] = svc.REPORT_REASONS.get(r["reason"], r["reason"])
        cams = [{k: d[k] for k in ("camera_id", "label_th", "zone_id", "source_mode", "status")} for d in svc.device_views(db, now, cfg)]
        counts: dict = {}
        for v in seats:
            key = "stale" if v["display_tone"] == "stale" else v["display_state"]
            counts[key] = counts.get(key, 0) + 1
        return {
            "mode": settings.mode,
            "simulation_active": run is not None,
            "simulation_banner": SIMULATION_BANNER if run is not None else None,
            "scenario": None if not run else {"run_id": run["id"], "name": run["scenario"], "base": run["base_scenario"],
                                              "started_at_utc": run["started_at_utc"], "cameras": run["cameras"],
                                              "description_th": sc.SCENARIO_INFO_TH.get(run["scenario"])},
            "cameras": cams,
            "pending_reports": pending,
            "counts": counts,
            "recommendable": sum(1 for v in seats if v["is_recommendable"]),
            "total_seats": len(seats),
            "recent_resolved_reports": [svc.public_report(r) for r in recent],
            "freshness_ttl_s": cfg.freshness_ttl_s,
        }

    async def ticker():
        last_prune = time.monotonic()
        while True:
            await asyncio.sleep(settings.tick_s)
            try:
                if settings.mode == "demo":
                    await asyncio.to_thread(svc.emit_scenario_tick, db, cfg, clock.now())
                await asyncio.to_thread(svc.expire_overrides, db, clock.now())
                if time.monotonic() - last_prune > 300:
                    await asyncio.to_thread(prune_observations)
                    last_prune = time.monotonic()
                hub.trigger()
            except Exception:
                log.exception("ticker failed")

    def prune_observations():
        cutoff = iso(clock.now() - timedelta(hours=2))
        with db.write() as conn:
            conn.execute("DELETE FROM seat_observations WHERE source='scenario' AND observed_at_utc < ?", (cutoff,))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        hub.bind_loop(asyncio.get_running_loop())
        tasks = []
        if settings.start_background:
            tasks.append(asyncio.create_task(ticker()))
            tasks.append(asyncio.create_task(hub.run(1.0)))
        log.info("Smart Library NEXT API started mode=%s db=%s", settings.mode, settings.db_path)
        yield
        for t in tasks:
            t.cancel()

    app = FastAPI(title="Smart Library NEXT V2 (local demo)", version="0.2.0", lifespan=lifespan)
    app.state.db = db
    app.state.cfg = cfg
    app.state.clock = clock
    app.state.hub = hub
    app.state.settings = settings

    @app.exception_handler(svc.ServiceError)
    async def service_error(_req: Request, exc: svc.ServiceError):
        return JSONResponse(status_code=exc.status, content={"error": exc.code, "message_th": exc.message_th})

    @app.exception_handler(HTTPException)
    async def http_error(_req: Request, exc: HTTPException):
        content = exc.detail if isinstance(exc.detail, dict) else {"error": str(exc.detail)}
        return JSONResponse(status_code=exc.status_code, content=content)

    # ------------------------------------------------------------ auth helpers

    def require_staff(x_staff_token: Optional[str] = Header(default=None)) -> str:
        if not x_staff_token or not hmac.compare_digest(x_staff_token, settings.staff_token):
            with db.write() as conn:
                svc.log_event(conn, clock.now(), "security", "ปฏิเสธคำขอเจ้าหน้าที่ที่ไม่มีสิทธิ์ (401)", "api")
            raise HTTPException(status_code=401, detail={"error": "STAFF_AUTH_REQUIRED", "message_th": "ต้องเข้าสู่ระบบเจ้าหน้าที่ (demo gate)"})
        return "staff-demo"

    def require_demo_mode():
        if settings.mode != "demo":
            raise HTTPException(status_code=404, detail="Not Found")

    def sign_session(sid: str, exp: int) -> str:
        return hmac.new(session_secret, f"{sid}.{exp}".encode(), hashlib.sha256).hexdigest()[:24]

    def require_session(x_session_token: Optional[str] = Header(default=None)) -> str:
        try:
            sid, exp_s, sig = (x_session_token or "").split(".")
            exp = int(exp_s)
        except ValueError:
            raise HTTPException(status_code=401, detail={"error": "SESSION_REQUIRED", "message_th": "ไม่พบ session ชั่วคราว กรุณาโหลดหน้าใหม่"})
        if not hmac.compare_digest(sig, sign_session(sid, exp)) or exp < int(clock.now().timestamp()):
            raise HTTPException(status_code=401, detail={"error": "SESSION_INVALID", "message_th": "session หมดอายุ กรุณาโหลดหน้าใหม่"})
        return sid

    def after_mutation():
        hub.trigger()

    # ------------------------------------------------------------ public read API

    @app.get("/api/health")
    def health():
        now = clock.now()
        seats = svc.seat_views(db, now, cfg)
        devs = svc.device_views(db, now, cfg)
        with db.read() as conn:
            run = svc.active_run(conn)
            cv_obs = row(conn.execute("SELECT COUNT(*) AS n, MAX(observed_at_utc) AS last FROM seat_observations WHERE source='cv'"))
        fresh = [v for v in seats if not v["is_stale"]]
        newest = max((v["observed_at_utc"] for v in seats if v["observed_at_utc"]), default=None)
        cams_ok = all(d["status"] == "healthy" for d in devs if d["source_mode"] == "scenario")
        return {
            "status": "ok",
            "server_time_utc": iso(now),
            "mode": settings.mode,
            "active_sources": (["scenario"] if run else []) + (["cv"] if cv_obs["n"] else []),
            "simulation_active": run is not None,
            "simulation_banner": SIMULATION_BANNER if run else None,
            "scenario": None if not run else {"name": run["scenario"], "base": run["base_scenario"], "started_at_utc": run["started_at_utc"],
                                              "cameras": run["cameras"]},
            "cameras": [{k: d[k] for k in ("camera_id", "label_th", "source_mode", "status", "last_seen_utc", "last_seen_age_s", "last_quality", "detail")} for d in devs],
            "readiness": "ready" if (fresh and cams_ok) else "degraded",
            "data_freshness": {"fresh_seats": len(fresh), "stale_seats": len(seats) - len(fresh), "newest_observation_utc": newest,
                               "ttl_s": cfg.freshness_ttl_s},
            "real_cv": {"observations": cv_obs["n"], "last_observation_utc": cv_obs["last"],
                        "note": "CV runs out-of-process (cv/run_cv.py) and pushes via /api/ingest/observations; the API itself never fabricates detections."},
            "engine_config": cfg.public_dict(),
        }

    @app.get("/api/zones")
    def zones():
        now = clock.now()
        seats = svc.seat_views(db, now, cfg)
        with db.read() as conn:
            zs = rows(conn.execute("SELECT * FROM zones WHERE is_public=1 ORDER BY zone_id"))
        for z in zs:
            mine = [v for v in seats if v["zone_id"] == z["zone_id"]]
            z["seat_count"] = len(mine)
            z["recommendable"] = sum(1 for v in mine if v["is_recommendable"])
            z["counts"] = {}
            for v in mine:
                key = "stale" if v["display_tone"] == "stale" else v["display_state"]
                z["counts"][key] = z["counts"].get(key, 0) + 1
        return {"server_time_utc": iso(now), "zones": zs}

    @app.get("/api/layout")
    def layout():
        with db.read() as conn:
            return {
                "zones": rows(conn.execute("SELECT * FROM zones WHERE is_public=1 ORDER BY zone_id")),
                "waypoints": rows(conn.execute("SELECT * FROM waypoints")),
                "edges": rows(conn.execute("SELECT * FROM waypoint_edges")),
                "adjacency": rows(conn.execute("SELECT * FROM seat_adjacency")),
                "seat_types_th": SEAT_TYPE_TH,
                "note_th": "ผังสาธิต (illustrative) ไม่ใช่ผังห้องสมุดจริง ข้อมูลปลั๊ก/โซนเงียบ/หน้าต่าง/ความติดกันเป็นข้อมูลสมมติ",
            }

    @app.get("/api/seats")
    def seats_list():
        now = clock.now()
        seats = svc.seat_views(db, now, cfg)
        return {"server_time_utc": iso(now), "seats": seats, "meta": meta(now, seats)}

    @app.get("/api/seats/{seat_id}")
    def seat_detail(seat_id: str):
        now = clock.now()
        for v in svc.seat_views(db, now, cfg):
            if v["seat_id"] == seat_id:
                with db.read() as conn:
                    hist = rows(conn.execute(
                        "SELECT observed_at_utc, raw_candidate, committed_state, evidence_codes, frame_quality, source, applied FROM seat_observations"
                        " WHERE seat_id=? ORDER BY id DESC LIMIT 8", (seat_id,)))
                for h in hist:
                    h["evidence_codes"] = jload(h["evidence_codes"])
                return {"server_time_utc": iso(now), "seat": v, "recent_observations": hist}
        raise HTTPException(404, detail={"error": "SEAT_NOT_FOUND", "message_th": f"ไม่พบที่นั่ง {seat_id}"})

    @app.get("/api/recommendations")
    def recommendations(
        quiet: bool = False, power: bool = False, window: Optional[str] = Query(default=None, pattern="^(must|prefer)$"),
        seat_type: Optional[str] = None, zone: Optional[str] = None, group_size: int = Query(default=1, ge=1, le=8),
        limit: int = Query(default=5, ge=1, le=24),
    ):
        if group_size > 2:
            raise HTTPException(422, detail={"error": "GROUP_SIZE_NOT_SUPPORTED",
                                             "message_th": "GroupFit ตอนนี้รองรับ 2 คน (กลุ่ม >2 คนเป็นงานอนาคต ยังไม่ทำ)"})
        if seat_type and seat_type not in SEAT_TYPE_TH:
            raise HTTPException(422, detail={"error": "BAD_SEAT_TYPE", "message_th": "ประเภทที่นั่งไม่ถูกต้อง"})
        now = clock.now()
        views = svc.seat_views(db, now, cfg)
        graph = Graph.load(db)
        with db.read() as conn:
            adjacency = rows(conn.execute("SELECT * FROM seat_adjacency"))
        f = Filters(quiet=quiet, power=power, window_must=window == "must", window_prefer=window == "prefer",
                    seat_type=seat_type, zone=zone, group_size=group_size, limit=limit)
        out = recommend(views, graph, f, adjacency)
        out["server_time_utc"] = iso(now)
        out["source_note_th"] = "ข้อมูลจากสถานการณ์จำลอง (SIMULATION)" if any(v["source"] == "scenario" for v in views) else None
        return out

    @app.get("/api/route")
    def route(to: str, from_: str = Query(default="ENTRANCE", alias="from")):
        g = Graph.load(db)
        r = g.route_to_seat(from_, to)
        if not r:
            raise HTTPException(404, detail={"error": "NO_ROUTE", "message_th": f"ไม่พบเส้นทางจาก {from_} ไป {to}"})
        return r

    @app.get("/api/stats")
    def stats():
        now = clock.now()
        seats = svc.seat_views(db, now, cfg)
        with db.read() as conn:
            run = svc.active_run(conn)
            rep = rows(conn.execute("SELECT review_status, COUNT(*) AS n FROM seat_reports GROUP BY review_status"))
            res_events = rows(conn.execute("SELECT payload FROM system_events WHERE category='report_resolved'"))
            cv = row(conn.execute("SELECT COUNT(*) AS n, COUNT(DISTINCT seat_id) AS seats, COUNT(DISTINCT observation_group_id) AS frames,"
                                  " MAX(observed_at_utc) AS last FROM seat_observations WHERE source='cv'"))
            cv_models = [r["model_version"] for r in rows(conn.execute("SELECT DISTINCT model_version FROM seat_observations WHERE source='cv'"))]
            scn_obs = row(conn.execute("SELECT COUNT(*) AS n FROM seat_observations WHERE source='scenario'"))["n"]
        sim = None
        if run:
            shown_avail = [v for v in seats if v["display_state"] == "available" and v["display_tone"] == "available"]
            truth = run["truth"]
            wrong = [v["seat_id"] for v in shown_avail if truth.get(v["seat_id"], {}).get("truth") != "available"]
            rec = [v for v in seats if v["is_recommendable"]]
            rec_wrong = [v["seat_id"] for v in rec if truth.get(v["seat_id"], {}).get("truth") != "available"]
            sim = {
                "label": "SIMULATED — ground truth is authored by the developer for the scenario; NOT a real accuracy measurement",
                "scenario": run["scenario"],
                "seats": len(seats),
                "shown_available": len(shown_avail),
                "shown_available_but_truth_not_available": wrong,
                "simulated_false_available_rate": round(len(wrong) / len(shown_avail), 3) if shown_avail else None,
                "recommendable": len(rec),
                "recommendable_but_truth_not_available": rec_wrong,
                "unknown_or_stale": sum(1 for v in seats if v["display_state"] == "unknown" or v["display_tone"] == "stale"),
                "scenario_observations_stored": scn_obs,
            }
        latencies = [jload(e["payload"]).get("resolution_latency_s") for e in res_events if e["payload"]]
        latencies = sorted(x for x in latencies if x is not None)
        return {
            "server_time_utc": iso(now),
            "simulation": sim,
            "real_cv": {"label": "REAL CV observations ingested via /api/ingest/observations (source='cv')",
                        "observations": cv["n"], "seats": cv["seats"], "frames": cv["frames"], "last_observation_utc": cv["last"],
                        "model_versions": [m for m in cv_models if m],
                        "accuracy": None,
                        "accuracy_note": "ไม่มีชุดข้อมูล ground truth ที่ติดป้ายโดยมนุษย์ จึงไม่คำนวณ accuracy / False Available ของ CV จริง"},
            "seatcheck": {"by_status": {r["review_status"]: r["n"] for r in rep},
                          "resolution_latency_s": {"n": len(latencies), "median": latencies[len(latencies) // 2] if latencies else None},
                          "note": "นับจากข้อมูลในฐานข้อมูลสาธิตเครื่องนี้ (รวมรายงานจำลองที่ติดป้าย is_simulated)"},
        }

    @app.get("/api/cv/status")
    def cv_status():
        p = Path(settings.cv_evidence_dir) / "latest_run.json"
        if not p.exists():
            return {"status": "NOT_RUN", "message_th": "ยังไม่มีผลการรัน CV จริงในเครื่องนี้"}
        data = json.loads(p.read_text(encoding="utf-8"))
        return data

    @app.get("/api/cv/annotated/{name}")
    def cv_image(name: str):
        if "/" in name or "\\" in name or ".." in name or not name.endswith(".jpg"):
            raise HTTPException(404)
        p = Path(settings.cv_evidence_dir) / name
        if not p.exists():
            raise HTTPException(404)
        return FileResponse(p)

    # ------------------------------------------------------------ student SeatCheck

    @app.get("/api/session")
    def new_session():
        sid = secrets.token_hex(8)
        exp = int((clock.now() + timedelta(hours=8)).timestamp())
        return {"session_token": f"{sid}.{exp}.{sign_session(sid, exp)}", "expires_at_utc": iso(datetime.fromtimestamp(exp, tz=clock.now().tzinfo)),
                "note_th": "session ชั่วคราวแบบไม่ระบุตัวตน ใช้จำกัดอัตราการรายงานเท่านั้น"}

    @app.post("/api/seat-reports", status_code=201)
    def create_report(body: ReportIn, sid: str = Depends(require_session)):
        r = svc.create_report(db, clock.now(), body.seat_id, body.reason, sid, body.client_report_id)
        after_mutation()
        return svc.public_report(r)

    @app.get("/api/seat-reports/mine")
    def my_reports(sid: str = Depends(require_session)):
        with db.read() as conn:
            rs = rows(conn.execute("SELECT * FROM seat_reports WHERE pseudo_session_id=? ORDER BY id DESC", (sid,)))
        for r in rs:
            r["reason_th"] = svc.REPORT_REASONS.get(r["reason"], r["reason"])
        return {"reports": [svc.public_report(r) for r in rs]}

    # ------------------------------------------------------------ staff (demo gate)

    @app.get("/api/admin/check")
    def admin_check(actor: str = Depends(require_staff)):
        return {"ok": True, "actor": actor, "note_th": "demo gate เท่านั้น ไม่ใช่ระบบยืนยันตัวตนสำหรับใช้งานจริง"}

    @app.get("/api/admin/seat-reports")
    def admin_reports(status: str = "pending", actor: str = Depends(require_staff)):
        return {"reports": svc.list_reports(db, status)}

    @app.post("/api/admin/seat-reports/{report_id}/resolve")
    def admin_resolve(report_id: int, body: ResolveIn, actor: str = Depends(require_staff)):
        r = svc.resolve_report(db, clock.now(), report_id, body.decision, body.reason, actor, body.override_state, body.override_minutes)
        after_mutation()
        return r

    @app.post("/api/admin/seats/{seat_id}/override")
    def admin_override(seat_id: str, body: OverrideIn, actor: str = Depends(require_staff)):
        r = svc.set_override(db, clock.now(), seat_id, body.state, body.reason, actor, body.expires_in_minutes)
        after_mutation()
        return r

    @app.delete("/api/admin/seats/{seat_id}/override")
    def admin_clear_override(seat_id: str, reason: str = "ตรวจแล้วใช้งานได้ตามปกติ", actor: str = Depends(require_staff)):
        r = svc.clear_override(db, clock.now(), seat_id, actor, reason)
        after_mutation()
        return r

    @app.get("/api/admin/events")
    def admin_events(limit: int = Query(default=100, ge=1, le=500), category: Optional[str] = None, actor: str = Depends(require_staff)):
        with db.read() as conn:
            if category:
                ev = rows(conn.execute("SELECT * FROM system_events WHERE category=? ORDER BY id DESC LIMIT ?", (category, limit)))
            else:
                ev = rows(conn.execute("SELECT * FROM system_events ORDER BY id DESC LIMIT ?", (limit,)))
        for e in ev:
            e["payload"] = jload(e["payload"])
        return {"events": ev}

    @app.get("/api/admin/devices")
    def admin_devices(actor: str = Depends(require_staff)):
        return {"devices": svc.device_views(db, clock.now(), cfg)}

    # ------------------------------------------------------------ demo / scenario lab (demo mode only)

    @app.get("/api/demo/scenarios", dependencies=[Depends(require_demo_mode)])
    def demo_scenarios():
        with db.read() as conn:
            run = svc.active_run(conn)
            history = rows(conn.execute("SELECT id, scenario, base_scenario, started_at_utc, ended_at_utc, frames_emitted FROM scenario_runs ORDER BY id DESC LIMIT 15"))
        return {"scenarios": [{"name": n, "description_th": sc.SCENARIO_INFO_TH[n]} for n in sc.SCENARIOS],
                "cameras": list(sc.SCENARIO_CAMERAS) + ["ALL"], "active": run, "history": history,
                "banner": SIMULATION_BANNER}

    @app.post("/api/demo/scenario", dependencies=[Depends(require_demo_mode)])
    def demo_scenario(body: ScenarioIn, actor: str = Depends(require_staff)):
        r = svc.start_scenario(db, clock.now(), body.scenario, actor, body.camera_id)
        after_mutation()
        return {**r, "banner": SIMULATION_BANNER}

    @app.post("/api/demo/reset", dependencies=[Depends(require_demo_mode)])
    def demo_reset(actor: str = Depends(require_staff)):
        seed(db)
        svc.start_scenario(db, clock.now(), "NORMAL", actor)
        after_mutation()
        return {"ok": True, "message_th": "รีเซ็ตฐานข้อมูลสาธิตและเริ่ม NORMAL ใหม่"}

    # ------------------------------------------------------------ real CV ingestion (device token)

    @app.post("/api/ingest/observations")
    def ingest(body: IngestIn, x_device_token: Optional[str] = Header(default=None)):
        if not x_device_token or not hmac.compare_digest(x_device_token, settings.device_token):
            raise HTTPException(401, detail={"error": "DEVICE_AUTH_REQUIRED"})
        if body.frame_quality not in FRAME_QUALITIES:
            raise HTTPException(422, detail={"error": "BAD_FRAME_QUALITY"})
        now = clock.now()
        observed = parse_iso(body.observed_at_utc)
        results = []
        with db.write() as conn:
            dev = row(conn.execute("SELECT source_mode FROM devices WHERE camera_id=?", (body.camera_id,)))
            if not dev or dev["source_mode"] != "cv":
                raise svc.ServiceError(422, "NOT_A_CV_DEVICE", "อุปกรณ์นี้ไม่ได้ลงทะเบียนเป็นแหล่ง CV จริง")
            svc.touch_device(conn, now, body.camera_id, "healthy" if body.frame_quality == "ok" else "degraded", body.frame_quality,
                             f"REAL CV · {body.model_version or 'unknown model'}")
            for s in body.seats:
                r = svc.ingest_observation(
                    conn, cfg, now, event_id=s.event_id, seat_id=s.seat_id, camera_id=body.camera_id, source="cv",
                    observed_at=observed, frame_quality=body.frame_quality,
                    detections=[Detection.from_dict(d.model_dump()) for d in s.detections],
                    model_version=body.model_version, observation_group_id=body.frame_id,
                )
                results.append(r.__dict__)
        after_mutation()
        return {"results": results}

    @app.get("/api/cv/lab-seats")
    def cv_lab_seats():
        now = clock.now()
        views = [v for v in svc.seat_views(db, now, cfg, include_lab=True) if v["zone_id"] == "LAB"]
        return {"server_time_utc": iso(now), "seats": views}

    # ------------------------------------------------------------ websocket

    @app.websocket("/ws/seats")
    async def ws_seats(ws: WebSocket):
        await hub.connect(ws)
        try:
            while True:
                msg = await ws.receive_text()
                if msg == "ping":
                    await ws.send_json({"type": "pong", "server_time_utc": iso(clock.now())})
        except WebSocketDisconnect:
            pass
        finally:
            hub.disconnect(ws)

    # ------------------------------------------------------------ built frontend (single-port launch)

    dist = Path(settings.web_dist)
    if (dist / "index.html").exists():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        def spa(full_path: str):
            if full_path.startswith(("api/", "ws/")):
                raise HTTPException(404)
            f = dist / full_path
            if full_path and f.is_file() and dist in f.resolve().parents:
                return FileResponse(f)
            # BUG-012: never let a browser keep an old index.html (it would load an old bundle after a rebuild)
            return FileResponse(dist / "index.html", headers={"Cache-Control": "no-cache, must-revalidate"})

    return app


app = None  # created lazily by uvicorn factory below


def get_app() -> FastAPI:
    return create_app()
