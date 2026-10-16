# P1 · 08 — Delivery checklist (before every PR)

## Code and tests
- [ ] My branch is up to date: `git fetch origin` then `git merge origin/main`, with no unresolved conflicts.
- [ ] `.venv\Scripts\python -m pytest -q`: 0 failed. I pasted the summary line into the PR.
- [ ] `tests/test_cv_v3.py` passes without torch or ultralytics installed.
- [ ] If I touched the sender: a live smoke run against a local server returned `applied`, then `duplicate`. The real JSON is in the PR.
- [ ] `.venv\Scripts\python scripts\check_ownership.py --owner P1 --base origin/main` shows no `BLOCK`. The output is in the PR.

## Data, privacy and truth
- [ ] `git status` is clean for `evidence/`, `presentation/` and `verification/`.
- [ ] No video, frames, images of people, weights, `.venv-cv` or tokens in the diff.
- [ ] Every media source has written permission. The experiment README states the source, consent (no names), camera, lighting and N.
- [ ] Every number in the PR or README comes from a file in the PR (metrics JSON/CSV, log), with N.
- [ ] Nothing simulated is called "CV" or "real", and no accuracy claim exists without AC-P1-21.

## Contract
- [ ] Payloads still match C1 (`05_INTEGRATION_CONTRACT.md`). Any new field has an approved CR.
- [ ] `latest_run.json` keys used by `CvLab.tsx` are unchanged, or P3 approved the change.
- [ ] I did not edit `services/**`, `apps/**` or any frozen file.

## PR
- [ ] Opened with `.github/pull_request_template.md`, label `person-1-cv`, and linked issues (`Closes #…`).
- [ ] The PR states what is new, what is V2 baseline, and what is still BLOCKED.
- [ ] The PR notes where AI tools helped.
- [ ] I did not merge my own PR. P4 merges after the integration checks.
