from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from app.database.db import db
from app.models.product import Product, Category
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.user import User, Role
from app.models.activity_log import ActivityLog
from app.utils.decorators import admin_required, manager_required, staff_required
from app.utils.helpers import paginate_query, format_currency, save_uploaded_file
from app.utils.notifications import build_order_status_notification
from sqlalchemy import func, desc, or_
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


def _get_product_form_categories(product=None):
    """Get categories shown in product form."""
    query = Category.query
    packaged_names = current_app.config.get('PACKAGED_CATEGORY_NAMES', [])
    if packaged_names:
        query = query.filter(Category.name.in_(packaged_names))
    else:
        hidden_names = current_app.config.get('HIDDEN_PRODUCT_CATEGORIES', [])
        if hidden_names:
            query = query.filter(~Category.name.in_(hidden_names))
    categories = query.order_by(Category.name).all()
    if product and product.category and product.category not in categories:
        categories.append(product.category)
    return categories

@admin_bp.route('/dashboard')
@login_required
@staff_required
def dashboard():
    """Admin dashboard with statistics"""
    # Statistics
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_users = User.query.count()
    total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    # Orders by status
    orders_by_status = [
        {'status': row[0], 'count': row[1]}
        for row in db.session.query(
            Order.status,
            func.count(Order.id)
        ).group_by(Order.status).all()
    ]
    
    # Revenue by day (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    # Use DATE() function for MySQL compatibility
    rows = (
        db.session.query(
            func.date(Order.created_at).label("data"),
            func.sum(Order.total_amount).label("revenue")
        )
        .filter(Order.created_at >= seven_days_ago)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )

    revenue_by_day =  [
        {
            "date": d.strftime("%Y-%m-%d"),
            "revenue": float(r or 0)
        }
        for d, r in rows
    ]
    
    # Low stock products
    low_stock_products = Product.query.filter(Product.stock < 10).limit(5).all()

    # Recent activity
    recent_activity = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         total_orders=total_orders,
                         total_users=total_users,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders,
                         orders_by_status=orders_by_status,
                         revenue_by_day=revenue_by_day,
                         low_stock_products=low_stock_products,
                         recent_activity=recent_activity)

