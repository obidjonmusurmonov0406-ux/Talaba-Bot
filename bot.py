import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# .env faylidan tokenni yuklash
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Asosiy menyu tugmalari
menu_buttons = [
    [KeyboardButton(text="📄 Mustaqil ish yaratish")],
    [KeyboardButton(text="📚 Namunalar"), KeyboardButton(text="ℹ️ Yordam")]
]
main_menu = ReplyKeyboardMarkup(keyboard=menu_buttons, resize_keyboard=True)

# /start buyrug'i
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Salom {message.from_user.first_name}! 👋\n"
        "Men talabalarga mustaqil ishlarni tayyorlashda yordam beraman.\n"
        "Keling, ishni boshlaymiz!",
        reply_markup=main_menu
    )

# Tugmalarni boshqarish
@dp.message(F.text == "📄 Mustaqil ish yaratish")
async def create_work(message: types.Message):
    await message.answer("Iltimos, mustaqil ish mavzusini yuboring. Men unga reja tuzib beraman.")

@dp.message(F.text == "📚 Namunalar")
async def show_samples(message: types.Message):
    await message.answer("Hozircha namunalar yuklanmagan. Tez kunda qo'shiladi!")

@dp.message(F.text == "ℹ️ Yordam")
async def help_info(message: types.Message):
    await message.answer("Muammo bo'lsa, adminga murojaat qiling: @admin_username")

# Har qanday matnga javob (Mavzu yuborilganda)
@dp.message()
async def handle_text(message: types.Message):
    if not message.text.startswith('/'):
        await message.answer(f"Qabul qilindi! '{message.text}' mavzusi bo'yicha ma'lumot qidiryapman... ✨")

# Botni yurgizish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi")
