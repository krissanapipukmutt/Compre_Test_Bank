import { describe, expect, it } from "vitest";
import subjects from "./data/subjects.json";
import chapters from "./data/chapters.json";
import topics from "./data/topics.json";
import glossary from "./data/glossary.json";
import references from "./data/source-references.json";
import questions from "./data/questions.json";
import {
  AcademicDataError,
  validateAcademicData,
  type RawAcademicPayloads,
} from "./data";

const valid: RawAcademicPayloads = {
  subjects,
  chapters,
  topics,
  glossary,
  sourceReferences: references,
  questions,
};

describe("academic data validation", () => {
  it("parses the complete bilingual dataset", () => {
    const data = validateAcademicData(valid);
    expect(data.subjects).toHaveLength(6);
    expect(data.questions).toHaveLength(105);
    expect(data.questions[0]?.question_th).toMatch(/[\u0E00-\u0E7F]/);
  });

  it("rejects invalid structures", () => {
    expect(() =>
      validateAcademicData({ ...valid, subjects: { subjects: null } }),
    ).toThrow(AcademicDataError);
  });

  it("rejects duplicate IDs", () => {
    const cloned = structuredClone(subjects);
    cloned.subjects.push(structuredClone(cloned.subjects[0]!));
    expect(() => validateAcademicData({ ...valid, subjects: cloned })).toThrow(
      /Duplicate/,
    );
  });

  it("rejects broken subject and chapter relationships", () => {
    const cloned = structuredClone(chapters);
    cloned.chapters[0]!.subject_id = "subject-missing";
    expect(() => validateAcademicData({ ...valid, chapters: cloned })).toThrow(
      /invalid subject/,
    );
  });

  it("rejects answer leakage on unresolved questions", () => {
    const cloned = structuredClone(questions);
    const item = cloned.questions.find(
      (question) => question.answer_status === "unresolvable_question",
    )!;
    item.correct_answer = item.choices[0]!.choice_id;
    item.choices[0]!.is_correct = true;
    expect(() => validateAcademicData({ ...valid, questions: cloned })).toThrow(
      /exposes an answer while unresolved/,
    );
  });
});
