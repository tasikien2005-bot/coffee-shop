# PHÂN TÍCH VÀ THIẾT KẾ CƠ SỞ DỮ LIỆU - COFFEE SHOP

**Hệ quản trị CSDL:** MySQL (utf8mb4)  
**ORM:** SQLAlchemy (Flask)  
**Tên database:** `coffee_shop`

---

## a. CÁC ĐỐI TƯỢNG - THỰC THỂ

| STT | Thực thể    | Mô tả ngắn |
|-----|-------------|------------|
| 1   | **Role**    | Vai trò người dùng trong hệ thống (admin, manager, staff, customer). |
| 2   | **User**    | Tài khoản người dùng: đăng nhập, thông tin cá nhân, thuộc một vai trò. |
| 3   | **Category**| Nhóm sản phẩm (ví dụ: Cà phê hạt nguyên chất, Cà phê bột pha phin, Cà phê hòa tan). |
| 4   | **Product** | Sản phẩm đóng gói: tên, giá, tồn kho, thuộc một danh mục. |
| 5   | **Order**   | Đơn hàng: do một user đặt, có tổng tiền, trạng thái, thanh toán, địa chỉ giao. |
| 6   | **OrderItem** | Chi tiết đơn hàng: sản phẩm, số lượng, đơn giá tại thời điểm đặt (bảng trung gian N-N giữa Order và Product). |

**Các kiểu dữ liệu đặc biệt (enum trong ứng dụng):**
- **OrderStatus:** pending, confirmed, processing, shipping, delivered, cancelled  
- **PaymentMethod:** cod, bank_transfer, momo, zalopay, vnpay  
- **PaymentStatus:** unpaid, paid, failed, refunded  

---

## b. MÔ HÌNH THỰC THỂ KẾT HỢP (ERD)

**Quan hệ giữa các thực thể:**

```
                    ┌─────────────┐
                    │    Role     │
                    │ id (PK)     │
                    │ name        │
                    │ description │
                    └──────┬──────┘
                           │ 1
                           │
                           │ N
                    ┌──────▼──────┐         ┌─────────────┐
                    │    User     │         │  Category   │
                    │ id (PK)     │         │ id (PK)     │
                    │ username    │         │ name        │
                    │ email       │         │ description │
                    │ role_id(FK) │         └──────┬──────┘
                    │ ...         │                │ 1
                    └──────┬──────┘                │
                           │ 1                     │ N
                           │                       │
                           │ N              ┌──────▼──────┐
                    ┌──────▼──────┐         │   Product   │
                    │   Order     │         │ id (PK)     │
                    │ id (PK)     │         │ name        │
                    │ user_id(FK) │         │ category_id │
                    │ total_amount│         │ price       │
                    │ status      │         │ stock       │
                    │ ...         │         └──────┬──────┘
                    └──────┬──────┘                │
                           │ 1                     │
                           │                       │
                           │ N              N      │
                    ┌──────▼──────────────────────▼──────┐
                    │            OrderItem               │
                    │ id (PK)                            │
                    │ order_id (FK) → orders             │
                    │ product_id (FK) → products         │
                    │ quantity, price                    │
                    └───────────────────────────────────┘
```

**Mô tả quan hệ:**
- **Role – User:** 1-N. Một vai trò có nhiều người dùng; mỗi user có đúng một role.
- **User – Order:** 1-N. Một user có nhiều đơn hàng; mỗi đơn thuộc một user.
- **Category – Product:** 1-N. Một danh mục có nhiều sản phẩm; mỗi sản phẩm thuộc một danh mục.
- **Order – OrderItem – Product:** Order và Product liên kết N-N qua OrderItem. Một đơn có nhiều dòng; mỗi dòng gắn với một sản phẩm và lưu số lượng + đơn giá tại thời điểm đặt.

---

## c. MÔ HÌNH VẬT LÝ (PDM) – Chuẩn hóa mức 3 (3NF)

PDM tương ứng ERD, chuẩn 3NF (không phụ thuộc hàm bắc cầu vào khóa):

