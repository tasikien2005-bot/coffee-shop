from datetime import datetime
from app.database.db import db


class Notification(db.Model):
    """Notification model for user updates"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship(
        'User',
        backref=db.backref('notifications', lazy=True)
    )
    order = db.relationship(
        'Order',
        backref=db.backref('notifications', lazy=True)
    )

    def __repr__(self):
        return f'<Notification {self.id} - User {self.user_id}>'
