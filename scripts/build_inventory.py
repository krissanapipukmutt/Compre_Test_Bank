#!/usr/bin/env python3
"""Build a reproducible inventory of the immutable academic source corpus."""

from __future__ import annotations

import csv
import hashlib
import json
import mimetypes
import re
import subprocess
import sys
import unicodedata
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

try:
    from pypdf import PdfReader
except ImportError as exc:  # pragma: no cover - actionable startup failure
    raise SystemExit("pypdf is required. Run: .venv/bin/pip install pypdf==5.9.0") from exc


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = ("TERM1", "TERM2")
GENERATED_ROOTS = {
    ".git",
    ".venv",
    "data",
    "docs",
    "reports",
    "scripts",
    "web",
    "node_modules",
}
MANAGEMENT_FILES = {"AGENTS.md", "PLANS.md", "TASKS.md", "PROJECT_STATE.md", "README.md"}
COURSE_TITLES = {
    "BIS601": "Business System Analysis and Design",
    "BIS602": "Business Decision and Data Analytics",
    "BIS603": "Strategies Marketing Management",
    "BIS604": "Business Data Management",
    "BIS605": "Software Development Technologies for Digital Business",
    "BIS606": "Digital Infrastructure and Cyber Security System",
}
TITLE_ALIASES = {
    "BIS601": (
        "business system analysis and design",
        "business systems analysis and design",
    ),
    "BIS602": ("business decision and data analytics",),
    "BIS603": (
        "strategies marketing management",
        "strategic marketing management",
        "strategy marketing management",
    ),
    "BIS604": (
        "business data management",
        "business database management",
        "business db management",
    ),
    "BIS605": ("software development technologies for digital business",),
    "BIS606": ("digital infrastructure and cyber security system",),
}
TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".csv",
    ".html",
    ".htm",
    ".css",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".php",
    ".json",
    ".ipynb",
    ".url",
    ".xml",
    ".drawio",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
ARCHIVE_EXTENSIONS = {".zip", ".dmg"}
OFFICE_XML_EXTENSIONS = {".docx", ".pptx", ".xlsx"}
LEGACY_OFFICE_EXTENSIONS = {".doc", ".xls", ".ppt"}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def source_paths() -> list[Path]:
    paths: list[Path] = []
    for directory in SOURCE_DIRS:
        source_root = ROOT / directory
        if source_root.exists():
            paths.extend(path for path in source_root.rglob("*") if path.is_file())
    for path in ROOT.iterdir():
        if (
            path.is_file()
            and path.name not in MANAGEMENT_FILES
            and path.name != ".DS_Store"
            and path.suffix.lower() in {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt"}
        ):
            paths.append(path)
    # Root .DS_Store was present in the initial corpus and remains part of inventory coverage.
    root_metadata = ROOT / ".DS_Store"
    if root_metadata.exists():
        paths.append(root_metadata)
    return sorted(set(paths), key=lambda item: relative(item).casefold())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_file_id(rel_path: str) -> str:
    token = hashlib.sha256(unicodedata.normalize("NFC", rel_path).encode("utf-8")).hexdigest()[:16]
    return f"file-{token}"


def read_text_file(path: Path, limit: int = 300_000) -> tuple[str, str, str]:
    raw = path.read_bytes()[:limit]
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding), "readable", f"text:{encoding}"
        except UnicodeDecodeError:
            continue
    return "", "unreadable", "text_decode_failed"


def xml_text(blob: bytes) -> str:
    root = ElementTree.fromstring(blob)
    parts: list[str] = []
    for node in root.iter():
        if node.text and node.tag.rsplit("}", 1)[-1] in {"t", "v", "f", "p"}:
            parts.append(node.text)
    return "\n".join(parts)


def extract_docx(path: Path) -> tuple[str, str, str]:
    with zipfile.ZipFile(path) as archive:
        names = sorted(
            name
            for name in archive.namelist()
            if name == "word/document.xml"
            or name.startswith("word/header")
            or name.startswith("word/footer")
        )
        text = "\n".join(xml_text(archive.read(name)) for name in names)
    return text, "readable", "docx_xml"


