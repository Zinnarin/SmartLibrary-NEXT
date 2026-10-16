# P3 · 06 — Acceptance criteria (Student Frontend)

**PASS** means you ran the check on your branch and the real output (and screenshots, where listed) is in the PR.

## Mandatory (every P3 PR)

| ID | Criterion | Command / check | Pass condition |
|---|---|---|---|
| AC-P3-01 | TypeScript and build | `cd apps\web; npm run build` | exit 0 (`tsc --noEmit` clean) |
| AC-P3-02 | Browser regression | server running → `powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1` | the 8 V2 specs plus `student_v3.spec.ts` pass, 0 flaky |
| AC-P3-03 | Backend untouched and green | `.venv\Scripts\python -m pytest -q` | 0 failed |
| AC-P3-04 | Ownership | `.venv\Scripts\python scripts\check_ownership.py --owner P3 --base origin/main` | no `BLOCK`; `live.tsx`/`package*.json` approved by P4 and `CvLab.tsx` by P1 when touched |
| AC-P3-05 | Frozen files | after the test run: `git status --short -- evidence presentation verification` | prints nothing (restore before committing) |

## Functional (the mission)

| ID | Criterion | Pass condition |
|---|---|---|
| AC-P3-10 | Source and freshness (issue #6) | every seat view shows the source (SIMULATION or CV) and the data age; `unknown`, `stale`, camera offline/degraded, pending report and override never look like a confirmed free seat. Screenshots before/after in the PR (`artifacts/`). |
| AC-P3-11 | BUG-011 still holds | `reliability.spec.ts` BUG-011 test passes: server unreachable → seats not shown as fresh, recommendations withdrawn; reconnect restores |
| AC-P3-12 | Mobile | no horizontal page scroll at 360 px and 390 px on the student page (asserted in e2e); the map stays usable (scroll inside `map-scroll` allowed) |
| AC-P3-13 | Keyboard | Tab reaches seats and Enter opens the detail (existing test) plus any new interactive element |
| AC-P3-14 | Student flow e2e (issue #8) | `student_v3.spec.ts`: quiet + power → reasons → GroupFit → Wayfinder → SeatCheck → the seat updates via WS **without reload**; 0 console errors |
| AC-P3-15 | Honest wording | no accuracy or probability percentages; `rank_score` never shown as %; Wayfinder shows `disclaimer_th`; GroupFit says adjacency is hand-recorded demo data |
| AC-P3-16 | SeatCheck integration (issue #7, after P4 PR-A) | `SeatDetail.tsx` uses `SeatCheckPanel`; every listed `data-testid` still present; `demo.spec.ts` + `reliability.spec.ts` pass |
| AC-P3-17 | PA-08 zones from `/api/layout` | the map renders the same zones as V2 with demo data (screenshot comparison); a zone added in a test fixture renders without code changes |
