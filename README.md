<<<<<<< HEAD
# Brewly Coffee Shop

Website bán cà phê online với hệ thống quản lý đơn hàng, kho, và tài khoản khách hàng.

## Giới thiệu

Brewly là nền tảng mua cà phê online, từ cà phê phin, espresso đến các loại hòa tan. Website được xây dựng bằng Flask + MySQL, hỗ trợ thanh toán COD và chuyển khoản QR, phân quyền đa cấp (admin, manager, staff, customer).

## Tính năng chính

### Cho khách hàng:
- Xem danh sách sản phẩm với tìm kiếm và lọc theo danh mục
- Xem chi tiết sản phẩm
- Thêm sản phẩm vào giỏ hàng
- Quản lý giỏ hàng (cập nhật, xóa sản phẩm)
- Đặt hàng
- Xem lịch sử đơn hàng
- Theo dõi trạng thái đơn hàng
- Hủy đơn hàng (nếu chưa được xử lý)

### Cho nhân viên/Quản lý/Admin:
- Dashboard với thống kê tổng quan
- Quản lý sản phẩm (CRUD)
- Quản lý danh mục sản phẩm
- Quản lý đơn hàng
- Cập nhật trạng thái đơn hàng
- Quản lý người dùng (Admin/Manager)
- Xem báo cáo và thống kê

## Công nghệ sử dụng

- **Backend**: Flask 3.1.2
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)
- **Database**: MySQL
- **Authentication**: Flask-Login
- **Security**: Flask-WTF (CSRF protection)
- **Frontend**: Bootstrap 5, Chart.js
- **Python**: 3.8+

## Cài đặt

### Yêu cầu hệ thống

- Python 3.8 trở lên
- MySQL Server 5.7 trở lên
- pip (Python package manager)

### Bước 1: Clone repository

```bash
git clone <repository-url>
cd caffe-shop
```

### Bước 2: Tạo virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Bước 3: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 4: Cấu hình database

1. Tạo database MySQL:
```sql
CREATE DATABASE coffee_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Cấu hình kết nối trong file `.env`:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/coffee_shop?charset=utf8mb4
```

Hoặc sử dụng Navicat để kết nối MySQL và tạo database.

### Bước 5: Khởi tạo database

```bash
flask init-db
```

Hoặc chạy trực tiếp:
```bash
python app.py
```

Lệnh này sẽ tự động tạo các bảng và dữ liệu mẫu.

### Bước 6: Chạy ứng dụng

```bash
python app.py
```

Hoặc:
```bash
flask run
```

Ứng dụng sẽ chạy tại: http://localhost:5000

## Tài khoản mặc định

Sau khi khởi tạo database, bạn có thể đăng nhập với:

- **Username**: admin
- **Password**: admin123
- **Role**: Admin

## Cấu trúc dự án

```
caffe-shop/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # Blueprint routes
│   ├── templates/           # Jinja2 templates
│   ├── static/              # Static files (CSS, JS, images)
│   ├── utils/               # Utility functions
│   └── database/            # Database configuration
├── database/
│   ├── schema.sql           # Database schema
│   └── seed.sql             # Sample data
├── config.py                # Configuration
├── app.py                   # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## API Routes

### Authentication
- `GET/POST /auth/login` - Đăng nhập
- `GET /auth/logout` - Đăng xuất
- `GET/POST /auth/register` - Đăng ký

### Products
- `GET /products/` - Danh sách sản phẩm
- `GET /products/<id>` - Chi tiết sản phẩm
- `POST /products/add-to-cart/<id>` - Thêm vào giỏ hàng

### Orders
- `GET /orders/` - Danh sách đơn hàng
- `POST /orders/create` - Tạo đơn hàng
- `GET /orders/<id>` - Chi tiết đơn hàng

### Admin
- `GET /admin/dashboard` - Dashboard admin
- `GET /admin/products` - Quản lý sản phẩm
- `GET /admin/orders` - Quản lý đơn hàng
- `GET /admin/users` - Quản lý người dùng

## Bảo mật

- Password được hash bằng Werkzeug
- CSRF protection với Flask-WTF
- SQL injection prevention với SQLAlchemy ORM
- XSS protection với Jinja2 auto-escaping
- Role-based access control

## Demo

Để demo hệ thống:

1. Đăng nhập với tài khoản admin
2. Tạo sản phẩm mới trong Admin > Quản lý sản phẩm
3. Đăng xuất và đăng ký tài khoản khách hàng mới
4. Xem sản phẩm và thêm vào giỏ hàng
5. Đặt hàng
6. Đăng nhập lại với admin để xem và cập nhật đơn hàng

## Tác giả

Đồ án tốt nghiệp CNTT

## License

MIT License
=======
# coffee-shop
>>>>>>> 5007646c68f18b1dc0d2d247e3998b9b5737654e
