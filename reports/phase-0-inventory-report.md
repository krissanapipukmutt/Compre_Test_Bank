# Phase 0 Inventory Report

- Status: **passed**
- Immutable source files inventoried: **374**
- Total source size: **979042016 bytes**
- Unique stable file IDs: **374**
- Exact duplicate groups: **14**
- Text-sample duplicate groups: **4**
- Unreadable/unsupported/non-text extraction items: **9**
- Course conflict items: **41**

## Validation

- All files discovered by the defined immutable-source scan are present in `data/file-inventory.json`.
- Every source has a SHA-256 baseline for later immutability checks.
- No original academic file was edited, moved, renamed, or deleted.
- Stable file IDs derive from normalized relative paths and are unique.
- Course mappings distinguish document-content evidence from directory-context fallback.
- Uncertain mappings, duplicate candidates, and unsupported extraction cases are reported.

## Warnings carried forward

- Image-only/no-text PDFs and diagrams need visual/manual coverage where academically relevant.
- Legacy Office files and installer/archive formats remain untouched and unsupported for academic text extraction.
- BIS603/BIS604 directory-code conflicts remain explicit.
