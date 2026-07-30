import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox

class InventoryView(ctk.CTkFrame):
    def __init__(self, parent, api_client):
        super().__init__(parent, fg_color="#f1f5f9")
        self.api_client = api_client
        self.products = []
        self.categories = []
        self.suppliers = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header bar
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="Inventory Catalog",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(side="left")

        btn_add = ctk.CTkButton(
            header_frame,
            text="➕ Add New Product",
            fg_color="#16a34a",
            hover_color="#15803d",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            command=self.open_add_modal
        )
        btn_add.pack(side="right", padx=5)

        btn_adjust = ctk.CTkButton(
            header_frame,
            text="📦 Adjust Stock",
            fg_color="#0284c7",
            hover_color="#0369a1",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            command=self.open_adjust_modal
        )
        btn_adjust.pack(side="right", padx=5)

        # Filter & Search Controls bar
        controls_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#cbd5e1")
        controls_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text="Search SKU, Product Name, Barcode...",
            width=260,
            fg_color="#f8fafc",
            border_color="#cbd5e1",
            text_color="#0f172a"
        )
        self.search_entry.pack(side="left", padx=15, pady=12)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_products())

        self.category_var = ctk.StringVar(value="All Categories")
        self.category_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            variable=self.category_var,
            values=["All Categories"],
            command=lambda v: self.load_products(),
            fg_color="#e2e8f0",
            button_color="#cbd5e1",
            text_color="#0f172a"
        )
        self.category_dropdown.pack(side="left", padx=10, pady=12)

        self.low_stock_chk = ctk.CTkCheckBox(
            controls_frame,
            text="Low Stock Only",
            command=self.load_products,
            text_color="#0f172a"
        )
        self.low_stock_chk.pack(side="left", padx=15, pady=12)

        btn_edit = ctk.CTkButton(
            controls_frame,
            text="✏️ Edit Selected",
            width=110,
            fg_color="#e2e8f0",
            hover_color="#cbd5e1",
            text_color="#0f172a",
            font=ctk.CTkFont(weight="bold"),
            command=self.open_edit_modal
        )
        btn_edit.pack(side="right", padx=10, pady=12)

        btn_delete = ctk.CTkButton(
            controls_frame,
            text="🗑️ Delete",
            width=90,
            fg_color="#ef4444",
            hover_color="#dc2626",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            command=self.handle_delete
        )
        btn_delete.pack(side="right", padx=5, pady=12)

        # Treeview Table
        table_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#cbd5e1")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#ffffff", foreground="#0f172a", fieldbackground="#ffffff", rowheight=30)
        style.configure("Treeview.Heading", background="#e2e8f0", foreground="#0f172a", font=('Helvetica', 10, 'bold'))
        style.map("Treeview", background=[('selected', '#0284c7')], foreground=[('selected', '#ffffff')])

        columns = ("id", "sku", "name", "category", "supplier", "cost", "unit", "stock", "reorder", "total_val", "alert")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("sku", text="SKU")
        self.tree.heading("name", text="Product Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("supplier", text="Supplier")
        self.tree.heading("cost", text="Cost (₹)")
        self.tree.heading("unit", text="Price (₹)")
        self.tree.heading("stock", text="Stock Qty")
        self.tree.heading("reorder", text="Reorder Level")
        self.tree.heading("total_val", text="Total Value (₹)")
        self.tree.heading("alert", text="Status Alert")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("sku", width=90)
        self.tree.column("name", width=200)
        self.tree.column("category", width=110)
        self.tree.column("supplier", width=120)
        self.tree.column("cost", width=80, anchor="e")
        self.tree.column("unit", width=80, anchor="e")
        self.tree.column("stock", width=75, anchor="center")
        self.tree.column("reorder", width=85, anchor="center")
        self.tree.column("total_val", width=100, anchor="e")
        self.tree.column("alert", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

        self.load_categories()
        self.load_suppliers()
        self.load_products()

    def load_categories(self):
        self.categories = self.api_client.get_categories()
        cat_names = ["All Categories"] + [c['name'] for c in self.categories]
        self.category_dropdown.configure(values=cat_names)

    def load_suppliers(self):
        self.suppliers = self.api_client.get_suppliers()

    def load_products(self):
        search = self.search_entry.get().strip()
        cat_val = self.category_var.get()
        cat_id = None
        if cat_val != "All Categories":
            for c in self.categories:
                if c['name'] == cat_val:
                    cat_id = c['id']
                    break
        low_stock = bool(self.low_stock_chk.get())

        self.products = self.api_client.get_products(search=search, category_id=cat_id, low_stock=low_stock)

        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in self.products:
            status = "⚠️ LOW STOCK" if p['is_low_stock'] else "OK"
            self.tree.insert("", "end", values=(
                p['id'],
                p['sku'],
                p['name'],
                p['category_name'],
                p['supplier_name'],
                f"₹{p['cost_price']:.2f}",
                f"₹{p['unit_price']:.2f}",
                p['stock_quantity'],
                p['reorder_level'],
                f"₹{p['total_value']:.2f}",
                status
            ))

    def get_selected_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product from the table first.")
            return None
        values = self.tree.item(selected[0], "values")
        p_id = int(values[0])
        for p in self.products:
            if p['id'] == p_id:
                return p
        return None

    def open_add_modal(self):
        ProductFormDialog(self, self.api_client, title="Add New Product", categories=self.categories, suppliers=self.suppliers, on_save=self.load_products)

    def open_edit_modal(self):
        product = self.get_selected_product()
        if product:
            ProductFormDialog(self, self.api_client, title="Edit Product", product=product, categories=self.categories, suppliers=self.suppliers, on_save=self.load_products)

    def open_adjust_modal(self):
        product = self.get_selected_product()
        if product:
            StockAdjustDialog(self, self.api_client, product=product, on_save=self.load_products)

    def handle_delete(self):
        product = self.get_selected_product()
        if not product:
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete product '{product['name']}'?"):
            success, msg = self.api_client.delete_product(product['id'])
            if success:
                messagebox.showinfo("Success", "Product deleted successfully.")
                self.load_products()
            else:
                messagebox.showerror("Error", msg)


class ProductFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, api_client, title, categories, suppliers, product=None, on_save=None):
        super().__init__(parent)
        self.api_client = api_client
        self.product = product
        self.categories = categories
        self.suppliers = suppliers
        self.on_save = on_save

        self.title(title)
        self.geometry("450x620")
        self.configure(fg_color="#ffffff")
        self.resizable(False, False)
        self.grab_set()

        lbl_title = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color="#0284c7")
        lbl_title.pack(pady=(20, 15))

        # Form Entries
        self.entries = {}
        fields = [
            ("SKU *", "sku", product['sku'] if product else ""),
            ("Product Name *", "name", product['name'] if product else ""),
            ("Cost Price (₹)", "cost_price", str(product['cost_price']) if product else "0.0"),
            ("Selling Price (₹) *", "unit_price", str(product['unit_price']) if product else "0.0"),
            ("Initial Stock Qty *", "stock_quantity", str(product['stock_quantity']) if product else "0"),
            ("Reorder Alert Level", "reorder_level", str(product['reorder_level']) if product else "10"),
            ("Barcode", "barcode", product.get('barcode', '') if product else ""),
        ]

        # Category Dropdown
        cat_frame = ctk.CTkFrame(self, fg_color="transparent")
        cat_frame.pack(fill="x", padx=35, pady=5)
        ctk.CTkLabel(cat_frame, text="Category *", text_color="#334155", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        cat_names = [c['name'] for c in categories]
        default_cat = product['category_name'] if product else (cat_names[0] if cat_names else "")
        self.cat_var = ctk.StringVar(value=default_cat)
        self.cat_menu = ctk.CTkOptionMenu(cat_frame, variable=self.cat_var, values=cat_names, fg_color="#f8fafc", text_color="#0f172a", button_color="#cbd5e1")
        self.cat_menu.pack(fill="x", pady=2)

        # Supplier Dropdown
        sup_frame = ctk.CTkFrame(self, fg_color="transparent")
        sup_frame.pack(fill="x", padx=35, pady=5)
        ctk.CTkLabel(sup_frame, text="Supplier", text_color="#334155", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        sup_names = ["None"] + [s['name'] for s in suppliers]
        default_sup = product['supplier_name'] if product and product.get('supplier_name') != 'N/A' else "None"
        self.sup_var = ctk.StringVar(value=default_sup)
        self.sup_menu = ctk.CTkOptionMenu(sup_frame, variable=self.sup_var, values=sup_names, fg_color="#f8fafc", text_color="#0f172a", button_color="#cbd5e1")
        self.sup_menu.pack(fill="x", pady=2)

        for label_text, key, val in fields:
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(fill="x", padx=35, pady=4)
            ctk.CTkLabel(frame, text=label_text, text_color="#334155", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            entry = ctk.CTkEntry(frame, fg_color="#f8fafc", border_color="#cbd5e1", text_color="#0f172a")
            entry.insert(0, val)
            entry.pack(fill="x", pady=2)
            self.entries[key] = entry

        btn_save = ctk.CTkButton(
            self,
            text="Save Product",
            fg_color="#16a34a",
            hover_color="#15803d",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            command=self.save
        )
        btn_save.pack(pady=20, padx=35, fill="x")

    def save(self):
        sku = self.entries['sku'].get().strip()
        name = self.entries['name'].get().strip()
        cat_name = self.cat_var.get()
        sup_name = self.sup_var.get()

        cat_id = None
        for c in self.categories:
            if c['name'] == cat_name:
                cat_id = c['id']
                break

        sup_id = None
        for s in self.suppliers:
            if s['name'] == sup_name:
                sup_id = s['id']
                break

        if not sku or not name or not cat_id:
            messagebox.showwarning("Validation Error", "SKU, Name, and Category are required.", parent=self)
            return

        try:
            cost_price = float(self.entries['cost_price'].get().strip())
            unit_price = float(self.entries['unit_price'].get().strip())
            stock_qty = int(self.entries['stock_quantity'].get().strip())
            reorder_lvl = int(self.entries['reorder_level'].get().strip())
        except ValueError:
            messagebox.showwarning("Validation Error", "Prices and Quantities must be valid numbers.", parent=self)
            return

        data = {
            'sku': sku,
            'name': name,
            'category_id': cat_id,
            'supplier_id': sup_id,
            'cost_price': cost_price,
            'unit_price': unit_price,
            'stock_quantity': stock_qty,
            'reorder_level': reorder_lvl,
            'barcode': self.entries['barcode'].get().strip(),
        }

        if self.product:
            success, msg, _ = self.api_client.update_product(self.product['id'], data)
        else:
            success, msg, _ = self.api_client.create_product(data)

        if success:
            if self.on_save:
                self.on_save()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)


class StockAdjustDialog(ctk.CTkToplevel):
    def __init__(self, parent, api_client, product, on_save=None):
        super().__init__(parent)
        self.api_client = api_client
        self.product = product
        self.on_save = on_save

        self.title(f"Stock Adjustment - {product['name']}")
        self.geometry("400x380")
        self.configure(fg_color="#ffffff")
        self.resizable(False, False)
        self.grab_set()

        lbl_title = ctk.CTkLabel(self, text=f"Stock Intake / Outgoing", font=ctk.CTkFont(size=16, weight="bold"), text_color="#0284c7")
        lbl_title.pack(pady=(20, 5))

        lbl_info = ctk.CTkLabel(self, text=f"Product: {product['name']} (Current Stock: {product['stock_quantity']})", text_color="#64748b")
        lbl_info.pack(pady=(0, 15))

        # Type Option
        ctk.CTkLabel(self, text="Transaction Type", text_color="#334155", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=35)
        self.type_var = ctk.StringVar(value="IN")
        self.type_menu = ctk.CTkOptionMenu(self, variable=self.type_var, values=["IN (Stock Intake)", "OUT (Stock Dispatch)", "ADJUSTMENT (Set Quantity)"], fg_color="#f8fafc", text_color="#0f172a", button_color="#cbd5e1")
        self.type_menu.pack(fill="x", padx=35, pady=5)

        # Quantity
        ctk.CTkLabel(self, text="Quantity", text_color="#334155", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=35)
        self.qty_entry = ctk.CTkEntry(self, fg_color="#f8fafc", border_color="#cbd5e1", text_color="#0f172a")
        self.qty_entry.insert(0, "10")
        self.qty_entry.pack(fill="x", padx=35, pady=5)

        # Note / Ref
        ctk.CTkLabel(self, text="Reference / Reason", text_color="#334155", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=35)
        self.note_entry = ctk.CTkEntry(self, placeholder_text="e.g. PO-901 or Damaged stock", fg_color="#f8fafc", border_color="#cbd5e1", text_color="#0f172a")
        self.note_entry.pack(fill="x", padx=35, pady=5)

        btn_submit = ctk.CTkButton(
            self,
            text="Submit Stock Transaction",
            fg_color="#0284c7",
            hover_color="#0369a1",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            command=self.submit
        )
        btn_submit.pack(pady=25, padx=35, fill="x")

    def submit(self):
        raw_type = self.type_var.get()
        if "IN" in raw_type:
            tx_type = "IN"
        elif "OUT" in raw_type:
            tx_type = "OUT"
        else:
            tx_type = "ADJUSTMENT"

        try:
            qty = int(self.qty_entry.get().strip())
        except ValueError:
            messagebox.showwarning("Error", "Quantity must be an integer.", parent=self)
            return

        note = self.note_entry.get().strip()

        success, msg, _ = self.api_client.add_stock_transaction(self.product['id'], tx_type, qty, note=note)
        if success:
            if self.on_save:
                self.on_save()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)
