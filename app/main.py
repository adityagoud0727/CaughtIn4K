# ============================================================
# CAUGHTIN4K - MAIN APPLICATION
# Localized Media Forensics & Privacy Protection Suite
# ============================================================

import os
import json
import hashlib
import threading
from pathlib import Path
from datetime import datetime

import customtkinter as ctk
from tkinter import filedialog, messagebox

# ------------------------------------------------------------
# CORE IMPORTS
# ------------------------------------------------------------

from app.core.image_analyzer import analyze_image
from app.core.sanitizer import sanitize_file

try:
    from app.core.steganography import (
        hide_message,
        extract_message
    )
    STEGO_AVAILABLE = True
except ImportError:
    STEGO_AVAILABLE = False

# ------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------

try:
    from app.database.db import (
        initialize_database,
        save_analysis,
        get_analysis_history,
        add_audit_log,
        save_stego_operation
    )
except ImportError:
    from app.database.db import (
        initialize_database,
        save_analysis,
        get_analysis_history,
        add_audit_log
    )

    def save_stego_operation(*args, **kwargs):
        pass

# ------------------------------------------------------------
# AUTHENTICATION
# ------------------------------------------------------------

from app.security.auth import authenticate_user


# ============================================================
# APPLICATION SETTINGS
# ============================================================

APP_NAME = "CaughtIn4K"
APP_VERSION = "1.0"

ctk.set_default_color_theme("blue")
ctk.set_appearance_mode("Light")


# ============================================================
# COLOR THEMES
# ============================================================

LIGHT = {
    "bg": "#F5F7FA",
    "sidebar": "#FFFFFF",
    "card": "#FFFFFF",
    "card_alt": "#F0F3F6",

    "text": "#1F2937",
    "text_secondary": "#64748B",

    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",

    "accent": "#D97706",
    "accent_hover": "#B45309",

    "success": "#15803D",
    "danger": "#DC2626",
    "warning": "#D97706",

    "border": "#D9E0E7",

    "input": "#FFFFFF",
    "input_border": "#CBD5E1",

    "nav_hover": "#EEF4FF",
    "nav_active": "#DBEAFE",

    "progress_bg": "#E2E8F0",

    "terminal": "#111827",
    "terminal_text": "#E5E7EB"
}

DARK = {
    "bg": "#111827",
    "sidebar": "#172033",
    "card": "#1F2937",
    "card_alt": "#273449",

    "text": "#F9FAFB",
    "text_secondary": "#AAB5C5",

    "primary": "#60A5FA",
    "primary_hover": "#3B82F6",

    "accent": "#F59E0B",
    "accent_hover": "#D97706",

    "success": "#4ADE80",
    "danger": "#F87171",
    "warning": "#FBBF24",

    "border": "#374151",

    "input": "#111827",
    "input_border": "#4B5563",

    "nav_hover": "#26354D",
    "nav_active": "#1E3A5F",

    "progress_bg": "#374151",

    "terminal": "#0B1120",
    "terminal_text": "#E5E7EB"
}


# ============================================================
# MAIN APPLICATION
# ============================================================

