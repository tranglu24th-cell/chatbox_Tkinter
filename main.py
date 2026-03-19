import customtkinter as ctk
import threading
import google.generativeai as genai
from PIL import Image

# ==========================================
# 1. CẤU HÌNH API - THAY KEY CỦA BẠN VÀO ĐÂY
# ==========================================
API_KEY = "AIzaSyDhyqJYsjplbAnnW-va3RtWIvPYUkd4a6k" # <-- Dán API Key thật của bạn vào đây

class GeminiAI:
    def __init__(self):
        self.chat_session = None
        try:
            genai.configure(api_key=API_KEY)
            # FIX LỖI 404: Thêm tiền tố 'models/' vào tên model
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.chat_session = self.model.start_chat(history=[])
        except Exception as e:
            print(f"Lỗi khởi tạo: {e}")

    def get_response(self, user_text):
        if not self.chat_session:
            return "❌ Lỗi: Chưa kết nối được API. Kiểm tra lại Key hoặc Internet."
        try:
            response = self.chat_session.send_message(user_text)
            return response.text
        except Exception as e:
            # Xử lý lỗi thân thiện hơn cho đồ án
            if "404" in str(e):
                return "🤖 Gemini: Model hiện tại không tìm thấy (404). Hãy thử cập nhật thư viện `pip install -U google-generativeai`."
            return f"❌ Lỗi: {str(e)}"

    def reset(self):
        self.chat_session = self.model.start_chat(history=[])

# Khởi tạo đối tượng AI
ai_assistant = GeminiAI()

# ==========================================
# 2. GIAO DIỆN PHONG CÁCH STREAMLIT
# ==========================================
ST_COLOR = {
    "bg": "#F0F2F6", "sidebar": "#FFFFFF", "text": "#31333F",
    "user_bg": "#FF4B4B", "user_text": "#FFFFFF",
    "ai_bg": "#FFFFFF", "ai_text": "#31333F", "border": "#DDE3EA"
}

class MessageBubble(ctk.CTkFrame):
    def __init__(self, master, sender, message):
        super().__init__(master, fg_color="transparent")
        is_user = (sender == "Bạn")
        bg = ST_COLOR["user_bg"] if is_user else ST_COLOR["ai_bg"]
        tx = ST_COLOR["user_text"] if is_user else ST_COLOR["ai_text"]
        align = "ne" if is_user else "nw"
        icon = "🧑‍💻" if is_user else "🤖"

        bubble = ctk.CTkFrame(self, fg_color=bg, corner_radius=15, border_width=1, border_color=ST_COLOR["border"])
        bubble.pack(anchor=align, padx=10, pady=5)

        ctk.CTkLabel(bubble, text=f"{icon} {sender}", font=("Arial", 12, "bold"), text_color=tx).pack(anchor="w", padx=15, pady=(8, 2))
        ctk.CTkLabel(bubble, text=message, font=("Arial", 14), text_color=tx, justify="left", wraplength=500).pack(anchor="w", padx=15, pady=(0, 10))

class StreamlitApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gemini Chatbox API - Pro Version")
        self.geometry("1100x750")
        self.configure(fg_color=ST_COLOR["bg"])

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=280, fg_color=ST_COLOR["sidebar"], corner_radius=0, border_width=1, border_color=ST_COLOR["border"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="✨ Gemini API", font=("Arial", 28, "bold"), text_color="#FF4B4B").pack(pady=(40, 10), padx=20, anchor="w")
        ctk.CTkLabel(self.sidebar, text="An Unofficial Chatbox app", font=("Arial", 14), text_color="#7D7F8A").pack(pady=(0, 30), padx=20, anchor="w")

        ctk.CTkButton(self.sidebar, text="🗑️ Clear Chat History", fg_color="transparent", text_color="#FF4B4B", 
                      border_color="#FF4B4B", border_width=1, hover_color="#FEECEB", command=self.clear_chat).pack(pady=10, padx=20, fill="x")

        # --- CHAT AREA ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=(80, 100))

        # --- INPUT AREA ---
        self.input_container = ctk.CTkFrame(self, fg_color=ST_COLOR["bg"])
        self.input_container.grid(row=0, column=1, sticky="sew", padx=30, pady=20)
        
        self.entry = ctk.CTkEntry(self.input_container, placeholder_text="Ask something...", height=50, corner_radius=10)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send())

        self.btn = ctk.CTkButton(self.input_container, text="Send ➔", width=100, height=50, fg_color="#FF4B4B", hover_color="#E04040", command=self.send)
        self.btn.pack(side="right")

    def send(self):
        msg = self.entry.get()
        if not msg.strip(): return
        
        self.add_msg("Bạn", msg)
        self.entry.delete(0, 'end')
        self.btn.configure(state="disabled", text="...")
        
        threading.Thread(target=self.call_api, args=(msg,), daemon=True).start()

    def call_api(self, msg):
        res = ai_assistant.get_response(msg)
        self.after(0, lambda: self.add_msg("Gemini", res))
        self.after(0, lambda: self.btn.configure(state="normal", text="Send ➔"))

    def add_msg(self, sender, msg):
        # 1. Tạo tin nhắn mới
        bubble = MessageBubble(self.scroll_frame, sender, msg)
        bubble.pack(fill="x", pady=5)
        
        # 2. Đợi 10ms để khung hình cập nhật rồi mới cuộn xuống đáy
        # Dòng này giúp giao diện "tự nhảy" xuống tin nhắn mới nhất
        self.after(10, lambda: self.scroll_frame._parent_canvas.yview_moveto(1.0))

    def clear_chat(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        ai_assistant.reset()

if __name__ == "__main__":
    app = StreamlitApp()
    app.after(500, lambda: app.add_msg("Gemini", "Chào bạn! Mình là Gemini. Hôm nay bạn cần hỗ trợ gì cho đồ án không?"))
    app.mainloop()