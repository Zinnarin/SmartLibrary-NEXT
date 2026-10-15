import { useEffect, useMemo, useRef, useState } from "react";
import { api, ApiError, type PublicReport, type RecResponse, type RouteResponse } from "../api";
import FloorMap from "../components/FloorMap";
import SeatDetail from "../components/SeatDetail";
import StudyMatch, { type MatchFilters } from "../components/StudyMatch";
import { TONE } from "../labels";
import { useLive } from "../live";

const MY_REPORTS_KEY = "sl_my_reports";

function loadMine(): number[] {
  try {
    return JSON.parse(sessionStorage.getItem(MY_REPORTS_KEY) || "[]");
  } catch {
    return [];
  }
}

export default function StudentPage() {
  const { seats, byId, meta, lastUpdate, linkDown } = useLive();
  const [selected, setSelected] = useState<string | null>(null);
  const [filters, setFilters] = useState<MatchFilters>({ quiet: false, power: false, window: "", seat_type: "", group_size: 1 });
  const [rec, setRec] = useState<RecResponse | null>(null);
  const [recErr, setRecErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [route, setRoute] = useState<RouteResponse | null>(null);
  const [dimReserved, setDimReserved] = useState(false);
  const [myReports, setMyReports] = useState<PublicReport[]>([]);
  const [toast, setToast] = useState<string | null>(null);
  const [watch, setWatch] = useState(false);
  const watchPrev = useRef<Set<string> | null>(null);
  const lastFetch = useRef(0);
  const seenResolved = useRef<Set<number>>(new Set());

  const query = useMemo(() => {
    const p = new URLSearchParams();
    if (filters.quiet) p.set("quiet", "true");
    if (filters.power) p.set("power", "true");
    if (filters.window) p.set("window", filters.window);
    if (filters.seat_type) p.set("seat_type", filters.seat_type);
    p.set("group_size", String(filters.group_size));
    return p.toString();
  }, [filters]);

  const fetchRec = async () => {
    lastFetch.current = Date.now();
    setLoading(true);
    try {
      setRec(await api<RecResponse>(`/api/recommendations?${query}`));
      setRecErr(null);
    } catch (e) {
      setRec(null); // never keep showing recommendations that can no longer be verified
      setRecErr(e instanceof ApiError ? e.message : "เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ จึงไม่แสดงคำแนะนำ");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRec();
  }, [query]);

  // re-rank whenever live seat data changes (throttled)
  useEffect(() => {
    if (!lastUpdate) return;
    const wait = Math.max(0, 1200 - (Date.now() - lastFetch.current));
    const t = window.setTimeout(fetchRec, wait);
    return () => window.clearTimeout(t);
  }, [lastUpdate]);

  // load this browser-session's own anonymous reports
  const refreshMine = async () => {
    if (!loadMine().length) return;
    try {
      const d = await api<{ reports: PublicReport[] }>("/api/seat-reports/mine", { session: true });
      setMyReports(d.reports);
    } catch {
      /* ignore */
    }
  };
  useEffect(() => {
    refreshMine();
  }, []);

  // notify when staff resolves one of *my* reports (pushed via WebSocket meta)
  useEffect(() => {
    const mine = new Set(loadMine());
    for (const r of meta?.recent_resolved_reports || []) {
      if (mine.has(r.id) && !seenResolved.current.has(r.id)) {
        seenResolved.current.add(r.id);
        if (myReports.find((m) => m.id === r.id && m.review_status === "pending")) {
          setToast(`รายงาน #${r.id} (${r.seat_id}): ${r.review_status === "accepted" ? "เจ้าหน้าที่ยืนยันแล้ว" : "เจ้าหน้าที่ตรวจแล้วไม่พบปัญหา"} — ${r.decision_reason}`);
        }
        refreshMine();
      }
    }
  }, [meta, myReports]);

  // SeatWatch: in-app only. Alerts when a seat newly appears among the verified matches. Never reserves/holds a seat.
  useEffect(() => {
    if (!rec || rec.mode !== "single") return;
    const ids = new Set((rec.results || []).map((r) => r.seat_id));
    if (watch && watchPrev.current) {
      const fresh = [...ids].filter((id) => !watchPrev.current!.has(id));
      if (fresh.length) setToast(`🔔 SeatWatch: ${fresh.join(", ")} ว่างและยืนยันแล้วตามเงื่อนไข (แจ้งในแอปเท่านั้น ไม่ได้จอง/กันที่นั่งให้)`);
    }
    watchPrev.current = ids;
  }, [rec, watch]);

  const shownRec = linkDown ? null : rec;
  const shownErr = linkDown ? "ขาดการเชื่อมต่อเซิร์ฟเวอร์ — ไม่แสดงคำแนะนำเพราะยืนยันความสดของข้อมูลไม่ได้" : recErr;
  const ranks: Record<string, number> = {};
  let pair: string[] = [];
  if (shownRec?.mode === "single") shownRec.results?.forEach((r, i) => (ranks[r.seat_id] = i + 1));
  if (shownRec?.mode === "group" && shownRec.group_results?.[0]) pair = shownRec.group_results[0].seats;

  const toggleRoute = async (id: string) => {
    if (route && route.points[route.points.length - 1].id === `SEAT:${id}`) {
      setRoute(null);
      return;
    }
    try {
      setRoute(await api<RouteResponse>(`/api/route?from=ENTRANCE&to=${id}`));
      setSelected(id);
    } catch (e) {
      setToast(e instanceof ApiError ? e.message : "หาเส้นทางไม่ได้");
    }
  };

  const onReported = (r: PublicReport) => {
    const mine = loadMine();
    if (!mine.includes(r.id)) sessionStorage.setItem(MY_REPORTS_KEY, JSON.stringify([...mine, r.id]));
    setMyReports((prev) => [r, ...prev.filter((p) => p.id !== r.id)]);
    setToast(r.duplicate ? `รายงาน #${r.id} ถูกส่งไปแล้วก่อนหน้านี้` : `ส่งรายงาน #${r.id} แล้ว — รอเจ้าหน้าที่ตรวจสอบ (สถานะที่นั่งยังไม่เปลี่ยนจนกว่าจะตรวจ)`);
    fetchRec();
  };

  useEffect(() => {
    if (!toast) return;
    const t = window.setTimeout(() => setToast(null), 7000);
    return () => window.clearTimeout(t);
  }, [toast]);

  const seat = selected ? byId[selected] : null;
  const routeTo = route ? route.points[route.points.length - 1].id.replace("SEAT:", "") : null;

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1.6fr)_minmax(340px,1fr)]">
      <div className="space-y-3">
        <section className="rounded-2xl border border-slate-300 bg-white p-2 shadow-sm sm:p-3">
          <div className="flex flex-wrap items-center justify-between gap-2 px-1 pb-2">
            <h2 className="text-lg font-bold">ผังที่นั่ง (ผังสาธิต)</h2>
            <label className="flex items-center gap-1 text-sm text-slate-600">
              <input type="checkbox" checked={dimReserved} onChange={(e) => setDimReserved(e.target.checked)} />
              ซ่อน/จางที่นั่ง “พบสิ่งของ”
            </label>
          </div>
          {seats.length === 0 ? (
            <p className="p-8 text-center text-slate-500">กำลังโหลดข้อมูลที่นั่ง…</p>
          ) : (
            <FloorMap seats={seats} selected={selected} onSelect={setSelected} ranks={ranks} groupPair={pair} route={route} dimReserved={dimReserved} />
          )}
          <Legend />
          {route && (
            <p className="mt-2 rounded-lg bg-violet-50 px-3 py-2 text-sm text-violet-900" data-testid="route-info">
              🧭 Wayfinder: ทางเข้า → ผ่าน {route.waypoints.length - 1} จุดทางเดิน (waypoint) → ที่นั่ง {routeTo} · ระยะ {route.total_cost_units.toFixed(0)} หน่วยผัง · {route.disclaimer_th}
            </p>
          )}
        </section>
      </div>
      <div className="space-y-4">
        {seat && (
          <SeatDetail
            seat={seat}
            onClose={() => setSelected(null)}
            onRoute={toggleRoute}
            routeActive={routeTo === seat.seat_id}
            onReported={onReported}
            myReports={myReports}
          />
        )}
        <StudyMatch filters={filters} setFilters={setFilters} rec={shownRec} loading={loading} error={shownErr} onPick={setSelected} onRoute={toggleRoute} />
        <label className="flex items-start gap-2 rounded-2xl border border-slate-300 bg-white p-3 text-sm shadow-sm" data-testid="seatwatch">
          <input type="checkbox" checked={watch} onChange={(e) => { setWatch(e.target.checked); watchPrev.current = null; }} className="mt-1" />
          <span>
            <b>🔔 SeatWatch</b> — แจ้งในแอปเมื่อมีที่นั่ง “ว่างที่ยืนยันแล้ว” ใหม่ตรงเงื่อนไขที่เลือก
            <span className="block text-xs text-slate-500">แจ้งเตือนเฉพาะในหน้านี้ ไม่ส่ง notification ของระบบ และไม่ได้จองหรือกันที่นั่งให้</span>
          </span>
        </label>
      </div>
      {toast && (
        <div role="status" className="fixed bottom-4 left-1/2 z-50 w-[min(92vw,560px)] -translate-x-1/2 rounded-xl bg-slate-900 px-4 py-3 text-white shadow-xl" data-testid="toast">
          {toast}
        </div>
      )}
    </div>
  );
}

function Legend() {
  const order: (keyof typeof TONE)[] = ["available", "occupied", "reserved", "unknown", "stale", "maintenance", "unavailable"];
  return (
    <div className="mt-2 flex flex-wrap gap-2 px-1 text-xs" aria-label="คำอธิบายสี">
      {order.map((k) => (
        <span key={k} className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 ${TONE[k].chip}`}>
          <span aria-hidden>{TONE[k].glyph}</span>
          {TONE[k].label}
        </span>
      ))}
      <span className="inline-flex items-center gap-1 rounded-full border border-violet-600 bg-violet-100 px-2 py-0.5 text-violet-900">! มีรายงานรอตรวจ</span>
      <span className="inline-flex items-center gap-1 rounded-full border border-green-700 px-2 py-0.5 text-green-800">① ที่แนะนำ</span>
      <span className="text-slate-500">⚡ = มีปลั๊ก</span>
    </div>
  );
}
