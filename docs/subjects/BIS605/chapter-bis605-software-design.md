# Software design and requirements

## การออกแบบซอฟต์แวร์และความต้องการ

### Concise summary

Design transforms requirements into modular responsibilities, interfaces, data, and interaction choices while controlling coupling and change impact.

### สรุปภาษาไทย

การออกแบบแปลงความต้องการเป็นความรับผิดชอบแบบโมดูล Interface ข้อมูล และปฏิสัมพันธ์ พร้อมควบคุม Coupling และผลกระทบจากการเปลี่ยนแปลง

### คำอธิบายโดยละเอียด

การออกแบบแปลงความต้องการเป็นความรับผิดชอบแบบโมดูล Interface ข้อมูล และปฏิสัมพันธ์ พร้อมควบคุม Coupling และผลกระทบจากการเปลี่ยนแปลง ให้เริ่มจากวัตถุประสงค์ทางธุรกิจ ระบุข้อมูลหรือเงื่อนไขที่ต้องใช้ เลือกแนวคิดหรือขั้นตอนให้ตรงกับโจทย์ ตรวจสมมติฐาน แล้วสื่อความหมายของผลลัพธ์และข้อจำกัดอย่างชัดเจน

### Technical terms and definitions

- **Modularity / ความเป็นโมดูล** — Decompose a system into focused, replaceable units.  
  แบ่งระบบเป็นหน่วยที่มุ่งหน้าที่และเปลี่ยนแทนได้
- **Cohesion / ความยึดเหนี่ยวภายใน** — How strongly the responsibilities inside a module belong together.  
  ระดับที่ความรับผิดชอบในโมดูลสัมพันธ์เป็นเรื่องเดียวกัน
- **Coupling / การพึ่งพาระหว่างโมดูล** — The degree of dependency between modules.  
  ระดับการพึ่งพากันระหว่างโมดูล

### Processes and frameworks

- Identify the purpose and boundary of Software design and requirements.
- Apply Modularity, Cohesion, Coupling in the order required by the case.
- Check assumptions, evidence quality, and stakeholder consequences.

### Formulas

- No primary formula is required for this chapter.

### Example

- Apply software design and requirements to a supplied exercise or business case and justify each choice from the source material.

### Comparison

- Distinguish `Modularity` from `Cohesion` by purpose, input, and decision use.

### Common misunderstandings

- Treating Modularity as a label to memorize instead of explaining its decision purpose.
- Presenting a result without checking assumptions, scope, or evidence limitations.

### Likely examination points

- Define and distinguish Modularity, Cohesion, Coupling.
- Apply the chapter framework to a short case and justify the selected concept.
- Interpret the result, limitation, or next action.

### Study aids

- Review: Design transforms requirements into modular responsibilities, interfaces, data, and interaction choices while controlling coupling and change impact.
- Memory aid: **Purpose → evidence → method → result → limitation.**
- Review questions:
  - What decision problem does Software design and requirements address?
  - How do Modularity and Cohesion differ?
  - Which assumptions or limitations should be disclosed?

### Sources

- `file-e35d30c4a92884e9` — `TERM1/BIS605/Midterm/Lecture/CH03_SoftwareDesign.pdf`, pp./slides 1–45

### Evidence

- Confidence: `high`
- Evidence type: `summarized_from_source`
