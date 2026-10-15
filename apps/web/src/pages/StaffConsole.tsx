import { useEffect, useState } from "react";
import { api, ApiError, getStaffToken, setStaffToken, type Seat } from "../api";
import { ago, CAMERA_TH, thDateTime, thTime, TONE } from "../labels";
import { useLive } from "../live";

interface Report {
  id: number;
  seat_id: string;
  reason: string;
  reason_th: string;
  created_at_utc: string;
  review_status: string;
  reviewed_at_utc: string | null;
  decision_reason: string | null;
  actor_id: string | null;
  is_simulated: boolean;
  display_state_at_report: string | null;
}

interface EventRow {
  id: number;
  created_at_utc: string;
  category: string;
  detail: string;
  source: string;
  seat_id: string | null;
  actor_id: string | null;
}

export function StaffGate({ children }: { children: React.ReactNode }) {
  const [ok, setOk] = useState<boolean | null>(null);
  const [pin, setPin] = useState("");
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => {
    if (!getStaffToken()) return setOk(false);
    api("/api/admin/check", { staff: true })
      .then(() => setOk(true))
      .catch(() => setOk(false));
  }, []);
  const login = async () => {
    setStaffToken(pin);
    try {
      await api("/api/admin/check", { staff: true });
      setOk(true);
      setErr(null);
    } catch (e) {
      setStaffToken(null);
      setErr(e instanceof ApiError ? e.message : "เข้าสู่ระบบไม่สำเร็จ");
    }
  };
  if (ok === null) return <p className="p-6 text-slate-500">กำลังตรวจสิทธิ์…</p>;
  if (!ok)
    return (
      <div className="mx-auto max-w-md rounded-2xl border border-slate-300 bg-white p-6 shadow-sm" data-testid="staff-login">
        <h2 className="text-xl font-bold">เข้าสู่ระบบเจ้าหน้าที่ (Demo gate)</h2>
        <p className="mt-1 text-sm text-slate-600">ระบบสาธิตในเครื่องเท่านั้น — ไม่ใช่ระบบยืนยันตัวตนสำหรับใช้งานจริง</p>
        <input
          type="password"
          value={pin}
          onChange={(e) => setPin(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && login()}
          placeholder="รหัสเจ้าหน้าที่ (ดู README)"
          className="mt-4 w-full rounded-xl border-2 border-slate-300 px-3 py-2"
          aria-label="รหัสเจ้าหน้าที่"
          data-testid="staff-pin"
        />
        {err && <p className="mt-2 rounded bg-red-100 px-2 py-1 text-sm text-red-800">{err}</p>}
        <button onClick={login} className="mt-3 w-full rounded-xl bg-slate-900 px-4 py-2 font-semibold text-white" data-testid="staff-login-btn">
          เข้าสู่ระบบ
        </button>
      </div>
    );
  return <>{children}</>;
}

export default function StaffConsole() {
  const [tab, setTab] = useState<"reports" | "seats" | "events">("reports");
  const { meta } = useLive();
  return (
    <StaffGate>
      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="mr-4 text-xl font-bold">Librarian Console</h2>
          <TabBtn on={tab === "reports"} onClick={() => setTab("reports")} testid="tab-reports">
            รายงาน SeatCheck {meta?.pending_reports ? <span className="ml-1 rounded-full bg-violet-600 px-2 text-white">{meta.pending_reports}</span> : null}
          </TabBtn>
          <TabBtn on={tab === "seats"} onClick={() => setTab("seats")} testid="tab-seats">
            ที่นั่ง & สุขภาพระบบ
          </TabBtn>
          <TabBtn on={tab === "events"} onClick={() => setTab("events")} testid="tab-events">
            Audit log
          </TabBtn>
          <button onClick={() => { setStaffToken(null); location.reload(); }} className="ml-auto text-sm text-slate-500 underline">
            ออกจากระบบ
          </button>
        </div>
        {tab === "reports" && <ReportsTab />}
        {tab === "seats" && <SeatsTab />}
        {tab === "events" && <EventsTab />}
      </div>
    </StaffGate>
  );
}

function TabBtn({ on, onClick, children, testid }: { on: boolean; onClick: () => void; children: React.ReactNode; testid: string }) {
  return (
    <button onClick={onClick} data-testid={testid} className={`rounded-xl px-3 py-1.5 font-semibold ${on ? "bg-slate-900 text-white" : "bg-white text-slate-700 border border-slate-300"}`}>
      {children}
    </button>
  );
}

