export type Tone = "available" | "occupied" | "reserved" | "unknown" | "stale" | "unavailable" | "maintenance";

export interface Override {
  id: number;
  state: string;
  reason: string;
  actor_id: string;
  created_at_utc: string;
  expires_at_utc: string | null;
  report_id: number | null;
}

export interface Seat {
  seat_id: string;
  zone_id: string;
  seat_type: string;
  has_power: boolean;
  near_window: boolean;
  quiet_zone: boolean;
  floor_x: number;
  floor_y: number;
  camera_id: string;
  metadata_source: string;
  physical_state: string;
  physical_state_label_th: string;
  display_state: string;
  display_state_label_th: string;
  display_tone: Tone;
  source: string | null;
  observed_at_utc: string | null;
  ingested_at_utc: string | null;
  is_stale: boolean;
  camera_health: string;
  quality_flag: string | null;
  evidence_codes: string[];
  latest_candidate: string | null;
  transition_pending: boolean;
  state_since_utc: string | null;
  last_confident_state: string | null;
  last_confident_at_utc: string | null;
  belongings_review_flag: boolean;
  pending_discrepancy: boolean;
  pending_report_count: number;
  manual_override: Override | null;
  is_recommendable: boolean;
  not_recommendable_reasons: string[];
  not_recommendable_reasons_th: string[];
  revision: number;
}

export interface Meta {
  mode: string;
  simulation_active: boolean;
  simulation_banner: string | null;
  scenario: null | { run_id: number; name: string; base: string; started_at_utc: string; cameras: Record<string, string>; description_th: string };
  cameras: { camera_id: string; label_th: string; zone_id: string; source_mode: string; status: string }[];
  pending_reports: number;
  counts: Record<string, number>;
  recommendable: number;
  total_seats: number;
  recent_resolved_reports: PublicReport[];
  freshness_ttl_s: number;
}

export interface PublicReport {
  id: number;
  seat_id: string;
  reason: string;
  reason_th: string;
  created_at_utc: string;
  review_status: "pending" | "accepted" | "rejected";
  reviewed_at_utc: string | null;
  decision_reason: string | null;
  is_simulated: boolean;
  duplicate?: boolean;
}

export interface Reason {
  kind: "must" | "trust" | "prefer" | "group";
  text_th: string;
}

export interface SingleResult {
  seat_id: string;
  zone_id: string;
  seat_type: string;
  seat_type_th: string;
  rank_score: number;
  walk_units: number;
  reasons: Reason[];
}

export interface GroupResult {
  seats: [string, string];
  relation: string;
  note_th: string;
  rank_score: number;
  walk_units: number;
  reasons: Reason[];
}

export interface RecResponse {
  mode: "single" | "group";
  results?: SingleResult[];
  group_results?: GroupResult[];
  excluded: { reason: string; text_th: string; seats: string[] }[];
  empty_message_th?: string;
  relax_suggestions?: { filter: string; label_th: string; would_match: number; text_th: string }[];
  matching_candidates: number;
  score_note_th: string;
  availability_note_th: string;
  hard_constraint_rules_th: string[];
  adjacency_source_th?: string;
}

export interface RouteResponse {
  waypoints: string[];
  points: { id: string; label_th: string; x: number; y: number }[];
  edges: [string, string][];
  total_cost_units: number;
  disclaimer_th: string;
}

export class ApiError extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

const STAFF_KEY = "sl_staff_token";
const SESSION_KEY = "sl_session_token";

function store(): Storage | null {
  try {
    return window.sessionStorage;
  } catch {
    return null;
  }
}

export function getStaffToken(): string | null {
  return store()?.getItem(STAFF_KEY) ?? null;
}
export function setStaffToken(t: string | null) {
  const s = store();
  if (!s) return;
  if (t) s.setItem(STAFF_KEY, t);
  else s.removeItem(STAFF_KEY);
}

async function getSessionToken(): Promise<string> {
  const s = store();
  const cached = s?.getItem(SESSION_KEY);
  if (cached) {
    const exp = Number(cached.split(".")[1] || 0);
    if (exp * 1000 > Date.now() + 60_000) return cached;
  }
  const r = await fetch("/api/session");
  const j = await r.json();
  s?.setItem(SESSION_KEY, j.session_token);
  return j.session_token;
}

export async function api<T = any>(
  path: string,
  opts: { method?: string; body?: unknown; staff?: boolean; session?: boolean } = {},
): Promise<T> {
  const headers: Record<string, string> = {};
  if (opts.body !== undefined) headers["Content-Type"] = "application/json";
  if (opts.staff) headers["X-Staff-Token"] = getStaffToken() || "";
  if (opts.session) headers["X-Session-Token"] = await getSessionToken();
  const r = await fetch(path, { method: opts.method || "GET", headers, body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined });
  const text = await r.text();
  let data: any = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { error: text };
  }
  if (!r.ok) {
    if (r.status === 401 && opts.session) store()?.removeItem(SESSION_KEY);
    const msg = data?.message_th || data?.detail?.[0]?.msg || data?.error || `HTTP ${r.status}`;
    throw new ApiError(r.status, data?.error || String(r.status), msg);
  }
  return data as T;
}

export function newClientId(): string {
  const c = (globalThis as any).crypto;
  if (c?.randomUUID) return c.randomUUID();
  return "r" + Math.random().toString(36).slice(2) + Date.now().toString(36);
}
