import asyncio
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8648309291:AAGLeQT72rvRFVsdw_dZdeSjwmgFKYb_Sa8"
ADMIN_CHAT_ID = 5753686567  # твой ID

# Хранилище для ответов админа: {admin_chat_id: target_user_id}
admin_reply_target = {}

# Ссылка на приложение бота (заполнится при запуске)
_bot_app = None

# ========== ОБРАБОТЧИКИ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Я бот поддержки Easy Movie.\n"
        "Я буду уведомлять администратора о новых сообщениях в чате на сайте.\n"
        "Чтобы ответить пользователю, нажмите кнопку под его сообщением."
    )

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает сообщения, пришедшие в личку боту."""
    user_id = update.effective_user.id

    # Если это ответ админа (он находится в режиме ответа)
    if user_id == ADMIN_CHAT_ID and user_id in admin_reply_target:
        target_user_id = admin_reply_target[user_id]
        text = update.message.text

        # Отправляем ответ пользователю через вебсокет
        # Импортируем здесь, чтобы избежать циклического импорта
        from app.websocket import socketio
        socketio.emit('new_message', {
            'user_id': target_user_id,
            'username': 'Администратор',
            'message': text,
            'time': datetime.now().strftime('%H:%M'),
            'is_admin': True
        }, room=f'user_{target_user_id}')

        await update.message.reply_text(f"✅ Ответ отправлен пользователю {target_user_id}")
        del admin_reply_target[user_id]

    else:
        # Это новое сообщение от пользователя (или админа не в режиме ответа)
        keyboard = [[InlineKeyboardButton("✅ Ответить", callback_data=f"reply_{user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"📨 <b>Новое сообщение от пользователя</b>\n"
                f"👤 <b>Имя:</b> {update.effective_user.full_name}\n"
                f"🆔 <b>ID:</b> {user_id}\n"
                f"⏰ <b>Время:</b> {datetime.now().strftime('%H:%M %d.%m.%Y')}\n\n"
                f"{update.message.text}"
            ),
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        await update.message.reply_text("✅ Ваше сообщение отправлено администратору. Ожидайте ответа.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатия на кнопку 'Ответить'."""
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith('reply_'):
        user_id = int(data.split('_')[1])
        admin_reply_target[update.effective_user.id] = user_id
        await query.edit_message_text(text="✏️ Введите ответ для пользователя (одним сообщением):")

# ========== ФУНКЦИИ ДЛЯ ВЫЗОВА ИЗ ВЕБСОКЕТА ==========
def send_notification(username, user_id, message):
    """Отправляет уведомление админу о новом сообщении в чате."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_async_notify(username, user_id, message))
        loop.close()
    except Exception as e:
        print(f"❌ Ошибка в send_notification: {e}")

async def _async_notify(username, user_id, message):
    """Асинхронная отправка уведомления через уже работающее приложение бота."""
    global _bot_app
    if _bot_app is None:
        print("❌ Бот ещё не запущен, уведомление не отправлено")
        return
    async with _bot_app:
        await _bot_app.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"📨 <b>Новое сообщение в чате поддержки</b>\n"
                f"👤 <b>Пользователь:</b> {username}\n"
                f"🆔 <b>ID:</b> {user_id}\n"
                f"⏰ <b>Время:</b> {datetime.now().strftime('%H:%M')}\n\n"
                f"{message}"
            ),
            parse_mode="HTML"
        )

# ========== ЗАПУСК БОТА ==========
def run_bot():
    """Запускает бота (эта функция выполняется в отдельном потоке)."""
    global _bot_app
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^reply_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
    _bot_app = app
    print("🤖 Telegram бот запущен и ожидает сообщения...")
    app.run_polling()

def start_bot():
    """Запускает бота в фоновом потоке."""
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()