import { useEffect, useState } from "react";
import { api, type Seat } from "../api";
import { thDateTime, TONE } from "../labels";

export default function CvLab() {
  const [st, setSt] = useState<any>(null);
  const [lab, setLab] = useState<Seat[]>([]);
  useEffect(() => {
    api("/api/cv/status").then(setSt).catch(() => setSt({ status: "ERROR" }));
    api<{ seats: Seat[] }>("/api/cv/lab-seats").then((d) => setLab(d.seats)).catch(() => {});
  }, []);
  if (!st) return <p className="text-slate-500">กำลังโหลด…</p>;
  const tag = st.status as string;
  const tagStyle =
    tag === "WORKING_TESTED" ? "bg-green-700 text-white" : tag === "BLOCKED" ? "bg-red-700 text-white" : "bg-slate-700 text-white";
  return (
    <div className="space-y-4" data-testid="cv-lab">
      <div className="rounded-2xl border border-slate-300 bg-white p-4">
        <div className="flex flex-wrap items-center gap-3">
          <h2 className="text-xl font-bold">CV Lab — YOLO + ROI (P1)</h2>
          <span className={`rounded-full px-3 py-1 text-sm font-bold ${tagStyle}`} data-testid="cv-status">Pipeline: {tag}</span>
          {st.scope && <span className="text-sm text-slate-600">{st.scope}</span>}
          {st.library_cv_status && (
            <span className="rounded-full bg-red-700 px-3 py-1 text-sm font-bold text-white" data-testid="cv-library-status">
              CV บนที่นั่งห้องสมุดจริง: {st.library_cv_status}
            </span>
          )}
        </div>
        {st.library_cv_blocker && <p className="mt-2 text-sm text-red-800">เหตุผล: {st.library_cv_blocker}</p>}
        {st.headline_th && <p className="mt-2 font-semibold">{st.headline_th}</p>}
        {st.message_th && <p className="mt-2">{st.message_th}</p>}
        {st.not_claimed_th && (
          <ul className="mt-2 list-disc space-y-0.5 pl-5 text-sm text-red-800">
            {st.not_claimed_th.map((x: string) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
        )}
      </div>
      {st.model && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-2xl border border-slate-300 bg-white p-4 text-sm">
            <h3 className="mb-2 font-bold">ข้อมูลการรันจริง</h3>
            <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1">
              <dt className="text-slate-500">เวลา</dt>
              <dd>{thDateTime(st.run_at_utc)}</dd>
              <dt className="text-slate-500">โมเดล</dt>
              <dd>{st.model?.name} ({st.model?.weights}) · ultralytics {st.model?.ultralytics_version}</dd>
              <dt className="text-slate-500">อุปกรณ์</dt>
              <dd>{st.environment?.device} · torch {st.environment?.torch_version}</dd>
              <dt className="text-slate-500">แหล่งภาพ</dt>
              <dd>{st.source?.description}</dd>
              <dt className="text-slate-500">สิทธิ์/ที่มา</dt>
              <dd>{st.source?.permission}</dd>
              <dt className="text-slate-500">เวลา inference</dt>
              <dd>{st.inference?.ms_per_frame_median != null ? `${st.inference.ms_per_frame_median} ms/เฟรม (median, n=${st.inference.frames})` : "—"}</dd>
              <dt className="text-slate-500">การส่งเข้า API</dt>
              <dd>{st.ingest?.summary || "—"}</dd>
            </dl>
          </div>
          {st.annotated_image && (
            <figure className="rounded-2xl border border-slate-300 bg-white p-2">
              <img src={`/api/cv/annotated/${st.annotated_image}`} alt="ผล YOLO จริงพร้อม ROI" className="w-full rounded-xl" />
              <figcaption className="p-2 text-xs text-slate-600">ภาพนี้คือผล inference จริงจากโมเดลบนภาพตัวอย่างที่ระบุ พร้อม ROI ที่กำหนดเอง (ไม่ใช่ห้องสมุด)</figcaption>
            </figure>
          )}
        </div>
      )}
      {st.rois && (
        <div className="overflow-x-auto rounded-2xl border border-slate-300 bg-white">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-100 text-left">
              <tr>
                <th className="px-3 py-2">ROI</th>
                <th className="px-3 py-2">ROI นี้ทดสอบอะไร</th>
                <th className="px-3 py-2">วัตถุที่ตรวจพบใน ROI (จริง)</th>
                <th className="px-3 py-2">raw candidate</th>
                <th className="px-3 py-2">committed (หลัง smoothing)</th>
                <th className="px-3 py-2">evidence codes</th>
              </tr>
            </thead>
            <tbody>
              {st.rois.map((r: any) => (
                <tr key={r.seat_id} className="border-t border-slate-200">
                  <td className="px-3 py-1.5 font-bold">{r.seat_id}</td>
                  <td className="px-3 py-1.5 text-xs text-slate-600">{r.note}</td>
                  <td className="px-3 py-1.5">{r.detections_summary}</td>
                  <td className="px-3 py-1.5">{r.raw_candidate}</td>
                  <td className="px-3 py-1.5">{r.committed_state}</td>
                  <td className="px-3 py-1.5 font-mono text-xs">{(r.codes || []).join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {st.robustness_checks && (
        <div className="rounded-2xl border border-slate-300 bg-white p-4 text-sm">
          <h3 className="font-bold">การทดสอบ quality gate (ใช้โมเดลจริง)</h3>
          <ul className="mt-1 list-disc space-y-0.5 pl-5">
            {st.robustness_checks.map((c: any) => (
              <li key={c.label}>
                {c.label}: quality = {(c.qualities || []).join(", ")}
                {c.detections_in_dark_frame ? ` · YOLO ยังเจอวัตถุ ${c.detections_in_dark_frame[0]} ชิ้นในภาพมืด แต่ระบบไม่ตัดสิน` : ""} → ผล: {Object.entries(c.final_states || {}).map(([k, v]) => `${k}=${v}`).join(", ")}
              </li>
            ))}
          </ul>
        </div>
      )}
      {lab.length > 0 && (
        <div className="rounded-2xl border border-slate-300 bg-white p-4">
          <h3 className="font-bold">สถานะ LAB seats ใน backend (source = cv)</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {lab.map((s) => (
              <span key={s.seat_id} className={`rounded-lg border px-2 py-1 text-sm ${TONE[s.display_tone].chip}`}>
                {s.seat_id}: {s.display_tone === "stale" ? `STALE (ล่าสุด ${s.physical_state_label_th})` : s.display_state_label_th} · source={s.source || "—"}
              </span>
            ))}
          </div>
          <p className="mt-1 text-xs text-slate-500">LAB seats ไม่แสดงบนผังนักศึกษาและไม่ถูกนำไปแนะนำ</p>
        </div>
      )}
      {st.errors && st.errors.length > 0 && (
        <pre className="overflow-x-auto rounded-2xl bg-slate-900 p-4 text-xs text-slate-100">{st.errors.join("\n")}</pre>
      )}
    </div>
  );
}