| Bảng        | Khóa chính | Khóa ngoại        | Ghi chú 3NF |
|------------|------------|--------------------|-------------|
| roles      | id         | -                  | Không phụ thuộc bắc cầu. |
| users      | id         | role_id → roles.id | Chỉ phụ thuộc vào id. |
| categories | id         | -                  | Không phụ thuộc bắc cầu. |
| products   | id         | category_id → categories.id | Chỉ phụ thuộc vào id. |
| orders     | id         | user_id → users.id | Chỉ phụ thuộc vào id. |
| order_items| id         | order_id → orders.id, product_id → products.id | Bảng trung gian; price lưu giá tại thời điểm đặt (không phụ thuộc bắc cầu vào product hiện tại). |

**Chuyển từ ERD sang PDM (PowerDesigner):**
1. Mỗi thực thể → một bảng; thuộc tính → cột.
2. Khóa chính (PK) cho mỗi bảng.
3. Quan hệ 1-N: khóa ngoại (FK) đặt ở bên N (users.role_id, products.category_id, orders.user_id, order_items.order_id, order_items.product_id).
4. Quan hệ N-N (Order–Product) đã được tách thành bảng order_items với hai FK.
5. Chuẩn hóa 3NF: loại bỏ phụ thuộc bắc cầu (trong thiết kế hiện tại không có thuộc tính nào phụ thuộc vào không-khóa nên đạt 3NF).

---

## d. LƯỢC ĐỒ CSDL QUAN HỆ (Tổng quan cho lập trình viên)

```
roles (id, name, description, created_at)
users (id, username, email, password_hash, full_name, phone, address, role_id, is_active, created_at, updated_at)
       FK: role_id → roles(id)

categories (id, name, description, created_at)
products (id, name, description, price, stock, category_id, image_url, is_active, created_at, updated_at)
         FK: category_id → categories(id)

orders (id, user_id, total_amount, status, payment_method, payment_status, shipping_address, notes, created_at, updated_at)
       FK: user_id → users(id)

order_items (id, order_id, product_id, quantity, price, created_at)
            FK: order_id → orders(id), product_id → products(id)
```

**Quy ước:** In đậm = NOT NULL / bắt buộc trong nghiệp vụ. Các trường PK/FK và nghiệp vụ chính đều có ràng buộc tương ứng trong PDM (xem mục f).

---

## e. LƯU ĐỒ CSDL (Database Diagram – Vật lý trên HQT CSDL)

Lưu đồ vật lý trên MySQL phản ánh đúng các bảng và khóa đã cài đặt (trùng với schema thực tế khi chạy ứng dụng):

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│      roles       │     │      users       │     │    categories    │
├──────────────────┤     ├──────────────────┤     ├──────────────────┤
│ PK id            │◄────│ FK role_id       │     │ PK id           │
│    name (UQ)     │     │ PK id            │     │    name (UQ)     │
│    description   │     │    username (UQ)  │     │    description   │
│    created_at    │     │    email (UQ)     │     │    created_at    │
└──────────────────┘     │    password_hash │     └────────┬─────────┘
                         │    full_name     │              │
                         │    phone         │              │
                         │    address       │              │
                         │    is_active     │     ┌────────▼─────────┐
                         │    created_at    │     │     products     │
                         │    updated_at   │     ├──────────────────┤
                         └────────┬────────┘     │ FK category_id    │◄───┐
                                  │              │ PK id             │    │
                                  │              │    name           │    │
                         ┌────────▼────────┐     │    description    │    │
                         │     orders      │     │    price          │    │
                         ├─────────────────┤     │    stock         │    │
                         │ FK user_id      │◄────│    image_url     │    │
                         │ PK id           │     │    is_active     │    │
                         │    total_amount │     │    created_at    │    │
                         │    status       │     │    updated_at    │    │
                         │ payment_method  │     └────────┬─────────┘    │
                         │ payment_status │              │               │
                         │ shipping_addr  │     ┌────────▼─────────────────────────┐
                         │    notes       │     │         order_items              │
                         │    created_at  │     ├──────────────────────────────────┤
                         │    updated_at  │     │ FK order_id   ───────────────────┼───► orders(id)
                         └────────┬───────┘     │ FK product_id ───────────────────┼───► products(id)
                                  │             │ PK id                            │
                                  └─────────────│    quantity                      │
                                                │    price                         │
                                                │    created_at                    │
                                                └──────────────────────────────────┘
