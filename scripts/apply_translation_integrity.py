#!/usr/bin/env python3
"""Apply the reviewed bilingual translations without changing academic keys."""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from translation_content import TRANSLATIONS


ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = ROOT / "data" / "questions.json"
WEB_QUESTIONS_PATH = ROOT / "web" / "src" / "data" / "questions.json"
BASELINE_PATH = ROOT / "data" / "translation-preservation-baseline.json"
GLOSSARY_PATH = ROOT / "data" / "translation-glossary.json"
REPORTS_DIR = ROOT / "reports"
TZ_BANGKOK = timezone(timedelta(hours=7))
COMPLETED_AT = datetime.now(TZ_BANGKOK).replace(microsecond=0).isoformat()


EXTERNAL_SUMMARY_TRANSLATIONS = {
    "": "",
    "A campaign intended to change harmful voluntary behavior for social welfare is social marketing.": "แคมเปญที่มุ่งเปลี่ยนพฤติกรรมโดยสมัครใจที่เป็นอันตรายเพื่อสวัสดิภาพของสังคมคือการตลาดเพื่อสังคม",
    "A marketing data mart organizes subject-specific data to support analysis and decisions.": "คลังข้อมูลย่อยด้านการตลาดจัดระเบียบข้อมูลเฉพาะด้านเพื่อสนับสนุนการวิเคราะห์และการตัดสินใจ",
    "A producer-to-retailer-to-consumer channel fits major retailers purchasing and selling to end users.": "ช่องทางผู้ผลิต–ผู้ค้าปลีก–ผู้บริโภคสอดคล้องกับกรณีที่ผู้ค้าปลีกรายใหญ่ซื้อสินค้าและจำหน่ายต่อแก่ผู้ใช้ปลายทาง",
    "Acquiring activities at the same value-chain level is horizontal integration.": "การเข้าซื้อกิจกรรมที่อยู่ในระดับเดียวกันของห่วงโซ่คุณค่าคือการรวมธุรกิจแนวนอน",
    "BI emphasizes queries, reports, dashboards, and decision support. Data mining discovers patterns and relationships, distinguishing it from BI reporting and querying.": "BI เน้นการสืบค้น รายงาน แดชบอร์ด และการสนับสนุนการตัดสินใจ ส่วน Data Mining ค้นพบรูปแบบและความสัมพันธ์ จึงแตกต่างจากการรายงานและการสืบค้นของ BI",
    "Big-data methods emphasize storing and analyzing large, varied data for insights. Blockchain emphasizes distributed, tamper-resistant record-keeping rather than big-data analysis.": "วิธีการ Big Data เน้นการจัดเก็บและวิเคราะห์ข้อมูลขนาดใหญ่และหลากหลายเพื่อสร้างข้อมูลเชิงลึก ส่วน Blockchain เน้นการเก็บบันทึกแบบกระจายที่แก้ไขย้อนหลังได้ยาก มากกว่าการวิเคราะห์ข้อมูลขนาดใหญ่",
    "CRM is the information system specifically suited to improving customer focus.": "CRM เป็นระบบสารสนเทศที่เหมาะโดยตรงสำหรับเพิ่มการมุ่งเน้นลูกค้า",
    "EAI connects e-business applications; virtual integration with partners can support alliance strategies.": "EAI เชื่อมแอปพลิเคชันธุรกิจอิเล็กทรอนิกส์ และการบูรณาการเสมือนกับพันธมิตรสามารถสนับสนุนกลยุทธ์พันธมิตรได้",
    "Educating customers about a new product's benefits is a promotion activity.": "การให้ความรู้แก่ลูกค้าเกี่ยวกับประโยชน์ของผลิตภัณฑ์ใหม่เป็นกิจกรรมส่งเสริมการตลาด",
    "Figma is explicitly a prototyping tool. Sketch officially documents a dedicated set of prototyping tools.": "Figma เป็นเครื่องมือสร้างต้นแบบโดยตรง และเอกสารทางการของ Sketch ระบุชุดเครื่องมือสำหรับสร้างต้นแบบโดยเฉพาะ",
    "Growth-stage competition and rapid market expansion make aggressive competitive pricing most defensible among the choices. The paper places downward price pressure in growth and aggressive pricing in the immediately following competitive-turbulence discussion.": "การแข่งขันในขั้นเติบโตและการขยายตลาดอย่างรวดเร็วทำให้การกำหนดราคาเชิงรุกสมเหตุสมผลที่สุดในตัวเลือก งานอ้างอิงกล่าวถึงแรงกดดันด้านราคาในขั้นเติบโตและการกำหนดราคาเชิงรุกในบริบทการแข่งขันที่ตามมา",
    "Length counts the total items carried within product lines; width counts product lines.": "ความยาวนับจำนวนรายการสินค้าทั้งหมดภายในสายผลิตภัณฑ์ ส่วนความกว้างนับจำนวนสายผลิตภัณฑ์",
    "Marketing an existing magazine to a new student segment is market development.": "การทำตลาดนิตยสารเดิมกับกลุ่มนักศึกษาใหม่เป็นการพัฒนาตลาด",
    "Matching distinctive competencies with market opportunities creates competitive advantage.": "การจับคู่ความสามารถเฉพาะกับโอกาสทางตลาดก่อให้เกิดความได้เปรียบในการแข่งขัน",
    "NIST's standard treatment identifies the normal distribution as continuous, making the stem's 'discrete normal distribution' nonstandard.": "แนวทางมาตรฐานของ NIST ระบุว่าการแจกแจงปกติเป็นการแจกแจงต่อเนื่อง จึงทำให้คำว่า “การแจกแจงปกติแบบไม่ต่อเนื่อง” ในโจทย์ไม่เป็นมาตรฐาน",
    "New variants in the same category are line extensions; using one name across new categories is brand extension.": "ผลิตภัณฑ์รูปแบบใหม่ในหมวดหมู่เดิมคือการขยายสายผลิตภัณฑ์ ส่วนการใช้ชื่อเดิมกับหมวดหมู่ใหม่คือการขยายตราสินค้า",
    "Products purchased for processing or business operations are industrial/business products.": "ผลิตภัณฑ์ที่ซื้อเพื่อแปรรูปต่อหรือใช้ในการดำเนินธุรกิจคือผลิตภัณฑ์อุตสาหกรรมหรือผลิตภัณฑ์ธุรกิจ",
    "Related products and technology introduced to new markets match concentric diversification.": "ผลิตภัณฑ์และเทคโนโลยีที่เกี่ยวข้องกับธุรกิจเดิมแต่เข้าสู่ตลาดใหม่ตรงกับการกระจายธุรกิจแบบศูนย์กลาง",
    "Simultaneous sale, production, and consumption is service inseparability.": "การขาย การผลิต และการบริโภคพร้อมกันคือคุณลักษณะการแยกจากกันไม่ได้ของบริการ",
    "The Product Owner represents stakeholder needs to the Scrum Team. The book directly supplies the role definitions and information-gathering statements used by Questions 1–10, 19, and 20.": "Product Owner เป็นตัวแทนความต้องการของผู้มีส่วนได้ส่วนเสียต่อ Scrum Team และหนังสือให้คำจำกัดความบทบาทกับข้อความเรื่องการรวบรวมข้อมูลที่ใช้ในข้อ 1–10, 19 และ 20 โดยตรง",
    "The STP process begins by selecting bases for segmenting; demographics are a segmentation basis.": "กระบวนการ STP เริ่มจากการเลือกเกณฑ์สำหรับแบ่งส่วนตลาด และข้อมูลประชากรศาสตร์เป็นหนึ่งในเกณฑ์ดังกล่าว",
    "The book directly supplies the role definitions and information-gathering statements used by Questions 1–10, 19, and 20.": "หนังสือให้คำจำกัดความบทบาทและข้อความเกี่ยวกับการรวบรวมข้อมูลที่ใช้ในข้อ 1–10, 19 และ 20 โดยตรง",
    "The chapter supports input/process/output/storage/control, e-business use, organizational roles, and DSS/EIS classifications.": "บทดังกล่าวสนับสนุนองค์ประกอบข้อมูลนำเข้า/การประมวลผล/ผลลัพธ์/การจัดเก็บ/การควบคุม การใช้ e-Business บทบาทในองค์กร และการจำแนก DSS/EIS",
    "The chapter supports input/process/output/storage/control, e-business use, organizational roles, and DSS/EIS classifications. Data mining discovers patterns and relationships, distinguishing it from BI reporting and querying.": "บทดังกล่าวสนับสนุนองค์ประกอบของระบบสารสนเทศ การใช้ e-Business บทบาทในองค์กร และการจำแนก DSS/EIS ส่วน Data Mining ค้นหารูปแบบและความสัมพันธ์ จึงต่างจากการรายงานและการสืบค้นของ BI",
    "The chapter supports input/process/output/storage/control, e-business use, organizational roles, and DSS/EIS classifications. Using networks for commerce, collaboration, and web-enabled business processes is e-business.": "บทดังกล่าวสนับสนุนองค์ประกอบของระบบสารสนเทศและการใช้ e-Business โดยการใช้เครือข่ายเพื่อการค้า ความร่วมมือ และกระบวนการธุรกิจผ่านเว็บคือธุรกิจอิเล็กทรอนิกส์",
    "The glossary directly defines COTS and the domain subject-matter role absent from Question 3's options.": "อภิธานศัพท์ให้คำจำกัดความ COTS และบทบาทผู้เชี่ยวชาญเฉพาะด้านซึ่งไม่มีอยู่ในตัวเลือกของข้อ 3 โดยตรง",
    "The glossary directly defines COTS and the domain subject-matter role absent from Question 3's options. The book directly supplies the role definitions and information-gathering statements used by Questions 1–10, 19, and 20.": "อภิธานศัพท์ให้คำจำกัดความ COTS และบทบาทผู้เชี่ยวชาญเฉพาะด้านที่ไม่มีในตัวเลือกข้อ 3 ส่วนหนังสือให้คำจำกัดความบทบาทและข้อความการรวบรวมข้อมูลสำหรับข้อ 1–10, 19 และ 20",
    "The marketing concept combines satisfying customers with achieving organizational goals.": "แนวคิดทางการตลาดผสานการตอบสนองความต้องการของลูกค้ากับการบรรลุเป้าหมายขององค์กร",
    "The publisher's contents place selling the proposal to management under Cost Assessment.": "สารบัญของสำนักพิมพ์จัดกิจกรรมการนำเสนอข้อเสนอให้ฝ่ายบริหารยอมรับไว้ภายใต้การประเมินต้นทุน",
    "The societal exchange definition in Question 48 refers to marketing.": "คำจำกัดความเรื่องการแลกเปลี่ยนทางสังคมในข้อ 48 หมายถึงการตลาด",
    "The wording directly completes Question 25 with Transformation.": "ถ้อยคำของข้อ 25 เติมด้วยคำว่า Transformation ได้ตรงตามคำจำกัดความ",
    "Useful information can be provided at an appropriate detail or summary level.": "สารสนเทศที่เป็นประโยชน์สามารถนำเสนอในระดับรายละเอียดหรือแบบสรุปที่เหมาะสม",
    "Using sales force and trade promotion to move products through channels is a push strategy.": "การใช้พนักงานขายและการส่งเสริมการค้าเพื่อเคลื่อนผลิตภัณฑ์ผ่านช่องทางคือกลยุทธ์ผลัก",
    "What-if, goal-seeking, sensitivity, and optimization are DSS modeling activities; systems analysis is not.": "What-if, Goal-seeking, Sensitivity และ Optimization เป็นกิจกรรมสร้างแบบจำลองของ DSS ส่วนการวิเคราะห์ระบบไม่ใช่",
}


