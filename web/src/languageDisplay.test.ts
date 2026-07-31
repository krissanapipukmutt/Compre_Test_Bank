import { describe, expect, it } from "vitest";
import {
  LANGUAGE_DISPLAY_STORAGE_KEY,
  applyLanguageDisplayMode,
  loadLanguageDisplayMode,
  resetLanguageDisplayMode,
  saveLanguageDisplayMode,
} from "./languageDisplay";

describe("language display preference", () => {
  it("uses the exact independent key and persists only supported modes", () => {
    const storage = window.localStorage;
    storage.clear();

    expect(loadLanguageDisplayMode(storage)).toBe("bilingual");
    expect(saveLanguageDisplayMode("english_only", storage)).toBe(true);
    expect(storage.getItem(LANGUAGE_DISPLAY_STORAGE_KEY)).toBe("english_only");
    expect(loadLanguageDisplayMode(storage)).toBe("english_only");

    storage.setItem(LANGUAGE_DISPLAY_STORAGE_KEY, "thai");
    expect(loadLanguageDisplayMode(storage)).toBe("bilingual");
  });

  it("migrates the retired English preference without changing progress data", () => {
    const storage = window.localStorage;
    const legacy = JSON.stringify({
      schemaVersion: 1,
      bookmarks: { chapterIds: ["chapter-1"] },
      preferences: { languageView: "english" },
    });
    storage.clear();
    storage.setItem("compre-study:v1", legacy);

    expect(loadLanguageDisplayMode(storage)).toBe("english_only");
    expect(storage.getItem("compre-study:v1")).toBe(legacy);
  });

  it("applies presentation metadata and resets only its own key", () => {
    const storage = window.localStorage;
    storage.clear();
    storage.setItem("unrelated", "keep");
    saveLanguageDisplayMode("english_only", storage);

    applyLanguageDisplayMode("english_only");
    expect(document.documentElement.dataset.languageDisplay).toBe(
      "english_only",
    );
    expect(document.documentElement.lang).toBe("en");

    resetLanguageDisplayMode(storage);
    expect(storage.getItem(LANGUAGE_DISPLAY_STORAGE_KEY)).toBeNull();
    expect(storage.getItem("unrelated")).toBe("keep");
  });
});
