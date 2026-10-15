import { createContext, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { api, type Meta, type Seat } from "./api";

export type Conn = "connecting" | "live" | "polling" | "offline";

interface LiveState {
  seats: Seat[];
  byId: Record<string, Seat>;
  meta: Meta | null;
  conn: Conn;
  /** server clock estimate in ms (Date.now() corrected by the server offset) */
  serverNow: number;
  lastUpdate: number | null;
  refresh: () => Promise<void>;
  ageOf: (iso: string | null | undefined) => number | null;
  /** no message/poll from the server for LINK_TIMEOUT_MS: everything on screen is treated as not current */
  linkDown: boolean;
  lastContactAt: number | null;
}

// Heartbeat arrives every <=5 s and seat deltas every ~2 s, so 10 s of silence means the link is broken.
const LINK_TIMEOUT_MS = 10_000;

const Ctx = createContext<LiveState | null>(null);

export function LiveProvider({ children }: { children: ReactNode }) {
  const [seatMap, setSeatMap] = useState<Record<string, Seat>>({});
  const [meta, setMeta] = useState<Meta | null>(null);
  const [conn, setConn] = useState<Conn>("connecting");
  const [offset, setOffset] = useState(0);
  const [tick, setTick] = useState(Date.now());
  const [lastUpdate, setLastUpdate] = useState<number | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const pollRef = useRef<number | null>(null);
  const backoff = useRef(1000);
  const lastMsg = useRef(0);

  const applyServerTime = (iso: string | undefined) => {
    if (iso) setOffset(new Date(iso).getTime() - Date.now());
  };

  const refresh = async () => {
    try {
      const d = await api<{ server_time_utc: string; seats: Seat[]; meta: Meta }>("/api/seats");
      const m: Record<string, Seat> = {};
      d.seats.forEach((s) => (m[s.seat_id] = s));
      setSeatMap(m);
      setMeta(d.meta);
      applyServerTime(d.server_time_utc);
      setLastUpdate(Date.now());
      lastMsg.current = Date.now();
      return;
    } catch {
      setConn((c) => (c === "live" ? c : "offline"));
    }
  };

  useEffect(() => {
    let closed = false;
    let reconnectTimer: number | null = null;

    const startPolling = () => {
      if (pollRef.current != null) return;
      refresh();
      pollRef.current = window.setInterval(refresh, 3000);
    };
    const stopPolling = () => {
      if (pollRef.current != null) window.clearInterval(pollRef.current);
      pollRef.current = null;
    };

    const connect = () => {
      if (closed) return;
      const proto = location.protocol === "https:" ? "wss" : "ws";
      const ws = new WebSocket(`${proto}://${location.host}/ws/seats`);
      wsRef.current = ws;
      ws.onopen = () => {
        backoff.current = 1000;
      };
      ws.onmessage = (ev) => {
        const msg = JSON.parse(ev.data);
        lastMsg.current = Date.now();
        if (msg.type === "snapshot") {
          const m: Record<string, Seat> = {};
          (msg.seats as Seat[]).forEach((s) => (m[s.seat_id] = s));
          setSeatMap(m);
          setMeta(msg.meta);
          applyServerTime(msg.server_time_utc);
          setConn("live");
          setLastUpdate(Date.now());
          stopPolling();
        } else if (msg.type === "heartbeat") {
          applyServerTime(msg.server_time_utc);
        } else if (msg.type === "delta") {
          if (msg.seats?.length) {
            setSeatMap((prev) => {
              const next = { ...prev };
              (msg.seats as Seat[]).forEach((s) => (next[s.seat_id] = s));
              return next;
            });
          }
          if (msg.meta) setMeta(msg.meta);
          applyServerTime(msg.server_time_utc);
          setLastUpdate(Date.now());
        }
      };
      ws.onclose = () => {
        if (closed) return;
        setConn("polling");
        startPolling();
        reconnectTimer = window.setTimeout(connect, backoff.current);
        backoff.current = Math.min(backoff.current * 2, 15000);
      };
      ws.onerror = () => ws.close();
    };

    connect();
    const watchdog = window.setInterval(() => {
      setTick(Date.now());
      // a silent socket for >10 s is treated as broken: fall back to polling
      if (wsRef.current?.readyState === WebSocket.OPEN && lastMsg.current && Date.now() - lastMsg.current > 10000) {
        wsRef.current.close();
      }
    }, 1000);
    return () => {
      closed = true;
      window.clearInterval(watchdog);
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      stopPolling();
      wsRef.current?.close();
    };
  }, []);

  const value = useMemo<LiveState>(() => {
    const serverNow = tick + offset;
    const ttl = meta?.freshness_ttl_s ?? 30;
    const linkDown = lastMsg.current > 0 ? tick - lastMsg.current > LINK_TIMEOUT_MS : conn === "offline";
    // BUG-011 fix: the browser re-applies the TTL rule itself, so a dead server/network can never leave old seats green.
    const effective = (s: Seat): Seat => {
      const age = s.observed_at_utc ? (serverNow - new Date(s.observed_at_utc).getTime()) / 1000 : null;
      const tooOld = age != null && age > ttl;
      if (!tooOld && !linkDown) return s;
      const code = linkDown ? "LINK_DOWN" : "STALE";
      const reasons = s.not_recommendable_reasons.includes(code) ? s.not_recommendable_reasons : [...s.not_recommendable_reasons, code];
      const th = s.not_recommendable_reasons.includes(code)
        ? s.not_recommendable_reasons_th
        : [...s.not_recommendable_reasons_th, linkDown ? "ขาดการเชื่อมต่อเซิร์ฟเวอร์ — ข้อมูลไม่เป็นปัจจุบัน" : "ข้อมูลเก่าเกินเวลาที่กำหนด (stale)"];
      return {
        ...s,
        is_stale: true,
        is_recommendable: false,
        display_tone: s.manual_override ? s.display_tone : "stale",
        not_recommendable_reasons: reasons,
        not_recommendable_reasons_th: th,
      };
    };
    const byId: Record<string, Seat> = {};
    Object.values(seatMap).forEach((s) => (byId[s.seat_id] = effective(s)));
    const seats = Object.values(byId).sort((a, b) => a.seat_id.localeCompare(b.seat_id));
    return {
      seats,
      byId,
      meta,
      conn,
      serverNow,
      lastUpdate,
      refresh,
      ageOf: (iso) => (iso ? Math.max(0, (serverNow - new Date(iso).getTime()) / 1000) : null),
      linkDown,
      lastContactAt: lastMsg.current || null,
    };
  }, [seatMap, meta, conn, tick, offset, lastUpdate]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useLive(): LiveState {
  const v = useContext(Ctx);
  if (!v) throw new Error("LiveProvider missing");
  return v;
}
