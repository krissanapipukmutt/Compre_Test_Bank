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

const translationPlaceholders = [
  "คำศัพท์/ข้อความภาษาอังกฤษตามต้นฉบับ",
  "translation pending",
  "untranslated",
  "todo",
  "n/a",
];

function translationPair(
  englishValue: unknown,
  thaiValue: unknown,
  label: string,
  reviewedLiteral = false,
): void {
  const english = text(englishValue, `${label} English`);
  const thai = text(thaiValue, `${label} Thai`);
  const lowered = thai.toLocaleLowerCase();
  if (
    translationPlaceholders.some((placeholder) =>
      lowered.includes(placeholder),
    )
  ) {
    throw new AcademicDataError(`${label} Thai contains placeholder text`);
  }
  if (english.trim() === thai.trim() && !reviewedLiteral) {
    throw new AcademicDataError(
      `${label} Thai repeats English without a reviewed literal exemption`,
    );
  }
  if (
    english.length >= 24 &&
    !/[\u0E00-\u0E7F]/u.test(thai) &&
    !reviewedLiteral
  ) {
    throw new AcademicDataError(`${label} Thai contains no meaningful Thai`);
  }
}

function finiteNumber(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new AcademicDataError(`${label} must be a finite number`);
  }
  return value;
}

function stringList(value: unknown, label: string): string[] {
  return list(value, label).map((item, index) =>
    text(item, `${label}[${index}]`),
  );
}

const sourceLabels = {
  course_material: ["From course materials", "จากเอกสารการเรียน"],
  supplementary_explanation: [
    "Supplementary explanation",
    "คำอธิบายเสริม",
  ],
  external_authoritative_source: [
    "Supplementary information from an authoritative external source",
    "ข้อมูลเสริมจากแหล่งภายนอกที่น่าเชื่อถือ",
  ],
} as const;

function validateSourceLabel(value: unknown, label: string): UnknownRecord {
  const item = record(value, label);
  const category = text(item.source_category, `${label}.source_category`);
  if (!(category in sourceLabels)) {
    throw new AcademicDataError(`${label} has an invalid source category`);
  }
  const [expectedEnglish, expectedThai] =
    sourceLabels[category as keyof typeof sourceLabels];
  if (
    item.source_label_en !== expectedEnglish ||
    item.source_label_th !== expectedThai
  ) {
    throw new AcademicDataError(`${label} has an invalid bilingual source label`);
  }
  return item;
}

