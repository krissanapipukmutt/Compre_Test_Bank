import subjectsJson from "./data/subjects.json";
import chaptersJson from "./data/chapters.json";
import topicsJson from "./data/topics.json";
import glossaryJson from "./data/glossary.json";
import referencesJson from "./data/source-references.json";
import questionsJson from "./data/questions.json";
import type {
  AcademicData,
  Chapter,
  GlossaryEntry,
  Question,
  SourceReference,
  Subject,
  Topic,
} from "./domain";

type UnknownRecord = Record<string, unknown>;

export class AcademicDataError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AcademicDataError";
  }
}

function record(value: unknown, label: string): UnknownRecord {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new AcademicDataError(`${label} must be an object`);
  }
  return value as UnknownRecord;
}

function list(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) {
    throw new AcademicDataError(`${label} must be an array`);
  }
  return value;
}

function text(value: unknown, label: string): string {
  if (typeof value !== "string" || !value.trim()) {
    throw new AcademicDataError(`${label} must be a non-empty string`);
  }
  return value;
}

function finiteNumber(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new AcademicDataError(`${label} must be a finite number`);
  }
  return value;
}

function validateVisualAssets(
  rawAssets: unknown,
  questionId: string,
): UnknownRecord[] {
  const assets = list(rawAssets, `${questionId}.visual_assets`).map(
    (asset, index) =>
      record(asset, `${questionId}.visual_assets[${index}]`),
  );
  uniqueIds(assets, "asset_id", `${questionId} visual assets`);
  const allowedPlacements = new Set([
    "after_translation_before_choices",
    "within_choice",
    "full_question_reference",
  ]);
  for (const asset of assets) {
    const path = text(asset.public_path, `${questionId} visual public_path`);
    if (asset.path !== path) {
      throw new AcademicDataError(
        `${questionId} visual path and public_path must match`,
      );
    }
    if (!path.startsWith("/exam-assets/") || path.includes("..")) {
      throw new AcademicDataError(
        `${questionId} visual path must be a safe /exam-assets/ path`,
      );
    }
    text(asset.alt_en, `${questionId} visual alt_en`);
    text(asset.alt_th, `${questionId} visual alt_th`);
    text(asset.sha256, `${questionId} visual sha256`);
    text(asset.source_file_id, `${questionId} visual source_file_id`);
    finiteNumber(asset.width, `${questionId} visual width`);
    finiteNumber(asset.height, `${questionId} visual height`);
    if (
      !allowedPlacements.has(
        text(asset.placement, `${questionId} visual placement`),
      )
    ) {
      throw new AcademicDataError(`${questionId} has an invalid visual placement`);
    }
  }
  return assets;
}

function uniqueIds(
  values: UnknownRecord[],
  field: string,
  label: string,
): Set<string> {
  const ids = values.map((item, index) =>
    text(item[field], `${label}[${index}].${field}`),
  );
  const unique = new Set(ids);
  if (unique.size !== ids.length) {
    throw new AcademicDataError(`Duplicate ${label} ${field}`);
  }
  return unique;
}

function payloadList(raw: unknown, key: string): UnknownRecord[] {
  const payload = record(raw, `${key} payload`);
  return list(payload[key], key).map((item, index) =>
    record(item, `${key}[${index}]`),
  );
}

export interface RawAcademicPayloads {
  subjects: unknown;
  chapters: unknown;
  topics: unknown;
  glossary: unknown;
  sourceReferences: unknown;
  questions: unknown;
}

