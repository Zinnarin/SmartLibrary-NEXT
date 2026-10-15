import { expect, test } from "@playwright/test";
import { execSync, spawn, type ChildProcess } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

/**
 * Real crash test (not a simulated route cut): this test starts its OWN backend on port 8020 with a throwaway DB,
 * kills the real server process while the page stays open, then starts it again and checks that the same page
 * reconnects by itself and only shows seats as available again after fresh evidence.
 */
const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const SHOTS = path.join(ROOT, "presentation", "screenshots");
const PORT = 8020;
const URL = `http://127.0.0.1:${PORT}`;
const DB = path.join(ROOT, ".pytest_tmp", "e2e_restart.db");

function startServer(): ChildProcess {
  return spawn(path.join(ROOT, ".venv", "Scripts", "python.exe"),
    ["-m", "uvicorn", "app.main:get_app", "--factory", "--app-dir", "services/api", "--host", "127.0.0.1", "--port", String(PORT)],
    { cwd: ROOT, env: { ...process.env, SL_DB_PATH: DB, SL_MODE: "demo" }, stdio: "ignore" });
}
function killServer(p: ChildProcess) {
  try { execSync(`taskkill /pid ${p.pid} /T /F`, { stdio: "ignore" }); } catch { /* already gone */ }
}
async function waitHealthy() {
  for (let i = 0; i < 60; i++) {
    try { if ((await fetch(`${URL}/api/health`)).ok) return; } catch { /* not up yet */ }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error("server did not start");
}

test("real server crash + restart: page goes not-current, then reconnects and re-confirms seats", async ({ page }) => {
  fs.mkdirSync(path.dirname(DB), { recursive: true });
  for (const f of [DB, `${DB}-wal`, `${DB}-shm`]) fs.rmSync(f, { force: true });
  let srv = startServer();
  try {
    await waitHealthy();
    await page.goto(URL + "/");
    await expect(page.getByTestId("conn")).toContainText("Live", { timeout: 15_000 });
    await expect(page.locator('[data-seat="B07"]')).toHaveAttribute("data-tone", "available", { timeout: 20_000 });

    killServer(srv); // real process kill
    await expect(page.getByTestId("link-down")).toBeVisible({ timeout: 20_000 });
    await expect(page.locator('[data-seat="B07"]')).toHaveAttribute("data-tone", "stale");
    await expect(page.locator('article[data-testid^="rec-"]')).toHaveCount(0);
    const greenWhileDown = await page.locator('[data-tone="available"]').count();
    expect(greenWhileDown).toBe(0);

    srv = startServer();
    await waitHealthy();
    // same page, no reload: client reconnects on its own (backoff <= 15 s)
    await expect(page.getByTestId("conn")).toContainText("Live", { timeout: 30_000 });
    await expect(page.getByTestId("link-down")).toHaveCount(0);
    // after a gap > TTL the engine must re-confirm (Unknown first), then Available after smoothing
    await expect(page.locator('[data-seat="B07"]')).toHaveAttribute("data-tone", "available", { timeout: 20_000 });
    await page.screenshot({ path: path.join(SHOTS, "22_after_real_server_restart.png") });
  } finally {
    killServer(srv);
  }
});
