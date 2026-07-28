import { expect, test, type Page } from "@playwright/test";

const requiredViewports = [
  { width: 320, height: 568 },
  { width: 360, height: 800 },
  { width: 390, height: 844 },
  { width: 412, height: 915 },
  { width: 768, height: 1024 },
  { width: 1024, height: 768 },
  { width: 1280, height: 800 },
];

async function expectNoDocumentOverflow(page: Page) {
  const overflow = await page.evaluate(
    () =>
      document.documentElement.scrollWidth -
      document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(1);
}

test("related-exam teaching and traceability stay readable at every required viewport", async ({
  page,
}) => {
  const topicId = "topic-bis604-sql-and-implementation-03";
  for (const viewport of requiredViewports) {
    await page.setViewportSize(viewport);
    await page.goto(`/#/library/topic/${topicId}`);
    const section = page.locator("#topic-related-exam");
    await expect(
      section.getByRole("heading", { name: /Related examination topics/ }),
    ).toBeVisible();
    await expect(section.getByText("2 questions", { exact: true })).toBeVisible();
    await expect(section.getByText("INTERSECT set operation")).toBeVisible();
    await expect(section.getByText("การดำเนินการเซต UNION")).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "UNION, UNION ALL, and INTERSECT" }),
    ).toBeVisible();
    await expect(
      section.getByRole("link", { name: /Practice this topic/ }),
    ).toBeVisible();
    await expectNoDocumentOverflow(page);
  }
});

test("topic practice uses the precise mapping and question review links back only after submission", async ({
  page,
}) => {
  const topicId = "topic-bis604-sql-and-implementation-03";
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`/#/library/topic/${topicId}`);
  await page.getByRole("link", { name: /Practice this topic/ }).click();
  await expect(page).toHaveURL(new RegExp(`topic=${topicId}`));
  await expect(page.getByLabel("Study topic")).toHaveValue(topicId);
  await expect(page.locator(".setup-summary > strong")).toHaveText("2");
  await page.getByRole("button", { name: /Start practice/ }).click();
  await expect(
    page.getByRole("link", {
      name: /Review the most relevant Study Library topic/,
    }),
  ).toHaveCount(0);
  await page.locator(".choice").first().click();
  await page.getByRole("button", { name: "Submit answer" }).click();
  const reviewLink = page.getByRole("link", {
    name: /Review the most relevant Study Library topic/,
  });
  await expect(reviewLink).toBeVisible();
  await expect(reviewLink).toHaveAttribute(
    "href",
    `#/library/topic/${topicId}`,
  );
  await expectNoDocumentOverflow(page);
});

test("answer warnings remain generic and untested topics do not claim absence of importance", async ({
  page,
}) => {
  await page.setViewportSize({ width: 412, height: 915 });
  await page.goto(
    "/#/library/topic/topic-bis605-backend-data-api-cloud-mobile-02",
  );
  const warning = page
    .locator("#topic-related-exam")
    .getByText(/related question retains an academic-review or scoring warning/);
  await expect(warning).toBeVisible();
  await expect(page.locator("#topic-related-exam")).not.toContainText(
    "Recommended answer",
  );

  await page.goto(
    "/#/library/topic/topic-bis601-development-methods-01",
  );
  await expect(
    page.getByText(/This does not mean the topic is unimportant/),
  ).toBeVisible();
  await expectNoDocumentOverflow(page);
});
