import os
import asyncio
import google.generativeai as genai
from pptx import Presentation
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

# --- KONFIGURATSIYA ---
TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini AI sozlash
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=TOKEN)
dp = Dispatcher()

class BotStates(StatesGroup):
    waiting_for_pptx = State()

# Taqdimot funksiyasi (KUCHAYTIRILGAN)
@dp.message(F.text == "📊 Professional Taqdimot (PPTX)")
async def pptx_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_pptx)
    await message.answer("📊 Taqdimot mavzusini yuboring (Masalan: 'Global isish'):")

@dp.message(BotStates.waiting_for_pptx)
async def handle_pptx(message: types.Message, state: FSMContext):
    msg = await message.answer("🎨 Slaydlar professional darajada tayyorlanmoqda...")
    try:
        # Kuchaytirilgan Prompt
        prompt = (
            f"'{message.text}' mavzusida 7 ta professional slayd yoz. "
            f"Har bir slayd 'SLAYD:' so'zi bilan boshlansin. "
            f"Slaydlar: 1.Kirish, 2-3.Mavzu mohiyati, 4-5.Tahlil va misollar, 6.Faktlar, 7.Xulosa."
        )
        response = model.generate_content(prompt)
        
        prs = Presentation()
        # 16:9 keng format
        prs.slide_width = 12192000
        prs.slide_height = 6858000
        
        slides_data = response.text.split("SLAYD:")
        for data in slides_data[1:]:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            lines = data.strip().split("\n")
            if lines:
                slide.shapes.title.text = lines[0].replace(":", "").strip()
                slide.placeholders[1].text = "\n".join(lines[1:]).strip()
        
        file_path = f"taqdimot_{message.from_user.id}.pptx"
        prs.save(file_path)
        await message.answer_document(FSInputFile(file_path), caption=f"✅ {message.text} tayyor!")
        os.remove(file_path)
    except Exception as e:
        await message.answer(f"❌ Xato: {str(e)}")
    await msg.delete()
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
