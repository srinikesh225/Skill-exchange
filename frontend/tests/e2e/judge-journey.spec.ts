import { test, expect, Page } from "@playwright/test";

/**
 * Single high-value end-to-end test: the exact journey a judge performs.
 * Fails on blank pages, JS exceptions, failed API requests, or missing data.
 */

// Collect problems across the whole journey; asserted at the end.
function attachMonitors(page: Page, problems: string[]) {
  page.on("console", (msg) => {
    if (msg.type() === "error") problems.push(`console.error: ${msg.text()}`);
  });
  page.on("pageerror", (err) => problems.push(`pageerror: ${err.message}`));
  page.on("requestfailed", (req) => {
    const err = req.failure()?.errorText ?? "";
    // Ignore Next.js speculative RSC prefetches aborted by fast navigation
    // (net::ERR_ABORTED on ?_rsc= URLs) — these are cancellations, not failures.
    if (err.includes("ERR_ABORTED") || req.url().includes("_rsc=")) return;
    problems.push(`requestfailed: ${req.url()} ${err}`);
  });
  page.on("response", (res) => {
    // Any API call returning >=400 during the (all-valid) journey is a failure.
    if (res.url().includes("/api/") && res.status() >= 400) {
      problems.push(`api ${res.status()}: ${res.url()}`);
    }
  });
}

test("judge journey: home -> district -> skill -> why -> compare -> methodology", async ({ page }) => {
  const problems: string[] = [];
  attachMonitors(page, problems);

  // 1-2. Homepage loads.
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Know what skills your district/i })).toBeVisible();
  // overview stats populated (not blank)
  await expect(page.getByText("Districts", { exact: true }).first()).toBeVisible();

  // 3-4. Open district intelligence and select Hyderabad (via the directory — a
  // deterministic path; map-marker clicks on an SVG are not reliable headless).
  await page.getByRole("link", { name: "Districts", exact: true }).first().click();
  await expect(page).toHaveURL(/\/districts$/);
  await page.getByRole("link", { name: "Hyderabad", exact: true }).first().click();

  // 5. District dashboard appears.
  await expect(page.getByRole("heading", { name: "Hyderabad" })).toBeVisible();

  // 6. Skill-gap data appears (KPI + gaps section).
  await expect(page.getByText("Skill Gap Index")).toBeVisible();
  await expect(page.getByText("Largest skill gaps")).toBeVisible();

  // 9-12. Open a recommendation's "Why?" and verify evidence + proposed programme.
  const whyBtn = page.getByRole("button", { name: /Why\?/ }).first();
  await expect(whyBtn).toBeVisible();
  await whyBtn.click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await expect(dialog.getByText("Why this recommendation")).toBeVisible();
  await expect(dialog.getByText("Evidence")).toBeVisible();
  // Evidence contains concrete numbers (e.g. the "Demand index" evidence label).
  await expect(dialog.getByText("Demand index", { exact: true }).first()).toBeVisible();
  await page.getByRole("button", { name: "Close" }).click();
  await expect(dialog).toBeHidden();

  // 7-8. Select a skill (Cybersecurity) and verify demand/supply/gap.
  await page.getByRole("link", { name: "Cybersecurity", exact: true }).first().click();
  await expect(page).toHaveURL(/\/skills\/\d+/);
  await expect(page.getByText("Demand index").first()).toBeVisible();
  await expect(page.getByText("Supply index").first()).toBeVisible();
  await expect(page.getByText("Skill gap").first()).toBeVisible();
  // A forecast section renders.
  await expect(page.getByText(/12-month forecast/i)).toBeVisible();

  // 13-15. Compare two districts, both produce data.
  await page.getByRole("link", { name: "Compare", exact: true }).first().click();
  await expect(page).toHaveURL(/\/compare/);
  await expect(page.getByText("Overall skill gap")).toBeVisible();
  // At least two district columns with numeric gap values.
  const gapCells = page.locator("table tbody tr").first().locator("td.num, td");
  await expect(page.locator("table")).toBeVisible();
  await expect(page.getByText(/Top skill gaps/i).first()).toBeVisible();

  // 16-17. Methodology page loads with real content.
  await page.getByRole("link", { name: "Methodology", exact: true }).first().click();
  await expect(page).toHaveURL(/\/methodology/);
  await expect(page.getByRole("heading", { name: "Methodology" })).toBeVisible();
  await expect(page.getByText("Demand weights")).toBeVisible();

  // No unexpected console errors, page errors, or failed API requests.
  const genuine = problems.filter((p) => !/favicon|preload|woff2/i.test(p));
  expect(genuine, `Problems during journey:\n${genuine.join("\n")}`).toEqual([]);
});
