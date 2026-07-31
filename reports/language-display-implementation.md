# Language Display Implementation

**Completed:** 2026-07-31
**Status:** Complete
**Modes:** `bilingual`, `english_only`
**Preference key:** `compre-language-display-mode`

## Outcome

The application now provides one global, persistent language-display control
that remains usable in the Study Library, Practice setup and sessions, Mock
setup and timed sessions, final-submission flow, Results, and question review.
The control is presentation-only: it does not create, replace, randomize, score,
or submit an examination session.

In bilingual mode, English content remains first and Thai content appears
directly below or beside its corresponding English label. In English-only mode,
Thai question stems, embedded statements, choices, explanations, helper text,
evidence labels, topic content, and bilingual-only source-path details are
hidden through explicit language markup. English content, selected-answer
styling, English feedback, and stable source identifiers remain visible.

## State separation

Language display and academic progress are stored independently:

| State | Storage | Contents |
| --- | --- | --- |
| Language display | `compre-language-display-mode` | `bilingual` or `english_only` only |
| Local progress | `compre-study:v1` | attempts, bookmarks, and practice preferences |
| Active exam | `compre-active-exam-session` | session ID, question IDs/order, choice IDs/order, answers, submitted IDs, current index, timer origin/duration, feedback mode, and finish state |

The retired `preferences.languageView` field is read once for compatibility and
removed when progress is normalized. No answers are stored per language, and
the active-session snapshot contains no copied question wording, choice text,
translation, explanation, or academic dataset.

An active session is restored by resolving its stable question and choice IDs
against the validated bundled dataset. A missing question, unknown choice, or
invalid choice order invalidates the snapshot rather than silently
reshuffling it.

## Timer and randomization safety

- Question and choice randomization still occurs only in `createSession`.
- Language mode is not passed to `createSession` and is not a session key or
  randomization dependency.
- The timer interval depends only on the session ID, timer start, and duration.
- The latest expiry callback is held in a ref, so an application rerender after
  a language change does not restart or pause the interval.
- Remaining time is derived from the unchanged absolute `startedAt` value.
- Refreshing an active exam restores the same session ID, question order,
  choice order, answers, submitted questions, index, and timer origin.

## Interface and accessibility

- Desktop: the selector is persistently available in the application rail.
- Mobile/tablet: a sticky compact language toolbar appears below the main
  header and above the exam-status toolbar.
- Visible labels are `EN + TH` and `EN only`.
- Accessible button names are `English and Thai` and `English only`.
- Both controls use `aria-pressed` and are grouped under `Language display`.
- Button targets have a minimum width and height of 2.75 rem (44 CSS pixels at
  the default root size).
- The mobile exam-status offset accounts for both sticky shell toolbars, so the
  selector does not cover the timer, question number, navigator, or actions.
- Switching is an in-place React state update; it does not navigate, reload, or
  intentionally alter scroll position.

## Answer-sealing behavior

Before submission, the existing `reveal` boundary remains authoritative.
Switching to bilingual mode adds only Thai presentation content. The answer
panel, correctness classes, option explanations, answer-status evidence, and
sources remain absent until the normal Practice submission or final Mock
submission.

After submission, the same rendered feedback can be switched live:

- English-only keeps English explanations and option explanations.
- Bilingual adds the Thai stem, choice translations, explanation, option
  explanations, warnings, and labels.
- Scoring and learner selections are derived from the same stable IDs in both
  modes.

## Academic preservation

No file under `data/`, `web/src/data/`, `TERM1/`, `TERM2/`, or the root academic
source set was changed. No question wording, choice wording, answer key,
answer status, evidence origin, score rule, translation, or visual asset was
modified.

## Primary implementation files

- `web/src/languageDisplay.ts`
- `web/src/activeSessionStorage.ts`
- `web/src/components/LanguageDisplayControl.tsx`
- `web/src/components/AppShell.tsx`
- `web/src/components/QuestionStem.tsx`
- `web/src/components/QuestionCard.tsx`
- `web/src/components/QuestionVisuals.tsx`
- `web/src/pages/Exam.tsx`
- `web/src/styles.css`