function ReportsTab() {
  const { byId, meta, ageOf } = useLive();
  const [reports, setReports] = useState<Report[]>([]);
  const [status, setStatus] = useState<"pending" | "all">("pending");
  const [err, setErr] = useState<string | null>(null);
  const load = async () => {
    try {
      const d = await api<{ reports: Report[] }>(`/api/admin/seat-reports?status=${status}`, { staff: true });
      setReports(d.reports);
      setErr(null);
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : String(e));
    }
  };
  useEffect(() => {
    load();
  }, [status, meta?.pending_reports, meta?.recent_resolved_reports?.[0]?.id]);
  return (
    <div className="space-y-3">
      <div className="flex gap-2 text-sm">
        <button onClick={() => setStatus("pending")} className={status === "pending" ? "font-bold underline" : ""}>รอตรวจ</button>
        <button onClick={() => setStatus("all")} className={status === "all" ? "font-bold underline" : ""}>ทั้งหมด</button>
      </div>
      {err && <p className="rounded bg-red-100 px-3 py-2 text-red-800">{err}</p>}
      {reports.length === 0 && <p className="rounded-xl bg-white p-6 text-center text-slate-500">ไม่มีรายงาน{status === "pending" ? "ที่รอตรวจ" : ""}</p>}
      {reports.map((r) => (
        <ReportCard key={r.id} r={r} seat={byId[r.seat_id]} onDone={load} ageOf={ageOf} />
      ))}
    </div>
  );
}

const DECISION_PRESETS = {
  accepted: ["ตรวจแล้วมีคนนั่งจริง กล้องมองไม่เห็น", "ตรวจแล้วมีสิ่งของวางจริง", "ที่นั่งชำรุด ปิดซ่อม"],
  rejected: ["ตรวจแล้วที่นั่งว่างจริง", "ไม่พบปัญหาตามที่รายงาน"],
};

