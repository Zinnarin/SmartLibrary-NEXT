import type { RecResponse } from "../api";

export interface MatchFilters {
  quiet: boolean;
  power: boolean;
  window: "" | "prefer" | "must";
  seat_type: string;
  group_size: 1 | 2;
}

interface Props {
  filters: MatchFilters;
  setFilters: (f: MatchFilters) => void;
  rec: RecResponse | null;
  loading: boolean;
  error: string | null;
  onPick: (seatId: string) => void;
  onRoute: (seatId: string) => void;
}

const KIND_STYLE: Record<string, string> = {
  must: "text-green-800",
  trust: "text-sky-800",
  prefer: "text-amber-800",
  group: "text-violet-800",
};
const KIND_ICON: Record<string, string> = { must: "✓", trust: "🛡", prefer: "★", group: "👥" };

export default function StudyMatch({ filters, setFilters, rec, loading, error, onPick, onRoute }: Props) {
  const toggle = (k: "quiet" | "power") => setFilters({ ...filters, [k]: !filters[k] });
  const relax = (f: string) => {
    if (f === "quiet") setFilters({ ...filters, quiet: false });
    if (f === "power") setFilters({ ...filters, power: false });
    if (f === "window") setFilters({ ...filters, window: "prefer" });
    if (f === "seat_type") setFilters({ ...filters, seat_type: "" });
  };
  return (
    <section className="rounded-2xl border border-slate-300 bg-white p-4 shadow-sm" data-testid="studymatch">
      <h2 className="text-lg font-bold text-slate-900">StudyMatch — หาที่นั่งที่ตรงเงื่อนไข</h2>
      <p className="mb-3 text-xs text-slate-500">แนะนำเฉพาะที่นั่ง “ว่าง” ที่ข้อมูลสดและน่าเชื่อถือเท่านั้น พร้อมเหตุผล</p>

      <div className="flex flex-wrap gap-2" role="group" aria-label="เงื่อนไขที่ต้องมี">
        <Chip on={filters.quiet} onClick={() => toggle("quiet")} testid="f-quiet">
          🤫 โซนเงียบ
        </Chip>
        <Chip on={filters.power} onClick={() => toggle("power")} testid="f-power">
          ⚡ มีปลั๊กไฟ
        </Chip>
        <select
          aria-label="หน้าต่าง"
          className="rounded-full border-2 border-slate-300 bg-white px-3 py-1 text-sm"
          value={filters.window}
          onChange={(e) => setFilters({ ...filters, window: e.target.value as MatchFilters["window"] })}
          data-testid="f-window"
        >
          <option value="">หน้าต่าง: ไม่สน</option>
          <option value="prefer">หน้าต่าง: ชอบ (ไม่บังคับ)</option>
          <option value="must">หน้าต่าง: ต้องมี</option>
        </select>
        <select
          aria-label="ประเภทที่นั่ง"
          className="rounded-full border-2 border-slate-300 bg-white px-3 py-1 text-sm"
          value={filters.seat_type}
          onChange={(e) => setFilters({ ...filters, seat_type: e.target.value })}
          data-testid="f-type"
        >
          <option value="">ทุกประเภท</option>
          <option value="single_desk">โต๊ะเดี่ยว</option>
          <option value="computer_desk">โต๊ะคอมพิวเตอร์</option>
          <option value="group_table">โต๊ะกลุ่ม</option>
          <option value="sofa">โซฟา</option>
        </select>
      </div>
      <div className="mt-2 flex gap-2" role="group" aria-label="จำนวนคน">
        <Chip on={filters.group_size === 1} onClick={() => setFilters({ ...filters, group_size: 1 })} testid="f-solo">
          👤 มาคนเดียว
        </Chip>
        <Chip on={filters.group_size === 2} onClick={() => setFilters({ ...filters, group_size: 2 })} testid="f-group2">
          👥 GroupFit: 2 คนนั่งติดกัน
        </Chip>
      </div>

      <div className="mt-4 space-y-3" aria-live="polite" data-testid="rec-results">
        {error && <p className="rounded bg-red-100 px-3 py-2 text-sm text-red-800">{error}</p>}
        {loading && !rec && <p className="text-sm text-slate-500">กำลังคำนวณ…</p>}
        {rec?.mode === "single" &&
          rec.results?.map((r, i) => (
            <article key={r.seat_id} className="rounded-xl border-2 border-green-600 bg-green-50/40 p-3" data-testid={`rec-${r.seat_id}`}>
              <div className="flex items-center justify-between gap-2">
                <h3 className="font-bold text-slate-900">
                  <span className="mr-2 inline-flex h-7 w-7 items-center justify-center rounded-full bg-green-700 text-white">{i + 1}</span>
                  {r.seat_id} · {r.seat_type_th} · โซน {r.zone_id}
                </h3>
                <div className="flex gap-1">
                  <button className="rounded-lg border border-slate-300 bg-white px-2 py-1 text-sm hover:bg-slate-50" onClick={() => onPick(r.seat_id)}>
                    ดูรายละเอียด
                  </button>
                  <button className="rounded-lg bg-violet-700 px-2 py-1 text-sm text-white" onClick={() => onRoute(r.seat_id)}>
                    🧭 นำทาง
                  </button>
                </div>
              </div>
              <ul className="mt-2 space-y-0.5 text-sm">
                {r.reasons.map((x, j) => (
                  <li key={j} className={KIND_STYLE[x.kind]}>
                    <span aria-hidden className="mr-1">{KIND_ICON[x.kind]}</span>
                    {x.text_th}
                  </li>
                ))}
              </ul>
            </article>
          ))}
        {rec?.mode === "group" &&
          rec.group_results?.map((g, i) => (
            <article key={g.seats.join("-")} className="rounded-xl border-2 border-green-600 bg-green-50/40 p-3" data-testid={`group-${g.seats.join("-")}`}>
              <div className="flex items-center justify-between gap-2">
                <h3 className="font-bold">
                  <span className="mr-2 inline-flex h-7 w-7 items-center justify-center rounded-full bg-green-700 text-white">{i + 1}</span>
                  {g.seats[0]} + {g.seats[1]}
                </h3>
                <button className="rounded-lg border border-slate-300 bg-white px-2 py-1 text-sm" onClick={() => onPick(g.seats[0])}>
                  ดูบนผัง
                </button>
              </div>
              <ul className="mt-2 space-y-0.5 text-sm">
                {g.reasons.map((x, j) => (
                  <li key={j} className={KIND_STYLE[x.kind]}>
                    <span aria-hidden className="mr-1">{KIND_ICON[x.kind]}</span>
                    {x.text_th}
                  </li>
                ))}
              </ul>
            </article>
          ))}
        {rec && rec.empty_message_th && (
          <div className="rounded-xl border-2 border-slate-400 bg-slate-50 p-3" data-testid="rec-empty">
            <p className="font-bold text-slate-900">⛔ {rec.empty_message_th}</p>
            <p className="text-sm text-slate-600">ระบบไม่แสดงที่นั่งที่ข้อมูลเก่า/ไม่แน่ใจ/มีรายงานค้างเป็น “ว่าง”</p>
            {rec.relax_suggestions && rec.relax_suggestions.length > 0 && (
              <div className="mt-2 space-y-1">
                <p className="text-sm font-semibold">ทางเลือก (คุณเลือกเองได้):</p>
                {rec.relax_suggestions.map((s) => (
                  <button key={s.filter} onClick={() => relax(s.filter)} className="block w-full rounded-lg border border-slate-300 bg-white px-2 py-1 text-left text-sm hover:bg-slate-100">
                    {s.text_th}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
        {rec && rec.excluded.length > 0 && (
          <details className="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-700" data-testid="rec-excluded">
            <summary className="cursor-pointer font-semibold">ที่นั่งที่ตรงเงื่อนไขแต่ไม่แนะนำ ({rec.excluded.reduce((a, e) => a + e.seats.length, 0)})</summary>
            <ul className="mt-1 space-y-0.5">
              {rec.excluded.map((e) => (
                <li key={e.reason}>
                  <b>{e.text_th}:</b> {e.seats.join(", ")}
                </li>
              ))}
            </ul>
          </details>
        )}
        {rec && (
          <p className="text-xs text-slate-500">
            {rec.score_note_th} · {rec.availability_note_th}
            {rec.adjacency_source_th ? ` · ${rec.adjacency_source_th}` : ""}
          </p>
        )}
      </div>
    </section>
  );
}

function Chip({ on, onClick, children, testid }: { on: boolean; onClick: () => void; children: React.ReactNode; testid?: string }) {
  return (
    <button
      onClick={onClick}
      aria-pressed={on}
      data-testid={testid}
      className={`rounded-full border-2 px-3 py-1 text-sm font-semibold transition ${
        on ? "border-green-700 bg-green-700 text-white" : "border-slate-300 bg-white text-slate-700 hover:border-slate-500"
      }`}
    >
      {children}
    </button>
  );
}
