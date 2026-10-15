import { defineConfig } from "@playwright/test";

// Uses the locally installed Microsoft Edge (no browser download). The app must already be running:
//   scripts/start_demo_windows.ps1   (serves http://127.0.0.1:8000)
export default defineConfig({
  testDir: "e2e",
  timeout: 240_000,
  expect: { timeout: 15_000 },
  workers: 1,
  reporter: [["list"], ["json", { outputFile: "../../evidence/playwright_results.json" }]],
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
