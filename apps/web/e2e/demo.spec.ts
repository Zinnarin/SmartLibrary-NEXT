import { expect, test, type Page } from "@playwright/test";
import path from "node:path";
import { SHOTS } from "./artifacts";

/**
 * Browser smoke path required by the master prompt:
 * open map -> filter quiet/power -> report mismatch on recommended seat -> staff review + mark maintenance
 * -> student view updates over WebSocket (no reload) -> simulate camera disconnect -> UI refuses stale seats.
 * Screenshots of the real running UI go to artifacts/e2e/screenshots/ (git-ignored; see ./artifacts.ts).
 * The frozen V2 screenshots in presentation/screenshots/ are never overwritten.
 */
const STAFF = process.env.SL_STAFF_TOKEN || "staff-demo-2569";
const shot = (p: Page, name: string, fullPage = false) => p.screenshot({ path: path.join(SHOTS, name), fullPage });

async function api(page: Page, method: string, url: string, body?: unknown) {
  const r = await page.request.fetch(url, { method, headers: { "X-Staff-Token": STAFF, "Content-Type": "application/json" }, data: body as any });
  expect(r.ok(), `${method} ${url} -> ${r.status()}`).toBeTruthy();
  return r.json();
}

async function loginStaff(page: Page) {
  await page.goto("/#/staff");
  await page.getByTestId("staff-pin").fill(STAFF);
  await page.getByTestId("staff-login-btn").click();
  await expect(page.getByTestId("tab-reports")).toBeVisible();
}

const seat = (p: Page, id: string) => p.locator(`[data-seat="${id}"]`);

test("CV Lab page shows the recorded real-CV run (or NOT_RUN/BLOCKED) without resetting data", async ({ page }) => {
  await page.goto("/#/cv");
  await expect(page.getByTestId("cv-status")).toBeVisible();
  await page.waitForTimeout(800);
  await page.screenshot({ path: path.join(SHOTS, "17_cv_lab.png"), fullPage: true });
});

