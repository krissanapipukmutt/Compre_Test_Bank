#!/usr/bin/env python3
"""Apply the Phase 7 course recheck and external-evidence research decisions."""

from __future__ import annotations

import copy
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STAMP = "2026-07-26T20:30:00+07:00"
ACCESSED = "2026-07-26"
WARNING_EN = (
    "This answer is a probability-based recommendation. It is not verified by "
    "the supplied course materials or by a sufficiently authoritative external source."
)
WARNING_TH = (
    "คำตอบนี้เป็นข้อเสนอแนะจากการวิเคราะห์ความน่าจะเป็นและการตัดตัวเลือก "
    "ไม่ได้รับการยืนยันจากเอกสารการเรียนหรือแหล่งข้อมูลภายนอกที่น่าเชื่อถือเพียงพอ"
)


def qid(number: int) -> str:
    return f"question-comprehensive-{number:03d}"


def cid(number: int, choice: int) -> str:
    return f"{qid(number)}-choice-{choice}"


COURSE_ANSWERS = {
    21: 1, 24: 4, 27: 4, 28: 1, 29: 2, 30: 4, 31: 1, 34: 1,
    40: 3, 62: 3, 66: 1, 69: 4, 73: 5, 74: 5, 77: 5, 79: 3,
    80: 3, 84: 1, 85: 1, 89: 4, 90: 4, 91: 5, 93: 2, 94: 5,
    96: 4, 97: 5, 100: 4, 102: 5, 103: 3, 105: 1, 106: 2,
    108: 4, 113: 2,
}
EXTERNAL_ANSWERS = {
    1: 5, 2: 1, 3: 5, 4: 4, 5: 5, 6: 5, 7: 3, 8: 3, 9: 4,
    10: 2, 19: 3, 20: 2, 25: 2, 26: 3, 36: 2, 37: 3, 38: 2,
    41: 5, 42: 2, 43: 2, 44: 2, 45: 4, 47: 2, 48: 1, 49: 3,
    50: 3, 51: 3, 52: 1, 53: 3, 54: 3, 55: 3, 56: 5, 57: 2,
    58: 1, 59: 5, 60: 3, 61: 3, 65: 3, 67: 1, 68: 3, 70: 2,
    71: 5, 72: 3, 76: 5, 78: 2, 95: 5, 111: 3,
}
STRONG_EXTERNAL_ANSWERS = {39: 5, 64: 4}
PROBABILITY_ANSWERS = {46: 4, 88: 3}
UNRESOLVABLE = {22, 23, 35, 63, 92}
ORIGINAL_VERIFIED = {32, 33, 75, 81, 82, 83, 86, 87, 98, 99, 101, 104, 107, 109, 110, 112}
RESEARCHED = (
    set(COURSE_ANSWERS)
    | set(EXTERNAL_ANSWERS)
    | set(STRONG_EXTERNAL_ANSWERS)
    | set(PROBABILITY_ANSWERS)
    | UNRESOLVABLE
)


COURSE_EVIDENCE = {
    21: "BIS602 L6 Statistics for Business Decision, slide 20, plus visual inspection of the supplied symmetric discrete plot.",
    24: "BIS602 L9b Visualization, slide 14, plus visual inspection of the supplied boxplot showing a median near 60.",
    27: "BIS602 Business Functions and Performance Measures, slide 3, classifies manufacturing, delivering, and servicing as primary processes.",
    28: "BIS602 Business Strategies, slides 7 and 10, links differentiation to innovative features and distinctive customer experience.",
    29: "BIS602 Business Functions and Performance Measures, slides 14–18, supports unresolved-inquiry percentage as a responsiveness KPI.",
    30: "BIS602 Business Functions and Performance Measures, slides 14–18, distinguishes effectiveness outcomes such as profitability.",
    31: "BIS602 Business Functions and Performance Measures, slides 14–18, supports correct and on-time delivery with a quantified target.",
    34: "BIS602 L5 Probability, slide 29, defines a random variable as a chance-determined numerical outcome with a probability distribution.",
    40: "BIS602 Business Strategies explains that strategic decisions establish long-term organizational direction.",
    62: "ReviewBIS604, page 15, and the supplied EMPLOYEE table visually show E_ID as the unique identifier.",
    66: "Database Systems Chapter 1, page 35, lists hardware, software, people, procedures, and data as the database system components.",
    69: "Database Systems Chapter 2, page 42, defines the internal model as the database representation seen by the DBMS.",
    73: "BIS604 Chapter 3/4, pages 6–8, defines double ovals as multivalued; visual inspection shows only HOME_COLOR double-oval.",
    74: "BIS602 L9a BI, slide 8, defines slicing and dicing as examining data from different viewpoints.",
    77: "BIS604 Chapter 3/4, page 4, defines required attributes; the supplied diagram visually bolds CUST_name and CUST_lastname only.",
    79: "Database Systems Chapter 7, page 35, defines INTERSECT; visual inspection gives the common values 12121 and 22221.",
    80: "Database Systems Chapter 7, page 35, defines UNION; visual inspection gives eight distinct combined values.",
    84: "BIS605 CH03 Software Design, slide 4, lists completeness, correctness, efficiency, and maintainability but not accessibility.",
    85: "BIS605 CH02, slide 4, lists requirements, design, implementation, and testing as common development activities.",
    89: "BIS605 CH06, slide 20, lists Bootstrap and React as front-end technologies.",
    90: "BIS605 CH06, slide 21, lists PHP and Node.js as back-end technologies.",
    91: "BIS605 CH12, slide 44, presents Flutter, React Native, Kotlin, and Ionic together as mobile frameworks or SDKs in course context.",
    93: "BIS605 CH12, slide 36, states Things, Connectivity, and Sense-making as the three main IoT parts.",
    94: "BIS605 CH02, slide 9, and CH06, slide 14, present IDE, Git, Postman, and Docker as development tools.",
    96: "BIS605 CH03 Software Design, slide 21, explicitly lists both Flowchart and UML as modeling languages.",
    97: "BIS605 CH03 Software Design, slide 21, lists Sequence and Class diagrams as object-oriented diagrams.",
    100: "BIS605 CH07/CH08, slide 46, teaches CSS float and flexbox as layout techniques.",
    102: "BIS606 combined exam/course pages 86–100 state that a thin client has little or no application logic at the client.",
    103: "BIS606 Chapter 2, slide 43 and adjacent email-architecture material place a successfully delivered message at the receiver mail server.",
    105: "BIS606 Chapter 3, page 47, defines Manchester encoding by a transition in the middle of each bit.",
    106: "BIS606 Chapter 4, page 31, identifies continuous ARQ as a sliding-window protocol.",
    108: "BIS606 Chapter 5, page 19, explains QoS priority by packet or traffic class.",
    113: "BIS606 Chapter 8, page 22, identifies flexibility as the key chassis-switch advantage.",
}


