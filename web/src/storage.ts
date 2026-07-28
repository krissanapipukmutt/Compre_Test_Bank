import type { ScoreSummary } from "./engine";

export const STORAGE_KEY = "compre-study:v1";

export interface Attempt {
  attemptId: string;
  createdAt: string;
  mode: "practice" | "mock";
  questionIds: string[];
  answers: Record<string, string[]>;
  choiceOrder: Record<string, string[]>;
  score: ScoreSummary;
  durationSeconds: number;
  subjectCodes: string[];
}

export interface LocalState {
  schemaVersion: 1;
  bookmarks: {
    chapterIds: string[];
    topicIds: string[];
    questionIds: string[];
  };
  attempts: Attempt[];
  preferences: {
    languageView: "bilingual" | "english" | "thai";
    feedbackMode: "immediate" | "delayed";
    randomizeQuestions: boolean;
    randomizeChoices: boolean;
  };
}

export const DEFAULT_LOCAL_STATE: LocalState = {
  schemaVersion: 1,
  bookmarks: { chapterIds: [], topicIds: [], questionIds: [] },
  attempts: [],
  preferences: {
    languageView: "bilingual",
    feedbackMode: "immediate",
    randomizeQuestions: true,
    randomizeChoices: true,
  },
};

function isLocalState(value: unknown): value is LocalState {
  if (!value || typeof value !== "object") {
    return false;
  }
  const candidate = value as Partial<LocalState>;
  return (
    candidate.schemaVersion === 1 &&
    Boolean(candidate.bookmarks) &&
    Array.isArray(candidate.bookmarks?.chapterIds) &&
    Array.isArray(candidate.bookmarks?.questionIds) &&
    Array.isArray(candidate.attempts) &&
    Boolean(candidate.preferences)
  );
}

export interface LoadResult {
  state: LocalState;
  recovered: boolean;
}

export function loadLocalState(storage: Storage = window.localStorage): LoadResult {
  try {
    const raw = storage.getItem(STORAGE_KEY);
    if (!raw) {
      return { state: structuredClone(DEFAULT_LOCAL_STATE), recovered: false };
    }
    const parsed: unknown = JSON.parse(raw);
    if (!isLocalState(parsed)) {
      return { state: structuredClone(DEFAULT_LOCAL_STATE), recovered: true };
    }
    return {
      state: {
        ...parsed,
        bookmarks: {
          ...parsed.bookmarks,
          topicIds: Array.isArray(parsed.bookmarks.topicIds)
            ? parsed.bookmarks.topicIds
            : [],
        },
      },
      recovered: false,
    };
  } catch {
    return { state: structuredClone(DEFAULT_LOCAL_STATE), recovered: true };
  }
}

export function saveLocalState(
  state: LocalState,
  storage: Storage = window.localStorage,
): boolean {
  try {
    storage.setItem(STORAGE_KEY, JSON.stringify(state));
    return true;
  } catch {
    return false;
  }
}

export function resetLocalState(
  storage: Storage = window.localStorage,
): LocalState {
  storage.removeItem(STORAGE_KEY);
  return structuredClone(DEFAULT_LOCAL_STATE);
}

export function toggleId(values: readonly string[], id: string): string[] {
  return values.includes(id)
    ? values.filter((value) => value !== id)
    : [...values, id];
}
