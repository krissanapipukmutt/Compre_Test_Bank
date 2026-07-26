# Repository Instructions

## Mission

Build and maintain a local-first bilingual comprehensive-examination study application from the academic source files in this repository.

## Source protection

- Treat `TERM1/`, `TERM2/`, and root-level academic files as immutable source material.
- Never move, rename, delete, overwrite, or re-save an original academic file.
- Keep generated content under `docs/`, `data/`, `reports/`, `scripts/`, or `web/`.
- Do not transmit academic files or extracted academic content to external services.
- Do not add secrets, paid services, authentication, or a backend without an explicit requirement.

## Academic integrity

- Preserve original English examination wording and choices exactly, except for logged, obvious OCR corrections.
- Never invent an answer or upgrade an inference to a verified answer.
- Use final answer statuses exactly as defined: `verified_from_course_material`, `verified_from_external_source`, `strongly_supported_by_external_source`, `probabilistic_recommendation`, `unresolvable_question`.
- Preserve the pre-research status in `original_answer_status`; never overwrite the historical classification.
- Use evidence origins exactly as defined: `COURSE_MATERIAL`, `EXTERNAL_AUTHORITATIVE`, `PROBABILISTIC_REASONING_ONLY`.
- Probability-based recommendations must retain the exact bilingual warning, a distribution totaling 100%, and human review.
- Use evidence types exactly as defined: `directly_stated`, `summarized_from_source`, `supplementary`, `uncertain`.
- Cite the stable source file ID and page or slide whenever determinable.
- Put low-confidence or ambiguous academic content in the appropriate human-review report.
- Thai translations must preserve meaning and must not reveal answers.

## Data and implementation

- Use UTF-8 and preserve Thai characters.
- Use stable IDs for files, subjects, chapters, topics, questions, and choices.
- Never use an array index as an answer key.
- Validate every generated JSON file and all cross-references.
- Keep the web application under `web/`, use TypeScript strict mode, and favor minimal dependencies.
- Do not expose answers in practice or mock-exam views before the learner submits.
- Do not reveal answer-status/evidence-origin badges before submission; show provenance and external-source details only in feedback/review.
- Normal scoring includes course-verified and externally verified items. Strong external support is learner opt-in; probability-only and unresolved items are unscored by default.
- Store progress and bookmarks locally in the browser.
- Build mobile-first and verify every required viewport.
- Use `apply_patch` for hand-edited source files and preserve unrelated work.

## Required workflow

- Inspect before editing and read `PLANS.md`, `TASKS.md`, and `PROJECT_STATE.md` before resuming.
- Work through Phases 0–6 in order, including every validation gate.
- Update `TASKS.md`, `PROJECT_STATE.md`, and `PLANS.md` after every phase.
- Write a phase-completion report under `reports/`.
- Run the relevant academic validation, lint, type check, tests, and production build after changes.
- If Git is available and the tree is safe, commit a completed phase intentionally. Do not initialize Git implicitly.
- Never run destructive Git or filesystem commands without explicit approval.

## Hard blockers

Record a hard blocker in `reports/blockers.md` and `PROJECT_STATE.md` only when the project is inaccessible, critical sources are encrypted or corrupted, administrator credentials are required, a destructive action is necessary, academic ambiguity would corrupt data, the application cannot be repaired to build, explicit approval is required, work would leave project scope, or remaining context is too low for safe continuation.
