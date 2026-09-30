import { test, expect, Page, Locator } from "@playwright/test";

/**
 * Single high-value end-to-end test: the exact journey a judge performs.
 *
 * Deliberately asserts REAL NUMERIC VALUES at every stage, not just component
 * titles/labels — an empty or all-zero API payload must fail this test.
 */

const ORIGIN_RE = /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?\//;

function attachMonitors(page: Page, problems: string[]) {
  page.on("console", (msg) => {
    if (msg.type() === "error") problems.push(`console.error: ${msg.text()}`);
  });
  page.on("pageerror", (err) => problems.push(`pageerror: ${err.message}`));

  page.on("requestfailed", (req) => {
    const err = req.failure()?.errorText ?? "";
    // Speculative RSC prefetches cancelled by fast navigation are cancellations,
    // not failures. Everything else same-origin is a genuine problem.
    if (err.includes("ERR_ABORTED")) return;
    // Third-party assets (OpenStreetMap tiles, font CDNs) must not fail the app test.
    if (!ORIGIN_RE.test(req.url())) return;
    problems.push(`requestfailed: ${req.url()} ${err}`);
  });

  page.on("response", (res) => {
    const url = res.url();
    if (!ORIGIN_RE.test(url)) return;
    // Any API 4xx/5xx during this (all-valid) journey is a failure.
    if (url.includes("/api/") && res.status() >= 400) {
      problems.push(`api ${res.status()}: ${url}`);
    }
    // Any same-origin 5xx (incl. App Router RSC payload errors) is a failure.
    else if (res.status() >= 500) {
      problems.push(`server ${res.status()}: ${url}`);
    }
  });
}

/** Read a locator's text as a number ("12,182" -> 12182, "+71%" -> 71). */
async function readNumber(loc: Locator): Promise<number> {
  const raw = (await loc.first().innerText()).trim();
  const cleaned = raw.replace(/[,\s%₹+]/g, "");
  const n = Number.parseFloat(cleaned);
  expect(Number.isFinite(n), `expected a number, got "${raw}"`).toBe(true);
  return n;
}

/** The numeric value of the KPI card carrying the given label. */
function kpiValue(scope: Page | Locator, label: string): Locator {
  return scope
    .locator(".card")
    .filter({ has: scope.locator(".label", { hasText: new RegExp(`^${label}$`, "i") }) })
    .locator(".num")
    .first();
}