@admin_bp.route('/products')
@login_required
@staff_required
def products():
    """Product management page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category', type=int)
    
    query = Product.query
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    query = query.order_by(Product.created_at.desc())
    pagination = paginate_query(query, page)
    
    categories = Category.query.all()
    
    return render_template('admin/products.html',
                         products=pagination.items,
                         pagination=pagination,
                         categories=categories,
                         search=search,
                         category_id=category_id)

@admin_bp.route('/products/create', methods=['GET', 'POST'])
@login_required
@staff_required
def create_product():
    """Create new product"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')
        category_id = request.form.get('category_id')
        image_file = request.files.get('image')
        
        if not all([name, price, category_id]):
            flash('Vui lòng điền đầy đủ thông tin bắt buộc.', 'danger')
            return redirect(url_for('admin.create_product'))
        
        image_url = None
        if image_file and image_file.filename:
            image_url = save_uploaded_file(image_file, folder='products')
            if not image_url:
                flash('Định dạng hình ảnh không hợp lệ.', 'danger')
                return redirect(url_for('admin.create_product'))

        try:
            product = Product(
                name=name,
                description=description,
                price=float(price),
                stock=int(stock) if stock else 0,
                category_id=int(category_id),
                image_url=image_url
            )
            db.session.add(product)
            db.session.flush()
            ActivityLog.log(current_user.id, 'create_product', 'product', product.id,
                            f'Tạo sản phẩm "{name}"')
            db.session.commit()
            flash('Tạo sản phẩm thành công!', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    categories = _get_product_form_categories()
    return render_template('admin/product_form.html', categories=categories)

@admin_bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@staff_required
def edit_product(id):
    """Edit product"""
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))
        product.category_id = int(request.form.get('category_id'))
        product.is_active = bool(request.form.get('is_active'))
        image_file = request.files.get('image')

        if image_file and image_file.filename:
            image_url = save_uploaded_file(image_file, folder='products')
            if not image_url:
                flash('Định dạng hình ảnh không hợp lệ.', 'danger')
                return redirect(url_for('admin.edit_product', id=id))
            product.image_url = image_url
        
        try:
            ActivityLog.log(current_user.id, 'update_product', 'product', product.id,
                            f'Sửa sản phẩm "{product.name}"')
            db.session.commit()
            flash('Cập nhật sản phẩm thành công!', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    categories = _get_product_form_categories(product)
    return render_template('admin/product_form.html', product=product, categories=categories)

@admin_bp.route('/products/<int:id>/delete', methods=['POST'])
@login_required
@staff_required
def delete_product(id):
    """Delete product, or deactivate if it has order history"""
    product = Product.query.get_or_404(id)
    
    try:
        product_name = product.name
        if product.order_items:
            product.is_active = False
            ActivityLog.log(current_user.id, 'delete_product', 'product', product.id,
                            f'Ẩn sản phẩm "{product_name}" (có đơn hàng)')
            db.session.commit()
            flash(f'Sản phẩm "{product_name}" đã có đơn hàng nên được ẩn thay vì xóa (để giữ lịch sử).', 'warning')
        else:
            ActivityLog.log(current_user.id, 'delete_product', 'product', id,
                            f'Xóa sản phẩm "{product_name}"')
            db.session.delete(product)
            db.session.commit()
            flash('Xóa sản phẩm thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('admin.products'))

@admin_bp.route('/orders')
@login_required
@staff_required
def orders():
    """Order management page"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Order.query
    
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(Order.created_at.desc())
    pagination = paginate_query(query, page)
    
    return render_template('admin/orders.html',
                         orders=pagination.items,
                         pagination=pagination,
                         status=status)

@admin_bp.route('/orders/<int:id>')
@login_required
@staff_required
def order_detail(id):
    """Order detail page"""
    order = Order.query.get_or_404(id)
    return render_template('admin/order_detail.html', order=order)

@admin_bp.route('/orders/<int:id>/update-status', methods=['POST'])
@login_required
@staff_required
def update_order_status(id):
    """Update order status"""
    order = Order.query.get_or_404(id)
    new_status = request.form.get('status')
    
    if not order.can_update_status(new_status):
        flash('Không thể cập nhật trạng thái đơn hàng.', 'danger')
        return redirect(url_for('admin.order_detail', id=id))
    
    old_status = order.status
    order.status = new_status
    order.processed_by = current_user.id
    notification = build_order_status_notification(order, new_status)
    if notification:
        db.session.add(notification)
    ActivityLog.log(current_user.id, 'update_order', 'order', order.id,
                    f'Đơn #{order.id}: {old_status} → {new_status}')
    try:
        db.session.commit()
        flash('Cập nhật trạng thái đơn hàng thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('admin.order_detail', id=id))


@admin_bp.route('/orders/<int:id>/update-payment', methods=['POST'])
@login_required
@staff_required
def update_payment_status(id):
    """Update order payment status"""
    order = Order.query.get_or_404(id)
    new_payment_status = request.form.get('payment_status')
    
    valid_statuses = [s.value for s in PaymentStatus]
    if new_payment_status not in valid_statuses:
        flash('Trạng thái thanh toán không hợp lệ.', 'danger')
        return redirect(url_for('admin.order_detail', id=id))
    
    old_payment = order.payment_status
    order.payment_status = new_payment_status
    ActivityLog.log(current_user.id, 'update_payment', 'order', order.id,
                    f'Đơn #{order.id}: TT {old_payment} → {new_payment_status}')
    try:
        db.session.commit()
        flash('Cập nhật trạng thái thanh toán thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('admin.order_detail', id=id))


@admin_bp.route('/users')
@login_required
@manager_required
def users():
    """User management page"""
    page = request.args.get('page', 1, type=int)
    role_id = request.args.get('role', type=int)
    search = request.args.get('search', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            or_(
                User.username.contains(search),
                User.email.contains(search),
                User.full_name.contains(search)
            )
        )
    
    if role_id:
        query = query.filter_by(role_id=role_id)
    
    query = query.order_by(User.created_at.desc())
    pagination = paginate_query(query, page)
    
    roles = Role.query.all()

    user_ids = [u.id for u in pagination.items]
    orders_processed = dict(
        db.session.query(Order.processed_by, func.count(Order.id))
        .filter(Order.processed_by.in_(user_ids))
        .group_by(Order.processed_by).all()
    ) if user_ids else {}

    actions_count = dict(
        db.session.query(ActivityLog.user_id, func.count(ActivityLog.id))
        .filter(ActivityLog.user_id.in_(user_ids))
        .group_by(ActivityLog.user_id).all()
    ) if user_ids else {}

    return render_template('admin/users.html',
                         users=pagination.items,
                         pagination=pagination,
                         roles=roles,
                         role_id=role_id,
                         search=search,
                         orders_processed=orders_processed,
                         actions_count=actions_count)


@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
@manager_required
def update_user_role(user_id):
    """Update a user's role"""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Bạn không thể thay đổi vai trò của chính mình.', 'danger')
        return redirect(url_for('admin.users'))

    new_role_id = request.form.get('role_id', type=int)
    role = Role.query.get(new_role_id)
    if not role:
        flash('Vai trò không hợp lệ.', 'danger')
        return redirect(url_for('admin.users'))

    if role.name == 'admin' and not current_user.is_admin():
        flash('Chỉ admin mới có thể gán quyền admin.', 'danger')
        return redirect(url_for('admin.users'))

    if user.is_admin() and not current_user.is_admin():
        flash('Chỉ admin mới có thể thay đổi vai trò của admin khác.', 'danger')
        return redirect(url_for('admin.users'))

    old_role = user.role.name
    user.role_id = new_role_id
    ActivityLog.log(current_user.id, 'change_role', 'user', user.id,
                    f'Đổi vai trò "{user.username}": {old_role} → {role.name}')
    try:
        db.session.commit()
        flash(f'Đã cập nhật vai trò của "{user.username}" thành "{role.name}".', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')

    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@manager_required
def toggle_user_active(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Bạn không thể khóa tài khoản của chính mình.', 'danger')
        return redirect(url_for('admin.users'))

    if user.is_admin() and not current_user.is_admin():
        flash('Chỉ admin mới có thể khóa tài khoản admin.', 'danger')
        return redirect(url_for('admin.users'))

    user.is_active = not user.is_active
    status_text = 'mở khóa' if user.is_active else 'khóa'
    ActivityLog.log(current_user.id, 'toggle_user', 'user', user.id,
                    f'Đã {status_text} tài khoản "{user.username}"')
    try:
        db.session.commit()
        flash(f'Đã {status_text} tài khoản "{user.username}".', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')

    return redirect(url_for('admin.users'))


@admin_bp.route('/users/create', methods=['POST'])
@login_required
@manager_required
def create_user():
    """Create a new staff/manager account"""
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    full_name = request.form.get('full_name', '').strip()
    new_role_id = request.form.get('role_id', type=int)

    if not all([username, email, password, new_role_id]):
        flash('Vui lòng điền đầy đủ thông tin.', 'danger')
        return redirect(url_for('admin.users'))

    role = Role.query.get(new_role_id)
    if not role:
        flash('Vai trò không hợp lệ.', 'danger')
        return redirect(url_for('admin.users'))

    if role.name == 'admin' and not current_user.is_admin():
        flash('Chỉ admin mới có thể tạo tài khoản admin.', 'danger')
        return redirect(url_for('admin.users'))

    if User.query.filter((User.username == username) | (User.email == email)).first():
        flash('Tên đăng nhập hoặc email đã tồn tại.', 'danger')
        return redirect(url_for('admin.users'))

    try:
        user = User(
            username=username,
            email=email,
            full_name=full_name or None,
            role_id=new_role_id
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        ActivityLog.log(current_user.id, 'create_user', 'user', user.id,
                        f'Tạo tài khoản "{username}" ({role.name})')
        db.session.commit()
        flash(f'Đã tạo tài khoản "{username}" với vai trò {role.name}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')

    return redirect(url_for('admin.users'))


@admin_bp.route('/activity-log')
@login_required
@manager_required
def activity_log():
    """Activity log page"""
    page = request.args.get('page', 1, type=int)
    user_filter = request.args.get('user_id', type=int)

    query = ActivityLog.query
    if user_filter:
        query = query.filter_by(user_id=user_filter)
    query = query.order_by(ActivityLog.created_at.desc())
    pagination = paginate_query(query, page, per_page=20)

    staff_users = User.query.join(Role).filter(
        Role.name.in_(['admin', 'manager', 'staff'])
    ).order_by(User.username).all()

    return render_template('admin/activity_log.html',
                         logs=pagination.items,
                         pagination=pagination,
                         staff_users=staff_users,
                         user_filter=user_filter)


@admin_bp.route('/categories')
@login_required
@staff_required
def categories():
    """Category management"""
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/create', methods=['POST'])
@login_required
@staff_required
def create_category():
    """Create category"""
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name:
        flash('Vui lòng nhập tên danh mục.', 'danger')
        return redirect(url_for('admin.categories'))
    
    if Category.query.filter_by(name=name).first():
        flash('Danh mục đã tồn tại.', 'danger')
        return redirect(url_for('admin.categories'))
    
    try:
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        flash('Tạo danh mục thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('admin.categories'))
