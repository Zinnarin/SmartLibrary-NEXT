import path from "node:path";
import { fileURLToPath } from "node:url";

/**
 * Where browser tests write generated output (screenshots, JSON results).
 * Default: <repo>/artifacts/ (git-ignored). Override with SL_ARTIFACT_DIR (relative to the repo root or absolute).
 * Frozen V2 evidence (evidence/*, presentation/*) is never allowed as a target, so a test run cannot
 * silently overwrite committed V2 screenshots/results. Curated V3 evidence may go to evidence/team_v3/
 * or presentation/v3/ on purpose.
 */
const HERE = path.dirname(fileURLToPath(import.meta.url));
export const REPO_ROOT = path.resolve(HERE, "../../..");

function resolveArtifactDir(): string {
  const dir = process.env.SL_ARTIFACT_DIR ? path.resolve(REPO_ROOT, process.env.SL_ARTIFACT_DIR) : path.join(REPO_ROOT, "artifacts");
  const rel = path.relative(REPO_ROOT, dir).split(path.sep).join("/");
  const frozen = ["evidence", "presentation", "verification", "reference", "templates", "docs"];
  const allowed = ["evidence/team_v3", "presentation/v3"];
  const top = rel.split("/")[0];
  if (frozen.includes(top) && !allowed.some((a) => rel === a || rel.startsWith(a + "/"))) {
    throw new Error(`SL_ARTIFACT_DIR=${rel} points into frozen V2 files; use artifacts/, evidence/team_v3/ or presentation/v3/`);
  }
  return dir;
}

export const ARTIFACT_DIR = resolveArtifactDir();
export const E2E_DIR = path.join(ARTIFACT_DIR, "e2e");
export const SHOTS = path.join(E2E_DIR, "screenshots");
