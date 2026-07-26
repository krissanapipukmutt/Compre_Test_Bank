# Classification

## การจำแนกประเภท

### Concise summary

Classification learns labeled categories; kNN predicts from nearby observations, while a confusion matrix separates types of correct and incorrect predictions.

### สรุปภาษาไทย

Classification เรียนรู้หมวดหมู่ที่มี Label โดย kNN พยากรณ์จากข้อมูลใกล้เคียง และ Confusion Matrix แยกประเภทผลทำนายที่ถูกและผิด

### คำอธิบายโดยละเอียด

Classification เรียนรู้หมวดหมู่ที่มี Label โดย kNN พยากรณ์จากข้อมูลใกล้เคียง และ Confusion Matrix แยกประเภทผลทำนายที่ถูกและผิด ให้เริ่มจากวัตถุประสงค์ทางธุรกิจ ระบุข้อมูลหรือเงื่อนไขที่ต้องใช้ เลือกแนวคิดหรือขั้นตอนให้ตรงกับโจทย์ ตรวจสมมติฐาน แล้วสื่อความหมายของผลลัพธ์และข้อจำกัดอย่างชัดเจน

### Technical terms and definitions

- **k-nearest neighbors / เพื่อนบ้านใกล้ที่สุด k ตัว** — A classifier that votes from the labels of nearby training cases.  
  ตัวจำแนกที่ลงคะแนนจาก Label ของกรณีฝึกที่อยู่ใกล้
- **Confusion matrix / เมทริกซ์ความสับสน** — Counts predictions by actual and predicted class.  
  นับผลทำนายแยกตามคลาสจริงและคลาสที่ทำนาย
- **Validation / การตรวจสอบแบบจำลอง** — Estimate generalization with data not used to fit the model.  
  ประเมินความสามารถกับข้อมูลที่ไม่ได้ใช้สร้างแบบจำลอง

### Processes and frameworks

- Identify the purpose and boundary of Classification.
- Apply k-nearest neighbors, Confusion matrix, Validation in the order required by the case.
- Check assumptions, evidence quality, and stakeholder consequences.

### Formulas

- `Accuracy = (TP + TN) / (TP + TN + FP + FN)`
- `Precision = TP / (TP + FP)`
- `Recall = TP / (TP + FN)`

### Example

- Apply classification to a supplied exercise or business case and justify each choice from the source material.

### Comparison

- Distinguish `k-nearest neighbors` from `Confusion matrix` by purpose, input, and decision use.

### Common misunderstandings

- Treating k-nearest neighbors as a label to memorize instead of explaining its decision purpose.
- Presenting a result without checking assumptions, scope, or evidence limitations.

### Likely examination points

- Define and distinguish k-nearest neighbors, Confusion matrix, Validation.
- Apply the chapter framework to a short case and justify the selected concept.
- Interpret the result, limitation, or next action.

### Study aids

- Review: Classification learns labeled categories; kNN predicts from nearby observations, while a confusion matrix separates types of correct and incorrect predictions.
- Memory aid: **Purpose → evidence → method → result → limitation.**
- Review questions:
  - What decision problem does Classification address?
  - How do k-nearest neighbors and Confusion matrix differ?
  - Which assumptions or limitations should be disclosed?

### Sources

- `file-793fca945ee860e3` — `TERM1/BIS602/Final/Lacture/L11 Classification.pdf`, pp./slides 1–17

### Evidence

- Confidence: `high`
- Evidence type: `summarized_from_source`
