from datetime import datetime
from enum import Enum
from app.database.db import db

class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PROCESSING = 'processing'
    SHIPPING = 'shipping'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class PaymentMethod(Enum):
    """Payment method enumeration"""
    COD = 'cod'
    BANK_TRANSFER = 'bank_transfer'
    MOMO = 'momo'
    ZALOPAY = 'zalopay'
    VNPAY = 'vnpay'

class PaymentStatus(Enum):
    """Payment status enumeration"""
    UNPAID = 'unpaid'
    PAID = 'paid'
    FAILED = 'failed'
    REFUNDED = 'refunded'

class Order(db.Model):
    """Order model"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default=OrderStatus.PENDING.value, nullable=False)
    payment_method = db.Column(db.String(20), default=PaymentMethod.COD.value)
    payment_status = db.Column(db.String(20), default=PaymentStatus.UNPAID.value)
    shipping_address = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    processor = db.relationship('User', foreign_keys=[processed_by], backref='processed_orders')
    
    def calculate_total(self):
        """Calculate total from order items"""
        total = sum(item.subtotal for item in self.items)
        self.total_amount = total
        return total
    
    def format_total(self):
        """Format total as currency"""
        return "{:,.0f}đ".format(float(self.total_amount)).replace(',', '.')
    
    def get_status_display(self):
        """Get human-readable status"""
        status_map = {
            'pending': 'Chờ xử lý',
            'confirmed': 'Đã xác nhận',
            'processing': 'Đang xử lý',
            'shipping': 'Đang giao hàng',
            'delivered': 'Đã giao hàng',
            'cancelled': 'Đã hủy'
        }
        return status_map.get(self.status, self.status)
    
    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.status in [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]

    def get_payment_method_display(self):
        """Get human-readable payment method"""
        method_map = {
            'cod': 'Thanh toán khi nhận hàng (COD)',
            'bank_transfer': 'Chuyển khoản ngân hàng',
            'momo': 'Ví MoMo',
            'zalopay': 'ZaloPay',
            'vnpay': 'VNPay',
        }
        return method_map.get(self.payment_method, self.payment_method or 'COD')

    def get_payment_status_display(self):
        """Get human-readable payment status"""
        status_map = {
            'unpaid': 'Chưa thanh toán',
            'paid': 'Đã thanh toán',
            'failed': 'Thanh toán thất bại',
            'refunded': 'Đã hoàn tiền',
        }
        return status_map.get(self.payment_status, self.payment_status or 'Chưa thanh toán')
    
    def get_valid_transitions(self):
        """Get valid next statuses for current status"""
        valid_transitions = {
            OrderStatus.PENDING.value: [OrderStatus.CONFIRMED.value, OrderStatus.CANCELLED.value],
            OrderStatus.CONFIRMED.value: [OrderStatus.PROCESSING.value, OrderStatus.CANCELLED.value],
            OrderStatus.PROCESSING.value: [OrderStatus.SHIPPING.value],
            OrderStatus.SHIPPING.value: [OrderStatus.DELIVERED.value],
            OrderStatus.DELIVERED.value: [],
            OrderStatus.CANCELLED.value: []
        }
        return valid_transitions.get(self.status, [])

    def can_update_status(self, new_status):
        """Check if status can be updated"""
        return new_status in self.get_valid_transitions()
    
    def __repr__(self):
        return f'<Order {self.id} - {self.status}>'

class OrderItem(db.Model):
    """Order item model"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Price at time of order
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return float(self.price) * self.quantity
    
    def format_subtotal(self):
        """Format subtotal as currency"""
        return "{:,.0f}đ".format(float(self.subtotal)).replace(',', '.')
    
    def __repr__(self):
        return f'<OrderItem {self.id} - Qty: {self.quantity}>'
