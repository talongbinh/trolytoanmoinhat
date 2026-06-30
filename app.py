import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

st.set_page_config(page_title="Trợ lý Học tập - Thầy Long Bình", page_icon="🤖")

def get_pdf_text(pdf_file_path):
    try:
        reader = PdfReader(pdf_file_path)
        return "\n".join([page.extract_text() for page in reader.pages])
    except: return ""

pdf_content = get_pdf_text("Test.pdf")
API_KEY = st.sidebar.text_input("Mã API Key:", type="password")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-3.5-flash")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Chào em, em cần thầy hỗ trợ nội dung nào?"}]
        st.session_state.step = "start" # start -> choosing -> hint/answer

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Nhập yêu cầu..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Logic điều khiển từng bước
        response = ""
        
        if st.session_state.step == "start":
            response = "Em muốn được gợi ý giải từng bước hay muốn thầy cho kết quả của cả bài?"
            st.session_state.step = "choosing"
            
        elif st.session_state.step == "choosing":
            if "gợi ý" in user_input.lower():
                st.session_state.step = "hint"
                response = "Được rồi, mình bắt đầu nhé! Với bài này, bước đầu tiên em cần xác định công thức nào? Hãy nêu hướng giải quyết của em đi."
            else:
                st.session_state.step = "answer"
                response = f"Đây là đáp án chi tiết:\n\n{pdf_content}\n\n(Thầy đã trích xuất từ đề bài)."
        
        elif st.session_state.step == "hint":
            # AI chỉ gợi ý bước tiếp theo, không giải hết
            prompt = f"Học sinh đang cần gợi ý giải bài tập. Đề bài: {pdf_content}. Học sinh vừa phản hồi: '{user_input}'. Hãy chỉ đưa ra gợi ý cho bước tiếp theo, KHÔNG giải hết bài."
            response = model.generate_content(prompt).text
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
            
        if st.session_state.step == "answer":
            st.session_state.step = "start" # Reset về đầu sau khi xong
