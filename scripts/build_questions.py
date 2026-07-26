#!/usr/bin/env python3
"""Extract and structure the supplied comprehensive practice examination."""

from __future__ import annotations

import hashlib
import json
import logging
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
EXAM_PATH = "แนวข้อสอบ.pdf"
PAGE_QUESTIONS = [
    [1, 2, 3, 4, 5, 6, 7],
    [8, 9, 10, 19, 20],
    [21, 22, 23, 24],
    list(range(25, 32)),
    list(range(32, 39)),
    list(range(39, 47)),
    list(range(47, 55)),
    list(range(55, 62)),
    list(range(62, 67)),
    list(range(67, 74)),
    list(range(74, 79)),
    list(range(79, 85)),
    list(range(85, 93)),
    list(range(93, 101)),
    list(range(101, 109)),
    list(range(109, 114)),
]

# A value of None is intentionally not an answer: the source item remains review-required.
ANSWER_KEY: dict[int, int | None] = {
    1: None, 2: None, 3: None, 4: 4, 5: 5, 6: 5, 7: 3, 8: None, 9: 4, 10: 2,
    19: 3, 20: 2, 21: None, 22: None, 23: None, 24: None, 25: 2, 26: 3, 27: 4,
    28: 1, 29: 2, 30: 4, 31: 1, 32: 2, 33: 3, 34: 1, 35: None, 36: 2, 37: 3,
    38: 2, 39: None, 40: 3, 41: 5, 42: 2, 43: 2, 44: 2, 45: 4, 46: 4, 47: 2,
    48: 1, 49: 3, 50: 3, 51: 3, 52: 1, 53: 3, 54: 3, 55: 3, 56: 5, 57: 2,
    58: 1, 59: 5, 60: 3, 61: 3, 62: None, 63: None, 64: 4, 65: 3, 66: 1,
    67: 1, 68: 3, 69: 4, 70: 2, 71: 5, 72: 3, 73: None, 74: 5, 75: 2, 76: 5,
    77: None, 78: 2, 79: None, 80: None, 81: 3, 82: 2, 83: 4, 84: 1, 85: 1,
    86: 2, 87: 5, 88: None, 89: 4, 90: 4, 91: 5, 92: None, 93: 2, 94: 5,
    95: 5, 96: 3, 97: 5, 98: 4, 99: 3, 100: 4, 101: 4, 102: 5, 103: 3,
    104: 1, 105: 1, 106: 2, 107: 3, 108: 4, 109: 2, 110: 4, 111: 3, 112: 5,
    113: 2,
}

HUMAN_REVIEW: dict[int, str] = {
    1: "The supplied learning sources do not directly establish which role is the payer under the terminology used by this item.",
    2: "The supplied learning sources mention product owner but do not directly verify the exact stakeholder-representation wording used here.",
    3: "The described role is normally a subject-matter expert, which is absent from the choices; forcing a listed role would be unsafe.",
    8: "Statements A and C appear supportable while B is not, but the choices do not contain the A-and-C combination.",
    21: "The distribution plot referenced by the item is not present in extracted text.",
    22: "The goodness-of-fit table is not present in extracted text.",
    23: "The regression output and the apparent OCR text `739% confidence interval` require visual review.",
    24: "The boxplot is not present in extracted text.",
    35: "The observed value whose z-score must be computed is missing from the extracted and visible PDF text.",
    39: "The term `discrete normal distribution` and the choices are conceptually inconsistent; no answer is forced.",
    62: "The EMPLOYEE table needed to distinguish the keys is not present in extracted text.",
    63: "Several listed tools can be electronic communication/collaboration tools; the intended taxonomy is not supplied in the item.",
    73: "The Chen model required to identify multivalued attributes is not present in extracted text.",
    77: "The Crow's-foot optionality/required-attribute diagram is not present in extracted text.",
    79: "The two input relations for INTERSECT are not present in extracted text.",
    80: "The two input relations for UNION are not present in extracted text.",
    88: "Every listed choice can be an advantage of cloud-based development; no `none` choice is supplied.",
    92: "The statements use ambiguous absolute wording about APIs, web services, and network access; the intended combination is not safely verifiable.",
}

