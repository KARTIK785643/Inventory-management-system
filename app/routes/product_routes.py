from flask import Blueprint, request, jsonify
from app.models import db, Product, Category, Supplier

product_bp = Blueprint('products', __name__, url_prefix='/api/products')

@product_bp.route('', methods=['GET'])
def get_products():
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', type=int)
    low_stock_only = request.args.get('low_stock', type=bool, default=False)

    query = Product.query

    if search:
        query = query.filter((Product.name.ilike(f'%{search}%')) | (Product.sku.ilike(f'%{search}%')) | (Product.barcode.ilike(f'%{search}%')))
    
    if category_id:
        query = query.filter(Product.category_id == category_id)

    products = query.all()

    if low_stock_only:
        products = [p for p in products if p.stock_quantity <= p.reorder_level]

    return jsonify([p.to_dict() for p in products]), 200

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200

@product_bp.route('', methods=['POST'])
def create_product():
    data = request.get_json() or {}
    
    required_fields = ['sku', 'name', 'category_id', 'unit_price']
    for field in required_fields:
        if field not in data or data[field] is None:
            return jsonify({'error': f'Field {field} is required'}), 400

    if Product.query.filter_by(sku=data['sku']).first():
        return jsonify({'error': f'Product with SKU {data["sku"]} already exists'}), 400

    category = Category.query.get(data['category_id'])
    if not category:
        return jsonify({'error': 'Invalid Category ID'}), 400

    product = Product(
        sku=data['sku'],
        name=data['name'],
        category_id=data['category_id'],
        supplier_id=data.get('supplier_id'),
        cost_price=float(data.get('cost_price', 0.0)),
        unit_price=float(data['unit_price']),
        stock_quantity=int(data.get('stock_quantity', 0)),
        reorder_level=int(data.get('reorder_level', 10)),
        barcode=data.get('barcode', ''),
        description=data.get('description', '')
    )

    db.session.add(product)
    db.session.commit()

    return jsonify(product.to_dict()), 201

@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json() or {}

    if 'sku' in data and data['sku'] != product.sku:
        if Product.query.filter_by(sku=data['sku']).first():
            return jsonify({'error': f'Product with SKU {data["sku"]} already exists'}), 400
        product.sku = data['sku']

    if 'name' in data:
        product.name = data['name']
    if 'category_id' in data:
        product.category_id = data['category_id']
    if 'supplier_id' in data:
        product.supplier_id = data['supplier_id']
    if 'cost_price' in data:
        product.cost_price = float(data['cost_price'])
    if 'unit_price' in data:
        product.unit_price = float(data['unit_price'])
    if 'stock_quantity' in data:
        product.stock_quantity = int(data['stock_quantity'])
    if 'reorder_level' in data:
        product.reorder_level = int(data['reorder_level'])
    if 'barcode' in data:
        product.barcode = data['barcode']
    if 'description' in data:
        product.description = data['description']

    db.session.commit()
    return jsonify(product.to_dict()), 200

@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200
