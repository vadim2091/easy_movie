import requests
from datetime import datetime

# Токен бота и ID админа
BOT_TOKEN = "8648309291:AAGLeQT72rvRFVsdw_dZdeSjwmgFKYb_Sa8"
ADMIN_CHAT_ID = 5753686567

def notify_admin(username, user_id, message):
    """Отправляет уведомление админу"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        text = (
            f"📨 <b>Новое сообщение в поддержке</b>\n"
            f"👤 <b>Пользователь:</b> {username}\n"
            f"🆔 <b>ID:</b> {user_id}\n"
            f"⏰ <b>Время:</b> {datetime.now().strftime('%H:%M %d.%m.%Y')}\n\n"
            f"💬 {message}"
        )
        data = {
            "chat_id": ADMIN_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        r = requests.post(url, data=data, timeout=5)
        if r.status_code == 200:
            print(f"✅ Уведомление отправлено в Telegram")
            return True
        else:
            print(f"❌ Ошибка Telegram: {r.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False