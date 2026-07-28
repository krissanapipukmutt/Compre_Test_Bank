import externalSourcesJson from "../data/external-sources.json";
import { useState } from "react";
import type { ExternalSource, PresentedQuestion } from "../domain";
import { scoreQuestion } from "../engine";
import {
  AcademicNotice,
  Badge,
  BookmarkButton,
  ConfidenceBadge,
  SourceList,
  StatusBadge,
} from "./Common";
import { MISSING_VISUAL_WARNING } from "../visual";
import { QuestionVisuals } from "./QuestionVisuals";
import {
  hasCompleteBilingualContent,
  MISSING_TRANSLATION_WARNING,
  TRANSLATION_REVIEW_WARNING,
} from "../translation";
import { FormattedQuestionBlock } from "./QuestionStem";
import { routeHref } from "../router";

const externalSourceById = new Map(
  (externalSourcesJson.external_sources as ExternalSource[]).map((source) => [
    source.source_id,
    source,
  ]),
);

function EvidenceDetails({ question }: { question: PresentedQuestion }) {
  const sources = question.external_source_ids
    .map((sourceId) => externalSourceById.get(sourceId))
    .filter((source): source is ExternalSource => source !== undefined);
  const choiceText = (choiceId: string) =>
    question.choices.find((choice) => choice.choice_id === choiceId)
      ?.original_text_en ?? choiceId;
  const choiceTextTh = (choiceId: string) =>
    question.choices.find((choice) => choice.choice_id === choiceId)?.text_th ??
    choiceId;

  return (
    <section className="evidence-details">
      <div className="question-meta">
        <StatusBadge status={question.answer_status} />
        <ConfidenceBadge confidence={question.confidence} />
        <Badge>{question.confidence_percentage}% evidence confidence</Badge>
      </div>

      {question.answer_status === "probabilistic_recommendation" ? (
        <AcademicNotice
          title="Probability-based recommendation · คำตอบจากการวิเคราะห์ความน่าจะเป็น"
          severity="danger"
        >
          <p>{question.probability_warning_en}</p>
          <p lang="th">{question.probability_warning_th}</p>
          <p>
            <strong>Recommended answer:</strong>{" "}
            {typeof question.final_answer === "string"
              ? choiceText(question.final_answer)
              : "No recommendation"}
            {typeof question.final_answer === "string" ? (
              <small className="bilingual-secondary" lang="th">
                <strong>คำตอบที่แนะนำ:</strong>{" "}
                {choiceTextTh(question.final_answer)}
              </small>
            ) : null}
          </p>
          <strong>Comparative probability by choice</strong>
          <ul>
            {question.probability_distribution.map((item) => (
              <li key={item.choice_id}>
                <span>
                  {choiceText(item.choice_id)} — {item.probability_percentage}%
                </span>
                <small className="bilingual-secondary" lang="th">
                  {choiceTextTh(item.choice_id)} —{" "}
                  {item.probability_percentage}%
                </small>
              </li>
            ))}
          </ul>
          <strong>Elimination reasoning</strong>
          <ul>
            {question.elimination_reasoning_en.map((item) => {
              const thaiReason = question.elimination_reasoning_th.find(
                (entry) => entry.choice_id === item.choice_id,
              );
              return (
                <li key={item.choice_id}>
                  <span>{item.reason}</span>
                  {thaiReason ? (
                    <small className="bilingual-secondary" lang="th">
                      {thaiReason.reason}
                    </small>
                  ) : null}
                </li>
              );
            })}
          </ul>
          <p>
            <strong>Remaining uncertainty:</strong>{" "}
            {question.remaining_uncertainty}
            <small className="bilingual-secondary" lang="th">
              <strong>ความไม่แน่นอนที่ยังเหลืออยู่:</strong>{" "}
              {question.remaining_uncertainty_th}
            </small>
          </p>
          <p>
            <strong>Human review required.</strong>
          </p>
        </AcademicNotice>
      ) : null}

      {question.answer_status === "unresolvable_question" ? (
        <AcademicNotice
          title="Answer remains unresolved · ยังไม่สามารถยืนยันคำตอบได้"
          severity="danger"
        >
          <p>{question.unresolved_reason}</p>
          <p lang="th">{question.unresolved_reason_th}</p>
          <p>This item is excluded from scoring and requires human review.</p>
          <p lang="th">ข้อนี้ไม่รวมในการให้คะแนนและต้องได้รับการตรวจทานโดยผู้เชี่ยวชาญ</p>
        </AcademicNotice>
      ) : null}

      {question.requires_human_review &&
      question.answer_status !== "probabilistic_recommendation" &&
      question.answer_status !== "unresolvable_question" ? (
        <AcademicNotice
          title="Human review remains required · ยังต้องตรวจสอบโดยผู้เชี่ยวชาญ"
          severity="warning"
        >
          <p>{question.unresolved_reason}</p>
          {question.unresolved_reason_th ? (
            <p lang="th">{question.unresolved_reason_th}</p>
          ) : null}
        </AcademicNotice>
      ) : null}

      {sources.length > 0 ? (
        <div className="external-evidence">
          <h4>External evidence · หลักฐานภายนอก</h4>
          <p>{question.external_evidence_summary_en}</p>
          <p lang="th">{question.external_evidence_summary_th}</p>
          {sources.map((source) => (
            <article className="external-source" key={source.source_id}>
              <h5>
                <a href={source.url} rel="noreferrer" target="_blank">
                  {source.title}
                </a>
              </h5>
              <dl>
                <div>
                  <dt>Organization / author</dt>
                  <dd>{source.organization_or_author}</dd>
                </div>
                <div>
                  <dt>Published / updated</dt>
                  <dd>
                    {source.last_updated_date ??
                      source.publication_date ??
                      "Date not stated"}
                  </dd>
                </div>
                <div>
                  <dt>Accessed</dt>
                  <dd>{source.accessed_date}</dd>
                </div>
                <div>
                  <dt>Relevant section</dt>
                  <dd>{source.relevant_section}</dd>
                </div>
              </dl>
              <p>{source.paraphrased_support}</p>
              {source.limitations ? (
                <p>
                  <strong>Limitations:</strong> {source.limitations}
                </p>
              ) : null}
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}

export function QuestionCard({
  question,
  selectedChoiceIds,
  reveal,
  bookmarked,
  onBookmark,
  onChange,
}: {
  question: PresentedQuestion;
  selectedChoiceIds: string[];
  reveal: boolean;
  bookmarked: boolean;
  onBookmark: () => void;
  onChange: (choiceIds: string[]) => void;
}) {
  const multiple = question.question_type === "multiple_select";
  const score = reveal ? scoreQuestion(question, selectedChoiceIds) : null;
  const [failedVisualQuestionId, setFailedVisualQuestionId] = useState<
    string | null
  >(null);
  const visualLoadFailed =
    failedVisualQuestionId === question.question_id;
  const translationInvalid = !hasCompleteBilingualContent(question);
  const translationNeedsReview =
    !translationInvalid &&
    question.translation_status !== "verified" &&
    question.translation_status !== "repaired";

  const update = (choiceId: string, checked: boolean) => {
    if (reveal) return;
    if (multiple) {
      onChange(
        checked
          ? [...selectedChoiceIds, choiceId]
          : selectedChoiceIds.filter((item) => item !== choiceId),
      );
    } else {
      onChange([choiceId]);
    }
  };

  return (
    <article className="question-card">
      <header className="question-card__header">
        <div className="question-meta">
          <Badge tone="teal">{question.subject_code}</Badge>
          <Badge>{question.difficulty}</Badge>
        </div>
        <BookmarkButton
          active={bookmarked}
          label={bookmarked ? "Remove question bookmark" : "Bookmark question"}
          onClick={onBookmark}
        />
      </header>

      <FormattedQuestionBlock question={question} />

      {translationInvalid ? (
        <p className="translation-warning" role="alert">
          {MISSING_TRANSLATION_WARNING}
        </p>
      ) : null}

      {translationNeedsReview ? (
        <p className="translation-review-warning">
          {TRANSLATION_REVIEW_WARNING}
        </p>
      ) : null}

      <QuestionVisuals
        assets={question.visual_assets}
        includeReference
        onEssentialError={() =>
          setFailedVisualQuestionId(question.question_id)
        }
      />

      {visualLoadFailed ? (
        <p className="missing-visual-warning" role="alert">
          {MISSING_VISUAL_WARNING}
        </p>
      ) : null}

      <fieldset className="choice-list">
        <legend>
          {multiple ? "Select all that apply" : "Choose one answer"} ·{" "}
          {multiple ? "เลือกทุกข้อที่ถูก" : "เลือกหนึ่งคำตอบ"}
        </legend>
        {question.choices.map((choice, index) => {
          const selected = selectedChoiceIds.includes(choice.choice_id);
          const revealClass = reveal
            ? choice.is_correct
              ? "is-correct"
              : selected
                ? "is-incorrect"
                : ""
            : "";
          return (
            <label
              className={`choice ${selected ? "is-selected" : ""} ${revealClass}`}
              key={choice.choice_id}
            >
              <input
                checked={selected}
                disabled={reveal || visualLoadFailed || translationInvalid}
                name={question.question_id}
                onChange={(event) =>
                  update(choice.choice_id, event.currentTarget.checked)
                }
                type={multiple ? "checkbox" : "radio"}
                value={choice.choice_id}
              />
              <span className="choice__marker" aria-hidden="true">
                {String.fromCharCode(65 + index)}
              </span>
              <span className="choice__copy">
                <span>{choice.original_text_en}</span>
                <small lang="th">{choice.text_th}</small>
                {choice.visual_assets?.length ? (
                  <QuestionVisuals
                    assets={choice.visual_assets}
                    onEssentialError={() =>
                      setFailedVisualQuestionId(question.question_id)
                    }
                  />
                ) : null}
                {reveal ? (
                  <span className="choice__explanation">
                    {choice.explanation_en}
                    <em lang="th">{choice.explanation_th}</em>
                  </span>
                ) : null}
              </span>
            </label>
          );
        })}
      </fieldset>

      {reveal ? (
        <section
          aria-live="polite"
          className={`answer-panel ${
            score?.correct ? "answer-panel--correct" : "answer-panel--review"
          }`}
        >
          <span className="eyebrow">
            {score?.scoreable
              ? score.correct
                ? "Correct · ถูกต้อง"
                : "Review · ทบทวน"
              : "Unscored reflection · ไม่ให้คะแนน"}
          </span>
          <h3>Explanation · คำอธิบาย</h3>
          <p>{question.explanation_en}</p>
          <p lang="th">{question.explanation_th}</p>
          <EvidenceDetails question={question} />
          <SourceList compact sources={question.source_references} />
          {question.study_topic_ids[0] ? (
            <a
              className="answer-panel__study-link button button--secondary"
              href={routeHref({
                name: "topic",
                topicId: question.study_topic_ids[0],
              })}
            >
              Review the most relevant Study Library topic ·
              ทบทวนหัวข้อที่เกี่ยวข้องที่สุด
            </a>
          ) : null}
        </section>
      ) : null}

      <footer className="question-card__footer">
        <span className="source-note">
          <span>
            Source question: {question.source_exam_relative_path}, page{" "}
            {question.source_page_or_slide}
          </span>
          <small lang="th">
            ที่มาของข้อสอบ: {question.source_exam_relative_path}, หน้า{" "}
            {question.source_page_or_slide}
          </small>
        </span>
        <span className="source-note">
          <span>{question.translation_note}</span>
          <small lang="th">{question.translation_note_th}</small>
        </span>
      </footer>
    </article>
  );
}
