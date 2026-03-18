-- Seed data for Coffee Shop Database
-- Sample data for demo and testing

USE coffee_shop;

-- Insert roles
INSERT INTO roles (name, description) VALUES
('admin', 'Quản trị viên hệ thống'),
('manager', 'Quản lý cửa hàng'),
('staff', 'Nhân viên'),
('customer', 'Khách hàng')
ON DUPLICATE KEY UPDATE name=name;

-- Insert categories
INSERT INTO categories (name, description) VALUES
('Cà phê hạt nguyên chất', 'Cà phê hạt, phù hợp xay theo khẩu vị'),
('Cà phê bột pha phin', 'Cà phê xay sẵn để pha phin'),
('Cà phê hòa tan', 'Cà phê hòa tan đóng gói'),
('Cà phê cao cấp', 'Dòng cao cấp, chọn lọc hạt'),
('Combo tiết kiệm', 'Combo nhiều sản phẩm, giá tốt')
ON DUPLICATE KEY UPDATE name=name;

-- Insert admin user (password: admin123)
-- Password hash for 'admin123' using werkzeug.security.generate_password_hash
INSERT INTO users (username, email, password_hash, full_name, role_id) VALUES
('admin', 'admin@coffeeshop.com', 'pbkdf2:sha256:600000$XxXxXxXx$hash_here', 'Quản trị viên', 1),
('manager', 'manager@coffeeshop.com', 'pbkdf2:sha256:600000$XxXxXxXx$hash_here', 'Quản lý cửa hàng', 2),
('staff', 'staff@coffeeshop.com', 'pbkdf2:sha256:600000$XxXxXxXx$hash_here', 'Nhân viên', 3),
('customer1', 'customer1@example.com', 'pbkdf2:sha256:600000$XxXxXxXx$hash_here', 'Khách hàng 1', 4)
ON DUPLICATE KEY UPDATE username=username;

-- Insert sample products (name, description, price, stock, category_id, image_url)
INSERT INTO products (name, description, price, stock, category_id, image_url) VALUES
('Cà phê hạt Robusta (Bịch 500g)', 'Cà phê hạt nguyên chất, phù hợp xay pha phin.', 165000, 50, 1, NULL),
('Cà phê bột rang mộc (Bịch 250g)', 'Bột rang mộc, đậm vị, pha phin.', 85000, 60, 2, NULL),
('Cà phê hòa tan 3in1 (Gói 20 gói)', 'Cà phê hòa tan đóng gói, tiện mang theo.', 62000, 80, 3, NULL),
('Cà phê đặc sản Arabica (Bịch 250g)', 'Dòng cao cấp, hương thơm trái cây.', 210000, 40, 4, NULL),
('Combo tiết kiệm 3 bịch (1kg)', 'Combo 3 bịch cà phê rang xay, tiết kiệm hơn.', 285000, 30, 5, NULL),
('Trung Nguyên G7 (Hộp 16 gói)', 'Cà phê hòa tan Trung Nguyên G7, hộp 16 gói.', 65000, 80, 3, 'images/coffee-boxes/coffee-box-trung-nguyen.svg'),
('Nestlé Nescafé (Hộp 20 gói)', 'Cà phê hòa tan Nestlé Nescafé, hộp 20 gói.', 72000, 60, 3, 'images/coffee-boxes/coffee-box-nescafe.svg'),
('Vinacafe (Hộp 20 gói)', 'Cà phê hòa tan Vinacafe truyền thống, hộp 20 gói.', 58000, 70, 3, 'images/coffee-boxes/coffee-box-vinacafe.svg')
ON DUPLICATE KEY UPDATE name=name;

-- Note: Password hashes need to be generated using Python:
-- from werkzeug.security import generate_password_hash
-- print(generate_password_hash('admin123'))
-- Replace the hash_here placeholders with actual hashes
