import { useEffect, useState } from "react";
import { ago, thTime, TONE } from "./labels";
import { LiveProvider, useLive } from "./live";
import CvLab from "./pages/CvLab";
import ScenarioLab from "./pages/ScenarioLab";
import StaffConsole from "./pages/StaffConsole";
import StudentPage from "./pages/StudentPage";

type Route = "student" | "staff" | "lab" | "cv";

function useHashRoute(): [Route, (r: Route) => void] {
  const parse = (): Route => {
    const h = location.hash.replace("#/", "");
    return (["staff", "lab", "cv"].includes(h) ? h : "student") as Route;
  };
  const [r, setR] = useState<Route>(parse());
  useEffect(() => {
    const on = () => setR(parse());
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);
  return [r, (x) => (location.hash = `#/${x === "student" ? "" : x}`)];
}

export default function App() {
  return (
    <LiveProvider>
      <Shell />
    </LiveProvider>
  );
}

function Shell() {
  const [route, go] = useHashRoute();
  const { meta, conn, lastUpdate, serverNow, linkDown, lastContactAt } = useLive();
  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      {meta?.simulation_banner && (
        <div className="sim-banner sticky top-0 z-40 px-4 py-2 text-center text-sm font-extrabold tracking-wide text-white sm:text-base" role="alert" data-testid="sim-banner">
          ⚠ {meta.simulation_banner} · สถานการณ์: {meta.scenario?.name}
        </div>
      )}
      {linkDown && (
        <div className="bg-red-700 px-4 py-2 text-center text-sm font-bold text-white sm:text-base" role="alert" data-testid="link-down">
          ⚠ ขาดการเชื่อมต่อเซิร์ฟเวอร์ (ได้รับข้อมูลล่าสุด {lastContactAt ? thTime(new Date(lastContactAt).toISOString()) : "—"}) — ข้อมูลไม่เป็นปัจจุบัน:
          ที่นั่งแสดงเป็น “ข้อมูลไม่เป็นปัจจุบัน” และไม่มีคำแนะนำจนกว่าจะเชื่อมต่อใหม่ (ระบบลองเชื่อมต่อเองอัตโนมัติ)
        </div>
      )}
      <header className="border-b border-slate-300 bg-white">
        <div className="mx-auto flex max-w-[1400px] flex-wrap items-center gap-3 px-4 py-3">
          <div className="mr-auto">
            <h1 className="text-xl font-extrabold text-slate-900 sm:text-2xl">
              Smart Library <span className="text-green-700">NEXT</span>
            </h1>
            <p className="text-xs text-slate-500">Find. Verify. Study. — ต้นแบบในเครื่อง (local prototype)</p>
          </div>
          <nav className="flex flex-wrap gap-1" aria-label="เมนูหลัก">
            <NavBtn on={route === "student"} onClick={() => go("student")} testid="nav-student">นักศึกษา</NavBtn>
            <NavBtn on={route === "staff"} onClick={() => go("staff")} testid="nav-staff">
              เจ้าหน้าที่{meta?.pending_reports ? <span className="ml-1 rounded-full bg-violet-600 px-1.5 text-xs text-white">{meta.pending_reports}</span> : null}
            </NavBtn>
            <NavBtn on={route === "lab"} onClick={() => go("lab")} testid="nav-lab">Scenario Lab</NavBtn>
            <NavBtn on={route === "cv"} onClick={() => go("cv")} testid="nav-cv">CV Lab</NavBtn>
          </nav>
        </div>
        <StatusBar conn={conn} lastUpdate={lastUpdate} serverNow={serverNow} />
      </header>
      <main className="mx-auto max-w-[1400px] px-3 py-4 sm:px-4">
        {route === "student" && <StudentPage />}
        {route === "staff" && <StaffConsole />}
        {route === "lab" && <ScenarioLab />}
        {route === "cv" && <CvLab />}
      </main>
      <footer className="mx-auto max-w-[1400px] px-4 pb-6 text-xs text-slate-500">
        ผังและข้อมูลที่นั่งเป็นข้อมูลสาธิต ไม่ใช่ห้องสมุดจริง · ไม่เก็บภาพ/ตัวตนผู้ใช้ · ระบบ staff เป็น demo gate ไม่ใช่การยืนยันตัวตนจริง
      </footer>
    </div>
  );
}

function StatusBar({ conn, lastUpdate, serverNow }: { conn: string; lastUpdate: number | null; serverNow: number }) {
  const { meta, seats } = useLive();
  // counts are computed from what the browser actually shows (after the client-side freshness guard)
  const counts: Record<string, number> = {};
  seats.forEach((v) => {
    const k = v.display_tone === "stale" ? "stale" : v.display_state;
    counts[k] = (counts[k] || 0) + 1;
  });
  const recommendable = seats.filter((v) => v.is_recommendable).length;
  const order = ["available", "occupied", "reserved", "unknown", "stale", "maintenance", "unavailable"] as const;
  const connLabel = conn === "live" ? "● Live (WebSocket)" : conn === "polling" ? "◐ Polling สำรอง (WS หลุด)" : conn === "offline" ? "○ ออฟไลน์" : "… กำลังเชื่อมต่อ";
  const connCls = conn === "live" ? "text-green-700" : conn === "polling" ? "text-amber-700" : "text-red-700";
  const offline = meta?.cameras.filter((c) => c.source_mode === "scenario" && c.status !== "healthy") || [];
  return (
    <div className="border-t border-slate-200 bg-slate-50">
      <div className="mx-auto flex max-w-[1400px] flex-wrap items-center gap-x-4 gap-y-1 px-4 py-2 text-sm">
        <span className={`font-semibold ${connCls}`} data-testid="conn">{connLabel}</span>
        <span className="text-slate-600">
          อัปเดตล่าสุด {lastUpdate ? thTime(new Date(lastUpdate).toISOString()) : "—"} ({lastUpdate ? ago((Date.now() - lastUpdate) / 1000) : "—"})
        </span>
        <span className="text-slate-600">
          แหล่งข้อมูล: <b className={meta?.simulation_active ? "text-amber-700" : ""}>{meta?.simulation_active ? "SIMULATION (Scenario Lab)" : "ไม่มีแหล่งจำลอง"}</b>
        </span>
        <span className="flex flex-wrap gap-1" data-testid="counts">
          {order
            .filter((k) => counts[k])
            .map((k) => (
              <span key={k} className={`rounded-full border px-2 text-xs ${TONE[k].chip}`}>
                {TONE[k].glyph} {TONE[k].label} {counts[k]}
              </span>
            ))}
        </span>
        <span className="text-slate-600">แนะนำได้ {seats.length ? recommendable : "—"}/{seats.length || "—"}</span>
        {offline.length > 0 && (
          <span className="rounded bg-red-100 px-2 font-semibold text-red-800" data-testid="camera-warning">
            ⚠ กล้อง{offline.map((c) => ` ${c.camera_id}=${c.status === "offline" ? "ออฟไลน์" : "คุณภาพต่ำ"}`).join(",")} — ที่นั่งในมุมกล้องนี้จะไม่ถูกแนะนำ
          </span>
        )}
      </div>
    </div>
  );
}

function NavBtn({ on, onClick, children, testid }: { on: boolean; onClick: () => void; children: React.ReactNode; testid: string }) {
  return (
    <button onClick={onClick} data-testid={testid} aria-current={on ? "page" : undefined}
      className={`rounded-xl px-3 py-1.5 text-sm font-semibold ${on ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"}`}>
      {children}
    </button>
  );
}
