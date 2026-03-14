import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# Токен бота (В КАВЫЧКАХ!)
BOT_TOKEN = "8648309291:AAGLeQT72rvRFVsdw_dZdeSjwmgFKYb_Sa8"
ADMIN_CHAT_ID = "5753686567"  # Узнай у @userinfobot

# Инициализация бота
bot = Bot(token="8648309291:AAGLeQT72rvRFVsdw_dZdeSjwmgFKYb_Sa8")
dp = Dispatcher()

# Хранилище состояний (в памяти)
admin_reply_to = {}

# Функция для отправки сообщения админу
async def send_to_admin(user, message):
    """Отправка уведомления админу о новом сообщении"""
    try:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Ответить", callback_data=f"reply_{user.id}"),
                    InlineKeyboardButton(text="❌ Закрыть", callback_data=f"close_{user.id}")
                ]
            ]
        )
        
        await bot.send_message(
            ADMIN_CHAT_ID,
            f"📨 <b>Новое сообщение от {user.username}</b>\n"
            f"🆔 ID: {user.id}\n"
            f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}\n\n"
            f"💬 <b>Сообщение:</b>\n{message}",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        print(f"✅ Сообщение отправлено админу в Telegram")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")
        return False

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот поддержки Easy Movie.\n"
        "Я буду уведомлять тебя о новых сообщениях на сайте."
    )

@dp.callback_query(lambda c: c.data.startswith('reply_'))
async def process_reply(callback: types.CallbackQuery):
    user_id = callback.data.split('_')[1]
    admin_reply_to[callback.from_user.id] = user_id
    await callback.answer()
    await callback.message.answer(f"✏️ Введите ответ для пользователя {user_id}:")

@dp.callback_query(lambda c: c.data.startswith('close_'))
async def process_close(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

@dp.message()
async def handle_all_messages(message: types.Message):
    if message.from_user.id in admin_reply_to:
        user_id = admin_reply_to[message.from_user.id]
        try:
            await bot.send_message(
                int(user_id),
                f"📨 <b>Ответ от поддержки:</b>\n\n{message.text}",
                parse_mode="HTML"
            )
            await message.answer(f"✅ Ответ отправлен пользователю {user_id}!")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
        finally:
            del admin_reply_to[message.from_user.id]

async def main():
    """Запуск бота"""
    print("🤖 Telegram бот запускается...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")

def start_bot():
    """Запуск бота в отдельном потоке"""
    # Создаем новый цикл событий для этого потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()