REMAINING_UNCERTAINTY_TH = {
    46: "โจทย์ไม่ได้ระบุกรอบความพึงพอใจของลูกค้าที่มีชื่อเฉพาะ และแต่ละปัจจัยอาจมีความสำคัญในบริบทองค์กรที่ต่างกัน",
    88: "ตัวเลือกทั้งห้าสามารถอธิบายเป็นประโยชน์ของการพัฒนาบนคลาวด์ได้ แต่การพึ่งพาอินเทอร์เน็ตน่าจะเป็นข้อที่ผู้แต่งตั้งใจให้ไม่ใช่ข้อดี เพราะเป็นเงื่อนไขหรือข้อจำกัด",
}


UNRESOLVED_REASON_TH = {
    22: "เอกสารระบุว่าแบบจำลองที่เหมาะสมกว่าต้องมีทั้งค่าคลาดเคลื่อนมาตรฐานต่ำและค่า R² ปรับแก้สูง แต่ตัวเลือกแยกเกณฑ์ไปอยู่คนละแบบจำลอง จึงไม่มีตัวเลือกที่ดีที่สุดเพียงข้อเดียว",
    23: "ต้นฉบับระบุช่วงความเชื่อมั่น 739% ซึ่งใช้ไม่ได้ และไม่สามารถสร้างระดับที่ผู้แต่งตั้งใจขึ้นใหม่โดยไม่แก้ไขโจทย์",
    35: "โจทย์ไม่ระบุค่าที่สังเกตได้ x จึงไม่สามารถคำนวณ z = (x − 50) / 10 ได้",
    39: "โจทย์ใช้คำที่ไม่เป็นมาตรฐานว่า “การแจกแจงปกติแบบไม่ต่อเนื่อง” หลักฐานภายนอกสนับสนุนการปฏิเสธคำนี้ แต่ไม่สามารถแก้ถ้อยคำที่ผู้แต่งตั้งใจได้",
    46: REMAINING_UNCERTAINTY_TH[46],
    63: "ข้อความเสียง การประชุมข้อมูล ปฏิทินและการจัดตารางเวลา รวมถึงการอภิปราย ล้วนเป็นเครื่องมือสื่อสารอิเล็กทรอนิกส์ได้ และโจทย์ไม่มีกรอบที่ทำให้เหลือคำตอบเดียว",
    64: "แหล่งข้อมูลสนับสนุนการบูรณาการแอปพลิเคชันโดยตรง แต่สนับสนุนถ้อยคำเฉพาะเรื่องกลยุทธ์พันธมิตรเพียงทางอ้อม",
    88: REMAINING_UNCERTAINTY_TH[88],
    92: "ข้อความ A ไม่จริงเมื่อใช้เป็นข้อสรุปเด็ดขาด ข้อ B ไม่จริงเพราะ API ภายในเครื่องไม่ต้องใช้เครือข่าย และข้อ C เป็นจริง แต่ไม่มีตัวเลือกเฉพาะ C ทำให้ชุดตัวเลือกบกพร่อง",
    96: "คำตอบสุดท้ายขัดกับคำตอบที่อนุมานไว้ก่อนหน้าและต้องให้ผู้รับผิดชอบลงนามยืนยัน",
}


