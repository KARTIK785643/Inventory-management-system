import customtkinter as ctk

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, api_client, on_login_success):
        super().__init__(parent, fg_color="#f1f5f9")
        self.api_client = api_client
        self.on_login_success = on_login_success

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Center White Card
        card = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=12, width=400, height=450, border_width=1, border_color="#cbd5e1")
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_propagate(False)

        card.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        card.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            card,
            text="INVENTORY MANAGEMENT",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#0284c7"
        )
        title.grid(row=0, column=0, pady=(30, 5))

        subtitle = ctk.CTkLabel(
            card,
            text="Sign in to access your stock portal",
            font=ctk.CTkFont(size=12),
            text_color="#64748b"
        )
        subtitle.grid(row=1, column=0, pady=(0, 20))

        # Username entry
        self.username_entry = ctk.CTkEntry(
            card,
            placeholder_text="Username",
            width=280,
            height=40,
            corner_radius=8,
            fg_color="#f8fafc",
            border_color="#cbd5e1",
            text_color="#0f172a"
        )
        self.username_entry.insert(0, "admin")
        self.username_entry.grid(row=2, column=0, pady=10)

        # Password entry
        self.password_entry = ctk.CTkEntry(
            card,
            placeholder_text="Password",
            show="•",
            width=280,
            height=40,
            corner_radius=8,
            fg_color="#f8fafc",
            border_color="#cbd5e1",
            text_color="#0f172a"
        )
        self.password_entry.insert(0, "admin123")
        self.password_entry.grid(row=3, column=0, pady=10)

        # Login button
        login_btn = ctk.CTkButton(
            card,
            text="Sign In",
            width=280,
            height=42,
            corner_radius=8,
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.handle_login
        )
        login_btn.grid(row=4, column=0, pady=(15, 10))

        self.error_label = ctk.CTkLabel(card, text="", text_color="#ef4444", font=ctk.CTkFont(size=12))
        self.error_label.grid(row=5, column=0, pady=5)

        hint_label = ctk.CTkLabel(card, text="Demo Login: admin / admin123", text_color="#64748b", font=ctk.CTkFont(size=11))
        hint_label.grid(row=6, column=0, pady=(0, 15))

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_label.configure(text="Please enter username and password")
            return

        success, msg, user = self.api_client.login(username, password)
        if success:
            self.error_label.configure(text="")
            self.on_login_success(user)
        else:
            self.error_label.configure(text=msg)
