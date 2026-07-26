# Pre-web Readiness

## Status

`ready_with_warnings`

## Decision

The academic datasets are structurally ready for web development. Medium warnings must remain visible in the product and final reports.

## Readiness checklist

- [x] Phase 0–2 JSON and relationship validation passes.
- [x] File, subject, chapter, topic, question, choice, and source references resolve.
- [x] Answer keys use stable choice IDs and survive reordering.
- [x] Review-required questions do not expose an answer.
- [x] Term 1 and Term 2 both contain subject/chapter content.
- [x] Original English examination text is retained.
- [x] Thai fields are present and technical terms are preserved.
- [x] Course-code conflicts and answer uncertainty are documented.
- [x] The UI can continue using status, confidence, and human-review warnings.

## Warnings the application must display

1. BIS603's exact code-title pairing is medium confidence.
2. `strongly_inferred` is not equivalent to source-verified.
3. `requires_human_review` questions are unscored and have no correct answer.
4. Diagram/table-dependent questions may lack their visual context in version 1.
5. English originals remain authoritative when checking Thai translation nuance.
