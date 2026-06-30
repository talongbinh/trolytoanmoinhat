import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Cấu hình trang
st.set_page_config(page_title="Trợ lý Học tập - Thầy Long Bình", page_icon="🤖")

st.title("🤖 Trợ Lý Học Tập Toán & KHTN")
st.subheader("Trường THCS Hoàng Văn Thụ - Thầy Long Bình")

# Hàm đọc file PDF
def get_pdf_text(pdf_file_path):
    try:
        reader = PdfReader(pdf_file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Lỗi đọc file: {e}"

# Load dữ liệu từ PDF
pdf_content = get_pdf_text("Test.pdf")

API_KEY = st.sidebar.text_input("Mã API Key:", type="password")

if not API_KEY:
    st.info("Vui lòng điền mã API Key để bắt đầu.")
else:
    genai.configure(api_key=API_KEY)
    
    system_instruction = f"""
    Bạn là trợ lý học tập của thầy Long Bình (THCS Hoàng Văn Thụ). 
    Dưới đây là ngân hàng bài tập từ file PDF:
    {pdf_content}
    
    QUY TẮC:
    1. Khi học sinh nhập tên câu hỏi (ví dụ: 'Câu 1'), hãy tìm đề bài trong dữ liệu trên.
    2. KHÔNG giải ngay. Hãy chào hỏi, xác nhận lại đề bài và đưa ra gợi ý bước đầu.
    3. Nếu học sinh đã đưa ra cách giải đúng, hãy xác nhận và cung cấp đáp án chi tiết để đối chiếu.
    4. Nếu không tìm thấy câu hỏi trong file, hãy thông báo lịch sự cho học sinh.
    """
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Nhập tên câu cần hỏi (ví dụ: Câu 1)..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        try:
            # Đã cập nhật đúng tên model là gemini-2.5-flash theo yêu cầu
            model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=system_instruction)
            chat = model.start_chat(history=[])
            response = chat.send_message(user_input)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            with st.chat_message("assistant"):
                st.write(response.text)
        except Exception as e:
            st.error(f"Lỗi hệ thống (Vui lòng kiểm tra lại API Key hoặc quyền truy cập model): {e}")
