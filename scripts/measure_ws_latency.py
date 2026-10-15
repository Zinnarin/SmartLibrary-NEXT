"""Measure staff-action -> WebSocket delta latency against the RUNNING local server.

For N trials it toggles a Maintenance override on one seat via the REST API and measures the time until
a WebSocket delta containing that seat with the new display_state arrives. Loopback on one machine:
this is NOT network latency in a real library, and NOT camera-event latency.
  .venv\\Scripts\\python scripts\\measure_ws_latency.py --trials 20
"""
from __future__ import annotations

import argparse
import asyncio
import json
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
import websockets

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8000"
STAFF = {"X-Staff-Token": "staff-demo-2569"}


async def main(trials: int, seat: str):
    lat = []
    async with websockets.connect(BASE.replace("http", "ws") + "/ws/seats", max_size=2**24) as ws:
        snap = json.loads(await ws.recv())
        assert snap["type"] == "snapshot"
        async with httpx.AsyncClient(base_url=BASE, timeout=10) as c:
            for i in range(trials):
                target = "maintenance" if i % 2 == 0 else None
                t0 = time.perf_counter()
                if target:
                    r = await c.post(f"/api/admin/seats/{seat}/override", json={"state": "maintenance", "reason": "latency probe"}, headers=STAFF)
                else:
                    r = await c.delete(f"/api/admin/seats/{seat}/override", headers=STAFF)
                r.raise_for_status()
                while True:
                    msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
                    if msg.get("type") != "delta":
                        continue
                    hit = [s for s in msg.get("seats") or [] if s["seat_id"] == seat]
                    if hit and ((target and hit[0]["display_state"] == "maintenance") or (not target and hit[0]["manual_override"] is None)):
                        break
                lat.append((time.perf_counter() - t0) * 1000)
                await asyncio.sleep(0.3)
    res = {
        "measured_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "what": "REST staff override (POST/DELETE) -> WebSocket delta received by a client, loopback 127.0.0.1",
        "not_what": "not camera-event latency, not over Wi-Fi/LAN, not production hardware",
        "machine": f"{platform.system()} {platform.release()} / {platform.processor()}",
        "trials": trials,
        "ms": [round(x, 1) for x in lat],
        "median_ms": round(statistics.median(lat), 1),
        "p90_ms": round(sorted(lat)[int(0.9 * (len(lat) - 1))], 1),
        "max_ms": round(max(lat), 1),
    }
    out = ROOT / "evidence" / "ws_latency.json"
    out.write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--seat", default="B07")
    a = ap.parse_args()
    asyncio.run(main(a.trials, a.seat))
