#!/usr/bin/env python3
"""Build the Phase 12 exam-to-Study-Library coverage repair and mappings.

This script never reads or writes answer keys. It links each supplied examination
question to a precise teaching topic, adds source-labelled bilingual concept
teaching, and emits bidirectional traceability data for the application.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DATE = "2026-07-28"

SOURCE_LABELS = {
    "COURSE_MATERIAL": (
        "course_material",
        "From course materials",
        "จากเอกสารการเรียน",
    ),
    "EXTERNAL_AUTHORITATIVE": (
        "external_authoritative_source",
        "Supplementary information from an authoritative external source",
        "ข้อมูลเสริมจากแหล่งภายนอกที่น่าเชื่อถือ",
    ),
    "SUPPLEMENTARY_EXPLANATION": (
        "supplementary_explanation",
        "Supplementary explanation",
        "คำอธิบายเสริม",
    ),
}

TOPIC = {
    "ba": "topic-bis601-analyst-and-system-success-02",
    "elicitation": "topic-bis601-requirements-03",
    "competitive": "topic-bis602-strategy-and-competition-01",
    "process": "topic-bis602-process-and-kpi-01",
    "kpi": "topic-bis602-process-and-kpi-02",
    "bsc": "topic-bis602-process-and-kpi-03",
    "data_quality": "topic-bis602-enterprise-data-01",
    "etl": "topic-bis602-enterprise-data-02",
    "expected": "topic-bis602-probability-and-statistics-01",
    "std": "topic-bis602-probability-and-statistics-02",
    "z": "topic-bis602-probability-and-statistics-03",
    "bi": "topic-bis602-bi-and-visualization-01",
    "olap": "topic-bis602-bi-and-visualization-02",
    "visual": "topic-bis602-bi-and-visualization-03",
    "depvar": "topic-bis602-regression-01",
    "coefficient": "topic-bis602-regression-02",
    "residual": "topic-bis602-regression-03",
    "strategy": "topic-bis603-strategy-foundations-01",
    "alternative": "topic-bis603-strategy-formulation-01",
    "alignment": "topic-bis603-strategy-formulation-03",
    "stp": "topic-bis603-marketing-foundations-01",
    "mix": "topic-bis603-marketing-foundations-02",
    "database": "topic-bis604-database-foundations-01",
    "dbms": "topic-bis604-database-foundations-02",
    "conceptual": "topic-bis604-data-models-01",
    "logical": "topic-bis604-data-models-02",
    "primary": "topic-bis604-relational-model-01",
    "cardinality": "topic-bis604-business-rules-and-erd-02",
    "ddl": "topic-bis604-sql-and-implementation-01",
    "join": "topic-bis604-sql-and-implementation-03",
    "architecture": "topic-bis605-architecture-and-sdlc-01",
    "lifecycle": "topic-bis605-architecture-and-sdlc-02",
    "modularity": "topic-bis605-software-design-01",
    "prototype": "topic-bis605-web-and-ui-design-03",
    "framework": "topic-bis605-development-technologies-01",
    "version": "topic-bis605-development-technologies-02",
    "html": "topic-bis605-frontend-01",
    "css": "topic-bis605-frontend-02",
    "dom": "topic-bis605-frontend-03",
    "server": "topic-bis605-backend-data-api-cloud-mobile-01",
    "api": "topic-bis605-backend-data-api-cloud-mobile-02",
    "cloud": "topic-bis605-backend-data-api-cloud-mobile-03",
    "protocol": "topic-bis606-communications-foundations-01",
    "encapsulation": "topic-bis606-communications-foundations-02",
    "medium": "topic-bis606-communications-foundations-03",
    "frame": "topic-bis606-data-link-and-tcpip-01",
    "routing": "topic-bis606-data-link-and-tcpip-02",
    "lan": "topic-bis606-lan-wan-internet-01",
    "network_management": "topic-bis606-lan-wan-internet-03",
}

# Exact concepts are deliberately phrased without any answer choice or answer key.
CONCEPTS = {
    1: ("Product funding and customer roles", "บทบาทผู้ให้ทุนและลูกค้าของผลิตภัณฑ์"),
    2: ("Product Owner and stakeholder representation", "เจ้าของผลิตภัณฑ์และการเป็นตัวแทนผู้มีส่วนได้ส่วนเสีย"),
    3: ("Subject-matter expert role", "บทบาทผู้เชี่ยวชาญเฉพาะด้าน"),
    4: ("Project governance and status reporting", "ธรรมาภิบาลโครงการและการรายงานสถานะ"),
    5: ("Interview-question preparation", "การเตรียมคำถามสัมภาษณ์"),
    6: ("Opening an information-gathering session", "การเปิดการประชุมเก็บรวบรวมข้อมูล"),
    7: ("Business-analyst competencies", "สมรรถนะของนักวิเคราะห์ธุรกิจ"),
    8: ("Business analyst and project manager responsibilities", "ความรับผิดชอบของนักวิเคราะห์ธุรกิจกับผู้จัดการโครงการ"),
    9: ("Business analyst as a change agent", "นักวิเคราะห์ธุรกิจในฐานะตัวแทนการเปลี่ยนแปลง"),
    10: ("Question selection and business context", "การเลือกคำถามและบริบททางธุรกิจ"),
    19: ("Business analyst versus systems analyst", "นักวิเคราะห์ธุรกิจกับนักวิเคราะห์ระบบ"),
    20: ("Interview conduct and corrective probing", "การดำเนินการสัมภาษณ์และการถามเจาะเพื่อแก้ความคลาดเคลื่อน"),
    21: ("Distribution shape from a plotted pattern", "รูปร่างการแจกแจงจากรูปแบบที่พล็อต"),
    22: ("Regression goodness-of-fit comparison", "การเปรียบเทียบความพอดีของแบบจำลองถดถอย"),
    23: ("Regression coefficient significance", "นัยสำคัญของสัมประสิทธิ์ถดถอย"),
    24: ("Median location in a boxplot", "ตำแหน่งมัธยฐานในแผนภาพกล่อง"),
    25: ("Digital transformation", "การเปลี่ยนผ่านสู่ดิจิทัล"),
    26: ("Sources of competitive advantage", "แหล่งที่มาของความได้เปรียบทางการแข่งขัน"),
    27: ("Primary and support business processes", "กระบวนการธุรกิจหลักและกระบวนการสนับสนุน"),
    28: ("Differentiation strategy", "กลยุทธ์สร้างความแตกต่าง"),
    29: ("KPI alignment with responsiveness", "การจัดตัวชี้วัดให้สอดคล้องกับการตอบสนอง"),
    30: ("Effectiveness versus efficiency", "ประสิทธิผลกับประสิทธิภาพ"),
    31: ("Balanced Scorecard measures and targets", "ตัววัดและค่าเป้าหมายใน Balanced Scorecard"),
    32: ("Z-score interpretation for outliers", "การตีความคะแนนมาตรฐานเพื่อระบุค่าผิดปกติ"),
    33: ("Median calculation for an even-sized dataset", "การคำนวณมัธยฐานของชุดข้อมูลจำนวนคู่"),
    34: ("Random-variable definition", "ความหมายของตัวแปรสุ่ม"),
    35: ("Z-score input requirements", "ข้อมูลที่จำเป็นในการคำนวณคะแนนมาตรฐาน"),
    36: ("Marketing data mart purpose", "วัตถุประสงค์ของดาต้ามาร์ตการตลาด"),
    37: ("Business intelligence versus data mining", "ธุรกิจอัจฉริยะกับการทำเหมืองข้อมูล"),
    38: ("Big data versus blockchain", "บิ๊กดาต้ากับบล็อกเชน"),
    39: ("Discrete variables and the normal distribution", "ตัวแปรไม่ต่อเนื่องกับการแจกแจงปกติ"),
    40: ("Strategic decision level", "ระดับการตัดสินใจเชิงกลยุทธ์"),
    41: ("Concentric diversification", "การกระจายธุรกิจแบบสัมพันธ์"),
    42: ("Social marketing", "การตลาดเพื่อสังคม"),
    43: ("Promotion within the marketing mix", "การส่งเสริมการตลาดในส่วนประสมการตลาด"),
    44: ("Segmentation-targeting-positioning sequence", "ลำดับการแบ่งส่วนตลาด การเลือกตลาดเป้าหมาย และการวางตำแหน่ง"),
    45: ("Marketing-channel participants", "ผู้มีส่วนร่วมในช่องทางการตลาด"),
    46: ("Customer-satisfaction success factors", "ปัจจัยความสำเร็จของความพึงพอใจลูกค้า"),
    47: ("Pricing across the product life cycle", "การกำหนดราคาตลอดวงจรชีวิตผลิตภัณฑ์"),
    48: ("Marketing as value exchange", "การตลาดในฐานะกระบวนการแลกเปลี่ยนคุณค่า"),
    49: ("Competitive advantage", "ความได้เปรียบทางการแข่งขัน"),
    50: ("Marketing concept and organizational goals", "แนวคิดการตลาดและเป้าหมายองค์การ"),
    51: ("Market-development growth strategy", "กลยุทธ์การเติบโตด้วยการพัฒนาตลาด"),
    52: ("Line extension", "การขยายสายผลิตภัณฑ์"),
    53: ("Brand extension", "การขยายตราสินค้า"),
    54: ("Industrial-product classification", "การจำแนกผลิตภัณฑ์อุตสาหกรรม"),
    55: ("Product-mix length", "ความยาวของส่วนประสมผลิตภัณฑ์"),
    56: ("Advertising reach characteristics", "ลักษณะการเข้าถึงของการโฆษณา"),
    57: ("Service inseparability", "ลักษณะไม่สามารถแยกการผลิตกับการบริโภคบริการ"),
    58: ("Push promotion strategy", "กลยุทธ์ส่งเสริมการตลาดแบบผลัก"),
    59: ("Horizontal integration", "การรวมกิจการในแนวราบ"),
    60: ("Demographic market segmentation", "การแบ่งส่วนตลาดตามประชากรศาสตร์"),
    61: ("Enterprise application integration", "การบูรณาการแอปพลิเคชันระดับองค์การ"),
    62: ("Primary keys and candidate keys", "คีย์หลักและคีย์ตัวเลือก"),
    63: ("Electronic communication and collaboration tools", "เครื่องมือสื่อสารและทำงานร่วมกันทางอิเล็กทรอนิกส์"),
    64: ("Information technology for alliance strategy", "เทคโนโลยีสารสนเทศเพื่อกลยุทธ์พันธมิตร"),
    65: ("Commercial off-the-shelf software", "ซอฟต์แวร์สำเร็จรูปเชิงพาณิชย์"),
    66: ("Database-system components", "องค์ประกอบของระบบฐานข้อมูล"),
    67: ("Decision-support analytical models", "แบบจำลองวิเคราะห์เพื่อสนับสนุนการตัดสินใจ"),
    68: ("Customer relationship management", "การบริหารความสัมพันธ์ลูกค้า"),
    69: ("External, conceptual, and internal database models", "แบบจำลองฐานข้อมูลระดับภายนอก แนวคิด และภายใน"),
    70: ("Information-system activities", "กิจกรรมของระบบสารสนเทศ"),
    71: ("Electronic business", "ธุรกิจอิเล็กทรอนิกส์"),
    72: ("Information quality and granularity", "คุณภาพและระดับรายละเอียดของสารสนเทศ"),
    73: ("Multivalued-attribute notation", "สัญลักษณ์แอตทริบิวต์หลายค่า"),
    74: ("OLAP slice-and-dice operations", "การดำเนินการ slice และ dice ใน OLAP"),
    75: ("SQL definition and language roles", "ความหมายและบทบาทของภาษา SQL"),
    76: ("Fundamental roles of information systems", "บทบาทพื้นฐานของระบบสารสนเทศ"),
    77: ("Required versus optional attributes", "แอตทริบิวต์บังคับกับแอตทริบิวต์ที่เลือกได้"),
    78: ("Management decision-support system types", "ประเภทระบบสารสนเทศเพื่อสนับสนุนการตัดสินใจของผู้บริหาร"),
    79: ("INTERSECT set operation", "การดำเนินการเซต INTERSECT"),
    80: ("UNION set operation", "การดำเนินการเซต UNION"),
    81: ("System-architecture scope", "ขอบเขตของสถาปัตยกรรมระบบ"),
    82: ("Client-server architecture of the Web", "สถาปัตยกรรมไคลเอนต์-เซิร์ฟเวอร์ของเว็บ"),
    83: ("Modularity as a design principle", "มอดูลาริตีในฐานะหลักการออกแบบ"),
    84: ("Software-design objectives", "วัตถุประสงค์ของการออกแบบซอฟต์แวร์"),
    85: ("Software-development process activities", "กิจกรรมในกระบวนการพัฒนาซอฟต์แวร์"),
    86: ("Web-server request and response handling", "การรับคำขอและส่งผลตอบกลับของเว็บเซิร์ฟเวอร์"),
    87: ("Browser and database responsibilities", "หน้าที่ของเว็บเบราว์เซอร์และฐานข้อมูล"),
    88: ("Cloud-development benefits and constraints", "ประโยชน์และข้อจำกัดของการพัฒนาบนคลาวด์"),
    89: ("Front-end technology classification", "การจำแนกเทคโนโลยีส่วนหน้า"),
    90: ("Back-end technology classification", "การจำแนกเทคโนโลยีส่วนหลัง"),
    91: ("Mobile-development frameworks", "เฟรมเวิร์กสำหรับพัฒนาอุปกรณ์เคลื่อนที่"),
    92: ("API scope and contract", "ขอบเขตและข้อตกลงของ API"),
    93: ("Internet of Things components", "องค์ประกอบของอินเทอร์เน็ตของสรรพสิ่ง"),
    94: ("Software-development tool categories", "หมวดหมู่เครื่องมือพัฒนาซอฟต์แวร์"),
    95: ("User-interface prototyping tools", "เครื่องมือสร้างต้นแบบส่วนติดต่อผู้ใช้"),
    96: ("Software-modeling languages", "ภาษาสำหรับสร้างแบบจำลองซอฟต์แวร์"),
    97: ("Object-oriented system diagrams", "แผนภาพระบบเชิงวัตถุ"),
    98: ("HTML inline style syntax", "ไวยากรณ์สไตล์แบบอินไลน์ใน HTML"),
    99: ("JavaScript function declarations", "การประกาศฟังก์ชันใน JavaScript"),
    100: ("CSS layout techniques", "เทคนิคการจัดวางด้วย CSS"),
    101: ("Five-layer Internet model", "แบบจำลองอินเทอร์เน็ตห้าชั้น"),
    102: ("Host, client-server, and tiered architectures", "สถาปัตยกรรมโฮสต์ ไคลเอนต์-เซิร์ฟเวอร์ และหลายชั้น"),
    103: ("SMTP delivery and email storage", "การส่งอีเมลด้วย SMTP และตำแหน่งจัดเก็บ"),
    104: ("Wavelength-division multiplexing and fiber", "การมัลติเพล็กซ์แบ่งความยาวคลื่นกับใยแก้วนำแสง"),
    105: ("Manchester encoding transitions", "การเปลี่ยนระดับสัญญาณในการเข้ารหัสแมนเชสเตอร์"),
    106: ("Sliding-window flow control and ARQ", "การควบคุมการไหลแบบหน้าต่างเลื่อนและ ARQ"),
    107: ("Ethernet MAC address length", "ความยาวที่อยู่ MAC ของอีเทอร์เน็ต"),
    108: ("Quality of Service prioritization", "การจัดลำดับความสำคัญด้วยคุณภาพการให้บริการ"),
    109: ("Exterior routing and BGP", "การกำหนดเส้นทางภายนอกและ BGP"),
    110: ("IPv6 as the IPv4 successor", "IPv6 ในฐานะรุ่นสืบทอดจาก IPv4"),
    111: ("Network-design cost assessment and proposal approval", "การประเมินต้นทุนและการขออนุมัติข้อเสนอออกแบบเครือข่าย"),
    112: ("Wireless LAN security protocols", "โพรโทคอลความมั่นคงปลอดภัยของ LAN ไร้สาย"),
    113: ("Chassis-switch flexibility", "ความยืดหยุ่นของสวิตช์แบบแชสซี"),
}


def group(
    group_id: str,
    question_numbers: list[int],
    topic: str,
    heading_en: str,
    heading_th: str,
    content_en: list[str],
    content_th: list[str],
    origin: str,
    skill: str,
    prerequisites: list[str] | None = None,
) -> dict:
    assert len(content_en) == len(content_th)
    return {
        "group_id": group_id,
        "question_numbers": question_numbers,
        "topic_id": topic,
        "heading_en": heading_en,
        "heading_th": heading_th,
        "content_en": content_en,
        "content_th": content_th,
        "origin": origin,
        "skill": skill,
        "prerequisites": prerequisites or [],
    }


GROUPS = [
    group("ba-stakeholder-roles", [1, 2, 3, 4], TOPIC["ba"],
          "Stakeholder roles around a business-analysis initiative",
          "บทบาทผู้มีส่วนได้ส่วนเสียรอบงานวิเคราะห์ธุรกิจ",
          [
              "Separate the economic customer or sponsor who funds an initiative from the people who use, own, govern, or deliver its solution.",
              "A Product Owner represents product value and stakeholder priorities to a delivery team; a subject-matter expert contributes deep domain knowledge.",
              "Project managers coordinate delivery constraints and status, while business and IT management provide governance, resources, and escalation paths.",
              "Determine a role from its accountability and decision rights, not merely from who attends a meeting or uses the system.",
          ],
          [
              "แยกผู้ให้ทุนหรือลูกค้าเชิงเศรษฐกิจออกจากผู้ใช้ เจ้าของ ผู้กำกับดูแล และผู้ส่งมอบโซลูชัน",
              "Product Owner เป็นตัวแทนคุณค่าและลำดับความสำคัญของผู้มีส่วนได้ส่วนเสียต่อทีมส่งมอบ ส่วนผู้เชี่ยวชาญเฉพาะด้านให้ความรู้เชิงลึกของโดเมน",
              "ผู้จัดการโครงการประสานข้อจำกัดและสถานะการส่งมอบ ขณะที่ฝ่ายบริหารธุรกิจและไอทีทำหน้าที่กำกับดูแล จัดทรัพยากร และรับเรื่องยกระดับ",
              "พิจารณาบทบาทจากความรับผิดชอบและสิทธิการตัดสินใจ ไม่ใช่เพียงผู้ที่เข้าประชุมหรือใช้ระบบ",
          ], "EXTERNAL_AUTHORITATIVE", "distinguish stakeholder accountabilities"),
    group("elicitation-planning", [5, 6, 10, 20], TOPIC["elicitation"],
          "Plan, open, and conduct an information-gathering session",
          "การวางแผน เปิด และดำเนินการประชุมเก็บรวบรวมข้อมูล",
          [
              "Prepare an objective, participant list, question sequence, and recording method before an interview; written questions improve coverage and follow-up.",
              "Open by explaining the business problem, intended outcome, participant relevance, time boundary, and how the information will be used.",
              "Choose open, closed, probing, and confirming questions according to the information needed and the respondent's context.",
              "Listen without premature correction, then test contradictions respectfully through paraphrasing, examples, and evidence-based follow-up.",
          ],
          [
              "เตรียมวัตถุประสงค์ รายชื่อผู้เข้าร่วม ลำดับคำถาม และวิธีบันทึกก่อนสัมภาษณ์ การเขียนคำถามช่วยให้ครอบคลุมและติดตามประเด็นได้",
              "เริ่มด้วยการอธิบายปัญหาธุรกิจ ผลลัพธ์ที่ต้องการ ความเกี่ยวข้องของผู้เข้าร่วม ขอบเขตเวลา และการนำข้อมูลไปใช้",
              "เลือกคำถามปลายเปิด ปลายปิด เจาะลึก และยืนยันให้เหมาะกับข้อมูลที่ต้องการและบริบทของผู้ตอบ",
              "ฟังโดยไม่รีบแก้ผู้ตอบ แล้วตรวจสอบข้อขัดแย้งอย่างให้เกียรติด้วยการทวนความ ตัวอย่าง และคำถามติดตามที่อิงหลักฐาน",
          ], "EXTERNAL_AUTHORITATIVE", "plan and evaluate elicitation"),
    group("ba-competencies", [7, 9], TOPIC["ba"],
          "Business-analyst competencies and change responsibility",
          "สมรรถนะและความรับผิดชอบต่อการเปลี่ยนแปลงของนักวิเคราะห์ธุรกิจ",
          [
              "Core competencies combine analytical thinking, communication, facilitation, domain learning, negotiation, and validation of needs and outcomes.",
              "A business analyst enables change by discovering needs, aligning stakeholders, clarifying requirements, and evaluating whether the solution creates value.",
              "Acceptance support can involve the analyst because it validates requirements; ownership of schedule and budget normally belongs to project management.",
          ],
          [
              "สมรรถนะหลักผสานการคิดวิเคราะห์ การสื่อสาร การอำนวยความสะดวก การเรียนรู้โดเมน การเจรจา และการตรวจสอบความต้องการกับผลลัพธ์",
              "นักวิเคราะห์ธุรกิจเอื้อให้เกิดการเปลี่ยนแปลงด้วยการค้นหาความต้องการ ประสานผู้มีส่วนได้ส่วนเสีย ทำข้อกำหนดให้ชัด และประเมินคุณค่าของโซลูชัน",
              "นักวิเคราะห์อาจสนับสนุนการทดสอบการยอมรับเพราะเป็นการตรวจสอบข้อกำหนด ส่วนเจ้าของกำหนดการและงบประมาณมักเป็นผู้จัดการโครงการ",
          ], "EXTERNAL_AUTHORITATIVE", "classify analyst competencies", [TOPIC["ba"]]),
    group("ba-role-boundaries", [8, 19], TOPIC["ba"],
          "Business analyst, systems analyst, and project manager",
          "นักวิเคราะห์ธุรกิจ นักวิเคราะห์ระบบ และผู้จัดการโครงการ",
          [
              "Business analysis concentrates on why change is needed and what outcomes and capabilities the organization requires.",
              "Systems analysis translates the required capability into a feasible system view, including behavior, information, interfaces, and technical constraints.",
              "Project management coordinates the temporary delivery effort through scope, schedule, cost, risk, resources, and stakeholder reporting.",
              "Real projects overlap, so classify a statement by its primary accountability rather than assuming rigid job-title boundaries.",
          ],
          [
              "การวิเคราะห์ธุรกิจเน้นเหตุผลที่ต้องเปลี่ยนแปลง รวมถึงผลลัพธ์และขีดความสามารถที่องค์การต้องการ",
              "การวิเคราะห์ระบบแปลงขีดความสามารถที่ต้องการเป็นมุมมองระบบที่เป็นไปได้ ครอบคลุมพฤติกรรม ข้อมูล ส่วนเชื่อมต่อ และข้อจำกัดทางเทคนิค",
              "การบริหารโครงการประสานงานส่งมอบชั่วคราวผ่านขอบเขต เวลา ต้นทุน ความเสี่ยง ทรัพยากร และการรายงานต่อผู้มีส่วนได้ส่วนเสีย",
              "งานจริงมีส่วนทับซ้อน จึงควรจำแนกข้อความจากความรับผิดชอบหลัก ไม่ใช่ยึดขอบเขตชื่อตำแหน่งอย่างตายตัว",
          ], "EXTERNAL_AUTHORITATIVE", "compare professional responsibilities"),
    group("descriptive-distributions", [21, 24, 33, 34], TOPIC["std"],
          "Read distributions, boxplots, medians, and random variables",
          "การอ่านการแจกแจง แผนภาพกล่อง มัธยฐาน และตัวแปรสุ่ม",
          [
              "Distribution shape describes symmetry, skew, modality, and unusual values; assess the entire plotted pattern before assigning a label.",
              "In a boxplot, the line inside the box marks the median, box edges mark quartiles, and whiskers show a stated range convention.",
              "For an even number of ordered observations, the median is the mean of the two central values.",
              "A random variable maps each outcome of a random process to a numerical value; it may be discrete or continuous.",
          ],
          [
              "รูปร่างการแจกแจงอธิบายความสมมาตร ความเบ้ จำนวนฐานนิยม และค่าผิดปกติ ควรพิจารณารูปแบบทั้งกราฟก่อนตั้งชื่อ",
              "ในแผนภาพกล่อง เส้นภายในกล่องคือมัธยฐาน ขอบกล่องคือควอร์ไทล์ และหนวดแสดงช่วงตามกติกาที่ระบุ",
              "เมื่อข้อมูลเรียงลำดับมีจำนวนคู่ มัธยฐานคือค่าเฉลี่ยของสองค่าตรงกลาง",
              "ตัวแปรสุ่มจับคู่ผลลัพธ์แต่ละแบบของกระบวนการสุ่มกับค่าตัวเลข และอาจเป็นแบบไม่ต่อเนื่องหรือต่อเนื่อง",
          ], "COURSE_MATERIAL", "interpret statistical representations"),
    group("regression-fit", [22], TOPIC["residual"],
          "Compare regression models without mixing criteria",
          "เปรียบเทียบแบบจำลองถดถอยโดยไม่ปะปนเกณฑ์",
          [
              "Goodness of fit and predictive error answer different questions: adjusted R-squared summarizes explained variation with a complexity penalty, while standard error or RMSE summarizes residual magnitude.",
              "Compare a metric only when the response variable, data split, units, and calculation convention are the same.",
              "When one model looks better on fit but worse on error, the evidence is mixed; state the tradeoff instead of inventing a single winner.",
          ],
          [
              "ความพอดีกับความคลาดเคลื่อนในการพยากรณ์ตอบคนละคำถาม adjusted R-squared สรุปความแปรปรวนที่อธิบายได้พร้อมลงโทษความซับซ้อน ส่วน standard error หรือ RMSE สรุปขนาดส่วนเหลือ",
              "ควรเปรียบเทียบตัวชี้วัดเมื่อใช้ตัวแปรตาม ชุดข้อมูล หน่วย และวิธีคำนวณเดียวกันเท่านั้น",
              "หากแบบจำลองหนึ่งดีกว่าด้านความพอดีแต่อีกด้านด้อยกว่า หลักฐานถือว่าผสมกัน ควรระบุข้อแลกเปลี่ยนแทนการสร้างผู้ชนะเพียงหนึ่งเดียว",
          ], "SUPPLEMENTARY_EXPLANATION", "evaluate conflicting model evidence", [TOPIC["depvar"], TOPIC["coefficient"]]),
    group("regression-significance", [23], TOPIC["coefficient"],
          "Interpret coefficient significance and confidence output",
          "การตีความนัยสำคัญของสัมประสิทธิ์และผลลัพธ์ช่วงความเชื่อมั่น",
          [
              "A coefficient estimates direction and magnitude conditional on the other predictors; its uncertainty is evaluated with a valid standard error, test statistic, p-value, or confidence interval.",
              "A confidence interval containing zero does not support a nonzero effect at the corresponding level.",
              "Malformed percentages, missing labels, or internally inconsistent regression output must be treated as insufficient evidence and reviewed before variable removal.",
          ],
          [
              "สัมประสิทธิ์ประมาณทิศทางและขนาดเมื่อควบคุมตัวทำนายอื่น ความไม่แน่นอนประเมินด้วยค่าคลาดเคลื่อนมาตรฐาน สถิติทดสอบ ค่า p หรือช่วงความเชื่อมั่นที่ถูกต้อง",
              "ช่วงความเชื่อมั่นที่ครอบคลุมศูนย์ไม่สนับสนุนผลที่ต่างจากศูนย์ ณ ระดับที่สอดคล้องกัน",
              "เปอร์เซ็นต์ผิดรูป ป้ายกำกับหาย หรือผลถดถอยขัดแย้งกันภายในเป็นหลักฐานไม่เพียงพอและต้องตรวจทานก่อนตัดตัวแปร",
          ], "SUPPLEMENTARY_EXPLANATION", "judge statistical evidence quality", [TOPIC["depvar"]]),
    group("z-score", [32], TOPIC["z"],
          "Compute and interpret a Z-score",
          "การคำนวณและตีความคะแนนมาตรฐาน",
          [
              "Use z = (x − mean) / standard deviation after confirming that all three values use compatible units.",
              "The sign shows whether the observation lies above or below the mean; the absolute magnitude shows distance in standard-deviation units.",
              "An outlier rule such as |z| greater than 2 or 3 is a stated convention, not an automatic universal law.",
          ],
          [
              "ใช้ z = (x − ค่าเฉลี่ย) / ส่วนเบี่ยงเบนมาตรฐาน หลังยืนยันว่าค่าทั้งสามใช้หน่วยที่เข้ากัน",
              "เครื่องหมายบอกว่าค่าสังเกตอยู่เหนือหรือต่ำกว่าค่าเฉลี่ย และค่าสัมบูรณ์บอกระยะห่างในหน่วยส่วนเบี่ยงเบนมาตรฐาน",
              "เกณฑ์ค่าผิดปกติ เช่น |z| มากกว่า 2 หรือ 3 เป็นข้อตกลงที่ต้องระบุ ไม่ใช่กฎสากลอัตโนมัติ",
          ], "COURSE_MATERIAL", "calculate and interpret a standardized value", [TOPIC["std"]]),
    group("z-score-missing-input", [35], TOPIC["z"],
          "Recognize when a Z-score cannot be calculated",
          "การระบุกรณีที่ไม่สามารถคำนวณคะแนนมาตรฐาน",
          [
              "A numerical Z-score requires an observation x, a mean, and a nonzero standard deviation.",
              "If the observation is absent, the expression can be stated symbolically but no unique numerical result exists.",
              "Do not infer a missing observation from answer choices; identify the missing input and request correction.",
          ],
          [
              "คะแนนมาตรฐานเชิงตัวเลขต้องมีค่าสังเกต x ค่าเฉลี่ย และส่วนเบี่ยงเบนมาตรฐานที่ไม่เป็นศูนย์",
              "หากไม่มีค่าสังเกต สามารถเขียนนิพจน์เชิงสัญลักษณ์ได้แต่ไม่มีผลลัพธ์ตัวเลขเพียงค่าเดียว",
              "ไม่ควรอนุมานค่าสังเกตที่หายไปจากตัวเลือก แต่ควรระบุข้อมูลที่ขาดและขอให้แก้ไข",
          ], "SUPPLEMENTARY_EXPLANATION", "identify insufficient quantitative information", [TOPIC["std"]]),
    group("normal-variable-types", [39], TOPIC["expected"],
          "Discrete variables and continuous normal models",
          "ตัวแปรไม่ต่อเนื่องและแบบจำลองปกติต่อเนื่อง",
          [
              "A discrete random variable takes countable values; a continuous random variable can take values across an interval.",
              "The normal distribution is a continuous probability model. A discrete distribution may look bell-shaped or be approximated by a normal model under stated conditions, but it is not literally a discrete normal distribution in elementary usage.",
              "Check the variable type and the assumptions before selecting a probability model.",
          ],
          [
              "ตัวแปรสุ่มไม่ต่อเนื่องรับค่าแบบนับได้ ส่วนตัวแปรสุ่มต่อเนื่องรับค่าได้ตลอดช่วง",
              "การแจกแจงปกติเป็นแบบจำลองความน่าจะเป็นต่อเนื่อง การแจกแจงไม่ต่อเนื่องอาจมีรูปคล้ายระฆังหรือประมาณด้วยแบบจำลองปกติภายใต้เงื่อนไข แต่โดยพื้นฐานไม่เรียกว่าแจกแจงปกติไม่ต่อเนื่องโดยตรง",
              "ตรวจสอบชนิดตัวแปรและสมมติฐานก่อนเลือกแบบจำลองความน่าจะเป็น",
          ], "EXTERNAL_AUTHORITATIVE", "distinguish probability model types"),
    group("digital-strategy", [25, 26], TOPIC["competitive"],
          "Digital transformation and competitive advantage",
          "การเปลี่ยนผ่านดิจิทัลและความได้เปรียบทางการแข่งขัน",
          [
              "Digitization converts information, digitalization improves a process with digital technology, and digital transformation changes capabilities, operating models, or value creation.",
              "Competitive advantage arises when a distinctive capability fits an external opportunity and creates value that rivals cannot easily match.",
              "Technology alone is not an advantage unless it changes customer value, cost, speed, quality, learning, or another defensible outcome.",
          ],
          [
              "digitization คือการแปลงข้อมูลเป็นดิจิทัล digitalization คือการปรับปรุงกระบวนการด้วยเทคโนโลยี และ digital transformation คือการเปลี่ยนขีดความสามารถ รูปแบบดำเนินงาน หรือการสร้างคุณค่า",
              "ความได้เปรียบทางการแข่งขันเกิดเมื่อขีดความสามารถเฉพาะสอดคล้องกับโอกาสภายนอกและสร้างคุณค่าที่คู่แข่งเลียนแบบได้ยาก",
              "เทคโนโลยีเพียงอย่างเดียวไม่ใช่ความได้เปรียบ เว้นแต่จะเปลี่ยนคุณค่าลูกค้า ต้นทุน ความเร็ว คุณภาพ การเรียนรู้ หรือผลลัพธ์ที่ป้องกันได้",
          ], "EXTERNAL_AUTHORITATIVE", "differentiate digital and strategic outcomes"),
    group("differentiation-decisions", [28, 40], TOPIC["competitive"],
          "Differentiation and strategic decision levels",
          "การสร้างความแตกต่างและระดับการตัดสินใจเชิงกลยุทธ์",
          [
              "Differentiation seeks valued uniqueness through features, quality, service, innovation, brand, or experience, and must justify any added cost.",
              "Strategic decisions are long-term, organization-wide, uncertain, and usually made by senior leadership; tactical decisions translate strategy into plans, while operational decisions control daily work.",
              "Classify an action by its intended competitive outcome and time horizon, not by the technology named in the action.",
          ],
          [
              "กลยุทธ์สร้างความแตกต่างมุ่งสร้างเอกลักษณ์ที่ลูกค้าให้คุณค่าผ่านคุณลักษณะ คุณภาพ บริการ นวัตกรรม ตราสินค้า หรือประสบการณ์ และต้องคุ้มกับต้นทุนเพิ่ม",
              "การตัดสินใจเชิงกลยุทธ์มีระยะยาว ครอบคลุมทั้งองค์การ ไม่แน่นอน และมักอยู่ที่ผู้บริหารระดับสูง ส่วนระดับยุทธวิธีแปลงกลยุทธ์เป็นแผน และระดับปฏิบัติการควบคุมงานประจำวัน",
              "จำแนกการกระทำจากผลการแข่งขันและกรอบเวลาที่ตั้งใจ ไม่ใช่จากชื่อเทคโนโลยีในข้อความ",
          ], "COURSE_MATERIAL", "classify competitive actions and decision levels", [TOPIC["competitive"]]),
    group("process-effectiveness", [27, 30], TOPIC["process"],
          "Primary processes, support processes, effectiveness, and efficiency",
          "กระบวนการหลัก กระบวนการสนับสนุน ประสิทธิผล และประสิทธิภาพ",
          [
              "Primary processes directly create and deliver customer value; support processes enable them through resources, controls, information, and infrastructure.",
              "Effectiveness asks whether the intended outcome is achieved; efficiency asks how economically resources are converted into that outcome.",
              "A measure can improve efficiency while harming effectiveness, so identify the goal before choosing the metric.",
          ],
          [
              "กระบวนการหลักสร้างและส่งมอบคุณค่าแก่ลูกค้าโดยตรง ส่วนกระบวนการสนับสนุนเอื้อด้วยทรัพยากร การควบคุม สารสนเทศ และโครงสร้างพื้นฐาน",
              "ประสิทธิผลถามว่าบรรลุผลลัพธ์ที่ตั้งใจหรือไม่ ส่วนประสิทธิภาพถามว่าใช้ทรัพยากรเพื่อสร้างผลลัพธ์อย่างคุ้มค่าเพียงใด",
              "ตัววัดอาจทำให้ประสิทธิภาพดีขึ้นแต่ทำลายประสิทธิผลได้ จึงต้องระบุเป้าหมายก่อนเลือกตัวชี้วัด",
          ], "COURSE_MATERIAL", "classify processes and performance intent"),
    group("kpi-design", [29], TOPIC["kpi"],
          "Design a KPI that matches the critical success factor",
          "การออกแบบ KPI ให้ตรงกับปัจจัยความสำเร็จที่สำคัญ",
          [
              "Translate a critical success factor into an observable result, then define the metric, direction, unit, time window, owner, and data source.",
              "Responsiveness is normally measured by elapsed response or resolution time, service-level attainment, or delay frequency rather than by an unrelated output count.",
              "A useful KPI is specific enough to drive action and balanced against quality and unintended behavior.",
          ],
          [
              "แปลงปัจจัยความสำเร็จที่สำคัญเป็นผลลัพธ์ที่สังเกตได้ แล้วกำหนดตัววัด ทิศทาง หน่วย ช่วงเวลา ผู้รับผิดชอบ และแหล่งข้อมูล",
              "การตอบสนองมักวัดด้วยเวลาตอบกลับหรือเวลาปิดงาน การบรรลุระดับบริการ หรือความถี่ของความล่าช้า ไม่ใช่จำนวนผลงานที่ไม่เกี่ยวข้อง",
              "KPI ที่ดีต้องเฉพาะเจาะจงพอให้เกิดการลงมือทำ และสมดุลกับคุณภาพและพฤติกรรมที่ไม่พึงประสงค์",
          ], "COURSE_MATERIAL", "construct an aligned performance indicator", [TOPIC["process"]]),
    group("bsc-targets", [31], TOPIC["bsc"],
          "Balanced Scorecard objectives, measures, and targets",
          "วัตถุประสงค์ ตัววัด และค่าเป้าหมายใน Balanced Scorecard",
          [
              "An objective states the desired result, a measure quantifies progress, a target states the desired value and deadline, and an initiative is the action taken.",
              "A complete target needs a baseline or comparison, unit, direction, and time horizon.",
              "Check alignment across financial, customer, internal-process, and learning-and-growth perspectives rather than optimizing one measure in isolation.",
          ],
          [
              "วัตถุประสงค์ระบุผลที่ต้องการ ตัววัดทำให้ความก้าวหน้าเป็นปริมาณ ค่าเป้าหมายระบุค่าที่ต้องการพร้อมกำหนดเวลา และโครงการริเริ่มคือการลงมือทำ",
              "ค่าเป้าหมายที่สมบูรณ์ต้องมีฐานหรือจุดเปรียบเทียบ หน่วย ทิศทาง และกรอบเวลา",
              "ตรวจสอบความสอดคล้องระหว่างมุมมองการเงิน ลูกค้า กระบวนการภายใน และการเรียนรู้และเติบโต แทนการเพิ่มประสิทธิภาพตัววัดเดียว",
          ], "COURSE_MATERIAL", "distinguish scorecard elements", [TOPIC["kpi"]]),
    group("bi-data-technologies", [36, 37, 38], TOPIC["bi"],
          "Data marts, BI, data mining, big data, and blockchain",
          "ดาต้ามาร์ต BI การทำเหมืองข้อมูล บิ๊กดาต้า และบล็อกเชน",
          [
              "A data mart is a subject- or department-focused analytical data store; a marketing mart integrates customer, campaign, channel, and transaction data for analysis.",
              "Business intelligence organizes reporting, querying, dashboards, and decision information; data mining searches data for previously unknown patterns or predictive relationships.",
              "Big data concerns data scale, speed, variety, and processing; blockchain is a distributed ledger design for shared, tamper-evident records.",
              "Compare technologies by purpose, data structure, users, and decision problem—not by whether each uses large amounts of data.",
          ],
          [
              "ดาต้ามาร์ตคือแหล่งข้อมูลวิเคราะห์ที่มุ่งเฉพาะเรื่องหรือหน่วยงาน ดาต้ามาร์ตการตลาดรวมข้อมูลลูกค้า แคมเปญ ช่องทาง และธุรกรรมเพื่อการวิเคราะห์",
              "ธุรกิจอัจฉริยะจัดการรายงาน การสืบค้น แดชบอร์ด และสารสนเทศเพื่อการตัดสินใจ ส่วนการทำเหมืองข้อมูลค้นหารูปแบบหรือความสัมพันธ์เชิงพยากรณ์ที่ยังไม่ทราบ",
              "บิ๊กดาต้าเน้นขนาด ความเร็ว ความหลากหลาย และการประมวลผลข้อมูล ส่วนบล็อกเชนเป็นบัญชีแยกประเภทแบบกระจายสำหรับระเบียนร่วมที่ตรวจพบการแก้ไขได้",
              "เปรียบเทียบเทคโนโลยีจากวัตถุประสงค์ โครงสร้างข้อมูล ผู้ใช้ และปัญหาการตัดสินใจ ไม่ใช่เพียงทุกอย่างใช้ข้อมูลจำนวนมาก",
          ], "EXTERNAL_AUTHORITATIVE", "compare enterprise data technologies"),
    group("enterprise-integration", [61, 64], TOPIC["etl"],
          "Enterprise integration and information-enabled alliances",
          "การบูรณาการระดับองค์การและพันธมิตรที่ขับเคลื่อนด้วยสารสนเทศ",
          [
              "Enterprise application integration connects independently built applications through interfaces, messages, transformation, orchestration, and shared process rules.",
              "Alliance strategies use agreed data standards, secure interorganizational links, shared platforms, and coordinated workflows to reduce friction between partners.",
              "Integration is broader than data extraction: it can synchronize transactions and business processes while preserving ownership boundaries.",
          ],
          [
              "การบูรณาการแอปพลิเคชันระดับองค์การเชื่อมแอปพลิเคชันที่สร้างแยกกันผ่านส่วนเชื่อมต่อ ข้อความ การแปลงข้อมูล การประสานงาน และกฎกระบวนการร่วม",
              "กลยุทธ์พันธมิตรใช้มาตรฐานข้อมูลที่ตกลงร่วม การเชื่อมต่อระหว่างองค์การที่ปลอดภัย แพลตฟอร์มร่วม และขั้นตอนงานประสานกันเพื่อลดความติดขัด",
              "การบูรณาการกว้างกว่าการดึงข้อมูล เพราะอาจประสานธุรกรรมและกระบวนการธุรกิจโดยยังคงขอบเขตความเป็นเจ้าของ",
          ], "EXTERNAL_AUTHORITATIVE", "explain integration mechanisms", [TOPIC["data_quality"]]),
    group("electronic-collaboration", [63], TOPIC["bi"],
          "Classify electronic communication and collaboration tools",
          "การจำแนกเครื่องมือสื่อสารและทำงานร่วมกันทางอิเล็กทรอนิกส์",
          [
              "Communication tools exchange messages; collaboration tools additionally coordinate shared work, artifacts, decisions, presence, or workflow.",
              "Email and messaging may support collaboration, but category boundaries depend on the definition and feature set supplied in the course.",
              "When a question omits its taxonomy, state the classification rule before judging an example and retain the ambiguity for review.",
          ],
          [
              "เครื่องมือสื่อสารใช้แลกเปลี่ยนข้อความ ส่วนเครื่องมือทำงานร่วมกันเพิ่มการประสานงาน สิ่งส่งมอบ การตัดสินใจ สถานะผู้ใช้ หรือขั้นตอนงานร่วม",
              "อีเมลและข้อความอาจสนับสนุนการทำงานร่วมกัน แต่ขอบเขตหมวดหมู่ขึ้นกับคำนิยามและชุดคุณลักษณะที่รายวิชาใช้",
              "เมื่อคำถามไม่ระบุอนุกรมวิธาน ควรบอกกฎการจำแนกก่อนตัดสินตัวอย่างและคงสถานะกำกวมไว้เพื่อตรวจทาน",
          ], "SUPPLEMENTARY_EXPLANATION", "apply an explicit classification rule"),
    group("is-foundations", [70, 71, 76], TOPIC["bi"],
          "Information-system activities, e-business, and business roles",
          "กิจกรรมของระบบสารสนเทศ ธุรกิจอิเล็กทรอนิกส์ และบทบาททางธุรกิจ",
          [
              "An information system accepts input, processes and stores data, produces output, and uses feedback or control to support an organizational purpose.",
              "E-business uses Internet and related network technologies to perform or enable business processes; e-commerce is the transaction-focused subset.",
              "Information systems support operations, managerial decision making, collaboration, innovation, and competitive strategy at different levels.",
          ],
          [
              "ระบบสารสนเทศรับข้อมูลเข้า ประมวลผลและจัดเก็บ สร้างผลลัพธ์ และใช้ข้อเสนอแนะหรือการควบคุมเพื่อสนับสนุนวัตถุประสงค์องค์การ",
              "ธุรกิจอิเล็กทรอนิกส์ใช้อินเทอร์เน็ตและเทคโนโลยีเครือข่ายที่เกี่ยวข้องเพื่อดำเนินหรือสนับสนุนกระบวนการธุรกิจ ส่วนพาณิชย์อิเล็กทรอนิกส์เป็นส่วนย่อยที่เน้นธุรกรรม",
              "ระบบสารสนเทศสนับสนุนการปฏิบัติการ การตัดสินใจของผู้บริหาร การทำงานร่วมกัน นวัตกรรม และกลยุทธ์การแข่งขันในระดับต่าง ๆ",
          ], "EXTERNAL_AUTHORITATIVE", "relate system activities to organizational roles"),
    group("dss-crm", [67, 68, 78], TOPIC["bi"],
          "Decision support, analytical models, and CRM",
          "การสนับสนุนการตัดสินใจ แบบจำลองวิเคราะห์ และ CRM",
          [
              "Decision-support analysis commonly includes what-if analysis, sensitivity analysis, goal seeking, optimization, and simulation; each changes or solves different variables.",
              "Operational systems support routine transactions, management systems summarize control information, decision-support systems analyze semi-structured choices, and executive systems emphasize strategic views.",
              "Customer relationship management integrates customer data and processes across marketing, sales, and service to improve acquisition, retention, and value.",
          ],
          [
              "การวิเคราะห์เพื่อสนับสนุนการตัดสินใจมักมี what-if การวิเคราะห์ความไว การค้นหาค่าเป้าหมาย การหาค่าเหมาะที่สุด และการจำลอง ซึ่งเปลี่ยนหรือแก้ตัวแปรต่างกัน",
              "ระบบปฏิบัติการสนับสนุนธุรกรรมประจำ ระบบสารสนเทศเพื่อการจัดการสรุปข้อมูลควบคุม ระบบสนับสนุนการตัดสินใจวิเคราะห์ปัญหากึ่งมีโครงสร้าง และระบบผู้บริหารเน้นมุมมองเชิงกลยุทธ์",
              "การบริหารความสัมพันธ์ลูกค้าบูรณาการข้อมูลและกระบวนการลูกค้าระหว่างการตลาด การขาย และบริการ เพื่อปรับปรุงการได้มา การรักษา และคุณค่าลูกค้า",
          ], "EXTERNAL_AUTHORITATIVE", "classify decision and customer systems"),
    group("information-quality", [72], TOPIC["data_quality"],
          "Information quality and granularity",
          "คุณภาพสารสนเทศและระดับรายละเอียด",
          [
              "Useful information is accurate, complete, timely, relevant, consistent, accessible, and expressed at an appropriate level of detail.",
              "Granularity means the degree of detail: fine-grained data supports detailed analysis, while aggregated data supports concise summaries.",
              "More detail is not automatically better; quality depends on fitness for the decision and the user's context.",
          ],
          [
              "สารสนเทศที่มีประโยชน์ควรถูกต้อง ครบถ้วน ทันเวลา เกี่ยวข้อง สอดคล้อง เข้าถึงได้ และมีระดับรายละเอียดเหมาะสม",
              "granularity คือระดับความละเอียด ข้อมูลละเอียดสนับสนุนการวิเคราะห์เฉพาะเจาะจง ส่วนข้อมูลรวมสนับสนุนบทสรุปกระชับ",
              "รายละเอียดมากไม่ได้ดีกว่าเสมอ คุณภาพขึ้นกับความเหมาะสมต่อการตัดสินใจและบริบทผู้ใช้",
          ], "EXTERNAL_AUTHORITATIVE", "evaluate fitness of information"),
    group("olap-operations", [74], TOPIC["olap"],
          "OLAP navigation operations",
          "การดำเนินการนำทางใน OLAP",
          [
              "Slice fixes one dimension to inspect a smaller cube; dice selects ranges or members across several dimensions.",
              "Drill-down moves to finer detail, roll-up aggregates to a higher level, and pivot rotates the analytical view.",
              "Identify which dimensions and hierarchy levels change before naming an operation.",
          ],
          [
              "slice กำหนดค่ามิติหนึ่งเพื่อดูคิวบ์ย่อย ส่วน dice เลือกช่วงหรือสมาชิกในหลายมิติ",
              "drill-down ลงสู่รายละเอียด roll-up รวมขึ้นสู่ระดับสูง และ pivot หมุนมุมมองการวิเคราะห์",
              "ระบุมิติและระดับลำดับชั้นที่เปลี่ยนก่อนตั้งชื่อการดำเนินการ",
          ], "COURSE_MATERIAL", "distinguish multidimensional operations", [TOPIC["bi"]]),
    group("marketing-fundamentals", [42, 48, 50], TOPIC["mix"],
          "Marketing, the marketing concept, and social marketing",
          "การตลาด แนวคิดการตลาด และการตลาดเพื่อสังคม",
          [
              "Marketing creates, communicates, delivers, and exchanges value to satisfy needs while meeting legitimate organizational objectives.",
              "The marketing concept begins with customer needs and coordinates the organization to satisfy them profitably or sustainably.",
              "Social marketing applies marketing principles to influence voluntary behavior for individual and societal benefit; it is not simply promotion by a nonprofit.",
          ],
          [
              "การตลาดสร้าง สื่อสาร ส่งมอบ และแลกเปลี่ยนคุณค่าเพื่อตอบสนองความต้องการพร้อมบรรลุเป้าหมายองค์การที่ชอบธรรม",
              "แนวคิดการตลาดเริ่มจากความต้องการลูกค้าและประสานทั้งองค์การเพื่อตอบสนองอย่างทำกำไรหรือยั่งยืน",
              "การตลาดเพื่อสังคมใช้หลักการตลาดเพื่อจูงใจพฤติกรรมโดยสมัครใจให้เกิดประโยชน์ต่อบุคคลและสังคม ไม่ใช่เพียงการประชาสัมพันธ์ขององค์การไม่แสวงกำไร",
          ], "EXTERNAL_AUTHORITATIVE", "distinguish related marketing concepts"),
    group("stp-channels", [44, 45, 60], TOPIC["stp"],
          "STP sequence, segmentation bases, and channels",
          "ลำดับ STP ฐานการแบ่งส่วน และช่องทางการตลาด",
          [
              "Segmentation divides a market into meaningful groups, targeting evaluates and selects groups, and positioning designs the intended place in the customer's mind.",
              "Common consumer segmentation bases are geographic, demographic, psychographic, and behavioral; classify a variable by what it describes.",
              "Marketing channels connect producers and users through intermediaries such as wholesalers, retailers, agents, and digital platforms.",
          ],
          [
              "การแบ่งส่วนตลาดแบ่งตลาดเป็นกลุ่มที่มีความหมาย การเลือกตลาดเป้าหมายประเมินและเลือกกลุ่ม และการวางตำแหน่งออกแบบภาพที่ต้องการในใจลูกค้า",
              "ฐานแบ่งส่วนผู้บริโภคที่พบบ่อยคือภูมิศาสตร์ ประชากรศาสตร์ จิตวิทยา และพฤติกรรม ให้จำแนกตัวแปรจากสิ่งที่ตัวแปรอธิบาย",
              "ช่องทางการตลาดเชื่อมผู้ผลิตกับผู้ใช้ผ่านคนกลาง เช่น ผู้ค้าส่ง ผู้ค้าปลีก ตัวแทน และแพลตฟอร์มดิจิทัล",
          ], "EXTERNAL_AUTHORITATIVE", "apply the STP and channel framework"),
    group("customer-satisfaction", [46], TOPIC["alignment"],
          "Customer satisfaction as a multi-factor outcome",
          "ความพึงพอใจลูกค้าในฐานะผลลัพธ์จากหลายปัจจัย",
          [
              "Customer satisfaction compares perceived performance with expectations and can be affected by quality, service, value, convenience, trust, and recovery.",
              "A critical success factor is context-specific; it should be derived from the organization's value proposition and validated with customer evidence.",
              "If a question supplies no context or governing framework, several factors may be defensible and the item should remain unscored pending review.",
          ],
          [
              "ความพึงพอใจลูกค้าเปรียบเทียบผลงานที่รับรู้กับความคาดหวัง และได้รับผลจากคุณภาพ บริการ คุณค่า ความสะดวก ความไว้วางใจ และการแก้ปัญหา",
              "ปัจจัยความสำเร็จที่สำคัญขึ้นกับบริบท ควรได้มาจากข้อเสนอคุณค่าขององค์การและตรวจสอบด้วยหลักฐานจากลูกค้า",
              "หากคำถามไม่ให้บริบทหรือกรอบอ้างอิง หลายปัจจัยอาจสมเหตุผลและควรคงข้อสอบเป็นไม่ให้คะแนนจนกว่าจะตรวจทาน",
          ], "SUPPLEMENTARY_EXPLANATION", "evaluate under-specified success factors"),
    group("growth-strategies", [41, 51, 59], TOPIC["alternative"],
          "Growth alternatives: market development, diversification, and integration",
          "ทางเลือกการเติบโต: การพัฒนาตลาด การกระจายธุรกิจ และการรวมกิจการ",
          [
              "Market development offers existing products to new segments or geographic markets; product development offers new products to existing markets.",
              "Related or concentric diversification enters a new product-market area that shares technology, marketing, capabilities, or another strategic fit.",
              "Horizontal integration acquires or combines with activities at the same value-chain level; vertical integration moves upstream or downstream.",
          ],
          [
              "การพัฒนาตลาดนำผลิตภัณฑ์เดิมไปสู่กลุ่มหรือพื้นที่ใหม่ ส่วนการพัฒนาผลิตภัณฑ์นำผลิตภัณฑ์ใหม่สู่ตลาดเดิม",
              "การกระจายธุรกิจแบบสัมพันธ์เข้าสู่ผลิตภัณฑ์-ตลาดใหม่ที่มีเทคโนโลยี การตลาด ขีดความสามารถ หรือความสอดคล้องเชิงกลยุทธ์ร่วมกัน",
              "การรวมกิจการแนวราบซื้อหรือรวมกิจกรรมในระดับเดียวกันของห่วงโซ่คุณค่า ส่วนแนวดิ่งเคลื่อนไปต้นน้ำหรือปลายน้ำ",
          ], "EXTERNAL_AUTHORITATIVE", "classify corporate growth alternatives", [TOPIC["strategy"]]),
    group("product-portfolio", [47, 52, 53, 54, 55], TOPIC["mix"],
          "Product life cycle, branding, classification, and product mix",
          "วงจรชีวิตผลิตภัณฑ์ ตราสินค้า การจำแนก และส่วนประสมผลิตภัณฑ์",
          [
              "Product-life-cycle stages—introduction, growth, maturity, and decline—change competition, demand, communication, and pricing considerations.",
              "A line extension adds variants within an existing category; a brand extension applies an established brand to a different category.",
              "Industrial products are bought for production, operations, resale, or organizational use rather than personal consumption.",
              "Product-mix width counts product lines, length counts total items, depth counts variants, and consistency describes relatedness among lines.",
          ],
          [
              "ช่วงแนะนำ เติบโต อิ่มตัว และถดถอยของวงจรชีวิตผลิตภัณฑ์ทำให้การแข่งขัน อุปสงค์ การสื่อสาร และการกำหนดราคาเปลี่ยนไป",
              "การขยายสายผลิตภัณฑ์เพิ่มรูปแบบในหมวดเดิม ส่วนการขยายตราสินค้านำตราเดิมไปใช้กับหมวดที่ต่างออกไป",
              "ผลิตภัณฑ์อุตสาหกรรมซื้อเพื่อการผลิต การดำเนินงาน การขายต่อ หรือใช้ในองค์การ ไม่ใช่เพื่อบริโภคส่วนบุคคล",
              "ความกว้างของส่วนประสมคือจำนวนสาย ความยาวคือจำนวนรายการรวม ความลึกคือจำนวนรูปแบบ และความสอดคล้องคือระดับความเกี่ยวข้องระหว่างสาย",
          ], "EXTERNAL_AUTHORITATIVE", "differentiate product-management terms"),
    group("promotion-services", [43, 56, 57, 58], TOPIC["mix"],
          "Promotion, advertising, push strategy, and service inseparability",
          "การส่งเสริมการตลาด การโฆษณา กลยุทธ์ผลัก และบริการที่แยกไม่ได้",
          [
              "Promotion communicates value through advertising, personal selling, sales promotion, public relations, and direct or digital methods; changing a product feature belongs mainly to product decisions.",
              "Advertising provides paid, nonpersonal communication that can reach geographically dispersed audiences with a consistent message.",
              "A push strategy directs selling and trade incentives through channel members; a pull strategy stimulates end-customer demand.",
              "Service inseparability means production and consumption often occur together, making the provider and interaction part of the service experience.",
          ],
          [
              "การส่งเสริมการตลาดสื่อสารคุณค่าผ่านโฆษณา การขายโดยบุคคล การส่งเสริมการขาย การประชาสัมพันธ์ และวิธีตรงหรือดิจิทัล ส่วนการเปลี่ยนคุณลักษณะอยู่ที่การตัดสินใจด้านผลิตภัณฑ์เป็นหลัก",
              "การโฆษณาเป็นการสื่อสารแบบไม่ใช้บุคคลและมีค่าใช้จ่าย สามารถเข้าถึงผู้ชมที่กระจายตัวด้วยข้อความสม่ำเสมอ",
              "กลยุทธ์ผลักใช้การขายและสิ่งจูงใจทางการค้าผ่านสมาชิกช่องทาง ส่วนกลยุทธ์ดึงกระตุ้นอุปสงค์จากลูกค้าปลายทาง",
              "บริการที่แยกไม่ได้หมายถึงการผลิตและบริโภคมักเกิดพร้อมกัน ผู้ให้บริการและปฏิสัมพันธ์จึงเป็นส่วนของประสบการณ์",
          ], "EXTERNAL_AUTHORITATIVE", "classify marketing-mix and service decisions"),
    group("competitive-advantage-marketing", [49], TOPIC["strategy"],
          "Strategic fit and competitive advantage",
          "ความสอดคล้องเชิงกลยุทธ์และความได้เปรียบทางการแข่งขัน",
          [
              "Competitive advantage links an internal competency with an external opportunity to create superior customer or economic value.",
              "The advantage must be relevant, scarce or differentiated, and difficult to neutralize long enough to matter.",
              "A strength with no market value is not yet an advantage; an opportunity without capability is not yet captured.",
          ],
          [
              "ความได้เปรียบทางการแข่งขันเชื่อมสมรรถนะภายในกับโอกาสภายนอกเพื่อสร้างคุณค่าลูกค้าหรือเศรษฐกิจที่เหนือกว่า",
              "ความได้เปรียบต้องเกี่ยวข้อง มีความหายากหรือแตกต่าง และยากต่อการทำให้หมดความหมายเป็นเวลานานพอ",
              "จุดแข็งที่ตลาดไม่เห็นคุณค่ายังไม่ใช่ความได้เปรียบ และโอกาสที่ไม่มีขีดความสามารถรองรับยังไม่ถูกคว้าไว้",
          ], "EXTERNAL_AUTHORITATIVE", "evaluate strategic fit"),
    group("database-system", [66], TOPIC["dbms"],
          "The five-part database-system environment",
          "สภาพแวดล้อมระบบฐานข้อมูลห้าส่วน",
          [
              "A database-system environment combines hardware, software, people, procedures, and data.",
              "The DBMS is software within the environment; it is not the entire database system.",
              "Classify an example by function: stored facts are data, operating instructions are procedures, and administrators, designers, developers, and users are people.",
          ],
          [
              "สภาพแวดล้อมระบบฐานข้อมูลประกอบด้วยฮาร์ดแวร์ ซอฟต์แวร์ บุคลากร กระบวนการ และข้อมูล",
              "DBMS เป็นซอฟต์แวร์ส่วนหนึ่งของสภาพแวดล้อม ไม่ใช่ระบบฐานข้อมูลทั้งหมด",
              "จำแนกตัวอย่างจากหน้าที่ ข้อเท็จจริงที่เก็บคือข้อมูล คำสั่งการทำงานคือกระบวนการ และผู้ดูแล นักออกแบบ นักพัฒนา และผู้ใช้คือบุคลากร",
          ], "COURSE_MATERIAL", "classify database-system components", [TOPIC["database"]]),
    group("database-keys", [62], TOPIC["primary"],
          "Candidate keys, primary keys, and uniqueness",
          "คีย์ตัวเลือก คีย์หลัก และความเป็นเอกลักษณ์",
          [
              "A superkey uniquely identifies a row; a candidate key is a minimal superkey with no unnecessary attribute.",
              "One candidate key is selected as the primary key, while the remaining candidate keys are alternate keys.",
              "Test each proposed key for uniqueness and minimality using the schema rules, not just the small sample of rows shown.",
              "A composite key uses more than one attribute when no component alone guarantees uniqueness.",
          ],
          [
              "ซูเปอร์คีย์ระบุแถวได้ไม่ซ้ำ ส่วนคีย์ตัวเลือกคือซูเปอร์คีย์ขั้นต่ำที่ไม่มีแอตทริบิวต์เกินจำเป็น",
              "เลือกคีย์ตัวเลือกหนึ่งเป็นคีย์หลัก และคีย์ตัวเลือกที่เหลือเป็นคีย์สำรอง",
              "ทดสอบคีย์ที่เสนอทั้งความไม่ซ้ำและความเป็นขั้นต่ำจากกฎสคีมา ไม่ใช่เพียงตัวอย่างแถวจำนวนเล็กน้อย",
              "คีย์ประกอบใช้หลายแอตทริบิวต์เมื่อองค์ประกอบใดเพียงตัวเดียวไม่รับประกันความไม่ซ้ำ",
          ], "COURSE_MATERIAL", "derive keys from a relation", [TOPIC["logical"]]),
    group("database-levels", [69], TOPIC["conceptual"],
          "External, conceptual, and internal database levels",
          "ระดับภายนอก แนวคิด และภายในของฐานข้อมูล",
          [
              "The external level presents user- or application-specific views; the conceptual level describes the integrated logical structure for the organization.",
              "The internal level describes physical storage structures, access paths, files, pages, and indexes.",
              "Data independence reduces the effect of changes at one level on the level above it.",
          ],
          [
              "ระดับภายนอกนำเสนอมุมมองเฉพาะผู้ใช้หรือแอปพลิเคชัน ส่วนระดับแนวคิดอธิบายโครงสร้างตรรกะแบบบูรณาการขององค์การ",
              "ระดับภายในอธิบายโครงสร้างจัดเก็บทางกายภาพ เส้นทางเข้าถึง แฟ้ม เพจ และดัชนี",
              "ความเป็นอิสระของข้อมูลลดผลกระทบของการเปลี่ยนแปลงระดับหนึ่งต่อระดับที่อยู่เหนือขึ้นไป",
          ], "COURSE_MATERIAL", "distinguish abstraction levels", [TOPIC["database"]]),
    group("erd-attributes", [73, 77], TOPIC["cardinality"],
          "Attribute notation: multivalued, required, optional, and derived",
          "สัญลักษณ์แอตทริบิวต์หลายค่า บังคับ เลือกได้ และคำนวณได้",
          [
              "In Chen notation, a double oval denotes a multivalued attribute, a dashed oval denotes a derived attribute, and underlining commonly identifies a key.",
              "In Crow's Foot models, required versus optional participation or attributes is expressed with the notation and constraints defined by the modeling convention.",
              "Read the legend and distinguish attribute notation from relationship cardinality before classifying a symbol.",
          ],
          [
              "ในสัญลักษณ์ Chen วงรีสองชั้นแทนแอตทริบิวต์หลายค่า วงรีเส้นประแทนแอตทริบิวต์คำนวณได้ และการขีดเส้นใต้มักระบุคีย์",
              "ในแบบจำลอง Crow's Foot ความเป็นบังคับหรือเลือกได้ของการมีส่วนร่วมหรือแอตทริบิวต์แสดงด้วยสัญลักษณ์และข้อจำกัดตามแบบแผน",
              "อ่านคำอธิบายสัญลักษณ์และแยกสัญลักษณ์แอตทริบิวต์จากคาร์ดินาลิตีของความสัมพันธ์ก่อนจำแนก",
          ], "COURSE_MATERIAL", "interpret ERD notation", [TOPIC["conceptual"]]),
    group("sql-roles", [75], TOPIC["ddl"],
          "SQL language roles",
          "บทบาทของภาษา SQL",
          [
              "SQL is the standard family of statements for defining, querying, manipulating, controlling, and transacting with relational data.",
              "DDL defines structures, DML queries or changes rows, DCL manages privileges, and transaction-control statements manage commit and rollback boundaries.",
              "A DBMS executes SQL, but SQL itself is a language rather than the database or DBMS.",
          ],
          [
              "SQL คือกลุ่มคำสั่งมาตรฐานสำหรับกำหนด สืบค้น จัดการ ควบคุม และทำธุรกรรมกับข้อมูลเชิงสัมพันธ์",
              "DDL กำหนดโครงสร้าง DML สืบค้นหรือเปลี่ยนแถว DCL จัดการสิทธิ์ และคำสั่งควบคุมธุรกรรมจัดการขอบเขต commit กับ rollback",
              "DBMS ประมวลผล SQL แต่ SQL เป็นภาษา ไม่ใช่ฐานข้อมูลหรือ DBMS",
          ], "COURSE_MATERIAL", "classify SQL statements", [TOPIC["database"]]),
    group("sql-set-operations", [79, 80], TOPIC["join"],
          "UNION, UNION ALL, and INTERSECT",
          "UNION, UNION ALL และ INTERSECT",
          [
              "Set operations combine query result sets vertically and require union-compatible columns: the same count in corresponding positions with compatible data types.",
              "UNION returns distinct rows from either input; UNION ALL retains duplicates; INTERSECT returns distinct rows present in both inputs.",
              "Evaluate each SELECT first, align columns by position rather than column name, apply the set rule, and then remove duplicates when the operator requires it.",
              "Set operations are different from joins: joins combine columns by matching rows, while set operations combine rows from compatible results.",
          ],
          [
              "การดำเนินการเซตรวมผลลัพธ์คำสั่งสืบค้นในแนวตั้งและต้องมีคอลัมน์ที่เข้ากันได้ คือจำนวนเท่ากันในตำแหน่งสอดคล้องและชนิดข้อมูลเข้ากัน",
              "UNION คืนแถวไม่ซ้ำที่อยู่ในผลลัพธ์ใดก็ได้ UNION ALL เก็บแถวซ้ำ และ INTERSECT คืนแถวไม่ซ้ำที่อยู่ในทั้งสองผลลัพธ์",
              "ประเมิน SELECT แต่ละชุดก่อน จับคู่คอลัมน์ตามตำแหน่งไม่ใช่ชื่อ ใช้กฎเซต แล้วจึงตัดแถวซ้ำเมื่อโอเปอเรเตอร์กำหนด",
              "การดำเนินการเซตต่างจาก join โดย join รวมคอลัมน์จากแถวที่ตรงกัน ส่วนการดำเนินการเซตรวมแถวจากผลลัพธ์ที่เข้ากัน",
          ], "COURSE_MATERIAL", "execute relational set operations", [TOPIC["ddl"]]),
    group("cots", [65], TOPIC["framework"],
          "Commercial off-the-shelf software",
          "ซอฟต์แวร์สำเร็จรูปเชิงพาณิชย์",
          [
              "Commercial off-the-shelf software is a prebuilt product offered to a market and configured or integrated for an adopting organization.",
              "Evaluate fit, configuration, licensing, vendor dependence, integration, security, updates, and total lifecycle cost against custom development.",
              "COTS describes acquisition and product availability, not a programming language or architectural pattern.",
          ],
          [
              "ซอฟต์แวร์สำเร็จรูปเชิงพาณิชย์เป็นผลิตภัณฑ์ที่สร้างไว้และจำหน่ายแก่ตลาด แล้วนำมากำหนดค่าและบูรณาการให้เข้ากับองค์การ",
              "ประเมินความเหมาะสม การกำหนดค่า ใบอนุญาต การพึ่งผู้ขาย การบูรณาการ ความมั่นคงปลอดภัย การอัปเดต และต้นทุนตลอดอายุเทียบกับการพัฒนาเอง",
              "COTS อธิบายวิธีจัดหาและความพร้อมของผลิตภัณฑ์ ไม่ใช่ภาษาโปรแกรมหรือรูปแบบสถาปัตยกรรม",
          ], "EXTERNAL_AUTHORITATIVE", "evaluate build-versus-buy terminology"),
    group("system-architecture", [81, 82], TOPIC["architecture"],
          "System architecture scope and client-server patterns",
          "ขอบเขตสถาปัตยกรรมระบบและรูปแบบไคลเอนต์-เซิร์ฟเวอร์",
          [
              "System architecture describes major components, responsibilities, interfaces, deployment boundaries, data movement, and quality constraints.",
              "The Web is commonly described as client-server: a browser client sends requests and a web server returns resources or application responses.",
              "Layered and multi-tier views separate presentation, application, and data responsibilities; physical deployment may differ from logical layers.",
          ],
          [
              "สถาปัตยกรรมระบบอธิบายองค์ประกอบหลัก ความรับผิดชอบ ส่วนเชื่อมต่อ ขอบเขตการติดตั้ง การไหลข้อมูล และข้อจำกัดด้านคุณภาพ",
              "เว็บมักอธิบายด้วยไคลเอนต์-เซิร์ฟเวอร์ โดยเบราว์เซอร์ส่งคำขอและเว็บเซิร์ฟเวอร์ส่งทรัพยากรหรือผลตอบกลับของแอปพลิเคชัน",
              "มุมมองแบบชั้นและหลายเทียร์แยกส่วนการนำเสนอ แอปพลิเคชัน และข้อมูล ส่วนการติดตั้งทางกายภาพอาจต่างจากชั้นเชิงตรรกะ",
          ], "COURSE_MATERIAL", "identify architectural responsibilities"),
    group("software-design", [83, 84], TOPIC["modularity"],
          "Modularity and software-design objectives",
          "มอดูลาริตีและวัตถุประสงค์การออกแบบซอฟต์แวร์",
          [
              "Modularity decomposes a system into units with clear responsibilities and interfaces so they can be understood, changed, tested, and reused.",
              "Good design seeks correctness, traceability, simplicity, maintainability, testability, security, performance, and appropriate reuse under real constraints.",
              "High cohesion keeps related responsibilities together; low coupling reduces unnecessary dependence between modules.",
          ],
          [
              "มอดูลาริตีแยกระบบเป็นหน่วยที่มีความรับผิดชอบและส่วนเชื่อมต่อชัด เพื่อให้เข้าใจ เปลี่ยน ทดสอบ และใช้ซ้ำได้",
              "การออกแบบที่ดีมุ่งความถูกต้อง การสืบย้อน ความเรียบง่าย การบำรุงรักษา การทดสอบ ความปลอดภัย สมรรถนะ และการใช้ซ้ำอย่างเหมาะสมภายใต้ข้อจำกัดจริง",
              "cohesion สูงรวมความรับผิดชอบที่เกี่ยวข้องไว้ด้วยกัน ส่วน coupling ต่ำลดการพึ่งพาที่ไม่จำเป็นระหว่างมอดูล",
          ], "COURSE_MATERIAL", "evaluate software-design qualities", [TOPIC["architecture"]]),
    group("development-process", [85], TOPIC["lifecycle"],
          "Common software-development activities",
          "กิจกรรมทั่วไปในการพัฒนาซอฟต์แวร์",
          [
              "Development includes requirements analysis, design, implementation, testing, deployment, operation, maintenance, and retirement, with planning and quality work across them.",
              "Iterative approaches revisit activities in short cycles; a lifecycle does not imply every activity occurs only once.",
              "Distinguish a development activity from a product, tool, role, or deployment environment.",
          ],
          [
              "การพัฒนาครอบคลุมการวิเคราะห์ข้อกำหนด ออกแบบ เขียนโปรแกรม ทดสอบ ติดตั้ง ปฏิบัติการ บำรุงรักษา และยุติระบบ โดยมีการวางแผนและคุณภาพตลอดทาง",
              "แนวทางวนซ้ำกลับมาทำกิจกรรมในรอบสั้น วงจรชีวิตไม่ได้หมายความว่าแต่ละกิจกรรมเกิดเพียงครั้งเดียว",
              "แยกกิจกรรมพัฒนาออกจากผลิตภัณฑ์ เครื่องมือ บทบาท หรือสภาพแวดล้อมติดตั้ง",
          ], "COURSE_MATERIAL", "classify lifecycle activities"),
    group("web-stack", [86, 87, 89, 90], TOPIC["server"],
          "Browser, web server, front end, back end, and database",
          "เบราว์เซอร์ เว็บเซิร์ฟเวอร์ ส่วนหน้า ส่วนหลัง และฐานข้อมูล",
          [
              "The browser renders HTML and CSS and executes client-side JavaScript; it sends HTTP requests but does not directly become a database server.",
              "A web server accepts requests and returns static resources or forwards dynamic work to application code.",
              "Front-end libraries and frameworks organize browser interfaces; back-end runtimes and frameworks implement server-side logic, access control, APIs, and data access.",
              "Classify a technology by where its code runs and its primary responsibility, while recognizing that some languages can run in more than one environment.",
          ],
          [
              "เบราว์เซอร์แสดง HTML และ CSS และประมวลผล JavaScript ฝั่งลูกค้า ส่งคำขอ HTTP แต่ไม่ได้กลายเป็นเซิร์ฟเวอร์ฐานข้อมูลโดยตรง",
              "เว็บเซิร์ฟเวอร์รับคำขอและคืนทรัพยากรคงที่หรือส่งงานแบบพลวัตไปยังโค้ดแอปพลิเคชัน",
              "ไลบรารีและเฟรมเวิร์กส่วนหน้าจัดระบบส่วนติดต่อในเบราว์เซอร์ ส่วนรันไทม์และเฟรมเวิร์กส่วนหลังทำตรรกะฝั่งเซิร์ฟเวอร์ การควบคุมสิทธิ์ API และการเข้าถึงข้อมูล",
              "จำแนกเทคโนโลยีจากสถานที่ประมวลผลและความรับผิดชอบหลัก พร้อมตระหนักว่าบางภาษาใช้ได้หลายสภาพแวดล้อม",
          ], "COURSE_MATERIAL", "classify web-stack components", [TOPIC["architecture"]]),
    group("cloud-tradeoffs", [88], TOPIC["cloud"],
          "Evaluate cloud-development benefits and constraints",
          "การประเมินประโยชน์และข้อจำกัดของการพัฒนาบนคลาวด์",
          [
              "Cloud services can provide rapid provisioning, elastic capacity, managed services, global reach, and usage-based cost.",
              "Constraints may include provider dependence, variable operating cost, latency, connectivity, compliance, data location, service limits, and migration complexity.",
              "Whether a characteristic is an advantage depends on workload and context; an under-specified 'NOT' question can have more than one defensible interpretation.",
          ],
          [
              "บริการคลาวด์ช่วยจัดสรรทรัพยากรเร็ว ปรับขนาดยืดหยุ่น ใช้บริการที่มีผู้ดูแล เข้าถึงทั่วโลก และคิดค่าใช้ตามการใช้จริง",
              "ข้อจำกัดอาจรวมการพึ่งผู้ให้บริการ ต้นทุนดำเนินงานผันแปร ความหน่วง การเชื่อมต่อ กฎระเบียบ ตำแหน่งข้อมูล ขีดจำกัดบริการ และความซับซ้อนในการย้าย",
              "คุณลักษณะจะเป็นข้อดีหรือไม่ขึ้นกับภาระงานและบริบท คำถามเชิงปฏิเสธที่ให้ข้อมูลไม่พออาจตีความได้สมเหตุผลมากกว่าหนึ่งแบบ",
          ], "SUPPLEMENTARY_EXPLANATION", "evaluate contextual technology tradeoffs"),
    group("mobile-api-iot", [91, 93], TOPIC["api"],
          "Mobile frameworks, APIs, and IoT solution parts",
          "เฟรมเวิร์กมือถือ API และส่วนประกอบโซลูชัน IoT",
          [
              "A mobile-development framework supplies reusable application structure, build tooling, UI components, or platform abstraction; distinguish it from a database, editor, or design artifact.",
              "An IoT solution usually connects devices or sensors, communication networks, edge or cloud processing, data storage and analysis, and an application or action layer.",
              "APIs provide defined interfaces between these components so implementation details can change without breaking the agreed contract.",
          ],
          [
              "เฟรมเวิร์กพัฒนามือถือให้โครงสร้างแอป เครื่องมือสร้าง คอมโพเนนต์ส่วนติดต่อ หรือชั้นนามธรรมของแพลตฟอร์มที่ใช้ซ้ำได้ และต้องแยกจากฐานข้อมูล โปรแกรมแก้ไข หรือชิ้นงานออกแบบ",
              "โซลูชัน IoT มักเชื่อมอุปกรณ์หรือเซนเซอร์ เครือข่าย การประมวลผลเอดจ์หรือคลาวด์ การจัดเก็บและวิเคราะห์ข้อมูล และชั้นแอปพลิเคชันหรือการกระทำ",
              "API ให้ส่วนเชื่อมต่อที่กำหนดระหว่างองค์ประกอบเหล่านี้ เพื่อให้รายละเอียดการทำงานเปลี่ยนได้โดยไม่ทำลายข้อตกลง",
          ], "COURSE_MATERIAL", "identify platform and IoT components"),
    group("api-scope", [92], TOPIC["api"],
          "API scope, contract, and transport",
          "ขอบเขต ข้อตกลง และการขนส่งของ API",
          [
              "An API is a defined interface through which software components request behavior or exchange data; a contract specifies operations, inputs, outputs, errors, and compatibility expectations.",
              "An API may be local or remote. A web API commonly uses network protocols, but not every API is a web service and not every interface requires the public Internet.",
              "When wording mixes API, web service, and network concepts, evaluate each claim against the stated scope and retain unresolved ambiguity.",
          ],
          [
              "API คือส่วนเชื่อมต่อที่กำหนดให้คอมโพเนนต์ซอฟต์แวร์ร้องขอพฤติกรรมหรือแลกเปลี่ยนข้อมูล ข้อตกลงระบุการดำเนินการ ข้อมูลเข้า ผลลัพธ์ ข้อผิดพลาด และความคาดหวังด้านความเข้ากันได้",
              "API อาจอยู่ภายในเครื่องหรือระยะไกล เว็บ API มักใช้โพรโทคอลเครือข่าย แต่ไม่ใช่ทุก API เป็นเว็บเซอร์วิสและไม่ใช่ทุกส่วนเชื่อมต่อต้องใช้อินเทอร์เน็ตสาธารณะ",
              "เมื่อถ้อยคำปะปน API เว็บเซอร์วิส และแนวคิดเครือข่าย ให้ประเมินแต่ละข้อความตามขอบเขตที่ระบุและคงความกำกวมที่แก้ไม่ได้",
          ], "SUPPLEMENTARY_EXPLANATION", "evaluate API definitions and scope"),
    group("development-tool-categories", [94], TOPIC["version"],
          "Development-tool categories",
          "หมวดหมู่เครื่องมือพัฒนาซอฟต์แวร์",
          [
              "IDEs support coding and debugging, version-control tools manage change history, API clients exercise interfaces, and containers package runtime environments.",
              "Classify a named product by its primary development purpose, even when it offers secondary features from another category.",
              "A business application used by an end user is not automatically a development tool merely because software was used to create it.",
          ],
          [
              "IDE สนับสนุนการเขียนและดีบัก ระบบควบคุมเวอร์ชันจัดการประวัติการเปลี่ยนแปลง ไคลเอนต์ API ทดลองส่วนเชื่อมต่อ และคอนเทนเนอร์บรรจุสภาพแวดล้อมรันไทม์",
              "จำแนกผลิตภัณฑ์จากวัตถุประสงค์หลักในการพัฒนา แม้จะมีคุณลักษณะรองของหมวดอื่น",
              "แอปพลิเคชันธุรกิจที่ผู้ใช้ปลายทางใช้งานไม่ได้เป็นเครื่องมือพัฒนาโดยอัตโนมัติเพียงเพราะมีซอฟต์แวร์ใช้สร้างแอปนั้น",
          ], "COURSE_MATERIAL", "classify software development tools"),
    group("prototyping-tools", [95], TOPIC["prototype"],
          "Interface prototyping tools",
          "เครื่องมือสร้างต้นแบบส่วนติดต่อ",
          [
              "Prototyping tools create static or interactive interface representations for exploring flows and testing ideas before full implementation.",
              "Low-fidelity prototypes emphasize structure and flow; high-fidelity prototypes add visual detail and realistic interaction.",
              "A prototype supports learning and validation but is not necessarily production application code.",
          ],
          [
              "เครื่องมือสร้างต้นแบบสร้างตัวแทนส่วนติดต่อแบบคงที่หรือโต้ตอบเพื่อสำรวจโฟลว์และทดสอบแนวคิดก่อนพัฒนาจริง",
              "ต้นแบบความละเอียดต่ำเน้นโครงสร้างและโฟลว์ ส่วนต้นแบบความละเอียดสูงเพิ่มรายละเอียดภาพและปฏิสัมพันธ์ใกล้เคียงจริง",
              "ต้นแบบสนับสนุนการเรียนรู้และตรวจสอบ แต่ไม่จำเป็นต้องเป็นโค้ดแอปพลิเคชันสำหรับใช้งานจริง",
          ], "EXTERNAL_AUTHORITATIVE", "identify prototyping tools"),
    group("modeling-diagrams", [96, 97], TOPIC["modularity"],
          "Software modeling languages and object-oriented diagrams",
          "ภาษาแบบจำลองซอฟต์แวร์และแผนภาพเชิงวัตถุ",
          [
              "A modeling language provides a defined notation and semantics for representing a system; UML is a general-purpose modeling language rather than one diagram.",
              "Class diagrams show classes, attributes, operations, and relationships; object diagrams show instances at a point in time; sequence diagrams show interactions over time.",
              "Choose a diagram from the view needed—structure, behavior, interaction, deployment, or data—and do not equate a programming language with a modeling notation.",
          ],
          [
              "ภาษาแบบจำลองให้สัญลักษณ์และความหมายที่กำหนดเพื่อแทนระบบ UML เป็นภาษาแบบจำลองอเนกประสงค์ ไม่ใช่แผนภาพเพียงชนิดเดียว",
              "แผนภาพคลาสแสดงคลาส แอตทริบิวต์ เมธอด และความสัมพันธ์ แผนภาพอ็อบเจกต์แสดงอินสแตนซ์ ณ เวลาใดเวลาหนึ่ง และแผนภาพลำดับแสดงปฏิสัมพันธ์ตามเวลา",
              "เลือกแผนภาพจากมุมมองที่ต้องการ เช่น โครงสร้าง พฤติกรรม ปฏิสัมพันธ์ การติดตั้ง หรือข้อมูล และไม่ถือว่าภาษาโปรแกรมเป็นสัญลักษณ์แบบจำลอง",
          ], "COURSE_MATERIAL", "select an appropriate modeling notation"),
    group("html-style", [98], TOPIC["html"],
          "HTML attributes and inline CSS declarations",
          "แอตทริบิวต์ HTML และประกาศ CSS แบบอินไลน์",
          [
              "An HTML start tag may carry a style attribute whose value contains CSS property-value declarations.",
              "A background color is a CSS presentation property; content belongs in the paragraph element and declarations use property: value syntax.",
              "Inline styles can demonstrate syntax, but reusable classes and stylesheets are normally preferable for maintainability.",
          ],
          [
              "แท็กเปิด HTML อาจมีแอตทริบิวต์ style ซึ่งค่าภายในเป็นประกาศคู่พร็อพเพอร์ตีและค่าของ CSS",
              "สีพื้นหลังเป็นคุณสมบัติการนำเสนอของ CSS เนื้อหาอยู่ภายในองค์ประกอบย่อหน้า และประกาศใช้ไวยากรณ์ property: value",
              "สไตล์อินไลน์ใช้สาธิตไวยากรณ์ได้ แต่คลาสและสไตล์ชีตที่ใช้ซ้ำมักบำรุงรักษาง่ายกว่า",
          ], "COURSE_MATERIAL", "recognize valid HTML and CSS syntax"),
    group("javascript-functions", [99], TOPIC["dom"],
          "JavaScript function forms",
          "รูปแบบฟังก์ชันใน JavaScript",
          [
              "A function declaration uses the function keyword, a name, parentheses for parameters, and a block body.",
              "Function expressions and arrow functions are alternatives with different syntax and some different binding behavior.",
              "Distinguish JavaScript syntax from HTML tags and CSS declarations before evaluating a code fragment.",
          ],
          [
              "การประกาศฟังก์ชันใช้คำว่า function ตามด้วยชื่อ วงเล็บสำหรับพารามิเตอร์ และบล็อกคำสั่ง",
              "นิพจน์ฟังก์ชันและ arrow function เป็นทางเลือกที่มีไวยากรณ์และพฤติกรรมการผูกค่าบางอย่างต่างกัน",
              "แยกไวยากรณ์ JavaScript จากแท็ก HTML และประกาศ CSS ก่อนประเมินส่วนโค้ด",
          ], "COURSE_MATERIAL", "recognize JavaScript function syntax"),
    group("css-layout", [100], TOPIC["css"],
          "CSS layout techniques",
          "เทคนิคการจัดวางด้วย CSS",
          [
              "CSS layout systems include normal flow, flexbox, grid, positioning, floats, and multicolumn layout; each solves a different spatial problem.",
              "Floats are a legacy layout technique originally intended for wrapping content, while flexbox and grid are modern layout systems.",
              "Media queries change styles at conditions such as viewport width; they support responsive behavior but are not themselves the layout structure.",
          ],
          [
              "ระบบจัดวาง CSS มี normal flow, flexbox, grid, positioning, float และหลายคอลัมน์ ซึ่งแก้ปัญหาพื้นที่ต่างกัน",
              "float เป็นเทคนิคจัดวางแบบเดิมที่ตั้งใจให้เนื้อหาล้อมรอบ ส่วน flexbox และ grid เป็นระบบจัดวางสมัยใหม่",
              "media query เปลี่ยนสไตล์ตามเงื่อนไข เช่น ความกว้างหน้าจอ จึงสนับสนุนการตอบสนองแต่ไม่ใช่โครงสร้างจัดวางด้วยตัวมันเอง",
          ], "COURSE_MATERIAL", "classify CSS layout mechanisms", [TOPIC["html"]]),
    group("internet-model", [101], TOPIC["encapsulation"],
          "The five-layer Internet model",
          "แบบจำลองอินเทอร์เน็ตห้าชั้น",
          [
              "A common five-layer Internet model contains application, transport, network, data-link, and physical layers.",
              "Each layer provides services upward and uses the layer below; encapsulation adds layer-specific control information as data moves downward.",
              "Do not mix this five-layer teaching model with the seven-layer OSI names without first identifying the model in use.",
          ],
          [
              "แบบจำลองอินเทอร์เน็ตห้าชั้นที่ใช้ทั่วไปประกอบด้วย application, transport, network, data-link และ physical",
              "แต่ละชั้นให้บริการแก่ชั้นบนและใช้ชั้นล่าง การห่อหุ้มเพิ่มข้อมูลควบคุมเฉพาะชั้นเมื่อข้อมูลเคลื่อนลง",
              "อย่าปะปนแบบจำลองสอนห้าชั้นกับชื่อเจ็ดชั้นของ OSI โดยไม่ระบุแบบจำลองที่กำลังใช้",
          ], "COURSE_MATERIAL", "classify networking layers", [TOPIC["protocol"]]),
    group("communication-architectures", [102, 103], TOPIC["protocol"],
          "Communication architectures and SMTP delivery",
          "สถาปัตยกรรมการสื่อสารและการส่งอีเมลด้วย SMTP",
          [
              "Host-based, client-server, and multi-tier architectures assign presentation, application, and data work to different computers; thin clients retain less local processing than thick clients.",
              "SMTP transfers outgoing mail between clients and mail servers or among servers; after accepted delivery, the recipient's mail server stores the message for later access.",
              "Retrieval protocols or webmail interfaces let the recipient read stored mail; sending and retrieving are distinct responsibilities.",
          ],
          [
              "สถาปัตยกรรมแบบโฮสต์ ไคลเอนต์-เซิร์ฟเวอร์ และหลายเทียร์กระจายงานนำเสนอ แอปพลิเคชัน และข้อมูลต่างกัน thin client ประมวลผลในเครื่องน้อยกว่า thick client",
              "SMTP ส่งจดหมายขาออกระหว่างไคลเอนต์กับเซิร์ฟเวอร์เมลหรือระหว่างเซิร์ฟเวอร์ หลังรับส่งสำเร็จเซิร์ฟเวอร์เมลผู้รับจัดเก็บข้อความเพื่อเปิดภายหลัง",
              "โพรโทคอลรับจดหมายหรือเว็บเมลช่วยให้ผู้รับอ่านจดหมายที่เก็บไว้ การส่งกับการรับเป็นความรับผิดชอบคนละส่วน",
          ], "COURSE_MATERIAL", "trace responsibilities in a communication architecture"),
    group("signals-media", [104, 105], TOPIC["medium"],
          "Optical multiplexing and Manchester encoding",
          "การมัลติเพล็กซ์เชิงแสงและการเข้ารหัสแมนเชสเตอร์",
          [
              "Wavelength-division multiplexing carries multiple optical channels on different light wavelengths over fiber.",
              "Manchester encoding represents each bit with a transition in the middle of the bit interval, combining timing information with data.",
              "The mapping of upward or downward transition to binary value depends on the stated convention, so use the convention supplied in the course or diagram.",
          ],
          [
              "การมัลติเพล็กซ์แบ่งความยาวคลื่นส่งหลายช่องสัญญาณแสงด้วยความยาวคลื่นต่างกันผ่านใยแก้วนำแสง",
              "การเข้ารหัสแมนเชสเตอร์แทนแต่ละบิตด้วยการเปลี่ยนระดับกลางช่วงบิต จึงรวมข้อมูลเวลาเข้ากับข้อมูล",
              "การจับคู่การเปลี่ยนขึ้นหรือลงกับค่าบิตขึ้นกับข้อตกลงที่ระบุ จึงต้องใช้ข้อตกลงจากบทเรียนหรือแผนภาพ",
          ], "COURSE_MATERIAL", "interpret transmission and signaling methods"),
    group("data-link", [106, 107], TOPIC["frame"],
          "Sliding windows, ARQ, and Ethernet addressing",
          "หน้าต่างเลื่อน ARQ และการกำหนดที่อยู่อีเทอร์เน็ต",
          [
              "Sliding-window protocols allow multiple frames to be outstanding before acknowledgment, improving link utilization while controlling flow.",
              "Continuous ARQ families use sequence numbers, acknowledgments, timers, and retransmission; variants differ in whether they repeat one frame or a range.",
              "A standard Ethernet MAC address is 48 bits, or 6 bytes, and identifies a link-layer interface within its applicable network scope.",
          ],
          [
              "โพรโทคอลหน้าต่างเลื่อนอนุญาตให้มีหลายเฟรมรอการยืนยันพร้อมกัน เพิ่มการใช้ลิงก์พร้อมควบคุมการไหล",
              "กลุ่ม continuous ARQ ใช้หมายเลขลำดับ การยืนยัน เวลา และการส่งซ้ำ โดยแต่ละแบบต่างกันว่าจะส่งซ้ำหนึ่งเฟรมหรือช่วงหนึ่ง",
              "ที่อยู่ MAC อีเทอร์เน็ตมาตรฐานยาว 48 บิตหรือ 6 ไบต์ และระบุส่วนเชื่อมต่อชั้นลิงก์ในขอบเขตเครือข่ายที่เกี่ยวข้อง",
          ], "COURSE_MATERIAL", "apply data-link control and addressing"),
    group("routing-qos-ipv6", [108, 109, 110], TOPIC["routing"],
          "QoS, exterior routing, BGP, and IPv6",
          "QoS การกำหนดเส้นทางภายนอก BGP และ IPv6",
          [
              "Quality of Service classifies and schedules traffic to meet latency, jitter, loss, or bandwidth needs; prioritization manages congestion rather than creating unlimited capacity.",
              "Exterior routing exchanges reachability between autonomous systems; BGP is the Internet's principal interdomain routing protocol.",
              "IPv6 expands address space and changes header and configuration mechanisms as the successor to IPv4; coexistence uses dual stack, tunneling, or translation.",
          ],
          [
              "คุณภาพการให้บริการจำแนกและจัดตารางทราฟฟิกเพื่อให้ตรงความต้องการด้านความหน่วง jitter การสูญหาย หรือแบนด์วิดท์ การจัดลำดับช่วยจัดการความคับคั่งแต่ไม่สร้างความจุไม่จำกัด",
              "การกำหนดเส้นทางภายนอกแลกเปลี่ยนการเข้าถึงระหว่างระบบอิสระ โดย BGP เป็นโพรโทคอลหลักระหว่างโดเมนของอินเทอร์เน็ต",
              "IPv6 เพิ่มพื้นที่ที่อยู่และเปลี่ยนกลไกส่วนหัวกับการกำหนดค่าในฐานะรุ่นสืบทอด IPv4 การอยู่ร่วมกันใช้ dual stack, tunneling หรือ translation",
          ], "COURSE_MATERIAL", "distinguish network-layer services", [TOPIC["protocol"]]),
    group("network-proposal", [111], TOPIC["network_management"],
          "Cost assessment and approval in network design",
          "การประเมินต้นทุนและการอนุมัติในการออกแบบเครือข่าย",
          [
              "A network-design process moves from requirements and traffic analysis through logical and physical design, costing, testing, implementation, and operation.",
              "Cost assessment compares capital, operating, staffing, migration, risk, and benefit assumptions before management approval.",
              "Selling a proposal means communicating business value, alternatives, risks, and evidence to decision makers; it is not a substitute for technical validation.",
          ],
          [
              "กระบวนการออกแบบเครือข่ายเริ่มจากข้อกำหนดและการวิเคราะห์ทราฟฟิก ไปสู่การออกแบบตรรกะและกายภาพ การคิดต้นทุน การทดสอบ การติดตั้ง และปฏิบัติการ",
              "การประเมินต้นทุนเปรียบเทียบเงินลงทุน ค่าใช้จ่ายดำเนินงาน บุคลากร การย้ายระบบ ความเสี่ยง และสมมติฐานผลประโยชน์ก่อนขออนุมัติ",
              "การนำเสนอข้อเสนอคือการสื่อสารคุณค่าธุรกิจ ทางเลือก ความเสี่ยง และหลักฐานแก่ผู้ตัดสินใจ ไม่ใช่สิ่งแทนการตรวจสอบทางเทคนิค",
          ], "EXTERNAL_AUTHORITATIVE", "place approval work in a design lifecycle"),
    group("wireless-switching", [112, 113], TOPIC["lan"],
          "Wireless LAN security and chassis switches",
          "ความปลอดภัย LAN ไร้สายและสวิตช์แบบแชสซี",
          [
              "Wireless LAN security protocols protect access and link traffic; modern deployments use WPA-family mechanisms with appropriate authentication and strong configuration.",
              "Legacy mechanisms may still appear in historical material but should not be treated as current security recommendations.",
              "A chassis switch accepts replaceable modules in a shared enclosure, supporting port-density, media, uplink, redundancy, and expansion flexibility at the cost of greater expense and complexity.",
          ],
          [
              "โพรโทคอลความปลอดภัย LAN ไร้สายปกป้องการเข้าถึงและทราฟฟิกชั้นลิงก์ การติดตั้งสมัยใหม่ใช้กลไกตระกูล WPA พร้อมการยืนยันตัวตนและการกำหนดค่าที่แข็งแรง",
              "กลไกเก่าอาจปรากฏในเอกสารเชิงประวัติศาสตร์ แต่ไม่ควรถือเป็นคำแนะนำความปลอดภัยปัจจุบัน",
              "สวิตช์แบบแชสซีรับโมดูลเปลี่ยนได้ในโครงร่วม ช่วยยืดหยุ่นด้านจำนวนพอร์ต สื่อ uplink ความซ้ำซ้อน และการขยาย แต่มีต้นทุนและความซับซ้อนสูงขึ้น",
          ], "COURSE_MATERIAL", "compare LAN technologies", [TOPIC["frame"]]),
]


INITIAL_FULL = {19, 32, 74, 83}
INITIAL_CONFLICTING = {22, 23, 35, 39, 46, 63, 64, 88, 92, 96}
INITIAL_KEYWORD = {
    1, 2, 3, 4, 25, 26, 37, 41, 44, 49, 62, 69, 72, 75, 80, 81, 95,
    101, 109, 110, 111,
}
INITIAL_MISSING = {
    5, 6, 7, 9, 10, 20, 21, 24, 33, 34, 36, 38, 40, 42, 43, 45, 47,
    48, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 65, 66, 67,
    68, 70, 71, 73, 76, 77, 78, 79, 86, 87, 89, 90, 91, 93, 97, 98,
    99, 100, 102, 103, 104, 105, 112, 113,
}


def question_id(number: int) -> str:
    return f"question-comprehensive-{number:03d}"


def initial_status(number: int) -> str:
    if number in INITIAL_FULL:
        return "fully_covered"
    if number in INITIAL_CONFLICTING:
        return "conflicting_or_uncertain"
    if number in INITIAL_KEYWORD:
        return "keyword_only"
    if number in INITIAL_MISSING:
        return "missing"
    return "partially_covered"


def final_status(origin: str) -> str:
    return {
        "COURSE_MATERIAL": "fully_covered",
        "EXTERNAL_AUTHORITATIVE": "covered_with_external_sources",
        "SUPPLEMENTARY_EXPLANATION": "covered_with_supplementary_content",
    }[origin]


def build() -> tuple[dict, dict, dict, dict]:
    topics_payload = json.loads((ROOT / "data/topics.json").read_text())
    questions_payload = json.loads((ROOT / "data/questions.json").read_text())
    external_payload = json.loads((ROOT / "data/external-sources.json").read_text())
    topics = topics_payload["topics"]
    questions = questions_payload["questions"]
    topic_by_id = {item["topic_id"]: item for item in topics}
    question_by_id = {item["question_id"]: item for item in questions}
    external_ids = {item["source_id"] for item in external_payload["external_sources"]}

    mapped_numbers = [number for item in GROUPS for number in item["question_numbers"]]
    expected_numbers = sorted(
        int(item["question_id"].rsplit("-", 1)[1]) for item in questions
    )
    if sorted(mapped_numbers) != expected_numbers:
        missing = sorted(set(expected_numbers) - set(mapped_numbers))
        duplicate = sorted(number for number, count in Counter(mapped_numbers).items() if count > 1)
        raise SystemExit(f"Coverage groups invalid: missing={missing}, duplicate={duplicate}")
    if set(CONCEPTS) != set(expected_numbers):
        raise SystemExit("CONCEPTS does not cover exactly the supplied questions")

    # Replace only prior generated coverage sections; retain every Phase 11 section.
    for topic in topics:
        topic["lesson_sections"] = [
            item for item in topic["lesson_sections"]
            if not item["section_id"].startswith("coverage-")
        ]

    coverage_records = []
    topic_questions: dict[str, list[str]] = defaultdict(list)
    topic_concepts: dict[str, list[dict]] = defaultdict(list)
    question_primary_topic: dict[str, str] = {}

    for item in GROUPS:
        topic = topic_by_id[item["topic_id"]]
        qids = [question_id(number) for number in item["question_numbers"]]
        group_questions = [question_by_id[qid] for qid in qids]
        source_refs = sorted({
            ref["source_reference_id"]
            for question in group_questions
            for ref in question["source_references"]
        })
        ext_ids = sorted({
            source_id
            for question in group_questions
            for source_id in question["external_source_ids"]
        })
        if item["origin"] == "EXTERNAL_AUTHORITATIVE" and not ext_ids:
            raise SystemExit(f"{item['group_id']} lacks an external source")
        if not set(ext_ids).issubset(external_ids):
            raise SystemExit(f"{item['group_id']} has an unknown external source")
        category, label_en, label_th = SOURCE_LABELS[item["origin"]]
        topic["lesson_sections"].append({
            "section_id": f"coverage-{item['group_id']}",
            "heading_en": item["heading_en"],
            "heading_th": item["heading_th"],
            "content_en": item["content_en"],
            "content_th": item["content_th"],
            "content_format": "bullet_list",
            "evidence_type": "exam_coverage_teaching",
            "source_category": category,
            "source_label_en": label_en,
            "source_label_th": label_th,
            "evidence_origin": item["origin"],
            "source_reference_ids": source_refs,
            "external_source_ids": ext_ids,
            "evidence_summary_en": (
                "General concept teaching linked to supplied examination evidence; "
                "no answer or choice text is reproduced."
            ),
            "evidence_summary_th": (
                "เนื้อหาแนวคิดทั่วไปที่เชื่อมกับหลักฐานข้อสอบที่ให้มา "
                "โดยไม่ทำซ้ำคำตอบหรือข้อความตัวเลือก"
            ),
            "related_question_ids": qids,
        })
        topic["content_updated_at"] = AUDIT_DATE

        for number, qid, question in zip(item["question_numbers"], qids, group_questions):
            concept_en, concept_th = CONCEPTS[number]
            topic_questions[item["topic_id"]].append(qid)
            topic_concepts[item["topic_id"]].append({
                "question_id": qid,
                "concept_en": concept_en,
                "concept_th": concept_th,
            })
            question_primary_topic[qid] = item["topic_id"]
            before = initial_status(number)
            answer_warning = (
                question["answer_status"] in {
                    "probabilistic_recommendation",
                    "unresolvable_question",
                    "strongly_supported_by_external_source",
                }
                or question["requires_human_review"]
            )
            coverage_records.append({
                "question_id": qid,
                "subject_code": question["subject_code"],
                "chapter_id": question["chapter_id"],
                "tested_topic_ids": [item["topic_id"]],
                "related_study_topic_ids": [item["topic_id"]],
                "primary_study_topic_id": item["topic_id"],
                "tested_concept_en": concept_en,
                "tested_concept_th": concept_th,
                "tested_skill": item["skill"],
                "required_prerequisite_topics": item["prerequisites"],
                "initial_coverage_status": before,
                "current_coverage_status": "fully_covered",
                "final_coverage_status": final_status(item["origin"]),
                "coverage_quality": (
                    "sufficient_for_guided_self-study_with_bilingual_definition, "
                    "comparison_or_rule, and decision guidance"
                ),
                "evidence_origin": item["origin"],
                "missing_content": (
                    [] if before == "fully_covered"
                    else [f"Before repair: {before.replace('_', ' ')} for the exact tested concept"]
                ),
                "recommended_action": "Retain the source-labelled concept lesson and bidirectional link.",
                "changes_made": [
                    f"Added or confirmed bilingual teaching section coverage-{item['group_id']}",
                    f"Linked the question precisely to {item['topic_id']}",
                ],
                "source_reference_ids": sorted(
                    ref["source_reference_id"]
                    for ref in question["source_references"]
                ),
                "external_source_ids": sorted(question["external_source_ids"]),
                "answer_status_warning": answer_warning,
                "answer_status_warning_en": (
                    "The academic answer record retains a review or scoring warning; "
                    "the Study Library teaches the concept without resolving the answer."
                    if answer_warning else ""
                ),
                "answer_status_warning_th": (
                    "ระเบียนคำตอบทางวิชาการยังมีคำเตือนด้านการตรวจทานหรือการให้คะแนน "
                    "คลังบทเรียนสอนแนวคิดโดยไม่ตัดสินคำตอบ"
                    if answer_warning else ""
                ),
                "human_review_note": (
                    "Coverage is complete, but the pre-existing academic-answer review state is preserved."
                    if answer_warning else None
                ),
                "audited_at": AUDIT_DATE,
            })

    # Precise links live in the dedicated mapping. Remove any stale generated
    # field so the immutable academic question record remains byte-compatible
    # with the pre-audit preservation gates.
    for question in questions:
        question.pop("study_topic_ids", None)

    topic_map_records = []
    for topic in topics:
        qids = sorted(
            topic_questions.get(topic["topic_id"], []),
            key=lambda value: int(value.rsplit("-", 1)[1]),
        )
        source_files = sorted({
            question_by_id[qid]["source_exam_relative_path"] for qid in qids
        })
        warning_count = sum(
            1 for qid in qids
            if question_by_id[qid]["requires_human_review"]
            or question_by_id[qid]["answer_status"] in {
                "probabilistic_recommendation",
                "unresolvable_question",
                "strongly_supported_by_external_source",
            }
        )
        difficulty = Counter(question_by_id[qid]["difficulty"] for qid in qids)
        topic_map_records.append({
            "topic_id": topic["topic_id"],
            "subject_code": topic["topic_id"].split("-")[1].upper(),
            "chapter_id": topic["chapter_id"],
            "related_question_ids": qids,
            "question_count": len(qids),
            "tested_concepts": topic_concepts.get(topic["topic_id"], []),
            "difficulty_counts": {
                "easy": difficulty["easy"],
                "medium": difficulty["medium"],
                "hard": difficulty["hard"],
            },
            "answer_status_warning_count": warning_count,
            "exam_frequency_signal": (
                "no_supplied_exam_example_found" if not qids
                else "appears_in_supplied_exam_examples" if len(qids) == 1
                else "appears_multiple_times_in_supplied_exam_examples"
            ),
            "source_exam_files": source_files,
            "updated_at": AUDIT_DATE,
        })

    coverage_payload = {
        "schema_version": "1.0.0",
        "generated_at": f"{AUDIT_DATE}T00:00:00+07:00",
        "audit_scope": (
            "All supplied comprehensive-examination questions mapped to the "
            "actual bilingual Study Library teaching needed to solve them."
        ),
        "answer_leakage_policy": (
            "No correct-answer identifiers, correct-choice text, probability "
            "distributions, or answer explanations are stored in this mapping."
        ),
        "question_study_coverage": sorted(
            coverage_records,
            key=lambda value: int(value["question_id"].rsplit("-", 1)[1]),
        ),
    }
    topic_map_payload = {
        "schema_version": "1.0.0",
        "generated_at": f"{AUDIT_DATE}T00:00:00+07:00",
        "study_topic_question_map": topic_map_records,
    }
    return topics_payload, questions_payload, coverage_payload, topic_map_payload


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    topics, questions, coverage, topic_map = build()
    outputs = {
        ROOT / "data/topics.json": topics,
        ROOT / "web/src/data/topics.json": topics,
        ROOT / "data/questions.json": questions,
        ROOT / "web/src/data/questions.json": questions,
        ROOT / "data/question-study-coverage.json": coverage,
        ROOT / "web/src/data/question-study-coverage.json": coverage,
        ROOT / "data/study-topic-question-map.json": topic_map,
        ROOT / "web/src/data/study-topic-question-map.json": topic_map,
    }
    if args.check:
        stale = []
        for path, payload in outputs.items():
            expected = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
            if not path.exists() or path.read_text() != expected:
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            raise SystemExit("Coverage outputs are stale: " + ", ".join(stale))
        print("Exam-to-study coverage outputs are current.")
        return
    for path, payload in outputs.items():
        write_json(path, payload)
    print(
        f"Wrote {len(coverage['question_study_coverage'])} question mappings, "
        f"{len(topic_map['study_topic_question_map'])} topic mappings, and "
        f"{sum(1 for t in topics['topics'] for s in t['lesson_sections'] if s['section_id'].startswith('coverage-'))} coverage lessons."
    )


if __name__ == "__main__":
    main()
