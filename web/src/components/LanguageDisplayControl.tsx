import type { LanguageDisplayMode } from "../languageDisplay";

export function LanguageDisplayControl({
  mode,
  onChange,
  className = "",
}: {
  mode: LanguageDisplayMode;
  onChange: (mode: LanguageDisplayMode) => void;
  className?: string;
}) {
  return (
    <div
      aria-label="Language display"
      className={`language-display-control ${className}`.trim()}
      role="group"
    >
      <button
        aria-label="English and Thai"
        aria-pressed={mode === "bilingual"}
        onClick={() => onChange("bilingual")}
        type="button"
      >
        EN + TH
      </button>
      <button
        aria-label="English only"
        aria-pressed={mode === "english_only"}
        onClick={() => onChange("english_only")}
        type="button"
      >
        EN only
      </button>
    </div>
  );
}
