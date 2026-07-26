import type {
  AnswerStatus,
  PresentedQuestion,
  Question,
  QuestionFilters,
} from "./domain";
import { isTranslationReady } from "./translation";

function hashSeed(seed: string): number {
  let value = 2166136261;
  for (const character of seed) {
    value ^= character.charCodeAt(0);
    value = Math.imul(value, 16777619);
  }
  return value >>> 0;
}

function randomFactory(seed: string): () => number {
  let value = hashSeed(seed);
  return () => {
    value += 0x6d2b79f5;
    let result = value;
    result = Math.imul(result ^ (result >>> 15), result | 1);
    result ^= result + Math.imul(result ^ (result >>> 7), result | 61);
    return ((result ^ (result >>> 14)) >>> 0) / 4294967296;
  };
}

export function shuffleWithSeed<T>(values: readonly T[], seed: string): T[] {
  const random = randomFactory(seed);
  const shuffled = [...values];
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const next = Math.floor(random() * (index + 1));
    const currentValue = shuffled[index];
    const nextValue = shuffled[next];
    if (currentValue !== undefined && nextValue !== undefined) {
      shuffled[index] = nextValue;
      shuffled[next] = currentValue;
    }
  }
  return shuffled;
}

export function presentQuestion(
  question: Question,
  seed: string,
  randomizeChoices: boolean,
): PresentedQuestion {
  return {
    ...question,
    choices: randomizeChoices
      ? shuffleWithSeed(question.choices, `${seed}:${question.question_id}`)
      : [...question.choices],
  };
}

export function filterQuestions(
  questions: readonly Question[],
  filters: QuestionFilters,
): Question[] {
  return questions.filter((question) => {
    if (filters.term && filters.term !== "all" && question.term !== filters.term) {
      return false;
    }
    if (
      filters.subjectCode &&
      question.subject_code !== filters.subjectCode
    ) {
      return false;
    }
    if (filters.chapterId && question.chapter_id !== filters.chapterId) {
      return false;
    }
    if (filters.topicId && !question.topic_ids.includes(filters.topicId)) {
      return false;
    }
    if (
      filters.difficulty &&
      filters.difficulty !== "all" &&
      question.difficulty !== filters.difficulty
    ) {
      return false;
    }
    if (
      filters.answerStatus &&
      filters.answerStatus !== "all" &&
      question.answer_status !== filters.answerStatus
    ) {
      return false;
    }
    return true;
  });
}

export interface QuestionScore {
  scoreable: boolean;
  correct: boolean | null;
  earned: number;
  possible: number;
}

export function isVisualReady(question: Question): boolean {
  if (
    !question.visual_scoring_eligible ||
    (question.visual_integrity_status !== "complete" &&
      question.visual_integrity_status !== "repaired")
  ) {
    return false;
  }
  return (
    !question.has_visual_content ||
    question.visual_assets.some((asset) => asset.is_essential)
  );
}

export function scoreQuestion(
  question: Question,
  selectedChoiceIds: readonly string[],
): QuestionScore {
  if (
    question.correct_answer === null ||
    question.answer_status === "probabilistic_recommendation" ||
    question.answer_status === "unresolvable_question" ||
    !isVisualReady(question) ||
    !isTranslationReady(question) ||
    (question.requires_human_review &&
      question.answer_status !== "strongly_supported_by_external_source")
  ) {
    return { scoreable: false, correct: null, earned: 0, possible: 0 };
  }
  const expected = Array.isArray(question.correct_answer)
    ? [...question.correct_answer].sort()
    : [question.correct_answer];
  const selected = [...selectedChoiceIds].sort();
  const correct =
    expected.length === selected.length &&
    expected.every((value, index) => value === selected[index]);
  return {
    scoreable: true,
    correct,
    earned: correct ? 1 : 0,
    possible: 1,
  };
}

export interface AnswerRecord {
  questionId: string;
  selectedChoiceIds: string[];
  score: QuestionScore;
}

export interface ScoreSummary {
  earned: number;
  possible: number;
  percent: number | null;
  correct: number;
  incorrect: number;
  unanswered: number;
  unscored: number;
}

export function scoreAttempt(
  questions: readonly Question[],
  answers: Readonly<Record<string, string[]>>,
): ScoreSummary {
  let earned = 0;
  let possible = 0;
  let correct = 0;
  let incorrect = 0;
  let unanswered = 0;
  let unscored = 0;
  for (const question of questions) {
    const selected = answers[question.question_id] ?? [];
    if (selected.length === 0) {
      unanswered += 1;
    }
    const score = scoreQuestion(question, selected);
    earned += score.earned;
    possible += score.possible;
    if (!score.scoreable) {
      unscored += 1;
    } else if (score.correct) {
      correct += 1;
    } else if (selected.length > 0) {
      incorrect += 1;
    }
  }
  return {
    earned,
    possible,
    percent: possible ? Math.round((earned / possible) * 100) : null,
    correct,
    incorrect,
    unanswered,
    unscored,
  };
}

export function answerStatusLabel(status: AnswerStatus): string {
  const labels: Record<AnswerStatus, string> = {
    verified_from_course_material: "Verified from course materials · ยืนยันจากเอกสารการเรียน",
    verified_from_external_source: "Verified from external sources · ยืนยันจากแหล่งข้อมูลภายนอก",
    strongly_supported_by_external_source:
      "Strongly supported by external sources · มีหลักฐานภายนอกสนับสนุน แต่ยังไม่ชัดเจนทั้งหมด",
    probabilistic_recommendation:
      "Probability-based recommendation · คำตอบจากการวิเคราะห์ความน่าจะเป็น",
    unresolvable_question:
      "Answer remains unresolved · ยังไม่สามารถยืนยันคำตอบได้",
  };
  return labels[status];
}
