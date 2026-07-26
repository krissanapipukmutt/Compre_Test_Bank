import { useMemo, useState } from "react";
import type { AcademicData } from "../domain";
import { scoreQuestion } from "../engine";
import type { LocalState } from "../storage";
import { routeHref } from "../router";
import {
  Badge,
  ConfirmDialog,
  EmptyState,
  Icon,
} from "../components/Common";

export function ProgressPage({
  data,
  localState,
  onReset,
}: {
  data: AcademicData;
  localState: LocalState;
  onReset: () => void;
}) {
  const [resetOpen, setResetOpen] = useState(false);
  const metrics = useMemo(() => {
    const bySubject = data.subjects.map((subject) => {
      let earned = 0;
      let possible = 0;
      for (const attempt of localState.attempts) {
        for (const questionId of attempt.questionIds) {
          const question = data.questions.find(
            (item) =>
              item.question_id === questionId &&
              item.subject_code === subject.course_code,
          );
          if (!question) continue;
          const score = scoreQuestion(
            question,
            attempt.answers[questionId] ?? [],
          );
          earned += score.earned;
          possible += score.possible;
        }
      }
      return {
        subject,
        earned,
        possible,
        percent: possible ? Math.round((earned / possible) * 100) : null,
      };
    });
    const topicMap = new Map<
      string,
      { topicId: string; earned: number; possible: number; attempts: number }
    >();
    for (const attempt of localState.attempts) {
      for (const questionId of attempt.questionIds) {
        const question = data.questions.find(
          (item) => item.question_id === questionId,
        );
        if (!question) continue;
        const score = scoreQuestion(
          question,
          attempt.answers[questionId] ?? [],
        );
        for (const topicId of question.topic_ids) {
          const current = topicMap.get(topicId) ?? {
            topicId,
            earned: 0,
            possible: 0,
            attempts: 0,
          };
          current.earned += score.earned;
          current.possible += score.possible;
          current.attempts += 1;
          topicMap.set(topicId, current);
        }
      }
    }
    const weakTopics = Array.from(topicMap.values())
      .filter((item) => item.possible > 0)
      .map((item) => ({
        ...item,
        percent: Math.round((item.earned / item.possible) * 100),
        topic: data.topicById.get(item.topicId),
      }))
      .filter((item) => item.topic)
      .sort((a, b) => a.percent - b.percent)
      .slice(0, 6);
    return { bySubject, weakTopics };
  }, [data, localState.attempts]);

  const latest = localState.attempts[0];
  const average = localState.attempts.length
    ? Math.round(
        localState.attempts.reduce(
          (sum, attempt) => sum + (attempt.score.percent ?? 0),
          0,
        ) / localState.attempts.length,
      )
    : null;

  return (
    <div className="page">
      <header className="page-header page-header--split">
        <div>
          <span className="eyebrow">Stored only in this browser</span>
          <h1>Progress & bookmarks</h1>
          <p lang="th">ประวัติ คะแนน หัวข้อที่ควรทบทวน และรายการที่บันทึกไว้</p>
        </div>
        <button
          className="button button--danger-ghost"
          onClick={() => setResetOpen(true)}
          type="button"
        >
          Reset progress
        </button>
      </header>

      <section className="metric-grid">
        <article className="metric-card metric-card--ink">
          <span>Attempts</span>
          <strong>{localState.attempts.length}</strong>
          <small>practice and mock sessions</small>
        </article>
        <article className="metric-card metric-card--teal">
          <span>Average</span>
          <strong>{average == null ? "—" : `${average}%`}</strong>
          <small>across scoreable questions</small>
        </article>
        <article className="metric-card metric-card--gold">
          <span>Latest</span>
          <strong>
            {latest?.score.percent == null ? "—" : `${latest.score.percent}%`}
          </strong>
          <small>{latest ? new Date(latest.createdAt).toLocaleDateString() : "No attempt yet"}</small>
        </article>
        <article className="metric-card">
          <span>Bookmarks</span>
          <strong>
            {localState.bookmarks.chapterIds.length +
              localState.bookmarks.questionIds.length}
          </strong>
          <small>chapters and questions</small>
        </article>
      </section>

      {localState.attempts.length === 0 ? (
        <EmptyState
          action={
            <a className="button button--primary" href={routeHref({ name: "practice" })}>
              Start your first practice
            </a>
          }
          title="Your notebook is ready"
        >
          <p>Complete a practice or mock session to see performance trends.</p>
        </EmptyState>
      ) : (
        <>
          <section className="progress-grid">
            <div>
              <div className="section-heading section-heading--compact">
                <div>
                  <span className="eyebrow">Subject performance</span>
                  <h2>Across all attempts</h2>
                </div>
              </div>
              <div className="performance-list">
                {metrics.bySubject.map(({ subject, percent, possible }) => (
                  <article key={subject.subject_id}>
                    <div>
                      <Badge tone="teal">{subject.course_code}</Badge>
                      <span>
                        <strong>{subject.course_title_en}</strong>
                        <small>{possible} scoreable responses</small>
                      </span>
                    </div>
                    <div className="performance-bar">
                      <span style={{ width: `${percent ?? 0}%` }} />
                    </div>
                    <strong>{percent == null ? "—" : `${percent}%`}</strong>
                  </article>
                ))}
              </div>
            </div>
            <aside>
              <div className="section-heading section-heading--compact">
                <div>
                  <span className="eyebrow">Weak topics</span>
                  <h2>Review next</h2>
                </div>
              </div>
              <div className="weak-topic-list">
                {metrics.weakTopics.map((item) => (
                  <a
                    href={routeHref({
                      name: "chapter",
                      chapterId: item.topic!.chapter_id,
                    })}
                    key={item.topicId}
                  >
                    <span>
                      <strong>{item.topic!.title_en}</strong>
                      <small lang="th">{item.topic!.title_th}</small>
                    </span>
                    <Badge tone={item.percent < 50 ? "danger" : "warning"}>
                      {item.percent}%
                    </Badge>
                  </a>
                ))}
              </div>
            </aside>
          </section>

          <section>
            <div className="section-heading">
              <div>
                <span className="eyebrow">Attempt history</span>
                <h2>Recent sessions</h2>
              </div>
            </div>
            <div className="table-scroll" role="region" aria-label="Attempt history" tabIndex={0}>
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Mode</th>
                    <th>Subjects</th>
                    <th>Questions</th>
                    <th>Score</th>
                  </tr>
                </thead>
                <tbody>
                  {localState.attempts.slice(0, 20).map((attempt) => (
                    <tr key={attempt.attemptId}>
                      <td>{new Date(attempt.createdAt).toLocaleString()}</td>
                      <td><Badge>{attempt.mode}</Badge></td>
                      <td>{attempt.subjectCodes.join(", ")}</td>
                      <td>{attempt.questionIds.length}</td>
                      <td>{attempt.score.percent == null ? "Unscored" : `${attempt.score.percent}%`}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}

      <section>
        <div className="section-heading">
          <div>
            <span className="eyebrow">Saved for later</span>
            <h2>Bookmarks</h2>
          </div>
        </div>
        <div className="bookmark-columns">
          <article>
            <h3>Study chapters</h3>
            {localState.bookmarks.chapterIds.length ? (
              <ul>
                {localState.bookmarks.chapterIds.map((chapterId) => {
                  const chapter = data.chapterById.get(chapterId);
                  return chapter ? (
                    <li key={chapterId}>
                      <a href={routeHref({ name: "chapter", chapterId })}>
                        <Badge>{chapter.course_code}</Badge>
                        <span>
                          {chapter.title_en}
                          <small lang="th">{chapter.title_th}</small>
                        </span>
                        <Icon name="arrow" size={16} />
                      </a>
                    </li>
                  ) : null;
                })}
              </ul>
            ) : (
              <p>No chapter bookmarks yet.</p>
            )}
          </article>
          <article>
            <h3>Practice questions</h3>
            {localState.bookmarks.questionIds.length ? (
              <ul>
                {localState.bookmarks.questionIds.map((questionId) => {
                  const question = data.questions.find(
                    (item) => item.question_id === questionId,
                  );
                  return question ? (
                    <li key={questionId}>
                      <a href={`${routeHref({ name: "practice" })}?question=${questionId}`}>
                        <Badge>{question.subject_code}</Badge>
                        <span>
                          {question.original_question_en}
                          <small lang="th">{question.question_th}</small>
                        </span>
                        <Icon name="arrow" size={16} />
                      </a>
                    </li>
                  ) : null;
                })}
              </ul>
            ) : (
              <p>No question bookmarks yet.</p>
            )}
          </article>
        </div>
      </section>

      <ConfirmDialog
        confirmLabel="Reset local progress"
        danger
        onCancel={() => setResetOpen(false)}
        onConfirm={() => {
          setResetOpen(false);
          onReset();
        }}
        open={resetOpen}
        title="Reset all progress?"
      >
        <p>
          This clears attempts, scores, preferences, and bookmarks saved by this
          application on this browser. Academic data and unrelated browser
          storage are not changed.
        </p>
        <p lang="th">การดำเนินการนี้ย้อนกลับไม่ได้</p>
      </ConfirmDialog>
    </div>
  );
}

