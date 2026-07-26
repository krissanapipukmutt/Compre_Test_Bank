#!/usr/bin/env python3
"""Build the bilingual Phase 1 knowledge base from verified local source paths."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def topic(en: str, th: str, definition_en: str, definition_th: str) -> dict[str, str]:
    return {
        "title_en": en,
        "title_th": th,
        "definition_en": definition_en,
        "definition_th": definition_th,
    }


def chapter(
    code: str,
    slug: str,
    title_en: str,
    title_th: str,
    summary_en: str,
    summary_th: str,
    sources: str | list[str],
    topics: list[dict[str, str]],
    *,
    formulas: list[str] | None = None,
    confidence: str = "high",
    evidence_type: str = "summarized_from_source",
) -> dict[str, Any]:
    return {
        "code": code,
        "slug": slug,
        "title_en": title_en,
        "title_th": title_th,
        "summary_en": summary_en,
        "summary_th": summary_th,
        "sources": [sources] if isinstance(sources, str) else sources,
        "topics": topics,
        "formulas": formulas or [],
        "confidence": confidence,
        "evidence_type": evidence_type,
    }


SUBJECTS: dict[str, dict[str, Any]] = {
    "BIS601": {
        "title_en": "Business System Analysis and Design",
        "title_th": "การวิเคราะห์และออกแบบระบบธุรกิจ",
        "term": "term-2",
        "overview_en": "BIS601 follows an analysis-to-design path: understand business problems, identify feasible projects, elicit and structure requirements, and model behavior, data flow, decisions, and end-to-end processes.",
        "overview_th": "BIS601 ดำเนินจากการวิเคราะห์ไปสู่การออกแบบ ได้แก่ ทำความเข้าใจปัญหาธุรกิจ ระบุโครงการที่เป็นไปได้ เก็บและจัดโครงสร้างความต้องการ และสร้างแบบจำลองพฤติกรรม การไหลของข้อมูล การตัดสินใจ และกระบวนการตั้งแต่ต้นจนจบ",
        "objectives_en": [
            "Explain the role and competencies of a systems/business analyst.",
            "Select and apply development and requirements methods.",
            "Create and interpret activity, use-case, DFD, decision, and BPMN models.",
        ],
        "objectives_th": [
            "อธิบายบทบาทและสมรรถนะของนักวิเคราะห์ระบบ/ธุรกิจ",
            "เลือกและประยุกต์วิธีพัฒนาระบบและวิธีวิเคราะห์ความต้องการ",
            "สร้างและตีความ Activity, Use Case, DFD, Decision และ BPMN",
        ],
        "mapping_confidence": "high",
        "mapping_note": "Course code and subject title are present across the supplied BIS601 course materials.",
    },
    "BIS602": {
        "title_en": "Business Decision and Data Analytics",
        "title_th": "การตัดสินใจและการวิเคราะห์ข้อมูลธุรกิจ",
        "term": "term-1",
        "overview_en": "BIS602 connects business strategy and performance decisions with enterprise data management, statistics, descriptive analytics, predictive models, association discovery, and simulation.",
        "overview_th": "BIS602 เชื่อมกลยุทธ์และการตัดสินใจด้านผลการดำเนินงานเข้ากับการจัดการข้อมูลองค์กร สถิติ การวิเคราะห์เชิงพรรณนา แบบจำลองเชิงพยากรณ์ การค้นหาความสัมพันธ์ และการจำลอง",
        "objectives_en": [
            "Frame business decisions with strategy, KPIs, and financial evidence.",
            "Prepare, summarize, and visualize business data.",
            "Interpret clustering, classification, regression, association, and simulation results.",
        ],
        "objectives_th": [
            "กำหนดกรอบการตัดสินใจด้วยกลยุทธ์ KPI และหลักฐานทางการเงิน",
            "เตรียม สรุป และแสดงภาพข้อมูลธุรกิจ",
            "ตีความผลการจัดกลุ่ม การจำแนก การถดถอย กฎความสัมพันธ์ และการจำลอง",
        ],
        "mapping_confidence": "high",
        "mapping_note": "Verified from `BIS602 2024 outline.pdf`, which states the code, English title, Thai title, and schedule.",
    },
    "BIS603": {
        "title_en": "Strategies Marketing Management",
        "title_th": "การจัดการการตลาดเชิงกลยุทธ์",
        "term": "term-2",
        "overview_en": "The supplied BIS603-context materials combine corporate strategy analysis and formulation with marketing foundations, digital campaigns, customer data, AI, and entrepreneurial financial strategy.",
        "overview_th": "เอกสารในบริบท BIS603 ผสานการวิเคราะห์และกำหนดกลยุทธ์องค์กรกับพื้นฐานการตลาด แคมเปญดิจิทัล ข้อมูลลูกค้า AI และกลยุทธ์การเงินสำหรับผู้ประกอบการ",
        "objectives_en": [
            "Analyze external and internal strategic conditions.",
            "Formulate coherent business and marketing choices.",
            "Connect segmentation, digital channels, data, AI, and financial logic.",
        ],
        "objectives_th": [
            "วิเคราะห์เงื่อนไขเชิงกลยุทธ์ภายนอกและภายใน",
            "กำหนดทางเลือกธุรกิจและการตลาดที่สอดคล้องกัน",
            "เชื่อมการแบ่งส่วนตลาด ช่องทางดิจิทัล ข้อมูล AI และตรรกะทางการเงิน",
        ],
        "mapping_confidence": "medium",
        "mapping_note": "The folder supplies the BIS603 code and a misspelled title; sampled lecture content confirms strategy/marketing topics but no authoritative course outline states the exact code-title pair.",
    },
    "BIS604": {
        "title_en": "Business Data Management",
        "title_th": "การจัดการข้อมูลธุรกิจ",
        "term": "term-2",
        "overview_en": "BIS604 develops database literacy from data-management foundations and data models through relational design, business rules, ER modeling, normalization, SQL implementation, and business use.",
        "overview_th": "BIS604 พัฒนาความรู้ฐานข้อมูลตั้งแต่พื้นฐานการจัดการข้อมูลและแบบจำลองข้อมูล ผ่านการออกแบบเชิงสัมพันธ์ กฎธุรกิจ ER การทำ Normalization การใช้ SQL และการนำข้อมูลไปใช้ในธุรกิจ",
        "objectives_en": [
            "Explain database systems and data-model tradeoffs.",
            "Transform business rules into relational and ER designs.",
            "Normalize and implement a database with SQL.",
        ],
        "objectives_th": [
            "อธิบายระบบฐานข้อมูลและข้อแลกเปลี่ยนของแบบจำลองข้อมูล",
            "แปลงกฎธุรกิจเป็นแบบเชิงสัมพันธ์และ ER",
            "ทำ Normalization และสร้างฐานข้อมูลด้วย SQL",
        ],
        "mapping_confidence": "high",
        "mapping_note": "Verified from `OutlineBIS604_1_2025_New1.pdf`, which states `BIS604 Business Data Management`.",
    },
    "BIS605": {
        "title_en": "Software Development Technologies for Digital Business",
        "title_th": "เทคโนโลยีการพัฒนาซอฟต์แวร์สำหรับธุรกิจดิจิทัล",
        "term": "term-1",
        "overview_en": "BIS605 covers the software lifecycle and design foundations, then applies them through front-end, back-end, database, API, cloud, and mobile technologies for digital-business solutions.",
        "overview_th": "BIS605 ครอบคลุมวงจรชีวิตและพื้นฐานการออกแบบซอฟต์แวร์ แล้วนำไปประยุกต์ผ่านเทคโนโลยี Front-end, Back-end, ฐานข้อมูล, API, Cloud และ Mobile สำหรับโซลูชันธุรกิจดิจิทัล",
        "objectives_en": [
            "Relate architecture, lifecycle, requirements, and design decisions.",
            "Build accessible interfaces with core web technologies.",
            "Explain server, database, API, cloud, and mobile integration.",
        ],
        "objectives_th": [
            "เชื่อมการตัดสินใจด้านสถาปัตยกรรม วงจรชีวิต ความต้องการ และการออกแบบ",
            "สร้างส่วนติดต่อที่เข้าถึงได้ด้วยเทคโนโลยีเว็บหลัก",
            "อธิบายการเชื่อม Server, Database, API, Cloud และ Mobile",
        ],
        "mapping_confidence": "high",
        "mapping_note": "Verified from the supplied BIS605 combined course material and chapter slides.",
    },
    "BIS606": {
        "title_en": "Digital Infrastructure and Cyber Security System",
        "title_th": "โครงสร้างพื้นฐานดิจิทัลและระบบความมั่นคงปลอดภัยไซเบอร์",
        "term": "term-1",
        "overview_en": "BIS606 spans data communications and network infrastructure, then applies continuity, risk, defense-in-depth, host/network controls, and security frameworks to protect digital services.",
        "overview_th": "BIS606 ครอบคลุมการสื่อสารข้อมูลและโครงสร้างพื้นฐานเครือข่าย ก่อนประยุกต์ความต่อเนื่องทางธุรกิจ ความเสี่ยง การป้องกันหลายชั้น การควบคุม Host/Network และกรอบความมั่นคงปลอดภัยเพื่อคุ้มครองบริการดิจิทัล",
        "objectives_en": [
            "Explain layered communication and network technologies.",
            "Assess continuity and cyber risks.",
            "Select network, server, system, and governance controls.",
        ],
        "objectives_th": [
            "อธิบายการสื่อสารแบบแบ่งชั้นและเทคโนโลยีเครือข่าย",
            "ประเมินความเสี่ยงด้านความต่อเนื่องและไซเบอร์",
            "เลือกการควบคุมเครือข่าย เซิร์ฟเวอร์ ระบบ และธรรมาภิบาล",
        ],
        "mapping_confidence": "high",
        "mapping_note": "Verified from `BIS606Syllabus_2_2024.docx` and the supplied combined course material.",
    },
}


CHAPTERS = [
    # BIS601
    chapter("BIS601", "analyst-and-system-success", "Analyst role and information-system success", "บทบาทนักวิเคราะห์และความสำเร็จของระบบสารสนเทศ", "Systems analysis begins by defining success, understanding failure, and distinguishing the analyst's business-facing responsibilities from technical implementation roles.", "การวิเคราะห์ระบบเริ่มจากนิยามความสำเร็จ ทำความเข้าใจความล้มเหลว และแยกความรับผิดชอบที่มุ่งธุรกิจของนักวิเคราะห์ออกจากบทบาทการนำเทคนิคไปใช้", "TERM2/BIS601 Business System Analysis and Design/MIDTERM/LACTURE/Chapter1/BIS601_2025_1_01a_intro.pdf", [
        topic("Information-system success", "ความสำเร็จของระบบสารสนเทศ", "Success depends on business value, adoption, quality, and fit—not delivery alone.", "ความสำเร็จขึ้นกับคุณค่าทางธุรกิจ การยอมรับ คุณภาพ และความสอดคล้อง ไม่ใช่เพียงส่งมอบเสร็จ"),
        topic("Systems analyst", "นักวิเคราะห์ระบบ", "An analyst bridges stakeholder needs and a feasible system solution.", "นักวิเคราะห์เชื่อมความต้องการผู้มีส่วนได้ส่วนเสียกับโซลูชันระบบที่เป็นไปได้"),
        topic("Problem and opportunity", "ปัญหาและโอกาส", "Analysis frames the gap between the current and desired business state.", "การวิเคราะห์กำหนดช่องว่างระหว่างสภาพธุรกิจปัจจุบันและสภาพที่ต้องการ"),
    ]),
    chapter("BIS601", "development-methods", "Development methods and lifecycle", "วิธีและวงจรชีวิตการพัฒนาระบบ", "Development methods organize planning, analysis, design, implementation, and evolution; method choice changes feedback speed, documentation, and risk handling.", "วิธีพัฒนาระบบจัดระเบียบการวางแผน วิเคราะห์ ออกแบบ นำไปใช้ และปรับปรุง โดยการเลือกวิธีมีผลต่อความเร็วของข้อเสนอแนะ เอกสาร และการจัดการความเสี่ยง", "TERM2/BIS601 Business System Analysis and Design/MIDTERM/LACTURE/Chapter2/BIS601_2025_1_04_method.pdf", [
        topic("SDLC", "วงจรชีวิตการพัฒนาระบบ", "A structured sequence for planning, analysis, design, implementation, and maintenance.", "ลำดับงานอย่างเป็นระบบตั้งแต่การวางแผน วิเคราะห์ ออกแบบ นำไปใช้ และบำรุงรักษา"),
        topic("Predictive method", "วิธีเชิงคาดการณ์", "A plan-driven approach suitable when scope is comparatively stable.", "แนวทางขับเคลื่อนด้วยแผน เหมาะเมื่อขอบเขตค่อนข้างคงที่"),
        topic("Adaptive method", "วิธีเชิงปรับตัว", "An iterative approach that learns through frequent delivery and feedback.", "แนวทางวนรอบที่เรียนรู้ผ่านการส่งมอบและข้อเสนอแนะบ่อยครั้ง"),
    ]),
    chapter("BIS601", "project-identification", "Project identification and feasibility", "การระบุโครงการและความเป็นไปได้", "Project selection translates business needs into a scoped proposal and tests organizational, technical, economic, and schedule feasibility before major commitment.", "การคัดเลือกโครงการแปลงความต้องการธุรกิจเป็นข้อเสนอที่มีขอบเขต และทดสอบความเป็นไปได้ด้านองค์กร เทคนิค เศรษฐศาสตร์ และเวลา ก่อนผูกพันทรัพยากรจำนวนมาก", "TERM2/BIS601 Business System Analysis and Design/MIDTERM/LACTURE/Chapter4/BIS601_2025_1_05a_ident.pdf", [
        topic("System request", "คำขอระบบ", "A concise statement of sponsor, need, requirements, value, and constraints.", "ข้อความกระชับระบุผู้สนับสนุน ความต้องการ คุณค่า และข้อจำกัด"),
        topic("Feasibility analysis", "การวิเคราะห์ความเป็นไปได้", "A structured test of whether a proposed project should proceed.", "การทดสอบอย่างมีโครงสร้างว่าโครงการที่เสนอควรดำเนินต่อหรือไม่"),
        topic("Project scope", "ขอบเขตโครงการ", "The agreed boundary of included outcomes, work, and exclusions.", "ขอบเขตที่ตกลงของผลลัพธ์ งานที่รวม และสิ่งที่ไม่รวม"),
    ]),
    chapter("BIS601", "requirements", "Requirements determination and elicitation", "การกำหนดและเก็บความต้องการ", "Requirements work identifies stakeholders, elicits needs through suitable techniques, resolves conflicts, and expresses verifiable functional and quality expectations.", "งานความต้องการระบุผู้มีส่วนได้ส่วนเสีย เก็บความต้องการด้วยเทคนิคที่เหมาะสม แก้ความขัดแย้ง และระบุความคาดหวังเชิงหน้าที่และคุณภาพที่ตรวจสอบได้", "TERM2/BIS601 Business System Analysis and Design/MIDTERM/LACTURE/Chapter5/BIS601_2025_1_06_req.pdf", [
        topic("Functional requirement", "ความต้องการเชิงหน้าที่", "A behavior or service the system must provide.", "พฤติกรรมหรือบริการที่ระบบต้องจัดให้"),
        topic("Non-functional requirement", "ความต้องการที่ไม่ใช่เชิงหน้าที่", "A quality or constraint such as performance, security, or usability.", "คุณลักษณะหรือข้อจำกัด เช่น ประสิทธิภาพ ความมั่นคงปลอดภัย หรือความง่ายในการใช้"),
        topic("Elicitation", "การเก็บความต้องการ", "Purposeful discovery through interviews, observation, workshops, documents, or prototypes.", "การค้นหาอย่างมีเป้าหมายผ่านการสัมภาษณ์ สังเกต เวิร์กช็อป เอกสาร หรือต้นแบบ"),
    ]),
    chapter("BIS601", "behavior-models", "Activity and use-case modeling", "การสร้างแบบจำลองกิจกรรมและกรณีใช้งาน", "Activity models show workflow, while use cases describe goal-oriented interactions between actors and the system boundary.", "Activity Diagram แสดงลำดับงาน ส่วน Use Case อธิบายปฏิสัมพันธ์ที่มุ่งเป้าหมายระหว่าง Actor กับขอบเขตระบบ", [
        "TERM2/BIS601 Business System Analysis and Design/FINAL/LEATURE/Chapter 8/BIS601_2025_1_08a_activity.pdf",
        "TERM2/BIS601 Business System Analysis and Design/FINAL/LEATURE/Chapter 9/BIS601_2025_1_09_usecases.pdf",
    ], [
        topic("Activity diagram", "แผนภาพกิจกรรม", "A behavioral model of actions, decisions, parallel paths, and flow.", "แบบจำลองพฤติกรรมของกิจกรรม การตัดสินใจ เส้นทางขนาน และการไหล"),
        topic("Actor", "ผู้กระทำ", "An external role that interacts with a system to achieve a goal.", "บทบาทภายนอกที่โต้ตอบกับระบบเพื่อบรรลุเป้าหมาย"),
        topic("Use case", "กรณีใช้งาน", "A sequence of interactions that delivers observable value to an actor.", "ลำดับปฏิสัมพันธ์ที่ส่งมอบคุณค่าที่สังเกตได้ให้ Actor"),
    ]),
    chapter("BIS601", "process-models", "Data-flow and decision modeling", "การสร้างแบบจำลองการไหลของข้อมูลและการตัดสินใจ", "DFDs separate processes, flows, stores, and external entities; decision models make conditional business logic complete and testable.", "DFD แยก Process, Data Flow, Data Store และ External Entity ส่วนแบบจำลองการตัดสินใจทำให้ตรรกะเงื่อนไขครบถ้วนและทดสอบได้", [
        "TERM2/BIS601 Business System Analysis and Design/FINAL/LEATURE/Chapter 10/BIS601_2025_1_10a_DFD.pdf",
        "TERM2/BIS601 Business System Analysis and Design/FINAL/LEATURE/Chapter 11/BIS601_2025_1_11_decision.pdf",
    ], [
        topic("Data-flow diagram", "แผนภาพการไหลของข้อมูล", "A logical model of how data enters, is transformed, stored, and leaves a system.", "แบบจำลองเชิงตรรกะว่าข้อมูลเข้าสู่ระบบ ถูกแปลง จัดเก็บ และออกจากระบบอย่างไร"),
        topic("Balancing", "การสมดุล DFD", "Inputs and outputs remain consistent across decomposition levels.", "ข้อมูลเข้าและออกต้องสอดคล้องกันระหว่างระดับการแตกกระบวนการ"),
        topic("Decision table", "ตารางการตัดสินใจ", "A tabular representation of condition combinations and resulting actions.", "ตารางแสดงชุดเงื่อนไขและการกระทำที่เกิดขึ้น"),
    ]),
    chapter("BIS601", "bpmn", "Business Process Model and Notation", "แบบจำลองและสัญลักษณ์กระบวนการธุรกิจ", "BPMN models events, activities, gateways, sequence flow, message flow, and responsibility across participants in an end-to-end process.", "BPMN ใช้ Event, Activity, Gateway, Sequence Flow, Message Flow และความรับผิดชอบของผู้มีส่วนร่วมเพื่อแสดงกระบวนการตั้งแต่ต้นจนจบ", "TERM2/BIS601 Business System Analysis and Design/FINAL/LEATURE/Chapter 13/BIS601_2025_1_13_BPMN.pdf", [
        topic("Event", "เหตุการณ์", "Something that starts, affects, or ends a process.", "สิ่งที่เริ่ม ส่งผลต่อ หรือยุติกระบวนการ"),
        topic("Gateway", "จุดแยก/รวมเส้นทาง", "A control point that splits or merges process paths.", "จุดควบคุมที่แยกหรือรวมเส้นทางกระบวนการ"),
        topic("Pool and lane", "พูลและเลน", "Responsibility boundaries for participants and roles.", "ขอบเขตความรับผิดชอบของผู้เข้าร่วมและบทบาท"),
    ]),
    # BIS602
    chapter("BIS602", "strategy-and-competition", "Business strategy and competitive advantage", "กลยุทธ์ธุรกิจและความได้เปรียบในการแข่งขัน", "Business strategy sets goals and uses value-chain and industry analysis to select defensible ways to compete with digital capabilities.", "กลยุทธ์ธุรกิจกำหนดเป้าหมายและใช้การวิเคราะห์ห่วงโซ่คุณค่าและอุตสาหกรรมเพื่อเลือกแนวทางแข่งขันที่ปกป้องได้ด้วยความสามารถดิจิทัล", "TERM1/BIS602/Midterm/Lecture/Business strategies.pdf", [
        topic("Competitive advantage", "ความได้เปรียบในการแข่งขัน", "A capability or position that lets a firm create superior value.", "ความสามารถหรือตำแหน่งที่ทำให้องค์กรสร้างคุณค่าเหนือกว่า"),
        topic("Porter's Five Forces", "แรงกดดันห้าประการของพอร์เตอร์", "A framework for analyzing industry rivalry, entry, substitutes, buyers, and suppliers.", "กรอบวิเคราะห์การแข่งขัน ผู้เข้าใหม่ สินค้าทดแทน ผู้ซื้อ และผู้ขาย"),
        topic("Value chain", "ห่วงโซ่คุณค่า", "Linked activities that create and deliver customer value.", "กิจกรรมที่เชื่อมกันเพื่อสร้างและส่งมอบคุณค่าแก่ลูกค้า"),
    ]),
    chapter("BIS602", "process-and-kpi", "Business processes and performance measures", "กระบวนการธุรกิจและตัวชี้วัดผลการดำเนินงาน", "Process management links objectives to measurable outcomes through suitable KPIs, baselines, targets, and causal interpretation.", "การจัดการกระบวนการเชื่อมวัตถุประสงค์กับผลลัพธ์ที่วัดได้ผ่าน KPI ที่เหมาะสม ค่าฐาน เป้าหมาย และการตีความเชิงเหตุผล", "TERM1/BIS602/Midterm/Lecture/BIS602 2023 L2 Business functions and performance measures.pdf", [
        topic("Business process", "กระบวนการธุรกิจ", "Coordinated activities that transform inputs into stakeholder value.", "กิจกรรมประสานกันที่แปลง Input เป็นคุณค่าสำหรับผู้มีส่วนได้ส่วนเสีย"),
        topic("KPI", "ตัวชี้วัดผลการดำเนินงานหลัก", "A metric tied to a critical objective and decision.", "ตัวชี้วัดที่ผูกกับวัตถุประสงค์และการตัดสินใจสำคัญ"),
        topic("Balanced Scorecard", "ดุลยภาพตัวชี้วัด", "A multi-perspective framework covering financial, customer, process, and learning outcomes.", "กรอบหลายมุมมอง ครอบคลุมการเงิน ลูกค้า กระบวนการ และการเรียนรู้"),
    ]),
    chapter("BIS602", "investment-decisions", "Business investment decisions", "การตัดสินใจลงทุนทางธุรกิจ", "Investment analysis compares cash flows across time using discounting, present value, NPV, and risk-aware assumptions.", "การวิเคราะห์การลงทุนเปรียบเทียบกระแสเงินสดต่างเวลาด้วยการคิดลด มูลค่าปัจจุบัน NPV และสมมติฐานที่คำนึงถึงความเสี่ยง", "TERM1/BIS602/Midterm/Lecture/L3 Business Investment Decision.pdf", [
        topic("Time value of money", "มูลค่าเงินตามเวลา", "Money available today differs in value from the same nominal amount later.", "เงินที่มีวันนี้มีมูลค่าไม่เท่ากับจำนวนเงินนามธรรมเดียวกันในอนาคต"),
        topic("Present value", "มูลค่าปัจจุบัน", "A future cash flow discounted to today's value.", "กระแสเงินสดอนาคตที่คิดลดกลับเป็นมูลค่าวันนี้"),
        topic("Net present value", "มูลค่าปัจจุบันสุทธิ", "Discounted benefits minus discounted costs; positive NPV indicates value under the assumptions.", "ผลประโยชน์คิดลดลบต้นทุนคิดลด โดย NPV บวกบ่งชี้การสร้างคุณค่าภายใต้สมมติฐาน"),
    ], formulas=["PV = FV / (1 + r)^n", "NPV = Σ(CF_t / (1 + r)^t) − C₀"]),
    chapter("BIS602", "enterprise-data", "Enterprise data management", "การจัดการข้อมูลองค์กร", "Enterprise data management coordinates data sources, quality, integration, governance, and lifecycle so analytics uses consistent and trustworthy data.", "การจัดการข้อมูลองค์กรประสานแหล่งข้อมูล คุณภาพ การบูรณาการ ธรรมาภิบาล และวงจรชีวิต เพื่อให้การวิเคราะห์ใช้ข้อมูลที่สอดคล้องและเชื่อถือได้", "TERM1/BIS602/Midterm/Lecture/L4 Enterprise Data Management 2024.pdf", [
        topic("Data quality", "คุณภาพข้อมูล", "Fitness for use across accuracy, completeness, consistency, timeliness, and validity.", "ความเหมาะสมต่อการใช้งานด้านความถูกต้อง ครบถ้วน สอดคล้อง ทันเวลา และเป็นไปตามกฎ"),
        topic("ETL", "กระบวนการ ETL", "Extract data, transform it to agreed rules, and load it into a target.", "ดึงข้อมูล แปลงตามกฎที่ตกลง และโหลดเข้าสู่ปลายทาง"),
        topic("Data governance", "ธรรมาภิบาลข้อมูล", "Decision rights, accountability, standards, and controls for data.", "สิทธิในการตัดสินใจ ความรับผิดชอบ มาตรฐาน และการควบคุมข้อมูล"),
    ]),
    chapter("BIS602", "probability-and-statistics", "Probability and business statistics", "ความน่าจะเป็นและสถิติธุรกิจ", "Probability represents uncertainty; descriptive statistics, distributions, z-scores, and outlier analysis support evidence-based business decisions.", "ความน่าจะเป็นแทนความไม่แน่นอน ส่วนสถิติเชิงพรรณนา การแจกแจง z-score และการวิเคราะห์ Outlier สนับสนุนการตัดสินใจด้วยหลักฐาน", [
        "TERM1/BIS602/Midterm/Lecture/L5 Probability v2024.pdf",
        "TERM1/BIS602/Midterm/Lecture/L6 Statistics for Business Decision.pdf",
    ], [
        topic("Expected value", "ค่าคาดหมาย", "The probability-weighted average outcome of a random variable.", "ค่าเฉลี่ยของผลลัพธ์ที่ถ่วงด้วยความน่าจะเป็น"),
        topic("Standard deviation", "ส่วนเบี่ยงเบนมาตรฐาน", "A measure of dispersion around the mean.", "ตัววัดการกระจายรอบค่าเฉลี่ย"),
        topic("Z-score", "คะแนนมาตรฐาน z", "The number of standard deviations an observation lies from the mean.", "จำนวนส่วนเบี่ยงเบนมาตรฐานที่ค่าสังเกตห่างจากค่าเฉลี่ย"),
    ], formulas=["E(X) = Σx·P(x)", "z = (x − μ) / σ"]),
    chapter("BIS602", "data-treatment", "Data treatment and transformation", "การจัดการและแปลงข้อมูล", "Preparation resolves missing values, invalid records, outliers, scale differences, and representation choices before analysis.", "การเตรียมข้อมูลจัดการค่าสูญหาย ระเบียนผิดปกติ Outlier ความต่างของสเกล และรูปแบบการแทนข้อมูลก่อนวิเคราะห์", "TERM1/BIS602/Final/Lacture/L8 Data Treatment and Transformation.pdf", [
        topic("Missing-data treatment", "การจัดการข้อมูลสูญหาย", "Omit or impute values using a method justified by the missingness and task.", "ตัดออกหรือเติมค่าด้วยวิธีที่เหมาะกับสาเหตุการสูญหายและงาน"),
        topic("Transformation", "การแปลงข้อมูล", "Change scale or representation to support analysis while preserving meaning.", "เปลี่ยนสเกลหรือรูปแบบเพื่อสนับสนุนการวิเคราะห์โดยรักษาความหมาย"),
        topic("Binning", "การแบ่งช่วง", "Convert continuous values into defined intervals.", "แปลงค่าต่อเนื่องเป็นช่วงที่กำหนด"),
    ]),
    chapter("BIS602", "bi-and-visualization", "Business intelligence and visualization", "ข่าวกรองธุรกิจและการแสดงภาพข้อมูล", "BI integrates data for reporting and multidimensional analysis; visualization selects encodings that reveal comparisons, trends, composition, and relationships without distortion.", "BI บูรณาการข้อมูลเพื่อรายงานและวิเคราะห์หลายมิติ ส่วนการแสดงภาพเลือกการเข้ารหัสที่เปิดเผยการเปรียบเทียบ แนวโน้ม องค์ประกอบ และความสัมพันธ์โดยไม่บิดเบือน", [
        "TERM1/BIS602/Final/Lacture/L9a BI.pdf",
        "TERM1/BIS602/Final/Lacture/L9b Visualization.pdf",
    ], [
        topic("Business intelligence", "ข่าวกรองธุรกิจ", "Processes and tools that turn integrated data into decision information.", "กระบวนการและเครื่องมือที่เปลี่ยนข้อมูลบูรณาการเป็นสารสนเทศเพื่อการตัดสินใจ"),
        topic("OLAP", "การวิเคราะห์ OLAP", "Interactive multidimensional analysis using operations such as slice, dice, drill, and roll-up.", "การวิเคราะห์หลายมิติแบบโต้ตอบด้วย Slice, Dice, Drill และ Roll-up"),
        topic("Visual encoding", "การเข้ารหัสด้วยภาพ", "Mapping values to position, length, color, shape, or other visual channels.", "การแมปค่ากับตำแหน่ง ความยาว สี รูปร่าง หรือช่องทางภาพอื่น"),
    ]),
    chapter("BIS602", "clustering", "Clustering", "การจัดกลุ่มข้อมูล", "Clustering is unsupervised learning that groups observations by similarity; k-means iteratively assigns points to centroids and updates those centroids.", "Clustering เป็นการเรียนรู้แบบไม่มี Label เพื่อจัดกลุ่มตามความคล้าย โดย k-means จะวนกำหนดจุดให้ Centroid และปรับ Centroid ใหม่", "TERM1/BIS602/Final/Lacture/L10 Clustering.pdf", [
        topic("Unsupervised learning", "การเรียนรู้แบบไม่มีผู้สอน", "Learning structure from observations without target labels.", "การเรียนรู้โครงสร้างจากข้อมูลโดยไม่มี Label เป้าหมาย"),
        topic("K-means", "เคมีนส์", "A centroid-based algorithm minimizing within-cluster squared distance.", "อัลกอริทึมอิงจุดศูนย์กลางที่ลดระยะกำลังสองภายในกลุ่ม"),
        topic("Cluster validation", "การตรวจสอบคุณภาพกลุ่ม", "Assess whether groups are compact, separated, stable, and useful.", "ประเมินว่ากลุ่มกระชับ แยกจากกัน เสถียร และใช้ประโยชน์ได้หรือไม่"),
    ]),
    chapter("BIS602", "classification", "Classification", "การจำแนกประเภท", "Classification learns labeled categories; kNN predicts from nearby observations, while a confusion matrix separates types of correct and incorrect predictions.", "Classification เรียนรู้หมวดหมู่ที่มี Label โดย kNN พยากรณ์จากข้อมูลใกล้เคียง และ Confusion Matrix แยกประเภทผลทำนายที่ถูกและผิด", "TERM1/BIS602/Final/Lacture/L11 Classification.pdf", [
        topic("k-nearest neighbors", "เพื่อนบ้านใกล้ที่สุด k ตัว", "A classifier that votes from the labels of nearby training cases.", "ตัวจำแนกที่ลงคะแนนจาก Label ของกรณีฝึกที่อยู่ใกล้"),
        topic("Confusion matrix", "เมทริกซ์ความสับสน", "Counts predictions by actual and predicted class.", "นับผลทำนายแยกตามคลาสจริงและคลาสที่ทำนาย"),
        topic("Validation", "การตรวจสอบแบบจำลอง", "Estimate generalization with data not used to fit the model.", "ประเมินความสามารถกับข้อมูลที่ไม่ได้ใช้สร้างแบบจำลอง"),
    ], formulas=["Accuracy = (TP + TN) / (TP + TN + FP + FN)", "Precision = TP / (TP + FP)", "Recall = TP / (TP + FN)"]),
    chapter("BIS602", "regression", "Regression", "การวิเคราะห์การถดถอย", "Regression estimates a numeric outcome from explanatory variables and requires interpretation of coefficients, fit, residuals, and assumptions.", "Regression ประมาณค่าผลลัพธ์เชิงตัวเลขจากตัวแปรอธิบาย และต้องตีความสัมประสิทธิ์ ความพอดี Residual และสมมติฐาน", "TERM1/BIS602/Final/Lacture/L12 Regression 2024-2.pdf", [
        topic("Dependent variable", "ตัวแปรตาม", "The numeric outcome a regression model explains or predicts.", "ผลลัพธ์เชิงตัวเลขที่แบบจำลองอธิบายหรือพยากรณ์"),
        topic("Coefficient", "สัมประสิทธิ์", "The estimated change in outcome associated with a predictor, conditional on the model.", "การเปลี่ยนแปลงผลลัพธ์โดยประมาณที่สัมพันธ์กับตัวแปรอธิบายภายใต้แบบจำลอง"),
        topic("Residual", "ค่าคลาดเคลื่อนคงเหลือ", "Observed outcome minus the model prediction.", "ผลลัพธ์จริงลบค่าที่แบบจำลองพยากรณ์"),
    ], formulas=["ŷ = β₀ + β₁x₁ + … + βₚxₚ", "residual = y − ŷ"]),
    chapter("BIS602", "association-and-simulation", "Association analysis and simulation", "การวิเคราะห์ความสัมพันธ์และการจำลอง", "Association rules reveal co-occurrence patterns through support, confidence, and lift; simulation samples uncertain inputs to study a distribution of possible outcomes.", "กฎความสัมพันธ์เปิดเผยรูปแบบการเกิดร่วมด้วย Support, Confidence และ Lift ส่วนการจำลองสุ่ม Input ที่ไม่แน่นอนเพื่อศึกษาการแจกแจงของผลลัพธ์ที่เป็นไปได้", [
        "TERM1/BIS602/Final/Lacture/Association mining.pdf",
        "TERM1/BIS602/Final/Lacture/BIS602 L14 Simulation.pdf",
    ], [
        topic("Support", "ค่าสนับสนุน", "The proportion of transactions containing an itemset.", "สัดส่วนธุรกรรมที่มีชุดรายการ"),
        topic("Confidence", "ค่าความเชื่อมั่นของกฎ", "The conditional frequency of the consequent when the antecedent occurs.", "ความถี่แบบมีเงื่อนไขของผลตามเมื่อเหตุเกิด"),
        topic("Monte Carlo simulation", "การจำลองมอนติคาร์โล", "Repeated random sampling to approximate an outcome distribution.", "การสุ่มซ้ำเพื่อประมาณการแจกแจงของผลลัพธ์"),
    ], formulas=["support(A→B) = P(A∩B)", "confidence(A→B) = P(B|A)", "lift(A→B) = P(B|A) / P(B)"]),
    # BIS605
    chapter("BIS605", "architecture-and-sdlc", "System architecture and software lifecycle", "สถาปัตยกรรมระบบและวงจรชีวิตซอฟต์แวร์", "Architecture describes components, responsibilities, and interactions; the lifecycle organizes how a team discovers, designs, builds, tests, deploys, and evolves the solution.", "สถาปัตยกรรมอธิบายองค์ประกอบ ความรับผิดชอบ และปฏิสัมพันธ์ ส่วนวงจรชีวิตจัดระเบียบการค้นหา ออกแบบ สร้าง ทดสอบ นำไปใช้ และปรับปรุงโซลูชัน", [
        "TERM1/BIS605/Midterm/Lecture/CH01_Introduction.pdf",
        "TERM1/BIS605/Midterm/Lecture/CH02_SWDevlopmentProcess.pdf",
    ], [
        topic("Layered architecture", "สถาปัตยกรรมแบบแบ่งชั้น", "Separates presentation, application, domain, and data responsibilities.", "แยกความรับผิดชอบด้านการนำเสนอ แอปพลิเคชัน โดเมน และข้อมูล"),
        topic("Software lifecycle", "วงจรชีวิตซอฟต์แวร์", "Activities that govern a software product from idea through operation.", "กิจกรรมที่กำกับผลิตภัณฑ์ซอฟต์แวร์ตั้งแต่แนวคิดถึงการปฏิบัติการ"),
        topic("Iterative delivery", "การส่งมอบแบบวนรอบ", "Build and evaluate increments to reduce uncertainty early.", "สร้างและประเมินส่วนเพิ่มเพื่อลดความไม่แน่นอนตั้งแต่ต้น"),
    ]),
    chapter("BIS605", "software-design", "Software design and requirements", "การออกแบบซอฟต์แวร์และความต้องการ", "Design transforms requirements into modular responsibilities, interfaces, data, and interaction choices while controlling coupling and change impact.", "การออกแบบแปลงความต้องการเป็นความรับผิดชอบแบบโมดูล Interface ข้อมูล และปฏิสัมพันธ์ พร้อมควบคุม Coupling และผลกระทบจากการเปลี่ยนแปลง", "TERM1/BIS605/Midterm/Lecture/CH03_SoftwareDesign.pdf", [
        topic("Modularity", "ความเป็นโมดูล", "Decompose a system into focused, replaceable units.", "แบ่งระบบเป็นหน่วยที่มุ่งหน้าที่และเปลี่ยนแทนได้"),
        topic("Cohesion", "ความยึดเหนี่ยวภายใน", "How strongly the responsibilities inside a module belong together.", "ระดับที่ความรับผิดชอบในโมดูลสัมพันธ์เป็นเรื่องเดียวกัน"),
        topic("Coupling", "การพึ่งพาระหว่างโมดูล", "The degree of dependency between modules.", "ระดับการพึ่งพากันระหว่างโมดูล"),
    ]),
    chapter("BIS605", "web-and-ui-design", "Web and interface design principles", "หลักการออกแบบเว็บและส่วนติดต่อ", "Good interfaces align information hierarchy, consistency, feedback, error prevention, accessibility, and responsive behavior with user tasks.", "ส่วนติดต่อที่ดีจัดลำดับข้อมูล ความสอดคล้อง Feedback การป้องกันข้อผิดพลาด การเข้าถึง และ Responsive ให้ตรงกับงานผู้ใช้", [
        "TERM1/BIS605/Midterm/Lecture/CH04_WebDesign_principles.pdf",
        "TERM1/BIS605/Midterm/Lecture/CH05_SoftwareDesign_Figma.pdf",
    ], [
        topic("Visual hierarchy", "ลำดับชั้นทางสายตา", "Use size, contrast, space, and position to communicate importance.", "ใช้ขนาด ความต่าง พื้นที่ว่าง และตำแหน่งเพื่อสื่อความสำคัญ"),
        topic("Usability", "ความสามารถในการใช้งาน", "Effectiveness, efficiency, and satisfaction for intended users.", "ประสิทธิผล ประสิทธิภาพ และความพึงพอใจของผู้ใช้เป้าหมาย"),
        topic("Prototype", "ต้นแบบ", "A testable representation used to learn before full implementation.", "ตัวแทนที่ทดสอบได้เพื่อเรียนรู้ก่อนพัฒนาจริงเต็มรูปแบบ"),
    ]),
    chapter("BIS605", "development-technologies", "Frameworks and development technologies", "เฟรมเวิร์กและเทคโนโลยีการพัฒนา", "Development technologies package conventions, reusable components, version control, containers, and service interfaces to improve delivery consistency.", "เทคโนโลยีการพัฒนารวม Convention ส่วนประกอบใช้ซ้ำ Version Control Container และ Service Interface เพื่อเพิ่มความสม่ำเสมอในการส่งมอบ", "TERM1/BIS605/Midterm/Lecture/CH06_SWDevelopmentTech.pdf", [
        topic("Framework", "เฟรมเวิร์ก", "A reusable structure and conventions for building applications.", "โครงสร้างและข้อตกลงที่ใช้ซ้ำในการสร้างแอปพลิเคชัน"),
        topic("Version control", "การควบคุมเวอร์ชัน", "Track and coordinate changes to source artifacts.", "ติดตามและประสานการเปลี่ยนแปลงของ Source"),
        topic("Container", "คอนเทนเนอร์", "A packaged runtime environment for a process and its dependencies.", "สภาพแวดล้อม Runtime ที่บรรจุ Process และ Dependency"),
    ]),
    chapter("BIS605", "frontend", "HTML, CSS, and JavaScript", "HTML, CSS และ JavaScript", "HTML provides semantic structure, CSS controls presentation and responsive layout, and JavaScript adds behavior and state in the browser.", "HTML ให้โครงสร้างเชิงความหมาย CSS ควบคุมการนำเสนอและ Layout แบบ Responsive ส่วน JavaScript เพิ่มพฤติกรรมและ State ใน Browser", [
        "TERM1/BIS605/Final/Lacture/CH07_FrontEndDevTech_HTML.pdf",
        "TERM1/BIS605/Final/Lacture/CH08_FrontEndDevTech_CSS.pdf",
        "TERM1/BIS605/Final/Lacture/CH09_FrontEndDevTech_JS.pdf",
    ], [
        topic("Semantic HTML", "HTML เชิงความหมาย", "Elements communicate document structure and control meaning.", "Element สื่อโครงสร้างเอกสารและความหมายของ Control"),
        topic("Responsive CSS", "CSS แบบตอบสนอง", "Layouts adapt to available space and user preferences.", "Layout ปรับตามพื้นที่และค่าที่ผู้ใช้เลือก"),
        topic("DOM event", "เหตุการณ์ DOM", "A browser signal handled to produce interactive behavior.", "สัญญาณจาก Browser ที่ถูกจัดการเพื่อสร้างปฏิสัมพันธ์"),
    ]),
    chapter("BIS605", "backend-data-api-cloud-mobile", "Back-end, database, API, cloud, and mobile technologies", "Back-end ฐานข้อมูล API Cloud และ Mobile", "Server-side logic validates requests and coordinates data; databases persist state; APIs define contracts; cloud and mobile technologies shape deployment and client constraints.", "ตรรกะฝั่ง Server ตรวจสอบ Request และประสานข้อมูล ฐานข้อมูลเก็บ State API กำหนด Contract ส่วน Cloud และ Mobile กำหนดข้อจำกัดการ Deploy และ Client", [
        "TERM1/BIS605/Final/Lacture/CH10_BackEndDevTech.pdf",
        "TERM1/BIS605/Final/Lacture/CH11_DatabaseTech.pdf",
        "TERM1/BIS605/Final/Lacture/CH12_API_WS_Cloud_Mobile_Tech 2025-04-05 05_11_06.pdf",
    ], [
        topic("Server-side validation", "การตรวจสอบฝั่งเซิร์ฟเวอร์", "Validate untrusted input where policy and data are controlled.", "ตรวจ Input ที่ไม่เชื่อถือในจุดที่ควบคุมนโยบายและข้อมูล"),
        topic("API contract", "สัญญา API", "An agreed request, response, error, and behavior interface.", "ข้อตกลงของ Request, Response, Error และพฤติกรรม"),
        topic("Cloud service model", "รูปแบบบริการคลาวด์", "A division of responsibility for infrastructure, platform, or software services.", "การแบ่งความรับผิดชอบสำหรับบริการ Infrastructure, Platform หรือ Software"),
    ]),
    # BIS606
    chapter("BIS606", "communications-foundations", "Network communication foundations", "พื้นฐานการสื่อสารเครือข่าย", "Network communication is organized in layers that define services, protocols, encapsulation, addressing, and physical transmission.", "การสื่อสารเครือข่ายจัดเป็นชั้นที่กำหนด Service, Protocol, Encapsulation, Addressing และการส่งสัญญาณทางกายภาพ", [
        "TERM1/BIS606/Midterm/Lecture/ch01 ed14_2.pptx",
        "TERM1/BIS606/Midterm/Lecture/ch02_e14_2 2.pptx",
    ], [
        topic("Protocol", "โพรโทคอล", "Rules and message formats used by communicating entities.", "กฎและรูปแบบข้อความที่หน่วยสื่อสารใช้ร่วมกัน"),
        topic("Encapsulation", "การห่อหุ้มข้อมูล", "Each layer adds control information around higher-layer data.", "แต่ละชั้นเพิ่มข้อมูลควบคุมรอบข้อมูลจากชั้นบน"),
        topic("Transmission medium", "สื่อส่งสัญญาณ", "The physical path carrying electrical, optical, or radio signals.", "เส้นทางกายภาพที่นำสัญญาณไฟฟ้า แสง หรือวิทยุ"),
    ]),
    chapter("BIS606", "data-link-and-tcpip", "Data link, network, and transport layers", "ชั้น Data Link, Network และ Transport", "Frames provide local delivery, IP routes packets across networks, and transport protocols provide application-to-application delivery with different reliability tradeoffs.", "Frame ส่งข้อมูลในเครือข่ายท้องถิ่น IP กำหนดเส้นทาง Packet ข้ามเครือข่าย และ Transport Protocol ส่งระหว่าง Application ด้วยข้อแลกเปลี่ยนด้านความน่าเชื่อถือ", [
        "TERM1/BIS606/Midterm/Lecture/ch03_e14.pdf",
        "TERM1/BIS606/Midterm/Lecture/ch04_14e.pdf",
        "TERM1/BIS606/Midterm/Lecture/ch05_14e.pdf",
    ], [
        topic("Frame", "เฟรม", "A data-link protocol data unit for local-network delivery.", "หน่วยข้อมูลของ Data Link สำหรับการส่งในเครือข่ายท้องถิ่น"),
        topic("IP routing", "การกำหนดเส้นทาง IP", "Forward packets toward destination networks using routing information.", "ส่งต่อ Packet ไปยังเครือข่ายปลายทางด้วยข้อมูลเส้นทาง"),
        topic("TCP and UDP", "TCP และ UDP", "Transport protocols offering different connection, reliability, and overhead properties.", "Transport Protocol ที่มีคุณสมบัติการเชื่อมต่อ ความน่าเชื่อถือ และ Overhead ต่างกัน"),
    ]),
    chapter("BIS606", "lan-wan-internet", "LAN, backbone, WAN, Internet, and network management", "LAN, Backbone, WAN, Internet และการจัดการเครือข่าย", "LANs connect local devices, backbones aggregate segments, WANs span locations, the Internet interconnects networks, and management observes and controls service health.", "LAN เชื่อมอุปกรณ์ในพื้นที่ Backbone รวม Segment, WAN เชื่อมพื้นที่ห่างไกล, Internet เชื่อมเครือข่าย และการจัดการติดตาม/ควบคุมสุขภาพบริการ", [
        "TERM1/BIS606/Final/Lecture/ch07 LAN 14e2.pdf",
        "TERM1/BIS606/Final/Lecture/ch08 Backbone_e142.pdf",
        "TERM1/BIS606/Final/Lecture/ch09 WAN_14e2.pdf",
        "TERM1/BIS606/Final/Lecture/ch10 Internet-14e.pdf",
        "TERM1/BIS606/Final/Lecture/ch12 NetworkMng 14e.pdf",
    ], [
        topic("LAN", "เครือข่ายท้องถิ่น", "A network serving devices within a limited area.", "เครือข่ายที่ให้บริการอุปกรณ์ในพื้นที่จำกัด"),
        topic("WAN", "เครือข่ายบริเวณกว้าง", "A network or service connecting geographically separated sites.", "เครือข่ายหรือบริการที่เชื่อมสถานที่ห่างกัน"),
        topic("Network management", "การจัดการเครือข่าย", "Configuration, monitoring, fault, performance, and security activities.", "กิจกรรมด้าน Configuration, Monitoring, Fault, Performance และ Security"),
    ]),
    chapter("BIS606", "cybersecurity-foundations", "Cybersecurity foundations", "พื้นฐานความมั่นคงปลอดภัยไซเบอร์", "Cybersecurity protects confidentiality, integrity, and availability by managing threats, vulnerabilities, likelihood, impact, controls, and residual risk.", "Cybersecurity คุ้มครอง Confidentiality, Integrity และ Availability ผ่านการจัดการภัยคุกคาม ช่องโหว่ โอกาส ผลกระทบ การควบคุม และความเสี่ยงคงเหลือ", "TERM1/BIS606/Final/Lecture/Ch11Cybersecurity 14e.pdf", [
        topic("CIA triad", "หลัก CIA", "Confidentiality, integrity, and availability security objectives.", "วัตถุประสงค์ด้านความลับ ความถูกต้องครบถ้วน และความพร้อมใช้"),
        topic("Threat and vulnerability", "ภัยคุกคามและช่องโหว่", "A threat may exploit a weakness to cause harm.", "ภัยคุกคามอาจใช้ประโยชน์จากจุดอ่อนเพื่อก่อผลเสีย"),
        topic("Defense in depth", "การป้องกันหลายชั้น", "Layer complementary preventive, detective, and corrective controls.", "ซ้อนการควบคุมเชิงป้องกัน ตรวจจับ และแก้ไขที่เสริมกัน"),
    ]),
    chapter("BIS606", "continuity-and-risk", "Business continuity and risk management", "ความต่อเนื่องทางธุรกิจและการจัดการความเสี่ยง", "Risk management prioritizes treatment using likelihood and impact; continuity planning prepares people, processes, sites, data, and technology to sustain or restore critical services.", "การจัดการความเสี่ยงจัดลำดับการตอบสนองด้วยโอกาสและผลกระทบ ส่วนแผนความต่อเนื่องเตรียมคน กระบวนการ สถานที่ ข้อมูล และเทคโนโลยีเพื่อคงหรือกู้บริการสำคัญ", [
        "TERM1/BIS606/Final/Lecture/12 Business Continuity Management.pdf",
        "TERM1/BIS606/Final/Lecture/13 Risk Management.pdf",
    ], [
        topic("Business impact analysis", "การวิเคราะห์ผลกระทบทางธุรกิจ", "Identify critical activities, dependencies, impacts, and recovery priorities.", "ระบุกิจกรรมสำคัญ การพึ่งพา ผลกระทบ และลำดับการกู้คืน"),
        topic("RTO", "เป้าหมายเวลาการกู้คืน", "Maximum targeted time to restore a service after disruption.", "เวลาสูงสุดเป้าหมายในการกู้บริการหลังหยุดชะงัก"),
        topic("Risk treatment", "การจัดการความเสี่ยง", "Avoid, reduce, transfer/share, or accept risk with accountability.", "หลีกเลี่ยง ลด โอน/แบ่งปัน หรือยอมรับความเสี่ยงอย่างมีผู้รับผิดชอบ"),
    ]),
    chapter("BIS606", "infrastructure-security", "Network, server, and system security", "ความมั่นคงปลอดภัยเครือข่าย เซิร์ฟเวอร์ และระบบ", "Infrastructure security combines segmentation, secure protocols, filtering, hardening, patching, identity, logging, endpoint controls, and monitoring.", "ความมั่นคงปลอดภัยโครงสร้างพื้นฐานผสาน Segmentation, Secure Protocol, Filtering, Hardening, Patching, Identity, Logging, Endpoint Control และ Monitoring", [
        "TERM1/BIS606/Final/Lecture/14 Networks Security-New.pdf",
        "TERM1/BIS606/Final/Lecture/15 Server Security.pdf",
        "TERM1/BIS606/Final/Lecture/16 System Security.pdf",
    ], [
        topic("Network segmentation", "การแบ่งส่วนเครือข่าย", "Limit trust and traffic pathways between security zones.", "จำกัดความไว้วางใจและเส้นทาง Traffic ระหว่างเขตความมั่นคง"),
        topic("System hardening", "การเสริมความแข็งแกร่งระบบ", "Reduce attack surface through secure configuration and removal of unnecessary services.", "ลดพื้นที่โจมตีด้วย Configuration ที่ปลอดภัยและตัด Service ที่ไม่จำเป็น"),
        topic("Security monitoring", "การเฝ้าระวังความมั่นคงปลอดภัย", "Collect and analyze events to detect and respond to abnormal behavior.", "รวบรวมและวิเคราะห์ Event เพื่อตรวจจับและตอบสนองพฤติกรรมผิดปกติ"),
    ]),
    chapter("BIS606", "security-frameworks", "ISO 27001 and CIS controls", "ISO 27001 และ CIS Controls", "Security frameworks turn risk decisions into governance, policies, control objectives, implementation evidence, measurement, audit, and continual improvement.", "กรอบความมั่นคงปลอดภัยแปลงการตัดสินใจด้านความเสี่ยงเป็นธรรมาภิบาล นโยบาย วัตถุประสงค์การควบคุม หลักฐานการดำเนินงาน การวัด Audit และการปรับปรุงต่อเนื่อง", "TERM1/BIS606/Final/Lecture/17. ISO 27001 and CIS.pdf", [
        topic("ISMS", "ระบบบริหารความมั่นคงปลอดภัยสารสนเทศ", "A managed system of scope, policies, risk treatment, controls, evidence, and improvement.", "ระบบบริหารที่มีขอบเขต นโยบาย การจัดการความเสี่ยง การควบคุม หลักฐาน และการปรับปรุง"),
        topic("Statement of Applicability", "เอกสารแสดงการประยุกต์ใช้การควบคุม", "Records selected controls and justification for inclusion or exclusion.", "บันทึกการควบคุมที่เลือกและเหตุผลที่รวมหรือไม่รวม"),
        topic("CIS Controls", "การควบคุม CIS", "Prioritized safeguards for common cyber risks.", "มาตรการป้องกันที่จัดลำดับสำหรับความเสี่ยงไซเบอร์ทั่วไป"),
    ]),
    # BIS603
    chapter("BIS603", "strategy-foundations", "Strategy foundations and foresight", "พื้นฐานกลยุทธ์และการมองอนาคต", "Strategy links a diagnosis of conditions, guiding choices, and coordinated actions; digital strategy connects business goals to changing technologies and capabilities.", "กลยุทธ์เชื่อมการวินิจฉัยเงื่อนไข ทางเลือกนำทาง และการกระทำที่ประสานกัน ส่วนกลยุทธ์ดิจิทัลเชื่อมเป้าหมายธุรกิจกับเทคโนโลยีและความสามารถที่เปลี่ยนแปลง", "TERM2/BIS603 Strategies Maketing Management/MIDTERM/LACTURE/Chapter1/Lecture 1 Intro to Strategy.pdf", [
        topic("Strategy", "กลยุทธ์", "An integrated set of choices about where and how to create advantage.", "ชุดทางเลือกที่บูรณาการว่าจะสร้างความได้เปรียบที่ใดและอย่างไร"),
        topic("Strategic foresight", "การมองอนาคตเชิงกลยุทธ์", "Explore plausible futures to improve present choices.", "สำรวจอนาคตที่เป็นไปได้เพื่อปรับปรุงการเลือกในปัจจุบัน"),
        topic("Digital capability", "ความสามารถดิจิทัล", "Organizational ability to use technology, data, people, and process toward strategy.", "ความสามารถองค์กรในการใช้เทคโนโลยี ข้อมูล คน และกระบวนการตามกลยุทธ์"),
    ], confidence="medium"),
    chapter("BIS603", "external-analysis", "External strategic analysis", "การวิเคราะห์กลยุทธ์ภายนอก", "External analysis examines macro forces, industry structure, stakeholders, competitors, opportunities, threats, and uncertainty outside the firm.", "การวิเคราะห์ภายนอกพิจารณาแรงระดับมหภาค โครงสร้างอุตสาหกรรม ผู้มีส่วนได้ส่วนเสีย คู่แข่ง โอกาส ภัยคุกคาม และความไม่แน่นอนภายนอกองค์กร", "TERM2/BIS603 Strategies Maketing Management/MIDTERM/LACTURE/Chapter2/Lecture 2 External Analysis.pdf", [
        topic("PESTEL", "PESTEL", "A scan of political, economic, social, technological, environmental, and legal forces.", "การสำรวจแรงด้านการเมือง เศรษฐกิจ สังคม เทคโนโลยี สิ่งแวดล้อม และกฎหมาย"),
        topic("Industry analysis", "การวิเคราะห์อุตสาหกรรม", "Assess structure, competitive pressure, and profit potential.", "ประเมินโครงสร้าง แรงแข่งขัน และศักยภาพกำไร"),
        topic("Opportunity and threat", "โอกาสและภัยคุกคาม", "External conditions that may help or hinder strategic objectives.", "เงื่อนไขภายนอกที่อาจสนับสนุนหรือขัดขวางวัตถุประสงค์"),
    ], confidence="medium"),
    chapter("BIS603", "internal-analysis", "Internal strategic analysis", "การวิเคราะห์กลยุทธ์ภายใน", "Internal analysis evaluates resources, capabilities, processes, culture, cost drivers, and distinctive strengths that can support advantage.", "การวิเคราะห์ภายในประเมินทรัพยากร ความสามารถ กระบวนการ วัฒนธรรม ตัวขับต้นทุน และจุดแข็งที่แตกต่างซึ่งสนับสนุนความได้เปรียบ", "TERM2/BIS603 Strategies Maketing Management/MIDTERM/LACTURE/Chapter3/Lecture 3 Internal Analysis.pdf", [
        topic("Resource", "ทรัพยากร", "An asset available to the organization.", "สินทรัพย์ที่องค์กรนำมาใช้ได้"),
        topic("Capability", "ความสามารถองค์กร", "A repeatable ability to coordinate resources and perform activities.", "ความสามารถทำซ้ำในการประสานทรัพยากรและดำเนินกิจกรรม"),
        topic("VRIO", "กรอบ VRIO", "Tests whether resources are valuable, rare, hard to imitate, and organizationally supported.", "ทดสอบว่าทรัพยากรมีคุณค่า หายาก เลียนแบบยาก และองค์กรรองรับหรือไม่"),
    ], confidence="medium"),
    chapter("BIS603", "strategy-formulation", "Strategy formulation and alignment", "การกำหนดและทำให้กลยุทธ์สอดคล้อง", "Formulation converts analysis into objectives, strategic alternatives, tradeoffs, a coherent choice, implementation priorities, and measures.", "การกำหนดกลยุทธ์แปลงผลวิเคราะห์เป็นวัตถุประสงค์ ทางเลือก ข้อแลกเปลี่ยน ทางเลือกที่สอดคล้อง ลำดับการนำไปใช้ และตัววัด", "TERM2/BIS603 Strategies Maketing Management/MIDTERM/LACTURE/Chapter4/Lecture4Strategy Formulationv2.pdf", [
        topic("Strategic alternative", "ทางเลือกเชิงกลยุทธ์", "A distinct route for achieving objectives.", "แนวทางที่แตกต่างเพื่อบรรลุวัตถุประสงค์"),
        topic("Tradeoff", "ข้อแลกเปลี่ยน", "Choosing one position or allocation limits another.", "การเลือกตำแหน่งหรือการจัดสรรหนึ่งย่อมจำกัดอีกทาง"),
        topic("Strategic alignment", "ความสอดคล้องเชิงกลยุทธ์", "Objectives, capabilities, initiatives, and measures reinforce one another.", "วัตถุประสงค์ ความสามารถ โครงการ และตัววัดสนับสนุนกัน"),
    ], confidence="medium"),
    chapter("BIS603", "marketing-foundations", "Marketing foundations and planning", "พื้นฐานและการวางแผนการตลาด", "Marketing identifies and serves selected customer needs through segmentation, targeting, positioning, coordinated value choices, situation analysis, and planned execution.", "การตลาดระบุและตอบสนองความต้องการลูกค้าเป้าหมายผ่าน Segmentation, Targeting, Positioning การกำหนดคุณค่า การวิเคราะห์สถานการณ์ และการดำเนินงานตามแผน", "TERM2/BIS603 Strategies Maketing Management/MIDTERM/LACTURE/Chapter6/Lecture 6_Intro_Marketing_2025_08_24.pdf", [
        topic("STP", "STP", "Segment the market, select targets, and position a value proposition.", "แบ่งส่วนตลาด เลือกตลาดเป้าหมาย และวางตำแหน่งคุณค่า"),
        topic("Marketing mix", "ส่วนประสมการตลาด", "Coordinated product, price, place, and promotion choices.", "ทางเลือกผลิตภัณฑ์ ราคา ช่องทาง และการส่งเสริมที่ประสานกัน"),
        topic("SOSTAC", "กรอบ SOSTAC", "Situation, objectives, strategy, tactics, action, and control planning.", "การวางแผน Situation, Objectives, Strategy, Tactics, Action และ Control"),
    ], confidence="medium"),
    chapter("BIS603", "digital-marketing-data-ai", "Digital marketing, customer data, and AI", "การตลาดดิจิทัล ข้อมูลลูกค้า และ AI", "Digital marketing coordinates paid, owned, and earned channels with measurable journeys; customer data and AI can improve targeting and decisions but introduce privacy, bias, and governance risks.", "การตลาดดิจิทัลประสานช่องทาง Paid, Owned และ Earned กับ Customer Journey ที่วัดได้ ข้อมูลลูกค้าและ AI ช่วย Targeting/Decision แต่เพิ่มความเสี่ยงด้านความเป็นส่วนตัว Bias และ Governance", [
        "TERM2/BIS603 Strategies Maketing Management/FINAL/Leature/Lecture 7_Intro_Digital_Marketing_2025_09_07.pdf",
        "TERM2/BIS603 Strategies Maketing Management/FINAL/Leature/Lecture 10 AI and Big Data in Marketing.pdf",
        "TERM2/BIS603 Strategies Maketing Management/FINAL/Leature/Cambridge Analyticas_long2025.pdf",
    ], [
        topic("Customer journey", "เส้นทางลูกค้า", "Stages and touchpoints through which a customer becomes aware, considers, converts, and remains.", "ขั้นและ Touchpoint ที่ลูกค้ารับรู้ พิจารณา ซื้อ และคงอยู่"),
        topic("Marketing attribution", "การระบุผลของช่องทางการตลาด", "Assign credit for outcomes across marketing interactions.", "กำหนดสัดส่วนผลลัพธ์ให้ปฏิสัมพันธ์ทางการตลาด"),
        topic("Responsible marketing data", "การใช้ข้อมูลการตลาดอย่างรับผิดชอบ", "Use data with purpose limitation, transparency, fairness, security, and accountability.", "ใช้ข้อมูลโดยจำกัดวัตถุประสงค์ โปร่งใส เป็นธรรม ปลอดภัย และรับผิดชอบ"),
    ], confidence="medium"),
    chapter("BIS603", "financial-strategy", "Financial strategy for entrepreneurs", "กลยุทธ์การเงินสำหรับผู้ประกอบการ", "Financial strategy connects business models and growth plans to revenue logic, cost structure, cash needs, funding choices, risk, and investor expectations.", "กลยุทธ์การเงินเชื่อมโมเดลธุรกิจและแผนเติบโตกับตรรกะรายได้ โครงสร้างต้นทุน เงินสดที่ต้องใช้ ทางเลือกเงินทุน ความเสี่ยง และความคาดหวังนักลงทุน", "TERM2/BIS603 Strategies Maketing Management/FINAL/Leature/Financial Strategy for Entrepreneurs [Backup].pdf", [
        topic("Unit economics", "เศรษฐศาสตร์ต่อหน่วย", "Revenue and variable cost relationships for one customer, order, or unit.", "ความสัมพันธ์รายได้และต้นทุนผันแปรต่อหนึ่งลูกค้า คำสั่งซื้อ หรือหน่วย"),
        topic("Cash runway", "ระยะเวลาที่เงินสดรองรับ", "How long available cash can fund operations at the current burn rate.", "ระยะเวลาที่เงินสดรองรับการดำเนินงานตามอัตราการใช้เงินปัจจุบัน"),
        topic("Funding choice", "ทางเลือกแหล่งเงินทุน", "Select equity, debt, internal cash, or alternatives with control and risk tradeoffs.", "เลือกทุน หนี้ เงินภายใน หรือทางเลือกอื่นโดยพิจารณาการควบคุมและความเสี่ยง"),
    ], confidence="medium"),
    # BIS604
    chapter("BIS604", "database-foundations", "Database and data-management foundations", "พื้นฐานฐานข้อมูลและการจัดการข้อมูล", "Database management replaces isolated files with shared, controlled data, metadata, integrity rules, security, and concurrent access managed through a DBMS.", "การจัดการฐานข้อมูลแทนไฟล์แยกส่วนด้วยข้อมูลร่วมที่ควบคุมได้ Metadata กฎความถูกต้อง Security และการเข้าถึงพร้อมกันผ่าน DBMS", [
        "TERM2/BIS603_BIS604 Bussiness Data Management/MIDTERM/LACTURE/OutlineBIS604_1_2025_New1.pdf",
        "TERM2/BIS603_BIS604 Bussiness Data Management/MIDTERM/LACTURE/Chapter1/01BusinessDBMgmt 2025-07-19 02_53_26.pdf",
    ], [
        topic("Database", "ฐานข้อมูล", "An organized, integrated collection of related data.", "ชุดข้อมูลที่เกี่ยวข้องซึ่งจัดระเบียบและบูรณาการ"),
        topic("DBMS", "ระบบจัดการฐานข้อมูล", "Software that defines, stores, queries, protects, and controls a database.", "ซอฟต์แวร์ที่กำหนด จัดเก็บ สืบค้น ปกป้อง และควบคุมฐานข้อมูล"),
        topic("Metadata", "เมทาดาทา", "Data describing structures, meaning, constraints, and lineage of other data.", "ข้อมูลที่อธิบายโครงสร้าง ความหมาย ข้อจำกัด และที่มาของข้อมูลอื่น"),
    ]),
    chapter("BIS604", "data-models", "Data models", "แบบจำลองข้อมูล", "A data model provides concepts and rules for describing entities, relationships, constraints, and operations at conceptual, logical, and physical levels.", "แบบจำลองข้อมูลให้แนวคิดและกฎเพื่ออธิบาย Entity, Relationship, Constraint และ Operation ในระดับ Conceptual, Logical และ Physical", "TERM2/BIS603_BIS604 Bussiness Data Management/MIDTERM/LACTURE/Chapter2/Coronel_DatabaseSystems_13e_ch02_adj4Covid.pdf", [
        topic("Conceptual model", "แบบจำลองเชิงแนวคิด", "A technology-independent business view of data and relationships.", "มุมมองข้อมูลและความสัมพันธ์ทางธุรกิจที่ไม่ผูกเทคโนโลยี"),
        topic("Logical model", "แบบจำลองเชิงตรรกะ", "A detailed structure for a model type, independent of a specific storage product.", "โครงสร้างละเอียดตามชนิดโมเดลโดยไม่ผูกผลิตภัณฑ์จัดเก็บ"),
        topic("Physical model", "แบบจำลองเชิงกายภาพ", "Implementation structures optimized for a specific DBMS.", "โครงสร้างนำไปใช้ที่ปรับให้เหมาะกับ DBMS เฉพาะ"),
    ]),
    chapter("BIS604", "relational-model", "Relational model and keys", "แบบจำลองเชิงสัมพันธ์และคีย์", "The relational model organizes tuples in relations, uses keys to identify and connect records, and enforces entity and referential integrity.", "แบบจำลองเชิงสัมพันธ์จัด Tuple ใน Relation ใช้ Key ระบุและเชื่อม Record และบังคับ Entity/Referential Integrity", "TERM2/BIS603_BIS604 Bussiness Data Management/MIDTERM/LACTURE/Chapter3/Coronel_PPT_Ch034_for2_2017CovidAddCandidateNew.pdf", [
        topic("Primary key", "คีย์หลัก", "A minimal selected identifier that is unique and not null.", "ตัวระบุขั้นต่ำที่เลือก ซึ่งไม่ซ้ำและไม่เป็น Null"),
        topic("Foreign key", "คีย์นอก", "Attributes referencing a candidate key in a related relation.", "Attribute ที่อ้าง Candidate Key ใน Relation ที่เกี่ยวข้อง"),
        topic("Referential integrity", "บูรณภาพการอ้างอิง", "Foreign-key values must match a referenced key or satisfy an allowed null rule.", "ค่าคีย์นอกต้องตรงกับคีย์ที่อ้าง หรือเป็น Null ตามกฎที่อนุญาต"),
    ]),
    chapter("BIS604", "business-rules-and-erd", "Business rules and ER modeling", "กฎธุรกิจและแบบจำลอง ER", "Business rules define entities, attributes, relationships, cardinality, participation, and constraints that an ER model makes explicit.", "กฎธุรกิจกำหนด Entity, Attribute, Relationship, Cardinality, Participation และ Constraint ซึ่ง ER Model ทำให้เห็นชัด", [
        "TERM2/BIS603_BIS604 Bussiness Data Management/MIDTERM/LACTURE/Chapter4/BusinessRulesExercise_additional_New.pdf",
        "TERM2/BIS603_BIS604 Bussiness Data Management/MIDTERM/LACTURE/Chapter5/Example4ERDSegment.pdf",
    ], [
        topic("Entity", "เอนทิตี", "A distinguishable business object or concept about which data is stored.", "วัตถุหรือแนวคิดธุรกิจที่แยกได้และต้องเก็บข้อมูล"),
        topic("Cardinality", "คาร์ดินาลิตี", "The maximum number of relationship occurrences allowed.", "จำนวนสูงสุดของความสัมพันธ์ที่อนุญาต"),
        topic("Associative entity", "เอนทิตีเชื่อม", "An entity used to represent a many-to-many relationship and its attributes.", "Entity ที่แทนความสัมพันธ์หลายต่อหลายและ Attribute ของความสัมพันธ์"),
    ]),
    chapter("BIS604", "normalization", "Normalization", "การทำ Normalization", "Normalization uses functional dependencies and normal forms to reduce redundancy and prevent insert, update, and delete anomalies while preserving required relationships.", "Normalization ใช้ Functional Dependency และ Normal Form เพื่อลดความซ้ำและป้องกัน Insert, Update, Delete Anomaly โดยรักษาความสัมพันธ์ที่จำเป็น", "TERM2/BIS603_BIS604 Bussiness Data Management/FINAL/Chapter6/Leature/Coronel_DatabaseSystems_13e_ch06.pdf", [
        topic("Functional dependency", "การขึ้นต่อกันเชิงฟังก์ชัน", "One attribute set determines another attribute set.", "ชุด Attribute หนึ่งกำหนดค่าของอีกชุด"),
        topic("Second normal form", "รูปแบบปกติที่สอง", "1NF with no partial dependency of a non-key attribute on a candidate key.", "1NF ที่ไม่มี Non-key Attribute ขึ้นกับเพียงบางส่วนของ Candidate Key"),
        topic("Third normal form", "รูปแบบปกติที่สาม", "2NF with no disallowed transitive dependency of non-key attributes.", "2NF ที่ไม่มีการขึ้นต่อแบบส่งผ่านของ Non-key Attribute ที่ไม่อนุญาต"),
    ]),
    chapter("BIS604", "sql-and-implementation", "SQL and database implementation", "SQL และการสร้างฐานข้อมูล", "SQL defines schema and constraints, changes stored data, and retrieves it through selection, projection, joins, grouping, expressions, and transactions.", "SQL กำหนด Schema/Constraint เปลี่ยนข้อมูล และสืบค้นด้วย Selection, Projection, Join, Grouping, Expression และ Transaction", [
        "TERM2/BIS603_BIS604 Bussiness Data Management/FINAL/Chapter7/Coronel_DatabaseSystems_13e_ch07.pdf",
        "TERM2/BIS603_BIS604 Bussiness Data Management/FINAL/Class10/ขั้นตอนในการเข้าใข้ SQLPlus เพื่อส่งคำสั่ง SQL Statement.pdf",
    ], [
        topic("DDL", "ภาษากำหนดข้อมูล", "SQL statements that create or alter database structures and constraints.", "คำสั่ง SQL ที่สร้างหรือแก้โครงสร้างและ Constraint"),
        topic("DML", "ภาษาจัดการข้อมูล", "SQL statements that insert, update, delete, and query data.", "คำสั่ง SQL สำหรับ Insert, Update, Delete และ Query"),
        topic("Join", "การเชื่อมตาราง", "Combine rows from related tables using a condition.", "รวมแถวจากตารางที่เกี่ยวข้องด้วยเงื่อนไข"),
    ]),
]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def ref_id(file_id: str, chapter_id: str) -> str:
    token = hashlib.sha256(f"{file_id}:{chapter_id}".encode("utf-8")).hexdigest()[:12]
    return f"ref-{token}"


def page_count(readability_note: str) -> int | None:
    match = re.match(r"pdf:(\d+)_pages", readability_note or "")
    return int(match.group(1)) if match else None


def dump(name: str, key: str, values: list[dict[str, Any]], generated_at: str) -> None:
    payload = {"schema_version": "1.0.0", "generated_at": generated_at, key: values}
    (ROOT / f"data/{name}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def markdown_list(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) if values else "- None identified."


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat()
    inventory_payload = json.loads((ROOT / "data/file-inventory.json").read_text(encoding="utf-8"))
    inventory_by_path = {item["relative_path"]: item for item in inventory_payload["files"]}
    subject_records: list[dict[str, Any]] = []
    chapter_records: list[dict[str, Any]] = []
    topic_records: list[dict[str, Any]] = []
    glossary_records: list[dict[str, Any]] = []
    source_references: list[dict[str, Any]] = []
    chapters_by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    source_ids_by_subject: dict[str, set[str]] = defaultdict(set)

    for order, spec in enumerate(CHAPTERS, 1):
        code = spec["code"]
        chapter_id = f"chapter-{code.casefold()}-{spec['slug']}"
        chapter_ref_ids: list[str] = []
        for source_path in spec["sources"]:
            if source_path not in inventory_by_path:
                raise SystemExit(f"Academic source missing from inventory: {source_path}")
            source = inventory_by_path[source_path]
            source_ids_by_subject[code].add(source["file_id"])
            source_reference_id = ref_id(source["file_id"], chapter_id)
            chapter_ref_ids.append(source_reference_id)
            locator_end = page_count(source["readability_note"])
            source_references.append(
                {
                    "source_reference_id": source_reference_id,
                    "file_id": source["file_id"],
                    "relative_path": source_path,
                    "locator_type": "page_or_slide_range",
                    "locator_start": 1,
                    "locator_end": locator_end,
                    "locator_note": (
                        f"Whole {locator_end}-page source supports this chapter-level summary."
                        if locator_end
                        else "Whole supplied slide/document source supports this chapter-level summary; exact final slide is not encoded in the inventory."
                    ),
                    "evidence_type": spec["evidence_type"],
                }
            )

        current_topics: list[str] = []
        glossary_ids: list[str] = []
        for topic_order, topic_spec in enumerate(spec["topics"], 1):
            topic_id = f"topic-{code.casefold()}-{spec['slug']}-{topic_order:02d}"
            glossary_id = f"glossary-{code.casefold()}-{spec['slug']}-{topic_order:02d}"
            current_topics.append(topic_id)
            glossary_ids.append(glossary_id)
            topic_records.append(
                {
                    "topic_id": topic_id,
                    "subject_id": f"subject-{code.casefold()}",
                    "chapter_id": chapter_id,
                    "title_en": topic_spec["title_en"],
                    "title_th": topic_spec["title_th"],
                    "summary_en": topic_spec["definition_en"],
                    "summary_th": topic_spec["definition_th"],
                    "source_reference_ids": chapter_ref_ids,
                    "confidence": spec["confidence"],
                    "evidence_type": spec["evidence_type"],
                    "order": topic_order,
                }
            )
            glossary_records.append(
                {
                    "glossary_id": glossary_id,
                    "term_en": topic_spec["title_en"],
                    "term_th": topic_spec["title_th"],
                    "definition_en": topic_spec["definition_en"],
                    "explanation_th": topic_spec["definition_th"],
                    "subject_id": f"subject-{code.casefold()}",
                    "chapter_id": chapter_id,
                    "source_reference_ids": chapter_ref_ids,
                    "confidence": spec["confidence"],
                    "evidence_type": spec["evidence_type"],
                }
            )

        concepts = [item["title_en"] for item in spec["topics"]]
        comparison = (
            f"Distinguish `{concepts[0]}` from `{concepts[1]}` by purpose, input, and decision use."
            if len(concepts) > 1
            else "Compare alternative applications by purpose and evidence."
        )
        chapter_record = {
            "chapter_id": chapter_id,
            "subject_id": f"subject-{code.casefold()}",
            "course_code": code,
            "title_en": spec["title_en"],
            "title_th": spec["title_th"],
            "concise_summary_en": spec["summary_en"],
            "concise_summary_th": spec["summary_th"],
            "detailed_explanation_th": (
                f"{spec['summary_th']} ให้เริ่มจากวัตถุประสงค์ทางธุรกิจ ระบุข้อมูลหรือเงื่อนไขที่ต้องใช้ "
                "เลือกแนวคิดหรือขั้นตอนให้ตรงกับโจทย์ ตรวจสมมติฐาน แล้วสื่อความหมายของผลลัพธ์และข้อจำกัดอย่างชัดเจน"
            ),
            "topic_ids": current_topics,
            "technical_terms": concepts,
            "definitions": [
                {
                    "term_en": item["title_en"],
                    "term_th": item["title_th"],
                    "definition_en": item["definition_en"],
                    "definition_th": item["definition_th"],
                }
                for item in spec["topics"]
            ],
            "concepts": concepts,
            "processes_and_frameworks": [
                f"Identify the purpose and boundary of {spec['title_en']}.",
                f"Apply {', '.join(concepts)} in the order required by the case.",
                "Check assumptions, evidence quality, and stakeholder consequences.",
            ],
            "formulas": spec["formulas"],
            "examples": [
                f"Apply {spec['title_en'].casefold()} to a supplied exercise or business case and justify each choice from the source material."
            ],
            "comparison_summaries": [comparison],
            "common_misunderstandings": [
                f"Treating {concepts[0]} as a label to memorize instead of explaining its decision purpose.",
                "Presenting a result without checking assumptions, scope, or evidence limitations.",
            ],
            "likely_examination_points": [
                f"Define and distinguish {', '.join(concepts)}.",
                f"Apply the chapter framework to a short case and justify the selected concept.",
                "Interpret the result, limitation, or next action.",
            ],
            "review_points": [
                spec["summary_en"],
                comparison,
                "Always connect the technique to a business decision and its evidence.",
            ],
            "memory_aid": "Purpose → evidence → method → result → limitation.",
            "short_review_questions": [
                f"What decision problem does {spec['title_en']} address?",
                f"How do {concepts[0]} and {concepts[1]} differ?" if len(concepts) > 1 else "What evidence is required?",
                "Which assumptions or limitations should be disclosed?",
            ],
            "source_reference_ids": chapter_ref_ids,
            "confidence": spec["confidence"],
            "evidence_type": spec["evidence_type"],
            "order": order,
        }
        chapter_records.append(chapter_record)
        chapters_by_subject[code].append(chapter_record)

    for code, subject in SUBJECTS.items():
        chapter_ids = [item["chapter_id"] for item in chapters_by_subject[code]]
        themes = [item["title_en"] for item in chapters_by_subject[code]]
        record = {
            "subject_id": f"subject-{code.casefold()}",
            "course_code": code,
            "course_title_en": subject["title_en"],
            "course_title_th": subject["title_th"],
            "term": subject["term"],
            "source_file_ids": sorted(source_ids_by_subject[code]),
            "learning_objectives_en": subject["objectives_en"],
            "learning_objectives_th": subject["objectives_th"],
            "overview_en": subject["overview_en"],
            "overview_th": subject["overview_th"],
            "major_themes": themes,
            "topic_relationships_en": "The chapters progress from foundations and problem framing to analysis/design techniques and applied decision or implementation concerns.",
            "topic_relationships_th": "บทเรียนดำเนินจากพื้นฐานและการกำหนดปัญหา ไปสู่เทคนิควิเคราะห์/ออกแบบและประเด็นการตัดสินใจหรือนำไปใช้",
            "examination_focus": [
                "Definitions and distinctions among core concepts",
                "Framework or process application to a short case",
                "Interpretation, limitations, and justified next actions",
            ],
            "chapter_ids": chapter_ids,
            "mapping_confidence": subject["mapping_confidence"],
            "mapping_note": subject["mapping_note"],
        }
        subject_records.append(record)

        subject_dir = ROOT / f"docs/subjects/{code}"
        subject_dir.mkdir(parents=True, exist_ok=True)
        source_paths = sorted(
            inventory_by_path_path
            for inventory_by_path_path, item in inventory_by_path.items()
            if item["file_id"] in source_ids_by_subject[code]
        )
        overview_md = f"""# {code} — {subject["title_en"]}

