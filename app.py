import streamlit as st
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import etl_pipeline 

st.set_page_config(page_title="Shutter Spec AI", page_icon="🏭", layout="centered")

DB_DIR = "./faiss_db"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
PDF_PATH = "catalog.pdf"

# ================= 🌟 ฝัง API Key ตรงนี้ =================
# ผมพิมพ์ตามภาพที่คุณส่งมาให้แล้ว แต่เพื่อความชัวร์ 100% (กันตัวพิมพ์เล็ก/ใหญ่ผิดเพี้ยน)
# คุณสามารถก๊อปปี้จากหน้าเว็บ Google มาวางทับในเครื่องหมายคำพูดด้านล่างนี้ได้เลยครับ
GEMINI_API_KEY = "AIzaSyDnXBXP7iGlKHPIFYV04_P6we5zH5O5Ztw"
# ========================================================

# [ระบบสร้างฐานข้อมูลอัตโนมัติบน Cloud]
if not os.path.exists(DB_DIR):
    st.warning("⚠️ ไม่พบฐานข้อมูล FAISS! ระบบกำลังสร้าง Knowledge Base อัตโนมัติ (อาจใช้เวลา 2-3 นาที)...")
    with st.spinner("AI กำลังอ่านและสกัดตารางสเปก..."):
        try:
            extracted_data = etl_pipeline.extract_data_from_pdf(PDF_PATH)
            if extracted_data:
                etl_pipeline.build_vector_database(extracted_data)
                st.success("🎉 สร้างฐานข้อมูลสำเร็จ! กำลังโหลดแอปพลิเคชัน...")
                st.rerun()
            else:
                st.error("❌ หาไฟล์เจอครับ แต่มันดึงข้อความออกมาไม่ได้เลย")
                st.stop()
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดตอนอ่านไฟล์: {e}")
            st.stop()

@st.cache_resource
def load_database():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return FAISS.load_local(DB_DIR, embeddings, allow_dangerous_deserialization=True)

vectorstore = load_database()

# ================= หน้าหลัก =================
st.title("🏭 ระบบค้นหาสเปกประตูเหล็กม้วน (AI RAG)")
st.caption("เทคโนโลยี: FAISS Vector Search + Gemini 1.5 Flash | พิมพ์ถามคำถามด้านล่างได้เลยครับ")

query = st.text_input("💬 สอบถามข้อมูลสเปกสินค้า:", placeholder="เช่น ความหนา 0.7 ราคาเท่าไหร่?")

if query:
    with st.spinner("🔍 กำลังค้นหาข้อมูล และให้ AI สรุปคำตอบ..."):
        # 1. ค้นหาข้อมูลดิบจาก FAISS DB
        results = vectorstore.similarity_search(query, k=3)
        
        if results:
            # 2. นำข้อมูลดิบมารวมกันเป็นตัวแปร Context
            context_text = "\n\n".join([f"อ้างอิงหน้าที่ {res.metadata['page']}:\n{res.page_content}" for res in results])
            
            # 3. สร้างคำสั่ง (Prompt)
            prompt_template = """
            คุณคือผู้ช่วยเชี่ยวชาญด้านสเปกประตูเหล็กม้วน
            หน้าที่ของคุณคือใช้ "ข้อมูลอ้างอิง" ที่ให้มาด้านล่างเพื่อตอบ "คำถาม" 
            คำเตือน: ข้อมูลอ้างอิงสกัดมาจาก PDF อาจจะมีสระภาษาไทยที่ผิดเพี้ยน หรือเว้นวรรคแปลกๆ ให้คุณอ่านทำความเข้าใจ และสรุปคำตอบออกมาเป็นภาษาไทยที่อ่านง่าย ถูกต้อง และเป็นมืออาชีพ
            หากในข้อมูลอ้างอิงไม่มีคำตอบที่เกี่ยวข้องเลย ให้ตอบว่า "ขออภัยครับ ไม่พบข้อมูลที่ตรงกับคำถามในแคตตาล็อก" ห้ามเดาข้อมูลเองเด็ดขาด

            ข้อมูลอ้างอิง:
            {context}

            คำถาม: {question}

            คำตอบ:"""
            
            prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
            
            # 4. ส่งข้อมูลให้ Gemini ทำงาน โดยใช้ API Key ที่ฝังไว้ด้านบน
            try:
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY, temperature=0.1)
                chain = prompt | llm
                
                answer = chain.invoke({"context": context_text, "question": query})
                
                # 5. แสดงผลลัพธ์
                st.success("🤖 AI สรุปคำตอบ:")
                st.markdown(f"**{answer.content}**")
                
                with st.expander("🔍 ดูข้อมูลดิบที่ AI ใช้เป็นอ้างอิง (Raw OCR Data)"):
                    st.markdown(context_text)
                    
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อกับ Gemini AI: {e}")
                st.info("💡 แนะนำให้ตรวจสอบว่า API Key พิมพ์ถูกทุกตัวอักษรหรือไม่ (แนะนำให้ก๊อปปี้จากเว็บมาวางทับในโค้ดอีกครั้ง)")
        else:
            st.warning("ไม่พบข้อมูลที่ตรงกับคำถามในแคตตาล็อกครับ")
