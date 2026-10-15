"""Deterministic demo dataset: ILLUSTRATIVE floor (not a real or verified library plan).

All seat attributes (power, quiet, window, adjacency) are manually authored demo metadata
(``metadata_source='demo_assumed'``). Coordinates are SVG floor-map units, NOT camera ROI pixels
and NOT metres.
"""
from __future__ import annotations

import math

from .db import Database, jdump
from .engine.timeutil import iso, utcnow

FLOOR = "ชั้นสาธิต (Demo floor)"

ZONES = [
    # zone_id, name_th, name_en, description, x, y, w, h, public
    ("A", "โซนเงียบ A", "Quiet A", "โต๊ะเดี่ยว/โต๊ะคอมพิวเตอร์ ห้ามคุย", 30, 50, 320, 420, 1),
    ("B", "โซนกลุ่ม B", "Group B", "โต๊ะกลุ่ม คุยได้เบา ๆ", 370, 50, 300, 420, 1),
    ("C", "โซนริมหน้าต่าง C", "Window C", "โซฟาริมหน้าต่างและโต๊ะบาร์", 690, 50, 280, 420, 1),
    ("LAB", "CV Lab (ไม่แสดงบนผังนักศึกษา)", "CV Lab", "ROI สำหรับทดสอบ YOLO เท่านั้น", 0, 0, 0, 0, 0),
]

DEVICES = [
    ("CAM-A", "กล้องจำลองโซน A", "A", "scenario"),
    ("CAM-B", "กล้องจำลองโซน B", "B", "scenario"),
    ("CAM-C", "กล้องจำลองโซน C", "C", "scenario"),
    ("CV-LAB", "แหล่งภาพ CV จริง (เฉพาะภาพที่ได้รับอนุญาต)", "LAB", "cv"),
]

WAYPOINTS = [
    ("ENTRANCE", "ทางเข้าหลัก", "entrance", 510, 650),
    ("J_HALL", "โถงกลาง", "junction", 510, 540),
    ("J_A", "ทางเดินหน้าโซน A", "junction", 185, 540),
    ("J_BL", "ทางเดินหน้าโซน B", "junction", 410, 540),
    ("J_C", "ทางเดินหน้าโซน C", "junction", 850, 540),
    ("A_ROW2", "ช่องทางเดินโซน A แถว 2", "access", 185, 260),
    ("A_ROW1", "ช่องทางเดินโซน A แถว 1", "access", 185, 110),
    ("B_T2", "ข้างโต๊ะกลุ่ม 2", "access", 410, 335),
    ("B_T1", "ข้างโต๊ะกลุ่ม 1", "access", 410, 155),
    ("C_LOW", "ช่องทางเดินโซน C ล่าง", "access", 850, 310),
    ("C_HIGH", "ช่องทางเดินโซน C บน", "access", 850, 150),
]

EDGES = [
    ("ENTRANCE", "J_HALL"),
    ("J_HALL", "J_BL"),
    ("J_A", "J_BL"),
    ("J_C", "J_HALL"),
    ("A_ROW2", "J_A"),
    ("A_ROW1", "A_ROW2"),
    ("B_T2", "J_BL"),
    ("B_T1", "B_T2"),
    ("C_LOW", "J_C"),
    ("C_HIGH", "C_LOW"),
]

# seat_id, zone, type, power, window, quiet, x, y, camera, access waypoint
SEATS = [
    ("A01", "A", "single_desk", 1, 1, 1, 70, 110, "CAM-A", "A_ROW1"),
    ("A02", "A", "single_desk", 1, 1, 1, 135, 110, "CAM-A", "A_ROW1"),
    ("A03", "A", "single_desk", 0, 1, 1, 235, 110, "CAM-A", "A_ROW1"),
    ("A04", "A", "single_desk", 0, 1, 1, 300, 110, "CAM-A", "A_ROW1"),
    ("A05", "A", "computer_desk", 1, 0, 1, 70, 260, "CAM-A", "A_ROW2"),
    ("A06", "A", "computer_desk", 1, 0, 1, 135, 260, "CAM-A", "A_ROW2"),
    ("A07", "A", "single_desk", 1, 0, 1, 235, 260, "CAM-A", "A_ROW2"),
    ("A08", "A", "single_desk", 0, 0, 1, 300, 260, "CAM-A", "A_ROW2"),
    ("B01", "B", "group_table", 1, 0, 0, 480, 110, "CAM-B", "B_T1"),
    ("B02", "B", "group_table", 1, 0, 0, 560, 110, "CAM-B", "B_T1"),
    ("B03", "B", "group_table", 0, 0, 0, 480, 200, "CAM-B", "B_T1"),
    ("B04", "B", "group_table", 0, 0, 0, 560, 200, "CAM-B", "B_T1"),
    ("B05", "B", "group_table", 1, 0, 0, 480, 290, "CAM-B", "B_T2"),
    ("B06", "B", "group_table", 1, 0, 0, 560, 290, "CAM-B", "B_T2"),
    ("B07", "B", "group_table", 0, 0, 0, 480, 380, "CAM-B", "B_T2"),
    ("B08", "B", "group_table", 0, 0, 0, 560, 380, "CAM-B", "B_T2"),
    ("C01", "C", "sofa", 0, 1, 0, 920, 110, "CAM-C", "C_HIGH"),
    ("C02", "C", "sofa", 1, 1, 0, 920, 190, "CAM-C", "C_HIGH"),
    ("C03", "C", "sofa", 1, 1, 0, 920, 270, "CAM-C", "C_LOW"),
    ("C04", "C", "sofa", 0, 1, 0, 920, 350, "CAM-C", "C_LOW"),
    ("C05", "C", "single_desk", 1, 0, 0, 780, 110, "CAM-C", "C_HIGH"),
    ("C06", "C", "single_desk", 1, 0, 0, 780, 190, "CAM-C", "C_HIGH"),
    ("C07", "C", "single_desk", 0, 0, 0, 780, 270, "CAM-C", "C_LOW"),
    ("C08", "C", "single_desk", 0, 0, 0, 780, 350, "CAM-C", "C_LOW"),
]

