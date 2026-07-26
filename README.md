# Comprehensive Examination Study Application

A local-first bilingual study application built from the supplied KMUTT comprehensive-examination materials. It combines an evidence-linked study library, practice queues, a timed mock examination, bookmarks, and browser-local progress tracking. Course, external, probability-only, and unresolved answers remain visibly distinct after submission.

## Supported subjects

| Term | Code | Subject |
| --- | --- | --- |
| 1 | BIS602 | Business Decision and Data Analytics |
| 1 | BIS605 | Software Development Technologies for Digital Business |
| 1 | BIS606 | Digital Infrastructure and Cyber Security System |
| 2 | BIS601 | Business System Analysis and Design |
| 2 | BIS603 | Strategies Marketing Management |
| 2 | BIS604 | Business Data Management |

The exact BIS603 code-title pairing has medium confidence because the supplied corpus does not contain a sampled authoritative outline that directly confirms it.

## Data sources and generated data

- `TERM1/`, `TERM2/`, and the academic files at the project root are the immutable source corpus.
- `data/file-inventory.json` records the 374 source files, their hashes, formats, and extraction status.
- `data/subjects.json`, `chapters.json`, `topics.json`, `glossary.json`, and `source-references.json` provide the academic knowledge base.
- `data/questions.json`, `exam-sets.json`, `question-source-map.json`, and `question-review-status.json` provide the examination bank.
- `data/external-sources.json`, `external-answer-evidence.json`, and `probabilistic-recommendations.json` provide the Phase 7 provenance and probability audit.
- `docs/subjects/` contains the bilingual, human-readable subject material.
- `web/src/data/` contains application-bundled copies of the validated JSON. Do not edit these copies as the academic source of truth.

All extraction and analysis are local. The application has no server component and sends no academic content to an external service.

## Installation

Prerequisites: Python 3, Node.js 20.19+ or 22.12+, and npm.

From the project root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install "pypdf==5.9.0"
cd web
npm install
npx playwright install chromium
```

## Run and verify

Exact development command:

```bash
cd /Users/krissanap/Document/KMUTT/COMPRE_CODEX/web
npm run dev -- --host 127.0.0.1
```

Exact academic-data validation command:

```bash
cd /Users/krissanap/Document/KMUTT/COMPRE_CODEX
.venv/bin/python scripts/validate_data.py --phase 7
.venv/bin/python scripts/validate_external_research.py --check-links
```

Exact unit/integration test command:

```bash
cd /Users/krissanap/Document/KMUTT/COMPRE_CODEX/web
npm test
```

Exact responsive browser test command:

```bash
cd /Users/krissanap/Document/KMUTT/COMPRE_CODEX/web
npm run test:e2e
```

Exact complete application gate:

```bash
cd /Users/krissanap/Document/KMUTT/COMPRE_CODEX/web
npm run check
```

Exact production build and preview commands:

```bash
cd /Users/krissanap/Document/KMUTT/COMPRE_CODEX/web
npm run build
npm run preview -- --host 127.0.0.1
```

Open the URL printed by Vite. The default development URL is `http://127.0.0.1:5173/`; the default preview URL is `http://127.0.0.1:4173/`.

## Responsive and browser support

The interface is mobile-first, keyboard usable, safe-area aware, and adapts its navigation, question navigator, dialogs, references, and content grids across phones, phone landscape, tablets, tablet landscape, and desktops. Automated Chromium checks cover twelve viewport matrices from 320 × 568 through 1440 × 900, including all nine required sizes. Representative evidence is stored in `reports/screenshots/`.

The production target is current stable Chrome, Edge, Firefox, and Safari with JavaScript and browser storage enabled. The release gate was automated in Chromium 151; the other engines are expected from standards-based React/CSS behavior but were not independently certified in this environment.

## Project structure

```text
AGENTS.md / PLANS.md / TASKS.md / PROJECT_STATE.md
TERM1/ TERM2/                 immutable academic sources
data/                         validated structured academic data
docs/subjects/                bilingual study documents
docs/architecture/            requirements, UX, technical, and test design
reports/                      phase, audit, release, and screenshot evidence
scripts/                      local inventory, generation, and validation tools
web/                          React + Vite + strict TypeScript application
```

## Academic review items

- 49 answers are verified from supplied course materials (including the 16 previously verified items).
- 47 answers are verified from inspected authoritative external sources.
- 2 answers are strongly supported externally and appear in mock exams only through the “Include externally supported questions” opt-in.
- 2 probability-only recommendations are confined to the unscored “Questions requiring judgment” practice queue.
- 5 defective or under-specified questions remain unresolvable, expose no answer, and are excluded from scored exams.
- Human review remains on those 9 uncertain items and on Q96 because its corrected answer contradicts the prior inferred key.
- English examination wording remains authoritative beside the Thai study translation.
- Long Thai distractors and nuanced explanations should receive native-speaker review before high-stakes use.
- See `reports/external-research-summary.md`, `reports/still-unresolved-questions.md`, `reports/question-answer-change-log.md`, and the earlier human-review audits.

## Known limitations

- Version 1 is static and single-device: progress and bookmarks remain in that browser's local storage and do not sync.
- Clearing site data removes saved progress.
- Browser-local records are not tamper-resistant and are intended for personal study, not official examination records.
- The complete offline bilingual dataset and external-source records produce a 1.98 MB minified JavaScript bundle (213 KB gzip), so Vite emits a non-blocking chunk-size warning.
- Formal screen-reader sessions and independent Firefox/Safari browser runs were not available for this release.
- The project root is not a Git repository, so no commit history was created or altered.
