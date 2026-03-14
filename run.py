from app import create_app
from app.websocket import socketio
import threading
import os

app = create_app()

# Флаг для запуска бота (глобальный)
_bot_started = False

def run_bot():
    """Запуск бота в отдельном потоке"""
    global _bot_started
    if _bot_started:
        return
    
    try:
        from app.telegram_bot import start_bot
        print("🤖 Telegram бот запускается...")
        _bot_started = True
        start_bot()
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        _bot_started = False

if __name__ == '__main__':
    # Запускаем бота ТОЛЬКО ОДИН РАЗ
    if not _bot_started:
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
    
    print("🚀 Easy Movie ЗАПУЩЕН!")
    print("📍 http://127.0.0.1:5000")
    
    # Отключаем автоперезагрузку debug режима
    socketio.run(app, debug=True, port=5000, use_reloader=False)