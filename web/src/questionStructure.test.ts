import { describe, expect, it } from "vitest";
import {
  embeddedOptionsDuplicateStructuredChoices,
  parseEmbeddedChoiceText,
} from "./questionStructure";

describe("embedded-choice parser", () => {
  it("leaves a standard structured question alone", () => {
    expect(
      parseEmbeddedChoiceText("Which answer best describes the relationship?"),
    ).toBeNull();
  });

  it("parses A), B), C) markers from one paragraph", () => {
    expect(
      parseEmbeddedChoiceText("Which is incorrect? A) First B) Second C) Third"),
    ).toEqual({
      pattern: "letter_parenthesis",
      stem: "Which is incorrect?",
      options: [
        { marker: "A", text: "First" },
        { marker: "B", text: "Second" },
        { marker: "C", text: "Third" },
      ],
    });
  });

  it("parses A., B., C. markers", () => {
    expect(
      parseEmbeddedChoiceText("Compare these. A. First B. Second C. Third")
        ?.pattern,
    ).toBe("letter_period");
  });

  it("parses (A), (B), (C) markers", () => {
    expect(
      parseEmbeddedChoiceText("Compare these. (A) First (B) Second (C) Third")
        ?.pattern,
    ).toBe("parenthesized_letter");
  });

  it("parses numbered statement markers without treating decimals as options", () => {
    expect(
      parseEmbeddedChoiceText(
        "Which statements apply? 1) Version 1.5 is stable 2) Version 2.0 is current 3) Both require testing",
      )?.options.map((option) => option.marker),
    ).toEqual(["1", "2", "3"]);
  });

  it("parses lowercase markers and normalizes their display labels", () => {
    expect(
      parseEmbeddedChoiceText("Choose one. a) First b) Second c) Third")
        ?.options.map((option) => option.marker),
    ).toEqual(["A", "B", "C"]);
  });

  it("identifies structured choices duplicated inside a flattened stem", () => {
    const parsed = parseEmbeddedChoiceText(
      "Choose one. A) First answer B) Second answer C) Third answer",
    )!;
    expect(
      embeddedOptionsDuplicateStructuredChoices(parsed, [
        "First answer",
        "Second answer",
        "Third answer",
      ]),
    ).toBe(true);
    expect(
      embeddedOptionsDuplicateStructuredChoices(parsed, [
        "A only",
        "B only",
        "All statements",
      ]),
    ).toBe(false);
  });

  it("does not split ordinary code parentheses", () => {
    expect(
      parseEmbeddedChoiceText(
        "What does function call(a) return before call(b) and call(c)?",
      ),
    ).toBeNull();
  });

  it("does not split SQL aliases and function calls", () => {
    expect(
      parseEmbeddedChoiceText(
        "SELECT A.id, B.name, COUNT(C.id) FROM A JOIN B ON A.id = B.id",
      ),
    ).toBeNull();
  });

  it("requires sequential markers rather than applying a global replacement", () => {
    expect(
      parseEmbeddedChoiceText("A) first C) third B) second"),
    ).toBeNull();
  });
});
