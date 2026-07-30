import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

class TransactionsView(ctk.CTkFrame):
    def __init__(self, parent, api_client):
        super().__init__(parent, fg_color="#f1f5f9")
        self.api_client = api_client

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="Stock Movement & Audit Transactions",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(side="left")

        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh Logs",
            width=120,
            fg_color="#e2e8f0",
            hover_color="#cbd5e1",
            text_color="#0f172a",
            font=ctk.CTkFont(weight="bold"),
            command=self.load_transactions
        )
        refresh_btn.pack(side="right")

        # Treeview Log Table
        table_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#cbd5e1")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        columns = ("id", "date", "type", "sku", "product", "qty", "ref", "note", "user")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("id", text="Tx ID")
        self.tree.heading("date", text="Date & Time")
        self.tree.heading("type", text="Type")
        self.tree.heading("sku", text="Product SKU")
        self.tree.heading("product", text="Product Name")
        self.tree.heading("qty", text="Qty Moved")
        self.tree.heading("ref", text="Reference #")
        self.tree.heading("note", text="Notes")
        self.tree.heading("user", text="Logged By")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("date", width=140, anchor="center")
        self.tree.column("type", width=90, anchor="center")
        self.tree.column("sku", width=100)
        self.tree.column("product", width=180)
        self.tree.column("qty", width=80, anchor="center")
        self.tree.column("ref", width=120)
        self.tree.column("note", width=220)
        self.tree.column("user", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

        self.load_transactions()

    def load_transactions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        transactions = self.api_client.get_stock_transactions()
        for t in transactions:
            tx_type = t['transaction_type']
            formatted_type = f"📥 {tx_type}" if tx_type == 'IN' else (f"📤 {tx_type}" if tx_type == 'OUT' else f"⚙️ {tx_type}")
            
            self.tree.insert("", "end", values=(
                t['id'],
                t['timestamp'],
                formatted_type,
                t['product_sku'],
                t['product_name'],
                t['quantity'],
                t['reference_no'],
                t['note'],
                t['username']
            ))