test("professor demo path (SIMULATION)", async ({ browser }) => {
  const student = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: "th-TH", timezoneId: "Asia/Bangkok" });
  const staff = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: "th-TH", timezoneId: "Asia/Bangkok" });
  const s = await student.newPage();
  const t = await staff.newPage();

  // clean, reproducible start: reset the demo DB and start NORMAL through the backend
  await s.goto("/");
  await api(s, "POST", "/api/demo/reset");
  await expect(s.getByTestId("sim-banner")).toContainText("SIMULATION — NOT REAL CAMERA DATA");
  await expect(s.getByTestId("conn")).toContainText("Live (WebSocket)");
  await expect(seat(s, "A07")).toHaveAttribute("data-tone", "available", { timeout: 20_000 });
  await expect(s.getByTestId("counts")).toContainText("ว่าง 12");
  await s.waitForTimeout(1500);
  await shot(s, "01_student_normal.png");

  // StudyMatch quiet + power
  await s.getByTestId("f-quiet").click();
  await s.getByTestId("f-power").click();
  await expect(s.getByTestId("rec-A07")).toBeVisible();
  await expect(s.getByTestId("rec-results").locator("article").first()).toContainText("A07");
  await shot(s, "02_studymatch_quiet_power.png");

  // seat detail + SeatCheck mismatch report on the recommended seat
  await seat(s, "A07").click();
  await expect(s.getByTestId("seat-detail")).toContainText("ที่นั่ง A07");
  await expect(s.getByTestId("trust")).toContainText("ความน่าเชื่อถือสูง");
  await shot(s, "03_seat_detail_A07.png");
  await s.getByTestId("seatcheck-open").click();
  await s.getByLabel("มีคนนั่งอยู่จริง").check();
  await shot(s, "04_seatcheck_form.png");
  await s.getByTestId("seatcheck-submit").click();
  await expect(s.getByTestId("toast")).toContainText("รอเจ้าหน้าที่ตรวจสอบ");
  await expect(s.getByTestId("pending-badge")).toBeVisible();
  // the report must NOT turn the seat occupied by itself; it only removes it from high-trust recommendations
  await expect(seat(s, "A07")).toHaveAttribute("data-tone", "available");
  await expect(s.getByTestId("rec-A07")).toHaveCount(0);
  await expect(s.getByTestId("rec-A05")).toBeVisible();
  await shot(s, "05_after_seatcheck_pending.png");

  // staff console: review + accept + Maintenance override
  await loginStaff(t);
  const card = t.locator('[data-testid^="report-"]').first();
  await expect(card).toContainText("A07");
  await shot(t, "06_staff_report_queue.png");
  const id = (await card.getAttribute("data-testid"))!.replace("report-", "");
  await t.getByTestId(`reason-${id}`).fill("ตรวจแล้วมีคนนั่งจริง กล้องมองไม่เห็น ปิดชั่วคราวเพื่อตรวจมุมกล้อง");
  await t.getByTestId(`ov-${id}`).selectOption("maintenance");
  await t.getByTestId(`resolve-${id}`).click();
  await expect(t.getByText("ไม่มีรายงานที่รอตรวจ")).toBeVisible();

  // student page updates live (WebSocket push, no reload)
  await expect(seat(s, "A07")).toHaveAttribute("data-tone", "maintenance", { timeout: 10_000 });
  await expect(s.getByTestId("seat-state")).toContainText("ซ่อม");
  await expect(s.getByTestId("conn")).toContainText("Live (WebSocket)");
  await expect(s.getByTestId("my-reports")).toContainText("เจ้าหน้าที่ยืนยันแล้ว");
  await shot(s, "07_student_updated_via_ws.png");

  await t.getByTestId("tab-events").click();
  await expect(t.locator("table")).toContainText("รายงาน #");
  await shot(t, "08_staff_audit_log.png");

  // camera disconnect (SIMULATED) -> seats of CAM-A are refused immediately, then STALE after TTL
  await api(s, "POST", "/api/demo/scenario", { scenario: "CAMERA_LOST", camera_id: "CAM-A" });
  await expect(s.getByTestId("camera-warning")).toContainText("CAM-A");
  await expect(s.getByTestId("rec-empty")).toContainText("ไม่มีที่นั่งที่ยืนยันได้ตอนนี้");
  await expect(seat(s, "A05")).toHaveAttribute("data-tone", "stale");
  await seat(s, "A05").click();
  await shot(s, "09_camera_lost_refused.png");
  await expect(s.getByTestId("seat-observed")).toContainText("STALE", { timeout: 45_000 });
  await expect(seat(s, "A07")).toHaveAttribute("data-tone", "maintenance"); // staff override still wins, sensor offline
  await shot(s, "10_camera_lost_stale_after_ttl.png");

  // recovery: camera back, seats need fresh repeated evidence before green again
  await api(s, "POST", "/api/demo/scenario", { scenario: "RECOVERED" });
  await expect(seat(s, "A05")).toHaveAttribute("data-tone", "available", { timeout: 20_000 });

  // GroupFit
  await s.getByTestId("f-quiet").click();
  await s.getByTestId("f-power").click();
  await s.getByTestId("f-group2").click();
  await expect(s.locator('[data-testid^="group-"]').first()).toBeVisible();
  await shot(s, "11_groupfit.png");

  // Wayfinder
  await s.getByTestId("f-solo").click();
  await seat(s, "C05").click();
  await s.getByTestId("route-btn").click();
  await expect(s.getByTestId("route-info")).toContainText("หน่วยผัง");
  await shot(s, "12_wayfinder.png");

  // Scenario Lab + other risk scenarios
  await t.goto("/#/lab");
  await t.getByTestId("run-LOW_CONFIDENCE").click();
  await expect(t.getByTestId("lab-active")).toHaveText("LOW_CONFIDENCE");
  await shot(t, "13_scenario_lab.png");
  await expect(seat(s, "C05")).toHaveAttribute("data-tone", "unknown", { timeout: 15_000 });
  await s.getByTestId("route-btn").click();
  await shot(s, "14_low_confidence_unknown.png");

  await t.getByTestId("run-BELONGINGS").click();
  await expect(seat(s, "A08")).toHaveAttribute("data-tone", "reserved", { timeout: 20_000 });
  await seat(s, "A08").click();
  await shot(s, "15_belongings_possibly_reserved.png");

  // mobile layout
  const m = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, locale: "th-TH", timezoneId: "Asia/Bangkok" });
  const mp = await m.newPage();
  await mp.goto("/");
  await expect(mp.getByTestId("sim-banner")).toBeVisible();
  await mp.waitForTimeout(1500);
  await shot(mp, "16_mobile_student.png", true);
  const overflow = await mp.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  expect(overflow, "no horizontal page scroll on phone width").toBeFalsy();

  // leave a clean NORMAL demo state behind
  await api(s, "POST", "/api/demo/reset");
  await student.close();
  await staff.close();
  await m.close();
});

test("WebSocket blocked -> polling fallback keeps data visible and honest", async ({ page }) => {
  // Simulate a network that kills the WebSocket: the client must fall back to REST polling.
  await page.routeWebSocket(/\/ws\/seats/, (ws) => ws.close());
  await page.goto("/");
  await expect(page.getByTestId("conn")).toContainText("Polling", { timeout: 15_000 });
  await expect(page.getByTestId("sim-banner")).toBeVisible();
  await expect(page.locator('[data-seat="A07"]')).toHaveAttribute("data-tone", /available|unknown|reserved|occupied|stale|maintenance|unavailable/);
  const before = await page.getByTestId("counts").innerText();
  expect(before.length).toBeGreaterThan(0);
  await page.screenshot({ path: path.join(SHOTS, "18_polling_fallback.png") });
});

test("SeatWatch alerts in-app when a verified matching seat becomes available", async ({ page }) => {
  await page.goto("/");
  await api(page, "POST", "/api/demo/reset");
  await expect(seat(page, "A07")).toHaveAttribute("data-tone", "available", { timeout: 20_000 });
  await page.getByTestId("f-quiet").click();
  await page.getByTestId("f-power").click();
  await expect(page.getByTestId("rec-A07")).toBeVisible();
  await api(page, "POST", "/api/admin/seats/A07/override", { state: "maintenance", reason: "ทดสอบ SeatWatch" });
  await expect(page.getByTestId("rec-A07")).toHaveCount(0);
  await page.getByTestId("seatwatch").locator("input").check();
  await page.waitForTimeout(2500); // let SeatWatch record the current verified set
  await api(page, "DELETE", "/api/admin/seats/A07/override");
  await expect(page.getByTestId("toast")).toContainText("SeatWatch: A07", { timeout: 15_000 });
  await page.screenshot({ path: path.join(SHOTS, "19_seatwatch_alert.png") });
  await api(page, "POST", "/api/demo/reset");
});
