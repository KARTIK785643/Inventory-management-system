from flask import Blueprint, request, jsonify
from app.models import db, Supplier

supplier_bp = Blueprint('suppliers', __name__, url_prefix='/api/suppliers')

@supplier_bp.route('', methods=['GET'])
def get_suppliers():
    suppliers = Supplier.query.all()
    return jsonify([s.to_dict() for s in suppliers]), 200

@supplier_bp.route('', methods=['POST'])
def create_supplier():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Supplier name is required'}), 400

    supplier = Supplier(
        name=name,
        contact_email=data.get('contact_email', ''),
        phone=data.get('phone', ''),
        address=data.get('address', '')
    )
    db.session.add(supplier)
    db.session.commit()

    return jsonify(supplier.to_dict()), 201

@supplier_bp.route('/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    data = request.get_json() or {}

    if 'name' in data:
        supplier.name = data['name']
    if 'contact_email' in data:
        supplier.contact_email = data['contact_email']
    if 'phone' in data:
        supplier.phone = data['phone']
    if 'address' in data:
        supplier.address = data['address']

    db.session.commit()
    return jsonify(supplier.to_dict()), 200

@supplier_bp.route('/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    db.session.delete(supplier)
    db.session.commit()
    return jsonify({'message': 'Supplier deleted successfully'}), 200
