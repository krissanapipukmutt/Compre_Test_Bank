import { expect, test, type Page } from "@playwright/test";

const STORAGE_KEY = "compre-study:v1";
async function openVisualQuestion(
  page: Page,
  {
    questionId = "question-comprehensive-080",
    heading = /UNION operator/,
    imageAlt = /relations separated by the UNION operator/,
  }: {
    questionId?: string;
    heading?: RegExp;
    imageAlt?: RegExp;
  } = {},
) {
  await page.addInitScript(
    ({ key, questionId }) => {
      localStorage.setItem(
        key,
        JSON.stringify({
          schemaVersion: 1,
          bookmarks: { chapterIds: [], questionIds: [questionId] },
          attempts: [],
          preferences: {
            languageView: "bilingual",
            feedbackMode: "immediate",
            randomizeQuestions: true,
            randomizeChoices: true,
          },
        }),
      );
    },
    { key: STORAGE_KEY, questionId },
  );
  await page.goto(`/#/practice?question=${questionId}`);
  await page.getByRole("button", { name: /Start practice/i }).click();
  await expect(page).toHaveURL(/practice-session/);
  await expect(
    page.getByRole("heading", { name: heading }),
  ).toBeVisible();
  const image = page.getByAltText(imageAlt);
  await expect(image).toBeVisible();
  await expect
    .poll(() => image.evaluate((node: HTMLImageElement) => node.naturalWidth))
    .toBeGreaterThan(0);
  return image;
}

async function expectNoHorizontalOverflow(page: Page) {
  const overflow = await page.evaluate(
    () =>
      document.documentElement.scrollWidth -
      document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(1);
}

test("essential visual, source image, zoom, Escape, and focus work in a real browser", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const inlineImage = await openVisualQuestion(page);
  await expectNoHorizontalOverflow(page);
  const headingBox = await page
    .getByRole("heading", { name: /UNION operator/ })
    .boundingBox();
  const imageBox = await inlineImage.boundingBox();
  const firstChoiceBox = await page.locator(".choice").first().boundingBox();
  expect(headingBox!.y + headingBox!.height).toBeLessThan(imageBox!.y);
  expect(imageBox!.y + imageBox!.height).toBeLessThan(firstChoiceBox!.y);

  const originalButton = page.getByRole("button", {
    name: /View original question image/,
  });
  await originalButton.click();
  const dialog = page.getByRole("dialog", {
    name: /View original question image/,
  });
  await expect(dialog).toBeVisible();
  const dialogBox = await dialog.boundingBox();
  expect(dialogBox?.width).toBe(390);
  expect(dialogBox?.height).toBe(844);
  const sourceImage = dialog.getByAltText(/Original source crop/);
  await expect
    .poll(() =>
      sourceImage.evaluate((node: HTMLImageElement) => node.naturalWidth),
    )
    .toBeGreaterThan(0);
  await dialog.getByRole("button", { name: "Zoom in" }).click();
  await expect(dialog.getByText("125%")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
  await expect(originalButton).toBeFocused();
});

test("an essential image network failure blocks the UNION question", async ({
  page,
}) => {
  await page.route(
    "**/question-comprehensive-080/question-visual-01.jpg",
    (route) => route.abort(),
  );
  await page.addInitScript(
    ({ key }) => {
      localStorage.setItem(
        key,
        JSON.stringify({
          schemaVersion: 1,
          bookmarks: {
            chapterIds: [],
            questionIds: ["question-comprehensive-080"],
          },
          attempts: [],
          preferences: {
            languageView: "bilingual",
            feedbackMode: "immediate",
            randomizeQuestions: true,
            randomizeChoices: true,
          },
        }),
      );
    },
    { key: STORAGE_KEY },
  );
  await page.goto("/#/practice?question=question-comprehensive-080");
  await page.getByRole("button", { name: /Start practice/i }).click();
  const warning =
    "This question is missing a required visual and cannot be answered reliably. / คำถามนี้ขาดภาพที่จำเป็นและไม่สามารถตอบได้อย่างน่าเชื่อถือ";
  await expect(page.getByRole("alert")).toHaveText(warning);
  await expect(page.getByRole("radio").first()).toBeDisabled();
  await expect(page.getByRole("button", { name: "Submit answer" })).toBeDisabled();
});

test("the repaired UNION question remains readable without clipping at representative viewports", async ({
  page,
}) => {
  for (const viewport of [
    { name: "mobile", width: 320, height: 568 },
    { name: "tablet", width: 768, height: 1024 },
    { name: "desktop", width: 1440, height: 900 },
  ]) {
    await page.setViewportSize({
      width: viewport.width,
      height: viewport.height,
    });
    const image = await openVisualQuestion(page);
    const imageBox = await image.boundingBox();
    expect(imageBox?.width ?? Infinity).toBeLessThanOrEqual(viewport.width);
    await expect(page.locator(".choice-list")).toBeVisible();
    await expectNoHorizontalOverflow(page);
    await page.screenshot({
      path: `../reports/screenshots/question-visuals/${viewport.name}/visual-question-080-${viewport.width}x${viewport.height}.png`,
      fullPage: true,
    });
  }
});

test("the repaired distribution diagram remains readable at mobile, tablet, and desktop widths", async ({
  page,
}) => {
  for (const viewport of [
    { name: "mobile", width: 390, height: 844 },
    { name: "tablet", width: 820, height: 1180 },
    { name: "desktop", width: 1280, height: 800 },
  ]) {
    await page.setViewportSize({
      width: viewport.width,
      height: viewport.height,
    });
    const image = await openVisualQuestion(page, {
      questionId: "question-comprehensive-021",
      heading: /distribution be described/,
      imageAlt: /distribution plot used by Question 21/,
    });
    const imageBox = await image.boundingBox();
    expect(imageBox?.width ?? Infinity).toBeLessThanOrEqual(viewport.width);
    await expect(page.locator(".choice-list")).toBeVisible();
    await expectNoHorizontalOverflow(page);
    await page.screenshot({
      path: `../reports/screenshots/question-visuals/${viewport.name}/visual-question-021-${viewport.width}x${viewport.height}.png`,
      fullPage: true,
    });
  }
});

test("visual assets are served with successful image responses", async ({
  request,
}) => {
  for (const path of [
    "/exam-assets/file-7357a61279704b42/question-comprehensive-021/question-visual-01.jpg",
    "/exam-assets/file-7357a61279704b42/question-comprehensive-080/question-visual-01.jpg",
    "/exam-assets/file-7357a61279704b42/question-comprehensive-080/full-question-reference.png",
  ]) {
    const response = await request.get(path);
    expect(response.ok()).toBe(true);
    expect(response.headers()["content-type"]).toMatch(/^image\//);
    expect((await response.body()).byteLength).toBeGreaterThan(1_000);
  }
});
