# Embedded-Choice Audit

## Outcome

All 105 questions were scanned. Exactly 9 source-verified candidates contain a sequence of embedded statements inside the flattened question paragraph. No additional question met the conservative ordered-marker rule, and no false positive was normalized.

| Question | Original source | Detected pattern | Statement markers | Selectable answers | Result |
| --- | --- | --- | --- | ---: | --- |
| question-comprehensive-004 | `แนวข้อสอบ.pdf` p. 1 | `letter_parenthesis_A_B_C` | A, B, C | 5 | Normalized / no review |
| question-comprehensive-006 | `แนวข้อสอบ.pdf` p. 1 | `letter_parenthesis_A_B_C` | A, B, C | 5 | Normalized / no review |
| question-comprehensive-007 | `แนวข้อสอบ.pdf` p. 1 | `letter_parenthesis_A_B_C` | A, B, C | 5 | Normalized / no review |
| question-comprehensive-008 | `แนวข้อสอบ.pdf` p. 2 | `letter_parenthesis_A_B_C` | A, B, C | 5 | Normalized / no review |
| question-comprehensive-009 | `แนวข้อสอบ.pdf` p. 2 | `letter_parenthesis_A_B_C` | A, B, C | 5 | Normalized / no review |
| question-comprehensive-010 | `แนวข้อสอบ.pdf` p. 2 | `letter_parenthesis_A_B_C` | A, B, C | 5 | Normalized / no review |
| question-comprehensive-019 | `แนวข้อสอบ.pdf` p. 2 | `letter_parenthesis_A_B_C` | A, B, C | 5 | Normalized / no review |
| question-comprehensive-020 | `แนวข้อสอบ.pdf` p. 2 | `letter_parenthesis_A_B_C` | A, B, C | 5 | Normalized / no review |
| question-comprehensive-028 | `แนวข้อสอบ.pdf` p. 4 | `source_numbered_statements_1_2_3` | 1, 2, 3 | 5 | Normalized / no review |

## Semantic finding

For all nine candidates, the embedded A/B/C—or original 1/2/3 for Q28—lines are propositions to evaluate. They are not the five selectable response choices. The existing selectable answers encode combinations such as one statement, a pair, or all statements. Replacing the five choices with the embedded lines would have changed the examination semantics and answer pointers, so the implementation instead renders:

1. normalized question stem;
2. embedded statement block in original order;
3. unchanged selectable answer choices.

Q28 is the only source-numbered case. Its original PDF uses 1/2/3; display normalization restores those source markers while retaining the prior raw extraction and its unchanged combination-answer choices.

## Detection safeguards

The reusable parser accepts sequential forms such as `A)`, `A.`, `(A)`, `1)`, and lowercase markers only when at least two ordered markers form a coherent sequence. Tests reject decimal values, SQL aliases, code parentheses, and out-of-order tokens. Data normalization is more restrictive: the nine approved IDs are verified against the cited PDF page before any structured display field is produced.

## Preservation result

- Raw English and Thai are preserved for 105/105 questions.
- Choice IDs, choice text, choice order, correct answer, acceptable answers, original answer, and final answer match the Phase 11 baseline for 105/105.
- Normalized: 9
- Display-formatted only: 0
- Ambiguous or structure-human-review: 0
- Unresolved structure IDs: none
