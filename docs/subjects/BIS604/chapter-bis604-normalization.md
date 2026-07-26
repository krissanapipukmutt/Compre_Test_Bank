# Normalization

## การทำ Normalization

### Concise summary

Normalization uses functional dependencies and normal forms to reduce redundancy and prevent insert, update, and delete anomalies while preserving required relationships.

### สรุปภาษาไทย

Normalization ใช้ Functional Dependency และ Normal Form เพื่อลดความซ้ำและป้องกัน Insert, Update, Delete Anomaly โดยรักษาความสัมพันธ์ที่จำเป็น

### คำอธิบายโดยละเอียด

Normalization ใช้ Functional Dependency และ Normal Form เพื่อลดความซ้ำและป้องกัน Insert, Update, Delete Anomaly โดยรักษาความสัมพันธ์ที่จำเป็น ให้เริ่มจากวัตถุประสงค์ทางธุรกิจ ระบุข้อมูลหรือเงื่อนไขที่ต้องใช้ เลือกแนวคิดหรือขั้นตอนให้ตรงกับโจทย์ ตรวจสมมติฐาน แล้วสื่อความหมายของผลลัพธ์และข้อจำกัดอย่างชัดเจน

### Technical terms and definitions

- **Functional dependency / การขึ้นต่อกันเชิงฟังก์ชัน** — One attribute set determines another attribute set.  
  ชุด Attribute หนึ่งกำหนดค่าของอีกชุด
- **Second normal form / รูปแบบปกติที่สอง** — 1NF with no partial dependency of a non-key attribute on a candidate key.  
  1NF ที่ไม่มี Non-key Attribute ขึ้นกับเพียงบางส่วนของ Candidate Key
- **Third normal form / รูปแบบปกติที่สาม** — 2NF with no disallowed transitive dependency of non-key attributes.  
  2NF ที่ไม่มีการขึ้นต่อแบบส่งผ่านของ Non-key Attribute ที่ไม่อนุญาต

### Processes and frameworks

- Identify the purpose and boundary of Normalization.
- Apply Functional dependency, Second normal form, Third normal form in the order required by the case.
- Check assumptions, evidence quality, and stakeholder consequences.

### Formulas

- No primary formula is required for this chapter.

### Example

- Apply normalization to a supplied exercise or business case and justify each choice from the source material.

### Comparison

- Distinguish `Functional dependency` from `Second normal form` by purpose, input, and decision use.

### Common misunderstandings

- Treating Functional dependency as a label to memorize instead of explaining its decision purpose.
- Presenting a result without checking assumptions, scope, or evidence limitations.

### Likely examination points

- Define and distinguish Functional dependency, Second normal form, Third normal form.
- Apply the chapter framework to a short case and justify the selected concept.
- Interpret the result, limitation, or next action.

### Study aids

- Review: Normalization uses functional dependencies and normal forms to reduce redundancy and prevent insert, update, and delete anomalies while preserving required relationships.
- Memory aid: **Purpose → evidence → method → result → limitation.**
- Review questions:
  - What decision problem does Normalization address?
  - How do Functional dependency and Second normal form differ?
  - Which assumptions or limitations should be disclosed?

### Sources

- `file-341f35b4328df935` — `TERM2/BIS603_BIS604 Bussiness Data Management/FINAL/Chapter6/Leature/Coronel_DatabaseSystems_13e_ch06.pdf`, pp./slides 1–41

### Evidence

- Confidence: `high`
- Evidence type: `summarized_from_source`
