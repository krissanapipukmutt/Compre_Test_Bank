# Project State

- **Status:** COMPLETE_WITH_RESEARCH_WARNINGS
- **Current phase:** Complete — Phases 0 through 8
- **Current task:** none
- **Completed phases:** Phase 0, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, Phase 6, Phase 7, Phase 8
- **Last successful validation:** Final source-boundary verification passes all 105 questions across 16 pages with 0 errors; Phase 8 visual asset/provenance/checkpoint/build validation passes with 0 errors and 0 warnings; Phase 7 preservation remains green; 32/32 unit/integration tests and 11/11 browser tests pass; lint, strict type check, responsive matrix, and production build pass
- **Last Git commit:** unavailable — project root is not a Git repository
- **Last safe checkpoint:** `backups/post-final-question-visual-verification-20260726T224400+0700.tar.gz` (recoverable archive used because no Git repository exists)
- **Research outcome:** 89 flagged questions reviewed; 33 newly verified from course materials; 47 verified externally; 2 strongly supported externally; 2 probability-based recommendations; 5 unresolvable
- **Visual-integrity outcome:** 105/105 questions manually audited and independently boundary-verified against 16 original pages; 48 wording triggers and 2 code-format items rechecked; 9 essential-visual questions complete; Q79 supplemental reference-crop cutoff repaired; 9 original embedded JPEGs and 9 lossless full-question reference PNGs packaged; 0 missing, partial, or visual-review questions; 0 academic answers changed
- **Unresolved warnings:** 10 questions retain human review (Q39, Q46, Q64, Q88, Q96 and 5 unresolvable items); BIS603 mapping warning; native-speaker review recommended for long Thai distractors; production JS is 1.98 MB uncompressed / 213 KB gzip; formal screen-reader and non-Chromium certification not completed
- **Hard blockers:** none
- **Next action:** optional human adjudication of the 10 flagged items, language review, code-splitting, or deployment; no required automated project work remains

## Commands needed to resume

```bash
cd /Users/krissanap/Document/KMUTT/COMPRE_CODEX
.venv/bin/python scripts/validate_data.py --phase 8
.venv/bin/python scripts/validate_exam_visual_integrity.py
.venv/bin/python scripts/validate_external_research.py --check-links
cd web
npm run check
npm run test:e2e
npm audit --audit-level=high
```
