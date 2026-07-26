import { describe, expect, it } from "vitest";
import { academicData } from "./data";
import { selectVisualAlt } from "./visual";

const asset = academicData.questions.find(
  (question) => question.question_id === "question-comprehensive-021",
)!.visual_assets[0]!;

describe("bilingual visual alternatives", () => {
  it("selects English and Thai alt text from the active language", () => {
    expect(selectVisualAlt(asset, "en")).toBe(asset.alt_en);
    expect(selectVisualAlt(asset, "en-US")).toBe(asset.alt_en);
    expect(selectVisualAlt(asset, "th")).toBe(asset.alt_th);
    expect(selectVisualAlt(asset, "th-TH")).toBe(asset.alt_th);
  });
});
