# P2 · 08 — Delivery checklist (before every PR)

## Code and tests
- [ ] Branch merged with `origin/main`; no conflicts.
- [ ] `.venv\Scripts\python -m pytest -q`: 0 failed. The summary line is in the PR.
- [ ] `cd apps\web; npm run build` passes.
- [ ] With the server running, `scripts\run_tests_windows.ps1` gives Playwright all green. Frozen files are untouched or restored.
- [ ] The C1b import check (AC-P2-06) prints `C1b OK`.
- [ ] `check_ownership.py --owner P2 --base origin/main` shows no `BLOCK`. The output is in the PR.

## Contract
- [ ] No existing route, field, enum or error code was removed or renamed, and no meaning changed. Otherwise there is an approved RED CR.
- [ ] Every new visible thing is optional, documented in `docs/api_contract_v3.md`, and has a recorded example plus a test.
- [ ] Safety invariant tests (06) are still green with **unchanged assertions**.
- [ ] If there is a schema change: a migration from the V2 demo DB is tested, and a rollback note is included.

## Truth and data
- [ ] No DB files, tokens or `.env` in the diff. Demo token defaults are unchanged unless the change was agreed.
- [ ] Simulation and real data stay separated (`source` guard tests pass).
- [ ] Any performance number comes with its method, N and hardware.

## PR
- [ ] Opened with `.github/pull_request_template.md`, label `person-2-backend`, and `Closes #…`.
- [ ] Consumers who must react are listed (P1 / P3 / P4) and tagged for review.
- [ ] The PR notes where AI tools helped.
- [ ] I did not merge my own PR.
