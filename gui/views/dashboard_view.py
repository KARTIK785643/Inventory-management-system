import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app.utils.chart_generator import generate_sales_chart_figure, generate_category_stock_figure

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, api_client):
        super().__init__(parent, fg_color="#f1f5f9")
        self.api_client = api_client

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Dashboard Overview",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(side="left")

        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh Data",
            width=120,
            height=32,
            fg_color="#e2e8f0",
            hover_color="#cbd5e1",
            text_color="#0f172a",
            font=ctk.CTkFont(weight="bold"),
            command=self.load_dashboard_data
        )
        refresh_btn.pack(side="right")

        # Container for Cards
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Main content scrollable area
        self.content_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.content_scroll.grid_columnconfigure(0, weight=1)

        self.load_dashboard_data()

    def create_kpi_card(self, parent, col, title, value, subtitle, color):
        card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=10, border_width=1, border_color="#cbd5e1")
        card.grid(row=0, column=col, padx=8, pady=5, sticky="ew")

        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color="#64748b")
        lbl_title.pack(anchor="w", padx=15, pady=(12, 2))

        lbl_val = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"), text_color=color)
        lbl_val.pack(anchor="w", padx=15, pady=2)

        lbl_sub = ctk.CTkLabel(card, text=subtitle, font=ctk.CTkFont(size=11), text_color="#94a3b8")
        lbl_sub.pack(anchor="w", padx=15, pady=(0, 12))

    def load_dashboard_data(self):
        # Clear cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        # Clear scroll content
        for widget in self.content_scroll.winfo_children():
            widget.destroy()

        data = self.api_client.get_dashboard_summary()

        total_prods = data.get('total_products', 0)
        low_stock = data.get('total_low_stock', 0)
        stock_val = data.get('total_stock_value', 0.0)
        sales_rev = data.get('total_sales_revenue', 0.0)

        # KPI Cards with Indian Rupees (₹)
        self.create_kpi_card(self.cards_frame, 0, "TOTAL PRODUCTS", f"{total_prods}", "Active Catalog Items", "#0284c7")
        self.create_kpi_card(self.cards_frame, 1, "LOW STOCK ALERTS", f"{low_stock}", "Requires Reorder", "#e11d48" if low_stock > 0 else "#16a34a")
        self.create_kpi_card(self.cards_frame, 2, "TOTAL STOCK VALUE", f"₹{stock_val:,.2f}", "Retail Valuation", "#9333ea")
        self.create_kpi_card(self.cards_frame, 3, "TOTAL SALES REVENUE", f"₹{sales_rev:,.2f}", "Completed Orders", "#16a34a")

        # Charts Section
        charts_container = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        charts_container.pack(fill="x", pady=10)
        charts_container.grid_columnconfigure((0, 1), weight=1)

        # Matplotlib Sales Chart Frame
        sales_frame = ctk.CTkFrame(charts_container, fg_color="#ffffff", corner_radius=10, border_width=1, border_color="#cbd5e1")
        sales_frame.grid(row=0, column=0, padx=8, pady=5, sticky="nsew")

        # Fetch Chart Figures
        categories = self.api_client.get_categories()
        products = self.api_client.get_products()
        orders = self.api_client.get_orders()

        # Build figures
        dates = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Today"]
        sales_data = [0.0] * 7
        if orders:
            for o in orders[:10]:
                sales_data[hash(o.get('id', 0)) % 7] += o.get('total_amount', 0)

        cat_names = [c['name'] for c in categories] if categories else ["None"]
        cat_counts = []
        for c in categories:
            cat_counts.append(sum(1 for p in products if p['category_id'] == c['id']))

        fig_sales = generate_sales_chart_figure(dates, sales_data)
        fig_cat = generate_category_stock_figure(cat_names if cat_names else ["General"], cat_counts if cat_counts else [len(products)])

        canvas_sales = FigureCanvasTkAgg(fig_sales, master=sales_frame)
        canvas_sales.draw()
        canvas_sales.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Stock Distribution Chart Frame
        cat_frame = ctk.CTkFrame(charts_container, fg_color="#ffffff", corner_radius=10, border_width=1, border_color="#cbd5e1")
        cat_frame.grid(row=0, column=1, padx=8, pady=5, sticky="nsew")

        canvas_cat = FigureCanvasTkAgg(fig_cat, master=cat_frame)
        canvas_cat.draw()
        canvas_cat.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Low Stock Alert Table Section
        low_stock_frame = ctk.CTkFrame(self.content_scroll, fg_color="#ffffff", corner_radius=10, border_width=1, border_color="#cbd5e1")
        low_stock_frame.pack(fill="x", pady=15, padx=8)

        lbl_alert = ctk.CTkLabel(
            low_stock_frame,
            text="⚠️ Low Stock Items Requiring Attention",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#d97706"
        )
        lbl_alert.pack(anchor="w", padx=15, pady=12)

        low_stock_items = data.get('low_stock_items', [])
        if not low_stock_items:
            no_alert = ctk.CTkLabel(low_stock_frame, text="All inventory levels are healthy!", text_color="#16a34a", font=ctk.CTkFont(size=13))
            no_alert.pack(padx=15, pady=(0, 15))
        else:
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Treeview", background="#ffffff", foreground="#0f172a", fieldbackground="#ffffff", rowheight=28)
            style.configure("Treeview.Heading", background="#e2e8f0", foreground="#0f172a", font=('Helvetica', 10, 'bold'))
            style.map("Treeview", background=[('selected', '#0284c7')], foreground=[('selected', '#ffffff')])

            tree = ttk.Treeview(low_stock_frame, columns=("sku", "name", "category", "qty", "reorder"), show="headings", height=5)
            tree.heading("sku", text="SKU")
            tree.heading("name", text="Product Name")
            tree.heading("category", text="Category")
            tree.heading("qty", text="Stock Qty")
            tree.heading("reorder", text="Reorder Level")

            tree.column("sku", width=100)
            tree.column("name", width=250)
            tree.column("category", width=120)
            tree.column("qty", width=90, anchor="center")
            tree.column("reorder", width=110, anchor="center")

            for item in low_stock_items:
                tree.insert("", "end", values=(
                    item.get('sku'),
                    item.get('name'),
                    item.get('category_name'),
                    item.get('stock_quantity'),
                    item.get('reorder_level')
                ))

            tree.pack(fill="x", padx=15, pady=(0, 15))
