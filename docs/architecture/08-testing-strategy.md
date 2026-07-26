# Testing Strategy

## Static/data gate

- Python academic validation checks JSON, unique IDs, parent/file references, stable answer IDs, evidence/status rules, and immutable source hashes.
- TypeScript runtime validation receives valid and deliberately invalid fixtures.

## Unit tests

- Single-choice and multiple-select scoring.
- Unanswered and review-required scoring.
- Seeded question/choice randomization and answer integrity afterward.
- Filters across term/subject/chapter/topic/difficulty/status.
- Timer calculations and one-time expiration submission.
- Progress serialization, corrupt storage fallback, bookmarks, reset, weak topics.

## Component/integration tests

- Thai renders intact.
- Answers/explanations are absent before submit and present afterward.
- Human-review warning is visible and an unscored item exposes no answer.
- Practice immediate/delayed feedback.
- Mock navigator, unanswered confirmation, score breakdown.
- Keyboard/mobile navigation and labelled dialogs.

## Browser/responsive tests

Playwright runs representative library, practice, active mock, review, progress, and modal states at:

- 320×568
- 360×800
- 375×667
- 390×844
- 412×915
- 768×1024
- 820×1180
- 1024×768
- 1280×800
- 1440×900

Assertions cover document `scrollWidth <= clientWidth` (no unintended overflow), reachable/touch-sized primary controls, opening/closing navigation, visible timer, usable navigator, wrapped source paths, and dialog bounds. Screenshots are captured for one phone, tablet, and desktop representative.

## Gates

Each implementation subphase runs academic validation, lint, `tsc --noEmit`, unit/integration tests, and production build. Phase 5.7/6 additionally run the full browser suite and representative screenshots.
