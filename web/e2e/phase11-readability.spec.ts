import { expect, test, type Page } from "@playwright/test";

const viewports = [
  { width: 320, height: 568 },
  { width: 360, height: 800 },
  { width: 390, height: 844 },
  { width: 412, height: 915 },
  { width: 768, height: 1024 },
  { width: 1024, height: 768 },
  { width: 1280, height: 800 },
  { width: 1440, height: 900 },
];

const STORAGE_KEY = "compre-study:v1";

async function expectNoDocumentOverflow(page: Page) {
  const overflow = await page.evaluate(
    () =>
      document.documentElement.scrollWidth -
      document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(1);
}

test.beforeEach(async ({ page }) => {
  await page.addInitScript(
    ({ key }) => {
      localStorage.setItem(
        key,
        JSON.stringify({
          schemaVersion: 1,
          bookmarks: {
            chapterIds: [],
            topicIds: [],
            questionIds: ["question-comprehensive-019"],
          },
          attempts: [],
          preferences: {
            languageView: "bilingual",
            feedbackMode: "immediate",
            randomizeQuestions: false,
            randomizeChoices: false,
          },
        }),
      );
    },
    { key: STORAGE_KEY },
  );
});

test("the Business Analyst regression fixture renders separate bilingual statements at every required viewport", async ({
  page,
}) => {
  for (const viewport of viewports) {
    await page.setViewportSize(viewport);
    await page.goto(
      "/#/practice?question=question-comprehensive-019",
    );
    await page.getByRole("button", { name: /Start practice/i }).click();

    const heading = page.getByRole("heading", {
      name: "Which of the following is Incorrect?",
    });
    const english = page.locator(
      '.embedded-option-list[data-language="en"] li',
    );
    const thai = page.locator(
      '.embedded-option-list[data-language="th"] li',
    );
    await expect(heading).toBeVisible();
    await expect(english).toHaveCount(3);
    await expect(thai).toHaveCount(3);
    await expect(english.nth(0)).toContainText("A)");
    await expect(english.nth(1)).toContainText("B)");
    await expect(english.nth(2)).toContainText("C)");
    await expect(thai.nth(0)).toContainText("นักวิเคราะห์ธุรกิจ");
    await expect(page.locator(".choice")).toHaveCount(5);

    const englishBoxes = await english.evaluateAll((nodes) =>
      nodes.map((node) => node.getBoundingClientRect().toJSON()),
    );
    const thaiBoxes = await thai.evaluateAll((nodes) =>
      nodes.map((node) => node.getBoundingClientRect().toJSON()),
    );
    for (const boxes of [englishBoxes, thaiBoxes]) {
      for (let index = 1; index < boxes.length; index += 1) {
        expect(boxes[index]!.y).toBeGreaterThan(
          boxes[index - 1]!.y + boxes[index - 1]!.height - 1,
        );
      }
    }
    expect(englishBoxes[2]!.y + englishBoxes[2]!.height).toBeLessThan(
      thaiBoxes[0]!.y,
    );
    const firstChoice = await page.locator(".choice").first().boundingBox();
    expect(thaiBoxes[2]!.y + thaiBoxes[2]!.height).toBeLessThan(
      firstChoice!.y,
    );
    const headingSize = await heading.evaluate((node) =>
      Number.parseFloat(getComputedStyle(node).fontSize),
    );
    if (viewport.width <= 412) {
      expect(headingSize).toBeLessThanOrEqual(28);
    }
    await expectNoDocumentOverflow(page);
  }
});

test("the enriched topic reader, chapter navigation, comparisons, and Thai content adapt at every required viewport", async ({
  page,
}) => {
  const route =
    "/#/library/topic/topic-bis601-analyst-and-system-success-02";
  for (const viewport of viewports) {
    await page.setViewportSize(viewport);
    await page.goto(route);
    await expect(
      page.getByRole("heading", { name: "Systems analyst", level: 1 }),
    ).toBeVisible();
    await expect(
      page.getByText("นักวิเคราะห์ระบบ", { exact: true }).first(),
    ).toBeVisible();
    await expect(page.locator(".topic-toc")).toBeVisible();
    await expect(
      page.getByRole("heading", {
        name: "Business Analyst vs Systems Analyst",
      }),
    ).toBeVisible();
    await expect(page.getByText("From course materials").first()).toBeVisible();
    await expect(page.getByText("Supplementary explanation").first()).toBeVisible();
    await expect(page.getByRole("link", { name: /Previous topic/ })).toBeVisible();
    await expect(page.getByRole("link", { name: /Next topic/ })).toBeVisible();

    const thaiParagraph = page
      .locator(".lesson-paragraphs p[lang='th']")
      .first();
    const metrics = await thaiParagraph.evaluate((node) => ({
      clientHeight: node.clientHeight,
      scrollHeight: node.scrollHeight,
      lineHeight: Number.parseFloat(getComputedStyle(node).lineHeight),
      fontSize: Number.parseFloat(getComputedStyle(node).fontSize),
    }));
    expect(metrics.scrollHeight - metrics.clientHeight).toBeLessThanOrEqual(1);
    expect(metrics.lineHeight).toBeGreaterThan(metrics.fontSize);

    if (viewport.width >= 1024) {
      await expect(page.locator(".chapter-topic-nav")).toBeVisible();
    }
    const comparison = page.locator(".comparison-scroll");
    await expect(comparison).toBeVisible();
    expect(await comparison.evaluate((node) => node.scrollWidth)).toBeGreaterThan(0);
    await expectNoDocumentOverflow(page);
  }
});

test("quantitative lessons expose formulas, variables, examples, and mistakes without page overflow", async ({
  page,
}) => {
  for (const viewport of [
    { width: 320, height: 568 },
    { width: 768, height: 1024 },
    { width: 1440, height: 900 },
  ]) {
    await page.setViewportSize(viewport);
    await page.goto(
      "/#/library/topic/topic-bis602-investment-decisions-03",
    );
    await expect(
      page.getByRole("heading", { name: "Formula guide" }),
    ).toBeVisible();
    await expect(page.locator(".formula-detail-list code")).toContainText(
      "NPV =",
    );
    await expect(
      page.getByRole("heading", { name: /Worked example/ }),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: /Common mistake/ }),
    ).toBeVisible();
    await expectNoDocumentOverflow(page);
  }
});

test("captures Phase 11 mobile and desktop readability evidence", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(
    "/#/library/topic/topic-bis601-analyst-and-system-success-02",
  );
  await page.screenshot({
    path: "../reports/screenshots/mobile/topic-reader-390x844.png",
    fullPage: true,
  });

  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(
    "/#/practice?question=question-comprehensive-019",
  );
  await page.getByRole("button", { name: /Start practice/i }).click();
  await page.screenshot({
    path: "../reports/screenshots/desktop/embedded-choice-question-1440x900.png",
    fullPage: true,
  });
});