def slide_number(name: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", name)
    return int(match.group(1)) if match else 0


def extract_pptx(path: Path, max_slides: int = 12) -> tuple[str, str, str]:
    with zipfile.ZipFile(path) as archive:
        names = sorted(
            (name for name in archive.namelist() if re.search(r"ppt/slides/slide\d+\.xml$", name)),
            key=slide_number,
        )[:max_slides]
        text = "\n".join(xml_text(archive.read(name)) for name in names)
    return text, "readable", f"pptx_xml:{len(names)}_slides_sampled"


def extract_xlsx(path: Path, max_sheets: int = 5) -> tuple[str, str, str]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        shared: list[str] = []
        if "xl/sharedStrings.xml" in names:
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.iter():
                if item.tag.rsplit("}", 1)[-1] == "si":
                    shared.append(" ".join((node.text or "") for node in item.iter() if node.tag.rsplit("}", 1)[-1] == "t"))
        sheets = sorted(
            (name for name in names if re.search(r"xl/worksheets/sheet\d+\.xml$", name))
        )[:max_sheets]
        parts = list(shared[:5000])
        for name in sheets:
            parts.append(xml_text(archive.read(name)))
    return "\n".join(parts), "readable", f"xlsx_xml:{len(sheets)}_sheets_sampled"


def extract_pdf(path: Path, max_pages: int = 8) -> tuple[str, str, str]:
    reader = PdfReader(str(path), strict=False)
    if reader.is_encrypted:
        try:
            unlocked = reader.decrypt("")
        except Exception:
            unlocked = 0
        if not unlocked:
            return "", "encrypted", "pdf_encrypted"
    page_count = len(reader.pages)
    parts: list[str] = []
    for page in reader.pages[:max_pages]:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    text = "\n".join(parts)
    status = "readable" if text.strip() else "image_or_no_extractable_text"
    return text, status, f"pdf:{page_count}_pages:{min(page_count, max_pages)}_sampled"


def extract_archive(path: Path) -> tuple[str, str, str]:
    if path.suffix.lower() != ".zip":
        return "", "unsupported", "disk_image_not_opened"
    with zipfile.ZipFile(path) as archive:
        corrupt_member = archive.testzip()
        if corrupt_member:
            return "", "corrupt", f"zip_crc_failed:{corrupt_member}"
        return "\n".join(archive.namelist()[:500]), "archive_readable", "zip_directory_only"


def extract_sample(path: Path) -> tuple[str, str, str]:
    suffix = path.suffix.lower()
    try:
        if suffix == ".pdf":
            return extract_pdf(path)
        if suffix == ".docx":
            return extract_docx(path)
        if suffix == ".pptx":
            return extract_pptx(path)
        if suffix == ".xlsx":
            return extract_xlsx(path)
        if suffix in TEXT_EXTENSIONS or path.name == "Exercise 4 ERD":
            return read_text_file(path)
        if suffix in IMAGE_EXTENSIONS:
            return "", "binary_readable", "image_not_ocr_processed"
        if suffix in ARCHIVE_EXTENSIONS:
            return extract_archive(path)
        if suffix in LEGACY_OFFICE_EXTENSIONS:
            return "", "unsupported", "legacy_office_format"
        if path.name == ".DS_Store":
            return "", "ignored_metadata", "macos_metadata"
        return "", "unsupported", "no_local_extractor"
    except (zipfile.BadZipFile, ElementTree.ParseError) as exc:
        return "", "corrupt", f"{type(exc).__name__}:{exc}"
    except Exception as exc:  # Keep the corpus inventory progressing and report the exact failure.
        return "", "unreadable", f"{type(exc).__name__}:{exc}"


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"\s+", " ", value).strip()


def content_codes(text: str) -> list[str]:
    return sorted(set(re.findall(r"\bBIS\s*[-_]?\s*(60[1-6])\b", text, re.IGNORECASE)))


def directory_codes(rel_path: str) -> list[str]:
    return sorted(set(re.findall(r"\bBIS\s*[-_]?\s*(60[1-6])\b", rel_path, re.IGNORECASE)))


def detect_course(rel_path: str, text: str) -> tuple[str | None, str | None, str, list[str]]:
    normalized = normalize_text(text)
    direct_codes = [f"BIS{digits}" for digits in content_codes(text)]
    title_codes = [
        code for code, aliases in TITLE_ALIASES.items() if any(alias in normalized for alias in aliases)
    ]
    confirmed = sorted(set(direct_codes + title_codes))
    path_codes = [f"BIS{digits}" for digits in directory_codes(rel_path)]
    notes: list[str] = []

    if len(confirmed) == 1:
        code = confirmed[0]
        basis = "document_content"
    elif len(confirmed) > 1:
        code = confirmed[0] if len(set(confirmed).intersection(path_codes)) == 1 else None
        basis = "document_content_conflict"
        notes.append(f"multiple course codes/titles detected in content: {', '.join(confirmed)}")
    elif len(path_codes) == 1:
        code = path_codes[0]
        basis = "directory_context_unverified"
        notes.append("course code not detected in extracted sample; retained as directory context only")
    elif len(path_codes) > 1:
        code = None
        basis = "directory_context_conflict"
        notes.append(f"multiple course codes in directory context: {', '.join(path_codes)}")
    else:
        code = None
        basis = "unclassified"
        notes.append("no course code or recognized title detected")

    title = COURSE_TITLES.get(code) if code else None
    return code, title, basis, notes


