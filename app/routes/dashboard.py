from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.database.db import db
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

def get_blog_posts():
    """Static blog posts for landing page"""
    return [
        {
            'slug': 'cach-phan-biet-robusta-va-arabica-cho-nguoi-moi',
            'title': 'Cách phân biệt Robusta và Arabica cho người mới uống',
            'excerpt': 'Robusta đắng, caffeine cao, giá rẻ. Arabica chua nhẹ, thơm phức tạp, giá cao hơn. Nhưng uống sao cho hợp khẩu vị mới là quan trọng...',
            'category': 'Hạt cà phê',
            'read_time': '4 phút đọc',
            'date': '16/03/2026',
            'icon': 'bi-cup-straw',
            'content': [
                'Robusta là loại phổ biến ở VN, đặc biệt miền Nam. Đắng rõ, caffeine gấp đôi Arabica, thường pha phin hoặc làm cà phê sữa. Giá khoảng 80-150k/kg.',
                'Arabica thì mềm hơn, có vị chua trái cây nhẹ, hương thơm phức tạp (hoa, chocolate, caramel tùy vùng trồng). Thường dùng cho espresso hoặc pour over. Giá 200-500k/kg.',
                'Thật ra không có loại nào "ngon hơn". Robusta đậm, tỉnh táo nhanh, hợp với sữa đặc. Arabica tinh tế, hợp uống đen hoặc latte. Thử cả hai rồi chọn theo sở thích là chuẩn nhất.'
            ]
        },
        {
            'slug': 'ba-cach-pha-ca-phe-tai-nha-khong-can-may',
            'title': 'Ba cách pha cà phê tại nhà không cần máy',
            'excerpt': 'Phin, French Press, và Cold Brew - ba cách pha đơn giản mà vẫn cho ly cà phê ngon. Không cần máy espresso vài chục triệu...',
            'category': 'Pha chế',
            'read_time': '5 phút đọc',
            'date': '14/03/2026',
            'icon': 'bi-cup-hot',
            'content': [
                'Phin: Cách truyền thống VN. Cho 2-3 thìa bột vào phin (xay vừa), đổ nước sôi từ từ, đợi 4-5 phút. Đơn giản, dễ điều chỉnh đậm/nhạt bằng lượng nước.',
                'French Press: Cho bột (xay thô) + nước nóng 90°C vào bình, khuấy nhẹ, đậy nắp đợi 4 phút rồi ấn piston xuống. Vị đậm hơn phin, có chút bã mịn lắng đáy.',
                'Cold Brew: Bột xay thô + nước lạnh (tỷ lệ 1:8), ngâm trong tủ lạnh 12-16 giờ. Vị ngọt tự nhiên, ít đắng, caffeine cao. Để được 3-4 ngày.'
            ]
        },
        {
            'slug': 'review-nhanh-5-loai-ca-phe-hop-pho-bien-o-vn',
            'title': 'Review nhanh 5 loại cà phê hộp phổ biến ở VN',
            'excerpt': 'G7, Nescafé, Vinacafe, Highlands, Wake Up 339 - loại nào đáng mua? Mình đã thử hết rồi chia sẻ luôn...',
            'category': 'Review',
            'read_time': '5 phút đọc',
            'date': '10/03/2026',
            'icon': 'bi-star',
            'content': [
                'G7 (65k/16 gói): Vị ngọt rõ, sữa nhiều, cà phê ít. Pha nhanh, ai cũng uống được. Best seller có lý do. Nhược: ngọt hơi nhiều nếu uống thường xuyên.',
                'Nescafé (72k/20 gói): Nhẹ nhàng hơn G7, bớt ngọt. Vị cà phê không đậm lắm. Giá trung bình, hộp lớn. Hợp người ít uống cà phê.',
                'Vinacafe (58k/20 gói): Hương rang kỹ, đắng rõ. Kiểu "cà phê xưa" mà bố mẹ thế hệ trước hay uống. Giá rẻ nhất nhưng không phải ai cũng quen.',
                'Highlands (89k/12 gói): Sữa đá hòa tan, ngọt sánh. Uống lạnh ngon, nhưng giá cao nhất. Packaging đẹp, thích hợp làm quà.',
                'Wake Up 339 (55k/20 gói): Đắng, ít ngọt. Giá sinh viên. Không fancy nhưng tỉnh táo tốt. Mình hay uống sáng khi cần code deadline.'
            ]
        },
        {
            'slug': 'tai-sao-ca-phe-viet-nam-ngon-ma-gia-re',
            'title': 'Tại sao cà phê Việt Nam ngon mà giá rẻ?',
            'excerpt': 'VN là nước xuất khẩu cà phê thứ 2 thế giới (sau Brazil), chủ yếu Robusta. Nhưng sao giá lại rẻ hơn Arabica nhập khẩu?',
            'category': 'Kiến thức',
            'read_time': '4 phút đọc',
            'date': '05/03/2026',
            'icon': 'bi-globe',
            'content': [
                'VN trồng chủ yếu Robusta (chiếm ~97%), đặc biệt ở Tây Nguyên (Đắk Lắk, Lâm Đồng, Gia Lai). Khí hậu nhiệt đới, đất bazan màu mỡ, phù hợp với Robusta - loại dễ trồng, năng suất cao.',
                'Robusta có caffeine gấp đôi Arabica, đắng hơn, thơm kém hơn, nên giá thấp hơn (thường 50-70% giá Arabica). Nhưng với người Việt, Robusta rang đúng cách thì rất phù hợp - đậm, tỉnh táo, hợp pha phin và uống với sữa đặc.',
                'Một số vùng ở Lâm Đồng, Sơn La cũng trồng Arabica nhưng quy mô nhỏ hơn. Arabica VN chất lượng ngon không thua Trung - Nam Mỹ, nhưng sản lượng ít nên giá cao (250-500k/kg).'
            ]
        }
    ]

@dashboard_bp.route('/')
def index():
    """Home page - blog style landing"""
    posts = get_blog_posts()

    latest_products = Product.query.filter_by(is_active=True)\
        .order_by(Product.created_at.desc())\
        .limit(6)\
        .all()

    show_admin_link = current_user.is_authenticated and (
        current_user.is_admin() or current_user.is_manager() or current_user.is_staff()
    )

    return render_template(
        'home.html',
        posts=posts,
        latest_products=latest_products,
        show_admin_link=show_admin_link
    )

@dashboard_bp.route('/blog/<slug>')
def blog_detail(slug):
    """Blog detail page"""
    posts = get_blog_posts()
    post = next((item for item in posts if item['slug'] == slug), None)
    if not post:
        abort(404)

    related_posts = [item for item in posts if item['slug'] != slug][:3]
    return render_template('blog_detail.html', post=post, related_posts=related_posts)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    if current_user.is_admin() or current_user.is_manager() or current_user.is_staff():
        return redirect(url_for('admin.dashboard'))
    
    # Customer dashboard
    recent_orders = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc())\
        .limit(5)\
        .all()
    
    total_orders = Order.query.filter_by(user_id=current_user.id).count()
    total_spent = db.session.query(func.sum(Order.total_amount))\
        .filter_by(user_id=current_user.id)\
        .scalar() or 0
    
    return render_template('customer/dashboard.html',
                         recent_orders=recent_orders,
                         total_orders=total_orders,
                         total_spent=total_spent)

@dashboard_bp.route('/about')
def about():
    """About us page"""
    return render_template('about.html')
