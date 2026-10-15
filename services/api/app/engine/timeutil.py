from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional

UTC = timezone.utc


def utcnow() -> datetime:
    return datetime.now(UTC)


def iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_iso(s: str) -> datetime:
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def age_seconds(now: datetime, then_iso: Optional[str]) -> Optional[float]:
    """Elapsed seconds, clamped at 0 so clock skew never yields a negative age."""
    if not then_iso:
        return None
    return max(0.0, (now - parse_iso(then_iso)).total_seconds())


class Clock:
    """Injectable clock so tests can advance time deterministically."""

    def __init__(self, fn: Optional[Callable[[], datetime]] = None):
        self._fn = fn or utcnow
        self._offset = 0.0

    def now(self) -> datetime:
        from datetime import timedelta

        return self._fn() + timedelta(seconds=self._offset)

    def advance(self, seconds: float) -> None:
        self._offset += seconds
