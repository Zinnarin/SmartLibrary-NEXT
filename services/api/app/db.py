"""SQLite persistence (stdlib sqlite3, explicit repeatable schema).

Deviation from spec note: the spec suggests SQLAlchemy; plain sqlite3 + an explicit schema was chosen
for transparent transactions (BEGIN IMMEDIATE) and zero extra dependencies. Logged in IMPLEMENTATION_REPORT.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS zones (
    zone_id TEXT PRIMARY KEY,
    name_th TEXT NOT NULL,
    name_en TEXT NOT NULL,
    description_th TEXT,
    x REAL, y REAL, w REAL, h REAL,
    is_public INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS waypoints (
    waypoint_id TEXT PRIMARY KEY,
    label_th TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('entrance','junction','access')),
    floor_x REAL NOT NULL,
    floor_y REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS waypoint_edges (
    a TEXT NOT NULL REFERENCES waypoints(waypoint_id),
    b TEXT NOT NULL REFERENCES waypoints(waypoint_id),
    cost REAL NOT NULL CHECK (cost > 0),
    PRIMARY KEY (a, b),
    CHECK (a < b)
);

CREATE TABLE IF NOT EXISTS devices (
    camera_id TEXT PRIMARY KEY,
    label_th TEXT NOT NULL,
    zone_id TEXT,
    source_mode TEXT NOT NULL CHECK (source_mode IN ('scenario','cv')),
    reported_status TEXT NOT NULL DEFAULT 'unknown',
    last_seen_utc TEXT,
    last_quality TEXT,
    detail TEXT,
    updated_at_utc TEXT
);

CREATE TABLE IF NOT EXISTS seats (
    seat_id TEXT PRIMARY KEY,
    floor TEXT NOT NULL,
    zone_id TEXT NOT NULL REFERENCES zones(zone_id),
    seat_type TEXT NOT NULL,
    has_power INTEGER NOT NULL,
    near_window INTEGER NOT NULL,
    quiet_zone INTEGER NOT NULL,
    floor_x REAL NOT NULL,
    floor_y REAL NOT NULL,
    roi_id TEXT,
    camera_id TEXT NOT NULL REFERENCES devices(camera_id),
    access_waypoint_id TEXT REFERENCES waypoints(waypoint_id),
    access_cost REAL NOT NULL DEFAULT 1,
    is_active INTEGER NOT NULL DEFAULT 1,
    metadata_source TEXT NOT NULL DEFAULT 'demo_assumed'
);

CREATE TABLE IF NOT EXISTS seat_adjacency (
    seat_a TEXT NOT NULL REFERENCES seats(seat_id),
    seat_b TEXT NOT NULL REFERENCES seats(seat_id),
    relation TEXT NOT NULL DEFAULT 'side_by_side',
    note_th TEXT,
    PRIMARY KEY (seat_a, seat_b),
    CHECK (seat_a < seat_b)
);

CREATE TABLE IF NOT EXISTS seat_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    seat_id TEXT NOT NULL REFERENCES seats(seat_id),
    observed_at_utc TEXT NOT NULL,
    ingested_at_utc TEXT NOT NULL,
    source TEXT NOT NULL CHECK (source IN ('scenario','cv')),
    camera_id TEXT,
    raw_candidate TEXT NOT NULL,
    committed_state TEXT NOT NULL,
    detector_confidence REAL,
    evidence_codes TEXT NOT NULL,
    detections TEXT,
    frame_quality TEXT NOT NULL,
    model_version TEXT,
    observation_group_id TEXT,
    applied INTEGER NOT NULL,
    apply_reason TEXT,
    scenario_run_id INTEGER
);
CREATE INDEX IF NOT EXISTS idx_obs_seat_time ON seat_observations(seat_id, observed_at_utc);
CREATE INDEX IF NOT EXISTS idx_obs_source ON seat_observations(source);

CREATE TABLE IF NOT EXISTS seat_current (
    seat_id TEXT PRIMARY KEY REFERENCES seats(seat_id),
    physical_state TEXT NOT NULL DEFAULT 'unknown',
    observed_at_utc TEXT,
    ingest_time_utc TEXT,
    source TEXT,
    quality_flag TEXT,
    user_report_pending INTEGER NOT NULL DEFAULT 0,
    manual_override_id INTEGER,
    engine_state TEXT,
    revision INTEGER NOT NULL DEFAULT 0,
    last_event_id TEXT
);

CREATE TABLE IF NOT EXISTS seat_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seat_id TEXT NOT NULL REFERENCES seats(seat_id),
    reason TEXT NOT NULL CHECK (reason IN ('reported_occupied','belongings_present','seat_inaccessible','other')),
    created_at_utc TEXT NOT NULL,
    pseudo_session_id TEXT NOT NULL,
    client_report_id TEXT UNIQUE,
    review_status TEXT NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending','accepted','rejected')),
    reviewed_at_utc TEXT,
    decision_reason TEXT,
    actor_id TEXT,
    is_simulated INTEGER NOT NULL DEFAULT 0,
    display_state_at_report TEXT,
    override_id INTEGER
);

CREATE TABLE IF NOT EXISTS manual_overrides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seat_id TEXT NOT NULL REFERENCES seats(seat_id),
    state TEXT NOT NULL CHECK (state IN ('unavailable','maintenance','unknown')),
    reason TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    cleared_at_utc TEXT,
    cleared_by TEXT,
    expires_at_utc TEXT,
    report_id INTEGER
);

CREATE TABLE IF NOT EXISTS system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at_utc TEXT NOT NULL,
    category TEXT NOT NULL,
    detail TEXT NOT NULL,
    source TEXT NOT NULL,
    seat_id TEXT,
    actor_id TEXT,
    payload TEXT
);

CREATE TABLE IF NOT EXISTS scenario_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario TEXT NOT NULL,
    base_scenario TEXT NOT NULL,
    started_at_utc TEXT NOT NULL,
    ended_at_utc TEXT,
    params TEXT NOT NULL,
    truth TEXT NOT NULL,
    cameras TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    frames_emitted INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


class Database:
    """Connection-per-operation with a process-wide write lock (SQLite single writer)."""

    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._write_lock = threading.RLock()
        conn = self._connect()
        try:
            conn.executescript(SCHEMA)
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10, check_same_thread=False, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=10000")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @contextmanager
    def read(self) -> Iterator[sqlite3.Connection]:
        conn = self._connect()
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def write(self) -> Iterator[sqlite3.Connection]:
        """Atomic transaction: commit on success, rollback on any exception."""
        with self._write_lock:
            conn = self._connect()
            try:
                conn.execute("BEGIN IMMEDIATE")
                yield conn
                conn.execute("COMMIT")
            except BaseException:
                conn.execute("ROLLBACK")
                raise
            finally:
                conn.close()


def rows(cur) -> list:
    return [dict(r) for r in cur.fetchall()]


def row(cur) -> Optional[dict]:
    r = cur.fetchone()
    return dict(r) if r else None


def jdump(v) -> str:
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"))


def jload(s):
    return json.loads(s) if s else None
