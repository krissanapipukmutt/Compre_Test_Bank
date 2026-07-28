import { useMemo, useState } from "react";
import type {
  AcademicData,
  Chapter,
  LessonSection,
  SourceLabelled,
  Subject,
  Topic,
} from "../domain";
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

function SourceCategoryLabel({ item }: { item: SourceLabelled }) {
  return (
    <span
      className={`content-source-label content-source-label--${item.source_category}`}
    >
      <strong>{item.source_label_en}</strong>
      <span lang="th">{item.source_label_th}</span>
    </span>
  );
}

function LessonSectionCard({ section }: { section: LessonSection }) {
  const listContent =
    section.content_format === "bullet_list" ||
    section.content_format === "numbered_steps";
  const ListTag = section.content_format === "numbered_steps" ? "ol" : "ul";
  return (
    <section className="lesson-section" id={section.section_id}>
      <SourceCategoryLabel item={section} />
      <h2>{section.heading_en}</h2>
      <p className="lesson-section__thai-heading" lang="th">
        {section.heading_th}
      </p>
      {listContent ? (
        <ListTag className="bilingual-lesson-list">
          {section.content_en.map((content, index) => (
            <li key={`${section.section_id}-${index}`}>
              <span>{content}</span>
              <small lang="th">{section.content_th[index]}</small>
            </li>
          ))}
        </ListTag>
      ) : (
        <div className="lesson-paragraphs">
          {section.content_en.map((content, index) => (
            <div key={`${section.section_id}-${index}`}>
              <p>{content}</p>
              {section.content_th[index] ? (
                <p lang="th">{section.content_th[index]}</p>
              ) : null}
            </div>
          ))}
        </div>
      )}
    </section>
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
        route: routeHref({ name: "topic", topicId: topic.topic_id }),
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
          <hr />
          <h3>How the chapters connect</h3>
          <p>{subject.topic_relationships_en}</p>
          <p lang="th">{subject.topic_relationships_th}</p>
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
          <section className="learning-objectives" id="chapter-objectives">
            <span className="eyebrow">Learning objectives · วัตถุประสงค์การเรียนรู้</span>
            <h2>After this chapter</h2>
            <ul className="check-list">
              {chapter.learning_objectives_en.map((objective, index) => (
                <li key={objective}>
                  <Icon name="check" size={18} />
                  <span>
                    {objective}
                    <small lang="th">
                      {chapter.learning_objectives_th[index]}
                    </small>
                  </span>
                </li>
              ))}
            </ul>
          </section>

          {chapter.lesson_sections.map((section) => (
            <LessonSectionCard key={section.section_id} section={section} />
          ))}

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
                <a
                  href={routeHref({ name: "topic", topicId: topic!.topic_id })}
                  key={topic!.topic_id}
                >
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <div>
                    <h3>{topic!.title_en}</h3>
                    <strong lang="th">{topic!.title_th}</strong>
                    <p>{topic!.summary_en}</p>
                    <p lang="th">{topic!.summary_th}</p>
                    <strong className="topic-stack__open">
                      Open full lesson <Icon name="arrow" size={16} />
                    </strong>
                  </div>
                </a>
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

function TopicTableOfContents({ topic }: { topic: Topic }) {
  const links = [
    ["topic-objectives", "Learning objectives", "วัตถุประสงค์"],
    ["topic-overview", "Overview", "ภาพรวม"],
    ...topic.lesson_sections.map((section) => [
      section.section_id,
      section.heading_en,
      section.heading_th,
    ]),
    ["topic-terms", "Key terminology", "คำศัพท์สำคัญ"],
    ["topic-comparisons", "Concept comparison", "การเปรียบเทียบ"],
    ["topic-process", "Workflow", "ขั้นตอน"],
    ...(topic.formulas.length
      ? [["topic-formulas", "Formulas", "สูตร"]]
      : []),
    ["topic-examples", "Practical example", "ตัวอย่าง"],
    ["topic-misunderstandings", "Common misunderstandings", "ความเข้าใจผิด"],
    ["topic-exam-focus", "Examination focus", "จุดเน้นข้อสอบ"],
    [
      "topic-related-exam",
      "Related examination topics",
      "หัวข้อที่เกี่ยวข้องกับแนวข้อสอบ",
    ],
    ["topic-quick-review", "Quick review", "ทบทวนด่วน"],
    ["topic-sources", "Source references", "แหล่งอ้างอิง"],
  ];
  return (
    <details className="topic-toc">
      <summary>On this page · เนื้อหาในหน้านี้</summary>
      <nav aria-label="Topic table of contents">
        {links.map(([id, english, thai]) => (
          <a href={`#${id}`} key={id}>
            <span>{english}</span>
            <small lang="th">{thai}</small>
          </a>
        ))}
      </nav>
    </details>
  );
}

export function TopicPage({
  data,
  topicId,
  bookmarked,
  onBookmark,
}: {
  data: AcademicData;
  topicId: string;
  bookmarked: boolean;
  onBookmark: () => void;
}) {
  const topic = data.topicById.get(topicId);
  if (!topic) {
    return (
      <EmptyState title="Topic not found">
        <a className="button button--primary" href={routeHref({ name: "library" })}>
          Back to library
        </a>
      </EmptyState>
    );
  }
  const chapter = data.chapterById.get(topic.chapter_id)!;
  const subject = data.subjects.find(
    (item) => item.subject_id === topic.subject_id,
  )!;
  const chapterTopics = chapter.topic_ids
    .map((id) => data.topicById.get(id))
    .filter((item): item is Topic => Boolean(item));
  const topicIndex = chapterTopics.findIndex((item) => item.topic_id === topicId);
  const previous = topicIndex > 0 ? chapterTopics[topicIndex - 1] : null;
  const next =
    topicIndex < chapterTopics.length - 1 ? chapterTopics[topicIndex + 1] : null;
  const sources = topic.source_reference_ids
    .map((id) => data.referenceById.get(id))
    .filter((item): item is NonNullable<typeof item> => Boolean(item));
  const examMap = data.questionMapByTopicId.get(topicId);

  return (
    <div className="page page--reader topic-page">
      <nav aria-label="Breadcrumb" className="breadcrumbs">
        <a href={routeHref({ name: "library" })}>Library</a>
        <Icon name="arrow" size={14} />
        <a href={routeHref({ name: "subject", code: subject.course_code })}>
          {subject.course_code}
        </a>
        <Icon name="arrow" size={14} />
        <a href={routeHref({ name: "chapter", chapterId: chapter.chapter_id })}>
          {chapter.title_en}
        </a>
        <Icon name="arrow" size={14} />
        <span>Topic</span>
      </nav>

      <header className="chapter-hero topic-hero">
        <div className="question-meta">
          <Badge tone="teal">{subject.course_code}</Badge>
          <ConfidenceBadge confidence={topic.confidence} />
          <Badge>{topic.evidence_type.replaceAll("_", " ")}</Badge>
        </div>
        <div className="chapter-hero__title">
          <div>
            <span className="eyebrow">
              Topic {topicIndex + 1} of {chapterTopics.length}
            </span>
            <h1>{topic.title_en}</h1>
            <p lang="th">{topic.title_th}</p>
          </div>
          <BookmarkButton
            active={bookmarked}
            label={bookmarked ? "Remove topic bookmark" : "Bookmark topic"}
            onClick={onBookmark}
          />
        </div>
        <p className="chapter-lead">{topic.overview_en}</p>
        <p className="chapter-lead chapter-lead--thai" lang="th">
          {topic.overview_th}
        </p>
      </header>

      <div className="topic-reader-layout">
        <aside className="topic-reader-nav">
          <TopicTableOfContents topic={topic} />
          <div className="chapter-topic-nav">
            <strong>{chapter.title_en}</strong>
            <small lang="th">{chapter.title_th}</small>
            {chapterTopics.map((item) => (
              <a
                aria-current={item.topic_id === topicId ? "page" : undefined}
                href={routeHref({ name: "topic", topicId: item.topic_id })}
                key={item.topic_id}
              >
                {item.title_en}
                <small lang="th">{item.title_th}</small>
              </a>
            ))}
          </div>
        </aside>

        <article className="reader-content topic-content">
          <section className="learning-objectives" id="topic-objectives">
            <span className="eyebrow">Learning objectives · วัตถุประสงค์การเรียนรู้</span>
            <h2>What you should understand</h2>
            <ul className="check-list">
              {topic.learning_objectives_en.map((objective, index) => (
                <li key={objective}>
                  <Icon name="check" size={18} />
                  <span>
                    {objective}
                    <small lang="th">{topic.learning_objectives_th[index]}</small>
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section className="topic-overview-card" id="topic-overview">
            <SourceCategoryLabel item={topic.key_terms[0]!} />
            <h2>Overview</h2>
            <p>{topic.overview_en}</p>
            <p lang="th">{topic.overview_th}</p>
          </section>

          {topic.lesson_sections.map((section) => (
            <LessonSectionCard key={section.section_id} section={section} />
          ))}

          <section id="topic-terms">
            <span className="eyebrow">Key terminology · คำศัพท์สำคัญ</span>
            <h2>Terms and definitions</h2>
            <div className="definition-grid">
              {topic.key_terms.map((term) => (
                <article id={term.glossary_id} key={term.glossary_id}>
                  <SourceCategoryLabel item={term} />
                  <h3>{term.term_en}</h3>
                  <strong lang="th">{term.term_th}</strong>
                  <p>{term.definition_en}</p>
                  <p lang="th">{term.explanation_th}</p>
                </article>
              ))}
            </div>
          </section>

          <section id="topic-comparisons">
            <span className="eyebrow">Concept comparison · เปรียบเทียบแนวคิด</span>
            <h2>{topic.comparisons[0]!.title_en}</h2>
            <p lang="th">{topic.comparisons[0]!.title_th}</p>
            {topic.comparisons.map((comparison) => (
              <div className="comparison-block" key={comparison.comparison_id}>
                <SourceCategoryLabel item={comparison} />
                <div className="comparison-scroll" role="region" tabIndex={0}>
                  <table>
                    <thead>
                      <tr>
                        <th>Aspect · ประเด็น</th>
                        <th>
                          {comparison.columns_en[0]}
                          <small lang="th">{comparison.columns_th[0]}</small>
                        </th>
                        <th>
                          {comparison.columns_en[1]}
                          <small lang="th">{comparison.columns_th[1]}</small>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {comparison.rows.map((row) => (
                        <tr key={row.aspect_en}>
                          <th>
                            {row.aspect_en}
                            <small lang="th">{row.aspect_th}</small>
                          </th>
                          <td>
                            {row.left_en}
                            <small lang="th">{row.left_th}</small>
                          </td>
                          <td>
                            {row.right_en}
                            <small lang="th">{row.right_th}</small>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </section>

          <section id="topic-process">
            <span className="eyebrow">Process or workflow · ขั้นตอน</span>
            <h2>Use the concept step by step</h2>
            <ol className="process-list">
              {topic.process_steps.map((step) => (
                <li key={step.step}>
                  <span>{step.step}</span>
                  <div>
                    <SourceCategoryLabel item={step} />
                    <h3>{step.title_en}</h3>
                    <strong lang="th">{step.title_th}</strong>
                    <p>{step.description_en}</p>
                    <p lang="th">{step.description_th}</p>
                  </div>
                </li>
              ))}
            </ol>
          </section>

          {topic.formulas.length ? (
            <section id="topic-formulas">
              <span className="eyebrow">Formula or rule · สูตรหรือกฎ</span>
              <h2>Formula guide</h2>
              <div className="formula-detail-list">
                {topic.formulas.map((formula) => (
                  <article key={formula.formula}>
                    <SourceCategoryLabel item={formula} />
                    <h3>{formula.title_en}</h3>
                    <strong lang="th">{formula.title_th}</strong>
                    <code>{formula.formula}</code>
                    <p>{formula.meaning_en}</p>
                    <p lang="th">{formula.meaning_th}</p>
                    <dl>
                      {formula.variables.map((variable) => (
                        <div key={variable.symbol}>
                          <dt>{variable.symbol}</dt>
                          <dd>
                            {variable.meaning_en}
                            <small lang="th">{variable.meaning_th}</small>
                          </dd>
                        </div>
                      ))}
                    </dl>
                    <h4>When to use · ใช้เมื่อใด</h4>
                    <p>{formula.when_en}</p>
                    <p lang="th">{formula.when_th}</p>
                    <h4>Worked example · ตัวอย่างคำนวณ</h4>
                    <p>{formula.example_en}</p>
                    <p lang="th">{formula.example_th}</p>
                    <h4>Common mistake · ข้อผิดพลาดที่พบบ่อย</h4>
                    <p>{formula.mistake_en}</p>
                    <p lang="th">{formula.mistake_th}</p>
                  </article>
                ))}
              </div>
            </section>
          ) : null}

          <section id="topic-examples">
            <span className="eyebrow">Practical example · ตัวอย่างการประยุกต์</span>
            <h2>Guided application</h2>
            {topic.examples.map((example) => (
              <article className="example-card" key={example.example_id}>
                <SourceCategoryLabel item={example} />
                <h3>{example.title_en}</h3>
                <strong lang="th">{example.title_th}</strong>
                <p>{example.scenario_en}</p>
                <p lang="th">{example.scenario_th}</p>
                <ol className="bilingual-lesson-list">
                  {example.walkthrough_en.map((step, index) => (
                    <li key={step}>
                      <span>{step}</span>
                      <small lang="th">{example.walkthrough_th[index]}</small>
                    </li>
                  ))}
                </ol>
              </article>
            ))}
          </section>

          <section id="topic-misunderstandings">
            <span className="eyebrow">Common misunderstandings · ความเข้าใจผิด</span>
            <h2>Watch for these traps</h2>
            <div className="misunderstanding-list">
              {topic.common_misunderstandings.map((item) => (
                <article key={item.misunderstanding_en}>
                  <SourceCategoryLabel item={item} />
                  <h3>{item.misunderstanding_en}</h3>
                  <p lang="th">{item.misunderstanding_th}</p>
                  <strong>Correction · แนวทางที่ถูก</strong>
                  <p>{item.correction_en}</p>
                  <p lang="th">{item.correction_th}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="study-aids" id="topic-exam-focus">
            <div>
              <SourceCategoryLabel item={topic.exam_focus} />
              <span className="eyebrow">Examination focus · จุดเน้นข้อสอบ</span>
              <h2>Read the wording carefully</h2>
              <ul>
                {topic.exam_focus.points_en?.map((point, index) => (
                  <li key={point}>
                    {point}
                    <small lang="th">{topic.exam_focus.points_th?.[index]}</small>
                  </li>
                ))}
              </ul>
              {topic.exam_focus.wording_signals.length ? (
                <p>
                  <strong>Observed wording:</strong>{" "}
                  {topic.exam_focus.wording_signals.join(", ")}
                </p>
              ) : null}
            </div>
          </section>

          <section className="topic-exam-links" id="topic-related-exam">
            <div className="section-heading section-heading--compact">
              <div>
                <span className="eyebrow">
                  Supplied-exam traceability · การสืบย้อนข้อสอบที่ได้รับ
                </span>
                <h2>
                  Related examination topics
                  <small lang="th">หัวข้อที่เกี่ยวข้องกับแนวข้อสอบ</small>
                </h2>
              </div>
              <Badge tone={examMap?.question_count ? "teal" : "warning"}>
                {examMap?.question_count ?? 0} questions
              </Badge>
            </div>
            {examMap?.question_count ? (
              <>
                <div className="topic-exam-links__summary">
                  <div>
                    <strong>Difficulty · ระดับความยาก</strong>
                    <span>
                      Easy {examMap.difficulty_counts.easy} · Medium{" "}
                      {examMap.difficulty_counts.medium} · Hard{" "}
                      {examMap.difficulty_counts.hard}
                    </span>
                  </div>
                  <div>
                    <strong>Observed frequency · ความถี่ที่พบ</strong>
                    <span>
                      {examMap.exam_frequency_signal ===
                      "appears_multiple_times_in_supplied_exam_examples"
                        ? "Appears multiple times in the supplied exam examples"
                        : "Appears once in the supplied exam examples"}
                    </span>
                  </div>
                </div>
                <h3>Tested concepts · แนวคิดที่ทดสอบ</h3>
                <ul className="bilingual-lesson-list">
                  {examMap.tested_concepts.map((concept) => (
                    <li key={concept.question_id}>
                      <span>{concept.concept_en}</span>
                      <small lang="th">{concept.concept_th}</small>
                    </li>
                  ))}
                </ul>
                {examMap.answer_status_warning_count ? (
                  <AcademicNotice
                    severity="warning"
                    title="Answer-status warning · คำเตือนสถานะคำตอบ"
                  >
                    <p>
                      {examMap.answer_status_warning_count} related{" "}
                      {examMap.answer_status_warning_count === 1
                        ? "question retains"
                        : "questions retain"}{" "}
                      an academic-review or scoring warning. The concept lesson
                      does not resolve or reveal those answers.
                    </p>
                    <p lang="th">
                      ข้อสอบที่เกี่ยวข้องจำนวน{" "}
                      {examMap.answer_status_warning_count} ข้อยังคงมีคำเตือนด้าน
                      การตรวจทานทางวิชาการหรือการให้คะแนน บทเรียนแนวคิดนี้ไม่ตัดสิน
                      หรือเปิดเผยคำตอบ
                    </p>
                  </AcademicNotice>
                ) : null}
                <a
                  className="button button--primary"
                  href={`${routeHref({ name: "practice" })}?topic=${encodeURIComponent(topicId)}`}
                >
                  Practice this topic · ฝึกหัวข้อนี้
                </a>
              </>
            ) : (
              <AcademicNotice title="No supplied exam example found · ไม่พบตัวอย่างในข้อสอบที่ได้รับ">
                <p>
                  This does not mean the topic is unimportant. It only records
                  that no question in the supplied examination set maps directly
                  to this topic.
                </p>
                <p lang="th">
                  ข้อมูลนี้ไม่ได้หมายความว่าหัวข้อไม่สำคัญ แต่หมายถึงยังไม่มีข้อใน
                  ชุดข้อสอบที่ได้รับซึ่งเชื่อมตรงกับหัวข้อนี้
                </p>
              </AcademicNotice>
            )}
          </section>

          <section className="review-card" id="topic-quick-review">
            <span className="eyebrow">Quick review · ทบทวนด่วน</span>
            <blockquote>{topic.quick_review.memory_aid_en}</blockquote>
            <p lang="th">{topic.quick_review.memory_aid_th}</p>
            <ul className="bilingual-lesson-list">
              {topic.quick_review.key_points_en.map((point, index) => (
                <li key={`${point}-${index}`}>
                  <span>{point}</span>
                  <small lang="th">
                    {topic.quick_review.key_points_th[index]}
                  </small>
                </li>
              ))}
            </ul>
            <p className="glossary-links">
              <strong>Related glossary terms:</strong>{" "}
              {topic.quick_review.related_glossary_ids?.map((id) => (
                <a href={`#${id}`} key={id}>
                  {data.glossary.find((entry) => entry.glossary_id === id)
                    ?.term_en ?? id}
                </a>
              ))}
            </p>
          </section>

          <section id="topic-sources">
            <SourceList sources={sources} />
          </section>

          <nav aria-label="Previous and next topic" className="topic-pagination">
            {previous ? (
              <a href={routeHref({ name: "topic", topicId: previous.topic_id })}>
                <span>Previous topic</span>
                <strong>{previous.title_en}</strong>
                <small lang="th">{previous.title_th}</small>
              </a>
            ) : (
              <span />
            )}
            {next ? (
              <a href={routeHref({ name: "topic", topicId: next.topic_id })}>
                <span>Next topic</span>
                <strong>{next.title_en}</strong>
                <small lang="th">{next.title_th}</small>
              </a>
            ) : null}
          </nav>
        </article>
      </div>
    </div>
  );
}
