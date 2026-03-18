from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.database.db import db
from app.models.notification import Notification

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/')
@login_required
def index():
    """Customer inbox for order notifications."""
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()

    if notifications:
        Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).update({Notification.is_read: True}, synchronize_session=False)
        db.session.commit()

    return render_template('customer/notifications.html', notifications=notifications)
