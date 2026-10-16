# P3 · 09 — Claude Code master prompt (Student Frontend)

How to use it:
1. Open the repository folder in Claude Code.
2. Make sure you are on `feature/v3-student`.
3. Paste everything inside the box below.

The prompt is self-contained.

```text
ROLE AND PROJECT
You are helping PERSON 3 (Student Frontend owner) of a 4-student team improve an EXISTING, working system:
Smart Library NEXT (private repo Zinnarin/SmartLibrary-NEXT). It shows library seat status only as far as evidence
supports it (unknown/stale instead of guessing available). Do NOT rebuild the system or replace the backend.
Web app: React 18 + TypeScript + Vite 6 + Tailwind 4 in apps/web (student side is MINE). Backend FastAPI
services/api (Person 2), Staff Console + e2e (Person 4), CV cv/ (Person 1). V2 baseline tag: v2-demo-baseline.

MY MISSION
Own the student-facing application: Floor Map, seat discovery, StudyMatch and GroupFit, navigation/usability,
realtime updates, correct source (SIMULATION vs CV) and freshness display, mobile-friendly use. Significant UI/UX
redesign, new student features, better interaction design and new recommendation experiences are allowed.
Never create an independent database/backend, never silently change API schemas, never present simulated data as real.

STEP 0 - INSPECT BEFORE CHANGING ANYTHING (report findings to me first)
1. git status; git branch --show-current (must be feature/v3-student); git fetch origin; git merge origin/main.
2. Read my package docs/team_v3/individual_handoff/P3_STUDENT_FRONTEND/01..08, the contract snapshot
   docs/team_v3/individual_handoff/SHARED_V3/03_SHARED_API_CONTRACTS.md (C0, C2, C4, C1c, PA, CT), the real
   recorded responses SHARED_V3/contract_examples/C2__*.json and C4__*.json, docs/team_v3/OWNERSHIP_MAP.csv, and
   docs/api_contract_v3.md if it exists (it overrides the snapshot).
3. Read the real code: apps/web/src/App.tsx, api.ts (single API client; parses session token <sid>.<exp>.<sig>),
   live.tsx (WS snapshot/delta/heartbeat, polling every 3 s, 10 s link timeout, BUG-011 browser TTL guard),
   labels.ts (zones A/B/C hard-coded), pages/StudentPage.tsx, components/FloorMap.tsx (zones hard-coded in SVG),
   SeatDetail.tsx (SeatCheck form today), StudyMatch.tsx, pages/CvLab.tsx, and apps/web/e2e/*.spec.ts for the
   data-testid values the tests depend on. Confirm every path exists.
4. Baseline: cd apps\web; npm ci; npm run build. Start the server (scripts\start_demo_windows.ps1) and run
   scripts\run_tests_windows.ps1 (expect Playwright 8/8). Before PR #16 is merged this writes into frozen
   presentation/screenshots/ and evidence/ - restore them with git restore and never commit them. Report exact output.

DISPLAY RULES (contract C2, must keep)
- A seat with is_recommendable=false (unknown, stale, camera offline/degraded, pending report, staff override,
  transition pending) must never look like a confirmed free seat.
- source="scenario" or meta.simulation_active => visibly SIMULATION. Only source="cv" may be called camera/CV data
  (today only LAB seats on the CV Lab page). No accuracy/probability percentages; rank_score is ordering only.
- Ages come from server_time_utc; keep the BUG-011 guard and WS/polling fallback.
- Wayfinder units are map units, not metres; keep disclaimer_th visible.

CHANGE LEVELS
GREEN (do it): any UI/UX redesign or new student feature using existing contract routes; PA-08 zones from /api/layout.
YELLOW (draft a change request for Person 4 BEFORE coding): new API field/endpoint (Person 2), live.tsx or
package.json changes (Person 4 approves), CvLab.tsx data changes (Person 1 approves), renaming data-testid values.
RED (all 4 approve): real CV seats on the student map (PA-03), relaxing any display safety rule.
Template: P3_STUDENT_FRONTEND/07_CHANGE_REQUEST_TEMPLATE.md.

HARD RULES
- Modify ONLY my files: apps/web/src/{App.tsx,api.ts,live.tsx*,labels.ts,main.tsx,styles.css},
  apps/web/src/pages/{StudentPage.tsx,CvLab.tsx*}, apps/web/src/components/{FloorMap.tsx,SeatDetail.tsx,StudyMatch.tsx},
  apps/web/{vite.config.ts,tsconfig.json,index.html,package.json*,package-lock.json*},
  apps/web/e2e/student_v3.spec.ts (* = needs co-approval). Never edit StaffConsole.tsx, ScenarioLab.tsx,
  SeatCheckPanel.tsx, other e2e specs, playwright.config.ts, services/**, cv/** or frozen V2 files.
- The UI must not compute seat state itself (except the existing BUG-011 safety guard).
- Never fabricate screenshots or results; never mark a test PASS without running it. Save screenshots in artifacts/.
- Do not merge to main.

WORK PLAN (one item at a time; test; report)
S1 source + freshness labels (#6); S2 mobile 360-390 px without horizontal page scroll, keyboard, clear empty/error
states; S3 clearer StudyMatch/GroupFit/Wayfinder without over-claiming; S4 PA-08 render zones from /api/layout with
identical demo result; S5 apps/web/e2e/student_v3.spec.ts (#8); S6 after Person 4's PR-A, use SeatCheckPanel in
SeatDetail.tsx keeping all data-testid values (#7); S7 align api.ts types with the contract.

BEFORE EACH PR
Run npm run build; pytest; with the server running scripts\run_tests_windows.ps1; scripts\check_ownership.py
--owner P3 --base origin/main; git status (no frozen changes). Give me exact outputs, before/after screenshots
(desktop + 390 px) and a PR description using .github/pull_request_template.md.
```
