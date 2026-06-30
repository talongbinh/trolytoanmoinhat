import streamlit as st
import google.generativeai as genai

# Cấu hình trang công khai cho học sinh THCS Hoàng Văn Thụ
st.set_page_config(page_title="Trợ lý Học tập - Thầy Long Bình", page_icon="🤖")

st.title("🤖 Trợ Lý Học Tập Toán & KHTN")
st.subheader("Trường THCS Hoàng Văn Thụ - Thầy Long Bình")
st.write("Chào các em! Hãy nhập bài tập mà các em đang gặp khó khăn vào đây để thầy hướng dẫn giải từng bước nhé!")

# Ô điền API Key bí mật ở thanh bên trái
API_KEY = st.sidebar.text_input("Mã API Key của thầy (Ẩn)", type="password", value="")

if not API_KEY:
    st.info("Vui lòng điền mã API Key ở thanh bên trái để kích hoạt ứng dụng.")
else:
    genai.configure(api_key=API_KEY)
    
    system_instruction = (
        "Bạn là trợ lý học tập AI môn Toán và Khoa học tự nhiên của thầy Long Bình tại trường THCS Hoàng Văn Thụ. "
        "Nhiệm vụ của bạn là hướng dẫn học sinh giải bài tập theo đúng phương pháp sư phạm từng bước một.\n\n"
        "QUY TẮC BẮT BUỘC:\n"
        "1. KHÔNG BAO GIỜ đưa ra lời giải chi tiết hay đáp số ngay từ đầu.\n"
        "2. Khi học sinh gửi đề bài, hãy chào hỏi thân thiện, sau đó chỉ ra hoặc hỏi học sinh về bước tư duy đầu tiên.\n"
        "3. Chia nhỏ bài toán thành các chặng. Đợi học sinh phản hồi xong bước trước mới gợi ý tiếp bước sau.\n"
        "4. Nếu học sinh làm sai, hãy nhẹ nhàng chỉ ra chỗ sai và đặt câu hỏi gợi ý để học sinh tự sửa."
    )
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Nhập đề bài hoặc câu trả lời của em..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        try:
            model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", system_instruction=system_instruction)
            api_history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat = model.start_chat(history=api_history)
            response = chat.send_message(user_input)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            with st.chat_message("assistant"):
                st.write(response.text)
        except Exception as e:
            st.error(f"Lỗi kết nối: {e}")