function validateLessonSections(
  value: unknown,
  label: string,
  referenceIds: Set<string>,
  minimum: number,
): void {
  const sections = list(value, label).map((item, index) =>
    validateSourceLabel(item, `${label}[${index}]`),
  );
  if (sections.length < minimum) {
    throw new AcademicDataError(`${label} must contain at least ${minimum} sections`);
  }
  const allowedFormats = new Set([
    "paragraph",
    "bullet_list",
    "numbered_steps",
    "comparison_table",
    "formula",
    "code",
    "example",
    "warning",
    "callout",
  ]);
  for (const section of sections) {
    text(section.section_id, `${label}.section_id`);
    translationPair(
      section.heading_en,
      section.heading_th,
      `${label}.heading`,
    );
    const english = stringList(section.content_en, `${label}.content_en`);
    const thai = stringList(section.content_th, `${label}.content_th`);
    if (!english.length || !thai.length) {
      throw new AcademicDataError(`${label} content cannot be empty`);
    }
    if (
      !allowedFormats.has(text(section.content_format, `${label}.content_format`))
    ) {
      throw new AcademicDataError(`${label} has an invalid content format`);
    }
    for (const sourceId of stringList(
      section.source_reference_ids,
      `${label}.source_reference_ids`,
    )) {
      if (!referenceIds.has(sourceId)) {
        throw new AcademicDataError(`${label} has an invalid source reference`);
      }
    }
  }
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
    if (item.content_status !== "enriched") {
      throw new AcademicDataError("subject content must be enriched");
    }
    const objectivesEn = stringList(
      item.learning_objectives_en,
      "subject.learning_objectives_en",
    );
    const objectivesTh = stringList(
      item.learning_objectives_th,
      "subject.learning_objectives_th",
    );
    if (objectivesEn.length < 3 || objectivesEn.length !== objectivesTh.length) {
      throw new AcademicDataError("subject objectives must be complete and bilingual");
    }
    translationPair(item.overview_en, item.overview_th, "subject.overview");
    validateLessonSections(
      item.lesson_sections,
      `subject ${String(item.subject_id)} lesson_sections`,
      referenceIds,
      2,
    );
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
    if (item.content_status !== "enriched") {
      throw new AcademicDataError(
        `Chapter ${String(item.chapter_id)} is not enriched`,
      );
    }
    translationPair(item.overview_en, item.overview_th, "chapter.overview");
    validateLessonSections(
      item.lesson_sections,
      `chapter ${String(item.chapter_id)} lesson_sections`,
      referenceIds,
      2,
    );
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
    if (item.content_status !== "enriched") {
      throw new AcademicDataError(`Topic ${String(item.topic_id)} is not enriched`);
    }
    translationPair(item.overview_en, item.overview_th, "topic.overview");
    const objectivesEn = stringList(
      item.learning_objectives_en,
      "topic.learning_objectives_en",
    );
    const objectivesTh = stringList(
      item.learning_objectives_th,
      "topic.learning_objectives_th",
    );
    if (objectivesEn.length < 3 || objectivesEn.length !== objectivesTh.length) {
      throw new AcademicDataError("topic objectives must be complete and bilingual");
    }
    validateLessonSections(
      item.lesson_sections,
      `topic ${String(item.topic_id)} lesson_sections`,
      referenceIds,
      3,
    );
    for (const collection of [
      "key_terms",
      "comparisons",
      "process_steps",
      "examples",
      "common_misunderstandings",
    ] as const) {
      const values = list(item[collection], `topic.${collection}`);
      if (!values.length) {
        throw new AcademicDataError(`topic.${collection} cannot be empty`);
      }
      values.forEach((value, index) =>
        validateSourceLabel(value, `topic.${collection}[${index}]`),
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
    translationPair(
      item.original_question_en,
      item.question_th,
      `${questionId}.question`,
    );
    if (
      item.raw_original_question_en !== item.original_question_en ||
      item.raw_original_question_th !== item.question_th
    ) {
      throw new AcademicDataError(`${questionId} does not preserve raw text`);
    }
    translationPair(
      item.normalized_question_en,
      item.normalized_question_th,
      `${questionId}.normalized_question`,
    );
    const normalizationStatus = text(
      item.normalization_status,
      `${questionId}.normalization_status`,
    );
    if (
      !new Set([
        "not_required",
        "normalized",
        "display_formatted_only",
        "ambiguous",
        "requires_human_review",
      ]).has(normalizationStatus)
    ) {
      throw new AcademicDataError(
        `${questionId} has an invalid normalization status`,
      );
    }
    if (typeof item.embedded_choices_detected !== "boolean") {
      throw new AcademicDataError(
        `${questionId}.embedded_choices_detected must be boolean`,
      );
    }
    const embeddedOptions = list(
      item.embedded_options,
      `${questionId}.embedded_options`,
    ).map((option, index) =>
      record(option, `${questionId}.embedded_options[${index}]`),
    );
    if (item.embedded_choices_detected === true) {
      if (normalizationStatus !== "normalized" || embeddedOptions.length < 2) {
        throw new AcademicDataError(
          `${questionId} has incomplete embedded-option normalization`,
        );
      }
      for (const option of embeddedOptions) {
        text(option.marker, `${questionId} embedded marker`);
        translationPair(
          option.original_text_en,
          option.text_th,
          `${questionId} embedded option`,
        );
      }
    } else if (embeddedOptions.length || normalizationStatus !== "not_required") {
      throw new AcademicDataError(
        `${questionId} has inconsistent normalization metadata`,
      );
    }
    const translationStatus = text(
      item.translation_status,
      `${questionId}.translation_status`,
    );
    if (
      !new Set([
        "verified",
        "repaired",
        "incomplete",
        "ambiguous",
        "requires_human_review",
      ]).has(translationStatus)
    ) {
      throw new AcademicDataError(
        `${questionId} has an invalid translation status`,
      );
    }
    if (!new Set(["high", "medium", "low"]).has(
      text(item.translation_quality, `${questionId}.translation_quality`),
    )) {
      throw new AcademicDataError(
        `${questionId} has an invalid translation quality`,
      );
    }
    text(item.translation_review_note, `${questionId}.translation_review_note`);
    text(item.translation_completed_at, `${questionId}.translation_completed_at`);
    list(item.translation_audit_log, `${questionId}.translation_audit_log`);
    translationPair(
      item.translation_note,
      item.translation_note_th,
      `${questionId}.translation_note`,
    );
    translationPair(
      item.explanation_en,
      item.explanation_th,
      `${questionId}.explanation`,
    );
    translationPair(
      item.original_explanation_en,
      item.original_explanation_th,
      `${questionId}.original_explanation`,
    );
    translationPair(
      item.final_explanation_en,
      item.final_explanation_th,
      `${questionId}.final_explanation`,
    );
    if (
      typeof item.external_evidence_summary_en === "string" &&
      item.external_evidence_summary_en.trim()
    ) {
      translationPair(
        item.external_evidence_summary_en,
        item.external_evidence_summary_th,
        `${questionId}.external_evidence_summary`,
      );
    }
    if (
      typeof item.remaining_uncertainty === "string" &&
      item.remaining_uncertainty.trim()
    ) {
      translationPair(
        item.remaining_uncertainty,
        item.remaining_uncertainty_th,
        `${questionId}.remaining_uncertainty`,
      );
    }
    if (
      typeof item.unresolved_reason === "string" &&
      item.unresolved_reason.trim()
    ) {
      translationPair(
        item.unresolved_reason,
        item.unresolved_reason_th,
        `${questionId}.unresolved_reason`,
      );
    }
    for (const choice of choices) {
      const choiceId = text(choice.choice_id, `${questionId} choice ID`);
      const choiceTranslationStatus = text(
        choice.translation_status,
        `${choiceId}.translation_status`,
      );
      if (
        choiceTranslationStatus !== "verified" &&
        choiceTranslationStatus !== "repaired"
      ) {
        throw new AcademicDataError(
          `${choiceId} has a non-ready translation status`,
        );
      }
      const reviewNote = text(
        choice.translation_review_note,
        `${choiceId}.translation_review_note`,
      );
      const reviewedLiteral =
        reviewNote.includes("คง") &&
        (reviewNote.includes("โค้ด") ||
          reviewNote.includes("ชื่อเฉพาะ") ||
          reviewNote.includes("ตัวระบุ") ||
          reviewNote.includes("ตัวเลข"));
      translationPair(
        choice.original_text_en,
        choice.text_th,
        `${choiceId}.choice`,
        reviewedLiteral,
      );
      translationPair(
        choice.explanation_en,
        choice.explanation_th,
        `${choiceId}.explanation`,
      );
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
