from app import create_app
from app.websocket import socketio
import threading
import os
import sys

app = create_app()

def start_bot():
    from app.telegram_bot import start_bot
    print("🚀 Запускаем поток бота...", flush=True)
    start_bot()

if __name__ == '__main__':
    print("🚀 Запуск Easy Movie...", flush=True)
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    print("🤖 Поток бота запущен", flush=True)
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)