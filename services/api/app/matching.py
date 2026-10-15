"""StudyMatch (explainable single-seat ranking), GroupFit (adjacent pair) and Wayfinder (graph route).

The ranking score only orders already-eligible seats by stated preferences. It is NOT a probability
that the seat is free and is never shown as a percentage.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .db import Database, rows

SEAT_TYPE_TH = {
    "single_desk": "โต๊ะเดี่ยว",
    "computer_desk": "โต๊ะคอมพิวเตอร์",
    "group_table": "โต๊ะกลุ่ม",
    "sofa": "โซฟา",
}

MUST_LABEL_TH = {
    "quiet": "โซนเงียบ",
    "power": "มีปลั๊กไฟ",
    "window": "ริมหน้าต่าง",
    "seat_type": "ประเภทที่นั่ง",
    "zone": "โซน",
}


@dataclass
class Filters:
    quiet: bool = False
    power: bool = False
    window_must: bool = False
    window_prefer: bool = False
    seat_type: Optional[str] = None
    zone: Optional[str] = None
    group_size: int = 1
    limit: int = 5

    def active_musts(self) -> List[str]:
        out = []
        if self.quiet:
            out.append("quiet")
        if self.power:
            out.append("power")
        if self.window_must:
            out.append("window")
        if self.seat_type:
            out.append("seat_type")
        if self.zone:
            out.append("zone")
        return out


def _matches(v: dict, f: Filters, skip: Optional[str] = None) -> bool:
    if f.quiet and skip != "quiet" and not v["quiet_zone"]:
        return False
    if f.power and skip != "power" and not v["has_power"]:
        return False
    if f.window_must and skip != "window" and not v["near_window"]:
        return False
    if f.seat_type and skip != "seat_type" and v["seat_type"] != f.seat_type:
        return False
    if f.zone and skip != "zone" and v["zone_id"] != f.zone:
        return False
    return True


# ---------------------------------------------------------------- Wayfinder


class Graph:
    def __init__(self, waypoints: List[dict], edges: List[dict], seats: List[dict]):
        self.wp = {w["waypoint_id"]: w for w in waypoints}
        self.adj: Dict[str, List[Tuple[str, float]]] = {w: [] for w in self.wp}
        self.edges = set()
        for e in edges:
            self.adj[e["a"]].append((e["b"], e["cost"]))
            self.adj[e["b"]].append((e["a"], e["cost"]))
            self.edges.add((e["a"], e["b"]))
        self.seat_access = {s["seat_id"]: (s["access_waypoint_id"], s["access_cost"], s["floor_x"], s["floor_y"]) for s in seats}

    @staticmethod
    def load(db: Database) -> "Graph":
        with db.read() as conn:
            return Graph(
                rows(conn.execute("SELECT * FROM waypoints")),
                rows(conn.execute("SELECT * FROM waypoint_edges")),
                rows(conn.execute("SELECT seat_id, access_waypoint_id, access_cost, floor_x, floor_y FROM seats WHERE is_active=1")),
            )

    def has_edge(self, a: str, b: str) -> bool:
        return (min(a, b), max(a, b)) in self.edges

    def dijkstra(self, src: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
        dist = {src: 0.0}
        prev: Dict[str, Optional[str]] = {src: None}
        pq = [(0.0, src)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist.get(u, float("inf")):
                continue
            for v, c in self.adj[u]:
                nd = d + c
                if nd < dist.get(v, float("inf")):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        return dist, prev

    def route_to_seat(self, src: str, seat_id: str) -> Optional[dict]:
        if src not in self.wp or seat_id not in self.seat_access:
            return None
        access, access_cost, sx, sy = self.seat_access[seat_id]
        dist, prev = self.dijkstra(src)
        if access not in dist:
            return None
        path = []
        cur: Optional[str] = access
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        points = [{"id": p, "label_th": self.wp[p]["label_th"], "x": self.wp[p]["floor_x"], "y": self.wp[p]["floor_y"]} for p in path]
        points.append({"id": f"SEAT:{seat_id}", "label_th": f"ที่นั่ง {seat_id}", "x": sx, "y": sy})
        return {
            "from": src,
            "to": seat_id,
            "waypoints": path,
            "points": points,
            "edges": [[path[i], path[i + 1]] for i in range(len(path) - 1)] + [[access, f"SEAT:{seat_id}"]],
            "total_cost_units": round(dist[access] + access_cost, 1),
            "disclaimer_th": "เส้นทางสาธิตบนผังจำลองเท่านั้น (หน่วยผัง ไม่ใช่เมตร) ยังไม่ได้ตรวจสอบกับอาคารจริงหรือรับรองการเข้าถึงสำหรับวีลแชร์ ไม่ใช้ GPS/เซนเซอร์ระบุตำแหน่ง",
        }

    def walk_costs(self, src: str = "ENTRANCE") -> Dict[str, float]:
        dist, _ = self.dijkstra(src)
        return {sid: round(dist.get(a, float("inf")) + c, 1) for sid, (a, c, _x, _y) in self.seat_access.items()}


# ---------------------------------------------------------------- StudyMatch


def _explain(v: dict, f: Filters, walk: float, max_walk: float) -> Tuple[float, List[dict]]:
    reasons = []
    if f.quiet:
        reasons.append({"kind": "must", "text_th": "อยู่ในโซนเงียบ ✓"})
    if f.power:
        reasons.append({"kind": "must", "text_th": "มีปลั๊กไฟ ✓"})
    if f.window_must:
        reasons.append({"kind": "must", "text_th": "ริมหน้าต่าง ✓"})
    if f.seat_type:
        reasons.append({"kind": "must", "text_th": f"เป็น{SEAT_TYPE_TH.get(v['seat_type'], v['seat_type'])} ✓"})
    if f.zone:
        reasons.append({"kind": "must", "text_th": f"อยู่ในโซน {v['zone_id']} ✓"})
    age = v.get("age_s")
    reasons.append({"kind": "trust", "text_th": "สถานะ 'ว่าง' ผ่านการยืนยันหลายเฟรมต่อเนื่อง (temporal smoothing)"})
    cam = "กล้องจำลองปกติ (SIMULATION)" if v.get("source") == "scenario" else "กล้องปกติ"
    reasons.append({"kind": "trust", "text_th": f"ข้อมูลสด: อัปเดตล่าสุด {age:.0f} วินาทีที่แล้ว · {cam}" if age is not None else f"ข้อมูลสด · {cam}"})
    reasons.append({"kind": "trust", "text_th": "ไม่มีรายงาน SeatCheck ค้าง และไม่มีการปิดโดยเจ้าหน้าที่"})
    score = 0.0
    if f.window_prefer and v["near_window"]:
        score += 2.0
        reasons.append({"kind": "prefer", "text_th": "ใกล้หน้าต่าง (ตามที่เลือกว่าชอบ)"})
    if max_walk > 0:
        walk_bonus = 1.5 * (1 - walk / max_walk)
        score += walk_bonus
    reasons.append({"kind": "prefer", "text_th": f"ระยะเดินจากทางเข้า {walk:.0f} หน่วยผัง (เส้นทางสาธิต)"})
    return round(score, 3), reasons


def _excluded_summary(candidates: List[dict]) -> List[dict]:
    from .engine.trust import REASON_TH

    counts: Dict[str, List[str]] = {}
    for v in candidates:
        if v["is_recommendable"]:
            continue
        # report the most important reason only, to keep the summary readable
        primary = v["not_recommendable_reasons"][0]
        counts.setdefault(primary, []).append(v["seat_id"])
    return [{"reason": k, "text_th": REASON_TH.get(k, k), "seats": sorted(s)} for k, s in sorted(counts.items(), key=lambda kv: -len(kv[1]))]


def _relax_suggestions(views: List[dict], f: Filters, eligible_fn) -> List[dict]:
    out = []
    for m in f.active_musts():
        n = eligible_fn(m)
        if n > 0:
            out.append({"filter": m, "label_th": MUST_LABEL_TH[m], "would_match": n,
                        "text_th": f"ถ้าไม่บังคับ '{MUST_LABEL_TH[m]}' จะมี {n} ตัวเลือกที่ยืนยันได้ (ระบบไม่ผ่อนเงื่อนไขให้อัตโนมัติ)"})
    return out


def recommend(views: List[dict], graph: Graph, f: Filters, adjacency: List[dict]) -> dict:
    walks = graph.walk_costs("ENTRANCE")
    finite = [w for w in walks.values() if w != float("inf")]
    max_walk = max(finite) if finite else 0.0
    candidates = [v for v in views if _matches(v, f)]
    eligible = [v for v in candidates if v["is_recommendable"]]

    base = {
        "filters": {"quiet": f.quiet, "power": f.power, "window_must": f.window_must, "window_prefer": f.window_prefer,
                    "seat_type": f.seat_type, "zone": f.zone, "group_size": f.group_size},
        "hard_constraint_rules_th": [
            "สถานะต้องเป็น 'ว่าง' ที่ผ่านการยืนยันซ้ำ",
            "ข้อมูลต้องสด (ไม่เกิน TTL) และกล้องไม่ออฟไลน์/ไม่ด้อยคุณภาพ",
            "ไม่มี override ของเจ้าหน้าที่ และไม่มีรายงาน SeatCheck ค้างตรวจ",
            "ตรงทุกเงื่อนไข 'ต้องมี' ที่ผู้ใช้เลือก",
        ],
        "score_note_th": "คะแนนใช้เรียงลำดับตามความชอบเท่านั้น ไม่ใช่ความน่าจะเป็นว่าที่นั่งว่าง",
        "matching_candidates": len(candidates),
        "excluded": _excluded_summary(candidates),
        "availability_note_th": "สถานะอาจเปลี่ยนก่อนคุณเดินไปถึง หากพบว่าไม่ตรง กด SeatCheck",
    }

    if f.group_size == 1:
        results = []
        for v in eligible:
            score, reasons = _explain(v, f, walks.get(v["seat_id"], 0.0), max_walk)
            results.append({"seat_id": v["seat_id"], "zone_id": v["zone_id"], "seat_type": v["seat_type"],
                            "seat_type_th": SEAT_TYPE_TH.get(v["seat_type"], v["seat_type"]),
                            "rank_score": score, "walk_units": walks.get(v["seat_id"]), "reasons": reasons,
                            "observed_at_utc": v["observed_at_utc"]})
        results.sort(key=lambda r: (-r["rank_score"], r["walk_units"] or 0, r["seat_id"]))
        results = results[: f.limit]
        out = dict(base, mode="single", results=results)
        if not results:
            out["empty_message_th"] = "ไม่มีที่นั่งที่ยืนยันได้ตอนนี้ตามเงื่อนไขที่เลือก"
            out["relax_suggestions"] = _relax_suggestions(
                views, f, lambda m: sum(1 for v in views if _matches(v, f, skip=m) and v["is_recommendable"]))
        return out

    if f.group_size == 2:
        elig_ids = {v["seat_id"]: v for v in eligible}

        def pairs_for(ok_ids: Dict[str, dict]):
            ps = []
            for e in adjacency:
                a, b = e["seat_a"], e["seat_b"]
                if a in ok_ids and b in ok_ids:
                    ps.append(e)
            return ps

        pairs = []
        for e in pairs_for(elig_ids):
            a, b = elig_ids[e["seat_a"]], elig_ids[e["seat_b"]]
            sa, ra = _explain(a, f, walks.get(a["seat_id"], 0.0), max_walk)
            sb, _rb = _explain(b, f, walks.get(b["seat_id"], 0.0), max_walk)
            reasons = [{"kind": "group", "text_th": f"{a['seat_id']} และ {b['seat_id']} อยู่ติดกันตามผังที่บันทึกด้วยมือ ({e.get('note_th') or e['relation']})"},
                       {"kind": "trust", "text_th": "ทั้งสองที่นั่งผ่านเกณฑ์ความน่าเชื่อถือทุกข้อ"}] + [r for r in ra if r["kind"] == "must"]
            pairs.append({"seats": [a["seat_id"], b["seat_id"]], "relation": e["relation"], "note_th": e.get("note_th"),
                          "rank_score": round(sa + sb, 3),
                          "walk_units": max(walks.get(a["seat_id"], 0.0), walks.get(b["seat_id"], 0.0)), "reasons": reasons})
        pairs.sort(key=lambda p: (-p["rank_score"], p["walk_units"], p["seats"]))
        pairs = pairs[: f.limit]
        out = dict(base, mode="group", group_results=pairs, adjacency_source_th="ความติดกันมาจากตาราง seat_adjacency ที่บันทึกด้วยมือ (ไม่ได้เดาจากระยะบนผัง)")
        if not pairs:
            out["empty_message_th"] = "ไม่มีที่นั่ง 2 ที่ติดกันที่ยืนยันได้ตอนนี้ตามเงื่อนไขที่เลือก"

            def n_pairs(m):
                ok = {v["seat_id"]: v for v in views if _matches(v, f, skip=m) and v["is_recommendable"]}
                return len(pairs_for(ok))

            out["relax_suggestions"] = _relax_suggestions(views, f, n_pairs)
        return out

    raise ValueError("group_size")
