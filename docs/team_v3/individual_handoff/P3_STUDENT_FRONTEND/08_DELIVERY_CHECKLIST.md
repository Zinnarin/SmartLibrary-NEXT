# P3 · 08 — Delivery checklist (before every PR)

## Code and tests
- [ ] Branch merged with `origin/main`; no conflicts.
- [ ] `npm run build` passes. The output is in the PR.
- [ ] With the server running, `scripts\run_tests_windows.ps1` passes: the 8 V2 specs, plus `student_v3.spec.ts` when present.
- [ ] `.venv\Scripts\python -m pytest -q` is still green.
- [ ] `check_ownership.py --owner P3 --base origin/main` shows no `BLOCK`. Approvals from P4 or P1 are noted where needed.
- [ ] `git status` shows no changes in `evidence/`, `presentation/` or `verification/` (restore Playwright screenshots).

## Contract and honesty
- [ ] Only contract routes are called, through `api.ts`. No new backend, DB or hard-coded seat states.
- [ ] SIMULATION is labelled wherever seat data appears. CV appears only where `source = "cv"`.
- [ ] Seats that are not recommendable never look like confirmed free seats. No percentages.
- [ ] The BUG-011 guard in `live.tsx` is intact (test passes).
- [ ] Every `data-testid` in `03_…` still exists, or P4 changed the specs together with me.

## Evidence
- [ ] Before/after screenshots (desktop and 390 px mobile) saved in `artifacts/` and attached to the PR. **Not** in `presentation/`.
- [ ] Any user feedback is described honestly (how many people, what they said). It is not called a user study.

## PR
- [ ] Opened with `.github/pull_request_template.md`, label `person-3-frontend`, and `Closes #…`.
- [ ] The PR notes where AI tools helped.
- [ ] I did not merge my own PR.
