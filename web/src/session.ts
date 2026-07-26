import type {
  PresentedQuestion,
  Question,
  QuestionFilters,
} from "./domain";
import {
  filterQuestions,
  isVisualReady,
  presentQuestion,
  shuffleWithSeed,
} from "./engine";
import { isTranslationReady } from "./translation";

export interface SessionConfig {
  mode: "practice" | "mock";
  filters: QuestionFilters;
  subjectCodes: string[];
  questionCount: number;
  feedbackMode: "immediate" | "delayed";
  randomizeQuestions: boolean;
  randomizeChoices: boolean;
  timerMinutes: number | null;
  bookmarkedQuestionIds?: string[];
  onlyIncorrectQuestionIds?: string[];
  onlyUnansweredQuestionIds?: string[];
  judgmentOnly?: boolean;
  includeStrongExternal?: boolean;
}

export interface ActiveSession {
  sessionId: string;
  mode: "practice" | "mock";
  questions: PresentedQuestion[];
  answers: Record<string, string[]>;
  submittedQuestionIds: string[];
  currentIndex: number;
  startedAt: number;
  durationSeconds: number | null;
  feedbackMode: "immediate" | "delayed";
  finished: boolean;
  finishedAt: number | null;
}

function sessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function createSession(
  questions: readonly Question[],
  config: SessionConfig,
  seed = sessionId(),
): ActiveSession {
  let candidates = filterQuestions(questions, config.filters);
  if (config.subjectCodes.length) {
    candidates = candidates.filter((question) =>
      config.subjectCodes.includes(question.subject_code),
    );
  }
  if (config.bookmarkedQuestionIds?.length) {
    candidates = candidates.filter((question) =>
      config.bookmarkedQuestionIds?.includes(question.question_id),
    );
  }
  if (config.onlyIncorrectQuestionIds?.length) {
    candidates = candidates.filter((question) =>
      config.onlyIncorrectQuestionIds?.includes(question.question_id),
    );
  }
  if (config.onlyUnansweredQuestionIds?.length) {
    candidates = candidates.filter((question) =>
      config.onlyUnansweredQuestionIds?.includes(question.question_id),
    );
  }
  if (config.judgmentOnly) {
    candidates = candidates.filter(
      (question) => question.answer_status === "probabilistic_recommendation",
    );
  }
  if (config.mode === "mock") {
    candidates = candidates.filter(
      (question) =>
        isVisualReady(question) &&
        isTranslationReady(question) &&
        ((!question.requires_human_review &&
          (question.answer_status === "verified_from_course_material" ||
            question.answer_status === "verified_from_external_source")) ||
          (config.includeStrongExternal === true &&
            question.answer_status ===
              "strongly_supported_by_external_source")),
    );
  }
  const selected = (
    config.randomizeQuestions
      ? shuffleWithSeed(candidates, `${seed}:questions`)
      : candidates
  ).slice(0, Math.max(1, config.questionCount));
  return {
    sessionId: seed,
    mode: config.mode,
    questions: selected.map((question) =>
      presentQuestion(question, seed, config.randomizeChoices),
    ),
    answers: {},
    submittedQuestionIds: [],
    currentIndex: 0,
    startedAt: Date.now(),
    durationSeconds:
      config.timerMinutes === null ? null : config.timerMinutes * 60,
    feedbackMode: config.feedbackMode,
    finished: false,
    finishedAt: null,
  };
}

export function remainingSeconds(
  startedAt: number,
  durationSeconds: number | null,
  now = Date.now(),
): number | null {
  if (durationSeconds === null) return null;
  const elapsed = Math.max(0, Math.floor((now - startedAt) / 1000));
  return Math.max(0, durationSeconds - elapsed);
}
