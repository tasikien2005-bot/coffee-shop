from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Bạn không có quyền truy cập trang này.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """Decorator to require manager or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_admin() or current_user.is_manager()):
            flash('Bạn không có quyền truy cập trang này.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    """Decorator to require staff, manager or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_manage_orders():
            flash('Bạn không có quyền truy cập trang này.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_customer(f):
    """Decorator to require authenticated customer"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để thêm vào giỏ hàng và đặt hàng.', 'info')
            next_url = request.referrer
            if next_url and (next_url.startswith(request.host_url) or next_url.startswith(request.url_root)):
                return redirect(url_for('auth.login', next=next_url))
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
