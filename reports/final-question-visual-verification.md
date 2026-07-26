# Final Question Visual Verification

Date: 2026-07-26  
Project root: `/Users/krissanap/Document/KMUTT/COMPRE_CODEX`  
Result: **PASS after one reference-crop repair**

## Scope and baselines

- Re-verified all 105 digital questions against all 16 pages of the immutable original `แนวข้อสอบ.pdf`.
- Confirmed source SHA-256 `766e02f240ba35a58329e12970e42ee59fe70fbe01f901f883fa23bb39239f41` against `data/file-inventory.json`.
- Confirmed every question ID, source file ID, and source page against `data/question-source-map.json`.
- Re-inspected the complete rendered source pages, all nine inline visual objects, and all nine full-question reference crops.
- Scanned 48 wording-priority questions containing terms such as “following,” “shown below,” “diagram,” “table,” or their Thai equivalents.
- Separately inspected Q98 and Q99 for source-significant HTML/JavaScript formatting. Their original one-line code strings, punctuation, capitalization, and ordering remain preserved as text; neither source question contains a separate image or multiline code block.
- Did not rely on wording alone: Q22 does not contain a trigger phrase but was correctly found through the PDF embedded-object and page-layout audit.

## Final inventory

| Measure | Result |
|---|---:|
| Questions verified | 105 |
| Original pages verified | 16 |
| Wording-priority questions checked | 48 |
| Code-format priority questions checked | 2 |
| Questions with essential visual content | 9 |
| Byte-preserved embedded inline objects | 9 |
| Lossless full-question reference crops | 9 |
| Referenced production assets | 18 |
| Missing essential visuals | 0 |
| Partially readable visuals | 0 |
| Visual human-review items | 0 |
| Academic answers modified | 0 |

## Essential-visual question results

| Question | Source page | Essential content | Ownership and order | Crop/result |
|---|---:|---|---|---|
| Q21 | 3 | Distribution graph | Original embedded object; after bilingual stem and before choices | Complete and readable |
| Q22 | 3 | Goodness-of-fit table | Original embedded object; after bilingual stem and before choices | Complete and readable |
| Q23 | 3 | Regression-results table | Original embedded object; after bilingual stem and before choices | Complete and readable |
| Q24 | 3 | Boxplot and numeric axis | Original embedded object; after bilingual stem and before choices | Complete and readable |
| Q62 | 9 | EMPLOYEE data table | Original embedded object; after bilingual stem and before choices | Complete and readable |
| Q73 | 10 | Chen entity diagram | Original embedded object; after bilingual stem and before choices | Complete and readable |
| Q77 | 11 | CUSTOMER entity/table diagram | Original embedded object; after bilingual stem and before choices | Complete and readable |
| Q79 | 12 | INTERSECT relation tables | Original embedded object; after bilingual stem and before choices | Complete after reference-crop repair |
| Q80 | 12 | UNION relation tables | Original embedded object; after bilingual stem and before choices | Complete and readable |

Each embedded image object maps geometrically to exactly one source-question boundary. Its stored source page, PDF object xref, bounding box, pixel dimensions, and SHA-256 match the original. No visual is assigned to a neighboring question.

## Defect found and repaired

The second-pass manual review found that Q79’s supplemental `full-question-reference.png` ended approximately 5.7 PDF points above the bottom of the final source choice line. The essential INTERSECT table was intact, but the reference image visibly clipped the lower part of choices 4 and 5.

The crop calculation in `scripts/audit_exam_visual_integrity.py` was corrected to:

- derive the lower edge from the final word inside the exact question boundary;
- retain a small verified context margin;
- stop immediately before the next question;
- begin immediately before the current question heading, excluding content from the preceding question.

All nine reference crops were regenerated and re-inspected. Q79 now contains the complete final choice line, and Q80 begins at its own heading without Q79 content. Asset metadata and hashes were regenerated. No question wording, choice, answer, translation, explanation, answer status, or evidence field changed.

## Requirement verification

| Requirement | Result | Evidence |
|---|---|---|
| Every essential visual is present | PASS | All nine PDF embedded objects have essential inline assets |
| Every visual belongs to the correct question | PASS | One-to-one xref-to-source-boundary verification |
| No crop is cut off | PASS | Content-bound geometric check plus manual review after Q79 repair |
| No crop includes unrelated questions | PASS | Crop top/bottom checked against previous/next source content bounds |
| Visual order matches the source | PASS | Data placement, component order, unit test, and Q80 browser geometry |
| Mobile enlargement is readable | PASS | Full-screen modal, zoom, pan, Escape, focus return, mobile screenshots |
| Missing visuals trigger a blocking warning | PASS | Unit failure test and real-browser Q80 network-failure injection |
| Incomplete visual questions are excluded from scoring | PASS | `isVisualReady` scoring and mock-session tests plus static validator |
| UNION table is between stem and choices | PASS | Q80 browser test verifies heading bottom < image top < first-choice top |
| Production build contains every asset | PASS | All 18 paths, hashes, dimensions, and built copies validated |

## Responsive and accessibility verification

The route-level suite passed without unintended horizontal document overflow at:

- 320 × 568
- 360 × 800
- 375 × 667
- 390 × 844
- 412 × 915
- 667 × 375
- 844 × 390
- 768 × 1024
- 820 × 1180
- 1024 × 768
- 1280 × 800
- 1440 × 900

Dedicated diagram/table verification covered Q21 and Q80 on phone, tablet, and desktop. The source-image viewer is full-screen on mobile and supports keyboard-accessible open/close, visible controls, zoom, internal panning, Escape close, and focus restoration. English/Thai alt selection remains tested, and visual metadata does not expose answer choices.

## Validation and build results

| Gate | Result |
|---|---|
| `scripts/verify_final_question_visuals.py` | PASS — 105 questions, 16 pages, 0 errors |
| `scripts/validate_data.py --phase 8` | PASS — 0 errors, 0 warnings |
| `scripts/validate_exam_visual_integrity.py --check-build` | PASS — 0 errors, 0 warnings |
| ESLint | PASS |
| Strict TypeScript | PASS |
| Unit/integration tests | PASS — 32/32 |
| Playwright browser tests | PASS — 11/11 |
| Responsive source-image tests | PASS |
| Production Vite build | PASS |

The build retains the existing non-blocking bundle-size advisory. It does not affect asset completeness or visual integrity.

## Academic-answer preservation

No restored visual proved an answer change was required. The Phase 8 preservation validator confirms that all non-visual question data remains identical to the pre-visual-integrity checkpoint. Existing answer-evidence review statuses remain separate from this verification.

## Final disposition

All 105 questions preserve the information required by their original examination pages. There are no unresolved visual-integrity question IDs and no questions requiring human review because of visual loss.
