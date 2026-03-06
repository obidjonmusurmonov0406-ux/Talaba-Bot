import os
import asyncio
import google.generativeai as genai
from pptx import Presentation
from docx import Document
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

# --- KONFIGURATSIYA ---
# Railway Variables'dan o'zgaruvchilarni olamiz
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Gemini AI ulanishi
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Holatlar (States)
class BotStates(StatesGroup):
    waiting_for_esse = State()
    waiting_for_pptx = State()

# --- MENYU ---
menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📝 Sifatli Esse (Word)"), KeyboardButton(text="📊 Professional Taqdimot (PPTX)")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Salom! Men Gemini AI bilan ishlaydigan aqlli yordamchiman. 🎓\n"
        "Wikipedia'dagi sifatsiz ma'lumotlar o'rniga, endi tahliliy ishlar tayyorlayman.", 
        reply_markup=menu
    )

# --- ESSE YARATISH ---
@dp.message(F.text == "📝 Sifatli Esse (Word)")
async def esse_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_esse)
    await message.answer("📝 Esse mavzusini yuboring (Masalan: 'O'zbekistonning boy madaniyati'):")

@dp.message(BotStates.waiting_for_esse)
async def handle_esse(message: types.Message, state: FSMContext):
    msg = await message.answer("🧠 AI mavzuni tahlil qilib, esse yozmoqda...")
    try:
        # Prompt orqali AIga aniq vazifa beramiz
        prompt = f"'{message.text}' mavzusida o'zbek tilida akademik esse yoz. Tarkib: Reja, Kirish, 3 ta asosiy qism va Xulosa."
        response = model.generate_content(prompt)
        
        # Word fayl yaratish
        doc = Document()
        doc.add_heading(message.text, 0)
        doc.add_paragraph(response.text)
        
        file_path = f"{message.text[:10]}.docx"
        doc.save(file_path)
        
        await message.answer_document(FSInputFile(file_path), caption=f"✅ '{message.text}' bo'yicha esse tayyor!")
        os.remove(file_path) # Serverni tozalash
    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi. API kalit yoki ulanishni tekshiring.")
    await msg.delete()
    await state.clear()

# --- TAQDIMOT YARATISH ---
@dp.message(F.text == "📊 Professional Taqdimot (PPTX)")
async def pptx_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_pptx)
    await message.answer("📊 Taqdimot mavzusini yuboring:")

@dp.message(BotStates.waiting_for_pptx)
async def handle_pptx(message: types.Message, state: FSMContext):
    msg = await message.answer("🎨 Taqdimot slaydlari tayyorlanmoqda...")
    try:
        prompt = f"'{message.text}' mavzusida 5 ta slayd uchun sarlavha va qisqa matn yoz (O'zbekcha). Har bir slaydni 'SLAYD:' so'zi bilan boshla."
        response = model.generate_content(prompt)
        
        prs = Presentation()
        # AI javobini slaydlarga bo'lish
        slides_data = response.text.split("SLAYD:")
        
        for data in slides_data[1:]:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            lines = data.strip().split("\n")
            slide.shapes.title.text = lines[0].replace(":", "")
            slide.placeholders[1].text = "\n".join(lines[1:])
            
        file_path = f"{message.text[:10]}.pptx"
        prs.save(file_path)
        await message.answer_document(FSInputFile(file_path), caption=f"✅ '{message.text}' mavzusidagi taqdimot tayyor!")
        os.remove(file_path)
    except Exception as e:
        await message.answer("❌ Taqdimot yaratishda xatolik.")
    await msg.delete()
    await state.clear()

# --- ASOSIY FUNKSIYA ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
