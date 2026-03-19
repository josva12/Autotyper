import customtkinter as ctk
import time
import threading
import random
from pynput.keyboard import Controller, Listener, Key

# --- COLOR PALETTE (Matched to your React UI) ---
BG_MAIN = "#1e1e2e"
BG_DARK = "#11111b"
BG_INPUT = "#181825"
BG_CARD = "#242536"
INDIGO = "#4f46e5"
INDIGO_HOVER = "#6366f1"
RED = "#ef4444"
RED_HOVER = "#f87171"
TEXT_LIGHT = "#f8fafc"
TEXT_MUTED = "#94a3b8"
BORDER_COLOR = "#334155"

class AutoTyperApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AutoTyper.AppImage")
        self.geometry("900x650")
        self.configure(fg_color=BG_MAIN)
        
        # State Variables
        self.is_running = False
        self.countdown = 0
        self.delay_var = ctk.StringVar(value="5") # Default 5 seconds
        self.delay_var.trace_add("write", self.validate_delay)
        
        self.keyboard_controller = Controller()

        self.setup_ui()
        self.start_hotkey_listener()

    def setup_ui(self):
        # Configure Grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ================= HEADER =================
        self.header = ctk.CTkFrame(self, height=40, fg_color=BG_DARK, corner_radius=0)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        ctk.CTkLabel(self.header, text="⌨ AUTOTYPER.APPIMAGE", font=("Arial", 12, "bold"), text_color=TEXT_LIGHT).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(self.header, text="🖥 Wayland/X11 Ready   |   🟢", font=("Arial", 11), text_color=TEXT_MUTED).pack(side="right", padx=15)

        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=60, fg_color=BG_DARK, corner_radius=0)
        self.sidebar.grid(row=1, column=0, sticky="ns")
        
        ctk.CTkButton(self.sidebar, text="⚡", width=40, height=40, fg_color=INDIGO, hover_color=INDIGO_HOVER, font=("Arial", 18)).pack(pady=(20, 10))
        ctk.CTkButton(self.sidebar, text="⏱", width=40, height=40, fg_color="transparent", hover_color=BG_INPUT, text_color=TEXT_MUTED, font=("Arial", 18)).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="ℹ", width=40, height=40, fg_color="transparent", hover_color=BG_INPUT, text_color=TEXT_MUTED, font=("Arial", 18)).pack(pady=10)

        # ================= MAIN CONTENT =================
        self.main_content = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=40, pady=30)

        # Title
        ctk.CTkLabel(self.main_content, text="Automation Template", font=("Arial", 28, "bold"), text_color=TEXT_LIGHT).pack(anchor="w")
        ctk.CTkLabel(self.main_content, text="Configure your content and delay. Maximum delay is 45 seconds.", font=("Arial", 12), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        # Config Card
        self.card = ctk.CTkFrame(self.main_content, fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR, corner_radius=15)
        self.card.pack(fill="both", expand=True)

        # Delay Settings Row
        self.delay_frame = ctk.CTkFrame(self.card, fg_color=BG_INPUT, corner_radius=10)
        self.delay_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(self.delay_frame, text="DELAY SETTING:", font=("Arial", 11, "bold"), text_color=TEXT_MUTED).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(self.delay_frame, text="seconds", font=("Arial", 11), text_color=TEXT_MUTED).pack(side="right", padx=15)
        self.delay_entry = ctk.CTkEntry(self.delay_frame, textvariable=self.delay_var, width=60, justify="center", font=("Arial", 16, "bold"), text_color=INDIGO, fg_color=BG_DARK, border_color=BORDER_COLOR)
        self.delay_entry.pack(side="right")

        # Text Area
        ctk.CTkLabel(self.card, text="CONTENT TO AUTO-TYPE", font=("Arial", 11, "bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=25)
        self.textbox = ctk.CTkTextbox(self.card, height=180, fg_color=BG_INPUT, text_color=TEXT_LIGHT, border_width=1, border_color=BORDER_COLOR, font=("Courier", 13))
        self.textbox.pack(fill="x", padx=20, pady=(5, 20))
        self.textbox.insert("1.0", "Paste or type the text you want to be automated here...")

        # Action Footer
        self.action_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(self.action_frame, text="✓ Autosave active", font=("Arial", 12), text_color=TEXT_MUTED).pack(side="left")
        
        self.start_btn = ctk.CTkButton(self.action_frame, text=f"▶ START ({self.delay_var.get()}s)", height=45, width=200, font=("Arial", 14, "bold"), fg_color=INDIGO, hover_color=INDIGO_HOVER, command=self.toggle_sequence)
        self.start_btn.pack(side="right")

        # Pro Tip
        self.tip_frame = ctk.CTkFrame(self.main_content, fg_color="#1e1b4b", border_width=1, border_color=INDIGO_HOVER, corner_radius=10)
        self.tip_frame.pack(fill="x", pady=20)
        tip_text = "Pro Tip: After clicking Start, you have exactly the set delay to click inside the target window (like a terminal, browser, or text editor) where you want the text to appear."
        ctk.CTkLabel(self.tip_frame, text="ℹ " + tip_text, font=("Arial", 12), text_color=TEXT_MUTED, wraplength=700, justify="left").pack(padx=15, pady=15, anchor="w")

        # ================= STATUS BAR =================
        self.statusbar = ctk.CTkFrame(self, height=30, fg_color=BG_DARK, corner_radius=0)
        self.statusbar.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        ctk.CTkLabel(self.statusbar, text="🟢 Daemon: Running   |   [Single Template Mode]", font=("Arial", 11), text_color=TEXT_MUTED).pack(side="left", padx=15)
        ctk.CTkLabel(self.statusbar, text="Global Stop: [ ESC ]", font=("Arial", 11, "bold"), text_color=TEXT_LIGHT).pack(side="right", padx=15)

    def validate_delay(self, *args):
        # Enforce numbers only and max 45
        val = self.delay_var.get()
        if not val.isdigit():
            self.delay_var.set(''.join(filter(str.isdigit, val)))
        elif int(val) > 45:
            self.delay_var.set("45")
            
        if not self.is_running:
            delay_val = self.delay_var.get() if self.delay_var.get() else "0"
            self.start_btn.configure(text=f"▶ START ({delay_val}s)")

    def start_hotkey_listener(self):
        # Global ESC to kill the process
        def on_press(key):
            if key == Key.esc:
                self.is_running = False
        listener = Listener(on_press=on_press)
        listener.daemon = True
        listener.start()

    def toggle_sequence(self):
        if self.is_running:
            self.is_running = False # This will break the running threads
        else:
            try:
                self.countdown = int(self.delay_var.get())
            except ValueError:
                self.countdown = 5
                
            self.is_running = True
            
            # Update UI for running state
            self.card.configure(border_color=INDIGO_HOVER)
            self.delay_entry.configure(state="disabled")
            
            # Start logic in background
            threading.Thread(target=self.countdown_routine, daemon=True).start()

    def countdown_routine(self):
        while self.countdown > 0 and self.is_running:
            self.start_btn.configure(text=f"⏹ {self.countdown}s", fg_color=RED, hover_color=RED_HOVER)
            time.sleep(1)
            self.countdown -= 1

        if self.is_running:
            self.start_btn.configure(text="TYPING...", fg_color=RED, hover_color=RED_HOVER)
            self.type_text()
        else:
            self.reset_ui()

    def type_text(self):
        text_to_type = self.textbox.get("1.0", "end-1c")
        
        # Slight typing delay to mimic humanity & prevent application crashing
        for char in text_to_type:
            if not self.is_running: break
            self.keyboard_controller.type(char)
            time.sleep(random.uniform(0.01, 0.05))
            
        self.is_running = False
        self.reset_ui()

    def reset_ui(self):
        self.card.configure(border_color=BORDER_COLOR)
        self.delay_entry.configure(state="normal")
        delay_val = self.delay_var.get() if self.delay_var.get() else "0"
        self.start_btn.configure(text=f"▶ START ({delay_val}s)", fg_color=INDIGO, hover_color=INDIGO_HOVER)

if __name__ == "__main__":
    app = AutoTyperApp()
    app.mainloop()
