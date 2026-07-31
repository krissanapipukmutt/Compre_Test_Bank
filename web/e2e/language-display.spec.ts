import { expect, test, type Locator, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";

const PROGRESS_KEY = "compre-study:v1";
const LANGUAGE_KEY = "compre-language-display-mode";
const SESSION_KEY = "compre-active-exam-session";

const questionFixtures = (
  JSON.parse(
    readFileSync(new URL("../src/data/questions.json", import.meta.url), "utf8"),
  ) as {
    questions: {
      question_id: string;
      original_question_en: string;
      choices: { choice_id: string; is_correct: boolean }[];
    }[];
  }
).questions;

type SessionSnapshot = {
  sessionId: string;
  questionIds: string[];
  choiceOrder: Record<string, string[]>;
  answers: Record<string, string[]>;
  submittedQuestionIds: string[];
  currentIndex: number;
  startedAt: number;
};

async function seedBrowser(
  page: Page,
  mode: "bilingual" | "english_only",
  bookmarkedQuestionIds: string[] = [],
) {
  await page.addInitScript(
    ({ languageKey, languageMode, progressKey, questionIds }) => {
      localStorage.setItem(languageKey, languageMode);
      localStorage.setItem(
        progressKey,
        JSON.stringify({
          schemaVersion: 1,
          bookmarks: {
            chapterIds: [],
            topicIds: [],
            questionIds,
          },
          attempts: [],
          preferences: {
            feedbackMode: "immediate",
            randomizeQuestions: false,
            randomizeChoices: false,
          },
        }),
      );
    },
    {
      languageKey: LANGUAGE_KEY,
      languageMode: mode,
      progressKey: PROGRESS_KEY,
      questionIds: bookmarkedQuestionIds,
    },
  );
}

function desktopLanguageControl(page: Page): Locator {
  return page.locator(".desktop-rail .language-display-control");
}

function mobileLanguageControl(page: Page): Locator {
  return page.locator(".mobile-language-bar .language-display-control");
}

async function storedSession(page: Page): Promise<SessionSnapshot> {
  return page.evaluate((key) => {
    const raw = localStorage.getItem(key);
    if (!raw) throw new Error("Active session snapshot is missing");
    return JSON.parse(raw) as SessionSnapshot;
  }, SESSION_KEY);
}

function secondsFromTimer(text: string): number {
  const match = text.match(/(\d{2}):(\d{2})/);
  if (!match) throw new Error(`Unexpected timer text: ${text}`);
  return Number(match[1]) * 60 + Number(match[2]);
}

async function startTenQuestionMock(page: Page) {
  await page.goto("/#/mock");
  await page.getByLabel("Question count").selectOption("10");
  await page.getByRole("button", { name: /Begin mock exam/i }).click();
  await expect(page.locator(".question-card")).toBeVisible();
}

test("timed mock switching preserves assessment state and keeps answers sealed through final submission", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await seedBrowser(page, "bilingual");
  await page.goto("/#/mock");
  const control = desktopLanguageControl(page);
  await control.getByRole("button", { name: "English only" }).click();
  await page.getByLabel("Question count").selectOption("10");
  await page.getByRole("button", { name: /Begin mock exam/i }).click();
  await expect(page.locator(".question-card")).toBeVisible();

  await expect(
    control.getByRole("button", { name: "English only" }),
  ).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByTestId("question-stem-th")).toBeHidden();
  await expect(page.locator(".answer-panel")).toHaveCount(0);
  await expect(page.locator(".choice.is-correct")).toHaveCount(0);

  const questionCard = page.locator(".question-card");
  const questionId = (await questionCard.getAttribute("data-question-id"))!;
  const question = questionFixtures.find(
    (item) => item.question_id === questionId,
  )!;
  const incorrectChoiceId = question.choices.find(
    (choice) => !choice.is_correct,
  )!.choice_id;
  const choiceOrder = await questionCard
    .locator(".choice")
    .evaluateAll((choices) =>
      choices.map((choice) => choice.getAttribute("data-choice-id")),
    );
  await questionCard
    .locator(`[data-choice-id="${incorrectChoiceId}"]`)
    .click();
  await expect(
    questionCard.locator(`[data-choice-id="${incorrectChoiceId}"] input`),
  ).toBeChecked();

  const timerBefore = secondsFromTimer(
    (await page.locator(".timer").textContent())!,
  );
  const before = await storedSession(page);
  const progressBefore = await page.evaluate(
    (key) => localStorage.getItem(key),
    PROGRESS_KEY,
  );

  await control.getByRole("button", { name: "English and Thai" }).click();
  await expect(page.getByTestId("question-stem-th")).toBeVisible();
  await expect(
    questionCard.locator(`[data-choice-id="${incorrectChoiceId}"] input`),
  ).toBeChecked();
  await expect(questionCard).toHaveAttribute("data-question-id", questionId);
  expect(
    await questionCard.locator(".choice").evaluateAll((choices) =>
      choices.map((choice) => choice.getAttribute("data-choice-id")),
    ),
  ).toEqual(choiceOrder);
  await expect(page.locator(".answer-panel")).toHaveCount(0);
  await expect(page.locator(".choice.is-correct")).toHaveCount(0);

  await page.waitForTimeout(1_150);
  const timerAfter = secondsFromTimer(
    (await page.locator(".timer").textContent())!,
  );
  expect(timerAfter).toBeLessThan(timerBefore);
  expect(timerAfter).toBeGreaterThanOrEqual(timerBefore - 3);
  const after = await storedSession(page);
  expect(after.sessionId).toBe(before.sessionId);
  expect(after.questionIds).toEqual(before.questionIds);
  expect(after.choiceOrder).toEqual(before.choiceOrder);
  expect(after.answers).toEqual(before.answers);
  expect(after.submittedQuestionIds).toEqual(before.submittedQuestionIds);
  expect(after.currentIndex).toBe(before.currentIndex);
  expect(after.startedAt).toBe(before.startedAt);
  expect(
    await page.evaluate((key) => localStorage.getItem(key), PROGRESS_KEY),
  ).toBe(progressBefore);

  for (const label of [
    "English only",
    "English and Thai",
    "English only",
  ]) {
    await control.getByRole("button", { name: label }).click();
  }
  await page
    .locator(".question-navigator")
    .getByRole("button", { name: /^Question 2,/ })
    .click();
  await expect(
    control.getByRole("button", { name: "English only" }),
  ).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByTestId("question-stem-th")).toBeHidden();

  await page
    .locator(".question-navigator")
    .getByRole("button", { name: /^Question 10,/ })
    .click();
  await control.getByRole("button", { name: "English and Thai" }).click();
  await control.getByRole("button", { name: "English only" }).click();
  await control.getByRole("button", { name: "English and Thai" }).click();
  await expect(page.getByTestId("question-stem-th")).toBeVisible();
  await page.getByRole("button", { name: /Review & submit/i }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.locator(".answer-panel")).toHaveCount(0);
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Submit exam" })
    .click();

  await expect(page).toHaveURL(/#\/mock-results/);
  const reviewed = page.locator(
    `.question-card[data-question-id="${questionId}"]`,
  );
  await expect(reviewed.locator(".answer-panel")).toBeVisible();
  await expect(
    reviewed.locator(`[data-choice-id="${incorrectChoiceId}"]`),
  ).toHaveClass(/is-incorrect/);
  await expect(reviewed.locator(".answer-panel > p[lang='th']")).toBeVisible();
  const scoreBeforeSwitch = await page.locator(".results-hero h1").textContent();

  await control.getByRole("button", { name: "English only" }).click();
  await expect(reviewed.locator(".answer-panel > p[lang='th']")).toBeHidden();
  await expect(reviewed.locator(".answer-panel > p:not([lang])")).toBeVisible();
  await expect(
    reviewed.locator(".choice__explanation em[lang='th']").first(),
  ).toBeHidden();
  expect(
    await reviewed
      .locator("[lang='th'], [data-language='th']")
      .evaluateAll(
        (nodes) =>
          nodes.filter((node) => getComputedStyle(node).display !== "none")
            .length,
      ),
  ).toBe(0);
  await expect(page.locator(".results-hero h1")).toHaveText(
    scoreBeforeSwitch!,
  );
  await control.getByRole("button", { name: "English and Thai" }).click();
  await expect(reviewed.locator(".answer-panel > p[lang='th']")).toBeVisible();
});

