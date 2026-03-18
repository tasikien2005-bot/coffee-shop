from datetime import datetime
from app.database.db import db

class Category(db.Model):
    """Category model for product categories"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    products = db.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    """Product model"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    @property
    def display_image_url(self):
        """URL ảnh hiển thị. Map đường dẫn cũ (products/) sang coffee-boxes/ để ảnh hộp không bị volume Docker ghi đè."""
        if not self.image_url:
            return None
        if 'coffee-box-' in self.image_url and 'images/products/' in self.image_url:
            return self.image_url.replace('images/products/', 'images/coffee-boxes/')
        return self.image_url

    def format_price(self):
        """Format price as currency"""
        return "{:,.0f}đ".format(float(self.price)).replace(',', '.')
    
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0
    
    def can_purchase(self, quantity=1):
        """Check if product can be purchased in given quantity"""
        return self.is_active and self.stock >= quantity
    
    def reduce_stock(self, quantity):
        """Reduce stock quantity"""
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False
    
    def increase_stock(self, quantity):
        """Increase stock quantity"""
        self.stock += quantity
    
    def __repr__(self):
        return f'<Product {self.name}>'
