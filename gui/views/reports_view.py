import os
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class ReportsView(ctk.CTkFrame):
    def __init__(self, parent, api_client):
        super().__init__(parent, fg_color="#f1f5f9")
        self.api_client = api_client
        self.orders = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="Reports, Analytics & Excel Export",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(side="left")

        # Export Buttons Bar
        export_bar = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10, border_width=1, border_color="#cbd5e1")
        export_bar.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        lbl_exp = ctk.CTkLabel(export_bar, text="📊 Excel Spreadsheets:", font=ctk.CTkFont(weight="bold"), text_color="#0284c7")
        lbl_exp.pack(side="left", padx=15, pady=12)

        btn_exp_inv = ctk.CTkButton(
            export_bar,
            text="📥 Export Inventory Excel (.xlsx)",
            fg_color="#16a34a",
            hover_color="#15803d",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            command=self.export_inventory_excel
        )
        btn_exp_inv.pack(side="left", padx=10, pady=12)

        btn_exp_sales = ctk.CTkButton(
            export_bar,
            text="📈 Export Sales Excel (.xlsx)",
            fg_color="#0284c7",
            hover_color="#0369a1",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            command=self.export_sales_excel
        )
        btn_exp_sales.pack(side="left", padx=10, pady=12)

        btn_dl_pdf = ctk.CTkButton(
            export_bar,
            text="📄 Download Invoice PDF",
            fg_color="#9333ea",
            hover_color="#7e22ce",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            command=self.download_selected_pdf
        )
        btn_dl_pdf.pack(side="right", padx=15, pady=12)

        # Sales Orders History Table
        table_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10, border_width=1, border_color="#cbd5e1")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        columns = ("id", "inv", "date", "customer", "subtotal", "tax", "discount", "total", "status", "user")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("inv", text="Invoice #")
        self.tree.heading("date", text="Date & Time")
        self.tree.heading("customer", text="Customer Name")
        self.tree.heading("subtotal", text="Subtotal (₹)")
        self.tree.heading("tax", text="Tax (₹)")
        self.tree.heading("discount", text="Discount (₹)")
        self.tree.heading("total", text="Total Amount (₹)")
        self.tree.heading("status", text="Status")
        self.tree.heading("user", text="Processed By")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("inv", width=120, anchor="center")
        self.tree.column("date", width=140, anchor="center")
        self.tree.column("customer", width=160)
        self.tree.column("subtotal", width=90, anchor="e")
        self.tree.column("tax", width=75, anchor="e")
        self.tree.column("discount", width=85, anchor="e")
        self.tree.column("total", width=110, anchor="e")
        self.tree.column("status", width=90, anchor="center")
        self.tree.column("user", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

        self.load_orders()

    def load_orders(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.orders = self.api_client.get_orders()
        for o in self.orders:
            self.tree.insert("", "end", values=(
                o['id'],
                o['invoice_number'],
                o['created_at'],
                o['customer_name'],
                f"₹{o['subtotal']:.2f}",
                f"₹{o['tax_amount']:.2f}",
                f"₹{o['discount_amount']:.2f}",
                f"₹{o['total_amount']:.2f}",
                o['status'],
                o['username']
            ))

    def export_inventory_excel(self):
        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Save Inventory Report",
            initialfile="Inventory_Catalog_Report.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if filepath:
            ok, msg = self.api_client.download_excel_report('inventory', filepath)
            if ok:
                messagebox.showinfo("Success", msg, parent=self)
                try:
                    os.startfile(filepath)
                except Exception:
                    pass
            else:
                messagebox.showerror("Error", msg, parent=self)

    def export_sales_excel(self):
        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Save Sales Report",
            initialfile="Sales_Report.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if filepath:
            ok, msg = self.api_client.download_excel_report('sales', filepath)
            if ok:
                messagebox.showinfo("Success", msg, parent=self)
                try:
                    os.startfile(filepath)
                except Exception:
                    pass
            else:
                messagebox.showerror("Error", msg, parent=self)

    def download_selected_pdf(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an order from the table first.", parent=self)
            return

        values = self.tree.item(selected[0], "values")
        order_id = int(values[0])
        inv_no = values[1]

        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Download PDF Invoice",
            initialfile=f"Invoice_{inv_no}.pdf",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if filepath:
            ok, msg = self.api_client.download_pdf_invoice(order_id, filepath)
            if ok:
                messagebox.showinfo("Success", msg, parent=self)
                try:
                    os.startfile(filepath)
                except Exception:
                    pass
            else:
                messagebox.showerror("Error", msg, parent=self)
