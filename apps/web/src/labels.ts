import type { Tone } from "./api";

export const TONE: Record<Tone, { label: string; glyph: string; fill: string; stroke: string; text: string; chip: string }> = {
  available: { label: "ว่าง", glyph: "✓", fill: "#dcfce7", stroke: "#15803d", text: "#14532d", chip: "bg-green-100 text-green-900 border-green-700" },
  occupied: { label: "มีคนนั่ง", glyph: "●", fill: "#fee2e2", stroke: "#b91c1c", text: "#7f1d1d", chip: "bg-red-100 text-red-900 border-red-700" },
  reserved: { label: "พบสิ่งของ / อาจถูกจับจอง", glyph: "◆", fill: "#fef3c7", stroke: "#b45309", text: "#78350f", chip: "bg-amber-100 text-amber-900 border-amber-700" },
  unknown: { label: "ไม่แน่ใจ", glyph: "?", fill: "#e2e8f0", stroke: "#475569", text: "#1e293b", chip: "bg-slate-200 text-slate-800 border-slate-600" },
  stale: { label: "ข้อมูลไม่เป็นปัจจุบัน", glyph: "⏱", fill: "url(#hatch)", stroke: "#64748b", text: "#334155", chip: "bg-slate-100 text-slate-700 border-slate-500 border-dashed" },
  unavailable: { label: "ปิดใช้งาน (เจ้าหน้าที่)", glyph: "✕", fill: "#1f2937", stroke: "#030712", text: "#f9fafb", chip: "bg-gray-800 text-white border-black" },
  maintenance: { label: "ซ่อม/ทำความสะอาด", glyph: "🔧", fill: "#dbeafe", stroke: "#1d4ed8", text: "#1e3a8a", chip: "bg-blue-100 text-blue-900 border-blue-700" },
};

export const SEAT_TYPE_TH: Record<string, string> = {
  single_desk: "โต๊ะเดี่ยว",
  computer_desk: "โต๊ะคอมพิวเตอร์",
  group_table: "โต๊ะกลุ่ม",
  sofa: "โซฟา",
};

export const ZONE_TH: Record<string, string> = { A: "โซนเงียบ A", B: "โซนกลุ่ม B", C: "โซนริมหน้าต่าง C" };

export const CAMERA_TH: Record<string, string> = {
  healthy: "ปกติ",
  degraded: "คุณภาพต่ำ",
  offline: "ออฟไลน์",
  unknown: "ไม่ทราบ",
  never_seen: "ยังไม่เคยส่งข้อมูล",
};

export const REPORT_REASONS: { value: string; label: string }[] = [
  { value: "reported_occupied", label: "มีคนนั่งอยู่จริง" },
  { value: "belongings_present", label: "มีสิ่งของวางอยู่" },
  { value: "seat_inaccessible", label: "เข้าไปนั่งไม่ได้ / ที่นั่งชำรุด" },
  { value: "other", label: "อื่น ๆ" },
];

const timeFmt = new Intl.DateTimeFormat("th-TH", { timeZone: "Asia/Bangkok", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
const dateTimeFmt = new Intl.DateTimeFormat("th-TH", {
  timeZone: "Asia/Bangkok",
  day: "numeric",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
});

export function thTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  return timeFmt.format(new Date(iso));
}
export function thDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  return dateTimeFmt.format(new Date(iso));
}

export function ago(seconds: number | null | undefined): string {
  if (seconds == null || !isFinite(seconds)) return "—";
  const s = Math.max(0, Math.round(seconds));
  if (s < 60) return `${s} วินาทีที่แล้ว`;
  if (s < 3600) return `${Math.floor(s / 60)} นาที ${s % 60} วินาทีที่แล้ว`;
  return `${Math.floor(s / 3600)} ชม. ${Math.floor((s % 3600) / 60)} นาทีที่แล้ว`;
}

export function duration(seconds: number | null | undefined): string {
  if (seconds == null || !isFinite(seconds)) return "—";
  const s = Math.max(0, Math.round(seconds));
  if (s < 60) return `${s} วินาที`;
  if (s < 3600) return `${Math.floor(s / 60)} นาที`;
  return `${Math.floor(s / 3600)} ชม. ${Math.floor((s % 3600) / 60)} นาที`;
}
