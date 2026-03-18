# Hướng dẫn cài đặt

Hướng dẫn chi tiết cài đặt và cấu hình hệ thống quản lý & bán cà phê.

## Yêu cầu hệ thống

### Phần mềm cần thiết

1. **Python 3.8+**
   - Tải từ: https://www.python.org/downloads/
   - Kiểm tra: `python --version`

2. **MySQL Server 5.7+**
   - Tải từ: https://dev.mysql.com/downloads/mysql/
   - Hoặc sử dụng XAMPP/WAMP bao gồm MySQL

3. **Navicat for MySQL** (Tùy chọn)
   - Để quản lý database dễ dàng hơn
   - Tải từ: https://www.navicat.com/

4. **Git** (Tùy chọn)
   - Để clone repository

## Cài đặt từng bước

### Bước 1: Chuẩn bị môi trường

#### Windows:
1. Cài đặt Python từ python.org
2. Trong quá trình cài đặt, chọn "Add Python to PATH"
3. Cài đặt MySQL Server hoặc XAMPP

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv mysql-server
```

#### macOS:
```bash
brew install python3 mysql
```

### Bước 2: Clone/Copy dự án

Nếu có Git:
```bash
git clone <repository-url>
cd caffe-shop
```

Hoặc giải nén file ZIP vào thư mục `caffe-shop`

### Bước 3: Tạo Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

Khi virtual environment được kích hoạt, bạn sẽ thấy `(venv)` ở đầu dòng lệnh.

### Bước 4: Cài đặt Python packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Bước 5: Cấu hình MySQL

#### Tạo database bằng MySQL Command Line:

```bash
mysql -u root -p
```

Trong MySQL:
```sql
CREATE DATABASE coffee_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES;
EXIT;
```

#### Hoặc sử dụng Navicat:

1. Mở Navicat for MySQL
2. Tạo connection mới:
   - Host: localhost
   - Port: 3306
   - Username: root
   - Password: (mật khẩu MySQL của bạn)
3. Kết nối
4. Click chuột phải > New Database
5. Tên: `coffee_shop`
6. Charset: `utf8mb4`
7. Collation: `utf8mb4_unicode_ci`
8. OK

### Bước 6: Cấu hình ứng dụng

1. Tạo file `.env` từ `.env.example`:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

2. Chỉnh sửa file `.env`:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/coffee_shop?charset=utf8mb4
```

Thay `your_password` bằng mật khẩu MySQL của bạn.

**Lưu ý**: Nếu MySQL không có mật khẩu, để trống:
```env
DATABASE_URL=mysql+pymysql://root:@localhost:3306/coffee_shop?charset=utf8mb4
```

### Bước 7: Khởi tạo database

Chạy lệnh để tạo bảng và dữ liệu mẫu:

```bash
flask init-db
```

Hoặc:
```bash
python app.py
```

Bạn sẽ thấy thông báo:
```
✓ Roles created
✓ Admin user created (username: admin, password: admin123)
✓ Categories created
✓ Sample products created
✓ Database initialization completed!
```

### Bước 8: Chạy ứng dụng

```bash
python app.py
```

Hoặc:
```bash
flask run
```

Ứng dụng sẽ chạy tại: **http://localhost:5000**

## Kiểm tra cài đặt

1. Mở trình duyệt và truy cập: http://localhost:5000
2. Đăng nhập với:
   - Username: `admin`
   - Password: `admin123`
3. Nếu đăng nhập thành công, bạn đã cài đặt thành công!

## Xử lý lỗi thường gặp

### Lỗi kết nối database

**Lỗi**: `Can't connect to MySQL server`

**Giải pháp**:
- Kiểm tra MySQL đã chạy chưa
- Kiểm tra username/password trong `.env`
- Kiểm tra port MySQL (mặc định 3306)

### Lỗi module không tìm thấy

**Lỗi**: `ModuleNotFoundError: No module named 'flask'`

**Giải pháp**:
- Đảm bảo virtual environment đã được kích hoạt
- Chạy lại: `pip install -r requirements.txt`

### Lỗi encoding

**Lỗi**: `UnicodeEncodeError`

**Giải pháp**:
- Đảm bảo database sử dụng charset `utf8mb4`
- Kiểm tra file `.env` có `charset=utf8mb4` trong DATABASE_URL

### Lỗi port đã được sử dụng

**Lỗi**: `Address already in use`

**Giải pháp**:
- Thay đổi port trong `app.py`: `app.run(port=5001)`
- Hoặc tắt ứng dụng đang chạy trên port 5000

## Cài đặt trên server production

Xem file `docs/DEPLOYMENT.md` để biết hướng dẫn deploy lên server.

## Hỗ trợ

Nếu gặp vấn đề, vui lòng kiểm tra:
1. Logs trong terminal
2. File `docs/API.md` để xem API documentation
3. File `README.md` để xem tổng quan