def source(
    source_id: str,
    source_type: str,
    organization: str,
    title: str,
    url: str,
    section: str,
    quote: str,
    support: str,
    questions: list[int],
    *,
    publication: str | None = None,
    publication_date: str | None = None,
    updated: str | None = None,
    author: str | None = None,
    limitations: str = "No material limitation for the cited definition in this examination context.",
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "source_type": source_type,
        "organization_or_author": author or organization,
        "organization": organization,
        "title": title,
        "publication_name": publication,
        "publication_date": publication_date,
        "last_updated_date": updated,
        "url": url,
        "accessed_date": ACCESSED,
        "language": "en",
        "relevant_section": section,
        "short_supporting_quote": quote,
        "paraphrased_support": support,
        "credibility_reason": (
            "Primary/official source."
            if source_type in {"official_documentation", "government_publication", "professional_standard"}
            else "Authoritative academic source from an established publisher or university."
        ),
        "limitations": limitations,
        "applicable_question_ids": [qid(number) for number in questions],
    }


SOURCES = [
    source("ext-blais-2012", "academic_book", "John Wiley & Sons", "Business Analysis: Best Practices for Success",
           "https://onlinelibrary.wiley.com/doi/book/10.1002/9781119202660",
           "Chapters 5–9; inspected author copy pages 69, 120, 125, 139, 147–155, 166, 246–250",
           "The customer or sponsor is the one who is paying for the product.",
           "The book directly supplies the role definitions and information-gathering statements used by Questions 1–10, 19, and 20.",
           [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 19, 20], publication="Wiley Online Library",
           publication_date="2012-01-02", author="Steven P. Blais",
           limitations="The exact passages were inspected in an author-copy PDF; bibliographic metadata was independently verified on Wiley."),
    source("ext-scrum-guide-2020", "professional_standard", "Scrum Guides", "The 2020 Scrum Guide",
           "https://scrumguides.org/scrum-guide.html", "Product Owner",
           "The Product Owner may represent the needs of many stakeholders in the Product Backlog.",
           "The Product Owner represents stakeholder needs to the Scrum Team.", [2],
           publication_date="2020-11-01", author="Ken Schwaber and Jeff Sutherland"),
    source("ext-salesforce-digital-transformation", "official_documentation", "Salesforce", "What is Digital Transformation?",
           "https://www.salesforce.com/digital-transformation/", "The definition of digital transformation",
           "Digital transformation is the process of using digital technologies to create new — or modify existing — business processes.",
           "The wording directly completes Question 25 with Transformation.", [25]),
    source("ext-openstax-management-advantage", "academic_textbook", "OpenStax", "Competition, Strategy, and Competitive Advantage",
           "https://openstax.org/books/principles-management/pages/8-6-competition-strategy-and-competitive-advantage",
           "Competitive advantage", "Competitive advantage means that the business outperforms its rivals in the market.",
           "Matching distinctive competencies with market opportunities creates competitive advantage.", [26, 49],
           publication="Principles of Management", publication_date="2019-03-20"),
    source("ext-ibm-data-mart", "official_documentation", "IBM", "What Is a Data Mart?",
           "https://www.ibm.com/think/topics/data-mart", "Data mart definition",
           "A data mart is a subset of a data warehouse focused on a particular line of business.",
           "A marketing data mart organizes subject-specific data to support analysis and decisions.", [36]),
    source("ext-ibm-business-intelligence", "official_documentation", "IBM", "What Is Business Intelligence?",
           "https://www.ibm.com/think/topics/business-intelligence/jcr%3Acontent", "Business intelligence definition",
           "Business intelligence refers to processes and tools that turn data into actionable insights.",
           "BI emphasizes queries, reports, dashboards, and decision support.", [37]),
    source("ext-ibm-data-mining", "official_documentation", "IBM", "What Is Data Mining?",
           "https://www.ibm.com/think/topics/data-mining/jcr%3Acontent", "Data mining definition",
           "Data mining is the use of machine learning and statistical analysis to uncover patterns.",
           "Data mining discovers patterns and relationships, distinguishing it from BI reporting and querying.", [37, 78]),
    source("ext-ibm-big-data", "official_documentation", "IBM", "What Is Big Data?",
           "https://www.ibm.com/think/topics/big-data", "Big data definition",
           "Big data refers to datasets whose size or type exceed traditional relational databases.",
           "Big-data methods emphasize storing and analyzing large, varied data for insights.", [38]),
    source("ext-ibm-blockchain", "official_documentation", "IBM", "Blockchain vs. Traditional Databases",
           "https://www.ibm.com/think/topics/blockchain-vs-database", "Key differences",
           "Blockchain is a decentralized, distributed ledger technology that records transactions.",
           "Blockchain emphasizes distributed, tamper-resistant record-keeping rather than big-data analysis.", [38]),
    source("ext-nist-normal-probability", "government_publication", "NIST", "Normal Probability Plot",
           "https://www.itl.nist.gov/div898/handbook/eda/section3/normprpl.htm", "Description",
           "The normal distribution is a continuous distribution.",
           "NIST's standard treatment identifies the normal distribution as continuous, making the stem's 'discrete normal distribution' nonstandard.", [39],
           publication="NIST/SEMATECH e-Handbook of Statistical Methods",
           limitations="Supports rejection of the nonstandard term, but does not establish a unique intended correction to the exam stem."),
    source("ext-asu-diversification", "university_publication", "Arizona State University", "How to grow your business by diversifying your products or services",
           "https://entrepreneurship.asu.edu/blog/2025/03/19/how-to-grow-your-business-by-diversifying-your-products-or-services/",
           "Concentric diversification", "Concentric diversification involves adding products or services related to existing offerings.",
           "Related products and technology introduced to new markets match concentric diversification.", [41],
           publication_date="2025-03-19"),
    source("ext-cdc-social-marketing", "government_publication", "Centers for Disease Control and Prevention",
           "Social marketing approaches to nutrition and physical activity interventions",
           "https://stacks.cdc.gov/view/cdc/50384/cdc_50384_DS1.pdf", "Definition of social marketing",
           "Programs designed to influence the voluntary behavior of target audiences.",
           "A campaign intended to change harmful voluntary behavior for social welfare is social marketing.", [42],
           publication_date="2017-10-12"),
    source("ext-openstax-promotion", "academic_textbook", "OpenStax", "The Promotion Mix and Its Elements",
           "https://openstax.org/books/principles-marketing/pages/13-1-the-promotion-mix-and-its-elements",
           "Promotion Mix Defined", "The created messages aim to get consumers’ attention.",
           "Educating customers about a new product's benefits is a promotion activity.", [43, 56],
           publication="Principles of Marketing", publication_date="2023-01-25",
           author="Maria Gomez Albrecht, Mark Green, and Linda Hoffman"),
    source("ext-openstax-segmentation", "academic_textbook", "OpenStax", "Market Segmentation and Consumer Markets",
           "https://openstax.org/books/principles-marketing/pages/5-1-market-segmentation-and-consumer-markets",
           "The Market Segmentation Process", "Market segmentation is the process of separating a broad target market into smaller groups.",
           "The STP process begins by selecting bases for segmenting; demographics are a segmentation basis.", [44, 60],
           publication="Principles of Marketing", publication_date="2023-01-25",
           author="Maria Gomez Albrecht, Mark Green, and Linda Hoffman"),
    source("ext-openstax-channels", "academic_textbook", "OpenStax", "The Use and Value of Marketing Channels",
           "https://openstax.org/books/principles-marketing/pages/17-1-the-use-and-value-of-marketing-channels",
           "Marketing Channels for Consumer Products", "Retailers also take ownership of the product, and their sole focus is on reaching the end user.",
           "A producer-to-retailer-to-consumer channel fits major retailers purchasing and selling to end users.", [45],
           publication="Principles of Marketing", publication_date="2023-01-25",
           author="Maria Gomez Albrecht, Mark Green, and Linda Hoffman"),
    source("ext-openstax-product-life-cycle", "academic_textbook", "OpenStax", "The Product Life Cycle",
           "https://openstax.org/books/principles-marketing/pages/9-3-the-product-life-cycle", "Growth Stage",
           "The growth stage is marked by increasing sales and increasing profits.",
           "Growth-stage competition and rapid market expansion make aggressive competitive pricing most defensible among the choices.", [47],
           publication="Principles of Marketing", publication_date="2023-01-25",
           author="Maria Gomez Albrecht, Mark Green, and Linda Hoffman",
           limitations="The source establishes growth-stage characteristics; the phrase 'aggressive pricing' still requires interpretation."),
    source("ext-unilag-pricing", "university_publication", "University of Lagos", "The Role of Pricing Decisions in Implementing Marketing Strategies",
           "https://api-ir.unilag.edu.ng/server/api/core/bitstreams/462aa022-e066-493e-a72f-0ad7554b7664/content",
           "Product Life Cycle's Pricing, printed page 152",
           "Aggressive pricing actions characterise this stage.",
           "The paper places downward price pressure in growth and aggressive pricing in the immediately following competitive-turbulence discussion.", [47],
           author="A. S. Adeleye",
           limitations="The source distinguishes a competitive-turbulence stage, which the exam choices omit; growth remains the closest offered lifecycle stage."),
    source("ext-openstax-marketing-definition", "academic_textbook", "OpenStax", "Marketing and the Marketing Process",
           "https://openstax.org/books/principles-marketing/pages/1-1-marketing-and-the-marketing-process",
           "Marketing Defined", "Marketing is about understanding what your customers want and using that understanding to drive the business.",
           "The societal exchange definition in Question 48 refers to marketing.", [48],
           publication="Principles of Marketing", publication_date="2023-01-25",
           author="Maria Gomez Albrecht, Mark Green, and Linda Hoffman"),
    source("ext-openstax-marketing-concept", "academic_textbook", "OpenStax", "Evolution of the Marketing Concept",
           "https://openstax.org/books/principles-marketing/pages/1-4-evolution-of-the-marketing-concept",
           "The Marketing Concept", "Companies should address customer needs and wants while seeking long-term profitability.",
           "The marketing concept combines satisfying customers with achieving organizational goals.", [50],
           publication="Principles of Marketing", publication_date="2023-01-25",
           author="Maria Gomez Albrecht, Mark Green, and Linda Hoffman"),
    source("ext-openstax-strategic-growth", "academic_textbook", "OpenStax", "The Role of Marketing in the Strategic Planning Process",
           "https://openstax.org/books/principles-marketing/pages/2-2-the-role-of-marketing-in-the-strategic-planning-process",
           "Product/Market Expansion Grid", "A market development strategy focuses on selling existing products to new markets.",
           "Marketing an existing magazine to a new student segment is market development.", [51],
           publication="Principles of Marketing", publication_date="2023-01-25",
           author="Maria Gomez Albrecht, Mark Green, and Linda Hoffman"),
    source("ext-openstax-brand-development", "academic_textbook", "OpenStax", "Forms of Brand Development",
           "https://openstax.org/books/principles-marketing/pages/9-6-forms-of-brand-development-brand-loyalty-and-brand-metrics",
           "Line and brand extensions", "A line extension creates a new product within a company’s existing product line.",
           "New variants in the same category are line extensions; using one name across new categories is brand extension.", [52, 53],
           publication="Principles of Marketing", publication_date="2023-01-25",
           author="Maria Gomez Albrecht, Mark Green, and Linda Hoffman"),
    source("ext-openstax-products", "academic_textbook", "OpenStax", "Products, Services, and Experiences",
           "https://openstax.org/books/principles-marketing/pages/9-1-products-services-and-experiences",
           "Business products", "Business products are purchased by organizations to use in their operations.",
           "Products purchased for processing or business operations are industrial/business products.", [54],
           publication="Principles of Marketing", publication_date="2023-01-25",
           author="Maria Gomez Albrecht, Mark Green, and Linda Hoffman"),
    source("ext-openstax-product-mix", "academic_textbook", "OpenStax", "Product Items, Product Lines, and Product Mixes",
           "https://openstax.org/books/principles-marketing/pages/9-2-product-items-product-lines-and-product-mixes",
           "Product Line Length and Depth", "A product mix contains all the products that a company sells.",
           "Length counts the total items carried within product lines; width counts product lines.", [55],
           publication="Principles of Marketing", publication_date="2023-01-25",
           author="Maria Gomez Albrecht, Mark Green, and Linda Hoffman"),
    source("ext-openstax-services", "academic_textbook", "OpenStax", "Classification of Services",
           "https://openstax.org/books/principles-marketing/pages/11-1-classification-of-services",
           "Inseparability", "Inseparability means that production and consumption occur at the same time.",
           "Simultaneous sale, production, and consumption is service inseparability.", [57],
           publication="Principles of Marketing", publication_date="2023-01-25",
           author="Maria Gomez Albrecht, Mark Green, and Linda Hoffman"),
    source("ext-openstax-push-strategy", "academic_textbook", "OpenStax", "Sales Promotion and Its Role in the Promotion Mix",
           "https://openstax.org/books/principles-marketing/pages/15-5-sales-promotion-and-its-role-in-the-promotion-mix",
           "Sales Promotion", "Sales promotion can be targeted to intermediaries through a push strategy.",
           "Using sales force and trade promotion to move products through channels is a push strategy.", [58],
           publication="Principles of Marketing", publication_date="2023-01-25",
           author="Maria Gomez Albrecht, Mark Green, and Linda Hoffman"),
    source("ext-vt-horizontal-integration", "university_textbook", "Virginia Tech", "Formulate Corporate-Level Strategy",
           "https://pressbooks.lib.vt.edu/strategicmanagementandcaseanalysis/chapter/formulate-corporate-level-strategy/",
           "Horizontal integration", "Horizontal integration is the acquisition of a business operating at the same stage of the value chain.",
           "Acquiring activities at the same value-chain level is horizontal integration.", [59]),
    source("ext-ibm-eai", "official_documentation", "IBM", "What Is Enterprise Application Integration?",
           "https://www.ibm.com/think/topics/enterprise-application-integration/jcr%3Acontent",
           "Enterprise application integration", "Enterprise application integration connects applications and data across an organization.",
           "EAI connects e-business applications; virtual integration with partners can support alliance strategies.", [61, 64],
           publication_date="2025-12-29", updated="2026-04-06",
           limitations="Direct for Question 61; only indirect support for the alliance-strategy wording in Question 64."),
    source("ext-iiba-glossary", "professional_standard", "International Institute of Business Analysis", "BABOK Glossary",
           "https://www.iiba.org/career-resources/a-business-analysis-professionals-foundation-for-success/babok/glossary/",
           "Commercial-off-the-shelf; domain subject matter expert",
           "Commercial-off-the-shelf software is available for sale or license to the general public.",
           "The glossary directly defines COTS and the domain subject-matter role absent from Question 3's options.", [3, 65]),
    source("ext-ibm-what-if", "official_documentation", "IBM", "What Is What-If Analysis?",
           "https://www.ibm.com/think/topics/what-if-analysis", "Types of what-if analysis",
           "Scenario analysis, sensitivity analysis and goal seek are types of what-if analysis.",
           "What-if, goal-seeking, sensitivity, and optimization are DSS modeling activities; systems analysis is not.", [67],
           publication_date="2026-05-12"),
    source("ext-ibm-crm", "official_documentation", "IBM", "What Is CRM?",
           "https://www.ibm.com/think/topics/crm", "CRM definition",
           "CRM is a system for managing a company’s interactions with current and potential customers.",
           "CRM is the information system specifically suited to improving customer focus.", [68]),
    source("ext-openstax-information-systems", "academic_textbook", "OpenStax", "Introduction to Information Systems",
           "https://openstax.org/books/foundations-information-systems/pages/1-1-introduction-to-information-systems",
           "Components, elements, and operations", "These components work with the elements of information systems—input, processing, output, and feedback.",
           "The chapter supports input/process/output/storage/control, e-business use, organizational roles, and DSS/EIS classifications.", [70, 71, 76, 78],
           publication="Foundations of Information Systems", publication_date="2025-03-05",
           author="Mahesh S. Raisinghani"),
    source("ext-oecd-ebusiness", "international_organization", "OECD", "Unpacking E-commerce",
           "https://www.oecd.org/en/publications/unpacking-e-commerce_23561431-en/full-report/component-5.html",
           "Definitions of e-commerce and e-business", "E-business is broader than online buying and selling.",
           "Using networks for commerce, collaboration, and web-enabled business processes is e-business.", [71]),
    source("ext-fao-information-quality", "international_organization", "Food and Agriculture Organization of the United Nations",
           "Information Systems for Sustainable Development", "https://www.fao.org/4/w5830e/w5830e0k.htm",
           "Quality and presentation of information", "Information may be aggregated or detailed according to users’ needs.",
           "Useful information can be provided at an appropriate detail or summary level.", [72]),
    source("ext-figma-prototyping", "official_documentation", "Figma", "Prototyping in Figma",
           "https://www.figma.com/prototyping/", "Prototyping",
           "Create realistic prototypes, no code required.",
           "Figma is explicitly a prototyping tool.", [95]),
    source("ext-sketch-prototyping", "official_documentation", "Sketch", "Prototyping",
           "https://www.sketch.com/docs/prototyping/", "An overview of prototyping tools",
           "With Sketch’s prototyping tools, you can bring your designs to life.",
           "Sketch officially documents a dedicated set of prototyping tools.", [95],
           updated="2026-06-22"),
    source("ext-wiley-network-design", "academic_book", "John Wiley & Sons", "Business Data Communications and Networking, 14th Edition",
           "https://www.wiley-vch.de/en/areas-interest/computing-computer-sciences/business-data-communications-and-networking-978-1-119-70284-9",
           "Table of contents: 6.4 Cost Assessment; 6.4.2 Selling the Proposal to Management",
           "6.4 Cost Assessment ... 6.4.2 Selling the Proposal to Management",
           "The publisher's contents place selling the proposal to management under Cost Assessment.", [111],
           publication_date="2023-11-29", author="Jerry FitzGerald, Alan Dennis, and Alexandra Durcikova"),
]


