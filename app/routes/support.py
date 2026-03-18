from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import User, SupportMessage

support_bp = Blueprint('support', __name__)

@support_bp.route('/support')
@login_required
def support():
    """Обычный чат поддержки для пользователей"""
    return render_template('support.html')

@support_bp.route('/admin/chat')
@login_required
def admin_chat():
    """Админская панель для просмотра всех чатов"""
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    
    # Получаем всех пользователей, у которых есть сообщения
    users_with_chats = User.query.join(SupportMessage).distinct().all()
    
    # Для каждого пользователя получаем последнее сообщение
    chats = []
    for user in users_with_chats:
        last_msg = SupportMessage.query.filter_by(user_id=user.id)\
            .order_by(SupportMessage.created_at.desc()).first()
        unread_count = SupportMessage.query.filter_by(
            user_id=user.id, 
            is_from_admin=False
        ).count()  # можно добавить поле is_read позже
        
        chats.append({
            'user': user,
            'last_message': last_msg.message if last_msg else '',
            'last_time': last_msg.created_at if last_msg else None,
            'unread': unread_count
        })

    @support_bp.route('/api/chat-history/<int:user_id>')
    @login_required
    def chat_history(user_id):
      if not current_user.is_admin and current_user.id != user_id:
        return {'error': 'Forbidden'}, 403
    
    messages = SupportMessage.query.filter_by(user_id=user_id)\
        .order_by(SupportMessage.created_at.asc())\
        .limit(100)\
        .all()
    
    return [{
        'id': m.id,
        'user_id': m.user_id,
        'username': m.user.username,
        'message': m.message,
        'time': m.created_at.strftime('%H:%M'),
        'is_admin': m.is_from_admin
    } for m in messages]
    return render_template('admin/chat.html', chats=chats)