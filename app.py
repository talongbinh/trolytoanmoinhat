import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Cấu hình trang
st.set_page_config(page_title="Trợ lý Học tập - Thầy Long Bình", page_icon="🤖")

# Hàm đọc file PDF và lấy text
def get_pdf_text(pdf_file_path):
    try:
        reader = PdfReader(pdf_file_path)
        text = ""
        for page in reader.pages:
            # Lấy text dưới dạng thô để giữ nguyên các ký tự LaTeX
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return ""

# Load nội dung từ Test.pdf
pdf_content = get_pdf_text("Test.pdf")

API_KEY = st.sidebar.text_input("Mã API Key:", type="password")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-3.5-flash")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Chào em, em cần thầy hỗ trợ nội dung nào?"}]
        st.session_state.step = "start"

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            # Hiển thị nội dung, hỗ trợ LaTeX nếu có $...$
            st.write(msg["content"])

    if user_input := st.chat_input("Nhập câu hỏi..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        response_text = ""
        
        # Logic 4 bước
        if st.session_state.step == "start":
            response_text = "Em muốn được gợi ý giải từng bước hay muốn thầy cho kết quả của cả bài?"
            st.session_state.step = "choosing"
            
        elif st.session_state.step == "choosing":
            if "gợi ý" in user_input.lower():
                st.session_state.step = "hinting"
                response_text = "Được rồi, mình đi từng bước nhé! Em hãy nêu hướng giải quyết đầu tiên của em là gì?"
            else:
                st.session_state.step = "done"
                response_text = f"Đây là đáp án:\n\n{pdf_content}"
        
        elif st.session_state.step == "hinting":
            prompt = f"Bạn là giáo viên. Dựa vào nội dung tài liệu LaTeX sau: {pdf_content}. Học sinh muốn được gợi ý bài tập '{user_input}'. Hãy chỉ đưa ra gợi ý bước tiếp theo, KHÔNG giải hết bài. Sử dụng cú pháp LaTeX cho công thức toán."
            response_text = model.generate_content(prompt).text
            
        # Hiển thị phản hồi với hỗ trợ LaTeX
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            # Streamlit tự động nhận diện LaTeX trong st.write() nếu bao quanh bởi $...$
            st.write(response_text)
            
        if st.session_state.step == "done":
            st.session_state.step = "start"
