from flask import Blueprint, request, jsonify
from app.models import db, Product, StockTransaction

stock_bp = Blueprint('stock', __name__, url_prefix='/api/stock-transactions')

@stock_bp.route('', methods=['GET'])
def get_transactions():
    product_id = request.args.get('product_id', type=int)
    query = StockTransaction.query

    if product_id:
        query = query.filter(StockTransaction.product_id == product_id)

    transactions = query.order_by(StockTransaction.timestamp.desc()).all()
    return jsonify([t.to_dict() for t in transactions]), 200

@stock_bp.route('', methods=['POST'])
def create_transaction():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    transaction_type = data.get('transaction_type')  # 'IN', 'OUT', 'ADJUSTMENT'
    quantity = data.get('quantity')
    user_id = data.get('user_id')
    reference_no = data.get('reference_no', '')
    note = data.get('note', '')

    if not product_id or not transaction_type or quantity is None:
        return jsonify({'error': 'product_id, transaction_type, and quantity are required'}), 400

    if transaction_type not in ['IN', 'OUT', 'ADJUSTMENT']:
        return jsonify({'error': 'Invalid transaction_type. Must be IN, OUT, or ADJUSTMENT'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    qty = int(quantity)
    if transaction_type == 'IN':
        product.stock_quantity += qty
    elif transaction_type == 'OUT':
        if product.stock_quantity < qty:
            return jsonify({'error': f'Insufficient stock. Current stock is {product.stock_quantity}'}), 400
        product.stock_quantity -= qty
    elif transaction_type == 'ADJUSTMENT':
        # Direct set
        product.stock_quantity = qty

    transaction = StockTransaction(
        product_id=product_id,
        transaction_type=transaction_type,
        quantity=qty,
        reference_no=reference_no,
        note=note,
        user_id=user_id
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        'transaction': transaction.to_dict(),
        'product': product.to_dict()
    }), 201
