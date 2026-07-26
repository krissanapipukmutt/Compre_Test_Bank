import { useMemo, useState } from "react";
import type { AcademicData, Chapter, Subject } from "../domain";
import { routeHref } from "../router";
import {
  AcademicNotice,
  Badge,
  BookmarkButton,
  ConfidenceBadge,
  EmptyState,
  Icon,
  SourceList,
} from "../components/Common";

function SubjectCard({
  subject,
  chapterCount,
  questionCount,
}: {
  subject: Subject;
  chapterCount: number;
  questionCount: number;
}) {
  return (
    <a
      className="subject-card"
      href={routeHref({ name: "subject", code: subject.course_code })}
    >
      <div className="subject-card__top">
        <Badge tone={subject.term === "term-1" ? "teal" : "warning"}>
          {subject.term === "term-1" ? "TERM 1" : "TERM 2"}
        </Badge>
        <span>{subject.course_code}</span>
      </div>
      <h3>{subject.course_title_en}</h3>
      <p lang="th">{subject.course_title_th}</p>
      <div className="subject-card__stats">
        <span>{chapterCount} chapters</span>
        <span>{questionCount} questions</span>
      </div>
      <span className="subject-card__open">
        Open subject <Icon name="arrow" size={17} />
      </span>
    </a>
  );
}

