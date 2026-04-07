# Automated Product Knowledge Base (RAG Pipeline)

**ระบบถาม-ตอบข้อมูลสเปกสินค้าอัจฉริยะวัสดุก่อสร้าง**

โปรเจคนี้คือการพัฒนาระบบโดย ธันยรัศมิ์ ประภาจิรสกุล เป็นระบบ Data Pipeline แบบอัตโนมัติ (Automated RAG Pipeline) 
เพื่อสกัดข้อมูลความรู้จาก "ไฟล์แคตตาล็อกสินค้า (PDF)" ซึ่งเป็น Unstructured Data นำมาจัดโครงสร้างใหม่และเก็บลงใน Vector Database 
เพื่อให้ AI สามารถค้นหาสเปกสินค้าได้อย่างรวดเร็วและแม่นยำ

## ปัญหาทางธุรกิจที่แก้ไข (Business Problem & Impact)
* **ปัญหา:** พนักงานขายและทีม Support ต้องเปิดหาข้อมูลสเปก (ความหนา, น้ำหนัก, ขนาดมอเตอร์) จากเอกสาร PDF หลายสิบหน้าด้วยตัวเอง ทำให้ล่าช้าและเสี่ยงต่อการตอบลูกค้าผิดพลาด
* **ทางแก้:** พัฒนา ETL Pipeline ดึงข้อความและ **ตารางสเปก** ออกจาก PDF อัตโนมัติ แปลงให้อยู่ในรูปแบบที่ AI ค้นหาได้ (Vector Embeddings) ลดเวลาค้นหาจากหลักนาทีเหลือเพียงไม่กี่วินาที

## สถาปัตยกรรมระบบ (Data Architecture)

```mermaid
graph TD
    A[ข้อมูล: ไฟล์ PDF (ต้องเป็นข้อความไม่ใช่รูปภาพ)] --> B{Data Extraction}
    B -->|ถอดข้อความ| C[pdfplumber]
    B -->|ถอดตาราง| D[Camelot]
    
    C --> E[Data Cleansing]
    D -->|แปลงตารางเป็น Markdown| E
    
    E --> F[Text Splitter & Chunking]
    F -->|แนบ Metadata| G[HuggingFace Embeddings]
    
    G --> H[(Vector DB: ChromaDB)]
    H <--> I[Retrieval System]
    I <--> J[Web UI: Streamlit]
