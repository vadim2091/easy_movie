import requests
from datetime import datetime

# Токен бота и ID админа (вставь свои)
BOT_TOKEN = "8648309291:AAGLeQT72rvRFVsdw_dZdeSjwmgFKYb_Sa8"
ADMIN_CHAT_ID = 5753686567  # без кавычек

def notify_admin(username, user_id, message):
    """Отправляет уведомление админу через Telegram API (синхронно, без asyncio)."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"📨 Новое сообщение от {username} (ID: {user_id}) в {datetime.now().strftime('%H:%M')}:\n\n{message}"
    data = {
        "chat_id": ADMIN_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, data=data, timeout=5)
        if r.status_code == 200:
            print("✅ Уведомление отправлено в Telegram")
        else:
            print(f"❌ Ошибка Telegram: {r.text}")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")