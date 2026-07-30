import customtkinter as ctk
from gui.api_client import APIClient
from gui.views.login_view import LoginView
from gui.views.dashboard_view import DashboardView
from gui.views.inventory_view import InventoryView
from gui.views.categories_suppliers_view import CategoriesSuppliersView
from gui.views.transactions_view import TransactionsView
from gui.views.pos_sales_view import POSSalesView
from gui.views.reports_view import ReportsView

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Inventory & Stock Management System")
        self.geometry("1280x760")
        self.minsize(1024, 650)
        self.configure(fg_color="#f1f5f9")

        self.api_client = APIClient()
        self.current_user = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Container
        self.container = ctk.CTkFrame(self, fg_color="#f1f5f9")
        self.container.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Show Login Screen by default
        self.show_login()

    def show_login(self):
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()

        login_view = LoginView(self.container, self.api_client, on_login_success=self.on_login_success)
        login_view.pack(fill="both", expand=True)

    def on_login_success(self, user):
        self.current_user = user
        
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()

        # Build Main App Layout (Sidebar + Header + Main View Area)
        self.container.grid_columnconfigure(0, weight=0)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(1, weight=1)

        # 1. Top Header Bar
        header = ctk.CTkFrame(self.container, fg_color="#ffffff", height=50, corner_radius=0, border_width=1, border_color="#e2e8f0")
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        logo_lbl = ctk.CTkLabel(
            header,
            text="📦 INVENTORY SYSTEM",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0284c7"
        )
        logo_lbl.grid(row=0, column=0, padx=20, pady=10)

        user_info = f"👤 Logged in: {user['full_name']} ({user['role'].upper()})"
        user_lbl = ctk.CTkLabel(header, text=user_info, font=ctk.CTkFont(size=12, weight="bold"), text_color="#334155")
        user_lbl.grid(row=0, column=1, sticky="e", padx=20, pady=10)

        # 2. Sidebar Navigation
        self.sidebar = ctk.CTkFrame(self.container, fg_color="#ffffff", width=220, corner_radius=0, border_width=1, border_color="#e2e8f0")
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # 3. Main Display View Frame
        self.view_frame = ctk.CTkFrame(self.container, fg_color="#f1f5f9", corner_radius=0)
        self.view_frame.grid(row=1, column=1, sticky="nsew")
        self.view_frame.grid_rowconfigure(0, weight=1)
        self.view_frame.grid_columnconfigure(0, weight=1)

        # Build Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊  Dashboard", self.show_dashboard),
            ("inventory", "📦  Inventory Catalog", self.show_inventory),
            ("categories", "📂  Categories & Suppliers", self.show_categories),
            ("transactions", "🔄  Stock Movements", self.show_transactions),
            ("pos", "💳  POS Sales Counter", self.show_pos),
            ("reports", "📈  Reports & Analytics", self.show_reports),
        ]

        for key, text, cmd in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                text_color="#475569",
                hover_color="#e2e8f0",
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda k=key, c=cmd: self.select_nav(k, c)
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.nav_buttons[key] = btn

        # Logout Button at bottom of sidebar
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪  Sign Out",
            anchor="w",
            height=42,
            corner_radius=8,
            fg_color="#ef4444",
            hover_color="#dc2626",
            text_color="#ffffff",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.show_login
        )
        logout_btn.pack(side="bottom", fill="x", padx=12, pady=20)

        # Default view: Dashboard
        self.select_nav("dashboard", self.show_dashboard)

    def select_nav(self, active_key, show_fn):
        for k, btn in self.nav_buttons.items():
            if k == active_key:
                btn.configure(fg_color="#0284c7", text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color="#475569")

        # Clear view frame
        for widget in self.view_frame.winfo_children():
            widget.destroy()

        show_fn()

    def show_dashboard(self):
        v = DashboardView(self.view_frame, self.api_client)
        v.pack(fill="both", expand=True)

    def show_inventory(self):
        v = InventoryView(self.view_frame, self.api_client)
        v.pack(fill="both", expand=True)

    def show_categories(self):
        v = CategoriesSuppliersView(self.view_frame, self.api_client)
        v.pack(fill="both", expand=True)

    def show_transactions(self):
        v = TransactionsView(self.view_frame, self.api_client)
        v.pack(fill="both", expand=True)

    def show_pos(self):
        v = POSSalesView(self.view_frame, self.api_client)
        v.pack(fill="both", expand=True)

    def show_reports(self):
        v = ReportsView(self.view_frame, self.api_client)
        v.pack(fill="both", expand=True)

if __name__ == '__main__':
    app = InventoryApp()
    app.mainloop()
