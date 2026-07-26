# Translation Integrity Audit

Completed: 2026-07-26 (Asia/Bangkok)

## Outcome

- Questions audited: 105
- Questions with complete reviewed Thai: 105
- Question stem fields repaired: 104
- Answer choices audited: 525
- Answer choices repaired: 490
- Preserved original-choice snapshot translations repaired: 490
- Question explanation fields repaired: 315
- Option explanation fields repaired: 125
- External evidence summaries repaired: 49
- Incomplete translations: 0
- Translation records requiring human review: 8
- Placeholder occurrences removed from the question dataset: 690
- Glossary terms: 24
- Answer-key changes caused by translation: 0

## Audit method

Every English stem and choice was reviewed in context against its question, subject, visual dependency, and existing evidence. Thai was rewritten as complete natural language rather than token substitution. Conditions, negatives, comparisons, examples, identifiers, code, and choice order were preserved. Code and proper names remain unchanged only when translation would alter them; these cases carry an explicit choice-level review note.

## Integrity controls

- `data/translation-preservation-baseline.json` fingerprints English originals, IDs, order, correctness flags, and answer statuses.
- `scripts/validate_translation_integrity.py` enforces completeness, placeholder rejection, Thai-density/context triggers, metadata, glossary consistency, and baseline preservation.
- Runtime loading blocks invalid bilingual data.
- Scored exam selection excludes questions whose translation status is incomplete, ambiguous, or requires human review.

## Frontend verification

The learner-facing layout now renders the English original before Thai for the question, each choice, final explanation, each option explanation, probability evidence, unresolved reasons, external evidence summaries, and source notes. Missing or placeholder Thai raises a bilingual blocking warning and disables answering. The new translation-readiness gate also prevents incomplete or review-required translations from contributing to scores or entering mock exams.

Modified application files:

- `web/src/translation.ts`
- `web/src/domain.ts`
- `web/src/data.ts`
- `web/src/engine.ts`
- `web/src/session.ts`
- `web/src/components/QuestionCard.tsx`
- `web/src/styles.css`

## Validation and test results

- Translation validator: 105 questions, 525 choices, 24 glossary terms, 0 errors, 0 warnings.
- Phase 8 preservation and visual validator: 0 errors, 0 warnings.
- Unit/integration tests: 40/40 passed.
- Browser tests: 12/12 passed.
- Required bilingual viewports: 320×568, 360×800, 390×844, 412×915, 768×1024, 1024×768, and 1280×800 all passed without horizontal overflow, clipping, ellipsis, or English/Thai order reversal.
- Production build: passed.
- Production visual assets: 18/18 referenced assets present and hash-matched.
- Dependency audit: 0 vulnerabilities.

## Human-review scope

The complete Thai text for Q22, Q23, Q32, Q35, Q60, Q63, Q69, and Q92 is retained for study, but the translation status remains `requires_human_review` because the English source is malformed, incomplete, or does not support a unique interpretation. These items are not treated as translation-ready for scored exams.
