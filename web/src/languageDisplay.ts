export const LANGUAGE_DISPLAY_STORAGE_KEY = "compre-language-display-mode";

export type LanguageDisplayMode = "bilingual" | "english_only";

export const DEFAULT_LANGUAGE_DISPLAY_MODE: LanguageDisplayMode = "bilingual";

export function isLanguageDisplayMode(
  value: unknown,
): value is LanguageDisplayMode {
  return value === "bilingual" || value === "english_only";
}

export function loadLanguageDisplayMode(
  storage: Storage = window.localStorage,
): LanguageDisplayMode {
  try {
    const stored = storage.getItem(LANGUAGE_DISPLAY_STORAGE_KEY);
    if (isLanguageDisplayMode(stored)) return stored;

    // One-time compatibility with the retired preference nested in v1 progress.
    const legacy = storage.getItem("compre-study:v1");
    if (legacy) {
      const parsed = JSON.parse(legacy) as {
        preferences?: { languageView?: unknown };
      };
      if (parsed.preferences?.languageView === "english") {
        return "english_only";
      }
      if (parsed.preferences?.languageView === "bilingual") {
        return "bilingual";
      }
    }
  } catch {
    // Invalid or inaccessible storage falls back to a safe presentation mode.
  }
  return DEFAULT_LANGUAGE_DISPLAY_MODE;
}

export function applyLanguageDisplayMode(mode: LanguageDisplayMode): void {
  document.documentElement.dataset.languageDisplay = mode;
  document.documentElement.lang = "en";
}

export function saveLanguageDisplayMode(
  mode: LanguageDisplayMode,
  storage: Storage = window.localStorage,
): boolean {
  try {
    storage.setItem(LANGUAGE_DISPLAY_STORAGE_KEY, mode);
    return true;
  } catch {
    return false;
  }
}

export function resetLanguageDisplayMode(
  storage: Storage = window.localStorage,
): void {
  storage.removeItem(LANGUAGE_DISPLAY_STORAGE_KEY);
}