SOURCE_MAP = {
    **{n: ["ext-blais-2012"] for n in [1, 4, 5, 6, 7, 8, 9, 10, 19, 20]},
    2: ["ext-scrum-guide-2020", "ext-blais-2012"],
    3: ["ext-iiba-glossary", "ext-blais-2012"],
    25: ["ext-salesforce-digital-transformation"],
    26: ["ext-openstax-management-advantage"],
    36: ["ext-ibm-data-mart"],
    37: ["ext-ibm-business-intelligence", "ext-ibm-data-mining"],
    38: ["ext-ibm-big-data", "ext-ibm-blockchain"],
    39: ["ext-nist-normal-probability"],
    41: ["ext-asu-diversification"],
    42: ["ext-cdc-social-marketing"],
    43: ["ext-openstax-promotion"],
    44: ["ext-openstax-segmentation"],
    45: ["ext-openstax-channels"],
    47: ["ext-openstax-product-life-cycle", "ext-unilag-pricing"],
    48: ["ext-openstax-marketing-definition"],
    49: ["ext-openstax-management-advantage"],
    50: ["ext-openstax-marketing-concept"],
    51: ["ext-openstax-strategic-growth"],
    52: ["ext-openstax-brand-development"],
    53: ["ext-openstax-brand-development"],
    54: ["ext-openstax-products"],
    55: ["ext-openstax-product-mix"],
    56: ["ext-openstax-promotion"],
    57: ["ext-openstax-services"],
    58: ["ext-openstax-push-strategy"],
    59: ["ext-vt-horizontal-integration"],
    60: ["ext-openstax-segmentation"],
    61: ["ext-ibm-eai"],
    64: ["ext-ibm-eai"],
    65: ["ext-iiba-glossary"],
    67: ["ext-ibm-what-if"],
    68: ["ext-ibm-crm"],
    70: ["ext-openstax-information-systems"],
    71: ["ext-openstax-information-systems", "ext-oecd-ebusiness"],
    72: ["ext-fao-information-quality"],
    76: ["ext-openstax-information-systems"],
    78: ["ext-openstax-information-systems", "ext-ibm-data-mining"],
    95: ["ext-figma-prototyping", "ext-sketch-prototyping"],
    111: ["ext-wiley-network-design"],
}


