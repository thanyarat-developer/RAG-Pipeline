import streamlit as st
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ================= การตั้งค่าหน้าเว็บ =================
st.set_page_config(page_title="Shutter Spec AI", page_icon="🏭", layout="centered")

# ================= โหลดโมเดลและฐานข้อมูล =================
DB_DIR = "./chroma_db"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

@st.cache_resource
def load_database():
    """โหลด Database แค่ครั้งเดียวเพื่อความรวดเร็ว"""
    if not os.path.exists(DB_DIR):
        return None
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    return vectorstore

vectorstore = load_database()

# ================= ส่วนของ UI (User Interface) =================
st.title("🏭 ระบบค้นหาสเปกประตูเหล็กม้วน (AI RAG)")
st.caption("พิมพ์ถามคำถามเกี่ยวกับสเปกสินค้า เช่น ความหนา, น้ำหนัก, หรือมอเตอร์")

if vectorstore is None:
    st.error("⚠️ ไม่พบฐานข้อมูล Vector (ChromaDB) กรุณารันไฟล์ `etl_pipeline.py` ก่อนครับ")
    st.stop()

# ช่องให้ผู้ใช้พิมพ์คำถาม
query = st.text_input("💬 สอบถามข้อมูลสเปกสินค้า:", placeholder="เช่น ประตูทนไฟกันไฟได้นานกี่ชั่วโมง?")

if query:
    with st.spinner("AI กำลังค้นหาข้อมูลจากแคตตาล็อก..."):
        # ค้นหาข้อมูลที่ตรงกันมากที่สุด 3 อันดับแรก
        results = vectorstore.similarity_search(query, k=3)
        
        if results:
            st.success("พบข้อมูลที่เกี่ยวข้องดังนี้:")
            for i, res in enumerate(results):
                # แสดงผลลัพธ์ในรูปแบบการ์ดเปิด-ปิดได้
                with st.expander(f"📌 อ้างอิง {i+1} (จากหน้า {res.metadata['page']} - ประเภท: {res.metadata['data_type']})", expanded=(i==0)):
                    st.markdown(res.page_content)
                    st.caption(f"แหล่งที่มา: {res.metadata['source']}")
        else:
            st.warning("ไม่พบข้อมูลที่ตรงกับคำถามในแคตตาล็อกครับ")

st.markdown("---")
st.markdown("**พัฒนาโดย:** ธันยรัศมิ์ ประภาจิรสกุล | **เทคโนโลยี:** LangChain, ChromaDB, Streamlit")
