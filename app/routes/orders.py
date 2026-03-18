from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from app.database.db import db
from app.models.order import Order, OrderItem, OrderStatus, PaymentMethod, PaymentStatus
from app.models.product import Product
from app.utils.decorators import login_required_customer, staff_required
from app.utils.helpers import paginate_query
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

def get_cart():
    """Get cart from session"""
    return session.get('cart', {})

@orders_bp.route('/')
@login_required
def index():
    """Order list page"""
    if current_user.is_admin() or current_user.is_manager() or current_user.is_staff():
        return redirect(url_for('admin.orders'))
    
    # Customer orders
    page = request.args.get('page', 1, type=int)
    query = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc())
    pagination = paginate_query(query, page)
    
    return render_template('customer/orders.html',
                         orders=pagination.items,
                         pagination=pagination)

@orders_bp.route('/create', methods=['POST'])
@login_required_customer
def create():
    """Create order from cart"""
    cart = get_cart()
    
    if not cart:
        flash('Giỏ hàng của bạn đang trống.', 'warning')
        return redirect(url_for('products.cart'))
    
    # Validate cart items
    order_items = []
    total_amount = 0
    
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if not product or not product.can_purchase(quantity):
            flash(f'Sản phẩm {product.name if product else "không tồn tại"} không đủ số lượng.', 'danger')
            return redirect(url_for('products.cart'))
        
        subtotal = float(product.price) * quantity
        total_amount += subtotal
        
        order_items.append({
            'product': product,
            'quantity': quantity,
            'price': product.price
        })
    
    # Create order
    shipping_address = request.form.get('shipping_address', '')
    notes = request.form.get('notes', '')
    payment_method = request.form.get('payment_method', 'cod')
    
    # Validate payment method
    valid_methods = [m.value for m in PaymentMethod]
    if payment_method not in valid_methods:
        payment_method = 'cod'
    
    try:
        order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            status=OrderStatus.PENDING.value,
            payment_method=payment_method,
            payment_status=PaymentStatus.UNPAID.value,
            shipping_address=shipping_address or current_user.address,
            notes=notes
        )
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items and reduce stock
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(order_item)
            
            # Reduce stock
            item_data['product'].reduce_stock(item_data['quantity'])
        
        db.session.commit()
        
        # Clear cart
        session['cart'] = {}
        
        # Redirect based on payment method
        if payment_method == 'cod':
            order.payment_status = PaymentStatus.UNPAID.value
            db.session.commit()
            flash('Đặt hàng thành công! Bạn sẽ thanh toán khi nhận hàng.', 'success')
            return redirect(url_for('orders.detail', id=order.id))
        else:
            # Redirect to payment page for e-payment
            return redirect(url_for('orders.payment', id=order.id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra khi đặt hàng: {str(e)}', 'danger')
        return redirect(url_for('products.cart'))

@orders_bp.route('/<int:id>')
@login_required
def detail(id):
    """Order detail page"""
    order = Order.query.get_or_404(id)
    
    # Check permission
    if not (current_user.is_admin() or current_user.is_manager() or 
            current_user.is_staff() or order.user_id == current_user.id):
        flash('Bạn không có quyền xem đơn hàng này.', 'danger')
        return redirect(url_for('orders.index'))
    
    template = 'admin/order_detail.html' if current_user.can_manage_orders() else 'customer/order_detail.html'
    return render_template(template, order=order)

@orders_bp.route('/<int:id>/payment')
@login_required_customer
def payment(id):
    """Payment page for electronic payment methods"""
    order = Order.query.get_or_404(id)
    
    if order.user_id != current_user.id:
        flash('Bạn không có quyền truy cập đơn hàng này.', 'danger')
        return redirect(url_for('orders.index'))
    
    if order.payment_status == PaymentStatus.PAID.value:
        flash('Đơn hàng này đã được thanh toán.', 'info')
        return redirect(url_for('orders.detail', id=order.id))
    
    # Bank transfer info
    bank_info = {
        'bank_name': 'Techcombank',
        'account_number': '1903 7249 3660 15',
        'account_holder': 'HUA HONG PHUOC',
        'branch': '',
        'transfer_content': f'COFFEE {order.id}'
    }
    
    return render_template('customer/payment.html', 
                         order=order, 
                         bank_info=bank_info)


@orders_bp.route('/<int:id>/confirm-payment', methods=['POST'])
@login_required_customer
def confirm_payment(id):
    """Customer confirms payment was made"""
    order = Order.query.get_or_404(id)
    
    if order.user_id != current_user.id:
        flash('Bạn không có quyền truy cập đơn hàng này.', 'danger')
        return redirect(url_for('orders.index'))
    
    if order.payment_status == PaymentStatus.PAID.value:
        flash('Đơn hàng này đã được thanh toán.', 'info')
        return redirect(url_for('orders.detail', id=order.id))
    
    try:
        order.payment_status = PaymentStatus.PAID.value
        db.session.commit()
        flash('Xác nhận thanh toán thành công! Chúng tôi sẽ xử lý đơn hàng sớm nhất.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('orders.detail', id=order.id))


@orders_bp.route('/<int:id>/cancel', methods=['POST'])
@login_required_customer
def cancel(id):
    """Cancel order (customer only)"""
    order = Order.query.get_or_404(id)
    
    if order.user_id != current_user.id:
        flash('Bạn không có quyền hủy đơn hàng này.', 'danger')
        return redirect(url_for('orders.index'))
    
    if not order.can_cancel():
        flash('Không thể hủy đơn hàng này.', 'danger')
        return redirect(url_for('orders.detail', id=id))
    
    try:
        # Restore stock
        for item in order.items:
            item.product.increase_stock(item.quantity)
        
        order.status = OrderStatus.CANCELLED.value
        db.session.commit()
        flash('Đã hủy đơn hàng thành công.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('orders.detail', id=id))
