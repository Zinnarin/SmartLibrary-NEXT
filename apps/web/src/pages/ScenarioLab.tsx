import { useEffect, useState } from "react";
import { api, ApiError } from "../api";
import { thDateTime, thTime } from "../labels";
import { useLive } from "../live";
import { StaffGate } from "./StaffConsole";

interface ScenarioInfo {
  name: string;
  description_th: string;
}

export default function ScenarioLab() {
  return (
    <StaffGate>
      <Lab />
    </StaffGate>
  );
}

function Lab() {
  const { meta } = useLive();
  const [list, setList] = useState<ScenarioInfo[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [camera, setCamera] = useState("CAM-A");
  const [busy, setBusy] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);

  const load = async () => {
    const d = await api<any>("/api/demo/scenarios");
    setList(d.scenarios);
    setHistory(d.history);
    setStats(await api("/api/stats"));
  };
  useEffect(() => {
    load().catch((e) => setMsg(e instanceof ApiError ? e.message : String(e)));
  }, [meta?.scenario?.run_id]);
  useEffect(() => {
    const t = window.setInterval(() => api("/api/stats").then(setStats).catch(() => {}), 3000);
    return () => window.clearInterval(t);
  }, []);

  const run = async (name: string) => {
    setBusy(name);
    setMsg(null);
    try {
      await api("/api/demo/scenario", { method: "POST", staff: true, body: { scenario: name, camera_id: name === "CAMERA_LOST" ? camera : undefined } });
      setMsg(`เริ่ม ${name} แล้ว (ผ่าน backend + WebSocket)`);
    } catch (e) {
      setMsg(e instanceof ApiError ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  };
  const reset = async () => {
    if (!confirm("รีเซ็ตฐานข้อมูลสาธิตทั้งหมด (รายงาน/override/log จะถูกลบ) ?")) return;
    await api("/api/demo/reset", { method: "POST", staff: true });
    setMsg("รีเซ็ตแล้ว เริ่ม NORMAL ใหม่");
  };

  const sim = stats?.simulation;
  return (
    <div className="space-y-4">
      <div className="rounded-2xl border-4 border-dashed border-amber-500 bg-amber-50 p-4">
        <h2 className="text-xl font-bold text-amber-900">Scenario Lab — SIMULATION ONLY</h2>
        <p className="text-sm text-amber-900">
          ปุ่มเหล่านี้สั่ง backend ให้สร้าง “เฟรมจำลอง” ทุก 2 วินาที แล้วส่งผ่าน State Engine เดียวกับข้อมูล CV จริง (บันทึกใน SQLite) ไม่ใช่การตรวจจับจากกล้อง ·
          ข้อมูลจำลองแยกจากสถิติ CV จริงเสมอ
        </p>
        <p className="mt-1 text-sm">
          สถานการณ์ปัจจุบัน: <b data-testid="lab-active">{meta?.scenario?.name || "—"}</b> (เริ่ม {thTime(meta?.scenario?.started_at_utc)}) · กล้อง:{" "}
          {meta?.scenario && Object.entries(meta.scenario.cameras).map(([k, v]) => `${k}=${v}`).join(", ")}
        </p>
      </div>
      {msg && <p className="rounded-xl bg-slate-900 px-4 py-2 text-white" data-testid="lab-msg">{msg}</p>}
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {list.map((s) => (
          <div key={s.name} className={`rounded-2xl border-2 bg-white p-4 ${meta?.scenario?.name === s.name ? "border-amber-500" : "border-slate-300"}`}>
            <h3 className="font-mono text-lg font-bold">{s.name}</h3>
            <p className="mb-3 text-sm text-slate-700">{s.description_th}</p>
            {s.name === "CAMERA_LOST" && (
              <select value={camera} onChange={(e) => setCamera(e.target.value)} className="mb-2 mr-2 rounded border px-2 py-1 text-sm" data-testid="lab-camera">
                <option value="CAM-A">CAM-A (โซนเงียบ A)</option>
                <option value="CAM-B">CAM-B</option>
                <option value="CAM-C">CAM-C</option>
                <option value="ALL">ทุกกล้อง</option>
              </select>
            )}
            <button disabled={busy !== null} onClick={() => run(s.name)} className="rounded-xl bg-amber-600 px-4 py-2 font-semibold text-white hover:bg-amber-700 disabled:opacity-50" data-testid={`run-${s.name}`}>
              {busy === s.name ? "กำลังเริ่ม…" : "เริ่มสถานการณ์นี้"}
            </button>
          </div>
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-300 bg-white p-4">
          <h3 className="font-bold">สถิติจากสถานการณ์จำลอง (SIMULATED)</h3>
          {sim ? (
            <ul className="mt-2 space-y-1 text-sm" data-testid="lab-stats">
              <li className="text-xs text-amber-800">{sim.label}</li>
              <li>ที่นั่งทั้งหมด {sim.seats} · แสดงว่าง {sim.shown_available} · แนะนำได้ {sim.recommendable} · ไม่แน่ใจ/ข้อมูลเก่า {sim.unknown_or_stale}</li>
              <li>
                แสดงว่างแต่ “ความจริงจำลอง” ไม่ว่าง: <b>{sim.shown_available_but_truth_not_available.join(", ") || "ไม่มี"}</b>
                {sim.simulated_false_available_rate != null && ` (simulated rate ${sim.simulated_false_available_rate})`}
              </li>
              <li>
                ถูกแนะนำแต่ความจริงจำลองไม่ว่าง: <b>{sim.recommendable_but_truth_not_available.join(", ") || "ไม่มี"}</b>
              </li>
              <li>observation จำลองที่เก็บไว้: {sim.scenario_observations_stored}</li>
            </ul>
          ) : (
            <p className="text-sm text-slate-500">—</p>
          )}
          <h3 className="mt-4 font-bold">CV จริง</h3>
          <p className="text-sm">observation จาก CV จริง: {stats?.real_cv?.observations ?? 0} · {stats?.real_cv?.accuracy_note}</p>
        </div>
        <div className="rounded-2xl border border-slate-300 bg-white p-4">
          <h3 className="font-bold">ประวัติการรันสถานการณ์ (จาก backend)</h3>
          <ul className="mt-2 space-y-0.5 text-sm">
            {history.map((h) => (
              <li key={h.id}>
                #{h.id} {h.scenario} (base {h.base_scenario}) · {thDateTime(h.started_at_utc)} · {h.frames_emitted} เฟรม
              </li>
            ))}
          </ul>
          <button onClick={reset} className="mt-4 rounded-xl border-2 border-red-600 px-3 py-1.5 text-sm font-semibold text-red-700">
            รีเซ็ตฐานข้อมูลสาธิต
          </button>
        </div>
      </div>
    </div>
  );
}
