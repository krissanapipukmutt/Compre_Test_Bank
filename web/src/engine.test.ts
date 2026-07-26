import { describe, expect, it } from "vitest";
import { academicData } from "./data";
import {
  filterQuestions,
  presentQuestion,
  scoreAttempt,
  scoreQuestion,
  shuffleWithSeed,
} from "./engine";
import type { Question } from "./domain";

const scoreable = academicData.questions.find(
  (question) =>
    question.correct_answer !== null && !question.requires_human_review,
)!;
const review = academicData.questions.find(
  (question) => question.answer_status === "unresolvable_question",
)!;

describe("question engine", () => {
  it("scores a single-choice answer by stable ID", () => {
    expect(scoreQuestion(scoreable, [scoreable.correct_answer as string])).toEqual(
      { scoreable: true, correct: true, earned: 1, possible: 1 },
    );
    expect(scoreQuestion(scoreable, [])).toMatchObject({
      correct: false,
      earned: 0,
    });
  });

  it("scores multiple-select independent of order", () => {
    const baseChoice = scoreable.choices[0]!;
    const secondChoice = scoreable.choices[1]!;
    const multiple: Question = {
      ...scoreable,
      question_type: "multiple_select",
      correct_answer: [baseChoice.choice_id, secondChoice.choice_id],
    };
    expect(
      scoreQuestion(multiple, [secondChoice.choice_id, baseChoice.choice_id])
        .correct,
    ).toBe(true);
    expect(scoreQuestion(multiple, [baseChoice.choice_id]).correct).toBe(false);
  });

  it("leaves review-required questions unscored", () => {
    expect(scoreQuestion(review, [])).toEqual({
      scoreable: false,
      correct: null,
      earned: 0,
      possible: 0,
    });
  });

  it("randomizes deterministically and preserves answer IDs", () => {
    const first = presentQuestion(scoreable, "attempt-one", true);
    const second = presentQuestion(scoreable, "attempt-one", true);
    expect(first.choices.map((choice) => choice.choice_id)).toEqual(
      second.choices.map((choice) => choice.choice_id),
    );
    expect(
      first.choices.some((choice) => choice.choice_id === first.correct_answer),
    ).toBe(true);
    expect(shuffleWithSeed([1, 2, 3, 4, 5], "a")).not.toEqual([1, 2, 3, 4, 5]);
  });

  it("preserves question and choice visual ownership during randomization", () => {
    const visualQuestion = academicData.questions.find(
      (question) => question.question_id === "question-comprehensive-080",
    )!;
    const originalAssetIds = visualQuestion.visual_assets.map(
      (asset) => asset.asset_id,
    );
    const presented = presentQuestion(visualQuestion, "visual-map", true);
    expect(presented.question_id).toBe(visualQuestion.question_id);
    expect(presented.visual_assets.map((asset) => asset.asset_id)).toEqual(
      originalAssetIds,
    );
    expect(
      presented.choices.every((choice) =>
        choice.choice_id.startsWith(visualQuestion.question_id),
      ),
    ).toBe(true);
  });

  it("excludes incomplete visual questions from scoring", () => {
    const unsafe: Question = {
      ...scoreable,
      has_visual_content: true,
      visual_integrity_status: "missing_visual",
      visual_scoring_eligible: false,
      visual_assets: [],
    };
    expect(
      scoreQuestion(unsafe, [unsafe.correct_answer as string]),
    ).toEqual({
      scoreable: false,
      correct: null,
      earned: 0,
      possible: 0,
    });
  });

  it("excludes incomplete translations from scoring without changing the answer key", () => {
    const unsafe: Question = {
      ...scoreable,
      translation_status: "incomplete",
      question_th: "",
    };
    expect(unsafe.correct_answer).toBe(scoreable.correct_answer);
    expect(
      scoreQuestion(unsafe, [unsafe.correct_answer as string]),
    ).toEqual({
      scoreable: false,
      correct: null,
      earned: 0,
      possible: 0,
    });
  });

  it("filters by term, subject, difficulty, and status", () => {
    const result = filterQuestions(academicData.questions, {
      term: "term-1",
      subjectCode: "BIS606",
      difficulty: "easy",
      answerStatus: "verified_from_course_material",
    });
    expect(result.length).toBeGreaterThan(0);
    expect(
      result.every(
        (question) =>
          question.term === "term-1" &&
          question.subject_code === "BIS606" &&
          question.difficulty === "easy" &&
          question.answer_status === "verified_from_course_material",
      ),
    ).toBe(true);
  });

  it("tracks unanswered and unscored questions", () => {
    const summary = scoreAttempt([scoreable, review], {});
    expect(summary.unanswered).toBe(2);
    expect(summary.unscored).toBe(1);
    expect(summary.possible).toBe(1);
  });
});
