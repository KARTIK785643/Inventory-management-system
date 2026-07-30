from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(32), default='staff')  # 'admin' or 'staff'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256), nullable=True)
    products = db.relationship('Product', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'product_count': len(self.products)
        }

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    contact_email = db.Column(db.String(128), nullable=True)
    phone = db.Column(db.String(32), nullable=True)
    address = db.Column(db.String(256), nullable=True)
    products = db.relationship('Product', backref='supplier', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_email': self.contact_email or '',
            'phone': self.phone or '',
            'address': self.address or '',
            'product_count': len(self.products)
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    cost_price = db.Column(db.Float, nullable=False, default=0.0)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=False, default=10)
    barcode = db.Column(db.String(64), nullable=True)
    description = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship('StockTransaction', backref='product', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        is_low_stock = self.stock_quantity <= self.reorder_level
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'N/A',
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else 'N/A',
            'cost_price': round(self.cost_price, 2),
            'unit_price': round(self.unit_price, 2),
            'stock_quantity': self.stock_quantity,
            'reorder_level': self.reorder_level,
            'is_low_stock': is_low_stock,
            'barcode': self.barcode or '',
            'description': self.description or '',
            'total_value': round(self.stock_quantity * self.unit_price, 2),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class StockTransaction(db.Model):
    __tablename__ = 'stock_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    transaction_type = db.Column(db.String(32), nullable=False)  # 'IN', 'OUT', 'ADJUSTMENT'
    quantity = db.Column(db.Integer, nullable=False)
    reference_no = db.Column(db.String(64), nullable=True)
    note = db.Column(db.String(256), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='transactions', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'N/A',
            'product_sku': self.product.sku if self.product else 'N/A',
            'transaction_type': self.transaction_type,
            'quantity': self.quantity,
            'reference_no': self.reference_no or '',
            'note': self.note or '',
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'System',
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    customer_name = db.Column(db.String(128), nullable=False, default='Walk-in Customer')
    customer_email = db.Column(db.String(128), nullable=True)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    tax_amount = db.Column(db.Float, nullable=False, default=0.0)
    discount_amount = db.Column(db.Float, nullable=False, default=0.0)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(32), nullable=False, default='COMPLETED')  # 'COMPLETED', 'CANCELLED'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    user = db.relationship('User', backref='orders', lazy=True)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email or '',
            'subtotal': round(self.subtotal, 2),
            'tax_amount': round(self.tax_amount, 2),
            'discount_amount': round(self.discount_amount, 2),
            'total_amount': round(self.total_amount, 2),
            'status': self.status,
            'item_count': len(self.items),
            'items': [item.to_dict() for item in self.items],
            'username': self.user.username if self.user else 'System',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)

    product = db.relationship('Product', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'N/A',
            'product_sku': self.product.sku if self.product else 'N/A',
            'quantity': self.quantity,
            'unit_price': round(self.unit_price, 2),
            'subtotal': round(self.subtotal, 2)
        }
