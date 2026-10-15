import sys
import warnings
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "api"))

warnings.filterwarnings("ignore", category=DeprecationWarning)

from app import services as svc  # noqa: E402
from app.engine.timeutil import Clock  # noqa: E402
from app.main import create_app  # noqa: E402
from app.settings import AppSettings  # noqa: E402

STAFF = {"X-Staff-Token": "staff-demo-2569"}


class Ctx:
    def __init__(self, app, client, clock):
        self.app, self.client, self.clock = app, client, clock
        self.db = app.state.db
        self.cfg = app.state.cfg

    def tick(self, n=1, dt=2.0):
        for _ in range(n):
            self.clock.advance(dt)
            svc.emit_scenario_tick(self.db, self.cfg, self.clock.now())

    def seats(self):
        return {v["seat_id"]: v for v in self.client.get("/api/seats").json()["seats"]}

    def session(self):
        return {"X-Session-Token": self.client.get("/api/session").json()["session_token"]}

    def scenario(self, name, camera_id=None):
        body = {"scenario": name}
        if camera_id:
            body["camera_id"] = camera_id
        r = self.client.post("/api/demo/scenario", json=body, headers=STAFF)
        assert r.status_code == 200, r.text
        return r.json()


def _make(tmp_path, mode="demo", background=False):
    from fastapi.testclient import TestClient

    s = AppSettings(db_path=str(tmp_path / "test.db"), mode=mode, start_background=background, tick_s=1000.0,
                    cv_evidence_dir=str(tmp_path / "cv"), web_dist=str(tmp_path / "nodist"))
    clock = Clock()
    app = create_app(s, clock=clock)
    return app, clock, TestClient


@pytest.fixture
def ctx(tmp_path):
    app, clock, TC = _make(tmp_path)
    c = TC(app)
    x = Ctx(app, c, clock)
    x.tick(5)  # warm-up: NORMAL scenario frames committed through the state engine
    return x


@pytest.fixture
def make_ctx(tmp_path):
    def factory(mode="demo", background=False):
        app, clock, TC = _make(tmp_path, mode=mode, background=background)
        return app, clock, TC

    return factory
