from app.telegram_bot import start_bot
import threading
import time

def run_bot():
    """Запуск бота"""
    print("🤖 Telegram бот запускается...")
    start_bot()

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    print("✅ Бот запущен в фоне")
    
    # Держим поток живым
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("👋 Останавливаем бота...")