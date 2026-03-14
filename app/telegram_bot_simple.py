import requests
from datetime import datetime

# Токен бота (твой)
BOT_TOKEN = "8648309291:AAGLeQT72rvRFVsdw_dZdeSjwmgFKYb_Sa8"
ADMIN_CHAT_ID = "5753686567"

def send_telegram_notification(username, user_id, message):
    """Отправка уведомления админу через простой requests"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    text = f"📨 <b>Новое сообщение от {username}</b>\n"
    text += f"🆔 ID: {user_id}\n"
    text += f"⏰ {datetime.now().strftime('%H:%M %d.%m.%Y')}\n\n"
    text += f"💬 {message}"
    
    data = {
        "chat_id": ADMIN_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        r = requests.post(url, data=data, timeout=5)
        if r.status_code == 200:
            print(f"✅ Уведомление отправлено в Telegram")
            return True
        else:
            print(f"❌ Ошибка Telegram: {r.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

# Функция для запуска (заглушка, чтоб не падало)
def start_bot():
    print("🤖 Telegram бот (упрощенный) готов к отправке уведомлений")