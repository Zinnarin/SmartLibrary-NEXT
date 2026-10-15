"""Build presentation/progress_update.pptx (editable 16:9, Thai) from REAL artefacts.

Numbers on the slides are read from evidence files produced by actual runs:
  evidence/pytest_junit.xml, evidence/playwright_results.json, evidence/cv/latest_run.json
Screenshots come from presentation/screenshots/ (captured by Playwright from the running UI).
Run:  .venv\\Scripts\\python scripts\\build_pptx.py
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "presentation" / "screenshots"
OUT = ROOT / "artifacts" / "pptx" / "progress_update_draft.pptx"  # frozen V2 decks are never the default
FONT = "Leelawadee UI"  # ships with Windows; renders Thai

NAVY = RGBColor(0x0F, 0x17, 0x2A)
SLATE = RGBColor(0x33, 0x41, 0x55)
MUTED = RGBColor(0x64, 0x74, 0x8B)
GREEN = RGBColor(0x15, 0x80, 0x3D)
LGREEN = RGBColor(0xDC, 0xFC, 0xE7)
AMBER = RGBColor(0xB4, 0x53, 0x09)
LAMBER = RGBColor(0xFE, 0xF3, 0xC7)
RED = RGBColor(0xB9, 0x1C, 0x1C)
LRED = RGBColor(0xFE, 0xE2, 0xE2)
BLUE = RGBColor(0x1D, 0x4E, 0xD8)
LBLUE = RGBColor(0xDB, 0xEA, 0xFE)
VIOLET = RGBColor(0x6D, 0x28, 0xD9)
LVIOLET = RGBColor(0xED, 0xE9, 0xFE)
GRAY = RGBColor(0xE2, 0xE8, 0xF0)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)


# ------------------------------------------------------------------ evidence


def evidence():
    ev = {"pytest": None, "e2e": None, "cv": None}
    j = ROOT / "evidence" / "pytest_junit.xml"
    if j.exists():
        r = ET.parse(j).getroot()
        s = r if r.tag == "testsuite" else r.find("testsuite")
        ev["pytest"] = {k: int(s.get(k, 0)) for k in ("tests", "failures", "errors", "skipped")}
    p = ROOT / "evidence" / "playwright_results.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        st = d.get("stats", {})
        ev["e2e"] = {"expected": st.get("expected", 0), "unexpected": st.get("unexpected", 0), "flaky": st.get("flaky", 0)}
    c = ROOT / "evidence" / "cv" / "latest_run.json"
    if c.exists():
        ev["cv"] = json.loads(c.read_text(encoding="utf-8"))
    return ev


# ------------------------------------------------------------------ helpers


def set_font(run, size=None, bold=None, color=None):
    f = run.font
    f.name = FONT
    if size:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if color is not None:
        f.color.rgb = color
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):  # Thai is a complex script: set cs (and ea) typeface explicitly
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {})
            rpr.append(el)
        el.set("typeface", FONT)


def text(slide, x, y, w, h, paras, *, size=18, color=SLATE, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.0):
    """paras: list of str or (str, dict(size,bold,color)) or list-of-runs [(str, dict), ...]."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    first = True
    for p in paras:
        para = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        para.alignment = align
        para.line_spacing = spacing
        runs = p if isinstance(p, list) else [p]
        for r in runs:
            if isinstance(r, tuple):
                t, o = r
            else:
                t, o = r, {}
            run = para.add_run()
            run.text = t
            set_font(run, o.get("size", size), o.get("bold", bold), o.get("color", color))
    return tb


def box(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, dash=False, lw=1.5):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
        if dash:
            from pptx.enum.dml import MSO_LINE

            s.line.dash_style = MSO_LINE.DASH
    s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = 0.12
    return s


def label_box(slide, x, y, w, h, title, sub, fill, line, *, title_size=15, sub_size=11, dash=False, tcolor=NAVY):
    s = box(slide, x, y, w, h, fill, line, dash=dash)
    tf = s.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.06)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = title
    set_font(r, title_size, True, tcolor)
    if sub:
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run()
        r2.text = sub
        set_font(r2, sub_size, False, SLATE)
    return s