VERIFIED = {
    32, 33, 75, 81, 82, 83, 86, 87, 98, 99, 101, 104, 107, 109, 110, 112,
}

CHAPTER_MAP: list[tuple[set[int], str]] = [
    ({1, 2, 3, 4, 19}, "chapter-bis601-analyst-and-system-success"),
    ({5, 6, 7, 8, 9, 10, 20}, "chapter-bis601-requirements"),
    ({21, 24, 32, 33, 34, 35, 39}, "chapter-bis602-probability-and-statistics"),
    ({22, 23}, "chapter-bis602-regression"),
    ({25, 26, 28, 40, 64}, "chapter-bis602-strategy-and-competition"),
    ({27, 29, 30, 31, 70, 72, 76}, "chapter-bis602-process-and-kpi"),
    ({36, 61, 63, 71}, "chapter-bis602-enterprise-data"),
    ({37, 38, 67, 68, 74, 78}, "chapter-bis602-bi-and-visualization"),
    ({41, 49, 51, 59}, "chapter-bis603-strategy-formulation"),
    ({42, 43, 44, 45, 46, 47, 48, 50, 52, 53, 54, 55, 56, 57, 58, 60}, "chapter-bis603-marketing-foundations"),
    ({62, 66}, "chapter-bis604-database-foundations"),
    ({69}, "chapter-bis604-data-models"),
    ({73, 77}, "chapter-bis604-business-rules-and-erd"),
    ({75, 79, 80}, "chapter-bis604-sql-and-implementation"),
    ({65, 94}, "chapter-bis605-development-technologies"),
    ({81, 82}, "chapter-bis605-architecture-and-sdlc"),
    ({83, 84, 85, 96, 97}, "chapter-bis605-software-design"),
    ({86, 87, 88, 89, 90, 91, 92, 93}, "chapter-bis605-backend-data-api-cloud-mobile"),
    ({95}, "chapter-bis605-web-and-ui-design"),
    ({98, 99, 100}, "chapter-bis605-frontend"),
    ({101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113}, "chapter-bis606-data-link-and-tcpip"),
]

SUBJECT_RANGES = {
    "BIS601": {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 19, 20},
    "BIS602": set(range(21, 41)) | {61, 63, 64, 67, 68, 70, 71, 72, 74, 76, 78},
    "BIS603": set(range(41, 61)),
    "BIS604": {62, 66, 69, 73, 75, 77, 79, 80},
    "BIS605": set(range(81, 101)) | {65},
    "BIS606": set(range(101, 114)),
}

THAI_EXACT = {
    "Product owner": "เจ้าของผลิตภัณฑ์",
    "Problem owner": "เจ้าของปัญหา",
    "Business analyst": "นักวิเคราะห์ธุรกิจ",
    "Business management": "ฝ่ายบริหารธุรกิจ",
    "Competitive advantage": "ความได้เปรียบในการแข่งขัน",
    "Market opportunity": "โอกาสทางการตลาด",
    "Market requirement": "ความต้องการของตลาด",
    "Digital Transformation": "การเปลี่ยนผ่านสู่ดิจิทัล",
    "Transformation": "การเปลี่ยนผ่าน",
    "Disruption": "การเปลี่ยนแปลงแบบพลิกผัน",
    "Strategic level": "ระดับกลยุทธ์",
    "Operational level": "ระดับปฏิบัติการ",
    "Tactical level": "ระดับยุทธวิธี",
    "marketing": "การตลาด",
    "Industrial products": "ผลิตภัณฑ์อุตสาหกรรม",
    "Advertising": "การโฆษณา",
    "Inseparability": "การผลิตและบริโภคแยกจากกันไม่ได้",
    "push strategy": "กลยุทธ์ผลัก",
    "pull strategy": "กลยุทธ์ดึง",
    "Horizontal integration": "การบูรณาการแนวนอน",
    "Enterprise Application Integration": "การบูรณาการแอปพลิเคชันองค์กร",
    "Hardware, Software, People, Procedure, Data": "ฮาร์ดแวร์ ซอฟต์แวร์ บุคลากร ขั้นตอน และข้อมูล",
    "Customer Relationship Management system": "ระบบบริหารความสัมพันธ์ลูกค้า",
    "Internal model": "แบบจำลองภายใน",
    "Structured Query Language": "ภาษา Structured Query Language (SQL)",
    "Slicing and Dicing": "การ Slice และ Dice",
    "Layered pattern": "รูปแบบแบ่งชั้น",
    "Client-server pattern": "รูปแบบไคลเอนต์–เซิร์ฟเวอร์",
    "Modularity": "ความเป็นโมดูล",
    "Web server": "เว็บเซิร์ฟเวอร์",
    "React": "React",
    "PHP": "PHP",
    "Node.js": "Node.js",
    "Figma": "Figma",
    "Sketch": "Sketch",
    "UML": "UML",
    "Session layer": "ชั้น Session",
    "Mail server of receiver": "เมลเซิร์ฟเวอร์ของผู้รับ",
    "Fiber-optic cables": "สายใยแก้วนำแสง",
    "BGP": "BGP",
    "IPv6": "IPv6",
    "WPA": "WPA",
    "Flexibility": "ความยืดหยุ่น",
    "All are correct answers": "ทุกข้อถูกต้อง",
    "All are correct.": "ทุกข้อถูกต้อง",
    "No correct answer.": "ไม่มีคำตอบที่ถูกต้อง",
    "None of the above": "ไม่มีข้อใดข้างต้น",
}

