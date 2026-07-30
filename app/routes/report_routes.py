import os
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, send_file, current_app, request
from app.models import db, Product, Category, Order, StockTransaction
from app.utils.excel_exporter import export_products_to_excel, export_sales_to_excel
from app.utils.chart_generator import generate_sales_chart_figure, generate_category_stock_figure, figure_to_base64

report_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@report_bp.route('/dashboard-summary', methods=['GET'])
def get_dashboard_summary():
    products = Product.query.all()
    total_products = len(products)
    low_stock_products = [p for p in products if p.stock_quantity <= p.reorder_level]
    total_low_stock = len(low_stock_products)
    
    total_stock_value = sum(p.stock_quantity * p.unit_price for p in products)
    total_inventory_cost = sum(p.stock_quantity * p.cost_price for p in products)
    
    orders = Order.query.filter_by(status='COMPLETED').all()
    total_sales_revenue = sum(o.total_amount for o in orders)
    total_orders_count = len(orders)

    return jsonify({
        'total_products': total_products,
        'total_low_stock': total_low_stock,
        'total_stock_value': round(total_stock_value, 2),
        'total_inventory_cost': round(total_inventory_cost, 2),
        'total_sales_revenue': round(total_sales_revenue, 2),
        'total_orders_count': total_orders_count,
        'low_stock_items': [p.to_dict() for p in low_stock_products[:5]]  # top 5 low stock items
    }), 200

@report_bp.route('/charts', methods=['GET'])
def get_charts():
    # 1. Sales Trend (by day for last 7 days)
    today = datetime.utcnow().date()
    dates = [(today - timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
    
    # Calculate daily sales sum
    sales_by_date = {d: 0.0 for d in dates}
    orders = Order.query.filter_by(status='COMPLETED').all()
    for o in orders:
        if o.created_at:
            d_str = o.created_at.strftime('%b %d')
            if d_str in sales_by_date:
                sales_by_date[d_str] += o.total_amount

    sales_amounts = [round(sales_by_date[d], 2) for d in dates]

    # 2. Stock by Category
    categories = Category.query.all()
    cat_names = []
    cat_stocks = []
    for c in categories:
        cat_names.append(c.name)
        total_qty = sum(p.stock_quantity for p in c.products)
        cat_stocks.append(total_qty)

    sales_fig = generate_sales_chart_figure(dates, sales_amounts)
    cat_fig = generate_category_stock_figure(cat_names, cat_stocks)

    return jsonify({
        'sales_chart_base64': figure_to_base64(sales_fig),
        'category_chart_base64': figure_to_base64(cat_fig)
    }), 200

@report_bp.route('/export/inventory/excel', methods=['GET'])
def export_inventory_excel():
    products = [p.to_dict() for p in Product.query.all()]
    exports_dir = current_app.config.get('REPORTS_DIR', './exports')
    filepath = os.path.join(exports_dir, 'Inventory_Catalog_Report.xlsx')

    export_products_to_excel(products, filepath)

    return send_file(
        filepath,
        as_attachment=True,
        download_name='Inventory_Catalog_Report.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@report_bp.route('/export/sales/excel', methods=['GET'])
def export_sales_excel():
    orders = [o.to_dict() for o in Order.query.all()]
    exports_dir = current_app.config.get('REPORTS_DIR', './exports')
    filepath = os.path.join(exports_dir, 'Sales_Report.xlsx')

    export_sales_to_excel(orders, filepath)

    return send_file(
        filepath,
        as_attachment=True,
        download_name='Sales_Report.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
