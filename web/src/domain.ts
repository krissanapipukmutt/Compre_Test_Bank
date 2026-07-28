export type Term = "term-1" | "term-2";
export type Confidence = "high" | "medium" | "low";
export type AnswerStatus =
  | "verified_from_course_material"
  | "verified_from_external_source"
  | "strongly_supported_by_external_source"
  | "probabilistic_recommendation"
  | "unresolvable_question";
export type Difficulty = "easy" | "medium" | "hard";
export type CognitiveLevel =
  | "remember"
  | "understand"
  | "apply"
  | "analyze"
  | "evaluate"
  | "create";

export interface SourceReference {
  source_reference_id: string;
  file_id: string;
  relative_path: string;
  locator_type: string;
  locator_start: number;
  locator_end: number | null;
  locator_note: string;
  evidence_type: string;
}

export type SourceCategory =
  | "course_material"
  | "supplementary_explanation"
  | "external_authoritative_source";

export interface SourceLabelled {
  source_category: SourceCategory;
  source_label_en: string;
  source_label_th: string;
}

export type LessonContentFormat =
  | "paragraph"
  | "bullet_list"
  | "numbered_steps"
  | "comparison_table"
  | "formula"
  | "code"
  | "example"
  | "warning"
  | "callout";

export interface LessonSection extends SourceLabelled {
  section_id: string;
  heading_en: string;
  heading_th: string;
  content_en: string[];
  content_th: string[];
  content_format: LessonContentFormat;
  evidence_type: string;
  source_reference_ids: string[];
}

export interface QuickReview {
  key_points_en: string[];
  key_points_th: string[];
  memory_aid_en: string;
  memory_aid_th: string;
  related_glossary_ids?: string[];
}

export interface Subject {
  subject_id: string;
  course_code: string;
  course_title_en: string;
  course_title_th: string;
  term: Term;
  source_file_ids: string[];
  learning_objectives_en: string[];
  learning_objectives_th: string[];
  overview_en: string;
  overview_th: string;
  major_themes: string[];
  topic_relationships_en: string;
  topic_relationships_th: string;
  examination_focus: string[];
  chapter_ids: string[];
  mapping_confidence: Confidence;
  mapping_note: string;
  source_reference_ids: string[];
  lesson_sections: LessonSection[];
  quick_review: QuickReview;
  content_status: "enriched";
  content_updated_at: string;
}

export interface ChapterDefinition {
  term_en: string;
  term_th: string;
  definition_en: string;
  definition_th: string;
}

export interface Chapter {
  chapter_id: string;
  subject_id: string;
  course_code: string;
  title_en: string;
  title_th: string;
  concise_summary_en: string;
  concise_summary_th: string;
  detailed_explanation_th: string;
  topic_ids: string[];
  technical_terms: string[];
  definitions: ChapterDefinition[];
  concepts: string[];
  processes_and_frameworks: string[];
  formulas: string[];
  examples: string[];
  comparison_summaries: string[];
  common_misunderstandings: string[];
  likely_examination_points: string[];
  review_points: string[];
  memory_aid: string;
  short_review_questions: string[];
  source_reference_ids: string[];
  confidence: Confidence;
  evidence_type: string;
  order: number;
  learning_objectives_en: string[];
  learning_objectives_th: string[];
  overview_en: string;
  overview_th: string;
  lesson_sections: LessonSection[];
  formula_details: FormulaDetail[];
  exam_focus: ExamFocus;
  quick_review: QuickReview;
  content_status: "enriched";
  content_updated_at: string;
}

export interface KeyTerm extends SourceLabelled {
  glossary_id: string;
  term_en: string;
  term_th: string;
  definition_en: string;
  explanation_th: string;
  evidence_type: string;
  confidence: Confidence;
  source_reference_ids: string[];
}

export interface ComparisonRow {
  aspect_en: string;
  aspect_th: string;
  left_en: string;
  left_th: string;
  right_en: string;
  right_th: string;
}

export interface ConceptComparison extends SourceLabelled {
  comparison_id: string;
  title_en: string;
  title_th: string;
  columns_en: string[];
  columns_th: string[];
  rows: ComparisonRow[];
  evidence_type: string;
  source_reference_ids: string[];
  source_question_ids: string[];
}

export interface ProcessStep extends SourceLabelled {
  step: number;
  title_en: string;
  title_th: string;
  description_en: string;
  description_th: string;
}

export interface FormulaVariable {
  symbol: string;
  meaning_en: string;
  meaning_th: string;
}

