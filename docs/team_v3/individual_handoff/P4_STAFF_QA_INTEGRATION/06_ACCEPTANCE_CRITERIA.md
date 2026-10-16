# P4 · 06 — Acceptance criteria (Staff, QA & Integration)

Your own PRs must meet the "Mandatory" and "Functional" rows below. The release must meet **all** of `SHARED_V3/07_FINAL_ACCEPTANCE_CRITERIA.md` (FA-01…FA-52). Those are your integration acceptance criteria.

## Mandatory (every P4 PR)

| ID | Criterion | Command / check | Pass condition |
|---|---|---|---|
| AC-P4-01 | No regression | `.venv\Scripts\python -m pytest -q` | 0 failed |
| AC-P4-02 | Build | `cd apps\web; npm run build` | exit 0 |
| AC-P4-03 | Browser regression | server running → `powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1` | all specs pass, 0 flaky; after PR #16, ends with `frozen-clean: OK` |
| AC-P4-04 | Ownership | `.venv\Scripts\python scripts\check_ownership.py --owner P4 --base origin/main` and `--audit` | no `BLOCK`; co-approvals recorded (P3 for `playwright.config.ts`/`SeatCheckPanel.tsx`, P2 for `ScenarioLab.tsx`/`test_reliability.py`/`pytest.ini`/`start_demo_windows.ps1`) |
| AC-P4-05 | CI honesty | the PR diff of `.github/workflows/ci.yml` | no check removed, skipped or made `continue-on-error` to turn red into green |

## Functional (your module)

| ID | Criterion | Pass condition |
|---|---|---|
| AC-P4-10 | Artifact isolation on `main` (issue #9) | after PR #16 merges: the full test script on `main` leaves `evidence/`, `presentation/`, `verification/` unchanged and prints `frozen-clean: OK` |
| AC-P4-11 | PR-A `SeatCheckPanel` (issue #10) | the component exists with the agreed props; unused until P3's PR-B; build + all e2e pass; same `data-testid` values |
| AC-P4-12 | Override semantics (issue #11) | confirming a "someone is sitting" report defaults to `unknown` (pending inspection); the UI wording matches; covered by e2e |
| AC-P4-13 | Staff reliability e2e (issue #12) | `staff_reliability_v3.spec.ts` covers: report → pending (seat leaves recommendations, physical state unchanged) → staff resolve with a reason → override → student page updates via WS **without reload within 5 s**; duplicate report → 429; wrong staff token → 401; override expiry returns the seat to sensor state; server kill → no green seats within the 10 s link timeout |
| AC-P4-14 | Contract tests | `tests/test_contract_v3.py`: for every file in `contract_examples/`, the live response has the same status, the same keys and the same JSON types (volatile values ignored); fails when a field is renamed in a test fixture |
| AC-P4-15 | Smoke | `integration/smoke/` reproduces playbook section 5 and exits non-zero on any mismatch; tokens read from env, never stored |
| AC-P4-16 | Staff operations | devices tab shows `status`, `last_seen_age_s`, `last_quality` from `GET /api/admin/devices`; screenshots in `artifacts/` |

## Integration (release gate)

| ID | Criterion | Pass condition |
|---|---|---|
| AC-P4-20 | Every merge logged | `evidence/team_v3/integration/INTEGRATION_LOG.md` has one entry per merged PR with real test numbers |
| AC-P4-21 | Final acceptance | `verification/TEAM_V3_ACCEPTANCE.csv` has every FA ID with PASS / FAIL / BLOCKED and an evidence path; no PASS without a file |
| AC-P4-22 | Release | tag `v3-integrated-demo` points to the commit that was verified; release notes list REAL / SIMULATED / PARTIAL / BLOCKED |
