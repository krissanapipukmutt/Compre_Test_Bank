# Final Test Report

Generated: 2026-07-26 (Asia/Bangkok)

## Outcome

**PASS.** Every required final gate completed successfully.

| Gate | Command | Result |
| --- | --- | --- |
| Academic/data validation | `.venv/bin/python scripts/validate_data.py --phase 6` | PASS — 0 errors, 0 warnings |
| Immutable-source hashes | inventory SHA-256 comparison | PASS — 374/374 match; 0 modified or missing |
| Architecture validation | `.venv/bin/python scripts/validate_architecture.py` | PASS — 0 errors |
| Independent academic audit | `.venv/bin/python scripts/run_academic_audit.py` | `ready_with_warnings`; 0 structural errors |
| Lint | `npm run lint` | PASS |
| Strict TypeScript | `npm run typecheck` | PASS |
| Unit/integration | `npm test` | PASS — 19/19 tests in 6 files |
| Production build | `npm run build` | PASS — 48 modules |
| Responsive browser | `npm run test:e2e` | PASS — 5/5 Playwright tests |
| Production preview | `npm run preview -- --host 127.0.0.1` plus HTTP probe | PASS — HTTP 200 and compiled asset entry present |
| Dependency audit | `npm audit --audit-level=high` | PASS — 0 vulnerabilities |

## Automated coverage highlights

- Invalid, duplicate, missing-reference, and answer-leakage data cases
- English/Thai field integrity
- Single- and multiple-answer scoring, unanswered and unscored review states
- Stable seeded randomization and filter behavior
- Timer/session behavior
- Bookmark, progress persistence, reset, and versioned storage
- Pre-submission answer sealing and post-submission explanation visibility
- Mobile drawer and responsive navigation
- Overflow, touch targets, Thai rendering, timer, navigator, and modal fit across twelve viewport matrices

## Build output

- HTML: 0.60 KB (0.36 KB gzip)
- CSS: 36.85 KB (7.69 KB gzip)
- JavaScript: 1,327.47 KB (177.07 KB gzip)

The build's only warning is Vite's advisory for a chunk above 500 KB.
