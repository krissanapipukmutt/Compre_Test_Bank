# Relational model and keys

## แบบจำลองเชิงสัมพันธ์และคีย์

### Concise summary

The relational model organizes tuples in relations, uses keys to identify and connect records, and enforces entity and referential integrity.

### สรุปภาษาไทย

แบบจำลองเชิงสัมพันธ์จัด Tuple ใน Relation ใช้ Key ระบุและเชื่อม Record และบังคับ Entity/Referential Integrity

### คำอธิบายโดยละเอียด

แบบจำลองเชิงสัมพันธ์จัด Tuple ใน Relation ใช้ Key ระบุและเชื่อม Record และบังคับ Entity/Referential Integrity ให้เริ่มจากวัตถุประสงค์ทางธุรกิจ ระบุข้อมูลหรือเงื่อนไขที่ต้องใช้ เลือกแนวคิดหรือขั้นตอนให้ตรงกับโจทย์ ตรวจสมมติฐาน แล้วสื่อความหมายของผลลัพธ์และข้อจำกัดอย่างชัดเจน

### Technical terms and definitions

- **Primary key / คีย์หลัก** — A minimal selected identifier that is unique and not null.  
  ตัวระบุขั้นต่ำที่เลือก ซึ่งไม่ซ้ำและไม่เป็น Null
- **Foreign key / คีย์นอก** — Attributes referencing a candidate key in a related relation.  
  Attribute ที่อ้าง Candidate Key ใน Relation ที่เกี่ยวข้อง
- **Referential integrity / บูรณภาพการอ้างอิง** — Foreign-key values must match a referenced key or satisfy an allowed null rule.  
  ค่าคีย์นอกต้องตรงกับคีย์ที่อ้าง หรือเป็น Null ตามกฎที่อนุญาต

### Processes and frameworks

- Identify the purpose and boundary of Relational model and keys.
- Apply Primary key, Foreign key, Referential integrity in the order required by the case.
- Check assumptions, evidence quality, and stakeholder consequences.

### Formulas

- No primary formula is required for this chapter.

### Example

- Apply relational model and keys to a supplied exercise or business case and justify each choice from the source material.

### Comparison

- Distinguish `Primary key` from `Foreign key` by purpose, input, and decision use.

### Common misunderstandings

- Treating Primary key as a label to memorize instead of explaining its decision purpose.
- Presenting a result without checking assumptions, scope, or evidence limitations.

### Likely examination points

- Define and distinguish Primary key, Foreign key, Referential integrity.
- Apply the chapter framework to a short case and justify the selected concept.
- Interpret the result, limitation, or next action.

### Study aids

- Review: The relational model organizes tuples in relations, uses keys to identify and connect records, and enforces entity and referential integrity.
- Memory aid: **Purpose → evidence → method → result → limitation.**
- Review questions:
  - What decision problem does Relational model and keys address?
  - How do Primary key and Foreign key differ?
  - Which assumptions or limitations should be disclosed?

### Sources

- `file-44af1285663d4416` — `TERM2/BIS603_BIS604 Bussiness Data Management/MIDTERM/LACTURE/Chapter3/Coronel_PPT_Ch034_for2_2017CovidAddCandidateNew.pdf`, pp./slides 1–54

### Evidence

- Confidence: `high`
- Evidence type: `summarized_from_source`
