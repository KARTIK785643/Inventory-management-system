from datetime import datetime, timedelta
import random
from app import create_app
from app.models import db, User, Category, Supplier, Product, StockTransaction, Order, OrderItem

def seed_database():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("Seeding database...")

        # 1. Users
        admin = User(username='admin', full_name='System Administrator', role='admin')
        admin.set_password('admin123')
        
        staff = User(username='staff', full_name='John Store Manager', role='staff')
        staff.set_password('staff123')

        db.session.add_all([admin, staff])
        db.session.commit()

        # 2. Categories
        cat_electronics = Category(name='Electronics', description='Gadgets, computers, and electronic accessories')
        cat_furniture = Category(name='Furniture', description='Office and home furniture items')
        cat_stationery = Category(name='Stationery', description='Office supplies, paper, and writing instruments')
        cat_hardware = Category(name='Hardware', description='Tools, cables, and mechanical parts')

        db.session.add_all([cat_electronics, cat_furniture, cat_stationery, cat_hardware])
        db.session.commit()

        # 3. Suppliers
        sup_tech = Supplier(name='TechDistro Global', contact_email='sales@techdistro.com', phone='+1-800-555-0192', address='100 Silicon Way, CA')
        sup_office = Supplier(name='Apex Office Supplies', contact_email='orders@apexoffice.com', phone='+1-800-555-4821', address='45 Industrial Pkwy, NY')
        sup_hardware = Supplier(name='Omni Hardware Corp', contact_email='info@omnihardware.com', phone='+1-800-555-9302', address='77 Tool Factory Rd, TX')

        db.session.add_all([sup_tech, sup_office, sup_hardware])
        db.session.commit()

        # 4. Products
        products_data = [
            # Electronics
            {'sku': 'ELE-001', 'name': 'Wireless Ergonomic Mouse', 'cat': cat_electronics, 'sup': sup_tech, 'cost': 18.50, 'unit': 39.99, 'qty': 45, 'reorder': 10, 'barcode': '890123456781'},
            {'sku': 'ELE-002', 'name': 'Mechanical RGB Keyboard', 'cat': cat_electronics, 'sup': sup_tech, 'cost': 42.00, 'unit': 89.99, 'qty': 18, 'reorder': 5, 'barcode': '890123456782'},
            {'sku': 'ELE-003', 'name': '27-inch 4K UHD Monitor', 'cat': cat_electronics, 'sup': sup_tech, 'cost': 190.00, 'unit': 329.99, 'qty': 4, 'reorder': 8, 'barcode': '890123456783'}, # Low Stock
            {'sku': 'ELE-004', 'name': 'USB-C Multi-port Hub', 'cat': cat_electronics, 'sup': sup_tech, 'cost': 12.00, 'unit': 29.99, 'qty': 3, 'reorder': 15, 'barcode': '890123456784'}, # Low Stock

            # Furniture
            {'sku': 'FUR-001', 'name': 'Ergonomic Mesh Office Chair', 'cat': cat_furniture, 'sup': sup_office, 'cost': 85.00, 'unit': 179.99, 'qty': 12, 'reorder': 5, 'barcode': '890123456785'},
            {'sku': 'FUR-002', 'name': 'Motorized Standing Desk', 'cat': cat_furniture, 'sup': sup_office, 'cost': 210.00, 'unit': 449.99, 'qty': 6, 'reorder': 3, 'barcode': '890123456786'},

            # Stationery
            {'sku': 'STA-001', 'name': 'Premium Heavy Duty Paper (500 Sheets)', 'cat': cat_stationery, 'sup': sup_office, 'cost': 4.20, 'unit': 9.50, 'qty': 120, 'reorder': 20, 'barcode': '890123456787'},
            {'sku': 'STA-002', 'name': 'Gel Pen Box (12 Pack)', 'cat': cat_stationery, 'sup': sup_office, 'cost': 3.10, 'unit': 7.99, 'qty': 8, 'reorder': 15, 'barcode': '890123456788'}, # Low stock
            {'sku': 'STA-003', 'name': 'Executive Leather Notebook', 'cat': cat_stationery, 'sup': sup_office, 'cost': 6.50, 'unit': 16.00, 'qty': 35, 'reorder': 10, 'barcode': '890123456789'},

            # Hardware
            {'sku': 'HDW-001', 'name': 'Cat6 High Speed Ethernet Cable 50ft', 'cat': cat_hardware, 'sup': sup_hardware, 'cost': 5.80, 'unit': 14.99, 'qty': 50, 'reorder': 12, 'barcode': '890123456790'},
            {'sku': 'HDW-002', 'name': 'Precision Tool Set (45 Pieces)', 'cat': cat_hardware, 'sup': sup_hardware, 'cost': 16.00, 'unit': 39.95, 'qty': 22, 'reorder': 8, 'barcode': '890123456791'}
        ]

        db_products = []
        for p_info in products_data:
            p = Product(
                sku=p_info['sku'],
                name=p_info['name'],
                category_id=p_info['cat'].id,
                supplier_id=p_info['sup'].id,
                cost_price=p_info['cost'],
                unit_price=p_info['unit'],
                stock_quantity=p_info['qty'],
                reorder_level=p_info['reorder'],
                barcode=p_info['barcode'],
                description=f"High quality {p_info['name']} for business and home use."
            )
            db.session.add(p)
            db_products.append(p)

        db.session.commit()

        # 5. Initial Stock IN Transactions
        for p in db_products:
            tx = StockTransaction(
                product_id=p.id,
                transaction_type='IN',
                quantity=p.stock_quantity + 10,
                reference_no='PO-INITIAL-001',
                note='Initial Stock Intake',
                user_id=admin.id,
                timestamp=datetime.utcnow() - timedelta(days=15)
            )
            db.session.add(tx)
        
        db.session.commit()

        # 6. Sample Orders / Invoices over the past 7 days for sales chart
        customers = [
            ('Alice Smith', 'alice.smith@example.com'),
            ('Bob Johnson', 'bob.j@example.com'),
            ('Corporate Tech Ltd', 'billing@corptech.com'),
            ('David Miller', 'david.m@example.com'),
            ('Emma Watson', 'emma.w@example.com'),
            ('Frank Wright', 'frank@example.com')
        ]

        now = datetime.utcnow()
        for i in range(6, -1, -1):
            order_date = now - timedelta(days=i, hours=random.randint(1, 8))
            num_orders_today = random.randint(1, 3)
            
            for j in range(num_orders_today):
                cust_name, cust_email = random.choice(customers)
                selected_products = random.sample(db_products, k=random.randint(1, 3))
                
                inv_no = f"INV-2026{i:02d}{j:02d}{random.randint(10,99)}"
                subtotal = 0.0
                order_items = []

                for prod in selected_products:
                    qty = random.randint(1, 2)
                    unit_p = prod.unit_price
                    line_total = round(qty * unit_p, 2)
                    subtotal += line_total
                    order_items.append({
                        'product_id': prod.id,
                        'qty': qty,
                        'unit_price': unit_p,
                        'subtotal': line_total
                    })

                tax = round(subtotal * 0.05, 2)
                discount = round(random.choice([0.0, 5.0, 10.0]) if subtotal > 50 else 0.0, 2)
                total = max(0.0, round(subtotal + tax - discount, 2))

                order = Order(
                    invoice_number=inv_no,
                    customer_name=cust_name,
                    customer_email=cust_email,
                    subtotal=subtotal,
                    tax_amount=tax,
                    discount_amount=discount,
                    total_amount=total,
                    status='COMPLETED',
                    created_at=order_date,
                    user_id=staff.id
                )
                db.session.add(order)
                db.session.flush()

                for item in order_items:
                    oi = OrderItem(
                        order_id=order.id,
                        product_id=item['product_id'],
                        quantity=item['qty'],
                        unit_price=item['unit_price'],
                        subtotal=item['subtotal']
                    )
                    db.session.add(oi)

        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
