import os
import asyncio
import google.generativeai as genai
from pptx import Presentation
from pptx.util import Inches, Pt
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

# --- SOZLAMALAR ---
TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=TOKEN)
dp = Dispatcher()

class BotStates(StatesGroup):
    waiting_for_pptx = State()

# --- MENYU ---
menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📊 Professional Taqdimot (PPTX)")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Salom! Men professional taqdimotlar yaratuvchi botman. 🚀", 
        reply_markup=menu
    )

@dp.message(F.text == "📊 Professional Taqdimot (PPTX)")
async def pptx_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_pptx)
    await message.answer("📊 Taqdimot mavzusini yuboring:")

@dp.message(BotStates.waiting_for_pptx)
async def handle_pptx(message: types.Message, state: FSMContext):
    msg = await message.answer("🎨 Slaydlar dizayni va mazmuni shakllantirilmoqda...")
    try:
        # Promptni kuchaytirish
        prompt = (
            f"'{message.text}' mavzusida 8 ta slayddan iborat professional taqdimot matni yoz. "
            f"Har bir slayd 'SLAYD:' so'zi bilan boshlansin. "
            f"Tuzilishi: 1.Sarlavha, 2.Reja, 3.Kirish, 4-6.Asosiy tahlil, 7.Xulosa, 8.Foydalanilgan manbalar. "
            f"Faqat o'zbek tilida, akademik tilda yoz."
        )
        response = model.generate_content(prompt)
        
        prs = Presentation()
        # 16:9 keng format (Zamonaviy dizayn)
        prs.slide_width = 12192000
        prs.slide_height = 6858000
        
        slides_data = response.text.split("SLAYD:")
        for data in slides_data[1:]:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            lines = data.strip().split("\n")
            
            if lines:
                # Sarlavha qismini sozlash
                title = slide.shapes.title
                title.text = lines[0].replace(":", "").strip()
                
                # Matn qismini punktlarga bo'lish
                content = slide.placeholders[1]
                clean_lines = [l.strip() for l in lines[1:] if l.strip()]
                content.text = "\n".join(clean_lines)

        file_path = f"taqdimot_{message.from_user.id}.pptx"
        prs.save(file_path)
        
        await message.answer_document(
            FSInputFile(file_path), 
            caption=f"✅ '{message.text}' mavzusidagi professional taqdimot tayyor!"
        )
        os.remove(file_path)
        
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
    
    await msg.delete()
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
