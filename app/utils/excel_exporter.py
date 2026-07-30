import os
import pandas as pd

def export_products_to_excel(products, filepath):
    """
    Exports a list of product dicts to an Excel file using Pandas and OpenPyXL with Indian Rupees (₹).
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    data = []
    for p in products:
        data.append({
            'Product ID': p.get('id'),
            'SKU': p.get('sku'),
            'Name': p.get('name'),
            'Category': p.get('category_name'),
            'Supplier': p.get('supplier_name'),
            'Cost Price (₹)': p.get('cost_price'),
            'Unit Price (₹)': p.get('unit_price'),
            'Stock Quantity': p.get('stock_quantity'),
            'Reorder Level': p.get('reorder_level'),
            'Total Stock Value (₹)': p.get('total_value'),
            'Low Stock Alert': 'YES' if p.get('is_low_stock') else 'NO'
        })
    
    df = pd.DataFrame(data)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Inventory Catalog', index=False)
        
    return filepath

def export_sales_to_excel(orders, filepath):
    """
    Exports a list of orders/invoices to an Excel file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    data = []
    for o in orders:
        data.append({
            'Invoice #': o.get('invoice_number'),
            'Customer Name': o.get('customer_name'),
            'Customer Email': o.get('customer_email'),
            'Subtotal (₹)': o.get('subtotal'),
            'Tax (₹)': o.get('tax_amount'),
            'Discount (₹)': o.get('discount_amount'),
            'Total (₹)': o.get('total_amount'),
            'Status': o.get('status'),
            'Processed By': o.get('username'),
            'Date': o.get('created_at')
        })
        
    df = pd.DataFrame(data)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sales Orders', index=False)
        
    return filepath