test("refresh during an active mock restores the same session without dataset duplication or reshuffling", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await seedBrowser(page, "english_only");
  await startTenQuestionMock(page);

  const card = page.locator(".question-card");
  const questionId = (await card.getAttribute("data-question-id"))!;
  const choiceId = (await card.locator(".choice").nth(1).getAttribute(
    "data-choice-id",
  ))!;
  await card.locator(`[data-choice-id="${choiceId}"]`).click();
  await page
    .locator(".question-navigator")
    .getByRole("button", { name: /^Question 2,/ })
    .click();
  const before = await storedSession(page);
  const timerBefore = secondsFromTimer(
    (await page.locator(".timer").textContent())!,
  );
  const serialized = await page.evaluate(
    (key) => localStorage.getItem(key)!,
    SESSION_KEY,
  );
  expect(serialized).not.toContain(
    questionFixtures.find((item) => item.question_id === questionId)!
      .original_question_en,
  );

  await page.reload();
  await expect(page.locator(".question-card")).toHaveAttribute(
    "data-question-id",
    before.questionIds[1]!,
  );
  const after = await storedSession(page);
  expect(after).toEqual(before);
  await page
    .locator(".question-navigator")
    .getByRole("button", { name: /^Question 1,/ })
    .click();
  await expect(
    page.locator(`[data-choice-id="${choiceId}"] input`),
  ).toBeChecked();
  expect(
    secondsFromTimer((await page.locator(".timer").textContent())!),
  ).toBeLessThanOrEqual(timerBefore);
  await expect(
    desktopLanguageControl(page).getByRole("button", {
      name: "English only",
    }),
  ).toHaveAttribute("aria-pressed", "true");
});

