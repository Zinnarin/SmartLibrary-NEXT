"""Image-plane ROI geometry (pixel coordinates of ONE camera view).

These polygons are NOT floor-map SVG coordinates. Each test seat has a seating/torso polygon and a
tabletop/belongings polygon, calibrated by hand against a specific image.
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

Point = Tuple[float, float]


def polygon_area(poly: Sequence[Point]) -> float:
    a = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


def point_in_polygon(p: Point, poly: Sequence[Point]) -> bool:
    x, y = p
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def _clip(subject: List[Point], edge_fn, intersect_fn) -> List[Point]:
    out: List[Point] = []
    if not subject:
        return out
    prev = subject[-1]
    for cur in subject:
        if edge_fn(cur):
            if not edge_fn(prev):
                out.append(intersect_fn(prev, cur))
            out.append(cur)
        elif edge_fn(prev):
            out.append(intersect_fn(prev, cur))
        prev = cur
    return out


def clip_polygon_to_box(poly: Sequence[Point], box: Sequence[float]) -> List[Point]:
    """Sutherland-Hodgman clip of an arbitrary simple polygon by an axis-aligned box (x1,y1,x2,y2)."""
    x1, y1, x2, y2 = box
    pts = list(poly)

    def ix(a, b, x):
        t = (x - a[0]) / ((b[0] - a[0]) or 1e-12)
        return (x, a[1] + t * (b[1] - a[1]))

    def iy(a, b, y):
        t = (y - a[1]) / ((b[1] - a[1]) or 1e-12)
        return (a[0] + t * (b[0] - a[0]), y)

    pts = _clip(pts, lambda p: p[0] >= x1, lambda a, b: ix(a, b, x1))
    pts = _clip(pts, lambda p: p[0] <= x2, lambda a, b: ix(a, b, x2))
    pts = _clip(pts, lambda p: p[1] >= y1, lambda a, b: iy(a, b, y1))
    pts = _clip(pts, lambda p: p[1] <= y2, lambda a, b: iy(a, b, y2))
    return pts


def box_overlap_fraction(box: Sequence[float], poly: Sequence[Point]) -> float:
    """Fraction of the detection box area that lies inside the polygon."""
    bw = max(0.0, box[2] - box[0])
    bh = max(0.0, box[3] - box[1])
    if bw * bh <= 0:
        return 0.0
    inter = clip_polygon_to_box(poly, box)
    if len(inter) < 3:
        return 0.0
    return min(1.0, polygon_area(inter) / (bw * bh))


def anchor_point(cls: str, box: Sequence[float]) -> Point:
    """Person: estimated hip point (65% down the box); objects: box centre."""
    x1, y1, x2, y2 = box
    if cls == "person":
        return ((x1 + x2) / 2.0, y1 + 0.65 * (y2 - y1))
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def relate_detection(cls: str, conf: float, box: Sequence[float], seat_poly, table_poly) -> dict:
    a = anchor_point(cls, box)
    return {
        "cls": cls,
        "conf": float(conf),
        "in_seat": point_in_polygon(a, seat_poly),
        "in_table": point_in_polygon(a, table_poly),
        "seat_overlap": box_overlap_fraction(box, seat_poly),
        "table_overlap": box_overlap_fraction(box, table_poly),
        "bbox": [float(v) for v in box],
    }
