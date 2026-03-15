from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from datetime import datetime
import threading
import requests
from app.telegram_bot_simple import send_telegram_notification

socketio = SocketIO(cors_allowed_origins="*")

active_users = {}
admin_room = "admins"

def get_db():
    from app import db
    return db

# ... остальные функции (connect, disconnect) без изменений ...

@socketio.on('send_message')
def handle_message(data):
    if not current_user.is_authenticated:
        return
    
    message = data.get('message', '').strip()
    if not message:
        return
    
    from app.models import SupportMessage
    db = get_db()
    
    msg = SupportMessage(
        user_id=current_user.id,
        message=message,
        is_from_admin=current_user.is_admin
    )
    db.session.add(msg)
    db.session.commit()
    
    response = {
        'id': msg.id,
        'user_id': current_user.id,
        'username': current_user.username,
        'message': message,
        'time': datetime.now().strftime('%H:%M'),
        'is_admin': current_user.is_admin
    }
    
    emit('new_message', response, broadcast=True)
    
# В функции handle_message, после отправки в чат, добавь:

    try:
        # Отправляем в Telegram через простой requests
        send_telegram_notification(
            current_user.username,
            current_user.id,
            message
        )
        print(f"📱 Уведомление отправлено: {message[:30]}...")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

        
@socketio.on('typing')
def handle_typing(data):
    if not current_user.is_authenticated:
        return
    
    is_typing = data.get('typing', False)
    
    if current_user.is_admin:
        to_user = data.get('to_user')
        if to_user:
            emit('user_typing', {
                'username': current_user.username,
                'typing': is_typing
            }, room=f"user_{to_user}")
    else:
        emit('user_typing', {
            'username': current_user.username,
            'typing': is_typing
        }, room=admin_room)

def load_chat_history():
    if not current_user.is_authenticated:
        return
    
    from app.models import SupportMessage, User
    db = get_db()
    
    if current_user.is_admin:
        messages = SupportMessage.query.order_by(SupportMessage.created_at.asc()).limit(50).all()
    else:
        messages = SupportMessage.query.filter_by(user_id=current_user.id)\
            .order_by(SupportMessage.created_at.asc()).all()
    
    history = []
    for msg in messages:
        user = User.query.get(msg.user_id)
        history.append({
            'id': msg.id,
            'user_id': msg.user_id,
            'username': user.username if user else 'Пользователь',
            'message': msg.message,
            'time': msg.created_at.strftime('%H:%M'),
            'is_admin': msg.is_from_admin
        })
    
    emit('chat_history', history, room=f"user_{current_user.id}")

    