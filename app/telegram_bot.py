import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from app.websocket import socketio  # импортируем socketio для отправки сообщений в чат
import requests
from datetime import datetime

def notify_admin(username, user_id, message):
    """Отправляет уведомление админу через Telegram API (синхронно)."""
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
        print(f"❌ Ошибка отправки в Telegram: {e}")
        
# Токен и ID админа (вставь свои)
BOT_TOKEN = "8648309291:AAGLeQT72rvRFVsdw_dZdeSjwmgFKYb_Sa8"
ADMIN_CHAT_ID = 5753686567  # без кавычек, просто число

# Словарь для хранения состояния ответов: {admin_chat_id: user_id}
admin_reply_target = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Я бот поддержки Easy Movie. Я буду уведомлять администратора о новых сообщениях.")

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений, пришедших в личку боту (от админа или пользователя)."""
    user_id = update.effective_user.id
    # Если это сообщение от админа и он сейчас отвечает кому-то
    if user_id == ADMIN_CHAT_ID and user_id in admin_reply_target:
        target_user_id = admin_reply_target[user_id]
        text = update.message.text
        # Отправляем сообщение пользователю через вебсокет
        socketio.emit('new_message', {
            'user_id': target_user_id,
            'username': 'Администратор',
            'message': text,
            'time': datetime.now().strftime('%H:%M'),
            'is_admin': True
        }, room=f'user_{target_user_id}')
        # Уведомляем админа, что отправлено
        await update.message.reply_text(f"✅ Ответ отправлен пользователю {target_user_id}")
        del admin_reply_target[user_id]
    else:
        # Это сообщение от обычного пользователя (или админа без контекста)
        # Отправляем админу уведомление с кнопкой
        keyboard = [
            [InlineKeyboardButton("✅ Ответить", callback_data=f"reply_{user_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📨 Новое сообщение от пользователя {update.effective_user.full_name} (ID: {user_id}):\n\n{update.message.text}",
            reply_markup=reply_markup
        )
        # Подтверждение пользователю
        await update.message.reply_text("✅ Ваше сообщение отправлено администратору. Ожидайте ответа.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатия на кнопку 'Ответить'."""
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith('reply_'):
        user_id = int(data.split('_')[1])
        # Сохраняем, что админ сейчас отвечает этому пользователю
        admin_reply_target[update.effective_user.id] = user_id
        await query.edit_message_text(text="✏️ Введите ответ для пользователя (одним сообщением):")

def run_bot():
    """Запуск бота в отдельном потоке."""
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^reply_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
    print("🤖 Telegram бот запущен")
    app.run_polling()

# Для запуска в отдельном потоке используем функцию start_bot
def start_bot():
    import threading
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()