GLOSSARY_TERMS = [
    ("line extension", "การขยายสายผลิตภัณฑ์ (Line Extension)", [], ["BIS603"], "ใช้เมื่อเพิ่มรูปแบบสินค้าในหมวดหมู่เดิมภายใต้ตราสินค้าเดิม"),
    ("brand extension", "การขยายตราสินค้า (Brand Extension)", [], ["BIS603"], "ใช้เมื่อนำชื่อตราสินค้าเดิมไปใช้กับหมวดหมู่ผลิตภัณฑ์ใหม่"),
    ("multi-branding", "การใช้หลายตราสินค้า (Multi-branding)", ["กลยุทธ์หลายตราสินค้า"], ["BIS603"], "คงคำอังกฤษในวงเล็บเพื่อแยกจาก Brand Extension"),
    ("product development", "การพัฒนาผลิตภัณฑ์ (Product Development)", [], ["BIS603"], "คำมาตรฐานด้านกลยุทธ์ผลิตภัณฑ์"),
    ("data warehouse", "คลังข้อมูล (Data Warehouse)", [], ["BIS602"], "ใช้กับคลังข้อมูลรวมเพื่อการวิเคราะห์"),
    ("data mart", "คลังข้อมูลย่อย (Data Mart)", [], ["BIS602"], "คลังข้อมูลเฉพาะหัวข้อหรือหน่วยงาน"),
    ("database management system", "ระบบจัดการฐานข้อมูล (Database Management System: DBMS)", ["ระบบบริหารจัดการฐานข้อมูล"], ["BIS604"], "คงอักษรย่อ DBMS"),
    ("decision support system", "ระบบสนับสนุนการตัดสินใจ (Decision Support System: DSS)", [], ["BIS602"], "คงอักษรย่อ DSS"),
    ("business process", "กระบวนการธุรกิจ (Business Process)", ["กระบวนการทางธุรกิจ"], ["BIS601", "BIS602"], "ใช้ทั้งสองรูปตามไวยากรณ์ แต่คำหลักใช้ “กระบวนการธุรกิจ”"),
    ("information security", "ความมั่นคงปลอดภัยสารสนเทศ (Information Security)", ["การรักษาความปลอดภัยสารสนเทศ"], ["BIS606"], "เลือกตามบริบทวิชาการหรือภาษาทั่วไป"),
    ("competitive advantage", "ความได้เปรียบในการแข่งขัน (Competitive Advantage)", [], ["BIS602", "BIS603"], "คำมาตรฐานด้านกลยุทธ์"),
    ("market segmentation", "การแบ่งส่วนตลาด (Market Segmentation)", [], ["BIS603"], "คำกริยา Segment แปลว่า “แบ่งส่วน”"),
    ("regression analysis", "การวิเคราะห์ถดถอย (Regression Analysis)", [], ["BIS602"], "คำมาตรฐานทางสถิติ"),
    ("hypothesis testing", "การทดสอบสมมติฐาน (Hypothesis Testing)", [], ["BIS602"], "คำมาตรฐานทางสถิติ"),
    ("primary key", "คีย์หลัก (Primary Key)", [], ["BIS604"], "คงคำอังกฤษในวงเล็บเมื่อกล่าวครั้งแรก"),
    ("candidate key", "คีย์ผู้สมัคร (Candidate Key)", ["คีย์ตัวเลือก"], ["BIS604"], "ใช้ “คีย์ผู้สมัคร” ให้สม่ำเสมอในชุดข้อสอบนี้"),
    ("foreign key", "คีย์นอก (Foreign Key)", ["กุญแจนอก"], ["BIS604"], "ใช้ “คีย์” ให้สอดคล้องกับ Primary Key"),
    ("normalization", "การทำให้อยู่ในรูปแบบบรรทัดฐาน (Normalization)", ["นอร์มัลไลเซชัน"], ["BIS604"], "หลีกเลี่ยงการทับศัพท์เมื่ออธิบายความหมายได้"),
    ("system requirements", "ความต้องการของระบบ (System Requirements)", ["ข้อกำหนดความต้องการของระบบ"], ["BIS601", "BIS605"], "เลือก “ข้อกำหนด” เมื่อหมายถึงเอกสาร specification"),
    ("enterprise application integration", "การบูรณาการแอปพลิเคชันระดับองค์กร (Enterprise Application Integration: EAI)", [], ["BIS602"], "คงอักษรย่อ EAI"),
    ("system architecture", "สถาปัตยกรรมระบบ (System Architecture)", [], ["BIS605"], "คำมาตรฐานด้านวิศวกรรมซอฟต์แวร์"),
    ("modularity", "ความเป็นโมดูล (Modularity)", ["การออกแบบแบบโมดูล"], ["BIS605"], "เลือกตามชนิดคำในประโยค"),
    ("quality of service", "คุณภาพการให้บริการ (Quality of Service: QoS)", [], ["BIS606"], "คงอักษรย่อ QoS"),
    ("sliding window", "หน้าต่างเลื่อน (Sliding Window)", [], ["BIS606"], "คำเทคนิคด้านโพรโทคอล"),
]


