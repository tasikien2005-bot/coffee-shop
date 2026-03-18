# Hướng dẫn Deploy

Hướng dẫn deploy hệ thống quản lý & bán cà phê lên môi trường production.

## Môi trường Production

### Yêu cầu Server

- **OS**: Linux (Ubuntu 20.04+ recommended) hoặc Windows Server
- **Python**: 3.8+
- **MySQL**: 5.7+
- **Web Server**: Nginx hoặc Apache (recommended: Nginx)
- **WSGI Server**: Gunicorn hoặc uWSGI

## Deploy trên Linux Server

### Bước 1: Chuẩn bị server

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python và dependencies
sudo apt install python3 python3-pip python3-venv mysql-server nginx git -y
```

### Bước 2: Setup MySQL

```bash
sudo mysql_secure_installation
```

Tạo database và user:
```sql
CREATE DATABASE coffee_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'coffeeshop'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON coffee_shop.* TO 'coffeeshop'@'localhost';
FLUSH PRIVILEGES;
```

### Bước 3: Deploy ứng dụng

```bash
# Tạo thư mục cho ứng dụng
sudo mkdir -p /var/www/coffeeshop
sudo chown $USER:$USER /var/www/coffeeshop

# Clone/Copy code
cd /var/www/coffeeshop
git clone <repository-url> .

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### Bước 4: Cấu hình environment

Tạo file `.env`:
```bash
nano .env
```

Nội dung:
```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-here-generate-with-openssl
DATABASE_URL=mysql+pymysql://coffeeshop:strong_password_here@localhost:3306/coffee_shop?charset=utf8mb4
```

Generate secret key:
```bash
openssl rand -hex 32
```

### Bước 5: Khởi tạo database

```bash
source venv/bin/activate
flask init-db
```

### Bước 6: Cấu hình Gunicorn

Tạo file `/var/www/coffeeshop/gunicorn_config.py`:
```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
```

Tạo systemd service `/etc/systemd/system/coffeeshop.service`:
```ini
[Unit]
Description=Gunicorn instance to serve Coffee Shop
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/coffeeshop
Environment="PATH=/var/www/coffeeshop/venv/bin"
ExecStart=/var/www/coffeeshop/venv/bin/gunicorn --config gunicorn_config.py app:app

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start coffeeshop
sudo systemctl enable coffeeshop
```

### Bước 7: Cấu hình Nginx

Tạo file `/etc/nginx/sites-available/coffeeshop`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/coffeeshop/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/coffeeshop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Bước 8: SSL với Let's Encrypt (Optional)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Deploy trên Heroku

### Bước 1: Tạo Procfile

Tạo file `Procfile`:
```
web: gunicorn app:app
```

### Bước 2: Cài đặt Heroku CLI

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli
```

### Bước 3: Deploy

```bash
heroku login
heroku create coffeeshop-app
heroku addons:create cleardb:ignite  # MySQL database
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(openssl rand -hex 32)

# Get database URL
heroku config:get CLEARDB_DATABASE_URL

# Set DATABASE_URL
heroku config:set DATABASE_URL=mysql+pymysql://...

git push heroku main
heroku run flask init-db
heroku open
```

## Deploy với Docker

### Tạo Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### Docker Compose

Tạo file `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=mysql+pymysql://coffeeshop:password@db:3306/coffee_shop
    depends_on:
      - db

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: coffee_shop
      MYSQL_USER: coffeeshop
      MYSQL_PASSWORD: password
      MYSQL_ROOT_PASSWORD: rootpassword
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
```

Deploy:
```bash
docker-compose up -d
```

## Deploy trên Windows Server với IIS

### Bước 1: Cài đặt Python và dependencies

```powershell
# Install Python
# Download từ python.org

# Install dependencies
pip install -r requirements.txt
pip install waitress
```

### Bước 2: Tạo startup script

Tạo file `start.bat`:
```batch
@echo off
cd /d %~dp0
venv\Scripts\activate
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

### Bước 3: Cấu hình IIS với URL Rewrite

Cài đặt URL Rewrite module và cấu hình reverse proxy đến localhost:5000

## Đổi tên miền (ví dụ: Brewly.click)

