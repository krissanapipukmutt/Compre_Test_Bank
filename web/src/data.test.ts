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

  it("rejects a missing Thai question translation", () => {
    const cloned = structuredClone(questions);
    cloned.questions[0]!.question_th = "";
    expect(() => validateAcademicData({ ...valid, questions: cloned })).toThrow(
      /question Thai must be a non-empty string/,
    );
  });

  it("rejects placeholder and repeated-English choice translations", () => {
    const placeholder = structuredClone(questions);
    placeholder.questions[0]!.choices[0]!.text_th =
      "คำศัพท์/ข้อความภาษาอังกฤษตามต้นฉบับ";
    expect(() =>
      validateAcademicData({ ...valid, questions: placeholder }),
    ).toThrow(/placeholder/);

    const repeated = structuredClone(questions);
    repeated.questions[0]!.choices[0]!.text_th =
      repeated.questions[0]!.choices[0]!.original_text_en;
    repeated.questions[0]!.choices[0]!.translation_review_note =
      "ตรวจแล้วแต่ไม่มีข้อยกเว้น";
    expect(() =>
      validateAcademicData({ ...valid, questions: repeated }),
    ).toThrow(/repeats English/);
  });

  it("keeps the supplied marketing fixture bilingual without changing its answer", () => {
    const data = validateAcademicData(valid);
    const marketing = data.questions.find(
      (question) => question.question_id === "question-comprehensive-052",
    )!;
    expect(marketing.original_question_en).toBe(
      "Using a successful brand name to introduce additional items in a given product category under the same brand name (such as new colors, package sizes, flavors, or forms) is called a(n):",
    );
    expect(marketing.question_th).toBe(
      "การใช้ชื่อตราสินค้าที่ประสบความสำเร็จเพื่อเพิ่มสินค้าใหม่ภายใต้ตราสินค้าเดิมในหมวดหมู่ผลิตภัณฑ์เดียวกัน เช่น การเพิ่มสี ขนาดบรรจุภัณฑ์ รสชาติ หรือรูปแบบ เรียกว่าอะไร",
    );
    expect(marketing.choices.map((choice) => choice.text_th)).toEqual([
      "การขยายสายผลิตภัณฑ์ (Line Extension)",
      "การพัฒนาผลิตภัณฑ์ (Product Development)",
      "การขยายตราสินค้า (Brand Extension)",
      "การใช้หลายตราสินค้า (Multi-branding)",
      "ตราสินค้าใหม่ (New Brands)",
    ]);
    expect(marketing.correct_answer).toBe(
      "question-comprehensive-052-choice-1",
    );
  });
});
