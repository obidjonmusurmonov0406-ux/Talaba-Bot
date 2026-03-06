import os
import asyncio
import wikipedia  # Avval buni o'rnatish kerak
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Wikipedia tilini o'zbekchaga sozlaymiz
wikipedia.set_lang("uz")

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Salom! Men tayyorman. Mavzuni yuboring, men matn tayyorlayman.")

@dp.message()
async def handle_work(message: types.Message):
    mavzu = message.text
    status_msg = await message.answer(f"🔍 '{mavzu}' bo'yicha ma'lumot qidiryapman...")
    
    try:
        # Wikipedia'dan ma'lumot qidirish
        summary = wikipedia.summary(mavzu, sentences=10)
        
        mustaqil_ish = (
            f"📚 **Mavzu: {mavzu}**\n\n"
            f"**REJA:**\n1. Kirish\n2. Mavzu haqida batafsil\n3. Xulosa\n\n"
            f"**MATN:**\n{summary}\n\n"
            f"✅ Mustaqil ish tayyor!"
        )
        await status_msg.edit_text(mustaqil_ish, parse_mode="Markdown")
    except:
        await status_msg.edit_text("❌ Kechirasiz, bu mavzu bo'yicha ma'lumot topa olmadim. Boshqa mavzu sinab ko'ring.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
