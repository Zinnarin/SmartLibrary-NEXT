import { useState } from "react";
import { api, ApiError, newClientId, type PublicReport, type Seat } from "../api";
import { ago, CAMERA_TH, duration, REPORT_REASONS, SEAT_TYPE_TH, thTime, TONE, ZONE_TH } from "../labels";
import { useLive } from "../live";

interface Props {
  seat: Seat;
  onClose: () => void;
  onRoute: (id: string) => void;
  routeActive: boolean;
  onReported: (r: PublicReport) => void;
  myReports: PublicReport[];
}

export default function SeatDetail({ seat, onClose, onRoute, routeActive, onReported, myReports }: Props) {
  const { ageOf, meta } = useLive();
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState("reported_occupied");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const t = TONE[seat.display_tone] || TONE.unknown;
  const age = ageOf(seat.observed_at_utc);
  const stateFor = ageOf(seat.state_since_utc);
  const mine = myReports.filter((r) => r.seat_id === seat.seat_id);

  const submit = async () => {
    setBusy(true);
    setErr(null);
    try {
      const r = await api<PublicReport>("/api/seat-reports", {
        method: "POST",
        session: true,
        body: { seat_id: seat.seat_id, reason, client_report_id: newClientId() },
      });
      onReported(r);
      setOpen(false);
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="rounded-2xl border border-slate-300 bg-white shadow-sm" aria-live="polite" data-testid="seat-detail">
      <header className="flex items-start justify-between gap-2 border-b border-slate-200 p-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">
            ที่นั่ง {seat.seat_id} · {SEAT_TYPE_TH[seat.seat_type] || seat.seat_type}
          </h2>
          <p className="text-sm text-slate-600">{ZONE_TH[seat.zone_id] || seat.zone_id}</p>
        </div>
        <button onClick={onClose} className="rounded-lg px-2 py-1 text-slate-500 hover:bg-slate-100" aria-label="ปิดรายละเอียด">
          ✕
        </button>
      </header>

      <div className="space-y-3 p-4 text-[15px]">
        <div className={`inline-flex items-center gap-2 rounded-full border-2 px-3 py-1 font-bold ${t.chip}`} data-testid="seat-state">
          <span aria-hidden>{t.glyph}</span>
          {seat.manual_override ? seat.display_state_label_th : seat.display_tone === "stale" ? `${t.label} (ล่าสุด: ${seat.physical_state_label_th})` : seat.display_state_label_th}
        </div>

        {seat.pending_discrepancy && (
          <div className="rounded-lg border border-violet-300 bg-violet-50 px-3 py-2 text-violet-900" data-testid="pending-badge">
            ⚑ มีรายงานที่ต้องตรวจสอบ ({seat.pending_report_count}) — ไม่นำมาแนะนำแบบความน่าเชื่อถือสูงจนกว่าเจ้าหน้าที่ตรวจ
          </div>
        )}

        {seat.manual_override && (
          <div className="rounded-lg border border-blue-300 bg-blue-50 px-3 py-2 text-blue-900">
            เจ้าหน้าที่ตั้งสถานะ: <b>{seat.display_state_label_th}</b> — {seat.manual_override.reason}
            <div className="text-xs">
              ตั้งเมื่อ {thTime(seat.manual_override.created_at_utc)}
              {seat.manual_override.expires_at_utc ? ` · หมดอายุ ${thTime(seat.manual_override.expires_at_utc)}` : ""} · สถานะจากหลักฐานกล้อง: {seat.physical_state_label_th}
            </div>
          </div>
        )}

        <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm">
          <dt className="text-slate-500">ข้อมูลล่าสุด</dt>
          <dd data-testid="seat-observed">
            {thTime(seat.observed_at_utc)} ({ago(age)}) {seat.is_stale && <b className="text-slate-700">· STALE เกิน {meta?.freshness_ttl_s ?? 30} วินาที</b>}
          </dd>
          <dt className="text-slate-500">แหล่งข้อมูล</dt>
          <dd>{seat.source === "scenario" ? <b className="text-amber-700">SIMULATION (Scenario Lab) — ไม่ใช่กล้องจริง</b> : seat.source === "cv" ? "กล้อง/CV จริง" : "—"}</dd>
          <dt className="text-slate-500">กล้อง</dt>
          <dd>
            {seat.camera_id}{seat.source === "scenario" ? " (กล้องจำลอง)" : ""} · <span className={seat.camera_health === "healthy" ? "text-green-700" : "font-bold text-red-700"}>{CAMERA_TH[seat.camera_health] || seat.camera_health}</span>
          </dd>
          <dt className="text-slate-500">สถานะนี้มาแล้ว</dt>
          <dd>{duration(stateFor)}</dd>
          {seat.physical_state === "unknown" && seat.last_confident_state && (
            <>
              <dt className="text-slate-500">ก่อนหน้าที่มั่นใจ</dt>
              <dd>
                {TONE[seat.last_confident_state as keyof typeof TONE]?.label || seat.last_confident_state} เมื่อ {thTime(seat.last_confident_at_utc)}
              </dd>
            </>
          )}
          <dt className="text-slate-500">หลักฐาน</dt>
          <dd className="font-mono text-xs">{seat.evidence_codes.join(", ") || "—"}</dd>
        </dl>

        {seat.display_state === "reserved" && (
          <p className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-900">
            พบสิ่งของวางต่อเนื่อง ไม่ใช่การจองอย่างเป็นทางการ (อาจเป็นของคนข้าง ๆ ก็ได้) · ระบบ<b>ไม่ปลดอัตโนมัติ</b>
            {seat.belongings_review_flag ? " · เกิน 30 นาทีแล้ว: แจ้งเจ้าหน้าที่ตรวจสอบ" : " · ครบ 30 นาทีจะแจ้งเจ้าหน้าที่ตรวจ"}
          </p>
        )}

        <div className="flex flex-wrap gap-2 text-sm">
          <Attr on={seat.quiet_zone} label="โซนเงียบ" />
          <Attr on={seat.has_power} label="⚡ ปลั๊กไฟ" />
          <Attr on={seat.near_window} label="ริมหน้าต่าง" />
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500">ข้อมูลที่นั่งเป็นข้อมูลสาธิต (สมมติ)</span>
        </div>

        <div className={`rounded-lg px-3 py-2 text-sm ${seat.is_recommendable ? "bg-green-50 text-green-900" : "bg-slate-100 text-slate-800"}`} data-testid="trust">
          {seat.is_recommendable ? (
            <b>✓ ความน่าเชื่อถือสูง: ผ่านทุกเงื่อนไข จึงแนะนำได้</b>
          ) : (
            <>
              <b>ไม่นำมาแนะนำ เพราะ:</b>
              <ul className="ml-5 list-disc">
                {seat.not_recommendable_reasons_th.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
            </>
          )}
        </div>
        <p className="text-xs text-slate-500">สถานะอาจเปลี่ยนก่อนคุณเดินไปถึง หากพบว่าไม่ตรง กด SeatCheck ด้านล่าง</p>

        <div className="flex flex-wrap gap-2">
          <button onClick={() => onRoute(seat.seat_id)} className="rounded-xl bg-violet-700 px-4 py-2 font-semibold text-white hover:bg-violet-800" data-testid="route-btn">
            {routeActive ? "ซ่อนเส้นทาง" : "🧭 นำทางจากทางเข้า"}
          </button>
          <button onClick={() => setOpen((o) => !o)} className="rounded-xl border-2 border-violet-700 px-4 py-2 font-semibold text-violet-800 hover:bg-violet-50" data-testid="seatcheck-open">
            SeatCheck: ที่นั่งจริงไม่ตรงกับระบบ
          </button>
        </div>

        {open && (
          <div className="space-y-2 rounded-xl border border-violet-300 bg-violet-50 p-3" data-testid="seatcheck-form">
            <p className="text-sm font-semibold text-violet-900">เกิดอะไรขึ้นที่ {seat.seat_id}?</p>
            {REPORT_REASONS.map((r) => (
              <label key={r.value} className="flex items-center gap-2 text-sm">
                <input type="radio" name="reason" value={r.value} checked={reason === r.value} onChange={() => setReason(r.value)} />
                {r.label}
              </label>
            ))}
            <p className="text-xs text-violet-800">
              ไม่ต้องระบุตัวตน ไม่ต้องถ่ายรูป · รายงาน 1 ครั้ง<b>จะไม่เปลี่ยนสถานะที่นั่งเอง</b> เจ้าหน้าที่จะตรวจสอบก่อน · ไม่มีการลงโทษผู้ใช้ที่นั่ง
            </p>
            {err && <p className="rounded bg-red-100 px-2 py-1 text-sm text-red-800" role="alert">{err}</p>}
            <button disabled={busy} onClick={submit} className="rounded-xl bg-violet-700 px-4 py-2 font-semibold text-white disabled:opacity-50" data-testid="seatcheck-submit">
              {busy ? "กำลังส่ง…" : "ส่งรายงาน"}
            </button>
          </div>
        )}

        {mine.length > 0 && (
          <div className="space-y-1 text-sm" data-testid="my-reports">
            {mine.map((r) => (
              <div key={r.id} className="rounded-lg border border-slate-200 px-3 py-1.5">
                รายงาน #{r.id}: {r.reason_th} —{" "}
                {r.review_status === "pending" ? (
                  <b className="text-violet-700">รอเจ้าหน้าที่ตรวจสอบ</b>
                ) : r.review_status === "accepted" ? (
                  <b className="text-green-700">เจ้าหน้าที่ยืนยันแล้ว: {r.decision_reason}</b>
                ) : (
                  <b className="text-slate-700">เจ้าหน้าที่ตรวจแล้วไม่พบปัญหา: {r.decision_reason}</b>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

function Attr({ on, label }: { on: boolean; label: string }) {
  return (
    <span className={`rounded-full border px-2 py-0.5 ${on ? "border-green-600 bg-green-50 text-green-800" : "border-slate-300 bg-white text-slate-400 line-through"}`}>
      {label}
    </span>
  );
}
