"""ROI geometry used by the real CV runner (pure python, no OpenCV needed)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cv"))

from roi import anchor_point, box_overlap_fraction, point_in_polygon, relate_detection  # noqa: E402

SQUARE = [(0, 0), (100, 0), (100, 100), (0, 100)]


def test_point_in_polygon():
    assert point_in_polygon((50, 50), SQUARE)
    assert not point_in_polygon((150, 50), SQUARE)


def test_overlap_fraction():
    assert box_overlap_fraction([0, 0, 100, 100], SQUARE) == 1.0
    assert abs(box_overlap_fraction([50, 0, 150, 100], SQUARE) - 0.5) < 1e-9
    assert box_overlap_fraction([200, 200, 300, 300], SQUARE) == 0.0


def test_person_anchor_is_hip_not_centre():
    x, y = anchor_point("person", [0, 0, 100, 200])
    assert (x, y) == (50, 130)
    assert anchor_point("backpack", [0, 0, 100, 200]) == (50, 100)


def test_walk_through_box_crossing_table_only():
    seat = [(0, 100), (100, 100), (100, 200), (0, 200)]
    table = [(0, 0), (100, 0), (100, 90), (0, 90)]
    # person standing in front of the table: hip point (150, 130) outside the seat polygon
    rel = relate_detection("person", 0.9, [100, 0, 200, 200], seat, table)
    assert rel["in_seat"] is False and rel["seat_overlap"] == 0.0
