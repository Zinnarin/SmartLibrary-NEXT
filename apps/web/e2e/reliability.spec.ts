import { expect, test, type Page } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";

/** Phase 2/3 verification: reliability + full student journey with console-error capture. */
const HERE = path.dirname(fileURLToPath(import.meta.url));
const SHOTS = path.resolve(HERE, "../../../presentation/screenshots");
const STAFF = process.env.SL_STAFF_TOKEN || "staff-demo-2569";
const seat = (p: Page, id: string) => p.locator(`[data-seat="${id}"]`);
const recCards = (p: Page) => p.locator('article[data-testid^="rec-"]');

async function api(page: Page, method: string, url: string, body?: unknown) {
  const r = await page.request.fetch(url, { method, headers: { "X-Staff-Token": STAFF, "Content-Type": "application/json" }, data: body as any });
  expect(r.ok(), `${method} ${url} -> ${r.status()}`).toBeTruthy();
  return r.json();
}

test("BUG-011 regression: server unreachable -> seats not shown as fresh, recommendations withdrawn; reconnect restores live data", async ({ page }) => {
  let cut = false;
  const live: { close: () => Promise<void> }[] = [];
  await page.routeWebSocket(/\/ws\/seats/, (ws) => {
    if (cut) {
      ws.close();
      return;
    }
    ws.connectToServer();
    live.push(ws);
  });
  await page.route("**/api/**", (r) => (cut ? r.abort() : r.continue()));
  await page.goto("/");
  await api(page, "POST", "/api/demo/reset");
  await expect(page.getByTestId("conn")).toContainText("Live", { timeout: 15_000 });
  await expect(seat(page, "B07")).toHaveAttribute("data-tone", "available", { timeout: 20_000 });
  await expect(recCards(page).first()).toBeVisible();

  // cut the server off (WS + REST) exactly like a crashed server / lost network
  cut = true;
  for (const ws of live.splice(0)) await ws.close();
  await page.waitForTimeout(12_000);
  await expect(seat(page, "B07"), "a seat must not stay green when no data can arrive").toHaveAttribute("data-tone", "stale", { timeout: 5_000 });
  await expect(recCards(page), "old recommendations must be withdrawn").toHaveCount(0);
  await expect(page.getByTestId("link-down")).toContainText("ข้อมูลไม่เป็นปัจจุบัน");
  await page.screenshot({ path: path.join(SHOTS, "20_server_unreachable_stale.png") });

  // network back: client must reconnect by itself and show fresh data again
  cut = false;
  await expect(page.getByTestId("conn")).toContainText("Live", { timeout: 30_000 });
  await expect(page.getByTestId("link-down")).toHaveCount(0);
  await expect(seat(page, "B07")).toHaveAttribute("data-tone", "available", { timeout: 20_000 });
  await expect(recCards(page).first()).toBeVisible({ timeout: 10_000 });
  await page.screenshot({ path: path.join(SHOTS, "21_reconnected_live.png") });
});

test("student journey in the requested order, with zero console/page errors", async ({ browser }) => {
  const errors: string[] = [];
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: "th-TH", timezoneId: "Asia/Bangkok" });
  const s = await ctx.newPage();
  const t = await ctx.newPage();
  for (const p of [s, t]) {
    p.on("console", (m) => m.type() === "error" && errors.push(`[console] ${m.text()}`));
    p.on("pageerror", (e) => errors.push(`[pageerror] ${e.message}`));
  }
  // 1-2 open + view
  await s.goto("/");
  await api(s, "POST", "/api/demo/reset");
  await expect(s.getByTestId("sim-banner")).toBeVisible();
  await expect(seat(s, "A07")).toHaveAttribute("data-tone", "available", { timeout: 20_000 });
  // 3-4 filter + StudyMatch
  await s.getByTestId("f-quiet").click();
  await s.getByTestId("f-power").click();
  await expect(recCards(s).first()).toContainText("A07");
  // 5 GroupFit (no adjacent quiet+power pair exists -> honest empty state, then relax by user choice)
  await s.getByTestId("f-group2").click();
  await expect(s.getByTestId("rec-empty")).toContainText("ไม่มีที่นั่ง 2 ที่ติดกัน");
  await s.getByTestId("f-power").click();
  await expect(s.locator('[data-testid="group-A07-A08"]')).toBeVisible();
  // 6 Wayfinder
  await s.getByTestId("f-solo").click();
  await s.getByTestId("f-power").click();
  await seat(s, "A07").click();
  await s.getByTestId("route-btn").click();
  await expect(s.getByTestId("route-info")).toContainText("A07");
  // 7-8 incorrect-seat feedback -> removed from recommendations, state unchanged
  await s.getByTestId("seatcheck-open").click();
  await s.getByLabel("มีคนนั่งอยู่จริง").check();
  await s.getByTestId("seatcheck-submit").click();
  await expect(s.getByTestId("pending-badge")).toBeVisible();
  await expect(s.getByTestId("rec-A07")).toHaveCount(0);
  await expect(seat(s, "A07")).toHaveAttribute("data-tone", "available");
  // 9-11 staff console: review + override
  await t.goto("/#/staff");
  await t.getByTestId("staff-pin").fill(STAFF);
  await t.getByTestId("staff-login-btn").click();
  const card = t.locator('[data-testid^="report-"]').first();
  await expect(card).toContainText("A07");
  const id = (await card.getAttribute("data-testid"))!.replace("report-", "");
  await t.getByTestId(`reason-${id}`).fill("ตรวจแล้วมีคนนั่งจริง");
  await t.getByTestId(`ov-${id}`).selectOption("unavailable");
  await t.getByTestId(`resolve-${id}`).click();
  // 12 real-time sync on the student page (no reload)
  await expect(seat(s, "A07")).toHaveAttribute("data-tone", "unavailable", { timeout: 10_000 });
  await expect(s.getByTestId("seat-state")).toContainText("ปิดใช้งาน");
  // visit remaining pages for console errors
  await t.goto("/#/lab");
  await expect(t.getByTestId("lab-active")).toBeVisible();
  await t.goto("/#/cv");
  await expect(t.getByTestId("cv-status")).toBeVisible();
  await api(s, "POST", "/api/demo/reset");
  await ctx.close();
  expect(errors, errors.join("\n")).toEqual([]);
});

test("map is keyboard-operable (Tab to a seat, Enter opens details)", async ({ page }) => {
  await page.goto("/");
  await expect(seat(page, "A01")).toBeVisible({ timeout: 15_000 });
  await seat(page, "A07").focus();
  await page.keyboard.press("Enter");
  await expect(page.getByTestId("seat-detail")).toContainText("ที่นั่ง A07");
  await page.keyboard.press("Tab"); // next seat is reachable by keyboard
  const focused = await page.evaluate(() => document.activeElement?.getAttribute("data-seat"));
  expect(focused).toBeTruthy();
});
