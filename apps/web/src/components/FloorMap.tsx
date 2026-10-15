import type { RouteResponse, Seat } from "../api";
import { SEAT_TYPE_TH, TONE } from "../labels";

const W = 52;
const H = 40;

interface Props {
  seats: Seat[];
  selected: string | null;
  onSelect: (id: string) => void;
  ranks: Record<string, number>;
  groupPair: string[];
  route: RouteResponse | null;
  dimReserved: boolean;
}

export default function FloorMap({ seats, selected, onSelect, ranks, groupPair, route, dimReserved }: Props) {
  const routePts = route ? route.points.map((p) => `${p.x},${p.y}`).join(" ") : "";
  return (
    <div className="overflow-x-auto" data-testid="map-scroll">
    <svg viewBox="0 0 1000 680" className="h-auto w-full min-w-[640px] select-none" role="group" aria-label="ผังที่นั่งสาธิต (ไม่ใช่ผังจริง)">
      <defs>
        <pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <rect width="8" height="8" fill="#f1f5f9" />
          <line x1="0" y1="0" x2="0" y2="8" stroke="#94a3b8" strokeWidth="3" />
        </pattern>
        <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#7c3aed" />
        </marker>
      </defs>
      {/* building shell */}
      <rect x="10" y="20" width="980" height="600" rx="14" fill="#ffffff" stroke="#334155" strokeWidth="3" />
      {/* windows (illustrative) */}
      <line x1="40" y1="20" x2="340" y2="20" stroke="#38bdf8" strokeWidth="8" />
      <text x="190" y="14" textAnchor="middle" fontSize="13" fill="#0369a1">หน้าต่าง</text>
      <line x1="990" y1="60" x2="990" y2="460" stroke="#38bdf8" strokeWidth="8" />
      <text x="978" y="260" textAnchor="middle" fontSize="13" fill="#0369a1" transform="rotate(90 978 260)">หน้าต่าง</text>

      {/* zones */}
      <Zone x={30} y={50} w={320} h={420} title="โซนเงียบ A" sub="Quiet · โต๊ะเดี่ยว/คอมพิวเตอร์" color="#eef2ff" />
      <Zone x={370} y={50} w={300} h={420} title="โซนกลุ่ม B" sub="Group · คุยได้เบา ๆ" color="#fdf4ff" />
      <Zone x={690} y={50} w={280} h={420} title="โซนริมหน้าต่าง C" sub="Window · โซฟา/โต๊ะบาร์" color="#f0fdfa" />

      {/* group tables in zone B */}
      <rect x="445" y="137" width="150" height="36" rx="6" fill="#e9d5ff" stroke="#a855f7" />
      <text x="520" y="160" textAnchor="middle" fontSize="12" fill="#6b21a8">โต๊ะกลุ่ม 1</text>
      <rect x="445" y="317" width="150" height="36" rx="6" fill="#e9d5ff" stroke="#a855f7" />
      <text x="520" y="340" textAnchor="middle" fontSize="12" fill="#6b21a8">โต๊ะกลุ่ม 2</text>
      {/* sofas in zone C */}
      <rect x="950" y="85" width="14" height="130" rx="5" fill="#99f6e4" />
      <rect x="950" y="245" width="14" height="130" rx="5" fill="#99f6e4" />
      <rect x="700" y="85" width="22" height="290" rx="5" fill="#ccfbf1" />
      <text x="711" y="230" textAnchor="middle" fontSize="11" fill="#0f766e" transform="rotate(-90 711 230)">โต๊ะบาร์</text>

      {/* corridor + entrance */}
      <rect x="30" y="500" width="940" height="80" rx="8" fill="#f8fafc" stroke="#cbd5e1" strokeDasharray="6 6" />
      <text x="80" y="545" fontSize="13" fill="#64748b">ทางเดินหลัก</text>
      <rect x="470" y="612" width="80" height="16" rx="4" fill="#0f172a" />
      <text x="562" y="646" textAnchor="start" fontSize="15" fontWeight="700" fill="#0f172a">◀ ทางเข้าหลัก (ENTRANCE)</text>

      {/* route */}
      {route && (
        <g aria-label="เส้นทางสาธิต">
          <polyline points={routePts} fill="none" stroke="#c4b5fd" strokeWidth="12" strokeLinecap="round" strokeLinejoin="round" />
          <polyline points={routePts} fill="none" stroke="#7c3aed" strokeWidth="4" strokeDasharray="10 8" strokeLinecap="round"
            strokeLinejoin="round" markerEnd="url(#arrow)" className="route-anim" />
          {route.points.slice(0, -1).map((p) => (
            <circle key={p.id} cx={p.x} cy={p.y} r="6" fill="#7c3aed" stroke="#fff" strokeWidth="2" />
          ))}
        </g>
      )}

      {/* seats */}
      {seats.map((s) => {
        const t = TONE[s.display_tone] || TONE.unknown;
        const rank = ranks[s.seat_id];
        const inPair = groupPair.includes(s.seat_id);
        const isSel = selected === s.seat_id;
        const dim = dimReserved && s.display_tone === "reserved";
        const label = `ที่นั่ง ${s.seat_id} ${t.label} ${SEAT_TYPE_TH[s.seat_type] || s.seat_type}${s.has_power ? " มีปลั๊ก" : ""}${
          s.pending_discrepancy ? " มีรายงานรอตรวจสอบ" : ""
        }${rank ? ` คำแนะนำอันดับ ${rank}` : ""}`;
        return (
          <g
            key={s.seat_id}
            transform={`translate(${s.floor_x - W / 2}, ${s.floor_y - H / 2})`}
            role="button"
            tabIndex={0}
            aria-label={label}
            aria-pressed={isSel}
            data-seat={s.seat_id}
            data-tone={s.display_tone}
            className="seat cursor-pointer focus:outline-none"
            opacity={dim ? 0.35 : 1}
            onClick={() => onSelect(s.seat_id)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onSelect(s.seat_id);
              }
            }}
          >
            {(rank || inPair) && <rect x={-6} y={-6} width={W + 12} height={H + 12} rx={10} fill="none" stroke="#16a34a" strokeWidth={4} className="pulse" />}
            {isSel && <rect x={-9} y={-9} width={W + 18} height={H + 18} rx={12} fill="none" stroke="#0f172a" strokeWidth={3} strokeDasharray="6 4" />}
            <rect width={W} height={H} rx={7} fill={t.fill} stroke={t.stroke} strokeWidth={2.5} strokeDasharray={s.display_tone === "stale" ? "5 3" : undefined} />
            <text x={W / 2} y={17} textAnchor="middle" fontSize="13" fontWeight="700" fill={t.text}>
              {s.seat_id}
            </text>
            <text x={W / 2} y={33} textAnchor="middle" fontSize="12" fill={t.text}>
              {t.glyph}
              {s.has_power ? " ⚡" : ""}
            </text>
            {s.pending_discrepancy && (
              <g transform={`translate(${W - 4}, -4)`}>
                <circle r="10" fill="#7c3aed" stroke="#fff" strokeWidth="2" />
                <text y="4.5" textAnchor="middle" fontSize="13" fontWeight="800" fill="#fff">!</text>
              </g>
            )}
            {rank && (
              <g transform="translate(-2, -2)">
                <circle r="11" fill="#15803d" stroke="#fff" strokeWidth="2" />
                <text y="4.5" textAnchor="middle" fontSize="12" fontWeight="800" fill="#fff">{rank}</text>
              </g>
            )}
          </g>
        );
      })}
    </svg>
    </div>
  );
}

function Zone({ x, y, w, h, title, sub, color }: { x: number; y: number; w: number; h: number; title: string; sub: string; color: string }) {
  return (
    <g>
      <rect x={x} y={y} width={w} height={h} rx="10" fill={color} stroke="#cbd5e1" />
      <text x={x + 12} y={y + h - 30} fontSize="16" fontWeight="700" fill="#334155">{title}</text>
      <text x={x + 12} y={y + h - 12} fontSize="12" fill="#64748b">{sub}</text>
    </g>
  );
}