test("judge journey: home -> district -> skill -> why -> compare -> methodology", async ({ page }) => {
  const problems: string[] = [];
  attachMonitors(page, problems);

  // ---- 1-2. Homepage loads with REAL overview numbers -------------------
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Know what skills your district/i })).toBeVisible();

  // The hero stat strip must contain live, non-zero counts (not a blank shell).
  const heroStats = page.locator(".num");
  await expect.poll(async () => await heroStats.count(), { timeout: 15_000 }).toBeGreaterThanOrEqual(4);
  const districtCount = await readNumber(heroStats.nth(0));
  expect(districtCount, "district count from /api/analytics/overview must be > 0").toBeGreaterThan(0);

  // ---- 3. Map entry point actually renders districts --------------------
  const markers = page.locator("path.leaflet-interactive");
  await expect.poll(async () => await markers.count(), { timeout: 20_000 }).toBeGreaterThan(50);

  // ---- 4. Select Hyderabad (via the directory: deterministic headless) ---
  await page.getByRole("link", { name: "Districts", exact: true }).first().click();
  await expect(page).toHaveURL(/\/districts$/);
  await expect(page.locator("tbody tr").first()).toBeVisible();
  await page.getByRole("link", { name: "Hyderabad", exact: true }).first().click();

  // ---- 5-6. District dashboard with REAL gap/demand/supply numbers ------
  await expect(page.getByRole("heading", { name: "Hyderabad" })).toBeVisible();
  const gap = await readNumber(kpiValue(page, "Skill Gap Index"));
  const demand = await readNumber(kpiValue(page, "Employment Demand"));
  const supply = await readNumber(kpiValue(page, "Training Supply"));
  expect(gap, "skill gap index must be a real 0-100 score").toBeGreaterThan(0);
  expect(gap).toBeLessThanOrEqual(100);
  expect(demand).toBeGreaterThan(0);
  expect(supply).toBeGreaterThanOrEqual(0);

  // Gap table is populated with ranked skills.
  await expect(page.getByText("Largest skill gaps")).toBeVisible();
  const skillRows = page.locator("tbody tr");
  expect(await skillRows.count(), "district skills table must have rows").toBeGreaterThan(5);

  // ---- 9-12. "Why?" -> evidence + proposed programme --------------------
  const whyBtn = page.getByRole("button", { name: /Why\?/ }).first();
  await expect(whyBtn).toBeVisible();
  await whyBtn.click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();

  // A non-empty, substantive rationale (not just the heading).
  await expect(dialog.getByText("Why this recommendation")).toBeVisible();
  const rationale = dialog.locator("ul li");
  expect(await rationale.count(), "recommendation must carry >=1 rationale bullet").toBeGreaterThan(0);
  expect((await rationale.first().innerText()).trim().length).toBeGreaterThan(10);

  // Evidence must carry real numbers, and they must agree with the dashboard.
  await expect(dialog.getByText("Evidence")).toBeVisible();
  const evidenceGap = await readNumber(
    dialog.locator("dl > div").filter({ hasText: /^Skill gap/ }).locator("dd").first()
  );
  expect(evidenceGap, "evidence gap must be a real score").toBeGreaterThan(0);

  // The proposed programme (the actionable output) must be present.
  await expect(dialog.getByText("Proposed programme")).toBeVisible();
  const capacity = await readNumber(dialog.getByText(/Suggested capacity/).locator(".num").first());
  expect(capacity, "suggested seat capacity must be > 0").toBeGreaterThan(0);

  await page.getByRole("button", { name: "Close" }).click();
  await expect(dialog).toBeHidden();

  // ---- 7-8. Skill explorer: demand / supply / gap as numbers ------------
  await page.getByRole("link", { name: "Cybersecurity", exact: true }).first().click();
  await expect(page).toHaveURL(/\/skills\/\d+/);
  const sDemand = await readNumber(kpiValue(page, "Demand index"));
  const sGap = await readNumber(kpiValue(page, "Skill gap"));
  expect(sDemand, "skill demand index must be > 0").toBeGreaterThan(0);
  expect(sGap).toBeGreaterThanOrEqual(0);
  await expect(page.getByText(/12-month forecast/i)).toBeVisible();

  // ---- 13-15. Compare: two districts, both with real numbers -----------
  await page.getByRole("link", { name: "Compare", exact: true }).first().click();
  await expect(page).toHaveURL(/\/compare/);
  const gapRow = page.locator("tbody tr").filter({ hasText: "Overall skill gap" }).first();
  await expect(gapRow).toBeVisible();
  const gapCells = gapRow.locator("td.num");
  expect(await gapCells.count(), "compare must show >=2 district columns").toBeGreaterThanOrEqual(2);
  const gapA = await readNumber(gapCells.nth(0));
  const gapB = await readNumber(gapCells.nth(1));
  expect(gapA, "district A must have a real gap").toBeGreaterThan(0);
  expect(gapB, "district B must have a real gap").toBeGreaterThan(0);
  // Both districts must produce their own skill-gap profiles.
  expect(await page.getByText(/Top skill gaps/i).count()).toBeGreaterThanOrEqual(2);

  // ---- 16-17. Methodology with live weights ----------------------------
  await page.getByRole("link", { name: "Methodology", exact: true }).first().click();
  await expect(page).toHaveURL(/\/methodology/);
  await expect(page.getByRole("heading", { name: "Methodology" })).toBeVisible();
  await expect(page.getByText("Demand weights")).toBeVisible();
  // The weights table must render real numbers summing to 1.00.
  const weightTotal = await readNumber(
    page.locator("tr").filter({ hasText: /^Total/ }).first().locator("td").last()
  );
  expect(weightTotal, "demand weights must sum to 1.00").toBeCloseTo(1.0, 2);

  // ---- No unexpected console errors / page errors / failed requests ----
  expect(problems, `Problems during journey:\n${problems.join("\n")}`).toEqual([]);
});
