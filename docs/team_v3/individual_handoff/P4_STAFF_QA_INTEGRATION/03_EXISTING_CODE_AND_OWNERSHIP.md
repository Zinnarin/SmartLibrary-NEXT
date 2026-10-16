# P4 · 03 — Existing code and ownership (Staff, QA & Integration)

Paths were verified with `git ls-files` on 2026-10-16. The rules live in `docs/team_v3/OWNERSHIP_MAP.csv` (first match wins). Check with `python scripts/check_ownership.py --owner P4 --base origin/main`.

## Files you own

| Path | Owner | Approval from | Status |
|---|---|---|---|
| `apps/web/src/pages/StaffConsole.tsx` | P4 | — | exists |
| `apps/web/src/pages/ScenarioLab.tsx` | P4 | P2 | exists |
| `apps/web/src/components/SeatCheckPanel.tsx` | P4 | P3 | new, planned (issue #10, PA-05) |
| `apps/web/e2e/demo.spec.ts` | P4 | — | exists |
| `apps/web/e2e/reliability.spec.ts` | P4 | — | exists |
| `apps/web/e2e/server_restart.spec.ts` | P4 | — | exists |
| `apps/web/e2e/staff_reliability_v3.spec.ts` | P4 | — | new, planned (issue #12) |
| `apps/web/e2e/artifacts.ts` | P4 | — | on `feature/v3-staff-qa` (PR #16), not on `main` yet |
| `apps/web/playwright.config.ts` | P4 | P3 | exists |
| `tests/test_reliability.py` | P4 | P2 | exists (7 tests) |
| `tests/test_artifact_isolation.py` | P4 | — | on `feature/v3-staff-qa` (PR #16), not on `main` yet |
| `tests/test_contract_v3.py` | P4 | P2 | new, planned (Q6) |
| `integration/smoke/README.md` | P4 | — | new, planned (Q8) |
| `integration/adapters/README.md` | P4 | — | new, planned (only if needed) |
| `scripts/run_tests_windows.ps1` | P4 | — | exists |
| `scripts/check_ownership.py` | P4 | — | exists |
| `scripts/start_demo_windows.ps1` | P4 | P2 | exists (BUG-013 safety logic) |
| `scripts/measure_ws_latency.py` | P4 | — | exists |
| `pytest.ini` | P4 | P2 | exists |
| `.github/workflows/ci.yml` | P4 | affected owner | exists |
| `.github/pull_request_template.md` | P4 | affected owner | exists |
| `.gitignore` | P4 | — | exists |
| `README.md` | P4 | — | exists |
| `docs/DEMO_RUNBOOK_TH.md` | P4 | — | exists |
| `docs/team_v3/OWNERSHIP_MAP.csv` | P4 | — | exists |
| `evidence/team_v3/V3_BASELINE_VERIFICATION.md` | P4 | — | exists |
| `verification/TEAM_V3_ACCEPTANCE.csv` | P4 | — | new, planned (FA-43) |
| `presentation/v3/README.md` | P4 | — | new, planned (V3 slides; never overwrite V2) |

Not yours: `services/**` (P2), `cv/**` (P1), the student UI (`App.tsx`, `api.ts`, `labels.ts`, `live.tsx`*, `pages/StudentPage.tsx`, `pages/CvLab.tsx`, `components/FloorMap.tsx`, `SeatDetail.tsx`, `StudyMatch.tsx`; P3), and the frozen V2 files.

\* You **co-approve** `apps/web/src/live.tsx` (BUG-011 guard) and `apps/web/package.json` / `package-lock.json`.

## Code map (verified on `main` @ `edc7903`)

| File:line | Symbol | Notes |
|---|---|---|
| `StaffConsole.tsx:30` | `StaffGate` | demo PIN, checked with `GET /api/admin/check`; token kept in `sessionStorage["sl_staff_token"]` |
| `StaffConsole.tsx:113` | `ReportsTab` | `GET /api/admin/seat-reports?status=pending\|all`; reloads when `meta.pending_reports` or the newest resolved report changes |
| `StaffConsole.tsx:145` | `DECISION_PRESETS` | canned reasons |
| `StaffConsole.tsx:150` | `ReportCard` | **`useState("maintenance")` on line 153 is the override default (issue #11)**; posts `resolve` with `override_state`/`override_minutes` |
| `StaffConsole.tsx:246` / `287` | `SeatsTab` / `SeatRow` | camera cards from `meta.cameras`; per-seat override set/clear (`POST`/`DELETE /api/admin/seats/{id}/override`) |
| `StaffConsole.tsx:359` | `EventsTab` | `GET /api/admin/events` |
| `ScenarioLab.tsx:12` | `ScenarioLab` | `/api/demo/scenarios`, `/api/demo/scenario`, `/api/demo/reset`, `/api/stats` |
| `apps/web/e2e/*.spec.ts` | 8 tests | demo path, WS-blocked → polling, SeatWatch, CV Lab, BUG-011, journey with 0 console errors, keyboard, real server restart |
| `tests/test_reliability.py` | 7 tests | unsafe-never-recommended property test, smoothing on scenario switch, override wins over the CV ingest path, `unknown` override, camera offline/stale, heartbeat timeout, seat detail/layout endpoints |
| `scripts/check_ownership.py` | `--audit`, `--owner P#\|auto --base` | ownership gate (CI runs `--audit`); `--frozen-clean` arrives with PR #16 |
| `scripts/run_tests_windows.ps1` | | on `main`: pytest → `evidence\pytest_output.txt` (**frozen**) + Playwright if `:8000` is up. PR #16 moves everything to `artifacts/` |

## Integration assets you maintain

- **The handoff packages:** `docs/team_v3/individual_handoff/`, including `FINAL_INTEGRATION_PLAYBOOK_TH.md` and `SHARED_V3/`.
- **Recorded contract examples:** `SHARED_V3/contract_examples/*.json`, 57 real responses from 2026-10-16.
- **Issues** #1–#15, labels, the PR template, CI, and the manual merge policy (no branch protection on the Free plan).

## Known limitations you inherit

1. The override default is `maintenance` (#11).
2. The staff identity is a single demo token, so the actor is always `staff-demo`.
3. Playwright does not run in CI (it needs local Edge), so you run it locally on every merge.
4. On `main`, the test tooling writes into frozen files until PR #16 merges.
5. The SeatCheck rate limit is per session only.
6. The camera warning in the shell covers only scenario cameras (P3's `App.tsx`).
7. There is no branch protection, so the merge policy depends on discipline.
