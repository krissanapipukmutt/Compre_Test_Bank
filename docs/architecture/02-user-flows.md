# User Flows

## First visit and study

```text
Open app → data validation → dashboard
  → choose term → choose subject → choose chapter → read bilingual topics
  → inspect glossary/source → bookmark chapter → return to dashboard
```

If validation fails, the learner receives a non-destructive error with the failed dataset name and reload guidance.

## Practice

```text
Practice setup → select filters → choose count/feedback/randomization
  → answer question → submit
  → immediate feedback OR next question
  → session summary → review incorrect/unanswered/bookmarked
```

The answer panel is absent before submit. Review-required questions show a warning, accept a learner response for reflection, and remain unscored.

## Mock examination

```text
Mock setup → select subjects/count/timer → start
  → answer/navigate/flag → timer expiry or submit action
  → unanswered confirmation → submit
  → total + subject/topic scores → bilingual answer review
```

Leaving an active mock triggers confirmation. Timer expiry submits once. Choice order is recorded with the attempt so review remains intelligible.

## Progress and reset

```text
Progress → inspect attempts/weak topics/history
  → open related practice OR manage bookmarks
  → reset → destructive confirmation → clear local progress only
```

## Keyboard/touch flow

- Skip link → header → primary navigation → page heading → controls → content.
- Mobile navigation opens into a labelled modal drawer, traps focus, closes with Escape/backdrop/close button, and restores focus.
- Question choices are native radio/checkbox controls wrapped in full-width tap targets.

