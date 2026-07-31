import {
  useEffect,
  useRef,
  useState,
  type Dispatch,
  type SetStateAction,
} from "react";
import type { AcademicData, AnswerStatus, Difficulty } from "../domain";
import { isVisualReady, scoreAttempt, scoreQuestion } from "../engine";
import type { ActiveSession, SessionConfig } from "../session";
import { remainingSeconds } from "../session";
import type { LocalState } from "../storage";
import { routeHref } from "../router";
import {
  AcademicNotice,
  Badge,
  ConfirmDialog,
  EmptyState,
  Icon,
} from "../components/Common";
import { QuestionCard } from "../components/QuestionCard";

function queryParameters(): URLSearchParams {
  const query = window.location.hash.split("?")[1] ?? "";
  return new URLSearchParams(query);
}

export function PracticeSetup({
  data,
  localState,
  onStart,
}: {
  data: AcademicData;
  localState: LocalState;
  onStart: (config: SessionConfig) => void;
}) {
  const params = queryParameters();
  const [subjectCode, setSubjectCode] = useState(params.get("subject") ?? "");
  const [chapterId, setChapterId] = useState(params.get("chapter") ?? "");
  const [topicId, setTopicId] = useState(params.get("topic") ?? "");
  const [difficulty, setDifficulty] = useState<Difficulty | "all">("all");
  const [answerStatus, setAnswerStatus] = useState<AnswerStatus | "all">("all");
  const [count, setCount] = useState(10);
  const [feedbackMode, setFeedbackMode] = useState<"immediate" | "delayed">(
    localState.preferences.feedbackMode,
  );
  const [randomizeQuestions, setRandomizeQuestions] = useState(
    localState.preferences.randomizeQuestions,
  );
  const [randomizeChoices, setRandomizeChoices] = useState(
    localState.preferences.randomizeChoices,
  );
  const [queue, setQueue] = useState<
    "all" | "bookmarked" | "incorrect" | "unanswered" | "judgment"
  >(params.has("question") ? "bookmarked" : "all");

  const lastAttempts = localState.attempts;
  const incorrectIds = Array.from(
    new Set(
      lastAttempts.flatMap((attempt) =>
        attempt.questionIds.filter((questionId) => {
          const question = data.questions.find(
            (item) => item.question_id === questionId,
          );
          if (!question) return false;
          return (
            scoreQuestion(question, attempt.answers[questionId] ?? []).correct ===
            false
          );
        }),
      ),
    ),
  );
  const unansweredIds = Array.from(
    new Set(
      lastAttempts.flatMap((attempt) =>
        attempt.questionIds.filter(
          (questionId) => (attempt.answers[questionId] ?? []).length === 0,
        ),
      ),
    ),
  );

  const available = data.questions.filter((question) => {
    if (subjectCode && question.subject_code !== subjectCode) return false;
    if (chapterId && question.chapter_id !== chapterId) return false;
    if (topicId && !question.study_topic_ids.includes(topicId)) return false;
    if (difficulty !== "all" && question.difficulty !== difficulty) return false;
    if (
      answerStatus !== "all" &&
      question.answer_status !== answerStatus
    )
      return false;
    if (
      answerStatus === "all" &&
      queue !== "judgment" &&
      (question.answer_status === "probabilistic_recommendation" ||
        question.answer_status === "unresolvable_question")
    )
      return false;
    if (
      queue === "bookmarked" &&
      !localState.bookmarks.questionIds.includes(question.question_id)
    )
      return false;
    if (queue === "incorrect" && !incorrectIds.includes(question.question_id))
      return false;
    if (queue === "unanswered" && !unansweredIds.includes(question.question_id))
      return false;
    if (
      queue === "judgment" &&
      question.answer_status !== "probabilistic_recommendation"
    )
      return false;
    return true;
  }).length;

  const chapters = data.chapters.filter(
    (chapter) => !subjectCode || chapter.course_code === subjectCode,
  );
  const topics = data.topics.filter(
    (topic) =>
      (!subjectCode ||
        data.subjects.find((subject) => subject.subject_id === topic.subject_id)
          ?.course_code === subjectCode) &&
      (!chapterId || topic.chapter_id === chapterId),
  );

  const start = () =>
    onStart({
      mode: "practice",
      filters: {
        subjectCode: subjectCode || undefined,
        chapterId: chapterId || undefined,
        topicId: topicId || undefined,
        difficulty,
        answerStatus,
      },
      subjectCodes: [],
      questionCount: Math.min(count, available),
      feedbackMode,
      randomizeQuestions,
      randomizeChoices,
      timerMinutes: null,
      bookmarkedQuestionIds:
        queue === "bookmarked" ? localState.bookmarks.questionIds : undefined,
      onlyIncorrectQuestionIds:
        queue === "incorrect" ? incorrectIds : undefined,
      onlyUnansweredQuestionIds:
        queue === "unanswered" ? unansweredIds : undefined,
      judgmentOnly: queue === "judgment",
    });

  return (
    <div className="page">
      <header className="page-header page-header--split">
        <div>
          <span className="eyebrow">Focused question sessions</span>
          <h1>Practice mode</h1>
          <p lang="th">เลือกหัวข้อ ฝึกแบบสุ่ม และรับคำอธิบายหลังส่งคำตอบ</p>
        </div>
        <div className="library-count">
          <strong>{available}</strong>
          <span>matching questions</span>
        </div>
      </header>

      <div className="setup-layout">
        <form className="setup-card" onSubmit={(event) => event.preventDefault()}>
          <section>
            <span className="setup-step">01</span>
            <div>
              <h2>Choose coverage</h2>
              <p lang="th">เลือกขอบเขตคำถาม</p>
            </div>
          </section>
          <div className="form-grid">
            <label>
              <span>Subject</span>
              <select
                onChange={(event) => {
                  setSubjectCode(event.currentTarget.value);
                  setChapterId("");
                  setTopicId("");
                }}
                value={subjectCode}
              >
                <option value="">All subjects</option>
                {data.subjects.map((subject) => (
                  <option key={subject.subject_id} value={subject.course_code}>
                    {subject.course_code} — {subject.course_title_en}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Chapter</span>
              <select
                onChange={(event) => {
                  setChapterId(event.currentTarget.value);
                  setTopicId("");
                }}
                value={chapterId}
              >
                <option value="">All chapters</option>
                {chapters.map((chapter) => (
                  <option key={chapter.chapter_id} value={chapter.chapter_id}>
                    {chapter.title_en}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Study topic</span>
              <select
                aria-label="Study topic"
                onChange={(event) => setTopicId(event.currentTarget.value)}
                value={topicId}
              >
                <option value="">All topics</option>
                {topics.map((topic) => (
                  <option key={topic.topic_id} value={topic.topic_id}>
                    {topic.title_en}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Difficulty</span>
              <select
                onChange={(event) =>
                  setDifficulty(event.currentTarget.value as Difficulty | "all")
                }
                value={difficulty}
              >
                <option value="all">All difficulties</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </label>
            <label>
              <span>Answer status</span>
              <select
                onChange={(event) =>
                  setAnswerStatus(
                    event.currentTarget.value as AnswerStatus | "all",
                  )
                }
                value={answerStatus}
              >
                <option value="all">All statuses</option>
                <option value="verified_from_course_material">
                  Verified from course materials
                </option>
                <option value="verified_from_external_source">
                  Verified from external sources
                </option>
                <option value="strongly_supported_by_external_source">
                  Strong external support
                </option>
                <option value="probabilistic_recommendation">
                  Probability-based recommendation
                </option>
                <option value="unresolvable_question">
                  Answer remains unresolved
                </option>
              </select>
            </label>
          </div>

          <section>
            <span className="setup-step">02</span>
            <div>
              <h2>Choose a review queue</h2>
              <p lang="th">ทบทวนตามสถานะการเรียน</p>
            </div>
          </section>
          <div className="radio-card-grid">
            {(
              [
                ["all", "All matching", `${available} available`],
                [
                  "bookmarked",
                  "Bookmarked",
                  `${localState.bookmarks.questionIds.length} saved`,
                ],
                ["incorrect", "Incorrect", `${incorrectIds.length} to review`],
                ["unanswered", "Unanswered", `${unansweredIds.length} to revisit`],
                [
                  "judgment",
                  "Questions requiring judgment",
                  `${
                    data.questions.filter(
                      (question) =>
                        question.answer_status ===
                        "probabilistic_recommendation",
                    ).length
                  } unscored`,
                ],
              ] as const
            ).map(([value, label, detail]) => (
              <label className={queue === value ? "is-selected" : ""} key={value}>
                <input
                  checked={queue === value}
                  name="queue"
                  onChange={() => setQueue(value)}
                  type="radio"
                />
                <strong>{label}</strong>
                <small>{detail}</small>
              </label>
            ))}
          </div>

          <section>
            <span className="setup-step">03</span>
            <div>
              <h2>Session behavior</h2>
              <p lang="th">กำหนดรูปแบบการฝึก</p>
            </div>
          </section>
          <div className="form-grid">
            <label>
              <span>Question count</span>
              <select
                onChange={(event) => setCount(Number(event.currentTarget.value))}
                value={count}
              >
                {[5, 10, 15, 20, 30, 50].map((value) => (
                  <option key={value} value={value}>
                    {value} questions
                  </option>
                ))}
              </select>
            </label>
            <fieldset className="inline-fieldset">
              <legend>Feedback</legend>
              <label>
                <input
                  checked={feedbackMode === "immediate"}
                  name="feedback"
                  onChange={() => setFeedbackMode("immediate")}
                  type="radio"
                />
                Immediate
              </label>
              <label>
                <input
                  checked={feedbackMode === "delayed"}
                  name="feedback"
                  onChange={() => setFeedbackMode("delayed")}
                  type="radio"
                />
                Delayed
              </label>
            </fieldset>
          </div>
          <div className="toggle-list">
            <label>
              <span>
                <strong>Random question order</strong>
                <small>Uses a stable session seed</small>
              </span>
              <input
                checked={randomizeQuestions}
                onChange={(event) =>
                  setRandomizeQuestions(event.currentTarget.checked)
                }
                role="switch"
                type="checkbox"
              />
            </label>
            <label>
              <span>
                <strong>Random choice order</strong>
                <small>Answer keys remain stable IDs</small>
              </span>
              <input
                checked={randomizeChoices}
                onChange={(event) =>
                  setRandomizeChoices(event.currentTarget.checked)
                }
                role="switch"
                type="checkbox"
              />
            </label>
          </div>
        </form>

        <aside className="setup-summary">
          <span className="eyebrow">Session summary</span>
          <strong>{Math.min(count, available)}</strong>
          <span>questions selected</span>
          <dl>
            <div>
              <dt>Feedback</dt>
              <dd>{feedbackMode}</dd>
            </div>
            <div>
              <dt>Queue</dt>
              <dd>{queue}</dd>
            </div>
            <div>
              <dt>Choice order</dt>
              <dd>{randomizeChoices ? "random" : "source"}</dd>
            </div>
          </dl>
          <button
            className="button button--primary button--wide"
            disabled={available === 0}
            onClick={start}
            type="button"
          >
            Start practice <Icon name="arrow" />
          </button>
          {available === 0 ? (
            <small>No questions match this combination. Adjust a filter or queue.</small>
          ) : null}
        </aside>
      </div>
    </div>
  );
}

export function MockSetup({
  data,
  onStart,
}: {
  data: AcademicData;
  onStart: (config: SessionConfig) => void;
}) {
  const [subjects, setSubjects] = useState<string[]>([]);
  const [count, setCount] = useState(20);
  const [timer, setTimer] = useState<number | null>(30);
  const [includeStrongExternal, setIncludeStrongExternal] = useState(false);
  const available = data.questions.filter(
    (question) =>
      (subjects.length === 0 || subjects.includes(question.subject_code)) &&
      isVisualReady(question) &&
      ((!question.requires_human_review &&
        (question.answer_status === "verified_from_course_material" ||
          question.answer_status === "verified_from_external_source")) ||
        (includeStrongExternal &&
          question.answer_status ===
            "strongly_supported_by_external_source")),
  ).length;
  const toggle = (code: string) =>
    setSubjects((current) =>
      current.includes(code)
        ? current.filter((item) => item !== code)
        : [...current, code],
    );
  return (
    <div className="page">
      <header className="page-header page-header--split">
        <div>
          <span className="eyebrow">Timed, delayed-feedback assessment</span>
          <h1>Mock examination</h1>
          <p lang="th">จำลองการสอบจริง โดยไม่แสดงคำตอบก่อนส่งข้อสอบ</p>
        </div>
        <div className="library-count library-count--dark">
          <Icon name="clock" size={26} />
          <span>Optional timer</span>
        </div>
      </header>
      <div className="setup-layout">
        <form className="setup-card" onSubmit={(event) => event.preventDefault()}>
          <section>
            <span className="setup-step">01</span>
            <div>
              <h2>Select subjects</h2>
              <p lang="th">ไม่เลือกหมายถึงใช้ทุกวิชา</p>
            </div>
          </section>
          <div className="subject-check-grid">
            {data.subjects.map((subject) => (
              <label
                className={subjects.includes(subject.course_code) ? "is-selected" : ""}
                key={subject.subject_id}
              >
                <input
                  checked={subjects.includes(subject.course_code)}
                  onChange={() => toggle(subject.course_code)}
                  type="checkbox"
                />
                <Badge>{subject.term === "term-1" ? "T1" : "T2"}</Badge>
                <strong>{subject.course_code}</strong>
                <small>{subject.course_title_en}</small>
              </label>
            ))}
          </div>

          <section>
            <span className="setup-step">02</span>
            <div>
              <h2>Exam settings</h2>
              <p lang="th">จำนวนข้อและเวลา</p>
            </div>
          </section>
          <div className="form-grid">
            <label>
              <span>Question count</span>
              <select
                onChange={(event) => setCount(Number(event.currentTarget.value))}
                value={count}
              >
                {[10, 20, 30, 50, 75, 100].map((value) => (
                  <option key={value} value={value}>
                    {value} questions
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Timer</span>
              <select
                onChange={(event) =>
                  setTimer(
                    event.currentTarget.value === "none"
                      ? null
                      : Number(event.currentTarget.value),
                  )
                }
                value={timer ?? "none"}
              >
                <option value="none">No timer</option>
                <option value="15">15 minutes</option>
                <option value="30">30 minutes</option>
                <option value="60">60 minutes</option>
                <option value="90">90 minutes</option>
              </select>
            </label>
          </div>
          <AcademicNotice title="Answers stay sealed" severity="info">
            <p>
              Explanations and supported answers appear only after final
              submission. Review-required items remain unscored.
            </p>
          </AcademicNotice>
          <div className="toggle-list">
            <label>
              <span>
                <strong>Include externally supported questions</strong>
                <small>
                  Adds items with strong external support that are not fully
                  definitive
                </small>
              </span>
              <input
                checked={includeStrongExternal}
                onChange={(event) =>
                  setIncludeStrongExternal(event.currentTarget.checked)
                }
                role="switch"
                type="checkbox"
              />
            </label>
          </div>
        </form>
        <aside className="setup-summary setup-summary--mock">
          <span className="eyebrow">Exam card</span>
          <strong>{Math.min(count, available)}</strong>
          <span>questions</span>
          <dl>
            <div>
              <dt>Subjects</dt>
              <dd>{subjects.length || "All 6"}</dd>
            </div>
            <div>
              <dt>Timer</dt>
              <dd>{timer ? `${timer} min` : "Off"}</dd>
            </div>
            <div>
              <dt>Feedback</dt>
              <dd>After submit</dd>
            </div>
          </dl>
          <button
            className="button button--primary button--wide"
            disabled={available === 0}
            onClick={() =>
              onStart({
                mode: "mock",
                filters: {},
                subjectCodes: subjects,
                questionCount: Math.min(count, available),
                feedbackMode: "delayed",
                randomizeQuestions: true,
                randomizeChoices: true,
                timerMinutes: timer,
                includeStrongExternal,
              })
            }
            type="button"
          >
            Begin mock exam <Icon name="arrow" />
          </button>
        </aside>
      </div>
    </div>
  );
}

function Timer({
  session,
  onExpire,
}: {
  session: ActiveSession;
  onExpire: () => void;
}) {
  const [remaining, setRemaining] = useState(() =>
    remainingSeconds(session.startedAt, session.durationSeconds),
  );
  const expiredRef = useRef(false);
  const onExpireRef = useRef(onExpire);

  useEffect(() => {
    onExpireRef.current = onExpire;
  }, [onExpire]);

  useEffect(() => {
    expiredRef.current = false;
    const tick = () => {
      const next = remainingSeconds(
        session.startedAt,
        session.durationSeconds,
      );
      setRemaining(next);
      if (next === 0 && !expiredRef.current) {
        expiredRef.current = true;
        onExpireRef.current();
      }
    };
    tick();
    if (session.durationSeconds === null) return;
    const timerId = window.setInterval(tick, 1000);
    return () => window.clearInterval(timerId);
  }, [session.durationSeconds, session.sessionId, session.startedAt]);
  if (remaining === null) return <span>Untimed</span>;
  const minutes = Math.floor(remaining / 60);
  const seconds = remaining % 60;
  return (
    <span aria-live={remaining <= 60 ? "polite" : "off"} className={remaining <= 60 ? "timer timer--urgent" : "timer"}>
      <Icon name="clock" size={18} />
      {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}
    </span>
  );
}

export function ExamSessionPage({
  session,
  setSession,
  bookmarkedQuestionIds,
  onBookmark,
  onFinish,
}: {
  session: ActiveSession | null;
  setSession: Dispatch<SetStateAction<ActiveSession | null>>;
  bookmarkedQuestionIds: string[];
  onBookmark: (questionId: string) => void;
  onFinish: () => void;
}) {
  const [confirmOpen, setConfirmOpen] = useState(false);
  if (!session || session.questions.length === 0) {
    return (
      <div className="page">
        <EmptyState title="No active session">
          <p>Configure a new practice or mock session to begin.</p>
          <a className="button button--primary" href={routeHref({ name: "practice" })}>
            Configure practice
          </a>
        </EmptyState>
      </div>
    );
  }
  const question = session.questions[session.currentIndex]!;
  const selected = session.answers[question.question_id] ?? [];
  const reveal =
    session.feedbackMode === "immediate" &&
    session.submittedQuestionIds.includes(question.question_id);
  const answeredCount = Object.values(session.answers).filter(
    (answer) => answer.length > 0,
  ).length;
  const unanswered = session.questions.length - answeredCount;

  const updateAnswer = (choiceIds: string[]) =>
    setSession((current) =>
      current
        ? {
            ...current,
            answers: { ...current.answers, [question.question_id]: choiceIds },
          }
        : current,
    );
  const submitCurrent = () =>
    setSession((current) =>
      current
        ? {
            ...current,
            submittedQuestionIds: Array.from(
              new Set([...current.submittedQuestionIds, question.question_id]),
            ),
          }
        : current,
    );
  const move = (index: number) =>
    setSession((current) =>
      current
        ? {
            ...current,
            currentIndex: Math.max(
              0,
              Math.min(index, current.questions.length - 1),
            ),
          }
        : current,
    );
  const next = () => {
    if (session.currentIndex === session.questions.length - 1) {
      if (session.mode === "practice") {
        onFinish();
      } else {
        setConfirmOpen(true);
      }
    } else {
      move(session.currentIndex + 1);
    }
  };

  return (
    <div className="exam-page">
      <header className="exam-status">
        <div>
          <Badge tone={session.mode === "mock" ? "danger" : "teal"}>
            {session.mode === "mock" ? "MOCK EXAM" : "PRACTICE"}
          </Badge>
          <span>
            Question {session.currentIndex + 1} of {session.questions.length}
          </span>
        </div>
        <div>
          <span>{answeredCount} answered</span>
          <span>{unanswered} unanswered</span>
          <Timer onExpire={onFinish} session={session} />
        </div>
      </header>

      <div className="exam-layout">
        <div className="exam-question">
          <QuestionCard
            bookmarked={bookmarkedQuestionIds.includes(question.question_id)}
            onBookmark={() => onBookmark(question.question_id)}
            onChange={updateAnswer}
            question={question}
            reveal={reveal}
            selectedChoiceIds={selected}
          />
          <div className="exam-actions">
            <button
              className="button button--ghost"
              disabled={session.currentIndex === 0}
              onClick={() => move(session.currentIndex - 1)}
              type="button"
            >
              Previous
            </button>
            {session.mode === "practice" &&
            session.feedbackMode === "immediate" &&
            !reveal ? (
              <button
                className="button button--primary"
                disabled={selected.length === 0}
                onClick={submitCurrent}
                type="button"
              >
                Submit answer
              </button>
            ) : (
              <button className="button button--primary" onClick={next} type="button">
                {session.currentIndex === session.questions.length - 1
                  ? session.mode === "mock"
                    ? "Review & submit"
                    : "Finish session"
                  : "Next question"}
                <Icon name="arrow" />
              </button>
            )}
          </div>
        </div>

        <aside className="question-navigator">
          <div>
            <span className="eyebrow">Navigator</span>
            <h2>Questions</h2>
          </div>
          <div className="navigator-grid">
            {session.questions.map((item, index) => {
              const answered = (session.answers[item.question_id] ?? []).length > 0;
              return (
                <button
                  aria-current={session.currentIndex === index ? "step" : undefined}
                  aria-label={`Question ${index + 1}${answered ? ", answered" : ", unanswered"}`}
                  className={`${answered ? "is-answered" : ""} ${session.currentIndex === index ? "is-current" : ""}`}
                  key={item.question_id}
                  onClick={() => move(index)}
                  type="button"
                >
                  {index + 1}
                </button>
              );
            })}
          </div>
          {session.mode === "mock" ? (
            <button
              className="button button--secondary button--wide"
              onClick={() => setConfirmOpen(true)}
              type="button"
            >
              Submit exam
            </button>
          ) : null}
        </aside>
      </div>

      <ConfirmDialog
        confirmLabel="Submit exam"
        onCancel={() => setConfirmOpen(false)}
        onConfirm={() => {
          setConfirmOpen(false);
          onFinish();
        }}
        open={confirmOpen}
        title="Submit your examination?"
      >
        <p>
          You answered {answeredCount} of {session.questions.length} questions.
          {unanswered
            ? ` ${unanswered} unanswered question${unanswered === 1 ? "" : "s"} will be recorded.`
            : " Every question has a response."}
        </p>
        <p lang="th">หลังส่งแล้วจะแก้คำตอบไม่ได้ และจะแสดงคำอธิบายผล</p>
      </ConfirmDialog>
    </div>
  );
}

export function SessionReviewPage({
  data,
  session,
  bookmarkedQuestionIds,
  onBookmark,
}: {
  data: AcademicData;
  session: ActiveSession | null;
  bookmarkedQuestionIds: string[];
  onBookmark: (questionId: string) => void;
}) {
  if (!session) {
    return (
      <div className="page">
        <EmptyState title="No completed session">
          <a className="button button--primary" href={routeHref({ name: "practice" })}>
            Start practice
          </a>
        </EmptyState>
      </div>
    );
  }
  const summary = scoreAttempt(session.questions, session.answers);
  const bySubject = data.subjects
    .map((subject) => {
      const questions = session.questions.filter(
        (question) => question.subject_code === subject.course_code,
      );
      return {
        subject,
        count: questions.length,
        summary: scoreAttempt(questions, session.answers),
      };
    })
    .filter((item) => item.count > 0);

  return (
    <div className="page page--results">
      <header className="results-hero">
        <div>
          <span className="eyebrow">
            {session.mode === "mock" ? "Mock examination complete" : "Practice complete"}
          </span>
          <h1>
            {summary.percent == null ? "Reflection complete" : `${summary.percent}%`}
          </h1>
          <p lang="th">
            {summary.percent == null
              ? "ชุดคำถามนี้ไม่มีข้อที่ให้คะแนน"
              : `ได้ ${summary.earned} จาก ${summary.possible} คะแนน`}
          </p>
        </div>
        <div className="results-score-grid">
          <div>
            <strong>{summary.correct}</strong>
            <span>correct</span>
          </div>
          <div>
            <strong>{summary.incorrect}</strong>
            <span>incorrect</span>
          </div>
          <div>
            <strong>{summary.unanswered}</strong>
            <span>unanswered</span>
          </div>
          <div>
            <strong>{summary.unscored}</strong>
            <span>unscored</span>
          </div>
        </div>
      </header>

      <section className="result-breakdown">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Performance by subject</span>
            <h2>Where to focus next</h2>
          </div>
        </div>
        <div className="performance-list">
          {bySubject.map(({ subject, count, summary: subjectSummary }) => (
            <article key={subject.subject_id}>
              <div>
                <Badge tone="teal">{subject.course_code}</Badge>
                <span>
                  <strong>{subject.course_title_en}</strong>
                  <small>{count} questions</small>
                </span>
              </div>
              <div
                aria-label={`${subjectSummary.percent ?? 0} percent`}
                className="performance-bar"
              >
                <span style={{ width: `${subjectSummary.percent ?? 0}%` }} />
              </div>
              <strong>{subjectSummary.percent ?? "—"}{subjectSummary.percent != null ? "%" : ""}</strong>
            </article>
          ))}
        </div>
      </section>

      <section>
        <div className="section-heading">
          <div>
            <span className="eyebrow">Bilingual answer review</span>
            <h2>Question by question</h2>
          </div>
          <a className="button button--secondary" href={routeHref({ name: "practice" })}>
            New practice
          </a>
        </div>
        <div className="review-stack">
          {session.questions.map((question, index) => (
            <div className="review-item" key={question.question_id}>
              <div className="review-item__label">Question {index + 1}</div>
              <QuestionCard
                bookmarked={bookmarkedQuestionIds.includes(question.question_id)}
                onBookmark={() => onBookmark(question.question_id)}
                onChange={() => undefined}
                question={question}
                reveal
                selectedChoiceIds={session.answers[question.question_id] ?? []}
              />
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
