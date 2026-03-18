from app.models.notification import Notification


def build_order_status_notification(order, new_status):
    """Create notification object for order status updates."""
    status_messages = {
        'shipping': {
            'title': 'Đơn hàng #{order_id} đang được giao',
            'message': 'Đơn hàng #{order_id} đã được bàn giao cho đơn vị vận chuyển.'
        },
        'delivered': {
            'title': 'Đơn hàng #{order_id} đã giao thành công',
            'message': 'Cảm ơn bạn đã mua hàng. Nếu có vấn đề, vui lòng liên hệ hỗ trợ.'
        }
    }

    payload = status_messages.get(new_status)
    if not payload:
        return None

    title = payload['title'].format(order_id=order.id)
    message = payload['message'].format(order_id=order.id)

    return Notification(
        user_id=order.user_id,
        order_id=order.id,
        title=title,
        message=message
    )