test("practice permits English attempts followed by bilingual feedback without changing the answer", async ({
  page,
}) => {
  const questionId = "question-comprehensive-027";
  await page.setViewportSize({ width: 1280, height: 800 });
  await seedBrowser(page, "english_only", [questionId]);
  await page.goto(`/#/practice?question=${questionId}`);
  await page.getByRole("button", { name: /Start practice/i }).click();

  const control = desktopLanguageControl(page);
  const input = page.locator(".question-card .choice input").first();
  await page.locator(".question-card .choice").first().click();
  await control.getByRole("button", { name: "English and Thai" }).click();
  await expect(input).toBeChecked();
  await expect(page.getByTestId("question-stem-th")).toBeVisible();
  await expect(page.locator(".answer-panel")).toHaveCount(0);

  await page.getByRole("button", { name: "Submit answer" }).click();
  await expect(page.locator(".answer-panel")).toBeVisible();
  await expect(page.locator(".answer-panel > p[lang='th']")).toBeVisible();
  await control.getByRole("button", { name: "English only" }).click();
  await expect(input).toBeChecked();
  await expect(page.locator(".answer-panel > p[lang='th']")).toBeHidden();
  await expect(page.locator(".answer-panel > p:not([lang])")).toBeVisible();
  await page.getByRole("button", { name: "Finish session" }).click();
  await expect(
    control.getByRole("button", { name: "English only" }),
  ).toHaveAttribute("aria-pressed", "true");
});

test("mobile timed-exam control has 44px targets and does not overlap exam status", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await seedBrowser(page, "english_only");
  await startTenQuestionMock(page);

  const control = mobileLanguageControl(page);
  await expect(control).toBeVisible();
  const boxes = await control.getByRole("button").evaluateAll((buttons) =>
    buttons.map((button) => {
      const box = button.getBoundingClientRect();
      return { width: box.width, height: box.height };
    }),
  );
  for (const box of boxes) {
    expect(box.width).toBeGreaterThanOrEqual(44);
    expect(box.height).toBeGreaterThanOrEqual(44);
  }
  const languageBar = await page.locator(".mobile-language-bar").boundingBox();
  const examStatus = await page.locator(".exam-status").boundingBox();
  expect(languageBar!.y + languageBar!.height).toBeLessThanOrEqual(
    examStatus!.y + 1,
  );

  const firstInput = page.locator(".question-card .choice input").first();
  await page.locator(".question-card .choice").first().click();
  const timerBefore = secondsFromTimer(
    (await page.locator(".timer").textContent())!,
  );
  await control.getByRole("button", { name: "English and Thai" }).click();
  await expect(firstInput).toBeChecked();
  await expect(page.getByTestId("question-stem-th")).toBeVisible();
  await page.waitForTimeout(1_100);
  expect(
    secondsFromTimer((await page.locator(".timer").textContent())!),
  ).toBeLessThan(timerBefore);
  expect(
    await page.evaluate(
      () =>
        document.documentElement.scrollWidth -
        document.documentElement.clientWidth,
    ),
  ).toBeLessThanOrEqual(1);
});

test("Study Library switches immediately and hides every rendered Thai block in English-only mode", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await seedBrowser(page, "bilingual");
  await page.goto(
    "/#/library/topic/topic-bis601-analyst-and-system-success-02",
  );
  const control = desktopLanguageControl(page);
  await expect(page.locator(".topic-content [lang='th']").first()).toBeVisible();

  await control.getByRole("button", { name: "English only" }).click();
  await expect(page.locator(".topic-content [lang='th']").first()).toBeHidden();
  expect(
    await page.locator(".topic-content [lang='th']").evaluateAll((nodes) =>
      nodes.filter((node) => {
        const style = getComputedStyle(node);
        return style.display !== "none" && style.visibility !== "hidden";
      }).length,
    ),
  ).toBe(0);
  await expect(
    page.getByRole("heading", { name: "Systems analyst", level: 1 }),
  ).toBeVisible();
  await expect.poll(() =>
    page.evaluate((key) => localStorage.getItem(key), LANGUAGE_KEY),
  ).toBe("english_only");
});