def arrow(slide, x1, y1, x2, y2, color=SLATE, dash=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(2)
    if dash:
        from pptx.enum.dml import MSO_LINE

        c.line.dash_style = MSO_LINE.DASH
    ln = c.line._get_or_add_ln()
    tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"})
    ln.append(tail)
    return c


def picture(slide, name, x, y, w=None, h=None, border=True):
    p = SHOTS / name
    if not p.exists():
        return label_box(slide, x, y, w or 3, h or 2, f"[ไม่มีภาพ {name}]", "ยังไม่ได้ capture", LRED, RED)
    pic = slide.shapes.add_picture(str(p), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    if border:
        pic.line.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
        pic.line.width = Pt(1)
    return pic


def cropped(name, box_px):
    """Crop a REAL screenshot (pixel box on the 1440x900 capture) with Pillow; keeps aspect ratio when placed."""
    from PIL import Image

    src = SHOTS / name
    out_dir = SHOTS / "crops"
    out_dir.mkdir(exist_ok=True)
    dst = out_dir / f"{src.stem}_{'_'.join(str(v) for v in box_px)}.png"
    with Image.open(src) as im:
        im.crop(box_px).save(dst)
    return dst


def picture_path(slide, path, x, y, w=None, h=None):
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    pic.line.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
    pic.line.width = Pt(1)
    return pic


def header(slide, n, title, kicker=None):
    box(slide, 0, 0, 13.333, 0.12, GREEN, shape=MSO_SHAPE.RECTANGLE)
    if kicker:
        text(slide, 0.5, 0.25, 9, 0.35, [kicker], size=13, color=GREEN, bold=True)
    text(slide, 0.5, 0.5 if kicker else 0.35, 12.3, 0.75, [title], size=30, color=NAVY, bold=True)
    text(slide, 0.5, 7.08, 9.5, 0.3, ["Smart Library NEXT V2 · รายงานความคืบหน้า 15 ต.ค. 2569"], size=10, color=MUTED)
    text(slide, 12.2, 7.08, 0.7, 0.3, [f"{n}/8"], size=10, color=MUTED, align=PP_ALIGN.RIGHT)


def notes(slide, s):
    slide.notes_slide.notes_text_frame.text = s


def sim_tag(slide, x=5.6, y=7.06, w=3.6):
    s = box(slide, x, y, w, 0.32, AMBER, shape=MSO_SHAPE.RECTANGLE)
    tf = s.text_frame
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "ภาพจริงจากต้นแบบ · ข้อมูล SIMULATION"
    set_font(r, 11, True, WHITE)


# ------------------------------------------------------------------ slides


def build():
    ev = evidence()
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # 1 ---------------------------------------------------------------- title + question
    s = prs.slides.add_slide(blank)
    box(s, 0, 0, 13.333, 7.5, NAVY, shape=MSO_SHAPE.RECTANGLE)
    box(s, 0, 0, 0.25, 7.5, GREEN, shape=MSO_SHAPE.RECTANGLE)
    text(s, 0.8, 0.7, 11, 1.1, [[("Smart Library ", {"color": WHITE}), ("NEXT", {"color": RGBColor(0x4A, 0xDE, 0x80)})]], size=54, bold=True)
    text(s, 0.8, 1.75, 11, 0.6, ["Find. Verify. Study."], size=28, color=RGBColor(0xCB, 0xD5, 0xE1), bold=True)
    text(s, 0.8, 2.45, 11.5, 0.6, ["ระบบค้นหาที่นั่งห้องสมุดที่ “เชื่อถือได้” — รายงานความคืบหน้า 15 ตุลาคม 2569"], size=22, color=WHITE)
    q = box(s, 0.8, 3.35, 11.7, 1.55, RGBColor(0x1E, 0x29, 0x3B), RGBColor(0x4A, 0xDE, 0x80))
    text(s, 1.05, 3.45, 11.3, 1.4, [
        [("คำถามของงานรอบนี้", {"size": 16, "bold": True, "color": RGBColor(0x4A, 0xDE, 0x80)})],
        [("ทำอย่างไรไม่ให้นักศึกษาเดินไปเจอที่นั่งที่ระบบบอกว่า “ว่าง” แต่จริง ๆ มีคนนั่ง มีของวาง หรือข้อมูลเก่าไปแล้ว — และเมื่อระบบผิด จะแก้กลับอย่างไร?", {"size": 22, "color": WHITE, "bold": True})],
    ], spacing=1.05)
    text(s, 0.8, 5.25, 8.5, 1.6, [
        "66072099 ธนกฤต แจ้งวงษ์ · 66085992 พสุธร ษ.สุนทรนิรัตน์",
        "66086024 ศิลป์ณริญ หรรษานุกรม · 66073001 กัญญาพัชร จารุเกษม",
        "SEC002",
    ], size=15, color=RGBColor(0xCB, 0xD5, 0xE1))
    text(s, 8.6, 5.3, 4.0, 1.4, ["สิ่งที่จะโชว์: ต้นแบบที่รันได้จริงในเครื่อง", "ข้อมูลที่นั่ง = SIMULATION (ไม่ใช่กล้องจริง)"], size=14,
         color=RGBColor(0xFD, 0xE6, 0x8A), align=PP_ALIGN.RIGHT)
    notes(s, "0:00–0:15 เปิดด้วยคำถาม: ระบบเดิมบอกได้ว่าว่างหรือไม่ แต่ยังไม่ตอบว่า 'เชื่อได้แค่ไหน' และ 'ถ้าผิดจะแก้อย่างไร'.")

    # 2 ---------------------------------------------------------------- previous work
    s = prs.slides.add_slide(blank)
    header(s, 2, "งานก่อนหน้า: ข้อเสนอเดิมของกลุ่ม (ยังเป็นแผน ไม่ใช่ระบบที่ทำเสร็จ)", "สรุปงานก่อนหน้า")
    label_box(s, 0.5, 1.45, 6.0, 0.55, "สไลด์เสนอหัวข้อ 15 หน้า · 1 ต.ค. 2569", None, LBLUE, BLUE, title_size=16)
    text(s, 0.6, 2.05, 5.9, 3.0, [
        "• ปัญหา: เดินหาที่นั่งเอง, ดูว่างแต่มีของวางจอง, ไม่รู้ประเภทที่นั่ง",
        "• 5 สถานะ: Available / Occupied / Reserved / Unavailable / Maintenance",
        "• กล้อง + YOLO + จับคู่ ROI + Smoothing กันกระพริบ",
        "• Floor Map กรองปลั๊ก/Quiet Zone, Admin Dashboard",
        "• Offline: แสดง “ข้อมูลไม่เป็นปัจจุบัน” เสมอ",
    ], size=16)
    label_box(s, 6.85, 1.45, 6.0, 0.55, "ข้อเสนอเชิงเทคนิค 13 หัวข้อ · 30 ก.ย. 2569", None, LBLUE, BLUE, title_size=16)
    text(s, 6.95, 2.05, 5.9, 3.0, [
        "• Decision tree: override → คน → สิ่งของ → ว่าง → smoothing",
        "• Edge-first: SQLite buffer, MQTT QoS1 + LWT, message_id กันซ้ำ",
        "• 10 failure cases: แสงน้อย, คนบัง, ยืนใกล้โต๊ะ, แก้วน้ำ, กล้องหลุด …",
        "• ค่าตั้งต้น: conf 0.5, smoothing 5 s, Reserved 30 นาที, heartbeat 30 s",
        "• Metrics: Precision/Recall/mAP, False Available/Reserved, latency",
    ], size=16)
    box(s, 0.5, 5.25, 12.35, 1.55, LAMBER, AMBER)
    text(s, 0.7, 5.33, 12.0, 1.4, [
        [("สถานะตามจริง: ", {"bold": True, "color": AMBER}), ("ทั้งสองไฟล์เป็น “ข้อเสนอ” — ยังไม่เคยติดตั้งกล้อง ไม่มีข้อมูลจริงจากห้องสมุด และยังไม่เคยได้รับคำติชมจากการนำเสนอ", {})],
        [("ค่า threshold ทุกตัวเป็น “ค่าตั้งต้นที่เสนอ” ", {"bold": True}), ("ไม่ใช่ผลการวัด — รอบนี้จึงคงไว้เป็นค่า config ที่ปรับได้ และบอกชัดว่าเป็นสมมติฐาน", {})],
    ], size=16)
    notes(s, "0:15–0:35 สรุปงานเดิม: PDF 15 หน้า (1 ต.ค.) + DOCX 13 หัวข้อ (30 ก.ย.). เน้นว่าเป็นข้อเสนอ ไม่ใช่ระบบที่ทำแล้ว.")

    # 3 ---------------------------------------------------------------- trust gap
    s = prs.slides.add_slide(blank)
    header(s, 3, "ช่องว่างจริง: “ว่าง” บนจอ ≠ ว่างจริงเสมอ", "ปัญหาที่ยกระดับ")
    gaps = [
        ("คนนั่งแต่กล้องมองไม่เห็น", "ถูกบัง/มุมกล้อง → ระบบเห็นว่าง\n(False Available)", LRED, RED),
        ("ของวางไว้ ≠ การจอง", "อาจเป็นของคนข้าง ๆ หรือลืมไว้\nต้องไม่อ้างว่า “จองแล้ว”", LAMBER, AMBER),
        ("ข้อมูลเก่า/กล้องหลุด", "สีเขียวค้างจากเมื่อ 10 นาทีก่อน\nพาไปผิดที่", GRAY, SLATE),
        ("ความมั่นใจต่ำ", "แสงมืด/เบลอ/เดินผ่าน\nไม่ควรเดาว่า “ว่าง”", GRAY, SLATE),
    ]
    for i, (t, d, f, l) in enumerate(gaps):
        label_box(s, 0.5 + i * 3.12, 1.5, 2.95, 1.55, t, d, f, l, title_size=17, sub_size=13)
    box(s, 0.5, 3.35, 12.35, 0.62, LVIOLET, VIOLET)
    text(s, 0.7, 3.4, 12, 0.55, [[("และระบบเดิมยังไม่มีช่องทางให้นักศึกษา “บอกว่าระบบผิด” และให้เจ้าหน้าที่แก้อย่างเป็นระบบ", {"bold": True, "color": VIOLET})]], size=18,
         anchor=MSO_ANCHOR.MIDDLE)
    steps = [("FIND", "StudyMatch แนะนำเฉพาะที่นั่ง\nว่าง + สด + เชื่อถือได้ พร้อมเหตุผล", LGREEN, GREEN),
             ("VERIFY", "SeatCheck: ถึงแล้วไม่ตรง กดรายงาน\nไม่ต้องระบุตัวตน/ไม่ถ่ายรูป", LVIOLET, VIOLET),
             ("RESOLVE", "เจ้าหน้าที่ตรวจ → override/ปิดเคส\nมีเหตุผล + audit + อัปเดตสดทุกจอ", LBLUE, BLUE)]
    for i, (t, d, f, l) in enumerate(steps):
        label_box(s, 0.5 + i * 4.2, 4.3, 3.85, 1.6, t, d, f, l, title_size=24, sub_size=14)
        if i < 2:
            arrow(s, 4.38 + i * 4.2, 5.1, 4.68 + i * 4.2, 5.1)
    text(s, 0.5, 6.15, 12.35, 0.8, ["ไม่อ้างว่าเป็นระบบแรกของโลก — จุดต่างคือการบูรณาการ trust-aware seat discovery + explainable matching + student→staff discrepancy loop และวัด False Available"],
         size=14, color=MUTED)
    notes(s, "0:35–0:55 ปัญหาไม่ใช่แค่ตรวจจับ แต่คือความน่าเชื่อถือของข้อมูลและการแก้เมื่อผิด → Find. Verify. Resolve.")

    # 4 ---------------------------------------------------------------- architecture
    cv_model = (ev["cv"] or {}).get("model", {}).get("name", "YOLO (ยังไม่รัน)")
    s = prs.slides.add_slide(blank)
    header(s, 4, "สถาปัตยกรรมที่รวมแล้ว: ส่วนที่รันจริง vs งานอนาคต", "Merged architecture")
    label_box(s, 0.5, 1.5, 2.9, 0.95, "ScenarioSource", "Scenario Lab · เฟรมจำลองทุก 2 วิ\n(SIMULATION)", LAMBER, AMBER, title_size=15)
    label_box(s, 0.5, 2.65, 2.9, 0.95, "YOLOObservationSource", "Ultralytics YOLO11n + OpenCV\nแยก venv, ส่งผ่าน /api/ingest", LGREEN, GREEN, title_size=15)
    label_box(s, 3.85, 1.5, 3.0, 2.1, "SeatEvidenceAdapter\n+ SeatStateEngine", "quality gate → คนนั่ง/เดินผ่าน → สิ่งของ\n→ ว่าง · temporal smoothing\nUnknown เมื่อหลักฐานไม่พอ\n(โค้ดเดียวกันทั้งจำลองและ CV)", LGREEN, GREEN, title_size=15)
    label_box(s, 7.3, 1.5, 2.6, 2.1, "FastAPI + SQLite", "observations · seat_current\nreports · overrides · audit\nidempotent event_id\nfreshness / health", LGREEN, GREEN, title_size=15)
    label_box(s, 10.35, 1.5, 2.5, 0.62, "นักศึกษา", "Map · StudyMatch · GroupFit · Wayfinder", LGREEN, GREEN, title_size=14, sub_size=10)
    label_box(s, 10.35, 2.24, 2.5, 0.62, "เจ้าหน้าที่", "SeatCheck review · override · audit", LGREEN, GREEN, title_size=14, sub_size=10)
    label_box(s, 10.35, 2.98, 2.5, 0.62, "Scenario / CV Lab", "ทดสอบเคสเสี่ยง · ผล CV จริง", LGREEN, GREEN, title_size=14, sub_size=10)
    arrow(s, 3.4, 1.97, 3.85, 2.3)
    arrow(s, 3.4, 3.12, 3.85, 2.85)
    arrow(s, 6.85, 2.55, 7.3, 2.55)
    for yy in (1.81, 2.55, 3.29):
        arrow(s, 9.9, 2.55, 10.35, yy)
    text(s, 9.55, 3.62, 3.3, 0.35, ["REST + WebSocket (polling สำรอง)"], size=11, color=MUTED, align=PP_ALIGN.RIGHT)
    text(s, 0.5, 4.1, 12, 0.4, [[("อนาคต (จากข้อเสนอเดิม — ยังไม่ได้ติดตั้ง/ทดสอบ)", {"bold": True, "color": MUTED})]], size=15)
    fut = [("IP Camera PoE / RTSP", "ต้องได้รับอนุญาต"), ("Edge Pi 5 / Jetson", "ยังไม่มีเครื่อง"), ("MQTT QoS1 + TLS + LWT", "store-and-forward"),
           ("PostgreSQL / Cloud", "ประวัติระยะยาว"), ("จอหน้าห้อง + LED GPIO", "ทำงานแม้เน็ตล่ม"), ("UPS / power-loss log", "ระดับ 3 ไฟดับ")]
    for i, (t, d) in enumerate(fut):
        label_box(s, 0.5 + i * 2.07, 4.55, 1.95, 0.95, t, d, WHITE, MUTED, title_size=12, sub_size=10, dash=True, tcolor=MUTED)
    box(s, 0.5, 5.75, 12.35, 0.85, LGREEN, GREEN)
    text(s, 0.7, 5.8, 12, 0.8, [
        [("กติกาความจริง: ", {"bold": True, "color": GREEN}), ("ข้อมูลจำลองใช้ engine และฐานข้อมูลเดียวกับ CV จริง แต่ติดป้าย source=scenario และแยกสถิติเสมอ", {})],
        [("รันบนเครื่องเดียว (127.0.0.1) — ", {"bold": True}), ("ยังไม่ใช่หลักฐานว่า edge/offline failover ใช้งานได้จริง", {})],
    ], size=15)
    notes(s, "0:55–1:05 ชี้กล่องเขียว = รันจริง, กล่องเส้นประ = งานอนาคตจากข้อเสนอเดิม.")

    # 5 ---------------------------------------------------------------- SeatSense states/health
    s = prs.slides.add_slide(blank)
    header(s, 5, "SeatSense: แยก “สถานะ” ออกจาก “ความน่าเชื่อถือ”", "Evidence · State · Health")
    rows = [
        ("ว่าง (Available)", "เห็นชัด ไม่มีคน/ของ ซ้ำ ≥ 4 เฟรม และ ≥ 5 วินาที", LGREEN, GREEN),
        ("มีคนนั่ง (Occupied)", "จุดสะโพกอยู่ในเบาะ + overlap · เดินผ่าน ≠ นั่ง", LRED, RED),
        ("พบสิ่งของ / อาจถูกจับจอง", "กระเป๋า/โน้ตบุ๊ก/หนังสือ ต่อเนื่อง · แก้วน้ำไม่นับ", LAMBER, AMBER),
        ("ไม่แน่ใจ (Unknown)", "มืด/เบลอ/ถูกบัง/ความมั่นใจต่ำ/คนยืนใกล้ → ไม่เดา", GRAY, SLATE),
        ("Unavailable / Maintenance", "เจ้าหน้าที่ตั้ง ชนะผลตรวจจับ แต่ยังโชว์ว่ากล้องออฟไลน์", LBLUE, BLUE),
    ]
    for i, (t, d, f, l) in enumerate(rows):
        y = 1.45 + i * 0.68
        label_box(s, 0.5, y, 2.75, 0.58, t, None, f, l, title_size=13)
        text(s, 3.35, y + 0.05, 3.6, 0.55, [d], size=13, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 0.5, 4.95, 6.5, 0.4, [[("+ มิติแยก: ", {"bold": True, "color": NAVY}), ("ความสด (STALE เกิน 30 วิ) · สุขภาพกล้อง · รายงานค้าง · override", {})]], size=14)
    box(s, 0.5, 5.4, 6.45, 1.5, LAMBER, AMBER)
    text(s, 0.65, 5.45, 6.2, 1.4, [
        [("ทำไม Reserved = “พบสิ่งของ / อาจถูกจับจอง” ไม่ใช่การจอง", {"bold": True, "color": AMBER, "size": 15})],
        "• กล้องเห็นแค่ “ของ” ไม่รู้ว่าเป็นของใคร หรือเจ้าของจะกลับไหม",
        "• ไม่มีระบบจองจริง → ห้ามบอกว่า “มีเจ้าของจองแล้ว”",
        "• เกิน 30 นาที แค่ติดธงให้เจ้าหน้าที่ดู — ไม่ปลดอัตโนมัติ ไม่ยึดของ",
    ], size=13)
    picture_path(s, cropped("10_camera_lost_stale_after_ttl.png", (36, 110, 1405, 870)), 7.2, 1.45, w=5.65)
    sim_tag(s)
    text(s, 7.2, 4.75, 5.65, 1.6, [
        [("ภาพ: กล้อง CAM-A หลุด (จำลอง) ", {"bold": True}), ("→ ที่นั่งโซน A เป็นลายเทา “ข้อมูลไม่เป็นปัจจุบัน” พร้อมเวลาล่าสุด ไม่ถูกแนะนำ; A07 ยังเป็น Maintenance เพราะเจ้าหน้าที่ตั้งไว้", {})],
    ], size=13)
    notes(s, "1:05–1:15 อธิบาย 5 สถานะเดิม + Unknown และมิติความสด/สุขภาพกล้อง. ชี้ว่า Reserved คือ 'พบสิ่งของ' ไม่ใช่การจอง.")

    # 6 ---------------------------------------------------------------- live user story
    s = prs.slides.add_slide(blank)
    header(s, 6, "เดโมจริง: Student → SeatCheck → Staff → อัปเดตสด", "User story ที่รันได้")
    shots = [("02_studymatch_quiet_power.png", "① กรอง เงียบ + ปลั๊ก → A07 อันดับ 1 พร้อมเหตุผล"),
             ("05_after_seatcheck_pending.png", "② SeatCheck ‘มีคนนั่ง’ → รอตรวจ · ถอน A07 จากคำแนะนำ"),
             ("06_staff_report_queue.png", "③ เจ้าหน้าที่เห็นรายงาน → ยืนยัน + เหตุผล + Maintenance 30 นาที"),
             ("07_student_updated_via_ws.png", "④ หน้านักศึกษาเปลี่ยนเป็น Maintenance ทันทีผ่าน WebSocket")]
    for i, (f, cap) in enumerate(shots):
        x = 0.5 + (i % 2) * 6.25
        y = 1.32 + (i // 2) * 2.86
        picture_path(s, cropped(f, (0, 150, 1440, 738)), x, y, w=5.95)
        text(s, x, y + 2.45, 6.0, 0.4, [cap], size=13, color=NAVY, bold=True)
    sim_tag(s)
    notes(s, "1:15–2:10 เดโมสด (หรือใช้ภาพนี้เป็น fallback): filter → A07 → SeatCheck → staff resolve → นักศึกษาเห็นเปลี่ยนสด → กดจำลองกล้องหลุด.")

    # 7 ---------------------------------------------------------------- evidence: tests / bugs / cv
    s = prs.slides.add_slide(blank)
    header(s, 7, "หลักฐาน: ทดสอบจริง · บัคที่เจอจริง · CV จริงแค่ไหน", "Evidence, not claims")
    pt = ev["pytest"]
    e2 = ev["e2e"]
    pt_line = (f"pytest: {pt['tests'] - pt['failures'] - pt['errors'] - pt['skipped']}/{pt['tests']} ผ่าน (fail {pt['failures']}, error {pt['errors']})" if pt else "pytest: ยังไม่มีผล")
    e2_line = (f"Playwright (Edge): {e2['expected']} ผ่าน / {e2['unexpected']} ล้ม" if e2 else "Playwright: ยังไม่มีผล")
    label_box(s, 0.5, 1.35, 4.0, 0.5, "ทดสอบที่รันจริง", None, LGREEN, GREEN, title_size=17)
    text(s, 0.55, 1.92, 3.95, 3.3, [
        [(pt_line, {"bold": True, "color": GREEN, "size": 16})],
        [(e2_line, {"bold": True, "color": GREEN, "size": 16})],
        "ครอบคลุม T01–T14: stale/กล้องหลุดไม่ถูกแนะนำ · low-conf → Unknown · override ชนะ + audit · รายงานไม่ตั้ง Occupied เอง · WS push · 401/rate-limit · GroupFit/route ใช้ข้อมูลกราฟจริง · event ซ้ำ/ย้อนเวลา",
        "Browser: เส้นทางนักศึกษาครบ 12 ขั้น (0 console error) · กล้องหลุด → stale · WS ถูกบล็อก → polling · kill เซิร์ฟเวอร์จริง → ไม่โชว์เขียวค้าง แล้วเชื่อมต่อใหม่เอง",
    ], size=14, spacing=1.05)
    label_box(s, 4.7, 1.35, 4.0, 0.5, "บัคที่เจอจริง (แก้แล้ว + retest)", None, LRED, RED, title_size=17)
    text(s, 4.75, 1.92, 3.95, 3.3, [
        [("BUG-001 ", {"bold": True, "color": RED}), ("กล้องกลับมาหลังหลุด เฟรมเดียวก็แนะนำ A07 → แก้: ขาดข้อมูล > TTL ต้องยืนยันใหม่", {})],
        [("BUG-011 ", {"bold": True, "color": RED}), ("เซิร์ฟเวอร์ล่ม หน้าเว็บยังโชว์ 12 ที่นั่งสีเขียว → แก้: browser ตรวจความสดเอง + ถอนคำแนะนำ", {})],
        [("BUG-013 ", {"bold": True, "color": RED}), ("สคริปต์ -Reset ลบ DB ที่เซิร์ฟเวอร์อื่นใช้อยู่ → แก้: ตรวจพอร์ต/โปรเซสก่อน", {})],
        [("รายละเอียด/อื่น ๆ: evidence/BUG_LOG.md", {"color": MUTED, "size": 12})],
    ], size=14, spacing=1.05)
    cv = ev["cv"]
    label_box(s, 8.9, 1.35, 3.95, 0.5, "CV (P1) ตามจริง", None, LBLUE, BLUE, title_size=17)
    if cv and cv.get("status") == "WORKING_TESTED":
        inf = cv.get("inference", {})
        rois = {r["seat_id"]: r for r in cv.get("rois", [])}
        lab1 = rois.get("LAB1", {}).get("committed_state")
        cv_lines = [
            [("Pipeline: WORKING_TESTED", {"bold": True, "color": GREEN, "size": 15})],
            f"{cv['model']['name']} (COCO pretrained) · {cv['environment']['device'].split(' (')[0].upper()} · median {inf.get('ms_per_frame_median')} ms/เฟรม · n={inf.get('frames')}",
            "ภาพตัวอย่าง bus.jpg + ROI 4 จุดวาดเอง → engine เดียวกัน → API (source=cv): " + ", ".join(f"{k}={v['committed_state']}" for k, v in rois.items()),
            [("ข้อค้นพบจริง: ", {"bold": True}), (f"LAB1 คน ‘ยืน’ ถูกตีเป็น {lab1} เพราะ ROI ทับช่วงสะโพก → ต้อง calibrate ROI กับเบาะจริง", {})] if lab1 == "occupied" else "",
            [("ที่นั่งห้องสมุดจริง: BLOCKED", {"bold": True, "color": RED, "size": 15})],
            "ไม่มีวิดีโอ/กล้องที่ได้รับอนุญาต → ไม่มี accuracy / False Available จริง · ไม่ได้ fine-tune",
        ]
    else:
        cv_lines = [[("CV: BLOCKED", {"bold": True, "color": RED, "size": 15})], (cv or {}).get("message_th", "ยังไม่ได้รัน"),
                    "ไม่มีวิดีโอ/กล้องที่ได้รับอนุญาต → ไม่มี accuracy / False Available จริง"]
    text(s, 8.95, 1.92, 3.9, 3.4, [c for c in cv_lines if c], size=13, spacing=1.0)
    if cv and cv.get("annotated_image") and (ROOT / "evidence" / "cv" / cv["annotated_image"]).exists():
        img = ROOT / "evidence" / "cv" / cv["annotated_image"]
        s.shapes.add_picture(str(img), Inches(11.55), Inches(5.3), height=Inches(1.7))
        text(s, 10.0, 5.95, 1.5, 0.9, ["ผล YOLO จริง (เบลอหน้า) →"], size=11, color=MUTED, align=PP_ALIGN.RIGHT)
    box(s, 0.5, 5.4, 9.4, 1.55, GRAY, SLATE)
    text(s, 0.7, 5.45, 9.1, 1.45, [
        [("ความเสี่ยงที่ “ยังไม่เกิด/ยังไม่ได้ทดสอบกับของจริง” (ไม่ใช่บัค): ", {"bold": True, "color": NAVY})],
        "แสงจ้า/มืดจริง · คนนั่งจมโซฟา · คนยืนคุยในมุมกล้อง · กล้องเลื่อนตำแหน่ง · Wi-Fi/LAN จริงล่ม · store-and-forward · ผัง/ปลั๊ก/โซนเงียบเป็นข้อมูลสมมติ",
        "ตัวเลข simulated False Available ใน Scenario Lab มาจาก ground truth ที่เราเขียนเอง — ใช้ทดสอบตรรกะ ไม่ใช่ความแม่นยำ",
    ], size=14)
    notes(s, "2:10–2:40 อ่านจำนวน test จริง บัค BUG-001 ที่เจอจริงและแก้แล้ว และบอกตรง ๆ ว่า CV บนห้องสมุดยัง BLOCKED.")

    # 8 ---------------------------------------------------------------- next + questions
    s = prs.slides.add_slide(blank)
    header(s, 8, "ขั้นต่อไป และ 3 คำถามถึงอาจารย์", "Next steps")
    text(s, 0.5, 1.4, 6.1, 4.5, [
        [("งานถัดไป (เรียงตามความสำคัญ)", {"bold": True, "color": NAVY, "size": 18})],
        "1. ขออนุญาตถ่ายวิดีโอฉากจัด 4–8 ที่นั่ง (มี consent) → calibrate ROI จริง",
        "2. ติดป้าย ground truth ด้วยมือ → วัด False Available, confusion matrix, Unknown coverage",
        "3. วัด latency เหตุการณ์ → หน้าจอ และเวลาที่ขึ้น STALE",
        "4. ยืนยันผังจริง: ปลั๊ก / โซนเงียบ / ที่นั่งติดกัน / ทางเดิน",
        "5. User study เล็ก: หาที่นั่งด้วยผังธรรมดา vs StudyMatch (ยังไม่ได้ทำ = PLANNED)",
        "6. ทดลอง edge + MQTT store-and-forward เมื่อมีอุปกรณ์",
    ], size=15, spacing=1.12)
    qs = [("1", "พื้นที่/กล้องไหนที่เราได้รับอนุญาตให้ทดลอง และถ่ายวิดีโอแบบมี consent ได้หรือไม่?"),
          ("2", "อาจารย์อยากให้เน้นหลักฐานแบบไหน: ความแม่นยำ CV (mAP) หรือผลกับผู้ใช้ (False Available / เวลาหาที่นั่ง)?"),
          ("3", "นโยบายกับ “ของวางที่นั่ง” ควรเป็นอย่างไร — ระบบควรแค่แจ้งเจ้าหน้าที่ หรือมีขั้นตอนอื่น?")]
    for i, (n, q) in enumerate(qs):
        y = 1.45 + i * 1.42
        label_box(s, 6.95, y, 0.75, 1.2, n, None, NAVY, NAVY, title_size=28, tcolor=WHITE)
        b = box(s, 7.8, y, 5.05, 1.2, LGREEN, GREEN)
        text(s, 7.95, y + 0.05, 4.8, 1.1, [q], size=15, color=NAVY, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    box(s, 0.5, 6.0, 12.35, 0.85, NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 0.7, 6.05, 12, 0.75, [[("สรุป: ", {"bold": True, "color": RGBColor(0x4A, 0xDE, 0x80)}),
                                     ("P0 (map, state/freshness, StudyMatch, SeatCheck→staff→WS, Scenario Lab) + GroupFit/Wayfinder รันและทดสอบแล้วด้วยข้อมูลจำลอง · CV จริงบนห้องสมุดยังรอการอนุญาต",
                                      {"color": WHITE})]], size=15, anchor=MSO_ANCHOR.MIDDLE)
    notes(s, "2:40–3:00 ปิดด้วยงานถัดไปและขออนุญาตพื้นที่/ภาพจริง + ผังจริง.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"saved {OUT} ({OUT.stat().st_size} bytes), slides={len(prs.slides)}")


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from artifacts_paths import assert_writable

    args = [a for a in sys.argv[1:] if a != "--overwrite-frozen"]
    if args:  # optional output path, e.g. presentation/v3/progress_update_v3.pptx
        OUT = ROOT / args[0]
    OUT = assert_writable(OUT, allow_frozen="--overwrite-frozen" in sys.argv)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    build()