export interface FormulaDetail extends SourceLabelled {
  formula: string;
  title_en: string;
  title_th: string;
  meaning_en: string;
  meaning_th: string;
  variables: FormulaVariable[];
  when_en: string;
  when_th: string;
  example_en: string;
  example_th: string;
  mistake_en: string;
  mistake_th: string;
  source_reference_ids: string[];
  evidence_type: string;
  worked_example_category: "supplementary_explanation";
}

export interface PracticalExample extends SourceLabelled {
  example_id: string;
  title_en: string;
  title_th: string;
  scenario_en: string;
  scenario_th: string;
  walkthrough_en: string[];
  walkthrough_th: string[];
}

export interface CommonMisunderstanding extends SourceLabelled {
  misunderstanding_en: string;
  misunderstanding_th: string;
  correction_en: string;
  correction_th: string;
}

export interface ExamFocus extends SourceLabelled {
  supported_question_ids: string[];
  wording_signals: string[];
  points_en?: string[];
  points_th?: string[];
  note_en?: string;
  note_th?: string;
}

export interface Topic {
  topic_id: string;
  subject_id: string;
  chapter_id: string;
  title_en: string;
  title_th: string;
  summary_en: string;
  summary_th: string;
  source_reference_ids: string[];
  confidence: Confidence;
  evidence_type: string;
  order: number;
  learning_objectives_en: string[];
  learning_objectives_th: string[];
  overview_en: string;
  overview_th: string;
  lesson_sections: LessonSection[];
  key_terms: KeyTerm[];
  comparisons: ConceptComparison[];
  process_steps: ProcessStep[];
  formulas: FormulaDetail[];
  examples: PracticalExample[];
  common_misunderstandings: CommonMisunderstanding[];
  exam_focus: ExamFocus;
  quick_review: QuickReview;
  human_review_note: string | null;
  content_status: "enriched";
  content_updated_at: string;
}

export interface GlossaryEntry {
  glossary_id: string;
  term_en: string;
  term_th: string;
  definition_en: string;
  explanation_th: string;
  subject_id: string;
  chapter_id: string;
  source_reference_ids: string[];
  confidence: Confidence;
  evidence_type: string;
}

export interface Choice {
  choice_id: string;
  original_text_en: string;
  text_th: string;
  is_correct: boolean;
  explanation_en: string;
  explanation_th: string;
  translation_status: "verified" | "repaired";
  translation_review_note: string;
  visual_assets?: VisualAsset[];
}

export type TranslationStatus =
  | "verified"
  | "repaired"
  | "incomplete"
  | "ambiguous"
  | "requires_human_review";

export interface TranslationAuditEntry {
  completed_at: string;
  action: string;
  result: TranslationStatus;
  fields_changed: string[];
  answer_key_changed: boolean;
  human_review_required: boolean;
  review_note: string;
}

export type VisualIntegrityStatus =
  | "complete"
  | "repaired"
  | "missing_visual"
  | "partially_readable"
  | "requires_human_review";

export type VisualContentPosition =
  | "after_translation_before_choices"
  | "within_choice"
  | "full_question_reference";

