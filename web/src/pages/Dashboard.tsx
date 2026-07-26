import type { AcademicData } from "../domain";
import type { LocalState } from "../storage";
import { routeHref } from "../router";
import { AcademicNotice, Badge, Icon } from "../components/Common";

export function Dashboard({
  data,
  localState,
}: {
  data: AcademicData;
  localState: LocalState;
}) {
  const reviewCount = data.questions.filter(
    (question) => question.requires_human_review,
  ).length;
  const latest = localState.attempts[0];
  const completedQuestions = new Set(
    localState.attempts.flatMap((attempt) => Object.keys(attempt.answers)),
  ).size;
  const questionProgress = Math.round(
    (completedQuestions / data.questions.length) * 100,
  );

  return (
    <div className="page page--dashboard">
      <section className="hero">
        <div className="hero__copy">
          <span className="eyebrow">Bilingual comprehensive examination</span>
          <h1>
            Study the evidence.
            <span lang="th">เข้าใจเหตุผล ไม่ใช่แค่จำคำตอบ</span>
          </h1>
          <p>
            A private fieldbook for six DBIS subjects—structured from your
            supplied lectures, exercises, and examination material.
          </p>
          <div className="hero__actions">
            <a className="button button--primary" href={routeHref({ name: "library" })}>
              Open study library <Icon name="arrow" />
            </a>
            <a className="button button--secondary" href={routeHref({ name: "practice" })}>
              Start practice
            </a>
          </div>
        </div>
        <div aria-label={`${questionProgress}% question coverage`} className="hero-meter">
          <div className="hero-meter__dial" style={{ "--progress": `${questionProgress * 3.6}deg` } as React.CSSProperties}>
            <span>{questionProgress}%</span>
          </div>
          <div>
            <strong>{completedQuestions}</strong>
            <span>of {data.questions.length} questions attempted</span>
          </div>
        </div>
      </section>

      <section aria-labelledby="overview-title">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Your field notes</span>
            <h2 id="overview-title">At a glance</h2>
          </div>
          <span className="section-heading__thai" lang="th">
            ภาพรวมการเรียน
          </span>
        </div>
        <div className="metric-grid">
          <article className="metric-card">
            <span>Subjects</span>
            <strong>{data.subjects.length}</strong>
            <small>3 in each term</small>
          </article>
          <article className="metric-card metric-card--teal">
            <span>Study chapters</span>
            <strong>{data.chapters.length}</strong>
            <small>{data.topics.length} structured topics</small>
          </article>
          <article className="metric-card metric-card--gold">
            <span>Question bank</span>
            <strong>{data.questions.length}</strong>
            <small>{reviewCount} clearly marked review items</small>
          </article>
          <article className="metric-card metric-card--ink">
            <span>Attempts</span>
            <strong>{localState.attempts.length}</strong>
            <small>
              {latest?.score.percent != null
                ? `Latest score ${latest.score.percent}%`
                : "Your history stays on this device"}
            </small>
          </article>
        </div>
      </section>

      <section className="dashboard-grid">
        <div>
          <div className="section-heading section-heading--compact">
            <div>
              <span className="eyebrow">Browse by term</span>
              <h2>Study library</h2>
            </div>
          </div>
          <div className="term-panels">
            {(["term-1", "term-2"] as const).map((term, termIndex) => (
              <article className="term-panel" key={term}>
                <div className="term-panel__number">0{termIndex + 1}</div>
                <div>
                  <span>Term {termIndex + 1}</span>
                  <h3>{termIndex === 0 ? "Analytics & Technology" : "Systems & Strategy"}</h3>
                  <div className="term-panel__subjects">
                    {data.subjects
                      .filter((subject) => subject.term === term)
                      .map((subject) => (
                        <a
                          href={routeHref({ name: "subject", code: subject.course_code })}
                          key={subject.subject_id}
                        >
                          <Badge tone="teal">{subject.course_code}</Badge>
                          <span>{subject.course_title_en}</span>
                          <Icon name="arrow" size={16} />
                        </a>
                      ))}
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>

        <aside className="dashboard-side">
          <div className="section-heading section-heading--compact">
            <div>
              <span className="eyebrow">Academic integrity</span>
              <h2>Know the evidence</h2>
            </div>
          </div>
          <AcademicNotice title="Statuses matter">
            <p>
              Verified, strongly inferred, and human-review answers are visibly
              different. Review-required questions are never scored.
            </p>
          </AcademicNotice>
          <div className="status-key">
            <div>
              <span className="status-dot status-dot--verified" />
              <span>
                <strong>16 source verified</strong>
                <small>Direct evidence in supplied material</small>
              </span>
            </div>
            <div>
              <span className="status-dot status-dot--inferred" />
              <span>
                <strong>71 strongly inferred</strong>
                <small>Supported, but not labelled verified</small>
              </span>
            </div>
            <div>
              <span className="status-dot status-dot--review" />
              <span>
                <strong>18 need review</strong>
                <small>Missing visual or flawed item</small>
              </span>
            </div>
          </div>
          <a className="text-link" href={routeHref({ name: "about" })}>
            How the data was prepared <Icon name="arrow" size={16} />
          </a>
        </aside>
      </section>
    </div>
  );
}
