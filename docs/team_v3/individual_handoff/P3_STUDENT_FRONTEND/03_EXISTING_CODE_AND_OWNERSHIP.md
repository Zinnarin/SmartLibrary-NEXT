# P3 · 03 — Existing code and ownership (Student Frontend)

Paths were verified with `git ls-files` on 2026-10-16. The rules live in `docs/team_v3/OWNERSHIP_MAP.csv` (first match wins). Check with `python scripts/check_ownership.py --owner P3 --base origin/main`.

## Files you own

| Path | Owner | Approval from | Status |
|---|---|---|---|
| `apps/web/src/App.tsx` | P3 | — | exists |
| `apps/web/src/api.ts` | P3 | — | exists (the single API client; types follow the contract) |
| `apps/web/src/live.tsx` | P3 | P4 | exists (WS + polling + BUG-011 guard) |
| `apps/web/src/labels.ts` | P3 | — | exists |
| `apps/web/src/main.tsx` | P3 | — | exists |
| `apps/web/src/styles.css` | P3 | — | exists |
| `apps/web/src/pages/StudentPage.tsx` | P3 | — | exists |
| `apps/web/src/pages/CvLab.tsx` | P3 | P1 | exists |
| `apps/web/src/components/FloorMap.tsx` | P3 | — | exists |
| `apps/web/src/components/SeatDetail.tsx` | P3 | — | exists (contains the SeatCheck form today) |
| `apps/web/src/components/StudyMatch.tsx` | P3 | — | exists |
| `apps/web/vite.config.ts` | P3 | — | exists (dev proxy `/api` + `/ws` → `127.0.0.1:8000`) |
| `apps/web/tsconfig.json` | P3 | — | exists |
| `apps/web/index.html` | P3 | — | exists |
| `apps/web/package.json` | P3 | P4 | exists |
| `apps/web/package-lock.json` | P3 | P4 | exists |
| `apps/web/e2e/student_v3.spec.ts` | P3 | — | new, planned (issue #8) |

Not yours, so do not edit:
- `apps/web/src/pages/StaffConsole.tsx` (P4).
- `apps/web/src/pages/ScenarioLab.tsx` (P4 + P2).
- `apps/web/src/components/SeatCheckPanel.tsx` (P4, new, planned).
- `apps/web/e2e/demo.spec.ts`, `reliability.spec.ts`, `server_restart.spec.ts` and `apps/web/playwright.config.ts` (P4; you approve the config).
- `services/**` (P2), `cv/**` (P1), and frozen V2 files.

## Code map (verified on `main` @ `edc7903`)

| File:line | Symbol | Notes |
|---|---|---|
| `App.tsx:9` | `type Route = "student" \| "staff" \| "lab" \| "cv"` | hash routing (`#/`, `#/staff`, `#/lab`, `#/cv`) |
| `App.tsx:33` | `Shell()` | SIMULATION banner (`data-testid="sim-banner"`), link-down banner (`link-down`), nav |
| `App.tsx:81` | `StatusBar()` | connection state (`conn`), counts (`counts`), camera warning (`camera-warning`; only scenario cameras today) |
| `api.ts:1–122` | `Tone`, `Override`, `Seat`, `Meta`, `PublicReport`, `RecResponse`, `RouteResponse` | TypeScript view of C2/C4. `Seat` omits `floor`, `age_s`, `state_for_s` and `belongings_for_s` |
| `api.ts:155` | `getSessionToken()` | caches the token in `sessionStorage["sl_session_token"]`; **parses the expiry from `token.split(".")[1]`** (C4) |
| `api.ts:168` | `api()` | adds `X-Staff-Token` / `X-Session-Token`; error message priority `message_th` → `detail[0].msg` → `error` |
| `live.tsx:22` | `LINK_TIMEOUT_MS = 10_000` | more than 10 s without a message → link down |
| `live.tsx:26` | `LiveProvider` | WS `snapshot`/`delta`/`heartbeat`; polling `GET /api/seats` every 3 s; backoff 1 → 15 s |
| `live.tsx:139` | `effective()` | **BUG-011 guard**: re-applies the TTL in the browser; on link-down marks seats stale and not recommendable (`LINK_DOWN`) |
| `labels.ts:3` / `20` | `TONE` / `ZONE_TH` | colours, glyphs and the hatch for `stale`; **zones A/B/C hard-coded** |
| `pages/StudentPage.tsx:19` | `StudentPage()` | calls `/api/recommendations`, `/api/seat-reports/mine`, `/api/route`; SeatWatch (line 99, in-app only); `sessionStorage["sl_my_reports"]` |
| `components/FloorMap.tsx:17` | `FloorMap` | SVG `viewBox 0 0 1000 680`; zones drawn by hard-coded `<Zone …>` (lines 40–42); seats at `floor_x`/`floor_y` |
| `components/SeatDetail.tsx:15` | `SeatDetail` | state chip, observed time, trust reasons, SIMULATION label (line 86), SeatCheck form `POST /api/seat-reports` (line 30) |
| `components/StudyMatch.tsx:29` | `StudyMatch` | filters, results, excluded summary, empty state + relax suggestions |
| `pages/CvLab.tsx:5` | `CvLab` | reads `/api/cv/status` keys (C1c) and `/api/cv/lab-seats` |

**`data-testid` values the e2e suites rely on** (keep them, or change them together with P4):
- Shell: `sim-banner`, `link-down`, `conn`, `counts`, `camera-warning`, `nav-student`, `nav-staff`, `nav-lab`, `nav-cv`.
- Seat detail: `seat-detail`, `seat-state`, `pending-badge`, `seat-observed`, `trust`, `route-btn`, `seatcheck-open`, `seatcheck-form`, `seatcheck-submit`, `my-reports`.
- Student page: `route-info`, `seatwatch`, `toast`, `map-scroll`.
- StudyMatch: `studymatch`, `f-window`, `f-type`, `rec-results`, `rec-empty`, `rec-excluded`.
- CV Lab: `cv-lab`, `cv-status`, `cv-library-status`.

## How to run

- **Build:** `cd apps\web; npm ci; npm run build`. The build runs `tsc --noEmit` and then `vite build` into `dist/`, which the server serves at `:8000`.
- **Dev with hot reload:** start the backend with `scripts\start_demo_windows.ps1`, then run `npm run dev` and open `http://127.0.0.1:5173`. Vite proxies `/api` and `/ws`.
- **e2e:** with the server on `:8000`, run `npx playwright test` from `apps/web`. It uses the locally installed Edge (`channel: msedge`).

## Tests that cover your module today

e2e (8, all passing):
- `demo.spec.ts`: professor demo path; WS blocked → polling; SeatWatch; CV Lab.
- `reliability.spec.ts`: BUG-011; the student journey with zero console errors; keyboard map.
- `server_restart.spec.ts`: real server kill and restart.

## Known limitations you inherit

1. Zones are hard-coded, so a new zone would not render (PA-08).
2. There is no CV data on the map; LAB seats are hidden by design.
3. The camera warning only considers scenario cameras.
4. Screen readers have not been tested.
5. The `Seat` type is a subset of the API.
6. Before PR #16 merges, Playwright writes screenshots into the frozen `presentation/screenshots/`. Restore them with `git restore presentation/screenshots/` and never commit them.