def detect_term(rel_path: str) -> str | None:
    first = rel_path.split("/", 1)[0].upper()
    if first == "TERM1":
        return "term-1"
    if first == "TERM2":
        return "term-2"
    return None


def category(rel_path: str, suffix: str, text: str) -> str:
    haystack = normalize_text(f"{rel_path} {text[:5000]}")
    if "/สอบ/" in f"/{rel_path}" or "/test/" in f"/{rel_path.casefold()}" or "แนวข้อสอบ" in rel_path:
        return "examination"
    if any(token in haystack for token in ("syllabus", "course outline", "courseoutline", "outlinebis")):
        return "course_outline"
    if any(token in rel_path.casefold() for token in ("/lecture/", "/lacture/", "/leature/")):
        return "lecture"
    if "summary" in rel_path.casefold() or "/สรุป/" in f"/{rel_path}":
        return "summary"
    if any(token in rel_path.casefold() for token in ("/exercise/", "/exersice/", "/work/", "homework", "assignment")):
        return "exercise_or_assignment"
    if "project" in rel_path.casefold() or "report" in rel_path.casefold():
        return "project_or_report"
    if suffix in {".ipynb", ".html", ".css", ".js", ".ts", ".tsx", ".php", ".drawio"}:
        return "source_code_or_model"
    if suffix in {".csv", ".xlsx", ".json"}:
        return "dataset_or_workbook"
    if suffix in ARCHIVE_EXTENSIONS:
        return "archive_or_installer"
    if suffix in IMAGE_EXTENSIONS:
        return "image_or_diagram"
    if rel_path.endswith(".url"):
        return "external_link_shortcut"
    if rel_path.endswith(".DS_Store"):
        return "system_metadata"
    return "other_academic_material"


def apparent_version(filename: str) -> str | None:
    stem = Path(filename).stem
    tokens: list[str] = []
    patterns = (
        r"\b(?:old|backup|final|solution|ans(?:wer)?|send)\b",
        r"\bv(?:ersion)?\s*\d+\b",
        r"\(\d+\)",
        r"_\d+$",
        r"\b20\d{2}(?:[-_]\d+)?\b",
    )
    for pattern in patterns:
        tokens.extend(match.group(0) for match in re.finditer(pattern, stem, re.IGNORECASE))
    return ", ".join(tokens) if tokens else None


def canonical_stem(filename: str) -> str:
    stem = unicodedata.normalize("NFKC", Path(filename).stem).casefold()
    stem = re.sub(r"\b(?:old|backup|final|solution|ans(?:wer)?|send|copy)\b", " ", stem)
    stem = re.sub(r"\bv(?:ersion)?\s*\d+\b|\(\d+\)|_\d+$", " ", stem)
    stem = re.sub(r"\b20\d{2}(?:[-_]\d+)?\b", " ", stem)
    return re.sub(r"[^a-z0-9\u0e00-\u0e7f]+", " ", stem).strip()


