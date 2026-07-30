from flask import Flask
from app.config import Config
from app.models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Enable simple CORS for desktop API calls
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.product_routes import product_bp
    from app.routes.category_routes import category_bp
    from app.routes.supplier_routes import supplier_bp
    from app.routes.stock_routes import stock_bp
    from app.routes.order_routes import order_bp
    from app.routes.report_routes import report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(supplier_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(report_bp)

    with app.app_context():
        db.create_all()

    return app