export interface CropCoordinates {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface VisualAsset {
  asset_id: string;
  asset_type: string;
  path: string;
  public_path: string;
  mime_type: "image/jpeg" | "image/png" | "image/webp" | "image/svg+xml";
  width: number;
  height: number;
  source_page: number;
  source_file_id: string;
  source_page_or_slide: number;
  source_bbox: CropCoordinates;
  crop_coordinates: CropCoordinates;
  placement: VisualContentPosition;
  is_essential: boolean;
  alt_en: string;
  alt_th: string;
  caption_en: string;
  caption_th: string;
  extraction_method: string;
  source_object_xref: number | null;
  sha256: string;
}

export interface ProbabilityDistribution {
  choice_id: string;
  probability_percentage: number;
}

export interface EliminationReason {
  choice_id: string;
  reason: string;
}

export interface ResearchAuditEntry {
  timestamp: string;
  action: string;
  result: string;
  source_ids: string[];
}

export interface EmbeddedOption {
  embedded_option_id: string;
  marker: string;
  original_text_en: string;
  text_th: string;
  source_page_or_slide: number;
}

export type NormalizationStatus =
  | "not_required"
  | "normalized"
  | "display_formatted_only"
  | "ambiguous"
  | "requires_human_review";

export interface NormalizationAuditEntry {
  completed_at: string;
  action: string;
  source_file_id: string;
  source_relative_path: string;
  source_page_or_slide: number;
  raw_question_sha256: string;
  detected_pattern: string;
  result: string;
  answer_key_before: string | string[] | null;
  answer_key_after: string | string[] | null;
  choice_ids_preserved: boolean;
  human_review_required: boolean;
}

export interface ExternalSource {
  source_id: string;
  source_type: string;
  organization_or_author: string;
  organization: string;
  title: string;
  publication_name: string | null;
  publication_date: string | null;
  last_updated_date: string | null;
  url: string;
  accessed_date: string;
  language: string;
  relevant_section: string;
  short_supporting_quote: string;
  paraphrased_support: string;
  credibility_reason: string;
  limitations: string;
  applicable_question_ids: string[];
}

export interface Question {
  question_id: string;
  source_exam_file_id: string;
  source_exam_relative_path: string;
  source_page_or_slide: number;
  term: Term;
  subject_code: string;
  subject_name: string;
  chapter_id: string;
  topic_ids: string[];
  question_type:
    | "single_choice"
    | "multiple_select"
    | "true_false"
    | "matching"
    | "short_answer"
    | "essay"
    | "calculation"
    | "case_analysis";
  original_question_en: string;
  question_th: string;
  choices: Choice[];
  correct_answer: string | string[] | null;
  acceptable_answers: string[];
  answer_status: AnswerStatus;
  confidence: Confidence;
  explanation_en: string;
  explanation_th: string;
  source_references: SourceReference[];
  evidence_summary: string;
  difficulty: Difficulty;
  cognitive_level: CognitiveLevel;
  tags: string[];
  detected_ambiguity: boolean;
  human_review_note: string | null;
  original_text_correction_log: string[];
  translation_note: string;
  translation_note_th: string;
  translation_status: TranslationStatus;
  translation_quality: Confidence;
  translation_review_note: string;
  translation_completed_at: string;
  translation_audit_log: TranslationAuditEntry[];
  original_answer: string | string[] | null;
  original_explanation_en: string;
  original_explanation_th: string;
  original_answer_status:
    | "verified_from_source"
    | "strongly_inferred"
    | "ambiguous"
    | "requires_human_review";
  final_answer_status: AnswerStatus;
  evidence_origin:
    | "COURSE_MATERIAL"
    | "EXTERNAL_AUTHORITATIVE"
    | "PROBABILISTIC_REASONING_ONLY";
  answer_source_type:
    | "supplied_course_material"
    | "external_authoritative_source"
    | "probabilistic_reasoning_only";
  external_source_ids: string[];
  external_evidence_summary_en: string;
  external_evidence_summary_th: string;
  course_evidence_locations: string[];
  final_answer: string | string[] | null;
  final_explanation_en: string;
  final_explanation_th: string;
  confidence_percentage: number;
  confidence_rationale_en: string;
  confidence_rationale_th: string;
  probability_distribution: ProbabilityDistribution[];
  elimination_reasoning_en: EliminationReason[];
  elimination_reasoning_th: EliminationReason[];
  probability_warning_en: string | null;
  probability_warning_th: string | null;
  remaining_uncertainty: string | null;
  remaining_uncertainty_th: string | null;
  unresolved_reason: string | null;
  unresolved_reason_th: string | null;
  requires_human_review: boolean;
  research_completed_at: string | null;
  research_audit_log: ResearchAuditEntry[];
  has_visual_content: boolean;
  visual_integrity_status: VisualIntegrityStatus;
  visual_content_position: VisualContentPosition | null;
  visual_assets: VisualAsset[];
  original_layout_notes: string;
  visual_extraction_method: string;
  visual_review_note: string | null;
  full_question_reference_asset: string | null;
  source_page_dimensions: {
    width: number;
    height: number;
    unit: "points";
  };
  visual_audit_completed_at: string;
  visual_scoring_eligible: boolean;
  raw_original_question_en: string;
  raw_original_question_th: string;
  normalized_question_en: string;
  normalized_question_th: string;
  embedded_choices_detected: boolean;
  embedded_choice_pattern: string | null;
  embedded_options: EmbeddedOption[];
  normalization_status: NormalizationStatus;
  normalization_confidence: Confidence;
  normalization_audit_log: NormalizationAuditEntry[];
  normalization_requires_human_review: boolean;
  normalization_human_review_note: string | null;
}

export interface AcademicData {
  subjects: Subject[];
  chapters: Chapter[];
  topics: Topic[];
  glossary: GlossaryEntry[];
  sourceReferences: SourceReference[];
  questions: Question[];
  subjectByCode: Map<string, Subject>;
  chapterById: Map<string, Chapter>;
  topicById: Map<string, Topic>;
  referenceById: Map<string, SourceReference>;
}

export interface QuestionFilters {
  term?: Term | "all";
  subjectCode?: string;
  chapterId?: string;
  topicId?: string;
  difficulty?: Difficulty | "all";
  answerStatus?: AnswerStatus | "all";
}

export interface PresentedQuestion extends Question {
  choices: Choice[];
}