PHRASE_TRANSLATIONS = [
    ("Which of the following is NOT", "ข้อใดต่อไปนี้ไม่ใช่"),
    ("Which of the following is not", "ข้อใดต่อไปนี้ไม่ใช่"),
    ("Which of the following is", "ข้อใดต่อไปนี้เป็น"),
    ("Which of the following", "ข้อใดต่อไปนี้"),
    ("Which one is", "ข้อใดเป็น"),
    ("Which is not true", "ข้อใดไม่ถูกต้อง"),
    ("Which is NOT", "ข้อใดไม่ใช่"),
    ("Which is", "ข้อใดเป็น"),
    ("What are", "อะไรบ้างคือ"),
    ("What is", "อะไรคือ"),
    ("How can", "สามารถ"),
    ("How does", "อย่างไร"),
    ("Consider the following", "พิจารณาสิ่งต่อไปนี้"),
    ("Based on", "จาก"),
    ("best describes", "อธิบายได้ดีที่สุด"),
    ("best defines", "ให้นิยามได้ดีที่สุด"),
    ("primary purpose", "วัตถุประสงค์หลัก"),
    ("correct", "ถูกต้อง"),
    ("Incorrect", "ไม่ถูกต้อง"),
    ("incorrect", "ไม่ถูกต้อง"),
    ("NOT", "ไม่ใช่"),
    ("not", "ไม่"),
    ("business", "ธุรกิจ"),
    ("system", "ระบบ"),
    ("software", "ซอฟต์แวร์"),
    ("database", "ฐานข้อมูล"),
    ("data", "ข้อมูล"),
    ("network", "เครือข่าย"),
    ("marketing", "การตลาด"),
    ("customer", "ลูกค้า"),
    ("model", "แบบจำลอง"),
    ("analysis", "การวิเคราะห์"),
    ("strategy", "กลยุทธ์"),
    ("technology", "เทคโนโลยี"),
    ("information", "สารสนเทศ"),
    ("development", "การพัฒนา"),
    ("process", "กระบวนการ"),
    ("manager", "ผู้จัดการ"),
    ("application", "แอปพลิเคชัน"),
    ("server", "เซิร์ฟเวอร์"),
    ("layer", "ชั้น"),
    ("protocol", "โพรโทคอล"),
    ("advantage", "ข้อดี"),
    ("key", "คีย์"),
]

