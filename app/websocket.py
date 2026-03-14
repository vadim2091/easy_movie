from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from datetime import datetime
import threading
import requests

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
    
    # ===== ИСПРАВЛЕННЫЙ TELEGRAM =====
    if not current_user.is_admin:
        try:
            # СОХРАНЯЕМ ДАННЫЕ ЗДЕСЬ (а не в потоке)
            user_id = current_user.id
            username = current_user.username
            msg_text = message
            
            def send_telegram(uid, uname, text):
                url = "https://api.telegram.org/bot8648309291:AAGLeQT72rvRFVsdw_dZdeSjwmgFKYb_Sa8/sendMessage"
                data = {
                    "chat_id": "5753686567",
                    "text": f"📨 <b>Новое сообщение от {uname}</b>\n🆔 ID: {uid}\n\n💬 {text}",
                    "parse_mode": "HTML"
                }
                try:
                    r = requests.post(url, data=data)
                    if r.status_code == 200:
                        print(f"✅ Telegram: {text[:30]}...")
                    else:
                        print(f"❌ Telegram ошибка: {r.text}")
                except Exception as e:
                    print(f"❌ Telegram исключение: {e}")
            
            # Передаем данные в поток
            thread = threading.Thread(target=send_telegram, args=(user_id, username, msg_text), daemon=True)
            thread.start()
            print(f"📱 Отправка в Telegram: {message[:30]}...")
            
        except Exception as e:
            print(f"❌ Ошибка отправки в Telegram: {e}")
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