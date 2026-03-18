from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.database.db import db
from app.models.user import User, Role
from app.utils.decorators import login_required_customer

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Tài khoản của bạn đã bị khóa.', 'danger')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            flash(f'Chào mừng trở lại, {user.username}!', 'success')
            
            # Redirect based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.is_admin() or user.is_manager() or user.is_staff():
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('dashboard.index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Bạn đã đăng xuất thành công.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration (customer only)"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('Vui lòng điền đầy đủ thông tin bắt buộc.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp.', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự.', 'danger')
            return render_template('auth/register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng.', 'danger')
            return render_template('auth/register.html')
        
        # Get customer role (id=4)
        customer_role = Role.query.filter_by(name='customer').first()
        if not customer_role:
            flash('Lỗi hệ thống. Vui lòng thử lại sau.', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role_id=customer_role.id
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra. Vui lòng thử lại.', 'danger')
    
    return render_template('auth/register.html')
