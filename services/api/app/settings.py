"""Local-only application settings (no secrets required, no cloud keys)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # project root (SmartLibrary_NEXT_V2_Ready)


@dataclass
class AppSettings:
    db_path: str = str(ROOT / "services" / "api" / "data" / "smartlibrary_demo.db")
    # 'demo' enables the Scenario Lab endpoints; 'production' disables /api/demo/* entirely.
    mode: str = "demo"
    # Demo gate only - NOT production authentication. Override with SL_STAFF_TOKEN.
    staff_token: str = "staff-demo-2569"
    # Token the local CV runner uses to push real observations. Override with SL_DEVICE_TOKEN.
    device_token: str = "cv-device-demo-2569"
    tick_s: float = 2.0  # simulated capture interval (proposal: 1-2 s)
    start_background: bool = True
    seed_if_empty: bool = True
    web_dist: str = str(ROOT / "apps" / "web" / "dist")
    cv_evidence_dir: str = str(ROOT / "evidence" / "cv")

    @staticmethod
    def from_env() -> "AppSettings":
        s = AppSettings()
        s.db_path = os.environ.get("SL_DB_PATH", s.db_path)
        s.mode = os.environ.get("SL_MODE", s.mode)
        s.staff_token = os.environ.get("SL_STAFF_TOKEN", s.staff_token)
        s.device_token = os.environ.get("SL_DEVICE_TOKEN", s.device_token)
        s.tick_s = float(os.environ.get("SL_TICK_S", s.tick_s))
        return s
