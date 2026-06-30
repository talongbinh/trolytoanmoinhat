import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Cấu hình
st.set_page_config(page_title="Trợ lý Học tập", page_icon="🤖")

def get_pdf_text(path):
    try:
        reader = PdfReader(path)
        return "\n".join([page.extract_text() for page in reader.pages])
    except: return "Lỗi không đọc được file."

pdf_content = get_pdf_text("Test.pdf")
API_KEY = st.sidebar.text_input("Mã API Key:", type="password")

if API_KEY:
    genai.configure(api_key=API_KEY)
    # Dùng model này để đảm bảo độ ổn định cao nhất
    model = genai.GenerativeModel("gemini-3.5-flash")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Chào em, em cần thầy hỗ trợ nội dung nào?"}]
        st.session_state.step = "start"

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Nhập câu hỏi..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        response = ""
        # BƯỚC 1 & 2: Chào hỏi và Phân loại
        if st.session_state.step == "start":
            response = "Em muốn được gợi ý giải từng bước hay muốn thầy cho kết quả của cả bài?"
            st.session_state.step = "choosing"
        
        # BƯỚC 3: Xử lý theo yêu cầu
        elif st.session_state.step == "choosing":
            if "gợi ý" in user_input.lower():
                st.session_state.step = "hinting"
                response = "Được rồi, chúng ta đi từng bước nhé. Hãy nêu bước đầu tiên em định làm là gì?"
            else:
                st.session_state.step = "done"
                response = f"Dưới đây là đáp án trích từ tài liệu:\n\n{pdf_content}"
        
        # BƯỚC 4: Gợi ý và nhận xét
        elif st.session_state.step == "hinting":
            prompt = f"""Bạn là thầy giáo. Dựa vào nội dung: {pdf_content}.
            Học sinh đang cần gợi ý cho câu hỏi '{st.session_state.messages[-3]['content']}'.
            Học sinh vừa làm: '{user_input}'.
            QUY ĐỊNH: 
            1. CHỈ GỢI Ý BƯỚC TIẾP THEO, KHÔNG ĐƯỢC GIẢI HẾT.
            2. Nếu học sinh làm đúng bước đó, hãy khen và yêu cầu bước tiếp.
            3. Nếu học sinh đã giải xong bài, hãy nhận xét chi tiết dựa trên đáp án trong file."""
            response = model.generate_content(prompt).text
            
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
            
        if st.session_state.step == "done":
            st.session_state.step = "start" # Reset lại để hỏi câu khác
