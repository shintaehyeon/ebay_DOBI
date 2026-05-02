# gui_tkinter.py
"""Tkinter based desktop GUI for DOBI automation.

Features:
- Input field for a single product URL.
- Button to start the full pipeline (scrape → AI → optional eBay listing).
- Text widget that captures stdout/stderr and shows logs in real‑time.
- Runs the heavy pipeline in a background thread so the UI stays responsive.
- Works on any macOS version because it uses the standard `tkinter` library
  (no customtkinter dependency).
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# Import the pipeline class (make sure the project root is in PYTHONPATH)
from pipeline import AutomationPipeline

# ------------------------------------------------------------
# Helper to redirect prints to the GUI log widget
# ------------------------------------------------------------
class PrintRedirector:
    def __init__(self, widget: scrolledtext.ScrolledText):
        self.widget = widget

    def write(self, message: str):
        # Append text in a thread‑safe way
        def append():
            self.widget.configure(state="normal")
            self.widget.insert(tk.END, message)
            self.widget.see(tk.END)
            self.widget.configure(state="disabled")
        self.widget.after(0, append)

    def flush(self):
        pass

# ------------------------------------------------------------
# Main Application Window
# ------------------------------------------------------------
class DobiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DOBI – 글로벌 리스팅 자동화")
        self.geometry("850x600")
        self.configure(bg="#2b2b2b")  # dark background

        # ---------- Layout ----------
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Title label
        title_lbl = ttk.Label(
            self,
            text="🚀 DOBI 역직구 자동화 대시보드",
            font=("Helvetica", 20, "bold"),
            foreground="#00ffcc",
            background="#2b2b2b",
        )
        title_lbl.grid(row=0, column=0, pady=(15, 5), padx=10, sticky="w")

        # Input frame (URL entry + Run button)
        input_frame = ttk.Frame(self)
        input_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
        input_frame.columnconfigure(0, weight=1)

        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(
            input_frame,
            textvariable=self.url_var,
            font=("Helvetica", 12),
            width=70,
        )
        url_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        url_entry.insert(0, "한국 쇼핑몰(무신사 등) 상품 URL을 입력하세요…")

        run_btn = ttk.Button(
            input_frame,
            text="🔧 수집 & eBay 등록",
            command=self.start_pipeline,
        )
        run_btn.grid(row=0, column=1, padx=5)
        self.run_button = run_btn

        # Log textbox (read‑only scrollable area)
        self.log_box = scrolledtext.ScrolledText(
            self,
            font=("Courier", 10),
            bg="#1e1e1e",
            fg="#d0ffd0",
            insertbackground="#d0ffd0",
            wrap=tk.WORD,
            height=20,
        )
        self.log_box.grid(row=2, column=0, padx=10, pady=(5, 15), sticky="nsew")
        self.log_box.insert(tk.END, "시스템 초기화 중...\n")
        self.log_box.configure(state="disabled")

        # Redirect stdout / stderr to the log widget
        sys.stdout = PrintRedirector(self.log_box)
        sys.stderr = PrintRedirector(self.log_box)

        # Load the pipeline in a background thread (AI model loading can be slow)
        threading.Thread(target=self.init_pipeline, daemon=True).start()

    # -----------------------------------------------------------------
    # Initialization of the heavy pipeline
    # -----------------------------------------------------------------
    def init_pipeline(self):
        try:
            self.pipeline = AutomationPipeline()
            print("\n✅ AI 엔진 및 파이프라인 초기화 완료!")
            print("▶️ URL을 입력하고 버튼을 눌러 주세요.\n")
        except Exception as exc:
            print(f"❌ 파이프라인 초기화 실패: {exc}")

    # -----------------------------------------------------------------
    # Start button callback – runs the pipeline for the entered URL
    # -----------------------------------------------------------------
    def start_pipeline(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("입력 오류", "상품 URL을 입력해 주세요.")
            return
        self.run_button.config(state="disabled")
        print("=" * 50)
        print(f"🚀 자동화 시작: {url}\n")
        threading.Thread(target=self.run_automation, args=(url,), daemon=True).start()

    def run_automation(self, url: str):
        try:
            # `do_list=True` will also push the product to eBay sandbox.
            self.pipeline.run_full_pipeline(url, do_list=True)
            print("\n🎉 모든 작업이 성공적으로 마무리되었습니다!")
        except Exception as e:
            print(f"\n❌ 작업 중 오류 발생: {e}")
        finally:
            print("=" * 50 + "\n")
            self.run_button.config(state="normal")

# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    app = DobiApp()
    app.mainloop()
