import { describe, expect, it } from "vitest";
import {
  DEFAULT_LOCAL_STATE,
  STORAGE_KEY,
  loadLocalState,
  resetLocalState,
  saveLocalState,
  toggleId,
} from "./storage";

describe("local progress storage", () => {
  it("persists and reloads progress", () => {
    const storage = window.localStorage;
    storage.clear();
    const state = structuredClone(DEFAULT_LOCAL_STATE);
    state.bookmarks.questionIds.push("question-1");
    expect(saveLocalState(state, storage)).toBe(true);
    expect(loadLocalState(storage).state.bookmarks.questionIds).toEqual([
      "question-1",
    ]);
  });

  it("recovers safely from invalid data", () => {
    window.localStorage.setItem(STORAGE_KEY, "{broken");
    const result = loadLocalState(window.localStorage);
    expect(result.recovered).toBe(true);
    expect(result.state).toEqual(DEFAULT_LOCAL_STATE);
  });

  it("toggles bookmarks and resets only the application key", () => {
    expect(toggleId([], "a")).toEqual(["a"]);
    expect(toggleId(["a"], "a")).toEqual([]);
    window.localStorage.setItem("unrelated", "keep");
    window.localStorage.setItem(STORAGE_KEY, "{}");
    resetLocalState(window.localStorage);
    expect(window.localStorage.getItem(STORAGE_KEY)).toBeNull();
    expect(window.localStorage.getItem("unrelated")).toBe("keep");
  });
});

