# Phase 3 Data Audit

Generated: 2026-07-26T11:53:18.585095+00:00

## Validation result

```text
Validation phase 2: PASS (0 errors, 0 warnings)
```

## Integrity checks

- Inventory file IDs: **374 unique**
- Subject IDs: **6/6 unique**
- Chapter IDs: **44/44 unique**
- Topic IDs: **132/132 unique**
- Glossary IDs: **132/132 unique**
- Question IDs: **105/105 unique**
- Stable answer keys resolving to choice IDs or intentionally null: **105/105**
- Invalid question/file references: **0**
- Verified-answer evidence coverage: **105/105**
- Review-required questions safely unscored: **18/18**
- Exam sets: **1**

## Source coverage

- Every immutable source inventoried: **374/374**
- Direct learning/exam evidence files selected: **71/374 (19.0%)**
- Selected evidence categories: `course_outline` 2, `examination` 1, `lecture` 66, `other_academic_material` 2
- Unselected/inventory-only categories: `archive_or_installer` 2, `course_outline` 4, `examination` 22, `exercise_or_assignment` 165, `external_link_shortcut` 3, `lecture` 58, `other_academic_material` 5, `project_or_report` 12, `source_code_or_model` 1, `summary` 18, `system_metadata` 13

Direct evidence selection favors course outlines and lecture sources over duplicate exports, student/project versions, datasets, exercises, system metadata, and installers. All unselected sources remain traceable in the inventory.

## Findings

- Critical: **0**
- High: **0**
- Medium: **4**
- Low: **1**
- Structural errors: **0**

No structural defect requires repair.