1. **Trong code:** Ứng dụng không hardcode tên miền; chỉ cần đổi branding (tên site) trong template nếu cần — đã dùng **Brewly** cho tên hiển thị.

2. **DNS:** Trỏ tên miền mới (Brewly.click) về server của bạn:
   - **A record** trỏ `Brewly.click` và `www.Brewly.click` tới IP server, **hoặc**
   - **CNAME** trỏ tới tunnel/load balancer nếu dùng Cloudflare hoặc CDN.

3. **Nginx (nếu dùng):** Sửa `server_name` trong site config:
   ```nginx
   server_name brewly.click www.brewly.click;
   ```
   Rồi: `sudo nginx -t && sudo systemctl reload nginx`

4. **Cloudflare Tunnel (docker-compose):** Trong Cloudflare Dashboard → Zero Trust → Tunnels → chọn tunnel → Public Hostname: thêm hostname `brewly.click` (và `www.brewly.click` nếu cần) trỏ tới service `http://web:5000`. Có thể xóa hostname cũ (coffee-manager.click) sau khi chuyển xong.

5. **SSL:** Nếu dùng Let's Encrypt: `sudo certbot --nginx -d brewly.click -d www.brewly.click`. Với Cloudflare Tunnel, SSL thường do Cloudflare cấp, không cần certbot trên server.

## Sau khi cập nhật code (quan trọng)

**Phải khởi động lại ứng dụng thì thay đổi mới có hiệu lực.**

- **Systemd (Gunicorn):**
  ```bash
  sudo systemctl restart coffeeshop
  ```
- **Docker / Docker Compose** (áp dụng cho Brewly.click nếu chạy bằng Docker):
  ```bash
  cd /var/www/html/coffee_shop
  docker-compose restart web
  ```
  Hoặc build lại nếu có thay đổi dependency: `docker-compose up -d --build web`
- **Heroku:** push code sẽ tự deploy; nếu không thấy thay đổi thì kiểm tra build logs.

## Kiểm tra sau khi deploy

1. **Kiểm tra ứng dụng chạy:**
   ```bash
   curl http://localhost:5000
   ```

2. **Kiểm tra database connection:**
   - Đăng nhập với admin account
   - Kiểm tra có thể tạo/xem sản phẩm

3. **Kiểm tra logs:**
   ```bash
   # Gunicorn logs
   sudo journalctl -u coffeeshop -f
   
   # Nginx logs
   sudo tail -f /var/log/nginx/error.log
   ```

## Bảo mật Production

1. **Thay đổi secret key:**
   ```bash
   openssl rand -hex 32
   ```

2. **Disable debug mode:**
   ```python
   DEBUG = False
   ```

3. **Setup firewall:**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

4. **Regular backups:**
   ```bash
   # Backup database
   mysqldump -u coffeeshop -p coffee_shop > backup_$(date +%Y%m%d).sql
   ```

5. **Update dependencies:**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

## Monitoring

### Logs

- Application logs: `/var/log/coffeeshop/`
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u coffeeshop`

### Health Check

Tạo endpoint `/health`:
```python
@app.route('/health')
def health():
    return {'status': 'ok'}, 200
```

## Troubleshooting

### Ứng dụng không start

```bash
# Check logs
sudo journalctl -u coffeeshop -n 50

# Check process
ps aux | grep gunicorn

# Restart service
sudo systemctl restart coffeeshop
```

### Database connection error

- Kiểm tra MySQL đang chạy: `sudo systemctl status mysql`
- Kiểm tra credentials trong `.env`
- Kiểm tra firewall rules

### Static files không load

- Kiểm tra Nginx config
- Kiểm tra permissions: `sudo chown -R www-data:www-data /var/www/coffeeshop/app/static`

## Backup và Restore

### Backup

```bash
# Database backup
mysqldump -u coffeeshop -p coffee_shop > backup.sql

# Files backup
tar -czf backup_files.tar.gz /var/www/coffeeshop
```

### Restore

```bash
# Restore database
mysql -u coffeeshop -p coffee_shop < backup.sql

# Restore files
tar -xzf backup_files.tar.gz -C /
```