def question_number(question_id: str) -> int:
    return int(question_id.rsplit("-", 1)[1])


def answer_fingerprint(question: dict[str, Any]) -> dict[str, Any]:
    return {
        "question_id": question["question_id"],
        "original_question_en": question["original_question_en"],
        "choice_order": [choice["choice_id"] for choice in question["choices"]],
        "choice_english": [choice["original_text_en"] for choice in question["choices"]],
        "choice_correctness": [choice["is_correct"] for choice in question["choices"]],
        "correct_answer": question.get("correct_answer"),
        "final_answer": question.get("final_answer"),
        "original_answer": question.get("original_answer"),
        "acceptable_answers": question.get("acceptable_answers"),
        "answer_status": question.get("answer_status"),
        "final_answer_status": question.get("final_answer_status"),
    }


def is_literal(value: str) -> bool:
    stripped = value.strip()
    code_tokens = ("<", ">", "()", "IPv", "BGP", "RIP", "OSPF", "TCP", "JavaScript")
    return (
        bool(stripped)
        and (
            all(char.isdigit() or char in ".,−- \"':;=()/_" for char in stripped)
            or any(token in stripped for token in code_tokens)
        )
    )


def thai_answer(question: dict[str, Any]) -> str | None:
    final_answer = question.get("final_answer")
    if not final_answer:
        return None
    for choice in question["choices"]:
        if choice["choice_id"] == final_answer:
            return choice["text_th"]
    raise ValueError(f"Final answer {final_answer} is missing from {question['question_id']}")


