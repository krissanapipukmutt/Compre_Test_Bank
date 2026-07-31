import { describe, expect, it } from "vitest";
import { academicData } from "./data";
import { createSession } from "./session";
import {
  ACTIVE_SESSION_STORAGE_KEY,
  loadActiveSession,
  saveActiveSession,
} from "./activeSessionStorage";

function deterministicSession() {
  return createSession(
    academicData.questions,
    {
      mode: "mock",
      filters: {},
      subjectCodes: [],
      questionCount: 3,
      feedbackMode: "delayed",
      randomizeQuestions: true,
      randomizeChoices: true,
      timerMinutes: 30,
    },
    "language-switch-regression",
  );
}

describe("active examination persistence", () => {
  it("restores IDs, order, answers, position, and timer origin without dataset copies", () => {
    const storage = window.localStorage;
    storage.clear();
    const session = deterministicSession();
    const first = session.questions[0]!;
    const selectedChoiceId = first.choices[1]!.choice_id;
    session.answers[first.question_id] = [selectedChoiceId];
    session.submittedQuestionIds = [first.question_id];
    session.currentIndex = 1;

    expect(saveActiveSession(session, storage)).toBe(true);
    const serialized = storage.getItem(ACTIVE_SESSION_STORAGE_KEY)!;
    expect(serialized).not.toContain(first.original_question_en);
    expect(serialized).not.toContain(first.choices[0]!.original_text_en);

    const restored = loadActiveSession(academicData.questions, storage)!;
    expect(restored.sessionId).toBe(session.sessionId);
    expect(restored.questions.map((question) => question.question_id)).toEqual(
      session.questions.map((question) => question.question_id),
    );
    expect(
      restored.questions.map((question) =>
        question.choices.map((choice) => choice.choice_id),
      ),
    ).toEqual(
      session.questions.map((question) =>
        question.choices.map((choice) => choice.choice_id),
      ),
    );
    expect(restored.answers).toEqual(session.answers);
    expect(restored.submittedQuestionIds).toEqual(
      session.submittedQuestionIds,
    );
    expect(restored.currentIndex).toBe(1);
    expect(restored.startedAt).toBe(session.startedAt);
    expect(restored.durationSeconds).toBe(session.durationSeconds);
  });

  it("rejects corrupt choice order instead of silently reshuffling", () => {
    const storage = window.localStorage;
    storage.clear();
    const session = deterministicSession();
    saveActiveSession(session, storage);
    const snapshot = JSON.parse(
      storage.getItem(ACTIVE_SESSION_STORAGE_KEY)!,
    ) as {
      questionIds: string[];
      choiceOrder: Record<string, string[]>;
    };
    snapshot.choiceOrder[snapshot.questionIds[0]!] = ["unknown-choice"];
    storage.setItem(ACTIVE_SESSION_STORAGE_KEY, JSON.stringify(snapshot));

    expect(loadActiveSession(academicData.questions, storage)).toBeNull();
    expect(storage.getItem(ACTIVE_SESSION_STORAGE_KEY)).toBeNull();
  });
});