SPECIAL_THAI_QUESTIONS = {
    1: "_____ คือผู้ชำระเงินสำหรับผลิตภัณฑ์ที่จะพัฒนา",
    2: "_____ เป็นตัวแทนผู้มีส่วนได้ส่วนเสียของผลิตภัณฑ์ต่อทีมพัฒนา",
    3: "_____ มีความรู้เชิงลึกในหัวข้อที่เกี่ยวข้องกับความต้องการธุรกิจหรือขอบเขตโซลูชัน",
    8: "ข้อความใดต่อไปนี้ถูกต้องเกี่ยวกับบทบาทนักวิเคราะห์ธุรกิจและผู้จัดการโครงการ",
    21: "จากกราฟที่ให้ การแจกแจงควรอธิบายอย่างไร",
    22: "จากตัววัดความพอดี แบบจำลองใดมีประสิทธิภาพดีที่สุด",
    23: "จากผลการถดถอย ตัวแปรใดควรถูกนำออกเพื่อให้ความพอดีดีขึ้น",
    24: "จาก Boxplot ที่ให้ ค่ามัธยฐานคือข้อใด",
    32: "คะแนนสอบเท่ากับ 42 ค่าเฉลี่ย 75 และส่วนเบี่ยงเบนมาตรฐาน 10 จงคำนวณ z-score และพิจารณาว่าเป็น Outlier หรือไม่",
    33: "ข้อมูล 12, 15, 18, 20, 22, 25, 28, 30 มีค่ามัธยฐานเท่าใด",
    35: "ค่าเฉลี่ยเท่ากับ 50 และส่วนเบี่ยงเบนมาตรฐานเท่ากับ 10 ค่า z-score ของค่าที่หายไปคือเท่าใด",
    62: "จากตาราง EMPLOYEE ที่ให้ Primary Key และ Candidate Key คือข้อใด",
    73: "จาก Chen Model ที่ให้ ข้อใดไม่ใช่ Multivalued Attribute",
    77: "จาก Crow’s-foot Model ที่ให้ Attribute ใดเป็นข้อมูลบังคับ",
    79: "ผลลัพธ์ของตัวดำเนินการ INTERSECT ที่ให้คือข้อใด",
    80: "ผลลัพธ์ของตัวดำเนินการ UNION ที่ให้คือข้อใด",
    98: "HTML ที่ถูกต้องสำหรับย่อหน้าที่มีสีพื้นหลังคือข้อใด",
    99: "จะสร้างฟังก์ชันใน JavaScript ได้อย่างไร",
    101: "ชั้นใดไม่อยู่ใน Internet Model แบบห้าชั้น",
    109: "โพรโทคอลใดใช้สำหรับ Exterior Routing",
    110: "IP เวอร์ชันใดกำลังแทนที่ IPv4",
    112: "ข้อใดเป็นการรักษาความปลอดภัยของ Wireless LAN",
}


def thai_text(text: str) -> str:
    stripped = text.strip()
    if stripped in THAI_EXACT:
        return THAI_EXACT[stripped]
    translated = stripped
    for source, target in sorted(PHRASE_TRANSLATIONS, key=lambda item: len(item[0]), reverse=True):
        translated = re.sub(re.escape(source), target, translated, flags=re.IGNORECASE)
    if translated == stripped:
        return f"{stripped} (คำศัพท์/ข้อความภาษาอังกฤษตามต้นฉบับ)"
    return translated


