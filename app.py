import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Cấu hình trang
st.set_page_config(page_title="Trợ lý Học tập - Thầy Long Bình", page_icon="🤖")

st.title("🤖 Trợ Lý Học Tập Toán")
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
    
   QUY TẮC PHẢN HỒI (BẮT BUỘC):
    1. Khi học sinh hỏi về một câu hỏi, hãy tra cứu trong file PDF để xác định đề bài.
    2. TRÌNH TỰ HƯỚNG DẪN:
       - Bước 1: Phân tích đề bài, xác định dạng toán và yêu cầu học sinh nêu công thức hoặc bước đầu tiên cần làm.
       - Bước 2: Nếu học sinh trả lời đúng, hãy khen ngợi và hướng dẫn bước tiếp theo.
       - Bước 3: Nếu học sinh trả lời sai, hãy nhẹ nhàng chỉ ra lỗi sai và gợi ý cách sửa.
    3. TRƯỜNG HỢP HỌC SINH KHÔNG BIẾT LÀM (Ví dụ: 'em chịu', 'em không biết', 'giải cho em đi'):
       - Bạn được phép cung cấp lời giải chi tiết, rõ ràng và kèm theo lời giải thích tại sao lại làm như vậy để học sinh hiểu bản chất.
    4. Luôn giữ thái độ thân thiện, khích lệ như một người thầy tâm huyết.
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
            model = genai.GenerativeModel(model_name="gemini-1.5-pro", system_instruction=system_instruction)
            chat = model.start_chat(history=[])
            response = chat.send_message(user_input)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            with st.chat_message("assistant"):
                st.write(response.text)
        except Exception as e:
            st.error(f"Lỗi hệ thống (Vui lòng kiểm tra lại API Key hoặc quyền truy cập model): {e}")
