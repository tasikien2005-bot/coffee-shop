import os
from app import create_app
from app.database.db import db
from app.models.user import User, Role
from app.models.product import Product, Category
from werkzeug.security import generate_password_hash


def init_database():
    app = create_app()

    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created")

        # ===== ROLES =====
        roles_data = [
            ('admin', 'Quản trị viên hệ thống'),
            ('manager', 'Quản lý cửa hàng'),
            ('staff', 'Nhân viên'),
            ('customer', 'Khách hàng')
        ]

        for name, desc in roles_data:
            if not Role.query.filter_by(name=name).first():
                db.session.add(Role(name=name, description=desc))

        db.session.commit()

        # ===== ADMIN USER =====
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role and not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@coffeeshop.com',
                full_name='Quản trị viên',
                role_id=admin_role.id,
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created")

        # ===== CATEGORIES =====
        categories = [
            ('Cà phê hạt nguyên chất', 'Cà phê hạt, phù hợp xay theo khẩu vị'),
            ('Cà phê bột pha phin', 'Cà phê xay sẵn để pha phin'),
            ('Cà phê hòa tan', 'Cà phê hòa tan đóng gói'),
            ('Cà phê cao cấp', 'Dòng cao cấp, chọn lọc hạt'),
            ('Combo tiết kiệm', 'Combo nhiều sản phẩm, giá tốt')
        ]

        for name, desc in categories:
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name, description=desc))

        db.session.commit()

        category_map = {
            c.name: c.id for c in Category.query.all()
        }

        # ===== PRODUCTS =====
        products = [
            ('Cà phê hạt Robusta (Bịch 500g)', 165000, 'Cà phê hạt nguyên chất'),
            ('Cà phê bột rang mộc (Bịch 250g)', 85000, 'Cà phê bột pha phin'),
            ('Cà phê hòa tan 3in1 (Gói 20 gói)', 62000, 'Cà phê hòa tan'),
            ('Cà phê đặc sản Arabica (Bịch 250g)', 210000, 'Cà phê cao cấp'),
            ('Combo tiết kiệm 3 bịch (1kg)', 285000, 'Combo tiết kiệm'),
            ('Trung Nguyên G7 (Hộp 16 gói)', 65000, 'Cà phê hòa tan'),
        ]

        for name, price, cat_name in products:
            if not Product.query.filter_by(name=name).first():
                db.session.add(Product(
                    name=name,
                    price=price,
                    stock=100,
                    category_id=category_map[cat_name]
                ))

        db.session.commit()

        print("\n✓ Database initialized successfully")
        print("Login: admin / admin123")


if __name__ == '__main__':
    init_database()