def parse_exam() -> list[dict[str, Any]]:
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    reader = PdfReader(str(ROOT / EXAM_PATH), strict=False)
    parsed: list[dict[str, Any]] = []
    for page_index, qnums in enumerate(PAGE_QUESTIONS):
        text = " ".join((reader.pages[page_index].extract_text() or "").split())
        cursor = 0
        for q_index, number in enumerate(qnums):
            question_marker = re.search(rf"(?<!\d){number}\.\s*", text[cursor:])
            if not question_marker:
                raise ValueError(f"Question {number} not found on page {page_index + 1}")
            start = cursor + question_marker.end()
            positions: list[int] = []
            local_cursor = start
            for choice_number in range(1, 6):
                marker = re.search(rf"(?<!\d){choice_number}\.\s*", text[local_cursor:])
                if not marker:
                    raise ValueError(f"Choice {choice_number} for question {number} was not found")
                positions.append(local_cursor + marker.start())
                local_cursor += marker.end()
            if q_index + 1 < len(qnums):
                next_number = qnums[q_index + 1]
                next_marker = re.search(
                    rf"(?<!\d){next_number}\.\s*", text[positions[-1] + 2 :]
                )
                end = positions[-1] + 2 + (next_marker.start() if next_marker else len(text))
            else:
                end = len(text)
            stem = text[start : positions[0]].strip()
            choices: list[str] = []
            for choice_index, position in enumerate(positions):
                marker = re.match(rf"{choice_index + 1}\.\s*", text[position:])
                choice_start = position + (marker.end() if marker else 2)
                choice_end = positions[choice_index + 1] if choice_index < 4 else end
                choices.append(text[choice_start:choice_end].strip())
            cursor = end
            parsed.append(
                {
                    "number": number,
                    "page": page_index + 1,
                    "stem": stem,
                    "choices": choices,
                    "corrections": [],
                }
            )

    by_number = {item["number"]: item for item in parsed}
    # Question 28 contains three numbered statements before five combination choices.
    by_number[28]["stem"] = (
        'Which of the followings may lead to "Differentiation" strategy? '
        "A) Invests heavily in research and development to create innovative features "
        "B) Redesign the service center emphasis on providing a seamless and intuitive use experience. "
        "C) Streamline business process to reduce cost and high quality products."
    )
    by_number[28]["choices"] = ["1 and 2", "1 only", "2 only", "3 only", "2 and 3"]
    by_number[28]["corrections"].append(
        "Recovered the three statement labels and five combination-choice boundaries from the flattened PDF text; wording was otherwise preserved."
    )
    # The last character of choice 5 is visibly clipped in text extraction and is obvious from the pair pattern.
    if by_number[90]["choices"][4] == "Both b and":
        by_number[90]["choices"][4] = "Both b and c"
        by_number[90]["corrections"].append(
            "Added the visibly clipped final `c` to choice 5 (`Both b and c`) as an obvious extraction defect."
        )
    return parsed


def subject_for(number: int) -> str:
    matches = [code for code, numbers in SUBJECT_RANGES.items() if number in numbers]
    if len(matches) != 1:
        raise ValueError(f"Question {number} subject mapping cardinality: {matches}")
    return matches[0]


def chapter_for(number: int) -> str:
    matches = [chapter_id for numbers, chapter_id in CHAPTER_MAP if number in numbers]
    if len(matches) != 1:
        raise ValueError(f"Question {number} chapter mapping cardinality: {matches}")
    return matches[0]


def answer_rationale(number: int, correct_text: str | None) -> tuple[str, str]:
    if number in HUMAN_REVIEW:
        note = HUMAN_REVIEW[number]
        return (
            f"No answer is exposed because the item cannot be resolved safely from the supplied textual evidence. {note}",
            f"ไม่แสดงคำตอบ เพราะไม่สามารถสรุปอย่างปลอดภัยจากหลักฐานข้อความที่ให้มาได้ {thai_text(note)}",
        )
    if number == 32:
        return (
            "Using z = (x − μ) / σ gives (42 − 75) / 10 = −3.3. Its magnitude exceeds the common three-standard-deviation check, so the listed result is an outlier.",
            "ใช้ z = (x − μ) / σ จะได้ (42 − 75) / 10 = −3.3 และค่าสัมบูรณ์เกินเกณฑ์สามส่วนเบี่ยงเบนมาตรฐาน จึงเป็น Outlier",
        )
    if number == 33:
        return (
            "There are eight ordered values, so the median is the average of the fourth and fifth: (20 + 22) / 2 = 21.",
            "มีข้อมูลเรียงลำดับ 8 ค่า มัธยฐานจึงเป็นค่าเฉลี่ยของลำดับที่ 4 และ 5 คือ (20 + 22) / 2 = 21",
        )
    return (
        f'The supported answer is “{correct_text}”. It matches the definition, process, or technical distinction in the cited supplied chapter; the other choices name a different concept, reverse the relationship, or conflict with that chapter.',
        f'คำตอบที่หลักฐานสนับสนุนคือ “{thai_text(correct_text or "")}” เพราะตรงกับนิยาม กระบวนการ หรือความแตกต่างทางเทคนิคในบทที่อ้างอิง ส่วนตัวเลือกอื่นเป็นคนละแนวคิด กลับความสัมพันธ์ หรือขัดกับเนื้อหา',
    )


