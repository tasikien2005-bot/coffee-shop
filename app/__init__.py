from flask import Flask, render_template, send_from_directory
from flask.cli import with_appcontext
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from app.database.db import db
from config import config
import os

# Initialize extensions
login_manager = LoginManager()
csrf = CSRFProtect()

def register_cli(app):
    @app.cli.command('init-db')
    @with_appcontext
    def init_db_command():
        """Initialize database with roles and sample data"""
        from app.models.user import User, Role
        from app.models.product import Product, Category
        from app.models.order import Order, OrderItem
        from app.models.notification import Notification
        from app.models.activity_log import ActivityLog

        db.create_all()

        # Create roles
        roles_data = [
            {'name': 'admin', 'description': 'Quản trị viên hệ thống'},
            {'name': 'manager', 'description': 'Quản lý cửa hàng'},
            {'name': 'staff', 'description': 'Nhân viên'},
            {'name': 'customer', 'description': 'Khách hàng'}
        ]

        for role_data in roles_data:
            role = Role.query.filter_by(name=role_data['name']).first()
            if not role:
                role = Role(**role_data)
                db.session.add(role)

        db.session.commit()
        print("✓ Roles created")

        # Create admin user
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@coffeeshop.com',
                    full_name='Quản trị viên',
                    role_id=admin_role.id
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✓ Admin user created (username: admin, password: admin123)")

        # Create sample categories (packaged products)
        categories_data = [
            {'name': 'Cà phê hạt nguyên chất', 'description': 'Cà phê hạt, phù hợp xay theo khẩu vị'},
            {'name': 'Cà phê bột pha phin', 'description': 'Cà phê xay sẵn để pha phin'},
            {'name': 'Cà phê hòa tan', 'description': 'Cà phê hòa tan đóng gói'},
            {'name': 'Cà phê cao cấp', 'description': 'Dòng cao cấp, chọn lọc hạt'},
            {'name': 'Combo tiết kiệm', 'description': 'Combo nhiều sản phẩm, giá tốt'}
        ]

        for cat_data in categories_data:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(**cat_data)
                db.session.add(category)

        db.session.commit()
        print("✓ Categories created")

        # Create sample products
        category_map = {c.name: c.id for c in Category.query.all()}
        products_data = [
            {
                'name': 'Cà phê hạt Robusta (Bịch 500g)',
                'description': 'Cà phê hạt nguyên chất, phù hợp xay pha phin.',
                'price': 165000,
                'stock': 50,
                'category_name': 'Cà phê hạt nguyên chất'
            },
            {
                'name': 'Cà phê bột rang mộc (Bịch 250g)',
                'description': 'Bột rang mộc, đậm vị, pha phin.',
                'price': 85000,
                'stock': 60,
                'category_name': 'Cà phê bột pha phin'
            },
            {
                'name': 'Cà phê hòa tan 3in1 (Gói 20 gói)',
                'description': 'Cà phê hòa tan đóng gói, tiện mang theo.',
                'price': 62000,
                'stock': 80,
                'category_name': 'Cà phê hòa tan'
            },
            {
                'name': 'Cà phê đặc sản Arabica (Bịch 250g)',
                'description': 'Dòng cao cấp, hương thơm trái cây.',
                'price': 210000,
                'stock': 40,
                'category_name': 'Cà phê cao cấp'
            },
            {
                'name': 'Combo tiết kiệm 3 bịch (1kg)',
                'description': 'Combo 3 bịch cà phê rang xay, tiết kiệm hơn.',
                'price': 285000,
                'stock': 30,
                'category_name': 'Combo tiết kiệm'
            },
            {
                'name': 'Trung Nguyên G7 (Hộp 16 gói)',
                'description': 'Cà phê hòa tan Trung Nguyên G7, hộp 16 gói, thơm đậm đà',
                'price': 65000,
                'stock': 80,
                'category_name': 'Cà phê hòa tan',
                'image_url': 'images/coffee-boxes/coffee-box-trung-nguyen.svg'
            },
            {
                'name': 'Nestlé Nescafé (Hộp 20 gói)',
                'description': 'Cà phê hòa tan Nestlé Nescafé, hộp 20 gói',
                'price': 72000,
                'stock': 60,
                'category_name': 'Cà phê hòa tan',
                'image_url': 'images/coffee-boxes/coffee-box-nescafe.svg'
            },
            {
                'name': 'Vinacafe (Hộp 20 gói)',
                'description': 'Cà phê hòa tan Vinacafe truyền thống, hộp 20 gói',
                'price': 58000,
                'stock': 70,
                'category_name': 'Cà phê hòa tan',
                'image_url': 'images/coffee-boxes/coffee-box-vinacafe.svg'
            },
        ]

        for prod_data in products_data:
            product = Product.query.filter_by(name=prod_data['name']).first()
            if not product:
                category_id = category_map.get(prod_data['category_name'])
                if not category_id:
                    print(f"! Skip product '{prod_data['name']}' (missing category)")
                    continue
                product = Product(
                    name=prod_data['name'],
                    description=prod_data['description'],
                    price=prod_data['price'],
                    stock=prod_data['stock'],
                    category_id=category_id,
                    image_url=prod_data.get('image_url')
                )
                db.session.add(product)

        db.session.commit()
        print("✓ Sample products created")
        print("\n✓ Database initialization completed!")
        print("\nDefault login credentials:")
        print("  Username: admin")
        print("  Password: admin123")

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config.get(config_name, config['default']))
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục.'
    login_manager.login_message_category = 'info'
    # csrf.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.products import products_bp
    from app.routes.orders import orders_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.notifications import notifications_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    
    # Register custom filters
    @app.template_filter('format_currency')
    def format_currency(value):
        """Format number with thousand separator (dot) and currency symbol"""
        try:
            return "{:,.0f}đ".format(float(value)).replace(',', '.')
        except (ValueError, TypeError):
            return f"{value}đ"

    @app.context_processor
    def inject_notification_count():
        """Provide unread notification count for customers."""
        packaged_categories = app.config.get('PACKAGED_CATEGORY_NAMES', [])
        if not current_user.is_authenticated or current_user.can_manage_orders():
            return {
                'unread_notification_count': 0,
                'packaged_categories': packaged_categories
            }
        from app.models.notification import Notification
        count = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()
        return {
            'unread_notification_count': count,
            'packaged_categories': packaged_categories
        }
    
    # Favicon (nhiều trình duyệt tự gọi /favicon.ico)
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.static_folder, 'images'),
            'favicon.svg',
            mimetype='image/svg+xml'
        )
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Register user loader
    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login"""
        from app.models.user import User
        return User.query.get(int(user_id))

    register_cli(app)

    return app
