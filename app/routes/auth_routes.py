from flask import Blueprint, request, jsonify
from app.models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200

@auth_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    full_name = data.get('full_name', username)
    role = data.get('role', 'staff')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    new_user = User(username=username, full_name=full_name, role=role)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.to_dict()), 201