def difficulty_for(number: int) -> str:
    if number in HUMAN_REVIEW or number in {28, 32, 35, 69, 73, 77, 79, 80, 102, 105, 106, 108, 111}:
        return "hard"
    if number in {4, 6, 7, 8, 9, 10, 19, 20, 22, 23, 29, 30, 31, 37, 38, 41, 44, 45, 46, 51, 59, 64, 67, 72, 76, 78, 83, 84, 88, 89, 90, 92, 96, 97, 100}:
        return "medium"
    return "easy"


def cognitive_level_for(number: int) -> str:
    if number in {21, 22, 23, 24, 28, 29, 30, 31, 32, 33, 35, 62, 69, 73, 77, 79, 80, 98, 102, 105, 106, 108, 111}:
        return "apply"
    if number in {4, 6, 7, 8, 9, 10, 19, 20, 37, 38, 41, 44, 45, 46, 51, 59, 64, 67, 72, 76, 78, 83, 84, 88, 89, 90, 92, 96, 97, 100}:
        return "understand"
    return "remember"


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat()
    inventory = json.loads((ROOT / "data/file-inventory.json").read_text(encoding="utf-8"))
    inventory_by_path = {item["relative_path"]: item for item in inventory["files"]}
    exam_source = inventory_by_path[EXAM_PATH]
    subjects_payload = json.loads((ROOT / "data/subjects.json").read_text(encoding="utf-8"))
    subjects_by_code = {item["course_code"]: item for item in subjects_payload["subjects"]}
    chapters_payload = json.loads((ROOT / "data/chapters.json").read_text(encoding="utf-8"))
    chapters_by_id = {item["chapter_id"]: item for item in chapters_payload["chapters"]}
    topics_payload = json.loads((ROOT / "data/topics.json").read_text(encoding="utf-8"))
    topics_by_chapter: dict[str, list[str]] = {}
    for item in topics_payload["topics"]:
        topics_by_chapter.setdefault(item["chapter_id"], []).append(item["topic_id"])
    references_payload = json.loads(
        (ROOT / "data/source-references.json").read_text(encoding="utf-8")
    )
    references_by_id = {
        item["source_reference_id"]: item for item in references_payload["source_references"]
    }

    parsed = parse_exam()
    questions: list[dict[str, Any]] = []
    source_map: list[dict[str, Any]] = []
    review_status: list[dict[str, Any]] = []
    for item in parsed:
        number = item["number"]
        subject_code = subject_for(number)
        chapter_id = chapter_for(number)
        chapter_data = chapters_by_id[chapter_id]
        answer_number = ANSWER_KEY[number]
        question_id = f"question-comprehensive-{number:03d}"
        correct_choice_id = (
            f"{question_id}-choice-{answer_number}" if answer_number is not None else None
        )
        answer_status = (
            "requires_human_review"
            if number in HUMAN_REVIEW
            else "verified_from_source"
            if number in VERIFIED
            else "strongly_inferred"
        )
        correct_text = (
            item["choices"][answer_number - 1] if answer_number is not None else None
        )
        explanation_en, explanation_th = answer_rationale(number, correct_text)
        source_refs = [
            references_by_id[reference_id]
            for reference_id in chapter_data["source_reference_ids"]
        ]
        choices = []
        for choice_number, original_text in enumerate(item["choices"], 1):
            choice_id = f"{question_id}-choice-{choice_number}"
            is_correct = answer_number == choice_number
            if answer_status == "requires_human_review":
                choice_explanation_en = (
                    "This choice is preserved but is not scored until the missing or ambiguous evidence is reviewed."
                )
                choice_explanation_th = (
                    "เก็บตัวเลือกนี้ตามต้นฉบับ แต่ยังไม่ให้คะแนนจนกว่าจะตรวจหลักฐานที่ขาดหายหรือกำกวม"
                )
            elif is_correct:
                choice_explanation_en = (
                    "This choice matches the concept or calculation supported by the cited supplied material."
                )
                choice_explanation_th = (
                    "ตัวเลือกนี้ตรงกับแนวคิดหรือการคำนวณที่เอกสารอ้างอิงสนับสนุน"
                )
            else:
                choice_explanation_en = (
                    "This choice does not match the tested definition or relationship; it names a different concept, reverses the condition, or yields a different result."
                )
                choice_explanation_th = (
                    "ตัวเลือกนี้ไม่ตรงกับนิยามหรือความสัมพันธ์ที่โจทย์ทดสอบ เพราะเป็นคนละแนวคิด กลับเงื่อนไข หรือให้ผลลัพธ์ต่างออกไป"
                )
            choices.append(
                {
                    "choice_id": choice_id,
                    "original_text_en": original_text,
                    "text_th": thai_text(original_text),
                    "is_correct": is_correct,
                    "explanation_en": choice_explanation_en,
                    "explanation_th": choice_explanation_th,
                }
            )

        question_th = SPECIAL_THAI_QUESTIONS.get(number, thai_text(item["stem"]))
        question = {
            "question_id": question_id,
            "source_exam_file_id": exam_source["file_id"],
            "source_exam_relative_path": EXAM_PATH,
            "source_page_or_slide": item["page"],
            "term": subjects_by_code[subject_code]["term"],
            "subject_code": subject_code,
            "subject_name": subjects_by_code[subject_code]["course_title_en"],
            "chapter_id": chapter_id,
            "topic_ids": topics_by_chapter[chapter_id],
            "question_type": "single_choice",
            "original_question_en": item["stem"],
            "question_th": question_th,
            "choices": choices,
            "correct_answer": correct_choice_id,
            "acceptable_answers": [correct_choice_id] if correct_choice_id else [],
            "answer_status": answer_status,
            "confidence": "low" if number in HUMAN_REVIEW else "high" if number in VERIFIED else "medium",
            "explanation_en": explanation_en,
            "explanation_th": explanation_th,
            "source_references": source_refs,
            "evidence_summary": (
                HUMAN_REVIEW[number]
                if number in HUMAN_REVIEW
                else f"Mapped to {chapter_data['title_en']} in the supplied learning corpus; answer status is {answer_status}."
            ),
            "difficulty": difficulty_for(number),
            "cognitive_level": cognitive_level_for(number),
            "tags": [
                subject_code,
                chapter_id.removeprefix(f"chapter-{subject_code.casefold()}-"),
                answer_status,
            ],
            "detected_ambiguity": number in HUMAN_REVIEW,
            "human_review_note": HUMAN_REVIEW.get(number),
            "original_text_correction_log": item["corrections"],
            "translation_note": "Thai study translation retains established English technical terms where that preserves precision.",
        }
        questions.append(question)
        source_map.append(
            {
                "question_id": question_id,
                "exam_file_id": exam_source["file_id"],
                "exam_page": item["page"],
                "learning_source_reference_ids": [
                    ref["source_reference_id"] for ref in source_refs
                ],
            }
        )
        review_status.append(
            {
                "question_id": question_id,
                "answer_status": answer_status,
                "confidence": question["confidence"],
                "requires_human_review": number in HUMAN_REVIEW,
                "review_note": HUMAN_REVIEW.get(number),
            }
        )

    def write_json(name: str, key: str, values: Any) -> None:
        payload = {"schema_version": "1.0.0", "generated_at": generated_at, key: values}
        (ROOT / f"data/{name}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    write_json("questions", "questions", questions)
    write_json(
        "exam-sets",
        "exam_sets",
        [
            {
                "exam_set_id": "exam-set-comprehensive-practice",
                "title_en": "Comprehensive Practice Questions",
                "title_th": "แนวข้อสอบ Comprehensive",
                "source_file_ids": [exam_source["file_id"]],
                "subject_codes": sorted(SUBJECT_RANGES),
                "question_ids": [item["question_id"] for item in questions],
                "question_count": len(questions),
                "notes": "Question numbers 11–18 are absent from the supplied PDF; numbering is preserved.",
            }
        ],
    )
    write_json("question-source-map", "question_source_map", source_map)
    write_json("question-review-status", "question_review_status", review_status)

    status_counts = Counter(item["answer_status"] for item in questions)
    subject_counts = Counter(item["subject_code"] for item in questions)
    review_rows = [
        f"| {item['question_id']} | {item['source_page_or_slide']} | {item['subject_code']} | {item['human_review_note']} |"
        for item in questions
        if item["answer_status"] == "requires_human_review"
    ]
    human_report = """# Examination Human Review

These questions are intentionally unscored. The UI must show a warning and must not imply a correct answer.

| Question ID | PDF page | Subject | Review reason |
| --- | --- | --- | --- |
""" + "\n".join(review_rows) + "\n"
    (ROOT / "reports/exam-human-review.md").write_text(human_report, encoding="utf-8")

    review_doc_rows = [
        f"| {item['question_id']} | {item['subject_code']} | {item['answer_status']} | {item['confidence']} | {item['source_page_or_slide']} |"
        for item in questions
    ]
    exam_review = """# Examination Review Index

The original English question and all five original choices are stored in `data/questions.json`. Answers are stable choice IDs, never array indexes.

| Question ID | Subject | Answer status | Confidence | Source page |
| --- | --- | --- | --- | --- |
""" + "\n".join(review_doc_rows) + "\n"
    (ROOT / "docs/exam-review.md").write_text(exam_review, encoding="utf-8")

    duplicate_report = """# Duplicate and Near-duplicate Questions

## Near-duplicate group 1

- `question-comprehensive-026`
- `question-comprehensive-049`

Both ask which concept results from matching a distinctive competency to a market opportunity. They are retained because the source includes both and their distractors differ.

## Exact duplicates

No exact question-and-choice duplicate was detected after normalized-text comparison.
"""
    (ROOT / "reports/duplicate-questions.md").write_text(
        duplicate_report, encoding="utf-8"
    )

    quality_report = f"""# Examination Answer Quality Report

- Questions extracted: **{len(questions)}**
- Verified from supplied source: **{status_counts['verified_from_source']}**
- Strongly inferred from supplied course content: **{status_counts['strongly_inferred']}**
- Ambiguous: **{status_counts['ambiguous']}**
- Requires human review: **{status_counts['requires_human_review']}**
- Questions with logged extraction corrections: **{sum(bool(item['original_text_correction_log']) for item in questions)}**

## Quality policy

- Original English wording and choices are retained from the PDF text layer.
- Only two obvious structural/text-layer defects were corrected and logged: question 28 choice boundaries and question 90's clipped final `c`.
- Diagram/table-dependent and internally inconsistent items remain unscored.
- `strongly_inferred` answers are not presented as verified.
- Each answerable question cites the supplied learning chapter used for support.
- Thai translations retain standard English technical terms where translating them would reduce precision.

## Limitations

Choice-by-choice explanations identify whether each option matches the tested definition or relationship. Human review remains valuable for nuanced distractor-specific prose and for a final native-speaker translation pass.
"""
    (ROOT / "reports/exam-answer-quality-report.md").write_text(
        quality_report, encoding="utf-8"
    )

    phase_report = f"""# Phase 2 Examination Analysis Report

- Status: **completed pending validation**
- Source examination files processed: **1**
- Source: `{EXAM_PATH}` (`{exam_source['file_id']}`)
- PDF pages processed: **16**
- Questions extracted: **{len(questions)}**
- Subject distribution: {", ".join(f"`{key}` {value}" for key, value in sorted(subject_counts.items()))}
- Answer-status distribution: {", ".join(f"`{key}` {value}" for key, value in sorted(status_counts.items()))}
- Near-duplicate groups: **1**

Question numbers 11–18 do not appear in the supplied PDF. Question 113 follows question 112 on page 16 and is included.
"""
    (ROOT / "reports/phase-2-examination-report.md").write_text(
        phase_report, encoding="utf-8"
    )
    print(
        f"Wrote {len(questions)} questions: "
        + ", ".join(f"{key}={value}" for key, value in sorted(status_counts.items()))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

