# API Documentation

Tài liệu API cho hệ thống quản lý & bán cà phê.

## Authentication Routes

### POST /auth/login
Đăng nhập người dùng.

**Request:**
```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123&remember=true
```

**Response:**
- Thành công: Redirect đến dashboard
- Thất bại: Hiển thị thông báo lỗi

### GET /auth/logout
Đăng xuất người dùng.

**Response:**
- Redirect đến trang đăng nhập

### POST /auth/register
Đăng ký tài khoản khách hàng mới.

**Request:**
```
POST /auth/register
Content-Type: application/x-www-form-urlencoded

username=customer1&email=customer1@example.com&password=123456&confirm_password=123456&full_name=Customer Name
```

**Response:**
- Thành công: Redirect đến trang đăng nhập
- Thất bại: Hiển thị thông báo lỗi

## Product Routes

### GET /products/
Danh sách sản phẩm.

**Query Parameters:**
- `page` (int): Số trang (mặc định: 1)
- `search` (string): Tìm kiếm theo tên
- `category` (int): Lọc theo category_id

**Example:**
```
GET /products/?page=1&search=cafe&category=1
```

### GET /products/<id>
Chi tiết sản phẩm.

**Parameters:**
- `id` (int): ID sản phẩm

**Example:**
```
GET /products/1
```

### POST /products/add-to-cart/<product_id>
Thêm sản phẩm vào giỏ hàng.

**Request:**
```
POST /products/add-to-cart/1
Content-Type: application/x-www-form-urlencoded

quantity=2
```

**Response:**
- Thành công: Flash message và redirect
- Thất bại: Flash error message

### GET /products/cart
Xem giỏ hàng.

**Response:**
- HTML page với danh sách sản phẩm trong giỏ hàng

### POST /products/cart/update
Cập nhật số lượng sản phẩm trong giỏ hàng.

**Request:**
```
POST /products/cart/update
Content-Type: application/x-www-form-urlencoded

product_id=1&quantity=3
```

### POST /products/cart/remove/<product_id>
Xóa sản phẩm khỏi giỏ hàng.

## Order Routes

### GET /orders/
Danh sách đơn hàng của người dùng hiện tại.

**Query Parameters:**
- `page` (int): Số trang

**Authentication:** Required

### POST /orders/create
Tạo đơn hàng từ giỏ hàng.

**Request:**
```
POST /orders/create
Content-Type: application/x-www-form-urlencoded

shipping_address=123 Main St&notes=Giao hàng buổi sáng
```

**Response:**
- Thành công: Redirect đến chi tiết đơn hàng
- Thất bại: Flash error message

**Authentication:** Required (Customer)

### GET /orders/<id>
Chi tiết đơn hàng.

**Parameters:**
- `id` (int): ID đơn hàng

**Authentication:** Required (Owner hoặc Admin/Staff)

### POST /orders/<id>/cancel
Hủy đơn hàng.

**Authentication:** Required (Owner only)

## Admin Routes

Tất cả admin routes yêu cầu authentication và quyền admin/staff.

### GET /admin/dashboard
Dashboard admin với thống kê.

**Required Role:** Staff, Manager, hoặc Admin

### GET /admin/products
Quản lý sản phẩm.

**Query Parameters:**
- `page` (int): Số trang
- `search` (string): Tìm kiếm
- `category` (int): Lọc theo category

**Required Role:** Staff, Manager, hoặc Admin

### GET /admin/products/create
Form tạo sản phẩm mới.

**Required Role:** Staff, Manager, hoặc Admin

### POST /admin/products/create
Tạo sản phẩm mới.

**Request:**
```
POST /admin/products/create
Content-Type: application/x-www-form-urlencoded

name=Cà phê hòa tan 3in1 (Gói 20 gói)&description=Cà phê hòa tan đóng gói&price=62000&stock=80&category_id=3
```

### GET /admin/products/<id>/edit
Form chỉnh sửa sản phẩm.

**Required Role:** Staff, Manager, hoặc Admin

### POST /admin/products/<id>/edit
Cập nhật sản phẩm.

### POST /admin/products/<id>/delete
Xóa sản phẩm.

**Required Role:** Staff, Manager, hoặc Admin

### GET /admin/orders
Quản lý đơn hàng.

**Query Parameters:**
- `page` (int): Số trang
- `status` (string): Lọc theo trạng thái

**Required Role:** Staff, Manager, hoặc Admin

### GET /admin/orders/<id>
Chi tiết đơn hàng (admin view).

**Required Role:** Staff, Manager, hoặc Admin

### POST /admin/orders/<id>/update-status
Cập nhật trạng thái đơn hàng.

**Request:**
```
POST /admin/orders/1/update-status
Content-Type: application/x-www-form-urlencoded

status=confirmed
```

**Status values:**
- `pending`: Chờ xử lý
- `confirmed`: Đã xác nhận
- `processing`: Đang xử lý
- `shipping`: Đang giao hàng
- `delivered`: Đã giao hàng
- `cancelled`: Đã hủy

**Required Role:** Staff, Manager, hoặc Admin

### GET /admin/users
Quản lý người dùng.

**Query Parameters:**
- `page` (int): Số trang
- `search` (string): Tìm kiếm
- `role` (int): Lọc theo role_id

**Required Role:** Manager hoặc Admin

### GET /admin/categories
Quản lý danh mục.

**Required Role:** Staff, Manager, hoặc Admin

### POST /admin/categories/create
Tạo danh mục mới.

**Request:**
```
POST /admin/categories/create
Content-Type: application/x-www-form-urlencoded

name=Cà phê hòa tan&description=Cà phê hòa tan đóng gói
```

## Dashboard Routes

### GET /
Trang chủ - redirect dựa trên role.

### GET /dashboard
Dashboard người dùng.

**Authentication:** Required

## Data Models

### User
```python
{
    "id": 1,
    "username": "admin",
    "email": "admin@coffeeshop.com",
    "full_name": "Quản trị viên",
    "role_id": 1,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
}
```

### Product
```python
{
    "id": 1,
    "name": "Cà phê hòa tan 3in1 (Gói 20 gói)",
    "description": "Cà phê hòa tan đóng gói",
    "price": 62000.00,
    "stock": 80,
    "category_id": 3,
    "is_active": true
}
```

### Order
```python
{
    "id": 1,
    "user_id": 4,
    "total_amount": 50000.00,
    "status": "pending",
    "shipping_address": "123 Main St",
    "created_at": "2024-01-01T00:00:00"
}
```

## Error Handling

Tất cả routes trả về HTTP status codes:
- `200`: Success
- `302`: Redirect
- `404`: Not Found
- `500`: Internal Server Error

Flash messages được sử dụng để hiển thị thông báo:
- `success`: Thành công (màu xanh)
- `danger`: Lỗi (màu đỏ)
- `warning`: Cảnh báo (màu vàng)
- `info`: Thông tin (màu xanh dương)

## Authentication

Hệ thống sử dụng Flask-Login để quản lý session. Sau khi đăng nhập thành công, session cookie được tạo và sử dụng cho các request tiếp theo.

## CSRF Protection

Tất cả POST requests yêu cầu CSRF token từ Flask-WTF. Token được tự động thêm vào forms.
