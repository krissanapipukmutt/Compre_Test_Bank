# Component Design

## Application shell

- `AppShell`: skip link, responsive rail/app bar/bottom nav, main landmark.
- `DesktopRail`, `MobileNav`, `NavigationDrawer`: share one route model.
- `PageHeader`, `Breadcrumbs`, `AcademicNotice`, `DataErrorScreen`.

## Library

- `TermSwitcher`, `SubjectCard`, `SubjectOverview`, `ChapterIndex`.
- `ChapterReader`, `TopicSection`, `GlossaryPanel`, `SourceList`.
- `SearchField`, `SearchResults`, `BookmarkButton`.

## Examination

- `PracticeSetup` and `MockSetup`: accessible fieldsets and filter summaries.
- `QuestionCard`: original English, Thai, warning, choices, submission state.
- `ChoiceList`: stable IDs, native input semantics, randomized presentation.
- `ExamStatus`: progress/timer/unanswered; compact sticky treatment.
- `QuestionNavigator`: grid on desktop, bottom sheet on mobile.
- `SubmissionDialog`, `AnswerReview`, `ChoiceExplanation`, `ScoreBreakdown`.

## Progress

- `ProgressOverview`, `MetricCard`, `SubjectPerformance`, `TopicBars`.
- `AttemptHistory`, `WeakTopicList`, `BookmarkList`, `ResetProgressDialog`.

## Engine modules

- `validateAcademicData`
- `filterQuestions`
- `shuffleWithSeed`
- `scoreQuestion` / `scoreAttempt`
- `createPracticeSession` / `createMockSession`
- `deriveWeakTopics`
- `loadLocalState` / `saveLocalState` / `resetLocalState`

Components receive stable domain objects and callbacks; they do not infer academic answers or read raw JSON directly.

