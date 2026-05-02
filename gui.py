import customtkinter as ctk
import threading
from pipeline import AutomationPipeline
import os
import sys

# 터미널의 print() 출력을 GUI 창으로 가로채는 클래스
class PrintRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", string)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def flush(self):
        pass

ctk.set_appearance_mode("Dark")  # 다크 모드 적용
ctk.set_default_color_theme("blue")  # 파란색 테마

class DobiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DOBI - 글로벌 리스팅 자동화 시스템")
        self.geometry("800x600")
        
        # 그리드 레이아웃 설정
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. 상단 타이틀
        self.title_label = ctk.CTkLabel(self, text="🚀 DOBI 역직구 자동화 대시보드", font=ctk.CTkFont(size=26, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 2. 입력 프레임 (URL 입력 및 버튼)
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(self.input_frame, placeholder_text="한국 쇼핑몰(무신사 등) 상품 URL을 붙여넣으세요...", height=40)
        self.url_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.start_button = ctk.CTkButton(self.input_frame, text="클릭 한 번에 수집 & 이베이 등록", font=ctk.CTkFont(weight="bold"), height=40, command=self.start_pipeline)
        self.start_button.grid(row=0, column=1, padx=10, pady=10)

        # 3. 로그 창 (터미널 출력 화면)
        self.log_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(size=14))
        self.log_textbox.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.log_textbox.insert("0.0", "시스템을 준비 중입니다. 잠시만 기다려주세요...\n")
        self.log_textbox.configure(state="disabled")

        # 터미널 출력을 로그 창으로 연결
        sys.stdout = PrintRedirector(self.log_textbox)

        # 파이프라인 백그라운드 초기화 (AI 모델 로딩으로 인한 멈춤 방지)
        threading.Thread(target=self.init_pipeline, daemon=True).start()

    def log(self, message):
        print(message) # 이제 print를 쓰면 자동으로 GUI 화면에 찍힙니다.

    def init_pipeline(self):
        try:
            self.pipeline = AutomationPipeline()
            self.log("\n✅ AI 엔진 및 파이프라인 초기화 완료!")
            self.log("▶️ URL을 입력하고 우측의 버튼을 클릭하세요.\n")
        except Exception as e:
            self.log(f"\n❌ 초기화 실패: {e}")

    def start_pipeline(self):
        url = self.url_entry.get().strip()
        if not url:
            self.log("❌ URL을 입력해야 작동합니다.")
            return

        self.start_button.configure(state="disabled")
        self.log("="*50)
        self.log(f"🚀 자동화 시작: {url}")
        
        # UI가 멈추지 않도록 별도의 쓰레드에서 실행
        threading.Thread(target=self.run_automation, args=(url,), daemon=True).start()

    def run_automation(self, url):
        try:
            # do_list=True를 줘서 실제 eBay API까지 연동되게 함
            self.pipeline.run_full_pipeline(url, do_list=True)
            self.log("\n🎉 모든 작업이 성공적으로 완료되었습니다!")
        except Exception as e:
            self.log(f"\n❌ 작업 중 에러 발생: {e}")
        finally:
            self.log("="*50 + "\n")
            self.start_button.configure(state="normal")

if __name__ == "__main__":
    app = DobiApp()
    app.mainloop()
