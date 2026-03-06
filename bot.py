import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Tokeningizni shu yerga qo'ying (Xavfsizlik uchun keyinchalik .env ga o'tamiz)
TOKEN = "8343853327:AAEviMe3JBMFauHZurr7WJcwvkL2a8kUI8I"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Tugmalar
menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✍️ Mustaqil ish yozish")],
    [KeyboardButton(text="ℹ️ Ma'lumot")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Salom! Mavzuni yuboring, men reja va matn tuzaman.", reply_markup=menu)

@dp.message()
async def handle_ai(message: types.Message):
    if message.text == "✍️ Mustaqil ish yozish":
        await message.answer("Mavzuni kiriting (masalan: 'Amir Temur hayoti'):")
    else:
        # Bu yerda sun'iy intellekt matn tayyorlaydi
        await message.answer(f"✅ '{message.text}' bo'yicha mustaqil ish tayyorlanmoqda...")
        
        # Namuna matn (Hozircha shablon, keyin buni AI ga ulaymiz)
        text = f"📚 Mavzu: {message.text}\n\n1. Kirish\n2. Asosiy qism\n3. Xulosa\n\nBu mavzu bo'yicha ma'lumotlar yig'ilmoqda..."
        await message.answer(text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
