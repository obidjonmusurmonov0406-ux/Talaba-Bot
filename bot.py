import os
import asyncio
import wikipedia
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Wikipedia tilini o'zbekchaga sozlaymiz
wikipedia.set_lang("uz")

# Tugmalar menyusi
menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✍️ Mustaqil ish yozish")],
    [KeyboardButton(text="ℹ️ Yordam")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Salom! Men 'Aqlli Talaba' botiman. 🎓\n\n"
        "Mustaqil ish yozish uchun pastdagi tugmani bosing va keyin mavzuni yozib yuboring.",
        reply_markup=menu
    )

@dp.message(F.text == "✍️ Mustaqil ish yozish")
async def ask_topic(message: types.Message):
    await message.answer("📝 Mustaqil ish mavzusini kiriting:\n(Masalan: *Amir Temur* yoki *Fizika*)", parse_mode="Markdown")

@dp.message()
async def search_wiki(message: types.Message):
    # Agar foydalanuvchi tugmani emas, mavzuni yuborgan bo'lsa
    if message.text == "ℹ️ Yordam":
        await message.answer("Mavzu yozing, men u haqida ma'lumot qidiraman.")
        return

    status = await message.answer("🔎 Ma'lumot qidirilmoqda, iltimos kuting...")
    
    try:
        # Avval qidirib ko'ramiz
        search_results = wikipedia.search(message.text)
        if not search_results:
            await status.edit_text("❌ Afsuski, bu mavzuda ma'lumot topilmadi. Boshqa so'zlar bilan urinib ko'ring.")
            return

        # Birinchi topilgan natijani olamiz
        page = wikipedia.page(search_results[0])
        text = page.summary[:1000] # Birinchi 1000 ta harfni olamiz
        
        result = (
            f"📚 **Mavzu: {page.title}**\n\n"
            f"**REJA:**\n1. Kirish\n2. {page.title} haqida umumiy ma'lumot\n3. Xulosa\n\n"
            f"**MATN:**\n{text}...\n\n"
            f"🔗 Batafsil: {page.url}"
        )
        await status.edit_text(result)
    except Exception as e:
        await status.edit_text("❌ Ma'lumot yuklashda xatolik yuz berdi yoki mavzu juda keng. Aniqroq yozing.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
