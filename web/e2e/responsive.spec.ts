import { expect, test, type Page } from "@playwright/test";

const viewports = [
  { width: 320, height: 568 },
  { width: 360, height: 800 },
  { width: 375, height: 667 },
  { width: 390, height: 844 },
  { width: 412, height: 915 },
  { width: 667, height: 375 },
  { width: 844, height: 390 },
  { width: 768, height: 1024 },
  { width: 820, height: 1180 },
  { width: 1024, height: 768 },
  { width: 1280, height: 800 },
  { width: 1440, height: 900 },
];

async function expectNoDocumentOverflow(page: Page) {
  const overflow = await page.evaluate(
    () =>
      document.documentElement.scrollWidth -
      document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(1);
}

test("dashboard and primary navigation fit every required viewport", async ({
  page,
}) => {
  for (const viewport of viewports) {
    await page.setViewportSize(viewport);
    await page.goto("/#/");
    await expect(page.getByRole("heading", { name: /Study the evidence/i })).toBeVisible();
    await expectNoDocumentOverflow(page);

    for (const route of ["library", "practice", "mock"]) {
      await page.goto(`/#/${route}`);
      await expectNoDocumentOverflow(page);
    }

    if (viewport.width < 1024) {
      const home = page
        .getByRole("navigation", { name: "Mobile primary navigation" })
        .getByRole("link", { name: "Home" });
      const box = await home.boundingBox();
      expect(box?.height ?? 0).toBeGreaterThanOrEqual(44);
    } else {
      await expect(
        page
          .getByRole("navigation", { name: "Primary navigation" })
          .getByRole("link", { name: "Dashboard" }),
      ).toBeVisible();
    }
  }
});

test("mobile drawer, library reader, and Thai content remain usable", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/#/library");
  await page.getByRole("button", { name: "Open navigation menu" }).click();
  await expect(page.getByRole("dialog", { name: "Navigation menu" })).toBeVisible();
  await page.getByRole("button", { name: "Close navigation menu" }).click();
  await expect(page.getByRole("dialog", { name: "Navigation menu" })).toBeHidden();
  await page.getByRole("link", { name: /BIS602/ }).first().click();
  await expect(page.getByText("การตัดสินใจและการวิเคราะห์ข้อมูลธุรกิจ")).toBeVisible();
  await page.getByRole("link", { name: /Business strategy and competitive advantage/i }).click();
  await expect(page.getByRole("heading", { name: "Terms & definitions" })).toBeVisible();
  await expectNoDocumentOverflow(page);
});

test("practice seals answers, reveals after submission, and uses tap-sized choices", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto("/#/practice");
  await page.getByRole("button", { name: /Start practice/i }).click();
  await expect(page).toHaveURL(/practice-session/);
  await expect(page.locator(".answer-panel")).toHaveCount(0);
  const firstChoice = page.locator(".choice").first();
  const choiceBox = await firstChoice.boundingBox();
  expect(choiceBox?.height ?? 0).toBeGreaterThanOrEqual(44);
  await firstChoice.click();
  await page.getByRole("button", { name: "Submit answer" }).click();
  await expect(page.locator(".answer-panel")).toBeVisible();
  await expectNoDocumentOverflow(page);
});

test("judgment practice is probability-labelled only after submission and remains unscored", async ({
  page,
}) => {
  const warning =
    "This answer is a probability-based recommendation. It is not verified by the supplied course materials or by a sufficiently authoritative external source.";
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/#/practice");
  await page
    .getByRole("radio", { name: /Questions requiring judgment/i })
    .check();
  await page.getByRole("button", { name: /Start practice/i }).click();
  await expect(page.getByText(warning, { exact: true })).toHaveCount(0);
  await page.locator(".choice").first().click();
  await page.getByRole("button", { name: "Submit answer" }).click();
  await expect(page.getByText(warning, { exact: true })).toBeVisible();
  await expect(
    page.getByText("Comparative probability by choice"),
  ).toBeVisible();
  await expect(page.getByText(/Unscored reflection/)).toBeVisible();
  await expectNoDocumentOverflow(page);
});

test("mock status, navigator, and submit dialog work on tablet and desktop", async ({
  page,
}) => {
  for (const viewport of [
    { width: 390, height: 844 },
    { width: 768, height: 1024 },
    { width: 1280, height: 800 },
  ]) {
    await page.setViewportSize(viewport);
    await page.goto("/#/mock");
    await page.getByRole("button", { name: /Begin mock exam/i }).click();
    await expect(page.locator(".exam-status .badge")).toHaveText("MOCK EXAM");
    await expect(page.locator(".timer")).toBeVisible();
    await expect(page.getByRole("complementary").getByRole("heading", { name: "Questions" })).toBeVisible();
    await page.getByRole("button", { name: "Submit exam" }).click();
    const dialog = page.getByRole("dialog", { name: "Submit your examination?" });
    await expect(dialog).toBeVisible();
    const dialogBox = await dialog.boundingBox();
    expect((dialogBox?.height ?? Infinity) <= viewport.height).toBe(true);
    await page.getByRole("button", { name: "Cancel" }).click();
    await expectNoDocumentOverflow(page);
  }
});

test("captures representative responsive evidence", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/#/");
  await page.screenshot({
    path: "../reports/screenshots/mobile/dashboard-390x844.png",
    fullPage: true,
  });

  await page.setViewportSize({ width: 768, height: 1024 });
  await page.goto("/#/library");
  await page.screenshot({
    path: "../reports/screenshots/tablet/library-768x1024.png",
    fullPage: true,
  });

  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/#/practice");
  await page.screenshot({
    path: "../reports/screenshots/desktop/practice-1440x900.png",
    fullPage: true,
  });
});