function ReportCard({ r, seat, onDone, ageOf }: { r: Report; seat?: Seat; onDone: () => void; ageOf: (s: string | null) => number | null }) {
  const [decision, setDecision] = useState<"accepted" | "rejected">("accepted");
  const [reason, setReason] = useState("");
  const [ov, setOv] = useState<"" | "maintenance" | "unavailable" | "unknown">("maintenance");
  const [minutes, setMinutes] = useState("30");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const t = seat ? TONE[seat.display_tone] : null;
  const submit = async () => {
    setBusy(true);
    setErr(null);
    try {
      await api(`/api/admin/seat-reports/${r.id}/resolve`, {
        method: "POST",
        staff: true,
        body: {
          decision,
          reason,
          override_state: decision === "accepted" && ov ? ov : null,
          override_minutes: decision === "accepted" && ov && minutes ? Number(minutes) : null,
        },
      });
      onDone();
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };
  return (
    <article className="rounded-2xl border border-slate-300 bg-white p-4 shadow-sm" data-testid={`report-${r.id}`}>
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-lg font-bold">#{r.id} · ที่นั่ง {r.seat_id}</h3>
        <span className="rounded-full bg-violet-100 px-2 py-0.5 text-sm text-violet-900">{r.reason_th}</span>
        {r.is_simulated && <span className="rounded-full bg-amber-200 px-2 py-0.5 text-xs font-bold text-amber-900">SIMULATED REPORT</span>}
        <span className="text-sm text-slate-500">ส่งเมื่อ {thTime(r.created_at_utc)} ({ago(ageOf(r.created_at_utc))})</span>
        <span className={`ml-auto rounded-full px-2 py-0.5 text-sm font-semibold ${r.review_status === "pending" ? "bg-violet-600 text-white" : "bg-slate-200"}`}>
          {r.review_status === "pending" ? "รอตรวจ" : r.review_status === "accepted" ? "ยืนยันแล้ว" : "ปฏิเสธแล้ว"}
        </span>
      </div>
      {seat && t && (
        <p className="mt-1 text-sm text-slate-700">
          สถานะปัจจุบันบนระบบ: <span className={`rounded border px-1.5 ${t.chip}`}>{t.glyph} {seat.display_state_label_th}</span> · หลักฐานจาก {seat.source === "scenario" ? "SIMULATION" : seat.source} ·
          กล้อง {CAMERA_TH[seat.camera_health]} · รายงานไม่ได้เปลี่ยนสถานะนี้อัตโนมัติ
        </p>
      )}
      {r.review_status !== "pending" ? (
        <p className="mt-2 text-sm">
          ตัดสินโดย {r.actor_id} เมื่อ {thDateTime(r.reviewed_at_utc)}: <b>{r.decision_reason}</b>
        </p>
      ) : (
        <div className="mt-3 space-y-2">
          <div className="flex gap-2">
            <label className="flex items-center gap-1">
              <input type="radio" checked={decision === "accepted"} onChange={() => setDecision("accepted")} /> ยืนยันรายงาน (ตรวจแล้วจริง)
            </label>
            <label className="flex items-center gap-1">
              <input type="radio" checked={decision === "rejected"} onChange={() => setDecision("rejected")} data-testid={`reject-${r.id}`} /> ปฏิเสธ (สถานะระบบถูกต้อง)
            </label>
          </div>
          <div className="flex flex-wrap gap-1">
            {DECISION_PRESETS[decision].map((p) => (
              <button key={p} onClick={() => setReason(p)} className="rounded-full border border-slate-300 px-2 py-0.5 text-xs hover:bg-slate-100">
                {p}
              </button>
            ))}
          </div>
          <textarea value={reason} onChange={(e) => setReason(e.target.value)} placeholder="เหตุผลการตัดสิน (จำเป็น)" className="w-full rounded-xl border-2 border-slate-300 px-3 py-2 text-sm" rows={2} data-testid={`reason-${r.id}`} />
          {decision === "accepted" && (
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span>ตั้งสถานะชั่วคราว:</span>
              <select value={ov} onChange={(e) => setOv(e.target.value as any)} className="rounded-lg border border-slate-300 px-2 py-1" data-testid={`ov-${r.id}`}>
                <option value="">ไม่ตั้ง (ปิดเคสอย่างเดียว)</option>
                <option value="maintenance">ซ่อม/ทำความสะอาด (Maintenance)</option>
                <option value="unavailable">ปิดใช้งาน (Unavailable)</option>
                <option value="unknown">ไม่แน่ใจ รอตรวจ (Unknown)</option>
              </select>
              {ov && (
                <>
                  <span>หมดอายุใน</span>
                  <input value={minutes} onChange={(e) => setMinutes(e.target.value.replace(/\D/g, ""))} className="w-16 rounded-lg border border-slate-300 px-2 py-1" />
                  <span>นาที</span>
                </>
              )}
            </div>
          )}
          {err && <p className="rounded bg-red-100 px-2 py-1 text-sm text-red-800">{err}</p>}
          <button disabled={busy} onClick={submit} className="rounded-xl bg-slate-900 px-4 py-2 font-semibold text-white disabled:opacity-50" data-testid={`resolve-${r.id}`}>
            บันทึกการตัดสิน + audit
          </button>
        </div>
      )}
    </article>
  );
}

function SeatsTab() {
  const { seats, meta, ageOf } = useLive();
  const [editing, setEditing] = useState<string | null>(null);
  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {meta?.cameras.map((c) => (
          <div key={c.camera_id} className={`rounded-xl border-2 bg-white p-3 ${c.status === "healthy" ? "border-green-600" : c.status === "degraded" ? "border-amber-500" : "border-red-600"}`}>
            <p className="font-bold">{c.camera_id}</p>
            <p className="text-sm text-slate-600">{c.label_th}</p>
            <p className="text-sm">
              สถานะ: <b>{CAMERA_TH[c.status] || c.status}</b> · แหล่ง: {c.source_mode === "scenario" ? "SIMULATION" : "CV จริง"}
            </p>
          </div>
        ))}
      </div>
      <div className="overflow-x-auto rounded-2xl border border-slate-300 bg-white">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-100 text-left">
            <tr>
              <th className="px-3 py-2">ที่นั่ง</th>
              <th className="px-3 py-2">แสดงผล</th>
              <th className="px-3 py-2">หลักฐาน (physical)</th>
              <th className="px-3 py-2">ความสด</th>
              <th className="px-3 py-2">กล้อง</th>
              <th className="px-3 py-2">รายงาน</th>
              <th className="px-3 py-2">Override</th>
              <th className="px-3 py-2"></th>
            </tr>
          </thead>
          <tbody>
            {seats.map((s) => (
              <SeatRow key={s.seat_id} s={s} age={ageOf(s.observed_at_utc)} editing={editing === s.seat_id} setEditing={setEditing} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SeatRow({ s, age, editing, setEditing }: { s: Seat; age: number | null; editing: boolean; setEditing: (v: string | null) => void }) {
  const t = TONE[s.display_tone];
  const [state, setState] = useState("maintenance");
  const [reason, setReason] = useState("");
  const [minutes, setMinutes] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const save = async () => {
    try {
      await api(`/api/admin/seats/${s.seat_id}/override`, {
        method: "POST",
        staff: true,
        body: { state, reason, expires_in_minutes: minutes ? Number(minutes) : null },
      });
      setEditing(null);
      setErr(null);
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : String(e));
    }
  };
  const clear = async () => {
    try {
      await api(`/api/admin/seats/${s.seat_id}/override?reason=${encodeURIComponent("ตรวจแล้วใช้งานได้ตามปกติ")}`, { method: "DELETE", staff: true });
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : String(e));
    }
  };
  return (
    <>
      <tr className="border-t border-slate-200" data-testid={`staff-seat-${s.seat_id}`}>
        <td className="px-3 py-1.5 font-bold">{s.seat_id}</td>
        <td className="px-3 py-1.5">
          <span className={`rounded border px-1.5 ${t.chip}`}>
            {t.glyph} {s.display_tone === "stale" ? "STALE" : s.display_state_label_th}
          </span>
        </td>
        <td className="px-3 py-1.5">{s.physical_state_label_th}</td>
        <td className="px-3 py-1.5">{s.is_stale ? <b className="text-red-700">STALE {ago(age)}</b> : ago(age)}</td>
        <td className="px-3 py-1.5">{CAMERA_TH[s.camera_health]}</td>
        <td className="px-3 py-1.5">{s.pending_report_count ? <b className="text-violet-700">{s.pending_report_count} รอตรวจ</b> : "—"}</td>
        <td className="px-3 py-1.5">{s.manual_override ? `${s.manual_override.state}: ${s.manual_override.reason}` : "—"}</td>
        <td className="px-3 py-1.5 whitespace-nowrap">
          <button className="rounded-lg border border-slate-300 px-2 py-0.5" onClick={() => setEditing(editing ? null : s.seat_id)} data-testid={`ov-edit-${s.seat_id}`}>
            ตั้งสถานะ
          </button>
          {s.manual_override && (
            <button className="ml-1 rounded-lg border border-red-300 px-2 py-0.5 text-red-700" onClick={clear} data-testid={`ov-clear-${s.seat_id}`}>
              ยกเลิก override
            </button>
          )}
        </td>
      </tr>
      {editing && (
        <tr className="bg-slate-50">
          <td colSpan={8} className="px-3 py-2">
            <div className="flex flex-wrap items-center gap-2">
              <select value={state} onChange={(e) => setState(e.target.value)} className="rounded border px-2 py-1">
                <option value="maintenance">Maintenance (ซ่อม/ทำความสะอาด)</option>
                <option value="unavailable">Unavailable (ปิดใช้งาน)</option>
                <option value="unknown">Unknown (รอตรวจ)</option>
              </select>
              <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="เหตุผล (จำเป็น)" className="min-w-[220px] flex-1 rounded border px-2 py-1" />
              <input value={minutes} onChange={(e) => setMinutes(e.target.value.replace(/\D/g, ""))} placeholder="หมดอายุ (นาที, เว้นว่าง=ไม่หมด)" className="w-56 rounded border px-2 py-1" />
              <button onClick={save} className="rounded bg-slate-900 px-3 py-1 text-white">บันทึก</button>
            </div>
            {err && <p className="mt-1 text-sm text-red-700">{err}</p>}
          </td>
        </tr>
      )}
    </>
  );
}

function EventsTab() {
  const [events, setEvents] = useState<EventRow[]>([]);
  const [cat, setCat] = useState("");
  const { meta } = useLive();
  useEffect(() => {
    api<{ events: EventRow[] }>(`/api/admin/events?limit=150${cat ? `&category=${cat}` : ""}`, { staff: true }).then((d) => setEvents(d.events));
  }, [cat, meta?.pending_reports, meta?.recent_resolved_reports?.[0]?.id, meta?.scenario?.run_id]);
  return (
    <div className="space-y-2">
      <select value={cat} onChange={(e) => setCat(e.target.value)} className="rounded border px-2 py-1 text-sm">
        <option value="">ทุกประเภท</option>
        <option value="report">report</option>
        <option value="report_resolved">report_resolved</option>
        <option value="override">override</option>
        <option value="scenario">scenario</option>
        <option value="state">state</option>
        <option value="security">security</option>
      </select>
      <div className="overflow-x-auto rounded-2xl border border-slate-300 bg-white">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-100 text-left">
            <tr>
              <th className="px-3 py-2">#</th>
              <th className="px-3 py-2">เวลา</th>
              <th className="px-3 py-2">ประเภท</th>
              <th className="px-3 py-2">รายละเอียด</th>
              <th className="px-3 py-2">แหล่ง</th>
              <th className="px-3 py-2">ผู้ทำ</th>
            </tr>
          </thead>
          <tbody>
            {events.map((e) => (
              <tr key={e.id} className="border-t border-slate-200">
                <td className="px-3 py-1">{e.id}</td>
                <td className="px-3 py-1 whitespace-nowrap">{thDateTime(e.created_at_utc)}</td>
                <td className="px-3 py-1">{e.category}</td>
                <td className="px-3 py-1">{e.detail}</td>
                <td className="px-3 py-1">{e.source}</td>
                <td className="px-3 py-1">{e.actor_id || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