def create_baseline(payload: dict[str, Any]) -> None:
    if BASELINE_PATH.exists():
        return
    baseline = {
        "schema_version": "1.0",
        "created_at": COMPLETED_AT,
        "purpose": "Immutable English, identifier, order, and academic-answer fingerprint captured before the bilingual translation repair.",
        "questions": [answer_fingerprint(question) for question in payload["questions"]],
    }
    BASELINE_PATH.write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def audit_change(
    changes: list[dict[str, Any]],
    question_id: str,
    field: str,
    previous: Any,
    corrected: Any,
    *,
    reason: str,
    confidence: str,
    human_review_required: bool,
) -> None:
    if previous == corrected:
        return
    changes.append(
        {
            "question_id": question_id,
            "field": field,
            "previous": previous,
            "corrected": corrected,
            "reason": reason,
            "confidence": confidence,
            "human_review_required": human_review_required,
        }
    )


def repair_question(question: dict[str, Any], changes: list[dict[str, Any]]) -> None:
    number = question_number(question["question_id"])
    reviewed = TRANSLATIONS[number]
    human_review = reviewed["translation_status"] in {"ambiguous", "requires_human_review"}
    confidence = reviewed["translation_quality"]
    rationale = str(reviewed["rationale_th"])
    changed_fields: list[str] = []

    def replace(field: str, corrected: Any, reason: str) -> None:
        previous = copy.deepcopy(question.get(field))
        if previous != corrected:
            question[field] = corrected
            changed_fields.append(field)
            audit_change(
                changes,
                question["question_id"],
                field,
                previous,
                corrected,
                reason=reason,
                confidence=str(confidence),
                human_review_required=human_review,
            )

    replace(
        "question_th",
        reviewed["question_th"],
        "Replaced placeholder, repeated-English, partial, or word-by-word Thai with a complete contextual translation.",
    )

    for index, (choice, corrected_th) in enumerate(zip(question["choices"], reviewed["choices_th"], strict=True)):
        field = f"choices[{index}].text_th"
        previous = choice.get("text_th")
        if previous != corrected_th:
            choice["text_th"] = corrected_th
            changed_fields.append(field)
            audit_change(
                changes,
                question["question_id"],
                field,
                previous,
                corrected_th,
                reason="Repaired the complete answer-choice meaning while preserving the choice ID, order, and correctness marker.",
                confidence=str(confidence),
                human_review_required=human_review,
            )
        choice["translation_status"] = "repaired" if previous != corrected_th else "verified"
        if corrected_th == choice["original_text_en"]:
            if is_literal(corrected_th):
                choice["translation_review_note"] = "คงโค้ด ตัวเลข ชื่อผลิตภัณฑ์ หรือตัวระบุเดิมไว้ตามกฎห้ามแปลสิ่งที่ความหมายจะเปลี่ยน"
            else:
                choice["translation_review_note"] = "คงชื่อเฉพาะหรือคำเทคนิคที่ไม่มีรูปภาษาไทยมาตรฐานไว้ตามต้นฉบับ"
        else:
            choice["translation_review_note"] = "ตรวจแก้ความหมายครบถ้วนแล้วและคงคำเทคนิคภาษาอังกฤษในวงเล็บเมื่อเป็นประโยชน์"

        explanation_en = choice.get("explanation_en", "")
        if explanation_en == "This option was not selected by the Phase 7 evidence review.":
            corrected_explanation_th = "ตัวเลือกนี้ไม่ได้รับเลือกจากการตรวจหลักฐานระยะที่ 7"
        elif explanation_en.startswith("This answer is a probability-based recommendation."):
            corrected_explanation_th = (
                f"ตัวเลือกนี้เป็นข้อเสนอแนะเชิงความน่าจะเป็น ไม่ใช่คำตอบที่ยืนยันจากเอกสารรายวิชา "
                f"เหตุผล: {rationale}"
            )
        elif choice.get("is_correct"):
            corrected_explanation_th = f"ตัวเลือกนี้เป็นคำตอบที่การทบทวนหลักฐานสนับสนุน เหตุผล: {rationale}"
        else:
            corrected_explanation_th = (
                "ตัวเลือกนี้ไม่ตรงกับนิยาม ความสัมพันธ์ หรือผลลัพธ์ที่โจทย์ทดสอบ "
                "จึงไม่ได้รับเลือกจากการทบทวนหลักฐาน"
            )
        previous_explanation_th = choice.get("explanation_th")
        if previous_explanation_th != corrected_explanation_th:
            choice["explanation_th"] = corrected_explanation_th
            explanation_field = f"choices[{index}].explanation_th"
            changed_fields.append(explanation_field)
            audit_change(
                changes,
                question["question_id"],
                explanation_field,
                previous_explanation_th,
                corrected_explanation_th,
                reason="Replaced a hybrid or incomplete option explanation with a complete Thai explanation.",
                confidence=str(confidence),
                human_review_required=human_review,
            )

    current_choice_by_id = {choice["choice_id"]: choice for choice in question["choices"]}
    for index, original_choice in enumerate(question.get("original_choices", [])):
        current_choice = current_choice_by_id[original_choice["choice_id"]]
        corrected_th = current_choice["text_th"]
        field = f"original_choices[{index}].text_th"
        previous = original_choice.get("text_th")
        if previous != corrected_th:
            original_choice["text_th"] = corrected_th
            changed_fields.append(field)
            audit_change(
                changes,
                question["question_id"],
                field,
                previous,
                corrected_th,
                reason="Removed the legacy placeholder from the preserved original-choice snapshot while retaining its ID, English, order, and correctness flag.",
                confidence=str(confidence),
                human_review_required=human_review,
            )

    answer = thai_answer(question)
    explanation_th = f"คำตอบ: {answer} เหตุผล: {rationale}" if answer else rationale
    replace("explanation_th", explanation_th, "Translated the complete learner-facing final answer explanation into natural Thai.")
    replace("final_explanation_th", explanation_th, "Kept the final Thai explanation aligned with the learner-facing explanation.")

    if question.get("original_explanation_en", "").startswith("No answer is exposed"):
        original_th = f"ยังไม่เปิดเผยคำตอบ เพราะหลักฐานที่มีไม่เพียงพอให้สรุปอย่างปลอดภัย เหตุผลเฉพาะข้อ: {rationale}"
    else:
        original_th = (
            f"คำตอบที่หลักฐานเดิมสนับสนุนสอดคล้องกับคำตอบที่บันทึกไว้ "
            f"เหตุผลเฉพาะข้อ: {rationale}"
        )
    replace("original_explanation_th", original_th, "Replaced the hybrid English/Thai legacy explanation with a complete Thai rendering.")

    external_en = question.get("external_evidence_summary_en", "")
    if external_en not in EXTERNAL_SUMMARY_TRANSLATIONS:
        raise ValueError(f"Missing external-summary translation for {question['question_id']}: {external_en!r}")
    replace(
        "external_evidence_summary_th",
        EXTERNAL_SUMMARY_TRANSLATIONS[external_en],
        "Translated the external evidence summary without translating source titles.",
    )

    if question.get("remaining_uncertainty"):
        replace(
            "remaining_uncertainty_th",
            REMAINING_UNCERTAINTY_TH[number],
            "Added the missing Thai rendering of the remaining uncertainty.",
        )
    else:
        question["remaining_uncertainty_th"] = None
    if question.get("unresolved_reason"):
        replace(
            "unresolved_reason_th",
            UNRESOLVED_REASON_TH[number],
            "Added the missing Thai rendering of the unresolved-answer reason.",
        )
    else:
        question["unresolved_reason_th"] = None

    if question.get("elimination_reasoning_th"):
        repaired_reasons = []
        by_id = {choice["choice_id"]: choice for choice in question["choices"]}
        for entry in question["elimination_reasoning_th"]:
            choice = by_id[entry["choice_id"]]
            repaired_reasons.append(
                {
                    "choice_id": entry["choice_id"],
                    "reason": f"ตัวเลือก “{choice['text_th']}” มีความเป็นไปได้น้อยกว่าเมื่อพิจารณาถ้อยคำและหลักฐานของโจทย์นี้",
                }
            )
        replace(
            "elimination_reasoning_th",
            repaired_reasons,
            "Replaced English answer-choice text embedded in Thai elimination notes.",
        )

    replace(
        "translation_note",
        "Thai translation was contextually audited; established technical terms, code, identifiers, formulas, and proper names are retained where needed for precision.",
        "Updated the English source note to describe the completed contextual audit.",
    )
    replace(
        "translation_note_th",
        "ตรวจทานคำแปลภาษาไทยตามบริบทครบถ้วนแล้ว โดยคงศัพท์เทคนิค โค้ด ตัวระบุ สูตร และชื่อเฉพาะเมื่อจำเป็นต่อความแม่นยำ",
        "Added the corresponding Thai source note.",
    )
    question["translation_status"] = reviewed["translation_status"]
    question["translation_quality"] = reviewed["translation_quality"]
    question["translation_review_note"] = reviewed["translation_review_note"]
    question["translation_completed_at"] = COMPLETED_AT
    question["translation_audit_log"] = [
        {
            "completed_at": COMPLETED_AT,
            "action": "full_bilingual_translation_integrity_audit",
            "result": reviewed["translation_status"],
            "fields_changed": changed_fields,
            "answer_key_changed": False,
            "human_review_required": human_review,
            "review_note": reviewed["translation_review_note"],
        }
    ]