export function LibraryPage({ data }: { data: AcademicData }) {
  const [term, setTerm] = useState<"all" | "term-1" | "term-2">("all");
  const [query, setQuery] = useState("");
  const normalized = query.trim().toLocaleLowerCase();
  const subjects = data.subjects.filter(
    (subject) => term === "all" || subject.term === term,
  );
  const results = useMemo(() => {
    if (normalized.length < 2) return [];
    const chapterResults = data.chapters
      .filter((chapter) =>
        [
          chapter.title_en,
          chapter.title_th,
          chapter.concise_summary_en,
          chapter.concise_summary_th,
        ]
          .join(" ")
          .toLocaleLowerCase()
          .includes(normalized),
      )
      .slice(0, 5)
      .map((chapter) => ({
        id: chapter.chapter_id,
        label: chapter.title_en,
        sublabel: chapter.title_th,
        route: routeHref({ name: "chapter", chapterId: chapter.chapter_id }),
        kind: "Chapter",
      }));
    const topicResults = data.topics
      .filter((topic) =>
        [topic.title_en, topic.title_th, topic.summary_en, topic.summary_th]
          .join(" ")
          .toLocaleLowerCase()
          .includes(normalized),
      )
      .slice(0, 5)
      .map((topic) => ({
        id: topic.topic_id,
        label: topic.title_en,
        sublabel: topic.title_th,
        route: routeHref({ name: "chapter", chapterId: topic.chapter_id }),
        kind: "Topic",
      }));
    const questionResults = data.questions
      .filter((question) =>
        [question.original_question_en, question.question_th]
          .join(" ")
          .toLocaleLowerCase()
          .includes(normalized),
      )
      .slice(0, 5)
      .map((question) => ({
        id: question.question_id,
        label: question.original_question_en,
        sublabel: question.question_th,
        route: `${routeHref({ name: "practice" })}?question=${question.question_id}`,
        kind: "Question",
      }));
    return [...chapterResults, ...topicResults, ...questionResults].slice(0, 12);
  }, [data, normalized]);

  return (
    <div className="page">
      <header className="page-header page-header--split">
        <div>
          <span className="eyebrow">Term → subject → chapter → topic</span>
          <h1>Study library</h1>
          <p lang="th">คลังเนื้อหาแบบสองภาษา พร้อมคำศัพท์ จุดออกสอบ และแหล่งอ้างอิง</p>
        </div>
        <div className="library-count">
          <strong>{data.chapters.length}</strong>
          <span>evidence-linked chapters</span>
        </div>
      </header>

      <section className="library-toolbar" aria-label="Library controls">
        <label className="search-box">
          <Icon name="search" />
          <span className="sr-only">Search the library</span>
          <input
            onChange={(event) => setQuery(event.currentTarget.value)}
            placeholder="Search English or Thai…"
            type="search"
            value={query}
          />
        </label>
        <div className="segmented" role="group" aria-label="Filter by term">
          {(["all", "term-1", "term-2"] as const).map((value) => (
            <button
              aria-pressed={term === value}
              className={term === value ? "is-active" : ""}
              key={value}
              onClick={() => setTerm(value)}
              type="button"
            >
              {value === "all" ? "All" : value === "term-1" ? "Term 1" : "Term 2"}
            </button>
          ))}
        </div>
      </section>

      {normalized.length >= 2 ? (
        <section className="search-results" aria-live="polite">
          <div className="section-heading section-heading--compact">
            <div>
              <span className="eyebrow">Search results</span>
              <h2>{results.length} matches for “{query}”</h2>
            </div>
          </div>
          {results.length ? (
            <div className="result-list">
              {results.map((result) => (
                <a href={result.route} key={result.id}>
                  <Badge>{result.kind}</Badge>
                  <span>
                    <strong>{result.label}</strong>
                    <small lang="th">{result.sublabel}</small>
                  </span>
                  <Icon name="arrow" size={18} />
                </a>
              ))}
            </div>
          ) : (
            <EmptyState title="No matching study notes">
              <p>Try a broader English or Thai term.</p>
            </EmptyState>
          )}
        </section>
      ) : (
        <section>
          <div className="section-heading">
            <div>
              <span className="eyebrow">Six validated subject areas</span>
              <h2>Choose your subject</h2>
            </div>
          </div>
          <div className="subject-grid">
            {subjects.map((subject) => (
              <SubjectCard
                chapterCount={subject.chapter_ids.length}
                key={subject.subject_id}
                questionCount={
                  data.questions.filter(
                    (question) => question.subject_code === subject.course_code,
                  ).length
                }
                subject={subject}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export function SubjectPage({
  data,
  code,
}: {
  data: AcademicData;
  code: string;
}) {
  const subject = data.subjectByCode.get(code);
  if (!subject) {
    return (
      <EmptyState title="Subject not found">
        <a className="button button--primary" href={routeHref({ name: "library" })}>
          Back to library
        </a>
      </EmptyState>
    );
  }
  const chapters = subject.chapter_ids
    .map((id) => data.chapterById.get(id))
    .filter((item): item is Chapter => Boolean(item));
  const questions = data.questions.filter(
    (question) => question.subject_code === code,
  );

  return (
    <div className="page">
      <nav aria-label="Breadcrumb" className="breadcrumbs">
        <a href={routeHref({ name: "library" })}>Library</a>
        <Icon name="arrow" size={14} />
        <span>{subject.course_code}</span>
      </nav>
      <header className="subject-hero">
        <div>
          <div className="question-meta">
            <Badge tone={subject.term === "term-1" ? "teal" : "warning"}>
              {subject.term === "term-1" ? "TERM 1" : "TERM 2"}
            </Badge>
            <ConfidenceBadge confidence={subject.mapping_confidence} />
          </div>
          <span className="subject-hero__code">{subject.course_code}</span>
          <h1>{subject.course_title_en}</h1>
          <p lang="th">{subject.course_title_th}</p>
        </div>
        <div className="subject-hero__stats">
          <div>
            <strong>{chapters.length}</strong>
            <span>chapters</span>
          </div>
          <div>
            <strong>{questions.length}</strong>
            <span>questions</span>
          </div>
        </div>
      </header>

      {subject.mapping_confidence !== "high" ? (
        <AcademicNotice title="Course mapping needs human confirmation">
          <p>{subject.mapping_note}</p>
        </AcademicNotice>
      ) : null}

      <div className="subject-layout">
        <article className="reading-card">
          <span className="eyebrow">Subject overview</span>
          <h2>What this course connects</h2>
          <p>{subject.overview_en}</p>
          <p lang="th">{subject.overview_th}</p>
          <hr />
          <h3>Learning objectives</h3>
          <ul className="check-list">
            {subject.learning_objectives_en.map((objective, index) => (
              <li key={objective}>
                <Icon name="check" size={18} />
                <span>
                  {objective}
                  <small lang="th">{subject.learning_objectives_th[index]}</small>
                </span>
              </li>
            ))}
          </ul>
        </article>
        <aside className="study-callout">
          <span className="study-callout__number">{questions.length}</span>
          <h2>Practice this subject</h2>
          <p>Build a filtered session using only {subject.course_code} questions.</p>
          <a
            className="button button--primary"
            href={`${routeHref({ name: "practice" })}?subject=${subject.course_code}`}
          >
            Configure practice
          </a>
        </aside>
      </div>

      <section>
        <div className="section-heading">
          <div>
            <span className="eyebrow">Chapter sequence</span>
            <h2>{chapters.length} study chapters</h2>
          </div>
        </div>
        <ol className="chapter-list">
          {chapters.map((chapter, index) => (
            <li key={chapter.chapter_id}>
              <a
                className="chapter-row"
                href={routeHref({ name: "chapter", chapterId: chapter.chapter_id })}
              >
                <span className="chapter-row__index">{String(index + 1).padStart(2, "0")}</span>
                <span className="chapter-row__copy">
                  <strong>{chapter.title_en}</strong>
                  <small lang="th">{chapter.title_th}</small>
                  <span>{chapter.concise_summary_en}</span>
                </span>
                <span className="chapter-row__meta">
                  <Badge>{chapter.topic_ids.length} topics</Badge>
                  <Icon name="arrow" />
                </span>
              </a>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}

export function ChapterPage({
  data,
  chapterId,
  bookmarked,
  onBookmark,
}: {
  data: AcademicData;
  chapterId: string;
  bookmarked: boolean;
  onBookmark: () => void;
}) {
  const chapter = data.chapterById.get(chapterId);
  if (!chapter) {
    return (
      <EmptyState title="Chapter not found">
        <a className="button button--primary" href={routeHref({ name: "library" })}>
          Back to library
        </a>
      </EmptyState>
    );
  }
  const subject = data.subjects.find(
    (item) => item.subject_id === chapter.subject_id,
  )!;
  const topics = chapter.topic_ids
    .map((id) => data.topicById.get(id))
    .filter((item) => Boolean(item));
  const sources = chapter.source_reference_ids
    .map((id) => data.referenceById.get(id))
    .filter((item) => Boolean(item));

  return (
    <div className="page page--reader">
      <nav aria-label="Breadcrumb" className="breadcrumbs">
        <a href={routeHref({ name: "library" })}>Library</a>
        <Icon name="arrow" size={14} />
        <a href={routeHref({ name: "subject", code: subject.course_code })}>
          {subject.course_code}
        </a>
        <Icon name="arrow" size={14} />
        <span>Chapter</span>
      </nav>
      <header className="chapter-hero">
        <div className="question-meta">
          <Badge tone="teal">{chapter.course_code}</Badge>
          <ConfidenceBadge confidence={chapter.confidence} />
          <Badge>{chapter.evidence_type.replaceAll("_", " ")}</Badge>
        </div>
        <div className="chapter-hero__title">
          <div>
            <span className="eyebrow">Study chapter</span>
            <h1>{chapter.title_en}</h1>
            <p lang="th">{chapter.title_th}</p>
          </div>
          <BookmarkButton
            active={bookmarked}
            label={bookmarked ? "Remove chapter bookmark" : "Bookmark chapter"}
            onClick={onBookmark}
          />
        </div>
        <p className="chapter-lead">{chapter.concise_summary_en}</p>
        <p className="chapter-lead chapter-lead--thai" lang="th">
          {chapter.concise_summary_th}
        </p>
      </header>

      <div className="reader-layout">
        <article className="reader-content">
          <section>
            <span className="eyebrow">Detailed explanation · คำอธิบาย</span>
            <p className="thai-detail" lang="th">
              {chapter.detailed_explanation_th}
            </p>
          </section>

          <section>
            <div className="section-heading section-heading--compact">
              <div>
                <span className="eyebrow">Core vocabulary</span>
                <h2>Terms & definitions</h2>
              </div>
            </div>
            <div className="definition-grid">
              {chapter.definitions.map((definition) => (
                <article key={definition.term_en}>
                  <h3>{definition.term_en}</h3>
                  <span lang="th">{definition.term_th}</span>
                  <p>{definition.definition_en}</p>
                  <p lang="th">{definition.definition_th}</p>
                </article>
              ))}
            </div>
          </section>

          <section>
            <div className="section-heading section-heading--compact">
              <div>
                <span className="eyebrow">Concept map</span>
                <h2>Topics in this chapter</h2>
              </div>
            </div>
            <div className="topic-stack">
              {topics.map((topic, index) => (
                <article key={topic!.topic_id}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <div>
                    <h3>{topic!.title_en}</h3>
                    <strong lang="th">{topic!.title_th}</strong>
                    <p>{topic!.summary_en}</p>
                    <p lang="th">{topic!.summary_th}</p>
                  </div>
                </article>
              ))}
            </div>
          </section>

          {chapter.formulas.length ? (
            <section className="formula-card">
              <span className="eyebrow">Formula sheet</span>
              <h2>Remember the relationship</h2>
              {chapter.formulas.map((formula) => (
                <code key={formula}>{formula}</code>
              ))}
            </section>
          ) : null}

          <section className="study-aids">
            <div>
              <span className="eyebrow">Exam lens</span>
              <h2>Likely examination points</h2>
              <ul>
                {chapter.likely_examination_points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            </div>
            <div>
              <span className="eyebrow">Common traps</span>
              <h2>Watch for these</h2>
              <ul>
                {chapter.common_misunderstandings.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            </div>
          </section>

          <section className="review-card">
            <span className="eyebrow">Memory aid</span>
            <blockquote>{chapter.memory_aid}</blockquote>
            <h2>Quick self-check</h2>
            <ol>
              {chapter.short_review_questions.map((question) => (
                <li key={question}>{question}</li>
              ))}
            </ol>
          </section>

          <SourceList sources={sources.filter((item): item is NonNullable<typeof item> => Boolean(item))} />
        </article>
        <aside className="reader-aside">
          <div className="reader-aside__card">
            <span>Chapter map</span>
            <strong>{topics.length}</strong>
            <small>topics</small>
            <strong>{chapter.technical_terms.length}</strong>
            <small>technical terms</small>
          </div>
          <a
            className="button button--secondary"
            href={`${routeHref({ name: "practice" })}?chapter=${chapter.chapter_id}`}
          >
            Practice this chapter
          </a>
        </aside>
      </div>
    </div>
  );
}