```

**Xác thực cài đặt:** Khi đã chạy `schema.sql` (hoặc `db.create_all()` với đủ cột payment_method, payment_status), diagram trên chính là lưu đồ vật lý trong MySQL (có thể xuất từ MySQL Workbench / phpMyAdmin / PowerDesigner reverse engineering từ database).

---

## f. CÁC BẢNG CSDL VÀ RBTV (Ràng buộc toàn vẹn)

### 1. Bảng `roles`

| Cột         | Kiểu dữ liệu | Ràng buộc        | Diễn giải |
|------------|--------------|-------------------|------------|
| id         | INT          | PK, AUTO_INCREMENT| Mã vai trò. |
| name       | VARCHAR(50)  | UNIQUE, NOT NULL  | Tên vai trò (admin, manager, staff, customer). |
| description| VARCHAR(200) | NULL              | Mô tả vai trò. |
| created_at | DATETIME     | DEFAULT CURRENT_TIMESTAMP | Thời điểm tạo. |

**RBTV:** Khóa chính (PK) trên `id`. UNIQUE trên `name`.

---

### 2. Bảng `users`

| Cột          | Kiểu dữ liệu | Ràng buộc        | Diễn giải |
|--------------|--------------|-------------------|------------|
| id           | INT          | PK, AUTO_INCREMENT| Mã người dùng. |
| username     | VARCHAR(80)  | UNIQUE, NOT NULL, INDEX | Tên đăng nhập. |
| email        | VARCHAR(120) | UNIQUE, NOT NULL, INDEX | Email. |
| password_hash| VARCHAR(255) | NOT NULL         | Mật khẩu đã băm. |
| full_name    | VARCHAR(100) | NULL             | Họ tên. |
| phone        | VARCHAR(20)  | NULL             | Số điện thoại. |
| address      | TEXT         | NULL             | Địa chỉ. |
| role_id      | INT          | NOT NULL, DEFAULT 4, FK → roles(id) | Vai trò; mặc định customer. |
| is_active    | BOOLEAN      | DEFAULT TRUE     | Trạng thái kích hoạt. |
| created_at   | DATETIME     | DEFAULT CURRENT_TIMESTAMP | Ngày tạo. |
| updated_at   | DATETIME     | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Ngày cập nhật. |

**RBTV:** PK `id`. FK `role_id` REFERENCES `roles(id)` ON DELETE RESTRICT. UNIQUE `username`, `email`. INDEX trên `username`, `email`.

---

### 3. Bảng `categories`

| Cột         | Kiểu dữ liệu | Ràng buộc        | Diễn giải |
|------------|--------------|-------------------|------------|
| id         | INT          | PK, AUTO_INCREMENT| Mã danh mục. |
| name       | VARCHAR(100) | UNIQUE, NOT NULL  | Tên danh mục. |
| description| TEXT         | NULL              | Mô tả. |
| created_at | DATETIME     | DEFAULT CURRENT_TIMESTAMP | Thời điểm tạo. |

**RBTV:** PK `id`. UNIQUE `name`.

---

### 4. Bảng `products`

| Cột         | Kiểu dữ liệu | Ràng buộc        | Diễn giải |
|------------|--------------|-------------------|------------|
| id         | INT          | PK, AUTO_INCREMENT| Mã sản phẩm. |
| name       | VARCHAR(200) | NOT NULL, INDEX   | Tên sản phẩm. |
| description| TEXT         | NULL              | Mô tả. |
| price      | DECIMAL(10,2)| NOT NULL          | Giá bán. |
| stock      | INT          | NOT NULL, DEFAULT 0 | Số lượng tồn kho. |
| category_id| INT          | NOT NULL, FK → categories(id) | Thuộc danh mục. |
| image_url  | VARCHAR(255) | NULL              | Đường dẫn ảnh. |
| is_active  | BOOLEAN      | DEFAULT TRUE      | Còn bán hay không. |
| created_at | DATETIME     | DEFAULT CURRENT_TIMESTAMP | Ngày tạo. |
| updated_at | DATETIME     | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Ngày cập nhật. |

**RBTV:** PK `id`. FK `category_id` REFERENCES `categories(id)` ON DELETE RESTRICT. INDEX trên `name`, `category_id`.

---

### 5. Bảng `orders`

| Cột             | Kiểu dữ liệu | Ràng buộc        | Diễn giải |
|-----------------|--------------|-------------------|------------|
| id              | INT          | PK, AUTO_INCREMENT| Mã đơn hàng. |
| user_id         | INT          | NOT NULL, FK → users(id) | Người đặt. |
| total_amount    | DECIMAL(10,2)| NOT NULL          | Tổng tiền đơn. |
| status          | VARCHAR(20)  | NOT NULL, DEFAULT 'pending', INDEX | Trạng thái đơn (pending, confirmed, …). |
| payment_method  | VARCHAR(20)  | DEFAULT 'cod'     | Hình thức thanh toán (cod, bank_transfer, momo, …). |
| payment_status  | VARCHAR(20)  | DEFAULT 'unpaid'  | Trạng thái thanh toán (unpaid, paid, failed, refunded). |
| shipping_address| TEXT         | NULL              | Địa chỉ giao hàng. |
| notes           | TEXT         | NULL              | Ghi chú đơn. |
| created_at      | DATETIME     | DEFAULT CURRENT_TIMESTAMP, INDEX | Thời điểm tạo. |
| updated_at      | DATETIME     | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Thời điểm cập nhật. |

**RBTV:** PK `id`. FK `user_id` REFERENCES `users(id)` ON DELETE RESTRICT. INDEX trên `user_id`, `status`, `created_at`.

**Lưu ý:** Nếu dùng file `database/schema.sql` cũ, cần bổ sung hai cột `payment_method` và `payment_status` cho bảng `orders` để khớp ứng dụng.

---

### 6. Bảng `order_items`

| Cột       | Kiểu dữ liệu | Ràng buộc        | Diễn giải |
|----------|--------------|-------------------|------------|
| id       | INT          | PK, AUTO_INCREMENT| Mã dòng đơn. |
| order_id | INT          | NOT NULL, FK → orders(id) | Đơn hàng. |
| product_id| INT         | NOT NULL, FK → products(id) | Sản phẩm. |
| quantity | INT          | NOT NULL          | Số lượng đặt. |
| price    | DECIMAL(10,2)| NOT NULL          | Đơn giá tại thời điểm đặt. |
| created_at| DATETIME    | DEFAULT CURRENT_TIMESTAMP | Thời điểm tạo. |

**RBTV:** PK `id`. FK `order_id` REFERENCES `orders(id)` ON DELETE CASCADE. FK `product_id` REFERENCES `products(id)` ON DELETE RESTRICT.

---

## TÓM TẮT RBTV GIỮA CÁC BẢNG

| Bảng        | Khóa chính | Khóa ngoại                          | Ghi chú |
|------------|------------|-------------------------------------|---------|
| roles      | id         | -                                   | -       |
| users      | id         | role_id → roles(id) RESTRICT        | -       |
| categories | id         | -                                   | -       |
| products   | id         | category_id → categories(id) RESTRICT | -     |
| orders     | id         | user_id → users(id) RESTRICT        | -       |
| order_items| id         | order_id → orders(id) CASCADE, product_id → products(id) RESTRICT | Xóa đơn thì xóa dòng; xóa sản phẩm không xóa dòng cũ. |

---

*Tài liệu được sinh từ mã nguồn và schema của dự án Coffee Shop. Cập nhật lần cuối theo models và database hiện tại.*
