import { useEffect, useState } from "react";
import { academicData } from "./data";
import { scoreAttempt } from "./engine";
import { navigate, useRoute } from "./router";
import { createSession, type ActiveSession, type SessionConfig } from "./session";
import {
  loadLocalState,
  resetLocalState,
  saveLocalState,
  toggleId,
  type Attempt,
  type LocalState,
} from "./storage";
import { AppShell } from "./components/AppShell";
import { AcademicNotice } from "./components/Common";
import { Dashboard } from "./pages/Dashboard";
import {
  ChapterPage,
  LibraryPage,
  SubjectPage,
} from "./pages/Library";
import {
  ExamSessionPage,
  MockSetup,
  PracticeSetup,
  SessionReviewPage,
} from "./pages/Exam";
import { ProgressPage } from "./pages/Progress";
import { AboutPage } from "./pages/About";

function App() {
  const route = useRoute();
  const initial = useState(() => loadLocalState());
  const [localState, setLocalState] = useState<LocalState>(initial[0].state);
  const [storageRecovered, setStorageRecovered] = useState(initial[0].recovered);
  const [activeSession, setActiveSession] = useState<ActiveSession | null>(null);

  useEffect(() => {
    saveLocalState(localState);
  }, [localState]);

  const startSession = (config: SessionConfig) => {
    const session = createSession(academicData.questions, config);
    setActiveSession(session);
    setLocalState((current) => ({
      ...current,
      preferences: {
        ...current.preferences,
        feedbackMode: config.feedbackMode,
        randomizeQuestions: config.randomizeQuestions,
        randomizeChoices: config.randomizeChoices,
      },
    }));
    navigate(
      config.mode === "mock"
        ? { name: "mock-exam" }
        : { name: "practice-session" },
    );
  };

  const finishSession = () => {
    if (!activeSession || activeSession.finished) return;
    const finishedAt = Date.now();
    const score = scoreAttempt(activeSession.questions, activeSession.answers);
    const attempt: Attempt = {
      attemptId: activeSession.sessionId,
      createdAt: new Date(finishedAt).toISOString(),
      mode: activeSession.mode,
      questionIds: activeSession.questions.map(
        (question) => question.question_id,
      ),
      answers: activeSession.answers,
      choiceOrder: Object.fromEntries(
        activeSession.questions.map((question) => [
          question.question_id,
          question.choices.map((choice) => choice.choice_id),
        ]),
      ),
      score,
      durationSeconds: Math.max(
        0,
        Math.round((finishedAt - activeSession.startedAt) / 1000),
      ),
      subjectCodes: Array.from(
        new Set(
          activeSession.questions.map((question) => question.subject_code),
        ),
      ),
    };
    setLocalState((current) => ({
      ...current,
      attempts: [attempt, ...current.attempts],
    }));
    setActiveSession((current) =>
      current
        ? {
            ...current,
            finished: true,
            finishedAt,
            submittedQuestionIds: current.questions.map(
              (question) => question.question_id,
            ),
          }
        : current,
    );
    navigate(
      activeSession.mode === "mock"
        ? { name: "mock-results" }
        : { name: "practice-review" },
    );
  };

  const toggleChapterBookmark = (chapterId: string) =>
    setLocalState((current) => ({
      ...current,
      bookmarks: {
        ...current.bookmarks,
        chapterIds: toggleId(current.bookmarks.chapterIds, chapterId),
      },
    }));
  const toggleQuestionBookmark = (questionId: string) =>
    setLocalState((current) => ({
      ...current,
      bookmarks: {
        ...current.bookmarks,
        questionIds: toggleId(current.bookmarks.questionIds, questionId),
      },
    }));

  let page;
  switch (route.name) {
    case "library":
      page = <LibraryPage data={academicData} />;
      break;
    case "subject":
      page = <SubjectPage code={route.code} data={academicData} />;
      break;
    case "chapter":
      page = (
        <ChapterPage
          bookmarked={localState.bookmarks.chapterIds.includes(route.chapterId)}
          chapterId={route.chapterId}
          data={academicData}
          onBookmark={() => toggleChapterBookmark(route.chapterId)}
        />
      );
      break;
    case "practice":
      page = (
        <PracticeSetup
          data={academicData}
          localState={localState}
          onStart={startSession}
        />
      );
      break;
    case "practice-session":
    case "mock-exam":
      page = (
        <ExamSessionPage
          bookmarkedQuestionIds={localState.bookmarks.questionIds}
          onBookmark={toggleQuestionBookmark}
          onFinish={finishSession}
          session={activeSession}
          setSession={setActiveSession}
        />
      );
      break;
    case "practice-review":
    case "mock-results":
      page = (
        <SessionReviewPage
          bookmarkedQuestionIds={localState.bookmarks.questionIds}
          data={academicData}
          onBookmark={toggleQuestionBookmark}
          session={activeSession}
        />
      );
      break;
    case "mock":
      page = <MockSetup data={academicData} onStart={startSession} />;
      break;
    case "progress":
      page = (
        <ProgressPage
          data={academicData}
          localState={localState}
          onReset={() => {
            setLocalState(resetLocalState());
            setActiveSession(null);
          }}
        />
      );
      break;
    case "about":
      page = <AboutPage data={academicData} />;
      break;
    case "home":
    default:
      page = <Dashboard data={academicData} localState={localState} />;
  }

  return (
    <AppShell route={route}>
      {storageRecovered ? (
        <div className="global-notice">
          <AcademicNotice title="Local progress was recovered" severity="danger">
            <p>
              Invalid saved state was ignored and safe defaults were loaded.
              Academic data was not affected.
            </p>
            <button
              className="text-button"
              onClick={() => setStorageRecovered(false)}
              type="button"
            >
              Dismiss
            </button>
          </AcademicNotice>
        </div>
      ) : null}
      {page}
    </AppShell>
  );
}

export default App;

