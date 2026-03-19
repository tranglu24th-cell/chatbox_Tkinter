import google.generativeai as genai

class GeminiAssistant:
    def __init__(self, api_key):
        # Cấu hình API
        genai.configure(api_key=api_key)
        # Sử dụng model flash cho nhanh hoặc pro nếu cần chính xác cao
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        # Bắt đầu phiên chat có lịch sử (Memory)
        self.chat_session = self.model.start_chat(history=[])

    def get_response(self, user_text):
        try:
            # Gửi tin nhắn và nhận phản hồi
            response = self.chat_session.send_message(user_text)
            return response.text
        except Exception as e:
            return f"Lỗi kết nối: {str(e)}"