# Quick Start Guide

Hướng dẫn nhanh để chạy hệ thống quản lý & bán cà phê.

## Cài đặt nhanh (5 phút)

### 1. Cài đặt dependencies

```bash
# Kích hoạt virtual environment
venv\Scripts\activate  # Windows
# hoặc
source venv/bin/activate  # Linux/Mac

# Cài đặt packages
pip install -r requirements.txt
```

### 2. Cấu hình database

Tạo file `.env`:
```env
FLASK_ENV=development
SECRET_KEY=dev-secret-key
DATABASE_URL=mysql+pymysql://root:@localhost:3306/coffee_shop?charset=utf8mb4
```

**Lưu ý**: Thay đổi thông tin database nếu cần.

### 3. Tạo database MySQL

Sử dụng Navicat hoặc MySQL Command Line:

```sql
CREATE DATABASE coffee_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Khởi tạo database

```bash
python init_db.py
```

Hoặc:
```bash
flask init-db
```

### 5. Chạy ứng dụng

```bash
python app.py
```

Truy cập: http://localhost:5000

## Đăng nhập

- **Username**: admin
- **Password**: admin123
- **Role**: Admin

## Cấu trúc chính

```
app/
├── models/          # Database models (User, Product, Order)
├── routes/          # URL routes (auth, admin, products, orders)
├── templates/       # HTML templates
├── static/          # CSS, JS, images
└── utils/           # Helper functions

database/
├── schema.sql       # Database schema
└── seed.sql         # Sample data
```

## Tính năng chính

### Khách hàng:
- Xem sản phẩm
- Thêm vào giỏ hàng
- Đặt hàng
- Xem lịch sử đơn hàng

### Admin/Staff:
- Dashboard với thống kê
- Quản lý sản phẩm
- Quản lý đơn hàng
- Quản lý người dùng (Admin/Manager)

## Troubleshooting

**Lỗi kết nối database:**
- Kiểm tra MySQL đang chạy
- Kiểm tra thông tin trong `.env`
- Kiểm tra database đã được tạo chưa

**Lỗi module không tìm thấy:**
- Đảm bảo virtual environment đã được kích hoạt
- Chạy lại: `pip install -r requirements.txt`

## Tài liệu đầy đủ

- `README.md` - Tổng quan dự án
- `docs/INSTALLATION.md` - Hướng dẫn cài đặt chi tiết
- `docs/API.md` - Tài liệu API
- `docs/DEPLOYMENT.md` - Hướng dẫn deploy

## Demo Flow

1. Đăng nhập với admin
2. Tạo sản phẩm mới trong Admin > Quản lý sản phẩm
3. Đăng xuất và đăng ký tài khoản khách hàng
4. Xem sản phẩm và thêm vào giỏ hàng
5. Đặt hàng
6. Đăng nhập lại admin để xem và cập nhật đơn hàng

# Xem trạng thái
docker-compose ps

# Xem logs
docker logs coffee_shop_web

# Dừng
docker-compose down

# Khởi động lại
docker-compose up -d

# Rebuild container (GIỮ dữ liệu database + ảnh)
docker-compose down && docker-compose up -d --build

# CHỈ dùng khi muốn XÓA SẠCH toàn bộ dữ liệu (database + ảnh upload):
# docker-compose down -v && docker-compose up -d --build