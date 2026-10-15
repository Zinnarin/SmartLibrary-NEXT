"""WebSocket hub: sends a snapshot on connect, then seat deltas and meta changes.

Time-varying fields (ages) are excluded from the change hash; clients compute ages from
``observed_at_utc`` and ``server_time_utc``. A 1 s sweep catches time-based transitions such as a
seat crossing the freshness TTL even when no new event arrives.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from typing import Callable, Dict, Optional, Set

from fastapi import WebSocket

log = logging.getLogger("smartlibrary.ws")

VOLATILE = ("age_s", "state_for_s", "belongings_for_s")


def _hash(v: dict) -> str:
    stable = {k: val for k, val in v.items() if k not in VOLATILE}
    return hashlib.sha1(json.dumps(stable, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


class Hub:
    def __init__(self, compute: Callable[[], dict]):
        self.compute = compute  # returns {"seats": [...], "meta": {...}, "server_time_utc": ...}
        self.clients: Set[WebSocket] = set()
        self._hashes: Dict[str, str] = {}
        self._meta_hash: Optional[str] = None
        self._event: Optional[asyncio.Event] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self.sent_messages = 0
        self._last_send = 0.0

    def bind_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._event = asyncio.Event()

    def trigger(self):
        """Thread-safe: request an immediate recompute + broadcast."""
        if self._loop and self._event:
            self._loop.call_soon_threadsafe(self._event.set)

    async def connect(self, ws: WebSocket):
        await ws.accept()
        state = await asyncio.to_thread(self.compute)
        await ws.send_json({"type": "snapshot", **state})
        self.clients.add(ws)

    def disconnect(self, ws: WebSocket):
        self.clients.discard(ws)

    async def run(self, interval_s: float = 1.0):
        assert self._event is not None
        while True:
            try:
                await asyncio.wait_for(self._event.wait(), timeout=interval_s)
            except asyncio.TimeoutError:
                pass
            self._event.clear()
            try:
                await self.broadcast_changes()
            except Exception:  # keep the hub alive; errors are logged
                log.exception("broadcast failed")

    async def broadcast_changes(self):
        state = await asyncio.to_thread(self.compute)
        changed = []
        for v in state["seats"]:
            h = _hash(v)
            if self._hashes.get(v["seat_id"]) != h:
                self._hashes[v["seat_id"]] = h
                changed.append(v)
        meta_h = hashlib.sha1(json.dumps(state["meta"], sort_keys=True, default=str).encode()).hexdigest()
        meta_changed = meta_h != self._meta_hash
        self._meta_hash = meta_h
        if not self.clients:
            return
        if not changed and not meta_changed:
            # keep-alive so clients can tell a quiet system from a dead socket
            if time.monotonic() - self._last_send > 5:
                await self.send_event({"type": "heartbeat", "server_time_utc": state["server_time_utc"]})
                self._last_send = time.monotonic()
            return
        msg = {"type": "delta", "server_time_utc": state["server_time_utc"], "seats": changed,
               "meta": state["meta"] if meta_changed else None}
        dead = []
        for ws in list(self.clients):
            try:
                await ws.send_json(msg)
                self.sent_messages += 1
                self._last_send = time.monotonic()
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def send_event(self, payload: dict):
        for ws in list(self.clients):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(ws)
