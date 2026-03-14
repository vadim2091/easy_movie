import requests
import json

# Твои данные
BOT_TOKEN = "8648309291:AAGLeQT72rvRFVsdw_dZdeSjwmgFKYb_Sa8"
CHAT_ID = "5753686567"  # Твой ID

# 1. Проверим работает ли бот вообще
print("🔄 Проверяем бота...")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
response = requests.get(url)
print(f"Статус: {response.status_code}")
print(f"Ответ: {response.text}\n")

# 2. Пробуем отправить сообщение
print("🔄 Отправляем тестовое сообщение...")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {
    "chat_id": CHAT_ID,
    "text": "🔴 ЭТО ТЕСТОВОЕ СООБЩЕНИЕ ИЗ PYTHON",
    "parse_mode": "HTML"
}

response = requests.post(url, data=data)
print(f"Статус: {response.status_code}")
print(f"Ответ: {response.text}")