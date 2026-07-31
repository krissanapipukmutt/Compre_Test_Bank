import type { PresentedQuestion, Question } from "./domain";
import type { ActiveSession } from "./session";

export const ACTIVE_SESSION_STORAGE_KEY = "compre-active-exam-session";

export interface ActiveSessionSnapshot {
  schemaVersion: 1;
  sessionId: string;
  mode: "practice" | "mock";
  questionIds: string[];
  choiceOrder: Record<string, string[]>;
  answers: Record<string, string[]>;
  submittedQuestionIds: string[];
  currentIndex: number;
  startedAt: number;
  durationSeconds: number | null;
  feedbackMode: "immediate" | "delayed";
  finished: boolean;
  finishedAt: number | null;
}

function isStringArray(value: unknown): value is string[] {
  return (
    Array.isArray(value) &&
    value.every((item) => typeof item === "string")
  );
}

function snapshotFromSession(session: ActiveSession): ActiveSessionSnapshot {
  return {
    schemaVersion: 1,
    sessionId: session.sessionId,
    mode: session.mode,
    questionIds: session.questions.map((question) => question.question_id),
    choiceOrder: Object.fromEntries(
      session.questions.map((question) => [
        question.question_id,
        question.choices.map((choice) => choice.choice_id),
      ]),
    ),
    answers: session.answers,
    submittedQuestionIds: session.submittedQuestionIds,
    currentIndex: session.currentIndex,
    startedAt: session.startedAt,
    durationSeconds: session.durationSeconds,
    feedbackMode: session.feedbackMode,
    finished: session.finished,
    finishedAt: session.finishedAt,
  };
}

function parseSnapshot(value: unknown): ActiveSessionSnapshot | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const item = value as Partial<ActiveSessionSnapshot>;
  if (
    item.schemaVersion !== 1 ||
    typeof item.sessionId !== "string" ||
    !item.sessionId ||
    (item.mode !== "practice" && item.mode !== "mock") ||
    !isStringArray(item.questionIds) ||
    item.questionIds.length === 0 ||
    new Set(item.questionIds).size !== item.questionIds.length ||
    !item.choiceOrder ||
    typeof item.choiceOrder !== "object" ||
    Array.isArray(item.choiceOrder) ||
    !item.answers ||
    typeof item.answers !== "object" ||
    Array.isArray(item.answers) ||
    !isStringArray(item.submittedQuestionIds) ||
    typeof item.currentIndex !== "number" ||
    !Number.isInteger(item.currentIndex) ||
    item.currentIndex < 0 ||
    item.currentIndex >= item.questionIds.length ||
    typeof item.startedAt !== "number" ||
    !Number.isFinite(item.startedAt) ||
    !(
      item.durationSeconds === null ||
      (typeof item.durationSeconds === "number" &&
        Number.isFinite(item.durationSeconds) &&
        item.durationSeconds >= 0)
    ) ||
    (item.feedbackMode !== "immediate" &&
      item.feedbackMode !== "delayed") ||
    typeof item.finished !== "boolean" ||
    !(
      item.finishedAt === null ||
      (typeof item.finishedAt === "number" &&
        Number.isFinite(item.finishedAt))
    )
  ) {
    return null;
  }
  return item as ActiveSessionSnapshot;
}

function restoreQuestion(
  question: Question,
  choiceIds: unknown,
): PresentedQuestion | null {
  if (!isStringArray(choiceIds)) return null;
  const choiceById = new Map(
    question.choices.map((choice) => [choice.choice_id, choice]),
  );
  if (
    choiceIds.length !== question.choices.length ||
    new Set(choiceIds).size !== choiceIds.length ||
    choiceIds.some((choiceId) => !choiceById.has(choiceId))
  ) {
    return null;
  }
  return {
    ...question,
    choices: choiceIds.map((choiceId) => choiceById.get(choiceId)!),
  };
}

export function restoreActiveSession(
  snapshot: ActiveSessionSnapshot,
  questions: readonly Question[],
): ActiveSession | null {
  const questionById = new Map(
    questions.map((question) => [question.question_id, question]),
  );
  const restored: PresentedQuestion[] = [];
  for (const questionId of snapshot.questionIds) {
    const question = questionById.get(questionId);
    const presented = question
      ? restoreQuestion(question, snapshot.choiceOrder[questionId])
      : null;
    if (!presented) return null;
    restored.push(presented);
  }
  const validQuestionIds = new Set(snapshot.questionIds);
  const choiceIdsByQuestion = new Map(
    restored.map((question) => [
      question.question_id,
      new Set(question.choices.map((choice) => choice.choice_id)),
    ]),
  );
  if (
    snapshot.submittedQuestionIds.some(
      (questionId) => !validQuestionIds.has(questionId),
    )
  ) {
    return null;
  }
  for (const [questionId, answer] of Object.entries(snapshot.answers)) {
    const choiceIds = choiceIdsByQuestion.get(questionId);
    if (
      !choiceIds ||
      !isStringArray(answer) ||
      answer.some((choiceId) => !choiceIds.has(choiceId))
    ) {
      return null;
    }
  }
  return {
    sessionId: snapshot.sessionId,
    mode: snapshot.mode,
    questions: restored,
    answers: snapshot.answers,
    submittedQuestionIds: snapshot.submittedQuestionIds,
    currentIndex: snapshot.currentIndex,
    startedAt: snapshot.startedAt,
    durationSeconds: snapshot.durationSeconds,
    feedbackMode: snapshot.feedbackMode,
    finished: snapshot.finished,
    finishedAt: snapshot.finishedAt,
  };
}

export function loadActiveSession(
  questions: readonly Question[],
  storage: Storage = window.localStorage,
): ActiveSession | null {
  try {
    const raw = storage.getItem(ACTIVE_SESSION_STORAGE_KEY);
    if (!raw) return null;
    const snapshot = parseSnapshot(JSON.parse(raw));
    const restored = snapshot
      ? restoreActiveSession(snapshot, questions)
      : null;
    if (!restored) storage.removeItem(ACTIVE_SESSION_STORAGE_KEY);
    return restored;
  } catch {
    storage.removeItem(ACTIVE_SESSION_STORAGE_KEY);
    return null;
  }
}

export function saveActiveSession(
  session: ActiveSession | null,
  storage: Storage = window.localStorage,
): boolean {
  try {
    if (!session) {
      storage.removeItem(ACTIVE_SESSION_STORAGE_KEY);
    } else {
      storage.setItem(
        ACTIVE_SESSION_STORAGE_KEY,
        JSON.stringify(snapshotFromSession(session)),
      );
    }
    return true;
  } catch {
    return false;
  }
}

export function clearActiveSession(
  storage: Storage = window.localStorage,
): void {
  storage.removeItem(ACTIVE_SESSION_STORAGE_KEY);
}
