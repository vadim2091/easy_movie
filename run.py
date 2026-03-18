from app import create_app
from app.websocket import socketio
import threading
import os

app = create_app()

def start_bot():
    from app.telegram_bot import start_bot
    start_bot()

if __name__ == '__main__':
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    print("🚀 Easy Movie запущен")
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)