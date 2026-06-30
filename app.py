import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

st.set_page_config(page_title="Trợ lý Học tập - Thầy Long Bình", page_icon="🤖")

# Hàm đọc PDF
def get_pdf_text(pdf_file_path):
    try:
        reader = PdfReader(pdf_file_path)
        return "\n".join([page.extract_text() for page in reader.pages])
    except: return ""

pdf_content = get_pdf_text("Test.pdf")

API_KEY = st.sidebar.text_input("Mã API Key:", type="password")

if not API_KEY:
    st.info("Vui lòng nhập API Key.")
else:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-3.5-flash")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Chào em, em cần thầy hỗ trợ nội dung nào?"}]
        st.session_state.mode = None # Lưu trạng thái: 'hint' hoặc 'answer'

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Nhập yêu cầu của em..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Xử lý logic theo bước
        # Bước 2: Phân loại yêu cầu
        if "giải" in user_input.lower() and st.session_state.mode is None:
            response = "Em muốn được gợi ý giải từng bước hay muốn thầy cung cấp kết quả của cả bài?"
            st.session_state.mode = "choosing"
        
        # Bước 3: Phân nhánh Gợi ý hoặc Đáp án
        elif st.session_state.mode == "choosing":
            if "gợi ý" in user_input.lower():
                st.session_state.mode = "hint"
                response = "Được rồi, chúng ta bắt đầu từng bước nhé. Với câu hỏi này, em hãy thử nêu hướng giải quyết đầu tiên hoặc công thức cần sử dụng xem nào?"
            else:
                st.session_state.mode = "answer"
                response = f"Đây là đáp án chính xác:\n\n{pdf_content}\n\n(Lưu ý: Thầy đã trích xuất đáp án từ file đề bài)."
        
        # Bước 4: Gợi ý tiếp hoặc nhận xét
        else:
            prompt = f"""Dựa vào nội dung đề bài sau: {pdf_content}.
            Hãy đóng vai thầy giáo, thực hiện tiếp việc hướng dẫn học sinh giải bài tập '{user_input}'.
            Nếu học sinh đã làm xong, hãy nhận xét chính xác dựa trên đáp án trong đề bài."""
            response = model.generate_content(prompt).text

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
