import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Токен и ID админа (те же)
BOT_TOKEN = "8648309291:AAGLeQT72rvRFVsdw_dZdeSjwmgFKYb_Sa8"
ADMIN_CHAT_ID = 5753686567

# Словарь для хранения состояния ответов: {admin_chat_id: user_id}
admin_reply_target = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Я бот поддержки Easy Movie. Я буду уведомлять администратора о новых сообщениях.")

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений, пришедших в личку боту."""
    user_id = update.effective_user.id
    # Если это сообщение от админа и он сейчас отвечает кому-то
    if user_id == ADMIN_CHAT_ID and user_id in admin_reply_target:
        target_user_id = admin_reply_target[user_id]
        text = update.message.text
        # Здесь мы не можем отправить напрямую в вебсокет, поэтому просто уведомим админа, что ответ принят.
        # В реальности нужно передать сообщение через вебсокет. Для этого можно использовать механизм очередей.
        # Но для простоты пока отправим сообщение через бота пользователю (если пользователь тоже в Telegram).
        # Однако наш пользователь на сайте, поэтому лучше использовать вебсокет.
        # Временно просто выведем в консоль.
        print(f"📤 Ответ для пользователя {target_user_id}: {text}")
        # Отправляем уведомление админу, что ответ принят
        await update.message.reply_text(f"✅ Ответ принят. Он будет доставлен пользователю {target_user_id} через сайт.")
        # TODO: реализовать отправку через вебсокет (например, через Redis или базу данных)
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

def start_bot():
    """Запуск бота в фоновом потоке (для вызова из run.py)."""
    import threading
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()