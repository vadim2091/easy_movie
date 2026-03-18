import requests
from datetime import datetime

BOT_TOKEN = "8648309291:AAGLeQT72rvRFVsdw_dZdeSjwmgFKYb_Sa8"
ADMIN_CHAT_ID = 5753686567

def send_notification(username, user_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = (
        f"📨 <b>Новое сообщение в чате поддержки</b>\n"
        f"👤 <b>Пользователь:</b> {username}\n"
        f"🆔 <b>ID:</b> {user_id}\n"
        f"⏰ <b>Время:</b> {datetime.now().strftime('%H:%M')}\n\n"
        f"{message}"
    )
    data = {
        "chat_id": ADMIN_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, data=data, timeout=5)
        if r.status_code == 200:
            print("✅ Уведомление отправлено в Telegram")
            return True
        else:
            print(f"❌ Ошибка Telegram: {r.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False