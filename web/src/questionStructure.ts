export type EmbeddedChoicePattern =
  | "letter_parenthesis"
  | "letter_period"
  | "parenthesized_letter"
  | "number_parenthesis";

export interface ParsedEmbeddedOption {
  marker: string;
  text: string;
}

export interface ParsedQuestionStructure {
  pattern: EmbeddedChoicePattern;
  stem: string;
  options: ParsedEmbeddedOption[];
}

interface PatternDefinition {
  name: EmbeddedChoicePattern;
  expression: RegExp;
  kind: "letter" | "number";
}

const patterns: PatternDefinition[] = [
  {
    name: "parenthesized_letter",
    expression: /(?:^|\s)\(([A-Ea-e])\)\s+/g,
    kind: "letter",
  },
  {
    name: "letter_parenthesis",
    expression: /(?:^|\s)([A-Ea-e])\)\s*/g,
    kind: "letter",
  },
  {
    name: "letter_period",
    expression: /(?:^|\s)([A-Ea-e])\.\s+/g,
    kind: "letter",
  },
  {
    name: "number_parenthesis",
    expression: /(?:^|\s)([1-5])\)\s+/g,
    kind: "number",
  },
];

function sequential(markers: string[], kind: "letter" | "number"): boolean {
  if (markers.length < 2) return false;
  const values = markers.map((marker) =>
    kind === "letter"
      ? marker.toUpperCase().charCodeAt(0) - 65
      : Number.parseInt(marker, 10) - 1,
  );
  return values.every(
    (value, index) => index === 0 || value === values[index - 1]! + 1,
  );
}

export function parseEmbeddedChoiceText(
  value: string,
): ParsedQuestionStructure | null {
  const candidates: ParsedQuestionStructure[] = [];
  for (const pattern of patterns) {
    const matches = [...value.matchAll(pattern.expression)];
    const markers = matches.map((match) => match[1] ?? "");
    if (!sequential(markers, pattern.kind)) continue;
    const markerStarts = matches.map((match) => {
      const markerOffset = match[0].indexOf(match[1] ?? "");
      return (match.index ?? 0) + Math.max(0, markerOffset);
    });
    const stem = value.slice(0, markerStarts[0]).trim();
    if (!stem) continue;
    const options = matches.map((match, index) => {
      const start = (match.index ?? 0) + match[0].length;
      const end = markerStarts[index + 1] ?? value.length;
      return {
        marker: (match[1] ?? "").toUpperCase(),
        text: value.slice(start, end).trim(),
      };
    });
    if (options.some((option) => !option.text)) continue;
    candidates.push({ pattern: pattern.name, stem, options });
  }
  return (
    candidates.sort(
      (left, right) => right.options.length - left.options.length,
    )[0] ?? null
  );
}

function comparableText(value: string): string {
  return value.toLocaleLowerCase().replace(/\s+/g, " ").trim();
}

export function embeddedOptionsDuplicateStructuredChoices(
  parsed: ParsedQuestionStructure,
  structuredChoices: string[],
): boolean {
  if (
    parsed.options.length < 2 ||
    parsed.options.length !== structuredChoices.length
  ) {
    return false;
  }
  return parsed.options.every(
    (option, index) =>
      comparableText(option.text) ===
      comparableText(structuredChoices[index] ?? ""),
  );
}