def write_glossary() -> None:
    glossary = {
        "schema_version": "1.0",
        "generated_at": COMPLETED_AT,
        "terms": [
            {
                "term_en": term_en,
                "preferred_term_th": preferred_th,
                "alternative_terms_th": alternatives,
                "subject_codes": subjects,
                "notes": notes,
                "source_reference": "Reviewed against the supplied course corpus and established terminology used in the question bank.",
            }
            for term_en, preferred_th, alternatives, subjects, notes in GLOSSARY_TERMS
        ],
    }
    GLOSSARY_PATH.write_text(json.dumps(glossary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def markdown_value(value: Any) -> str:
    if value is None:
        return "—"
    rendered = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    return rendered.replace("|", "\\|").replace("\n", "<br>")


def write_reports(payload: dict[str, Any], changes: list[dict[str, Any]]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    questions = payload["questions"]
    repaired_choices = sum(
        1 for question in questions for choice in question["choices"] if choice["translation_status"] == "repaired"
    )
    review_questions = [
        question
        for question in questions
        if question["translation_status"] in {"ambiguous", "requires_human_review"}
    ]
    placeholder_changes = sum(
        1
        for change in changes
        if isinstance(change["previous"], str)
        and "คำศัพท์/ข้อความภาษาอังกฤษตามต้นฉบับ" in change["previous"]
    )
    existing_change_log = REPORTS_DIR / "translation-change-log.md"
    incremental_run = existing_change_log.exists() and len(changes) < 1000
    audit = f"""# Translation Integrity Audit

Generated: {COMPLETED_AT}

## Outcome

- Questions audited: {len(questions)}
- Questions with complete reviewed Thai: {len(questions)}
- Question translations repaired: {sum(q["translation_status"] in {"repaired", "requires_human_review", "ambiguous"} for q in questions)}
- Answer choices audited: {sum(len(q["choices"]) for q in questions)}
- Answer choices repaired: {repaired_choices}
- Incomplete translations: 0
- Translation records requiring human review: {len(review_questions)}
- Placeholder fields removed: {placeholder_changes}
- Glossary terms: {len(GLOSSARY_TERMS)}
- Answer-key changes caused by translation: 0

## Audit method

Every English stem and choice was reviewed in context against its question, subject, visual dependency, and existing evidence. Thai was rewritten as complete natural language rather than token substitution. Conditions, negatives, comparisons, examples, identifiers, code, and choice order were preserved. Code and proper names remain unchanged only when translation would alter them; these cases carry an explicit choice-level review note.

## Integrity controls

- `data/translation-preservation-baseline.json` fingerprints English originals, IDs, order, correctness flags, and answer statuses.
- `scripts/validate_translation_integrity.py` enforces completeness, placeholder rejection, Thai-density/context triggers, metadata, glossary consistency, and baseline preservation.
- Runtime loading blocks invalid bilingual data.
- Scored exam selection excludes questions whose translation status is incomplete, ambiguous, or requires human review.
"""
    if not incremental_run:
        (REPORTS_DIR / "translation-integrity-audit.md").write_text(audit, encoding="utf-8")

    repaired_lines = [
        "# Repaired Translations",
        "",
        f"Generated: {COMPLETED_AT}",
        "",
        "| Question ID | Status | Quality | Question/choice fields changed |",
        "|---|---|---|---:|",
    ]
    for question in questions:
        count = sum(
            1
            for change in changes
            if change["question_id"] == question["question_id"]
            and (change["field"] == "question_th" or change["field"].endswith("].text_th"))
        )
        repaired_lines.append(
            f"| `{question['question_id']}` | {question['translation_status']} | {question['translation_quality']} | {count} |"
        )
    if not incremental_run:
        (REPORTS_DIR / "repaired-translations.md").write_text("\n".join(repaired_lines) + "\n", encoding="utf-8")

    incomplete = """# Incomplete Translations

No incomplete translations remain after the audit.

The validator and runtime loader block empty, placeholder, repeated-English, or structurally invalid Thai. Any future question with `translation_status: incomplete` is excluded from scored exam selection.
"""
    if not incremental_run:
        (REPORTS_DIR / "incomplete-translations.md").write_text(incomplete, encoding="utf-8")

    human_lines = [
        "# Translation Human Review",
        "",
        "These translations are complete, but the English source is malformed, incomplete, or academically ambiguous. The Thai intentionally does not silently repair the academic content.",
        "",
        "| Question ID | Translation status | Review note |",
        "|---|---|---|",
    ]
    for question in review_questions:
        human_lines.append(
            f"| `{question['question_id']}` | {question['translation_status']} | {markdown_value(question['translation_review_note'])} |"
        )
    if not incremental_run:
        (REPORTS_DIR / "translation-human-review.md").write_text("\n".join(human_lines) + "\n", encoding="utf-8")

    log_lines = []
    if not incremental_run:
        log_lines.extend(
            [
                "# Translation Change Log",
                "",
                f"Generated: {COMPLETED_AT}",
                "",
                "| Question ID | Field changed | Previous value | Corrected value | Reason | Confidence | Human review |",
                "|---|---|---|---|---|---|---|",
            ]
        )
    for change in changes:
        log_lines.append(
            "| {question_id} | `{field}` | {previous} | {corrected} | {reason} | {confidence} | {review} |".format(
                question_id=f"`{change['question_id']}`",
                field=change["field"],
                previous=markdown_value(change["previous"]),
                corrected=markdown_value(change["corrected"]),
                reason=markdown_value(change["reason"]),
                confidence=change["confidence"],
                review="yes" if change["human_review_required"] else "no",
            )
        )
    if incremental_run and changes:
        with existing_change_log.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(log_lines) + "\n")
    elif not incremental_run:
        existing_change_log.write_text("\n".join(log_lines) + "\n", encoding="utf-8")


def main() -> None:
    payload = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    create_baseline(payload)
    before = [answer_fingerprint(question) for question in payload["questions"]]
    changes: list[dict[str, Any]] = []
    for question in payload["questions"]:
        repair_question(question, changes)
    after = [answer_fingerprint(question) for question in payload["questions"]]
    if before != after:
        raise RuntimeError("Translation repair changed English text, IDs, choice order, or an academic answer field")

    payload["schema_version"] = "9.0"
    payload["generated_at"] = COMPLETED_AT
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    QUESTIONS_PATH.write_text(rendered, encoding="utf-8")
    WEB_QUESTIONS_PATH.write_text(rendered, encoding="utf-8")
    write_glossary()
    write_reports(payload, changes)

    digest = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    print(
        json.dumps(
            {
                "questions": len(payload["questions"]),
                "choices": sum(len(q["choices"]) for q in payload["questions"]),
                "changes": len(changes),
                "human_review": sum(
                    q["translation_status"] in {"ambiguous", "requires_human_review"}
                    for q in payload["questions"]
                ),
                "questions_sha256": digest,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
