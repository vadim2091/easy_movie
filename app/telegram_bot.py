import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# Токен бота
BOT_TOKEN = "8648309291:AAGLeQT72rvRFVsdw_dZdeSjwmgFKYb_Sa8"
ADMIN_CHAT_ID = "5753686567"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

admin_reply_to = {}

async def send_to_admin(user, message):
    """Отправка уведомления админу"""
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
            f"⏰ {datetime.now().strftime('%H:%M %d.%m.%Y')}\n\n"
            f"💬 {message}",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return True
    except Exception as e:
        print(f"❌ Telegram ошибка: {e}")
        return False

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Бот поддержки Easy Movie")

@dp.callback_query(lambda c: c.data.startswith('reply_'))
async def process_reply(callback: types.CallbackQuery):
    user_id = callback.data.split('_')[1]
    admin_reply_to[callback.from_user.id] = user_id
    await callback.answer()
    await callback.message.answer(f"✏️ Введите ответ для {user_id}:")

@dp.message()
async def handle_message(message: types.Message):
    if message.from_user.id in admin_reply_to:
        user_id = admin_reply_to[message.from_user.id]
        await bot.send_message(int(user_id), f"📨 <b>Ответ:</b>\n{message.text}", parse_mode="HTML")
        await message.answer(f"✅ Отправлено {user_id}")
        del admin_reply_to[message.from_user.id]

async def main():
    await dp.start_polling(bot)

def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())