from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.database.db import db

class Role(db.Model):
    """Role model for user roles"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    users = db.relationship('User', backref='role', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    """User model with authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, default=4)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan',
                             foreign_keys='Order.user_id')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role.name == 'admin'
    
    def is_manager(self):
        """Check if user is manager"""
        return self.role.name == 'manager'
    
    def is_staff(self):
        """Check if user is staff"""
        return self.role.name == 'staff'
    
    def is_customer(self):
        """Check if user is customer"""
        return self.role.name == 'customer'
    
    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.is_admin() or self.is_manager()
    
    def can_manage_products(self):
        """Check if user can manage products"""
        return self.is_admin() or self.is_manager() or self.is_staff()
    
    def can_manage_orders(self):
        """Check if user can manage orders"""
        return self.is_admin() or self.is_manager() or self.is_staff()
    
    def __repr__(self):
        return f'<User {self.username}>'