## ชื่อวิชา

{subject["title_th"]}

## Subject overview

{subject["overview_en"]}

## ภาพรวมรายวิชา

{subject["overview_th"]}

## Learning objectives

{markdown_list(subject["objectives_en"])}

## วัตถุประสงค์การเรียนรู้

{markdown_list(subject["objectives_th"])}

## Chapter structure

{markdown_list([f'[{item["title_en"]}]({item["chapter_id"]}.md) — {item["title_th"]}' for item in chapters_by_subject[code]])}

## Examination focus supported by sources

- Define and distinguish the chapter's core terms.
- Apply a process, framework, formula, or model to a short business case.
- Interpret evidence, assumptions, limitations, and a justified next action.

## Source documents used

{markdown_list([f'`{path}`' for path in source_paths])}

## Mapping status

- Confidence: `{subject["mapping_confidence"]}`
- Note: {subject["mapping_note"]}
"""
        (subject_dir / "overview.md").write_text(overview_md, encoding="utf-8")

    for item in chapter_records:
        subject_dir = ROOT / f"docs/subjects/{item['course_code']}"
        definition_lines = [
            f"- **{definition['term_en']} / {definition['term_th']}** — {definition['definition_en']}  \n  {definition['definition_th']}"
            for definition in item["definitions"]
        ]
        sources = [
            next(ref for ref in source_references if ref["source_reference_id"] == source_ref)
            for source_ref in item["source_reference_ids"]
        ]
        source_lines = [
            f"- `{source['file_id']}` — `{source['relative_path']}`, "
            f"{'pp./slides ' + str(source['locator_start']) + '–' + str(source['locator_end']) if source['locator_end'] else 'whole document/slide deck'}"
            for source in sources
        ]
        chapter_md = f"""# {item["title_en"]}

