from flask import Blueprint, request, jsonify
from app.models import db, Category

category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

@category_bp.route('', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories]), 200

@category_bp.route('', methods=['POST'])
def create_category():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Category name is required'}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({'error': f'Category {name} already exists'}), 400

    category = Category(name=name, description=data.get('description', ''))
    db.session.add(category)
    db.session.commit()

    return jsonify(category.to_dict()), 201

@category_bp.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json() or {}
    
    if 'name' in data and data['name'] != category.name:
        if Category.query.filter_by(name=data['name']).first():
            return jsonify({'error': f'Category {data["name"]} already exists'}), 400
        category.name = data['name']

    if 'description' in data:
        category.description = data['description']

    db.session.commit()
    return jsonify(category.to_dict()), 200

@category_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.products and len(category.products) > 0:
        return jsonify({'error': 'Cannot delete category containing products'}), 400

    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'}), 200
