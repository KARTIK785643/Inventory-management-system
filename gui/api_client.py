import requests

class APIClient:
    def __init__(self, base_url="http://127.0.0.1:5000/api"):
        self.base_url = base_url
        self.current_user = None

    def login(self, username, password):
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={'username': username, 'password': password},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.current_user = data.get('user')
                return True, "Login successful", self.current_user
            else:
                err = response.json().get('error', 'Login failed')
                return False, err, None
        except Exception as e:
            return False, f"Server connection failed: {str(e)}", None

    def get_dashboard_summary(self):
        try:
            res = requests.get(f"{self.base_url}/reports/dashboard-summary", timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print(f"Error fetching dashboard summary: {e}")
        return {}

    def get_products(self, search="", category_id=None, low_stock=False):
        try:
            params = {}
            if search:
                params['search'] = search
            if category_id:
                params['category_id'] = category_id
            if low_stock:
                params['low_stock'] = True
            res = requests.get(f"{self.base_url}/products", params=params, timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print(f"Error fetching products: {e}")
        return []

    def create_product(self, product_data):
        try:
            res = requests.post(f"{self.base_url}/products", json=product_data, timeout=5)
            if res.status_code == 201:
                return True, "Product created successfully", res.json()
            return False, res.json().get('error', 'Failed to create product'), None
        except Exception as e:
            return False, str(e), None

    def update_product(self, product_id, product_data):
        try:
            res = requests.put(f"{self.base_url}/products/{product_id}", json=product_data, timeout=5)
            if res.status_code == 200:
                return True, "Product updated successfully", res.json()
            return False, res.json().get('error', 'Failed to update product'), None
        except Exception as e:
            return False, str(e), None

    def delete_product(self, product_id):
        try:
            res = requests.delete(f"{self.base_url}/products/{product_id}", timeout=5)
            if res.status_code == 200:
                return True, "Product deleted"
            return False, res.json().get('error', 'Failed to delete')
        except Exception as e:
            return False, str(e)

    def get_categories(self):
        try:
            res = requests.get(f"{self.base_url}/categories", timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    def create_category(self, name, description=""):
        try:
            res = requests.post(f"{self.base_url}/categories", json={'name': name, 'description': description}, timeout=5)
            if res.status_code == 201:
                return True, "Category created", res.json()
            return False, res.json().get('error', 'Error'), None
        except Exception as e:
            return False, str(e), None

    def get_suppliers(self):
        try:
            res = requests.get(f"{self.base_url}/suppliers", timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    def create_supplier(self, name, email="", phone="", address=""):
        try:
            res = requests.post(f"{self.base_url}/suppliers", json={
                'name': name, 'contact_email': email, 'phone': phone, 'address': address
            }, timeout=5)
            if res.status_code == 201:
                return True, "Supplier created", res.json()
            return False, res.json().get('error', 'Error'), None
        except Exception as e:
            return False, str(e), None

    def get_stock_transactions(self, product_id=None):
        try:
            params = {}
            if product_id:
                params['product_id'] = product_id
            res = requests.get(f"{self.base_url}/stock-transactions", params=params, timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print(f"Error stock tx: {e}")
        return []

    def add_stock_transaction(self, product_id, tx_type, quantity, ref="", note=""):
        try:
            user_id = self.current_user['id'] if self.current_user else None
            res = requests.post(f"{self.base_url}/stock-transactions", json={
                'product_id': product_id,
                'transaction_type': tx_type,
                'quantity': quantity,
                'reference_no': ref,
                'note': note,
                'user_id': user_id
            }, timeout=5)
            if res.status_code == 201:
                return True, "Transaction recorded", res.json()
            return False, res.json().get('error', 'Error'), None
        except Exception as e:
            return False, str(e), None

    def create_order(self, customer_name, customer_email, items, discount=0.0, tax_rate=0.05):
        try:
            user_id = self.current_user['id'] if self.current_user else None
            res = requests.post(f"{self.base_url}/orders", json={
                'customer_name': customer_name,
                'customer_email': customer_email,
                'items': items,
                'discount_amount': discount,
                'tax_rate': tax_rate,
                'user_id': user_id
            }, timeout=5)
            if res.status_code == 201:
                return True, "Order completed successfully", res.json()
            return False, res.json().get('error', 'Failed to create order'), None
        except Exception as e:
            return False, str(e), None

    def get_orders(self):
        try:
            res = requests.get(f"{self.base_url}/orders", timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    def get_pdf_invoice_url(self, order_id):
        return f"{self.base_url}/orders/{order_id}/pdf"

    def download_pdf_invoice(self, order_id, save_path):
        try:
            url = f"{self.base_url}/orders/{order_id}/pdf"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(res.content)
                return True, f"Invoice saved to {save_path}"
            return False, "Failed to download PDF invoice"
        except Exception as e:
            return False, str(e)

    def download_excel_report(self, report_type, save_path):
        """
        report_type: 'inventory' or 'sales'
        """
        try:
            url = f"{self.base_url}/reports/export/{report_type}/excel"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(res.content)
                return True, f"Report saved to {save_path}"
            return False, "Failed to download Excel report"
        except Exception as e:
            return False, str(e)
