"""YOLOObservationSource - real Ultralytics YOLO + OpenCV + ROI vertical slice.

Runs OUT OF PROCESS (separate .venv-cv) so the demo API never depends on torch/ultralytics.
It performs genuine model inference, relates detections to hand-calibrated image-plane ROIs,
applies the SAME pure-Python SeatEvidenceAdapter + SeatStateEngine as the API, and can push the
observations to the API (source='cv', device CV-LAB, seats LAB1..LAB4) - never to demo seats.

Usage (from project root):
  .venv-cv\\Scripts\\python cv\\run_cv.py suite                      # evidence suite on the bundled sample image
  .venv-cv\\Scripts\\python cv\\run_cv.py image --source path.jpg --roi cv\\roi_config.json --frames 8 --post
  .venv-cv\\Scripts\\python cv\\run_cv.py webcam --index 0 --roi my_roi.json --consent "I am the operator; scene staged with consent"

Privacy: raw frames are NOT stored by default for video/webcam. Annotated images are saved only for the
licensed bundled sample image, or when --save-annotated is passed explicitly together with --consent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "api"))
sys.path.insert(0, str(ROOT / "cv"))

from app.engine.config import EngineConfig  # noqa: E402  (pure python, shared with the API)
from app.engine.evidence import Detection, classify  # noqa: E402
from app.engine.state_engine import SeatEngineState, step  # noqa: E402
from roi import relate_detection  # noqa: E402

EVIDENCE = ROOT / "evidence" / "cv"
EVIDENCE.mkdir(parents=True, exist_ok=True)
CFG = EngineConfig()
API = "http://127.0.0.1:8000"
DEVICE_TOKEN = "cv-device-demo-2569"


def utc_iso(dt=None) -> str:
    dt = dt or datetime.now(timezone.utc)
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def frame_quality(cv2, frame) -> tuple[str, dict]:
    """Proposal s.9: abnormal brightness or low Laplacian variance => do not decide."""
    if frame is None:
        return "no_frame", {}
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean = float(gray.mean())
    lap = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    m = {"brightness_mean": round(mean, 1), "laplacian_var": round(lap, 1)}
    if mean < 40:
        return "dark", m
    if mean > 225:
        return "bright", m
    if lap < 50:
        return "blur", m
    return "ok", m


def load_model(weights: str):
    import torch
    import ultralytics
    from ultralytics import YOLO

    model = YOLO(weights)
    wpath = Path(getattr(model, "ckpt_path", "") or weights)
    info = {
        "name": Path(weights).stem,
        "weights": str(wpath.name),
        "weights_sha256": sha256(wpath) if wpath.exists() else None,
        "ultralytics_version": ultralytics.__version__,
        "task": model.task,
        "num_classes": len(model.names),
        "pretrained_dataset": "COCO (80 classes) - pretrained weights, NOT fine-tuned by this project",
        "has_literal_bag_class": "bag" in model.names.values(),
        "belongings_classes_present": sorted(c for c in model.names.values() if c in CFG.belongings_classes),
    }
    env = {
        "python": platform.python_version(),
        "torch_version": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "device": "cpu (torch CPU build; GPU not used)" if not torch.cuda.is_available() else f"cuda:{torch.cuda.get_device_name(0)}",
        "os": f"{platform.system()} {platform.release()} ({platform.version()})",
        "cpu": platform.processor(),
    }
    return model, info, env


def infer(model, frame, imgsz=640):
    t0 = time.perf_counter()
    res = model.predict(frame, conf=CFG.low_conf_threshold, imgsz=imgsz, verbose=False)[0]
    ms = (time.perf_counter() - t0) * 1000
    dets = []
    for b in res.boxes:
        cls = model.names[int(b.cls)]
        dets.append({"cls": cls, "conf": float(b.conf), "bbox": [float(v) for v in b.xyxy[0].tolist()]})
    return dets, ms


def per_seat(dets, rois):
    out = {}
    for r in rois:
        related = []
        for d in dets:
            rel = relate_detection(d["cls"], d["conf"], d["bbox"], r["seat_polygon"], r["table_polygon"])
            if rel["in_seat"] or rel["in_table"] or rel["seat_overlap"] > 0 or rel["table_overlap"] > 0:
                related.append(rel)
        out[r["seat_id"]] = related
    return out


def post(camera_id, frame_id, observed_at, quality, model_version, seat_dets):
    import requests

    body = {
        "camera_id": camera_id,
        "frame_id": frame_id,
        "observed_at_utc": observed_at,
        "frame_quality": quality,
        "model_version": model_version,
        "seats": [{"seat_id": sid, "event_id": f"{frame_id}-{sid}", "detections": dets} for sid, dets in seat_dets.items()],
    }
    r = requests.post(f"{API}/api/ingest/observations", json=body, headers={"X-Device-Token": DEVICE_TOKEN}, timeout=10)
    r.raise_for_status()
    return r.json()


def annotate(cv2, frame, dets, rois, seat_states, path: Path, title: str):
    img = frame.copy()
    # privacy: blur the head region (top 22%) of every detected person in the SAVED image only
    for d in dets:
        if d["cls"] != "person":
            continue
        x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
        hy = y1 + int(0.22 * (y2 - y1))
        x1, y1 = max(0, x1), max(0, y1)
        if hy > y1 and x2 > x1:
            img[y1:hy, x1:x2] = cv2.GaussianBlur(img[y1:hy, x1:x2], (0, 0), 18)
    for r in rois:
        import numpy as np

        sp = np.array(r["seat_polygon"], dtype=np.int32)
        tp = np.array(r["table_polygon"], dtype=np.int32)
        cv2.polylines(img, [sp], True, (0, 200, 0), 3)
        cv2.polylines(img, [tp], True, (0, 160, 255), 3)
        x, y = r["seat_polygon"][0]
        cv2.putText(img, f"{r['seat_id']}: {seat_states.get(r['seat_id'], '?')}", (int(x) + 4, int(y) - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)
        cv2.putText(img, f"{r['seat_id']}: {seat_states.get(r['seat_id'], '?')}", (int(x) + 4, int(y) - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    for d in dets:
        x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
        col = (40, 40, 230) if d["cls"] == "person" else (230, 120, 30)
        cv2.rectangle(img, (x1, y1), (x2, y2), col, 2)
        label = f"{d['cls']} {d['conf']:.2f}"
        cv2.putText(img, label, (x1, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
        cv2.putText(img, label, (x1, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.rectangle(img, (0, 0), (img.shape[1], 30), (0, 0, 0), -1)
    cv2.putText(img, title, (8, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    cv2.imwrite(str(path), img)


def run_frames(model, model_info, frames_iter, rois, *, camera_id, do_post, interval_s, run_id, label):
    """frames_iter yields (frame or None, error_text or None). Returns structured run record."""
    import cv2

    states = {r["seat_id"]: SeatEngineState() for r in rois}
    last_dets, last_frame, ms_list, frames_log, ingest_results, errors = [], None, [], [], [], []
    model_version = f"{model_info['name']} ({model_info['weights']}, ultralytics {model_info['ultralytics_version']}, COCO pretrained)"
    for i, (frame, err) in enumerate(frames_iter):
        observed = datetime.now(timezone.utc)
        q, qm = frame_quality(cv2, frame)
        dets, ms = ([], None)
        if err:
            errors.append(err)
        if frame is not None:
            dets, ms = infer(model, frame)
            ms_list.append(ms)
            last_frame = frame
            last_dets = dets
        seat_dets = per_seat(dets, rois) if frame is not None else {r["seat_id"]: [] for r in rois}
        frame_rec = {"frame": i, "observed_at_utc": utc_iso(observed), "quality": q, "quality_metrics": qm,
                     "inference_ms": None if ms is None else round(ms, 1), "detections": dets, "seats": {}}
        for r in rois:
            sid = r["seat_id"]
            cand = classify([Detection.from_dict(d) for d in seat_dets[sid]], q, CFG)
            states[sid], res = step(states[sid], cand, observed, CFG)
            frame_rec["seats"][sid] = {"raw_candidate": cand.state, "codes": cand.codes, "committed": states[sid].committed_state,
                                       "related_detections": seat_dets[sid]}
        if do_post:
            try:
                ingest_results.append(post(camera_id, f"{run_id}-f{i:03d}", utc_iso(observed), q, model_version, seat_dets))
            except Exception as e:  # recorded honestly
                errors.append(f"POST failed: {e!r}")
        frames_log.append(frame_rec)
        if interval_s:
            time.sleep(interval_s)
    return {
        "label": label,
        "frames": len(frames_log),
        "ms_per_frame_median": round(statistics.median(ms_list), 1) if ms_list else None,
        "ms_per_frame_all": [round(m, 1) for m in ms_list],
        "frames_log": frames_log,
        "final_states": {sid: s.committed_state for sid, s in states.items()},
        "ingest_results": ingest_results,
        "errors": errors,
        "_last_frame": last_frame,
        "_last_dets": last_dets,
    }


def still_frames(cv2, path: Path, n: int, perturb: str | None = None):
    for _ in range(n):
        img = cv2.imread(str(path))
        if img is None:
            yield None, f"cv2.imread returned None for {path} (file missing or unreadable)"
            continue
        if perturb == "dark":
            img = (img * 0.12).astype("uint8")
        yield img, None


def cmd_suite(args):
    import cv2
    import ultralytics

    run_id = "cv" + datetime.now().strftime("%Y%m%d%H%M%S")
    roi_cfg = json.loads((ROOT / "cv" / "roi_config.json").read_text(encoding="utf-8"))
    sample = Path(ultralytics.__file__).parent / "assets" / roi_cfg["source_image"]
    errors = []
    try:
        model, minfo, env = load_model(args.weights)
    except Exception:
        tb = traceback.format_exc()
        rec = {"status": "BLOCKED", "run_at_utc": utc_iso(), "message_th": "โหลดโมเดล YOLO ไม่สำเร็จ (ดู error จริงด้านล่าง)", "errors": [tb]}
        (EVIDENCE / "latest_run.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        print(tb)
        return 1
    rois = roi_cfg["seats"]
    main = run_frames(model, minfo, still_frames(cv2, sample, args.frames), rois, camera_id="CV-LAB", do_post=args.post,
                      interval_s=args.interval, run_id=run_id, label="sample image replayed as consecutive frames")
    dark = run_frames(model, minfo, still_frames(cv2, sample, 3, perturb="dark"), rois, camera_id="CV-LAB", do_post=False,
                      interval_s=0, run_id=run_id + "d", label="same image darkened x0.12 (synthetic perturbation, quality-gate check)")
    missing = run_frames(model, minfo, still_frames(cv2, ROOT / "cv" / "__missing_source__.jpg", 2), rois, camera_id="CV-LAB",
                         do_post=False, interval_s=0, run_id=run_id + "m", label="missing source file (camera-lost analogue)")

    ann_name = f"annotated_{run_id}.jpg"
    if main["_last_frame"] is not None:
        annotate(cv2, main["_last_frame"], main["_last_dets"], rois, main["final_states"], EVIDENCE / ann_name,
                 f"REAL {minfo['name']} inference on Ultralytics sample image (NOT a library) | ROIs hand-drawn | {run_id}")
    last = main["frames_log"][-1]
    roi_rows = []
    for r in rois:
        sid = r["seat_id"]
        rel = last["seats"][sid]["related_detections"]
        roi_rows.append({
            "seat_id": sid,
            "note": r.get("note"),
            "detections_summary": ", ".join(f"{d['cls']} {d['conf']:.2f} (in_seat={d['in_seat']}, seat_overlap={d['seat_overlap']:.2f}, in_table={d['in_table']})" for d in rel) or "ไม่มี",
            "raw_candidate": last["seats"][sid]["raw_candidate"],
            "committed_state": main["final_states"][sid],
            "codes": last["seats"][sid]["codes"],
        })
    api_states = None
    if args.post:
        try:
            import requests

            api_states = requests.get(f"{API}/api/cv/lab-seats", timeout=5).json()["seats"]
            api_states = {s["seat_id"]: {"physical_state": s["physical_state"], "source": s["source"]} for s in api_states}
        except Exception as e:
            errors.append(f"GET lab-seats failed: {e!r}")
    n_ingested = sum(len(x["results"]) for x in main["ingest_results"])
    rec = {
        "status": "WORKING_TESTED",
        "scope": "เฉพาะ pipeline บนภาพตัวอย่างของ Ultralytics — ไม่ใช่ภาพห้องสมุด",
        "library_cv_status": "BLOCKED",
        "library_cv_blocker": "ไม่มีวิดีโอ/ภาพห้องสมุดที่ได้รับอนุญาต และไม่ได้รับอนุญาตใช้ webcam ในเซสชันนี้ จึงยังไม่มีการวัดความแม่นยำบนที่นั่งจริง",
        "headline_th": f"รัน {minfo['name']} จริง {main['frames']} เฟรม (ภาพนิ่งเดิมซ้ำ) + ROI 4 จุด → state engine เดียวกับระบบ → ส่งเข้า API เป็น source='cv'",
        "not_claimed_th": [
            "ไม่ใช่ภาพจากห้องสมุดหรือกล้อง CCTV ของมหาวิทยาลัย",
            "ROI วาดด้วยมือบนภาพตัวอย่างเพื่อทดสอบทุกกิ่งของ decision logic ไม่ใช่ที่นั่งจริง",
            "ไม่มี ground truth ที่ติดป้ายโดยมนุษย์ → ไม่มี accuracy / mAP / False Available ของ CV",
            "ไม่ได้ fine-tune โมเดล ใช้ COCO pretrained weights",
        ],
        "run_id": run_id,
        "run_at_utc": utc_iso(),
        "model": minfo,
        "environment": env,
        "source": {
            "description": f"ultralytics/assets/{roi_cfg['source_image']} (ภาพตัวอย่างที่มากับแพ็กเกจ ultralytics)",
            "path": str(sample),
            "sha256": sha256(sample) if sample.exists() else None,
            "permission": "ภาพตัวอย่างที่แจกจ่ายมากับแพ็กเกจ ultralytics (AGPL-3.0) ใช้ทดสอบในเครื่องเท่านั้น ไม่เผยแพร่ภาพบุคคลต่อสาธารณะ",
            "frames_note": f"ภาพนิ่ง 1 ภาพ ประมวลผลซ้ำ {main['frames']} ครั้ง ห่างกัน {args.interval} วินาที เพื่อให้ผ่าน temporal smoothing (ทุกครั้งคือ inference จริง)",
        },
        "rois": roi_rows,
        "inference": {"frames": main["frames"], "ms_per_frame_median": main["ms_per_frame_median"], "ms_per_frame_all": main["ms_per_frame_all"],
                      "imgsz": 640, "conf_floor": CFG.low_conf_threshold, "decision_conf_threshold": CFG.conf_threshold},
        "ingest": {"posted": bool(args.post), "observations_ingested": n_ingested, "api_lab_seat_states": api_states,
                   "summary": f"ส่ง {n_ingested} observation เข้า /api/ingest/observations (CV-LAB)" if args.post else "ไม่ได้ส่งเข้า API"},
        "robustness_checks": [
            {"label": dark["label"], "qualities": [f["quality"] for f in dark["frames_log"]],
             "brightness": [f["quality_metrics"].get("brightness_mean") for f in dark["frames_log"]],
             "detections_in_dark_frame": [len(f["detections"]) for f in dark["frames_log"]], "final_states": dark["final_states"]},
            {"label": missing["label"], "qualities": [f["quality"] for f in missing["frames_log"]], "final_states": missing["final_states"],
             "errors": missing["errors"]},
        ],
        "annotated_image": ann_name if main["_last_frame"] is not None else None,
        "errors": errors + main["errors"],
        "frames_log_file": f"run_{run_id}.json",
    }
    full = dict(rec)
    full["frames_log"] = main["frames_log"]
    (EVIDENCE / f"run_{run_id}.json").write_text(json.dumps(full, ensure_ascii=False, indent=2), encoding="utf-8")
    (EVIDENCE / "latest_run.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    with open(EVIDENCE / "run_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{rec['run_at_utc']}] {run_id} model={minfo['name']} device={env['device']} frames={main['frames']} "
                f"median_ms={main['ms_per_frame_median']} final={main['final_states']} ingested={n_ingested} "
                f"dark={rec['robustness_checks'][0]['final_states']} missing={rec['robustness_checks'][1]['final_states']} errors={len(rec['errors'])}\n")
    print(json.dumps({k: rec[k] for k in ("status", "run_id", "rois", "inference", "ingest", "robustness_checks", "errors")}, ensure_ascii=False, indent=2))
    return 0


def cmd_webcam(args):
    """Only for an operator-consented, staged scene. Frames are never written to disk unless --save-annotated."""
    if not args.consent or len(args.consent.strip()) < 10:
        print("REFUSED: webcam use requires --consent \"<statement of who consented and what scene is staged>\"")
        return 2
    import cv2

    model, minfo, env = load_model(args.weights)
    rois = json.loads(Path(args.roi).read_text(encoding="utf-8"))["seats"]
    cap = cv2.VideoCapture(args.index, cv2.CAP_DSHOW)

    def frames():
        for _ in range(args.frames):
            ok, fr = cap.read()
            yield (fr if ok else None), (None if ok else "VideoCapture.read() failed")

    run_id = "cam" + datetime.now().strftime("%Y%m%d%H%M%S")
    out = run_frames(model, minfo, frames(), rois, camera_id="CV-LAB", do_post=args.post, interval_s=args.interval, run_id=run_id,
                     label=f"webcam index {args.index} (consent: {args.consent})")
    cap.release()
    if args.save_annotated and out["_last_frame"] is not None:
        annotate(cv2, out["_last_frame"], out["_last_dets"], rois, out["final_states"], EVIDENCE / f"annotated_{run_id}.jpg", f"REAL webcam inference {run_id}")
    rec = {k: v for k, v in out.items() if not k.startswith("_")}
    rec.update({"run_id": run_id, "model": minfo, "environment": env, "consent": args.consent})
    (EVIDENCE / f"run_{run_id}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"final_states": out["final_states"], "median_ms": out["ms_per_frame_median"], "errors": out["errors"]}, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("suite")
    s.add_argument("--weights", default=str(ROOT / "cv" / "models" / "yolo11n.pt"))
    s.add_argument("--frames", type=int, default=8)
    s.add_argument("--interval", type=float, default=1.0)
    s.add_argument("--post", action="store_true")
    w = sub.add_parser("webcam")
    w.add_argument("--weights", default=str(ROOT / "cv" / "models" / "yolo11n.pt"))
    w.add_argument("--index", type=int, default=0)
    w.add_argument("--roi", required=True)
    w.add_argument("--frames", type=int, default=10)
    w.add_argument("--interval", type=float, default=1.0)
    w.add_argument("--consent", default="")
    w.add_argument("--post", action="store_true")
    w.add_argument("--save-annotated", action="store_true")
    a = ap.parse_args()
    return cmd_suite(a) if a.cmd == "suite" else cmd_webcam(a)


if __name__ == "__main__":
    sys.exit(main())
