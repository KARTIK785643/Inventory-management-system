import os
import uuid
from flask import Blueprint, request, jsonify, send_file, current_app
from app.models import db, Product, Order, OrderItem, StockTransaction
from app.utils.pdf_generator import generate_invoice_pdf

order_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@order_bp.route('', methods=['GET'])
def get_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200

@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict()), 200

@order_bp.route('', methods=['POST'])
def create_order():
    data = request.get_json() or {}
    items = data.get('items', [])
    if not items:
        return jsonify({'error': 'Order must contain at least one item'}), 400

    customer_name = data.get('customer_name', 'Walk-in Customer')
    customer_email = data.get('customer_email', '')
    discount_amount = float(data.get('discount_amount', 0.0))
    tax_rate = float(data.get('tax_rate', 0.05))  # Default 5% tax
    user_id = data.get('user_id')

    # Validate stock and calculate totals
    subtotal = 0.0
    order_items_to_create = []

    for item_data in items:
        p_id = item_data.get('product_id')
        qty = int(item_data.get('quantity', 1))
        
        product = Product.query.get(p_id)
        if not product:
            return jsonify({'error': f'Product ID {p_id} not found'}), 404
        
        if product.stock_quantity < qty:
            return jsonify({'error': f'Insufficient stock for product "{product.name}". Required: {qty}, Available: {product.stock_quantity}'}), 400

        unit_price = float(item_data.get('unit_price', product.unit_price))
        line_subtotal = round(unit_price * qty, 2)
        subtotal += line_subtotal

        order_items_to_create.append({
            'product': product,
            'quantity': qty,
            'unit_price': unit_price,
            'subtotal': line_subtotal
        })

    tax_amount = round(subtotal * tax_rate, 2)
    total_amount = max(0.0, round(subtotal + tax_amount - discount_amount, 2))

    invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"

    new_order = Order(
        invoice_number=invoice_number,
        customer_name=customer_name,
        customer_email=customer_email,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total_amount=total_amount,
        status='COMPLETED',
        user_id=user_id
    )

    db.session.add(new_order)
    db.session.flush()  # Get order.id

    for item_info in order_items_to_create:
        p = item_info['product']
        q = item_info['quantity']
        
        # Deduct product stock
        p.stock_quantity -= q

        # Create OrderItem
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=p.id,
            quantity=q,
            unit_price=item_info['unit_price'],
            subtotal=item_info['subtotal']
        )
        db.session.add(order_item)

        # Log Stock OUT transaction
        stock_tx = StockTransaction(
            product_id=p.id,
            transaction_type='OUT',
            quantity=q,
            reference_no=invoice_number,
            note=f"Sales Order #{invoice_number}",
            user_id=user_id
        )
        db.session.add(stock_tx)

    db.session.commit()

    return jsonify(new_order.to_dict()), 201

@order_bp.route('/<int:order_id>/pdf', methods=['GET'])
def get_order_pdf(order_id):
    order = Order.query.get_or_404(order_id)
    exports_dir = current_app.config.get('REPORTS_DIR', './exports')
    filename = f"Invoice_{order.invoice_number}.pdf"
    filepath = os.path.join(exports_dir, filename)

    generate_invoice_pdf(order.to_dict(), filepath)

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
