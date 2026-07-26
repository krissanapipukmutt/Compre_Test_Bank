import { describe, expect, it } from "vitest";
import { academicData } from "./data";
import { createSession, remainingSeconds } from "./session";
import type { Question } from "./domain";

describe("session creation and timer", () => {
  it("creates filtered randomized sessions with stable answer integrity", () => {
    const session = createSession(
      academicData.questions,
      {
        mode: "practice",
        filters: { subjectCode: "BIS606" },
        subjectCodes: [],
        questionCount: 5,
        feedbackMode: "immediate",
        randomizeQuestions: true,
        randomizeChoices: true,
        timerMinutes: null,
      },
      "stable-seed",
    );
    expect(session.questions).toHaveLength(5);
    expect(
      session.questions.every((question) => question.subject_code === "BIS606"),
    ).toBe(true);
    expect(
      session.questions.every(
        (question) =>
          question.correct_answer === null ||
          question.choices.some(
            (choice) => choice.choice_id === question.correct_answer,
          ),
      ),
    ).toBe(true);
  });

  it("calculates timer expiration without going below zero", () => {
    const startedAt = 1_000_000;
    expect(remainingSeconds(startedAt, 60, startedAt + 10_000)).toBe(50);
    expect(remainingSeconds(startedAt, 60, startedAt + 61_000)).toBe(0);
    expect(remainingSeconds(startedAt, null, startedAt + 61_000)).toBeNull();
  });

  it("enforces mock evidence eligibility and the strong-external opt-in", () => {
    const normal = createSession(
      academicData.questions,
      {
        mode: "mock",
        filters: {},
        subjectCodes: [],
        questionCount: 105,
        feedbackMode: "delayed",
        randomizeQuestions: false,
        randomizeChoices: false,
        timerMinutes: null,
      },
      "normal-mock",
    );
    expect(
      normal.questions.every(
        (question) =>
          !question.requires_human_review &&
          (question.answer_status === "verified_from_course_material" ||
            question.answer_status === "verified_from_external_source"),
      ),
    ).toBe(true);

    const withStrongExternal = createSession(
      academicData.questions,
      {
        mode: "mock",
        filters: {},
        subjectCodes: [],
        questionCount: 105,
        feedbackMode: "delayed",
        randomizeQuestions: false,
        randomizeChoices: false,
        timerMinutes: null,
        includeStrongExternal: true,
      },
      "external-opt-in",
    );
    expect(withStrongExternal.questions.length).toBe(
      normal.questions.length + 2,
    );
    expect(
      withStrongExternal.questions.some(
        (question) =>
          question.answer_status ===
          "strongly_supported_by_external_source",
      ),
    ).toBe(true);
  });

  it("creates an unscored probability-only judgment queue", () => {
    const session = createSession(
      academicData.questions,
      {
        mode: "practice",
        filters: {},
        subjectCodes: [],
        questionCount: 10,
        feedbackMode: "immediate",
        randomizeQuestions: false,
        randomizeChoices: false,
        timerMinutes: null,
        judgmentOnly: true,
      },
      "judgment",
    );
    expect(session.questions).toHaveLength(2);
    expect(
      session.questions.every(
        (question) =>
          question.answer_status === "probabilistic_recommendation",
      ),
    ).toBe(true);
  });

  it("excludes visually incomplete questions from mock sessions", () => {
    const safe = academicData.questions.find(
      (question) =>
        question.answer_status === "verified_from_course_material" &&
        !question.requires_human_review,
    )!;
    const incomplete: Question = {
      ...safe,
      question_id: "synthetic-visually-incomplete",
      has_visual_content: true,
      visual_integrity_status: "partially_readable",
      visual_scoring_eligible: false,
      visual_assets: [],
    };
    const session = createSession(
      [incomplete],
      {
        mode: "mock",
        filters: {},
        subjectCodes: [],
        questionCount: 1,
        feedbackMode: "delayed",
        randomizeQuestions: false,
        randomizeChoices: false,
        timerMinutes: null,
      },
      "visual-safety",
    );
    expect(session.questions).toHaveLength(0);
  });
});
