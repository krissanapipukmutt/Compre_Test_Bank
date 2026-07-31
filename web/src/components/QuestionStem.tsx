import type { PresentedQuestion } from "../domain";

function EmbeddedOptionLines({
  question,
  language,
}: {
  question: PresentedQuestion;
  language: "en" | "th";
}) {
  if (!question.embedded_options.length) return null;
  return (
    <ol
      aria-label={
        language === "en"
          ? "Statements referenced by the answer choices"
          : "ข้อความที่ตัวเลือกคำตอบอ้างถึง"
      }
      className="embedded-option-list"
      data-language={language}
      lang={language === "th" ? "th" : undefined}
    >
      {question.embedded_options.map((option) => (
        <li key={option.embedded_option_id}>
          <span aria-hidden="true" className="embedded-option-list__marker">
            {option.marker})
          </span>
          <span>
            {language === "en" ? option.original_text_en : option.text_th}
          </span>
        </li>
      ))}
    </ol>
  );
}

export function FormattedQuestionBlock({
  question,
}: {
  question: PresentedQuestion;
}) {
  return (
    <div className="question-copy">
      <span className="eyebrow" data-language="en">
        Original English <span lang="th">· ต้นฉบับภาษาอังกฤษ</span>
      </span>
      <h2 data-testid="question-stem-en">
        {question.normalized_question_en}
      </h2>
      <EmbeddedOptionLines language="en" question={question} />
      <div className="translation-block" data-language="th" lang="th">
        <span>คำแปลภาษาไทย</span>
        <p data-testid="question-stem-th">
          {question.normalized_question_th}
        </p>
        <EmbeddedOptionLines language="th" question={question} />
      </div>
      {question.normalization_requires_human_review ? (
        <p className="question-format-warning" role="status">
          Question formatting requires human review{" "}
          <span lang="th">· รูปแบบคำถามต้องได้รับการตรวจทาน</span>
        </p>
      ) : null}
    </div>
  );
}