# Manually authored physical adjacency (side-by-side seats). NOT derived from SVG distance.
ADJACENCY = [
    ("A01", "A02", "โต๊ะริมหน้าต่างคู่ซ้าย"),
    ("A03", "A04", "โต๊ะริมหน้าต่างคู่ขวา"),
    ("A05", "A06", "โต๊ะคอมพิวเตอร์คู่"),
    ("A07", "A08", "โต๊ะเดี่ยวคู่ติดกัน"),
    ("B01", "B02", "โต๊ะกลุ่ม 1 ฝั่งบน"),
    ("B03", "B04", "โต๊ะกลุ่ม 1 ฝั่งล่าง"),
    ("B05", "B06", "โต๊ะกลุ่ม 2 ฝั่งบน"),
    ("B07", "B08", "โต๊ะกลุ่ม 2 ฝั่งล่าง"),
    ("C01", "C02", "โซฟาตัวเดียวกัน"),
    ("C03", "C04", "โซฟาตัวเดียวกัน"),
    ("C05", "C06", "โต๊ะบาร์ติดกัน"),
    ("C07", "C08", "โต๊ะบาร์ติดกัน"),
]

# CV lab seats: only used by the real YOLO pipeline (never shown on the student map).
LAB_SEATS = [f"LAB{i}" for i in range(1, 5)]


def _dist(a, b) -> float:
    return round(math.hypot(a[0] - b[0], a[1] - b[1]), 1)


def seed(db: Database, *, reset: bool = True) -> None:
    now = iso(utcnow())
    wp_xy = {w[0]: (w[3], w[4]) for w in WAYPOINTS}
    with db.write() as conn:
        if reset:
            for t in (
                "seat_observations", "seat_current", "seat_reports", "manual_overrides", "system_events",
                "scenario_runs", "seat_adjacency", "seats", "waypoint_edges", "waypoints", "devices", "zones",
            ):
                conn.execute(f"DELETE FROM {t}")
        conn.executemany(
            "INSERT INTO zones(zone_id,name_th,name_en,description_th,x,y,w,h,is_public) VALUES (?,?,?,?,?,?,?,?,?)",
            ZONES,
        )
        conn.executemany(
            "INSERT INTO devices(camera_id,label_th,zone_id,source_mode,reported_status,updated_at_utc) VALUES (?,?,?,?, 'unknown', ?)",
            [(d[0], d[1], d[2], d[3], now) for d in DEVICES],
        )
        conn.executemany(
            "INSERT INTO waypoints(waypoint_id,label_th,kind,floor_x,floor_y) VALUES (?,?,?,?,?)", WAYPOINTS
        )
        conn.executemany(
            "INSERT INTO waypoint_edges(a,b,cost) VALUES (?,?,?)",
            [(min(a, b), max(a, b), _dist(wp_xy[a], wp_xy[b])) for a, b in EDGES],
        )
        for sid, zone, stype, power, window, quiet, x, y, cam, wp in SEATS:
            conn.execute(
                "INSERT INTO seats(seat_id,floor,zone_id,seat_type,has_power,near_window,quiet_zone,floor_x,floor_y,"
                "roi_id,camera_id,access_waypoint_id,access_cost,is_active,metadata_source) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,1,'demo_assumed')",
                (sid, FLOOR, zone, stype, power, window, quiet, x, y, None, cam, wp, _dist((x, y), wp_xy[wp])),
            )
        for sid in LAB_SEATS:
            conn.execute(
                "INSERT INTO seats(seat_id,floor,zone_id,seat_type,has_power,near_window,quiet_zone,floor_x,floor_y,"
                "roi_id,camera_id,access_waypoint_id,access_cost,is_active,metadata_source) VALUES (?,?,?,?,0,0,0,0,0,?,?,NULL,1,0,'cv_lab_roi')",
                (sid, "CV Lab", "LAB", "lab_roi", f"cv/roi_config.json#{sid}", "CV-LAB"),
            )
        conn.executemany(
            "INSERT INTO seat_adjacency(seat_a,seat_b,relation,note_th) VALUES (?,?, 'side_by_side', ?)",
            [(min(a, b), max(a, b), note) for a, b, note in ADJACENCY],
        )
        for sid in [s[0] for s in SEATS] + LAB_SEATS:
            conn.execute(
                "INSERT INTO seat_current(seat_id, physical_state, engine_state, revision) VALUES (?, 'unknown', ?, 0)",
                (sid, jdump({})),
            )
        conn.execute(
            "INSERT INTO system_events(created_at_utc,category,detail,source,payload) VALUES (?,?,?,?,?)",
            (now, "system", "ฐานข้อมูลสาธิตถูกสร้างใหม่ (seed)", "system", jdump({"seats": len(SEATS), "lab_seats": len(LAB_SEATS)})),
        )
