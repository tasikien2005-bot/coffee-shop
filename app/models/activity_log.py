from datetime import datetime
from app.database.db import db


class ActivityLog(db.Model):
    """Tracks admin/staff actions for audit purposes."""
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    target_type = db.Column(db.String(30), nullable=False)
    target_id = db.Column(db.Integer)
    description = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', backref=db.backref('activity_logs', lazy='dynamic'))

    ACTION_LABELS = {
        'create_product': 'Tạo sản phẩm',
        'update_product': 'Sửa sản phẩm',
        'delete_product': 'Xóa/ẩn sản phẩm',
        'update_order': 'Cập nhật đơn hàng',
        'update_payment': 'Cập nhật thanh toán',
        'change_role': 'Đổi vai trò',
        'toggle_user': 'Khóa/mở tài khoản',
        'create_user': 'Tạo tài khoản',
    }

    @classmethod
    def log(cls, user_id, action, target_type, target_id, description):
        entry = cls(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description
        )
        db.session.add(entry)
        return entry

    def get_action_label(self):
        return self.ACTION_LABELS.get(self.action, self.action)

    def __repr__(self):
        return f'<ActivityLog {self.id} {self.action}>'
