#!/usr/bin/env python3
"""Build structured, bilingual, source-labelled Study Library lessons."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WEB_DATA = ROOT / "web/src/data"
GENERATED_AT = "2026-07-28T09:30:00+07:00"

COURSE_LABEL = {
    "source_category": "course_material",
    "source_label_en": "From course materials",
    "source_label_th": "จากเอกสารการเรียน",
}
SUPPLEMENTARY_LABEL = {
    "source_category": "supplementary_explanation",
    "source_label_en": "Supplementary explanation",
    "source_label_th": "คำอธิบายเสริม",
}


def read_json(name: str) -> dict[str, Any]:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def write_payload(name: str, payload: dict[str, Any]) -> None:
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    (DATA / name).write_text(rendered, encoding="utf-8")
    (WEB_DATA / name).write_text(rendered, encoding="utf-8")


def labelled(category: dict[str, str], **values: Any) -> dict[str, Any]:
    return {**values, **category}


def question_wording(question: dict[str, Any]) -> list[str]:
    lowered = question["original_question_en"].casefold()
    phrases = (
        "incorrect",
        "except",
        "best",
        "most appropriate",
        "primarily",
    )
    return [phrase for phrase in phrases if phrase in lowered]


FORMULA_DETAILS: dict[str, dict[str, Any]] = {
    "PV = FV / (1 + r)^n": {
        "title_en": "Present value",
        "title_th": "มูลค่าปัจจุบัน",
        "meaning_en": "Discount a future value back to its equivalent value today.",
        "meaning_th": "คิดลดมูลค่าในอนาคตให้เป็นมูลค่าเทียบเท่า ณ วันนี้",
        "variables": [
            {"symbol": "PV", "meaning_en": "present value", "meaning_th": "มูลค่าปัจจุบัน"},
            {"symbol": "FV", "meaning_en": "future value", "meaning_th": "มูลค่าในอนาคต"},
            {"symbol": "r", "meaning_en": "discount rate per period", "meaning_th": "อัตราคิดลดต่อช่วงเวลา"},
            {"symbol": "n", "meaning_en": "number of periods", "meaning_th": "จำนวนช่วงเวลา"},
        ],
        "when_en": "Use when cash amounts occur at different times and must be compared at today’s value.",
        "when_th": "ใช้เมื่อกระแสเงินเกิดต่างเวลาและต้องเปรียบเทียบด้วยมูลค่า ณ วันนี้",
        "example_en": "Supplementary example: FV = 110, r = 10%, n = 1 gives PV = 100.",
        "example_th": "ตัวอย่างเสริม: FV = 110, r = 10%, n = 1 จะได้ PV = 100",
        "mistake_en": "Do not mix annual rates with monthly periods.",
        "mistake_th": "อย่าใช้อัตรารายปีกับจำนวนช่วงเวลาเป็นเดือนโดยไม่ปรับหน่วย",
    },
    "NPV = Σ(CF_t / (1 + r)^t) − C₀": {
        "title_en": "Net present value",
        "title_th": "มูลค่าปัจจุบันสุทธิ",
        "meaning_en": "Sum discounted cash flows and subtract the initial investment.",
        "meaning_th": "รวมกระแสเงินสดที่คิดลดแล้วและหักเงินลงทุนเริ่มต้น",
        "variables": [
            {"symbol": "CF_t", "meaning_en": "cash flow at time t", "meaning_th": "กระแสเงินสด ณ เวลา t"},
            {"symbol": "r", "meaning_en": "discount rate", "meaning_th": "อัตราคิดลด"},
            {"symbol": "t", "meaning_en": "time period", "meaning_th": "ช่วงเวลา"},
            {"symbol": "C₀", "meaning_en": "initial investment", "meaning_th": "เงินลงทุนเริ่มต้น"},
        ],
        "when_en": "Use to evaluate an investment from time-adjusted inflows and outflows.",
        "when_th": "ใช้ประเมินการลงทุนจากกระแสเงินรับและจ่ายที่ปรับมูลค่าตามเวลาแล้ว",
        "example_en": "Supplementary example: invest 100 now and receive 110 in one year at 10%; NPV = 0.",
        "example_th": "ตัวอย่างเสริม: ลงทุน 100 วันนี้ รับ 110 ในหนึ่งปี ที่อัตรา 10% จะได้ NPV = 0",
        "mistake_en": "Keep the initial outlay’s sign and timing consistent.",
        "mistake_th": "ต้องกำหนดเครื่องหมายและเวลาของเงินลงทุนเริ่มต้นให้สอดคล้อง",
    },
    "E(X) = Σx·P(x)": {
        "title_en": "Expected value",
        "title_th": "ค่าคาดหมาย",
        "meaning_en": "Weight each possible value by its probability.",
        "meaning_th": "ถ่วงน้ำหนักค่าที่เป็นไปได้แต่ละค่าด้วยความน่าจะเป็น",
        "variables": [
            {"symbol": "x", "meaning_en": "possible outcome", "meaning_th": "ผลลัพธ์ที่เป็นไปได้"},
            {"symbol": "P(x)", "meaning_en": "probability of x", "meaning_th": "ความน่าจะเป็นของ x"},
        ],
        "when_en": "Use to summarize the long-run center of a discrete uncertain outcome.",
        "when_th": "ใช้สรุปค่ากลางระยะยาวของผลลัพธ์ไม่แน่นอนแบบไม่ต่อเนื่อง",
        "example_en": "Supplementary example: outcomes 0 and 100 with probabilities 0.6 and 0.4 give E(X) = 40.",
        "example_th": "ตัวอย่างเสริม: ผลลัพธ์ 0 และ 100 มีความน่าจะเป็น 0.6 และ 0.4 จะได้ E(X) = 40",
        "mistake_en": "Probabilities must describe the complete distribution and total 1.",
        "mistake_th": "ความน่าจะเป็นต้องครอบคลุมการแจกแจงทั้งหมดและรวมกันเป็น 1",
    },
    "z = (x − μ) / σ": {
        "title_en": "Z-score",
        "title_th": "คะแนนมาตรฐาน z",
        "meaning_en": "Express how many standard deviations an observation is from the mean.",
        "meaning_th": "แสดงว่าค่าสังเกตอยู่ห่างจากค่าเฉลี่ยกี่ส่วนเบี่ยงเบนมาตรฐาน",
        "variables": [
            {"symbol": "x", "meaning_en": "observed value", "meaning_th": "ค่าที่สังเกต"},
            {"symbol": "μ", "meaning_en": "population mean", "meaning_th": "ค่าเฉลี่ยประชากร"},
            {"symbol": "σ", "meaning_en": "population standard deviation", "meaning_th": "ส่วนเบี่ยงเบนมาตรฐานประชากร"},
        ],
        "when_en": "Use to standardize values or identify unusually distant observations.",
        "when_th": "ใช้แปลงค่าเป็นมาตรฐานหรือระบุค่าที่ห่างจากค่าเฉลี่ยผิดปกติ",
        "example_en": "Supplementary example: x = 70, μ = 50, σ = 10 gives z = 2.",
        "example_th": "ตัวอย่างเสริม: x = 70, μ = 50, σ = 10 จะได้ z = 2",
        "mistake_en": "A negative z-score means below the mean, not an invalid value.",
        "mistake_th": "ค่า z ติดลบหมายถึงต่ำกว่าค่าเฉลี่ย ไม่ได้หมายถึงค่าผิดพลาด",
    },
    "Accuracy = (TP + TN) / (TP + TN + FP + FN)": {
        "title_en": "Accuracy",
        "title_th": "ความถูกต้องโดยรวม",
        "meaning_en": "Measure the share of all predictions classified correctly.",
        "meaning_th": "วัดสัดส่วนการพยากรณ์ทั้งหมดที่จำแนกได้ถูกต้อง",
        "variables": [
            {"symbol": "TP/TN", "meaning_en": "correct positive/negative predictions", "meaning_th": "การพยากรณ์บวก/ลบที่ถูกต้อง"},
            {"symbol": "FP/FN", "meaning_en": "incorrect positive/negative predictions", "meaning_th": "การพยากรณ์บวก/ลบที่ผิด"},
        ],
        "when_en": "Use when both classes matter and class imbalance is not hiding errors.",
        "when_th": "ใช้เมื่อทั้งสองคลาสสำคัญและความไม่สมดุลของคลาสไม่บดบังข้อผิดพลาด",
        "example_en": "Supplementary example: TP=40, TN=50, FP=5, FN=5 gives accuracy 90%.",
        "example_th": "ตัวอย่างเสริม: TP=40, TN=50, FP=5, FN=5 จะได้ Accuracy 90%",
        "mistake_en": "High accuracy can mislead when one class dominates.",
        "mistake_th": "Accuracy สูงอาจทำให้เข้าใจผิดเมื่อคลาสหนึ่งมีจำนวนมากกว่ามาก",
    },
    "Precision = TP / (TP + FP)": {
        "title_en": "Precision",
        "title_th": "ความแม่นยำของผลบวก",
        "meaning_en": "Measure how many predicted positives are truly positive.",
        "meaning_th": "วัดว่าสิ่งที่พยากรณ์ว่าเป็นบวกนั้นเป็นบวกจริงกี่ส่วน",
        "variables": [
            {"symbol": "TP", "meaning_en": "true positives", "meaning_th": "ผลบวกจริง"},
            {"symbol": "FP", "meaning_en": "false positives", "meaning_th": "ผลบวกลวง"},
        ],
        "when_en": "Use when false-positive decisions are costly.",
        "when_th": "ใช้เมื่อการตัดสินใจที่เป็นผลบวกลวงมีต้นทุนสูง",
        "example_en": "Supplementary example: TP=40 and FP=5 gives precision 88.9%.",
        "example_th": "ตัวอย่างเสริม: TP=40 และ FP=5 จะได้ Precision 88.9%",
        "mistake_en": "Precision does not measure missed positives.",
        "mistake_th": "Precision ไม่ได้วัดกรณีบวกที่แบบจำลองพลาด",
    },
    "Recall = TP / (TP + FN)": {
        "title_en": "Recall",
        "title_th": "ความครอบคลุมผลบวก",
        "meaning_en": "Measure how many actual positives are detected.",
        "meaning_th": "วัดว่าสามารถตรวจพบกรณีบวกจริงได้กี่ส่วน",
        "variables": [
            {"symbol": "TP", "meaning_en": "true positives", "meaning_th": "ผลบวกจริง"},
            {"symbol": "FN", "meaning_en": "false negatives", "meaning_th": "ผลลบลวง"},
        ],
        "when_en": "Use when missing a positive case is costly.",
        "when_th": "ใช้เมื่อการพลาดกรณีบวกมีต้นทุนสูง",
        "example_en": "Supplementary example: TP=40 and FN=5 gives recall 88.9%.",
        "example_th": "ตัวอย่างเสริม: TP=40 และ FN=5 จะได้ Recall 88.9%",
        "mistake_en": "Recall alone does not reveal false-positive volume.",
        "mistake_th": "Recall เพียงค่าเดียวไม่แสดงจำนวนผลบวกลวง",
    },
    "ŷ = β₀ + β₁x₁ + … + βₚxₚ": {
        "title_en": "Regression prediction",
        "title_th": "ค่าพยากรณ์จากการถดถอย",
        "meaning_en": "Combine an intercept and weighted explanatory variables to predict a numeric outcome.",
        "meaning_th": "รวมค่าคงที่และตัวแปรอธิบายที่ถ่วงด้วยสัมประสิทธิ์เพื่อพยากรณ์ค่าตัวเลข",
        "variables": [
            {"symbol": "ŷ", "meaning_en": "predicted outcome", "meaning_th": "ค่าผลลัพธ์ที่พยากรณ์"},
            {"symbol": "β₀", "meaning_en": "intercept", "meaning_th": "ค่าคงที่"},
            {"symbol": "β₁…βₚ", "meaning_en": "coefficients", "meaning_th": "สัมประสิทธิ์"},
            {"symbol": "x₁…xₚ", "meaning_en": "explanatory variables", "meaning_th": "ตัวแปรอธิบาย"},
        ],
        "when_en": "Use when estimating a continuous dependent variable from explanatory variables.",
        "when_th": "ใช้ประมาณตัวแปรตามแบบต่อเนื่องจากตัวแปรอธิบาย",
        "example_en": "Supplementary example: β₀=10, β₁=2, x=5 gives ŷ=20.",
        "example_th": "ตัวอย่างเสริม: β₀=10, β₁=2, x=5 จะได้ ŷ=20",
        "mistake_en": "A coefficient’s interpretation depends on holding the other variables constant.",
        "mistake_th": "การตีความสัมประสิทธิ์ต้องถือว่าตัวแปรอื่นคงที่",
    },
    "residual = y − ŷ": {
        "title_en": "Residual",
        "title_th": "ค่าคลาดเคลื่อนคงเหลือ",
        "meaning_en": "Measure the observed outcome minus its prediction.",
        "meaning_th": "วัดผลลัพธ์จริงลบด้วยค่าที่พยากรณ์",
        "variables": [
            {"symbol": "y", "meaning_en": "observed outcome", "meaning_th": "ผลลัพธ์จริง"},
            {"symbol": "ŷ", "meaning_en": "predicted outcome", "meaning_th": "ผลลัพธ์ที่พยากรณ์"},
        ],
        "when_en": "Use to diagnose prediction error and regression assumptions.",
        "when_th": "ใช้วิเคราะห์ข้อผิดพลาดการพยากรณ์และสมมติฐานของการถดถอย",
        "example_en": "Supplementary example: y=23 and ŷ=20 gives residual=3.",
        "example_th": "ตัวอย่างเสริม: y=23 และ ŷ=20 จะได้ Residual=3",
        "mistake_en": "Do not reverse the subtraction when interpreting the sign.",
        "mistake_th": "อย่าสลับลำดับการลบเมื่อตีความเครื่องหมายของค่า",
    },
    "support(A→B) = P(A∩B)": {
        "title_en": "Support",
        "title_th": "ค่าสนับสนุน",
        "meaning_en": "Measure how frequently A and B occur together.",
        "meaning_th": "วัดความถี่ที่ A และ B เกิดร่วมกัน",
        "variables": [
            {"symbol": "P(A∩B)", "meaning_en": "joint probability of A and B", "meaning_th": "ความน่าจะเป็นร่วมของ A และ B"}
        ],
        "when_en": "Use to screen association rules by prevalence.",
        "when_th": "ใช้คัดกรองกฎความสัมพันธ์ตามความถี่ที่พบ",
        "example_en": "Supplementary example: if 20% of baskets contain A and B, support is 0.20.",
        "example_th": "ตัวอย่างเสริม: หาก 20% ของตะกร้ามี A และ B ร่วมกัน Support เท่ากับ 0.20",
        "mistake_en": "A strong implication can still have low support.",
        "mistake_th": "กฎที่มีความสัมพันธ์สูงอาจมี Support ต่ำได้",
    },
    "confidence(A→B) = P(B|A)": {
        "title_en": "Confidence",
        "title_th": "ค่าความเชื่อมั่นของกฎ",
        "meaning_en": "Measure the conditional chance of B among cases containing A.",
        "meaning_th": "วัดโอกาสแบบมีเงื่อนไขที่จะพบ B ในกรณีที่มี A",
        "variables": [
            {"symbol": "P(B|A)", "meaning_en": "probability of B given A", "meaning_th": "ความน่าจะเป็นของ B เมื่อกำหนดให้มี A"}
        ],
        "when_en": "Use to assess the directional reliability of an association rule.",
        "when_th": "ใช้ประเมินความน่าเชื่อถือเชิงทิศทางของกฎความสัมพันธ์",
        "example_en": "Supplementary example: P(A∩B)=0.20 and P(A)=0.40 gives confidence 0.50.",
        "example_th": "ตัวอย่างเสริม: P(A∩B)=0.20 และ P(A)=0.40 จะได้ Confidence 0.50",
        "mistake_en": "Confidence A→B is not generally equal to confidence B→A.",
        "mistake_th": "Confidence ของ A→B โดยทั่วไปไม่เท่ากับ Confidence ของ B→A",
    },
    "lift(A→B) = P(B|A) / P(B)": {
        "title_en": "Lift",
        "title_th": "ค่าลิฟต์",
        "meaning_en": "Compare rule confidence with B’s baseline probability.",
        "meaning_th": "เปรียบเทียบ Confidence ของกฎกับความน่าจะเป็นพื้นฐานของ B",
        "variables": [
            {"symbol": "P(B|A)", "meaning_en": "conditional probability of B", "meaning_th": "ความน่าจะเป็นแบบมีเงื่อนไขของ B"},
            {"symbol": "P(B)", "meaning_en": "baseline probability of B", "meaning_th": "ความน่าจะเป็นพื้นฐานของ B"},
        ],
        "when_en": "Use to see whether co-occurrence exceeds what B’s popularity alone suggests.",
        "when_th": "ใช้ดูว่าการเกิดร่วมสูงกว่าที่ความนิยมพื้นฐานของ B อธิบายหรือไม่",
        "example_en": "Supplementary example: confidence=0.50 and P(B)=0.25 gives lift=2.",
        "example_th": "ตัวอย่างเสริม: Confidence=0.50 และ P(B)=0.25 จะได้ Lift=2",
        "mistake_en": "Lift near 1 indicates little association beyond the baseline.",
        "mistake_th": "Lift ใกล้ 1 หมายถึงแทบไม่มีความสัมพันธ์เกินกว่าค่าพื้นฐาน",
    },
}

TOPIC_FORMULAS = {
    "topic-bis602-investment-decisions-01": [
        "PV = FV / (1 + r)^n",
        "NPV = Σ(CF_t / (1 + r)^t) − C₀",
    ],
    "topic-bis602-investment-decisions-02": ["PV = FV / (1 + r)^n"],
    "topic-bis602-investment-decisions-03": ["NPV = Σ(CF_t / (1 + r)^t) − C₀"],
    "topic-bis602-probability-and-statistics-01": ["E(X) = Σx·P(x)"],
    "topic-bis602-probability-and-statistics-02": ["z = (x − μ) / σ"],
    "topic-bis602-probability-and-statistics-03": ["z = (x − μ) / σ"],
    "topic-bis602-classification-02": [
        "Accuracy = (TP + TN) / (TP + TN + FP + FN)",
        "Precision = TP / (TP + FP)",
        "Recall = TP / (TP + FN)",
    ],
    "topic-bis602-classification-03": [
        "Accuracy = (TP + TN) / (TP + TN + FP + FN)",
        "Precision = TP / (TP + FP)",
        "Recall = TP / (TP + FN)",
    ],
    "topic-bis602-regression-01": ["ŷ = β₀ + β₁x₁ + … + βₚxₚ"],
    "topic-bis602-regression-02": ["ŷ = β₀ + β₁x₁ + … + βₚxₚ"],
    "topic-bis602-regression-03": ["residual = y − ŷ"],
    "topic-bis602-association-and-simulation-01": ["support(A→B) = P(A∩B)"],
    "topic-bis602-association-and-simulation-02": [
        "confidence(A→B) = P(B|A)",
        "lift(A→B) = P(B|A) / P(B)",
    ],
}

SPECIAL_COMPARISONS: dict[str, dict[str, Any]] = {
    "topic-bis601-analyst-and-system-success-02": {
        "title_en": "Business Analyst vs Systems Analyst",
        "title_th": "นักวิเคราะห์ธุรกิจ เทียบกับ นักวิเคราะห์ระบบ",
        "columns_en": ["Business Analyst", "Systems Analyst"],
        "columns_th": ["นักวิเคราะห์ธุรกิจ", "นักวิเคราะห์ระบบ"],
        "comparison_target_en": "Business Analyst",
        "comparison_target_th": "นักวิเคราะห์ธุรกิจ",
        "rows": [
            {
                "aspect_en": "Primary question",
                "aspect_th": "คำถามหลัก",
                "left_en": "What must the business do to solve the problem?",
                "left_th": "ธุรกิจต้องทำอะไรเพื่อแก้ปัญหา",
                "right_en": "How should the solution be implemented using technology?",
                "right_th": "ควรนำแนวทางแก้ไขไปใช้ด้วยเทคโนโลยีอย่างไร",
            },
            {
                "aspect_en": "Focus",
                "aspect_th": "จุดเน้น",
                "left_en": "Business need, value, stakeholder change, and required outcome.",
                "left_th": "ความต้องการและคุณค่าทางธุรกิจ การเปลี่ยนแปลงของผู้มีส่วนได้ส่วนเสีย และผลลัพธ์ที่ต้องการ",
                "right_en": "Feasible system design, technical implementation, and solution operation.",
                "right_th": "การออกแบบระบบที่เป็นไปได้ การนำเทคนิคไปใช้ และการทำงานของโซลูชัน",
            },
        ],
        "source_reference_ids": ["ref-df3d0f3ce677"],
        "source_question_ids": ["question-comprehensive-019"],
    },
    "topic-bis601-development-methods-02": {
        "title_en": "Predictive Method vs Adaptive Method",
        "title_th": "วิธีเชิงคาดการณ์ เทียบกับ วิธีเชิงปรับตัว",
        "columns_en": ["Predictive Method", "Adaptive Method"],
        "columns_th": ["วิธีเชิงคาดการณ์", "วิธีเชิงปรับตัว"],
        "rows": [
            {
                "aspect_en": "Planning",
                "aspect_th": "การวางแผน",
                "left_en": "Plan-driven work fits comparatively stable scope.",
                "left_th": "ขับเคลื่อนด้วยแผนและเหมาะกับขอบเขตที่ค่อนข้างคงที่",
                "right_en": "Iterative work revises scope and solution through feedback.",
                "right_th": "ทำงานเป็นรอบและปรับขอบเขตกับโซลูชันจากข้อเสนอแนะ",
            },
            {
                "aspect_en": "Change handling",
                "aspect_th": "การรองรับการเปลี่ยนแปลง",
                "left_en": "Change is assessed against an established plan.",
                "left_th": "ประเมินการเปลี่ยนแปลงเทียบกับแผนที่กำหนดไว้",
                "right_en": "Change is expected and incorporated between iterations.",
                "right_th": "คาดหมายการเปลี่ยนแปลงและนำมาปรับในแต่ละรอบ",
            },
        ],
        "source_reference_ids": ["ref-cc0c959ac842"],
    },
    "topic-bis602-bi-and-visualization-01": {
        "title_en": "Descriptive Analytics vs Predictive Analytics",
        "title_th": "การวิเคราะห์เชิงพรรณนา เทียบกับ การวิเคราะห์เชิงพยากรณ์",
        "columns_en": ["Descriptive Analytics", "Predictive Analytics"],
        "columns_th": ["การวิเคราะห์เชิงพรรณนา", "การวิเคราะห์เชิงพยากรณ์"],
        "rows": [
            {
                "aspect_en": "Question answered",
                "aspect_th": "คำถามที่ตอบ",
                "left_en": "What happened or what is happening?",
                "left_th": "เกิดอะไรขึ้นหรือกำลังเกิดอะไรขึ้น",
                "right_en": "What is likely to happen?",
                "right_th": "มีแนวโน้มว่าจะเกิดอะไรขึ้น",
            },
            {
                "aspect_en": "Typical use",
                "aspect_th": "การใช้งานทั่วไป",
                "left_en": "Reporting and dashboards summarize observed data.",
                "left_th": "รายงานและแดชบอร์ดสรุปข้อมูลที่สังเกตได้",
                "right_en": "Models estimate future outcomes from patterns in data.",
                "right_th": "แบบจำลองประมาณผลลัพธ์ในอนาคตจากรูปแบบในข้อมูล",
            },
        ],
        "source_reference_ids": ["ref-39852560330e", "ref-b8fc1abdab20"],
    },
    "topic-bis604-relational-model-01": {
        "title_en": "Primary Key vs Foreign Key",
        "title_th": "คีย์หลัก เทียบกับ คีย์นอก",
        "columns_en": ["Primary Key", "Foreign Key"],
        "columns_th": ["คีย์หลัก", "คีย์นอก"],
        "rows": [
            {
                "aspect_en": "Purpose",
                "aspect_th": "วัตถุประสงค์",
                "left_en": "Uniquely identifies each row in its own relation.",
                "left_th": "ระบุแต่ละแถวในรีเลชันของตนเองไม่ให้ซ้ำ",
                "right_en": "References a candidate or primary key in another or the same relation.",
                "right_th": "อ้างถึงคีย์ผู้สมัครหรือคีย์หลักในรีเลชันอื่นหรือรีเลชันเดียวกัน",
            },
            {
                "aspect_en": "Integrity role",
                "aspect_th": "บทบาทด้านบูรณภาพ",
                "left_en": "Supports entity integrity.",
                "left_th": "สนับสนุนบูรณภาพของเอนทิตี",
                "right_en": "Supports referential integrity between related rows.",
                "right_th": "สนับสนุนบูรณภาพการอ้างอิงระหว่างแถวที่สัมพันธ์กัน",
            },
        ],
        "source_reference_ids": ["ref-1f0a58974a9f"],
    },
    "topic-bis604-sql-and-implementation-03": {
        "title_en": "UNION vs UNION ALL",
        "title_th": "UNION เทียบกับ UNION ALL",
        "columns_en": ["UNION", "UNION ALL"],
        "columns_th": ["UNION", "UNION ALL"],
        "rows": [
            {
                "aspect_en": "Duplicate rows",
                "aspect_th": "แถวซ้ำ",
                "left_en": "Combines query results without retaining duplicate rows.",
                "left_th": "รวมผลลัพธ์ของคำสั่งค้นโดยไม่เก็บแถวซ้ำ",
                "right_en": "Combines query results and retains duplicate rows.",
                "right_th": "รวมผลลัพธ์ของคำสั่งค้นและเก็บแถวซ้ำไว้",
            },
            {
                "aspect_en": "Use",
                "aspect_th": "การใช้",
                "left_en": "Use when the result must represent a set of distinct rows.",
                "left_th": "ใช้เมื่อต้องการผลลัพธ์เป็นชุดแถวที่ไม่ซ้ำ",
                "right_en": "Use when every occurrence must remain in the result.",
                "right_th": "ใช้เมื่อต้องคงทุกการปรากฏของแถวไว้ในผลลัพธ์",
            },
        ],
        "source_reference_ids": ["ref-0361f1ec60b4"],
        "source_question_ids": ["question-comprehensive-080"],
    },
}


def formula_record(expression: str, source_ids: list[str]) -> dict[str, Any]:
    return labelled(
        COURSE_LABEL,
        formula=expression,
        source_reference_ids=source_ids,
        evidence_type="summarized_from_source",
        worked_example_category="supplementary_explanation",
        **FORMULA_DETAILS[expression],
    )


def enrich_subject(
    subject: dict[str, Any],
    references: list[dict[str, Any]],
    chapters: list[dict[str, Any]],
) -> dict[str, Any]:
    source_ids = {
        reference["source_reference_id"]
        for reference in references
        if reference["file_id"] in subject["source_file_ids"]
    }
    ordered_chapters = [
        chapter for chapter in chapters if chapter["subject_id"] == subject["subject_id"]
    ]
    subject["source_reference_ids"] = sorted(source_ids)
    subject["lesson_sections"] = [
        labelled(
            COURSE_LABEL,
            section_id=f"{subject['subject_id']}-overview",
            heading_en="Course overview",
            heading_th="ภาพรวมรายวิชา",
            content_en=[subject["overview_en"]],
            content_th=[subject["overview_th"]],
            content_format="paragraph",
            evidence_type="summarized_from_source",
            source_reference_ids=sorted(source_ids),
        ),
        labelled(
            COURSE_LABEL,
            section_id=f"{subject['subject_id']}-learning-path",
            heading_en="How the chapters connect",
            heading_th="ความเชื่อมโยงของบทเรียน",
            content_en=[
                subject["topic_relationships_en"],
                *[chapter["concise_summary_en"] for chapter in ordered_chapters],
            ],
            content_th=[
                subject["topic_relationships_th"],
                *[chapter["concise_summary_th"] for chapter in ordered_chapters],
            ],
            content_format="bullet_list",
            evidence_type="summarized_from_source",
            source_reference_ids=sorted(source_ids),
        ),
    ]
    subject["quick_review"] = {
        "key_points_en": subject["major_themes"][:7],
        "key_points_th": [chapter["title_th"] for chapter in ordered_chapters[:7]],
        "memory_aid_en": "Move from foundation → method → application → evidence.",
        "memory_aid_th": "ทบทวนจาก พื้นฐาน → วิธีการ → การประยุกต์ → หลักฐาน",
    }
    subject["content_status"] = "enriched"
    subject["content_updated_at"] = GENERATED_AT
    return subject


def enrich_chapter(
    chapter: dict[str, Any],
    chapter_topics: list[dict[str, Any]],
    question_ids: list[str],
    wording_signals: list[str],
) -> dict[str, Any]:
    titles_en = [topic["title_en"] for topic in chapter_topics]
    titles_th = [topic["title_th"] for topic in chapter_topics]
    source_ids = chapter["source_reference_ids"]
    chapter["learning_objectives_en"] = [
        f"Explain the core purpose of {chapter['title_en']}.",
        f"Distinguish the chapter concepts: {', '.join(titles_en)}.",
        "Apply the cited concepts while stating assumptions and limitations.",
    ]
    chapter["learning_objectives_th"] = [
        f"อธิบายวัตถุประสงค์หลักของ {chapter['title_th']}",
        f"แยกความแตกต่างระหว่างแนวคิดสำคัญ ได้แก่ {', '.join(titles_th)}",
        "ประยุกต์แนวคิดที่มีแหล่งอ้างอิง พร้อมระบุสมมติฐานและข้อจำกัด",
    ]
    chapter["overview_en"] = chapter["concise_summary_en"]
    chapter["overview_th"] = chapter["concise_summary_th"]
    chapter["lesson_sections"] = [
        labelled(
            COURSE_LABEL,
            section_id=f"{chapter['chapter_id']}-foundation",
            heading_en="Chapter foundation",
            heading_th="พื้นฐานของบท",
            content_en=[chapter["concise_summary_en"]],
            content_th=[chapter["concise_summary_th"]],
            content_format="paragraph",
            evidence_type=chapter["evidence_type"],
            source_reference_ids=source_ids,
        ),
        labelled(
            SUPPLEMENTARY_LABEL,
            section_id=f"{chapter['chapter_id']}-study-method",
            heading_en="How to study this chapter",
            heading_th="แนวทางศึกษาเนื้อหาในบท",
            content_en=[
                "Start with the cited definitions and identify the decision purpose.",
                f"Compare {', '.join(titles_en)} rather than memorizing isolated labels.",
                "Apply the concept to the supplied case or question, then state the evidence and limitation.",
            ],
            content_th=[
                "เริ่มจากนิยามที่มีแหล่งอ้างอิงและระบุวัตถุประสงค์ของการตัดสินใจ",
                f"เปรียบเทียบ {', '.join(titles_th)} แทนการจำคำศัพท์แยกส่วน",
                "ประยุกต์แนวคิดกับกรณีหรือโจทย์ที่ให้มา แล้วระบุหลักฐานและข้อจำกัด",
            ],
            content_format="numbered_steps",
            evidence_type="supplementary",
            source_reference_ids=source_ids,
        ),
    ]
    chapter["formula_details"] = [
        formula_record(expression, source_ids)
        for expression in chapter["formulas"]
        if expression in FORMULA_DETAILS
    ]
    chapter["exam_focus"] = {
        "supported_question_ids": question_ids,
        "wording_signals": wording_signals,
        "note_en": (
            "The supplied examination maps directly to this chapter; use the listed "
            "question IDs as evidence of tested distinctions."
            if question_ids
            else "No supplied examination question is directly mapped to this chapter; this is not a frequency prediction."
        ),
        "note_th": (
            "ข้อสอบที่ให้มามีข้อที่เชื่อมโยงกับบทนี้โดยตรง ให้ใช้รหัสข้อที่ระบุเป็นหลักฐานของประเด็นที่ทดสอบ"
            if question_ids
            else "ยังไม่มีข้อสอบที่ให้มาซึ่งเชื่อมโยงกับบทนี้โดยตรง ข้อความนี้ไม่ใช่การคาดการณ์ความถี่ออกสอบ"
        ),
    }
    chapter["quick_review"] = {
        "key_points_en": chapter["review_points"][:7],
        "key_points_th": [
            chapter["concise_summary_th"],
            *[topic["summary_th"] for topic in chapter_topics],
        ][:7],
        "memory_aid_en": chapter["memory_aid"],
        "memory_aid_th": "วัตถุประสงค์ → หลักฐาน → วิธีการ → ผลลัพธ์ → ข้อจำกัด",
    }
    chapter["content_status"] = "enriched"
    chapter["content_updated_at"] = GENERATED_AT
    return chapter


def enrich_topic(
    topic: dict[str, Any],
    chapter: dict[str, Any],
    glossary_entry: dict[str, Any],
    comparison_entry: dict[str, Any],
    question_ids: list[str],
    wording_signals: list[str],
) -> dict[str, Any]:
    source_ids = topic["source_reference_ids"]
    title_en = topic["title_en"]
    title_th = topic["title_th"]
    special_comparison = SPECIAL_COMPARISONS.get(topic["topic_id"])
    comparison_title_en = (
        special_comparison.get(
            "comparison_target_en", special_comparison["columns_en"][1]
        )
        if special_comparison
        else comparison_entry["term_en"]
    )
    comparison_title_th = (
        special_comparison.get(
            "comparison_target_th", special_comparison["columns_th"][1]
        )
        if special_comparison
        else comparison_entry["term_th"]
    )
    topic["learning_objectives_en"] = [
        f"Explain {title_en} using the cited course definition.",
        f"Distinguish {title_en} from {comparison_title_en}.",
        f"Apply {title_en} within {chapter['title_en']} and state the supporting evidence.",
    ]
    topic["learning_objectives_th"] = [
        f"อธิบาย {title_th} โดยใช้นิยามจากเอกสารอ้างอิง",
        f"แยกความแตกต่างระหว่าง {title_th} กับ {comparison_title_th}",
        f"ประยุกต์ {title_th} ในเรื่อง {chapter['title_th']} พร้อมระบุหลักฐานสนับสนุน",
    ]
    topic["overview_en"] = topic["summary_en"]
    topic["overview_th"] = topic["summary_th"]
    topic["lesson_sections"] = [
        labelled(
            COURSE_LABEL,
            section_id=f"{topic['topic_id']}-core",
            heading_en="Core concept",
            heading_th="แนวคิดหลัก",
            content_en=[glossary_entry["definition_en"]],
            content_th=[glossary_entry["explanation_th"]],
            content_format="paragraph",
            evidence_type=topic["evidence_type"],
            source_reference_ids=source_ids,
        ),
        labelled(
            COURSE_LABEL,
            section_id=f"{topic['topic_id']}-relationship",
            heading_en="Relationship within the chapter",
            heading_th="ความสัมพันธ์ภายในบท",
            content_en=[topic["summary_en"], chapter["concise_summary_en"]],
            content_th=[topic["summary_th"], chapter["concise_summary_th"]],
            content_format="paragraph",
            evidence_type=topic["evidence_type"],
            source_reference_ids=source_ids,
        ),
        labelled(
            SUPPLEMENTARY_LABEL,
            section_id=f"{topic['topic_id']}-reasoning",
            heading_en="Step-by-step reasoning guide",
            heading_th="แนวทางคิดทีละขั้น",
            content_en=[
                "Identify the decision, problem, or relationship being asked about.",
                f"Match the case evidence to the cited definition of {title_en}.",
                f"Compare it with {comparison_title_en}; do not decide from a keyword alone.",
                "State the conclusion, source evidence, assumption, and limitation.",
            ],
            content_th=[
                "ระบุการตัดสินใจ ปัญหา หรือความสัมพันธ์ที่โจทย์ถาม",
                f"จับคู่หลักฐานในกรณีกับนิยามของ {title_th} ที่มีแหล่งอ้างอิง",
                f"เปรียบเทียบกับ {comparison_title_th} และอย่าตัดสินจากคำสำคัญเพียงคำเดียว",
                "สรุปผล พร้อมระบุแหล่งหลักฐาน สมมติฐาน และข้อจำกัด",
            ],
            content_format="numbered_steps",
            evidence_type="supplementary",
            source_reference_ids=source_ids,
        ),
    ]
    topic["key_terms"] = [
        labelled(
            COURSE_LABEL,
            glossary_id=glossary_entry["glossary_id"],
            term_en=glossary_entry["term_en"],
            term_th=glossary_entry["term_th"],
            definition_en=glossary_entry["definition_en"],
            explanation_th=glossary_entry["explanation_th"],
            evidence_type=glossary_entry["evidence_type"],
            confidence=glossary_entry["confidence"],
            source_reference_ids=glossary_entry["source_reference_ids"],
        )
    ]
    if special_comparison:
        topic["comparisons"] = [
            labelled(
                COURSE_LABEL,
                comparison_id=f"{topic['topic_id']}-comparison",
                title_en=special_comparison["title_en"],
                title_th=special_comparison["title_th"],
                columns_en=special_comparison["columns_en"],
                columns_th=special_comparison["columns_th"],
                rows=special_comparison["rows"],
                evidence_type="summarized_from_source",
                source_reference_ids=special_comparison["source_reference_ids"],
                source_question_ids=special_comparison.get(
                    "source_question_ids", []
                ),
            )
        ]
    else:
        topic["comparisons"] = [
            labelled(
                COURSE_LABEL,
                comparison_id=f"{topic['topic_id']}-comparison",
                title_en=f"{title_en} vs {comparison_title_en}",
                title_th=f"{title_th} เทียบกับ {comparison_title_th}",
                columns_en=[title_en, comparison_title_en],
                columns_th=[title_th, comparison_title_th],
                rows=[
                    {
                        "aspect_en": "Course definition",
                        "aspect_th": "นิยามจากเอกสาร",
                        "left_en": glossary_entry["definition_en"],
                        "left_th": glossary_entry["explanation_th"],
                        "right_en": comparison_entry["definition_en"],
                        "right_th": comparison_entry["explanation_th"],
                    }
                ],
                evidence_type="summarized_from_source",
                source_reference_ids=sorted(
                    set(source_ids + comparison_entry["source_reference_ids"])
                ),
                source_question_ids=[],
            )
        ]
    topic["process_steps"] = [
        labelled(
            SUPPLEMENTARY_LABEL,
            step=1,
            title_en="Frame the question",
            title_th="กำหนดกรอบคำถาม",
            description_en=f"Identify why {title_en} is relevant to the case.",
            description_th=f"ระบุว่าเหตุใด {title_th} จึงเกี่ยวข้องกับกรณี",
        ),
        labelled(
            SUPPLEMENTARY_LABEL,
            step=2,
            title_en="Locate evidence",
            title_th="ค้นหาหลักฐาน",
            description_en="Use the cited definition, inputs, conditions, or relationships.",
            description_th="ใช้นิยาม ข้อมูลนำเข้า เงื่อนไข หรือความสัมพันธ์จากแหล่งอ้างอิง",
        ),
        labelled(
            SUPPLEMENTARY_LABEL,
            step=3,
            title_en="Apply and check",
            title_th="ประยุกต์และตรวจสอบ",
            description_en="Apply the concept and test whether a related concept fits better.",
            description_th="ประยุกต์แนวคิดและตรวจว่าแนวคิดที่เกี่ยวข้องเหมาะสมกว่าหรือไม่",
        ),
        labelled(
            SUPPLEMENTARY_LABEL,
            step=4,
            title_en="Interpret",
            title_th="ตีความ",
            description_en="Explain the result, assumption, limitation, and next action.",
            description_th="อธิบายผลลัพธ์ สมมติฐาน ข้อจำกัด และการดำเนินการถัดไป",
        ),
    ]
    topic["formulas"] = [
        formula_record(expression, source_ids)
        for expression in TOPIC_FORMULAS.get(topic["topic_id"], [])
    ]
    topic["examples"] = [
        labelled(
            SUPPLEMENTARY_LABEL,
            example_id=f"{topic['topic_id']}-example",
            title_en="Guided application",
            title_th="ตัวอย่างการประยุกต์แบบมีแนวทาง",
            scenario_en=(
                f"In a short {chapter['title_en']} case, identify evidence that "
                f"matches this definition of {title_en}: {glossary_entry['definition_en']}"
            ),
            scenario_th=(
                f"ในกรณีสั้นเกี่ยวกับ {chapter['title_th']} ให้ระบุหลักฐานที่ตรงกับ"
                f"นิยามของ {title_th}: {glossary_entry['explanation_th']}"
            ),
            walkthrough_en=[
                "Underline the decision or relationship in the case.",
                f"Compare the evidence with {title_en} and {comparison_title_en}.",
                "Choose the better-supported concept and cite the matching evidence.",
            ],
            walkthrough_th=[
                "ขีดเส้นใต้การตัดสินใจหรือความสัมพันธ์ในกรณี",
                f"เปรียบเทียบหลักฐานกับ {title_th} และ {comparison_title_th}",
                "เลือกแนวคิดที่มีหลักฐานสนับสนุนดีกว่าและอ้างข้อความที่ตรงกัน",
            ],
        )
    ]
    topic["common_misunderstandings"] = [
        labelled(
            SUPPLEMENTARY_LABEL,
            misunderstanding_en=(
                f"Treating {title_en} and {comparison_title_en} as interchangeable "
                "without comparing their definitions."
            ),
            misunderstanding_th=(
                f"มองว่า {title_th} และ {comparison_title_th} ใช้แทนกันได้ "
                "โดยไม่เปรียบเทียบนิยาม"
            ),
            correction_en="Use the cited definition and the case’s decision purpose.",
            correction_th="ใช้นิยามที่มีแหล่งอ้างอิงและวัตถุประสงค์การตัดสินใจของกรณี",
        ),
        labelled(
            SUPPLEMENTARY_LABEL,
            misunderstanding_en="Selecting an answer from a familiar keyword alone.",
            misunderstanding_th="เลือกคำตอบจากคำสำคัญที่คุ้นเคยเพียงอย่างเดียว",
            correction_en="Check the full condition, relationship, exception word, and limitation.",
            correction_th="ตรวจเงื่อนไข ความสัมพันธ์ คำบอกข้อยกเว้น และข้อจำกัดให้ครบ",
        ),
    ]
    topic["exam_focus"] = {
        **COURSE_LABEL,
        "supported_question_ids": question_ids,
        "wording_signals": wording_signals,
        "points_en": (
            [
                f"Supplied examination examples map {title_en} to: {', '.join(question_ids)}.",
                "Read negative or comparative wording before evaluating the statements and selectable answers.",
            ]
            if question_ids
            else [
                "No supplied examination example is directly mapped to this topic.",
                "Study the definition and chapter relationship without treating this as a frequency prediction.",
            ]
        ),
        "points_th": (
            [
                f"ข้อสอบที่ให้มาเชื่อมโยง {title_th} กับข้อ: {', '.join(question_ids)}",
                "อ่านคำปฏิเสธหรือคำเปรียบเทียบให้ครบก่อนประเมินข้อความและตัวเลือกคำตอบ",
            ]
            if question_ids
            else [
                "ยังไม่มีตัวอย่างข้อสอบที่ให้มาซึ่งเชื่อมโยงกับหัวข้อนี้โดยตรง",
                "ศึกษานิยามและความสัมพันธ์ในบท โดยไม่ถือเป็นการคาดการณ์ความถี่ออกสอบ",
            ]
        ),
    }
    topic["quick_review"] = {
        "key_points_en": [
            glossary_entry["definition_en"],
            f"Within {chapter['title_en']}: {chapter['concise_summary_en']}",
            f"Distinguish it from {comparison_title_en} with source evidence.",
        ],
        "key_points_th": [
            glossary_entry["explanation_th"],
            f"ภายในเรื่อง {chapter['title_th']}: {chapter['concise_summary_th']}",
            f"แยกจาก {comparison_title_th} โดยใช้หลักฐานจากแหล่งอ้างอิง",
        ],
        "memory_aid_en": f"{title_en}: definition → evidence → comparison → decision.",
        "memory_aid_th": f"{title_th}: นิยาม → หลักฐาน → เปรียบเทียบ → ตัดสินใจ",
        "related_glossary_ids": [
            glossary_entry["glossary_id"],
            comparison_entry["glossary_id"],
        ],
    }
    topic["human_review_note"] = (
        None
        if topic["confidence"] == "high"
        else "Retain the existing confidence warning and verify against the cited source before high-stakes use."
    )
    topic["content_status"] = "enriched"
    topic["content_updated_at"] = GENERATED_AT
    return topic


def main() -> int:
    subjects_payload = read_json("subjects.json")
    chapters_payload = read_json("chapters.json")
    topics_payload = read_json("topics.json")
    glossary_payload = read_json("glossary.json")
    references = read_json("source-references.json")["source_references"]
    questions = read_json("questions.json")["questions"]

    subjects = subjects_payload["subjects"]
    chapters = chapters_payload["chapters"]
    topics = topics_payload["topics"]
    glossary = glossary_payload["glossary"]
    chapter_by_id = {chapter["chapter_id"]: chapter for chapter in chapters}
    glossary_by_topic = {
        (entry["chapter_id"], entry["term_en"].casefold()): entry
        for entry in glossary
    }
    questions_by_topic: dict[str, list[dict[str, Any]]] = {}
    questions_by_chapter: dict[str, list[dict[str, Any]]] = {}
    for question in questions:
        questions_by_chapter.setdefault(question["chapter_id"], []).append(question)
        for topic_id in question["topic_ids"]:
            questions_by_topic.setdefault(topic_id, []).append(question)

    for subject in subjects:
        enrich_subject(subject, references, chapters)

    for chapter in chapters:
        chapter_topics = sorted(
            [topic for topic in topics if topic["chapter_id"] == chapter["chapter_id"]],
            key=lambda topic: topic["order"],
        )
        mapped = questions_by_chapter.get(chapter["chapter_id"], [])
        enrich_chapter(
            chapter,
            chapter_topics,
            [question["question_id"] for question in mapped],
            sorted({signal for question in mapped for signal in question_wording(question)}),
        )

    for chapter_id, chapter_topics in {
        chapter["chapter_id"]: sorted(
            [topic for topic in topics if topic["chapter_id"] == chapter["chapter_id"]],
            key=lambda topic: topic["order"],
        )
        for chapter in chapters
    }.items():
        for index, topic in enumerate(chapter_topics):
            glossary_entry = glossary_by_topic[(chapter_id, topic["title_en"].casefold())]
            comparison_topic = chapter_topics[(index + 1) % len(chapter_topics)]
            comparison_entry = glossary_by_topic[
                (chapter_id, comparison_topic["title_en"].casefold())
            ]
            mapped = questions_by_topic.get(topic["topic_id"], [])
            enrich_topic(
                topic,
                chapter_by_id[chapter_id],
                glossary_entry,
                comparison_entry,
                [question["question_id"] for question in mapped],
                sorted(
                    {
                        signal
                        for question in mapped
                        for signal in question_wording(question)
                    }
                ),
            )

    for payload in (subjects_payload, chapters_payload, topics_payload):
        payload["schema_version"] = "2.0.0"
        payload["generated_at"] = GENERATED_AT
    write_payload("subjects.json", subjects_payload)
    write_payload("chapters.json", chapters_payload)
    write_payload("topics.json", topics_payload)

    supplemental_sections = sum(
        section["source_category"] == "supplementary_explanation"
        for chapter in chapters
        for section in chapter["lesson_sections"]
    ) + sum(
        section["source_category"] == "supplementary_explanation"
        for topic in topics
        for section in topic["lesson_sections"]
    )
    print(
        "Study Library enrichment: "
        f"{len(subjects)} subjects, {len(chapters)} chapters, {len(topics)} topics, "
        f"{supplemental_sections} supplementary lesson sections."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
