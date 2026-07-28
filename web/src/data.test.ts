import { describe, expect, it } from "vitest";
import subjects from "./data/subjects.json";
import chapters from "./data/chapters.json";
import topics from "./data/topics.json";
import glossary from "./data/glossary.json";
import references from "./data/source-references.json";
import questions from "./data/questions.json";
import externalSources from "./data/external-sources.json";
import questionStudyCoverage from "./data/question-study-coverage.json";
import studyTopicQuestionMap from "./data/study-topic-question-map.json";
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
  externalSources,
  questionStudyCoverage,
  studyTopicQuestionMap,
};

describe("academic data validation", () => {
  it("parses the complete bilingual dataset", () => {
    const data = validateAcademicData(valid);
    expect(data.subjects).toHaveLength(6);
    expect(data.chapters).toHaveLength(44);
    expect(data.topics).toHaveLength(132);
    expect(data.questions).toHaveLength(105);
    expect(data.questionStudyCoverage).toHaveLength(105);
    expect(data.studyTopicQuestionMap).toHaveLength(132);
    expect(data.questions[0]?.question_th).toMatch(/[\u0E00-\u0E7F]/);
  });

  it("loads structured bilingual learning content for every topic", () => {
    const data = validateAcademicData(valid);
    for (const topic of data.topics) {
      expect(topic.learning_objectives_en).toHaveLength(
        topic.learning_objectives_th.length,
      );
      expect(topic.learning_objectives_en.length).toBeGreaterThanOrEqual(3);
      expect(topic.lesson_sections.length).toBeGreaterThanOrEqual(3);
      expect(topic.key_terms.length).toBeGreaterThanOrEqual(1);
      expect(topic.comparisons.length).toBeGreaterThanOrEqual(1);
      expect(topic.process_steps.length).toBeGreaterThanOrEqual(3);
      expect(topic.examples.length).toBeGreaterThanOrEqual(1);
      expect(topic.common_misunderstandings.length).toBeGreaterThanOrEqual(1);
      expect(topic.exam_focus.points_en).toHaveLength(
        topic.exam_focus.points_th?.length ?? 0,
      );
      expect(topic.quick_review.key_points_en.length).toBeGreaterThanOrEqual(3);
    }
  });

  it("loads complete bidirectional exam-to-study coverage without answer leakage", () => {
    const data = validateAcademicData(valid);
    expect(data.questionStudyCoverage).toHaveLength(data.questions.length);
    expect(data.studyTopicQuestionMap).toHaveLength(data.topics.length);
    expect(
      data.questionStudyCoverage.every(
        (item) => item.current_coverage_status === "fully_covered",
      ),
    ).toBe(true);
    expect(
      data.studyTopicQuestionMap.reduce(
        (total, item) => total + item.question_count,
        0,
      ),
    ).toBe(105);
    for (const coverage of data.questionStudyCoverage) {
      const reverse = data.questionMapByTopicId.get(
        coverage.primary_study_topic_id,
      );
      expect(reverse?.related_question_ids).toContain(coverage.question_id);
      expect(
        data.questions.find(
          (question) => question.question_id === coverage.question_id,
        )?.study_topic_ids,
      ).toEqual(coverage.related_study_topic_ids);
    }
    const serialized = JSON.stringify(data.questionStudyCoverage);
    expect(serialized).not.toContain('"correct_answer"');
    expect(serialized).not.toContain('"final_answer"');
    expect(serialized).not.toContain("choice-");
  });

  it("loads only the nine source-verified embedded-statement questions", () => {
    const data = validateAcademicData(valid);
    const normalized = data.questions
      .filter((question) => question.embedded_choices_detected)
      .map((question) => question.question_id);

    expect(normalized).toEqual([
      "question-comprehensive-004",
      "question-comprehensive-006",
      "question-comprehensive-007",
      "question-comprehensive-008",
      "question-comprehensive-009",
      "question-comprehensive-010",
      "question-comprehensive-019",
      "question-comprehensive-020",
      "question-comprehensive-028",
    ]);
    for (const question of data.questions) {
      expect(question.raw_original_question_en).toBe(
        question.original_question_en,
      );
      expect(question.raw_original_question_th).toBe(question.question_th);
      if (question.embedded_choices_detected) {
        expect(question.normalization_status).toBe("normalized");
        expect(question.embedded_options).toHaveLength(3);
      } else {
        expect(question.normalization_status).toBe("not_required");
        expect(question.embedded_options).toHaveLength(0);
      }
    }
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