def mime_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    if guessed:
        return guessed
    try:
        result = subprocess.run(
            ["file", "-b", "--mime-type", str(path)],
            check=False,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or "application/octet-stream"
    except OSError:
        return "application/octet-stream"


def markdown_table(rows: list[list[str]], headers: list[str]) -> str:
    def safe(value: Any) -> str:
        return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")

    result = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    result.extend("| " + " | ".join(safe(cell) for cell in row) + " |" for row in rows)
    return "\n".join(result)


def write_outputs(records: list[dict[str, Any]], generated_at: str) -> None:
    hash_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    text_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    version_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        hash_groups[record["sha256"]].append(record)
        if record["sample_text_fingerprint"]:
            text_groups[record["sample_text_fingerprint"]].append(record)
        canonical = canonical_stem(record["filename"])
        if canonical:
            version_groups[f'{record["detected_subject_code"]}|{canonical}'].append(record)

    exact_groups = [group for group in hash_groups.values() if len(group) > 1]
    text_duplicate_groups = [
        group
        for group in text_groups.values()
        if len(group) > 1 and len({item["sha256"] for item in group}) > 1
    ]
    version_candidate_groups = [
        group
        for group in version_groups.values()
        if len(group) > 1 and len({item["sha256"] for item in group}) > 1
    ]

    exact_ids = {item["file_id"] for group in exact_groups for item in group}
    text_ids = {item["file_id"] for group in text_duplicate_groups for item in group}
    version_ids = {item["file_id"] for group in version_candidate_groups for item in group}
    for record in records:
        if record["file_id"] in exact_ids:
            record["duplicate_status"] = "exact_duplicate"
        elif record["file_id"] in text_ids:
            record["duplicate_status"] = "sample_text_duplicate"
        elif record["file_id"] in version_ids:
            record["duplicate_status"] = "possible_version"
        else:
            record["duplicate_status"] = "unique"

    payload = {
        "schema_version": "1.0.0",
        "generated_at": generated_at,
        "inventory_scope": {
            "source_directories": list(SOURCE_DIRS),
            "root_academic_files": True,
            "generated_directories_excluded": sorted(GENERATED_ROOTS),
            "management_files_excluded": sorted(MANAGEMENT_FILES),
        },
        "source_file_count": len(records),
        "files": records,
    }
    (ROOT / "data/file-inventory.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    counts = Counter(record["readable_status"] for record in records)
    category_counts = Counter(record["document_category"] for record in records)
    course_counts = Counter(record["detected_subject_code"] or "unclassified" for record in records)
    inventory_rows = [
        [
            record["file_id"],
            record["relative_path"],
            record["size_bytes"],
            record["detected_term"],
            record["detected_subject_code"],
            record["document_category"],
            record["readable_status"],
            record["duplicate_status"],
        ]
        for record in records
    ]
    inventory_md = f"""# File Inventory

Generated: {generated_at}

This inventory covers the {len(records)} immutable source files that existed under `TERM1/`, `TERM2/`, and the root academic-file scope. Generated project directories and management files are deliberately excluded to avoid a circular inventory.

## Summary

- Source files: {len(records)}
- Total bytes: {sum(record["size_bytes"] for record in records)}
- Readability: {", ".join(f"`{key}` {value}" for key, value in sorted(counts.items()))}
- Categories: {", ".join(f"`{key}` {value}" for key, value in sorted(category_counts.items()))}
- Course mappings: {", ".join(f"`{key}` {value}" for key, value in sorted(course_counts.items()))}
- Exact duplicate groups: {len(exact_groups)}
- Sample-text duplicate groups: {len(text_duplicate_groups)}
- Possible version groups: {len(version_candidate_groups)}

Course classification uses extracted document content when the course code/title is visible. Directory context is retained only as an explicitly unverified fallback.

## Files

{markdown_table(inventory_rows, ["File ID", "Relative path", "Bytes", "Term", "Course", "Category", "Readable", "Duplicate"])}
"""
    (ROOT / "docs/00-file-inventory.md").write_text(inventory_md, encoding="utf-8")

    by_code: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_code[record["detected_subject_code"] or "unclassified"].append(record)
    mapping_rows: list[list[str]] = []
    for code, items in sorted(by_code.items()):
        content_count = sum(item["classification_basis"] == "document_content" for item in items)
        terms = ", ".join(sorted({item["detected_term"] or "unknown" for item in items}))
        title = COURSE_TITLES.get(code, "Unclassified")
        mapping_rows.append([code, title, terms, str(len(items)), str(content_count)])
    mapping_md = f"""# Course Mapping

Course titles below are recognized from supplied document content. Counts distinguish direct content confirmation from directory-context fallback. Conflicts remain in `reports/course-code-conflicts.md`.

{markdown_table(mapping_rows, ["Course code", "Normalized title", "Term", "Files", "Content-confirmed files"])}

## Interpretation notes

- `BIS603` is used by the supplied strategic/marketing materials.
- `BIS604` is used by the supplied business data/database management materials.
- The directory named `BIS603_BIS604 Bussiness Data Management` is not silently normalized; individual documents are classified by extracted content and conflicting context is reported.
- Files without visible code/title evidence retain an unverified directory context or remain unclassified.
"""
    (ROOT / "docs/01-course-mapping.md").write_text(mapping_md, encoding="utf-8")

    def group_lines(groups: list[list[dict[str, Any]]]) -> str:
        if not groups:
            return "None.\n"
        sections: list[str] = []
        for number, group in enumerate(groups, 1):
            sections.append(f"### Group {number}\n")
            sections.extend(f"- `{item['file_id']}` — `{item['relative_path']}`" for item in group)
            sections.append("")
        return "\n".join(sections)

    duplicate_md = f"""# Duplicate and Version Candidates

## Exact-content duplicates

{group_lines(exact_groups)}
## Matching extracted-text samples with different bytes

{group_lines(text_duplicate_groups)}
## Filename-based version candidates

{group_lines(version_candidate_groups)}
No file was removed or renamed. Version candidates are review signals, not assertions that a file is obsolete.
"""
    (ROOT / "reports/duplicate-files.md").write_text(duplicate_md, encoding="utf-8")

    unreadable = [
        record
        for record in records
        if record["readable_status"]
        in {"encrypted", "corrupt", "unreadable", "unsupported", "image_or_no_extractable_text"}
    ]
    unreadable_rows = [
        [item["file_id"], item["relative_path"], item["readable_status"], item["readability_note"]]
        for item in unreadable
    ]
    unreadable_md = f"""# Unreadable, Unsupported, and Non-text Sources

These {len(unreadable)} items require either visual/manual review or a format-specific local extractor. `image_or_no_extractable_text` does not imply corruption.

{markdown_table(unreadable_rows, ["File ID", "Relative path", "Status", "Reason"])}
"""
    (ROOT / "reports/unreadable-files.md").write_text(unreadable_md, encoding="utf-8")

    conflicts = [
        record
        for record in records
        if "conflict" in record["classification_basis"]
        or (
            record["relative_path"].startswith("TERM2/BIS603_BIS604")
            and record["detected_subject_code"] != "BIS604"
        )
    ]
    conflict_rows = [
        [
            item["file_id"],
            item["relative_path"],
            item["detected_subject_code"],
            item["classification_basis"],
            "; ".join(item["notes"]),
        ]
        for item in conflicts
    ]
    conflicts_md = f"""# Course-code Conflicts

The source directory `TERM2/BIS603_BIS604 Bussiness Data Management` embeds two codes, while supplied course-outline and database materials indicate BIS604. No uncertain code has been silently changed.

{markdown_table(conflict_rows, ["File ID", "Relative path", "Detected course", "Basis", "Notes"])}
"""
    (ROOT / "reports/course-code-conflicts.md").write_text(conflicts_md, encoding="utf-8")

    status = "passed" if records and len({item["file_id"] for item in records}) == len(records) else "failed"
    report = f"""# Phase 0 Inventory Report

- Status: **{status}**
- Immutable source files inventoried: **{len(records)}**
- Total source size: **{sum(item["size_bytes"] for item in records)} bytes**
- Unique stable file IDs: **{len({item["file_id"] for item in records})}**
- Exact duplicate groups: **{len(exact_groups)}**
- Text-sample duplicate groups: **{len(text_duplicate_groups)}**
- Unreadable/unsupported/non-text extraction items: **{len(unreadable)}**
- Course conflict items: **{len(conflicts)}**

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
"""
    (ROOT / "reports/phase-0-inventory-report.md").write_text(report, encoding="utf-8")


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat()
    paths = source_paths()
    records: list[dict[str, Any]] = []
    for index, path in enumerate(paths, 1):
        rel_path = relative(path)
        text, readable_status, readability_note = extract_sample(path)
        normalized = normalize_text(text)
        code, title, basis, notes = detect_course(rel_path, text)
        file_hash = sha256(path)
        record = {
            "file_id": stable_file_id(rel_path),
            "relative_path": rel_path,
            "filename": path.name,
            "extension": path.suffix.lower() or None,
            "mime_type": mime_type(path),
            "size_bytes": path.stat().st_size,
            "sha256": file_hash,
            "detected_term": detect_term(rel_path),
            "detected_subject_code": code,
            "detected_subject_title": title,
            "classification_basis": basis,
            "document_category": category(rel_path, path.suffix.lower(), text),
            "apparent_version": apparent_version(path.name),
            "readable_status": readable_status,
            "readability_note": readability_note,
            "duplicate_status": "pending",
            "sample_text_fingerprint": (
                hashlib.sha256(normalized[:30_000].encode("utf-8")).hexdigest()
                if len(normalized) >= 80
                else None
            ),
            "notes": notes,
        }
        records.append(record)
        if index % 25 == 0 or index == len(paths):
            print(f"Inventoried {index}/{len(paths)}: {rel_path}", flush=True)
    write_outputs(records, generated_at)
    print(f"Wrote Phase 0 inventory for {len(records)} source files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