class CaughtIn4K(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("CaughtIn4K - Media Forensics Suite")
        self.geometry("1400x850")
        self.minsize(1100, 700)

        self.current_theme = "light"

        self.last_analysis = None
        self.selected_file = None
        self.current_page = "home"
        self.current_username = None

        self.nav_buttons = []

        self.setup_database()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.show_splash()

    # ========================================================
    # THEME
    # ========================================================

    def colors(self):
        if self.current_theme == "dark":
            return DARK
        return LIGHT

    def apply_theme(self):
        """
        Toggle the complete application between Light and Dark.
        """

        if self.current_theme == "light":
            self.current_theme = "dark"
            ctk.set_appearance_mode("Dark")
        else:
            self.current_theme = "light"
            ctk.set_appearance_mode("Light")

        if hasattr(self, "main_container"):
            self.refresh_current_page()

    def refresh_current_page(self):

        page = self.current_page

        if page == "home":
            self.show_home()

        elif page == "analyze":
            self.show_analyze()

        elif page == "extracted":
            self.show_extracted_data()

        elif page == "sanitize":
            self.show_sanitize()

        elif page == "pixelvault":
            self.show_pixelvault()

        elif page == "audit":
            self.show_audit()

        elif page == "reports":
            self.show_reports()

    # ========================================================
    # DATABASE
    # ========================================================

    def setup_database(self):

        try:
            initialize_database()
        except Exception as error:
            print("Database initialization error:", error)

    # ========================================================
    # SPLASH SCREEN
    # ========================================================

    def show_splash(self):

        self.clear_window()

        self.configure(fg_color="#111827")

        container = ctk.CTkFrame(
            self,
            fg_color="#111827"
        )
        container.pack(
            expand=True,
            fill="both"
        )

        logo = ctk.CTkLabel(
            container,
            text="C4K",
            font=ctk.CTkFont(
                size=72,
                weight="bold"
            ),
            text_color="#F59E0B"
        )
        logo.pack(
            pady=(180, 10)
        )

        title = ctk.CTkLabel(
            container,
            text="CaughtIn4K",
            font=ctk.CTkFont(
                size=34,
                weight="bold"
            ),
            text_color="#FFFFFF"
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            container,
            text="Media Forensics • Privacy • Steganography",
            font=ctk.CTkFont(size=15),
            text_color="#CBD5E1"
        )
        subtitle.pack(pady=10)

        progress = ctk.CTkProgressBar(
            container,
            width=300,
            mode="indeterminate"
        )
        progress.pack(pady=30)

        progress.start()

        self.after(
            2200,
            self.show_loading
        )

    # ========================================================
    # LOADING
    # ========================================================

    def show_loading(self):

        self.clear_window()

        self.configure(fg_color="#F5F7FA")

        frame = ctk.CTkFrame(
            self,
            fg_color="#F5F7FA"
        )
        frame.pack(
            expand=True,
            fill="both"
        )

        title = ctk.CTkLabel(
            frame,
            text="Preparing CaughtIn4K",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            ),
            text_color="#1F2937"
        )
        title.pack(
            pady=(250, 15)
        )

        status = ctk.CTkLabel(
            frame,
            text="Initializing forensic modules...",
            font=ctk.CTkFont(size=14),
            text_color="#64748B"
        )
        status.pack()

        progress = ctk.CTkProgressBar(
            frame,
            width=400
        )
        progress.pack(pady=25)

        progress.set(0)

        def animate(value=0):

            if value <= 1:
                progress.set(value)
                self.after(
                    20,
                    lambda: animate(value + 0.025)
                )
            else:
                self.show_login()

        animate()

    # ========================================================
    # LOGIN
    # ========================================================

    def show_login(self):

        self.clear_window()

        c = self.colors()

        self.configure(
            fg_color=c["bg"]
        )

        outer = ctk.CTkFrame(
            self,
            fg_color=c["bg"]
        )
        outer.pack(
            expand=True,
            fill="both"
        )

        card = ctk.CTkFrame(
            outer,
            width=450,
            height=520,
            corner_radius=20,
            fg_color=c["card"],
            border_width=1,
            border_color=c["border"]
        )

        card.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        logo = ctk.CTkLabel(
            card,
            text="C4K",
            font=ctk.CTkFont(
                size=46,
                weight="bold"
            ),
            text_color=c["accent"]
        )
        logo.pack(
            pady=(45, 5)
        )

        title = ctk.CTkLabel(
            card,
            text="CaughtIn4K",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            ),
            text_color=c["text"]
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            card,
            text="Local Media Forensics Suite",
            font=ctk.CTkFont(
                size=14
            ),
            text_color=c["text_secondary"]
        )
        subtitle.pack(
            pady=(5, 35)
        )

        username = ctk.CTkEntry(
            card,
            width=330,
            height=45,
            placeholder_text="Username",
            fg_color=c["input"],
            border_color=c["input_border"],
            text_color=c["text"]
        )
        username.pack(
            pady=8
        )

        password = ctk.CTkEntry(
            card,
            width=330,
            height=45,
            placeholder_text="Password",
            show="●",
            fg_color=c["input"],
            border_color=c["input_border"],
            text_color=c["text"]
        )
        password.pack(
            pady=8
        )

        message = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=c["danger"]
        )
        message.pack(
            pady=5
        )

        def login():

            user = username.get().strip()
            pwd = password.get()

            if not user or not pwd:
                message.configure(
                    text="Please enter username and password."
                )
                return

            try:

                authenticated, user_info = authenticate_user(
                    user,
                    pwd
                )

                if authenticated:

                    self.current_username = user_info["username"]

                    try:
                        add_audit_log(
                            "LOGIN",
                            "",
                            "SUCCESS"
                        )
                    except Exception:
                        pass

                    self.build_main_interface()

                else:

                    message.configure(
                        text="Invalid username or password."
                    )

            except Exception as error:

                message.configure(
                    text=f"Login error: {error}"
                )

        login_button = ctk.CTkButton(
            card,
            width=330,
            height=45,
            text="LOGIN",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            fg_color=c["primary"],
            hover_color=c["primary_hover"],
            command=login
        )

        login_button.pack(
            pady=15
        )

        def focus_password(event=None):
            password.focus_set()
            return "break"

        def submit_login(event=None):
            login()
            return "break"

        username.bind("<Return>", focus_password)
        password.bind("<Return>", submit_login)

        footer = ctk.CTkLabel(
            card,
            text="Local authentication • Your files stay on this device",
            font=ctk.CTkFont(size=11),
            text_color=c["text_secondary"]
        )

        footer.pack(
            pady=(15, 0)
        )

        username.focus()

    # ========================================================
    # MAIN INTERFACE
    # ========================================================

    def build_main_interface(self):

        self.clear_window()

        c = self.colors()

        self.configure(
            fg_color=c["bg"]
        )

        # ----------------------------------------------------
        # SIDEBAR
        # ----------------------------------------------------

        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color=c["sidebar"],
            border_width=1,
            border_color=c["border"]
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        # Logo

        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        logo_frame.pack(
            fill="x",
            pady=(25, 20),
            padx=20
        )

        logo = ctk.CTkLabel(
            logo_frame,
            text="C4K",
            font=ctk.CTkFont(
                size=34,
                weight="bold"
            ),
            text_color=c["accent"]
        )

        logo.pack(
            side="left"
        )

        logo_text = ctk.CTkLabel(
            logo_frame,
            text="CaughtIn4K",
            font=ctk.CTkFont(
                size=19,
                weight="bold"
            ),
            text_color=c["text"]
        )

        logo_text.pack(
            side="left",
            padx=8
        )

        # Navigation

        self.nav_buttons = []

        self.create_nav_button(
            "⌂   Dashboard",
            self.show_home
        )

        self.create_nav_button(
            "◉   Analyze File",
            self.show_analyze
        )

        self.create_nav_button(
            "▣   Extracted Data",
            self.show_extracted_data
        )

        self.create_nav_button(
            "✦   Sanitize",
            self.show_sanitize
        )

        self.create_nav_button(
            "◆   PixelVault",
            self.show_pixelvault
        )

        self.create_nav_button(
            "◷   Audit History",
            self.show_audit
        )

        self.create_nav_button(
            "▤   Reports",
            self.show_reports
        )

        # Bottom area

        bottom = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        bottom.pack(
            side="bottom",
            fill="x",
            padx=15,
            pady=20
        )

        # Theme toggle

        theme_frame = ctk.CTkFrame(
            bottom,
            fg_color=c["card_alt"],
            corner_radius=10
        )
        theme_frame.pack(
            fill="x",
            pady=(0, 10)
        )

        self.theme_label = ctk.CTkLabel(
            theme_frame,
            text="☀  Light Mode",
            text_color=c["text"],
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            )
        )

        self.theme_label.pack(
            side="left",
            padx=10,
            pady=10
        )

        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="",
            width=45,
            command=self.toggle_theme,
            progress_color=c["primary"],
            button_color=c["primary"]
        )

        self.theme_switch.pack(
            side="right",
            padx=8
        )

        if self.current_theme == "dark":
            self.theme_switch.select()

        # User

        user_label = ctk.CTkLabel(
            bottom,
            text=f"●  {self.current_username}",
            text_color=c["text_secondary"],
            anchor="w"
        )
        user_label.pack(
            fill="x",
            pady=5
        )

        logout = ctk.CTkButton(
            bottom,
            text="Logout",
            height=38,
            fg_color="transparent",
            hover_color=c["nav_hover"],
            border_width=1,
            border_color=c["border"],
            text_color=c["text"],
            command=self.logout
        )

        logout.pack(
            fill="x"
        )

        # ----------------------------------------------------
        # MAIN CONTENT
        # ----------------------------------------------------

        self.main_container = ctk.CTkFrame(
            self,
            fg_color=c["bg"],
            corner_radius=0
        )

        self.main_container.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.show_home()

    # ========================================================
    # NAVIGATION BUTTON
    # ========================================================

    def create_nav_button(
        self,
        text,
        command
    ):

        c = self.colors()

        button = ctk.CTkButton(
            self.sidebar,
            text=text,
            height=45,
            corner_radius=9,
            anchor="w",
            fg_color="transparent",
            hover_color=c["nav_hover"],
            text_color=c["text"],
            font=ctk.CTkFont(size=13),
            command=command
        )

        button.pack(
            fill="x",
            padx=12,
            pady=3
        )

        self.nav_buttons.append(button)

    # ========================================================
    # THEME TOGGLE
    # ========================================================

    def toggle_theme(self):

        self.apply_theme()

    # ========================================================
    # CLEAR MAIN CONTENT
    # ========================================================

    def clear_main(self):

        if hasattr(self, "main_container"):

            for widget in self.main_container.winfo_children():
                widget.destroy()

    # ========================================================
    # CLEAR WHOLE WINDOW
    # ========================================================

    def clear_window(self):

        for widget in self.winfo_children():
            widget.destroy()

    # ========================================================
    # PAGE HEADER
    # ========================================================

    def page_header(
        self,
        title,
        subtitle=""
    ):

        c = self.colors()

        frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )

        frame.pack(
            fill="x",
            padx=35,
            pady=(30, 15)
        )

        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            ),
            text_color=c["text"],
            anchor="w"
        )

        title_label.pack(
            anchor="w"
        )

        if subtitle:

            sub = ctk.CTkLabel(
                frame,
                text=subtitle,
                font=ctk.CTkFont(
                    size=13
                ),
                text_color=c["text_secondary"],
                anchor="w"
            )

            sub.pack(
                anchor="w",
                pady=(5, 0)
            )

        return frame

    # ========================================================
    # HOME
    # ========================================================

    def show_home(self):

        self.current_page = "home"

        self.clear_main()

        c = self.colors()

        self.page_header(
            "Security Dashboard",
            "Analyze, inspect and protect your media files."
        )

        # Cards

        cards = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )

        cards.pack(
            fill="x",
            padx=35,
            pady=10
        )

        cards.grid_columnconfigure(
            (0, 1, 2),
            weight=1
        )

        self.dashboard_card(
            cards,
            0,
            "◉",
            "Media Analysis",
            "Inspect metadata and calculate privacy risk.",
            c["primary"],
            self.show_analyze
        )

        self.dashboard_card(
            cards,
            1,
            "✦",
            "Privacy Sanitizer",
            "Create a cleaned copy of supported images.",
            c["success"],
            self.show_sanitize
        )

        self.dashboard_card(
            cards,
            2,
            "◆",
            "PixelVault",
            "Encrypt and hide secret messages in PNG files.",
            c["accent"],
            self.show_pixelvault
        )

        # Recent analysis

        section = ctk.CTkFrame(
            self.main_container,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        section.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=20
        )

        ctk.CTkLabel(
            section,
            text="Recent Analysis",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            text_color=c["text"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 5)
        )

        try:

            history = get_analysis_history()

            if history:

                for row in history[:5]:

                    self.history_row(
                        section,
                        row
                    )

            else:

                ctk.CTkLabel(
                    section,
                    text="No analysis records yet.",
                    text_color=c["text_secondary"]
                ).pack(
                    pady=40
                )

        except Exception as error:

            ctk.CTkLabel(
                section,
                text=f"Unable to load history: {error}",
                text_color=c["danger"]
            ).pack(
                pady=40
            )

    # ========================================================
    # DASHBOARD CARD
    # ========================================================

    def dashboard_card(
        self,
        parent,
        column,
        icon,
        title,
        description,
        color,
        command
    ):

        c = self.colors()

        frame = ctk.CTkFrame(
            parent,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        frame.grid(
            row=0,
            column=column,
            padx=8,
            sticky="nsew"
        )

        ctk.CTkLabel(
            frame,
            text=icon,
            font=ctk.CTkFont(
                size=32
            ),
            text_color=color
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 5)
        )

        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            text_color=c["text"]
        ).pack(
            anchor="w",
            padx=20
        )

        ctk.CTkLabel(
            frame,
            text=description,
            wraplength=280,
            justify="left",
            font=ctk.CTkFont(size=12),
            text_color=c["text_secondary"]
        ).pack(
            anchor="w",
            padx=20,
            pady=8
        )

        ctk.CTkButton(
            frame,
            text="Open",
            height=35,
            fg_color=color,
            hover_color=color,
            command=command
        ).pack(
            fill="x",
            padx=20,
            pady=(5, 20)
        )

    # ========================================================
    # HISTORY ROW
    # ========================================================

    def history_row(
        self,
        parent,
        row
    ):

        c = self.colors()

        frame = ctk.CTkFrame(
            parent,
            fg_color=c["card_alt"],
            corner_radius=8
        )

        frame.pack(
            fill="x",
            padx=20,
            pady=5
        )

        values = list(row)

        filename = str(values[1]) if len(values) > 1 else "Unknown"
        risk = values[5] if len(values) > 5 else 0
        created = values[6] if len(values) > 6 else ""

        ctk.CTkLabel(
            frame,
            text=filename,
            text_color=c["text"],
            anchor="w"
        ).pack(
            side="left",
            padx=15,
            pady=10
        )

        ctk.CTkLabel(
            frame,
            text=f"Risk: {risk}/100",
            text_color=self.risk_color(risk),
            font=ctk.CTkFont(
                weight="bold"
            )
        ).pack(
            side="right",
            padx=15
        )

        ctk.CTkLabel(
            frame,
            text=str(created),
            text_color=c["text_secondary"]
        ).pack(
            side="right",
            padx=15
        )

    # ========================================================
    # ANALYZE PAGE
    # ========================================================

    def show_analyze(self):

        self.current_page = "analyze"

        self.clear_main()

        c = self.colors()

        self.page_header(
            "Media Analysis",
            "Inspect a supported file and identify privacy-sensitive information."
        )

        body = ctk.CTkFrame(
            self.main_container,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        body.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=10
        )

        self.selected_file_label = ctk.CTkLabel(
            body,
            text="No file selected",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            text_color=c["text"]
        )

        self.selected_file_label.pack(
            pady=(60, 10)
        )

        ctk.CTkLabel(
            body,
            text="Supported image formats: JPG, JPEG and PNG",
            text_color=c["text_secondary"]
        ).pack()

        ctk.CTkButton(
            body,
            text="Select File",
            width=220,
            height=45,
            fg_color=c["primary"],
            hover_color=c["primary_hover"],
            command=self.select_file
        ).pack(
            pady=25
        )

        self.analysis_status = ctk.CTkLabel(
            body,
            text="",
            text_color=c["text_secondary"]
        )

        self.analysis_status.pack(
            pady=5
        )

        self.analyze_button = ctk.CTkButton(
            body,
            text="RUN FORENSIC ANALYSIS",
            width=280,
            height=48,
            fg_color=c["accent"],
            hover_color=c["accent_hover"],
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            state="disabled",
            command=self.run_analysis
        )

        self.analyze_button.pack(
            pady=15
        )

    # ========================================================
    # SELECT FILE
    # ========================================================

    def select_file(self):

        file_path = filedialog.askopenfilename(
            title="Select file",
            filetypes=[
                (
                    "Supported Images",
                    "*.jpg *.jpeg *.png"
                ),
                (
                    "JPEG",
                    "*.jpg *.jpeg"
                ),
                (
                    "PNG",
                    "*.png"
                )
            ]
        )

        if not file_path:
            return

        self.selected_file = file_path

        if hasattr(
            self,
            "selected_file_label"
        ):

            self.selected_file_label.configure(
                text=Path(file_path).name
            )

        if hasattr(
            self,
            "analyze_button"
        ):

            self.analyze_button.configure(
                state="normal"
            )

    # ========================================================
    # RUN ANALYSIS
    # ========================================================

    def run_analysis(self):

        if not self.selected_file:
            return

        self.analysis_status.configure(
            text="Analyzing file..."
        )

        self.analyze_button.configure(
            state="disabled"
        )

        thread = threading.Thread(
            target=self.analysis_worker,
            daemon=True
        )

        thread.start()

    def analysis_worker(self):

        try:

            result = analyze_image(
                self.selected_file
            )

            self.after(
                0,
                lambda: self.analysis_complete(
                    result
                )
            )

        except Exception as error:

            self.after(
                0,
                lambda: self.analysis_failed(
                    error
                )
            )

    def analysis_complete(
        self,
        result
    ):

        self.last_analysis = result

        try:

            file_data = result.get(
                "file",
                {}
            )

            filename = file_data.get(
                "name",
                Path(self.selected_file).name
            )

            file_type = file_data.get(
                "type",
                "Unknown"
            )

            sha256 = file_data.get(
                "sha256",
                ""
            )

            risk = result.get(
                "risk",
                {}
            )

            score = risk.get(
                "score",
                0
            )

            findings = result.get(
                "findings",
                []
            )

            try:

                save_analysis(
                    filename,
                    file_type,
                    sha256,
                    score,
                    findings
                )

            except Exception as db_error:

                print(
                    "Could not save analysis:",
                    db_error
                )

            try:

                add_audit_log(
                    "ANALYZE",
                    filename,
                    "SUCCESS"
                )

            except Exception:
                pass

        except Exception as error:

            print(
                "Database processing error:",
                error
            )

        self.analysis_status.configure(
            text="Analysis completed successfully."
        )

        self.analyze_button.configure(
            state="normal"
        )

        self.display_analysis(
            result
        )

    def analysis_failed(
        self,
        error
    ):

        self.analysis_status.configure(
            text=f"Analysis error: {error}",
            text_color=self.colors()["danger"]
        )

        self.analyze_button.configure(
            state="normal"
        )

        messagebox.showerror(
            "Analysis Error",
            str(error)
        )

    # ========================================================
    # DISPLAY ANALYSIS
    # ========================================================

    def display_analysis(
        self,
        result
    ):

        self.current_page = "analyze"

        self.clear_main()

        c = self.colors()

        file_data = result.get(
            "file",
            {}
        )

        metadata = result.get(
            "metadata",
            {}
        )

        findings = result.get(
            "findings",
            []
        )

        risk = result.get(
            "risk",
            {}
        )

        file_name = file_data.get(
            "name",
            "Unknown"
        )

        file_type = file_data.get(
            "type",
            "Unknown"
        )

        file_size = file_data.get(
            "size",
            0
        )

        width = file_data.get(
            "width",
            "Unknown"
        )

        height = file_data.get(
            "height",
            "Unknown"
        )

        sha256 = file_data.get(
            "sha256",
            "Unknown"
        )

        risk_score = risk.get(
            "score",
            0
        )

        risk_level = risk.get(
            "level",
            "MINIMAL"
        )

        self.page_header(
            "Analysis Results",
            f"Detailed forensic inspection of {file_name}"
        )

        # ----------------------------------------------------
        # TOP INFORMATION
        # ----------------------------------------------------

        top = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )

        top.pack(
            fill="x",
            padx=35,
            pady=5
        )

        top.grid_columnconfigure(
            0,
            weight=3
        )

        top.grid_columnconfigure(
            1,
            weight=1
        )

        # File information

        info = ctk.CTkFrame(
            top,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        info.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 10)
        )

        ctk.CTkLabel(
            info,
            text="File Information",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            text_color=c["text"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 10)
        )

        self.info_row(
            info,
            "File Name",
            file_name
        )

        self.info_row(
            info,
            "File Type",
            file_type
        )

        self.info_row(
            info,
            "File Size",
            f"{file_size:,} bytes"
        )

        if width != "Unknown" and height != "Unknown":

            self.info_row(
                info,
                "Resolution",
                f"{width} × {height}"
            )

        self.info_row(
            info,
            "SHA-256",
            sha256
        )

        # Risk card

        risk_card = ctk.CTkFrame(
            top,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        risk_card.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        ctk.CTkLabel(
            risk_card,
            text="Privacy Risk",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            text_color=c["text"]
        ).pack(
            pady=(20, 5)
        )

        ctk.CTkLabel(
            risk_card,
            text=str(risk_score),
            font=ctk.CTkFont(
                size=52,
                weight="bold"
            ),
            text_color=self.risk_color(
                risk_score
            )
        ).pack()

        ctk.CTkLabel(
            risk_card,
            text="/ 100",
            text_color=c["text_secondary"]
        ).pack()

        ctk.CTkLabel(
            risk_card,
            text=risk_level,
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            ),
            text_color=self.risk_color(
                risk_score
            )
        ).pack(
            pady=10
        )

        # ----------------------------------------------------
        # METADATA + FINDINGS
        # ----------------------------------------------------

        lower = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )

        lower.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=15
        )

        lower.grid_columnconfigure(
            0,
            weight=1
        )

        lower.grid_columnconfigure(
            1,
            weight=1
        )

        # Metadata

        metadata_card = ctk.CTkFrame(
            lower,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        metadata_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8)
        )

        ctk.CTkLabel(
            metadata_card,
            text="Detected Metadata",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            text_color=c["text"]
        ).pack(
            anchor="w",
            padx=20,
            pady=15
        )

        scroll = ctk.CTkScrollableFrame(
            metadata_card,
            fg_color="transparent"
        )

        scroll.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        if metadata:

            for key, value in metadata.items():

                self.metadata_row(
                    scroll,
                    key,
                    value
                )

        else:

            ctk.CTkLabel(
                scroll,
                text="No metadata detected.",
                text_color=c["text_secondary"]
            ).pack(
                pady=30
            )

        # Findings

        findings_card = ctk.CTkFrame(
            lower,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        findings_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0)
        )

        ctk.CTkLabel(
            findings_card,
            text="Privacy Findings",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            text_color=c["text"]
        ).pack(
            anchor="w",
            padx=20,
            pady=15
        )

        finding_scroll = ctk.CTkScrollableFrame(
            findings_card,
            fg_color="transparent"
        )

        finding_scroll.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        if findings:

            for finding in findings:

                self.finding_row(
                    finding_scroll,
                    finding
                )

        else:

            ctk.CTkLabel(
                finding_scroll,
                text="✓ No privacy-sensitive metadata detected.",
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                ),
                text_color=c["success"]
            ).pack(
                pady=30
            )

        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        buttons = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )

        buttons.pack(
            fill="x",
            padx=35,
            pady=(0, 20)
        )

        ctk.CTkButton(
            buttons,
            text="View Extracted Data",
            height=42,
            fg_color=c["primary"],
            hover_color=c["primary_hover"],
            command=self.show_extracted_data
        ).pack(
            side="left",
            padx=(0, 10)
        )

        ctk.CTkButton(
            buttons,
            text="Sanitize File",
            height=42,
            fg_color=c["success"],
            hover_color=c["success"],
            command=self.show_sanitize
        ).pack(
            side="left"
        )

    # ========================================================
    # INFO ROW
    # ========================================================

    def info_row(
        self,
        parent,
        key,
        value
    ):

        c = self.colors()

        row = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            padx=15,
            pady=4
        )

        ctk.CTkLabel(
            row,
            text=key,
            width=110,
            anchor="w",
            text_color=c["text_secondary"]
        ).pack(
            side="left"
        )

        ctk.CTkLabel(
            row,
            text=str(value),
            anchor="w",
            justify="left",
            wraplength=500,
            text_color=c["text"]
        ).pack(
            side="left",
            fill="x",
            expand=True
        )

    # ========================================================
    # METADATA ROW
    # ========================================================

    def metadata_row(
        self,
        parent,
        key,
        value
    ):

        c = self.colors()

        frame = ctk.CTkFrame(
            parent,
            fg_color=c["card_alt"],
            corner_radius=8
        )

        frame.pack(
            fill="x",
            pady=4
        )

        ctk.CTkLabel(
            frame,
            text=str(key),
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            text_color=c["text"],
            anchor="w"
        ).pack(
            fill="x",
            padx=12,
            pady=(8, 0)
        )

        ctk.CTkLabel(
            frame,
            text=str(value),
            text_color=c["text_secondary"],
            anchor="w",
            justify="left",
            wraplength=480
        ).pack(
            fill="x",
            padx=12,
            pady=(2, 8)
        )

    # ========================================================
    # FINDING ROW
    # ========================================================

    def finding_row(
        self,
        parent,
        finding
    ):

        c = self.colors()

        if isinstance(
            finding,
            dict
        ):

            category = finding.get(
                "category",
                "Privacy"
            )

            field = finding.get(
                "field",
                finding.get(
                    "field_name",
                    "Unknown"
                )
            )

            value = finding.get(
                "value",
                finding.get(
                    "field_value",
                    ""
                )
            )

            level = finding.get(
                "risk",
                finding.get(
                    "risk_level",
                    "LOW"
                )
            )

        else:

            category = "Privacy"
            field = str(finding)
            value = ""
            level = "LOW"

        if str(level).upper() == "HIGH":
            level_color = c["danger"]

        elif str(level).upper() == "MEDIUM":
            level_color = c["warning"]

        else:
            level_color = c["primary"]

        frame = ctk.CTkFrame(
            parent,
            fg_color=c["card_alt"],
            corner_radius=8,
            border_width=1,
            border_color=c["border"]
        )

        frame.pack(
            fill="x",
            pady=5
        )

        header = ctk.CTkFrame(
            frame,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=12,
            pady=(8, 2)
        )

        ctk.CTkLabel(
            header,
            text=str(category),
            text_color=c["text"],
            font=ctk.CTkFont(
                weight="bold"
            )
        ).pack(
            side="left"
        )

        ctk.CTkLabel(
            header,
            text=str(level).upper(),
            text_color=level_color,
            font=ctk.CTkFont(
                weight="bold"
            )
        ).pack(
            side="right"
        )

        ctk.CTkLabel(
            frame,
            text=f"{field}: {value}",
            text_color=c["text_secondary"],
            anchor="w",
            justify="left",
            wraplength=480
        ).pack(
            fill="x",
            padx=12,
            pady=(2, 10)
        )

    # ========================================================
    # EXTRACTED DATA
    # ========================================================

    def show_extracted_data(self):

        self.current_page = "extracted"

        self.clear_main()

        c = self.colors()

        self.page_header(
            "Extracted Data",
            "A complete view of the information detected inside the selected file."
        )

        if not self.last_analysis:

            empty = ctk.CTkFrame(
                self.main_container,
                fg_color=c["card"],
                corner_radius=14
            )

            empty.pack(
                fill="both",
                expand=True,
                padx=35,
                pady=15
            )

            ctk.CTkLabel(
                empty,
                text="No analysis available",
                font=ctk.CTkFont(
                    size=22,
                    weight="bold"
                ),
                text_color=c["text"]
            ).pack(
                pady=(180, 10)
            )

            ctk.CTkLabel(
                empty,
                text="Analyze a file first to view its extracted data.",
                text_color=c["text_secondary"]
            ).pack()

            ctk.CTkButton(
                empty,
                text="Analyze File",
                command=self.show_analyze
            ).pack(
                pady=20
            )

            return

        result = self.last_analysis

        file_data = result.get(
            "file",
            {}
        )

        metadata = result.get(
            "metadata",
            {}
        )

        findings = result.get(
            "findings",
            []
        )

        risk = result.get(
            "risk",
            {}
        )

        outer = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color="transparent"
        )

        outer.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=5
        )

        # File section

        file_card = ctk.CTkFrame(
            outer,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        file_card.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ctk.CTkLabel(
            file_card,
            text="File Details",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            text_color=c["text"]
        ).pack(
            anchor="w",
            padx=20,
            pady=15
        )

        for key, value in [
            ("File Name", file_data.get("name", "Unknown")),
            ("File Type", file_data.get("type", "Unknown")),
            ("File Size", f'{file_data.get("size", 0):,} bytes'),
            (
                "Resolution",
                f'{file_data.get("width", "Unknown")} × '
                f'{file_data.get("height", "Unknown")}'
            ),
            ("SHA-256", file_data.get("sha256", "Unknown")),
            ("Risk Score", f'{risk.get("score", 0)}/100'),
            ("Risk Level", risk.get("level", "MINIMAL"))
        ]:

            self.info_row(
                file_card,
                key,
                value
            )

        # Metadata

        metadata_card = ctk.CTkFrame(
            outer,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        metadata_card.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ctk.CTkLabel(
            metadata_card,
            text=f"Metadata ({len(metadata)})",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            text_color=c["text"]
        ).pack(
            anchor="w",
            padx=20,
            pady=15
        )

        for key, value in metadata.items():

            self.metadata_row(
                metadata_card,
                key,
                value
            )

        if not metadata:

            ctk.CTkLabel(
                metadata_card,
                text="No metadata fields detected.",
                text_color=c["text_secondary"]
            ).pack(
                pady=20
            )

        # Findings

        finding_card = ctk.CTkFrame(
            outer,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        finding_card.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ctk.CTkLabel(
            finding_card,
            text=f"Privacy Findings ({len(findings)})",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            text_color=c["text"]
        ).pack(
            anchor="w",
            padx=20,
            pady=15
        )

        for finding in findings:

            self.finding_row(
                finding_card,
                finding
            )

        if not findings:

            ctk.CTkLabel(
                finding_card,
                text="✓ No privacy-sensitive findings detected.",
                text_color=c["success"],
                font=ctk.CTkFont(
                    weight="bold"
                )
            ).pack(
                pady=20
            )

    # ========================================================
    # SANITIZER PAGE
    # ========================================================

    def show_sanitize(self):

        self.current_page = "sanitize"

        self.clear_main()

        c = self.colors()

        self.page_header(
            "Privacy Sanitizer",
            "Create a cleaned copy of a supported image without privacy-sensitive metadata."
        )

        card = ctk.CTkFrame(
            self.main_container,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        card.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=10
        )

        ctk.CTkLabel(
            card,
            text="Remove Metadata",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            ),
            text_color=c["text"]
        ).pack(
            pady=(80, 10)
        )

        ctk.CTkLabel(
            card,
            text=(
                "The sanitizer creates a new copy of the image "
                "without the original metadata."
            ),
            text_color=c["text_secondary"]
        ).pack()

        self.sanitize_file_label = ctk.CTkLabel(
            card,
            text="No file selected",
            text_color=c["text"]
        )

        self.sanitize_file_label.pack(
            pady=25
        )

        ctk.CTkButton(
            card,
            text="Select Image",
            width=220,
            height=42,
            command=self.select_sanitize_file,
            fg_color=c["primary"],
            hover_color=c["primary_hover"]
        ).pack(
            pady=10
        )

        self.sanitize_button = ctk.CTkButton(
            card,
            text="SANITIZE IMAGE",
            width=220,
            height=42,
            command=self.perform_sanitize,
            fg_color=c["success"],
            hover_color=c["success"],
            state="disabled"
        )

        self.sanitize_button.pack(
            pady=10
        )

        self.sanitize_status = ctk.CTkLabel(
            card,
            text="",
            text_color=c["text_secondary"]
        )

        self.sanitize_status.pack(
            pady=20
        )

    def select_sanitize_file(self):

        file_path = filedialog.askopenfilename(
            title="Select image to sanitize",
            filetypes=[
                (
                    "Images",
                    "*.jpg *.jpeg *.png"
                )
            ]
        )

        if not file_path:
            return

        self.sanitize_selected_file = file_path

        self.sanitize_file_label.configure(
            text=Path(file_path).name
        )

        self.sanitize_button.configure(
            state="normal"
        )

    def perform_sanitize(self):

        if not hasattr(
            self,
            "sanitize_selected_file"
        ):
            return

        try:

            cleaned = sanitize_file(
                self.sanitize_selected_file
            )

            filename = Path(
                self.sanitize_selected_file
            ).name

            try:

                add_audit_log(
                    "SANITIZE",
                    filename,
                    "SUCCESS"
                )

            except Exception:
                pass

            self.sanitize_status.configure(
                text=f"Cleaned file created:\n{cleaned}",
                text_color=self.colors()["success"]
            )

            messagebox.showinfo(
                "Sanitization Complete",
                f"Cleaned file created:\n\n{cleaned}"
            )

        except Exception as error:

            self.sanitize_status.configure(
                text=f"Sanitization failed: {error}",
                text_color=self.colors()["danger"]
            )

            messagebox.showerror(
                "Sanitization Error",
                str(error)
            )

    # ========================================================
    # PIXELVAULT
    # ========================================================

    def show_pixelvault(self):

        self.current_page = "pixelvault"

        self.clear_main()

        c = self.colors()

        self.page_header(
            "PixelVault",
            "Cryptographic steganography for hiding encrypted messages inside PNG images."
        )

        if not STEGO_AVAILABLE:

            ctk.CTkLabel(
                self.main_container,
                text="PixelVault module is unavailable.",
                text_color=c["danger"]
            ).pack(
                pady=100
            )

            return

        container = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color="transparent"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=5
        )

        # ----------------------------------------------------
        # HIDE
        # ----------------------------------------------------

        hide_card = ctk.CTkFrame(
            container,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        hide_card.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ctk.CTkLabel(
            hide_card,
            text="Hide Secret Message",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            text_color=c["text"]
        ).pack(
            anchor="w",
            padx=20,
            pady=15
        )

        self.stego_image_label = ctk.CTkLabel(
            hide_card,
            text="No PNG selected",
            text_color=c["text_secondary"]
        )

        self.stego_image_label.pack(
            anchor="w",
            padx=20,
            pady=5
        )

        ctk.CTkButton(
            hide_card,
            text="Select PNG",
            command=self.select_stego_image
        ).pack(
            anchor="w",
            padx=20,
            pady=8
        )

        self.secret_box = ctk.CTkTextbox(
            hide_card,
            height=130
        )

        self.secret_box.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.secret_box.insert(
            "1.0",
            "Enter secret message..."
        )

        self.stego_password = ctk.CTkEntry(
            hide_card,
            placeholder_text="Password",
            show="●"
        )

        self.stego_password.pack(
            fill="x",
            padx=20,
            pady=8
        )

        ctk.CTkButton(
            hide_card,
            text="ENCRYPT & HIDE MESSAGE",
            height=42,
            fg_color=c["accent"],
            hover_color=c["accent_hover"],
            command=self.hide_secret
        ).pack(
            fill="x",
            padx=20,
            pady=(5, 20)
        )

        # ----------------------------------------------------
        # EXTRACT
        # ----------------------------------------------------

        extract_card = ctk.CTkFrame(
            container,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        extract_card.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ctk.CTkLabel(
            extract_card,
            text="Extract Secret Message",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            text_color=c["text"]
        ).pack(
            anchor="w",
            padx=20,
            pady=15
        )

        self.extract_image_label = ctk.CTkLabel(
            extract_card,
            text="No PNG selected",
            text_color=c["text_secondary"]
        )

        self.extract_image_label.pack(
            anchor="w",
            padx=20,
            pady=5
        )

        ctk.CTkButton(
            extract_card,
            text="Select PNG",
            command=self.select_extract_image
        ).pack(
            anchor="w",
            padx=20,
            pady=8
        )

        self.extract_password = ctk.CTkEntry(
            extract_card,
            placeholder_text="Password",
            show="●"
        )

        self.extract_password.pack(
            fill="x",
            padx=20,
            pady=8
        )

        ctk.CTkButton(
            extract_card,
            text="EXTRACT MESSAGE",
            height=42,
            fg_color=c["primary"],
            hover_color=c["primary_hover"],
            command=self.extract_secret
        ).pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.extracted_message = ctk.CTkTextbox(
            extract_card,
            height=140
        )

        self.extracted_message.pack(
            fill="x",
            padx=20,
            pady=(5, 20)
        )

        self.extracted_message.configure(
            state="disabled"
        )

    # ========================================================
    # STEGO SELECT IMAGE
    # ========================================================

    def select_stego_image(self):

        path = filedialog.askopenfilename(
            title="Select PNG",
            filetypes=[
                ("PNG", "*.png")
            ]
        )

        if path:

            self.stego_input = path

            self.stego_image_label.configure(
                text=Path(path).name
            )

    def select_extract_image(self):

        path = filedialog.askopenfilename(
            title="Select PNG",
            filetypes=[
                ("PNG", "*.png")
            ]
        )

        if path:

            self.extract_input = path

            self.extract_image_label.configure(
                text=Path(path).name
            )

    # ========================================================
    # HIDE SECRET
    # ========================================================

    def hide_secret(self):

        if not hasattr(
            self,
            "stego_input"
        ):

            messagebox.showwarning(
                "Select Image",
                "Please select a PNG image first."
            )

            return

        message = self.secret_box.get(
            "1.0",
            "end"
        ).strip()

        password = self.stego_password.get()

        if not message:

            messagebox.showwarning(
                "Message Required",
                "Enter a secret message."
            )

            return

        if not password:

            messagebox.showwarning(
                "Password Required",
                "Enter a password."
            )

            return

        output = filedialog.asksaveasfilename(
            title="Save stego image",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png")
            ]
        )

        if not output:
            return

        try:

            hide_message(
                self.stego_input,
                output,
                message,
                password
            )

            file_hash = self.calculate_hash(
                output
            )

            save_stego_operation(
                Path(output).name,
                "HIDE",
                file_hash
            )

            try:

                add_audit_log(
                    "PIXELVAULT_HIDE",
                    Path(output).name,
                    "SUCCESS"
                )

            except Exception:
                pass

            messagebox.showinfo(
                "PixelVault",
                f"Encrypted message hidden successfully.\n\n{output}"
            )

        except Exception as error:

            messagebox.showerror(
                "PixelVault Error",
                str(error)
            )

    # ========================================================
    # EXTRACT SECRET
    # ========================================================

    def extract_secret(self):

        if not hasattr(
            self,
            "extract_input"
        ):

            messagebox.showwarning(
                "Select Image",
                "Please select a PNG image first."
            )

            return

        password = self.extract_password.get()

        if not password:

            messagebox.showwarning(
                "Password Required",
                "Enter the password."
            )

            return

        try:

            message = extract_message(
                self.extract_input,
                password
            )

            self.extracted_message.configure(
                state="normal"
            )

            self.extracted_message.delete(
                "1.0",
                "end"
            )

            self.extracted_message.insert(
                "1.0",
                message
            )

            self.extracted_message.configure(
                state="disabled"
            )

            file_hash = self.calculate_hash(
                self.extract_input
            )

            save_stego_operation(
                Path(self.extract_input).name,
                "EXTRACT",
                file_hash
            )

            try:

                add_audit_log(
                    "PIXELVAULT_EXTRACT",
                    Path(self.extract_input).name,
                    "SUCCESS"
                )

            except Exception:
                pass

        except Exception as error:

            messagebox.showerror(
                "Extraction Error",
                str(error)
            )

    # ========================================================
    # HASH
    # ========================================================

    def calculate_hash(
        self,
        file_path
    ):

        sha256 = hashlib.sha256()

        with open(
            file_path,
            "rb"
        ) as file:

            while True:

                block = file.read(
                    1024 * 1024
                )

                if not block:
                    break

                sha256.update(block)

        return sha256.hexdigest()

    # ========================================================
    # AUDIT HISTORY
    # ========================================================

    def show_audit(self):

        self.current_page = "audit"

        self.clear_main()

        c = self.colors()

        self.page_header(
            "Audit History",
            "Local activity records generated by CaughtIn4K."
        )

        card = ctk.CTkFrame(
            self.main_container,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        card.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=10
        )

        try:

            from app.database.db import get_connection

            connection = get_connection()

            cursor = connection.execute(
                """
                SELECT action, filename, status, created_at
                FROM audit_logs
                ORDER BY id DESC
                """
            )

            rows = cursor.fetchall()

            connection.close()

            if not rows:

                ctk.CTkLabel(
                    card,
                    text="No audit records yet.",
                    text_color=c["text_secondary"]
                ).pack(
                    pady=100
                )

                return

            table = ctk.CTkScrollableFrame(
                card,
                fg_color="transparent"
            )

            table.pack(
                fill="both",
                expand=True,
                padx=15,
                pady=15
            )

            for row in rows:

                action = row[0]
                filename = row[1]
                status = row[2]
                created = row[3]

                frame = ctk.CTkFrame(
                    table,
                    fg_color=c["card_alt"],
                    corner_radius=8
                )

                frame.pack(
                    fill="x",
                    pady=4
                )

                ctk.CTkLabel(
                    frame,
                    text=action,
                    width=150,
                    anchor="w",
                    text_color=c["primary"],
                    font=ctk.CTkFont(
                        weight="bold"
                    )
                ).pack(
                    side="left",
                    padx=12,
                    pady=10
                )

                ctk.CTkLabel(
                    frame,
                    text=filename or "-",
                    anchor="w",
                    text_color=c["text"]
                ).pack(
                    side="left",
                    fill="x",
                    expand=True
                )

                ctk.CTkLabel(
                    frame,
                    text=status,
                    text_color=c["success"]
                ).pack(
                    side="right",
                    padx=12
                )

                ctk.CTkLabel(
                    frame,
                    text=str(created),
                    text_color=c["text_secondary"]
                ).pack(
                    side="right",
                    padx=12
                )

        except Exception as error:

            ctk.CTkLabel(
                card,
                text=f"Unable to load audit history:\n{error}",
                text_color=c["danger"]
            ).pack(
                pady=100
            )

    # ========================================================
    # REPORTS
    # ========================================================

    def show_reports(self):

        self.current_page = "reports"

        self.clear_main()

        c = self.colors()

        self.page_header(
            "Reports",
            "Generate a report from the latest forensic analysis."
        )

        card = ctk.CTkFrame(
            self.main_container,
            fg_color=c["card"],
            corner_radius=14,
            border_width=1,
            border_color=c["border"]
        )

        card.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=10
        )

        if not self.last_analysis:

            ctk.CTkLabel(
                card,
                text="No analysis available.",
                font=ctk.CTkFont(
                    size=22,
                    weight="bold"
                ),
                text_color=c["text"]
            ).pack(
                pady=(180, 10)
            )

            ctk.CTkLabel(
                card,
                text="Analyze a file before generating a report.",
                text_color=c["text_secondary"]
            ).pack()

            ctk.CTkButton(
                card,
                text="Analyze File",
                command=self.show_analyze
            ).pack(
                pady=20
            )

            return

        ctk.CTkLabel(
            card,
            text="Generate Forensic Report",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            ),
            text_color=c["text"]
        ).pack(
            pady=(90, 10)
        )

        ctk.CTkLabel(
            card,
            text=(
                "The report contains file information, "
                "SHA-256 hash, metadata, findings and risk score."
            ),
            text_color=c["text_secondary"]
        ).pack()

        ctk.CTkButton(
            card,
            text="EXPORT JSON REPORT",
            width=250,
            height=45,
            fg_color=c["primary"],
            hover_color=c["primary_hover"],
            command=self.generate_json_report
        ).pack(
            pady=30
        )

    # ========================================================
    # GENERATE JSON REPORT
    # ========================================================

    def generate_json_report(self):

        if not self.last_analysis:
            return

        c = self.colors()

        reports_dir = Path(__file__).resolve().parents[1] / "reports"

        reports_dir.mkdir(
            exist_ok=True
        )

        result = self.last_analysis

        file_data = result.get(
            "file",
            {}
        )

        filename = file_data.get(
            "name",
            "analysis"
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        output = reports_dir / (
            f"{Path(filename).stem}_report_{timestamp}.json"
        )

        report = {
            "application": APP_NAME,
            "version": APP_VERSION,
            "generated_at": datetime.now().isoformat(),
            "file": result.get(
                "file",
                {}
            ),
            "metadata": result.get(
                "metadata",
                {}
            ),
            "findings": result.get(
                "findings",
                []
            ),
            "risk": result.get(
                "risk",
                {}
            )
        }

        try:

            with open(
                output,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    report,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            try:

                add_audit_log(
                    "GENERATE_REPORT",
                    filename,
                    "SUCCESS"
                )

            except Exception:
                pass

            messagebox.showinfo(
                "Report Generated",
                f"Report saved successfully:\n\n{output}"
            )

        except Exception as error:

            messagebox.showerror(
                "Report Error",
                str(error)
            )

    # ========================================================
    # RISK COLOR
    # ========================================================

    def risk_color(
        self,
        score
    ):

        c = self.colors()

        try:
            score = int(score)
        except Exception:
            score = 0

        if score >= 70:
            return c["danger"]

        if score >= 40:
            return c["warning"]

        if score > 0:
            return c["primary"]

        return c["success"]

    # ========================================================
    # LOGOUT
    # ========================================================

    def logout(self):

        try:

            add_audit_log(
                "LOGOUT",
                "",
                "SUCCESS"
            )

        except Exception:
            pass

        self.current_username = None
        self.last_analysis = None
        self.selected_file = None

        self.show_login()

    # ========================================================
    # CLOSE APPLICATION
    # ========================================================

    def on_close(self):

        try:

            if self.current_username:

                add_audit_log(
                    "APPLICATION_EXIT",
                    "",
                    "SUCCESS"
                )

        except Exception:
            pass

        self.destroy()


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    app = CaughtIn4K()

    app.mainloop()