## {item["title_th"]}

### Concise summary

{item["concise_summary_en"]}

### สรุปภาษาไทย

{item["concise_summary_th"]}

### คำอธิบายโดยละเอียด

{item["detailed_explanation_th"]}

### Technical terms and definitions

{chr(10).join(definition_lines)}

### Processes and frameworks

{markdown_list(item["processes_and_frameworks"])}

### Formulas

{markdown_list([f'`{formula}`' for formula in item["formulas"]]) if item["formulas"] else "- No primary formula is required for this chapter."}

### Example

{markdown_list(item["examples"])}

### Comparison

{markdown_list(item["comparison_summaries"])}

### Common misunderstandings

{markdown_list(item["common_misunderstandings"])}

### Likely examination points

{markdown_list(item["likely_examination_points"])}

### Study aids

- Review: {item["review_points"][0]}
- Memory aid: **{item["memory_aid"]}**
- Review questions:
{chr(10).join(f'  - {question}' for question in item["short_review_questions"])}

### Sources

{chr(10).join(source_lines)}

### Evidence

- Confidence: `{item["confidence"]}`
- Evidence type: `{item["evidence_type"]}`
"""
        (subject_dir / f"{item['chapter_id']}.md").write_text(chapter_md, encoding="utf-8")

    dump("subjects", "subjects", subject_records, generated_at)
    dump("chapters", "chapters", chapter_records, generated_at)
    dump("topics", "topics", topic_records, generated_at)
    dump("glossary", "glossary", glossary_records, generated_at)
    dump("source-references", "source_references", source_references, generated_at)

    review = f"""# Phase 1 Content Human Review

