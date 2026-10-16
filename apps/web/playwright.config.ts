import { defineConfig } from "@playwright/test";
import path from "node:path";
import { E2E_DIR } from "./e2e/artifacts";

// Uses the locally installed Microsoft Edge (no browser download). The app must already be running:
//   scripts/start_demo_windows.ps1   (serves http://127.0.0.1:8000)
// Generated output goes to <repo>/artifacts/e2e/ (git-ignored) or SL_ARTIFACT_DIR - never to frozen V2 evidence.
export default defineConfig({
  testDir: "e2e",
  timeout: 240_000,
  expect: { timeout: 15_000 },
  workers: 1,
  outputDir: path.join(E2E_DIR, "test-results"),
  reporter: [["list"], ["json", { outputFile: path.join(E2E_DIR, "playwright_results.json") }]],
  use: {
    baseURL: process.env.SL_BASE_URL || "http://127.0.0.1:8000",
    channel: "msedge",
    headless: true,
    viewport: { width: 1440, height: 900 },
    locale: "th-TH",
    timezoneId: "Asia/Bangkok",
    screenshot: "only-on-failure",
  },
});
