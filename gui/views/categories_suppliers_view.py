import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox

class CategoriesSuppliersView(ctk.CTkFrame):
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
            text="Categories & Suppliers Management",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0f172a"
        )
        title.pack(side="left")

        # Tabview for Categories / Suppliers
        self.tabview = ctk.CTkTabview(self, fg_color="#ffffff", segmented_button_selected_color="#0284c7")
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        self.tab_cat = self.tabview.add("Product Categories")
        self.tab_sup = self.tabview.add("Suppliers & Vendors")

        self.setup_categories_tab()
        self.setup_suppliers_tab()

    def setup_categories_tab(self):
        self.tab_cat.grid_columnconfigure(0, weight=1)
        self.tab_cat.grid_rowconfigure(1, weight=1)

        btn_frame = ctk.CTkFrame(self.tab_cat, fg_color="transparent")
        btn_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=10)

        btn_add = ctk.CTkButton(
            btn_frame,
            text="➕ Add New Category",
            fg_color="#16a34a",
            hover_color="#15803d",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            command=self.open_add_category_modal
        )
        btn_add.pack(side="left")

        # Treeview
        tree_frame = ctk.CTkFrame(self.tab_cat, fg_color="#ffffff")
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        self.cat_tree = ttk.Treeview(tree_frame, columns=("id", "name", "desc", "count"), show="headings")
        self.cat_tree.heading("id", text="ID")
        self.cat_tree.heading("name", text="Category Name")
        self.cat_tree.heading("desc", text="Description")
        self.cat_tree.heading("count", text="Associated Products")

        self.cat_tree.column("id", width=60, anchor="center")
        self.cat_tree.column("name", width=180)
        self.cat_tree.column("desc", width=350)
        self.cat_tree.column("count", width=140, anchor="center")

        self.cat_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_categories()

    def setup_suppliers_tab(self):
        self.tab_sup.grid_columnconfigure(0, weight=1)
        self.tab_sup.grid_rowconfigure(1, weight=1)

        btn_frame = ctk.CTkFrame(self.tab_sup, fg_color="transparent")
        btn_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=10)

        btn_add = ctk.CTkButton(
            btn_frame,
            text="➕ Add New Supplier",
            fg_color="#16a34a",
            hover_color="#15803d",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            command=self.open_add_supplier_modal
        )
        btn_add.pack(side="left")

        tree_frame = ctk.CTkFrame(self.tab_sup, fg_color="#ffffff")
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        self.sup_tree = ttk.Treeview(tree_frame, columns=("id", "name", "email", "phone", "address"), show="headings")
        self.sup_tree.heading("id", text="ID")
        self.sup_tree.heading("name", text="Supplier Name")
        self.sup_tree.heading("email", text="Email Contact")
        self.sup_tree.heading("phone", text="Phone Number")
        self.sup_tree.heading("address", text="Address")

        self.sup_tree.column("id", width=60, anchor="center")
        self.sup_tree.column("name", width=180)
        self.sup_tree.column("email", width=180)
        self.sup_tree.column("phone", width=140)
        self.sup_tree.column("address", width=250)

        self.sup_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_suppliers()

    def load_categories(self):
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)
        cats = self.api_client.get_categories()
        for c in cats:
            self.cat_tree.insert("", "end", values=(c['id'], c['name'], c['description'], c['product_count']))

    def load_suppliers(self):
        for item in self.sup_tree.get_children():
            self.sup_tree.delete(item)
        sups = self.api_client.get_suppliers()
        for s in sups:
            self.sup_tree.insert("", "end", values=(s['id'], s['name'], s['contact_email'], s['phone'], s['address']))

    def open_add_category_modal(self):
        dialog = ctk.CTkInputDialog(text="Enter Category Name:", title="Add Category")
        name = dialog.get_input()
        if name and name.strip():
            success, msg, _ = self.api_client.create_category(name.strip())
            if success:
                self.load_categories()
            else:
                messagebox.showerror("Error", msg)

    def open_add_supplier_modal(self):
        SupplierModal(self, self.api_client, on_save=self.load_suppliers)


class SupplierModal(ctk.CTkToplevel):
    def __init__(self, parent, api_client, on_save=None):
        super().__init__(parent)
        self.api_client = api_client
        self.on_save = on_save

        self.title("Add New Supplier")
        self.geometry("400x380")
        self.configure(fg_color="#ffffff")
        self.resizable(False, False)
        self.grab_set()

        lbl_title = ctk.CTkLabel(self, text="Add New Supplier Details", font=ctk.CTkFont(size=16, weight="bold"), text_color="#0284c7")
        lbl_title.pack(pady=(20, 15))

        self.name_e = self.create_field("Supplier / Vendor Name *")
        self.email_e = self.create_field("Email Address")
        self.phone_e = self.create_field("Phone Number")
        self.addr_e = self.create_field("Physical Address")

        btn_save = ctk.CTkButton(
            self,
            text="Save Supplier",
            fg_color="#16a34a",
            hover_color="#15803d",
            text_color="#ffffff",
            font=ctk.CTkFont(weight="bold"),
            command=self.save
        )
        btn_save.pack(pady=20, padx=35, fill="x")

    def create_field(self, label):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=35, pady=4)
        ctk.CTkLabel(frame, text=label, text_color="#334155", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        entry = ctk.CTkEntry(frame, fg_color="#f8fafc", border_color="#cbd5e1", text_color="#0f172a")
        entry.pack(fill="x", pady=2)
        return entry

    def save(self):
        name = self.name_e.get().strip()
        if not name:
            messagebox.showwarning("Validation Error", "Supplier name is required.", parent=self)
            return

        success, msg, _ = self.api_client.create_supplier(
            name=name,
            email=self.email_e.get().strip(),
            phone=self.phone_e.get().strip(),
            address=self.addr_e.get().strip()
        )

        if success:
            if self.on_save:
                self.on_save()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)
