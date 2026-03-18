from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.product import Product, Category
from app.utils.helpers import paginate_query
from app.utils.decorators import login_required_customer
from app.database.db import db

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
def index():
    """Product catalog page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category', type=int)
    
    query = Product.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    query = query.order_by(Product.created_at.desc())
    pagination = paginate_query(query, page, per_page=12)
    
    categories = Category.query.all()
    
    return render_template('customer/index.html',
                         products=pagination.items,
                         pagination=pagination,
                         categories=categories,
                         search=search,
                         category_id=category_id)

@products_bp.route('/<int:id>')
def detail(id):
    """Product detail page"""
    product = Product.query.get_or_404(id)
    
    if not product.is_active:
        flash('Sản phẩm không tồn tại.', 'danger')
        return redirect(url_for('products.index'))
    
    return render_template('customer/product_detail.html', product=product)

def get_cart():
    """Get cart from session"""
    return session.get('cart', {})

def save_cart(cart):
    """Save cart to session"""
    session['cart'] = cart

@products_bp.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required_customer
def add_to_cart(product_id):
    """Add product to cart"""
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    if not product.can_purchase(quantity):
        flash('Sản phẩm không đủ số lượng.', 'danger')
        return redirect(url_for('products.detail', id=product_id))
    
    cart = get_cart()
    
    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity
    
    save_cart(cart)
    flash(f'Đã thêm {product.name} vào giỏ hàng!', 'success')
    
    return redirect(request.referrer or url_for('products.index'))

@products_bp.route('/cart')
@login_required_customer
def cart():
    """Shopping cart page"""
    cart = get_cart()
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product and product.is_active:
            subtotal = float(product.price) * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
    
    return render_template('customer/cart.html', cart_items=cart_items, total=total)

@products_bp.route('/cart/update', methods=['POST'])
@login_required_customer
def update_cart():
    """Update cart item quantity"""
    cart = get_cart()
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 0))
    
    if quantity <= 0:
        cart.pop(str(product_id), None)
    else:
        product = Product.query.get(int(product_id))
        if product and product.can_purchase(quantity):
            cart[str(product_id)] = quantity
        else:
            flash('Sản phẩm không đủ số lượng.', 'danger')
    
    save_cart(cart)
    return redirect(url_for('products.cart'))

@products_bp.route('/cart/remove/<int:product_id>', methods=['POST'])
@login_required_customer
def remove_from_cart(product_id):
    """Remove product from cart"""
    cart = get_cart()
    cart.pop(str(product_id), None)
    save_cart(cart)
    flash('Đã xóa sản phẩm khỏi giỏ hàng.', 'info')
    return redirect(url_for('products.cart'))

@products_bp.route('/cart/clear', methods=['POST'])
@login_required_customer
def clear_cart():
    """Clear cart"""
    save_cart({})
    flash('Đã xóa tất cả sản phẩm khỏi giỏ hàng.', 'info')
    return redirect(url_for('products.cart'))