## Medium-confidence course mapping

- `subject-bis603` — The supplied directory pairs `BIS603` with `Strategies Maketing Management`, and the lectures clearly cover strategy and marketing, but no sampled authoritative outline states the exact code-title pair. The normalized display title remains the supplied wording and is not presented as independently verified.

## Extraction limitations carried forward

- Five PDFs have no extractable text sample and require visual inspection if used for a specific academic claim.
- Image and Draw.io diagrams were inventoried but not OCR-transcribed; no claim in the structured knowledge base depends solely on them.
- Legacy `.doc` files remain unsupported; equivalent PDF/PPTX/DOCX sources were used where available.

## Supplementary study aids

The reusable prompts “purpose → evidence → method → result → limitation,” generic review questions, and generic case-application instructions are labelled in the data as part of source-summarized chapter aids. They organize study but do not introduce a new academic answer.

## Low-confidence generated content

No low-confidence chapter, topic, or glossary entry was generated. Medium-confidence BIS603 entries retain their mapping warning.
"""
    (ROOT / "reports/content-human-review.md").write_text(review, encoding="utf-8")

    report = f"""# Phase 1 Content Analysis Report

- Status: **completed pending validation**
- Subjects: **{len(subject_records)}**
- Chapters: **{len(chapter_records)}**
- Topics: **{len(topic_records)}**
- Glossary entries: **{len(glossary_records)}**
- Source references: **{len(source_references)}**
- Bilingual subject overviews: **{len(subject_records)}**
- Bilingual chapter documents: **{len(chapter_records)}**

## Method

The knowledge base follows verified course outlines and the supplied lecture sequence. Each chapter is anchored to one or more immutable source file IDs. Chapter-level references cover the complete source used for synthesis; topics and glossary definitions inherit those references. No original file was modified.

## Coverage

- Term 1: BIS602, BIS605, BIS606
- Term 2: BIS601, BIS603-context strategy/marketing materials, BIS604
- Foundations, frameworks, formulas where applicable, examples, comparisons, traps, likely examination points, memory aids, and review questions are represented.

## Warnings

- BIS603's exact code-title pairing remains medium confidence and requires human confirmation.
- Visual-only diagrams and image-only PDFs remain inventoried but were not used as sole textual evidence.
"""
    (ROOT / "reports/phase-1-content-analysis-report.md").write_text(report, encoding="utf-8")
    print(
        f"Wrote {len(subject_records)} subjects, {len(chapter_records)} chapters, "
        f"{len(topic_records)} topics, and {len(glossary_records)} glossary entries."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

