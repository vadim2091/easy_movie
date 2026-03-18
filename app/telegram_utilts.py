def notify_admin(username, user_id, message):
    print(f"📤 Попытка отправить уведомление: {username}, {user_id}")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text = f"📨 Новое сообщение от {username} (ID: {user_id}) в {datetime.now().strftime('%H:%M')}:\n\n{message}"
    data = {
        "chat_id": ADMIN_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        print(f"📤 Отправка запроса к Telegram...")
        r = requests.post(url, data=data, timeout=5)
        print(f"📤 Статус ответа: {r.status_code}")
        print(f"📤 Текст ответа: {r.text[:200]}")
        if r.status_code == 200:
            print("✅ Уведомление отправлено в Telegram")
        else:
            print(f"❌ Ошибка Telegram: {r.text}")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")