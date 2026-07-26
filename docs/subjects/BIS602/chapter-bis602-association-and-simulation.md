# Association analysis and simulation

## การวิเคราะห์ความสัมพันธ์และการจำลอง

### Concise summary

Association rules reveal co-occurrence patterns through support, confidence, and lift; simulation samples uncertain inputs to study a distribution of possible outcomes.

### สรุปภาษาไทย

กฎความสัมพันธ์เปิดเผยรูปแบบการเกิดร่วมด้วย Support, Confidence และ Lift ส่วนการจำลองสุ่ม Input ที่ไม่แน่นอนเพื่อศึกษาการแจกแจงของผลลัพธ์ที่เป็นไปได้

### คำอธิบายโดยละเอียด

กฎความสัมพันธ์เปิดเผยรูปแบบการเกิดร่วมด้วย Support, Confidence และ Lift ส่วนการจำลองสุ่ม Input ที่ไม่แน่นอนเพื่อศึกษาการแจกแจงของผลลัพธ์ที่เป็นไปได้ ให้เริ่มจากวัตถุประสงค์ทางธุรกิจ ระบุข้อมูลหรือเงื่อนไขที่ต้องใช้ เลือกแนวคิดหรือขั้นตอนให้ตรงกับโจทย์ ตรวจสมมติฐาน แล้วสื่อความหมายของผลลัพธ์และข้อจำกัดอย่างชัดเจน

### Technical terms and definitions

- **Support / ค่าสนับสนุน** — The proportion of transactions containing an itemset.  
  สัดส่วนธุรกรรมที่มีชุดรายการ
- **Confidence / ค่าความเชื่อมั่นของกฎ** — The conditional frequency of the consequent when the antecedent occurs.  
  ความถี่แบบมีเงื่อนไขของผลตามเมื่อเหตุเกิด
- **Monte Carlo simulation / การจำลองมอนติคาร์โล** — Repeated random sampling to approximate an outcome distribution.  
  การสุ่มซ้ำเพื่อประมาณการแจกแจงของผลลัพธ์

### Processes and frameworks

- Identify the purpose and boundary of Association analysis and simulation.
- Apply Support, Confidence, Monte Carlo simulation in the order required by the case.
- Check assumptions, evidence quality, and stakeholder consequences.

### Formulas

- `support(A→B) = P(A∩B)`
- `confidence(A→B) = P(B|A)`
- `lift(A→B) = P(B|A) / P(B)`

### Example

- Apply association analysis and simulation to a supplied exercise or business case and justify each choice from the source material.

### Comparison

- Distinguish `Support` from `Confidence` by purpose, input, and decision use.

### Common misunderstandings

- Treating Support as a label to memorize instead of explaining its decision purpose.
- Presenting a result without checking assumptions, scope, or evidence limitations.

### Likely examination points

- Define and distinguish Support, Confidence, Monte Carlo simulation.
- Apply the chapter framework to a short case and justify the selected concept.
- Interpret the result, limitation, or next action.

### Study aids

- Review: Association rules reveal co-occurrence patterns through support, confidence, and lift; simulation samples uncertain inputs to study a distribution of possible outcomes.
- Memory aid: **Purpose → evidence → method → result → limitation.**
- Review questions:
  - What decision problem does Association analysis and simulation address?
  - How do Support and Confidence differ?
  - Which assumptions or limitations should be disclosed?

### Sources

- `file-b2b50f4c76749d2f` — `TERM1/BIS602/Final/Lacture/Association mining.pdf`, pp./slides 1–19
- `file-94caeadde455c76c` — `TERM1/BIS602/Final/Lacture/BIS602 L14 Simulation.pdf`, pp./slides 1–28

### Evidence

- Confidence: `high`
- Evidence type: `summarized_from_source`
