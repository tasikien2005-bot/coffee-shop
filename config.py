import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Flask-Login settings
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'app/static/images'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Category visibility for product form
    HIDDEN_PRODUCT_CATEGORIES = []

    # Packaged category naming
    PACKAGED_CATEGORY_NAMES = [
        'Cà phê hạt nguyên chất',
        'Cà phê bột pha phin',
        'Cà phê hòa tan',
        'Cà phê cao cấp',
        'Combo tiết kiệm'
    ]

    # SQLAlchemy connection pool settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20,
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    # Khi chạy trên host (không trong Docker): dùng localhost:3307 (MySQL trong Docker map ra 3307).
    # Khi chạy trong Docker: cần set DATABASE_URL=...@db:3306/... (docker-compose đã set).
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://rikai:Admin%40123@127.0.0.1:3307/coffee_shop?charset=utf8mb4'
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://rikai:Admin%40123@db:3306/coffee_shop?charset=utf8mb4'
    SESSION_COOKIE_SECURE = False  # Set to True when using HTTPS
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
