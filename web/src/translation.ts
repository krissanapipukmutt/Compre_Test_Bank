import type { Choice, Question } from "./domain";

export const MISSING_TRANSLATION_WARNING =
  "Thai translation is missing or invalid. คำแปลภาษาไทยขาดหายหรือไม่สมบูรณ์ จึงปิดการตอบข้อนี้ไว้";

export const TRANSLATION_REVIEW_WARNING =
  "Translation is complete but remains flagged for source-language review. คำแปลครบถ้วนแล้ว แต่ต้นฉบับยังต้องได้รับการทบทวน";

const placeholders = [
  "คำศัพท์/ข้อความภาษาอังกฤษตามต้นฉบับ",
  "translation pending",
  "untranslated",
  "todo",
  "n/a",
];

function isReviewedLiteral(choice: Choice): boolean {
  const note = choice.translation_review_note ?? "";
  return (
    note.includes("คง") &&
    (note.includes("โค้ด") ||
      note.includes("ชื่อเฉพาะ") ||
      note.includes("ตัวระบุ") ||
      note.includes("ตัวเลข"))
  );
}

export function isValidTranslationText(
  english: string,
  thai: string,
  reviewedLiteral = false,
): boolean {
  const source = english.trim();
  const translation = thai.trim();
  if (!source || !translation) return false;
  const lowered = translation.toLocaleLowerCase();
  if (placeholders.some((placeholder) => lowered.includes(placeholder))) {
    return false;
  }
  if (source === translation && !reviewedLiteral) return false;
  if (
    source.length >= 24 &&
    !/[\u0E00-\u0E7F]/u.test(translation) &&
    !reviewedLiteral
  ) {
    return false;
  }
  return true;
}

export function hasCompleteBilingualContent(question: Question): boolean {
  if (
    !isValidTranslationText(
      question.original_question_en,
      question.question_th,
    )
  ) {
    return false;
  }
  if (
    !isValidTranslationText(
      question.explanation_en,
      question.explanation_th,
    )
  ) {
    return false;
  }
  return question.choices.every(
    (choice) =>
      isValidTranslationText(
        choice.original_text_en,
        choice.text_th,
        isReviewedLiteral(choice),
      ) &&
      isValidTranslationText(
        choice.explanation_en,
        choice.explanation_th,
      ),
  );
}

export function isTranslationReady(question: Question): boolean {
  return (
    hasCompleteBilingualContent(question) &&
    (question.translation_status === "verified" ||
      question.translation_status === "repaired")
  );
}
