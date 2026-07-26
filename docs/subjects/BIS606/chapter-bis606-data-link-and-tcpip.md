# Data link, network, and transport layers

## ชั้น Data Link, Network และ Transport

### Concise summary

Frames provide local delivery, IP routes packets across networks, and transport protocols provide application-to-application delivery with different reliability tradeoffs.

### สรุปภาษาไทย

Frame ส่งข้อมูลในเครือข่ายท้องถิ่น IP กำหนดเส้นทาง Packet ข้ามเครือข่าย และ Transport Protocol ส่งระหว่าง Application ด้วยข้อแลกเปลี่ยนด้านความน่าเชื่อถือ

### คำอธิบายโดยละเอียด

Frame ส่งข้อมูลในเครือข่ายท้องถิ่น IP กำหนดเส้นทาง Packet ข้ามเครือข่าย และ Transport Protocol ส่งระหว่าง Application ด้วยข้อแลกเปลี่ยนด้านความน่าเชื่อถือ ให้เริ่มจากวัตถุประสงค์ทางธุรกิจ ระบุข้อมูลหรือเงื่อนไขที่ต้องใช้ เลือกแนวคิดหรือขั้นตอนให้ตรงกับโจทย์ ตรวจสมมติฐาน แล้วสื่อความหมายของผลลัพธ์และข้อจำกัดอย่างชัดเจน

### Technical terms and definitions

- **Frame / เฟรม** — A data-link protocol data unit for local-network delivery.  
  หน่วยข้อมูลของ Data Link สำหรับการส่งในเครือข่ายท้องถิ่น
- **IP routing / การกำหนดเส้นทาง IP** — Forward packets toward destination networks using routing information.  
  ส่งต่อ Packet ไปยังเครือข่ายปลายทางด้วยข้อมูลเส้นทาง
- **TCP and UDP / TCP และ UDP** — Transport protocols offering different connection, reliability, and overhead properties.  
  Transport Protocol ที่มีคุณสมบัติการเชื่อมต่อ ความน่าเชื่อถือ และ Overhead ต่างกัน

### Processes and frameworks

- Identify the purpose and boundary of Data link, network, and transport layers.
- Apply Frame, IP routing, TCP and UDP in the order required by the case.
- Check assumptions, evidence quality, and stakeholder consequences.

### Formulas

- No primary formula is required for this chapter.

### Example

- Apply data link, network, and transport layers to a supplied exercise or business case and justify each choice from the source material.

### Comparison

- Distinguish `Frame` from `IP routing` by purpose, input, and decision use.

### Common misunderstandings

- Treating Frame as a label to memorize instead of explaining its decision purpose.
- Presenting a result without checking assumptions, scope, or evidence limitations.

### Likely examination points

- Define and distinguish Frame, IP routing, TCP and UDP.
- Apply the chapter framework to a short case and justify the selected concept.
- Interpret the result, limitation, or next action.

### Study aids

- Review: Frames provide local delivery, IP routes packets across networks, and transport protocols provide application-to-application delivery with different reliability tradeoffs.
- Memory aid: **Purpose → evidence → method → result → limitation.**
- Review questions:
  - What decision problem does Data link, network, and transport layers address?
  - How do Frame and IP routing differ?
  - Which assumptions or limitations should be disclosed?

### Sources

- `file-b2ad8cad2c8374ec` — `TERM1/BIS606/Midterm/Lecture/ch03_e14.pdf`, pp./slides 1–86
- `file-882f2430d45fc213` — `TERM1/BIS606/Midterm/Lecture/ch04_14e.pdf`, pp./slides 1–68
- `file-c2bd7b1ca3176963` — `TERM1/BIS606/Midterm/Lecture/ch05_14e.pdf`, pp./slides 1–99

### Evidence

- Confidence: `high`
- Evidence type: `summarized_from_source`
