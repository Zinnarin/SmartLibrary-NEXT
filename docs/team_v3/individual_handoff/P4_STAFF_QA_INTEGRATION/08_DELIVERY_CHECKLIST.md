# P4 · 08 — Delivery checklist

## A. Before every P4 PR (your own work)
- [ ] Branch merged with `origin/main`; no conflicts.
- [ ] `pytest`, `npm run build` and `run_tests_windows.ps1` (server running) are all green. Exact outputs are in the PR.
- [ ] `check_ownership.py --owner P4 --base origin/main` and `--audit` show no `BLOCK`. Co-approvals are requested.
- [ ] Frozen V2 files are untouched (`git status`).
- [ ] No test or CI check was weakened, skipped or deleted.
- [ ] The PR uses the template, has labels `person-4-qa` (+ `integration`), links issues, and notes where AI helped.

## B. Before merging anyone's PR (integration gate)
- [ ] CI green (`backend` and `frontend`).
- [ ] Ownership has no `BLOCK`. Every `REVIEW`/`OK*` file has its owner's approval in the PR.
- [ ] Contract changes have an approved CR, an updated `docs/api_contract_v3.md` and updated `contract_examples/`.
- [ ] A trial merge on `integration/v3-rN` passes the full regression (playbook section 4) plus the smoke for the touched contracts (section 5).
- [ ] The PR states clearly what is REAL, SIMULATED and BLOCKED. There is no unmeasured accuracy claim.
- [ ] Merged with **Squash and merge**, then an entry was added to `INTEGRATION_LOG.md`.

## C. Before the release tag
- [ ] Every FA row in `verification/TEAM_V3_ACCEPTANCE.csv` is filled in with evidence paths.
- [ ] `evidence/team_v3/final/` is complete and matches the tagged commit hash.
- [ ] The runbook and slides use only evidence-backed numbers, label SIMULATION, and state the CV status honestly.
- [ ] The repo is still **private**. No tokens, DB files, weights or media of people anywhere in history.
- [ ] Team approval is recorded in an issue, then the tag is created (and pushed only with the repo owner's authorization).
