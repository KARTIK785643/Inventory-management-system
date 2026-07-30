import os
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class POSSalesView(ctk.CTkFrame):
    def __init__(self, parent, api_client):
        super().__init__(parent, fg_color="#f1f5f9")
        self.api_client = api_client
        self.cart = []
        self.all_products = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="Point of Sale (POS) & Billing Counter",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(side="left")

        # Left Frame - Product Selection
        left_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10, border_width=1, border_color="#cbd5e1")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(0, 20))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(2, weight=1)

        lbl_catalog = ctk.CTkLabel(left_frame, text="Available Products", font=ctk.CTkFont(size=16, weight="bold"), text_color="#0284c7")
        lbl_catalog.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        self.search_entry = ctk.CTkEntry(left_frame, placeholder_text="Search product by name or SKU...", fg_color="#f8fafc", border_color="#cbd5e1", text_color="#0f172a")
        self.search_entry.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_catalog())

        # Catalog Treeview
        catalog_tree_frame = ctk.CTkFrame(left_frame, fg_color="#f8fafc")
        catalog_tree_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(5, 15))
        catalog_tree_frame.grid_columnconfigure(0, weight=1)
        catalog_tree_frame.grid_rowconfigure(0, weight=1)

        self.catalog_tree = ttk.Treeview(catalog_tree_frame, columns=("sku", "name", "price", "stock"), show="headings")
        self.catalog_tree.heading("sku", text="SKU")
        self.catalog_tree.heading("name", text="Product Name")
        self.catalog_tree.heading("price", text="Price (₹)")
        self.catalog_tree.heading("stock", text="Stock")

        self.catalog_tree.column("sku", width=80)
        self.catalog_tree.column("name", width=180)
        self.catalog_tree.column("price", width=80, anchor="e")
        self.catalog_tree.column("stock", width=60, anchor="center")

        self.catalog_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.catalog_tree.bind("<Double-1>", lambda e: self.add_to_cart())

        btn_add_cart = ctk.CTkButton(
            left_frame,
            text="🛒 Add to Cart",
            fg_color="#0284c7",
            hover_color="#0369a1",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            command=self.add_to_cart
        )
        btn_add_cart.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))

        # Right Frame - Cart & Checkout
        right_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10, border_width=1, border_color="#cbd5e1")
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=(0, 20))
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        lbl_cart = ctk.CTkLabel(right_frame, text="Active Shopping Cart", font=ctk.CTkFont(size=16, weight="bold"), text_color="#16a34a")
        lbl_cart.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        # Cart Treeview
        cart_tree_frame = ctk.CTkFrame(right_frame, fg_color="#f8fafc")
        cart_tree_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        cart_tree_frame.grid_columnconfigure(0, weight=1)
        cart_tree_frame.grid_rowconfigure(0, weight=1)

        self.cart_tree = ttk.Treeview(cart_tree_frame, columns=("name", "price", "qty", "subtotal"), show="headings")
        self.cart_tree.heading("name", text="Item")
        self.cart_tree.heading("price", text="Price (₹)")
        self.cart_tree.heading("qty", text="Qty")
        self.cart_tree.heading("subtotal", text="Subtotal (₹)")

        self.cart_tree.column("name", width=160)
        self.cart_tree.column("price", width=75, anchor="e")
        self.cart_tree.column("qty", width=60, anchor="center")
        self.cart_tree.column("subtotal", width=85, anchor="e")

        self.cart_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Cart Controls (Remove / Clear)
        cart_ctrl = ctk.CTkFrame(right_frame, fg_color="transparent")
        cart_ctrl.grid(row=2, column=0, sticky="ew", padx=15, pady=5)

        btn_remove = ctk.CTkButton(cart_ctrl, text="❌ Remove Item", width=110, fg_color="#ef4444", hover_color="#dc2626", text_color="#ffffff", command=self.remove_from_cart)
        btn_remove.pack(side="left")

        btn_clear = ctk.CTkButton(cart_ctrl, text="🧹 Clear Cart", width=100, fg_color="#e2e8f0", hover_color="#cbd5e1", text_color="#0f172a", command=self.clear_cart)
        btn_clear.pack(side="right")

        # Summary & Customer Info Box
        summary_box = ctk.CTkFrame(right_frame, fg_color="#f8fafc", corner_radius=8, border_width=1, border_color="#cbd5e1")
        summary_box.grid(row=3, column=0, sticky="ew", padx=15, pady=(5, 15))
        summary_box.grid_columnconfigure((0, 1), weight=1)

        self.cust_name_entry = ctk.CTkEntry(summary_box, placeholder_text="Customer Name (Default: Walk-in)", fg_color="#ffffff", border_color="#cbd5e1", text_color="#0f172a")
        self.cust_name_entry.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 5))

        self.cust_email_entry = ctk.CTkEntry(summary_box, placeholder_text="Customer Email (Optional)", fg_color="#ffffff", border_color="#cbd5e1", text_color="#0f172a")
        self.cust_email_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=5)

        self.discount_entry = ctk.CTkEntry(summary_box, placeholder_text="Discount (₹)", fg_color="#ffffff", border_color="#cbd5e1", text_color="#0f172a")
        self.discount_entry.insert(0, "0.0")
        self.discount_entry.grid(row=2, column=0, sticky="ew", padx=(12, 6), pady=5)
        self.discount_entry.bind("<KeyRelease>", lambda e: self.update_cart_totals())

        self.tax_entry = ctk.CTkEntry(summary_box, placeholder_text="Tax Rate (e.g. 0.05)", fg_color="#ffffff", border_color="#cbd5e1", text_color="#0f172a")
        self.tax_entry.insert(0, "0.05")
        self.tax_entry.grid(row=2, column=1, sticky="ew", padx=(6, 12), pady=5)
        self.tax_entry.bind("<KeyRelease>", lambda e: self.update_cart_totals())

        self.lbl_grand_total = ctk.CTkLabel(summary_box, text="TOTAL: ₹0.00", font=ctk.CTkFont(size=18, weight="bold"), text_color="#16a34a")
        self.lbl_grand_total.grid(row=3, column=0, columnspan=2, pady=10)

        btn_checkout = ctk.CTkButton(
            summary_box,
            text="💳 Complete Checkout & Print PDF Invoice",
            height=40,
            fg_color="#16a34a",
            hover_color="#15803d",
            text_color="#ffffff",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.process_checkout
        )
        btn_checkout.grid(row=4, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))

        self.load_catalog()

    def load_catalog(self):
        self.all_products = self.api_client.get_products()
        self.filter_catalog()

    def filter_catalog(self):
        search = self.search_entry.get().strip().lower()
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)

        for p in self.all_products:
            if not search or search in p['name'].lower() or search in p['sku'].lower():
                self.catalog_tree.insert("", "end", values=(
                    p['sku'],
                    p['name'],
                    f"₹{p['unit_price']:.2f}",
                    p['stock_quantity']
                ))

    def add_to_cart(self):
        selected = self.catalog_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product from the left catalog.", parent=self)
            return

        sku = self.catalog_tree.item(selected[0], "values")[0]
        prod = None
        for p in self.all_products:
            if p['sku'] == sku:
                prod = p
                break

        if not prod:
            return

        if prod['stock_quantity'] <= 0:
            messagebox.showerror("Out of Stock", f"Product '{prod['name']}' is out of stock!", parent=self)
            return

        # Check if already in cart
        for item in self.cart:
            if item['product']['id'] == prod['id']:
                if item['qty'] + 1 > prod['stock_quantity']:
                    messagebox.showwarning("Stock Limit", f"Cannot add more. Available stock is {prod['stock_quantity']}", parent=self)
                    return
                item['qty'] += 1
                self.render_cart()
                return

        self.cart.append({'product': prod, 'qty': 1})
        self.render_cart()

    def remove_from_cart(self):
        selected = self.cart_tree.selection()
        if not selected:
            return
        idx = self.cart_tree.index(selected[0])
        del self.cart[idx]
        self.render_cart()

    def clear_cart(self):
        self.cart.clear()
        self.render_cart()

    def render_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        for c_item in self.cart:
            p = c_item['product']
            q = c_item['qty']
            subtotal = q * p['unit_price']
            self.cart_tree.insert("", "end", values=(
                p['name'],
                f"₹{p['unit_price']:.2f}",
                q,
                f"₹{subtotal:.2f}"
            ))

        self.update_cart_totals()

    def update_cart_totals(self):
        subtotal = sum(item['qty'] * item['product']['unit_price'] for item in self.cart)
        
        try:
            discount = float(self.discount_entry.get().strip())
        except ValueError:
            discount = 0.0

        try:
            tax_rate = float(self.tax_entry.get().strip())
        except ValueError:
            tax_rate = 0.05

        tax_amt = subtotal * tax_rate
        total = max(0.0, subtotal + tax_amt - discount)

        self.lbl_grand_total.configure(text=f"TOTAL: ₹{total:,.2f}")

    def process_checkout(self):
        if not self.cart:
            messagebox.showwarning("Cart Empty", "Please add products to the cart before checkout.", parent=self)
            return

        cust_name = self.cust_name_entry.get().strip() or "Walk-in Customer"
        cust_email = self.cust_email_entry.get().strip()

        try:
            discount = float(self.discount_entry.get().strip())
        except ValueError:
            discount = 0.0

        try:
            tax_rate = float(self.tax_entry.get().strip())
        except ValueError:
            tax_rate = 0.05

        order_items = [{'product_id': item['product']['id'], 'quantity': item['qty'], 'unit_price': item['product']['unit_price']} for item in self.cart]

        success, msg, order_data = self.api_client.create_order(
            customer_name=cust_name,
            customer_email=cust_email,
            items=order_items,
            discount=discount,
            tax_rate=tax_rate
        )

        if success:
            order_id = order_data['id']
            inv_no = order_data['invoice_number']
            
            messagebox.showinfo("Success", f"Order #{inv_no} placed successfully!", parent=self)

            # Offer to save PDF invoice
            save_path = filedialog.asksaveasfilename(
                parent=self,
                title="Save PDF Invoice",
                initialfile=f"Invoice_{inv_no}.pdf",
                defaultextension=".pdf",
                filetypes=[("PDF Documents", "*.pdf")]
            )
            if save_path:
                ok, p_msg = self.api_client.download_pdf_invoice(order_id, save_path)
                if ok:
                    messagebox.showinfo("PDF Saved", p_msg, parent=self)
                    try:
                        os.startfile(save_path)
                    except Exception:
                        pass
                else:
                    messagebox.showerror("Error", p_msg, parent=self)

            # Reset cart and refresh catalog
            self.clear_cart()
            self.load_catalog()
        else:
            messagebox.showerror("Checkout Failed", msg, parent=self)
