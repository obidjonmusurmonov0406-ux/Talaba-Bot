import os
import asyncio
import wikipedia
from pptx import Presentation
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

wikipedia.set_lang("uz")

# Tugmalar menyusi
menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📝 Esse yozish"), KeyboardButton(text="📊 Taqdimot qilish")],
    [KeyboardButton(text="ℹ️ Yordam")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Salom! Men 'Aqlli Talaba' botiman. 🎓\nNima yordam kerak?", reply_markup=menu)

# --- ESSE YOZISH QISMI ---
@dp.message(F.text == "📝 Esse yozish")
async def esse_start(message: types.Message):
    await message.answer("Esse mavzusini yuboring:")

# --- TAQDIMOT YARATISH QISMI ---
@dp.message(F.text == "📊 Taqdimot qilish")
async def ppt_start(message: types.Message):
    await message.answer("Taqdimot mavzusini yuboring (masalan: Quyosh tizimi):")

@dp.message()
async def handle_all(message: types.Message):
    mavzu = message.text
    status = await message.answer("⏳ Ishlamoqdaman...")

    try:
        # Wikipedia'dan asosiy ma'lumotni olamiz
        search = wikipedia.search(mavzu)
        page = wikipedia.page(search[0])
        info = page.summary[:1500]

        # Agar foydalanuvchi Taqdimot so'ragan bo'lsa (oxirgi bosilgan tugmani tekshirish o'rniga sodda mantiq)
        if "📊" in str(message.reply_to_message) or len(mavzu) < 50: 
            # PowerPoint yaratish
            prs = Presentation()
            
            # 1-Slayd: Titul
            slide1 = prs.slides.add_slide(prs.slide_layouts[0])
            slide1.shapes.title.text = page.title
            slide1.shapes.placeholders[1].text = "Mustaqil ish\nTayyorladi: Aqlli Talaba Boti"

            # 2-Slayd: Ma'lumot
            slide2 = prs.slides.add_slide(prs.slide_layouts[1])
            slide2.shapes.title.text = "Mavzu haqida"
            slide2.shapes.placeholders[1].text = info[:500]

            file_path = f"{mavzu}.pptx"
            prs.save(file_path)
            
            # Faylni yuborish
            input_file = FSInputFile(file_path)
            await message.answer_document(input_file, caption=f"✅ {mavzu} bo'yicha taqdimot tayyor!")
            os.remove(file_path) # Serverda joy egallamasligi uchun o'chiramiz
            await status.delete()
        
    except Exception as e:
        await status.edit_text("❌ Xatolik: Mavzuni aniqroq yozing yoki boshqa mavzu sinab ko'ring.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
