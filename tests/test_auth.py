"""
Tests for authentication routes
"""
import pytest
from app import create_app
from app.database.db import db
from app.models.user import User, Role

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_login_page(client):
    """Test login page loads"""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Đăng nhập' in response.data

def test_register_page(client):
    """Test register page loads"""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Đăng ký' in response.data

def test_login_success(client, app):
    """Test successful login"""
    with app.app_context():
        # Create role
        role = Role(name='customer', description='Customer')
        db.session.add(role)
        db.session.commit()
        
        # Create user
        user = User(username='testuser', email='test@test.com', role_id=role.id)
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
    
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200

def test_login_failure(client):
    """Test login with wrong credentials"""
    response = client.post('/auth/login', data={
        'username': 'wronguser',
        'password': 'wrongpass'
    })
    
    assert b'Tên đăng nhập hoặc mật khẩu không đúng' in response.data