export function validateAcademicData(raw: RawAcademicPayloads): AcademicData {
  const subjectRecords = payloadList(raw.subjects, "subjects");
  const chapterRecords = payloadList(raw.chapters, "chapters");
  const topicRecords = payloadList(raw.topics, "topics");
  const glossaryRecords = payloadList(raw.glossary, "glossary");
  const referenceRecords = payloadList(
    raw.sourceReferences,
    "source_references",
  );
  const questionRecords = payloadList(raw.questions, "questions");

  const subjectIds = uniqueIds(subjectRecords, "subject_id", "subjects");
  const subjectCodes = uniqueIds(subjectRecords, "course_code", "subjects");
  const chapterIds = uniqueIds(chapterRecords, "chapter_id", "chapters");
  const topicIds = uniqueIds(topicRecords, "topic_id", "topics");
  uniqueIds(glossaryRecords, "glossary_id", "glossary");
  const referenceIds = uniqueIds(
    referenceRecords,
    "source_reference_id",
    "source_references",
  );
  uniqueIds(questionRecords, "question_id", "questions");

  for (const item of subjectRecords) {
    text(item.course_title_en, "subject.course_title_en");
    text(item.course_title_th, "subject.course_title_th");
    if (!Array.isArray(item.chapter_ids)) {
      throw new AcademicDataError("subject.chapter_ids must be an array");
    }
  }
  for (const item of chapterRecords) {
    if (!subjectIds.has(text(item.subject_id, "chapter.subject_id"))) {
      throw new AcademicDataError(
        `Chapter ${String(item.chapter_id)} has an invalid subject`,
      );
    }
    for (const sourceId of list(
      item.source_reference_ids,
      "chapter.source_reference_ids",
    )) {
      if (!referenceIds.has(text(sourceId, "chapter source reference"))) {
        throw new AcademicDataError(
          `Chapter ${String(item.chapter_id)} has an invalid source reference`,
        );
      }
    }
  }
  for (const item of topicRecords) {
    if (!subjectIds.has(text(item.subject_id, "topic.subject_id"))) {
      throw new AcademicDataError(
        `Topic ${String(item.topic_id)} has an invalid subject`,
      );
    }
    if (!chapterIds.has(text(item.chapter_id, "topic.chapter_id"))) {
      throw new AcademicDataError(
        `Topic ${String(item.topic_id)} has an invalid chapter`,
      );
    }
  }
  for (const item of glossaryRecords) {
    if (!chapterIds.has(text(item.chapter_id, "glossary.chapter_id"))) {
      throw new AcademicDataError(
        `Glossary ${String(item.glossary_id)} has an invalid chapter`,
      );
    }
  }
  for (const item of questionRecords) {
    const questionId = text(item.question_id, "question.question_id");
    if (!subjectCodes.has(text(item.subject_code, "question.subject_code"))) {
      throw new AcademicDataError(`${questionId} has an invalid subject`);
    }
    if (!chapterIds.has(text(item.chapter_id, "question.chapter_id"))) {
      throw new AcademicDataError(`${questionId} has an invalid chapter`);
    }
    for (const topicId of list(item.topic_ids, "question.topic_ids")) {
      if (!topicIds.has(text(topicId, "question topic"))) {
        throw new AcademicDataError(`${questionId} has an invalid topic`);
      }
    }
    const choices = list(item.choices, "question.choices").map((choice, index) =>
      record(choice, `${questionId}.choices[${index}]`),
    );
    const choiceIds = uniqueIds(choices, "choice_id", `${questionId} choices`);
    text(item.original_question_en, `${questionId}.original_question_en`);
    text(item.question_th, `${questionId}.question_th`);
    for (const choice of choices) {
      text(choice.original_text_en, `${questionId} choice original`);
      text(choice.text_th, `${questionId} choice Thai`);
      if (choice.visual_assets !== undefined) {
        validateVisualAssets(
          choice.visual_assets,
          `${questionId}.${String(choice.choice_id)}`,
        );
      }
    }
    const hasVisual = item.has_visual_content;
    if (typeof hasVisual !== "boolean") {
      throw new AcademicDataError(
        `${questionId}.has_visual_content must be a boolean`,
      );
    }
    const visualStatus = text(
      item.visual_integrity_status,
      `${questionId}.visual_integrity_status`,
    );
    if (
      !new Set([
        "complete",
        "repaired",
        "missing_visual",
        "partially_readable",
        "requires_human_review",
      ]).has(visualStatus)
    ) {
      throw new AcademicDataError(
        `${questionId} has an invalid visual-integrity status`,
      );
    }
    const visualAssets = validateVisualAssets(item.visual_assets, questionId);
    if (
      hasVisual &&
      (visualStatus === "complete" || visualStatus === "repaired") &&
      !visualAssets.some((asset) => asset.is_essential === true)
    ) {
      throw new AcademicDataError(
        `${questionId} is visually complete without an essential asset`,
      );
    }
    if (
      typeof item.visual_scoring_eligible !== "boolean" ||
      item.visual_scoring_eligible !==
        (visualStatus === "complete" || visualStatus === "repaired")
    ) {
      throw new AcademicDataError(
        `${questionId} has inconsistent visual scoring eligibility`,
      );
    }
    text(
      item.original_layout_notes,
      `${questionId}.original_layout_notes`,
    );
    text(
      item.visual_extraction_method,
      `${questionId}.visual_extraction_method`,
    );
    const dimensions = record(
      item.source_page_dimensions,
      `${questionId}.source_page_dimensions`,
    );
    finiteNumber(dimensions.width, `${questionId} source page width`);
    finiteNumber(dimensions.height, `${questionId} source page height`);
    text(
      item.visual_audit_completed_at,
      `${questionId}.visual_audit_completed_at`,
    );
    const correctAnswer = item.correct_answer;
    if (typeof correctAnswer === "string" && !choiceIds.has(correctAnswer)) {
      throw new AcademicDataError(`${questionId} has an invalid answer choice`);
    }
    if (
      Array.isArray(correctAnswer) &&
      correctAnswer.some(
        (choiceId) =>
          typeof choiceId !== "string" || !choiceIds.has(choiceId),
      )
    ) {
      throw new AcademicDataError(`${questionId} has invalid answer choices`);
    }
    const answerStatus = text(item.answer_status, `${questionId}.answer_status`);
    const allowedAnswerStatuses = new Set([
      "verified_from_course_material",
      "verified_from_external_source",
      "strongly_supported_by_external_source",
      "probabilistic_recommendation",
      "unresolvable_question",
    ]);
    if (!allowedAnswerStatuses.has(answerStatus)) {
      throw new AcademicDataError(
        `${questionId} has an invalid final answer status`,
      );
    }
    if (
      answerStatus === "unresolvable_question" &&
      (correctAnswer !== null ||
        choices.some((choice) => choice.is_correct === true))
    ) {
      throw new AcademicDataError(
        `${questionId} exposes an answer while unresolved`,
      );
    }
    if (
      answerStatus === "verified_from_course_material" &&
      list(item.source_references, `${questionId}.source_references`).length ===
        0
    ) {
      throw new AcademicDataError(`${questionId} verified without evidence`);
    }
    if (
      (answerStatus === "verified_from_external_source" ||
        answerStatus === "strongly_supported_by_external_source") &&
      list(
        item.external_source_ids,
        `${questionId}.external_source_ids`,
      ).length === 0
    ) {
      throw new AcademicDataError(
        `${questionId} externally supported without evidence`,
      );
    }
    if (answerStatus === "probabilistic_recommendation") {
      const probabilityTotal = list(
        item.probability_distribution,
        `${questionId}.probability_distribution`,
      ).reduce<number>((total, row, index) => {
        const probability = record(
          row,
          `${questionId}.probability_distribution[${index}]`,
        ).probability_percentage;
        if (typeof probability !== "number") {
          throw new AcademicDataError(
            `${questionId} has an invalid probability`,
          );
        }
        return total + probability;
      }, 0);
      if (probabilityTotal !== 100) {
        throw new AcademicDataError(
          `${questionId} probabilities must total 100`,
        );
      }
      text(
        item.probability_warning_en,
        `${questionId}.probability_warning_en`,
      );
      text(
        item.probability_warning_th,
        `${questionId}.probability_warning_th`,
      );
    }
  }

  const subjects = subjectRecords as unknown as Subject[];
  const chapters = chapterRecords as unknown as Chapter[];
  const topics = topicRecords as unknown as Topic[];
  const glossary = glossaryRecords as unknown as GlossaryEntry[];
  const sourceReferences =
    referenceRecords as unknown as SourceReference[];
  const questions = questionRecords as unknown as Question[];
  return {
    subjects,
    chapters,
    topics,
    glossary,
    sourceReferences,
    questions,
    subjectByCode: new Map(subjects.map((item) => [item.course_code, item])),
    chapterById: new Map(chapters.map((item) => [item.chapter_id, item])),
    topicById: new Map(topics.map((item) => [item.topic_id, item])),
    referenceById: new Map(
      sourceReferences.map((item) => [item.source_reference_id, item]),
    ),
  };
}

export const academicData = validateAcademicData({
  subjects: subjectsJson,
  chapters: chaptersJson,
  topics: topicsJson,
  glossary: glossaryJson,
  sourceReferences: referencesJson,
  questions: questionsJson,
});
