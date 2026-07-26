# Acceptance Criteria

## Academic and data

- AC-01: All bundled JSON parses and passes runtime relationships.
- AC-02: Every displayed question retains its English original and five stable choices.
- AC-03: Verified answers have evidence; inferred answers are labelled; review-required questions are unscored.
- AC-04: Randomization never changes which stable choice ID is correct.
- AC-05: BIS603 and diagram/table warnings remain visible where relevant.

## Study

- AC-06: Learner can reach every subject and chapter from its term.
- AC-07: English/Thai summaries, glossary, study aids, confidence, and sources render.
- AC-08: Search returns English and Thai subject/chapter/topic/question matches.
- AC-09: Chapter/question bookmarks survive reload.

## Practice and mock

- AC-10: All required practice filters work together.
- AC-11: No answer or explanation appears before submission.
- AC-12: Immediate/delayed feedback and review queues behave as configured.
- AC-13: Mock supports subject/count/timer, navigator, unanswered confirmation, submission, subject/topic scores, and bilingual review.
- AC-14: Timer expiry submits once and remains visible without obstructing the question.

## Progress

- AC-15: Attempts, history, subject/topic performance, weak topics, and bookmarks persist locally.
- AC-16: Reset requires confirmation and clears only application progress.

## Responsive/accessibility

- AC-17: No unintended document-level horizontal overflow at all ten target viewports.
- AC-18: Mobile navigation, filters, navigator, choices, timer, dialogs, and source references remain usable.
- AC-19: Interactive targets are generally at least 44×44 px and do not rely on hover.
- AC-20: Keyboard flow, visible focus, labelled controls/dialogs, semantic landmarks, contrast, reduced motion, and Thai line wrapping pass review.

## Engineering/release

- AC-21: Academic validation, lint, strict type check, tests, and production build pass.
- AC-22: Production preview loads without runtime/data errors and makes no external requests.
- AC-23: README and final reports contain exact commands, results, limitations, and unresolved academic reviews.