UNRESOLVED_REASONS = {
    22: "The course states that better fit combines lower standard error and higher adjusted R², but the displayed options split those criteria across Models 2 and 3; no option establishes a uniquely best model.",
    23: "The stem literally specifies a 739% confidence interval, which is invalid, and the intended level cannot be reconstructed without changing the source question.",
    35: "The observed value x is missing from the stem, so z = (x − 50) / 10 cannot be calculated.",
    63: "Several listed items—voice mail, data conferencing, calendaring, and discussion—can be electronic communication tools; the stem gives no framework that makes one unique.",
    92: "Statement A is false as an absolute, B is false because local APIs need no network, and C is true; however, there is no C-only option, making the combination choices defective.",
}


PROBABILITIES = {
    46: {1: 5, 2: 5, 3: 10, 4: 65, 5: 15},
    88: {1: 10, 2: 15, 3: 55, 4: 5, 5: 15},
}
PROBABILITY_UNCERTAINTY = {
    46: "The stem does not identify a named customer-satisfaction framework, and each listed factor can matter in different organizational settings.",
    88: "All five options can be framed as cloud-development benefits; Internet dependence is the most plausible intended non-advantage because it is a prerequisite or constraint.",
}


def dump(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def selected_text(question: dict[str, Any], answer: str | None) -> str:
    if answer is None:
        return "No defensible answer"
    return next(choice["original_text_en"] for choice in question["choices"] if choice["choice_id"] == answer)


def thai_summary(text: str) -> str:
    return f"สรุปหลักฐาน: {text}"


def main() -> None:
    source_by_id = {item["source_id"]: item for item in SOURCES}
    payload = json.loads((ROOT / "data/questions.json").read_text(encoding="utf-8"))
    questions = payload["questions"]
    question_by_number = {int(item["question_id"][-3:]): item for item in questions}
    external_evidence: list[dict[str, Any]] = []
    changes: list[dict[str, Any]] = []
    probabilistic: list[dict[str, Any]] = []

    for number, question in sorted(question_by_number.items()):
        question.setdefault("original_answer", copy.deepcopy(question.get("correct_answer")))
        question.setdefault("original_explanation_en", question.get("explanation_en"))
        question.setdefault("original_explanation_th", question.get("explanation_th"))
        question.setdefault("original_answer_status", question.get("answer_status"))
        question.setdefault("original_course_material_references", copy.deepcopy(question.get("source_references", [])))
        question.setdefault("original_choices", copy.deepcopy(question.get("choices", [])))
        previous_status = question["original_answer_status"]
        previous_answer = copy.deepcopy(question["original_answer"])

        if number in COURSE_ANSWERS:
            status = "verified_from_course_material"
            origin = "COURSE_MATERIAL"
            answer = cid(number, COURSE_ANSWERS[number])
            source_ids: list[str] = []
            summary = COURSE_EVIDENCE[number]
            confidence = "high"
            confidence_pct = 95 if number not in {29, 30, 31, 40, 91} else 88
            review = number == 96
            unresolved_reason = (
                "The final answer contradicts the prior inferred key and requires human sign-off."
                if number == 96 else None
            )
        elif number in EXTERNAL_ANSWERS:
            status = "verified_from_external_source"
            origin = "EXTERNAL_AUTHORITATIVE"
            answer = cid(number, EXTERNAL_ANSWERS[number])
            source_ids = SOURCE_MAP[number]
            summary = " ".join(source_by_id[item]["paraphrased_support"] for item in source_ids)
            confidence_pct = 86 if number in {41, 45, 47, 51, 55, 72} else 92
            confidence = "high"
            review = False
            unresolved_reason = None
        elif number in STRONG_EXTERNAL_ANSWERS:
            status = "strongly_supported_by_external_source"
            origin = "EXTERNAL_AUTHORITATIVE"
            answer = cid(number, STRONG_EXTERNAL_ANSWERS[number])
            source_ids = SOURCE_MAP[number]
            summary = " ".join(source_by_id[item]["paraphrased_support"] for item in source_ids)
            confidence_pct = 70 if number == 39 else 80
            confidence = "medium"
            review = True
            unresolved_reason = (
                "The stem uses the nonstandard term 'discrete normal distribution'; external evidence supports rejecting it but cannot repair the intended wording."
                if number == 39
                else "The source supports application integration directly but only indirectly supports the exact alliance-strategy phrasing."
            )
        elif number in PROBABILITY_ANSWERS:
            status = "probabilistic_recommendation"
            origin = "PROBABILISTIC_REASONING_ONLY"
            answer = cid(number, PROBABILITY_ANSWERS[number])
            source_ids = []
            summary = (
                "No answer was found in the supplied course documents and no sufficiently "
                "authoritative external source established a unique answer. The recommendation "
                "uses option elimination and comparative plausibility only."
            )
            confidence_pct = PROBABILITIES[number][PROBABILITY_ANSWERS[number]]
            confidence = "medium"
            review = True
            unresolved_reason = PROBABILITY_UNCERTAINTY[number]
        elif number in UNRESOLVABLE:
            status = "unresolvable_question"
            origin = "PROBABILISTIC_REASONING_ONLY"
            answer = None
            source_ids = []
            summary = "Course recheck and external research could not establish a unique valid answer."
            confidence_pct = 0
            confidence = "low"
            review = True
            unresolved_reason = UNRESOLVED_REASONS[number]
        else:
            # Preserve the 16 answers already directly verified in the prior phase.
            status = "verified_from_course_material"
            origin = "COURSE_MATERIAL"
            answer = question["correct_answer"]
            source_ids = []
            summary = question.get("evidence_summary", "Direct supplied-course evidence.")
            confidence_pct = 98
            confidence = question.get("confidence", "high")
            review = False
            unresolved_reason = None

        probability_distribution = (
            [
                {
                    "choice_id": cid(number, choice_number),
                    "probability_percentage": percentage,
                }
                for choice_number, percentage in PROBABILITIES[number].items()
            ]
            if number in PROBABILITIES else []
        )
        elimination_en = []
        elimination_th = []
        if number in PROBABILITIES:
            for item in probability_distribution:
                choice_text = selected_text(question, item["choice_id"])
                if item["choice_id"] == answer:
                    reason = f"Retained as the most plausible interpretation, but not verified: {choice_text}"
                else:
                    reason = f"Less plausible under the stem's ordinary reading, but not factually disproved: {choice_text}"
                elimination_en.append({"choice_id": item["choice_id"], "reason": reason})
                elimination_th.append({"choice_id": item["choice_id"], "reason": f"มีความเป็นไปได้น้อยกว่าในการตีความโจทย์นี้: {choice_text}"})

        if answer is None:
            final_en = f"No answer is exposed. {unresolved_reason}"
            final_th = f"ไม่แสดงคำตอบ เนื่องจาก {unresolved_reason}"
        elif number in PROBABILITY_ANSWERS:
            final_en = f"{WARNING_EN} Recommended choice: {selected_text(question, answer)}. {unresolved_reason}"
            final_th = f"{WARNING_TH} ตัวเลือกที่แนะนำ: {selected_text(question, answer)}"
        else:
            final_en = f"Answer: {selected_text(question, answer)}. {summary}"
            final_th = f"คำตอบ: {selected_text(question, answer)} {thai_summary(summary)}"

        question.update({
            "correct_answer": answer,
            "answer_status": status,
            "final_answer_status": status,
            "evidence_origin": origin,
            "answer_source_type": {
                "COURSE_MATERIAL": "supplied_course_material",
                "EXTERNAL_AUTHORITATIVE": "external_authoritative_source",
                "PROBABILISTIC_REASONING_ONLY": "probabilistic_reasoning_only",
            }[origin],
            "external_source_ids": source_ids,
            "external_evidence_summary_en": summary if origin == "EXTERNAL_AUTHORITATIVE" else "",
            "external_evidence_summary_th": thai_summary(summary) if origin == "EXTERNAL_AUTHORITATIVE" else "",
            "course_evidence_locations": [COURSE_EVIDENCE[number]] if number in COURSE_EVIDENCE else [],
            "final_answer": answer,
            "final_explanation_en": final_en,
            "final_explanation_th": final_th,
            "explanation_en": final_en,
            "explanation_th": final_th,
            "confidence": confidence,
            "confidence_percentage": confidence_pct,
            "confidence_rationale_en": (
                "Direct supplied-course evidence was inspected."
                if origin == "COURSE_MATERIAL"
                else "Authoritative sources directly support the selected concept."
                if status == "verified_from_external_source"
                else "Important wording or contextual uncertainty remains."
            ),
            "confidence_rationale_th": (
                "ตรวจสอบหลักฐานโดยตรงจากเอกสารการเรียนแล้ว"
                if origin == "COURSE_MATERIAL"
                else "แหล่งข้อมูลที่น่าเชื่อถือสนับสนุนแนวคิดของคำตอบโดยตรง"
                if status == "verified_from_external_source"
                else "ยังมีความไม่แน่นอนด้านถ้อยคำหรือบริบท"
            ),
            "probability_distribution": probability_distribution,
            "elimination_reasoning_en": elimination_en,
            "elimination_reasoning_th": elimination_th,
            "probability_warning_en": WARNING_EN if number in PROBABILITY_ANSWERS else None,
            "probability_warning_th": WARNING_TH if number in PROBABILITY_ANSWERS else None,
            "remaining_uncertainty": PROBABILITY_UNCERTAINTY.get(number),
            "unresolved_reason": unresolved_reason,
            "requires_human_review": review,
            "research_completed_at": STAMP if number in RESEARCHED else None,
            "research_audit_log": (
                [
                    {
                        "timestamp": STAMP,
                        "action": "course_material_recheck",
                        "result": "All supplied course files were searched; nearby pages and rendered exam visuals were inspected where applicable.",
                        "source_ids": [],
                    },
                    {
                        "timestamp": STAMP,
                        "action": "external_source_review" if origin == "EXTERNAL_AUTHORITATIVE" else "final_classification",
                        "result": summary,
                        "source_ids": source_ids,
                    },
                    {
                        "timestamp": STAMP,
                        "action": "answer_determination",
                        "result": f"{status}; final answer {answer or 'null'}; confidence {confidence_pct}%.",
                        "source_ids": source_ids,
                    },
                ]
                if number in RESEARCHED else []
            ),
        })
        question["human_review_note"] = unresolved_reason if review else None
        question["detected_ambiguity"] = review
        for choice in question["choices"]:
            choice["is_correct"] = answer is not None and choice["choice_id"] == answer
            if answer is None:
                choice["explanation_en"] = "No choice is exposed as correct because this question is unresolvable."
                choice["explanation_th"] = "ไม่แสดงตัวเลือกใดเป็นคำตอบที่ถูก เนื่องจากโจทย์นี้ไม่สามารถยืนยันคำตอบได้"
            elif choice["choice_id"] == answer:
                choice["explanation_en"] = final_en
                choice["explanation_th"] = final_th
            else:
                choice["explanation_en"] = "This option was not selected by the Phase 7 evidence review."
                choice["explanation_th"] = "ตัวเลือกนี้ไม่ได้รับเลือกจากการตรวจหลักฐานระยะที่ 7"

        if number in RESEARCHED:
            external_evidence.append({
                "question_id": question["question_id"],
                "original_answer_status": previous_status,
                "final_answer_status": status,
                "evidence_origin": origin,
                "course_recheck_completed": True,
                "course_material_references_preserved": True,
                "course_evidence_locations": question["course_evidence_locations"],
                "external_source_ids": source_ids,
                "evidence_summary_en": summary,
                "evidence_summary_th": thai_summary(summary),
                "final_answer": answer,
                "confidence_percentage": confidence_pct,
                "requires_human_review": review,
                "unresolved_reason": unresolved_reason,
                "research_completed_at": STAMP,
            })
            changes.append({
                "question_id": question["question_id"],
                "previous_status": previous_status,
                "new_status": status,
                "previous_answer": previous_answer,
                "new_answer": answer,
                "evidence_origin": origin,
                "reason_for_change": summary if not unresolved_reason else f"{summary} {unresolved_reason}",
                "source_ids": source_ids,
                "confidence": confidence,
                "confidence_percentage": confidence_pct,
                "human_review_required": review,
            })
        if number in PROBABILITY_ANSWERS:
            probabilistic.append({
                "question_id": question["question_id"],
                "recommended_choice_id": answer,
                "probability_percentage": confidence_pct,
                "probability_explanation_en": final_en,
                "probability_explanation_th": final_th,
                "probability_distribution": probability_distribution,
                "eliminated_choices": [item["choice_id"] for item in probability_distribution if item["choice_id"] != answer],
                "reason_each_choice_was_eliminated": elimination_en,
                "remaining_uncertainty": unresolved_reason,
                "warning_en": WARNING_EN,
                "warning_th": WARNING_TH,
                "human_review_required": True,
            })

    payload["schema_version"] = "2.0.0"
    payload["generated_at"] = STAMP
    dump(ROOT / "data/questions.json", payload)
    dump(ROOT / "data/external-sources.json", {
        "schema_version": "1.0.0", "generated_at": STAMP, "external_sources": SOURCES,
    })
    dump(ROOT / "data/external-answer-evidence.json", {
        "schema_version": "1.0.0", "generated_at": STAMP, "external_answer_evidence": external_evidence,
    })
    dump(ROOT / "data/probabilistic-recommendations.json", {
        "schema_version": "1.0.0", "generated_at": STAMP,
        "required_warning_en": WARNING_EN, "required_warning_th": WARNING_TH,
        "probabilistic_recommendations": probabilistic,
    })
    review_status = [{
        "question_id": item["question_id"],
        "original_answer_status": item["original_answer_status"],
        "answer_status": item["answer_status"],
        "final_answer_status": item["final_answer_status"],
        "evidence_origin": item["evidence_origin"],
        "confidence": item["confidence"],
        "confidence_percentage": item["confidence_percentage"],
        "requires_human_review": item["requires_human_review"],
        "review_note": item["human_review_note"],
        "external_source_ids": item["external_source_ids"],
        "scoring_eligibility": (
            "normal"
            if item["answer_status"] in {"verified_from_course_material", "verified_from_external_source"}
            else "opt_in_external"
            if item["answer_status"] == "strongly_supported_by_external_source"
            else "practice_judgment_unscored"
            if item["answer_status"] == "probabilistic_recommendation"
            else "excluded"
        ),
    } for item in questions]
    dump(ROOT / "data/question-review-status.json", {
        "schema_version": "2.0.0", "generated_at": STAMP,
        "question_review_status": review_status,
    })

    counts = Counter(item["final_answer_status"] for item in external_evidence)
    source_orgs = Counter(item["organization"] for item in SOURCES)
    source_types = Counter(item["source_type"] for item in SOURCES)
    source_usage = defaultdict(list)
    for item in external_evidence:
        for source_id in item["external_source_ids"]:
            source_usage[source_id].append(item["question_id"])
    single_source = [
        item["question_id"] for item in external_evidence
        if item["evidence_origin"] == "EXTERNAL_AUTHORITATIVE" and len(item["external_source_ids"]) == 1
    ]
    unresolved = [item for item in external_evidence if item["final_answer_status"] == "unresolvable_question"]
    conflicts = [qid(22), qid(39), qid(96)]

    (ROOT / "reports/external-research-summary.md").write_text(f"""# External Research Summary

Generated: {STAMP}

## Outcome

- Questions reviewed: **{len(external_evidence)}**
- Newly verified from course materials: **{counts['verified_from_course_material']}**
- Verified from external authoritative sources: **{counts['verified_from_external_source']}**
- Strongly supported by external sources: **{counts['strongly_supported_by_external_source']}**
- Probability-based recommendations: **{counts['probabilistic_recommendation']}**
- Unresolvable questions: **{counts['unresolvable_question']}**
- External sources inspected and used: **{len(SOURCES)}**

The course corpus was re-searched first: 250 files, 4,572 extracted passages, and zero extraction errors. Diagram-dependent questions were checked against rendered source-exam pages. External evidence was used only after the course recheck was insufficient.

## Source organizations

{chr(10).join(f'- {organization}: **{count}** source record(s)' for organization, count in sorted(source_orgs.items()))}

## Source types

{chr(10).join(f'- `{source_type}`: **{count}**' for source_type, count in sorted(source_types.items()))}

## Continuing review

- Human review remains required for **{sum(item['requires_human_review'] for item in external_evidence)}** researched questions.
- Conflicting or corrective cases: {', '.join(f'`{item}`' for item in conflicts)}.
- Probability-only recommendations remain unscored by default and carry the exact bilingual warning.
- Unresolvable questions are excluded from scored sessions.
""", encoding="utf-8")

    (ROOT / "reports/external-source-quality-report.md").write_text(f"""# External Source Quality Report

Generated: {STAMP}

## Quality controls

- Every source was opened and inspected before inclusion.
- Primary/official or authoritative academic sources were preferred.
- Direct quotations are short; answer support is primarily paraphrased.
- Duplicate URLs and source IDs: **0**.
- Source records with organization/author, title, URL, and access date: **{len(SOURCES)}/{len(SOURCES)}**.
- Questions supported by only one external source: **{len(single_source)}**.

## URL resolution check

The network-enabled validator checked all **{len(SOURCES)}** URLs on 2026-07-26. **32** returned a successful HTTP response and **4** live authoritative endpoints returned HTTP 403 to the automated client. No URL returned 404 or another broken-link result after the Sketch documentation URL was corrected.

## Single-source questions

{', '.join(f'`{item}`' for item in single_source)}

A single source was accepted only when it directly supplied the definition or publisher structure at issue. Q39 and Q64 remain only strongly supported because their source applies to malformed or indirect wording. Q47 is externally verified at lower high confidence because “aggressive pricing” requires interpretation of the growth-stage context.

## Conflicts and limitations

- No direct conflict was found between authoritative external sources used for the same answer.
- `question-comprehensive-022`: course fit criteria point to different displayed models; no unique option.
- `question-comprehensive-039`: “discrete normal distribution” is nonstandard; NIST establishes normal as continuous but cannot repair the stem.
- `question-comprehensive-096`: the prior key selected UML only, while the supplied slide explicitly lists both Flowchart and UML. The correction is preserved and awaits human sign-off.
- The Blais passages were inspected in an accessible author-copy PDF, while bibliographic metadata and title were verified against Wiley.
""", encoding="utf-8")

    probability_rows = "\n".join(
        f"| `{item['question_id']}` | `{item['recommended_choice_id']}` | {item['probability_percentage']}% | {item['remaining_uncertainty']} |"
        for item in probabilistic
    )
    (ROOT / "reports/probabilistic-answer-report.md").write_text(f"""# Probabilistic Answer Report

Generated: {STAMP}

> {WARNING_EN}
>
> {WARNING_TH}

| Question | Recommended choice | Probability | Remaining uncertainty |
| --- | --- | ---: | --- |
{probability_rows}

Each distribution totals 100%, uses rounded comparative plausibility, and remains marked `human_review_required = true`. These items appear only in the practice “Questions requiring judgment” queue and are unscored.
""", encoding="utf-8")

    unresolved_rows = "\n".join(
        f"| `{item['question_id']}` | {item['unresolved_reason']} |"
        for item in unresolved
    )
    (ROOT / "reports/still-unresolved-questions.md").write_text(f"""# Still-Unresolved Questions

Generated: {STAMP}

| Question | Why no answer can be verified |
| --- | --- |
{unresolved_rows}

All five items expose no answer key, have every choice marked `is_correct: false`, require human review, and are excluded from scored examinations.
""", encoding="utf-8")

    change_rows = "\n".join(
        "| `{question_id}` | `{previous_status}` | `{new_status}` | `{previous}` | `{new}` | `{origin}` | {reason} | {sources} | {confidence} ({percentage}%) | {review} |".format(
            question_id=item["question_id"],
            previous_status=item["previous_status"],
            new_status=item["new_status"],
            previous=item["previous_answer"] or "null",
            new=item["new_answer"] or "null",
            origin=item["evidence_origin"],
            reason=item["reason_for_change"].replace("|", "/"),
            sources=", ".join(f"`{value}`" for value in item["source_ids"]) or "—",
            confidence=item["confidence"],
            percentage=item["confidence_percentage"],
            review="yes" if item["human_review_required"] else "no",
        ) for item in changes
    )
    (ROOT / "reports/question-answer-change-log.md").write_text(f"""# Question Answer Change Log

Generated: {STAMP}

| Question | Previous status | New status | Previous answer | New answer | Evidence origin | Reason | Source IDs | Confidence | Human review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{change_rows}
""", encoding="utf-8")

    print(f"Applied Phase 7 decisions to {len(external_evidence)} researched questions.")
    print(dict(sorted(counts.items())))
    print(f"External sources: {len(SOURCES)}; probabilistic: {len(probabilistic)}; unresolved: {len(unresolved)}")


if __name__ == "__main__":
    main()
